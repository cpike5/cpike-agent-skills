---
description: Parallel multi-reviewer PR review — posts a structured comment to the PR
argument-hint: "<pr-number> [--scope minimal|light|standard|full]"
---

# Review PR

Orchestrate parallel specialist sub-agent reviews of a GitHub PR. Produces a human-readable summary and posts a structured, agent-actionable comment to the PR.

**This command is a lightweight orchestrator.** All analysis is delegated to `code-reviewer` sub-agents with targeted focus prompts.

## Arguments

```
<pr-number> [--scope minimal|light|standard|full]
---
$ARGUMENTS
```

First token = PR number. `--scope` (optional) sets the review tier; if omitted, auto-detect from the diff.

## Orchestrator Rules

1. **Never read source files or write findings yourself** — sub-agents do that
2. **Run reviewers in parallel** — fan out simultaneously, collect results
3. **Pass summaries forward** — not full outputs between stages

## Phase 1: Gather PR Context

```bash
gh pr view {number} --json title,body,author,baseRefName,headRefName,labels,url
gh pr diff {number}
gh pr view {number} --json files
```

Retain: title, a 2–3 sentence summary of intent, branches, URL, labels, the changed file list, and approximate added/removed line counts.

### Scope Detection

If `--scope` is provided, use it. Otherwise:

| Scope | Heuristic |
|-------|-----------|
| **Minimal** | Only docs/config changed (`.md`, `.json`, `.yml`, `.txt` — no `.cs`/`.razor`/`.ts`) |
| **Light** | <5 files changed AND <100 added lines |
| **Standard** | 5–20 files OR 100–500 added lines |
| **Full** | >20 files OR >500 added lines OR label `breaking-change` or `major` |

### Conditional Reviewers (any tier)

- **+UX/UI**: any `.razor`, `.css`, `.scss`, `.js`, `.ts`, or `.html` files changed
- **+Data Layer**: EF migration files (`*Migration*.cs`, `*DbContext*`, `*Repository*`, `*Query*`) or paths containing `/Migrations/`, `/Data/`, `/Persistence/`

### Reviewer Matrix

| Scope | Reviewers |
|-------|-----------|
| **Minimal** | Docs Gaps |
| **Light** | Code Quality, Test Coverage, Breaking Changes |
| **Standard** | Code Quality, Security, Test Coverage, Spec Alignment, Docs Gaps, Breaking Changes |
| **Full** | All of Standard + UX/UI and Data Layer (if triggered) |

## Phase 2: Build Shared Context Pack

Assemble once, pass to every sub-agent:

```
## Shared PR Context

### PR #{number}: {title}
{2–3 sentence summary of PR intent}

### Changed Files
{list of files grouped by layer/concern}

### Diff Summary
- Files changed: {count} | Lines added ~{n} / removed ~{n}
- Key areas: {brief description, e.g., "new OrderService with 3 methods, migration for Orders table"}

### Project Architecture
{summary from the project's CLAUDE.md, if present — architecture, layering, conventions}

### Relevant Docs
{docs files that seem related to the changed code, if a docs/ dir exists}
```

## Phase 3: Fan Out Reviewers (Parallel)

Spawn ALL applicable `code-reviewer` sub-agents **in parallel**. Every reviewer gets the same prompt skeleton with its focus section swapped in:

```
## Task
{Focus} review of PR #{number}: {title}

{Shared Context Pack}

## Your Focus: {Focus}
{focus bullets from the definitions below}

## Instructions
1. Run `gh pr diff {number}` to see all changes
2. Read changed files in full where needed for context
3. Focus ONLY on the diff — do not review or audit unchanged code

Respond in EXACTLY this format (omit empty sections):

### Critical
- `file.cs:42` — [issue and how to fix]

### Major
- `file.cs:88` — [issue and how to fix]

### Minor
- [optional suggestion]

### Positive Highlights
- [good patterns worth noting, if any]

### Verdict
{APPROVED | NEEDS_CHANGES} — APPROVED if no Critical or Major findings
```

### Reviewer Focus Definitions

- **Code Quality** — bugs, logic errors, unhandled edge cases; duplication, long methods, magic numbers, inappropriate coupling; SOLID violations; naming clarity and consistency; overly clever code that will be hard to maintain.
- **Security** — missing auth checks or broken access control; SQL/command injection, XSS; OWASP Top 10 in the changed code; sensitive data exposure (logged secrets, unencrypted PII); insecure deserialization, SSRF, path traversal; hardcoded credentials.
- **Test Coverage** — are new/changed public methods, error paths, and edge cases tested? Were existing tests updated for behavior changes? Judge whether important behaviors are verified, not line-coverage percentages. Findings should name the missing test scenario.
- **Spec Alignment** — read the PR description (`gh pr view {number}`) and any related docs/ specs; compare stated goals and acceptance criteria against what was implemented; flag scope creep and unfulfilled promises.
- **Docs Gaps** — new public APIs, endpoints, or config options with no docs; changed behavior that existing docs no longer describe; new user-facing features with no guide or README update; missing comments on non-obvious logic. Note what's missing — don't rewrite docs.
- **Breaking Changes** — renamed/removed public methods, classes, or endpoints; changed signatures or request/response shapes; changed config keys or semantics; schema changes requiring migration (and whether it's included); behavior changes existing callers depend on. Note the migration path.
- **UX/UI** (conditional) — static analysis of component files, no screenshots: consistency with sibling components; duplicate controls; reuse of shared components vs inline reimplementation; CSS/JS conventions; accessibility basics (labels, alt text, semantic HTML, keyboard navigation); is the new page/feature reachable via navigation?
- **Data Layer** (conditional) — query correctness; N+1 risks (missing `.Include()`, loading collections in loops); missing indexes; EF Core/ORM patterns (async, no sync-over-async); destructive migrations without safety steps; transaction boundaries; soft-delete and audit-field handling in queries.

## Phase 4: Collect and Synthesize

Track per finding: severity, reviewer source, file:line (if given), action description.

**Dedup rule:** same file:line flagged for different reasons → keep both (different perspectives); identical issue with the same description → keep the higher-severity copy.

## Phase 5: Display Human-Readable Summary

```
## PR #{number} Review — {title}

**Scope:** {tier} | **Reviewers:** {comma-separated list}
**Verdict:** {APPROVED / NEEDS_CHANGES}

### Critical ({count})
- **[Code Quality]** `file.cs:42` — description

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

Post with `gh pr comment {number} --body`, same structure as Phase 5 with each finding tagged `**[Reviewer]**`, a `**Scope:** {tier} | **Reviewers:** {list} | **Date:** {today}` header line, and the footer:

```
---
*Generated by /review-pr — review only, no auto-fixes applied.*
```

Omit empty severity sections. If all reviewers approved, the body is just the header, `All reviewers approved — no issues found.`, and the footer.

## Output

Report to the user:
- The human-readable summary (Phase 5)
- Confirmation that the PR comment was posted
- Any sub-agent errors or skipped reviewers (with reason)
