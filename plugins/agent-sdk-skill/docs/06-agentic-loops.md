# Agentic Loops

An agentic loop is the cycle of: send request → receive tool calls → execute tools → return results → repeat until `end_turn`.

.NET has no Agent SDK. You build loops manually or delegate to `UseFunctionInvocation()`.

## Pattern 1: IChatClient Auto-Loop (Simplest)

`UseFunctionInvocation()` middleware runs the entire tool-call cycle automatically. Use this unless you need control over individual iterations.

```csharp
using Anthropic;
using Microsoft.Extensions.AI;

public class SimpleAgent
{
    private readonly IChatClient _client;
    private readonly List<ChatMessage> _history = new();

    public SimpleAgent(IChatClient client)
    {
        _client = client;
    }

    public async Task<string> RunAsync(string prompt, ChatOptions options)
    {
        _history.Add(new ChatMessage(ChatRole.User, prompt));

        var response = await _client.GetResponseAsync(_history, options);

        _history.Add(response.Message);
        return response.Message.Text ?? string.Empty;
    }
}

// Registration
services.AddSingleton<IChatClient>(_ =>
    new AnthropicClient()
        .AsIChatClient("claude-opus-4-6")
        .AsBuilder()
        .UseFunctionInvocation()
        .Build());
```

**Iteration cap with auto-loop:** `UseFunctionInvocation()` defaults to no cap. Use `MaximumIterationsPerRequest` if your tools can loop infinitely:

```csharp
.AsBuilder()
.UseFunctionInvocation(options => options.MaximumIterationsPerRequest = 10)
.Build()
```

## Pattern 2: Manual Messages API Loop (Full Control)

Use when you need to inspect each iteration, log tool calls, enforce per-tool authorization, or integrate with observability.

```csharp
using Anthropic;
using Anthropic.Models.Messages;
using System.Text.Json;

public async Task<string> RunManualLoopAsync(
    string userPrompt,
    string systemPrompt,
    IReadOnlyList<Tool> tools,
    int maxIterations = 10)
{
    var messages = new List<Message>
    {
        new() { Role = Role.User, Content = userPrompt }
    };

    for (int i = 0; i < maxIterations; i++)
    {
        var response = await _client.Messages.Create(new MessageCreateParams
        {
            Model = "claude-opus-4-6",
            MaxTokens = 4096,
            System = systemPrompt,
            Tools = tools,
            Messages = messages.ToArray(),
        });

        // Append assistant turn to history
        messages.Add(new Message { Role = Role.Assistant, Content = response.Content });

        if (response.StopReason == "end_turn")
            return ExtractText(response.Content);

        if (response.StopReason != "tool_use")
            break;  // max_tokens or stop_sequence — handle as needed

        // Execute all tool calls and collect results
        var toolResults = new List<ContentBlock>();

        foreach (var block in response.Content)
        {
            if (!block.TryPickToolUse(out var toolUse))
                continue;

            var result = await ExecuteToolAsync(toolUse.Name, toolUse.Input);

            toolResults.Add(new ToolResultContentBlock
            {
                ToolUseId = toolUse.Id,
                Content = result,
            });
        }

        // Return ALL results in a single user message
        messages.Add(new Message { Role = Role.User, Content = toolResults });
    }

    return "Max iterations reached without a final answer.";
}

private static string ExtractText(IReadOnlyList<ContentBlock> content)
    => string.Concat(content
        .Where(b => b.TryPickText(out _))
        .Select(b => { b.TryPickText(out var t); return t.Text; }));
```

**Guards:**
- Always set `maxIterations` — runaway loops burn tokens
- Log each iteration with tool name, input hash, and token counts
- Detect `stop_reason == "max_tokens"` and either trim history or surface an error

## Pattern 3: Streaming Agentic Loop

Stream text tokens to the caller in real time while still handling tool calls between turns.

```csharp
using Anthropic;
using Anthropic.Models.Messages;

public async IAsyncEnumerable<string> RunStreamingLoopAsync(
    string userPrompt,
    MessageCreateParams baseParams,
    [EnumeratorCancellation] CancellationToken ct = default)
{
    var messages = new List<Message>
    {
        new() { Role = Role.User, Content = userPrompt }
    };

    int iterations = 0;
    const int MaxIterations = 10;

    while (iterations++ < MaxIterations)
    {
        var parameters = baseParams with { Messages = messages.ToArray() };
        var aggregator = new MessageContentAggregator();

        await foreach (var rawEvent in _client.Messages
            .CreateStreaming(parameters)
            .CollectAsync(aggregator)
            .WithCancellation(ct))
        {
            if (rawEvent.TryPickContentBlockDelta(out var delta)
                && delta.Delta.TryPickText(out var textDelta))
            {
                yield return textDelta.Text;  // Real-time text to caller
            }
        }

        var fullMessage = await aggregator.Message();
        messages.Add(new Message { Role = Role.Assistant, Content = fullMessage.Content });

        if (fullMessage.StopReason == "end_turn")
            yield break;

        if (fullMessage.StopReason != "tool_use")
            yield break;

        // Execute tools (same as non-streaming pattern)
        var toolResults = new List<ContentBlock>();
        foreach (var block in fullMessage.Content)
        {
            if (!block.TryPickToolUse(out var toolUse))
                continue;

            var result = await ExecuteToolAsync(toolUse.Name, toolUse.Input);
            toolResults.Add(new ToolResultContentBlock
            {
                ToolUseId = toolUse.Id,
                Content = result,
            });
        }

        messages.Add(new Message { Role = Role.User, Content = toolResults });
    }
}
```

**Key points:**
- `MessageContentAggregator` accumulates stream events into a complete `Message` for history
- Yield text deltas immediately; handle tool calls after the stream completes for that turn
- Dispose considerations: `IAsyncEnumerable` from `CreateStreaming` is disposed when enumeration ends; `CollectAsync` wraps this cleanly

## Pattern 4: DI-Friendly Agent Service (Production)

```csharp
// Program.cs / Startup
services.AddSingleton<AnthropicClient>(sp =>
    new AnthropicClient { ApiKey = sp.GetRequiredService<IConfiguration>()["Anthropic:ApiKey"] });

services.AddSingleton<IChatClient>(sp =>
    sp.GetRequiredService<AnthropicClient>()
        .AsIChatClient("claude-opus-4-6")
        .AsBuilder()
        .UseFunctionInvocation()
        .Build());

services.AddScoped<AgentService>();
```

```csharp
public class AgentService
{
    private readonly IChatClient _client;
    private readonly ILogger<AgentService> _logger;

    public AgentService(IChatClient client, ILogger<AgentService> logger)
    {
        _client = client;
        _logger = logger;
    }

    public async Task<string> ProcessAsync(
        string prompt,
        IEnumerable<AITool> tools,
        CancellationToken ct = default)
    {
        var options = new ChatOptions { Tools = tools.ToList() };

        _logger.LogInformation("Agent starting. Prompt length: {Length}", prompt.Length);

        try
        {
            var response = await _client.GetResponseAsync(prompt, options, ct);
            _logger.LogInformation("Agent finished. Usage: {Usage}", response.Usage);
            return response.Message.Text ?? string.Empty;
        }
        catch (AnthropicRateLimitException ex)
        {
            _logger.LogWarning(ex, "Rate limited");
            throw;
        }
        catch (Anthropic5xxException ex)
        {
            _logger.LogError(ex, "Server error from Anthropic API");
            throw;
        }
    }
}
```

## Conversation History Management

Long-running agents accumulate history that eventually exceeds the context window. Two strategies:

**Sliding window** — keep only the last N messages:

```csharp
private List<Message> TrimHistory(List<Message> history, int keepLast = 20)
{
    if (history.Count <= keepLast) return history;
    return history.Skip(history.Count - keepLast).ToList();
}
```

**Summarize and compact** — compress old turns into a summary message:

```csharp
private async Task<List<Message>> CompactHistoryAsync(List<Message> history)
{
    if (history.Count <= 20) return history;

    var older = history.Take(history.Count - 10).ToList();
    var recent = history.Skip(history.Count - 10).ToList();

    var summary = await _client.GetResponseAsync(
        $"Summarize this conversation, preserving key decisions and facts:\n{FormatMessages(older)}");

    return
    [
        new() { Role = Role.User,      Content = $"Prior context summary: {summary.Message.Text}" },
        new() { Role = Role.Assistant, Content = "Understood." },
        .. recent,
    ];
}
```

## Stop Reason Decision Tree

```
response.StopReason
├── "end_turn"      → extract text, return to caller, done
├── "tool_use"      → dispatch tools, add results, loop
├── "max_tokens"    → trim history or raise MaxTokens, loop or surface error
└── "stop_sequence" → extract text, handle as application-specific signal
```

## Iteration Guard Checklist

- Set `maxIterations` (10 is a reasonable default for most agents)
- Log iteration number, tool names called, and token usage each turn
- Surface `"Max iterations reached"` as a structured error, not a silent empty string
- Track cumulative token usage across turns to prevent runaway costs
