# CI Monitor Instructions

Monitor a PR's CI checks, diagnose failures, dispatch specialist sub-agents to fix them, and loop until CI passes or max iterations are reached.

**This command is a lightweight orchestrator.** All diagnosis is done from CI logs. All fixes are delegated to specialist sub-agents. Never read or edit source files directly.

## Arguments

```
<pr-number> [--max-iterations N]

Examples:
  /ci-monitor 123
  /ci-monitor 123 --max-iterations 5
  /ci-monitor 456 --max-iterations 1
---
$ARGUMENTS
```

**Parsing:** First token = PR number (required). `--max-iterations` (optional, default 3) sets the fix-loop cap. Aliases: `--max`, `-n`.

## Orchestrator Rules

**CRITICAL: You are a lightweight coordinator. Follow these rules:**

1. **Never read source files directly** — sub-agents do that
2. **Never write code or edit files yourself** — sub-agents implement all fixes
3. **Keep sub-agent prompts focused** — include only the failure context they need
4. **Track attempted fixes** — avoid infinite loops on the same failure

## Phase 1: Initialize

1. Fetch PR metadata:
   ```bash
   gh pr view {number} --json headRefName,baseRefName,title,url,state
   ```
2. If the PR is not open, abort: "PR #{number} is {state} — nothing to monitor."
3. Check out the PR's head branch:
   ```bash
   git fetch origin {headRefName} && git checkout {headRefName} && git pull origin {headRefName}
   ```
4. Read the project's `CLAUDE.md` for architecture context (pass to sub-agents later).
5. Initialize tracking state:
   - `iteration = 0`
   - `max_iterations` from args (default 3)
   - `attempted_fixes = []` — list of `{check_name, failure_signature}` tuples
   - `fix_history = []` — list of `{iteration, check, category, description}` records

## Phase 2: Poll CI Checks

1. Fetch current check status:
   ```bash
   gh pr checks {number} --json name,state,conclusion,detailsUrl
   ```

2. Categorize each check:
   - **Pending**: `state` is `PENDING`, `IN_PROGRESS`, or `QUEUED`
   - **Passed**: `conclusion` is `SUCCESS`, `NEUTRAL`, or `SKIPPED`
   - **Failed**: `conclusion` is `FAILURE`, `TIMED_OUT`, `ACTION_REQUIRED`, or `CANCELLED`

3. Decision logic:
   - **All passed** → proceed to Phase 6 (success exit).
   - **Any pending, none failed** → report "Waiting for {N} pending checks: {names}..." and re-poll.
   - **Any pending AND any failed** → wait for pending checks to complete before proceeding (batch all failures in one iteration).
   - **All terminal, some failed** → proceed to Phase 3.

4. **Stall guard**: If checks remain pending with no state change for 30 minutes, proceed to Phase 6 (stalled exit).

## Phase 3: Diagnose Failures

For each failed check:

1. Extract the run ID from `detailsUrl` (parse the GitHub Actions URL pattern: `.../actions/runs/{run-id}`).

2. Fetch failed logs:
   ```bash
   gh run view {run-id} --log-failed
   ```

3. **Categorize the failure** using log content:

   | Category | Signal Patterns | Sub-agent |
   |----------|----------------|-----------|
   | **Build error** | `error CS`, `error MSB`, `Build FAILED`, `could not resolve`, `The type or namespace` | `dotnet-fixer` (single-file) or `dotnet-specialist` (multi-file / architectural) |
   | **Test failure** | `Failed!`, `X Error(s)`, `Assert.`, `Expected:`, `Test Run Failed`, `[FAIL]` | `test-writer` (test needs updating) or `dotnet-fixer` (implementation is wrong) |
   | **Lint/format** | `SA1`, `IDE0`, `CA1`, `dotnet format`, `style violation`, `whitespace` | `dotnet-fixer` |
   | **Security scan** | `CVE-`, `vulnerability`, `security advisory`, `Dependabot`, `snyk`, `trivy` | `security-hardener` |
   | **Workflow/infra** | `docker`, `Dockerfile`, `action`, `workflow`, `yaml`, `runner`, `timeout`, `service unavailable` | `devops-specialist` |

4. **Sub-category disambiguation** for Build/Test:
   - Build error mentioning a single file with a clear error code → `dotnet-fixer`
   - Build error spanning multiple files or involving project references → `dotnet-specialist`
   - Test failure where the test assertion is wrong → `test-writer`
   - Test failure where the implementation is buggy → `dotnet-fixer`
   - If ambiguous → default to `dotnet-fixer`

5. **Batch related failures**: Group failures from the same category that share a root cause into a single fix unit.

6. **Dedup against attempted_fixes**: If a failure has the same `check_name` AND the same `failure_signature` (first 200 chars of error) as a previous attempt, mark it **unfixable** — the prior fix didn't resolve it. Do not retry.

7. If ALL failures are marked unfixable → proceed to Phase 6 (unfixable exit).

## Phase 4: Dispatch Fix Sub-agents

For each failure group (deduplicated, not previously attempted), dispatch the appropriate specialist sub-agent.

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
- PR branch: {headRefName}
- Base branch: {baseRefName}
- Iteration: {current_iteration} of {max_iterations}

## Constraints
- Fix ONLY the CI failure described above
- Do NOT refactor unrelated code
- Do NOT change test expectations unless the test is genuinely wrong
- If the fix requires architectural changes beyond your scope, report back with what's needed instead of making partial changes
```

### Dispatch Rules

- Failures in **different categories** → dispatch sub-agents in **parallel**.
- Multiple failures in the **same category** → batch into a **single sub-agent** dispatch.
- If a test failure depends on a build error being fixed first → dispatch **sequentially**: build fix first, then test fix.

### Agent-Specific Prompt Additions

**For `dotnet-fixer`:**
- Include exact error codes (CS####) and file paths from the log.

**For `dotnet-specialist`:**
- Include broader context about which projects are affected and any project/package reference issues.

**For `test-writer`:**
- Include the test name, expected vs actual values.
- Clarify whether the test or the implementation needs updating.

**For `security-hardener`:**
- Include CVE numbers, affected packages, and suggested remediation from scan output.

**For `devops-specialist`:**
- Include the workflow file path (e.g., `.github/workflows/ci.yml`).
- Include the full step output where the failure occurred.

## Phase 5: Commit, Push, and Loop

1. **Verify changes exist**: Run `git status`. If no files were modified, treat the failure as unfixable for this iteration and note it.

2. **Stage and commit**:
   ```
   fix(ci): {brief description of what was fixed}

   CI monitor iteration {N}/{max}
   Fixes: {comma-separated list of check names addressed}
   ```

3. **Push**:
   ```bash
   git push origin {headRefName}
   ```

4. **Update tracking**:
   - Increment `iteration`.
   - Append each `{check_name, failure_signature}` to `attempted_fixes`.
   - Append fix details to `fix_history`.

5. **Loop decision**:
   - If `iteration >= max_iterations` → proceed to Phase 6 (max iterations exit).
   - Otherwise → return to Phase 2.

## Phase 6: Report Results

Display a summary based on the exit condition.

### Success — All Checks Passing

```
## CI Monitor — PR #{number}: {title}

**Result:** ALL CHECKS PASSING
**Iterations:** {N} fix iteration(s)
**PR:** {url}

### Fix History
| Iteration | Check | Category | Fix Applied |
|-----------|-------|----------|-------------|
| 1 | build | Build error | Added missing using in OrderService.cs |
| 2 | tests | Test failure | Updated assertion in OrderTests.cs |

All CI checks are now green.
```

### Max Iterations Reached

```
## CI Monitor — PR #{number}: {title}

**Result:** MAX ITERATIONS REACHED ({max})
**PR:** {url}

### Remaining Failures
- **{check_name}**: {brief description}

### Fix History
| Iteration | Check | Category | Fix Applied |
|-----------|-------|----------|-------------|

### Recommendation
{Specific advice on what to investigate manually}
```

### Unfixable Failure Detected

```
## CI Monitor — PR #{number}: {title}

**Result:** UNFIXABLE FAILURE DETECTED
**PR:** {url}

### Unfixable Failures
- **{check_name}**: {description} — Same failure persisted after fix attempt in iteration {N}.

### Fix History
| Iteration | Check | Category | Fix Applied |
|-----------|-------|----------|-------------|

### Recommendation
{Specific advice}
```

### CI Checks Stalled

```
## CI Monitor — PR #{number}: {title}

**Result:** CI CHECKS STALLED
**PR:** {url}

### Stalled Checks
- **{check_name}**: {state} for >{duration}

No fixes were attempted. CI checks may be queued or experiencing infrastructure issues.
```

## Output

Report to the user:
- Final result status (PASSING / MAX_ITERATIONS / UNFIXABLE / STALLED)
- Number of iterations executed
- Fix history table with categories
- Any remaining failures with recommendations
- PR URL
- Any sub-agent errors that occurred
