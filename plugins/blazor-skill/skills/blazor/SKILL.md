---
name: blazor
description: "Use this skill when implementing Blazor pages, components, forms, or any Blazor UI work. Covers render modes (InteractiveServer, InteractiveWebAssembly, InteractiveAuto, Static SSR), component lifecycle, state management, JS interop, routing, styling (CSS isolation, .razor.css), design aesthetics, DI, auth (AuthorizeView, Identity), EditForm, and common UX patterns (modals, toasts, Virtualize). Produces visually distinctive output that avoids generic AI aesthetics. Invoke when: creating or modifying .razor files, working with EditForm or input components, configuring render modes, debugging Blazor-specific issues (event handlers not working, prerendering problems, auth issues), or when the user asks about Blazor patterns."
---

# Blazor Development Knowledge Base

You are implementing Blazor components. Read the relevant reference docs below based on what you're building. **Always check render mode first** — it's the #1 source of bugs.

## Design Thinking

Before coding any UI, commit to a **bold aesthetic direction**. Consider the purpose, audience, and tone — then choose a clear visual identity (minimal, maximalist, editorial, brutalist, etc.) and execute it with precision. Unless brand guidelines dictate otherwise, avoid generic AI aesthetics: no Inter/Roboto defaults, no purple gradients on white, no cookie-cutter card grids. Every project deserves a fresh, intentional design. See `12-design-aesthetics.md` for full guidance on typography, color, motion, and spatial composition in Blazor.

## Quick Decision: What Render Mode?

- Need SEO, HttpContext, or cookie auth? → **Static SSR** (no @rendermode)
- Need interactivity with low latency? → **@rendermode InteractiveServer**
- Need offline/client-side? → **@rendermode InteractiveWebAssembly**
- Want both? → **@rendermode InteractiveAuto**

If event handlers don't work, CHECK THE RENDER MODE FIRST — starting with `<Routes>` in `App.razor`. Per-page `@rendermode` directives are **silently ignored** if `<Routes>` has no render mode.

## Reference Documentation

Read the relevant docs based on your task:

### Always Read First
- ${CLAUDE_PLUGIN_ROOT}/docs/01-render-modes.md — The foundation. Understand which mode you're in before writing any code.

### Core Topics (read as needed)
- ${CLAUDE_PLUGIN_ROOT}/docs/02-component-lifecycle.md — OnInitialized, OnAfterRender, disposal, prerendering double-execution
- ${CLAUDE_PLUGIN_ROOT}/docs/03-forms-validation.md — EditForm, input components, DataAnnotations, custom validation
- ${CLAUDE_PLUGIN_ROOT}/docs/04-state-management.md — StateHasChanged, cascading values, PersistentComponentState, browser storage
- ${CLAUDE_PLUGIN_ROOT}/docs/05-components.md — Parameters, RenderFragment, generics, DynamicComponent, Virtualize, @key, @ref
- ${CLAUDE_PLUGIN_ROOT}/docs/06-js-interop.md — IJSRuntime, module imports, ElementReference, calling .NET from JS, disposal
- ${CLAUDE_PLUGIN_ROOT}/docs/07-routing-navigation.md — @page, route params, NavigationManager, query strings, NavLink
- ${CLAUDE_PLUGIN_ROOT}/docs/08-styling.md — CSS isolation (.razor.css), ::deep, conditional classes, design tokens, theming
- ${CLAUDE_PLUGIN_ROOT}/docs/09-dependency-injection.md — Service lifetimes, @inject, OwningComponentBase, HttpClient patterns
- ${CLAUDE_PLUGIN_ROOT}/docs/10-event-handling-performance.md — Event handling, debouncing, Virtualize, modals, toasts, file upload
- ${CLAUDE_PLUGIN_ROOT}/docs/11-authentication-authorization.md — AuthorizeView, [Authorize], HttpContext pain points, Identity UI

### Design & Aesthetics
- ${CLAUDE_PLUGIN_ROOT}/docs/12-design-aesthetics.md — Typography, color systems, motion/animation, spatial composition, anti-patterns, Blazor-specific design tips

## Critical Rules (Common Mistakes)

1. **No @rendermode = Static SSR** — Event handlers (`@onclick`, `@oninput`) are INERT. Add a render mode. **Check `App.razor` first**: `<Routes @rendermode="InteractiveServer" />` must be set, or per-page `@rendermode` directives do nothing.
2. **JS interop only in OnAfterRender** — Not available during OnInitialized or prerendering.
3. **OnInitializedAsync runs TWICE with prerendering** — Use `[PersistentState]` (.NET 10+) or `PersistentComponentState`.
4. **Always dispose**: IJSObjectReference, DotNetObjectReference, event subscriptions, CancellationTokenSource.
5. **HttpContext is NOT available in interactive render modes** — Use `AuthenticationStateProvider` instead.
6. **Identity pages MUST be Static SSR** — They need HttpContext for cookies.
7. **Singleton services on Blazor Server leak between users** — Use `AddScoped`.
8. **StateHasChanged from background threads** — Wrap in `InvokeAsync(StateHasChanged)`.
9. **FormName is required for SSR forms** — Without it, Blazor can't dispatch the POST.
10. **Cascading values don't cross render mode boundaries** — Use `AddCascadingValue` in DI instead.
