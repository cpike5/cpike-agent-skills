# OpenTelemetry to Elastic Integration

Reference for exporting OpenTelemetry signals from .NET 8+ applications to Elastic APM Server or Elastic Cloud. Assumes familiarity with `07-opentelemetry.md` (OTel SDK) and `06-elastic-apm.md` (native Elastic APM).

---

## OTLP Export to Elastic APM Server (Self-Hosted)

Elastic APM Server accepts OTLP over gRPC (port 8200) and HTTP (port 8200). Use `OpenTelemetry.Exporter.OpenTelemetryProtocol`.

```csharp
// Program.cs
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter(otlp =>
        {
            otlp.Endpoint = new Uri("http://localhost:8200");
            otlp.Protocol = OtlpExportProtocol.Grpc;
            otlp.Headers = "Authorization=Bearer <secret-token>";
        }))
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()
        .AddOtlpExporter(otlp =>
        {
            otlp.Endpoint = new Uri("http://localhost:8200");
            otlp.Protocol = OtlpExportProtocol.Grpc;
            otlp.Headers = "Authorization=Bearer <secret-token>";
        }));
```

**Authentication header format:**

| APM Server auth mode | Header value |
|---|---|
| Secret token | `Authorization=Bearer <your-secret-token>` |
| API key | `Authorization=ApiKey <base64-encoded-id:key>` |
| No auth (dev only) | Omit `Headers` entirely |

The base64 API key value is `Base64(id:api_key_value)` — the same format as Elasticsearch HTTP API keys.

**appsettings.json alternative** — use environment variables or config to avoid hardcoding credentials:

```json
{
  "OpenTelemetry": {
    "Otlp": {
      "Endpoint": "http://localhost:8200",
      "Headers": "Authorization=Bearer <secret-token>"
    }
  }
}
```

```csharp
otlp.Endpoint = new Uri(configuration["OpenTelemetry:Otlp:Endpoint"]!);
otlp.Headers = configuration["OpenTelemetry:Otlp:Headers"]!;
```

---

## OTLP Export to Elastic Cloud

Elastic Cloud uses HTTPS with a per-deployment APM endpoint and either a secret token or an API key.

**Endpoint format:**

```
https://<deployment-id>.apm.<region>.aws.cloud.es.io
```

The path suffix `/` is the root — do not append `/v1/traces` manually; the OTLP exporter appends the correct path automatically for gRPC and HTTP/protobuf modes.

```csharp
otlp.Endpoint = new Uri("https://<deployment-id>.apm.<region>.aws.cloud.es.io");
otlp.Protocol = OtlpExportProtocol.HttpProtobuf;   // required for Elastic Cloud; gRPC may be blocked
otlp.Headers = "Authorization=Bearer <secret-token>";
```

For API key auth on Elastic Cloud:

```csharp
// Encode "id:api_key_value" to Base64 first
otlp.Headers = "Authorization=ApiKey <base64-id-colon-apikey>";
```

> Use `OtlpExportProtocol.HttpProtobuf` for Elastic Cloud. Some cloud environments block gRPC (HTTP/2) at the load balancer level. HTTP/protobuf uses port 443 and is universally supported.

---

## Feature Comparison: Native Elastic APM Agent vs OpenTelemetry SDK

| Capability | Native Elastic APM Agent | OpenTelemetry SDK |
|---|---|---|
| **Auto-instrumentation** | Broad: ASP.NET Core, EF Core, HttpClient, gRPC, Redis, RabbitMQ, Kafka, SqlClient | Good: ASP.NET Core, HttpClient, gRPC, EF Core, SqlClient — via contrib packages |
| **Custom instrumentation API** | `ITracer` / `ISpan` (Elastic-specific) | `ActivitySource` / `Activity` (.NET standard) |
| **Metrics API** | Built-in CPU, memory, transaction metrics | `Meter` / `Counter` / `Histogram` (OTLP or Prometheus export) |
| **Configuration** | Single `ElasticApm` config section or env vars | Per-signal configuration; more moving parts |
| **Multi-backend export** | Elastic only | Any OTLP-compatible backend (Elastic, Jaeger, Zipkin, OTEL Collector) |
| **Vendor lock-in** | High — `ITracer` is Elastic-specific | Low — `ActivitySource` is a .NET BCL type |
| **Log correlation** | Automatic via `ILogger` enricher | Manual or via EDOT (see below) |
| **Maturity / stability** | Stable, production-proven | Stable for tracing/metrics; logs signal is newer |
| **Sampling support** | Head-based sampling via config | Head-based and tail-based via SDK or OTel Collector |
| **Profiling integration** | Elastic Universal Profiling (native agent only) | Not available via OTel SDK alone |

---

## When to Choose Each Approach

### Choose the Native Elastic APM Agent when:

- Your team is already invested in the Elastic Stack and has no plans to change backends.
- You want the simplest possible setup — one NuGet package, one config section.
- You need Elastic-specific features: Universal Profiling, detailed EF Core query capture, or Elastic-managed sampling rules.
- You are instrumenting an existing codebase and want auto-instrumentation without code changes.

### Choose the OpenTelemetry SDK when:

- You need vendor neutrality — the ability to swap or multi-export to Jaeger, Datadog, or a corporate OTEL Collector without changing application code.
- You are instrumenting a new service and want to avoid `ITracer` coupling.
- Your organization standardizes on OTel as the observability contract across multiple platforms.
- You need tail-based sampling via an OTel Collector in front of Elastic.
- Future-proofing is a priority — OTel is the CNCF standard and will remain relevant regardless of backend.

---

## Migration Path: Native Elastic APM to OpenTelemetry

Migrate incrementally by service. Do not attempt a fleet-wide cutover.

**Step 1 — Add OTel packages alongside the existing agent.**

```xml
<PackageReference Include="OpenTelemetry.Extensions.Hosting" Version="1.*" />
<PackageReference Include="OpenTelemetry.Instrumentation.AspNetCore" Version="1.*" />
<PackageReference Include="OpenTelemetry.Instrumentation.Http" Version="1.*" />
<PackageReference Include="OpenTelemetry.Exporter.OpenTelemetryProtocol" Version="1.*" />
```

**Step 2 — Replace `ITracer` custom spans with `ActivitySource`.**

```csharp
// Before — Elastic APM native
public class OrderService
{
    private readonly ITracer _tracer;

    public async Task ProcessAsync(int orderId)
    {
        var span = _tracer.CurrentTransaction?.StartSpan("ProcessOrder", ApiConstants.TypeCustom);
        try { /* ... */ }
        finally { span?.End(); }
    }
}

// After — OpenTelemetry ActivitySource
public class OrderService
{
    private static readonly ActivitySource _source = new("MyApp.Orders");

    public async Task ProcessAsync(int orderId)
    {
        using var activity = _source.StartActivity("ProcessOrder");
        activity?.SetTag("order.id", orderId);
        /* ... */
    }
}
```

**Step 3 — Register `ActivitySource` names with the OTel SDK.**

```csharp
.WithTracing(tracing => tracing
    .AddSource("MyApp.Orders")
    .AddSource("MyApp.Payments")
    .AddAspNetCoreInstrumentation()
    .AddOtlpExporter(/* ... */));
```

**Step 4 — Remove `Elastic.Apm.NetCoreAll` or `Elastic.Apm.AspNetCore` package references** once all custom spans and APM middleware calls have been replaced. Verify in Kibana that traces appear under the OTel service name before removing the native agent.

**Step 5 — Update log correlation.** The native agent injects `transaction.id` and `trace.id` automatically. With OTel, use the EDOT distribution (see below) or manually enrich Serilog with `Activity.Current`.

---

## Config Mapping: Elastic APM Env Vars to OTel Equivalents

| Elastic APM Variable | OTel Equivalent | Notes |
|---|---|---|
| `ELASTIC_APM_SERVICE_NAME` | `OTEL_SERVICE_NAME` | Sets `service.name` resource attribute |
| `ELASTIC_APM_SERVICE_VERSION` | `OTEL_SERVICE_VERSION` | Sets `service.version` resource attribute |
| `ELASTIC_APM_ENVIRONMENT` | `OTEL_DEPLOYMENT_ENVIRONMENT` (resource attr) | Set via `ResourceBuilder.AddAttributes` |
| `ELASTIC_APM_SERVER_URL` | `OTEL_EXPORTER_OTLP_ENDPOINT` | Full URL including port |
| `ELASTIC_APM_SECRET_TOKEN` | `OTEL_EXPORTER_OTLP_HEADERS` | Format: `Authorization=Bearer <token>` |
| `ELASTIC_APM_API_KEY` | `OTEL_EXPORTER_OTLP_HEADERS` | Format: `Authorization=ApiKey <base64>` |
| `ELASTIC_APM_TRANSACTION_SAMPLE_RATE` | `OTEL_TRACES_SAMPLER` + `OTEL_TRACES_SAMPLER_ARG` | Sampler: `traceidratio`; arg: `0.25` |
| `ELASTIC_APM_DISABLE_INSTRUMENTATIONS` | No direct equivalent | Remove specific `Add*Instrumentation()` calls |
| `ELASTIC_APM_LOG_LEVEL` | `OTEL_LOG_LEVEL` | Values: `debug`, `info`, `warn`, `error` |

---

## Elastic EDOT .NET Distribution

EDOT (Elastic Distribution of OpenTelemetry for .NET) is Elastic's supported wrapper around the OTel .NET SDK. Install via:

```xml
<PackageReference Include="Elastic.OpenTelemetry" Version="1.*" />
```

**What EDOT adds over the base OTel SDK:**

- Automatic Elastic resource attributes (`service.name`, `deployment.environment`) sourced from `ELASTIC_APM_*` env vars for backward compatibility during migration.
- Pre-configured OTLP exporter defaults pointing to Elastic APM Server.
- Built-in log correlation: injects `trace.id` and `transaction.id` into `ILogger` scope, matching the Elastic ECS schema expected by Kibana.
- Simplified `AddElasticOpenTelemetry()` registration that wires tracing, metrics, and log export in one call.

```csharp
// Program.cs — EDOT simplified setup
builder.Services.AddElasticOpenTelemetry(options =>
{
    options.Tracing.AddSource("MyApp.Orders");
});
```

EDOT respects `OTEL_*` standard environment variables and also accepts `ELASTIC_APM_*` variables, making it the lowest-friction migration target from the native Elastic APM agent.

---

## Gotchas and Compatibility Notes

**Service name casing.** Elastic APM normalizes service names to lowercase with hyphens. OTel does not normalize. Set `OTEL_SERVICE_NAME` in lowercase-hyphenated form (`my-app-api`) to match existing Kibana service dashboards after migration.

**Trace ID format.** Both the native Elastic agent and OTel use W3C TraceContext (128-bit trace IDs). Distributed traces between a native-agent service and an OTel-instrumented service will correlate correctly as long as W3C propagation is active on both sides — which is the default for both.

**gRPC vs HTTP/protobuf.** The OTel SDK defaults to gRPC (`OtlpExportProtocol.Grpc`). Elastic APM Server supports both, but firewalls, proxies, and Elastic Cloud may block gRPC. Always verify connectivity; switch to `HttpProtobuf` if traces are silently dropped.

**Metric naming differences.** Native Elastic APM metric names use dot notation (`transaction.duration.us`). OTel metrics use the OpenMetrics convention (`http.server.request.duration` in seconds). Kibana dashboards built against native APM metric names will not automatically display OTel metrics — rebuild or clone dashboards after migration.

**Double-export risk.** If both the native agent and OTel SDK are active simultaneously during migration, spans may appear twice in Kibana. Limit dual-active time to a single service at a time and validate in a non-production environment first.

**Logs signal maturity.** OTel log export (via `OpenTelemetry.Exporter.OpenTelemetryProtocol` for logs) is stable as of OTel .NET 1.9. However, Elastic's log ingestion via OTLP is newer than its trace/metric support. Prefer Serilog → Elasticsearch sink for logs until your Elastic Stack version is confirmed to fully support OTLP log ingestion (Elastic Stack 8.0+ recommended).
