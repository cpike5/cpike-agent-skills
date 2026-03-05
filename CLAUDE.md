# CLAUDE.md

Multi-plugin Claude Code repository. Each plugin under `plugins/<name>/` provides a domain-specific knowledge base — no executable code.

## Key Conventions

- **Doc numbering**: `docs/` files use sequential `01-NN` numbering. Preserve ordering.
- **SKILL.md frontmatter**: `description` controls skill invocation. Keep trigger phrases current.
- **Doc references**: SKILL.md uses `${CLAUDE_PLUGIN_ROOT}/docs/filename.md`. New docs must be referenced there.
- **Plugin versions**: Bump in each plugin's `.claude-plugin/plugin.json` on meaningful changes.
- **Marketplace manifest**: `.claude-plugin/marketplace.json` at repo root. Update when adding/removing plugins.

## Editing Guidelines

- Edit within the plugin boundary (`plugins/<name>/`).
- SKILL.md = compact router. Add detail to `docs/` files, not SKILL.md.
- Ensure SKILL.md references any new docs.
