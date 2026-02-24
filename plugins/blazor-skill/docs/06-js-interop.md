# JavaScript Interop

## Core API: IJSRuntime

Inject `IJSRuntime` to call JavaScript from .NET.

```razor
@inject IJSRuntime JS
```

### Calling JS Functions

```csharp
// No return value
await JS.InvokeVoidAsync("functionName", arg1, arg2);

// With return value (TValue must be JSON-serializable)
string result = await JS.InvokeAsync<string>("functionName", arg1);
```

- Parameters are passed as `object[]`, must be JSON-serializable
- `InvokeAsync` automatically unwraps JS `Promise` objects
- Optional `CancellationToken` and `TimeSpan` timeout parameters supported

## Module Isolation (IJSObjectReference)

Prefer ES module imports over polluting `window`. Import returns `IJSObjectReference`.

```csharp
private IJSObjectReference? module;

protected override async Task OnAfterRenderAsync(bool firstRender)
{
    if (firstRender)
    {
        module = await JS.InvokeAsync<IJSObjectReference>(
            "import", "./scripts.js");
    }
}

private async Task DoSomething()
{
    if (module is not null)
        await module.InvokeVoidAsync("myExportedFunction");
}
```

```javascript
// wwwroot/scripts.js
export function myExportedFunction() {
    // ...
}
```

## Collocated JS Files (.razor.js)

Place a `.razor.js` file next to the `.razor` component. Blazor serves it automatically.

```
Components/Pages/
    MyComponent.razor
    MyComponent.razor.js    <-- collocated
```

```csharp
// Load path is relative to wwwroot
module = await JS.InvokeAsync<IJSObjectReference>(
    "import", "./Components/Pages/MyComponent.razor.js");
```

For Razor Class Libraries:
```csharp
module = await JS.InvokeAsync<IJSObjectReference>(
    "import", "./_content/MyLibrary/scripts.js");
```

## ElementReference

Use `@ref` to capture a DOM element reference, then pass it to JS.

```razor
<input @ref="inputElement" />

@code {
    private ElementReference inputElement;

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
            await JS.InvokeVoidAsync("focusElement", inputElement);
    }
}
```

```javascript
export function focusElement(element) {
    element.focus();
}
```

**WARNING**: Never mutate DOM elements that Blazor manages (elements with Blazor-rendered children). Only use `ElementReference` for empty containers or to trigger events.

## Calling .NET from JavaScript

### Static Methods

```csharp
[JSInvokable]
public static Task<int[]> ReturnArrayAsync()
    => Task.FromResult(new int[] { 1, 2, 3 });
```

```javascript
const data = await DotNet.invokeMethodAsync('MyAssemblyName', 'ReturnArrayAsync');
```

### Instance Methods (DotNetObjectReference)

```razor
@implements IDisposable

@code {
    private DotNetObjectReference<MyComponent>? objRef;

    protected override void OnInitialized()
        => objRef = DotNetObjectReference.Create(this);

    private async Task PassToJs()
        => await JS.InvokeVoidAsync("registerHandler", objRef);

    [JSInvokable]
    public string GetMessage() => $"Hello from .NET!";

    public void Dispose() => objRef?.Dispose();
}
```

```javascript
window.registerHandler = (dotNetHelper) => {
    // Call instance method
    const msg = await dotNetHelper.invokeMethodAsync('GetMessage');
};
```

When a `[JSInvokable]` method updates component state, call `StateHasChanged()`:

```csharp
[JSInvokable]
public void OnWindowResize(int width, int height)
{
    windowWidth = width;
    StateHasChanged();
}
```

## Lifecycle Timing

JS interop is **only available after the component renders**. The DOM does not exist during `OnInitialized`.

| Lifecycle Method | JS Interop Available? |
|---|---|
| `OnInitialized` | NO |
| `OnParametersSet` | NO |
| `OnAfterRender(firstRender: true)` | YES |
| `OnAfterRender(firstRender: false)` | YES |

During prerendering (server-side), there is no browser connection at all. Always guard with `firstRender`.

## Render Mode Differences

### Interactive Server (SignalR)
- All calls are async over WebSocket
- Circuit disconnection throws `JSDisconnectedException`
- Browser APIs requiring user gesture context (e.g., Fullscreen) cannot be called through interop; use native `onclick` attribute instead

### Interactive WebAssembly
- Synchronous calls available via `IJSInProcessRuntime`:
```csharp
var jsInProcess = (IJSInProcessRuntime)JS;
var value = jsInProcess.Invoke<string>("myFunction");
```
- `[JSImport]`/`[JSExport]` API available (WASM only)

## Error Handling

```csharp
try
{
    await JS.InvokeVoidAsync("myFunction");
}
catch (JSDisconnectedException)
{
    // SignalR circuit disconnected - safe to ignore during cleanup
}
catch (JSException ex)
{
    // JavaScript threw an error
}
catch (TaskCanceledException)
{
    // Call timed out or was cancelled
}
```

## Disposal (Critical)

Always implement `IAsyncDisposable` for components holding JS references.

```csharp
@implements IAsyncDisposable

@code {
    private IJSObjectReference? module;
    private DotNetObjectReference<MyComponent>? dotNetRef;

    async ValueTask IAsyncDisposable.DisposeAsync()
    {
        if (module is not null)
        {
            try { await module.DisposeAsync(); }
            catch (JSDisconnectedException) { }
        }
        dotNetRef?.Dispose();
    }
}
```

**Memory leak sources:**
- Undisposed `IJSObjectReference` - JS module stays in memory
- Undisposed `DotNetObjectReference` - .NET object can't be GC'd
- JS event listeners not removed on dispose

## Common Patterns

### localStorage
```javascript
export function getItem(key) { return localStorage.getItem(key); }
export function setItem(key, value) { localStorage.setItem(key, value); }
export function removeItem(key) { localStorage.removeItem(key); }
```

### Clipboard
```javascript
export async function copyToClipboard(text) {
    await navigator.clipboard.writeText(text);
}
```

### Scroll
```javascript
export function scrollIntoView(element) {
    element.scrollIntoView({ behavior: 'smooth' });
}
export function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
```

### Window Events with .NET Callback
```javascript
export function addResizeHandler(dotNetHelper) {
    window.addEventListener('resize', () => {
        dotNetHelper.invokeMethodAsync('OnWindowResize',
            window.innerWidth, window.innerHeight);
    });
}
```

## Quick Reference

| Task | Code |
|---|---|
| Call JS, no return | `await JS.InvokeVoidAsync("func", args)` |
| Call JS, with return | `await JS.InvokeAsync<T>("func", args)` |
| Import JS module | `await JS.InvokeAsync<IJSObjectReference>("import", "./file.js")` |
| Reference DOM element | `@ref="myRef"` + `ElementReference myRef` |
| .NET callable from JS | `[JSInvokable]` on public method |
| Pass instance to JS | `DotNetObjectReference.Create(this)` |
| Static .NET from JS | `DotNet.invokeMethodAsync('Assembly', 'Method')` |
| Instance .NET from JS | `dotNetHelper.invokeMethodAsync('Method')` |
| Sync interop (WASM) | Cast to `IJSInProcessRuntime` |
| Collocated JS | `ComponentName.razor.js` next to `ComponentName.razor` |
