---
description: Gather focused context about a GitHub issue to prepare for follow-up work
argument-hint: "<issue-number> [more issue numbers...]"
---

# Read Issue Instructions

Gather focused context about a GitHub issue to prepare for follow-up work.

## User Arguments

```
Issue number(s) to review. Multiple issues can be provided separated by spaces.
---
$ARGUMENTS
```

## Process

### 1. Fetch Issue Hierarchy

For each issue provided:

1. Use `${CLAUDE_PLUGIN_ROOT}/scripts/gh-view -Issue NUMBER` to get the issue with parent/sub-issues
2. If the issue has a **parent**, fetch the parent to understand broader context
3. Note any **sub-issues** for potential relevance

### 2. Review Issue Content

Use `gh issue view NUMBER` to get the full issue body and comments. Note:
- Description and acceptance criteria
- Labels (bug, feature, task, etc.)
- Current state (open, closed)
- Any linked PRs or commits
- Comments with additional context or decisions

### 3. Read CLAUDE.md

Read the project's CLAUDE.md to understand:
- Which architectural layer this issue affects
- Relevant configuration options (exact class names)
- Relevant page routes (if UI-related)
- Key documentation that might help
- Existing patterns to follow

### 4. Identify Affected Code Areas

Based on the issue and CLAUDE.md, identify (but don't read yet):

1. Specific files/components likely affected
2. For services: the **interface file** (not implementation)
3. For UI changes: the page route from CLAUDE.md
4. For configuration: the exact Options class name

### 5. Check Related Resources

Look for references in the issue to:
- Other issues (dependencies, related work)
- Documentation in `docs/` folder
- Specific files or components mentioned

### 6. Check Lessons Learned

If `docs/lessons-learned/` exists, scan for relevant entries.

## Output Format

```markdown
## Issue Overview
[1-2 sentence summary]

## Context
- **Parent:** #[number] [title] (if applicable)
- **Sub-issues:** #[numbers] (if applicable)
- **Labels:** [labels]
- **Scope estimate:** Trivial | Small | Medium | Large

## CLAUDE.md References
- **Layer:** [affected layer — e.g. Core | Infrastructure | Application on .NET projects; adapt to the project's stack]
- **Related docs:** [links from Key Documentation table]
- **Config options:** [exact class name if applicable]
- **Page route:** [if UI change, from UI Page Routes table]
- **Pattern to follow:** [if applicable]

## Files Likely Affected
- `path/to/interface.cs` - [reason]
- `path/to/file.cs` - [reason]

## Key Requirements
- [Acceptance criteria from issue]
- [Important constraints from comments]

## Ready For
- [ ] Implementation (/fix-issue)
- [ ] Questions/clarification needed
```

## Goal

Prepare just enough context that `/fix-issue` can proceed without redundant exploration.
