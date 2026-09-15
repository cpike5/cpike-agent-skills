# Workflow

## Pre-exploration

Before scanning the tree, read whichever of these exist: `README.md`, `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, and any existing `project-map/`. They set the framing for everything else and tell you whether this is a fresh map or a refresh.

## Fresh map vs refresh

**Fresh**: no `project-map/` exists. Create it and write every document.

**Refresh**: `project-map/` exists. Don't regenerate blindly.

1. Read each existing document and note its `Generated` commit from the header.
2. Diff the tree since that commit (`git diff --stat <commit>..HEAD`, plus `git log --oneline`) to see which areas changed.
3. Rewrite only the documents whose subject changed; update headers on the rest.
4. Legacy maps use `A-top-level-structure.md` … `F-integrations.md`. Migrate them to the current filenames and delete the old ones.

## Document header

Every document starts with:

```markdown
> Generated <YYYY-MM-DD> at commit `<short-sha>` by /map-project. Refresh with `/map-project` when this drifts.
```

This is what makes refresh possible and tells a reader how much to trust the map.

## Exploration order

Only one real dependency exists: `domains.md` synthesizes `structure.md`, `documentation.md`, and `architecture.md`. Everything else is independent. If subagents are available, fan out exploration for structure, documentation, architecture, configuration, and integrations in parallel, then write in the table order from SKILL.md so the taxonomy fixed in `architecture.md` is available before `domains.md` and `conventions.md`.

Exploration subagents return findings, not documents — you write the documents so the voice and taxonomy stay consistent.

## Size budget

Target under 150 lines per document, and under 80 for `structure.md` and `documentation.md`. Mermaid blocks count. A document over budget is almost always enumerating something that should be summarized with a pattern ("one `I{Entity}Repository` per aggregate root") or dropped.

## The index

`project-map/README.md` is the entry point and the last thing you write. It contains the header, a one-line description per document with a relative link, and a short "how to use this map" paragraph: start with `README.md` at the project root, then `structure.md`, then jump to whichever document answers your question. When done, offer to add a single line to the project's CLAUDE.md pointing at `project-map/README.md`.

## Stack notes

Instructions assume .NET (solution files, EF Core, `IOptions<T>`, DI registration in `Program.cs`). For other stacks, substitute the equivalent: `package.json`/`go.mod`/`pyproject.toml` for projects, ORM models for entities, exported interfaces or protocols for contracts, the framework's config loader for `IOptions`. The judgement calls in each doc apply regardless of stack.
