---
name: prototype-ui
description: Produce a plain HTML/CSS/JS prototype of a new feature or UI change in the app's own visual language — extract the codebase's design language, write a feature summary and UX spec (pages, components, visual hierarchy, user flows, states), then delegate the actual HTML build to a Sonnet sub-agent and verify the result. Use this whenever the user wants to see what something will look like in the browser before it is built — "prototype the settings page", "mock up the new dashboard", "show me what X would look like", "build a clickable demo of", "wireframe the onboarding flow", "what would the finished feature look like" — even if they never say "prototype" or "mockup". Also use it when another skill (design-feature, a planning session) reaches the point of needing screen mockups and sub-agents are available. Not for production code, and not for a full interactive design workshop (that is design-feature; it can call this skill for its mockup step).
---

# Prototype a UI feature

You are the designer and the orchestrator; a Sonnet sub-agent is the builder.
Your context is for judgment — understanding the feature, reading the app's
visual language, deciding what screens and components exist and how they fit
together. The HTML itself is bulky, mechanical, and easy to check, so it gets
delegated. If you find yourself writing `<div class="card">` blocks, stop: that
is the builder's job.

The result is a set of self-contained HTML files the user can open from the
filesystem and click through, plus the two documents that produced them. The
prototype is a *spec the user can look at*, not a drawing: it uses the app's
real class names, real layout shell, real tokens, and realistic data, so what
they react to is the feature, not the styling.

## What this skill produces

Everything lands in one folder, by default `docs/prototypes/<feature-slug>/`
(check `CLAUDE.md` and the existing `docs/` tree first — if the repo already
keeps designs or mockups somewhere, use that instead and say so).

```
docs/prototypes/settings-page/
├── design-language.md   # extracted from the codebase — tokens, shell, components
├── feature-spec.md      # what's being built — summary, pages, components, flows, states
├── index.html           # links every screen with a one-line description
├── settings-general.html
├── settings-notifications.html
└── settings-general-empty.html   # a separate file when a state differs a lot
```

`design-language.md` is reusable: the next prototype for the same app should
start from it and only refresh it if the app has changed. Check for an existing
one before extracting again.

## Workflow

### 0. Pin down the feature — lightly

If the user has already described the feature (or another skill is invoking
this one with a description), do not re-interview them. Reflect it back in two
or three sentences and probe only real gaps: *which* screens are new versus
changed, what the entry point is, whether there is a scope edge they care about.
One question at a time, and only if it would change what gets built. If you
can make a reasonable assumption, make it, and write it in the spec's
Assumptions section so it is visible rather than silent.

### 1. Extract the design language

Goal: a document that lets an agent who has never seen the app produce a page
that looks like it belongs there. Read `${CLAUDE_PLUGIN_ROOT}/skills/prototype-ui/references/design-language.md` for what
to capture and the template to fill.

**Delegate this when sub-agents are available** — it is exactly the kind of
read-heavy, output-mostly-discarded work that should not fill your context.
Spawn a Sonnet explorer with the extraction brief from the reference file, and
have it write `design-language.md` directly. Read the result and spot-check two
or three claims against the code (does `.btn-primary` actually exist? is the
sidebar really 240px?). If sub-agents are not available, do the extraction
yourself, but read selectively: token files and the shared component folder in
full, then the two or three existing pages closest to what you are building,
not the whole app.

Where to look, roughly in order of value:

- Token / theme files: `*.tokens.css`, `app.css`/`site.css` custom properties,
  a `tailwind.config.*`, a `design-system/` folder, a Claude Design export.
- The shared component library: `Components/Shared/`, `Components/Layout/`,
  `src/components/ui/`, or the framework equivalent.
- The layout shell: `MainLayout.razor`, `_Layout.cshtml`, `App.vue`,
  `layout.tsx` — whatever wraps every page. The prototype must reproduce it.
- Two or three pages closest in kind to the new screens (a settings page for a
  settings feature; a list-and-detail pair for a CRUD feature).

If the app has no real design system — inline styles, bare framework defaults,
three different button styles — say so to the user before continuing, and agree
whether to mirror the existing look faithfully anyway or to prototype in a
proposed style. Do not silently invent a visual language the app does not have;
the user will react to the styling instead of the feature.

### 2. Write the feature summary

The first section of `feature-spec.md` (template in
`${CLAUDE_PLUGIN_ROOT}/skills/prototype-ui/references/feature-spec.md`): what the feature is, who uses it, what problem it
solves, what is in scope and explicitly out of scope, and any constraints
(existing behaviour that must not change, data that must appear, a flow that
must stay under N clicks). Written for the builder, who was not in the
conversation — no "as discussed", no references to the chat.

### 3. Design the UX

This is the part that needs your judgment, so do it yourself. Fill the rest of
`feature-spec.md`:

- **Pages / screens** — each new or changed screen, its route or navigation
  location, and its purpose in one line. Decide page vs. tab vs. modal vs.
  drawer here, following what the app already does for similar things.
- **Visual hierarchy per screen** — what the user's eye should land on first,
  second, third. Primary action, secondary actions, where the destructive one
  lives. Which region is the layout shell (unchanged) and which is new.
- **Components** — for each screen, the components it is made of. Mark each
  one **existing** (name the app's class or component, e.g. `.card`,
  `<AppButton>`), **existing-but-varied** (an existing component in a new
  configuration), or **new**. For every *new* component — a slider, a sparkline
  chart, a colour picker, a tag input — describe it in enough detail that two
  builders would produce roughly the same thing: what it shows, how it behaves,
  which existing tokens it should be built from, and what it should visually
  resemble in the current app.
- **User flows** — the paths through the screens, as short numbered lists.
  "Open settings → Notifications tab → toggle email digest → Save → toast
  confirms". Include the failure path for anything that can fail.
- **States** — per screen: default/populated, empty, loading, error or
  validation. State which of these get their own HTML file and which are shown
  within one file (a tab that can be toggled, a "simulate error" link). Empty
  and error states are where implementation ambiguity hides, so do not skip
  them.
- **Sample data** — concrete, realistic values the builder should use. Real
  names, real-looking amounts and dates, plausible edge cases (a long name, a
  zero, a 300-item list). "Lorem ipsum" and "Item 1" hide layout problems.
- **Interactivity** — what should actually work in the browser: tabs switch,
  modal opens, validation shows on submit, a toggle flips. Keep it to what
  helps the user feel the flow. It is a prototype, not a working app.
- **Assumptions and open questions** — anything you decided without asking.

Keep the spec proportionate. A one-screen change needs a page; a five-screen
feature needs a few. Every line should change what the builder produces.

### 4. Brief the Sonnet builder

Read `${CLAUDE_PLUGIN_ROOT}/skills/prototype-ui/references/builder-brief.md` for the brief template and the builder's
ground rules; paste the ground rules into the brief verbatim rather than
paraphrasing them each time.

The builder starts with no memory. The brief must be self-contained: include
the paths to both documents *and* tell the builder to read them first, list the
files it should produce with the state each one shows, and give the output
folder. Point it at the real layout shell and component files so it can copy
markup rather than reconstruct it from your description.

**Spawning.** In Claude Code use the Task tool with the builder brief as the
prompt. If the Task tool exposes a `model` parameter, set it to `sonnet`. If it
does not, copy `${CLAUDE_PLUGIN_ROOT}/skills/prototype-ui/assets/prototype-builder.md` into the repo's `.claude/agents/`
(it declares `model: sonnet`) and spawn with that agent type. Either way, tell
the user which you used.

**Splitting.** One builder for up to three or four screens. Beyond that, one
builder per screen or per flow, run in parallel, each writing only its own
files — never two builders on the same file. When splitting, have the first
builder (or a quick extra one) produce a `_shell.html` skeleton with the layout
chrome and shared styles that the others copy from, so the screens match each
other, not just the app.

### 5. Verify and fix

A builder reporting "done" is a claim. Check it:

1. Open each HTML file (`view` is enough; render it in a browser or inline
   viewer if the session has one) and walk `feature-spec.md` screen by screen:
   every screen present, every listed component present, every state present,
   sample data used, primary action where the hierarchy said it goes.
2. Check fidelity against `design-language.md`: the layout shell is
   reproduced, the app's class names are used for existing components, no
   external stylesheet or CDN links, no invented colours where a token exists.
3. Check it is self-contained: opening the file from disk with no server and
   no network gives the intended page.

If something is wrong, send the *specific* findings back to a fresh builder as
a fix list ("`settings-general.html`: sidebar is missing the active-state
highlight on Settings; the Save button uses `#3b82f6` instead of
`var(--color-primary)`"). Do not re-run the same brief and hope. Cap it at two
fix rounds; if it is still off, the spec or the design-language document is
probably the problem — fix that, then rebuild.

### 6. Report

Tell the user the folder path, list the screens with one line each, and note
any assumptions you made and anything the design-language extraction found
that they should know (for example, "the app has two competing card styles; I
used the one from the newer pages"). Then stop. Do not start implementing the
feature, and do not create issues or branches.

## When this skill is invoked by another skill

If `design-feature` (or any planning session) calls this at its mockup step,
the feature summary and often the UX design already exist in that session's
notes. Do not redo them: lift them into `feature-spec.md`, extract the design
language if it has not been extracted already, and go straight to briefing the
builder. Save the output where the calling skill says the design docs live.

## Things that go wrong

- **Building the HTML yourself.** It works, and it burns the context that
  should be spent on getting the spec right. The skill exists to delegate.
- **A thin design-language document.** "Uses blue and a sidebar" produces a
  generic page. The builder needs actual tokens, actual class names, actual
  markup snippets. Fidelity is the whole point.
- **A spec that describes the feature but not the screens.** The builder then
  designs the UX itself, and the user reviews the builder's guesses instead of
  yours. Decide the hierarchy, the components and the states before delegating.
- **New components described in one line.** "A slider for the threshold" gives
  the builder a bare `<input type="range">`. Say how it should look in this
  app, what it should be built from, and what it shows.
- **Skipping empty, loading and error states.** These are the states the user
  has not imagined, and where the real implementation will diverge from what
  they expected.
- **Linking the app's stylesheet instead of copying what is needed.** The
  prototype then breaks when the stylesheet moves, and does not open from the
  filesystem. Copy the tokens and the component rules in.
- **Trusting the builder's summary.** Open the files. It takes a minute and
  catches most problems.
