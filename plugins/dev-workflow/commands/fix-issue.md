# Fix Issue Instructions

Fix a GitHub issue: understand it, explore the codebase, implement the fix, review, then commit and PR.
Use a team of agents to complete the work below.

## Arguments

```
<issue-number> [base-branch] [-- extra context]

Examples:
  /fix-issue 123
  /fix-issue 123 feature/auth
  /fix-issue 123 -- focus on validation logic
---
$ARGUMENTS
```

**Parsing:** First token = issue number. Second token (if not `--`) = base branch. Everything after `--` = extra context.

## Phase 1: Understand the Issue

1. **Read the issue** using both `${CLAUDE_PLUGIN_ROOT}/scripts/gh-view -Issue {number}` and `gh issue view {number}` to get the full picture including any parent/sub-issue hierarchy.

2. **If the issue has a parent issue**, read it for broader context. If it has sub-issues, scan them to understand the scope boundary — what's in vs out for this issue.

3. **Read the project's CLAUDE.md** for architecture, conventions, and relevant patterns.

4. **Set up the branch:**
   - If base branch provided and doesn't exist: create from `main`, push with `-u`
   - If base branch provided and exists: fetch latest
   - If no base branch: default to `main`
   - Create task branch: `task/issue-{number}`

## Phase 2: Explore

Spawn an **Explore subagent** to investigate the codebase. Give it:
- The issue requirements
- Architecture context from CLAUDE.md
- What to look for (relevant files, patterns to follow, related code)

Use the exploration results to inform a clear implementation approach.

## Phase 3: Implement

Spawn **implementation subagent(s)** to make the changes. Provide:
- Issue requirements and acceptance criteria
- Architecture/convention context from CLAUDE.md
- Exploration findings (relevant files, patterns, interfaces)
- Any extra context from the user

Load the appropriate skills (blazor-skill for Blazor components, frontend design for UI designs and prototypes).
Choose the appropriate specialist agent type for the work (e.g., `dotnet-specialist`, `dotnet-fixer`, `database-specialist`, etc.).

## Phase 4: Review

Spawn a **code-reviewer subagent** to review the changes. If review finds critical or major issues, spawn another implementation subagent to address them. Max 2 review iterations — after that, note unresolved items in the PR.

If UI files were changed (`.razor`, `.css`, `wwwroot/`), also spawn a **ui-critic subagent**.

## Phase 5: Commit & PR

1. Stage and commit changes with a conventional commit message (`feat:`, `fix:`, etc.) referencing the issue number
2. Push the branch
3. Create a PR with `gh pr create --base {base-branch}`:
   - Title: concise description
   - Body: summary of changes, `Closes #{number}`, any unresolved review items

## Output

Report to the user:
- PR URL
- Brief summary of what was implemented (include code/ui review status)
- Any unresolved items or follow-up needed
