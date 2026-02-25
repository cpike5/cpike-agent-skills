# Structured Logging in Blazor

## The Core Problem

Blazor's render modes create logging traps that do not exist in classic MVC/Razor Pages: prerendering fires lifecycle methods twice (duplicate log entries), ErrorBoundary swallows exceptions silently, and WASM logs are invisible to server-side infrastructure by default. This doc covers `Microsoft.Extensions.Logging` patterns that work correctly across all render modes. For Serilog sinks, OpenTelemetry exporters, and Elastic APM, see the observability-skill plugin.

---

## ILogger\<T\> in Components

### Razor file injection

```razor
@* Pages/OrderDetail.razor *@
@inject ILogger<OrderDetail> Logger

@code {
    [Parameter] public int OrderId { get; set; }

    protected override async Task OnInitializedAsync()
    {
        Logger.LogInformation("Loading order {OrderId}", OrderId);
        order = await OrderService.GetAsync(OrderId);
    }
}
```

`@inject ILogger<T>` resolves from the DI container. **Always use the component's own type as `T`** — this sets the log category to the fully-qualified component name, making namespace-based filtering precise.

### Code-behind injection

```csharp
// Pages/OrderDetail.razor.cs
public partial class OrderDetail
{
    [Inject] private ILogger<OrderDetail> Logger { get; set; } = default!;
}
```

Or via **primary constructor** (C# 12): `public partial class OrderDetail(ILogger<OrderDetail> logger)`

---

## Avoiding Prerender Noise

`OnInitializedAsync` runs **twice** when prerendering is enabled: once during the static render phase, once when the interactive runtime attaches. Log statements inside it produce identical duplicate entries.

### Guard with RendererInfo.IsInteractive (.NET 9+)

```razor
@* Pages/Dashboard.razor *@
@inject ILogger<Dashboard> Logger

@code {
    protected override async Task OnInitializedAsync()
    {
        if (RendererInfo.IsInteractive)
        {
            // Runs only after interactive runtime is attached — no duplicate
            Logger.LogInformation("Dashboard initialized interactively");
        }

        data = await DashboardService.GetSummaryAsync();
    }
}
```

### Boolean flag via OnAfterRender (pre-.NET 9 fallback)

```razor
@* Pages/Dashboard.razor *@
@inject ILogger<Dashboard> Logger

@code {
    private bool _initialized;

    protected override async Task OnInitializedAsync()
    {
        data = await DashboardService.GetSummaryAsync();
        // Do NOT log here — runs twice
    }

    protected override void OnAfterRender(bool firstRender)
    {
        if (firstRender && !_initialized)
        {
            _initialized = true;
            // OnAfterRender is NOT called during prerendering
            Logger.LogInformation("Dashboard interactive render complete");
        }
    }
}
```

---

## Log Level Guidance

| Level | When to Use | Blazor Examples |
|---|---|---|
| **Trace** | Extremely detailed internal flow; disabled in production | Parameter values entering `SetParametersAsync`, every `ShouldRender` return value |
| **Debug** | Render cycles, state transitions, cache hits/misses | Component mounted, parameter changed, circuit reconnecting |
| **Information** | Meaningful user actions and business events | User logged in, form submitted, page navigated, order placed |
| **Warning** | Degraded state, validation failures, unexpected-but-recoverable situations | API retry triggered, fallback value used, stale cache served, validation rejected |
| **Error** | Unhandled exceptions, failed API calls, circuit errors | `HttpRequestException` from service call, JS interop failure, unhandled exception in `ErrorBoundary` |
| **Critical** | Application cannot continue; rare in Blazor | Catastrophic DI failure at startup, circuit host crash |

**Rule**: Default to **Information** for user-visible actions, **Warning** for recoverable issues, **Error** for caught exceptions. Do not log at **Error** if you handled the condition and returned a fallback.

---

## Structured Logging in Blazor

Use **message templates** with named placeholders. Never use string interpolation — it destroys structured log properties and makes log querying impossible.

### Bad — string interpolation

```csharp
// BAD: properties are lost; logged as a flat string
Logger.LogInformation($"User {userId} submitted form {formName}");
```

### Good — message template

```csharp
// GOOD: UserId and FormName are queryable structured properties
Logger.LogInformation("User {UserId} submitted form {FormName}", userId, formName);
```

### Semantic properties for component context

```csharp
// Pages/CheckoutForm.razor.cs
public partial class CheckoutForm
{
    [Inject] private ILogger<CheckoutForm> Logger { get; set; } = default!;
    [Parameter] public int CartId { get; set; }

    private async Task HandleSubmitAsync(EditContext editContext)
    {
        Logger.LogInformation(
            "Checkout submitted for cart {CartId} by user {UserId}",
            CartId,
            CurrentUser.Id);

        try
        {
            var order = await OrderService.PlaceOrderAsync(CartId);
            Logger.LogInformation(
                "Order {OrderId} created from cart {CartId}",
                order.Id,
                CartId);
        }
        catch (PaymentException ex)
        {
            Logger.LogError(ex,
                "Payment failed for cart {CartId}, provider {Provider}",
                CartId,
                ex.Provider);
        }
    }
}
```

**Conventions**: Use PascalCase placeholders (`{UserId}`, `{OrderId}`). Be consistent across the app for filterability. Include entity IDs, not raw messages.

---

## ErrorBoundary Logging

The default `ErrorBoundary` component catches exceptions and renders fallback UI but **does not log**. Errors disappear silently unless you subclass it.

```csharp
// Components/LoggingErrorBoundary.cs
using Microsoft.AspNetCore.Components.Web;

public class LoggingErrorBoundary : ErrorBoundary
{
    [Inject]
    private ILogger<LoggingErrorBoundary> Logger { get; set; } = default!;

    protected override Task OnErrorAsync(Exception exception)
    {
        Logger.LogError(
            exception,
            "Unhandled exception in component boundary. Component: {ComponentName}",
            CurrentException?.TargetSite?.DeclaringType?.Name ?? "Unknown");

        return Task.CompletedTask;
    }
}
```

```razor
@* Usage — replace <ErrorBoundary> with <LoggingErrorBoundary> *@
<LoggingErrorBoundary>
    <ChildContent>
        <OrderSummary OrderId="@OrderId" />
    </ChildContent>
    <ErrorContent>
        <p class="text-danger">Something went wrong. Please refresh.</p>
    </ErrorContent>
</LoggingErrorBoundary>
```

---

## Circuit Diagnostics

Track Blazor Server circuit lifecycle events for debugging connection issues and per-user session correlation.

```csharp
// Infrastructure/LoggingCircuitHandler.cs
using Microsoft.AspNetCore.Components.Server.Circuits;

public sealed class LoggingCircuitHandler : CircuitHandler
{
    private readonly ILogger<LoggingCircuitHandler> _logger;

    public LoggingCircuitHandler(ILogger<LoggingCircuitHandler> logger)
        => _logger = logger;

    public override Task OnCircuitOpenedAsync(Circuit circuit, CancellationToken ct)
    {
        _logger.LogInformation("Circuit opened. CircuitId: {CircuitId}", circuit.Id);
        return Task.CompletedTask;
    }

    public override Task OnConnectionUpAsync(Circuit circuit, CancellationToken ct)
    {
        _logger.LogDebug("Circuit connection up. CircuitId: {CircuitId}", circuit.Id);
        return Task.CompletedTask;
    }

    public override Task OnConnectionDownAsync(Circuit circuit, CancellationToken ct)
    {
        _logger.LogWarning("Circuit connection lost. CircuitId: {CircuitId}", circuit.Id);
        return Task.CompletedTask;
    }

    public override Task OnCircuitClosedAsync(Circuit circuit, CancellationToken ct)
    {
        _logger.LogInformation("Circuit closed. CircuitId: {CircuitId}", circuit.Id);
        return Task.CompletedTask;
    }
}
```

```csharp
// Program.cs — register as scoped (one per circuit)
builder.Services.AddScoped<CircuitHandler, LoggingCircuitHandler>();
```

---

## WASM Logging Configuration

In Blazor WASM, the default logging provider writes to the **browser developer console**. Log output is invisible to server-side log infrastructure without additional work (see WASM Log Relay below).

### Filter by namespace in wwwroot/appsettings.json

```json
// wwwroot/appsettings.json (loaded automatically by WebAssemblyHostBuilder)
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "MyApp.Client.Pages": "Information",
      "MyApp.Client.Services": "Debug",
      "Microsoft.AspNetCore.Components": "Warning"
    }
  }
}
```

Use `wwwroot/appsettings.Development.json` for environment overrides. Keep `Default` at `Warning` or higher in production — every WASM log entry is a synchronous JS interop call.

---

## WASM Log Relay Pattern

WASM logs are scoped to the browser tab and never reach the server. For production observability, relay client-side logs to a server endpoint that feeds them into the server's logging pipeline.

### Client: HttpLogger and HttpLoggerProvider

```csharp
// Client/Logging/HttpLogEntry.cs
public record HttpLogEntry(
    string Category,
    string Level,
    string Message,
    DateTimeOffset Timestamp,
    string? Exception = null);
```

```csharp
// Client/Logging/HttpLogger.cs
public sealed class HttpLogger(
    string category,
    LogLevel minLevel,
    HttpLoggerProcessor processor) : ILogger
{
    public IDisposable? BeginScope<TState>(TState state) => null;
    public bool IsEnabled(LogLevel logLevel) => logLevel >= minLevel;

    public void Log<TState>(
        LogLevel logLevel,
        EventId eventId,
        TState state,
        Exception? exception,
        Func<TState, Exception?, string> formatter)
    {
        if (!IsEnabled(logLevel)) return;

        processor.Enqueue(new HttpLogEntry(
            category,
            logLevel.ToString(),
            formatter(state, exception),
            DateTimeOffset.UtcNow,
            exception?.ToString()));
    }
}
```

```csharp
// Client/Logging/HttpLoggerProcessor.cs
// Batches entries and flushes on a timer or when the buffer is full.
public sealed class HttpLoggerProcessor : IAsyncDisposable
{
    private readonly HttpClient _http;
    private readonly List<HttpLogEntry> _buffer = [];
    private readonly SemaphoreSlim _lock = new(1, 1);
    private readonly PeriodicTimer _timer = new(TimeSpan.FromSeconds(5));
    private const int MaxBatch = 50;

    public HttpLoggerProcessor(HttpClient http)
    {
        _http = http;
        _ = FlushLoopAsync();
    }

    public void Enqueue(HttpLogEntry entry)
    {
        lock (_buffer)
        {
            _buffer.Add(entry);
            if (_buffer.Count >= MaxBatch)
                _ = FlushAsync();
        }
    }

    private async Task FlushLoopAsync()
    {
        while (await _timer.WaitForNextTickAsync())
            await FlushAsync();
    }

    public async Task FlushAsync()
    {
        List<HttpLogEntry> batch;
        lock (_buffer)
        {
            if (_buffer.Count == 0) return;
            batch = [.._buffer];
            _buffer.Clear();
        }

        try
        {
            await _http.PostAsJsonAsync("/api/logs", batch);
        }
        catch
        {
            // Swallow — avoid infinite logging loops on relay failure
        }
    }

    public async ValueTask DisposeAsync()
    {
        _timer.Dispose();
        await FlushAsync();
    }
}
```

```csharp
// Client/Logging/HttpLoggerProvider.cs
[ProviderAlias("Http")]
public sealed class HttpLoggerProvider(HttpLoggerProcessor processor) : ILoggerProvider
{
    public ILogger CreateLogger(string categoryName)
        => new HttpLogger(categoryName, LogLevel.Warning, processor);

    public void Dispose() { }
}
```

### Client: Program.cs registration

```csharp
// Client/Program.cs
var builder = WebAssemblyHostBuilder.CreateDefault(args);

// Dedicated HttpClient for log relay — use base address of the server
builder.Services.AddSingleton(sp =>
    new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });

builder.Services.AddSingleton<HttpLoggerProcessor>();
builder.Services.AddSingleton<ILoggerProvider, HttpLoggerProvider>();

await builder.Build().RunAsync();
```

### Server: minimal API endpoint

```csharp
// Server/Program.cs (or a separate endpoint file)
app.MapPost("/api/logs", async (
    IReadOnlyList<HttpLogEntry> entries,
    ILoggerFactory loggerFactory) =>
{
    foreach (var entry in entries)
    {
        var logger = loggerFactory.CreateLogger($"WASM.{entry.Category}");
        var level = Enum.TryParse<LogLevel>(entry.Level, out var l) ? l : LogLevel.Information;

        if (logger.IsEnabled(level))
        {
            logger.Log(level, "{Message} (client timestamp: {Timestamp})",
                entry.Message, entry.Timestamp);

            if (entry.Exception is not null)
                logger.Log(level, "Client exception: {Exception}", entry.Exception);
        }
    }

    return Results.NoContent();
});
```

**Design notes**: Timer-based batching (5s) balances freshness with HTTP overhead. `MaxBatch = 50` prevents buffer runaway. Swallow on flush failure to avoid infinite logging loops. Category prefix `WASM.` separates client from server logs. For Serilog sinks or OpenTelemetry exporters on the server endpoint, see the observability-skill plugin.

---

## Common Mistakes

| Mistake | Symptom / Risk | Fix |
|---|---|---|
| String interpolation in log calls: `$"User {id} submitted"` | Structured properties lost; log becomes a flat string; unqueryable in any log backend | Use message templates: `"User {UserId} submitted", userId` |
| Logging sensitive data (passwords, tokens, PII) in message templates | Data appears in plaintext in log sinks, exported traces, and log files | Scrub before logging; log opaque identifiers (`{UserId}`, `{SessionId}`) not raw values |
| Excessive Debug/Trace logging left on in production | High CPU from string formatting, large log volumes, increased cost | Set `Default` log level to `Warning` in production `appsettings.json`; use `IsEnabled` guard for expensive payloads |
| Not guarding `OnInitializedAsync` logs against prerender double-execution | Every log statement inside `OnInitialized` fires twice; confusing duplicate entries | Guard with `RendererInfo.IsInteractive` (.NET 9+) or `OnAfterRender` boolean flag |
| Using the default `<ErrorBoundary>` without logging | Exceptions caught and discarded silently; no trace in logs or monitoring | Subclass `ErrorBoundary`, override `OnErrorAsync`, and log with `Logger.LogError(exception, ...)` |
| Ignoring WASM logs (browser console only) | Client-side errors and warnings are invisible to server-side monitoring and alerting | Implement the WASM Log Relay pattern to POST batched log entries to `/api/logs` |
| Logging inside tight render loops (`BuildRenderTree`, `ShouldRender`) | Severe performance degradation; render-time allocations in hot paths | Move logging to event handlers and lifecycle methods, not render methods |
