# Streaming

## CreateStreaming

`client.Messages.CreateStreaming` returns `IAsyncEnumerable<RawMessageStreamEvent>`. Enumerate with `await foreach`.

```csharp
using Anthropic;
using Anthropic.Models.Messages;

MessageCreateParams parameters = new()
{
    Model = "claude-opus-4-6",
    MaxTokens = 1024,
    Messages = [new() { Role = Role.User, Content = "Explain async/await in C#." }],
};

await foreach (var ev in client.Messages.CreateStreaming(parameters))
{
    Console.WriteLine(ev);  // prints each raw event
}
```

## Stream Aggregation

### Simple: collapse to a single Message

```csharp
IAsyncEnumerable<RawMessageStreamEvent> stream = client.Messages.CreateStreaming(parameters);
Message message = await stream.Aggregate();

Console.WriteLine(message.Content);
```

Use when you do not need real-time token output — just want the complete response after streaming finishes.

### Advanced: real-time output + complete Message

`MessageContentAggregator` accumulates events during enumeration and produces the full `Message` at the end.

```csharp
var aggregator = new MessageContentAggregator();

await foreach (var rawEvent in client.Messages
    .CreateStreaming(parameters)
    .CollectAsync(aggregator))
{
    if (rawEvent.TryPickContentBlockDelta(out var delta))
    {
        if (delta.Delta.TryPickText(out var textDelta))
            Console.Write(textDelta.Text);          // stream text in real time
    }
}

Message full = await aggregator.Message();          // complete aggregated message
Console.WriteLine($"\nStop reason: {full.StopReason}");
```

## Delta Processing

`RawMessageStreamEvent` is a discriminated union. Use `TryPick*` methods to safely extract specific event types.

| Method | Event type | Payload |
|---|---|---|
| `TryPickContentBlockDelta` | `content_block_delta` | `ContentBlockDeltaEvent` |
| `TryPickContentBlockStart` | `content_block_start` | `ContentBlockStartEvent` |
| `TryPickContentBlockStop` | `content_block_stop` | `ContentBlockStopEvent` |
| `TryPickMessageStart` | `message_start` | `MessageStartEvent` |
| `TryPickMessageDelta` | `message_delta` | `MessageDeltaEvent` (usage, stop_reason) |
| `TryPickMessageStop` | `message_stop` | `MessageStopEvent` |

### Text deltas

```csharp
if (rawEvent.TryPickContentBlockDelta(out var delta)
    && delta.Delta.TryPickText(out var textDelta))
{
    Console.Write(textDelta.Text);
}
```

### Thinking deltas (extended thinking)

```csharp
if (rawEvent.TryPickContentBlockDelta(out var delta)
    && delta.Delta.TryPickThinking(out var thinkingDelta))
{
    Console.Write(thinkingDelta.Thinking);  // internal reasoning text
}
```

### Stop reason from stream

```csharp
if (rawEvent.TryPickMessageDelta(out var msgDelta))
{
    Console.WriteLine($"Stop: {msgDelta.Delta.StopReason}");
    Console.WriteLine($"Output tokens: {msgDelta.Usage.OutputTokens}");
}
```

## Streaming to ASP.NET Core Response

Stream Claude's response directly to an HTTP client using `IAsyncEnumerable`:

```csharp
[HttpGet("stream")]
public async IAsyncEnumerable<string> StreamResponse(
    [FromQuery] string prompt,
    [EnumeratorCancellation] CancellationToken ct)
{
    var parameters = new MessageCreateParams
    {
        Model = "claude-opus-4-6",
        MaxTokens = 2048,
        Messages = [new() { Role = Role.User, Content = prompt }],
    };

    await foreach (var ev in _client.Messages.CreateStreaming(parameters).WithCancellation(ct))
    {
        if (ev.TryPickContentBlockDelta(out var delta)
            && delta.Delta.TryPickText(out var text))
        {
            yield return text.Text;
        }
    }
}
```

## Streaming with Tool Use in Agentic Loops

In an agentic loop, stream text for each turn, then check `StopReason` to decide whether to execute tools.

```csharp
public async IAsyncEnumerable<string> RunStreamingAgentAsync(
    string userPrompt,
    MessageCreateParams baseParams,
    [EnumeratorCancellation] CancellationToken ct = default)
{
    var messages = new List<Message>
    {
        new() { Role = Role.User, Content = userPrompt }
    };

    int iteration = 0;
    while (iteration++ < 10)
    {
        var aggregator = new MessageContentAggregator();

        await foreach (var rawEvent in _client.Messages
            .CreateStreaming(baseParams with { Messages = messages.ToArray() })
            .CollectAsync(aggregator)
            .WithCancellation(ct))
        {
            if (rawEvent.TryPickContentBlockDelta(out var delta)
                && delta.Delta.TryPickText(out var textDelta))
            {
                yield return textDelta.Text;  // stream to caller as it arrives
            }
        }

        var full = await aggregator.Message();
        messages.Add(new Message { Role = Role.Assistant, Content = full.Content });

        if (full.StopReason == "end_turn")
            yield break;

        if (full.StopReason != "tool_use")
            yield break;

        // Execute tools synchronously between turns
        var results = new List<ContentBlock>();
        foreach (var block in full.Content)
        {
            if (!block.TryPickToolUse(out var toolUse)) continue;
            var output = await ExecuteToolAsync(toolUse.Name, toolUse.Input, ct);
            results.Add(new ToolResultContentBlock { ToolUseId = toolUse.Id, Content = output });
        }

        messages.Add(new Message { Role = Role.User, Content = results });
    }
}
```

**Critical:** `MessageContentAggregator` must be created fresh per turn. It accumulates events for exactly one request.

## IChatClient Streaming

The `IChatClient` abstraction also supports streaming:

```csharp
IChatClient chatClient = new AnthropicClient()
    .AsIChatClient("claude-opus-4-6")
    .AsBuilder()
    .UseFunctionInvocation()
    .Build();

await foreach (var update in chatClient.GetStreamingResponseAsync("Write a haiku.", options))
{
    Console.Write(update);
}
```

`GetStreamingResponseAsync` returns `IAsyncEnumerable<StreamingChatCompletionUpdate>`. Each update contains a `Text` property. Tool calls are handled transparently by the middleware.

## Disposal

`CreateStreaming` returns a lazy `IAsyncEnumerable`. Disposal happens automatically when:
- Enumeration completes (all events consumed)
- The `await foreach` loop is exited via `break` or exception
- The `CancellationToken` is cancelled

Always pass a `CancellationToken` in server-side code to ensure the HTTP connection is cleaned up if the client disconnects.

## Decision: Streaming vs Non-Streaming

| Criterion | Use streaming | Use non-streaming |
|---|---|---|
| User-facing UI (chat) | Yes | No |
| Background jobs | No | Yes |
| Long responses (>500 tokens) | Yes — better UX | Acceptable |
| Need `StopReason` immediately | No — use `MessageDelta` event | Yes |
| Agentic loop with tool use | Yes — stream text per turn | Yes — simpler |
| Token counting for billing | `MessageDelta.Usage` | `response.Usage` |
