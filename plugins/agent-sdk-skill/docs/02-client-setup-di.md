# Client Setup & DI Registration

## AnthropicClient Instantiation

```csharp
using Anthropic;

// Option 1: Environment variables (recommended)
// Reads ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL
AnthropicClient client = new();

// Option 2: Explicit API key
AnthropicClient client = new() { ApiKey = "sk-..." };

// Option 3: Combination (env vars merged with overrides)
AnthropicClient client = new() { ApiKey = "sk-...", BaseUrl = "https://custom.endpoint.com" };
```

## Authentication

| Property | Environment Variable | Required | Default |
|----------|---------------------|----------|---------|
| `ApiKey` | `ANTHROPIC_API_KEY` | No | — |
| `AuthToken` | `ANTHROPIC_AUTH_TOKEN` | No | — |
| `BaseUrl` | `ANTHROPIC_BASE_URL` | Yes | `https://api.anthropic.com` |

**Never hardcode API keys in source code.** Use environment variables, user secrets, or a vault.

## IChatClient via AsIChatClient()

The official SDK exposes `IChatClient` from `Microsoft.Extensions.AI.Abstractions`:

```csharp
using Anthropic;
using Microsoft.Extensions.AI;

IChatClient chatClient = new AnthropicClient()
    .AsIChatClient("claude-sonnet-4-5-20250929")
    .AsBuilder()
    .UseFunctionInvocation()  // Enables automatic tool call loop
    .Build();
```

**Key:** `UseFunctionInvocation()` makes the client automatically execute tools and feed results back to Claude without you writing the loop.

## DI Registration (Recommended)

```csharp
// Program.cs or Startup.cs
services.AddSingleton<AnthropicClient>(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    return new AnthropicClient() { ApiKey = config["Anthropic:ApiKey"] };
});

services.AddSingleton<IChatClient>(sp =>
{
    var anthropicClient = sp.GetRequiredService<AnthropicClient>();
    return anthropicClient
        .AsIChatClient("claude-sonnet-4-5-20250929")
        .AsBuilder()
        .UseFunctionInvocation()
        .Build();
});
```

**Register both as Singleton.** AnthropicClient is thread-safe and manages its own HttpClient. IChatClient wraps it and should also be singleton.

## DI with IOptions Pattern

```csharp
public class AnthropicOptions
{
    public string ApiKey { get; set; } = string.Empty;
    public string Model { get; set; } = "claude-sonnet-4-5-20250929";
    public int MaxRetries { get; set; } = 2;
}

// Registration
services.Configure<AnthropicOptions>(config.GetSection("Anthropic"));

services.AddSingleton<AnthropicClient>(sp =>
{
    var options = sp.GetRequiredService<IOptions<AnthropicOptions>>().Value;
    return new AnthropicClient() { ApiKey = options.ApiKey, MaxRetries = options.MaxRetries };
});

services.AddSingleton<IChatClient>(sp =>
{
    var options = sp.GetRequiredService<IOptions<AnthropicOptions>>().Value;
    var client = sp.GetRequiredService<AnthropicClient>();
    return client
        .AsIChatClient(options.Model)
        .AsBuilder()
        .UseFunctionInvocation()
        .Build();
});
```

```json
// appsettings.json
{
  "Anthropic": {
    "ApiKey": "",
    "Model": "claude-sonnet-4-5-20250929",
    "MaxRetries": 3
  }
}
```

## Temporary Configuration Override

Override settings per-request without changing the client:

```csharp
var message = await client
    .WithOptions(options =>
        options with
        {
            BaseUrl = "https://example.com",
            Timeout = TimeSpan.FromSeconds(42),
        }
    )
    .Messages.Create(parameters);
```

## Retry Configuration

```csharp
// Global: set on client
AnthropicClient client = new() { MaxRetries = 5 };

// Per-request override
var message = await client
    .WithOptions(options => options with { MaxRetries = 3 })
    .Messages.Create(parameters);
```

Built-in retries cover: connection errors, 408, 409, 429, 5xx (exponential backoff).

## Microsoft.Extensions.AI Integration

`IChatClient` is the standard interface from `Microsoft.Extensions.AI.Abstractions`. Benefits:

| Feature | Description |
|---------|-------------|
| Provider-agnostic | Same interface for OpenAI, Anthropic, local models |
| Middleware pipeline | `AsBuilder()` adds logging, caching, function invocation |
| MCP integration | Pass MCP tools directly as `ChatOptions.Tools` |
| Semantic Kernel | IChatClient plugs into SK kernel |

## Agent Service Pattern

```csharp
public class AgentService
{
    private readonly IChatClient _chatClient;
    private readonly ILogger<AgentService> _logger;

    public AgentService(IChatClient chatClient, ILogger<AgentService> logger)
    {
        _chatClient = chatClient;
        _logger = logger;
    }

    public async Task<string> ProcessAsync(string prompt, IEnumerable<AITool> tools)
    {
        var options = new ChatOptions { Tools = tools.ToList() };
        var response = await _chatClient.GetResponseAsync(prompt, options);
        return response.Message.Text ?? "";
    }
}
```

## Multi-Cloud Setup

```bash
# AWS Bedrock
dotnet add package Anthropic.Bedrock

# Microsoft Foundry (Azure)
dotnet add package Anthropic.Foundry
```

Client instantiation follows the same pattern — refer to cloud-specific package docs for auth configuration.
