# cpike-agent-skills

A multi-plugin Claude Code repository bundling three domain-specific skill plugins for .NET development. Each plugin provides a comprehensive knowledge base that Claude Code can invoke on demand — no executable code ships with this repo.

## Plugins

### blazor-skill (v2.2.0)

Blazor UI development knowledge base covering render modes, component lifecycle, forms, state management, JS interop, routing, styling, DI, authentication, and design aesthetics. Targets .NET 8+ Blazor with an emphasis on distinctive, non-generic UI output.

**12 docs** — render modes, component lifecycle, forms & validation, state management, components, JS interop, routing & navigation, styling, DI, event handling & performance, auth, design aesthetics.

### observability-skill (v1.0.0)

.NET observability knowledge base covering structured logging, Serilog, Seq, Elastic APM, OpenTelemetry, APM-log correlation, naming conventions, and instrumentation patterns. Targets .NET 8+ (LTS) with a DI-first approach (`ITracer`, `ILogger<T>`).

**12 docs** — structured logging, Serilog configuration, Serilog sinks, Seq, Elastic logging, Elastic APM, OpenTelemetry, OTel-Elastic integration, APM correlation, naming conventions, instrumentation patterns, observability philosophy.

### elasticsearch-skill (v1.0.0)

Elasticsearch and Kibana knowledge base covering ES 8.x REST API, Query DSL, aggregations, .NET client integration, Kibana APIs, KQL, ECS logging, data streams, ILM, ingest pipelines, and alerting.

**13 docs** — Query DSL, search & pagination, index management, document CRUD, aggregations, .NET client, .NET patterns, Kibana API, Kibana visualizations, KQL syntax, ECS logging, data streams & ILM, ingest & alerting.

## Repository Structure

```
cpike-agent-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace manifest listing all plugins
├── plugins/
│   ├── blazor-skill/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── docs/01-12.md
│   │   └── skills/blazor/SKILL.md
│   ├── observability-skill/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── docs/01-12.md
│   │   └── skills/observability/SKILL.md
│   └── elasticsearch-skill/
│       ├── .claude-plugin/plugin.json
│       ├── docs/01-13.md
│       └── skills/elasticsearch/SKILL.md
└── CLAUDE.md
```

## Installation

Install from the Claude Code plugin marketplace, or add manually by cloning this repo and pointing Claude Code at the plugin directories.

## Contributing

- Each plugin is self-contained under `plugins/<name>/`. Edit within plugin boundaries.
- Docs use sequential numbering (`01-NN`). Preserve ordering when adding new docs.
- New docs must be referenced in the plugin's `SKILL.md` to be discoverable.
- Bump the version in each plugin's `plugin.json` on meaningful changes.
