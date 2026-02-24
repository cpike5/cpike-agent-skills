# Elastic APM — Native .NET Agent

Reference for the Elastic APM native .NET agent. Covers package selection, setup,
auto-instrumentation, manual instrumentation (DI-first), distributed tracing, error
capture, and agent configuration.

---

## NuGet Packages

| Package | When to Use |
|---|---|
| `Elastic.Apm.NetCoreAll` | Full auto-instrumentation. Instruments HTTP, EF Core, gRPC, Redis, and more with one call. Recommended for most applications. |
| `Elastic.Apm.AspNetCore` | Lighter option — ASP.NET Core middleware only. Add individual sub-packages (`Elastic.Apm.EntityFrameworkCore`, `Elastic.Apm.GrpcClient`) as needed. |

Use `Elastic.Apm.NetCoreAll` unless you have a reason to control exactly which integrations are active.

---

## Program.cs Setup

### Full Auto-Instrumentation (`NetCoreAll`)

```csharp
var builder = WebApplication.CreateBuilder(args);

// Registers ITracer in DI and enables all auto-instrumentation.
builder.Services.AddAllElasticApm();

var app = builder.Build();

// Activates the ASP.NET Core request tracking middleware.
app.UseAllElasticApm();

app.Run();
```

`AddAllElasticApm()` registers `ITracer` in the DI container, which is the interface
you inject into services. `UseAllElasticApm()` adds the middleware that creates a
transaction for every incoming HTTP request.

### Lighter Setup (`AspNetCore` + selective packages)

```csharp
builder.Services.AddElasticApm(
    new HttpDiagnosticsSubscriber(),
    new EfCoreDiagnosticsSubscriber());

app.UseElasticApm(builder.Configuration);
```

---

## What Auto-Instrumentation Captures

When using `Elastic.Apm.NetCoreAll`, the following are captured automatically with no
additional code:

| Signal | Detail |
|---|---|
| Incoming HTTP requests | Creates a transaction per request; captures method, URL, status code, duration |
| Outgoing HTTP calls | Creates a child span; requires `IHttpClientFactory` or `HttpClient` via DI |
| EF Core queries | Creates a span per DB round-trip; captures SQL statement (configurable) |
| gRPC calls (client + server) | Creates transactions and spans for gRPC methods |
| Redis commands (StackExchange.Redis) | Creates a span per command |
| Azure Service Bus | Creates spans for send/receive (requires `Elastic.Apm.Azure.ServiceBus`) |
| Elasticsearch client | Captured via OpenTelemetry bridge or native APM client |

Distributed trace context (W3C `traceparent` header) is injected and extracted
automatically for all outgoing and incoming HTTP requests.

---

## DI-First: Injecting `ITracer`

This is the correct pattern for all application services. Constructor-inject `ITracer`
— do not call `Agent.Tracer` from service classes.

```csharp
using Elastic.Apm.Api;

public class OrderService
{
    private readonly ITracer _tracer;
    private readonly IOrderRepository _repository;

    public OrderService(ITracer tracer, IOrderRepository repository)
    {
        _tracer = tracer;
        _repository = repository;
    }

    public async Task<Order> ProcessOrderAsync(int orderId)
    {
        // CurrentTransaction is set automatically by the APM middleware for HTTP requests.
        // StartSpan returns null if there is no active transaction — always null-check.
        var span = _tracer.CurrentTransaction?.StartSpan(
            "ProcessOrder",
            ApiConstants.TypeDb,
            ApiConstants.SubtypeElasticsearch);

        try
        {
            var order = await _repository.GetByIdAsync(orderId);
            span?.SetLabel("order.id", orderId);
            span?.SetLabel("order.status", order.Status.ToString());
            return order;
        }
        catch (Exception ex)
        {
            span?.CaptureException(ex);
            throw;
        }
        finally
        {
            span?.End(); // Always end in finally — never skip this.
        }
    }
}
```

`ITracer` is available in DI after calling `AddAllElasticApm()`. No additional
registration is needed.

---

## Static Fallback: `Agent.Tracer`

Use `Agent.Tracer` only when the DI container is not available: startup code, static
utility methods, or `Program.cs` before `Build()` is called.

```csharp
// Acceptable: startup code outside DI
public static class StartupDiagnostics
{
    public static void RecordStartup(string version)
    {
        // Agent.Tracer can be null if the agent has not been initialized.
        var tracer = Agent.Tracer;
        if (tracer == null) return;

        var transaction = tracer.StartTransaction("ApplicationStartup", ApiConstants.TypeRequest);
        try
        {
            transaction.SetLabel("app.version", version);
        }
        finally
        {
            transaction.End();
        }
    }
}
```

Never use `Agent.Tracer` in a class that is already in the DI container. If a service
is registered with DI, inject `ITracer` instead.

---

## Manual Transactions

Create a manual transaction for work that runs outside an HTTP request (background
jobs, console commands, message consumers).

```csharp
public class ReportGenerationJob
{
    private readonly ITracer _tracer;

    public ReportGenerationJob(ITracer tracer)
    {
        _tracer = tracer;
    }

    public async Task RunAsync(string reportType)
    {
        // Name and type follow APM naming conventions — no IDs in the name.
        var transaction = _tracer.StartTransaction(
            $"GenerateReport/{reportType}",
            ApiConstants.TypeRequest);

        try
        {
            transaction.SetLabel("report.type", reportType);
            await GenerateAsync(reportType);
            transaction.Result = "success";
        }
        catch (Exception ex)
        {
            transaction.CaptureException(ex);
            transaction.Result = "error";
            throw;
        }
        finally
        {
            transaction.End(); // Required. Omitting this leaks memory and corrupts the trace tree.
        }
    }
}
```

---

## Manual Spans

Spans represent a unit of work within a transaction. Always null-check
`CurrentTransaction` before starting a span — it is null when no transaction is active
(e.g., background threads that do not create their own transaction).

```csharp
public async Task<SearchResult> SearchCatalogAsync(string query)
{
    // Guard: CurrentTransaction is null outside an active transaction context.
    var span = _tracer.CurrentTransaction?.StartSpan(
        "CatalogSearch",
        ApiConstants.TypeDb,
        ApiConstants.SubtypeElasticsearch,
        ApiConstants.ActionQuery);

    try
    {
        var result = await _searchClient.SearchAsync(query);
        span?.SetLabel("search.hits", result.Total);
        return result;
    }
    catch (Exception ex)
    {
        span?.CaptureException(ex);
        throw;
    }
    finally
    {
        span?.End(); // Always in finally, even if span is null (the null-safe call is safe here).
    }
}
```

### Built-in Type/Subtype Constants (`ApiConstants`)

| Constant | Value |
|---|---|
| `ApiConstants.TypeRequest` | `"request"` |
| `ApiConstants.TypeDb` | `"db"` |
| `ApiConstants.TypeExternal` | `"external"` |
| `ApiConstants.SubtypeHttp` | `"http"` |
| `ApiConstants.SubtypeElasticsearch` | `"elasticsearch"` |
| `ApiConstants.ActionQuery` | `"query"` |
| `ApiConstants.ActionExec` | `"exec"` |

---

## Proper Disposal: try/finally Is Mandatory

Elastic APM does not implement `IDisposable` on transactions and spans. There is no
`using` block. The `End()` call is the only way to close them.

```csharp
// CORRECT
var span = _tracer.CurrentTransaction?.StartSpan("DoWork", ApiConstants.TypeRequest);
try
{
    await DoWorkAsync();
}
finally
{
    span?.End(); // Runs whether DoWorkAsync throws or not.
}

// WRONG — if DoWorkAsync throws, span.End() is never called.
var span = _tracer.CurrentTransaction?.StartSpan("DoWork", ApiConstants.TypeRequest);
await DoWorkAsync();
span?.End(); // Unreachable on exception.
```

Unclosed spans corrupt the trace tree in Kibana and cause parent transactions to
appear as incomplete.

---

## Custom Context and Labels

### Labels (searchable key-value metadata)

Labels are indexed and appear in the Kibana APM UI. Keep cardinality low — never
use user IDs, order IDs, or GUIDs as label values.

```csharp
transaction.SetLabel("tenant", tenantSlug);           // string
transaction.SetLabel("feature.flag.enabled", true);   // bool
transaction.SetLabel("item.count", itemCount);        // int/double
```

Labels are available on both transactions and spans.

### Custom Context

```csharp
// Set structured custom context (not indexed, but visible in trace detail).
transaction.Custom["workflow"] = "checkout";
transaction.Custom["experiment"] = "new-pricing-v2";
```

### Capturing Exceptions

```csharp
catch (Exception ex)
{
    // Attaches the exception to the transaction/span and marks it as failed.
    transaction.CaptureException(ex);
    // or on a span:
    span?.CaptureException(ex);
    throw;
}
```

`CaptureException` sets the outcome to `Failure` and records the exception stack
trace in the APM event. Always call it before rethrowing.

---

## Distributed Tracing

### How It Works

Elastic APM implements the W3C TraceContext specification. When a transaction is
active, outgoing HTTP requests automatically include a `traceparent` header. The
receiving service reads this header and creates a child transaction linked to the
same trace.

No additional configuration is required when using `IHttpClientFactory`.

```csharp
// This outgoing request automatically carries the traceparent header.
// The downstream service's APM agent reads it and links its transaction to this trace.
public class CatalogClient
{
    private readonly HttpClient _http;

    public CatalogClient(HttpClient http)
    {
        _http = http; // Registered via IHttpClientFactory — header propagation is automatic.
    }

    public async Task<Product> GetProductAsync(int id)
    {
        return await _http.GetFromJsonAsync<Product>($"/api/products/{id}");
    }
}
```

### Cross-Service Correlation

All services involved in the same originating request share a `trace.id`. In Kibana
APM, the distributed trace waterfall shows every span across every service in a
single view.

For non-HTTP transports (message queues, gRPC background consumers), manually
propagate the trace context:

```csharp
// Producer: inject traceparent into message headers
var traceParent = DistributedTracingData.BuildString(
    _tracer.CurrentTransaction?.TraceId,
    _tracer.CurrentTransaction?.Id,
    _tracer.CurrentTransaction?.IsSampled ?? false);

message.Headers.Add("traceparent", traceParent);

// Consumer: restore trace context when starting the transaction
var incomingTraceData = DistributedTracingData.TryDeserializeFromString(
    message.Headers["traceparent"]);

var transaction = _tracer.StartTransaction(
    "ProcessMessage",
    ApiConstants.TypeRequest,
    incomingTraceData); // Links this transaction to the upstream trace.
```

---

## Agent Configuration

Configuration is read from environment variables, `appsettings.json`, or both.
Environment variables take precedence.

### Environment Variables

| Variable | Description | Example |
|---|---|---|
| `ELASTIC_APM_SERVER_URL` | APM Server endpoint | `http://apm-server:8200` |
| `ELASTIC_APM_SERVICE_NAME` | Service name in APM UI | `OrderService` |
| `ELASTIC_APM_ENVIRONMENT` | Deployment environment | `production` |
| `ELASTIC_APM_SECRET_TOKEN` | Auth token for APM Server | `abc123` |
| `ELASTIC_APM_API_KEY` | API key auth (alternative to secret token) | `base64key==` |
| `ELASTIC_APM_TRANSACTION_SAMPLE_RATE` | Sampling rate (0.0–1.0) | `0.1` |
| `ELASTIC_APM_LOG_LEVEL` | Agent log verbosity | `Warning` |
| `ELASTIC_APM_CAPTURE_BODY` | Capture HTTP request body | `off` / `errors` / `all` |
| `ELASTIC_APM_SANITIZE_FIELD_NAMES` | Field names to redact | `password,token,secret` |
| `ELASTIC_APM_GLOBAL_LABELS` | Labels applied to every event | `region=us-east` |

### appsettings.json

```json
{
  "ElasticApm": {
    "ServerUrl": "http://apm-server:8200",
    "ServiceName": "OrderService",
    "Environment": "production",
    "TransactionSampleRate": 1.0,
    "LogLevel": "Warning",
    "CaptureBody": "off",
    "SanitizeFieldNames": ["password", "authorization", "token"]
  }
}
```

The agent reads the `ElasticApm` section automatically when you call `AddAllElasticApm()`.

### Sampling

```bash
# Sample 10% of transactions in production.
ELASTIC_APM_TRANSACTION_SAMPLE_RATE=0.1

# Sample everything in development/staging.
ELASTIC_APM_TRANSACTION_SAMPLE_RATE=1.0
```

Sampling is head-based. When a transaction is not sampled, its spans are not
collected, but the transaction still appears in APM with duration and outcome recorded.
Child services respect the sampling decision from the incoming `traceparent` header —
you do not need to configure the same rate on every service.

---

## Common Mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| `span.End()` not in `finally` | Span is never closed on exception; trace tree is corrupted | Always use `try/finally { span?.End(); }` |
| Not null-checking `CurrentTransaction` | `NullReferenceException` in background threads | Guard with `?.`: `_tracer.CurrentTransaction?.StartSpan(...)` |
| Using `Agent.Tracer` in DI services | Bypasses the registered `ITracer`; harder to test | Inject `ITracer` via constructor |
| High-cardinality transaction names | Cardinality explosion in APM storage; unusable aggregations | Use route templates, not resolved IDs |
| Forgetting `CaptureException` before `End()` | Error is not linked to the span; outcome stays `Unknown` | Call `CaptureException` in the `catch` block, before `finally` |
| Skipping `UseAllElasticApm()` | HTTP requests are not tracked; no transactions appear in APM | Always call both `AddAllElasticApm()` and `UseAllElasticApm()` |
