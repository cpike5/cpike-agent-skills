# Seq Reference — .NET Observability

Seq is a structured log server that accepts events from Serilog (and other sources), indexes every
property value, and provides a query UI, signals, dashboards, and alerting. It is the recommended
local and team-level log destination for .NET applications using Serilog.

---

## NuGet Package

```xml
<PackageReference Include="Serilog.Sinks.Seq" Version="8.*" />
```

---

## Sink Setup

### appsettings.json (preferred)

```json
{
  "Serilog": {
    "Using": ["Serilog.Sinks.Seq"],
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft.AspNetCore": "Warning",
        "System.Net.Http": "Warning",
        "Microsoft.EntityFrameworkCore.Database.Command": "Warning"
      }
    },
    "WriteTo": [
      {
        "Name": "Seq",
        "Args": {
          "serverUrl": "http://localhost:5341",
          "apiKey": "your-api-key-here",
          "restrictedToMinimumLevel": "Information"
        }
      }
    ],
    "Enrich": ["FromLogContext", "WithMachineName", "WithThreadId"],
    "Properties": {
      "Application": "MyServiceName",
      "Environment": "Development"
    }
  }
}
```

### Code configuration

```csharp
builder.Host.UseSerilog((context, services, configuration) =>
{
    configuration
        .ReadFrom.Configuration(context.Configuration)
        .ReadFrom.Services(services)
        .Enrich.FromLogContext()
        .WriteTo.Seq(
            serverUrl: context.Configuration["Seq:ServerUrl"] ?? "http://localhost:5341",
            apiKey: context.Configuration["Seq:ApiKey"],
            restrictedToMinimumLevel: LogEventLevel.Information);
});
```

Store the URL and API key in `appsettings.json` or environment variables — never hard-code them.
The default Seq server URL is `http://localhost:5341`.

---

## Querying Structured Data

Seq uses its own filter expression language. All structured log properties are directly queryable.

### Basic filter syntax

| Pattern | Example |
|---------|---------|
| Property equality | `StatusCode = 500` |
| String comparison | `Application = 'OrderService'` |
| Numeric comparison | `ElapsedMs > 1000` |
| Null check | `UserId is not null` |
| Boolean | `IsAuthenticated` |
| Negation | `not IsAuthenticated` |
| Compound | `StatusCode = 500 and Application = 'OrderService'` |

### String functions

```
Contains(RequestPath, '/api/orders')
StartsWith(Application, 'Order')
EndsWith(CorrelationId, 'abc123')
Like(Message, '%timeout%')
```

### Level filtering

```
@Level = 'Error'
@Level in ['Warning', 'Error']
```

### Time-scoped queries

Use the time range selector in the UI. In filter expressions, `@Timestamp` is available:

```
@Timestamp >= Now() - 1h
```

### Common query patterns

```
# All errors for a specific service
@Level = 'Error' and Application = 'PaymentService'

# Slow HTTP requests
ElapsedMs > 2000 and RequestPath is not null

# Specific user's activity
UserId = 'user-42' and @Level != 'Debug'

# Failed database commands
SourceContext = 'Microsoft.EntityFrameworkCore.Database.Command' and StatusCode = 500

# Events with a specific correlation ID
CorrelationId = 'abc123-def456'
```

---

## Signals

Signals are saved filter expressions that appear as named views in the Seq sidebar. Use them to
create permanent, shared views for common concerns.

### Creating a signal

1. Run a query that produces the desired results
2. Click **Signal** > **Save as Signal**
3. Name it and optionally assign a color

### Recommended signals to create

| Signal Name | Filter Expression |
|-------------|------------------|
| Errors Only | `@Level = 'Error'` |
| Warnings and Above | `@Level in ['Warning', 'Error', 'Fatal']` |
| Slow Requests | `ElapsedMs > 1000` |
| Payment Service | `Application = 'PaymentService'` |
| Unhandled Exceptions | `@Exception is not null` |
| Auth Failures | `EventType = 'AuthFailure' or StatusCode = 401` |

Signals can be combined in the UI using the multi-signal selector to narrow searches interactively
(e.g., "Errors Only" AND "Payment Service").

---

## Dashboards

Dashboards display charts built from Seq queries. They provide at-a-glance metrics derived directly
from structured log data without a separate metrics pipeline.

### Creating a chart

1. Navigate to **Dashboards** > **Add Dashboard**
2. Add a chart, set the query and aggregation:

| Chart Type | Use For | Example Query |
|------------|---------|---------------|
| Count over time | Error rate | `@Level = 'Error'` |
| Mean/Percentile | Latency trends | aggregate on `ElapsedMs` where `ElapsedMs is not null` |
| Count grouped | Errors by service | group by `Application` where `@Level = 'Error'` |

### Useful dashboard charts

```
# Request rate by status code
group by StatusCode

# 95th percentile response time (requires numeric ElapsedMs property)
percentile(ElapsedMs, 95) where ElapsedMs is not null

# Error count by application
count(*) where @Level = 'Error' group by Application
```

---

## API Keys

API keys control access to Seq. Issue a separate key per application or environment.

### Key types

| Type | Purpose |
|------|---------|
| Ingestion-only | Write logs from an application; cannot read events |
| Read/Write | Used by dashboards, integrations, or admin scripts |

### Creating a key

1. Open Seq > **Settings** > **API Keys** > **Add API Key**
2. Set a descriptive title (e.g., `OrderService-Production`)
3. Choose **Ingest only** for application sinks
4. Copy the key — it is only shown once

### Using a key in configuration

```json
{
  "Seq": {
    "ServerUrl": "http://seq:5341",
    "ApiKey": "your-ingestion-key"
  }
}
```

Pass the key via environment variable in production:

```
SEQ__APIKEY=your-ingestion-key
```

---

## Health Endpoint Monitoring

Seq exposes a health check endpoint at `GET /health`. Use it with ASP.NET Core health checks to
verify Seq connectivity before accepting traffic.

```csharp
builder.Services.AddHealthChecks()
    .AddUrlGroup(
        new Uri("http://localhost:5341/health"),
        name: "seq",
        failureStatus: HealthStatus.Degraded,
        tags: ["observability", "logging"]);
```

The endpoint returns HTTP 200 when Seq is healthy. HTTP 503 or a connection failure indicates Seq
is unavailable. Configure this as `Degraded` (not `Unhealthy`) so a Seq outage does not take your
application out of the load balancer rotation.

---

## Alerts

Seq supports alerts that trigger on saved queries.

### Email alerts

1. Install the Seq.App.EmailPlus app from Seq's app store
2. Configure SMTP settings under **Settings** > **Apps**
3. Create an alert on a signal (e.g., "Errors Only") with a threshold and interval

### Webhook alerts

Use the `Seq.App.HttpRequest` app to POST to Slack, Teams, PagerDuty, or any HTTP endpoint.

```json
{
  "Url": "https://hooks.slack.com/services/...",
  "Body": "{{ $Message }}",
  "ContentType": "application/json"
}
```

### Alert best practices

- Set a **suppression window** (e.g., 5 minutes) to avoid alert storms during an outage
- Alert on rate changes, not raw counts, for high-traffic services
- Use signals as alert targets so the same filter drives both the UI view and the alert

---

## Retention Policies

Seq stores events in a local database. Without retention policies, disk usage grows unbounded.

### Configuring retention

**Settings** > **Retention Policies** > **Add Policy**

| Recommended Policy | Retention |
|--------------------|-----------|
| Debug and Verbose | 1 day |
| Information | 7 days |
| Warning | 30 days |
| Error and Fatal | 90 days |

Retention policies are applied per log level. Lower-level events (Debug, Verbose) accumulate
quickly and should be pruned aggressively. Error and Fatal events are small in volume and high
in diagnostic value — retain them longer.

---

## Seq with Docker (Local Development)

```yaml
# docker-compose.yml
services:
  seq:
    image: datalust/seq:latest
    container_name: seq
    environment:
      ACCEPT_EULA: "Y"
    ports:
      - "5341:5341"   # ingestion
      - "8080:80"     # web UI → http://localhost:8080
    volumes:
      - seq-data:/data

volumes:
  seq-data:
```

Start with `docker compose up -d seq`. The web UI is at `http://localhost:8080`. No API key is
required for a single-user local instance unless you configure authentication.

---

## Best Practices

- **One API key per service** — Never share ingestion keys between applications. Revoke and rotate
  keys per service independently.
- **Set `Application` as a global property** — Add it in `appsettings.json` under
  `Serilog.Properties`. Every event then carries a queryable `Application` field.
- **Use meaningful application names** — Match the service name to its deployment identifier
  (e.g., `OrderService`, not `App1`). This makes multi-service dashboards readable.
- **Configure retention policies on first setup** — Do not wait until disk space is exhausted.
  Set policies immediately after installing Seq.
- **Separate Seq instances per environment** — Development, staging, and production should each
  have their own Seq instance to prevent log pollution and allow different retention policies.
- **Index only what you query** — Avoid logging very large object graphs or unbounded collections.
  Destructure selectively with `Destructure.ByTransforming<T>()` to keep event sizes small.
- **Use signals for team-shared views** — Signals defined on the Seq server are visible to all
  users. Create and name them consistently so the whole team navigates the same views.
