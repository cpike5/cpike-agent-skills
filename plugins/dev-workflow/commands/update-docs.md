# Update Docs Instructions

Assess project documentation for accuracy, gaps, and staleness, then spawn sub-agents to fix issues and open a PR with suggested changes.

**This command is a lightweight orchestrator.** All assessment is delegated to read-only sub-agents. All writing is delegated to specialist sub-agents. Never read source files or write documentation directly.

## Arguments

```
[--pr <number>] [--commit <sha>] [--since <ref>] [--branch <name>] [--dry-run] [--verbose]

Examples:
  /update-docs
  /update-docs --pr 42
  /update-docs --commit abc123f
  /update-docs --since v2.1.0
  /update-docs --branch feat/new-api
  /update-docs --dry-run
  /update-docs --pr 42 --verbose
  /update-docs --dry-run --verbose
---
$ARGUMENTS
```

**Parsing:**
- All arguments are optional.
- `--pr <number>` — scope assessment to a specific PR's changes.
- `--commit <sha>` — scope to a specific commit.
- `--since <ref>` — scope to all changes since a version tag, commit, or PR merge.
- `--branch <name>` — scope to a branch's changes vs its base.
- `--dry-run` — run assessment phases only; report findings but do not write docs or create a PR.
- `--verbose` — output progress updates as each phase completes. Default: silent until final summary.
- If no scope arg is provided, infer scope from git state (see Phase 1).

## Orchestrator Rules

**CRITICAL: You are a lightweight coordinator. Follow these rules:**

1. **Never read source files directly** — sub-agents do that
2. **Never write or edit documentation yourself** — sub-agents produce all changes
3. **Keep sub-agent prompts focused** — include only the context they need
4. **Run assessment agents in parallel** — fan out simultaneously, collect results
5. **Run writing agents in parallel** — one per doc area, fan out simultaneously
6. **Pass summaries forward** — merge sub-agent findings into a synthesis, not raw output

## Phase 1: Determine Scope

Resolve what change set to assess documentation against.

### Priority Order

Explicit args override git state inference:

1. **`--pr`** — Fetch the PR diff as the change set:
   ```bash
   gh pr view {number} --json title,body,headRefName,baseRefName,files,labels
   gh pr diff {number}
   ```

2. **`--commit`** — Use the commit as the change set:
   ```bash
   git show {sha} --stat
   git diff {sha}~1 {sha}
   ```

3. **`--since`** — All changes from ref to HEAD:
   ```bash
   git log --oneline {ref}..HEAD
   git diff {ref}..HEAD --stat
   ```

4. **`--branch`** — Changes on the named branch vs its merge base:
   ```bash
   git merge-base main {branch}
   git diff $(git merge-base main {branch})..{branch} --stat
   ```

5. **Infer from git state** (no args given):
   - **Uncommitted changes exist** → scope to the working tree diff (`git diff` + `git diff --cached`). Assume the user is mid-task and wants docs assessed against their in-progress work.
   - **Clean tree, on a feature branch** → scope to the branch vs its merge base with main.
   - **Clean tree, on main** → **full sweep mode**. Assess all project documentation holistically.

### Context Gathering

Regardless of scope mode, also collect:
```bash
git remote get-url origin   # repo identity
```

Read the project's `CLAUDE.md` (if it exists) for architecture context — pass a summary to all sub-agents.

Run `tree -L 2` on the project root and any `docs/` directory to map the documentation structure.

Record:
- **Scope mode**: PR / commit / since / branch / working-tree / full-sweep
- **Change summary**: files changed, areas affected (group by layer/concern)
- **Existing doc structure**: what docs exist, where, and their naming conventions
- **Project context**: summary from CLAUDE.md, language/framework, repo structure

If `--verbose`, report: `Phase 1 complete — scope: {mode}, {N} files in change set, {M} existing doc files found.`

## Phase 2: Parallel Assessment (Read-Only Sub-Agents)

Spawn **four** read-only assessment sub-agents in parallel. Each receives the shared context from Phase 1 and a targeted focus prompt.

**In full-sweep mode**, all four agents assess the entire project. **In scoped mode**, agents focus on documentation relevant to the change set but may note broader issues they encounter.

### Shared Context Pack

Assemble once, include in every sub-agent prompt:

```
## Documentation Assessment Context

### Scope
- **Mode:** {PR #N / commit abc123 / since v2.1 / branch feat/xyz / working-tree / full-sweep}
- **Change summary:** {brief description of what changed}

### Changed Files
{list of files in the change set, grouped by area}

### Existing Documentation
{tree output of docs/ and any doc files found}

### Project Context
{summary from CLAUDE.md — architecture, conventions, tech stack}
```

### Agent 1: Feature Coverage Assessor

```
## Task
Assess whether documented features accurately reflect what the code actually does.

{Shared Context Pack}

## Your Focus: Feature Accuracy
For each piece of feature documentation you find:
- Does the documented behavior match the current code implementation?
- Are documented examples, parameters, or configuration options still correct?
- Are there features described that no longer exist or work differently?

## Instructions
1. Identify all feature-related documentation (README feature sections, docs/ guides, API docs)
2. For each documented feature, read the corresponding source code
3. Flag any mismatch between docs and code behavior
4. In scoped mode: prioritize docs related to the change set, but note other inaccuracies found

Respond in EXACTLY this format:

### Inaccurate
- `{doc_file}` — {what's wrong and what the code actually does}

### Outdated
- `{doc_file}` — {what changed and when, if identifiable}

### Accurate
- `{doc_file}` — {confirmed accurate}

### Summary
{2-3 sentence overview of feature documentation accuracy}
```

### Agent 2: Gap Detection Assessor

```
## Task
Identify undocumented features, APIs, or behaviors that should have documentation.

{Shared Context Pack}

## Your Focus: Documentation Gaps
Look for things that exist in code but have no corresponding documentation:
- Public APIs, endpoints, or services with no docs
- Configuration options or environment variables not documented
- User-facing features with no guide or README mention
- Important architectural decisions with no explanation
- Non-obvious behavior or edge cases that would surprise a user or future agent

## Instructions
1. Map the project's public surface area (APIs, commands, features, config)
2. Cross-reference against existing documentation
3. Identify gaps — things that exist but aren't documented
4. In scoped mode: focus on gaps introduced or revealed by the change set
5. Assess impact: a missing doc for a core feature is Critical; a missing doc for an internal utility is Minor

Respond in EXACTLY this format:

### Critical Gaps
- {what's missing} — {why it matters, where docs should be added}

### Major Gaps
- {what's missing} — {explanation}

### Minor Gaps
- {what's missing} — {explanation}

### Summary
{2-3 sentence overview of documentation completeness}
```

### Agent 3: Change Impact Assessor

```
## Task
Assess whether recent changes have been properly reflected in documentation.

{Shared Context Pack}

## Your Focus: Change Impact on Docs
For the changes in scope, determine:
- Did the changes modify behavior that is currently documented? If so, were docs updated?
- Did the changes introduce new features or APIs that need new documentation?
- Did the changes remove or rename things that are referenced in existing docs?
- Were any doc changes included in the change set? If so, are they accurate and complete?

## Instructions
1. Read the full diff / change set carefully
2. For each significant change, search existing docs for references to the affected code
3. Flag docs that reference changed behavior but weren't updated
4. Flag new additions that have no corresponding docs
5. If docs WERE updated in the change set, verify they're accurate
6. In full-sweep mode: check the last 10-20 commits for undocumented changes

Respond in EXACTLY this format:

### Docs Need Updating
- `{doc_file}` — {what changed in code and what the doc still says}

### New Docs Needed
- {what was added} — {suggested doc location and content outline}

### Docs Already Updated (Verification)
- `{doc_file}` — {verified accurate / has issues: description}

### Summary
{2-3 sentence overview of change-to-doc alignment}
```

### Agent 4: Staleness Assessor

```
## Task
Identify documentation that references things that no longer exist or are no longer accurate.

{Shared Context Pack}

## Your Focus: Stale Documentation
Scan all project documentation for references that are outdated:
- File paths, class names, or function names that no longer exist
- Configuration keys or environment variables that were renamed or removed
- Links to internal files or sections that are broken
- Version-specific instructions that reference old versions
- Screenshots or examples that show outdated UI or output
- Dependencies or tools referenced that are no longer used

## Instructions
1. Read each documentation file
2. For every concrete reference (file path, class name, config key, command), verify it still exists
3. For every link (internal or external), verify it resolves
4. Flag anything that references non-existent code, files, or resources
5. In scoped mode: prioritize docs related to the change set, but note staleness found elsewhere

Respond in EXACTLY this format:

### Critical Staleness
- `{doc_file}` — {references X which no longer exists / was renamed to Y}

### Major Staleness
- `{doc_file}` — {description}

### Minor Staleness
- `{doc_file}` — {description}

### Summary
{2-3 sentence overview of documentation freshness}
```

If `--verbose`, report as each agent completes: `Assessment complete: {agent_name} — {finding_count} findings.`

## Phase 3: Synthesize Findings

Collect all four assessment results and merge into a unified picture.

### Merge Rules

1. **Deduplicate**: If multiple assessors flag the same doc file for the same issue, keep the most detailed finding.
2. **Group by doc file**: Organize all findings per documentation file, regardless of which assessor found them.
3. **Prioritize by severity**: Critical > Major > Minor.
4. **Cross-reference**: If the Gap assessor says "X needs docs" and the Change Impact assessor says "X was added without docs," merge into a single finding.

### Determine Required Actions

For each finding, classify the action:

| Action | Description |
|--------|-------------|
| **Update** | Existing doc needs content corrected or expanded |
| **Create** | New doc file needs to be written |
| **Bootstrap** | No docs exist at all; create foundational README + architecture doc |
| **Remove** | Doc references something that no longer exists and the doc itself is obsolete |

### Bootstrap Detection

If the project has **no documentation at all** (no README, no docs/ folder, no doc files):
- Add a **Bootstrap** action to create a basic README.md and top-level architecture doc.
- Assessment agents will have limited findings — that's expected.

### Produce Summary

Generate a text summary of findings:

```
## Documentation Assessment — {project_name}

**Scope:** {mode} | **Date:** {today}

### Overview
{2-3 sentence executive summary}

### Findings by Severity
- **Critical:** {count} — {brief list}
- **Major:** {count} — {brief list}
- **Minor:** {count} — {brief list}

### Required Actions
| Doc File | Action | Findings |
|----------|--------|----------|
| README.md | Update | Feature X description is inaccurate; missing section for feature Y |
| docs/api.md | Update | Endpoint /foo was renamed to /bar |
| docs/deployment.md | Create | No deployment documentation exists |

### Assessment Details
{Grouped findings from all assessors, organized by doc file}
```

If `--verbose`, report: `Phase 3 complete — {N} findings, {M} docs require action.`

### Dry Run Exit

If `--dry-run` is set, display the summary and **stop here**. Do not proceed to Phase 4 or 5.

```
## Dry Run Complete

{Full summary from above}

To apply these changes, run `/update-docs` again without `--dry-run`.
```

## Phase 4: Parallel Doc Writing (Sub-Agents)

If there are required actions from Phase 3, spawn writing sub-agents in parallel — **one agent per doc file** that needs changes.

### Writing Agent Assignment

| Action | Agent Type | Task |
|--------|-----------|------|
| **Update** | `docs-writer` | Edit the existing doc file based on findings |
| **Create** | `docs-writer` | Write a new doc file following project conventions |
| **Bootstrap** | `docs-writer` | Create foundational docs (README.md, architecture overview) |
| **Remove** | (orchestrator handles) | Delete or flag the obsolete doc — no sub-agent needed |

### Writing Agent Prompt Template

```
## Task
{Update / Create / Bootstrap} documentation: {doc_file}

## Findings to Address
{List of specific findings for this doc file from Phase 3}

## Project Context
- **Project:** {name and summary from CLAUDE.md}
- **Tech stack:** {languages, frameworks}
- **Doc conventions:** {naming patterns, formatting style observed in existing docs}

## Existing Doc Content
{If updating: full content of the current doc file}
{If creating: "New file — no existing content"}
{If bootstrapping: "No project docs exist. Create foundational documentation."}

## Source Code References
{Relevant source file paths and brief descriptions that the doc should reference}

## Instructions
- Match the project's existing documentation style and format
- Be accurate — only document what the code actually does
- Be concise — documentation should be useful, not exhaustive
- For updates: preserve the existing structure; change only what the findings require
- For new docs: follow the naming and structure conventions of existing docs
- For bootstrap: create a practical README with project overview, setup, and usage; create an architecture overview if the project has meaningful structure
- Write the complete file content — do not use placeholders or TODOs
```

Dispatch all writing agents in parallel. Each writes to its target file.

If `--verbose`, report as each completes: `Doc written: {doc_file} ({action}).`

## Phase 5: Create PR

After all writing agents complete:

1. **Verify changes exist**: Run `git status`. If no files were modified (agents found nothing to change), skip PR creation and report that docs are up to date.

2. **Create a branch**:
   ```bash
   git checkout -b docs/update-{timestamp}
   ```
   Where `{timestamp}` is a short date-time string (e.g., `docs/update-20260418-1430`).

3. **Stage and commit** all doc changes:
   ```
   docs: update project documentation

   Automated documentation update via /update-docs.
   Scope: {mode description}
   
   Changes:
   - {brief list of what was updated/created/removed}
   ```

4. **Push and create PR**:
   ```bash
   git push -u origin docs/update-{timestamp}
   ```
   
   ```bash
   gh pr create --base {original_branch} --title "docs: update project documentation" --body "$(cat <<'EOF'
   ## Summary
   
   Automated documentation assessment and update via `/update-docs`.
   
   **Scope:** {mode} — {description of what was assessed}
   **Findings:** {N} total ({critical} critical, {major} major, {minor} minor)
   
   ## Changes Made
   
   | Doc File | Action | Description |
   |----------|--------|-------------|
   | {file} | {Updated/Created/Removed} | {brief description} |
   
   ## Assessment Details
   
   {Condensed findings summary — what was wrong and how it was fixed}
   
   ## What Was Assessed
   
   - **Feature Coverage:** Are documented features accurate?
   - **Gap Detection:** What's undocumented that should be?
   - **Change Impact:** Do recent changes have doc implications?
   - **Staleness:** What references outdated code/behavior?
   
   ---
   *Generated by `/update-docs` — review suggested changes before merging.*
   EOF
   )"
   ```

5. **Return to the original branch**:
   ```bash
   git checkout {original_branch}
   ```

If `--verbose`, report: `Phase 5 complete — PR #{number} created.`

## Phase 6: Report Results

Display a final summary based on what happened.

### Changes Made — PR Created

```
## Documentation Update — {project_name}

**Scope:** {mode} | **Date:** {today}
**Result:** PR created with documentation updates

### Assessment Summary
- **Critical findings:** {count}
- **Major findings:** {count}
- **Minor findings:** {count}

### Changes Made
| Doc File | Action | Description |
|----------|--------|-------------|
| README.md | Updated | Corrected feature X description |
| docs/api.md | Updated | Fixed endpoint references |
| docs/deployment.md | Created | New deployment guide |

### PR
{PR URL}

Review the suggested changes and merge if they look good.
```

### No Changes Needed

```
## Documentation Update — {project_name}

**Scope:** {mode} | **Date:** {today}
**Result:** Documentation is up to date

All assessed documentation accurately reflects the current codebase. No changes required.
```

### Dry Run Report

```
## Documentation Assessment (Dry Run) — {project_name}

**Scope:** {mode} | **Date:** {today}
**Result:** {N} findings identified (dry run — no changes made)

{Full findings summary from Phase 3}

To apply fixes, run `/update-docs` again without `--dry-run`.
```

## Output

Report to the user:
- Final result status (PR created / up to date / dry run)
- Finding counts by severity
- Table of changes made (if any)
- PR URL (if created)
- Any sub-agent errors that occurred
