# Component Lifecycle

## Lifecycle Event Order

### First Render
1. Component instance created, property injection performed
2. `SetParametersAsync` — receives incoming parameters
3. `OnInitialized` / `OnInitializedAsync` — first render only
4. `OnParametersSet` / `OnParametersSetAsync`
5. Render
6. `OnAfterRender(firstRender: true)` / `OnAfterRenderAsync(firstRender: true)` — interactive only, NOT during prerendering/static SSR

### Subsequent Rerenders (parent rerenders, StateHasChanged, event handlers)
1. `SetParametersAsync`
2. `OnParametersSet` / `OnParametersSetAsync`
3. `ShouldRender` check (if false, skip render)
4. Render
5. `OnAfterRender(firstRender: false)` / `OnAfterRenderAsync(firstRender: false)`

For each pair, the synchronous version always runs before the async version.

## SetParametersAsync

Called every time parameters are set or changed. Receives a `ParameterView` with all `[Parameter]` and `[CascadingParameter]` values.

```csharp
public override async Task SetParametersAsync(ParameterView parameters)
{
    if (parameters.TryGetValue<string>(nameof(Param), out var value))
    {
        // React to specific parameter before base processes them
    }

    await base.SetParametersAsync(parameters); // ALWAYS call base
}
```

**Rule**: Almost always call `await base.SetParametersAsync(parameters)`. Skipping it breaks the entire lifecycle chain.

## OnInitialized / OnInitializedAsync

Runs **once only** after the first `SetParametersAsync`. Use for one-time initialization.

```csharp
protected override void OnInitialized()
{
    message = "Initialized";
}

protected override async Task OnInitializedAsync()
{
    data = await MyService.GetDataAsync();
}
```

**With prerendering**: Runs **twice** — once during static prerender on server, once when interactive runtime starts. Use `[PersistentState]` (.NET 10+) or `PersistentComponentState` to prevent double work.

**Null-guard pattern for async data**:
```razor
@if (movies == null)
{
    <p><em>Loading...</em></p>
}
else
{
    @foreach (var m in movies) { <p>@m.Title</p> }
}

@code {
    private Movie[]? movies;

    protected override async Task OnInitializedAsync()
    {
        movies = await MovieService.GetMoviesAsync();
    }
}
```

### Preventing Double Execution (.NET 10+)

```razor
@attribute [StreamRendering]

@code {
    [PersistentState]
    public string? Data { get; set; }

    protected override async Task OnInitializedAsync()
    {
        Data ??= await LoadDataAsync(); // Only runs once during prerender
    }
}
```

### Pre-.NET 9 Approach

```razor
@implements IDisposable
@inject PersistentComponentState ApplicationState

@code {
    private string? data;
    private PersistingComponentStateSubscription persistingSubscription;

    protected override async Task OnInitializedAsync()
    {
        if (!ApplicationState.TryTakeFromJson<string>(nameof(data), out var restored))
        {
            data = await LoadDataAsync();
        }
        else
        {
            data = restored!;
        }
        persistingSubscription = ApplicationState.RegisterOnPersisting(PersistData);
    }

    private Task PersistData()
    {
        ApplicationState.PersistAsJson(nameof(data), data);
        return Task.CompletedTask;
    }

    void IDisposable.Dispose() => persistingSubscription.Dispose();
}
```

## OnParametersSet / OnParametersSetAsync

Called after `OnInitialized` on first render, and after `SetParametersAsync` on every subsequent rerender where the parent supplies parameters.

**Caveat**: Called even when parameter values haven't actually changed (for complex-type parameters). Implement your own change detection if needed.

```csharp
private int _previousId;

protected override async Task OnParametersSetAsync()
{
    if (Id != _previousId)
    {
        _previousId = Id;
        data = await DataService.LoadAsync(Id);
    }
}
```

## OnAfterRender / OnAfterRenderAsync

Called after the component has rendered interactively and the browser DOM is updated.

**Critical restrictions**:
- NOT called during prerendering or static SSR
- `OnAfterRenderAsync` does NOT schedule a further render cycle after its Task completes (intentional — prevents infinite loops)

**Use for**: JS interop, focus management, third-party JS library init.

```csharp
protected override async Task OnAfterRenderAsync(bool firstRender)
{
    if (firstRender)
    {
        // DOM exists, element references valid, JS interop safe
        module = await JS.InvokeAsync<IJSObjectReference>("import", "./scripts.js");
        await JS.InvokeVoidAsync("focusElement", inputRef);
        StateHasChanged(); // Safe here if guarded to prevent infinite loop
    }
}
```

## ShouldRender

Suppress unnecessary rerenders. Returns `true` by default. **Not called on first render**.

```csharp
private bool shouldRender = true;

protected override bool ShouldRender() => shouldRender;

private async Task ProcessBatch()
{
    shouldRender = false;
    foreach (var item in items)
        await ProcessItemAsync(item);
    shouldRender = true;
    StateHasChanged();
}
```

## Dispose / DisposeAsync

Called when the component is removed from the render tree. Implement `IDisposable` or `IAsyncDisposable`.

```razor
@implements IDisposable

@code {
    private CancellationTokenSource cts = new();

    public void Dispose()
    {
        if (!cts.IsCancellationRequested)
            cts.Cancel();
        cts?.Dispose();
    }
}
```

```razor
@implements IAsyncDisposable

@code {
    private IJSObjectReference? jsModule;

    public async ValueTask DisposeAsync()
    {
        if (jsModule is not null)
            await jsModule.DisposeAsync();
    }
}
```

**Always dispose**: Event subscriptions, timers, CancellationTokenSources, JS object references, DotNetObjectReferences.

## Lifecycle with Prerendering Summary

| Event | During Prerender? | During Interactive? |
|---|---|---|
| `SetParametersAsync` | YES | YES |
| `OnInitialized(Async)` | YES | YES (again!) |
| `OnParametersSet(Async)` | YES | YES |
| `OnAfterRender(Async)` | NO | YES |
| `Dispose` | YES (prerender instance) | YES (interactive instance) |

## Key Gotchas

1. `OnInitializedAsync` runs twice with prerendering — use `[PersistentState]` or `IMemoryCache`
2. `OnAfterRender` is the only safe place for JS interop
3. Always `await base.SetParametersAsync(parameters)` unless you know exactly what you're doing
4. `OnParametersSet` fires even when nothing changed (complex-type parameters)
5. Always implement `IDisposable`/`IAsyncDisposable` and unsubscribe from events
6. `OnAfterRenderAsync` does NOT auto-rerender after completion — by design
7. `ShouldRender` is not called on first render
