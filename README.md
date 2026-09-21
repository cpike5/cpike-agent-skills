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

### html-reports-skill (v1.4.0)

Project report writing — audits, scope reviews, status updates, findings, estimates, schedules, post-mortems. Defaults to Markdown and carries the document structure and writing conventions for both formats; builds a themed, self-contained HTML report when the content needs a Gantt chart, waterfall chart, schema or architecture diagram, KPI row, or a client-facing deliverable. Reports are written in simplified English by default — short active sentences, one term per concept, no padding.

**5 docs** — HTML build workflow, theming from the host app's palette, component reference, editorial guidance, and the simplified-English writing rules. Ships `scripts/derive_theme.py`, `scripts/build_report.py` and `scripts/rasterize.py` (screenshots the built report so the visuals get looked at) plus the CSS/JS asset library.

### project-setup-skill (v1.0.0)

Project setup and onboarding — what a repository needs before an agent session is productive in it, and the order to install it in. Covers `CLAUDE.md`, the `SessionStart` hook and the local-dev-environment doc, the CI build gate, versioning and GHCR image publishing, the release and rollback flow, VPS deployment with Docker Compose behind nginx, PR conventions, documentation standards, and the three test layers including a real ephemeral Postgres and deterministic Playwright screenshots.

**7 docs** — onboarding workflow, Claude Code setup, CI/CD, deployment, pull requests, documentation standards, testing. Ships copy-ready `assets/` — `.claude/` settings and .NET/Node `SessionStart` hooks, `build.yml`, `docker-release.yml`, `dependabot.yml`, a PR template, `Dockerfile`, `Directory.Build.props`, the prod compose file, deploy script, nginx site config, `test-db.sh` and `screenshot.mjs`.

### design-feature-skill (v1.0.0)

Interactive end-to-end feature design session — workshop a half-formed idea with the user, read the codebase and its design system, propose the architecture with Mermaid diagrams, build HTML mockups of the new screens in the app's own visual language, and write the design docs into the repo. No production code is written; the session ends at the docs and hands off from there.

**Skill only** — one SKILL.md covering the eight-phase workflow (talk it through, explore the codebase, learn the design system, architecture, mockups, confirm, write docs, wait), the facilitation posture, and the failure modes to avoid. Pairs with `handoff-skill`.

### handoff-skill (v1.0.0)

Generate a short, copy/paste-ready prompt for a fresh agent in a new chat. Infers the next unit of work from the session — the next phase of a plan, or the start of implementation after a design session — and names the docs to read and the code to explore. Outputs only the prompt, in a fenced code block, with no commentary.

**Skill only** — one SKILL.md covering task inference, the `Task` / `Read` / `Explore` prompt structure, what to leave out, and worked examples. Picks up where `design-feature-skill` leaves off.

### prototype-ui-skill (v1.0.0)

Prototype a feature or UI change as plain HTML/CSS/JS the user can open in a browser before anything is built. Extracts the codebase's design language (tokens, layout shell, components), writes a feature summary and UX spec, delegates the bulky HTML build to a Sonnet sub-agent, then verifies the result against the spec. No production code. Pairs with `design-feature-skill`, which calls it for its mockup step.

**Skill + 3 references + 1 asset** — SKILL.md orchestrates the workflow; `references/` holds the design-language, feature-spec and builder-brief templates; `assets/prototype-builder.md` is a drop-in `model: sonnet` sub-agent definition.

## Repository Structure

```
cpike-agent-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace manifest listing all plugins
├── plugins/
│   ├── agent-sdk-skill/
│   ├── avalonia-skill/
│   ├── blazor-skill/
│   ├── design-feature-skill/
│   ├── elasticsearch-skill/
│   ├── frontend-design-skill/
│   ├── handoff-skill/
│   ├── html-reports-skill/
│   ├── huemint-skill/
│   ├── mermaid-skill/
│   ├── observability-skill/
│   ├── obsidian-skill/
│   ├── project-setup-skill/
│   ├── prototype-ui-skill/
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
