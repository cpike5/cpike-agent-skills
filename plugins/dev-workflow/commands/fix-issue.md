---
description: Fix a GitHub issue, milestone phase, or discussed problem end-to-end — implement, review, commit, PR
argument-hint: "[issue-number | phase <name>] [base-branch] [-- extra context]"
---

# Fix Issue Instructions

Fix a problem: understand it, implement the fix, review, then commit and PR.
Use a team of agents to complete the work below.

## Arguments

```
[issue-number | phase <name>] [base-branch] [-- extra context]

Examples:
  /fix-issue                              # use conversation context
  /fix-issue 123                          # fetch single GitHub issue
  /fix-issue 123 feature/auth
  /fix-issue 123 -- focus on validation logic
  /fix-issue -- the login redirect is broken
  /fix-issue phase 1                      # implement all issues in milestone "Phase 1"
  /fix-issue phase 1 feature/phase-1
---
$ARGUMENTS
```

**Parsing:**
- If arguments start with `phase` (case-insensitive), everything up to a branch token or `--` is the milestone name → **Mode C**
- If the first token is a number → **Mode A**
- Otherwise (empty or starts with `--`) → **Mode B**
- Second non-`phase` token (if not `--`) = base branch. Everything after `--` = extra context note.

## Phase 1: Understand the Problem

**Determine mode from arguments:**

### Mode A — Single GitHub issue
1. Read the issue using `gh issue view {number}` for the full description, labels, and comments.
2. If the issue references a parent issue, read it for broader context. Scan any sub-issues to understand scope boundaries.
3. Task branch: `task/issue-{number}`

### Mode B — Conversation context
1. The problem is already understood from the current conversation — do NOT fetch any GitHub issue or re-explore what was already found.
2. Summarize the problem statement and root cause from the conversation in a few sentences. This summary drives the rest of the workflow.
3. Task branch: short kebab-case slug from the problem (e.g. `fix/login-redirect`). Use timestamp suffix `fix/topic-YYYYMMDD` only if the topic is ambiguous.

### Mode C — Milestone / project phase
1. Fetch all open issues in the milestone: `gh issue list --milestone "{name}" --state open --json number,title,body,labels`
2. Read each issue in full. Note any explicit dependency signals ("depends on #N", "blocked by #N", sub-issue relationships, or sequencing implied by the issue titles/descriptions).
3. Group issues into **independent** (can be implemented in parallel) and **sequential** (must follow another issue). Present this grouping briefly to the user before proceeding — if the grouping looks wrong, stop and ask.
4. Task branch: `feat/phase-{name}` (kebab-cased, e.g. `feat/phase-1`, `feat/phase-auth-foundation`)

**All modes:**
- Read the project's CLAUDE.md for architecture, conventions, and relevant patterns.
- Set up the branch:
  - If base branch provided and doesn't exist: create from `main`, push with `-u`
  - If base branch provided and exists: fetch latest
  - If no base branch: default to `main`
  - Create the task branch derived above.

## Phase 2: Explore (conditional)

**Skip entirely for Mode B** if the conversation already identified specific files and root cause. Proceed directly to Phase 3.

**For Mode C**, spawn a **single shared Explore subagent** covering the full scope of all milestone issues rather than per-issue explorations. Give it the full issue list and ask it to identify: relevant files per issue, shared patterns, and any architectural concerns that span multiple issues.

**For Mode A** (or Mode C if scope is unclear), spawn an **Explore subagent** with:
- The issue requirements
- Architecture context from CLAUDE.md
- What to look for (relevant files, patterns, related code)

Use exploration results to inform implementation.

## Phase 3: Implement

**Mode A / Mode B:** Spawn a single **implementation subagent** with full context (problem, CLAUDE.md conventions, exploration findings, extra context).

**Mode C:** Spawn implementation subagents based on the dependency grouping from Phase 1:
- Spawn **parallel agents** for all independent issues simultaneously, each scoped to its own issue.
- After parallel agents complete, spawn **sequential agents** for dependent issues in dependency order, passing relevant output from prior agents as context.
- Each agent receives: its issue requirements, CLAUDE.md conventions, shared exploration findings, and any context from prerequisite issues.

For all modes, load appropriate skills (blazor for Blazor components, frontend-design for UI) and choose the right specialist agent type (`dotnet-specialist`, `database-specialist`, etc.). Specialist agents come from the dev-agents plugin — if a named type is unavailable, or the project isn't .NET (e.g. a Python one-off), use `general-purpose`.

## Phase 4: Review

Spawn a **code-reviewer subagent** over all changes. If critical or major issues are found, spawn another implementation subagent to address them. Max 2 review iterations — after that, note unresolved items in the PR.

If UI files were changed (`.razor`, `.css`, `wwwroot/`), also spawn a **ui-critic subagent**.

## Phase 5: Commit & PR

1. Stage and commit with a conventional commit message (`feat:`, `fix:`, etc.)
   - Mode A: reference the issue (`fix: resolve login redirect (#123)`)
   - Mode B: describe the fix concisely
   - Mode C: use a phase-level message (`feat: implement phase 1 — auth foundation`)
2. Push the branch
3. Create a PR with `gh pr create --base {base-branch}`:
   - Title: concise description
   - Body: summary of changes, `Closes #N` for each issue closed (Mode A/C), any unresolved review items

## Output

Report to the user:
- PR URL
- Brief summary of what was implemented (include code/ui review status)
- **Mode C only**: list each issue with its implementation status
- Any unresolved items or follow-up needed
