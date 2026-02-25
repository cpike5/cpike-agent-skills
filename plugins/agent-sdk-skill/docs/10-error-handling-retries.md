# Error Handling and Retries

## Exception Hierarchy

All SDK exceptions derive from `AnthropicException`.

| HTTP Status | Exception Class | Common Cause |
|-------------|----------------|--------------|
| 400 | `AnthropicBadRequestException` | Malformed request, invalid model |
| 401 | `AnthropicUnauthorizedException` | Invalid or missing API key |
| 403 | `AnthropicForbiddenException` | API key lacks permission |
| 404 | `AnthropicNotFoundException` | Model or resource not found |
| 422 | `AnthropicUnprocessableEntityException` | Valid JSON but semantically wrong |
| 429 | `AnthropicRateLimitException` | Too many requests |
| 5xx | `Anthropic5xxException` | Anthropic server error |
| — | `AnthropicException` | Base class; connection errors, timeouts |

## Basic Error Handling

```csharp
try
{
    var message = await client.Messages.Create(parameters);
    return ExtractText(message.Content);
}
catch (AnthropicRateLimitException ex)
{
    _logger.LogWarning("Rate limited. Retry after: {RetryAfter}", ex.RetryAfter);
    throw;
}
catch (AnthropicUnauthorizedException)
{
    _logger.LogError("Invalid API key. Check ANTHROPIC_API_KEY configuration.");
    throw;
}
catch (Anthropic5xxException ex)
{
    _logger.LogError(ex, "Anthropic server error {StatusCode}", ex.StatusCode);
    throw;
}
catch (AnthropicBadRequestException ex)
{
    _logger.LogError("Bad request: {Message}", ex.Message);
    throw; // Don't retry -- fix the request
}
catch (AnthropicException ex)
{
    _logger.LogError(ex, "Anthropic error");
    throw;
}
```

## Built-in Retries

The SDK automatically retries **2 times** with exponential backoff for:

- Connection errors / timeouts
- `408` Request Timeout
- `409` Conflict
- `429` Rate Limit
- `5xx` Server Errors

Configuring retries:

```csharp
// Client-wide retry count
AnthropicClient client = new() { MaxRetries = 5 };

// Per-request override
var message = await client
    .WithOptions(options => options with { MaxRetries = 0 })  // Disable retries
    .Messages.Create(parameters);
```

## Polly Integration (Circuit Breaker)

For production agents, add a circuit breaker to prevent cascade failures when Anthropic is degraded:

```csharp
using Polly;
using Polly.CircuitBreaker;

// In DI setup
services.AddSingleton<ResiliencePipeline>(sp =>
    new ResiliencePipelineBuilder()
        .AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(2),
            BackoffType = DelayBackoffType.Exponential,
            ShouldHandle = new PredicateBuilder()
                .Handle<AnthropicRateLimitException>()
                .Handle<Anthropic5xxException>()
        })
        .AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            SamplingDuration = TimeSpan.FromSeconds(30),
            MinimumThroughput = 5,
            BreakDuration = TimeSpan.FromSeconds(60),
            ShouldHandle = new PredicateBuilder()
                .Handle<Anthropic5xxException>()
        })
        .Build()
);

// Usage in agent service
public class ResilientAgentService(
    AnthropicClient client,
    ResiliencePipeline pipeline,
    ILogger<ResilientAgentService> logger)
{
    public async Task<string> RunAsync(MessageCreateParams parameters)
    {
        return await pipeline.ExecuteAsync(async ct =>
        {
            var message = await client.Messages.Create(parameters);
            return ExtractText(message.Content);
        });
    }
}
```

## Graceful Degradation in Agentic Loops

When a tool throws an exception inside an agentic loop, return the error as a `tool_result` with `is_error: true` rather than crashing the loop. Claude can then decide how to recover.

```csharp
public async Task<object> ExecuteToolSafely(string toolUseId, string toolName, JsonElement input)
{
    try
    {
        var result = await _toolHandlers[toolName](input);
        return new
        {
            type = "tool_result",
            tool_use_id = toolUseId,
            content = result
        };
    }
    catch (Exception ex)
    {
        _logger.LogWarning(ex, "Tool {ToolName} failed", toolName);
        return new
        {
            type = "tool_result",
            tool_use_id = toolUseId,
            content = $"Tool execution failed: {ex.Message}. Please try a different approach.",
            is_error = true
        };
    }
}
```

Full agentic loop with graceful degradation:

```csharp
public async Task<string> RunAgentLoopAsync(string userPrompt, int maxIterations = 10)
{
    var messages = new List<Message>
    {
        new() { Role = Role.User, Content = userPrompt }
    };

    for (int i = 0; i < maxIterations; i++)
    {
        var parameters = _baseParams with { Messages = messages.ToArray() };

        Message response;
        try
        {
            response = await _client.Messages.Create(parameters);
        }
        catch (AnthropicRateLimitException)
        {
            // SDK already retried — surface to caller for higher-level handling
            throw;
        }
        catch (AnthropicException ex) when (i < maxIterations - 1)
        {
            _logger.LogError(ex, "API error on iteration {Iteration}", i);
            throw;
        }

        messages.Add(new() { Role = Role.Assistant, Content = response.Content });

        if (response.StopReason == "end_turn")
            return ExtractText(response.Content);

        if (response.StopReason == "tool_use")
        {
            var toolResults = new List<object>();

            foreach (var block in response.Content)
            {
                if (block.TryPickToolUse(out var toolUse))
                {
                    // Execute tool with error containment
                    var result = await ExecuteToolSafely(
                        toolUse.Id, toolUse.Name, toolUse.Input);
                    toolResults.Add(result);
                }
            }

            messages.Add(new()
            {
                Role = Role.User,
                Content = toolResults
            });
        }
    }

    _logger.LogWarning("Agent reached max iterations ({Max})", maxIterations);
    return "Max iterations reached without a final answer.";
}
```

## Timeout Configuration

```csharp
// Client-wide timeout
AnthropicClient client = new() { Timeout = TimeSpan.FromSeconds(120) };

// Per-request timeout (streaming agents often need longer timeouts)
var message = await client
    .WithOptions(options => options with { Timeout = TimeSpan.FromMinutes(5) })
    .Messages.Create(parameters);
```

## What Not to Retry

| Exception | Action |
|-----------|--------|
| `AnthropicBadRequestException` | Fix the request -- retrying is pointless |
| `AnthropicUnauthorizedException` | Fix the API key -- retrying is pointless |
| `AnthropicForbiddenException` | Check permissions -- retrying is pointless |
| `AnthropicNotFoundException` | Wrong model or endpoint -- fix the config |
| `AnthropicRateLimitException` | Retry with backoff (SDK handles automatically) |
| `Anthropic5xxException` | Retry with backoff (SDK handles automatically) |
| Tool execution error | Return as `is_error` tool result -- let Claude recover |

## Structured Logging Pattern

Log enough context to debug failures in production:

```csharp
catch (AnthropicException ex)
{
    _logger.LogError(ex,
        "Anthropic API error. Model={Model} InputTokens={InputTokens} Iteration={Iteration}",
        parameters.Model,
        _lastInputTokens,
        _currentIteration);
    throw;
}
```
