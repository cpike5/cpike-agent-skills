# Tool Definitions

## Tool Definition Schema

```json
{
  "name": "get_weather",
  "description": "Get the current weather in a given location. Returns temperature and conditions for the specified city. Use this when a user asks about current weather conditions. Does not provide forecasts or historical data.",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g. San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "The unit of temperature"
      }
    },
    "required": ["location"]
  }
}
```

## Description Best Practices

**Write 3-4 sentence descriptions.** This is the single most important factor in tool performance.

| Aspect | Include | Example |
|--------|---------|---------|
| What it does | Primary function | "Retrieves the current stock price for a given ticker symbol." |
| When to use | Triggering conditions | "Use when the user asks about current or recent stock prices." |
| What it returns | Output format | "Returns the latest trade price in USD." |
| Limitations | What it can't do | "Does not provide forecasts or historical data." |

**Bad:** `"description": "Gets weather"`
**Good:** `"description": "Get the current weather in a given location. Returns temperature, humidity, and conditions. Use when a user asks about current weather. Does not provide forecasts or historical data."`

## Parameter Documentation

- Use **unambiguous names**: `user_id` not `user`
- Add **descriptions with examples**: `"The city and state, e.g. San Francisco, CA"`
- Use **enums** for constrained values: `"enum": ["celsius", "fahrenheit"]`
- Mark **required vs optional** explicitly in the `required` array

## Input Examples

`input_examples` shows Claude concrete usage patterns:

```json
{
  "name": "search_logs",
  "description": "Search application logs with structured query. Returns matching log entries with timestamps and severity. Use for debugging, monitoring, or incident investigation.",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Search query string" },
      "time_range": { "type": "string", "description": "e.g. last_1h, last_24h, last_7d" },
      "severity": { "type": "string", "enum": ["debug", "info", "warn", "error"] }
    },
    "required": ["query"]
  },
  "input_examples": [
    { "query": "status:500", "time_range": "last_1h", "severity": "error" },
    { "query": "user_id:12345", "time_range": "last_24h" },
    { "query": "timeout OR connection_refused", "severity": "warn" }
  ]
}
```

## Strict Mode (Structured Outputs)

Add `strict: true` for guaranteed schema conformance:

```json
{
  "name": "create_order",
  "description": "Create a new order in the system.",
  "strict": true,
  "input_schema": {
    "type": "object",
    "properties": {
      "product_id": { "type": "string" },
      "quantity": { "type": "integer" }
    },
    "required": ["product_id", "quantity"]
  }
}
```

Strict mode ensures Claude's tool calls always match your schema exactly — no type mismatches or missing fields.

## tool_choice

Control whether and how Claude uses tools:

| Value | Behavior |
|-------|----------|
| `{"type": "auto"}` | Claude decides (default) |
| `{"type": "any"}` | Must use at least one tool |
| `{"type": "tool", "name": "get_weather"}` | Must use specific tool |
| `{"type": "none"}` | Prevent tool use |

```csharp
// In MessageCreateParams (raw API)
// tool_choice is set as part of the request body

// With IChatClient, tool_choice is controlled via ChatOptions
var options = new ChatOptions
{
    Tools = tools,
    // ToolMode can control forced/auto selection
};
```

## Parallel Tool Calls

Claude can call multiple tools in a single response when operations are independent:

```json
// Claude's response
{
  "content": [
    { "type": "tool_use", "id": "toolu_1", "name": "get_weather", "input": { "location": "NYC" } },
    { "type": "tool_use", "id": "toolu_2", "name": "get_time", "input": { "timezone": "EST" } }
  ]
}
```

**You must return ALL tool_results together in a single user message:**

```json
{
  "role": "user",
  "content": [
    { "type": "tool_result", "tool_use_id": "toolu_1", "content": "72F, sunny" },
    { "type": "tool_result", "tool_use_id": "toolu_2", "content": "2:30 PM EST" }
  ]
}
```

Never send partial results. Execute all tools (in parallel if possible), collect all results, send together.

## Complex Schema Patterns

### Nested Objects

```json
{
  "input_schema": {
    "type": "object",
    "properties": {
      "filter": {
        "type": "object",
        "properties": {
          "date_range": {
            "type": "object",
            "properties": {
              "start": { "type": "string", "format": "date" },
              "end": { "type": "string", "format": "date" }
            }
          },
          "status": { "type": "string", "enum": ["active", "archived"] }
        }
      }
    }
  }
}
```

### Arrays

```json
{
  "input_schema": {
    "type": "object",
    "properties": {
      "tags": {
        "type": "array",
        "items": { "type": "string" },
        "description": "List of tags to filter by"
      }
    }
  }
}
```

## Tool Naming Conventions

- Use **snake_case**: `get_weather`, `search_database`
- Use **meaningful namespacing**: `github_list_prs`, `slack_send_message`
- **Consolidate related operations** into fewer tools with an `action` parameter rather than separate tools per action

## Response Format Best Practices

From Anthropic's "Writing Tools for Agents" guide:

| Practice | Description |
|----------|-------------|
| Semantic field names | Return `name`, `image_url` — not `uuid`, `mime_type` |
| Response format parameter | Optional `response_format` enum (`concise` / `detailed`) |
| Pagination & filtering | Sensible defaults, avoid dumping everything |
| Actionable errors | Specific, correctable error messages |
| Format testing | Test XML vs JSON vs Markdown for your use case |
