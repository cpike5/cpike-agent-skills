# Components

## Component Structure

### Single-File Pattern
```razor
@page "/counter"

<h1>Counter</h1>
<p>Current count: @currentCount</p>
<button @onclick="IncrementCount">Click me</button>

@code {
    private int currentCount = 0;
    private void IncrementCount() => currentCount++;
}
```

### Code-Behind Pattern (.razor.cs)
Split markup and logic into two files that compile to the same partial class.

```razor
@* Counter.razor *@
@page "/counter"
<p>@currentCount</p>
<button @onclick="IncrementCount">Click me</button>
```

```csharp
// Counter.razor.cs
namespace MyApp.Components.Pages;

public partial class Counter
{
    private int currentCount = 0;
    private void IncrementCount() => currentCount++;
}
```

The `partial` keyword is essential.

### Naming
- File names: PascalCase (`ProductDetail.razor`)
- URLs: kebab-case (`/product-detail`)

## Parameters

### [Parameter]
```csharp
[Parameter]
public string Title { get; set; } = "Default";

[Parameter]
public int? Count { get; set; }
```

Parent sets them as attributes: `<MyCard Title="Hello" Count="42" />`

### [EditorRequired]
```csharp
[Parameter, EditorRequired]
public string Title { get; set; } = "";
```

**Do NOT use** C# `required` modifier or `init` accessor on parameters — they're set via reflection and will fail.

### Best Practices
- Use auto-properties — no custom get/set logic
- React to changes in `OnParametersSet(Async)`, not in the setter

## RenderFragment (Child Content)

### ChildContent Convention
```razor
@* Card.razor *@
<div class="card">
    <div class="card-body">@ChildContent</div>
</div>

@code {
    [Parameter]
    public RenderFragment? ChildContent { get; set; }
}
```

Usage: `<Card>Hello world</Card>`

### Multiple Named Slots
```razor
@* Panel.razor *@
<div class="panel-header">@Header</div>
<div class="panel-body">@ChildContent</div>
<div class="panel-footer">@Footer</div>

@code {
    [Parameter] public RenderFragment? Header { get; set; }
    [Parameter] public RenderFragment? ChildContent { get; set; }
    [Parameter] public RenderFragment? Footer { get; set; }
}
```

```razor
<Panel>
    <Header><h2>Title</h2></Header>
    <ChildContent><p>Body</p></ChildContent>
    <Footer><small>Footer</small></Footer>
</Panel>
```

### RenderFragment<T> (Typed Templates)
```razor
@typeparam TItem

<ul>
    @foreach (var item in Items ?? Enumerable.Empty<TItem>())
    {
        <li>@ItemTemplate(item)</li>
    }
</ul>

@code {
    [Parameter] public IEnumerable<TItem>? Items { get; set; }
    [Parameter] public RenderFragment<TItem>? ItemTemplate { get; set; }
}
```

```razor
<GenericList Items="people" TItem="Person">
    <ItemTemplate Context="person">
        <strong>@person.Name</strong> — @person.Age
    </ItemTemplate>
</GenericList>
```

## Generic Components

```razor
@typeparam TItem
@typeparam TValue where TValue : class, new()
```

### Cascaded Type Parameters
```razor
@* Parent cascades its type parameter to descendants *@
@attribute [CascadingTypeParameter(nameof(TItem))]
@typeparam TItem

@ChildContent

@code {
    [Parameter] public RenderFragment? ChildContent { get; set; }
}
```

## DynamicComponent

Render a component from a `System.Type` at runtime.

```razor
<DynamicComponent Type="componentType" Parameters="parameters" />

@code {
    private Type componentType = typeof(MyWidget);
    private Dictionary<string, object> parameters = new()
    {
        { "Title", "Dynamic!" },
        { "Count", 42 }
    };
}
```

## Virtualize

Only renders visible items for large lists.

```razor
<Virtualize Items="allItems" Context="item">
    <p>@item.Name</p>
</Virtualize>
```

### With ItemsProvider (Server-Side Paging)
```razor
<Virtualize ItemsProvider="LoadItems" Context="item" ItemSize="50">
    <ItemContent>
        <p>@item.Name</p>
    </ItemContent>
    <Placeholder>
        <p>Loading...</p>
    </Placeholder>
    <EmptyContent>
        <p>No items found.</p>
    </EmptyContent>
</Virtualize>

@code {
    private async ValueTask<ItemsProviderResult<MyItem>> LoadItems(
        ItemsProviderRequest request)
    {
        var items = await DataService.GetItemsAsync(
            request.StartIndex, request.Count, request.CancellationToken);
        return new ItemsProviderResult<MyItem>(items, totalCount);
    }
}
```

- `ItemSize` (default 50px) — set to match actual item height
- `OverscanCount` (default 3) — items rendered beyond visible area
- `SpacerElement="tr"` for table layouts
- `RefreshDataAsync()` to force data reload
- Requires identical item heights and single vertical stack

## @key Directive

Gives Blazor stable identity for list items. Use entity IDs, not loop indices.

```razor
@foreach (var person in people)
{
    <PersonCard @key="person.Id" Person="person" />
}
```

## @ref Directive

Capture component or element references.

```razor
<input @ref="inputElement" />
<MyComponent @ref="componentRef" />

@code {
    private ElementReference inputElement;
    private MyComponent? componentRef;

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
            await inputElement.FocusAsync();
    }
}
```

References are `null` until after first render. Access in `OnAfterRender`.

## Error Boundaries

```razor
<ErrorBoundary>
    <ChildContent>
        <RiskyComponent />
    </ChildContent>
    <ErrorContent Context="exception">
        <p class="error">Something went wrong: @exception.Message</p>
    </ErrorContent>
</ErrorBoundary>
```

- `Recover()` to reset boundary state
- `MaximumErrorCount` to limit catches
- Subclass and override `OnErrorAsync` for logging
