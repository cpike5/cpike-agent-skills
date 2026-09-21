# Briefing the builder

The builder is a Sonnet sub-agent with a fresh context. It knows nothing about
the app, the conversation, or your intent. The brief has to carry all of it —
but as pointers plus rules, not as a paste of everything you have read. The two
documents on disk are the content; the brief tells the builder to read them and
how to behave.

## Brief template

Fill the placeholders. Keep the ground rules verbatim; they are the part the
builder is most likely to get wrong without being told.

> **Goal:** produce a clickable HTML prototype of *<feature name>* for the
> *<app name>* app so the product owner can see what the finished feature
> will look like in the browser. This is a prototype, not production code.
>
> **Read first, fully:**
> 1. `<path>/feature-spec.md` — what to build: screens, components,
>    hierarchy, flows, states, sample data.
> 2. `<path>/design-language.md` — how it must look: tokens, layout shell,
>    component markup and CSS to copy.
> 3. For reference when copying markup: `<layout shell file>`,
>    `<shared components folder>`, `<closest existing page>`.
>
> **Produce**, in `<output folder>`:
> - `<file-1>.html` — <screen, state>
> - `<file-2>.html` — <screen, state>
> - `index.html` — a plain list linking every file with its one-line
>   description from the spec.
> <If a `_shell.html` exists: "Start every page from `_shell.html`; do not
> alter it.">
>
> **Ground rules**
> 1. Each file is self-contained: all CSS and JS inline, no links to the
>    app's stylesheets, no CDN or network requests, no build step. It must
>    open from the filesystem with no server and look right.
> 2. Copy, don't reinvent. Use the app's class names and markup from
>    `design-language.md` for every component marked *existing*. Use its
>    tokens (`var(--…)`) for every colour, font, spacing and radius; do not
>    introduce a hex value where a token exists. Reproduce the layout shell
>    exactly, with the correct nav item highlighted.
> 3. Components marked *new* are built from the app's tokens to the spec's
>    description, so they look like siblings of the existing components.
>    If the description leaves something undecided, choose the option most
>    consistent with the existing components and note it in your report.
> 4. Use the spec's sample data verbatim. No lorem ipsum, no "Item 1".
> 5. Implement only the interactivity the spec lists (tabs, a toggle, a
>    validation state, a modal). Plain JavaScript, small. Nothing else needs
>    to work; do not build data handling or persistence.
> 6. Every state the spec assigns to a file must be visible in that file,
>    either as the default view or reachable with a click that is obviously
>    labelled (e.g. a small "Show empty state" link in a corner).
> 7. Icons must render offline: inline the SVGs (from the app's icon set if
>    available) — no icon fonts loaded from the network.
> 8. Charts and other graphics are inline SVG sketches in the app's style,
>    not a charting library.
> 9. Do not create or modify any file outside `<output folder>`. Do not touch
>    `src/` or any application code.
> 10. Do not restyle, "improve", or modernise anything. Fidelity to the
>     existing look is the entire point; a prettier page in a different
>     style is a failure.
>
> **Report back** in under 200 words: the files written, any spec item you
> could not satisfy and why, any decision you had to make that the spec did
> not cover, and any place `design-language.md` was wrong or missing
> something you needed. Do not paste file contents.

## Fix-round brief

After verification, send a *fresh* builder a brief like this rather than
reopening the original:

> **Goal:** correct the prototype in `<output folder>` so it matches
> `feature-spec.md` and `design-language.md` (read both first). Same ground
> rules as the original build (below). Change only what is listed.
>
> **Fixes:**
> - `settings-general.html`: the Settings nav item is not highlighted as
>   active — use the `.nav-item.active` pattern from the design-language doc.
> - `settings-general.html`: Save button uses `#3b82f6`; use
>   `var(--color-primary)`.
> - `settings-notifications.html`: the empty state is missing entirely — add
>   it as a "Show empty state" toggle per rule 6.
>
> <ground rules pasted here>
>
> **Report back:** the fixes applied, anything you could not do.

## Splitting across builders

For more than three or four screens, split by screen or by flow and run the
builders in parallel. To keep the screens consistent with each other:

1. Have one builder (or the first one, before the others start) produce
   `_shell.html`: the layout chrome, the inline token block, and the shared
   component CSS, with an empty content area and a comment marking where page
   content goes.
2. Every other builder's brief says: "Start from `_shell.html`; copy it and
   fill the content area. Do not edit `_shell.html`."
3. No two builders write the same file. The `index.html` is written by you or
   by one designated builder after the others finish.
