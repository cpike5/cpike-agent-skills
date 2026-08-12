# Thinking (Adaptive)

Thinking gives Claude an internal reasoning phase before producing a final response. The model generates a `thinking` content block, followed by a `text` content block with the final answer.

**Adaptive thinking replaced manual thinking budgets.** On current models you no longer set a token budget — Claude decides when and how much to think, and you tune depth with the `effort` parameter.

| Model | Thinking config |
|---|---|
| Claude Opus 5 | On by default — omitting `Thinking` runs adaptive; `ThinkingConfigAdaptive` is equivalent. `ThinkingConfigDisabled` only allowed at effort `high` or below |
| Claude Sonnet 5, Opus 4.8/4.7 | `ThinkingConfigAdaptive` (Sonnet 5 defaults to adaptive when omitted; Opus 4.8/4.7 run without thinking when omitted) |
| Opus 4.6 / Sonnet 4.6 | `ThinkingConfigAdaptive` recommended; `BudgetTokens` deprecated |
| Older (Sonnet 4.5, Haiku 4.5) | `ThinkingConfigEnabled { BudgetTokens = N }` (budget < MaxTokens, min 1024) |

**`BudgetTokens` returns a 400 on Claude Opus 5, Opus 4.8/4.7, Sonnet 5, and Fable 5.** If you're carrying `ThinkingConfigEnabledParams { BudgetTokens = ... }` forward from older code, replace it with adaptive thinking + effort.

## When to Lean on Thinking

| Use case | Benefit |
|---|---|
| Multi-step math or logic | Reduces errors vs direct answer |
| Complex planning (e.g., scheduling, architecture) | Structured breakdown |
| Hard coding problems | Explores edge cases before responding |
| Research synthesis | Integrates contradictory sources |

For simple lookups or latency-sensitive endpoints, lower `Effort` instead of disabling thinking — low effort with adaptive thinking is usually better (and cheaper) than thinking-off.

## Basic Usage (Official SDK)

Non-streaming works fine; stream when responses are long (see below).

```csharp
using Anthropic;
using Anthropic.Models.Messages;

var response = await client.Messages.Create(new MessageCreateParams
{
    Model = "claude-opus-5",
    MaxTokens = 16000,
    // Display opt-in: default is "omitted" (thinking blocks arrive with empty text)
    Thinking = new ThinkingConfigAdaptive { Display = Display.Summarized },
    OutputConfig = new OutputConfig { Effort = Effort.High },
    Messages = [new() { Role = Role.User, Content = "Design a database schema for a multi-tenant SaaS billing system." }],
});

foreach (var block in response.Content)
{
    if (block.TryPickThinking(out var thinking))
        Console.WriteLine($"[Thinking]\n{thinking.Thinking}");
    else if (block.TryPickText(out var text))
        Console.WriteLine($"[Answer]\n{text.Text}");
}
```

## Effort: the Depth Control

`Effort` lives inside `OutputConfig` and controls thinking depth and overall token spend. API levels: `low` / `medium` / `high` / `xhigh` / `max` (default `high`).

| Level | Use when |
|---|---|
| `xhigh` | Hardest coding and agentic tasks |
| `high` | Default for intelligence-sensitive work |
| `medium` | Cost-conscious balance |
| `low` | Short, scoped, latency-sensitive tasks |

**Rule:** `MaxTokens` caps thinking *plus* response text. Give headroom — 16K+ for non-trivial tasks, and stream at 64K+.

## Reading Thinking Output

On Claude Opus 5 / Opus 4.8 / 4.7 / Sonnet 5, `Thinking.Display` defaults to `"omitted"`: thinking blocks still appear but their text is empty. Set `Display = Display.Summarized` to receive a readable summary. Display controls visibility only — thinking happens and is billed the same either way; the raw chain of thought is never returned on the newest models.

If your product streams reasoning to users, the omitted default looks like a long pause before output — opt into summarized display explicitly.

## Streaming Thinking Deltas

```csharp
var aggregator = new MessageContentAggregator();

await foreach (var rawEvent in client.Messages
    .CreateStreaming(parameters)
    .CollectAsync(aggregator))
{
    if (rawEvent.TryPickContentBlockDelta(out var delta))
    {
        if (delta.Delta.TryPickThinking(out var thinkingDelta))
            Console.Write(thinkingDelta.Thinking);   // reasoning summary tokens
        else if (delta.Delta.TryPickText(out var textDelta))
            Console.Write(textDelta.Text);           // final answer tokens
    }
}

Message full = await aggregator.Message();
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
        CancellationToken ct = default)
    {
        var response = await _client.Messages.Create(new MessageCreateParams
        {
            Model = "claude-opus-5",
            MaxTokens = 16000,
            Thinking = new ThinkingConfigAdaptive { Display = Display.Summarized },
            OutputConfig = new OutputConfig { Effort = Effort.High },
            Messages = [new() { Role = Role.User, Content = prompt }],
        });

        _logger.LogInformation("Output tokens (incl. thinking): {Tokens}", response.Usage.OutputTokens);

        var reasoning = string.Concat(response.Content
            .Where(b => b.TryPickThinking(out _))
            .Select(b => { b.TryPickThinking(out var t); return t.Thinking; }));

        var answer = string.Concat(response.Content
            .Where(b => b.TryPickText(out _))
            .Select(b => { b.TryPickText(out var t); return t.Text; }));

        return (reasoning, answer);
    }
}
```

## Thinking in Agentic Loops

Thinking blocks must be preserved in conversation history when continuing a multi-turn session. Pass the complete assistant message (including thinking blocks) back as the next turn.

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

**Do not strip thinking blocks** from history — pass them back unchanged, even when their text is empty. The API rejects modified blocks, and adaptive thinking interleaves reasoning between tool calls that the model relies on.

## Cost Guidance

Thinking tokens bill as output tokens. `Effort` is the cost lever: step down a level before reaching for prompt-side workarounds. `MaxTokens` remains the hard cap on thinking + answer combined.

## Legacy: BudgetTokens on Older Models

Only for Sonnet 4.5 / Haiku 4.5 (and, deprecated, the 4.6 family):

```csharp
Thinking = new ThinkingConfigEnabled { BudgetTokens = 6000 },  // must be < MaxTokens, min 1024
```

The unofficial `Anthropic.SDK` package exposes the same concept as `ThinkingParameters { BudgetTokens = N }` — the identical model restrictions apply, so check that SDK's releases for adaptive-thinking support before targeting current models with it.
