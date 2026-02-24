# .NET Integration Patterns

## DI Registration

### Options Class

```csharp
public class ElasticsearchOptions
{
    public const string SectionName = "Elasticsearch";

    public string Url { get; set; } = "https://localhost:9200";
    public string? ApiKey { get; set; }
    public string? CertificateFingerprint { get; set; }
    public string DefaultIndex { get; set; } = "default";
}
```

### appsettings.json

```json
{
  "Elasticsearch": {
    "Url": "https://localhost:9200",
    "ApiKey": "base64-encoded-api-key",
    "CertificateFingerprint": "AB:CD:EF:01:23:45:67:89",
    "DefaultIndex": "my-app"
  }
}
```

### IServiceCollection Extension Method

```csharp
public static class ElasticsearchServiceCollectionExtensions
{
    public static IServiceCollection AddElasticsearch(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.Configure<ElasticsearchOptions>(
            configuration.GetSection(ElasticsearchOptions.SectionName));

        services.AddSingleton<ElasticsearchClient>(sp =>
        {
            var options = sp.GetRequiredService<IOptions<ElasticsearchOptions>>().Value;

            var settings = new ElasticsearchClientSettings(new Uri(options.Url))
                .DefaultIndex(options.DefaultIndex);

            if (!string.IsNullOrEmpty(options.ApiKey))
                settings.Authentication(new ApiKey(options.ApiKey));

            if (!string.IsNullOrEmpty(options.CertificateFingerprint))
                settings.CertificateFingerprint(options.CertificateFingerprint);

            return new ElasticsearchClient(settings);
        });

        return services;
    }
}
```

**Registration in Program.cs:**

```csharp
builder.Services.AddElasticsearch(builder.Configuration);
```

- **`ElasticsearchClient` must be registered as singleton** -- it manages connection pooling, node sniffing, and thread-safe state internally
- `IOptions<ElasticsearchOptions>` enables configuration reload without restart when using `IOptionsMonitor<T>`

## Repository Pattern

### Interface

```csharp
public interface ISearchRepository<T> where T : class
{
    Task<T?> GetByIdAsync(string id, CancellationToken ct = default);
    Task<IReadOnlyCollection<T>> SearchAsync(Action<SearchRequestDescriptor<T>> configure, CancellationToken ct = default);
    Task<string> IndexAsync(T document, CancellationToken ct = default);
    Task<bool> DeleteAsync(string id, CancellationToken ct = default);
    Task<BulkResponse> BulkIndexAsync(IEnumerable<T> documents, CancellationToken ct = default);
}
```

### Implementation

```csharp
public class ElasticsearchRepository<T> : ISearchRepository<T> where T : class
{
    private readonly ElasticsearchClient _client;
    private readonly ILogger<ElasticsearchRepository<T>> _logger;

    public ElasticsearchRepository(
        ElasticsearchClient client,
        ILogger<ElasticsearchRepository<T>> logger)
    {
        _client = client;
        _logger = logger;
    }

    public async Task<T?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        var response = await _client.GetAsync<T>(id, ct);

        if (!response.IsValidResponse)
        {
            _logger.LogWarning("Get {Id} failed: {Error}", id, response.DebugInformation);
            return null;
        }

        return response.Source;
    }

    public async Task<IReadOnlyCollection<T>> SearchAsync(
        Action<SearchRequestDescriptor<T>> configure,
        CancellationToken ct = default)
    {
        var response = await _client.SearchAsync(configure, ct);

        if (!response.IsValidResponse)
        {
            _logger.LogError("Search failed: {Error}", response.DebugInformation);
            return Array.Empty<T>();
        }

        return response.Documents;
    }

    public async Task<string> IndexAsync(T document, CancellationToken ct = default)
    {
        var response = await _client.IndexAsync(document, ct);

        if (!response.IsValidResponse)
            throw new InvalidOperationException($"Index failed: {response.DebugInformation}");

        return response.Id;
    }

    public async Task<bool> DeleteAsync(string id, CancellationToken ct = default)
    {
        var response = await _client.DeleteAsync(id, ct);
        return response.IsValidResponse;
    }

    public async Task<BulkResponse> BulkIndexAsync(
        IEnumerable<T> documents,
        CancellationToken ct = default)
    {
        var response = await _client.BulkAsync(b => b.IndexMany(documents), ct);

        if (response.Errors)
        {
            foreach (var item in response.ItemsWithErrors)
                _logger.LogError("Bulk index error for {Id}: {Reason}", item.Id, item.Error?.Reason);
        }

        return response;
    }
}
```

**DI registration with per-type index resolution:**

```csharp
services.AddSingleton<ISearchRepository<Product>>(sp =>
{
    var client = sp.GetRequiredService<ElasticsearchClient>();
    var logger = sp.GetRequiredService<ILogger<ElasticsearchRepository<Product>>>();
    return new ElasticsearchRepository<Product>(client, logger);
});
```

## Error Handling

### Response Inspection

```csharp
var response = await client.SearchAsync<Product>(s => s.Index("products"));

// Primary success check
if (!response.IsValidResponse)
{
    // Server-side error (4xx/5xx with structured error body)
    if (response.ElasticsearchServerError is { } serverError)
    {
        Console.WriteLine($"Status: {serverError.Status}");
        Console.WriteLine($"Error: {serverError.Error.Type} - {serverError.Error.Reason}");
    }

    // Low-level HTTP details
    var apiCall = response.ApiCallDetails;
    Console.WriteLine($"HTTP {apiCall.HttpStatusCode}");
    Console.WriteLine($"URI: {apiCall.Uri}");

    // Full debug output (request + response bytes when EnableDebugMode is on)
    Console.WriteLine(response.DebugInformation);
}
```

### Response Check Summary

| Property | Use Case |
|----------|----------|
| `response.IsValidResponse` | **Primary check** -- `true` when HTTP 2xx and no errors |
| `response.ElasticsearchServerError` | Structured error from Elasticsearch (type, reason, status) |
| `response.ApiCallDetails` | HTTP status code, URI, request/response bytes |
| `response.DebugInformation` | Human-readable debug string (for logging) |

## Polly Retry

### Built-in Client Retries

```csharp
var settings = new ElasticsearchClientSettings(new Uri("https://localhost:9200"))
    .MaxRetries(3)
    .MaxRetryTimeout(TimeSpan.FromSeconds(60));
```

- Built-in retries handle **connection failures** and **502/503/504** responses
- Retries use the connection pool to try different nodes

### Polly for Application-Level Retry

```csharp
services.AddSingleton<ElasticsearchClient>(sp =>
{
    var options = sp.GetRequiredService<IOptions<ElasticsearchOptions>>().Value;
    var settings = new ElasticsearchClientSettings(new Uri(options.Url));
    return new ElasticsearchClient(settings);
});

services.AddResiliencePipeline("elasticsearch", builder =>
{
    builder
        .AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(1),
            BackoffType = DelayBackoffType.Exponential,
            ShouldHandle = new PredicateBuilder()
                .Handle<TransportException>()
        })
        .AddTimeout(TimeSpan.FromSeconds(30));
});
```

**Usage with `ResiliencePipeline`:**

```csharp
public class ResilientSearchService
{
    private readonly ElasticsearchClient _client;
    private readonly ResiliencePipeline _pipeline;

    public ResilientSearchService(
        ElasticsearchClient client,
        ResiliencePipelineProvider<string> pipelineProvider)
    {
        _client = client;
        _pipeline = pipelineProvider.GetPipeline("elasticsearch");
    }

    public async Task<IReadOnlyCollection<Product>> SearchAsync(string query)
    {
        var response = await _pipeline.ExecuteAsync(
            async ct => await _client.SearchAsync<Product>(s => s
                .Index("products")
                .Query(q => q.Match(m => m.Field(f => f.Name).Query(query))),
                ct),
            CancellationToken.None);

        return response.Documents;
    }
}
```

## Health Checks

### NuGet Package

```
AspNetCore.HealthChecks.Elasticsearch
```

### Basic Registration

```csharp
builder.Services.AddHealthChecks()
    .AddElasticsearch(
        sp => sp.GetRequiredService<ElasticsearchClient>(),
        name: "elasticsearch",
        tags: new[] { "ready" });
```

### Custom Health Check

```csharp
public class ElasticsearchHealthCheck : IHealthCheck
{
    private readonly ElasticsearchClient _client;

    public ElasticsearchHealthCheck(ElasticsearchClient client)
    {
        _client = client;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken ct = default)
    {
        var response = await _client.Cluster.HealthAsync(ct);

        if (!response.IsValidResponse)
            return HealthCheckResult.Unhealthy("Cluster unreachable");

        return response.Status switch
        {
            HealthStatus.Green => HealthCheckResult.Healthy("Cluster green"),
            HealthStatus.Yellow => HealthCheckResult.Degraded("Cluster yellow"),
            _ => HealthCheckResult.Unhealthy($"Cluster {response.Status}")
        };
    }
}
```

**Registration:**

```csharp
builder.Services.AddHealthChecks()
    .AddCheck<ElasticsearchHealthCheck>("elasticsearch", tags: new[] { "ready" });

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
```

## Serilog Sinks

### Official Sink: Elastic.Serilog.Sinks (Recommended)

- **NuGet**: `Elastic.Serilog.Sinks`
- Ships logs as **ECS-compliant** documents
- Writes to **data streams** (not classic indices)
- Supports buffered/durable shipping

**Code-based configuration:**

```csharp
Log.Logger = new LoggerConfiguration()
    .WriteTo.Elasticsearch(new[] { new Uri("https://localhost:9200") }, opts =>
    {
        opts.DataStream = new DataStreamName("logs", "app", "default");
        opts.BootstrapMethod = BootstrapMethod.Failure;
        opts.ConfigureChannel = channelOpts =>
        {
            channelOpts.BufferOptions = new BufferOptions
            {
                ExportMaxConcurrency = 3,
                InboundBufferMaxSize = 1000
            };
        };
    }, transport =>
    {
        transport.Authentication(new ApiKey("base64-api-key"));
    })
    .CreateLogger();
```

**appsettings.json configuration:**

```json
{
  "Serilog": {
    "Using": ["Elastic.Serilog.Sinks"],
    "WriteTo": [
      {
        "Name": "Elasticsearch",
        "Args": {
          "nodes": ["https://localhost:9200"],
          "dataStream": "logs-app-default",
          "bootstrapMethod": "Failure"
        }
      }
    ]
  }
}
```

| Feature | Detail |
|---------|--------|
| **Data stream naming** | `logs-{dataset}-{namespace}` convention |
| **BootstrapMethod** | `Failure` = fail if data stream can't be created; `Silent` = ignore; `None` = skip bootstrap |
| **ECS compliance** | Automatic -- logs are structured per Elastic Common Schema |
| **Buffering** | In-memory with configurable concurrency and buffer size |

### Community Sink: Serilog.Sinks.Elasticsearch (Archived)

- **NuGet**: `Serilog.Sinks.Elasticsearch`
- **Archived June 2024** -- no longer maintained
- Does **not** produce ECS-compliant output by default

```csharp
Log.Logger = new LoggerConfiguration()
    .WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri("https://localhost:9200"))
    {
        IndexFormat = "logs-app-{0:yyyy.MM.dd}",
        BatchAction = ElasticOpType.Create,
        AutoRegisterTemplate = true,
        NumberOfShards = 1
    })
    .CreateLogger();
```

| Limitation | Detail |
|-----------|--------|
| **No ECS** | Requires `Elastic.CommonSchema.Serilog` for ECS formatting |
| **No data streams** | Uses classic index-per-day pattern |
| **No maintenance** | Archived -- security and compatibility issues will not be fixed |

**Always use `Elastic.Serilog.Sinks` for new projects.**

## Common Mistakes

- **Registering `ElasticsearchClient` as transient or scoped** -- the client manages its own connection pool and is thread-safe; **register as singleton**
- **Not using `IOptions<T>` pattern** -- hardcoding connection strings prevents environment-specific configuration and secret management
- **Not checking `response.IsValidResponse`** -- Elasticsearch can return HTTP 200 with partial failures (bulk errors, shard failures); always inspect the response
- **Using `Serilog.Sinks.Elasticsearch` for new projects** -- the community sink was archived June 2024; use `Elastic.Serilog.Sinks` (official) instead
- **Not disposing `BulkAll` observer** -- `BulkAll` returns an `IDisposable`; wrap in `using` or call `Dispose` to avoid resource leaks
- **Swallowing exceptions without logging `DebugInformation`** -- `response.DebugInformation` contains the request/response details needed to diagnose failures; always log it on error
