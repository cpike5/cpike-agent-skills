# Desktop Observability

Observability patterns specific to desktop applications. For foundational patterns (structured logging conventions, Serilog pipeline configuration, Elastic APM, OpenTelemetry, and naming conventions), **see the observability-skill plugin** -- those patterns apply directly. This doc focuses on what is different for desktop.

---

## Serilog Setup for Desktop

Desktop apps do not have an HTTP request pipeline or a web host. Wire Serilog in `Program.cs` before building the Avalonia app.

### Log File Location

**Always** write logs to the platform-appropriate local app data folder. Never write to the install directory (it may be read-only or sandboxed).

```csharp
var logPath = Path.Combine(
    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
    "MyApp",
    "logs",
    "app-.log");
```

### Full Bootstrap Example

```csharp
using Serilog;
using Serilog.Events;

public static class Program
{
    [STAThread]
    public static void Main(string[] args)
    {
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .MinimumLevel.Override("Avalonia", LogEventLevel.Warning)
            .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
            .Enrich.FromLogContext()
            .Enrich.WithProperty("Application", "MyApp")
            .Enrich.WithProperty("AppVersion", typeof(Program).Assembly
                .GetName().Version?.ToString() ?? "0.0.0")
            .Enrich.WithProperty("MachineName", Environment.MachineName)
            .Enrich.WithProperty("OSVersion", Environment.OSVersion.ToString())
            .WriteTo.Async(a => a.File(   // Async wrapper prevents UI thread blocking
                Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "MyApp", "logs", "app-.log"),
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 14,
                outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}] {Message:lj}{NewLine}{Exception}"))
            .WriteTo.Seq("http://localhost:5341")  // local dev only
            .CreateLogger();

        Log.Information("Application starting");

        // Global exception handlers
        AppDomain.CurrentDomain.UnhandledException += (_, e) =>
        {
            Log.Fatal((Exception)e.ExceptionObject, "Unhandled domain exception");
            Log.CloseAndFlush();
        };

        TaskScheduler.UnobservedTaskException += (_, e) =>
        {
            Log.Error(e.Exception, "Unobserved task exception");
            e.SetObserved();
        };

        try
        {
            BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);
        }
        catch (Exception ex)
        {
            Log.Fatal(ex, "Application terminated unexpectedly");
            throw;
        }
        finally
        {
            Log.CloseAndFlush();
        }
    }

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .LogToTrace();
}
```

**Key packages**:

| Package | Purpose |
|---------|---------|
| `Serilog` | Core library |
| `Serilog.Sinks.File` | Rolling file output |
| `Serilog.Sinks.Async` | Async wrapper to prevent UI blocking |
| `Serilog.Sinks.Seq` | Seq ingestion (local dev) |
| `Serilog.Enrichers.Environment` | Machine name, OS |

### Why WriteTo.Async()

File I/O blocks the calling thread. In a desktop app, logging on the UI thread without `Async()` causes micro-stutters during scrolling and interaction. **Always** wrap file sinks with `WriteTo.Async()`.

---

## Crash Reporting

### Capturing All Unhandled Exceptions

Wire three handlers to cover every exception source:

```csharp
// 1. Any thread (non-Task)
AppDomain.CurrentDomain.UnhandledException += (_, e) =>
{
    var ex = (Exception)e.ExceptionObject;
    WriteCrashDump(ex);
    Log.Fatal(ex, "Unhandled domain exception");
    Log.CloseAndFlush();
};

// 2. Fire-and-forget async
TaskScheduler.UnobservedTaskException += (_, e) =>
{
    Log.Error(e.Exception, "Unobserved task exception");
    e.SetObserved();
};

// 3. ReactiveUI pipelines (if using ReactiveUI)
RxApp.DefaultExceptionHandler = Observer.Create<Exception>(ex =>
{
    Log.Error(ex, "Unhandled exception in reactive pipeline");
});
```

### Writing a Crash Dump

Write a simple crash file that persists even if the logging pipeline fails.

```csharp
private static void WriteCrashDump(Exception ex)
{
    try
    {
        var crashDir = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "MyApp", "crashes");
        Directory.CreateDirectory(crashDir);

        var crashFile = Path.Combine(crashDir,
            $"crash-{DateTime.UtcNow:yyyyMMdd-HHmmss}.txt");

        var content = $"""
            Timestamp: {DateTime.UtcNow:O}
            OS: {Environment.OSVersion}
            Runtime: {Environment.Version}
            App Version: {typeof(Program).Assembly.GetName().Version}

            {ex}
            """;

        File.WriteAllText(crashFile, content);
    }
    catch
    {
        // Last resort — crash dump itself failed. Nothing we can do.
    }
}
```

### Telemetry Opt-In

**Never** send crash data or telemetry without user consent. Show a dialog on first run.

```csharp
public partial class TelemetryConsentViewModel : ObservableObject
{
    [ObservableProperty]
    private bool _crashReportingEnabled;

    [ObservableProperty]
    private bool _usageTelemetryEnabled;

    [RelayCommand]
    private void SavePreferences()
    {
        _settingsService.Set("CrashReporting", CrashReportingEnabled);
        _settingsService.Set("UsageTelemetry", UsageTelemetryEnabled);
    }
}
```

---

## Performance Diagnostics

### Startup Time

Measure from process start to first window render.

```csharp
public static class Program
{
    private static readonly Stopwatch StartupTimer = Stopwatch.StartNew();

    [STAThread]
    public static void Main(string[] args)
    {
        // ... Serilog setup ...
        BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);
    }

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .AfterSetup(_ =>
            {
                Log.Information("Avalonia initialized in {ElapsedMs}ms",
                    StartupTimer.ElapsedMilliseconds);
            });
}
```

Log the total startup time when the main window renders:

```csharp
// In MainWindow code-behind
protected override void OnOpened(EventArgs e)
{
    base.OnOpened(e);
    Log.Information("Main window opened in {ElapsedMs}ms",
        Program.StartupTimer.ElapsedMilliseconds);
    Program.StartupTimer.Stop();
}
```

### Instrumenting Long Operations

Use `ILogger` with `Stopwatch` for operations that may affect perceived performance.

```csharp
public class DataService : IDataService
{
    private readonly ILogger<DataService> _logger;

    public async Task<List<Item>> LoadItemsAsync(CancellationToken ct)
    {
        var sw = Stopwatch.StartNew();
        try
        {
            var items = await _repository.GetAllAsync(ct);
            _logger.LogInformation("Loaded {Count} items in {ElapsedMs}ms",
                items.Count, sw.ElapsedMilliseconds);
            return items;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load items after {ElapsedMs}ms",
                sw.ElapsedMilliseconds);
            throw;
        }
    }
}
```

---

## User Session Context Enrichment

Desktop apps have no HTTP request context. Enrich logs with machine and session information instead.

### Custom Enricher

```csharp
using Serilog.Core;
using Serilog.Events;

public class DesktopContextEnricher : ILogEventEnricher
{
    private readonly LogEventProperty _appVersion;
    private readonly LogEventProperty _osVersion;
    private readonly LogEventProperty _machineName;
    private readonly LogEventProperty _screenResolution;
    private readonly LogEventProperty _runtime;

    public DesktopContextEnricher()
    {
        var version = typeof(DesktopContextEnricher).Assembly
            .GetName().Version?.ToString() ?? "0.0.0";

        _appVersion = new LogEventProperty("AppVersion", new ScalarValue(version));
        _osVersion = new LogEventProperty("OSVersion",
            new ScalarValue(Environment.OSVersion.ToString()));
        _machineName = new LogEventProperty("MachineName",
            new ScalarValue(Environment.MachineName));
        _runtime = new LogEventProperty("Runtime",
            new ScalarValue(Environment.Version.ToString()));

        // Screen resolution — get primary screen
        _screenResolution = new LogEventProperty("ScreenResolution",
            new ScalarValue("unknown"));  // set after Avalonia initializes
    }

    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory factory)
    {
        logEvent.AddPropertyIfAbsent(_appVersion);
        logEvent.AddPropertyIfAbsent(_osVersion);
        logEvent.AddPropertyIfAbsent(_machineName);
        logEvent.AddPropertyIfAbsent(_runtime);
        logEvent.AddPropertyIfAbsent(_screenResolution);
    }
}
```

Register it:

```csharp
Log.Logger = new LoggerConfiguration()
    .Enrich.With<DesktopContextEnricher>()
    // ... sinks
    .CreateLogger();
```

### Session-Level Properties

Push per-session properties that persist across all log entries for that session.

```csharp
// On app startup, after user authentication
using (LogContext.PushProperty("SessionId", Guid.NewGuid()))
using (LogContext.PushProperty("UserRole", currentUser.Role))  // role, not name
{
    // All logs within this scope include SessionId and UserRole
}
```

---

## Offline-First Telemetry

Desktop apps are not always connected. Buffer logs locally and upload when connectivity allows.

### Durable Seq Sink

Seq's sink has a built-in durable buffer that writes to disk when the server is unreachable, then replays when connectivity returns.

```csharp
.WriteTo.Seq(
    "https://seq.mycompany.com",
    bufferBaseFilename: Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "MyApp", "logs", "seq-buffer"),  // durable buffer on disk
    retainedInvalidPayloadsLimitBytes: 5_000_000,  // 5 MB cap
    period: TimeSpan.FromSeconds(10))  // batch interval
```

### Log Rotation

Prevent disk bloat with `retainedFileCountLimit` and `fileSizeLimitBytes`.

```csharp
.WriteTo.Async(a => a.File(
    logPath,
    rollingInterval: RollingInterval.Day,
    retainedFileCountLimit: 14,          // keep 2 weeks
    fileSizeLimitBytes: 50_000_000,      // 50 MB per file max
    rollOnFileSizeLimit: true))
```

---

## OpenTelemetry for Desktop

Use OpenTelemetry to trace background operations and export metrics when the app is online.

### Setup in DI

```csharp
using OpenTelemetry;
using OpenTelemetry.Trace;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;

private static void ConfigureServices(IServiceCollection services)
{
    services.AddOpenTelemetry()
        .ConfigureResource(r => r
            .AddService(
                serviceName: "MyApp.Desktop",
                serviceVersion: typeof(Program).Assembly
                    .GetName().Version?.ToString() ?? "0.0.0")
            .AddAttributes(new Dictionary<string, object>
            {
                ["deployment.environment"] = "production",
                ["host.name"] = Environment.MachineName,
                ["os.description"] = Environment.OSVersion.ToString()
            }))
        .WithTracing(t => t
            .AddSource("MyApp.*")          // match your ActivitySource names
            .AddHttpClientInstrumentation()
            .AddOtlpExporter(o =>
            {
                o.Endpoint = new Uri("https://otel.mycompany.com");
            }))
        .WithMetrics(m => m
            .AddMeter("MyApp.*")
            .AddProcessInstrumentation()   // CPU, memory, GC
            .AddOtlpExporter());
}
```

### Custom Traces

```csharp
using System.Diagnostics;

public class FileExportService
{
    private static readonly ActivitySource Activity = new("MyApp.FileExport");

    public async Task ExportAsync(string path, CancellationToken ct)
    {
        using var span = Activity.StartActivity("ExportToFile");
        span?.SetTag("file.path", SanitizePath(path));  // no PII in paths

        // ... export logic
        span?.SetTag("file.size_bytes", new FileInfo(path).Length);
    }
}
```

### Custom Metrics

```csharp
using System.Diagnostics.Metrics;

public class AppMetrics
{
    private static readonly Meter Meter = new("MyApp.Desktop");

    // Counters for user actions
    public static readonly Counter<long> CommandExecuted =
        Meter.CreateCounter<long>("app.command.executed");

    // Gauge for active windows
    public static readonly UpDownCounter<int> ActiveWindows =
        Meter.CreateUpDownCounter<int>("app.windows.active");

    // Histogram for operation duration
    public static readonly Histogram<double> OperationDuration =
        Meter.CreateHistogram<double>("app.operation.duration_ms");
}
```

---

## Connecting to Shared Observability Backend

Use the **same** Seq or Elastic APM instance that your web services use. Distinguish desktop telemetry with the `Application` property.

```csharp
.Enrich.WithProperty("Application", "MyApp.Desktop")  // vs "MyApp.Api", "MyApp.Worker"
```

Follow the naming conventions from the observability-skill plugin. Consistent property names (`Application`, `Environment`, `MachineName`) let you filter and correlate across desktop and server logs in the same dashboard.

### Querying in Seq

```
Application = 'MyApp.Desktop' and @Level = 'Error'
```

### Querying in Kibana (KQL)

```
service.name: "MyApp.Desktop" and log.level: "error"
```

---

## Privacy Considerations

Desktop telemetry is **different** from server-side logging. You are logging from a user's personal machine.

### Rules

| Rule | Rationale |
|------|-----------|
| No PII in logs | Usernames, emails, file paths with user folders are PII |
| Sanitize file paths | Replace user directory with placeholder |
| Opt-in only | Crash reporting and telemetry require explicit user consent |
| Allow opt-out at any time | Settings panel toggle, takes effect immediately |
| Data deletion | Provide a way to clear local logs and request server-side deletion |
| Minimize collection | Only collect what you need to diagnose issues |

### Path Sanitization

```csharp
public static string SanitizePath(string path)
{
    // Replace user profile directory with placeholder
    var userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
    if (path.StartsWith(userProfile, StringComparison.OrdinalIgnoreCase))
        return path.Replace(userProfile, "~");

    return path;
}
```

### Respecting User Preferences

```csharp
// Check consent before enabling remote sinks
var config = new LoggerConfiguration()
    .WriteTo.Async(a => a.File(logPath,  // always log locally
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 14));

if (settings.CrashReportingEnabled)
{
    config = config.WriteTo.Seq("https://seq.mycompany.com",
        restrictedToMinimumLevel: LogEventLevel.Error);  // errors only
}

if (settings.UsageTelemetryEnabled)
{
    config = config.WriteTo.Seq("https://seq.mycompany.com");  // all levels
}

Log.Logger = config.CreateLogger();
```

**Never** silently enable telemetry. If a user has not opted in, local file logging only.
