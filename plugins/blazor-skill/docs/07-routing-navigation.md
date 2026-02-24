# Routing and Navigation

## @page Directive

Compiles to `[RouteAttribute]`. Multiple routes supported per component.

```razor
@page "/users"
@page "/people"
```

## Route Parameters

```razor
@page "/user/{Id:int}"
@page "/user/{Name}"

@code {
    [Parameter] public int Id { get; set; }
    [Parameter] public string Name { get; set; } = "";
}
```

### Optional Parameters
```razor
@page "/user/{Id:int?}"

@code {
    [Parameter] public int? Id { get; set; }

    protected override void OnParametersSet()
    {
        Id ??= 1; // Default value
    }
}
```

### Route Constraints
`:bool`, `:datetime`, `:decimal`, `:double`, `:float`, `:guid`, `:int`, `:long`, `:nonfile`

Combine with optional: `{option:bool?}`

### Catch-All Parameters
```razor
@page "/catch-all/{*pageRoute}"

@code {
    [Parameter] public string? PageRoute { get; set; }
}
```

## NavigationManager

```csharp
@inject NavigationManager Navigation

// Current URL
var url = Navigation.Uri;
var baseUrl = Navigation.BaseUri;

// Navigate
Navigation.NavigateTo("/users");
Navigation.NavigateTo("/users", forceLoad: true);    // Full page reload
Navigation.NavigateTo("/users", replace: true);       // Replace history entry

// Build URL with query parameters
var uri = Navigation.GetUriWithQueryParameter("page", 3);
var uri = Navigation.GetUriWithQueryParameter("filter", (string?)null); // Remove param

// Refresh current page
Navigation.Refresh();

// Trigger 404
Navigation.NotFound();
```

### Listen for Navigation
```razor
@implements IDisposable

@code {
    protected override void OnInitialized()
        => Navigation.LocationChanged += HandleLocationChanged;

    private void HandleLocationChanged(object? sender, LocationChangedEventArgs e)
    {
        // e.Location = new URL
        // e.IsNavigationIntercepted = true if link click, false if NavigateTo
    }

    public void Dispose()
        => Navigation.LocationChanged -= HandleLocationChanged;
}
```

### Pre-Navigation Hooks
```csharp
Navigation.RegisterLocationChangingHandler(async context =>
{
    if (hasUnsavedChanges)
        context.PreventNavigation();
});
```

## Query String Parameters

```razor
@page "/search"

@code {
    [SupplyParameterFromQuery]
    private string? Filter { get; set; }

    [SupplyParameterFromQuery]
    private int? Page { get; set; }

    [SupplyParameterFromQuery(Name = "q")]
    private string? SearchQuery { get; set; }

    // Array support: ?tag=blazor&tag=dotnet
    [SupplyParameterFromQuery(Name = "tag")]
    private string[]? Tags { get; set; }
}
```

Supported types: `bool`, `DateTime`, `decimal`, `double`, `float`, `Guid`, `int`, `long`, `string`, nullable variants, arrays.

## NavLink Component

Renders `<a>` with automatic `active` class.

```razor
<NavLink href="/" Match="NavLinkMatch.All">Home</NavLink>
<NavLink href="/users" Match="NavLinkMatch.Prefix">Users</NavLink>
```

- `NavLinkMatch.All` — exact match (use for home page)
- `NavLinkMatch.Prefix` — prefix match (default, use for sections)
- `ActiveClass` — customize the CSS class name

## Enhanced Navigation (.NET 8+)

Intercepts link clicks and uses `fetch` instead of full page reload.

```html
<!-- Disable per-link -->
<a href="/external" data-enhance-nav="false">External</a>

<!-- Preserve dynamic DOM content across updates -->
<div data-permanent>
    <!-- Content managed by external JS -->
</div>
```

- `Navigation.NavigateTo` uses enhanced navigation by default
- `forceLoad: true` bypasses it
- Enhanced forms: `<EditForm Enhance>` or `<form data-enhance>`

## Not Found Handling

```csharp
// In a component — triggers 404
Navigation.NotFound();
```

Router-level:
```razor
<Router AppAssembly="typeof(App).Assembly" NotFoundPage="typeof(NotFound)">
    ...
</Router>
```

## Route Precedence

When multiple routes could match a URL, Blazor uses these rules (highest to lowest priority):

1. **More segments win** — `/users/active` beats `/{*catch-all}`
2. **Literal segments beat parameters** — `/users/active` beats `/users/{status}`
3. **Constrained parameters beat unconstrained** — `{Id:int}` beats `{Id}`
4. **Catch-all parameters are lowest priority** — `{*path}` only matches when nothing else does

If two routes have identical precedence, routing is ambiguous and Blazor throws an exception at startup.

## FocusOnNavigate

Improves accessibility by setting focus to an element after navigation — critical for screen readers and keyboard users.

```razor
@* App.razor or Routes.razor *@
<FocusOnNavigate RouteData="routeData" Selector="h1" />
```

- `Selector` uses a CSS selector to identify the element to focus
- Place it alongside `<RouteView>` in the router configuration
- Typically targets the main `<h1>` heading so assistive tech announces the new page

## Navigation Lock (Unsaved Changes)

Prevent accidental navigation away from a form with unsaved changes:

```razor
<NavigationLock OnBeforeInternalNavigation="OnBeforeNavigation" ConfirmExternalNavigation />

@code {
    private async Task OnBeforeNavigation(LocationChangingContext context)
    {
        if (hasUnsavedChanges)
        {
            var confirmed = await JS.InvokeAsync<bool>("confirm", "Discard unsaved changes?");
            if (!confirmed) context.PreventNavigation();
        }
    }
}
```

- `ConfirmExternalNavigation` shows the browser's built-in prompt for external navigations (tab close, address bar)
- Internal navigation is handled by the `OnBeforeInternalNavigation` callback
