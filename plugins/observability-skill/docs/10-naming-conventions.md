# Naming Conventions for .NET Observability

Reference for consistent naming of transactions, spans, metrics, and log properties across Serilog, Elastic APM, and OpenTelemetry in .NET 8+ applications.

---

## Why Naming Consistency Matters

APM tools group transactions, aggregate metrics, and build dashboards based on names. Inconsistent names fragment your data — the same logical operation appears as dozens of unrelated entries. Consistent naming means:

- Transaction throughput and error rates roll up correctly
- Dashboards reflect real traffic patterns
- Alerting rules cover entire operation classes, not individual instances

---

## Transaction Naming

Transactions represent the top-level unit of work: an HTTP request, a background job run, or a message consumed.

### HTTP Endpoints — Route-Based (Preferred)

Use the **route template**, not the resolved URL. Route templates are low-cardinality; resolved URLs are not.

```text
Good:  GET /api/orders/{id}
Good:  POST /api/orders
Good:  DELETE /api/customers/{customerId}/addresses/{addressId}

Bad:   GET /api/orders/12345          -- specific ID leaks into the name
Bad:   GET /api/orders/99999          -- now a separate transaction in APM
Bad:   GET /api/orders/search?q=boots -- query strings create unbounded cardinality
```

Elastic APM and the OpenTelemetry ASP.NET Core instrumentation both capture the route template automatically when using attribute routing or minimal API route patterns. No custom code is needed.

### HTTP Endpoints — Controller-Based Naming

When route templates are unavailable or you prefer a code-centric label:

```text
OrderController.GetById
OrderController.Create
PaymentController.Charge
CustomerController.ListAddresses
```

Format: `{ControllerName}.{ActionName}` — omit the `Controller` suffix only if your APM tool strips it automatically (Elastic APM does not strip it by default).

### Background Jobs

Name jobs after the logical work being performed, not the scheduler mechanism:

```text
ProcessPaymentJob
SendOrderConfirmationEmailJob
ReconcileInventoryJob
PurgeExpiredSessionsJob
```

In Elastic APM, set the transaction name explicitly when using Hangfire or a hosted service:

```csharp
// Hangfire — set in IJobActivator or the job method attribute is not enough
[DisplayName("ProcessPaymentJob")]
public class ProcessPaymentJob(IElasticApm apm) : IJob
{
    public async Task Execute(IJobExecutionContext context)
    {
        await apm.Tracer.CaptureTransaction("ProcessPaymentJob", "backgroundjob", async t =>
        {
            // job work here
        });
    }
}

// IHostedService / Worker — start the transaction manually
public async Task DoWorkAsync(CancellationToken ct)
{
    await _apm.Tracer.CaptureTransaction("ReconcileInventoryJob", "backgroundjob", async t =>
    {
        await ReconcileAsync(ct);
    });
}
```

### Message Handlers

Use `Handle{EventName}` to make the consumed message type obvious in the transaction list:

```text
HandleOrderCreatedEvent
HandlePaymentFailedEvent
HandleInventoryReservedEvent
HandleCustomerRegisteredEvent
```

---

## Span Naming

Spans are child operations within a transaction. Names should identify the operation type and target without embedding variable data.

### Database Spans

```text
db.query SELECT orders
db.query OrderRepository.GetById
db.query INSERT payments
db.query PaymentRepository.Create
db.execute sp_RecalculateInventory
```

OTel semantic conventions use `db.operation` + `db.sql.table` as attributes rather than embedding them in the span name. When naming custom spans, follow the pattern `db.{operation} {target}` where target is either the table name or the repository method — not an ID.

```csharp
// Custom span around a raw query
using var span = _tracer.StartSpan("db.query OrderRepository.GetById");
var order = await _db.Orders.FindAsync(orderId);
span.End();
```

### Outbound HTTP Spans

```text
HTTP GET api.stripe.com
HTTP POST hooks.slack.com
HTTP GET api.github.com
```

Format: `HTTP {METHOD} {host}` — use the host only, never the full URL with path parameters or query strings.

The `System.Net.Http` OpenTelemetry instrumentation (`OpenTelemetry.Instrumentation.Http`) generates these names automatically. Do not override them unless the host is a generic load balancer where the downstream service name is more meaningful.

### Custom Business Logic Spans

Use a `{domain}.{operation}` dot-separated hierarchy:

```text
process.validate-order
process.calculate-tax
cache.get orders:{id}
cache.set orders:{id}
email.send order-confirmation
payment.tokenize-card
pdf.render invoice
```

The `{id}` placeholder in cache key spans is acceptable only if your APM tool treats it as a template — use literal `{id}` or `:id`, not the resolved value.

```csharp
// OpenTelemetry custom span
using var activity = _activitySource.StartActivity("process.validate-order");
activity?.SetTag("order.id", orderId);
activity?.SetTag("order.item_count", itemCount);
ValidateOrder(order);
```

---

## Metric Naming Conventions

### Hierarchy with Dots

Use dot notation to create a hierarchy from general to specific:

```text
http.server.request.duration
http.server.request.count
http.client.request.duration
db.query.duration
db.connection.pool.size
messaging.consumer.message.count
cache.hit.count
cache.miss.count
```

### Units

Include units in the metric name **or** via instrument unit metadata — not both.

```text
// Unit in the name (acceptable when your APM does not support unit metadata)
http.server.request.duration.ms
db.query.duration.ms
job.execution.duration.s

// Unit as metadata (preferred with OTel — cleaner names, unit carried in the instrument)
http.server.request.duration   (unit: "ms")
db.query.duration              (unit: "ms")
```

With the .NET Metrics API:

```csharp
// Unit in instrument definition — do not repeat it in the name
var requestDuration = _meter.CreateHistogram<double>(
    name: "http.server.request.duration",
    unit: "ms",
    description: "Duration of HTTP server requests");

// Consistent tags — low-cardinality only
requestDuration.Record(elapsed.TotalMilliseconds, new TagList
{
    { "http.method", method },
    { "http.route", routeTemplate },   // template, not resolved URL
    { "http.status_code", statusCode }
});
```

### OTel Semantic Conventions Alignment

The OpenTelemetry project publishes [semantic conventions](https://opentelemetry.io/docs/specs/semconv/) for common metric and span names. Where a convention exists, use it — it enables out-of-the-box dashboard compatibility.

| Semantic convention name | Unit | Description |
|---|---|---|
| `http.server.request.duration` | `s` | Server-side HTTP request latency |
| `http.client.request.duration` | `s` | Client-side outbound HTTP latency |
| `db.client.operation.duration` | `s` | Database operation latency |
| `messaging.client.operation.duration` | `s` | Messaging publish/consume latency |
| `process.runtime.dotnet.gc.duration` | `s` | .NET GC pause duration |

Use `s` (seconds) as the unit for durations in OTel-native metrics; convert to milliseconds only at the dashboard layer.

---

## Log Property Naming Conventions

### PascalCase for All Serilog Properties

Serilog property names appear as fields in Seq and Elastic. Use PascalCase consistently:

```csharp
// Correct
_logger.LogInformation("Order {OrderId} placed by {UserId}, total {OrderTotal:C}",
    order.Id, userId, order.Total);

_logger.LogWarning("Payment retry {AttemptNumber} of {MaxAttempts} for order {OrderId}",
    attempt, maxAttempts, orderId);

_logger.LogError(ex, "Job {JobName} failed after {ElapsedMs}ms", jobName, elapsed.TotalMilliseconds);

// Wrong — inconsistent casing breaks cross-service queries
_logger.LogInformation("Order {orderId} placed by {user_id}", order.Id, userId);
_logger.LogInformation("Order {order_id} total {orderTotal}", order.Id, order.Total);
```

### Common Property Name Standards

Establish these names once and use them everywhere across all services:

| Property | Type | Notes |
|---|---|---|
| `OrderId` | `int` / `Guid` | Not `Id`, not `order_id` |
| `UserId` | `int` / `Guid` | Not `UserID`, not `userId` |
| `TenantId` | `int` / `Guid` | Pushed via middleware `LogContext` |
| `CorrelationId` | `string` | Matches `X-Correlation-ID` header |
| `ElapsedMs` | `double` | Milliseconds, not `Duration` or `Elapsed` |
| `StatusCode` | `int` | HTTP status code |
| `RequestPath` | `string` | Route template, not resolved path |
| `JobName` | `string` | Background job type name |
| `AttemptNumber` | `int` | Current retry count |
| `MaxAttempts` | `int` | Configured retry limit |
| `ExceptionType` | `string` | Use when logging exception type without full exception object |

Do not use Serilog reserved names as property names: `Message`, `Timestamp`, `Level`, `Exception`, `Properties`.

---

## Avoiding High-Cardinality Names

### What High Cardinality Means

Cardinality is the number of distinct values a field or name can take. A field with 5 possible values is low-cardinality. A field that contains an order ID, user ID, or GUID has cardinality equal to the number of records in your system — potentially millions.

APM tools index transaction names, span names, and metric tag values. High-cardinality names cause:

- **Index bloat** — millions of distinct entries in the transactions index
- **Dashboard breakdown** — charts become unreadable; aggregation is meaningless
- **Query degradation** — time-series stores slow down significantly under high-cardinality tag sets
- **Cost** — many SaaS APM platforms charge per unique series; high cardinality multiplies cost directly

### Concrete Examples

| Scenario | Bad (high cardinality) | Good (low cardinality) |
|---|---|---|
| HTTP transaction name | `GET /api/orders/98732` | `GET /api/orders/{id}` |
| HTTP transaction name | `GET /api/search?q=red+shoes&page=3` | `GET /api/search` |
| Span name | `db.query SELECT * FROM orders WHERE id = 98732` | `db.query SELECT orders` |
| Span name | `cache.get orders:98732` | `cache.get orders:{id}` |
| Metric tag | `{ user_id: "u-99812" }` | omit — never tag metrics with user IDs |
| Metric tag | `{ endpoint: "/api/orders/98732" }` | `{ route: "/api/orders/{id}" }` |
| Log property used as metric dimension | `RequestPath = "/api/orders/12345"` | `RouteName = "GetOrderById"` |

### What Is Safe to Use as a Tag or Name

- HTTP method (`GET`, `POST`) — ~5 values
- HTTP status code — ~20 values used in practice
- HTTP route template — bounded by the number of routes in your API
- Environment (`production`, `staging`) — ~3 values
- Service name — bounded by the number of services
- Job type name — bounded by the number of job classes
- Boolean flags (`is_retry`, `cache_hit`) — 2 values

---

## Grouping Strategy

APM tools group transactions by name to build service maps, latency histograms, and error rate charts. The name is the grouping key.

If `GET /api/orders/12345` and `GET /api/orders/67890` are two distinct names, they produce two rows in your APM transaction list with 1 sample each. If they are both `GET /api/orders/{id}`, they produce one row with accurate aggregate statistics.

Design names to group by **operation type**, not by **operation instance**.

Background jobs and message handlers are naturally low-cardinality — `ProcessPaymentJob` runs many times but always carries the same name. The job parameters (order ID, amount) belong as span tags or log properties, not in the transaction name.

---

## Naming Cheat Sheet

| Signal | Pattern | Example |
|---|---|---|
| HTTP transaction | `{METHOD} {route template}` | `GET /api/orders/{id}` |
| Controller transaction | `{Controller}.{Action}` | `OrderController.GetById` |
| Background job transaction | `{JobTypeName}` | `ProcessPaymentJob` |
| Message handler transaction | `Handle{EventName}` | `HandleOrderCreatedEvent` |
| DB span | `db.query {operation} {table}` | `db.query SELECT orders` |
| DB span (repo style) | `db.query {Repo}.{Method}` | `db.query OrderRepository.GetById` |
| Outbound HTTP span | `HTTP {METHOD} {host}` | `HTTP POST api.stripe.com` |
| Custom business span | `{domain}.{operation}` | `process.validate-order` |
| Cache span | `cache.{op} {entity}:{param}` | `cache.get orders:{id}` |
| Metric name | `{system}.{subsystem}.{name}` | `http.server.request.duration` |
| Metric unit (in name) | append `.{unit}` | `http.server.request.duration.ms` |
| Log property | PascalCase noun phrase | `OrderId`, `ElapsedMs`, `TenantId` |

**Never embed resolved IDs, user data, or query string values in transaction names, span names, or metric tag values.**
