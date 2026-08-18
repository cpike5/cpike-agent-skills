# cpike-agent-skills

A multi-plugin Claude Code repository bundling domain-specific skill plugins for development. Each plugin provides a comprehensive knowledge base that Claude Code can invoke on demand — no executable code ships with this repo.

## Plugins

### blazor-skill (v2.3.0)

Blazor UI development knowledge base covering render modes, component lifecycle, forms, state management, JS interop, routing, styling, DI, authentication, security, and design aesthetics. Targets .NET 8+ Blazor with an emphasis on distinctive, non-generic UI output.

**16 docs** — render modes, component lifecycle, forms & validation, state management, components, JS interop, routing & navigation, styling, DI, event handling & performance, auth, design aesthetics, security, external auth providers, two-factor authentication, logging & diagnostics.

### observability-skill (v1.0.0)

.NET observability knowledge base covering structured logging, Serilog, Seq, Elastic APM, OpenTelemetry, APM-log correlation, naming conventions, and instrumentation patterns. Targets .NET 8+ (LTS) with a DI-first approach (`ITracer`, `ILogger<T>`).

**12 docs** — structured logging, Serilog configuration, Serilog sinks, Seq, Elastic logging, Elastic APM, OpenTelemetry, OTel-Elastic integration, APM correlation, naming conventions, instrumentation patterns, observability philosophy.

### elasticsearch-skill (v1.0.0)

Elasticsearch and Kibana knowledge base covering ES 8.x REST API, Query DSL, aggregations, .NET client integration, Kibana APIs, KQL, ECS logging, data streams, ILM, ingest pipelines, and alerting.

**13 docs** — Query DSL, search & pagination, index management, document CRUD, aggregations, .NET client, .NET patterns, Kibana API, Kibana visualizations, KQL syntax, ECS logging, data streams & ILM, ingest & alerting.

### agent-sdk-skill (v1.0.0)

Knowledge base for building Claude-powered AI agents in .NET using the Anthropic C# SDK, covering tool use, agentic loops, streaming, extended thinking, context management, and architecture patterns.

**13 docs** — SDK setup, chat completions, tool use, agentic loops, streaming, extended thinking, context management, system prompts, error handling, multi-cloud deployment, MCP integration, Semantic Kernel, architecture patterns.

### huemint-skill (v1.7.0)

Huemint API knowledge base for generating constraint-based color palettes and building HTML/CSS prototypes that showcase them.

**8 docs** — API basics, adjacency matrices, color locking, model selection, palette refinement, natural language translation, HTML/CSS showcases, advanced patterns.

### mermaid-skill (v1.0.0)

Mermaid diagram generation knowledge base covering syntax, flowcharts, sequence diagrams, class diagrams, state diagrams, ER diagrams, C4, architecture diagrams, git graphs, styling, and .NET architecture patterns.

**11 docs** — flowcharts, sequence diagrams, class diagrams, state diagrams, ER diagrams, C4 diagrams, architecture diagrams, git graphs, styling & theming, .NET patterns, diagram selection guide.

### avalonia-skill (v1.0.0)

Avalonia UI knowledge base for building cross-platform desktop applications with MVVM, styling, theming, data binding, animations, platform integration, and deployment.

**16 docs** — controls, layouts, styling & theming, MVVM, data binding, animations, platform integration, desktop UI design, deployment, dialogs & windowing, data templates, commands & interactions, custom controls, performance, accessibility, testing.

### frontend-design-skill (v1.0.0)

Frontend design knowledge base for engineering distinctive, non-generic interfaces with architectural CSS, editorial typography, and high-fidelity interactions.

**8 docs** — design language selection, architectural typography, advanced CSS layout, surface & depth, motion & micro-interactions, CSS custom property systems, anti-pattern avoidance, implementation workflow.

### roundtable (v1.0.0)

Structured roundtable brainstorming facilitation with a BA chair, domain experts, and user persona panels for feature ideation, UX design, and enhancement planning.

**4 docs** — facilitation framework, expert panel design, user persona panels, session management.

### obsidian-skill (v1.0.0)

Obsidian vault knowledge base for reading, creating, editing, and maintaining Markdown notes safely — frontmatter/properties, wikilinks, embeds, block references, callouts, tags, Dataview, Templater, link integrity, and surgical editing that doesn't break Obsidian-specific syntax.

**1 doc** — syntax & tooling reference (frontmatter, links/embeds/block refs, callouts, tags, formatting extras, Dataview, Templater, git/`.obsidian/`, editing pitfalls).

### html-reports-skill (v1.3.0)

Project report writing — audits, scope reviews, status updates, findings, estimates, schedules, post-mortems. Defaults to Markdown and carries the document structure and writing conventions for both formats; builds a themed, self-contained HTML report when the content needs a Gantt chart, waterfall chart, KPI row, or a client-facing deliverable. Reports are written in simplified English by default — short active sentences, one term per concept, no padding.

**5 docs** — HTML build workflow, theming from the host app's palette, component reference, editorial guidance, and the simplified-English writing rules. Ships `scripts/derive_theme.py` and `scripts/build_report.py` plus the CSS/JS asset library.

## Repository Structure

```
cpike-agent-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace manifest listing all plugins
├── plugins/
│   ├── agent-sdk-skill/
│   ├── avalonia-skill/
│   ├── blazor-skill/
│   ├── elasticsearch-skill/
│   ├── frontend-design-skill/
│   ├── html-reports-skill/
│   ├── huemint-skill/
│   ├── mermaid-skill/
│   ├── observability-skill/
│   ├── obsidian-skill/
│   └── roundtable/
└── CLAUDE.md
```

Each plugin follows the same structure:
```
plugin-name/
├── .claude-plugin/plugin.json    # Plugin manifest with version
├── docs/01-NN.md                 # Numbered knowledge base docs
├── assets/, scripts/             # Optional: templates and helper scripts
└── skills/<name>/SKILL.md        # Skill router with trigger phrases
```

## Installation

Install from the Claude Code plugin marketplace, or add manually by cloning this repo and pointing Claude Code at the plugin directories.

## Contributing

- Each plugin is self-contained under `plugins/<name>/`. Edit within plugin boundaries.
- Docs use sequential numbering (`01-NN`). Preserve ordering when adding new docs.
- New docs must be referenced in the plugin's `SKILL.md` to be discoverable.
- Bump the version in each plugin's `plugin.json` on meaningful changes.
- Update `.claude-plugin/marketplace.json` when adding or removing plugins.
