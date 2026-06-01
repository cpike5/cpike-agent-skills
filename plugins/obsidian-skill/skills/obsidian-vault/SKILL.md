---
name: obsidian-vault
description: Read, create, edit, and maintain notes in an Obsidian vault. Use this skill whenever the user is working with an Obsidian vault, a folder of Markdown notes, or mentions ".md notes", "my vault", "my notes", frontmatter/properties, wikilinks, callouts, Dataview, or templates — even if they don't say the word "Obsidian". Especially important when editing existing notes, since Obsidian-specific syntax (wikilinks, embeds, block refs) and link integrity are easy to break with naive Markdown editing.
---

# Working with Obsidian Vaults

An Obsidian vault is just a folder of plain `.md` files plus a `.obsidian/` config directory. The value of this skill is knowing the Obsidian-specific conventions that ordinary Markdown tooling does not respect — get these right and edits stay safe, links stay intact, and notes render as the user expects.

## Before you touch anything

1. **Locate the vault root.** It is the folder containing `.obsidian/`. All wikilinks resolve relative to the vault, not the current file's folder, so you need the root to reason about links.
2. **Never edit `.obsidian/` unless asked.** It holds plugin config, hotkeys, and workspace state. Corrupting it can break the user's setup. If version-controlling the vault, most of it should be gitignored (see references).
3. **Read before you write.** Obsidian files often contain frontmatter and special syntax that looks like ordinary text but has meaning. Read the whole note first.
4. **Preserve, don't reformat.** Do not "tidy" Markdown, reflow paragraphs, or normalize link style across a note unless that is the task. Surgical edits only — the user's notes are their long-term memory.

## Frontmatter (Properties)

Obsidian's metadata lives in YAML frontmatter at the very top of the file, fenced by `---`. Obsidian calls these **Properties**.

```markdown
---
title: My Note
aliases: [MN, MyNote]
tags: [project/dotnet, reference]
created: 2026-06-01
status: draft
---
```

Rules that matter:

- The opening `---` must be the **first line** of the file. No blank lines, no BOM, no content above it, or Obsidian won't parse it as frontmatter.
- `tags`, `aliases`, and `cssclasses` are **reserved keys** with special behavior. `tags` here are equivalent to inline `#tags`. `aliases` make the note findable/linkable under alternate names.
- Malformed YAML fails **silently** — the note just shows no properties. Quote any value containing a colon, `#`, `@`, or a leading special character (e.g. `title: "Re: the meeting"`).
- When adding a property, check whether one already exists before appending a duplicate key. If frontmatter is absent and you need to add some, insert a new block at the very top.
- Keep property names consistent with the rest of the vault — Dataview queries and the Properties UI rely on stable names. Look at sibling notes before inventing a new key.

## Obsidian-specific syntax — handle with care

These are **non-standard Markdown**. They will not render in GitHub, VS Code preview, or most other tools, and naive find/replace can silently break them.

- **Wikilinks:** `[[Note Name]]`, with display text `[[Note Name|shown text]]`, to a heading `[[Note#Heading]]`, to a block `[[Note#^block-id]]`.
- **Embeds / transclusion:** `![[Note Name]]` embeds another note inline; also works for images, PDFs, audio.
- **Block references:** a trailing `^block-id` on a line makes it linkable.
- **Callouts:** `> [!note]`, `> [!warning]`, `> [!tip]`, etc. A trailing `+`/`-` makes them foldable: `> [!info]-`.
- **Tags:** inline `#tag`, nested as `#parent/child`.
- **Comments:** `%%hidden%%` does not render in reading view.

See `${CLAUDE_PLUGIN_ROOT}/docs/01-syntax.md` for the full set and edge cases.

## The cardinal rule: protect link integrity

Links are the connective tissue of a vault. The most damaging thing an agent can do is silently orphan notes.

- **Renaming or moving a note breaks every `[[wikilink]]` pointing at it.** Obsidian's own UI auto-updates these; you are not in the UI. If you rename a note (file or its display name), you **must** search the whole vault for references to the old name and update them — including embeds `![[...]]`, heading links `[[Note#...]]`, and block links `[[Note#^...]]`. Do a vault-wide grep for the old basename.
- Prefer adding an `alias` over renaming when the goal is just to make a note findable under a new name — it's non-destructive.
- When deleting a note, warn the user about inbound links rather than leaving dangling references, and offer to list what points to it.
- Wikilinks match by note **basename** across the whole vault (filenames are usually unique vault-wide). Two notes with the same name are ambiguous — flag it rather than guessing.

## Creating new notes

- Filename = the note's identity. Use the title the user will link to; avoid characters illegal in Obsidian links: `[ ] # ^ | :` and OS-illegal characters like `/ \ ?`.
- Start with frontmatter if the vault uses it consistently (check a few existing notes for the house style — tags, created date, status fields).
- Match the surrounding vault's conventions for folders, casing, and link style rather than imposing your own.
- If the vault has a `templates/` folder, read the relevant template and follow it.

## Editing existing notes

- Make the smallest change that accomplishes the task.
- Leave frontmatter, callouts, embeds, and block IDs intact unless they are the thing being edited. In particular, never strip a `^block-id` — something may link to it.
- If you change a heading that is the target of a `[[Note#Heading]]` link, update those links too (grep for the old heading text).
- Don't convert wikilinks to standard Markdown links (or vice versa) unless asked — the vault has a global setting for which style it uses.

## Common requests and how to approach them

- **"Add a tag/property to these notes"** → edit frontmatter (or inline `#tag`), matching existing key names; don't duplicate keys.
- **"Link these related notes"** → add `[[wikilinks]]`; verify each target note actually exists by its basename.
- **"Make a MOC / index note"** → a note that is mostly `[[links]]` to others; confirm each link resolves.
- **"Clean up / find broken links"** → grep all `[[...]]` targets against actual filenames; report orphans and dangling links before changing anything.
- **"Set up a Dataview query"** → fenced ` ```dataview ` block; requires the Dataview community plugin and consistent property names. See `${CLAUDE_PLUGIN_ROOT}/docs/01-syntax.md`.

## Sanity check before finishing

- Frontmatter still valid YAML and still the first thing in the file?
- Any renamed note/heading — did you update every inbound link?
- Did you avoid editing `.obsidian/`?
- Did you preserve syntax you didn't need to touch (callouts, embeds, block IDs, comments)?

For the complete syntax reference, Dataview/Templater notes, and git/gitignore guidance, read `${CLAUDE_PLUGIN_ROOT}/docs/01-syntax.md`.
