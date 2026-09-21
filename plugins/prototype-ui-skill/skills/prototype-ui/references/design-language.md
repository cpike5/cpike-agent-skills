# Extracting the design language

The design-language document has one job: let a builder who has never seen the
app produce a page that looks like it belongs there. Everything in it should be
*copied from the code*, not described from impression. "The buttons are
rounded" is an impression; `.btn { border-radius: var(--radius-md); }` is a
fact the builder can reuse.

## Explorer brief (when delegating the extraction)

Spawn a Sonnet sub-agent with this, filling the placeholders:

> **Goal:** produce `<output-path>/design-language.md` describing the visual
> language of this app precisely enough that another agent can build a new
> page in plain HTML/CSS that is indistinguishable in style from the existing
> ones. Do not modify any file outside `<output-path>`.
>
> **Read, in this order:** `CLAUDE.md` and any `docs/` design or style
> documentation; theme/token files (`*.tokens.css`, `app.css`, `site.css`,
> `tailwind.config.*`, `design-system/`, any Claude Design export); the shared
> component folder (`<path if known>`); the layout shell (`<path if known>`);
> then these pages, which are closest to what will be prototyped:
> `<page paths>`. Read component and page markup fully — you need the actual
> class names and structure, not a summary of them.
>
> **Write** the document using the template below. Every colour, font,
> spacing value and class name must come from the code; where you are
> inferring something (for example, a convention you see repeated but never
> declared), mark it *(inferred)*. Include real markup snippets for each
> component, trimmed to the structural minimum — the builder will copy them.
> If the app has no consistent design system (competing styles, inline CSS,
> framework defaults) say so at the top and describe the *most recent*
> style, naming which pages use it.
>
> **Report back** in under 150 words: where the tokens live, whether the
> system is consistent, and anything the prototype will find hard to
> reproduce (icon fonts, canvas charts, third-party widgets). Do not paste
> the document into your report; it is on disk.

## What to capture

Not every app has every one of these. Capture what exists; note what does not.

**Tokens.** Colour palette as CSS custom properties (name, value, and what it
is used for — background, surface, border, text, primary, danger, success…).
Font families with fallbacks, the type scale (sizes and weights actually used
for h1/h2/body/small/mono), line-height, letter-spacing if set. Spacing scale.
Border radii. Shadows. Breakpoints. Transitions. If tokens are Tailwind
classes rather than custom properties, record the Tailwind config and the
classes the app actually uses for each role.

**Dark mode / themes.** Does the app have one? How is it switched (class on
`<html>`, `prefers-color-scheme`, a data attribute)? Which tokens change?

**Layout shell.** The chrome every page sits in: sidebar or top nav, its width
and background, where the logo goes, how the current item is highlighted,
where user/account controls live, the content area's max-width and padding,
whether there is a page header region and what goes in it (title, breadcrumb,
actions). Include the markup, trimmed.

**Page idioms.** How a page is titled. Where primary actions sit (top right of
the header? bottom of a form?). How lists and tables are laid out; how a
detail view is laid out; how forms group fields and where labels go. How
sections are separated. How empty, loading and error states are shown
elsewhere in the app (a specific component? plain text? nothing?).

**Component catalogue.** For each shared component — button variants, inputs,
select, checkbox/toggle, card, table, tabs, modal/dialog, toast/alert, badge,
dropdown/menu, pagination, avatar, and anything domain-specific — record: the
class names or component name, a trimmed markup snippet, the states it
supports (hover, active, disabled, error), and the CSS that makes it look the
way it does. Note which are present but rarely used.

**Icons.** Which set (Lucide, Heroicons, Font Awesome, an SVG sprite, an icon
font) and how they are referenced. The builder must be able to reproduce
icons offline — record whether the SVGs can be inlined and where they are.

**Data display.** Number, currency and date formats as shown in the UI.
Charts: which library, and what the existing ones look like (so a new chart
can be sketched in inline SVG in the same style).

**Motion.** Any transitions or animations the app uses consistently.

**Gaps and inconsistencies.** Anything the prototype will have to decide
about because the app itself has not.

## Template

```markdown
# Design language — <App name>
Extracted <date> from <commit or branch>. Source files: <list>.
Consistency: <consistent | mostly consistent, see Gaps | inconsistent — describing the style used on <pages>>

## Tokens
```css
:root {
  --color-bg: #…;        /* page background */
  --color-surface: #…;   /* cards, panels */
  …
  --font-sans: …;
  --radius-md: …;
  --shadow-sm: …;
}
```
Type scale: …
Spacing: …
Dark mode: …

## Layout shell
<one paragraph, then trimmed markup + the CSS that positions it>

## Page idioms
- Page header: …
- Primary action placement: …
- Lists/tables: …
- Forms: …
- Empty / loading / error: …

## Components
### Button
Classes: `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-sm`
```html
<button class="btn btn-primary">Save changes</button>
```
```css
.btn { … }
```
States: …
### Card
…

## Icons
…

## Data display
…

## Gaps and inconsistencies
- …
```
