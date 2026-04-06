# Review PR Instructions

Orchestrate parallel specialist sub-agent reviews of a GitHub PR. Produces a human-readable summary and posts a structured, agent-actionable comment to the PR.

**This command is a lightweight orchestrator.** All heavy analysis is delegated to `code-reviewer` sub-agents with targeted focus prompts.

## Arguments

```
<pr-number> [--scope minimal|light|standard|full]

Examples:
  /review-pr 123
  /review-pr 123 --scope full
  /review-pr 123 --scope light
---
$ARGUMENTS
```

**Parsing:** First token = PR number. `--scope` flag (optional) sets the review tier. If omitted, auto-detect from PR diff.

## Orchestrator Rules

**CRITICAL: You are a lightweight coordinator. Follow these rules:**

1. **Never read source files directly** — sub-agents do that
2. **Never write review findings yourself** — sub-agents produce all findings
3. **Keep sub-agent prompts focused** — include only what they need
4. **Pass summaries forward** — not full outputs between stages
5. **Run reviewers in parallel** — fan out simultaneously, collect results

## Phase 1: Gather PR Context

Run these commands to build the shared context pack:

```bash
gh pr view {number} --json title,body,author,baseRefName,headRefName,labels,url
gh pr diff {number}
gh pr view {number} --json files
```

Extract and retain:
- PR title and 2–3 sentence summary of intent
- Base branch and head branch
- PR URL
- Full list of changed files (with paths)
- Diff line count (approximate — count `+` lines in diff)
- Labels

### Scope Detection

If `--scope` flag provided, use it. Otherwise auto-detect:

| Scope | Heuristic |
|-------|-----------|
| **Minimal** | Only docs/config changed (`.md`, `.json`, `.yml`, `.txt`, no `.cs`/`.razor`/`.ts`) |
| **Light** | <5 files changed AND <100 added lines |
| **Standard** | 5–20 files OR 100–500 added lines |
| **Full** | >20 files OR >500 added lines OR label `breaking-change` OR label `major` |

### Conditional Reviewer Detection

Always detect regardless of scope tier:
- **+UX/UI reviewer**: any `.razor`, `.css`, `.scss`, `.js`, `.ts`, or `.html` files changed
- **+Data layer reviewer**: any EF migration files (`*Migration*.cs`, `*DbContext*`, `*Repository*`, `*Query*`), or paths containing `/Migrations/`, `/Data/`, `/Persistence/`

### Reviewer Matrix

| Scope | Reviewers |
|-------|-----------|
| **Minimal** | Docs Gaps |
| **Light** | Code Quality, Test Coverage, Breaking Changes |
| **Standard** | Code Quality, Security, Test Coverage, Spec Alignment, Docs Gaps, Breaking Changes |
| **Full** | Code Quality, Security, Test Coverage, Spec Alignment, Docs Gaps, Breaking Changes, UX/UI (if applicable), Data Layer (if applicable) |

For Minimal/Light/Standard: always append UX/UI and/or Data Layer reviewers if triggered by file types above.

## Phase 2: Build Shared Context Pack

Assemble once, pass to every sub-agent:

```
## Shared PR Context

### PR #{number}: {title}
{2–3 sentence summary of PR intent}

### Changed Files
{list of files grouped by layer/concern}
- Core/Domain: [list]
- Infrastructure/Data: [list]
- Application/API: [list]
- UI/Components: [list]
- Docs/Config: [list]

### Diff Summary
- Files changed: {count}
- Lines added: ~{count} | Lines removed: ~{count}
- Key areas: {brief description, e.g., "new OrderService with 3 methods, migration for Orders table"}

### Project Architecture
Multi-plugin Claude Code repository. Plugins under plugins/<name>/ provide domain-specific knowledge.
(If reviewing a .NET project: three-layer architecture — Core → Infrastructure → Application)

### Relevant Docs
{If docs/ dir exists: list any docs files that seem related to the changed code}
```

## Phase 3: Fan Out Reviewer Sub-Agents (Parallel)

Spawn ALL applicable `code-reviewer` sub-agents **in parallel** using the reviewer prompts below. Each receives: the shared context pack + its targeted focus prompt.

### Code Quality Reviewer Prompt

```
## Task
Code quality review of PR #{number}: {title}

{Shared Context Pack}

## Your Focus: Code Quality
Review the changed files for:
- Bugs, logic errors, edge cases not handled
- Code smells: duplication, long methods, magic numbers, inappropriate coupling
- SOLID principles violations
- Naming: clarity, consistency with surrounding code
- Complexity: overly clever code that is hard to maintain

## Instructions
1. Run `gh pr diff {number}` to see all changes
2. For files with significant changes, read them in full for context
3. Focus ONLY on the diff — do not review unchanged code

Respond in EXACTLY this format:

### Critical
- `file.cs:42` — [description of issue and how to fix]

### Major
- `file.cs:88` — [description of issue and how to fix]

### Minor
- `file.cs:12` — [optional suggestion]

### Positive Highlights
- [Good patterns worth noting, if any]

### Verdict
{APPROVED | NEEDS_CHANGES}

If no Critical or Major issues, verdict is APPROVED.
```

### Security Reviewer Prompt

```
## Task
Security review of PR #{number}: {title}

{Shared Context Pack}

## Your Focus: Security
Review the changed files for:
- Authentication/authorization gaps (missing auth checks, broken access control)
- Injection risks: SQL injection, command injection, XSS
- OWASP Top 10 in the changed code
- Sensitive data exposure (logging secrets, unencrypted PII)
- Insecure deserialization, SSRF, path traversal
- Hardcoded credentials or secrets

## Instructions
1. Run `gh pr diff {number}` to see all changes
2. Read files with security-sensitive changes in full
3. Focus ONLY on the diff — do not audit unchanged code

Respond in EXACTLY this format:

### Critical
- `file.cs:42` — [description of issue and how to fix]

### Major
- `file.cs:88` — [description of issue and how to fix]

### Minor
- `file.cs:12` — [optional note]

### Positive Highlights
- [Good security patterns, if any]

### Verdict
{APPROVED | NEEDS_CHANGES}
```

### Test Coverage Reviewer Prompt

```
## Task
Test coverage review of PR #{number}: {title}

{Shared Context Pack}

## Your Focus: Test Coverage
Review whether the important paths are tested:
- Are the new/changed public methods covered by tests?
- Are error paths and edge cases tested?
- Are there tests for the acceptance criteria implied by the PR?
- Are existing tests updated to reflect behavior changes?

Do NOT focus on line coverage percentages — focus on whether the important behaviors are verified.

## Instructions
1. Run `gh pr diff {number}` to see all changes
2. Look at test files in the diff and any test files for changed components
3. Identify gaps: what important behavior has no test?

Respond in EXACTLY this format:

### Critical
- `file.cs:42` — [description of gap and suggested test]

### Major
- [missing test scenario] — [explanation]

### Minor
- [optional test suggestion]

### Positive Highlights
- [Good testing patterns, if any]

### Verdict
{APPROVED | NEEDS_CHANGES}
```

### Spec Alignment Reviewer Prompt

```
## Task
Spec alignment review of PR #{number}: {title}

{Shared Context Pack}

## Your Focus: Spec Alignment
Check whether the implementation matches the stated intent:
- Read any docs/ files relevant to the changed area
- Compare the PR body's stated goals against what was actually implemented
- Look for scope creep (things implemented that weren't asked for)
- Look for gaps (things promised in PR description that aren't implemented)
- Check if acceptance criteria in the PR body are met

## Instructions
1. Run `gh pr diff {number}` to see all changes
2. Run `gh pr view {number}` to read the PR description carefully
3. Look in docs/ for any related specs, BRDs, or user stories
4. Cross-reference intent vs. implementation

Respond in EXACTLY this format:

### Critical
- [gap or misalignment] — [explanation]

### Major
- [gap or misalignment] — [explanation]

### Minor
- [optional observation]

### Positive Highlights
- [Alignment wins, if any]

### Verdict
{APPROVED | NEEDS_CHANGES}
```

### Docs Gaps Reviewer Prompt

```
## Task
Documentation gaps review of PR #{number}: {title}

{Shared Context Pack}

## Your Focus: Documentation Gaps
Identify missing or outdated documentation:
- New public APIs, endpoints, or configuration options with no docs
- Changed behavior that existing docs no longer accurately describe
- New user-facing features with no guide or README update
- Missing inline comments on non-obvious logic

## Instructions
1. Run `gh pr diff {number}` to see all changes
2. Check docs/ directory for related documentation
3. Note what's missing — do not rewrite docs yourself

Respond in EXACTLY this format:

### Critical
- [missing doc] — [why it's needed and where it should go]

### Major
- [missing doc] — [explanation]

### Minor
- [optional doc suggestion]

### Positive Highlights
- [Good documentation, if any]

### Verdict
{APPROVED | NEEDS_CHANGES}
```

### Breaking Changes Reviewer Prompt

```
## Task
Breaking changes review of PR #{number}: {title}

{Shared Context Pack}

## Your Focus: Breaking Changes
Identify changes that break existing callers or behavior:
- Renamed or removed public methods, classes, or interfaces
- Changed method signatures (added required parameters, removed parameters, changed return types)
- Renamed or removed API endpoints
- Changed endpoint request/response shape
- Changed configuration key names or semantics
- Database schema changes that require migration (and whether the migration is included)
- Behavior changes that existing callers depend on

## Instructions
1. Run `gh pr diff {number}` to see all changes
2. Focus on public surface area changes
3. Note what migration path (if any) is needed

Respond in EXACTLY this format:

### Critical
- `file.cs:42` — [breaking change description and migration path]

### Major
- `file.cs:88` — [description]

### Minor
- [optional note]

### Positive Highlights
- [Good backwards-compatibility patterns, if any]

### Verdict
{APPROVED | NEEDS_CHANGES}
```

### UX/UI Reviewer Prompt (conditional — only if UI files changed)

```
## Task
UX/UI review of PR #{number}: {title}

{Shared Context Pack}

## Your Focus: UX/UI (Static Analysis)
Review component files for UI quality — no screenshots needed:
- Component consistency: does the new UI match patterns in sibling components?
- Duplicate controls: are there redundant buttons, inputs, or sections?
- Proper component reuse: are existing shared components used, or re-implemented inline?
- CSS/JS patterns: follows project conventions, no inline styles where classes exist
- Accessibility basics: labels on inputs, alt text, semantic HTML, keyboard navigation hints
- Navigation: can users reach the new page/feature? Is there a nav link or entry point?

## Instructions
1. Run `gh pr diff {number}` to see UI file changes
2. Read the changed component files in full
3. Compare against sibling components for consistency

Respond in EXACTLY this format:

### Critical
- `Component.razor:42` — [issue and fix]

### Major
- `Component.razor:88` — [issue and fix]

### Minor
- [optional suggestion]

### Positive Highlights
- [Good UI patterns, if any]

### Verdict
{APPROVED | NEEDS_CHANGES}
```

### Data Layer Reviewer Prompt (conditional — only if data layer files changed)

```
## Task
Data layer review of PR #{number}: {title}

{Shared Context Pack}

## Your Focus: Data Layer
Review data access code for correctness and safety:
- Query correctness: does the query return the right data?
- N+1 risks: missing `.Include()`, loading collections in loops
- Missing indexes: queries filtering on unindexed columns
- EF Core patterns: proper use of DbContext, async methods, no sync-over-async
- Migration safety: destructive migrations (column drops, renames) without safety steps
- Transaction boundaries: operations that should be atomic but aren't
- Soft delete / audit field handling: are these respected in queries?

## Instructions
1. Run `gh pr diff {number}` to see data layer changes
2. Read migration files and repository/query changes in full
3. Check DbContext configuration changes carefully

Respond in EXACTLY this format:

### Critical
- `Repository.cs:42` — [issue and fix]

### Major
- `Repository.cs:88` — [issue and fix]

### Minor
- [optional note]

### Positive Highlights
- [Good data patterns, if any]

### Verdict
{APPROVED | NEEDS_CHANGES}
```

## Phase 4: Collect and Synthesize Results

Collect responses from all sub-agents. For each finding, track:
- Severity (Critical / Major / Minor)
- Reviewer source
- File + line reference (if provided)
- Action description

Synthesize into two outputs: human summary (for conversation) and structured PR comment.

### Dedup Rule

If two reviewers flag the same file:line for different reasons, keep both findings (different perspectives). If they flag the exact same issue with the same description, keep the higher-severity one.

## Phase 5: Display Human-Readable Summary

Display in conversation, grouped by severity:

```
## PR #{number} Review — {title}

**Scope:** {tier} | **Reviewers:** {comma-separated list}
**Verdict:** {APPROVED / NEEDS_CHANGES}

### Critical ({count})
- **[Code Quality]** `file.cs:42` — description
- **[Security]** `file.cs:88` — description

### Major ({count})
- **[Test Coverage]** — missing test for X

### Minor ({count})
- **[Docs Gaps]** `file.md` — suggestion

### Positive Highlights
- Good patterns observed across reviewers

---
*Review comment posted to PR.*
```

If all reviewers approved: display `### All reviewers approved — no issues found.`

## Phase 6: Post Structured PR Comment

Post to GitHub using:

```bash
gh pr comment {number} --body "$(cat <<'EOF'
## PR Review — #{number}

**Scope:** {tier} | **Reviewers:** {list} | **Date:** {today}

### Critical
- **[Reviewer]** `file.cs:42` — [action description]

### Major
- **[Reviewer]** `file.cs:88` — [action description]

### Minor
- **[Reviewer]** `file.cs:12` — [suggestion]

### Positive Highlights
- [Good patterns worth noting]

---
*Generated by /review-pr — review only, no auto-fixes applied.*
EOF
)"
```

If there are no findings in a severity tier, omit that section entirely.
If all reviewers approved, body is:

```markdown
## PR Review — #{number}

**Scope:** {tier} | **Reviewers:** {list} | **Date:** {today}

All reviewers approved — no issues found.

---
*Generated by /review-pr — review only, no auto-fixes applied.*
```

## Output

Report to the user:
- Human-readable summary (from Phase 5)
- Confirmation that PR comment was posted
- Any sub-agent errors or skipped reviewers (with reason)
