# Git Graph

## Overview

- Syntax prefix: `gitGraph`
- Visualizes branch topology, commits, merges, and tags
- Renders left-to-right by default; time flows left to right
- Default branch is `main` (configurable via `init` directive)

```mermaid
gitGraph
    commit id: "Initial commit"
    branch feature/auth
    checkout feature/auth
    commit id: "Add login page"
    checkout main
    merge feature/auth
```

## Commits

```mermaid
gitGraph
    commit
    commit id: "fix: null check"
    commit id: "feat: payment" tag: "v1.2.0"
    commit id: "revert bad deploy" type: REVERSE
    commit id: "highlight release" type: HIGHLIGHT
```

| Attribute | Syntax | Effect |
|-----------|--------|--------|
| Basic commit | `commit` | Auto-generated ID, no label |
| Custom ID/label | `commit id: "message"` | Sets display label |
| Tag | `commit id: "msg" tag: "v1.0"` | Adds tag badge above commit |
| Type | `commit id: "msg" type: HIGHLIGHT` | Changes commit circle styling |

### Commit Types

| Type | Visual | Use |
|------|--------|-----|
| `NORMAL` | Filled circle | Default commit (implicit when `type` omitted) |
| `REVERSE` | Circle with X | Reverts, rollbacks |
| `HIGHLIGHT` | Filled rectangle | Release commits, milestones |

- Multiple attributes combine: `commit id: "release" tag: "v2.0" type: HIGHLIGHT`

## Branches

```mermaid
gitGraph
    commit
    branch develop order: 1
    branch feature/login order: 2
    checkout feature/login
    commit id: "Add login"
    checkout develop
    merge feature/login
```

- `branch name` -- creates and checks out a new branch from the current HEAD
- `branch name order: N` -- controls vertical position in the diagram; lower number = higher on the diagram
- Branch ordering is visual only; it does not affect merge logic

## Checkout

- `checkout branchName` -- switches the active branch; subsequent `commit` statements apply to this branch
- Must `checkout` an existing branch or `main` -- referencing an undeclared branch causes a parse error

## Merge

```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit id: "feature work"
    checkout main
    merge develop id: "Merge develop" tag: "v1.0.0" type: HIGHLIGHT
```

| Merge attribute | Syntax | Effect |
|----------------|--------|--------|
| Basic merge | `merge branchName` | Auto-generated merge commit |
| Custom label | `merge branchName id: "msg"` | Sets merge commit display label |
| Tag on merge | `merge branchName tag: "v2.0"` | Adds tag badge to merge commit |
| Type | `merge branchName type: REVERSE` | Applies commit type styling to merge commit |

- After `merge`, the current branch remains the one that received the merge (the target, not the source)

## Cherry-Pick

```mermaid
gitGraph
    commit id: "A"
    commit id: "B"
    branch hotfix
    checkout hotfix
    commit id: "C"
    checkout main
    cherry-pick id: "C"
```

- `cherry-pick id: "commitId"` -- re-applies a specific commit onto the current branch
- The `id` value must match the `id` of an existing commit in the diagram exactly
- **When cherry-picking a merge commit**, specify the parent to resolve ambiguity:
  `cherry-pick id: "mergeCommitId" parent: "parentCommitId"`

## Tags

Tags are attached inline on `commit` or `merge` statements:

```mermaid
gitGraph
    commit id: "init"
    commit id: "stable" tag: "v1.0.0"
    branch release/2.0
    checkout release/2.0
    commit id: "rc1" tag: "v2.0.0-rc1"
    checkout main
    merge release/2.0 tag: "v2.0.0" type: HIGHLIGHT
```

- Tags render as badge labels above the commit dot
- Multiple tags on one commit are not supported -- only one `tag:` per statement

## Configuration

```mermaid
%%{init: {
  'gitGraph': {
    'mainBranchName': 'main',
    'mainBranchOrder': 0,
    'showCommitLabel': true,
    'rotateCommitLabel': false,
    'parallelCommits': false
  }
}}%%
gitGraph
    commit id: "first"
    branch develop
    checkout develop
    commit id: "dev work"
```

| Config Key | Default | Effect |
|-----------|---------|--------|
| `mainBranchName` | `"main"` | Name of the primary branch |
| `mainBranchOrder` | `0` | Vertical position of main branch |
| `showCommitLabel` | `true` | Show commit ID / label text on commits |
| `rotateCommitLabel` | `true` | Rotate long commit labels 45 degrees |
| `parallelCommits` | `false` | Align commits across branches by time rather than sequence |

- `rotateCommitLabel: false` improves readability for short labels; leave `true` for long SHA-style labels

## Workflow Pattern: GitFlow

```mermaid
%%{init: {'gitGraph': {'mainBranchName': 'main', 'rotateCommitLabel': false}}}%%
gitGraph
    commit id: "init" tag: "v0.1.0"

    branch develop order: 1
    checkout develop
    commit id: "dev baseline"

    branch feature/payments order: 2
    checkout feature/payments
    commit id: "payment model"
    commit id: "payment api"
    checkout develop
    merge feature/payments id: "Merge payments"

    branch feature/notifications order: 3
    checkout feature/notifications
    commit id: "email templates"
    checkout develop
    merge feature/notifications id: "Merge notifications"

    branch release/1.0 order: 1
    checkout release/1.0
    commit id: "bump version"
    commit id: "fix regression"
    checkout main
    merge release/1.0 id: "Release 1.0" tag: "v1.0.0" type: HIGHLIGHT
    checkout develop
    merge release/1.0 id: "Back-merge 1.0"

    branch hotfix/payment-null order: 1
    checkout hotfix/payment-null
    commit id: "null guard" type: REVERSE
    checkout main
    merge hotfix/payment-null tag: "v1.0.1" type: HIGHLIGHT
    checkout develop
    merge hotfix/payment-null id: "Back-merge hotfix"
```

**GitFlow branch roles:**

| Branch | Purpose | Merges into |
|--------|---------|------------|
| `main` | Stable released code | -- |
| `develop` | Integration branch | `main` (via release) |
| `feature/*` | Individual features | `develop` |
| `release/*` | Release stabilization | `main` + `develop` |
| `hotfix/*` | Production bug fixes | `main` + `develop` |

## Workflow Pattern: Trunk-Based Development

```mermaid
%%{init: {'gitGraph': {'mainBranchName': 'main', 'rotateCommitLabel': false}}}%%
gitGraph
    commit id: "baseline" tag: "v1.0.0"

    branch feature/search order: 1
    checkout feature/search
    commit id: "search index"
    commit id: "search api"
    checkout main
    merge feature/search id: "Squash: search"

    commit id: "hotfix: null ref" type: REVERSE

    branch feature/export order: 1
    checkout feature/export
    commit id: "csv export"
    checkout main
    merge feature/export id: "Squash: export" tag: "v1.1.0" type: HIGHLIGHT
```

**Trunk-based rules:**
- **`main` is always deployable** -- no long-lived integration branches
- Feature branches are **short-lived** (hours to days, not weeks)
- Merge frequently; use feature flags for incomplete work
- **Squash merges** keep `main` history linear and readable

## Common Mistakes

- **Checking out an undeclared branch** -- `checkout foo` before `branch foo` causes a parse error; always declare with `branch` first
- **Cherry-picking with a non-existent id** -- the `id` in `cherry-pick id: "X"` must exactly match a `commit id: "X"` elsewhere in the diagram
- **Using `merge` without being on the target branch** -- you must `checkout targetBranch` before `merge sourceBranch`
- **Expecting horizontal time alignment by default** -- `parallelCommits: false` (default) sequences commits by statement order, not wall-clock time; enable `parallelCommits: true` to align across branches
- **Multiple tags on one commit** -- only one `tag:` attribute per `commit` or `merge` statement is supported
- **Spaces in branch names** -- use `/` or `-` as separators: `feature/login`, not `feature login`
