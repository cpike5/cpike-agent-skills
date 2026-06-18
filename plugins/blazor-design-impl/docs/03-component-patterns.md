# Component Implementation Patterns

## Naming Conventions

| Concept | Convention | Example |
|---|---|---|
| Razor file | PascalCase, same as manifest `name` | `Button.razor` |
| BEM CSS block | Derived from `.jsx` class names | `.btn`, `.badge`, `.card` |
| Enum type | `{ComponentName}{PropName}` | `ButtonVariant`, `ButtonSize` |
| Enum values | PascalCase of the string union members | `"primary"` → `Primary` |
| CSS variant modifier | `{block}--{lowerCaseEnumValue}` | `.btn--primary`, `.badge--success` |
| CSS size modifier | `{block}--{lowerCaseSize}` | `.btn--sm`, `.btn--lg` |
| CSS element | `{block}__{partName}` | `.btn__icon`, `.card__header` |

**Derive BEM class names directly from the `.jsx` source.** Do not invent class names.

---

## General Razor Component Template

```razor
<{root-element} class="@CssClass" [event-bindings] @attributes="AdditionalAttributes">
    @if (IconLeft != null)
    {
        <span class="{block}__icon {block}__icon--left">@IconLeft</span>
    }
    @ChildContent
    @if (IconRight != null)
    {
        <span class="{block}__icon {block}__icon--right">@IconRight</span>
    }
</{root-element}>

@code {
    public enum {ComponentName}Variant { Primary, Secondary, Ghost, Subtle, Danger }
    public enum {ComponentName}Size { Sm, Md, Lg }

    [Parameter] public {ComponentName}Variant Variant { get; set; } = {ComponentName}Variant.Primary;
    [Parameter] public {ComponentName}Size Size { get; set; } = {ComponentName}Size.Md;
    [Parameter] public bool Disabled { get; set; }
    [Parameter] public RenderFragment? ChildContent { get; set; }
    [Parameter] public RenderFragment? IconLeft { get; set; }
    [Parameter] public RenderFragment? IconRight { get; set; }
    [Parameter] public EventCallback OnClick { get; set; }
    [Parameter(CaptureUnmatchedValues = true)]
    public Dictionary<string, object>? AdditionalAttributes { get; set; }

    private string CssClass => string.Join(" ", new[]
    {
        "{block}",
        $"{block}--{Variant.ToString().ToLower()}",
        Size != {ComponentName}Size.Md ? $"{block}--{Size.ToString().ToLower()}" : null,
        Disabled ? "{block}--disabled" : null,
    }.Where(c => c != null));
}
```

Adapt this template to the actual component — not every component has all slots or parameters.

---

## Parameter Rules

### Enums
- Define as `public enum` **inside** `@code {}` — this keeps them discoverable without extra `using` statements
- Set the default to whatever the `.prompt.md` identifies as the default variant
- If there is no explicit default in the spec, use the first value
- C# enum value casing: `Primary` not `primary`. CSS modifier uses `.ToLower()` at runtime.

### RenderFragment (icon slots, named content areas)
- Named `ChildContent` for the main body content
- Named after the JSX prop for other slots: `IconLeft`, `IconRight`, `Action`, `Footer`, etc.
- The consumer provides an inline Lucide `<svg>` element — the component just renders it as-is
- Sizing SVGs: use `::deep svg` in scoped CSS (see CSS section below)

### EventCallback
- Use `EventCallback` (not `Action` or `Func`) — Blazor manages rendering lifecycle through it
- Typed variant: `EventCallback<T>` where `T` is the event payload (e.g. `EventCallback<string>`)
- Common bindings: `EventCallback OnClick`, `EventCallback<MouseEventArgs> OnClick` for raw event args

### AdditionalAttributes
- Add `[Parameter(CaptureUnmatchedValues = true)] public Dictionary<string, object>? AdditionalAttributes { get; set; }` **only** when the `.d.ts` interface extends an HTML attributes type (`React.ButtonHTMLAttributes`, `React.InputHTMLAttributes`, etc.)
- Spread with `@attributes="AdditionalAttributes"` on the root HTML element
- Do NOT add to pure container/layout components (Card, Field, etc.) that don't need HTML passthrough

---

## Two-Way Binding (Form Controls)

For form controls with `@bind-Value` support:

```razor
<input
    id="@Id"
    value="@Value"
    @oninput="HandleChange"
    class="@CssClass"
    disabled="@Disabled"
    @attributes="AdditionalAttributes" />

@code {
    [Parameter] public string? Value { get; set; }
    [Parameter] public EventCallback<string?> ValueChanged { get; set; }
    [Parameter] public Expression<Func<string?>>? ValueExpression { get; set; }
    [Parameter] public string? Id { get; set; }
    [Parameter] public bool Disabled { get; set; }
    [Parameter] public bool Invalid { get; set; }
    [Parameter(CaptureUnmatchedValues = true)]
    public Dictionary<string, object>? AdditionalAttributes { get; set; }

    private async Task HandleChange(ChangeEventArgs e)
    {
        Value = e.Value?.ToString();
        await ValueChanged.InvokeAsync(Value);
    }
}
```

Include `ValueExpression` for `EditForm` validation integration — without it, field validation messages won't work.

For boolean controls (Checkbox, Switch):
```csharp
[Parameter] public bool Value { get; set; }
[Parameter] public EventCallback<bool> ValueChanged { get; set; }
[Parameter] public Expression<Func<bool>>? ValueExpression { get; set; }
```

---

## CSS Template

```css
/* ── {ComponentName} ─────────────────────────────── */

.{block} {
    /* layout */
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    /* sizing */
    height: var(--control-md);
    padding: 0 var(--space-4);
    /* typography */
    font-family: var(--font-sans);
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    line-height: 1;
    white-space: nowrap;
    /* shape */
    border-radius: var(--radius-md);
    border: 1px solid transparent;
    /* interaction */
    cursor: pointer;
    user-select: none;
    /* motion */
    transition:
        background-color var(--duration-instant) var(--ease-standard),
        border-color var(--duration-instant) var(--ease-standard),
        color var(--duration-instant) var(--ease-standard),
        box-shadow var(--duration-instant) var(--ease-standard);
}

/* Variant modifiers */
.{block}--primary {
    background: var(--accent);
    color: var(--text-on-accent);
}

.{block}--primary:hover:not(:disabled) {
    background: var(--accent-hover);
}

.{block}--primary:active:not(:disabled) {
    background: var(--accent-active);
}

.{block}--secondary {
    background: var(--surface-card);
    color: var(--text-primary);
    border-color: var(--border-default);
}

.{block}--secondary:hover:not(:disabled) {
    background: var(--surface-hover);
}

.{block}--ghost {
    background: transparent;
    color: var(--text-secondary);
}

.{block}--ghost:hover:not(:disabled) {
    background: var(--surface-hover);
    color: var(--text-primary);
}

/* Size modifiers */
.{block}--sm {
    height: var(--control-sm);
    padding: 0 var(--space-3);
    font-size: var(--text-xs);
}

.{block}--lg {
    height: var(--control-lg);
    padding: 0 var(--space-5);
    font-size: var(--text-base);
}

/* Focus ring */
.{block}:focus-visible {
    outline: none;
    box-shadow: var(--shadow-focus);
}

/* Disabled */
.{block}:disabled,
.{block}--disabled {
    opacity: 0.45;
    cursor: not-allowed;
    pointer-events: none;
}

/* Icons passed as RenderFragment — size via ::deep */
.{block}__icon ::deep svg {
    width: 16px;
    height: 16px;
    stroke: currentColor;
    stroke-width: 2;
    fill: none;
    flex-shrink: 0;
}
```

### CSS Token Rules

**Always use semantic aliases. Never use raw ramp values** (`--slate-900`, `--terra-500`).

| Category | Token |
|---|---|
| Backgrounds | `--surface-card`, `--surface-app`, `--surface-sidebar`, `--surface-hover`, `--surface-sunken` |
| Text | `--text-primary`, `--text-secondary`, `--text-tertiary`, `--text-accent`, `--text-on-accent` |
| Borders | `--border-subtle`, `--border-default`, `--border-strong`, `--border-accent` |
| Accent | `--accent`, `--accent-hover`, `--accent-active`, `--accent-subtle`, `--accent-subtle-hover` |
| Status | `--success-fg/bg/solid`, `--warning-fg/bg/solid`, `--danger-fg/bg/solid`, `--info-fg/bg/solid` |
| Sizing | `--control-sm` (28px), `--control-md` (34px), `--control-lg` (40px) |
| Shadow | `--shadow-xs` through `--shadow-xl`, `--shadow-focus` (focus ring), `--shadow-accent` |
| Motion | `--duration-instant` (80ms), `--duration-fast` (120ms), `--ease-standard` |

Dark mode is automatic — semantic aliases are redeclared under `[data-theme="dark"]` in the token files. Components need no dark-mode rules.

---

## Component Category Patterns

### Display Components (Card, Badge, Tag, Avatar)

Pure presentation — no events, no `AdditionalAttributes`. Root is `<div>` or `<span>`.

```razor
<span class="@CssClass">
    @if (Dot) { <span class="badge__dot" aria-hidden="true"></span> }
    @ChildContent
</span>

@code {
    public enum BadgeTone { Neutral, Success, Warning, Danger, Info, Accent }

    [Parameter] public BadgeTone Tone { get; set; } = BadgeTone.Neutral;
    [Parameter] public bool Dot { get; set; }
    [Parameter] public RenderFragment? ChildContent { get; set; }

    private string CssClass => string.Join(" ", new[]
    {
        "badge",
        $"badge--{Tone.ToString().ToLower()}",
        Dot ? "badge--dot" : null,
    }.Where(c => c != null));
}
```

```css
.badge { display: inline-flex; align-items: center; gap: var(--space-1); padding: 2px var(--space-2); font-size: var(--text-xs); font-weight: var(--weight-medium); border-radius: var(--radius-pill); white-space: nowrap; }
.badge--neutral { background: var(--surface-hover); color: var(--text-secondary); }
.badge--success { background: var(--success-bg); color: var(--success-fg); }
.badge--warning { background: var(--warning-bg); color: var(--warning-fg); }
.badge--danger  { background: var(--danger-bg);  color: var(--danger-fg);  }
.badge--info    { background: var(--info-bg);    color: var(--info-fg);    }
.badge--accent  { background: var(--accent-subtle); color: var(--text-accent); }
.badge__dot { width: 6px; height: 6px; border-radius: var(--radius-full); background: currentColor; flex-shrink: 0; }
```

### Action Controls (Button, IconButton)

Add `EventCallback OnClick`, `AdditionalAttributes`, `Disabled`. Root is `<button type="@Type">`.

```razor
<button class="@CssClass" type="@Type" disabled="@Disabled" @onclick="OnClick" @attributes="AdditionalAttributes">
    @if (IconLeft != null) { <span class="btn__icon btn__icon--left">@IconLeft</span> }
    @ChildContent
    @if (IconRight != null) { <span class="btn__icon btn__icon--right">@IconRight</span> }
</button>

@code {
    public enum ButtonVariant { Primary, Secondary, Ghost, Subtle, Danger }
    public enum ButtonSize { Sm, Md, Lg }

    [Parameter] public ButtonVariant Variant { get; set; } = ButtonVariant.Primary;
    [Parameter] public ButtonSize Size { get; set; } = ButtonSize.Md;
    [Parameter] public bool Disabled { get; set; }
    [Parameter] public bool FullWidth { get; set; }
    [Parameter] public string Type { get; set; } = "button";
    [Parameter] public RenderFragment? ChildContent { get; set; }
    [Parameter] public RenderFragment? IconLeft { get; set; }
    [Parameter] public RenderFragment? IconRight { get; set; }
    [Parameter] public EventCallback OnClick { get; set; }
    [Parameter(CaptureUnmatchedValues = true)]
    public Dictionary<string, object>? AdditionalAttributes { get; set; }

    private string CssClass => string.Join(" ", new[]
    {
        "btn",
        $"btn--{Variant.ToString().ToLower()}",
        Size != ButtonSize.Md ? $"btn--{Size.ToString().ToLower()}" : null,
        FullWidth ? "btn--full" : null,
        Disabled ? "btn--disabled" : null,
    }.Where(c => c != null));
}
```

### Form Controls (Input, Textarea, Select)

Use two-way binding with `ValueExpression`. Add `Invalid` parameter for validation state.

The `Field` component (if present in the manifest) is a label-wrapper — it takes `Label`, `For`, `Hint?`, `Error?`, `Required` parameters and renders `ChildContent` below the label. It does NOT use two-way binding itself.

```razor
<div class="@CssClass">
    @if (IconLeft != null)
    {
        <span class="input__icon input__icon--left">@IconLeft</span>
    }
    <input
        id="@Id"
        type="@Type"
        value="@Value"
        placeholder="@Placeholder"
        disabled="@Disabled"
        @oninput="HandleChange"
        @attributes="AdditionalAttributes" />
    @if (Trailing != null)
    {
        <span class="input__trailing">@Trailing</span>
    }
</div>

@code {
    public enum InputSize { Sm, Md, Lg }

    [Parameter] public InputSize Size { get; set; } = InputSize.Md;
    [Parameter] public string? Value { get; set; }
    [Parameter] public EventCallback<string?> ValueChanged { get; set; }
    [Parameter] public Expression<Func<string?>>? ValueExpression { get; set; }
    [Parameter] public string Type { get; set; } = "text";
    [Parameter] public string? Id { get; set; }
    [Parameter] public string? Placeholder { get; set; }
    [Parameter] public bool Disabled { get; set; }
    [Parameter] public bool Invalid { get; set; }
    [Parameter] public RenderFragment? IconLeft { get; set; }
    [Parameter] public RenderFragment? Trailing { get; set; }
    [Parameter(CaptureUnmatchedValues = true)]
    public Dictionary<string, object>? AdditionalAttributes { get; set; }

    private async Task HandleChange(ChangeEventArgs e)
    {
        Value = e.Value?.ToString();
        await ValueChanged.InvokeAsync(Value);
    }

    private string CssClass => string.Join(" ", new[]
    {
        "input",
        Size != InputSize.Md ? $"input--{Size.ToString().ToLower()}" : null,
        IconLeft != null ? "input--has-icon-left" : null,
        Trailing != null ? "input--has-trailing" : null,
        Invalid ? "input--invalid" : null,
        Disabled ? "input--disabled" : null,
    }.Where(c => c != null));
}
```

For Checkbox and Switch (boolean value), use:
```csharp
[Parameter] public bool Value { get; set; }
[Parameter] public EventCallback<bool> ValueChanged { get; set; }
[Parameter] public Expression<Func<bool>>? ValueExpression { get; set; }
```

### Overlay Components (Dialog, Toast, Banner, Tooltip)

Implement without JS interop using C# state and CSS:

**Dialog** — use CSS show/hide driven by `IsOpen` bool. The parent controls open state:
```razor
@if (IsOpen)
{
    <div class="dialog__backdrop" @onclick="HandleClose"></div>
    <div class="dialog" role="dialog" aria-modal="true">
        <div class="dialog__panel">
            @ChildContent
        </div>
    </div>
}

@code {
    [Parameter] public bool IsOpen { get; set; }
    [Parameter] public EventCallback OnClose { get; set; }
    [Parameter] public RenderFragment? ChildContent { get; set; }

    private async Task HandleClose() => await OnClose.InvokeAsync();
}
```
```css
.dialog__backdrop { position: fixed; inset: 0; background: var(--surface-overlay); z-index: 50; }
.dialog { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 51; pointer-events: none; }
.dialog__panel { pointer-events: all; background: var(--surface-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); box-shadow: var(--shadow-xl); padding: var(--space-6); min-width: 360px; max-width: 560px; width: 100%; }
```

**Tooltip** — pure CSS `:hover`, no state needed:
```razor
<span class="tooltip">
    @Trigger
    <span class="tooltip__tip" role="tooltip">@Content</span>
</span>

@code {
    [Parameter] public RenderFragment? Trigger { get; set; }
    [Parameter] public RenderFragment? Content { get; set; }
}
```
```css
.tooltip { position: relative; display: inline-flex; }
.tooltip__tip { position: absolute; bottom: calc(100% + var(--space-1)); left: 50%; transform: translateX(-50%); background: var(--text-primary); color: var(--text-inverse); font-size: var(--text-xs); padding: var(--space-1) var(--space-2); border-radius: var(--radius-sm); white-space: nowrap; pointer-events: none; opacity: 0; transition: opacity var(--duration-instant) var(--ease-standard); }
.tooltip:hover .tooltip__tip { opacity: 1; }
```

**Toast** — parent page renders it conditionally in a fixed container:
```razor
@if (IsVisible)
{
    <div class="toast toast--@Tone.ToString().ToLower()" role="alert">
        @ChildContent
        <button class="toast__close" @onclick="() => IsVisibleChanged.InvokeAsync(false)">&#x2715;</button>
    </div>
}
```

**Banner** — inline alert, always visible, not dismissable by default:
```razor
<div class="banner banner--@Tone.ToString().ToLower()" role="alert">
    @ChildContent
</div>
```

### Navigation (Tabs, NavItem)

**Tabs** — C# active-tab state, no routing:
```razor
<div class="tabs" role="tablist">
    @foreach (var tab in Tabs)
    {
        <button class="@($"tabs__tab{(_activeId == tab.Id ? " tabs__tab--active" : "")}")"
                role="tab"
                aria-selected="@(_activeId == tab.Id)"
                @onclick="() => SetTab(tab.Id)">
            @tab.Label
        </button>
    }
</div>

@code {
    public record TabItem(string Id, string Label);

    [Parameter] public List<TabItem> Tabs { get; set; } = [];
    [Parameter] public string? ActiveId { get; set; }
    [Parameter] public EventCallback<string> ActiveIdChanged { get; set; }

    private string _activeId => ActiveId ?? Tabs.FirstOrDefault()?.Id ?? "";

    private async Task SetTab(string id) => await ActiveIdChanged.InvokeAsync(id);
}
```

**NavItem** — for sidebar nav, use `<NavLink>` from `Microsoft.AspNetCore.Components.Routing`:
```razor
<NavLink class="snav-item" href="@Href" Match="@Match">
    @if (Icon != null) { <span class="snav-item__icon">@Icon</span> }
    <span>@Label</span>
</NavLink>

@code {
    [Parameter] public string Href { get; set; } = "";
    [Parameter] public string? Label { get; set; }
    [Parameter] public RenderFragment? Icon { get; set; }
    [Parameter] public NavLinkMatch Match { get; set; } = NavLinkMatch.Prefix;
}
```
Active state from the NavLink `active` class:
```css
::deep .snav-item.active { background: var(--accent-subtle); color: var(--text-accent); border-left: 2px solid var(--accent); }
```
