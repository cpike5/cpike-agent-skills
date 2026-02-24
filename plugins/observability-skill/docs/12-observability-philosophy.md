# Observability Philosophy — .NET Applications

Strategic principles and decision frameworks for building observable .NET systems. This document is intentionally light on code; see the numbered reference docs for implementation details.

---

## The Three Pillars

Observability is built on three complementary signal types. Each answers a different question.

| Pillar | Central question | Strength | Weakness |
|--------|-----------------|----------|----------|
| **Logs** | What happened at this moment? | Rich, freeform context per event | Hard to correlate across services; expensive at volume |
| **Traces** | How did this request flow through the system? | End-to-end visibility; latency breakdown per span | Require instrumentation at every hop; sampling loses detail |
| **Metrics** | How is the system behaving over time? | Low cost; ideal for alerting and trending | No per-request context; cardinality limits what you can label |

Use all three together. A spike in the error-rate metric tells you *something is wrong*. A trace shows you *which service and operation*. A log shows you *exactly what failed and why*.

---

## The Goal

> **Any request that passed through any service should be fully reconstructable from observability data, without needing to reproduce the issue.**

This means:

- A correlation ID (trace ID) present on every log event and every outbound HTTP header
- Spans that capture the critical operations within each service, linked across service boundaries
- Metrics that reflect the health of those operations in aggregate
- All three signals queryable in one place, or at minimum cross-linked by trace ID

If you cannot answer "what happened to request X?" from your tooling without SSH access to a server, your observability is incomplete.

---

## Anti-Patterns

### Log-and-Forget

Logging unstructured text strings with embedded values, then never querying those logs.

**What it looks like:** `_logger.LogInformation($"Order {id} failed");`

**Why it matters:** The value is unindexed. You cannot filter, aggregate, or correlate it. Logs become write-only artifacts.

### No Correlation

Log events exist but cannot be tied to a specific request or trace. Each service logs in isolation.

**What it looks like:** No `CorrelationId` or `TraceId` property on log events; `X-Correlation-ID` header not forwarded between services.

**Why it matters:** You can see that something failed, but you cannot reconstruct the request path that caused it. Debugging requires guesswork.

### Excessive Verbosity at Information Level

Logging every method entry, every loop iteration, or every cache check at `Information`. The signal drowns in noise.

**Why it matters:** High event volume increases storage cost, slows query tools, and — most critically — makes real errors invisible. `Information` should mark meaningful milestones, not execution steps. Use `Debug` or `Verbose` for diagnostics that should be off in production.

### Metric Cardinality Explosion

Using high-cardinality values (user IDs, order IDs, request paths with parameters) as metric label dimensions.

**What it looks like:** A counter labeled with `userId` that grows by one unique series per user.

**Why it matters:** Metrics systems (Prometheus, Elastic APM) store one time series per unique label combination. Unbounded cardinality exhausts memory, corrupts dashboards, and crashes metric stores. Metric labels must use bounded enumerations: service name, environment, status code, operation name.

### Alert Fatigue

Too many alerts, too many false positives, too little context. Teams learn to ignore them.

**Why it matters:** When a real incident fires, it blends into background noise. Alert fatigue is an observability failure with operational consequences. Fewer, higher-confidence alerts are always preferable to comprehensive but noisy coverage.

### Observability as Afterthought

Adding instrumentation after a production incident, rather than before. Treating it as infrastructure work separate from feature development.

**Why it matters:** You cannot debug what you did not instrument. Retroactive instrumentation means the next incident occurs before you have data. Instrumentation belongs in the definition of done for every feature and every service.

---

## What Good Observability Looks Like

- **Any request is traceable end-to-end.** Given a trace ID, you can reconstruct the full path across every service that touched the request, with latency at each hop.
- **Errors surface automatically with full context.** An unhandled exception carries the trace ID, user context, request details, and inner exception — without requiring a developer to add log statements after the fact.
- **Performance regressions are visible before users complain.** Latency percentile metrics and slow-span detection catch degradations in minutes, not days.
- **Dashboards answer real questions.** "What is our p95 checkout latency?" and "How many payment failures occurred in the last hour?" — not vanity metrics like raw request count with no baseline.
- **Alerts are actionable and owned.** Every alert has a known owner, a runbook, and a clear action. Alerts that have fired with no response in the last 30 days are candidates for removal.

---

## Alert Hygiene

Every alert should satisfy all four of these conditions before it goes to production:

| Property | Question to answer |
|----------|--------------------|
| **Owner** | Which team or person is responsible for responding? |
| **Runbook** | Is there a documented set of steps to investigate and resolve this? |
| **Action** | Is there a concrete thing the responder can do? Alerts that end in "monitor the situation" are noise. |
| **Expected frequency** | How often should this alert fire in normal operation? If the answer is "never," what is the escalation path when it does? |

Alerts with no runbook get ignored. Alerts with no owner get silenced. Alerts that fire constantly train teams to disable them. Review alert history quarterly and retire anything that has not driven a meaningful action.

---

## Signal Selection — Deciding What to Instrument

Not everything is worth instrumenting. The cost of instrumentation is real: developer time, runtime overhead, storage, and cognitive load on anyone reading the data.

Apply the **80/20 rule**: identify the 20% of operations that represent 80% of user-visible risk and instrument those thoroughly. Everything else gets baseline coverage.

### Start with user-facing boundaries

Instrument every HTTP request in and out, every message consumed from a queue, and every background job execution. These are the entry points where problems manifest for users.

### Instrument what you cannot retry or replay

Database writes, payment calls, email sends, and external API calls that have side effects. If these fail silently, you have a data integrity problem, not just a performance problem.

### Skip what you can derive

If you log every HTTP response with status code and duration, you do not need a separate log event for "request completed." If you capture a span around a database call, you do not also need a log event for every SQL statement unless you are debugging.

### Let errors guide coverage gaps

After any production incident, ask: "What data did we wish we had?" That is where to add instrumentation next. Do not add it everywhere preemptively.

---

## Cost Awareness

Observability data is not free. Every log event, span, and metric series has a cost in storage, network, and processing. Being intentional about what you emit is part of being a good steward of infrastructure.

| Signal | Primary cost driver | Mitigation |
|--------|--------------------|----|
| Logs | Volume (events per second × average event size) | Raise minimum level to `Warning` in production for noisy namespaces; use sampling for `Debug` |
| Traces | Span volume; trace storage | Head-based sampling (e.g., 10% of requests) with guaranteed capture of errors and slow requests |
| Metrics | Cardinality (number of unique label combinations) | Audit label dimensions; remove high-cardinality labels; use histograms instead of raw value recording |

A common misconfiguration is leaving `Microsoft.EntityFrameworkCore.Database.Command` at `Information` in production, logging every SQL statement. This can easily 10x log volume with low diagnostic value.

---

## Observability Maturity Model

Use this to assess where a system currently sits and what the next step is. Progress is incremental — do not attempt to jump from Level 0 to Level 4.

| Level | Description | Key capabilities | What you can answer |
|-------|-------------|-----------------|---------------------|
| **0** | Console or file logging with `Console.WriteLine` or `Debug.WriteLine` | Local only; no structure; no persistence | "What happened on my machine" |
| **1** | Structured logging with named properties (`ILogger<T>` + Serilog) | Machine-readable fields; consistent log levels; exception capture | "What happened in this service" |
| **2** | Centralized and searchable (Seq, Elasticsearch, Application Insights) | All services write to one place; full-text and property search; retention policies | "What happened across services at time T" |
| **3** | Correlated traces and logs (OpenTelemetry, Elastic APM) | Trace IDs on every log event; spans linked across service boundaries; distributed trace view | "What happened to this specific request" |
| **4** | Full observability: metrics, alerting, dashboards, SLOs | Latency/error/saturation metrics; actionable alerts with runbooks; dashboards answering operational questions; SLO tracking | "Is the system healthy right now, and will it be healthy tomorrow?" |

Most .NET applications in active development should target Level 3. Level 4 is appropriate for services with defined SLOs and on-call ownership. Level 2 is a reasonable minimum for any system in production.

> Reaching Level 4 is not a one-time project. It is a practice maintained through code review, incident retrospectives, and periodic review of alerts and dashboards.
