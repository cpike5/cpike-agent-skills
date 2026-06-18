---
name: blazor-design-impl
description: "Implement a Claude Design export into a Blazor project — wires in the CSS design token system, creates Razor components, and adapts existing or new pages to use them. Works in any Blazor project structure (existing app, new project, class library). Invoke when: the user has a Claude Design export and wants to implement it in Blazor; when the user says 'implement the design system in Blazor', 'create Blazor components from the design export', 'add these components to my app', or 'wire up the design system'."
---

# Blazor Design Impl

You are implementing a Claude Design export into a Blazor project.

## Required Inputs

Before doing any work, confirm you have:

1. **Design export path** — directory containing `_ds_manifest.json`, `tokens/`, and `components/`
2. **Target project path** — the Blazor project to integrate into (current directory if not specified)
3. **What to do with pages** — adapt existing pages, create a new showcase page, or skip pages entirely

If any are missing, ask the user before proceeding.

## Execution Phases

Work through these in order. Read each referenced doc before starting that phase.

### Phase 1 — Parse the Design Export

Read `${CLAUDE_PLUGIN_ROOT}/docs/01-manifest-parsing.md`.

Parse `_ds_manifest.json` and each component's `.d.ts` + `.prompt.md` + `.jsx` to understand:
- All CSS token files and their import order
- Every component to implement, its parameters, and its DOM structure
- Dark mode selector

### Phase 2 — Detect the Target Project

Read `${CLAUDE_PLUGIN_ROOT}/docs/02-project-integration.md`.

Explore the target project to find where things belong:
- Where to put CSS files (`wwwroot/css/` or equivalent)
- Where to add the CSS link (`_Host.cshtml`, `App.razor`, `index.html`)
- Where to put component `.razor` files (existing `Components/` folder, or decide with the user)
- Where `_Imports.razor` is (for adding `@using`)
- What the project namespace is

### Phase 3 — Wire the Design System

Still using `${CLAUDE_PLUGIN_ROOT}/docs/02-project-integration.md`.

Place the token CSS files and wire them into the project:
- Copy token files to `wwwroot/css/tokens/` (or a subfolder named after the design system)
- Create a `styles.css` entry point that `@import`s them in the correct order
- Add the `<link>` to the host file
- Create an `app-tokens.css` stub alongside it for app-level overrides

### Phase 4 — Implement Components

Read `${CLAUDE_PLUGIN_ROOT}/docs/03-component-patterns.md`.

For each component in the manifest, create:
- `{ComponentName}.razor` — Blazor component
- `{ComponentName}.razor.css` — scoped styles using semantic tokens

Place them wherever the detection phase identified as the component location.
Add `@using {ComponentNamespace}` to `_Imports.razor` if needed.

### Phase 5 — Handle Pages

Read `${CLAUDE_PLUGIN_ROOT}/docs/04-page-adaptation.md`.

Based on what the user asked for:
- **Adapt existing pages** — read them, identify manual HTML that could use the new components, apply the replacements
- **Create a showcase page** — build a new page that demonstrates every implemented component across all variants and states
- **Skip** — leave pages alone

### Phase 6 — Verify

Run `dotnet build` from the project root. Fix any compilation errors. Report what was added, where it was placed, and how to use it.
