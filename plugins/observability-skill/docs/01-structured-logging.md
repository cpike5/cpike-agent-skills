# Structured Logging with Serilog

Reference for Serilog structured logging in .NET 8+ applications. Assumes `ILogger<T>` injection via DI.

---

## Message Templates

Message templates are named placeholders, not format strings. They are the foundation of structured logging because Serilog captures the placeholder name and value as separate fields on the log event.

```csharp
// Correct — "OrderId" becomes a searchable property
_logger.LogInformation("Processing order {OrderId} for customer {CustomerId}", order.Id, order.CustomerId);

// Wrong — string interpolation destroys structure; logged as a plain string
_logger.LogInformation($"Processing order {order.Id} for customer {order.CustomerId}");

// Wrong — string concatenation, same problem
_logger.LogInformation("Processing order " + order.Id + " for customer " + order.CustomerId);
```

The rendered message looks identical in a console, but only the first form produces queryable fields. In Seq you can filter on `OrderId = 42`; with interpolation you cannot.

---

## Semantic Logging vs Text Logging

Semantic (structured) logging attaches machine-readable context. Text logging embeds values inline and requires text parsing to extract them.

**Text logging (avoid):**
```csharp
_logger.LogInformation("User 1042 placed order 9981 worth $149.99 at 2026-02-23T10:00:00Z");
```

**Semantic logging (preferred):**
```csharp
_logger.LogInformation(
    "Order placed for {UserId} worth {OrderTotal:C}",
    userId,
    orderTotal);
```

Resulting log event properties (queryable individually):
```
UserId       = 1042
OrderTotal   = 149.99
Message      = "Order placed for 1042 worth $149.99"
Timestamp    = 2026-02-23T10:00:00Z
```

---

## Log Levels

| Level | When to use | Example |
|-------|-------------|---------|
| `Verbose` | Extremely detailed trace data; off in production | Loop iteration values, raw bytes |
| `Debug` | Developer diagnostics; off in production by default | Method entry/exit, resolved config values |
| `Information` | Normal application milestones | Order placed, user logged in, background job started |
| `Warning` | Unexpected but recoverable conditions | Retry attempted, fallback used, config missing with default |
| `Error` | Operation failed; requires investigation | Unhandled exception, external API failure, DB write failed |
| `Fatal` | Application cannot continue | Cannot connect to DB at startup, missing required secret |

```csharp
_logger.LogDebug("Cache miss for key {CacheKey}, fetching from database", cacheKey);

_logger.LogInformation("Payment processed for order {OrderId}, amount {Amount:C}", orderId, amount);

_logger.LogWarning("Payment gateway timeout on attempt {Attempt} of {MaxAttempts} for order {OrderId}",
    attempt, maxAttempts, orderId);

_logger.LogError(ex, "Failed to charge payment for order {OrderId}", orderId);

_logger.LogCritical("Database connection pool exhausted — application cannot serve requests");
```

> Use `LogError` with the exception as the first argument so Serilog attaches the full exception object (type, message, stack trace) as a structured property, not just the rendered message.

---

## Enrichers

Enrichers add properties to every log event automatically. Configure them in `appsettings.json` or in `UseSerilog()`.

### Built-in Enrichers (`Serilog.Enrichers.Environment`, `Serilog.Enrichers.Thread`)

```json
// appsettings.json
{
  "Serilog": {
    "Enrich": [
      "WithMachineName",
      "WithEnvironmentName",
      "WithThreadId"
    ]
  }
}
```

Produces properties: `MachineName`, `EnvironmentName`, `ThreadId` on every event.

### Correlation ID Enricher (`Serilog.Enrichers.CorrelationId`)

```csharp
// Program.cs — add to HTTP pipeline before Serilog middleware
builder.Services.AddHttpContextAccessor();

builder.Host.UseSerilog((context, services, config) =>
{
    config
        .ReadFrom.Configuration(context.Configuration)
        .ReadFrom.Services(services)
        .Enrich.WithCorrelationId();   // reads X-Correlation-ID header or generates one
});
```

### Custom Enricher

Use `LogContext.PushProperty` for request-scoped values (e.g., tenant ID from a claim):

```csharp
// Middleware — push once, available on all events within the request
public class TenantLoggingMiddleware
{
    private readonly RequestDelegate _next;

    public TenantLoggingMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context)
    {
        var tenantId = context.User.FindFirstValue("tenant_id");

        using (LogContext.PushProperty("TenantId", tenantId))
        {
            await _next(context);
        }
    }
}
```

For application-wide static enrichment, implement `ILogEventEnricher`:

```csharp
public class AppVersionEnricher : ILogEventEnricher
{
    private readonly string _version;

    public AppVersionEnricher(string version) => _version = version;

    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory factory)
    {
        logEvent.AddPropertyIfAbsent(
            factory.CreateProperty("AppVersion", _version));
    }
}

// Registration
config.Enrich.With(new AppVersionEnricher("2.4.1"));
```

---

## Structured Properties and Destructuring Operators

When logging an object, the operator before the placeholder name controls how Serilog captures it.

| Operator | Syntax | Behavior |
|----------|--------|----------|
| None (scalar) | `{ProductId}` | Calls `.ToString()` on the value |
| Destructure | `{@Order}` | Captures all public properties as a nested structure |
| Stringify | `{$Status}` | Forces `.ToString()` even on complex types |

```csharp
var order = new Order { Id = 42, Total = 99.99m, Status = OrderStatus.Pending };

// Scalar — logs "42" (ToString on the int Id, not the whole object)
_logger.LogInformation("Order ID: {OrderId}", order.Id);

// Destructure — logs { Id: 42, Total: 99.99, Status: "Pending" } as a nested object
_logger.LogInformation("Order created: {@Order}", order);

// Stringify — logs the ToString() representation of the whole object
_logger.LogInformation("Order state: {$Order}", order);
```

### Controlling Destructuring Depth

Destructuring captures all public properties recursively by default. For large objects, use a destructuring policy or project only what you need:

```csharp
// Project to an anonymous type — log only relevant fields
_logger.LogInformation("Order created: {@OrderSummary}", new
{
    order.Id,
    order.Total,
    order.Status
});
```

---

## Property Naming Conventions

- Use **PascalCase** for all property names: `OrderId`, `UserId`, `RequestPath`
- Be **consistent across services** — `UserId` everywhere, not `userId`, `user_id`, or `UserID`
- Use **domain vocabulary** — `OrderId` not `Id`, `PaymentAmount` not `Amount`
- Avoid generic names that collide with Serilog built-ins: `Message`, `Timestamp`, `Level`, `Exception`

---

## Common Mistakes and Anti-Patterns

### 1. String Interpolation in Templates

```csharp
// WRONG — the template is a fixed string; interpolation evaluates before Serilog sees it
_logger.LogInformation($"User {userId} logged in");

// Correct
_logger.LogInformation("User {UserId} logged in", userId);
```

### 2. Logging Sensitive Data

```csharp
// WRONG — password, token, and connection string in log properties
_logger.LogDebug("Authenticating user {Username} with password {Password}", username, password);
_logger.LogDebug("Connecting with {ConnectionString}", connString);

// Correct — omit sensitive values entirely; log only safe identifiers
_logger.LogDebug("Authenticating user {Username}", username);
_logger.LogInformation("Database connection established for catalog {DatabaseName}", dbName);
```

Do not log: passwords, API keys, tokens, connection strings, PII (email, phone, SSN), credit card numbers.

### 3. Repeating Context Properties on Every Call

```csharp
// WRONG — TenantId repeated on every log call in the request
_logger.LogInformation("Order placed {OrderId} tenant {TenantId}", orderId, tenantId);
_logger.LogInformation("Payment initiated {OrderId} tenant {TenantId}", orderId, tenantId);

// Correct — push once via LogContext in middleware
using (LogContext.PushProperty("TenantId", tenantId))
{
    _logger.LogInformation("Order placed {OrderId}", orderId);
    _logger.LogInformation("Payment initiated {OrderId}", orderId);
}
```

### 4. Swallowing the Exception Object

```csharp
// WRONG — exception detail becomes part of the message string only
_logger.LogError("Payment failed: " + ex.Message);

// Correct — pass exception as the first argument for full structured capture
_logger.LogError(ex, "Payment failed for order {OrderId}", orderId);
```

### 5. Logging at the Wrong Level

```csharp
// WRONG — a handled 404 is not an error
_logger.LogError("Product {ProductId} not found", productId);

// Correct — not found is a normal condition, log as Warning or Information
_logger.LogWarning("Product {ProductId} not found in catalog", productId);
```

### 6. Over-Logging in Hot Paths

Do not log inside tight loops or per-item in a bulk operation. Log a summary after the operation:

```csharp
// WRONG — one log event per order in a batch of thousands
foreach (var order in orders)
{
    _logger.LogInformation("Processing order {OrderId}", order.Id);
    Process(order);
}

// Correct — log the batch summary
_logger.LogInformation("Processing batch of {OrderCount} orders", orders.Count);
foreach (var order in orders)
    Process(order);
_logger.LogInformation("Batch complete. Succeeded: {Succeeded}, Failed: {Failed}", succeeded, failed);
```

### 7. Using `{@}` on Large Object Graphs

Destructuring with `{@}` on an EF entity or response DTO can serialize hundreds of properties and child collections. Always project to an anonymous type or use a destructuring policy.

---

## Quick Reference

```csharp
// Inject
public class OrderService
{
    private readonly ILogger<OrderService> _logger;

    public OrderService(ILogger<OrderService> logger) => _logger = logger;
}

// Template — named placeholders, no interpolation
_logger.LogInformation("Order {OrderId} placed by {UserId}", order.Id, userId);

// Exception — exception is always the first argument
_logger.LogError(ex, "Failed to process order {OrderId}", orderId);

// Destructure — project to avoid over-capture
_logger.LogDebug("Request received: {@RequestSummary}", new { req.Method, req.Path, req.ContentLength });

// Scoped enrichment — push at entry point, available throughout the call chain
using (LogContext.PushProperty("CorrelationId", correlationId))
{
    await ProcessAsync();
}
```
