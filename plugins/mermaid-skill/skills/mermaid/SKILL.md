---
name: mermaid
description: "Use this skill when generating Mermaid diagrams for software architecture, data models, workflows, or system design. Covers flowcharts, sequence diagrams, class diagrams, state diagrams, ER diagrams, C4 diagrams, architecture diagrams, git graphs, styling/theming, and .NET architecture patterns. Invoke when: creating or editing Mermaid diagram code, choosing which diagram type fits a scenario, debugging Mermaid parse errors, styling diagrams with themes or classDef, generating architecture diagrams for .NET systems (Clean Architecture, CQRS, middleware pipeline, microservices, Blazor component trees, EF Core models, deployment topologies), or when the user asks about Mermaid syntax, diagram best practices, or visual documentation."
---

# Mermaid Diagram Knowledge Base

You are generating Mermaid diagrams. Read the relevant reference docs below based on what you're diagramming. **Always check syntax foundations first** — parse errors are the #1 issue.

## Quick Decision: Which Diagram Type?

| Scenario | Diagram Type | Doc |
|----------|-------------|-----|
| Process flow, decision logic, pipelines | Flowchart | 02 |
| Request/response between services or actors | Sequence | 03 |
| Domain model, class relationships, interfaces | Class | 04 |
| Lifecycle, state machine, workflow states | State | 05 |
| Database schema, entity relationships | ER | 06 |
| System context, containers, components (C4 model) | C4 | 07 |
| Infrastructure, deployment, cloud topology | Architecture | 08 |
| Branch/merge strategy, release history | Git Graph | 09 |
| Custom colors, branding, visual polish | Styling | 10 |
| Ready-made .NET architecture templates | .NET Patterns | 11 |

## Reference Documentation

### Always Read First
- ${CLAUDE_PLUGIN_ROOT}/docs/01-syntax-foundations.md — Directives, node IDs, label quoting/escaping, arrow types, common parse errors

### Diagram Types (read as needed)
- ${CLAUDE_PLUGIN_ROOT}/docs/02-flowchart.md — Direction, node shapes, subgraphs, click events, layout tips
- ${CLAUDE_PLUGIN_ROOT}/docs/03-sequence.md — Participants, message types, activations, control flow, notes, boxes
- ${CLAUDE_PLUGIN_ROOT}/docs/04-class.md — Visibility, members, relationships, cardinality, generics, namespaces
- ${CLAUDE_PLUGIN_ROOT}/docs/05-state.md — States, transitions, composite states, choice/fork/join, concurrency
- ${CLAUDE_PLUGIN_ROOT}/docs/06-er.md — Entities, attributes, cardinality, identifying vs non-identifying, EF Core mapping
- ${CLAUDE_PLUGIN_ROOT}/docs/07-c4.md — Context/Container/Component/Deployment, persons, systems, boundaries
- ${CLAUDE_PLUGIN_ROOT}/docs/08-architecture.md — Beta syntax, groups, services, icon sets, edges, junctions
- ${CLAUDE_PLUGIN_ROOT}/docs/09-git-graph.md — Commits, branches, merges, cherry-pick, tags, workflow patterns

### Styling & Patterns
- ${CLAUDE_PLUGIN_ROOT}/docs/10-styling-theming.md — Themes, themeVariables, classDef, per-diagram config, color palettes
- ${CLAUDE_PLUGIN_ROOT}/docs/11-dotnet-patterns.md — Ready-to-adapt templates: Clean Architecture, DI, middleware, CQRS, Blazor, EF, microservices, deployment

## Critical Rules (Common Parse Errors)

1. **Quote labels with special characters** — Colons, parentheses, semicolons, and brackets in labels cause parse failures. Wrap in `"double quotes"` or use HTML entities (`#58;` for colon, #40; #41; for parens, #59; for semicolon).
2. **Node IDs must be alphanumeric** — No spaces, no hyphens, no starting with numbers. Use camelCase or underscores: `orderService`, `db_main`.
3. **Avoid reserved words as IDs** — `end`, `style`, `class`, `click`, `subgraph`, `graph`, `flowchart` are reserved. Rename: `endState`, `styleNode`.
4. **Space after arrows** — `A-->B` may fail in some contexts. Always use `A --> B` with spaces.
5. **Use `stateDiagram-v2`** — The v1 syntax is deprecated and has known bugs. Always declare `stateDiagram-v2`.
6. **ER diagram requires relationship labels** — Every relationship line needs a label string: `Customer ||--o{ Order : "places"`. Omitting the label causes a parse error.
7. **C4 aliases must be unique** — Duplicate aliases across boundaries silently break rendering. Prefix with boundary context: `api_db`, `auth_db`.
8. **Init directive must be first line** — `%%{init: {...}}%%` must appear before any diagram declaration. Placing it after causes it to be ignored.
9. **No empty subgraphs** — A `subgraph` block with no nodes inside causes a parse error. Add at least one node or remove the subgraph.
10. **Backtick labels for markdown** — To use bold/italic in node labels, wrap with backticks: `` A["`**Bold** text`"] ``. Regular quotes don't support markdown formatting.
