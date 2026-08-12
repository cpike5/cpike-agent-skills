# Context Management

## Context Window Limits by Model

| Model | Context Window | Notes |
|-------|---------------|-------|
| Claude Opus 5 / Sonnet 5 | 1M tokens | 128K max output (stream for large outputs) |
| Claude Opus 4.6–4.8 / Sonnet 4.6 | 1M tokens | |
| Claude Haiku 4.5 | 200K tokens | 64K max output |

A token is roughly 3-4 characters of English text — but counts are model-specific (Sonnet 5's tokenizer produces ~30% more tokens than Sonnet 4.6 for the same text), so re-baseline with the count-tokens endpoint when switching models rather than reusing measured numbers.

## Token Counting (Official SDK)

The official `Anthropic` package exposes `count_tokens` directly:

```csharp
using Anthropic.Models.Messages;

MessageTokensCount result = await client.Messages.CountTokens(new MessageCountTokensParams
{
    Model = "claude-opus-5",
    Messages = messages,
});
Console.WriteLine($"Input tokens: {result.InputTokens}");
```

Use this before sending to decide whether to compact the conversation first. (The unofficial `Anthropic.SDK` package has an equivalent `CountMessageTokensAsync`.)

## Response Usage Fields

Every `Message` response includes token usage:

```csharp
var message = await client.Messages.Create(parameters);

Console.WriteLine($"Input tokens:  {message.Usage.InputTokens}");
Console.WriteLine($"Output tokens: {message.Usage.OutputTokens}");
Console.WriteLine($"Cache read:    {message.Usage.CacheReadInputTokens}");
Console.WriteLine($"Cache write:   {message.Usage.CacheCreationInputTokens}");
```

Track cumulative usage over a session to detect runaway context growth:

```csharp
public class TokenBudget
{
    public int TotalInputTokens { get; private set; }
    public int TotalOutputTokens { get; private set; }
    public int MaxInputTokens { get; init; } = 150_000;

    public void Record(Usage usage)
    {
        TotalInputTokens += usage.InputTokens;
        TotalOutputTokens += usage.OutputTokens;
    }

    public bool IsNearLimit => TotalInputTokens > MaxInputTokens * 0.8;
    public bool IsOverLimit => TotalInputTokens > MaxInputTokens;
}
```

## Server-Side Compaction (Beta)

Before building client-side compaction, note the API can now do this for you: with the `compact-2026-01-12` beta header and `context_management: {edits: [{type: "compact_20260112"}]}` on the beta messages endpoint, the API summarizes earlier context server-side when the conversation approaches the window. The critical rule is to append the full `response.Content` (including `compaction` blocks) back into history — extracting only the text silently loses the compaction state. The client-side strategies below remain useful when you need deterministic control or are off the beta surface.

## Conversation History for Long-Running Agents

Agents accumulate history. Left unmanaged, conversations eventually exceed the context window.

```csharp
public class ConversationManager
{
    private readonly List<Message> _history = new();
    private readonly AnthropicClient _client;
    private readonly ILogger<ConversationManager> _logger;

    private const int MaxMessages = 50;
    private const int RecentMessageWindow = 20;

    public void AddUserMessage(string content)
        => _history.Add(new() { Role = Role.User, Content = content });

    public void AddAssistantMessage(object content)
        => _history.Add(new() { Role = Role.Assistant, Content = content });

    public async Task<List<Message>> GetMessagesAsync()
    {
        if (_history.Count <= MaxMessages)
            return _history;

        _logger.LogInformation(
            "Compacting conversation: {Count} messages -> compacted",
            _history.Count);

        return await CompactAsync();
    }
}
```

## Sliding Window Compaction

Discard old messages and keep the recent window. Fast but loses historical context.

```csharp
private List<Message> SlidingWindow(int keepCount = 20)
{
    if (_history.Count <= keepCount)
        return _history;

    return _history
        .TakeLast(keepCount)
        .ToList();
}
```

**Constraint:** The first message in a conversation must have `Role.User`. If sliding window cuts to an assistant message, shift one more:

```csharp
private List<Message> SlidingWindow(int keepCount = 20)
{
    var recent = _history.TakeLast(keepCount).ToList();

    // Ensure conversation starts with a user message
    while (recent.Count > 0 && recent[0].Role == Role.Assistant)
        recent.RemoveAt(0);

    return recent;
}
```

## Summarization Compaction

Use a separate Claude call to summarize the older portion, then inject the summary as context. Preserves meaning at the cost of an extra API call.

```csharp
private async Task<List<Message>> CompactAsync()
{
    var olderMessages = _history
        .Take(_history.Count - RecentMessageWindow)
        .ToList();
    var recentMessages = _history
        .TakeLast(RecentMessageWindow)
        .ToList();

    var summary = await SummarizeAsync(olderMessages);

    return
    [
        new()
        {
            Role = Role.User,
            Content = $"[Previous conversation summary]\n{summary}"
        },
        new()
        {
            Role = Role.Assistant,
            Content = "Understood. I have context from our earlier discussion."
        },
        .. recentMessages
    ];
}

private async Task<string> SummarizeAsync(List<Message> messages)
{
    var formatted = string.Join("\n\n", messages.Select(m =>
        $"{m.Role}: {ExtractText(m.Content)}"));

    var summaryParams = new MessageCreateParams
    {
        Model = "claude-haiku-4-5",  // Use a fast/cheap model
        MaxTokens = 1024,
        System = "Summarize the following conversation concisely. Preserve all key decisions, facts, and outcomes. Use bullet points.",
        Messages =
        [
            new() { Role = Role.User, Content = formatted }
        ]
    };

    var response = await _client.Messages.Create(summaryParams);
    return ExtractText(response.Content);
}
```

## Complete ConversationManager

```csharp
public class ConversationManager
{
    private readonly List<Message> _history = new();
    private readonly AnthropicClient _client;
    private readonly ILogger<ConversationManager> _logger;

    private const int CompactionThreshold = 40;
    private const int RecentMessageWindow = 15;

    public ConversationManager(AnthropicClient client, ILogger<ConversationManager> logger)
    {
        _client = client;
        _logger = logger;
    }

    public void Add(Role role, object content)
        => _history.Add(new() { Role = role, Content = content });

    public async Task<Message[]> GetContextAsync()
    {
        if (_history.Count < CompactionThreshold)
            return _history.ToArray();

        _logger.LogInformation(
            "Compacting {Total} messages, keeping recent {Window}",
            _history.Count, RecentMessageWindow);

        var compacted = await CompactAsync();
        _history.Clear();
        _history.AddRange(compacted);
        return _history.ToArray();
    }

    public int MessageCount => _history.Count;

    private async Task<List<Message>> CompactAsync()
    {
        var older = _history.SkipLast(RecentMessageWindow).ToList();
        var recent = _history.TakeLast(RecentMessageWindow).ToList();
        var summary = await SummarizeAsync(older);

        var result = new List<Message>
        {
            new() { Role = Role.User, Content = $"[Conversation history summary]\n{summary}" },
            new() { Role = Role.Assistant, Content = "I have the prior conversation context." }
        };
        result.AddRange(recent);
        return result;
    }

    private async Task<string> SummarizeAsync(List<Message> messages)
    {
        var text = string.Join("\n\n", messages.Select(m =>
            $"{m.Role.ToString().ToUpper()}: {ExtractText(m.Content)}"));

        var response = await _client.Messages.Create(new MessageCreateParams
        {
            Model = "claude-haiku-4-5",
            MaxTokens = 512,
            System = "Summarize this conversation. Preserve decisions, file paths, code changes, and key facts as bullet points.",
            Messages = [new() { Role = Role.User, Content = text }]
        });

        return ExtractText(response.Content);
    }

    private static string ExtractText(object content)
    {
        if (content is string s) return s;
        if (content is IEnumerable<ContentBlock> blocks)
            return string.Concat(blocks.OfType<TextBlock>().Select(b => b.Text));
        return content?.ToString() ?? "";
    }
}
```

## Strategy Comparison

| Strategy | Token Cost | Context Fidelity | Latency | Use When |
|----------|-----------|-----------------|---------|----------|
| Sliding window | None | Low (loses history) | None | Short task agents |
| Summarization | Extra API call | Medium | +1 LLM call | Long conversations |
| Hybrid | Extra API call | High | +1 LLM call | Production agents |

Hybrid: summarize old messages AND keep the recent window intact.

## Proactive Compaction

Check token usage after each response and compact before the next call:

```csharp
var response = await _client.Messages.Create(parameters);
_tokenBudget.Record(response.Usage);

if (_tokenBudget.IsNearLimit)
{
    _logger.LogInformation("Approaching token limit, compacting conversation");
    var compacted = await _conversationManager.GetContextAsync();
    // Use compacted messages for next iteration
}
```
