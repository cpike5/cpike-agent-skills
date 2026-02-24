---
name: observability
description: "Use this skill when implementing .NET observability, logging, tracing, or metrics. Covers Serilog (structured logging, message templates, enrichers, sinks), Seq (querying, signals, dashboards), Elastic APM (native agent, ITracer, transactions, spans, distributed tracing), OpenTelemetry (ActivitySource, Meter, OTLP exporters), APM-log correlation (trace.id injection, W3C TraceContext), naming conventions (transaction names, span names, metric names, avoiding high-cardinality), and instrumentation patterns (middleware, action filters, IHttpClientFactory, EF Core, background services). Targets .NET 8+ (LTS). Prefers DI-first approach (ITracer, ILogger<T>) over static accessors. Invoke when: configuring Serilog or logging pipeline, setting up Elastic APM or OpenTelemetry, adding manual instrumentation (transactions, spans, activities), correlating logs with traces, debugging observability issues (missing traces, broken correlation, high-cardinality names), or when the user asks about logging, tracing, metrics, or monitoring patterns."
---

# .NET Observability Knowledge Base

You are implementing observability for a .NET application. Read the relevant reference docs below based on what you're building. **Always use DI-first patterns** — inject `ITracer`, `ILogger<T>`, etc. rather than using static accessors.

## Observability Philosophy

Good observability answers three questions: **What happened?** (logs), **Where did it happen?** (traces), **How much?** (metrics). Every signal should be correlated — a single request should be traceable across logs, spans, and metrics via trace context. See `12-observability-philosophy.md` for the full framework.

## Quick Decision: Which Signal Type?

- Need to understand a specific request's journey? → **Distributed Tracing** (Elastic APM or OpenTelemetry)
- Need to debug unexpected behavior or errors? → **Structured Logging** (Serilog → Seq / Elasticsearch)
- Need to track rates, durations, or resource usage? → **Metrics** (OpenTelemetry Meters or Elastic APM)
- Need all three correlated? → **APM + Serilog with trace context enrichment** (see doc 09)

## Reference Documentation

Read the relevant docs based on your task:

### Logging Foundation (start here for logging)
- ${CLAUDE_PLUGIN_ROOT}/docs/01-structured-logging.md — Message templates, semantic logging, enrichers, log levels, destructuring
- ${CLAUDE_PLUGIN_ROOT}/docs/02-serilog-configuration.md — appsettings.json config, UseSerilog(), minimum level overrides, IServiceCollection registration
- ${CLAUDE_PLUGIN_ROOT}/docs/03-serilog-sinks.md — Console, File, Seq, Elasticsearch sinks, async wrappers, formatting

### Log Destinations
- ${CLAUDE_PLUGIN_ROOT}/docs/04-seq.md — Seq sink setup, querying, signals, dashboards, API keys, health checks
- ${CLAUDE_PLUGIN_ROOT}/docs/05-elastic-logging.md — Elasticsearch sink, ECS formatting, index naming, ILM, data streams

### APM & Tracing
- ${CLAUDE_PLUGIN_ROOT}/docs/06-elastic-apm.md — Native Elastic APM agent, ITracer (DI-first), transactions, spans, distributed tracing, W3C propagation
- ${CLAUDE_PLUGIN_ROOT}/docs/07-opentelemetry.md — OTel .NET SDK, ActivitySource, Activity spans, Meter/Counter/Histogram, OTLP exporters
- ${CLAUDE_PLUGIN_ROOT}/docs/08-otel-elastic-integration.md — OTel-to-Elastic export, feature comparison, migration path, config mapping

### Correlation & Conventions
- ${CLAUDE_PLUGIN_ROOT}/docs/09-apm-correlation.md — Log-trace correlation, trace.id injection, Serilog enrichers, cross-service trace visualization
- ${CLAUDE_PLUGIN_ROOT}/docs/10-naming-conventions.md — Transaction naming, span naming, metric naming, PascalCase properties, avoiding high-cardinality

### Patterns & Philosophy
- ${CLAUDE_PLUGIN_ROOT}/docs/11-instrumentation-patterns.md — Middleware, action filters, health check exclusion, sampling, IHttpClientFactory, EF Core, error capture
- ${CLAUDE_PLUGIN_ROOT}/docs/12-observability-philosophy.md — Three pillars, anti-patterns, alert hygiene, signal selection

## Critical Rules

1. **Never use string interpolation in message templates** — Use `Log.Information("Processing order {OrderId}", orderId)` not `Log.Information($"Processing order {orderId}")`. Interpolation defeats structured logging.
2. **Always null-check `CurrentTransaction`** — `_tracer.CurrentTransaction` can be null when no transaction is active (background threads, startup code). Always guard: `_tracer.CurrentTransaction?.StartSpan(...)`.
3. **Always null-check `Activity.Current`** — `Activity.Current` is null when no listener is registered or no parent activity exists. Always guard before accessing properties.
4. **Always close spans/transactions in try/finally or using blocks** — Unclosed spans leak memory and corrupt trace trees. Use `try/finally { span.End(); }` or the `using` pattern.
5. **Always capture exceptions on spans before ending them** — Call `span.CaptureException(ex)` or `activity?.SetStatus(ActivityStatusCode.Error)` in the catch block, before the finally block ends the span.
6. **Never log sensitive data** — PII, passwords, tokens, connection strings must never appear in log properties. Use `[LogMasked]` attributes or custom destructuring policies.
7. **Always propagate trace context across service boundaries** — HTTP calls automatically propagate W3C traceparent headers when using `IHttpClientFactory`. For message queues, manually inject/extract trace context.
8. **Avoid high-cardinality transaction/metric names** — Never include user IDs, order IDs, or GUIDs in transaction names. Use route templates (`GET /api/orders/{id}`) not resolved paths (`GET /api/orders/12345`).
9. **Use DI-first, static as fallback** — Inject `ITracer` and `ILogger<T>` via constructor injection. Only use `Agent.Tracer` or `Serilog.Log.Logger` in non-DI contexts (startup, static helpers).
10. **Always set minimum level overrides for noisy namespaces** — Suppress `Microsoft.AspNetCore` to Warning, `System.Net.Http` to Warning, `Microsoft.EntityFrameworkCore.Database.Command` to Warning (or Information if you need query logging).
11. **Use `LogContext.PushProperty` for request-scoped enrichment** — Don't repeat the same property on every log call. Push it once at the middleware/filter level.
12. **Never fire-and-forget without trace context** — Background work (`Task.Run`, `IHostedService`) loses ambient trace context. Explicitly capture and restore `Activity.Current` or start a new transaction linked to the parent.
