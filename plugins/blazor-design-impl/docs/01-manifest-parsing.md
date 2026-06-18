# Reading a Claude Design Export

A Claude Design export is a directory with this structure:

```
design-reference/           (or any name the user chooses)
├── _ds_manifest.json       ← machine-readable source of truth — start here
├── _ds_bundle.js           ← React component bundle (ignore)
├── readme.md               ← brand narrative (read for aesthetic context)
├── styles.css              ← CSS entry point (mirrors what we'll create)
├── tokens/                 ← 8 CSS token files (copy verbatim)
│   ├── fonts.css
│   ├── colors.css
│   ├── typography.css
│   ├── spacing.css
│   ├── radius.css
│   ├── shadows.css
│   ├── motion.css
│   └── base.css
├── components/
│   ├── buttons/
│   │   ├── Button.jsx          ← React impl → DOM structure reference
│   │   ├── Button.d.ts         ← TypeScript prop types → Blazor parameter spec
│   │   ├── Button.prompt.md    ← Behavioral description
│   │   └── buttons.card.html   ← Preview card (ignore)
│   ├── display/
│   ├── forms/
│   ├── feedback/
│   └── navigation/
├── guidelines/             ← Visual reference only (ignore for implementation)
└── ui_kits/                ← Full React app (reference only)
```

## Step 1: Parse `_ds_manifest.json`

This is your primary spec. Read it and extract:

### `namespace`
The bundle namespace string (e.g. `"PikeCMSDesignSystem_b495f5"`). Not used in Blazor — record it in CLAUDE.md as "design system namespace" for traceability.

### `components`
Array of `{name, sourcePath}`. Each entry becomes one `.razor` + `.razor.css` file pair.

```json
"components": [
  {"name": "Button",    "sourcePath": "components/buttons/Button.jsx"},
  {"name": "Badge",     "sourcePath": "components/display/Badge.jsx"},
  {"name": "Card",      "sourcePath": "components/display/Card.jsx"},
  ...
]
```

Derive spec file paths by replacing `.jsx` extension:
- TypeScript types → `components/buttons/Button.d.ts`
- Behavioral spec → `components/buttons/Button.prompt.md`
- DOM reference → `components/buttons/Button.jsx` (the `.jsx` itself)

### `globalCssPaths`
Ordered array of CSS file paths. Use this exact order when creating `styles.css`:
```json
"globalCssPaths": ["tokens/fonts.css", "tokens/colors.css", ..., "tokens/base.css"]
```

### `tokens`
Full flat token list with `{name, value, kind, definedIn, scope?}`.
- Tokens **without** `scope` are light-mode (default) values.
- Tokens **with** `scope: "[data-theme=\"dark\"]"` are dark-mode overrides.

Use this list to understand what semantic aliases are available without reading every token file:
- `--surface-*` — background surfaces
- `--text-*` — text colors
- `--border-*` — border colors  
- `--accent*` — brand accent (primary CTA color)
- `--success-*`, `--warning-*`, `--danger-*`, `--info-*` — status colors
- `--space-*` — spacing scale (4px base unit)
- `--control-sm/md/lg` — standard control heights (28 / 34 / 40px)
- `--radius-*` — border radius scale
- `--shadow-*` — elevation shadows; `--shadow-focus` for focus rings
- `--duration-*`, `--ease-*` — motion tokens

### `themes`
Array of `{selector, label}`. The first entry's `selector` (e.g. `[data-theme="dark"]`) is the dark mode attribute set on `<html>`.

### `brandFonts`
Array of `{family, tokens[]}`. Fonts are already in `tokens/fonts.css`; note them for CLAUDE.md.

---

## Step 2: Read Component Specs

For each entry in `components`, read these three files before writing any code:

### `.d.ts` — Primary Parameter Spec

Parse the TypeScript interface to extract every prop. Map types to C#:

| TypeScript | C# Blazor |
|---|---|
| `string` | `string?` |
| `string \| undefined` | `string?` |
| `boolean` | `bool` (default `false`) |
| `number` | `int` or `double` |
| `"a" \| "b" \| "c"` | `public enum ComponentVariant { A, B, C }` |
| `React.ReactNode` | `RenderFragment?` |
| `() => void` | `EventCallback` |
| `(value: T) => void` | `EventCallback<T>` |
| JSDoc `@default "primary"` | C# default: `= ComponentVariant.Primary` |

**If the interface extends `React.HTMLAttributes<HTMLElement>` (or any HTML element type)**, the component accepts arbitrary HTML attributes. Add:
```csharp
[Parameter(CaptureUnmatchedValues = true)]
public Dictionary<string, object>? AdditionalAttributes { get; set; }
```

### `.prompt.md` — Behavioral Description

Read for:
- Which variant is the default and its semantic meaning
- Size/height specifications (cross-reference with `--control-sm/md/lg`)
- Icon slot behavior ("pass an SVG node")
- State behaviors: disabled, error/invalid, loading
- Usage rules ("one primary per view", "use ghost for toolbar actions")

### `.jsx` — DOM Structure Reference

**This is critical for getting CSS class names right.** Read to extract:
- Root HTML element (`button`, `div`, `span`, `label`, `input`, `textarea`, `select`, etc.)
- CSS class names and their BEM pattern
- Child element structure (icon wrapper class, label wrapper class, etc.)
- Conditional class logic (how variant/size map to modifier classes)

Example: if the JSX renders:
```jsx
<button className={`btn btn--${variant} btn--${size}${disabled ? ' btn--disabled' : ''}`}>
  {iconLeft && <span className="btn__icon btn__icon--left">{iconLeft}</span>}
  {children}
</button>
```

Then: BEM block = `btn`, variant modifier = `btn--primary`, icon element = `btn__icon`.

---

## Step 3: Build Your Implementation Plan

Before writing any file, compile this inventory:

For each component, note:
1. **C# class name** — same as `name` from manifest
2. **Root HTML element** — from `.jsx`
3. **BEM CSS block** — from `.jsx` class attribute
4. **Parameters** — from `.d.ts` with type mapping applied
5. **Enums needed** — each union string type becomes a nested `public enum`
6. **Needs AdditionalAttributes?** — if `.d.ts` extends HTML attributes
7. **Has icon slots?** — `RenderFragment` named `IconLeft`, `IconRight`, `Icon`, etc.
8. **Has two-way binding?** — form controls need `Value`, `ValueChanged`, `ValueExpression`
9. **Category** — determines implementation pattern (see `03-component-patterns.md`)

Categories map to patterns:
- **Display** (Card, Badge, Tag, Avatar) — pure presentation, no events
- **Action** (Button, IconButton) — click events, variants, sizes
- **Form** (Input, Textarea, Select, Checkbox, Switch, Field) — two-way binding, validation
- **Overlay** (Dialog, Toast, Banner, Tooltip) — visibility state, no JS interop
- **Navigation** (Tabs, NavItem) — active state, routing integration
