---
description: Assess docs for accuracy, gaps, and staleness; fix via sub-agents and open a PR
argument-hint: "[--pr N | --commit SHA | --since REF | --branch NAME] [--dry-run] [--verbose]"
---

# Update Docs

Assess project documentation for accuracy, gaps, and staleness, then spawn sub-agents to fix issues and open a PR with suggested changes.

**This command is a lightweight orchestrator.** Assessment is delegated to read-only sub-agents; writing is delegated to `docs-writer` sub-agents (from the dev-agents plugin — use `general-purpose` if unavailable). Never read source files or write documentation directly.

## Arguments

```
[--pr <number>] [--commit <sha>] [--since <ref>] [--branch <name>] [--dry-run] [--verbose]
---
$ARGUMENTS
```

All optional. `--pr` / `--commit` / `--since` / `--branch` scope the assessment to that change set. `--dry-run` runs assessment only — report findings, write nothing. `--verbose` emits a one-line progress update as each phase and sub-agent completes (default: silent until the final summary).

## Phase 1: Determine Scope

Explicit args win; otherwise infer from git state:

| Scope | Change set |
|-------|-----------|
| `--pr N` | `gh pr view N --json title,body,headRefName,baseRefName,files,labels` + `gh pr diff N` |
| `--commit SHA` | `git show SHA --stat` + `git diff SHA~1 SHA` |
| `--since REF` | `git log --oneline REF..HEAD` + `git diff REF..HEAD --stat` |
| `--branch NAME` | diff vs `git merge-base main NAME` |
| (no args) uncommitted changes | working tree diff (`git diff` + `git diff --cached`) — assume the user wants docs assessed against in-progress work |
| (no args) clean tree, feature branch | branch vs merge-base with main |
| (no args) clean tree, on main | **full sweep** — assess all project documentation holistically |

Also: read the project's `CLAUDE.md` (summarize for sub-agents) and map the doc structure (`tree -L 2` on the project root and any `docs/` directory).

Record: scope mode, change summary (files/areas affected), existing doc structure and naming conventions, project context.

## Phase 2: Parallel Assessment (Read-Only Sub-Agents)

Spawn **four** read-only assessors in parallel. In full-sweep mode they assess the entire project; in scoped mode they prioritize docs related to the change set but may note broader issues they encounter.

Every assessor gets the same prompt skeleton with its focus section swapped in:

```
## Task
{Focus} assessment of project documentation.

## Documentation Assessment Context
- **Scope:** {mode} — {change summary}
- **Changed files:** {list, grouped by area}
- **Existing documentation:** {tree of doc files found}
- **Project context:** {summary from CLAUDE.md — architecture, conventions, tech stack}

## Your Focus: {Focus}
{focus bullets from the definitions below}

Respond in EXACTLY this format (omit empty sections):

### Critical
- `{doc_file}` — {finding: what's wrong, missing, or stale — and what the code actually does}

### Major
- `{doc_file}` — {finding}

### Minor
- `{doc_file}` — {finding}

### Summary
{2-3 sentence overview}
```

### Assessor Focus Definitions

- **Feature Accuracy** — for each documented feature, read the corresponding source code: does the documented behavior match the implementation? Are examples, parameters, and configuration options still correct? Are features described that no longer exist or work differently?
- **Gap Detection** — map the project's public surface area (APIs, endpoints, commands, config, env vars, user-facing features) and cross-reference against existing docs; flag what exists but is undocumented. Weight by impact: a missing doc for a core feature is Critical; for an internal utility, Minor.
- **Change Impact** — read the change set carefully: did it modify documented behavior without updating docs? Introduce features or APIs needing new docs? Remove or rename things existing docs still reference? If docs WERE updated in the change set, verify they're accurate and complete. In full-sweep mode, check the last 10–20 commits for undocumented changes.
- **Staleness** — verify every concrete reference in each doc still exists and resolves: file paths, class/function names, config keys, commands, internal and external links, version-specific instructions, screenshots/examples, referenced dependencies or tools.

## Phase 3: Synthesize Findings

Merge all four result sets:

1. **Deduplicate** — same doc + same issue → keep the most detailed finding. Cross-reference related findings ("X needs docs" + "X was added without docs" → one finding).
2. **Group by doc file**, prioritized Critical > Major > Minor.
3. **Classify the action per finding:**

| Action | Description |
|--------|-------------|
| **Update** | Existing doc needs content corrected or expanded |
| **Create** | New doc file needs to be written |
| **Bootstrap** | No docs exist at all (no README, no docs/) → create foundational README + architecture doc |
| **Remove** | Doc is obsolete — orchestrator deletes or flags it directly, no sub-agent |

Produce a summary: scope, 2–3 sentence executive overview, finding counts by severity, and a required-actions table (doc file / action / findings).

**Dry run:** if `--dry-run`, display the summary and stop here. Note: "To apply these changes, run `/update-docs` again without `--dry-run`."

## Phase 4: Parallel Doc Writing

Spawn writing sub-agents in parallel — **one per doc file** that needs changes:

```
## Task
{Update / Create / Bootstrap} documentation: {doc_file}

## Findings to Address
{specific findings for this doc file from Phase 3}

## Project Context
- **Project:** {name and summary from CLAUDE.md}
- **Tech stack:** {languages, frameworks}
- **Doc conventions:** {naming patterns, formatting style observed in existing docs}

## Existing Doc Content
{full current content if updating; otherwise "New file — no existing content"}

## Source Code References
{relevant source file paths and brief descriptions the doc should reflect}

## Instructions
- Match the project's existing documentation style; be accurate — document only what the code actually does; be concise
- For updates: preserve the existing structure; change only what the findings require
- For bootstrap: create a practical README (overview, setup, usage) plus an architecture overview if the project has meaningful structure
- Write the complete file content — no placeholders or TODOs
```

## Phase 5: Create PR

1. Run `git status` — if no files were modified, skip PR creation and report that docs are up to date.
2. Create a branch `docs/update-{timestamp}` (e.g. `docs/update-20260418-1430`) and commit all doc changes:
   ```
   docs: update project documentation

   Automated documentation update via /update-docs.
   Scope: {mode description}
   Changes: {brief list of what was updated/created/removed}
   ```
3. Push with `-u` and `gh pr create --base {original_branch}` with title `docs: update project documentation` and a body containing: scope, finding counts by severity, a changes table (doc file / action / description), condensed assessment details, and the footer `*Generated by /update-docs — review suggested changes before merging.*`
4. Return to the original branch.

## Phase 6: Report Results

One summary format — the result line and conditional sections vary:

```
## Documentation Update — {project_name}

**Scope:** {mode} | **Date:** {today}
**Result:** {PR created with documentation updates | Documentation is up to date | {N} findings identified (dry run — no changes made)}

### Assessment Summary
- Critical: {n} | Major: {n} | Minor: {n}

### Changes Made               ← omit if none
| Doc File | Action | Description |
|----------|--------|-------------|
| README.md | Updated | Corrected feature X description |

### PR                         ← if created
{PR URL} — review the suggested changes and merge if they look good.
```

For dry runs, include the full findings summary from Phase 3. Also report any sub-agent errors that occurred.
