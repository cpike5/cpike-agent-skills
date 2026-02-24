# Instrumentation Patterns — .NET 8+

Practical patterns for instrumenting ASP.NET Core applications. All examples use constructor injection. Target framework: .NET 8+.

---

## Middleware Instrumentation

Custom middleware is the right place to start a root span, attach request-scoped properties to `LogContext`, and ensure cleanup runs for every request regardless of what happens downstream.

```csharp
public class TracingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<TracingMiddleware> _logger;
    private readonly ActivitySource _activitySource;

    public TracingMiddleware(
        RequestDelegate next,
        ILogger<TracingMiddleware> logger,
        ActivitySource activitySource)
    {
        _next = next;
        _logger = logger;
        _activitySource = activitySource;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Start a span — returns null when no listener is registered (safe to proceed)
        using var activity = _activitySource.StartActivity(
            $"{context.Request.Method} {context.Request.Path}",
            ActivityKind.Server);

        // Attach structured properties for every log event in this request
        using var logScope = LogContext.PushProperty("TraceId", activity?.TraceId.ToString());

        activity?.SetTag("http.method", context.Request.Method);
        activity?.SetTag("http.url", context.Request.Path);

        try
        {
            await _next(context);

            activity?.SetTag("http.status_code", context.Response.StatusCode);

            if (context.Response.StatusCode >= 500)
                activity?.SetStatus(ActivityStatusCode.Error, $"HTTP {context.Response.StatusCode}");
        }
        catch (Exception ex)
        {
            // Capture on the span BEFORE the using block disposes it
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            _logger.LogError(ex, "Unhandled exception for {RequestMethod} {RequestPath}",
                context.Request.Method, context.Request.Path);
            throw;
        }
    }
}

// Registration in Program.cs
app.UseMiddleware<TracingMiddleware>();
```

Register `ActivitySource` as a singleton:

```csharp
builder.Services.AddSingleton(new ActivitySource("MyApp"));
```

---

## Action Filter Instrumentation

Action filters run inside routing, giving you access to `ActionDescriptor`, route values, and the resolved controller/action name. Use them for per-action spans that sit as children of the middleware root span.

```csharp
public class ActionTracingFilter : IAsyncActionFilter
{
    private readonly ILogger<ActionTracingFilter> _logger;
    private readonly ActivitySource _activitySource;

    public ActionTracingFilter(
        ILogger<ActionTracingFilter> logger,
        ActivitySource activitySource)
    {
        _logger = logger;
        _activitySource = activitySource;
    }

    public async Task OnActionExecutionAsync(
        ActionExecutingContext context,
        ActionExecutionDelegate next)
    {
        var descriptor = context.ActionDescriptor as ControllerActionDescriptor;
        var spanName = $"{descriptor?.ControllerName}.{descriptor?.ActionName}";

        using var activity = _activitySource.StartActivity(spanName, ActivityKind.Internal);
        activity?.SetTag("controller", descriptor?.ControllerName);
        activity?.SetTag("action", descriptor?.ActionName);

        ActionExecutedContext result;
        try
        {
            result = await next();
        }
        catch (Exception ex)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            throw;
        }

        if (result.Exception != null && !result.ExceptionHandled)
        {
            activity?.SetStatus(ActivityStatusCode.Error, result.Exception.Message);
            activity?.RecordException(result.Exception);
        }
    }
}

// Registration — applies globally
builder.Services.AddControllers(options =>
    options.Filters.Add<ActionTracingFilter>());
```

---

## Health Check Exclusion

Health and readiness probes from load balancers generate constant traffic. Exclude them from APM transactions and Serilog request logs to avoid polluting traces and skewing latency statistics.

### Serilog request log exclusion

```csharp
app.UseSerilogRequestLogging(options =>
{
    options.MessageTemplate =
        "HTTP {RequestMethod} {RequestPath} responded {StatusCode} in {Elapsed:0.0000} ms";

    // Return false to suppress the log event for health/ready paths
    options.GetLevel = (httpContext, elapsed, ex) =>
    {
        if (httpContext.Request.Path.StartsWithSegments("/health") ||
            httpContext.Request.Path.StartsWithSegments("/ready"))
            return LogEventLevel.Verbose; // Verbose is filtered out by default minimum level

        return ex != null || httpContext.Response.StatusCode >= 500
            ? LogEventLevel.Error
            : LogEventLevel.Information;
    };
});
```

### OpenTelemetry sampler exclusion

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation(options =>
        {
            options.Filter = httpContext =>
                !httpContext.Request.Path.StartsWithSegments("/health") &&
                !httpContext.Request.Path.StartsWithSegments("/ready");
        }));
```

---

## Sampling Strategies

Sampling controls what fraction of traces are recorded and exported. Apply it at the OpenTelemetry SDK level.

### Head-based rate sampling (simplest)

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .SetSampler(new TraceIdRatioBasedSampler(0.1))); // 10% of traces
```

### Conditional sampler — 100% errors, 10% success

This is the recommended production pattern: never drop error traces, sample normal traffic.

```csharp
public sealed class ErrorAlwaysSampler : Sampler
{
    private readonly double _successRate;
    private readonly TraceIdRatioBasedSampler _ratioSampler;

    public ErrorAlwaysSampler(double successSampleRate = 0.10)
    {
        _successRate = successSampleRate;
        _ratioSampler = new TraceIdRatioBasedSampler(successSampleRate);
    }

    public override SamplingResult ShouldSample(in SamplingParameters parameters)
    {
        // Always sample if there is an error tag on the root span
        foreach (var tag in parameters.Tags)
        {
            if (tag.Key == "error" && tag.Value is true)
                return new SamplingResult(SamplingDecision.RecordAndSample);

            if (tag.Key == "http.status_code" && tag.Value is int status && status >= 500)
                return new SamplingResult(SamplingDecision.RecordAndSample);
        }

        // Delegate normal traffic to ratio sampler
        return _ratioSampler.ShouldSample(in parameters);
    }
}

// Registration
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .SetSampler(new ErrorAlwaysSampler(successSampleRate: 0.10)));
```

---

## Performance Overhead

| Instrumentation | Typical overhead | Notes |
|----------------|-----------------|-------|
| `ActivitySource.StartActivity()` | ~200–500 ns | Near-zero when no listener registered (returns null immediately) |
| `LogContext.PushProperty()` | ~1–2 µs | Allocates a small linked-list node per property |
| OTel SDK span creation | ~2–5 µs per span | Includes tag storage and parent resolution |
| Elastic APM span | ~5–15 µs per span | Includes serialization buffer allocation |
| `ILogger` log event (filtered out) | ~50–100 ns | Level check avoids allocation |
| `ILogger` log event (written) | ~2–10 µs | Includes message template parsing and sink dispatch |

**When to worry:** Instrumentation overhead matters in sub-millisecond hot paths (tight loops, in-memory caches, serializers). For network-bound I/O (HTTP, SQL, message queues), instrumentation cost is irrelevant — the I/O is 3–4 orders of magnitude slower.

**Practical rule:** Do not add per-item spans inside loops over large collections. Instrument the operation as a whole; add item count as a tag.

---

## Background Service Tracing

`BackgroundService` and `IHostedService` run outside the ASP.NET Core request pipeline. There is no ambient `Activity.Current` unless you create one. Always start a new root activity per logical job execution.

```csharp
public class OrderProcessingWorker : BackgroundService
{
    private readonly ILogger<OrderProcessingWorker> _logger;
    private readonly ActivitySource _activitySource;
    private readonly IServiceScopeFactory _scopeFactory;

    public OrderProcessingWorker(
        ILogger<OrderProcessingWorker> logger,
        ActivitySource activitySource,
        IServiceScopeFactory scopeFactory)
    {
        _logger = logger;
        _activitySource = activitySource;
        _scopeFactory = scopeFactory;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            await ProcessBatchAsync(stoppingToken);
            await Task.Delay(TimeSpan.FromSeconds(30), stoppingToken);
        }
    }

    private async Task ProcessBatchAsync(CancellationToken cancellationToken)
    {
        // Start a root activity — this is the trace root for this job run
        using var activity = _activitySource.StartActivity(
            "OrderProcessingWorker.ProcessBatch",
            ActivityKind.Internal);

        using var logScope = LogContext.PushProperty("TraceId", activity?.TraceId.ToString());

        _logger.LogInformation("Starting order processing batch");

        try
        {
            await using var scope = _scopeFactory.CreateAsyncScope();
            var service = scope.ServiceProvider.GetRequiredService<IOrderService>();
            var count = await service.ProcessPendingOrdersAsync(cancellationToken);

            activity?.SetTag("orders.processed", count);
            _logger.LogInformation("Batch complete. Processed {OrderCount} orders", count);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            _logger.LogError(ex, "Order processing batch failed");
        }
    }
}
```

### Propagating trace context from a message queue

When a background worker consumes a message that was produced by another service, restore the trace context from the message headers so the worker span links to the originating trace.

```csharp
private async Task ProcessMessageAsync(Message message, CancellationToken cancellationToken)
{
    // Extract W3C traceparent from the message headers
    ActivityContext parentContext = default;
    if (message.Headers.TryGetValue("traceparent", out var traceparent))
    {
        ActivityContext.TryParse(traceparent, null, out parentContext);
    }

    using var activity = _activitySource.StartActivity(
        "OrderQueue.ProcessMessage",
        ActivityKind.Consumer,
        parentContext);

    // ... process message
}
```

---

## IHttpClientFactory Tracing

When `AddOpenTelemetry()` includes `AddHttpClientInstrumentation()`, outgoing requests made via `IHttpClientFactory` are automatically instrumented with W3C `traceparent` header injection. No additional code is required for propagation.

### Automatic instrumentation setup

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddHttpClientInstrumentation(options =>
        {
            // Exclude health check pings from downstream spans
            options.FilterHttpRequestMessage = req =>
                req.RequestUri?.AbsolutePath.StartsWith("/health") != true;
        }));

builder.Services.AddHttpClient<IPaymentGatewayClient, PaymentGatewayClient>();
```

### Adding custom tags to outgoing request spans

Use `DelegatingHandler` to enrich the automatically-created span without disabling automatic instrumentation.

```csharp
public class TelemetryEnrichmentHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        // Activity.Current at this point is the auto-created HttpClient span
        Activity.Current?.SetTag("payment.service.region", "eu-west-1");

        var response = await base.SendAsync(request, cancellationToken);

        Activity.Current?.SetTag("payment.response.status", (int)response.StatusCode);
        return response;
    }
}

// Registration
builder.Services.AddHttpClient<IPaymentGatewayClient, PaymentGatewayClient>()
    .AddHttpMessageHandler<TelemetryEnrichmentHandler>();

builder.Services.AddTransient<TelemetryEnrichmentHandler>();
```

---

## EF Core Query Tracing

`AddEntityFrameworkCoreInstrumentation()` automatically captures every SQL command as a child span including the query text (configurable), duration, and table. This covers the majority of EF Core observability needs.

### Automatic setup

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddEntityFrameworkCoreInstrumentation(options =>
        {
            // Include query text — disable in production if queries may contain PII
            options.SetDbStatementForText = true;
        }));
```

### Custom spans around repository operations

Add a span at the repository boundary when you want to group multiple queries under a single named operation (e.g., "Load order with line items and inventory").

```csharp
public class OrderRepository : IOrderRepository
{
    private readonly AppDbContext _context;
    private readonly ActivitySource _activitySource;

    public OrderRepository(AppDbContext context, ActivitySource activitySource)
    {
        _context = context;
        _activitySource = activitySource;
    }

    public async Task<Order?> GetWithDetailsAsync(int orderId, CancellationToken cancellationToken)
    {
        using var activity = _activitySource.StartActivity(
            "OrderRepository.GetWithDetails",
            ActivityKind.Internal);

        activity?.SetTag("order.id", orderId);

        try
        {
            var order = await _context.Orders
                .Include(o => o.LineItems)
                .Include(o => o.Customer)
                .FirstOrDefaultAsync(o => o.Id == orderId, cancellationToken);

            activity?.SetTag("order.found", order is not null);
            return order;
        }
        catch (Exception ex)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            throw;
        }
    }
}
```

---

## Proper Resource Cleanup

Spans and activities are `IDisposable`. An unclosed span leaks memory and produces a corrupt trace tree (the span never appears to end in the APM UI).

### Using pattern (preferred)

```csharp
// Activity is ended automatically when the using block exits, even on exception
using var activity = _activitySource.StartActivity("MyOperation");
// ... work here
```

### try/finally (when using is not applicable)

Use `try/finally` when the span must outlive a single scope, or when you need to conditionally end it from multiple code paths.

```csharp
var activity = _activitySource.StartActivity("LongRunningOperation");
try
{
    await DoWorkAsync();
}
catch (Exception ex)
{
    activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
    activity?.RecordException(ex);
    throw;
}
finally
{
    // Always called, even if DoWorkAsync throws or if activity is null
    activity?.Dispose();
}
```

**Rule:** Error capture must happen in the `catch` block, before `finally` disposes the activity. Setting status after `Dispose()` has no effect.

---

## Null-Safe Patterns

`ActivitySource.StartActivity()` returns `null` when no listener is registered. `Activity.Current` is `null` when called outside an active trace. Both are expected conditions — guard against null at every access point.

```csharp
// StartActivity() — always use var + null-conditional operator
using var activity = _activitySource.StartActivity("MySpan"); // may be null
activity?.SetTag("key", "value");                             // safe
activity?.SetStatus(ActivityStatusCode.Ok);                   // safe

// Activity.Current — null outside a trace; use null-conditional throughout
var traceId = Activity.Current?.TraceId.ToString();           // returns null safely
Activity.Current?.SetTag("user.id", userId);                  // no-op when null

// Do NOT do this — NullReferenceException when no trace is active
var traceId = Activity.Current.TraceId.ToString(); // WRONG

// Null-coalescing for fallback values
var correlationId = Activity.Current?.TraceId.ToString() ?? Guid.NewGuid().ToString("N");
```

---

## Error Capture

Recording an exception on a span before ending it is what makes the span appear as an error in APM UIs. The order of operations matters: capture in `catch`, dispose in `finally`.

### OpenTelemetry (ActivitySource)

```csharp
using var activity = _activitySource.StartActivity("ProcessPayment");
try
{
    await _paymentService.ChargeAsync(order.Total, order.PaymentToken);
}
catch (PaymentDeclinedException ex)
{
    // Set error status and record exception — both are needed
    activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
    activity?.RecordException(ex);             // adds exception.* attributes to the span

    _logger.LogWarning(ex, "Payment declined for order {OrderId}", order.Id);
    throw;
}
catch (Exception ex)
{
    activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
    activity?.RecordException(ex);

    _logger.LogError(ex, "Payment service failure for order {OrderId}", order.Id);
    throw;
}
```

`RecordException(ex)` adds `exception.type`, `exception.message`, and `exception.stacktrace` as span attributes per the OpenTelemetry semantic conventions. These appear as exception events in Jaeger, Zipkin, and Elastic APM.

---

## Correlation ID Middleware

A correlation ID ties together all log events and spans for a single logical request, even across service boundaries. Generate one if the caller does not provide it, propagate it outward on responses, and push it into `LogContext` so every log event in the request carries it.

```csharp
public class CorrelationIdMiddleware
{
    private const string HeaderName = "X-Correlation-ID";

    private readonly RequestDelegate _next;

    public CorrelationIdMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context)
    {
        // Accept from caller or generate a new one
        var correlationId = context.Request.Headers[HeaderName].FirstOrDefault()
            ?? Activity.Current?.TraceId.ToString()
            ?? Guid.NewGuid().ToString("N");

        // Echo it back so callers can correlate their own logs
        context.Response.Headers[HeaderName] = correlationId;

        // Store on HttpContext for downstream access
        context.Items["CorrelationId"] = correlationId;

        // Push into Serilog's LogContext for all log events in this request
        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            // Tag the current OTel span if one is active
            Activity.Current?.SetTag("correlation.id", correlationId);

            await _next(context);
        }
    }
}

// Registration — place before routing and authentication middleware
app.UseMiddleware<CorrelationIdMiddleware>();
```

### Propagating correlation ID on outgoing HTTP calls

Register a `DelegatingHandler` that reads the ID from `IHttpContextAccessor` and forwards it:

```csharp
public class CorrelationIdForwardingHandler : DelegatingHandler
{
    private const string HeaderName = "X-Correlation-ID";
    private readonly IHttpContextAccessor _httpContextAccessor;

    public CorrelationIdForwardingHandler(IHttpContextAccessor httpContextAccessor)
        => _httpContextAccessor = httpContextAccessor;

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var correlationId = _httpContextAccessor.HttpContext?.Items["CorrelationId"] as string
            ?? Activity.Current?.TraceId.ToString();

        if (correlationId is not null)
            request.Headers.TryAddWithoutValidation(HeaderName, correlationId);

        return base.SendAsync(request, cancellationToken);
    }
}

// Registration
builder.Services.AddHttpContextAccessor();
builder.Services.AddTransient<CorrelationIdForwardingHandler>();

builder.Services.AddHttpClient<IDownstreamClient, DownstreamClient>()
    .AddHttpMessageHandler<CorrelationIdForwardingHandler>();
```

---

## See Also

- `docs/07-opentelemetry.md` — `ActivitySource`, `Activity`, `Meter` SDK setup and OTLP exporters
- `docs/06-elastic-apm.md` — `ITracer`, `ITransaction`, `ISpan` with Elastic APM native agent
- `docs/09-apm-correlation.md` — Injecting trace IDs into Serilog log events for log-trace correlation
- `docs/10-naming-conventions.md` — Span and transaction naming rules, avoiding high-cardinality names
