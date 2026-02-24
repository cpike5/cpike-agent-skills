# Elastic Common Schema (ECS)

## Why ECS

- **Standardized field names** across all teams, services, and data sources
- **Out-of-the-box Kibana dashboards** — Logs, APM, Security, Observability all expect ECS fields
- **Cross-team correlation** — trace a request from frontend → API → queue → worker using shared field names
- **OpenTelemetry convergence** — ECS and OTel semantic conventions are merging; adopting ECS now is forward-compatible
- **Beats and Elastic Agent** produce ECS-compliant data by default

## Base Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `@timestamp` | `date` | **Yes** | Event timestamp. ILM, data streams, and sorting depend on this field. |
| `message` | `match_only_text` | No | Human-readable event description. Full-text searchable. |
| `tags` | `keyword` | No | Flat list of tags for filtering (`["production", "web-tier"]`). |
| `labels` | `object` | No | Key-value pairs for custom metadata. **Keys must not contain dots.** |

## Log Fields

| Field | Type | Description |
|-------|------|-------------|
| `log.level` | `keyword` | Severity: `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL` |
| `log.logger` | `keyword` | Logger name (`MyApp.Services.OrderService`) |
| `log.origin.file.name` | `keyword` | Source file that produced the log |
| `log.origin.function` | `keyword` | Function/method name |

## Event Fields

| Field | Type | Description |
|-------|------|-------------|
| `event.kind` | `keyword` | Top-level classification: `event`, `alert`, `metric`, `state`, `signal` |
| `event.category` | `keyword` | Category array: `authentication`, `database`, `network`, `process`, `web` |
| `event.type` | `keyword` | Subcategory: `access`, `creation`, `deletion`, `error`, `info`, `start`, `end` |
| `event.outcome` | `keyword` | Result: `success`, `failure`, `unknown` |
| `event.action` | `keyword` | Specific action taken (`user-login`, `order-created`) |
| `event.duration` | `long` | Duration in **nanoseconds** |
| `event.ingested` | `date` | Timestamp when the event entered the pipeline |
| `event.original` | `keyword` | Raw, unprocessed event text. Useful for reprocessing. |

## Host Fields

| Field | Type | Description |
|-------|------|-------------|
| `host.name` | `keyword` | Host identifier (may differ from hostname) |
| `host.hostname` | `keyword` | FQDN or short hostname |
| `host.ip` | `ip` | One or more host IP addresses |
| `host.os.name` | `keyword` | OS name (`Windows`, `Ubuntu`) |
| `host.architecture` | `keyword` | CPU architecture (`x86_64`, `arm64`) |

## Service Fields

| Field | Type | Description |
|-------|------|-------------|
| `service.name` | `keyword` | **Required for APM.** Logical service name (`order-api`). |
| `service.version` | `keyword` | Deployed version (`2.4.1`, `abc123`) |
| `service.environment` | `keyword` | Deployment environment (`production`, `staging`) |
| `service.node.name` | `keyword` | Instance identifier within a scaled service |

## Trace/Span Fields

| Field | Type | Description |
|-------|------|-------------|
| `trace.id` | `keyword` | W3C trace ID (32 hex chars). Links logs → APM traces. |
| `span.id` | `keyword` | Span ID (16 hex chars) |
| `transaction.id` | `keyword` | APM transaction ID (16 hex chars) |

## Error Fields

| Field | Type | Description |
|-------|------|-------------|
| `error.message` | `match_only_text` | Error description text |
| `error.type` | `keyword` | Exception class (`System.NullReferenceException`) |
| `error.stack_trace` | `wildcard` | Full stack trace. **Use `wildcard` type, not `text`.** |
| `error.code` | `keyword` | Numeric or string error code |

## HTTP Fields

| Field | Type | Description |
|-------|------|-------------|
| `http.request.method` | `keyword` | HTTP method (`GET`, `POST`), uppercased |
| `http.response.status_code` | `long` | Response status code (`200`, `404`, `503`) |
| `http.request.body.bytes` | `long` | Request body size in bytes |
| `http.response.body.bytes` | `long` | Response body size in bytes |
| `url.full` | `wildcard` | Complete URL. **Use `wildcard` type for efficient prefix/suffix queries.** |
| `url.path` | `wildcard` | URL path component (`/api/v2/orders`) |

## User Fields

| Field | Type | Description |
|-------|------|-------------|
| `user.name` | `keyword` | Username or login name |
| `user.id` | `keyword` | Unique user identifier |
| `user.email` | `keyword` | User email address |
| `user.roles` | `keyword` | Array of assigned roles |

## Using `ecs@mappings` Component Template

- Elasticsearch ships a built-in `ecs@mappings` component template
- Compose it into index templates to get **automatic ECS field types** without manual mapping

```json
PUT _index_template/my-app-template
{
  "index_patterns": ["logs-myapp-*"],
  "data_stream": {},
  "composed_of": [
    "ecs@mappings",
    "logs@settings",
    "my-app-mappings"
  ],
  "priority": 200
}
```

- `ecs@mappings` handles base ECS fields — add a custom component template for app-specific fields
- **Priority**: higher number wins when index patterns overlap

## Field Type Recommendations

| Use Case | Recommended Type | Reason |
|----------|-----------------|--------|
| Structured values (status, name, id) | `keyword` | Exact match, aggregations, sorting |
| Log messages, descriptions | `match_only_text` | Full-text search, no scoring overhead, less disk than `text` |
| Stack traces, URLs | `wildcard` | Efficient `wildcard` and `regexp` queries on long strings |
| Numeric codes (HTTP status) | `long` | Range queries, aggregations |
| Timestamps | `date` | Date math, histograms, sorting |
| IP addresses | `ip` | CIDR range queries |

## Common Mistakes

- **Using non-ECS field names** — `level` instead of `log.level`, `hostname` instead of `host.name`, `status` instead of `http.response.status_code`. Kibana dashboards and detection rules expect ECS names.
- **Using `text` type for structured fields** — `text` fields cannot be used in aggregations or exact-match filters. Use `keyword`.
- **Not including `@timestamp`** — Data streams **require** it. ILM rollover and time-based queries depend on it. Documents without `@timestamp` are rejected by data streams.
- **Dots in `labels` keys** — `labels.app.name` creates nested object mapping conflicts. Use underscores: `labels.app_name`.
- **Using `text` for stack traces** — Stack traces are long and rarely searched by individual terms. Use `wildcard` for `error.stack_trace`.
- **Storing `event.duration` in milliseconds** — ECS specifies **nanoseconds**. Multiply ms values by `1000000`.
