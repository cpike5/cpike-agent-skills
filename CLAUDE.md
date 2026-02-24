# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **multi-plugin Claude Code repository** that bundles three skill plugins under a single marketplace manifest. Each plugin provides a domain-specific knowledge base — no executable code ships with this repo.

## Repository Structure

```
cpike-agent-skills/
├── .claude-plugin/
│   └── marketplace.json          # Single marketplace manifest listing all 3 plugins
├── plugins/
│   ├── blazor-skill/             # Blazor UI development knowledge base (12 docs)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── docs/01-12 .md
│   │   └── skills/blazor/SKILL.md
│   ├── observability-skill/      # .NET observability knowledge base (12 docs)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── docs/01-12 .md
│   │   └── skills/observability/SKILL.md
│   └── elasticsearch-skill/      # Elasticsearch & Kibana knowledge base (13 docs)
│       ├── .claude-plugin/plugin.json
│       ├── docs/01-13 .md
│       └── skills/elasticsearch/SKILL.md
├── .gitignore
└── CLAUDE.md
```

## Key Conventions

- **Doc numbering**: Each plugin's `docs/` directory uses sequential numbering (`01-NN`). Preserve ordering when adding new docs.
- **SKILL.md frontmatter**: The `description` field controls when Claude invokes a skill. Keep trigger phrases current.
- **Doc references**: All SKILL.md files use `${CLAUDE_PLUGIN_ROOT}/docs/filename.md` to reference their docs. New docs must be referenced in SKILL.md to be discoverable.
- **Plugin versions**: Tracked individually in each plugin's `.claude-plugin/plugin.json`. Bump on meaningful changes.
- **Marketplace manifest**: `.claude-plugin/marketplace.json` at the repo root lists all plugins. Update it when adding or removing plugins.

## Plugin-Specific Notes

### blazor-skill
- Emphasizes bold, distinctive aesthetics over generic UI
- Covers render modes, lifecycle, forms, state, components, JS interop, routing, styling, DI, auth, design aesthetics
- Target: .NET 8+ Blazor

### observability-skill
- DI-first stance: examples default to `ITracer`, `ILogger<T>` over static accessors
- Covers Serilog, Seq, Elastic APM, OpenTelemetry, APM correlation, naming conventions, instrumentation patterns
- Target: .NET 8+ (LTS)

### elasticsearch-skill
- Covers ES 8.x REST API, .NET client, Kibana APIs, KQL, ECS logging, data streams, ILM, ingest pipelines
- Terse, declarative writing with tables for comparisons

## Editing Guidelines

- Each plugin is self-contained under `plugins/<name>/`. Edit within the plugin boundary.
- When updating patterns, update the relevant `docs/` file and ensure SKILL.md references it.
- Keep SKILL.md files compact — they act as routers, not full references.
- Add detail to `docs/` files, not to SKILL.md.
