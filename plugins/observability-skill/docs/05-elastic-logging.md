# Elastic Logging

Reference for shipping .NET structured logs to Elasticsearch via Serilog. Covers sink setup, ECS formatting, index strategies, ILM, resilience, and authentication.

---

## NuGet Packages

```xml
<!-- Core sink -->
<PackageReference Include="Serilog.Sinks.Elasticsearch" Version="10.*" />

<!-- ECS formatting (recommended) -->
<PackageReference Include="Serilog.Formatting.Elasticsearch" Version="10.*" />
```

> **Version alignment**: `Serilog.Sinks.Elasticsearch` v10+ targets .NET 8 and Elasticsearch 8.x. Verify the sink and formatter packages share the same major version to avoid serialization mismatches.

---

## Basic Setup

### Code-based configuration

```csharp
using Serilog;
using Serilog.Sinks.Elasticsearch;
using Serilog.Formatting.Elasticsearch;

Log.Logger = new LoggerConfiguration()
    .Enrich.FromLogContext()
    .WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri("http://localhost:9200"))
    {
        IndexFormat = "myapp-logs-{0:yyyy.MM.dd}",
        AutoRegisterTemplate = true,
        AutoRegisterTemplateVersion = AutoRegisterTemplateVersion.ESv8,
        CustomFormatter = new EcsTextFormatter()
    })
    .CreateLogger();
```

### appsettings.json configuration

```json
{
  "Serilog": {
    "Using": ["Serilog.Sinks.Elasticsearch"],
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft.AspNetCore": "Warning",
        "System.Net.Http": "Warning"
      }
    },
    "WriteTo": [
      {
        "Name": "Elasticsearch",
        "Args": {
          "nodeUris": "http://localhost:9200",
          "indexFormat": "myapp-logs-{0:yyyy.MM.dd}",
          "autoRegisterTemplate": true,
          "autoRegisterTemplateVersion": "ESv8",
          "customFormatter": "Serilog.Formatting.Elasticsearch.EcsTextFormatter, Serilog.Formatting.Elasticsearch"
        }
      }
    ]
  }
}
```

Register with the .NET host:

```csharp
builder.Host.UseSerilog((context, services, configuration) =>
    configuration.ReadFrom.Configuration(context.Configuration));
```

---

## ECS Formatting

Elastic Common Schema (ECS) standardizes field names so logs, APM traces, and metrics share a consistent structure inside Elasticsearch.

### EcsTextFormatter

Produces fully ECS-compliant JSON. Use this when shipping to an ECS-aware stack (Elastic APM, Fleet, Kibana Discover).

```csharp
CustomFormatter = new EcsTextFormatter()
```

Key output fields:

| ECS Field | Source |
|---|---|
| `@timestamp` | Log event timestamp |
| `log.level` | Serilog level |
| `message` | Rendered message |
| `log.logger` | `SourceContext` property |
| `error.message` / `error.stack_trace` | Exception details |
| `labels.*` | Custom string properties |
| `trace.id` / `transaction.id` | APM correlation properties (if present) |

### ElasticsearchJsonFormatter

Produces Elasticsearch-compatible JSON without strict ECS field mapping. Use when you need legacy compatibility or want raw Serilog property names preserved.

```csharp
CustomFormatter = new ElasticsearchJsonFormatter(renderMessage: true)
```

**Recommendation**: Prefer `EcsTextFormatter` for new projects. It enables log-to-trace correlation in Kibana without extra configuration.

---

## Index Naming Strategies

### Daily indices (default)

```csharp
IndexFormat = "myapp-logs-{0:yyyy.MM.dd}"
// Produces: myapp-logs-2026.02.23
```

### Monthly indices (lower volume workloads)

```csharp
IndexFormat = "myapp-logs-{0:yyyy.MM}"
// Produces: myapp-logs-2026.02
```

### Environment-scoped indices

```csharp
var env = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "production";
IndexFormat = $"myapp-{env.ToLower()}-logs-{{0:yyyy.MM.dd}}"
// Produces: myapp-staging-logs-2026.02.23
```

### Custom index per log level

Use `ModifyConnectionSettings` and a custom `IndexDecider` delegate to route errors to a separate index:

```csharp
new ElasticsearchSinkOptions(nodeUri)
{
    IndexFormat = "myapp-logs-{0:yyyy.MM.dd}",
    IndexDecider = (logEvent, offset) =>
        logEvent.Level >= LogEventLevel.Error
            ? $"myapp-errors-{offset:yyyy.MM.dd}"
            : $"myapp-logs-{offset:yyyy.MM.dd}"
}
```

---

## Data Streams vs Classic Indices

| Concern | Data Streams | Classic Indices |
|---|---|---|
| Write pattern | Append-only (logs, events) | Read/write |
| ILM integration | Built-in via backing indices | Requires explicit rollover alias |
| Rollover | Automatic | Manual or alias-based |
| Update/delete documents | Not supported | Supported |
| Kibana index pattern | Single data stream name | Wildcard pattern required |
| Recommended for | New log pipelines (.NET 8+, ES 8+) | Legacy setups, mutation-heavy data |

**When to use data streams**: New greenfield projects targeting Elasticsearch 8.x. The sink supports data streams via the `DataStreamName` option:

```csharp
new ElasticsearchSinkOptions(nodeUri)
{
    DataStreamName = "myapp-logs",   // creates logs-myapp-logs data stream
    AutoRegisterTemplate = true
}
```

**When to use classic indices**: Existing pipelines, Elasticsearch versions below 7.9, or when documents require post-write updates (unusual for logs).

---

## ILM — Index Lifecycle Management

ILM automates index retention through four phases. Define a policy once; attach it to an index template.

### Phase overview

| Phase | Trigger | Typical action |
|---|---|---|
| Hot | Index is active | Shard allocation, write activity |
| Warm | Age or size threshold | Shrink shards, force-merge, reduce replicas |
| Cold | Longer age threshold | Move to cheaper hardware/tier |
| Delete | Final retention boundary | Remove index |

### Attaching the default policy in sink options

```csharp
new ElasticsearchSinkOptions(nodeUri)
{
    IndexFormat = "myapp-logs-{0:yyyy.MM.dd}",
    AutoRegisterTemplate = true,
    AutoRegisterTemplateVersion = AutoRegisterTemplateVersion.ESv8,
    LifecycleName = "myapp-logs-policy",   // must exist in Elasticsearch
    RolloverAlias = "myapp-logs"
}
```

### Minimal ILM policy (Elasticsearch API)

```json
PUT _ilm/policy/myapp-logs-policy
{
  "policy": {
    "phases": {
      "hot":    { "actions": { "rollover": { "max_age": "1d", "max_size": "50gb" } } },
      "warm":   { "min_age": "7d",  "actions": { "shrink": { "number_of_shards": 1 }, "forcemerge": { "max_num_segments": 1 } } },
      "cold":   { "min_age": "30d", "actions": { "freeze": {} } },
      "delete": { "min_age": "90d", "actions": { "delete": {} } }
    }
  }
}
```

> ILM policies must be created in Elasticsearch directly (Kibana Stack Management or API). The Serilog sink references an existing policy by name — it does not create policies automatically.

---

## Durable / Buffered Mode

The durable sink buffers log events to a local disk file before forwarding to Elasticsearch. If the cluster is unavailable, events are not lost.

```csharp
using Serilog.Sinks.Elasticsearch;

new ElasticsearchSinkOptions(nodeUri)
{
    IndexFormat = "myapp-logs-{0:yyyy.MM.dd}",
    BufferBaseFilename = "/var/log/myapp/elastic-buffer",  // path prefix, not full filename
    BufferFileSizeLimitBytes = 100_000_000,                // 100 MB per buffer file
    BufferFileCountLimit = 5,                              // keep at most 5 buffer files
    BatchAction = ElasticOpType.Create
}
```

Buffer files are created as `<BufferBaseFilename>-*.json`. The sink replays them in order once connectivity is restored.

**When to enable durable mode**: Any production workload where log loss is unacceptable (audit trails, compliance). The trade-off is additional disk I/O and the need to monitor buffer directory growth.

---

## Authentication

### API key (recommended)

```csharp
new ElasticsearchSinkOptions(nodeUri)
{
    ModifyConnectionSettings = conn =>
        conn.ApiKeyAuthentication("key-id", "api-key-value")
}
```

Via appsettings.json — store secrets in environment variables or Secret Manager, not in source:

```json
"Args": {
  "nodeUris": "https://my-cluster:9200",
  "indexFormat": "myapp-logs-{0:yyyy.MM.dd}",
  "modifyConnectionSettings": "ApiKey"
}
```

For full control, configure the connection in code and read credentials from `IConfiguration`:

```csharp
builder.Host.UseSerilog((ctx, services, cfg) =>
{
    var esUri = new Uri(ctx.Configuration["Elastic:Uri"]!);
    var apiKeyId = ctx.Configuration["Elastic:ApiKeyId"]!;
    var apiKey = ctx.Configuration["Elastic:ApiKey"]!;

    cfg.WriteTo.Elasticsearch(new ElasticsearchSinkOptions(esUri)
    {
        IndexFormat = "myapp-logs-{0:yyyy.MM.dd}",
        ModifyConnectionSettings = conn => conn.ApiKeyAuthentication(apiKeyId, apiKey),
        CustomFormatter = new EcsTextFormatter()
    });
});
```

### Basic auth

```csharp
ModifyConnectionSettings = conn =>
    conn.BasicAuthentication("username", "password")
```

### Cloud ID (Elastic Cloud)

```csharp
var options = new ElasticsearchSinkOptions
{
    ModifyConnectionSettings = conn =>
        conn.CloudId("deployment-name:base64-cloud-id")
            .ApiKeyAuthentication("key-id", "api-key-value")
};
```

---

## Property-to-Field Mapping

Serilog properties are serialized into the Elasticsearch document. Field placement depends on the formatter used.

| Serilog property | `EcsTextFormatter` output | `ElasticsearchJsonFormatter` output |
|---|---|---|
| `SourceContext` | `log.logger` | `fields.SourceContext` |
| `RequestId` | `labels.RequestId` | `fields.RequestId` |
| `UserId` (scalar) | `labels.UserId` | `fields.UserId` |
| `Order` (object) | `labels.Order` (flattened string) | `fields.Order` (object) |
| `trace.id` (injected) | `trace.id` | `fields.TraceId` |
| Exception | `error.message`, `error.stack_trace` | `exception.*` |

> ECS restricts `labels.*` values to strings. Complex objects destructured with `@` are serialized to JSON strings under `labels`. Use `ElasticsearchJsonFormatter` if you need objects preserved as nested Elasticsearch types.

---

## Common Issues

### Template conflicts

**Symptom**: Logs stop indexing; Elasticsearch returns a `mapper_parsing_exception`.

**Cause**: A pre-existing index template defines different field types than what the sink's auto-registered template expects.

**Resolution**:
1. Delete the conflicting template: `DELETE _index_template/serilog-events-template`
2. Set `AutoRegisterTemplate = true` and `OverwriteTemplate = true` in sink options to force re-registration on startup.
3. For production, manage index templates explicitly via Kibana or Terraform rather than relying on auto-registration.

### Mapping explosions from uncontrolled properties

**Symptom**: Elasticsearch field count grows unboundedly; cluster performance degrades; `limit of total fields [1000] has been exceeded` errors appear.

**Cause**: Logging objects with highly variable property names — dictionaries with user-controlled keys, deserialized JSON blobs, or unrestricted `@object` destructuring.

**Resolution**:
- Use scalar properties for indexable values: `Log.Information("Request completed {StatusCode} in {Elapsed}ms", code, elapsed)`
- Avoid `{@request}` destructuring on large or variable objects. Serialize to a single string property instead.
- Enable dynamic mapping restrictions in your index template:
  ```json
  "mappings": { "dynamic": "strict" }
  ```
- Add a `LogContext` filter to drop or cap known high-cardinality properties before they reach the sink.

### Sink silently dropping events

**Symptom**: Logs appear in console/file sinks but not in Elasticsearch.

**Common causes and fixes**:
- `EmitEventFailure` defaults to `WriteToSelfLog`. Enable `SelfLog.Enable(Console.Error)` during development to surface sink errors.
- Clock skew between the application host and Elasticsearch can reject documents. Ensure NTP is configured.
- The buffer directory (durable mode) may lack write permissions; verify the application user has write access.
