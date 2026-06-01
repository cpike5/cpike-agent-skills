# Obsidian Syntax & Tooling Reference

Read this when you need the full detail behind the SKILL.md summary.

## Contents
- Frontmatter / Properties
- Links, embeds, block references
- Callouts
- Tags
- Comments and formatting extras
- Dataview
- Templater / core Templates
- Git and `.obsidian/`
- Editing pitfalls cheat-sheet

---

## Frontmatter / Properties

Typed property kinds Obsidian recognizes: Text, List, Number, Checkbox (boolean), Date, Date & time. The type is inferred from the YAML value and remembered per key across the vault.

```markdown
---
title: Example
aliases:
  - Alt Name One
  - Alt Name Two
tags:
  - area/work
  - status/active
priority: 2
done: false
due: 2026-06-15
---
```

Notes:
- List syntax can be flow (`[a, b]`) or block (one `- item` per line). Both work; match the vault's style.
- Reserved keys: `tags`, `aliases`, `cssclasses`. Everything else is user-defined.
- A `#` at the start of a YAML value starts a comment in some parsers — quote tag-like values.
- Inline (Dataview) fields use `key:: value` syntax in the body and are separate from YAML frontmatter.

## Links, embeds, block references

| Purpose | Syntax |
|---|---|
| Link to note | `[[Note Name]]` |
| Link with alias text | `[[Note Name\|display text]]` |
| Link to heading | `[[Note Name#Heading]]` |
| Link to sub-heading | `[[Note Name#Heading#Subheading]]` |
| Link to block | `[[Note Name#^block-id]]` |
| Heading link, same note | `[[#Heading]]` |
| Block link, same note | `[[#^block-id]]` |
| Embed/transclude note | `![[Note Name]]` |
| Embed heading/block | `![[Note#Heading]]`, `![[Note#^block-id]]` |
| Embed image | `![[image.png]]` or `![[image.png\|200]]` (width) |
| Standard MD link | `[text](path/to/note.md)` |

- A **block** is a paragraph, list item, table, etc. Give it an ID by appending ` ^block-id` (space, caret, no spaces in the id) at the end of the block. Obsidian auto-generates random IDs when you link to a block via the UI; keep any that exist.
- Wikilinks resolve by basename across the whole vault. With `Use Wikilinks` off (Settings → Files and Links), Obsidian uses standard Markdown links with relative paths instead. Don't mix styles; follow the vault's setting.
- "Shortest path when possible" vs "Relative/Absolute path" is a vault setting that affects how links are written — when in doubt, copy the form already used in the vault.

## Callouts

```markdown
> [!note] Optional custom title
> Body of the callout.
> Can span multiple lines.
```

- Foldable: `> [!tip]+` (starts expanded) or `> [!tip]-` (starts collapsed).
- Built-in types: note, abstract/summary/tldr, info, todo, tip/hint/important, success/check/done, question/help/faq, warning/caution/attention, failure/fail/missing, danger/error, bug, example, quote/cite.
- Callouts can nest and can contain other Markdown, including links and embeds.

## Tags

- Inline: `#tag`, nested `#parent/child/grandchild`.
- Valid characters: letters, digits, `_`, `-`, `/`. A tag cannot be purely numeric.
- Frontmatter `tags:` and inline `#tags` populate the same tag index.

## Comments and formatting extras

- Comment (hidden in reading view): `%%this is a comment%%`, can be multiline.
- Highlight: `==highlighted==`.
- Strikethrough, bold, italic: standard Markdown.
- Math: `$inline$` and `$$block$$` (KaTeX).
- Mermaid diagrams: fenced ` ```mermaid ` blocks.
- Footnotes: `[^1]` with `[^1]: definition` elsewhere.
- Task lists: `- [ ]` / `- [x]`; Obsidian and plugins read these as tasks.

## Dataview (community plugin)

Queries live in fenced blocks and depend on consistent property/field names.

````markdown
```dataview
TABLE status, due
FROM #area/work
WHERE done = false
SORT due ASC
```
````

- `dataview` (DQL) renders a table/list/task view; `dataviewjs` runs JS.
- Inline fields `key:: value` in the body are queryable alongside frontmatter.
- Only works if the user has the Dataview plugin installed — note this assumption rather than assuming it renders.

## Templater / core Templates

- Core **Templates** plugin: simple text insertion with `{{title}}`, `{{date}}`, `{{time}}` placeholders.
- **Templater** (community): richer, uses `<% tp.* %>` syntax (e.g. `<% tp.file.title %>`, `<% tp.date.now() %>`).
- If a `templates/` (or similarly named) folder exists, read the relevant template and follow its structure when creating notes.

## Git and `.obsidian/`

If the vault is a git repo, a reasonable `.gitignore`:

```
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.trash/
```

- `workspace.json` changes constantly (pane layout) and creates noisy diffs — usually ignored.
- Some users intentionally commit the rest of `.obsidian/` to sync plugins and settings across machines; don't override their choice.
- The `.trash/` folder holds Obsidian's local deletions if that setting is enabled.

## Editing pitfalls cheat-sheet

- Adding content above frontmatter → frontmatter stops being recognized. Keep `---` on line 1.
- Renaming a note without updating `[[links]]` → orphaned references. Grep the vault for the old basename.
- Editing a heading that is a link target → `[[Note#Heading]]` links break. Update them.
- Removing a `^block-id` → any `[[Note#^id]]` link to it breaks.
- Find/replace across the vault on a common word → can corrupt links/tags. Scope replacements; prefer matching `[[...]]`/`#...` forms explicitly.
- Converting wikilinks ↔ standard links wholesale → fights the vault's global setting. Don't unless asked.
- Reflowing/auto-formatting Markdown → changes diffs and can split block IDs or callout lines. Make surgical edits.
