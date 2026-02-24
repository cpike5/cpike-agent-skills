# OpenTelemetry for .NET

OpenTelemetry (OTel) is the vendor-neutral SDK for distributed tracing, metrics, and (experimentally) logging. In .NET, tracing is built on `System.Diagnostics.Activity` and metrics on `System.Diagnostics.Metrics` — OTel wraps these standard types with exporters and instrumentation libraries.

## NuGet Packages

```xml
<!-- Core hosting integration -->
<PackageReference Include="OpenTelemetry.Extensions.Hosting" Version="1.*" />

<!-- Auto-instrumentation -->
<PackageReference Include="OpenTelemetry.Instrumentation.AspNetCore" Version="1.*" />
<PackageReference Include="OpenTelemetry.Instrumentation.Http" Version="1.*" />

<!-- OTLP exporter (sends to Collector, Seq, Elastic, etc.) -->
<PackageReference Include="OpenTelemetry.Exporter.OpenTelemetryProtocol" Version="1.*" />

<!-- Optional: console exporter for debugging -->
<PackageReference Include="OpenTelemetry.Exporter.Console" Version="1.*" />
```

## Setup in Program.cs (.NET 8+)

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService(
            serviceName: "MyApi",
            serviceVersion: "2.1.0"))
    .WithTracing(tracing => tracing
        .AddSource(MyInstrumentation.ActivitySourceName)  // register custom source
        .AddAspNetCoreInstrumentation(options =>
        {
            options.RecordException = true;
            options.Filter = ctx => ctx.Request.Path != "/healthz";
        })
        .AddHttpClientInstrumentation()
        .AddOtlpExporter(otlp =>
        {
            otlp.Endpoint = new Uri(builder.Configuration["Otlp:Endpoint"]!);
        }))
    .WithMetrics(metrics => metrics
        .AddMeter(MyInstrumentation.MeterName)            // register custom meter
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter(otlp =>
        {
            otlp.Endpoint = new Uri(builder.Configuration["Otlp:Endpoint"]!);
        }));

// Register instrumentation helper as singleton
builder.Services.AddSingleton<MyInstrumentation>();
```

## ActivitySource — Custom Trace Spans

### Defining the Source

Define `ActivitySource` once as a singleton. The name must match what you pass to `AddSource()`.

```csharp
public sealed class MyInstrumentation : IDisposable
{
    public const string ActivitySourceName = "MyApi";
    public const string MeterName = "MyApi";

    public readonly ActivitySource ActivitySource = new(ActivitySourceName, "2.1.0");
    public readonly Meter Meter = new(MeterName, "2.1.0");

    public void Dispose()
    {
        ActivitySource.Dispose();
        Meter.Dispose();
    }
}
```

### DI Registration and Injection

```csharp
// Registration (already shown in Program.cs above)
builder.Services.AddSingleton<MyInstrumentation>();

// Injection
public class OrderService
{
    private readonly ActivitySource _source;

    public OrderService(MyInstrumentation instrumentation)
    {
        _source = instrumentation.ActivitySource;
    }
}
```

## Custom Activity Spans

### Starting an Activity

`StartActivity()` returns `null` when no listener has subscribed to the source (e.g., in tests or when OTel is disabled). Always null-check.

```csharp
public async Task<Order> ProcessOrderAsync(Guid orderId)
{
    // Always use a using block — ensures Dispose() is called, which ends the span
    using var activity = _source.StartActivity("ProcessOrder");

    // Guard: activity is null when no listener is registered
    activity?.SetTag("order.id", orderId.ToString());
    activity?.SetTag("order.source", "api");

    try
    {
        var order = await _repository.GetAsync(orderId);
        activity?.SetTag("order.status", order.Status.ToString());
        activity?.SetStatus(ActivityStatusCode.Ok);
        return order;
    }
    catch (Exception ex)
    {
        activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
        activity?.RecordException(ex);
        throw;
    }
}
```

### Activity Kinds

```csharp
// Client = outbound call; Server = inbound; Internal = in-process
using var activity = _source.StartActivity("CallExternalService", ActivityKind.Client);
```

### Setting Tags

Tags are key-value pairs attached to the span. Use OpenTelemetry semantic conventions for well-known names.

```csharp
activity?.SetTag("db.system", "postgresql");
activity?.SetTag("db.name", "orders");
activity?.SetTag("db.operation", "SELECT");
activity?.SetTag("http.method", "POST");
activity?.SetTag("http.url", "https://payments.internal/charge");
```

### Adding Events

Events are timestamped log entries attached to the span (not to be confused with log sinks).

```csharp
activity?.AddEvent(new ActivityEvent("RetryAttempted", tags:
    new ActivityTagsCollection
    {
        { "retry.attempt", 2 },
        { "retry.reason", "Timeout" }
    }));
```

### Status Codes

```csharp
activity?.SetStatus(ActivityStatusCode.Ok);
activity?.SetStatus(ActivityStatusCode.Error, "Payment gateway timeout");
// Unset is the default — do not set Ok prematurely; let instrumentation infer it
```

### Activity Null-Checking Rules

```csharp
// WRONG — throws NullReferenceException when activity is null
var activity = _source.StartActivity("DoWork");
activity.SetTag("key", "value");   // crash if no listener

// CORRECT — null-conditional throughout
using var activity = _source.StartActivity("DoWork");
activity?.SetTag("key", "value");

// CORRECT — guard block when you need activity reference repeatedly
using var activity = _source.StartActivity("DoWork");
if (activity is not null)
{
    activity.SetTag("key", "value");
    activity.SetTag("user.id", userId);
}
```

### Proper Activity Disposal

The `using` block is the preferred pattern. Use `try/finally` only when you need to inspect the activity after it ends.

```csharp
// Preferred: using block
using var activity = _source.StartActivity("DoWork");
// ... work ...
// activity.Dispose() is called automatically at end of block, ending the span

// Alternative: try/finally (needed when activity scope crosses await boundaries
// that can't use using, or when you set status in finally)
var activity = _source.StartActivity("DoWork");
try
{
    // ... work ...
    activity?.SetStatus(ActivityStatusCode.Ok);
}
catch (Exception ex)
{
    activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
    activity?.RecordException(ex);
    throw;
}
finally
{
    activity?.Dispose();  // Always dispose, even on exception
}
```

## Meters and Metrics

### Creating Instruments

```csharp
public sealed class MyInstrumentation : IDisposable
{
    public const string MeterName = "MyApi";

    private readonly Meter _meter;

    // Counter: monotonically increasing value (requests processed, errors)
    public readonly Counter<long> OrdersProcessed;

    // Histogram: distribution of values (request duration, payload size)
    public readonly Histogram<double> OrderProcessingDuration;

    // UpDownCounter: value that can increase or decrease (queue depth, active connections)
    public readonly UpDownCounter<int> ActiveOrders;

    public MyInstrumentation()
    {
        _meter = new Meter(MeterName, "2.1.0");

        OrdersProcessed = _meter.CreateCounter<long>(
            "orders.processed",
            unit: "{order}",
            description: "Total number of orders processed");

        OrderProcessingDuration = _meter.CreateHistogram<double>(
            "orders.processing_duration",
            unit: "s",
            description: "Time to process an order, in seconds");

        ActiveOrders = _meter.CreateUpDownCounter<int>(
            "orders.active",
            unit: "{order}",
            description: "Number of orders currently being processed");
    }

    public void Dispose() => _meter.Dispose();
}
```

### Recording Measurements

```csharp
public class OrderService
{
    private readonly MyInstrumentation _instrumentation;

    public async Task ProcessOrderAsync(Guid orderId)
    {
        _instrumentation.ActiveOrders.Add(1, new TagList
        {
            { "order.type", "standard" }
        });

        var sw = Stopwatch.StartNew();
        try
        {
            await DoProcessingAsync(orderId);

            _instrumentation.OrdersProcessed.Add(1, new TagList
            {
                { "order.type", "standard" },
                { "result", "success" }
            });
        }
        catch
        {
            _instrumentation.OrdersProcessed.Add(1, new TagList
            {
                { "order.type", "standard" },
                { "result", "error" }
            });
            throw;
        }
        finally
        {
            sw.Stop();
            _instrumentation.OrderProcessingDuration.Record(
                sw.Elapsed.TotalSeconds,
                new TagList { { "order.type", "standard" } });

            _instrumentation.ActiveOrders.Add(-1, new TagList
            {
                { "order.type", "standard" }
            });
        }
    }
}
```

## OTLP Exporter Configuration

### appsettings.json

```json
{
  "Otlp": {
    "Endpoint": "http://localhost:4317"
  }
}
```

### Exporter Options

```csharp
.AddOtlpExporter(otlp =>
{
    otlp.Endpoint = new Uri("http://localhost:4317");
    otlp.Protocol = OtlpExportProtocol.Grpc;    // default; use HttpProtobuf for port 4318
    otlp.ExportProcessorType = ExportProcessorType.Batch;  // default; Simple is synchronous
})
```

## Distributed Tracing and Context Propagation

### How It Works

W3C TraceContext propagation is enabled by default in `AddHttpClientInstrumentation()`. Any `HttpClient` managed by `IHttpClientFactory` automatically injects `traceparent` and `tracestate` headers on outbound requests. Receiving services using `AddAspNetCoreInstrumentation()` automatically extract and continue the trace.

```
Service A                         Service B
--------                         ---------
Activity "HandleRequest"  ---->  Activity "HandleRequest" (child, same TraceId)
  sets traceparent header           reads traceparent header
```

### W3C Baggage

Baggage propagates key-value pairs across service boundaries (not stored in spans — use tags for span-local data).

```csharp
// Set baggage on outbound context
Baggage.SetBaggage("tenant.id", tenantId);
Baggage.SetBaggage("correlation.id", correlationId);

// Read baggage on receiving service
var tenantId = Baggage.GetBaggage("tenant.id");
```

### Manual Context Extraction (Message Queues)

```csharp
// Producer: inject context into message headers
var propagator = Propagators.DefaultTextMapPropagator;
propagator.Inject(
    new PropagationContext(Activity.Current?.Context ?? default, Baggage.Current),
    message.Headers,
    (headers, key, value) => headers[key] = value);

// Consumer: extract and restore context
var parentContext = propagator.Extract(
    default,
    message.Headers,
    (headers, key) => headers.TryGetValue(key, out var val) ? new[] { val } : Array.Empty<string>());

using var activity = _source.StartActivity(
    "ConsumeMessage",
    ActivityKind.Consumer,
    parentContext.ActivityContext);
```

## Console Exporter (Debugging)

Add alongside OTLP during development to see spans in terminal output without a collector running.

```csharp
.WithTracing(tracing => tracing
    .AddSource(MyInstrumentation.ActivitySourceName)
    .AddAspNetCoreInstrumentation()
    .AddConsoleExporter())    // outputs span details to stdout
```

## Resource Configuration

Resources are metadata attached to every span and metric from this service instance.

```csharp
.ConfigureResource(resource => resource
    .AddService(
        serviceName: builder.Configuration["Otlp:ServiceName"] ?? "MyApi",
        serviceVersion: typeof(Program).Assembly
            .GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion ?? "unknown")
    .AddAttributes(new Dictionary<string, object>
    {
        ["deployment.environment"] = builder.Environment.EnvironmentName.ToLowerInvariant(),
        ["host.name"] = Environment.MachineName
    }))
```

## Common Mistakes

| Mistake | Consequence | Fix |
|--------|-------------|-----|
| Not null-checking `StartActivity()` result | `NullReferenceException` in test/no-listener environments | Always use `?.` or guard with `is not null` |
| Not calling `Dispose()` on Activity | Span never ends; trace tree is corrupted | Always use `using` or `try/finally { activity?.Dispose(); }` |
| Setting `ActivityStatusCode.Ok` before work completes | Misleading traces for failed requests | Set status in `catch` and `finally` only |
| Including user/entity IDs in meter dimension names | High cardinality explodes metric storage | Use low-cardinality tags only (status, type, region) |
| Registering `ActivitySource` or `Meter` without `AddSource`/`AddMeter` | Spans and measurements are silently dropped | Match source/meter names exactly in OTel builder |
| Using `Activity.Current` directly without null-check | Crash in contexts with no active activity | Guard: `Activity.Current?.SetTag(...)` |
