# Event Handling and Performance

## Event Handling

### Basic Syntax
```razor
<button @onclick="HandleClick">Click</button>
<input @oninput="HandleInput" />
<input @onchange="HandleChange" />
<form @onsubmit="HandleSubmit">

@code {
    private void HandleClick(MouseEventArgs e) { }
    private void HandleInput(ChangeEventArgs e) { var val = e.Value; }
    private void HandleChange(ChangeEventArgs e) { }
    private async Task HandleSubmit() { }
}
```

### Lambda Expressions
```razor
<button @onclick="() => message = "Clicked!"">Click</button>
<button @onclick="() => Delete(item.Id)">Delete</button>
<button @onclick="async () => await SaveAsync()">Save</button>
```

**Performance note**: Lambdas create a new delegate per render. For hot paths (items in large lists), prefer a method with parameter.

### preventDefault and stopPropagation
```razor
<a href="/about" @onclick="HandleClick" @onclick:preventDefault>
    Handled in C#, browser won't navigate
</a>

<div @onclick="OuterClick">
    <button @onclick="InnerClick" @onclick:stopPropagation>
        Won't bubble to parent
    </button>
</div>
```

### Event Args Types

| Event | Args Type |
|---|---|
| `@onclick` | `MouseEventArgs` |
| `@onchange`, `@oninput` | `ChangeEventArgs` |
| `@onkeydown`, `@onkeyup` | `KeyboardEventArgs` |
| `@onfocus`, `@onblur` | `FocusEventArgs` |
| `@ondragstart`, `@ondrop` | `DragEventArgs` |
| `@onsubmit` | `EventArgs` |

## Debouncing Input

### Timer Pattern
```razor
<input @oninput="HandleSearchInput" placeholder="Search..." />

@code {
    private Timer? debounceTimer;
    private string searchTerm = "";

    private void HandleSearchInput(ChangeEventArgs e)
    {
        debounceTimer?.Dispose();
        debounceTimer = new Timer(async _ =>
        {
            searchTerm = e.Value?.ToString() ?? "";
            await InvokeAsync(async () =>
            {
                await PerformSearch(searchTerm);
                StateHasChanged();
            });
        }, null, 300, Timeout.Infinite);
    }
}
```

### CancellationToken Pattern (Cancel In-Flight Requests)
```razor
@code {
    private CancellationTokenSource? cts;

    private async Task HandleSearchInput(ChangeEventArgs e)
    {
        cts?.Cancel();
        cts = new CancellationTokenSource();
        var token = cts.Token;

        await Task.Delay(300, token); // Debounce

        if (!token.IsCancellationRequested)
        {
            results = await SearchService.SearchAsync(e.Value?.ToString(), token);
        }
    }
}
```

## Performance Optimization

### ShouldRender
Override to prevent unnecessary rerenders. Not called on first render.

```csharp
protected override bool ShouldRender() => shouldRender;
```

### @key for Lists
Stabilizes component instances. Use entity IDs, not loop indices.

```razor
@foreach (var item in items)
{
    <ItemRow @key="item.Id" Item="item" />
}
```

### Virtualize for Large Lists
Only renders visible items. See Components doc.

### Avoid Excessive Lambda Allocations
```razor
@* In a large list — avoid creating N lambdas per render *@
@foreach (var item in items)
{
    @* Better: use a method that takes the item *@
    <button @onclick="() => Delete(item)">Delete</button>
}
```

### StateHasChanged Coalescing
Multiple `StateHasChanged` calls in the same synchronous block coalesce to one render. Safe to call multiple times.

### Component Granularity
- Split large components so rerenders are scoped to the changed area
- A parent rerender causes all children to re-evaluate (though `ShouldRender` can block)
- Avoid one massive page component — extract sections that update independently

## Common UX Patterns

### Modal Dialog
```razor
@* Modal.razor *@
@if (IsVisible)
{
    <div class="modal-backdrop" @onclick="Close"></div>
    <div class="modal">
        <div class="modal-header">
            <h5>@Title</h5>
            <button @onclick="Close">&times;</button>
        </div>
        <div class="modal-body">@ChildContent</div>
        <div class="modal-footer">@Footer</div>
    </div>
}

@code {
    [Parameter] public bool IsVisible { get; set; }
    [Parameter] public string Title { get; set; } = "";
    [Parameter] public RenderFragment? ChildContent { get; set; }
    [Parameter] public RenderFragment? Footer { get; set; }
    [Parameter] public EventCallback OnClose { get; set; }

    private async Task Close() => await OnClose.InvokeAsync();
}
```

### Toast Notification Service
```csharp
public class ToastService
{
    public event Action<string, string>? OnShow; // message, type

    public void ShowSuccess(string message) => OnShow?.Invoke(message, "success");
    public void ShowError(string message) => OnShow?.Invoke(message, "danger");
}
```

```csharp
builder.Services.AddScoped<ToastService>();
```

### Confirmation Dialog (Awaitable)
```csharp
public class ConfirmService
{
    private TaskCompletionSource<bool>? tcs;

    public event Action<string>? OnShow;

    public Task<bool> ConfirmAsync(string message)
    {
        tcs = new TaskCompletionSource<bool>();
        OnShow?.Invoke(message);
        return tcs.Task;
    }

    public void Respond(bool confirmed) => tcs?.SetResult(confirmed);
}
```

```csharp
// Usage
if (await ConfirmService.ConfirmAsync("Delete this item?"))
{
    await DeleteItem();
}
```

### File Upload
```razor
<InputFile OnChange="HandleFile" accept=".pdf,.jpg" multiple />

@code {
    private async Task HandleFile(InputFileChangeEventArgs e)
    {
        foreach (var file in e.GetMultipleFiles(maxAllowedFiles: 10))
        {
            // file.Name, file.Size, file.ContentType
            using var stream = file.OpenReadStream(maxAllowedSize: 10 * 1024 * 1024);
            // Process stream...
        }
    }

    // Browser-side image resize (WASM)
    private async Task HandleImage(InputFileChangeEventArgs e)
    {
        var imageFile = e.File;
        var resized = await imageFile.RequestImageFileAsync("image/jpeg", 300, 300);
        using var stream = resized.OpenReadStream();
        // Upload resized image...
    }
}
```

### Data Table Pattern (Sort/Filter/Page)
```razor
@code {
    private IEnumerable<Item> items = [];
    private string sortColumn = "Name";
    private bool sortAscending = true;
    private string filter = "";
    private int currentPage = 1;
    private int pageSize = 10;

    private IEnumerable<Item> FilteredItems => items
        .Where(i => string.IsNullOrEmpty(filter)
            || i.Name.Contains(filter, StringComparison.OrdinalIgnoreCase))
        .OrderBy(sortColumn, sortAscending)
        .Skip((currentPage - 1) * pageSize)
        .Take(pageSize);

    private void Sort(string column)
    {
        if (sortColumn == column)
            sortAscending = !sortAscending;
        else
        {
            sortColumn = column;
            sortAscending = true;
        }
    }
}
```

### Drag and Drop
```razor
<div class="drop-zone"
     @ondragover:preventDefault
     @ondrop="() => HandleDrop(targetIndex)">

    @foreach (var item in items)
    {
        <div draggable="true"
             @ondragstart="() => draggedItem = item"
             class="@(draggedItem == item ? "dragging" : "")">
            @item.Name
        </div>
    }
</div>
```
