# Serilog Sinks Reference

Sinks are the output destinations for Serilog. A logger can write to one or many sinks simultaneously. This document covers the standard sinks for .NET 8+ applications, configuration patterns, output formatting, and performance considerations.

---

## NuGet Packages

| Sink | Package |
|------|---------|
| Console | `Serilog.Sinks.Console` |
| File | `Serilog.Sinks.File` |
| Seq | `Serilog.Sinks.Seq` |
| Elasticsearch | `Serilog.Sinks.Elasticsearch` |
| Async wrapper | `Serilog.Sinks.Async` |

Install example:

```bash
dotnet add package Serilog.Sinks.Console
dotnet add package Serilog.Sinks.File
dotnet add package Serilog.Sinks.Seq
dotnet add package Serilog.Sinks.Elasticsearch
dotnet add package Serilog.Sinks.Async
```

---

## Sink Configuration in Code

Configure sinks on `LoggerConfiguration` using the fluent API. All sinks are registered via `WriteTo`.

```csharp
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .WriteTo.Console()
    .WriteTo.File("logs/app.log", rollingInterval: RollingInterval.Day)
    .WriteTo.Seq("http://localhost:5341")
    .CreateLogger();
```

In an ASP.NET Core host, use `UseSerilog()` in `Program.cs`:

```csharp
builder.Host.UseSerilog((context, services, configuration) =>
{
    configuration
        .ReadFrom.Configuration(context.Configuration)
        .ReadFrom.Services(services)
        .Enrich.FromLogContext()
        .WriteTo.Console()
        .WriteTo.Seq(context.Configuration["Seq:ServerUrl"]!);
});
```

---

## Sink Configuration in appsettings.json

The `Serilog.Settings.Configuration` package enables full sink configuration via `appsettings.json`. This is the preferred approach for environment-specific configuration.

```json
{
  "Serilog": {
    "Using": [
      "Serilog.Sinks.Console",
      "Serilog.Sinks.File",
      "Serilog.Sinks.Seq"
    ],
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
        "Name": "Console",
        "Args": {
          "outputTemplate": "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}"
        }
      },
      {
        "Name": "File",
        "Args": {
          "path": "logs/app-.log",
          "rollingInterval": "Day",
          "retainedFileCountLimit": 14,
          "fileSizeLimitBytes": 104857600,
          "buffered": false
        }
      },
      {
        "Name": "Seq",
        "Args": {
          "serverUrl": "http://localhost:5341",
          "apiKey": ""
        }
      }
    ],
    "Enrich": ["FromLogContext", "WithMachineName", "WithThreadId"]
  }
}
```

---

## Multiple Sinks

Serilog writes to all configured sinks for every log event that passes the minimum level filter. No additional configuration is needed — chain `WriteTo` calls.

```csharp
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .WriteTo.File("logs/app-.log", rollingInterval: RollingInterval.Day)
    .WriteTo.Seq("http://localhost:5341")
    .WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri("http://localhost:9200"))
    {
        IndexFormat = "app-logs-{0:yyyy.MM.dd}",
        AutoRegisterTemplate = true
    })
    .CreateLogger();
```

Use `WriteTo.Logger()` to create a sub-logger with independent filtering — for example, writing only errors to a file while sending everything to Seq:

```csharp
Log.Logger = new LoggerConfiguration()
    .WriteTo.Seq("http://localhost:5341")
    .WriteTo.Logger(lc => lc
        .Filter.ByIncludingOnly(e => e.Level >= LogEventLevel.Error)
        .WriteTo.File("logs/errors-.log", rollingInterval: RollingInterval.Day))
    .CreateLogger();
```

---

## Console Sink

### Output Templates

Plain-text output uses an output template. Properties are referenced by name in curly braces.

```csharp
.WriteTo.Console(
    outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {SourceContext} {Message:lj}{NewLine}{Exception}")
```

Common template tokens:

| Token | Description |
|-------|-------------|
| `{Timestamp:HH:mm:ss}` | Local time with format |
| `{Level:u3}` | Level as 3-char uppercase (INF, WRN, ERR) |
| `{SourceContext}` | Logger name (usually the class name) |
| `{Message:lj}` | Rendered message; `:lj` renders objects as JSON |
| `{Properties:j}` | All extra properties as JSON |
| `{Exception}` | Exception message and stack trace |
| `{NewLine}` | Platform newline |

### Themes

```csharp
using Serilog.Sinks.SystemConsole.Themes;

.WriteTo.Console(theme: AnsiConsoleTheme.Code)
```

Available built-in themes: `AnsiConsoleTheme.Code`, `AnsiConsoleTheme.Grayscale`, `AnsiConsoleTheme.Literate`, `SystemConsoleTheme.Literate`, `SystemConsoleTheme.Grayscale`.

---

## File Sink

### Rolling Intervals

```csharp
.WriteTo.File(
    path: "logs/app-.log",
    rollingInterval: RollingInterval.Day,    // new file each day
    retainedFileCountLimit: 14,              // keep last 14 files
    fileSizeLimitBytes: 100 * 1024 * 1024,  // 100 MB per file
    rollOnFileSizeLimit: true)               // roll when size limit hit
```

Rolling interval options: `Infinite`, `Year`, `Month`, `Day`, `Hour`, `Minute`.

The path must include a placeholder (`-`) where the date/counter is inserted: `logs/app-.log` becomes `logs/app-20260223.log`.

### Buffered File Writes

Set `buffered: true` to reduce I/O at the cost of potential data loss on crash:

```csharp
.WriteTo.File("logs/app-.log", rollingInterval: RollingInterval.Day, buffered: true)
```

Use buffered mode only when log throughput is high and losing a small number of events on crash is acceptable. For audit trails or critical logs, leave `buffered: false` (default).

---

## Async Wrapper

The async wrapper offloads sink writes to a background thread, preventing log I/O from blocking request threads.

```csharp
.WriteTo.Async(a => a.File("logs/app-.log", rollingInterval: RollingInterval.Day))
.WriteTo.Async(a => a.Seq("http://localhost:5341"))
```

### When to Use Async

- Wrap file sinks in production where log volume is high.
- Wrap Seq or Elasticsearch sinks to avoid blocking on network calls.
- Do not wrap the Console sink in development — synchronous output is easier to read during debugging.

### Async Buffer Size

The default in-memory buffer is 10,000 events. If the sink falls behind and the buffer fills, events are dropped (not blocked). Increase the buffer for burst-heavy workloads:

```csharp
.WriteTo.Async(a => a.File("logs/app-.log"), bufferSize: 50000)
```

### appsettings.json — Async Wrapper

```json
{
  "Serilog": {
    "Using": ["Serilog.Sinks.Async", "Serilog.Sinks.File"],
    "WriteTo": [
      {
        "Name": "Async",
        "Args": {
          "configure": [
            {
              "Name": "File",
              "Args": {
                "path": "logs/app-.log",
                "rollingInterval": "Day"
              }
            }
          ]
        }
      }
    ]
  }
}
```

---

## Output Formatting

### Plain Text (Output Template)

Default for Console and File. Configured via `outputTemplate` — see Console section above.

### CompactJsonFormatter

Writes each event as a single-line JSON object. Machine-readable and efficient for log shippers.

```csharp
using Serilog.Formatting.Compact;

.WriteTo.File(new CompactJsonFormatter(), "logs/app-.json", rollingInterval: RollingInterval.Day)
.WriteTo.Console(new CompactJsonFormatter())
```

Sample output:
```json
{"@t":"2026-02-23T10:00:00.000Z","@mt":"Order {OrderId} submitted","@l":"Information","OrderId":42,"SourceContext":"OrderService"}
```

### RenderedCompactJsonFormatter

Identical to `CompactJsonFormatter` but includes the pre-rendered message string as `@m`. Useful when the consuming system does not support Serilog message template rendering.

```csharp
using Serilog.Formatting.Compact;

.WriteTo.File(new RenderedCompactJsonFormatter(), "logs/app-.json", rollingInterval: RollingInterval.Day)
```

### Elasticsearch-Specific Formatter

When sending to Elasticsearch use `ElasticsearchJsonFormatter` to produce ECS-compatible documents:

```csharp
using Serilog.Sinks.Elasticsearch;

.WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri("http://localhost:9200"))
{
    IndexFormat = "app-logs-{0:yyyy.MM.dd}",
    AutoRegisterTemplate = true,
    AutoRegisterTemplateVersion = AutoRegisterTemplateVersion.ESv7,
    CustomFormatter = new ElasticsearchJsonFormatter()
})
```

---

## Buffered and Durable Sinks

### Durable File Sink

The standard file sink loses buffered events on crash. For durable delivery, use the durable file sink (requires `Serilog.Sinks.File` with `durable: true` option not available natively — use `Serilog.Sinks.RollingFile` with a log shipper, or rely on the async wrapper with `blockWhenFull: true`).

For guaranteed delivery, write to file with `CompactJsonFormatter` and ship with Filebeat or a similar agent.

### Durable Seq Sink

The Seq sink supports a durable (disk-buffered) mode that stores events locally before forwarding, preventing loss during Seq downtime:

```csharp
.WriteTo.DurableSeqUsingFileSizeRolledBuffers(
    serverUrl: "http://localhost:5341",
    bufferBaseFilename: "logs/seq-buffer",
    bufferFileSizeLimitBytes: 50 * 1024 * 1024,
    retainedBufferFileCountLimit: 5)
```

This requires the standard `Serilog.Sinks.Seq` package (v5+). Use when Seq availability is not guaranteed (network partitions, rolling deployments).

### Durable Elasticsearch Sink

```csharp
.WriteTo.DurableElasticsearchWithFileSizeRolledBuffers(
    new ElasticsearchSinkOptions(new Uri("http://localhost:9200"))
    {
        IndexFormat = "app-logs-{0:yyyy.MM.dd}",
        BufferBaseFilename = "logs/elastic-buffer",
        BufferFileSizeLimitBytes = 50 * 1024 * 1024,
        RetainedInvalidPayloadsLimitBytes = 5 * 1024 * 1024
    })
```

---

## Performance Considerations

| Concern | Recommendation |
|---------|---------------|
| High log throughput | Wrap file and network sinks with `Async` |
| Network sink latency | Always wrap Seq and Elasticsearch with `Async` |
| Disk I/O on hot paths | Use `buffered: true` on File sink or async wrapper |
| Buffer overflow (dropped events) | Increase `bufferSize` on async wrapper; monitor drop rate |
| Guaranteed delivery | Use durable sink variants; accept higher disk I/O |
| Development iteration | Use Console sink without async for immediate output |
| Structured querying | Prefer `CompactJsonFormatter` for file output; send to Seq/Elasticsearch |

### Batch Size Tuning (Elasticsearch)

```csharp
new ElasticsearchSinkOptions(new Uri("http://localhost:9200"))
{
    BatchAction = ElasticOpType.Index,
    BatchPostingLimit = 50,           // events per batch
    Period = TimeSpan.FromSeconds(2)  // flush interval
}
```

### Avoiding Sink Overhead in Tight Loops

Serilog evaluates the minimum level before constructing the log event. Keep minimum levels appropriately high for noisy namespaces (see `MinimumLevel.Override` in appsettings.json above) to avoid allocating log event objects that are immediately discarded.

---

## See Also

- `docs/02-serilog-configuration.md` — `UseSerilog()`, minimum level overrides, enrichers, `ReadFrom.Configuration`
- `docs/04-seq.md` — Seq sink setup, API keys, Seq-specific querying
- `docs/05-elastic-logging.md` — Elasticsearch sink, ECS formatting, index lifecycle management
