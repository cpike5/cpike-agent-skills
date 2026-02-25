# Extended Thinking

Extended thinking gives Claude a scratchpad for internal reasoning before producing a final response. The model generates a `thinking` content block containing its chain of thought, followed by a `text` content block with the final answer.

## When to Use

| Use case | Benefit |
|---|---|
| Multi-step math or logic | Reduces errors vs direct answer |
| Complex planning (e.g., scheduling, architecture) | Forces structured breakdown |
| Ambiguous requirements | Surfaced reasoning aids review |
| Hard coding problems | Explores edge cases before responding |
| Research synthesis | Integrates contradictory sources |

**Do not use** for simple factual lookups, short classification tasks, or latency-sensitive endpoints — thinking tokens count toward output costs and increase latency.

## BudgetTokens

`BudgetTokens` is the maximum number of tokens Claude may use for internal reasoning. It is a budget, not a fixed amount — Claude uses only what it needs.

| Task complexity | Recommended budget |
|---|---|
| Simple (1-2 step reasoning) | 1,000 – 2,000 |
| Moderate (planning, debug) | 4,000 – 8,000 |
| Hard (architecture, math proofs) | 10,000 – 16,000 |
| Maximum allowed | 32,000 |

**Rule:** `BudgetTokens` must be less than `MaxTokens`. Set `MaxTokens` to at least `BudgetTokens + expected_answer_tokens`.

## Official SDK (Streaming Required)

The official `Anthropic` SDK exposes extended thinking via streaming. Non-streaming requests with thinking enabled are not currently supported in the official SDK.

```csharp
using Anthropic;
using Anthropic.Models.Messages;

MessageCreateParams parameters = new()
{
    Model = "claude-opus-4-6",
    MaxTokens = 8192,
    Thinking = new ThinkingConfigEnabledParams
    {
        BudgetTokens = 6000,
    },
    Messages = [new() { Role = Role.User, Content = "Design a database schema for a multi-tenant SaaS billing system." }],
};

var aggregator = new MessageContentAggregator();

await foreach (var rawEvent in client.Messages
    .CreateStreaming(parameters)
    .CollectAsync(aggregator))
{
    if (rawEvent.TryPickContentBlockDelta(out var delta))
    {
        if (delta.Delta.TryPickThinking(out var thinkingDelta))
        {
            // Internal reasoning — optionally display or log
            Console.Write(thinkingDelta.Thinking);
        }
        else if (delta.Delta.TryPickText(out var textDelta))
        {
            // Final answer tokens
            Console.Write(textDelta.Text);
        }
    }
}

// Inspect the complete message after streaming
Message full = await aggregator.Message();

foreach (var block in full.Content)
{
    if (block.TryPickThinking(out var thinking))
        Console.WriteLine($"[Thinking]\n{thinking.Thinking}");
    else if (block.TryPickText(out var text))
        Console.WriteLine($"[Answer]\n{text.Text}");
}
```

## Unofficial SDK (Non-Streaming Available)

`Anthropic.SDK` supports extended thinking in both streaming and non-streaming modes.

### Non-streaming

```csharp
using Anthropic.SDK;
using Anthropic.SDK.Messaging;

var client = new AnthropicClient();

var parameters = new MessageParameters
{
    Messages = [new Message(RoleType.User, "Prove that sqrt(2) is irrational.")],
    Model = AnthropicModels.Claude46Sonnet,
    MaxTokens = 8000,
    Thinking = new ThinkingParameters { BudgetTokens = 6000 },
};

var result = await client.Messages.GetClaudeMessageAsync(parameters);

string thoughts = result.Message.ThinkingContent;  // raw thinking text
string answer  = result.Message.ToString();         // final response text
```

### Streaming (unofficial SDK)

```csharp
var parameters = new MessageParameters
{
    Messages = [new Message(RoleType.User, "Plan a microservices migration strategy.")],
    Model = AnthropicModels.Claude46Sonnet,
    MaxTokens = 8000,
    Stream = true,
    Thinking = new ThinkingParameters { BudgetTokens = 5000 },
};

await foreach (var res in client.Messages.StreamClaudeMessageAsync(parameters))
{
    if (res.Delta?.Type == "thinking_delta")
        Console.Write(res.Delta.Thinking);
    else if (res.Delta?.Text != null)
        Console.Write(res.Delta.Text);
}
```

## Accessing Thinking Content Blocks

After streaming with `MessageContentAggregator` (official SDK), iterate `full.Content` to separate thinking from text:

```csharp
var thinkingBlocks = new List<string>();
var textBlocks = new List<string>();

foreach (var block in full.Content)
{
    if (block.TryPickThinking(out var t))
        thinkingBlocks.Add(t.Thinking);
    else if (block.TryPickText(out var txt))
        textBlocks.Add(txt.Text);
}

string reasoning = string.Join("\n", thinkingBlocks);
string answer    = string.Join("\n", textBlocks);
```

## DI-Friendly Thinking Service

```csharp
public class ThinkingAgent
{
    private readonly AnthropicClient _client;
    private readonly ILogger<ThinkingAgent> _logger;

    public ThinkingAgent(AnthropicClient client, ILogger<ThinkingAgent> logger)
    {
        _client = client;
        _logger = logger;
    }

    public async Task<(string Reasoning, string Answer)> ReasonAsync(
        string prompt,
        int budgetTokens = 4000,
        CancellationToken ct = default)
    {
        var parameters = new MessageCreateParams
        {
            Model = "claude-opus-4-6",
            MaxTokens = budgetTokens + 2048,
            Thinking = new ThinkingConfigEnabledParams { BudgetTokens = budgetTokens },
            Messages = [new() { Role = Role.User, Content = prompt }],
        };

        var aggregator = new MessageContentAggregator();
        int thinkingTokens = 0;

        await foreach (var ev in _client.Messages
            .CreateStreaming(parameters)
            .CollectAsync(aggregator)
            .WithCancellation(ct))
        {
            if (ev.TryPickMessageDelta(out var msgDelta))
                thinkingTokens = (int)(msgDelta.Usage.CacheReadInputTokens ?? 0);
        }

        var full = await aggregator.Message();
        _logger.LogInformation("Thinking used {Tokens} tokens", full.Usage.OutputTokens);

        var reasoning = string.Concat(full.Content
            .Where(b => b.TryPickThinking(out _))
            .Select(b => { b.TryPickThinking(out var t); return t.Thinking; }));

        var answer = string.Concat(full.Content
            .Where(b => b.TryPickText(out _))
            .Select(b => { b.TryPickText(out var t); return t.Text; }));

        return (reasoning, answer);
    }
}
```

## Extended Thinking in Agentic Loops

Thinking blocks must be preserved in conversation history when continuing a multi-turn thinking session. Pass the complete assistant message (including thinking blocks) back as the next turn.

```csharp
// After a thinking turn:
messages.Add(new Message
{
    Role = Role.Assistant,
    Content = full.Content,  // includes both thinking and text blocks
});

// Next user turn continues with full context
messages.Add(new Message { Role = Role.User, Content = "Now implement the schema in SQL." });
```

**Do not strip thinking blocks** from history when continuing a thinking-enabled conversation — the model uses prior thinking to maintain reasoning consistency.

## Token Cost Guidance

Thinking tokens count toward output token billing. Estimate costs before enabling:

| Budget | Approx. cost multiplier vs no thinking |
|---|---|
| 2,000 tokens | ~2x output tokens |
| 8,000 tokens | ~5-8x output tokens |
| 16,000 tokens | ~10-15x output tokens |

Use `MaxTokens` as a hard cost cap: if `MaxTokens = 6500` and `BudgetTokens = 6000`, the answer has at most 500 tokens available.

## SDK Comparison

| Feature | Official `Anthropic` | Unofficial `Anthropic.SDK` |
|---|---|---|
| Non-streaming thinking | Not supported | Yes (`GetClaudeMessageAsync`) |
| Streaming thinking | Yes (`CreateStreaming`) | Yes (`StreamClaudeMessageAsync`) |
| Access thinking text | `TryPickThinking` on blocks | `result.Message.ThinkingContent` |
| Config API | `ThinkingConfigEnabledParams` | `ThinkingParameters` |
| DI integration | Via `AnthropicClient` in DI | Via `AnthropicClient` in DI |
