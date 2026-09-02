# Theming a report from the host application

The report should read as part of the same product as the application it documents. Derive the
theme automatically; do not ask the user for colours.

## What to look for, in order

Stop at the first source that yields a usable palette.

1. **A design-token file.** `tokens.css`, `theme.css`, `variables.css`, `_variables.scss`,
   `design-tokens.json`, or a Claude Design export. Best source: already structured, already
   named by role.
2. **CSS custom properties in the app's main stylesheet.** Look for a `:root { --… }` block in
   `app.css`, `site.css`, `main.css`, `styles.css`, `wwwroot/css/`, `src/styles/`,
   `assets/css/`.
3. **A framework config.** `tailwind.config.js` (the `theme.extend.colors` block),
   `_bootstrap-overrides.scss`, a MudBlazor or Material theme object in code.
4. **The most frequent non-neutral colour** across the app's stylesheets. Crude, but a brand
   colour is usually the most-repeated hex in a codebase.
5. **Nothing found.** Use the plugin's default palette unchanged — `${CLAUDE_PLUGIN_ROOT}/assets/theme.css`. A neutral,
   legible report is better than a wrong one. Mention in your summary that no app palette was
   found.

Useful starting point:

```bash
grep -rhoE '#[0-9a-fA-F]{6}\b' --include='*.css' --include='*.scss' . \
  | tr 'A-F' 'a-f' | sort | uniq -c | sort -rn | head -20
```

Filter out near-white, near-black and near-grey results before picking — those are surfaces and
text, not the brand colour.

## Mapping

| Report token | Take it from |
| --- | --- |
| `--plane` | the app's page or body background |
| `--surface` | the app's card or panel background |
| `--ink` | the app's primary text colour |
| `--warn` | the app's danger / error / destructive colour |
| `--good` | the app's success colour |
| `--c0` | the app's primary or brand colour |
| `--c1`–`--c5` | the app's chart or status colours if it has them; otherwise derived |

Surfaces and ink carry most of the "same product" feeling. Get those right and the report reads
as a sibling of the app even when the accent colours differ.

## Typography

Colour makes a report match the app. **Type is what makes it look designed rather than
defaulted** — a serif heading over sans body copy reads as a document; sans over sans reads as a
web page. Three tokens carry it: `--font-display` (headings, `.sc-name`), `--font-body`,
`--font-mono` (`code`, figures, `.step-n`, `.when`).

Find the app's faces where you found its colours — a `font-family` on `body`, a
`--font-*`/`$font-*` token, or the Tailwind `theme.fontFamily` block — then pick the preset
nearest to them:

| The app's headings are… | Pass |
| --- | --- |
| A serif or a display serif (Cormorant, Playfair, Lora, Merriweather) | `--display-font serif` |
| A slab or a typewriter face | `--display-font slab` |
| Helvetica/Inter/Karla-ish, or you found nothing | omit — the default system sans |
| Deliberately neutral and tight (Helvetica Neue, Akzidenz) | `--display-font grotesk` |

**Never link a web font.** The app can; the report cannot — it has to render from disk, offline,
in two years, and `build_report.py` rejects the `<link>`. Presets are widely-installed stacks
chosen to sit near a family, not to match it. A literal stack works too:
`--body-font '"Segoe UI", system-ui, sans-serif'`.

The safest strong move is a serif display over the system sans body. Setting `--font-body` to a
serif as well makes long reports harder to skim; do it only when the app itself does.

## One scheme or two

The default theme carries light and dark, and the body carries a `#theme-toggle` button. That is
right for most apps.

When the application has **only one scheme** — a dark-only product, a print-styled internal tool —
match it: pass `--mode dark` (or `--mode light`), take `--plane` and `--surface` from the app's
actual surfaces, and **leave the toggle button out of the body**. A toggle that flips a report
into a scheme the product does not have is worse than no toggle.

```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/derive_theme.py" --primary "#c9a8ec" --mode dark \
    --plane "#161c17" --surface "#1e251f" --display-font serif > .reports/theme.css
```

`--mode` is a property of the repository's theme, not of one report. Decide it once, when
`.reports/` is created.

## Running the derivation

```bash
# minimum: just the brand colour
python3 "$CLAUDE_PLUGIN_ROOT/scripts/derive_theme.py" --primary "#7c3aed" > .reports/theme.css

# better: everything you found
python3 "$CLAUDE_PLUGIN_ROOT/scripts/derive_theme.py" \
    --primary "#7c3aed" --plane "#faf9fb" --surface "#ffffff" \
    --ink "#18181b" --warn "#dc2626" --good "#16a34a" \
    > .reports/theme.css

# pin the app's own chart colours into the categorical series
python3 "$CLAUDE_PLUGIN_ROOT/scripts/derive_theme.py" --primary "#7c3aed" \
    --series "#7c3aed,#f97316,#0ea5e9" > .reports/theme.css
```

Check legibility before committing:

```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/derive_theme.py" --primary "#7c3aed" --check
```

## What the script does, and why

An application palette and a report palette want different things, so the script fills the gap:

- **Six distinguishable categorical colours.** Gantt bars and legends need these; most apps
  define two or three accents at most. Unpinned slots come from an evenly spaced hue wheel
  anchored on the brand colour, so they never collide.
- **A text colour per series colour.** Each `--cN` gets a matching `--cN-ink`, chosen by
  contrast. This is why bar labels stay legible on a yellow bar and on a navy one. Never
  hand-edit a `--cN` without updating its `--cN-ink`.
- **Two contrast constraints per series colour**: at least 4.5:1 against its own bar text, and at
  least 2.2:1 against the page, so a bar reads as a shape and not a wash. Colours are nudged in
  lightness until both hold.
- **A full dark set.** Apps often have no dark mode; reports need one, because they get read on
  phones at night. Hues are preserved and lightness lifted. Under `--mode dark` that set becomes
  the only set, emitted on `:root` with no media query and no toggle hook.
- **Type and rhythm tokens.** `--font-display`, `--font-body`, `--font-mono`, plus `--measure`
  (the prose line length every component respects), `--radius` / `--radius-sm` (small on
  purpose — 6px and 4px; a report is a document, not an app) and `--tracking-caps`.
- **Neutrals derived from the ink.** `--ink-2`, `--ink-muted`, `--grid`, `--axis` and both
  border tokens are mixes of the app's ink and plane, so the rules and labels carry the app's
  warmth or coolness rather than a generic grey. `--shadow` is emitted but only the tooltip
  uses it.

## Cases needing judgement

**A near-neutral brand colour** (a very dark navy, a near-black) produces a low-chroma series
where the six colours are distinguishable by hue but similar in value. Pin explicit series
colours with `--series` if the app has any chart colours at all.

**A very saturated brand colour** is clamped to a calmer saturation band for the series, so a
neon accent yields bars that can carry a label and sit next to five neighbours. `--c0` will be a
little quieter than the brand swatch. Pin it with `--series` only if the app's own charts use the
full-strength colour.

**A brand colour that is already very light** (a pastel, a mint) will be darkened by the
derivation, so the report's `--c0` will not match the app's brand swatch exactly. This is
correct: a pastel bar with a label on it is unreadable. Do not override it back.

**An app with a strict brand guide** may forbid derived colours. If you find a brand document
saying so, pin all six with `--series` and accept whatever contrast results, but say in your
summary which ones fall short.

## Re-deriving

Only when the application's palette actually changes. Do not regenerate per report — already
delivered reports keep their inlined copy of the old theme, which is correct behaviour for an
archived document. A report that silently restyles itself after delivery is a liability.
