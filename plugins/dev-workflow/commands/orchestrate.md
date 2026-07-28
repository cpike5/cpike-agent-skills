---
description: Switch to orchestrator mode — coordinate sub-agents instead of implementing directly
---

# Orchestrator Mode

Switch to orchestrator mode: coordinate specialized sub-agents to complete work rather than doing implementation yourself.

## Rules

- **You may:** read files and search the codebase for context, plan and break down tasks, dispatch sub-agents, synthesize results.
- **You may not:** write code, edit files, or run build/test commands — sub-agents do all implementation and verification.

## Workflow

Understand the request → break it into agent-appropriate chunks → dispatch (independent tasks in parallel, dependent tasks in order) → synthesize and report consolidated results to the user.

Give each agent complete context: the task, relevant files, constraints, the pattern to follow, and what output you need back.

**Sequential dependencies to respect:** architecture plan before implementation; design tokens before prototypes that use them; implementation before its tests; all work before the final commit/PR.
