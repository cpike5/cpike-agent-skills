# Create Issue Instructions

Create a GitHub issue with proper structure and context for efficient implementation.

## User Arguments

```
$ARGUMENTS
```

## Process

### 1. Understand the Issue

Get a brief understanding of what the issue is about:
- What problem does it solve or feature does it add?
- Is it a bug, feature, task, or enhancement?
- What's the expected scope (trivial, small, medium, large)?

### 2. Read CLAUDE.md

**CRITICAL:** Before creating the issue, read the project's CLAUDE.md to:
- Understand which architectural layer is affected
- Identify relevant configuration options or page routes
- Find related documentation to reference
- Understand existing patterns

### 3. Gather Context for Implementation

Include enough detail that an implementation agent can work without extensive exploration:

- **For bugs:** Include steps to reproduce, expected vs actual behavior
- **For features:** Include acceptance criteria, affected components
- **For UI changes:** Reference the page route from CLAUDE.md
- **For config changes:** Reference the exact Options class name

### 4. Check Existing Labels

Review the repository's existing labels to ensure consistency:
```bash
gh label list
```

### 5. Create the Issue

Use `gh issue create` with:
- Clear, descriptive title
- Structured body with implementation hints
- Appropriate labels

## Issue Body Template

```markdown
## Description
[Clear description of the issue]

## Acceptance Criteria
- [ ] [Specific, testable criteria]
- [ ] [Specific, testable criteria]

## Technical Context
- **Layer:** [Core | Infrastructure | Application]
- **Files likely affected:** [paths from CLAUDE.md lookup]
- **Related docs:** [links to relevant documentation]
- **Pattern to follow:** [reference to existing similar implementation]

## Additional Notes
[Any constraints, related issues, or implementation hints]
```

## When to Escalate

If the issue isn't straightforward:
- Complex bugs: Investigate root cause before creating issue
- Architectural questions: Have systems-architect assess scope
- Large features: Consider breaking into sub-issues

## Creating Sub-Issues

For larger features, create a parent issue then sub-issues:

```bash
# Create parent issue
gh issue create --title "Feature: [name]" --label "epic"

# Create sub-issues and link them
gh issue create --title "Task: [subtask]" --label "task"
${CLAUDE_PLUGIN_ROOT}/scripts/gh-link -Parent [parent-number] -Child [child-number]
```

## Expected Output

- Issue URL
- Summary of what was created
- Any sub-issues if applicable
