---
description: Flesh out a sparse brain-dump GitHub issue with details, acceptance criteria, and sub-issues
argument-hint: "<issue-number>"
---

# Expand Issue

Take a sparse/brain-dump GitHub issue and flesh it out with proper details, acceptance criteria, technical context, and sub-issues as needed. Document only — do not start implementing.

## User Arguments

```
Issue number to expand
---
$ARGUMENTS
```

## Process

1. **Read the issue.** `${CLAUDE_PLUGIN_ROOT}/scripts/gh-view -Issue NUMBER` for the parent/sub-issue hierarchy, then `gh issue view NUMBER` for full content. Identify the core idea, issue type, and rough scope.
2. **Read the project's CLAUDE.md** for architecture, configuration options, page routes, related docs, and existing patterns.
3. **Assess structure:**
   - Small/focused → flesh out the single issue
   - Medium/multi-part → 2–4 sub-issues
   - Large/epic → feature-level sub-issues, each with tasks
4. **Expand.** Update the issue body with `gh issue edit NUMBER --body` using the template below, adapted to the issue type — bugs get repro steps and expected/actual behavior; tasks get a definition of done. Adapt layer names to the project's stack (the template assumes .NET layering, but this command may be used on Python or other stacks).
5. **For sub-issues:** update the parent with an overview linking each child, then create and link the children:

   ```bash
   gh issue create --title "[Type]: [Description]" --label "task" --body "..."
   ${CLAUDE_PLUGIN_ROOT}/scripts/gh-link -Parent <parent> -Child <child>
   ```

6. **Labels.** Check `gh label list`; apply type (bug/feature/task/epic), area, priority, and scope labels consistent with the repo.

## Issue Body Template

```markdown
## Description
[Expanded description of what was requested]

## Acceptance Criteria
- [ ] [Specific, testable criterion]

## Technical Context
- **Layer:** [affected layer]
- **Files likely affected:** [from CLAUDE.md lookup]
- **Related docs:** [links]
- **Pattern to follow:** [reference]

## Implementation Notes
[Helpful context for the implementing agent]
```

Sub-issues use the same shape plus a `Part of #[parent]` footer. Keep them focused and reference the parent for shared context instead of duplicating it.

## What NOT to Do

- Don't start implementing — just document
- Don't over-engineer the breakdown, and don't create sub-issues for trivial (< 1 file) tasks

## Output

- Summary of changes made to the issue
- Sub-issues created (with links) and the updated issue URL
- Recommended next step (usually `/fix-issue NUMBER`)
