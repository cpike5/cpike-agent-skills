# Messages API

## MessageCreateParams

```csharp
using Anthropic;
using Anthropic.Models.Messages;

AnthropicClient client = new();

MessageCreateParams parameters = new()
{
    MaxTokens = 1024,
    Messages =
    [
        new()
        {
            Role = Role.User,
            Content = "Hello, Claude",
        },
    ],
    Model = Model.ClaudeSonnet4_5_20250929,
};

var message = await client.Messages.Create(parameters);
Console.WriteLine(message);
```

## Parameters Reference

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `Model` | `string` | Yes | Model identifier |
| `MaxTokens` | `int` | Yes | Maximum output tokens |
| `Messages` | `Message[]` | Yes | Conversation history |
| `System` | `string` | No | System prompt |
| `Temperature` | `double?` | No | 0.0–1.0 (default varies by model) |
| `TopP` | `double?` | No | Nucleus sampling |
| `TopK` | `int?` | No | Top-K sampling |
| `StopSequences` | `string[]?` | No | Custom stop sequences |

## Model Selection

```csharp
// Type-safe model constants
Model = Model.ClaudeSonnet4_5_20250929

// String model IDs (for latest or custom)
Model = "claude-opus-4-6"
Model = "claude-sonnet-4-5-20250929"
Model = "claude-haiku-4-5"
```

| Model | Best For | Context Window |
|-------|----------|---------------|
| `claude-opus-4-6` | Complex reasoning, extended thinking | 200K |
| `claude-sonnet-4-5-20250929` | Balanced performance/cost | 200K |
| `claude-haiku-4-5` | Fast, low-cost tasks | 200K |

## Message Structure

Messages alternate between `user` and `assistant` roles:

```csharp
Messages =
[
    new() { Role = Role.User, Content = "What is 2+2?" },
    new() { Role = Role.Assistant, Content = "4." },
    new() { Role = Role.User, Content = "And 3+3?" },
]
```

**Rules:**
- First message must be `Role.User`
- Roles must alternate (user → assistant → user → ...)
- Content can be a string or array of content blocks

## Content Blocks

Messages support multiple content block types:

```csharp
// Simple text
new() { Role = Role.User, Content = "Hello" }

// Multiple content blocks (for tool results, images, etc.)
new()
{
    Role = Role.User,
    Content = new object[]
    {
        new { type = "text", text = "What's in this image?" },
        new { type = "image", source = new { type = "base64", media_type = "image/png", data = base64Data } }
    }
}
```

## System Prompt

```csharp
var parameters = new MessageCreateParams
{
    Model = "claude-sonnet-4-5-20250929",
    MaxTokens = 4096,
    System = "You are a helpful coding assistant specializing in .NET.",
    Messages = [new() { Role = Role.User, Content = "Fix the bug in auth.py" }],
};
```

When tools are defined, the API auto-generates a tool prompt and appends your system prompt after it.

## Response Structure

```csharp
var message = await client.Messages.Create(parameters);

// Key fields
message.Id          // "msg_..."
message.Role        // "assistant"
message.Content     // Array of content blocks
message.StopReason  // "end_turn", "tool_use", "max_tokens", "stop_sequence"
message.Usage       // Token usage
```

## StopReason Values

| StopReason | Meaning | Action |
|------------|---------|--------|
| `end_turn` | Claude finished naturally | Return response to user |
| `tool_use` | Claude wants to call tools | Execute tools, send results, loop |
| `max_tokens` | Hit MaxTokens limit | Increase limit or handle truncation |
| `stop_sequence` | Hit a custom stop sequence | Handle based on your logic |

**In agentic loops, always check StopReason.** If it's `tool_use`, execute the tools and continue the loop. If `end_turn`, extract the text response and return it.

## Token Usage

```csharp
var message = await client.Messages.Create(parameters);

int inputTokens = message.Usage.InputTokens;
int outputTokens = message.Usage.OutputTokens;
```

Use these for cost tracking, rate limiting decisions, and context window management.

## Extracting Text from Response

```csharp
// Content is an array of blocks — extract text blocks
var textContent = message.Content
    .Where(b => b is TextBlock)
    .Cast<TextBlock>()
    .Select(b => b.Text);

string fullResponse = string.Join("", textContent);
```

## Multi-Turn Conversation

Build conversation history by appending messages:

```csharp
var history = new List<Message>();

// User turn
history.Add(new() { Role = Role.User, Content = userInput });

// API call
var parameters = new MessageCreateParams
{
    Model = "claude-sonnet-4-5-20250929",
    MaxTokens = 4096,
    Messages = history.ToArray(),
};
var response = await client.Messages.Create(parameters);

// Add assistant response to history
history.Add(new() { Role = Role.Assistant, Content = response.Content });
```

## Config Override Per-Request

```csharp
var message = await client
    .WithOptions(options =>
        options with
        {
            BaseUrl = "https://custom-proxy.example.com",
            Timeout = TimeSpan.FromSeconds(120),
            MaxRetries = 5,
        }
    )
    .Messages.Create(parameters);
```
