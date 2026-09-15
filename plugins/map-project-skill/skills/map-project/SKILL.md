---
name: map-project
description: "Generate or refresh a project-map/ folder: a compact set of architecture documents that let an agent (or a new team member) answer 'where is X?' and 'what does this system do?' without reading the whole codebase. Use this skill whenever the user asks to map, survey, or document the structure of a codebase, generate a project map or architecture overview, or onboard agents to a repository — phrases like 'map this project', 'generate a project map', 'create architecture docs', 'survey this codebase', 'refresh the project map'. Also use it when a project-map/ folder already exists and the user wants it updated. Not for documenting a single feature or writing API reference docs. .NET-first (solutions, EF Core, IOptions) with fallbacks for other stacks."
---

# /map-project — Project Architecture Map

Produce a `project-map/` folder at the project root. The map is for discoverability: it answers "where is X?", "what does this system do?", and "where do I add Y?". It does not explain how anything works internally — that's what the code is for.

## Output

| File | Answers |
|------|---------|
| `project-map/README.md` | Index: one line per document, how to use the map |
| `project-map/structure.md` | What's at the top level and why it matters |
| `project-map/documentation.md` | Where existing docs live, grouped by topic |
| `project-map/architecture.md` | Projects, layering, data model, service contracts |
| `project-map/domains.md` | Feature domain map (Mermaid) and priority-domain diagrams |
| `project-map/configuration.md` | Config sources, load order, what goes where |
| `project-map/integrations.md` | External services, data stores, observability, credentials |
| `project-map/conventions.md` | How to add an entity, endpoint, service, migration, test |

## Reference

Read first — it covers pre-exploration, refresh mode, parallel exploration, size budget, and the header every document carries:

- ${CLAUDE_PLUGIN_ROOT}/docs/01-workflow.md

Then one doc per output document, read as you reach it:

- ${CLAUDE_PLUGIN_ROOT}/docs/02-structure.md
- ${CLAUDE_PLUGIN_ROOT}/docs/03-documentation.md
- ${CLAUDE_PLUGIN_ROOT}/docs/04-architecture.md
- ${CLAUDE_PLUGIN_ROOT}/docs/05-domains.md
- ${CLAUDE_PLUGIN_ROOT}/docs/06-configuration.md
- ${CLAUDE_PLUGIN_ROOT}/docs/07-integrations.md
- ${CLAUDE_PLUGIN_ROOT}/docs/08-conventions.md

## Principles

1. **Map, don't enumerate.** Include what an agent needs to avoid wasted exploration; skip the rest. If a document is growing past its budget, you're listing instead of mapping.
2. **One taxonomy.** Derive domain groupings from the code's own folder and namespace names, fix them in `architecture.md`, and reuse them verbatim in every later document.
3. **Priorities come from the user when possible.** In an interactive session, ask which domains matter most before drawing domain diagrams. In a headless run, rank from evidence (fan-in, file counts, recent churn) and record the ranking in `domains.md`.
4. **CLAUDE.md holds rules; project-map holds the map.** Don't duplicate conventions that CLAUDE.md already states — link to them. Do offer to add a one-line pointer to `project-map/` in CLAUDE.md when the map is done.
