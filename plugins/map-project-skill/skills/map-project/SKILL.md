---
name: map-project
description: "Use this skill when mapping a project's architecture, generating a project-map/ folder, creating high-level architecture documentation for agent or human consumption, or when the user asks to map, survey, or document the structure of a codebase. Invoke when: the user says 'map this project', 'generate a project map', 'create architecture docs', 'survey this codebase', or wants a comprehensive overview of a project's structure, domains, configuration, and integrations."
---

# /map-project — Project Architecture Mapping

Generate a `project-map/` folder with 6 documents that give agents (and humans) a complete picture of the project without reading every file.

## Output Documents

| Document | File | Content |
|----------|------|---------|
| A | `A-top-level-structure.md` | Architecturally significant top-level files and directories |
| B | `B-documentation-index.md` | Documentation inventory grouped by domain |
| C | `C-source-architecture.md` | Solution structure, data model, service contracts |
| D | `D-feature-map.md` | Feature domain map (Mermaid) + per-domain class diagrams |
| E | `E-configuration.md` | Configuration sources, what goes where, DB-stored settings |
| F | `F-integrations.md` | External services, dependencies, credentials |

## Step Reference

| Step | Document | Doc |
|------|----------|-----|
| 1. Top-Level Structure | A | 02 |
| 2. Documentation Index | B | 03 |
| 3. Source Architecture | C | 04 |
| 4. Feature Map & Domain Diagrams | D | 05 |
| 5. Configuration | E | 06 |
| 6. External Integrations | F | 07 |

## Reference Documentation

### Always Read First
- ${CLAUDE_PLUGIN_ROOT}/docs/01-general-workflow.md — Pre-exploration, sequential workflow, output conventions

### Steps (read as needed)
- ${CLAUDE_PLUGIN_ROOT}/docs/02-top-level-structure.md — Document A: root directory mapping
- ${CLAUDE_PLUGIN_ROOT}/docs/03-documentation-index.md — Document B: docs inventory
- ${CLAUDE_PLUGIN_ROOT}/docs/04-source-architecture.md — Document C: solution, data model, service contracts
- ${CLAUDE_PLUGIN_ROOT}/docs/05-feature-map.md — Document D: Mermaid feature map + domain diagrams
- ${CLAUDE_PLUGIN_ROOT}/docs/06-configuration.md — Document E: config sources, classes, DB settings
- ${CLAUDE_PLUGIN_ROOT}/docs/07-integrations.md — Document F: dependencies, APIs, credentials

## General Principles

1. **Optimize for discoverability** — the map answers "where is X?" and "what does this system do?" not "how does X work internally?"
2. **Use judgement over exhaustiveness** — include what's architecturally significant, skip noise. Ask: would an agent need this to avoid wasting time exploring?
3. **Group by domain consistently** — use the same domain groupings across all documents so the map is navigable.
4. **Consult the user on priorities** — they know which parts of the system matter most. Don't map everything to equal depth.
