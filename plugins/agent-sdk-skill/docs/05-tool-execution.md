# Tool Execution

## How Claude Signals Tool Use

When Claude wants to call a tool, the response has `stop_reason: "tool_use"` and one or more `tool_use` content blocks:

```json
{
  "stop_reason": "tool_use",
  "content": [
    { "type": "text", "text": "I'll look that up." },
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq917835lq9",
      "name": "get_weather",
      "input": { "location": "San Francisco, CA", "unit": "celsius" }
    }
  ]
}
```

You execute the tool and return a `tool_result` content block in the **next user message**:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "15 degrees celsius, mostly cloudy"
    }
  ]
}
```

## Parallel Tool Calls

Claude may call multiple tools in a single response when operations are independent. **All `tool_result` blocks must be returned together in a single user message** — never one at a time.

```json
// Claude's response
{
  "content": [
    { "type": "tool_use", "id": "toolu_1", "name": "get_weather", "input": { "location": "NYC" } },
    { "type": "tool_use", "id": "toolu_2", "name": "get_time",    "input": { "timezone": "America/New_York" } }
  ]
}

// Your reply — ALL results in ONE user message
{
  "role": "user",
  "content": [
    { "type": "tool_result", "tool_use_id": "toolu_1", "content": "72F, sunny" },
    { "type": "tool_result", "tool_use_id": "toolu_2", "content": "2:30 PM EST" }
  ]
}
```

## Approach 1: IChatClient with Automatic Execution

`UseFunctionInvocation()` handles the `tool_use`/`tool_result` cycle automatically. No loop to write.

```csharp
using Anthropic;
using Microsoft.Extensions.AI;

IChatClient chatClient = new AnthropicClient()
    .AsIChatClient("claude-opus-4-6")
    .AsBuilder()
    .UseFunctionInvocation()
    .Build();

ChatOptions options = new()
{
    Tools =
    [
        AIFunctionFactory.Create(
            () => Environment.UserName,
            "get_current_user",
            "Returns the current OS user name."
        ),
        AIFunctionFactory.Create(
            (string path) => File.ReadAllText(path),
            "read_file",
            "Reads and returns the contents of a file at the specified path."
        ),
    ],
};

var response = await chatClient.GetResponseAsync("Who am I logged in as?", options);
Console.WriteLine(response.Message.Text);
```

**When to use:** Simple tool scenarios; you do not need to inspect intermediate tool calls.

## Approach 2: AIFunctionFactory.Create Patterns

`AIFunctionFactory.Create` accepts a delegate and infers parameter names and types from the signature. The third argument is the description Claude uses to decide when to call the tool.

```csharp
// Synchronous lambda
AIFunctionFactory.Create(
    (string city) => GetTemperature(city),
    "get_temperature",
    "Gets the current temperature in Celsius for the specified city name."
)

// Async lambda
AIFunctionFactory.Create(
    async (string query, CancellationToken ct) => await SearchDbAsync(query, ct),
    "search_records",
    "Searches the customer database for records matching the query string."
)

// Multi-parameter
AIFunctionFactory.Create(
    (string path, string content) =>
    {
        File.WriteAllText(path, content);
        return "Written successfully.";
    },
    "write_file",
    "Writes text content to a file. Creates the file if it does not exist."
)
```

**Parameter tips:**
- Use specific types (`int`, `bool`, `string`) — they are serialized into the JSON schema
- Name parameters clearly; the name appears in the schema Claude sees
- Return `string` from the delegate; complex objects are serialized to JSON automatically

## Approach 3: Manual Dispatch (Full Control)

Use when you need to inspect tool calls, implement access control, log inputs/outputs, or handle errors per tool.

```csharp
using Anthropic;
using Anthropic.Models.Messages;
using System.Text.Json;

// Execute a single turn, dispatch tool calls, return tool results
async Task<List<ContentBlock>> DispatchToolsAsync(
    IReadOnlyList<ContentBlock> content,
    Dictionary<string, Func<JsonElement, Task<string>>> handlers)
{
    var toolResults = new List<ContentBlock>();

    foreach (var block in content)
    {
        if (!block.TryPickToolUse(out var toolUse))
            continue;

        string result;
        if (handlers.TryGetValue(toolUse.Name, out var handler))
        {
            try
            {
                result = await handler(toolUse.Input);
            }
            catch (Exception ex)
            {
                result = $"Error: {ex.Message}";
            }
        }
        else
        {
            result = $"Unknown tool: {toolUse.Name}";
        }

        toolResults.Add(new ToolResultContentBlock
        {
            ToolUseId = toolUse.Id,
            Content = result,
        });
    }

    return toolResults;
}
```

Caller pattern:

```csharp
var handlers = new Dictionary<string, Func<JsonElement, Task<string>>>
{
    ["get_weather"] = async input =>
    {
        var location = input.GetProperty("location").GetString()!;
        return await WeatherService.GetAsync(location);
    },
    ["read_file"] = async input =>
    {
        var path = input.GetProperty("path").GetString()!;
        return await File.ReadAllTextAsync(path);
    },
};

// After receiving response with stop_reason == "tool_use":
var toolResults = await DispatchToolsAsync(response.Content, handlers);

messages.Add(new Message
{
    Role = Role.User,
    Content = toolResults,  // All results in a single message
});
```

## Stop Reason Reference

| `StopReason` | Meaning | Action |
|---|---|---|
| `"end_turn"` | Claude finished | Extract text, return to caller |
| `"tool_use"` | Tool calls pending | Execute tools, append results, loop |
| `"max_tokens"` | Token limit hit | Handle truncation or increase `MaxTokens` |
| `"stop_sequence"` | Custom stop sequence matched | Extract text, handle as needed |

## Tool Error Handling

Return error information as a `tool_result` — do not throw. Claude can recover and try alternatives.

```csharp
// Good: return error in content
new ToolResultContentBlock
{
    ToolUseId = toolUse.Id,
    Content = "Error: File not found at path '/etc/missing.txt'. Check that the path exists.",
    IsError = true,
}

// Bad: throw — breaks the loop and loses conversation state
throw new FileNotFoundException("...");
```

## Controlling Tool Choice

Pass `tool_choice` to constrain which tools Claude may call:

```csharp
// Force Claude to use a specific tool
"tool_choice": { "type": "tool", "name": "get_weather" }

// Claude must use at least one tool
"tool_choice": { "type": "any" }

// Claude decides (default)
"tool_choice": { "type": "auto" }

// No tools — plain text response
"tool_choice": { "type": "none" }
```

## Decision: Auto vs Manual

| Criterion | Use IChatClient auto | Use manual dispatch |
|---|---|---|
| Number of tools | Any | Any |
| Need to log tool I/O | No (middleware possible) | Yes |
| Need per-tool auth/validation | No | Yes |
| Need to cancel mid-loop | No | Yes |
| Streaming tokens during loop | Limited | Yes |
| Access to intermediate tool calls | No | Yes |
| Code complexity budget | Low | Higher |
