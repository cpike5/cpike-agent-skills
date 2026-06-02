# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Multi-plugin Claude Code marketplace. Every plugin under `plugins/<name>/` is a knowledge base or agent/command bundle — **no executable application code, no build/lint/test step**. "Testing" a change means reading the Markdown back and checking references resolve. Don't hunt for a test runner; there isn't one.

## Plugin Shapes

Plugins are built from three building blocks. Most use one; some combine them (e.g. `frontend-design-skill` and `obsidian-skill` ship **both** a skill and agents). Identify what a plugin contains before changing its structure:

1. **Skill + docs**: `skills/<name>/SKILL.md` is a compact router whose `description` frontmatter controls when the skill triggers; `docs/01-NN.md` hold the detail. The skill directory name often differs from the plugin name (`blazor-skill` plugin → `skills/blazor/`). SKILL.md references docs as `${CLAUDE_PLUGIN_ROOT}/docs/filename.md`.
2. **Commands** (`dev-workflow` only): `commands/<name>.md` — each file is one slash command (e.g. `/release`, `/fix-issue`).
3. **Agents**: `agents/<name>.md` — each file is one subagent with `name`, `description`, `tools`, `model` frontmatter followed by the system prompt. `dev-agents` is the general .NET roster; the UI-focused agents (`design-specialist`, `html-prototyper`, `ui-critic`) live in `frontend-design-skill/agents/`, and `vault-docs-maintainer` in `obsidian-skill/agents/` — agents sit with the domain they serve, not all in `dev-agents`.

`hooks/hooks.json` + a script (elasticsearch-skill, huemint-skill) auto-approve specific Bash calls via `PreToolUse`. Hook commands invoke `${CLAUDE_PLUGIN_ROOT}/hooks/<script>`.

## Key Conventions

- **Doc numbering**: `docs/` files use sequential `01-NN` numbering. Preserve ordering; new docs get the next number.
- **Doc references**: A new doc is invisible unless SKILL.md references it via `${CLAUDE_PLUGIN_ROOT}/docs/filename.md`. Always wire it in.
- **SKILL.md = router**: Keep it compact. Put detail in `docs/`, not SKILL.md. The `description` frontmatter is the trigger contract — keep its phrases current with the docs.
- **Versions**: Bump `plugins/<name>/.claude-plugin/plugin.json` `version` on meaningful changes.
- **Marketplace manifest**: `.claude-plugin/marketplace.json` (repo root) lists every plugin with its `source` and `description`. Update it when adding or removing a plugin.
- **README.md** is a public-facing index and drifts easily (it currently lists fewer plugins than the manifest). The manifest is the source of truth for what ships.

## Editing Guidelines

- Stay within one plugin's boundary (`plugins/<name>/`) per change.
- When adding a plugin: create the directory, add `plugin.json`, register it in `marketplace.json`, and (for skill plugins) ensure SKILL.md references every doc.
