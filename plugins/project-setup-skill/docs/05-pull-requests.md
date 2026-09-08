# Pull Requests

Template: `${CLAUDE_PLUGIN_ROOT}/assets/github/pull_request_template.md`. Copy to
`.github/pull_request_template.md`; GitHub pre-fills it on PRs opened in the web
UI. PRs opened by tooling bypass it, so `CLAUDE.md` must instruct agents to
mirror the sections.

## Why these five sections

The template exists because a PR body has one reader — the person deciding
whether this is safe to merge — and they need different things than the diff
gives them.

- **Summary** — the *why*. The diff already says what changed; nothing in the
  repository says why it should. This is also what you read a year later when
  `git log` is the only remaining record.
- **Key Changes** — the *what*, grouped by area and naming files, so a reviewer
  starts at the important file instead of at whatever the diff sorts first.
- **Implementation Details** — the decisions a reviewer would otherwise have to
  reverse-engineer: why this approach over the obvious one, what edge case forced
  the odd-looking branch, what the backward-compatibility story is. This is the
  section that prevents "why didn't you just…" review rounds.
- **Deliberately Not Done** — scope seen and consciously left out, with a reason
  and a pointer to where it is tracked. Distinguishes a decision from an
  oversight, which is otherwise indistinguishable from outside.
- **Verification** — what was *actually run*. Not what should pass.

## The rule that matters most

**Verification is a factual report, not a claim of confidence.** "Ran
`dotnet test`, 1104 passed" is verification. "Fully tested" is not. If something
could not be verified, say so plainly and say why — an unverified claim here
costs far more than an acknowledged gap, because it spends the reviewer's trust
on every subsequent PR.

Name the layer, too: "unit tests pass" and "passes against a real Postgres" are
different claims, and only the second covers a query or a constraint
(`${CLAUDE_PLUGIN_ROOT}/docs/07-testing.md`). For UI work, verification means
the change was driven in the running app at both a desktop and a mobile
breakpoint. A screenshot is the
evidence.

## Scope

One PR, one reason to exist. An unrelated fix noticed along the way goes in its
own PR, or in "Deliberately Not Done" with a follow-up reference. Mixed PRs are
reviewed worse and reverted with collateral damage.

## Conventions

- Title: imperative and specific — "Add meal-plan scaling to the Kitchen", not
  "Kitchen updates". It becomes the squash commit subject.
- Never put a model identifier or tool name in a title, body, or commit message.
- A schema change ships with its migration in the same PR. Applying migrations at
  startup means a model change without one fails at runtime, not at build.
- A new or changed agent tool points at its spec. A new feature points at its doc.
- Both CI checks green before requesting review, not after.
