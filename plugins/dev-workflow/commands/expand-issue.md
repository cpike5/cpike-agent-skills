# Expand Issue Instructions

Take a sparse/brain-dump GitHub issue and flesh it out with proper details, acceptance criteria, technical context, and sub-issues as needed.

## User Arguments

```
Issue number to expand
---
#$ARGUMENTS
```

## Purpose

You often create quick issues as brain dumps to capture ideas. This command:
1. Reviews the sparse issue
2. Adds proper structure and implementation details
3. Breaks it into sub-issues if needed
4. Updates the original issue with complete context

## Process

### 1. Read the Issue

Use `${CLAUDE_PLUGIN_ROOT}/scripts/gh-view -Issue NUMBER` to get the issue with any existing hierarchy, then `gh issue view NUMBER` for full content.

Understand:
- What's the core idea/request?
- Is this a bug, feature, epic, or task?
- What scope does this seem to be (small, medium, large)?

### 2. Read CLAUDE.md

**CRITICAL:** Read the project's CLAUDE.md to understand:
- Architecture and layer structure
- Relevant configuration options
- Relevant page routes (if UI-related)
- Related documentation
- Existing patterns

### 3. Assess Scope and Structure

| Original Scope | Action |
|----------------|--------|
| Small/focused | Flesh out the single issue with details |
| Medium/multi-part | Consider 2-4 sub-issues |
| Large/epic | Break into feature-level sub-issues, each with tasks |

### 4. Gather Technical Context

Based on CLAUDE.md and the issue intent, identify:
- Which architectural layer(s) are affected
- Specific files/components likely involved
- Configuration options (exact class names)
- Page routes (if UI changes)
- Patterns to follow

### 5. Expand the Issue

#### For Small Issues

Update the original issue body with:

```markdown
## Description
[Expanded description of what was requested]

## Acceptance Criteria
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]

## Technical Context
- **Layer:** [Core | Infrastructure | Application]
- **Files likely affected:** [from CLAUDE.md lookup]
- **Related docs:** [links]
- **Pattern to follow:** [reference]

## Implementation Notes
[Any helpful context for the implementing agent]
```

Use `gh issue edit NUMBER --body "new body"` to update.

#### For Medium/Large Issues

1. Update the parent issue with overview and link to sub-issues
2. Create sub-issues with proper details
3. Link sub-issues to parent

```bash
# Create sub-issue
gh issue create --title "[Type]: [Description]" --label "task" --body "..."

# Link to parent
${CLAUDE_PLUGIN_ROOT}/scripts/gh-link -Parent [parent] -Child [new-issue]
```

### 6. Add Appropriate Labels

Review and update labels:
```bash
gh label list  # Check available labels
gh issue edit NUMBER --add-label "feature,frontend"
```

Common label patterns:
- **Type:** bug, feature, task, enhancement, epic
- **Area:** frontend, backend, database, api, docs
- **Priority:** priority:high, priority:low
- **Scope:** scope:small, scope:medium, scope:large

## Sub-Issue Templates

### Feature Sub-Issue
```markdown
## Description
[What this feature does]

## Acceptance Criteria
- [ ] [Criterion]

## Technical Context
- **Layer:** [Layer]
- **Files:** [Files from CLAUDE.md]
- **Pattern:** [Reference]

## Parent Issue
Part of #[parent-number]
```

### Task Sub-Issue
```markdown
## Task
[Specific implementation task]

## Definition of Done
- [ ] [Specific outcome]

## Technical Details
- **File(s):** [Exact paths]
- **Pattern:** [Reference to follow]

## Parent Issue
Part of #[parent-number]
```

### Bug Sub-Issue
```markdown
## Bug
[Bug description]

## Steps to Reproduce
1. [Step]

## Expected Behavior
[What should happen]

## Actual Behavior
[What happens instead]

## Likely Cause
- **File:** [Path]
- **Area:** [Component/service]

## Parent Issue
Part of #[parent-number]
```

## Example Expansion

**Before (brain dump):**
> Add user preferences page

**After (expanded with sub-issues):**

**Parent Issue (updated):**
```markdown
## Description
Add a user preferences page where users can configure their personal settings including notification preferences, display options, and timezone.

## Sub-Issues
- #43 Backend: Create UserPreferences entity and service
- #44 Frontend: Create Preferences page UI
- #45 Backend: Add preferences API endpoints

## Technical Context
- **Layer:** All layers (Core, Infrastructure, Application)
- **Related docs:** [settings-page.md], [form-implementation-standards.md]
- **Pattern:** Follow existing Settings page pattern
```

## What NOT to Do

- Don't start implementing - just document
- Don't over-engineer the breakdown - keep sub-issues focused
- Don't create sub-issues for trivial tasks (< 1 file change)
- Don't duplicate context - reference parent issue

## Expected Output

- Summary of changes made to the issue
- List of sub-issues created (with links)
- Updated issue URL
- Recommended next step (usually `/fix-issue #NUMBER`)
