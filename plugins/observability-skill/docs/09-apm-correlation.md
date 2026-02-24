# APM-Log Correlation

Reference for connecting distributed traces to log events in .NET 8+ applications using Elastic APM, OpenTelemetry, Serilog, and Seq.

---

## Why Correlation Matters

A trace tells you *what* a request did across services and *how long* each step took. Logs tell you *why* something happened. Without correlation, these two streams are isolated — you must manually cross-reference timestamps and guess which log lines belong to a failing span.

Correlation injects trace identifiers as properties on every log event produced during a traced operation. This lets you:

- Jump from a slow or failed span in Kibana APM directly to the log lines that produced it
- Filter all log output in Seq to a single transaction or span using one ID
- Reconstruct the exact sequence of events across multiple services involved in one user request

---

## Elastic APM Automatic Log Correlation

The `Elastic.Apm.SerilogEnricher` package injects three trace-context properties onto every Serilog log event automatically, as long as the event is produced on a thread that has an active Elastic APM transaction or span.

| Property | Source | Example Value |
|---|---|---|
| `ElasticApmTraceId` | Active trace | `4bf92f3577b34da6a3ce929d0e0e4736` |
| `ElasticApmTransactionId` | Active transaction | `00f067aa0ba902b7` |
| `ElasticApmSpanId` | Active span (if any) | `a2fb4a1d1a96d312` |

### NuGet Package

```
Elastic.Apm.SerilogEnricher
```

### Configuration

Add the enricher to the Serilog pipeline. Use `ReadFrom.Services(services)` in `UseSerilog()` so the enricher can resolve `ITracer` from DI.

```csharp
// Program.cs
builder.Host.UseSerilog((context, services, configuration) =>
    configuration
        .ReadFrom.Configuration(context.Configuration)
        .ReadFrom.Services(services)
        .Enrich.FromLogContext()
        .Enrich.WithElasticApmCorrelationInfo()   // <-- Elastic APM enricher
);
```

Or in `appsettings.json` (requires `Elastic.Apm.SerilogEnricher` listed under `Using`):

```json
{
  "Serilog": {
    "Using": [ "Elastic.Apm.SerilogEnricher" ],
    "Enrich": [
      "FromLogContext",
      "WithElasticApmCorrelationInfo"
    ]
  }
}
```

When no active transaction exists (e.g., a background queue consumer before the APM agent starts a transaction), the enricher adds the properties with empty values rather than omitting them.

---

## W3C TraceContext Standard

The W3C TraceContext specification defines how trace context propagates across HTTP boundaries via the `traceparent` header.

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             ^  ^                                ^                ^
             |  trace-id (128-bit hex, 32 chars) |                trace-flags
             version                             parent-id (64-bit hex, 16 chars)
```

| Field | Length | Description |
|---|---|---|
| `version` | 2 hex | Always `00` in the current spec |
| `trace-id` | 32 hex | Globally unique identifier for the entire distributed trace |
| `parent-id` | 16 hex | Identifier of the calling span — becomes the parent for the receiving span |
| `trace-flags` | 2 hex | `01` = sampled, `00` = not sampled |

Both Elastic APM and OpenTelemetry honour this header by default. Services do not need to be on the same platform — an Elastic APM-instrumented service can propagate context to an OpenTelemetry-instrumented downstream service and the trace will stitch together.

---

## Distributed Tracing Across Services

### HTTP — Automatic Propagation

`HttpClient` instances created via `IHttpClientFactory` propagate the `traceparent` (and Elastic `elastic-apm-traceparent`) header automatically when the Elastic APM agent or OpenTelemetry instrumentation is active. No code change is required.

```csharp
// IHttpClientFactory — trace headers injected automatically
public class CatalogClient(IHttpClientFactory factory)
{
    private readonly HttpClient _http = factory.CreateClient("catalog");

    public async Task<Product?> GetProductAsync(int id, CancellationToken ct)
    {
        // traceparent header is added by the agent/OTel instrumentation
        return await _http.GetFromJsonAsync<Product>($"/products/{id}", ct);
    }
}
```

### Message Queues — Manual Context Propagation

Message brokers (RabbitMQ, Azure Service Bus, Kafka) do not have a built-in header propagation mechanism that APM agents can hook into automatically. Inject and extract the `traceparent` header manually.

**Producer — inject context into message headers:**

```csharp
using System.Diagnostics;
using OpenTelemetry;
using OpenTelemetry.Context.Propagation;

public class OrderPublisher(IMessageBus bus)
{
    private static readonly TextMapPropagator Propagator =
        Propagators.DefaultTextMapPropagator;

    public async Task PublishOrderCreatedAsync(OrderCreatedEvent evt)
    {
        var headers = new Dictionary<string, string>();

        // Inject current trace context into the headers dictionary
        Propagator.Inject(
            new PropagationContext(Activity.Current?.Context ?? default, Baggage.Current),
            headers,
            static (carrier, key, value) => carrier[key] = value);

        await bus.PublishAsync(evt, headers);
    }
}
```

**Consumer — extract context from message headers and restore it:**

```csharp
public class OrderCreatedConsumer(IMessageBus bus)
{
    private static readonly ActivitySource ActivitySource =
        new("MyApp.Messaging");

    private static readonly TextMapPropagator Propagator =
        Propagators.DefaultTextMapPropagator;

    public async Task HandleAsync(OrderCreatedEvent evt, IDictionary<string, string> headers)
    {
        // Restore propagated context
        var parentContext = Propagator.Extract(
            default,
            headers,
            static (carrier, key) =>
                carrier.TryGetValue(key, out var value)
                    ? new[] { value }
                    : Array.Empty<string>());

        Baggage.Current = parentContext.Baggage;

        // Start a child span under the restored parent
        using var activity = ActivitySource.StartActivity(
            "order-created-consumer",
            ActivityKind.Consumer,
            parentContext.ActivityContext);

        activity?.SetTag("messaging.system", "rabbitmq");
        activity?.SetTag("order.id", evt.OrderId);

        await ProcessAsync(evt);
    }
}
```

### gRPC — Automatic Propagation

OpenTelemetry's `Grpc.AspNetCore` instrumentation injects and extracts `traceparent` via gRPC metadata automatically. Register it alongside the HTTP instrumentation:

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddGrpcClientInstrumentation()   // outbound gRPC calls
        .AddSource("MyApp.*"));
```

---

## OpenTelemetry Correlation

When using OpenTelemetry (without Elastic APM), trace context is available on `Activity.Current`. `Activity.TraceId` and `Activity.SpanId` are the OTel equivalents of the Elastic APM properties.

| OTel Property | Elastic APM Property | Description |
|---|---|---|
| `Activity.Current.TraceId` | `ElasticApmTraceId` | 128-bit trace identifier |
| `Activity.Current.SpanId` | `ElasticApmSpanId` | Current span identifier |
| `Activity.Current.Id` | `ElasticApmTransactionId` | W3C formatted span identifier |

### Custom Serilog Enricher for OpenTelemetry Trace Context

Use this enricher when running OpenTelemetry without the Elastic APM agent. It reads `Activity.Current` at log time and attaches trace properties to every event.

```csharp
using System.Diagnostics;
using Serilog.Core;
using Serilog.Events;

public sealed class OpenTelemetryTraceEnricher : ILogEventEnricher
{
    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory propertyFactory)
    {
        var activity = Activity.Current;

        if (activity is null)
            return;

        logEvent.AddPropertyIfAbsent(
            propertyFactory.CreateProperty("TraceId", activity.TraceId.ToString()));

        logEvent.AddPropertyIfAbsent(
            propertyFactory.CreateProperty("SpanId", activity.SpanId.ToString()));

        logEvent.AddPropertyIfAbsent(
            propertyFactory.CreateProperty("ParentSpanId", activity.ParentSpanId.ToString()));

        // Expose the W3C traceparent header value for cross-system correlation
        if (!string.IsNullOrEmpty(activity.Id))
        {
            logEvent.AddPropertyIfAbsent(
                propertyFactory.CreateProperty("TraceParent", activity.Id));
        }
    }
}
```

**Registration:**

```csharp
builder.Host.UseSerilog((context, services, configuration) =>
    configuration
        .ReadFrom.Configuration(context.Configuration)
        .ReadFrom.Services(services)
        .Enrich.FromLogContext()
        .Enrich.With<OpenTelemetryTraceEnricher>()
);
```

The enricher adds `TraceId`, `SpanId`, `ParentSpanId`, and `TraceParent` as queryable properties on every log event produced within an active span.

---

## Viewing Correlated Logs in Kibana APM

When `ElasticApmTraceId` is present on log events and those events are shipped to Elasticsearch (via Filebeat, an Elastic sink, or the Elastic Common Schema formatter), Kibana APM surfaces them on the transaction and span detail pages.

**To navigate from a trace to its logs:**

1. Open Kibana APM and locate the service.
2. Select a transaction from the Transactions tab.
3. Open the transaction detail view — select the **Logs** tab.
4. Kibana automatically queries for log documents where `trace.id` matches the current transaction's trace ID.

The **Logs** tab is only populated when:
- Log events include `ElasticApmTraceId` (or the OTel `trace.id` field in ECS format)
- Logs are indexed in the same Elasticsearch cluster that Kibana APM is connected to
- The APM integration or a data view covers the log indices

---

## Cross-Service Trace Visualization in Kibana APM

Distributed traces that span multiple services appear in the **Waterfall view** on the transaction detail page.

```
Service A: POST /checkout                      [===================] 320 ms
  Service B: GET /inventory/{sku}              [===]                 42 ms
  Service C: POST /payments/charge             [=========]          180 ms
    Service D: RPC ValidateCard                [====]                61 ms
  Service A: INSERT orders                     [=]                   18 ms
```

Each bar represents a span. Clicking a span shows:
- Duration and timing relative to the root transaction
- Tags and labels attached to the span
- The **Logs** tab scoped to that individual span's `SpanId`

For the waterfall to stitch spans together, every service must propagate the same `traceparent` header. Services using Elastic APM agents, OpenTelemetry SDK, or W3C-compliant middleware all interoperate without additional configuration.

---

## Seq Correlation

Seq does not have a dedicated APM integration, but trace IDs on log properties are fully queryable.

**Filter by trace ID in Seq:**

```
ElasticApmTraceId = '4bf92f3577b34da6a3ce929d0e0e4736'
```

Or using the OTel enricher properties:

```
TraceId = '4bf92f3577b34da6a3ce929d0e0e4736'
```

**Cross-service log correlation in Seq** — because the same `TraceId` value appears on logs from every service that participated in the trace, a single filter returns a unified event stream across all services ordered by timestamp.

Tip: save a Seq signal or workspace with the trace ID filter when debugging a specific incident. This lets you toggle between all-services and single-service views without re-typing the filter.

---

## Required NuGet Packages

| Package | Purpose |
|---|---|
| `Elastic.Apm.SerilogEnricher` | `WithElasticApmCorrelationInfo()` enricher |
| `Elastic.Apm.AspNetCore` | Elastic APM middleware and agent bootstrapping |
| `OpenTelemetry.Extensions.Hosting` | `AddOpenTelemetry()` host integration |
| `OpenTelemetry.Instrumentation.AspNetCore` | Automatic HTTP server span creation |
| `OpenTelemetry.Instrumentation.GrpcNetClient` | Automatic gRPC client span creation |
| `OpenTelemetry.Context.Propagation` | `TextMapPropagator`, `Propagators` for manual queue propagation |
| `Serilog.AspNetCore` | `UseSerilog()`, `ReadFrom.Services()` |
