---
description: Create a well-structured GitHub issue with implementation context
argument-hint: "<description of the issue>"
---

# Create Issue

Create a GitHub issue with enough structure and context that an implementation agent can work without extensive exploration.

## User Arguments

```
$ARGUMENTS
```

## Process

1. **Understand the issue** — what problem it solves or feature it adds; bug, feature, task, or enhancement; rough scope.
2. **Read the project's CLAUDE.md first** — identify the affected architectural layer, relevant configuration options, page routes, related docs, and existing patterns to reference.
3. **Gather implementation context:**
   - Bugs: steps to reproduce, expected vs actual behavior
   - Features: acceptance criteria, affected components
   - UI changes: the page route; config changes: the exact options/settings class name
4. **Check existing labels** with `gh label list` and apply consistent ones.
5. **Create the issue** with `gh issue create` — clear title, structured body, appropriate labels.

## Issue Body Template

Adapt layer names and stack-specific references to the project — the template assumes .NET-style Core/Infrastructure/Application layering, but this command may also be used on Python or other stacks.

```markdown
## Description
[Clear description of the issue]

## Acceptance Criteria
- [ ] [Specific, testable criteria]

## Technical Context
- **Layer:** [affected layer]
- **Files likely affected:** [paths from CLAUDE.md lookup]
- **Related docs:** [links to relevant documentation]
- **Pattern to follow:** [reference to existing similar implementation]

## Additional Notes
[Constraints, related issues, or implementation hints]
```

## Larger Features

Create a parent issue (label `epic`), then sub-issues, linking each to the parent:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/gh-link -Parent <parent-number> -Child <child-number>
```

If the issue isn't straightforward — complex bug, open architectural question — investigate the root cause or assess scope before creating it.

## Output

- Issue URL and summary of what was created
- Any sub-issues created
