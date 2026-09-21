# The feature spec

`feature-spec.md` is written for the builder, who was not in the conversation
and has not read the codebase. It says *what* to build and *how it should be
organised*; `design-language.md` says how it should look. Between the two, the
builder should never have to make a design decision — only a rendering one.

Scale it to the feature. A single new modal needs half a page. A multi-screen
feature needs a section per screen. Cut anything that would not change what the
builder produces.

## Template

```markdown
# Feature spec — <feature name>
Prototype folder: `<path>`. Design language: `design-language.md`.

## Summary
<Two to four sentences: what the feature is, who uses it, what problem it
solves. Written as a description of the finished feature, not the chat.>

**In scope:** …
**Out of scope:** …
**Constraints:** <existing behaviour that must not change, required data,
performance/accessibility requirements, anything the user insisted on>

## Screens
| # | Screen | Location / route | New or changed | File |
|---|--------|------------------|----------------|------|
| 1 | Settings — General | `/settings` (new top-level nav item, after Reports) | New | `settings-general.html` |
| 2 | Settings — Notifications | `/settings/notifications` (tab within 1) | New | `settings-notifications.html` |

## Screen 1 — Settings — General
**Purpose:** …
**Layout:** <which shell regions are unchanged; what the content area contains,
top to bottom / left to right>
**Visual hierarchy:** 1) page title + description, 2) the form sections,
3) Save (primary, sticky footer), Discard (secondary, beside it). Danger zone
(delete workspace) is last, visually separated, uses the danger button.
**Components:**
- Page header — existing (`.page-header`)
- Tab bar — existing (`.tabs`), tabs: General, Notifications, Integrations,
  Billing. Active = General.
- Settings section — existing-but-varied: `.card` with a title and description
  row on the left and controls on the right (two-column inside the card; see
  sample layout below)
- Text input, select, toggle — existing (`.input`, `.select`, `.toggle`)
- Threshold slider — **new**. A horizontal range control 0–100 with the current
  value shown in a small `.badge` to its right, updating live. Track uses
  `--color-border`, filled portion `--color-primary`, thumb a 16px circle with
  `--shadow-sm`. Should feel like a sibling of `.toggle`.
- Sticky action footer — **new**. Full-width bar pinned to the bottom of the
  content area, `--color-surface` background, top border, contains Discard +
  Save right-aligned. Appears only when the form is dirty (in the prototype:
  always visible, with a note).
**States:**
- Populated (default) — in `settings-general.html`
- Validation error — same file; clicking Save with the workspace name empty
  shows the app's inline error style under that field
- Loading — not shown (page loads with data in this app)
**Sample data:** Workspace "Northwind Traders", owner "Priya Raman", timezone
"America/Toronto", threshold 65, plan "Team (12 seats)".

## Screen 2 — …

## User flows
1. **Change the alert threshold:** Nav → Settings → General → drag slider →
   footer appears → Save → toast "Settings saved" → footer disappears.
2. **Failed save:** … → Save → inline error on the offending field, footer
   stays, toast not shown.

## Interactivity to implement
- Tabs switch between the two screens (link between the files is fine).
- Slider updates its badge live.
- Save with empty workspace name shows the validation state; otherwise shows
  the toast.
- Nothing else needs to work.

## Assumptions
- Settings is a top-level nav item rather than under the account menu, because
  the app's other admin areas (Users, Reports) are top-level.
- …

## Open questions
- …
```

## Notes on filling it in

- **Component classification matters.** *Existing* means "copy the markup from
  the design-language doc". *Existing-but-varied* means "start from that
  markup and change X". *New* means "build it from the tokens, to this
  description". The builder will treat these differently; mislabelling a new
  component as existing produces a hunt for a class that does not exist.
- **Say where the primary action goes.** Left unsaid, every builder puts it
  somewhere different.
- **Decide page vs. tab vs. modal yourself,** by looking at what the app does
  for comparable features. Do not offload that to the builder.
- **Sample data should stress the layout.** Include the long name, the zero,
  the overdue item, the list that needs scrolling.
- **Assumptions are not optional.** Anything you chose without asking the user
  goes here, so the user can see and reverse it.
