# Serilog Configuration Reference

.NET 8+ configuration patterns for Serilog. All examples use the DI-first approach.

---

## appsettings.json Structure

The canonical `Serilog` section controls the logging pipeline without requiring code changes per environment.

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
        "Microsoft": "Warning",
        "Microsoft.AspNetCore": "Warning",
        "Microsoft.EntityFrameworkCore.Database.Command": "Warning",
        "System.Net.Http": "Warning",
        "System": "Warning"
      }
    },
    "WriteTo": [
      { "Name": "Console" },
      {
        "Name": "File",
        "Args": {
          "path": "logs/app-.log",
          "rollingInterval": "Day",
          "retainedFileCountLimit": 14,
          "outputTemplate": "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}"
        }
      },
      {
        "Name": "Seq",
        "Args": { "serverUrl": "http://localhost:5341" }
      }
    ],
    "Enrich": [
      "FromLogContext",
      "WithMachineName",
      "WithThreadId",
      "WithEnvironmentName"
    ],
    "Properties": {
      "Application": "MyApp"
    }
  }
}
```

Key fields:

| Field | Purpose |
|---|---|
| `Using` | Assembly names to load sinks from. Required for JSON-configured sinks. |
| `MinimumLevel.Default` | Global floor level. |
| `MinimumLevel.Override` | Per-namespace overrides. More specific namespaces win. |
| `WriteTo` | Sink pipeline — processed in order. |
| `Enrich` | Enrichers applied to every event. Requires matching `Serilog.Enrichers.*` package. |
| `Properties` | Static key-value pairs added to every event. |

---

## Minimum Level Overrides

Always suppress noisy framework namespaces. Overrides are prefix-matched — the longest matching prefix wins.

```json
"MinimumLevel": {
  "Default": "Information",
  "Override": {
    "Microsoft":                                    "Warning",
    "Microsoft.AspNetCore":                         "Warning",
    "Microsoft.AspNetCore.Hosting.Diagnostics":     "Information",
    "Microsoft.EntityFrameworkCore":                "Warning",
    "Microsoft.EntityFrameworkCore.Database.Command": "Information",
    "System":                                       "Warning",
    "System.Net.Http":                              "Warning"
  }
}
```

`Microsoft.AspNetCore.Hosting.Diagnostics` is re-enabled at `Information` to retain request start/end events while suppressing everything else under `Microsoft.AspNetCore`.

---

## Environment-Specific Overrides

`appsettings.{Environment}.json` is merged over the base file. Only declare the keys that differ.

**appsettings.Development.json** — verbose local logging, no file sink needed:

```json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Debug",
      "Override": {
        "Microsoft.EntityFrameworkCore.Database.Command": "Information",
        "Microsoft": "Information"
      }
    },
    "WriteTo": [
      {
        "Name": "Console",
        "Args": {
          "theme": "Serilog.Sinks.SystemConsole.Themes.AnsiConsoleTheme::Code, Serilog.Sinks.Console",
          "outputTemplate": "[{Timestamp:HH:mm:ss} {Level:u3}] {SourceContext}{NewLine}  {Message:lj}{NewLine}{Exception}"
        }
      },
      {
        "Name": "Seq",
        "Args": { "serverUrl": "http://localhost:5341" }
      }
    ]
  }
}
```

**appsettings.Production.json** — structured JSON output, no local Seq:

```json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information"
    },
    "WriteTo": [
      { "Name": "Console" },
      {
        "Name": "File",
        "Args": {
          "path": "/var/log/myapp/app-.json",
          "rollingInterval": "Day",
          "formatter": "Serilog.Formatting.Compact.CompactJsonFormatter, Serilog.Formatting.Compact"
        }
      }
    ]
  }
}
```

---

## UseSerilog() vs AddSerilog()

| Method | Where | Replaces | Use When |
|---|---|---|---|
| `UseSerilog()` | `IHostBuilder` | .NET default logging entirely | Standard apps. Preferred — bootstrap logger pattern works cleanly here. |
| `AddSerilog()` | `IServiceCollection` | Only the `ILogger` DI registration | Integrating into an existing DI container where the host is not yours (e.g., Azure Functions v4 with custom host). |

**Prefer `UseSerilog()`** for all standard ASP.NET Core and Worker Service applications. It hooks into the host lifetime so Serilog flushes on graceful shutdown.

---

## IServiceCollection Registration Pattern

`AddSerilog()` is used when you must register inside `ConfigureServices` rather than on the host builder. Wire up the `ILogger` adapter so DI consumers receive Serilog-backed instances.

```csharp
// Only use this pattern when UseSerilog() is not an option.
builder.Services.AddSerilog(lc => lc
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext());
```

---

## Complete Program.cs — Recommended Setup

Two-stage initialization protects startup errors from being swallowed before Serilog is fully configured.

```csharp
using Serilog;
using Serilog.Events;

// Stage 1 — bootstrap logger captures startup errors before full config loads.
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Information)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .CreateBootstrapLogger();

try
{
    Log.Information("Starting application");

    var builder = WebApplication.CreateBuilder(args);

    // Stage 2 — replace bootstrap logger with the fully-configured logger.
    builder.Host.UseSerilog((context, services, configuration) =>
        configuration
            .ReadFrom.Configuration(context.Configuration)   // appsettings.json + overrides
            .ReadFrom.Services(services)                     // allows sinks/enrichers from DI
            .Enrich.FromLogContext()
    );

    builder.Services.AddControllers();
    // ... other registrations

    var app = builder.Build();

    // Add Serilog request logging middleware.
    // Place after exception handlers but before routing/auth.
    app.UseSerilogRequestLogging(options =>
    {
        options.MessageTemplate =
            "HTTP {RequestMethod} {RequestPath} responded {StatusCode} in {Elapsed:0.0000} ms";

        // Attach additional per-request properties.
        options.EnrichDiagnosticContext = (diagnosticContext, httpContext) =>
        {
            diagnosticContext.Set("RequestHost", httpContext.Request.Host.Value);
            diagnosticContext.Set("RequestScheme", httpContext.Request.Scheme);
        };
    });

    app.MapControllers();

    await app.RunAsync();
    return 0;
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
    return 1;
}
finally
{
    // Flush and close on exit — critical for async sinks (Seq, Elasticsearch).
    await Log.CloseAndFlushAsync();
}
```

### Why Two-Stage Initialization

| Stage | Logger | Captures |
|---|---|---|
| Bootstrap | `CreateBootstrapLogger()` | Configuration load failures, DI registration errors, host build exceptions |
| Final | `ReadFrom.Configuration(...)` | All application log events with full pipeline |

Without stage 1, any exception thrown before `UseSerilog()` completes is written only to the default .NET console logger (no structured output, no Seq).

`ReadFrom.Services(services)` in stage 2 enables sinks and enrichers that are themselves registered in DI — required for Elastic APM log correlation enrichers and custom sink implementations.

---

## Filter Expressions (Serilog.Expressions)

Install `Serilog.Expressions` to filter by structured property values in `appsettings.json`.

```json
"WriteTo": [
  {
    "Name": "Seq",
    "Args": {
      "serverUrl": "http://localhost:5341",
      "controlLevelSwitch": "$controlSwitch"
    }
  }
],
"Filter": [
  {
    "Name": "ByExcluding",
    "Args": {
      "expression": "RequestPath like '/health%'"
    }
  },
  {
    "Name": "ByExcluding",
    "Args": {
      "expression": "@l = 'Debug' and SourceContext like 'Microsoft%'"
    }
  }
]
```

Expression operators: `=`, `<>`, `like` (wildcard `%`), `not`, `and`, `or`. Property access uses the structured property name directly (e.g., `StatusCode`, `RequestPath`, `SourceContext`). `@l` is the built-in level token.

---

## Required NuGet Packages

| Package | Purpose |
|---|---|
| `Serilog.AspNetCore` | `UseSerilog()`, `UseSerilogRequestLogging()` |
| `Serilog.Settings.Configuration` | `ReadFrom.Configuration()` |
| `Serilog.Expressions` | Filter expressions in config |
| `Serilog.Enrichers.Environment` | `WithMachineName()`, `WithEnvironmentName()` |
| `Serilog.Enrichers.Thread` | `WithThreadId()` |
| `Serilog.Formatting.Compact` | `CompactJsonFormatter` for structured file output |

Sinks are covered in `03-serilog-sinks.md`.
