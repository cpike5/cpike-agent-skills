---
name: handoff
description: Generate a short handoff prompt the user can paste into a new chat so a fresh agent can pick up implementation work. Use this whenever the user invokes /handoff, asks for a "handoff prompt", "handoff", "prompt for the next chat/agent/session", or wants to "hand this off" after a design, planning, or implementation session. The output is only the prompt in a code block — no commentary.
---

# Handoff

Produce a prompt for a fresh agent in a new chat. The prompt tells that agent what to complete and where to look. It is copy/paste-ready and nothing else.

## Infer the task from context

Look at what happened in this session and pick the matching case:

- **Design / spec / plan session just finished** → the task is to start implementation. If the plan has phases, the task is Phase 1.
- **Implementation session just finished Phase N** → the task is Phase N+1.
- **The plan deviated, or the user says otherwise** → follow the user or the actual state, not the original plan.
- **No phases** → the task is "implement the design" or the next concrete unit of work.

Never assume the receiving agent has any memory of this chat. Everything it needs must be discoverable from the docs and code you point it at.

## What goes in the prompt

Keep it short. Include only these parts, in this order:

1. **The task**: one bold line — `**Task:** Complete Phase N (<title>) of <feature/project name>.` Name the phase by number and title if the plan has one.
2. **Documents to read**: a `**Read:**` label followed by a bulleted list, one file path per bullet in backticks. Use paths as they exist in the repo — almost always under `docs/`. Cite the exact files touched or referenced in this session; do not invent paths.
3. **Code to explore**: an `**Explore:**` label followed by a bulleted list, one item per bullet in backticks. List the services, classes, modules, or files that matter for this task — the things an agent would waste time discovering on its own. Names only, a short list.
4. **Go**: a final plain line — `Then proceed with the implementation.`

Add a single `**Note:**` line between Explore and Go only if something essential is not in the docs — e.g. a decision made mid-session that changed the plan. Otherwise leave it out.

## What stays out

- What was completed, test status, verification, commit state
- Summaries of the design or plan (the docs are the source of truth)
- Instructions to run `/handoff` again — the user asks for it manually
- Tone directives, persona, or general best-practice reminders
- Any commentary, preamble, headers, or explanation outside the code block

## Output format

Respond with **only** a fenced code block (` ```markdown `) containing the prompt. No text before or after it.

Inside the block, use basic markdown only: bold labels, bulleted lists, backticks for paths and identifiers, and blank lines between sections. No headers, tables, numbered lists, or nested bullets.

Skeleton:

```markdown
**Task:** Complete Phase N (<title>) of <feature/project name>.

**Read:**
- `<path>`
- `<path>`

**Explore:**
- `<identifier>`
- `<identifier>`

Then proceed with the implementation.
```

## Examples

After a design session that produced `docs/design/notification-service.md` and `docs/plans/notification-service-plan.md` with four phases:

```markdown
**Task:** Complete Phase 1 (Domain model and persistence) of the notification service.

**Read:**
- `docs/design/notification-service.md`
- `docs/plans/notification-service-plan.md`

**Explore:**
- `NotificationRepository`
- `OutboxPublisher` (existing)
- EF Core configuration under `src/Infrastructure/Persistence`

Then proceed with the implementation.
```

After finishing Phase 2 of that plan:

```markdown
**Task:** Complete Phase 3 (Delivery channels) of the notification service.

**Read:**
- `docs/plans/notification-service-plan.md`
- `docs/design/notification-service.md`

**Explore:**
- `NotificationDispatcher`
- `INotificationChannel`
- `EmailChannel`

Then proceed with the implementation.
```

After a session where the plan changed:

```markdown
**Task:** Complete Phase 3 (Delivery channels) of the notification service.

**Read:**
- `docs/plans/notification-service-plan.md`
- `docs/design/notification-service.md`

**Explore:**
- `NotificationDispatcher`
- `INotificationChannel`

**Note:** SMS delivery was dropped from scope in Phase 2; only implement the email channel.

Then proceed with the implementation.
```
