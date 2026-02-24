# Render Modes

## The Four Render Modes

### Static SSR (Default)
No `@rendermode` directive = static HTML. No SignalR circuit, no WASM runtime.

- Event handlers (`@onclick`, `@oninput`, etc.) are **completely inert** — the HTML ships as-is
- `OnAfterRender` never fires
- **Use for**: SEO content, read-only pages, Identity/auth pages that depend on HTTP cookies

```razor
@page "/about"
@* No @rendermode = Static SSR *@
@* This button does NOTHING when clicked: *@
<button @onclick="DoWork">Click</button>
```

### Interactive Server (SignalR)
Component runs on the server. DOM events travel over a persistent SignalR WebSocket connection. Server processes events, re-renders, sends DOM diffs back.

```razor
@page "/dashboard"
@rendermode InteractiveServer
```

**Circuit lifecycle**: Created when first Interactive Server component renders. Closed when none remain. On connection drop, Blazor retries with backoff. When timeout expires, circuit and all server-side state are lost.

**Program.cs**:
```csharp
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();
```

### Interactive WebAssembly (Client-Side)
.NET runtime (WASM) and app bundle downloaded to browser, cached after first visit. Runs entirely client-side — no server connection during interaction.

```razor
@page "/counter"
@rendermode InteractiveWebAssembly
```

**Requirements**: Component must live in the `.Client` project.

### Interactive Auto
Hybrid: first visit uses Server (immediate interactivity), WASM downloads silently in background. Subsequent visits use WASM from cache. **No mid-session handoff** — switch happens between sessions.

```csharp
// Program.cs — requires both
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents()
    .AddInteractiveWebAssemblyComponents();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode()
    .AddInteractiveWebAssemblyRenderMode();
```

**Requirements**: Component must live in the `.Client` project.

## Setting Render Modes

### Per-Component Definition (inside .razor file)
```razor
@rendermode InteractiveServer
```

### Per-Component Instance (from parent markup)
```razor
<MyWidget @rendermode="InteractiveServer" />
```

### Entire App (App.razor)
```razor
<HeadOutlet @rendermode="InteractiveServer" />
<Routes @rendermode="InteractiveServer" />
```
Note: The `App` component itself cannot be made interactive.

### Without Prerendering
```razor
@rendermode @(new InteractiveServerRenderMode(prerender: false))
@rendermode @(new InteractiveWebAssemblyRenderMode(prerender: false))
@rendermode @(new InteractiveAutoRenderMode(prerender: false))
```

### Custom Shorthand (in _Imports.razor)
```csharp
public static IComponentRenderMode InteractiveServerNoPrerender { get; } =
    new InteractiveServerRenderMode(prerender: false);
```

The shorthand names (`InteractiveServer`, etc.) work because templates add this to `_Imports.razor`:
```razor
@using static Microsoft.AspNetCore.Components.Web.RenderMode
```

## Render Mode Propagation Rules

- Render modes flow **downward** — children inherit from parents
- You **cannot** mix interactive render modes in a parent/child relationship (Server parent cannot host WASM child)
- **Sibling** components can use different render modes
- `RenderFragment` / `ChildContent` cannot cross render mode boundaries (not JSON-serializable)

### ⚠️ The `<Routes>` Propagation Trap

**`@rendermode` on a page is silently ignored if `<Routes>` in `App.razor` has no render mode.** This is the most common interactivity bug:

```razor
@* Page says interactive, but it's NOT — Routes is static *@
@page "/dashboard"
@rendermode InteractiveServer   @* ← This does NOTHING *@
<button @onclick="DoWork">Click</button>  @* Inert! *@
```

The fix: either set the render mode on `<Routes>` in `App.razor` (makes the whole app interactive), or use per-component instance render modes from an already-interactive parent.

**When building any page with event handlers, always verify `App.razor` first:**
```razor
<!-- App.razor — Routes MUST have a render mode for per-page interactivity to work -->
<Routes @rendermode="InteractiveServer" />
```

Per-page `@rendermode` directives only work when the page is rendered within an interactive routing context. If `<Routes>` is static, the router renders all pages as static SSR regardless of their declared render mode.

## Detecting Render Mode at Runtime

```razor
@* Check if currently interactive (not prerendering) *@
@if (RendererInfo.IsInteractive) { <button @onclick="Save">Save</button> }

@* Check which runtime *@
@if (RendererInfo.Name == "Server")      { /* Interactive Server */ }
@if (RendererInfo.Name == "WebAssembly") { /* Interactive WASM */ }
@if (RendererInfo.Name == "Static")      { /* Static SSR */ }

@* Check assigned render mode type *@
@if (AssignedRenderMode is null)                            { /* Static SSR */ }
@if (AssignedRenderMode is InteractiveServerRenderMode)     { /* Server */ }
@if (AssignedRenderMode is InteractiveWebAssemblyRenderMode){ /* WASM */ }
@if (AssignedRenderMode is InteractiveAutoRenderMode)       { /* Auto */ }
```

## Prerendering

All interactive components prerender by default. The component renders statically on the server first (fast HTML), then the interactive runtime boots and re-renders.

### The Double-Render Problem
`OnInitialized(Async)` runs **twice**: once during static prerender, once when interactivity establishes.

**Consequences:**
- HTTP requests fire twice
- Side effects (database writes, emails) occur twice
- UI may flicker as prerendered content is replaced

**Solution**: `PersistentComponentState` (see State Management doc).

### Key Facts
- `OnAfterRender` does NOT fire during prerendering — only after interactive boot
- Internal navigation (after app is interactive) does NOT prerender
- `HttpContext` is only available during prerendering, NOT in interactive mode

### Disabling Prerendering
```razor
<MyComp @rendermode="new InteractiveServerRenderMode(prerender: false)" />
```

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Event handlers do nothing | No `@rendermode` (static SSR) | Add `@rendermode InteractiveServer` (or WASM/Auto) |
| `@rendermode` on page but events still inert | `<Routes>` in `App.razor` has no render mode — page directive is silently ignored | Add `@rendermode="InteractiveServer"` to `<Routes>` in `App.razor` |
| Service injection error during prerender | Client-only service (e.g., `IWebAssemblyHostEnvironment`) not available on server | Disable prerendering, make injection optional, or register server-side fallback |
| "Cannot create component... render mode not supported" | WASM child inside Server parent | Restructure as siblings, not parent/child |
| Component not in WASM bundle | WebAssembly component in server project | Move to `.Client` project |
| `ChildContent` error crossing render boundaries | `RenderFragment` not serializable | Wrap interactive component in parameter-free wrapper |
