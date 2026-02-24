# State Management

## Component State

### Private Fields
Simplest form — scoped to the component instance, lost on refresh/navigation/circuit loss.

```razor
@code {
    private int currentCount = 0;
    private void IncrementCount() => currentCount++;
}
```

### [Parameter] Properties
Receive values from parent components. Must be `public`. **Do not modify from within the component** — the parent owns the value.

```razor
@code {
    [Parameter]
    public string Title { get; set; } = "";

    [Parameter]
    public int Count { get; set; }
}
```

## StateHasChanged()

Notifies the renderer that state has changed and a rerender is needed.

### Called Automatically After:
- Event handlers (`@onclick`, `@onchange`, etc.)
- `EventCallback` delegates complete
- Lifecycle methods complete

### Must Call Manually When:
- Timer callbacks
- Background service notifications
- External event subscriptions

### Thread Safety — InvokeAsync

State changes from outside Blazor's synchronization context (timers, Task.Run, background services) must be wrapped:

```csharp
// WRONG — throws InvalidOperationException
timer.Elapsed += (s, e) => { data = Fetch(); StateHasChanged(); };

// CORRECT
timer.Elapsed += async (s, e) =>
{
    data = Fetch();
    await InvokeAsync(StateHasChanged);
};
```

## Cascading Values and Parameters

Ancestor provides data to all descendants without explicit parameter passing at each level.

### Provider
```razor
<CascadingValue Value="theme">
    @ChildContent
</CascadingValue>

@code {
    private ThemeInfo theme = new() { ButtonClass = "btn-success" };
}
```

### Consumer
```razor
@code {
    [CascadingParameter]
    private ThemeInfo? ThemeInfo { get; set; }
}
```

### Named (disambiguation when same type)
```razor
<CascadingValue Value="val1" Name="First">
    <CascadingValue Value="val2" Name="Second">
        @ChildContent
    </CascadingValue>
</CascadingValue>
```
```csharp
[CascadingParameter(Name = "First")] private MyType? First { get; set; }
[CascadingParameter(Name = "Second")] private MyType? Second { get; set; }
```

### Root-Level (works across render mode boundaries)
```csharp
// Program.cs — available to ALL components including interactive
builder.Services.AddCascadingValue(sp => new ThemeInfo { ButtonClass = "btn-primary" });
```

### Performance Rules
- `IsFixed="true"` prevents subscriptions — use when value never changes
- Any property change causes ALL subscribed components to rerender
- Create granular classes, cascade separately to limit rerender scope
- Avoid a single large global state class

### Render Mode Boundary Rule
Cascading parameters from `<CascadingValue>` components **do not cross** static SSR → interactive boundaries. Root-level cascading values (registered via `AddCascadingValue` in DI) DO work across boundaries.

## DI-Based State

### State Container Pattern
```csharp
public class StateContainer
{
    private string? savedString;

    public string Property
    {
        get => savedString ?? string.Empty;
        set { savedString = value; NotifyStateChanged(); }
    }

    public event Action? OnChange;
    private void NotifyStateChanged() => OnChange?.Invoke();
}
```

### Registration

| Hosting | Registration | Behavior |
|---|---|---|
| Blazor Server | `AddScoped` | One instance per circuit (per user) |
| Blazor WASM | `AddSingleton` | One instance per browser tab |

**CRITICAL**: Never use `AddSingleton` for user state on Blazor Server — it leaks between users.

### Consuming
```razor
@implements IDisposable
@inject StateContainer StateContainer

<p>@StateContainer.Property</p>

@code {
    protected override void OnInitialized()
        => StateContainer.OnChange += StateHasChanged;

    public void Dispose()
        => StateContainer.OnChange -= StateHasChanged; // Always unsubscribe
}
```

## PersistentComponentState

Solves the prerender double-initialization problem.

### .NET 10+ (`[PersistentState]` attribute)
```razor
@code {
    [PersistentState]
    public int? CurrentCount { get; set; }

    protected override void OnInitialized()
    {
        CurrentCount ??= Random.Shared.Next(100); // Only computed once
    }
}
```

Options:
- `AllowUpdates = true` — refresh during enhanced navigation
- `RestoreBehavior = RestoreBehavior.SkipInitialValue` — skip during prerendering
- `RestoreBehavior = RestoreBehavior.SkipLastSnapshot` — skip during reconnection

### Pre-.NET 10 (Manual)
```razor
@implements IDisposable
@inject PersistentComponentState ApplicationState

@code {
    private int currentCount;
    private PersistingComponentStateSubscription persistingSubscription;

    protected override void OnInitialized()
    {
        if (!ApplicationState.TryTakeFromJson<int>(nameof(currentCount), out var restored))
            currentCount = Random.Shared.Next(100);
        else
            currentCount = restored;

        persistingSubscription = ApplicationState.RegisterOnPersisting(() =>
        {
            ApplicationState.PersistAsJson(nameof(currentCount), currentCount);
            return Task.CompletedTask;
        });
    }

    void IDisposable.Dispose() => persistingSubscription.Dispose();
}
```

**Warning**: WASM persisted data is visible in browser source — don't persist secrets.

## Browser Storage

### ProtectedLocalStorage / ProtectedSessionStorage
Server-side Blazor only. Uses ASP.NET Core Data Protection to encrypt values.

| | localStorage | sessionStorage |
|---|---|---|
| Persists across restarts | Yes | No |
| Shared across tabs | Yes | No |
| Use case | Long-term preferences | Per-session data |

```razor
@using Microsoft.AspNetCore.Components.Server.ProtectedBrowserStorage
@inject ProtectedSessionStorage ProtectedSessionStore

@code {
    // MUST use OnAfterRenderAsync — not available during prerendering
    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            var result = await ProtectedSessionStore.GetAsync<int>("count");
            currentCount = result.Success ? result.Value : 0;
            StateHasChanged();
        }
    }

    private async Task Save()
    {
        await ProtectedSessionStore.SetAsync("count", currentCount);
    }
}
```

## URL/Query String State

Use for bookmarkable, shareable, refresh-surviving state.

### [SupplyParameterFromQuery]
```razor
@page "/search"

@code {
    [SupplyParameterFromQuery]
    private string? Filter { get; set; }

    [SupplyParameterFromQuery]
    private int? Page { get; set; }

    [SupplyParameterFromQuery(Name = "q")]
    private string? SearchQuery { get; set; }
}
```

URL: `/search?filter=active&page=3&q=hello`

### NavigationManager
```csharp
@inject NavigationManager Navigation

// Navigate
Navigation.NavigateTo($"/search?page={page}");

// Replace history entry
Navigation.NavigateTo($"/search?page={page}", replace: true);

// Build URL with query parameter
var uri = Navigation.GetUriWithQueryParameter("page", 3);

// Remove parameter
var uri = Navigation.GetUriWithQueryParameter("filter", (string?)null);
```

## Component Communication

| Direction | Mechanism |
|---|---|
| Parent → Child | `[Parameter]` |
| Child → Parent | `EventCallback<T>` |
| Parent → All Descendants | `CascadingValue` / `[CascadingParameter]` |
| Sibling ↔ Sibling | Lift state to parent, or shared DI service |
| Any ↔ Any (app-wide) | Scoped DI service with `OnChange` event |

### EventCallback (Child → Parent)

Automatically calls `StateHasChanged` on the parent. Supports async. Null-safe to invoke.

```razor
<!-- Child -->
<button @onclick="() => OnSaved.InvokeAsync(item)">Save</button>

@code {
    [Parameter] public EventCallback<Item> OnSaved { get; set; }
}
```

```razor
<!-- Parent -->
<ChildComponent OnSaved="HandleSaved" />

@code {
    private void HandleSaved(Item item) { /* ... */ }
}
```

### EventCallback vs Action

| | EventCallback | Action/Func |
|---|---|---|
| Auto StateHasChanged on parent | Yes | No |
| Async support | Yes | Requires Func<Task> |
| Null-safe invoke | Yes | No |
| **Use?** | **Always prefer** | Avoid for component events |

## Choosing the Right Approach

| Scenario | Approach |
|---|---|
| Local component data | Private fields |
| Parent → child data | `[Parameter]` |
| Child notifies parent | `EventCallback<T>` |
| Sibling communication | Lift state to parent or shared DI service |
| Data for all descendants | `CascadingValue` / `[CascadingParameter]` |
| App-wide settings | Root-level `AddCascadingValue` |
| User state per circuit | `AddScoped` DI service |
| Survive prerender → interactive | `[PersistentState]` |
| Survive page refresh | URL route/query parameters |
| Long-term browser persistence | `ProtectedLocalStorage` |
| Per-session browser persistence | `ProtectedSessionStorage` |

## Common Pitfalls

1. **State loss during prerender** — Use `[PersistentState]` or `PersistentComponentState`
2. **Browser storage during prerender** — Only in `OnAfterRenderAsync`, never `OnInitialized`
3. **Cascading values across render modes** — Use `AddCascadingValue` in DI, not `<CascadingValue>`
4. **Singleton on Server** — Leaks state between users; use `AddScoped`
5. **Missing IDisposable** — Always unsubscribe from `OnChange` events
6. **StateHasChanged from non-Blazor thread** — Wrap in `InvokeAsync`
7. **Async init without loading indicator** — Track `isLoading` explicitly
