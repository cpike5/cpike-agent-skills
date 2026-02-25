# Advanced Features

## MCP Integration

The Model Context Protocol (MCP) lets agents connect to external tool servers. The official C# SDK integrates via `IChatClient` and the Microsoft MCP C# SDK (`ModelContextProtocol.Client`).

```bash
dotnet add package Anthropic
dotnet add package ModelContextProtocol.Client
dotnet add package Microsoft.Extensions.AI
```

### Connecting to an MCP Server

```csharp
using Anthropic;
using Microsoft.Extensions.AI;
using ModelContextProtocol.Client;

// Build the IChatClient
IChatClient chatClient = new AnthropicClient()
    .AsIChatClient("claude-opus-4-6")
    .AsBuilder()
    .UseFunctionInvocation()
    .Build();

// Connect to an MCP server (HTTP transport)
McpClient mcpServer = await McpClient.CreateAsync(
    new HttpClientTransport(new()
    {
        Endpoint = new Uri("https://learn.microsoft.com/api/mcp")
    }));

// List available tools from the MCP server
IList<AITool> mcpTools = await mcpServer.ListToolsAsync();

// Use them in a chat call
ChatOptions options = new() { Tools = [.. mcpTools] };
var response = await chatClient.GetResponseAsync(
    "Tell me about IChatClient in Microsoft.Extensions.AI", options);

Console.WriteLine(response.Message.Text);
```

### DI Registration for MCP

```csharp
// Program.cs
services.AddSingleton<IChatClient>(sp =>
    new AnthropicClient()
        .AsIChatClient("claude-opus-4-6")
        .AsBuilder()
        .UseFunctionInvocation()
        .Build()
);

services.AddSingleton<McpClient>(async sp =>
    await McpClient.CreateAsync(
        new HttpClientTransport(new()
        {
            Endpoint = new Uri(configuration["Mcp:Endpoint"]
                ?? throw new InvalidOperationException("MCP:Endpoint not configured"))
        }))
);

// Agent service
public class McpAgentService(IChatClient chatClient, McpClient mcpClient)
{
    public async Task<string> RunAsync(string prompt)
    {
        var tools = await mcpClient.ListToolsAsync();
        var options = new ChatOptions { Tools = [.. tools] };
        var response = await chatClient.GetResponseAsync(prompt, options);
        return response.Message.Text ?? "";
    }
}
```

### Combining MCP Tools with Local Tools

```csharp
var mcpTools = await mcpClient.ListToolsAsync();

var localTools = new List<AITool>
{
    AIFunctionFactory.Create(
        (string query) => SearchLocalDatabase(query),
        "search_internal_db",
        "Search the internal company database."
    )
};

var options = new ChatOptions { Tools = [.. mcpTools, .. localTools] };
```

## Programmatic Tool Calling

A pattern where Claude writes code to orchestrate tool calls programmatically within a sandboxed execution container. Reduces token consumption for multi-tool workflows.

**Available on:** Claude Opus 4.6 and Sonnet 4.5+.

### How It Works

Instead of tool calls going back to your application one at a time, Claude writes code that calls tools in loops, filters results, and returns only aggregated conclusions. This is configured at the API level via the `code_execution` tool type.

```json
{
  "tools": [
    {
      "type": "code_execution_20260120",
      "name": "code_execution"
    },
    {
      "name": "query_database",
      "description": "Execute a SQL query against the sales database. Returns rows as JSON.",
      "input_schema": {
        "type": "object",
        "properties": {
          "sql": { "type": "string", "description": "The SQL query to execute" }
        },
        "required": ["sql"]
      },
      "allowed_callers": ["code_execution_20260120"]
    }
  ]
}
```

The `allowed_callers` field restricts a tool to only be callable from within code execution — not directly by Claude's normal tool use flow. This enables Claude to batch many queries internally without a round-trip per call.

### .NET HTTP Request

Since the official C# SDK does not yet wrap this in a typed API, send the request directly:

```csharp
using System.Net.Http.Json;

public class ProgrammaticToolAgent(HttpClient http, string apiKey)
{
    public async Task<string> RunAsync(string prompt)
    {
        http.DefaultRequestHeaders.Add("x-api-key", apiKey);
        http.DefaultRequestHeaders.Add("anthropic-version", "2023-06-01");
        http.DefaultRequestHeaders.Add("anthropic-beta", "code-execution-20260120");

        var request = new
        {
            model = "claude-opus-4-6",
            max_tokens = 4096,
            tools = new object[]
            {
                new { type = "code_execution_20260120", name = "code_execution" },
                new
                {
                    name = "query_database",
                    description = "Execute a SQL query and return rows as JSON.",
                    input_schema = new
                    {
                        type = "object",
                        properties = new { sql = new { type = "string" } },
                        required = new[] { "sql" }
                    },
                    allowed_callers = new[] { "code_execution_20260120" }
                }
            },
            messages = new[]
            {
                new { role = "user", content = prompt }
            }
        };

        var response = await http.PostAsJsonAsync(
            "https://api.anthropic.com/v1/messages", request);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadFromJsonAsync<MessageResponse>();
        return result?.Content?.FirstOrDefault()?.Text ?? "";
    }
}
```

## Multi-Cloud Support

Switch between Anthropic's API, AWS Bedrock, and Azure (Microsoft Foundry) using separate NuGet packages. API surface is identical.

```bash
# Anthropic direct (default)
dotnet add package Anthropic

# AWS Bedrock
dotnet add package Anthropic.Bedrock

# Microsoft Azure (Foundry)
dotnet add package Anthropic.Foundry
```

### Bedrock

```csharp
using Anthropic.Bedrock;

// Reads AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION from environment
AnthropicBedrockClient client = new();

var message = await client.Messages.Create(new()
{
    Model = "anthropic.claude-opus-4-6-20251101-v1:0",  // Bedrock model ARN format
    MaxTokens = 1024,
    Messages = [new() { Role = Role.User, Content = "Hello!" }]
});
```

### Azure Foundry

```csharp
using Anthropic.Foundry;

AnthropicFoundryClient client = new()
{
    ApiKey = Environment.GetEnvironmentVariable("AZURE_FOUNDRY_API_KEY"),
    BaseUrl = "https://your-resource.services.ai.azure.com/models/claude-opus-4-6"
};

var message = await client.Messages.Create(new()
{
    Model = "claude-opus-4-6",
    MaxTokens = 1024,
    Messages = [new() { Role = Role.User, Content = "Hello!" }]
});
```

### Abstracting the Provider

Use the shared `AnthropicClient` base type to write provider-agnostic code:

```csharp
// Resolved at startup based on config
services.AddSingleton<AnthropicClient>(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    return config["Anthropic:Provider"] switch
    {
        "Bedrock" => new AnthropicBedrockClient() as AnthropicClient,
        "Foundry" => new AnthropicFoundryClient() { ApiKey = config["Anthropic:ApiKey"] },
        _ => new AnthropicClient() { ApiKey = config["Anthropic:ApiKey"] }
    };
});
```

## Semantic Kernel Integration

Both the official and unofficial SDKs expose `IChatClient`, making Claude available in Semantic Kernel via the `IChatClient` bridge.

```bash
dotnet add package Microsoft.SemanticKernel
dotnet add package Anthropic.SDK  # Unofficial SDK has documented SK integration
```

### Unofficial SDK + Semantic Kernel

```csharp
using Anthropic.SDK;
using Microsoft.SemanticKernel;

IChatClient CreateChatClient(IServiceProvider _)
    => new AnthropicClient().Messages
        .AsBuilder()
        .UseFunctionInvocation()
        .Build();

var kernelBuilder = Kernel.CreateBuilder();
kernelBuilder.Services.AddSingleton(CreateChatClient);
kernelBuilder.Plugins.AddFromType<WeatherPlugin>("Weather");
kernelBuilder.Plugins.AddFromType<CalendarPlugin>("Calendar");

var kernel = kernelBuilder.Build();

// Invoke a Semantic Kernel function
var result = await kernel.InvokePromptAsync(
    "What is the weather in Seattle and do I have any meetings today?");

Console.WriteLine(result);
```

### Native Plugin Definition for SK

```csharp
public class WeatherPlugin
{
    [KernelFunction("get_current_weather")]
    [Description("Get the current weather for a city.")]
    public async Task<string> GetWeatherAsync(
        [Description("The city name")] string city)
    {
        // Call real weather API
        return $"72F, sunny in {city}";
    }
}
```

### Official SDK + Semantic Kernel

```csharp
using Anthropic;

IChatClient CreateChatClient(IServiceProvider _)
    => new AnthropicClient()
        .AsIChatClient("claude-opus-4-6")
        .AsBuilder()
        .UseFunctionInvocation()
        .Build();

var kernelBuilder = Kernel.CreateBuilder();
kernelBuilder.Services.AddSingleton(CreateChatClient);
var kernel = kernelBuilder.Build();
```

## Feature Availability Matrix

| Feature | Official SDK (`Anthropic`) | Unofficial SDK (`Anthropic.SDK`) |
|---------|--------------------------|----------------------------------|
| IChatClient | `AsIChatClient()` | `.Messages` directly |
| Tool use | `AIFunctionFactory` + `UseFunctionInvocation()` | Same |
| Extended thinking | Via stream aggregation | `ThinkingParameters` |
| Token counting | Not exposed | `CountMessageTokensAsync()` |
| Semantic Kernel | Via IChatClient bridge | Documented examples |
| MCP | Via `IChatClient` + `McpClient` | Via `IChatClient` + `McpClient` |
| AWS Bedrock | `Anthropic.Bedrock` package | Not available |
| Azure Foundry | `Anthropic.Foundry` package | Not available |
| Programmatic tool calling | Raw HTTP (not SDK-wrapped) | Raw HTTP (not SDK-wrapped) |
