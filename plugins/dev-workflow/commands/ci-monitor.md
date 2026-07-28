---
description: Monitor a PR's CI checks, dispatch fix agents, and loop until green
argument-hint: "<pr-number> [--max-iterations N]"
---

# CI Monitor

Monitor a PR's CI checks, diagnose failures, dispatch specialist sub-agents to fix them, and loop until CI passes or max iterations are reached.

**This command is a lightweight orchestrator.** All diagnosis is done from CI logs. All fixes are delegated to specialist sub-agents. Never read or edit source files directly.

## Arguments

```
<pr-number> [--max-iterations N]
---
$ARGUMENTS
```

First token = PR number (required). `--max-iterations` (aliases `--max`, `-n`) caps the fix loop; default 3.

## Orchestrator Rules

1. **Never read source files or write code yourself** — sub-agents do that
2. **Keep sub-agent prompts focused** — include only the failure context they need
3. **Track attempted fixes** — avoid infinite loops on the same failure

## Phase 1: Initialize

1. Fetch PR metadata: `gh pr view {number} --json headRefName,baseRefName,title,url,state`. If the PR is not open, abort: "PR #{number} is {state} — nothing to monitor."
2. Check out the PR's head branch: `git fetch origin {headRefName} && git checkout {headRefName} && git pull origin {headRefName}`
3. Read the project's `CLAUDE.md` for architecture context (pass a summary to sub-agents later).
4. Initialize tracking: `iteration = 0`, `max_iterations` from args, `attempted_fixes = []` (list of `{check_name, failure_signature}` tuples), `fix_history = []`.

## Phase 2: Wait for Checks

1. Block until checks reach a terminal state:
   ```bash
   gh pr checks {number} --watch
   ```
   Run in the background if checks are long-running. If checks remain pending with no state change for ~30 minutes, treat as stalled → Phase 6.

2. Fetch the structured result:
   ```bash
   gh pr checks {number} --json name,state,conclusion,detailsUrl
   ```
   - **Passed**: conclusion is `SUCCESS`, `NEUTRAL`, or `SKIPPED`
   - **Failed**: conclusion is `FAILURE`, `TIMED_OUT`, `ACTION_REQUIRED`, or `CANCELLED`

3. All passed → Phase 6 (success). Any failed → Phase 3, batching **all** failures into one iteration.

## Phase 3: Diagnose Failures

For each failed check:

1. Extract the run ID from `detailsUrl` (pattern `.../actions/runs/{run-id}`) and fetch failed logs: `gh run view {run-id} --log-failed`

2. **Categorize the failure** using log content:

   | Category | Signal Patterns | Sub-agent |
   |----------|----------------|-----------|
   | **Build error** | `error CS`, `error MSB`, `Build FAILED`, `could not resolve`, `The type or namespace` | `dotnet-fixer` (single-file) or `dotnet-specialist` (multi-file / architectural) |
   | **Test failure** | `Failed!`, `X Error(s)`, `Assert.`, `Expected:`, `Test Run Failed`, `[FAIL]` | `test-writer` (test needs updating) or `dotnet-fixer` (implementation is wrong) |
   | **Lint/format** | `SA1`, `IDE0`, `CA1`, `dotnet format`, `style violation`, `whitespace` | `dotnet-fixer` |
   | **Security scan** | `CVE-`, `vulnerability`, `security advisory`, `Dependabot`, `snyk`, `trivy` | `security-hardener` |
   | **Workflow/infra** | `docker`, `Dockerfile`, `action`, `workflow`, `yaml`, `runner`, `timeout`, `service unavailable` | `devops-specialist` |

   Specialist agents come from the **dev-agents** plugin. If a named agent type is unavailable, or the project isn't .NET (e.g. a Python one-off), map the category to the equivalent stack tooling and use `general-purpose`.

3. **Disambiguation** for Build/Test: single file with a clear error code → `dotnet-fixer`; multiple files or project references → `dotnet-specialist`; wrong test assertion → `test-writer`; buggy implementation → `dotnet-fixer`; ambiguous → `dotnet-fixer`.

4. **Batch** same-category failures that share a root cause into a single fix unit.

5. **Dedup against attempted_fixes**: same `check_name` AND same `failure_signature` (first 200 chars of error) as a previous attempt → mark **unfixable** (the prior fix didn't resolve it); do not retry. If ALL failures are unfixable → Phase 6.

## Phase 4: Dispatch Fix Sub-agents

Failures in different categories → dispatch in **parallel**. Multiple failures in the same category → one batched sub-agent. A test failure that depends on a build fix → **sequential**: build fix first.

### Sub-agent Prompt Template

```
## Task
Fix CI failure in PR #{number}: {pr_title}

## Failure Details
- **Check name:** {check_name}
- **Category:** {Build error | Test failure | Lint/format | Security scan | Workflow/infra}
- **Error log (relevant excerpt):**

{trimmed_log_excerpt — max 200 lines, focused on the error}

## Context
- Project: {summary from CLAUDE.md}
- PR branch: {headRefName} | Base: {baseRefName}
- Iteration: {current_iteration} of {max_iterations}

## Constraints
- Fix ONLY the CI failure described above
- Do NOT refactor unrelated code
- Do NOT change test expectations unless the test is genuinely wrong
- If the fix requires architectural changes beyond your scope, report back with what's needed instead of making partial changes
```

### Per-agent prompt additions

- `dotnet-fixer`: exact error codes (CS####) and file paths from the log
- `dotnet-specialist`: which projects are affected and any project/package reference issues
- `test-writer`: test name, expected vs actual values, and whether the test or the implementation should change
- `security-hardener`: CVE numbers, affected packages, suggested remediation from scan output
- `devops-specialist`: the workflow file path and the full step output where the failure occurred

## Phase 5: Commit, Push, and Loop

1. Run `git status` — if no files were modified, treat the failure as unfixable for this iteration and note it.
2. Stage and commit:
   ```
   fix(ci): {brief description of what was fixed}

   CI monitor iteration {N}/{max}
   Fixes: {comma-separated check names addressed}
   ```
3. Push: `git push origin {headRefName}`
4. Increment `iteration`; append to `attempted_fixes` and `fix_history`.
5. `iteration >= max_iterations` → Phase 6; otherwise → Phase 2.

## Phase 6: Report Results

One summary format — the result line and conditional sections vary by exit condition:

```
## CI Monitor — PR #{number}: {title}

**Result:** {ALL CHECKS PASSING | MAX ITERATIONS REACHED ({max}) | UNFIXABLE FAILURE DETECTED | CI CHECKS STALLED}
**Iterations:** {N} fix iteration(s)
**PR:** {url}

### Fix History
| Iteration | Check | Category | Fix Applied |
|-----------|-------|----------|-------------|
| 1 | build | Build error | Added missing using in OrderService.cs |

### Remaining Failures        ← omit on success
- **{check_name}**: {description — for unfixable, note the same failure persisted after the fix in iteration {N}; for stalled, the pending state and duration}

### Recommendation            ← omit on success
{Specific advice on what to investigate manually}
```

Also report any sub-agent errors that occurred.
