# Page Adaptation

After components are implemented, the skill can either adapt existing pages or create a new showcase page. The user chooses which mode at the start.

---

## Mode A: Adapt Existing Pages

Read each target page and identify HTML patterns that should be replaced with the new components.

### What to look for

| Raw HTML pattern | Replace with |
|---|---|
| `<button class="btn ...">` | `<Button Variant="...">` |
| `<span class="badge ...">` | `<Badge Tone="...">` |
| `<div class="card ...">` | `<Card>` |
| `<input class="..." type="text">` | `<Input @bind-Value="...">` |
| `<label>...<input>...</label>` | `<Field Label="..."><Input .../></Field>` |
| `<select ...>` | `<Select @bind-Value="...">` |
| Hand-rolled dialog markup | `<Dialog IsOpen="..." OnClose="...">` |

### Process for each page

1. Read the `.razor` file
2. Identify which components apply (match HTML patterns to the component list from the manifest)
3. Replace the raw HTML with component calls — preserving all logic and bound values
4. Remove the now-redundant inline CSS classes that the component handles
5. Keep any page-specific layout/structural CSS that isn't covered by components
6. Verify the page still compiles (`dotnet build`)

### What NOT to change

- Page routing (`@page "..."`)
- `@code {}` logic — only the markup changes
- Layout structure (`<div class="grid">`, flex containers, page sections)
- Any HTML that doesn't map to an available component

---

## Mode B: Create a Showcase Page

Build a new `.razor` page that demonstrates every component from the manifest across all variants, sizes, and states. Useful as a living style guide and visual regression reference.

### File location
Place it where other pages live (e.g., `Pages/Components.razor` or `Components/Showcase.razor`). Use `@page "/components"` (or `/showcase`).

### Page structure

```razor
@page "/components"

<PageTitle>Component Showcase</PageTitle>

<div class="showcase">
    <header class="showcase__header">
        <h1>Design System Components</h1>
        <p>All components, variants, and states.</p>
    </header>

    <!-- One <section> per component -->
</div>
```

### Section template (repeat for each component)

```razor
<section class="showcase__section">
    <h2 class="showcase__section-title">{ComponentName}</h2>

    <div class="showcase__row">
        <p class="showcase__label">Variants</p>
        <div class="showcase__group">
            <!-- one instance per variant -->
        </div>
    </div>

    <div class="showcase__row">
        <p class="showcase__label">Sizes</p>
        <div class="showcase__group">
            <!-- one instance per size (if applicable) -->
        </div>
    </div>

    <div class="showcase__row">
        <p class="showcase__label">States</p>
        <div class="showcase__group">
            <!-- disabled, invalid, loading, etc. -->
        </div>
    </div>
</section>
```

### Minimal co-located CSS

```css
.showcase { display: flex; flex-direction: column; gap: var(--space-12); padding: var(--space-8) 0; }
.showcase__header { padding-bottom: var(--space-6); border-bottom: 1px solid var(--border-subtle); }
.showcase__header h1 { font-size: var(--text-3xl); font-weight: var(--weight-bold); color: var(--text-primary); margin: 0 0 var(--space-2); }
.showcase__header p { color: var(--text-secondary); margin: 0; }
.showcase__section { display: flex; flex-direction: column; gap: var(--space-4); }
.showcase__section-title { font-size: var(--text-lg); font-weight: var(--weight-semibold); color: var(--text-primary); margin: 0; padding-bottom: var(--space-3); border-bottom: 1px solid var(--border-subtle); }
.showcase__row { display: flex; flex-direction: column; gap: var(--space-2); }
.showcase__label { font-size: var(--text-xs); font-weight: var(--weight-semibold); color: var(--text-tertiary); text-transform: uppercase; letter-spacing: var(--tracking-wider); margin: 0; }
.showcase__group { display: flex; align-items: center; flex-wrap: wrap; gap: var(--space-3); }
```

### Interactive state in `@code {}`

Add only what's needed to demo interactive components:

```csharp
@code {
    // form controls
    private string _textValue = "";
    private bool _checked;
    private bool _toggled;
    private string _selected = "";

    // overlays
    private bool _dialogOpen;

    // navigation
    private string _activeTab = "";
}
```

### Component-specific notes for the showcase

**Form controls** — wrap in a `Field` component (if one exists) and use a live bound value:
```razor
<Field Label="Email" For="email-field">
    <Input Id="email-field" @bind-Value="_textValue" Placeholder="you@example.com" />
</Field>
<Field Label="Invalid example" Error="This field is required">
    <Input Invalid Placeholder="error state" />
</Field>
```

**Dialog** — add a trigger button:
```razor
<Button @onclick="() => _dialogOpen = true">Open dialog</Button>
<Dialog IsOpen="_dialogOpen" OnClose="() => _dialogOpen = false">
    <p>Dialog content here.</p>
    <Button @onclick="() => _dialogOpen = false">Close</Button>
</Dialog>
```

**Tabs** — pass a static list:
```razor
<Tabs Tabs="@_tabs" @bind-ActiveId="_activeTab" />
@code {
    private List<Tabs.TabItem> _tabs =
    [
        new("overview", "Overview"),
        new("details", "Details"),
        new("history", "History"),
    ];
}
```

---

## Mode C: Skip Pages

If the user only wants the design system and components wired up (no page changes), skip this phase entirely and go straight to verification.
