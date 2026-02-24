# Authentication and Authorization

## The Big Pain Point: HttpContext vs Render Modes

This is the #1 source of confusion in Blazor auth:

| Render Mode | HttpContext Available? | How to Get User |
|---|---|---|
| Static SSR | YES | `HttpContext.User` |
| Prerendering phase | YES | `HttpContext.User` |
| Interactive Server (SignalR) | **NO** | `AuthenticationStateProvider` |
| Interactive WebAssembly | **NO** | `AuthenticationStateProvider` |

**Why**: After the initial HTTP request completes, Interactive Server communicates over SignalR WebSocket — there is no HTTP request, so no HttpContext. WASM runs entirely in the browser.

**This is why Identity pages (login, register, etc.) use Static SSR** — they need HttpContext to set cookies and read form posts.

### The Error You'll See
```
Cannot resolve scoped service 'Microsoft.AspNetCore.Http.IHttpContextAccessor'
from root provider.
```
Or `HttpContext` is null in an interactive component.

### The Rule
- **Static SSR pages**: Use `HttpContext` freely
- **Interactive components**: Use `AuthenticationStateProvider` or `[CascadingParameter] Task<AuthenticationState>`
- **Never inject IHttpContextAccessor into interactive components**

## AuthenticationStateProvider

The foundation of Blazor auth. Provides a `Task<AuthenticationState>` containing the user's `ClaimsPrincipal`.

```csharp
public abstract class AuthenticationStateProvider
{
    public abstract Task<AuthenticationState> GetAuthenticationStateAsync();
    public event AuthenticationStateChangedHandler? AuthenticationStateChanged;
    protected void NotifyAuthenticationStateChanged(Task<AuthenticationState> task);
}
```

### Server-Side
Built-in provider reads from the circuit's authentication state (established during the initial HTTP connection). Registered automatically by `AddInteractiveServerComponents()`.

### WASM
Must be implemented to read tokens (JWT) from browser storage and construct a ClaimsPrincipal. Common pattern:

```csharp
public class CustomAuthStateProvider : AuthenticationStateProvider
{
    private readonly HttpClient _http;
    private readonly ILocalStorageService _localStorage;

    public override async Task<AuthenticationState> GetAuthenticationStateAsync()
    {
        var token = await _localStorage.GetItemAsync<string>("authToken");
        if (string.IsNullOrEmpty(token))
            return new AuthenticationState(new ClaimsPrincipal(new ClaimsIdentity()));

        var claims = ParseClaimsFromJwt(token);
        var identity = new ClaimsIdentity(claims, "jwt");
        return new AuthenticationState(new ClaimsPrincipal(identity));
    }
}
```

## Setup

### Program.cs (Blazor Web App with Identity)
```csharp
builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = IdentityConstants.ApplicationScheme;
    options.DefaultSignInScheme = IdentityConstants.ExternalScheme;
})
.AddIdentityCookies();

builder.Services.AddIdentityCore<ApplicationUser>()
    .AddEntityFrameworkStores<ApplicationDbContext>()
    .AddSignInManager()
    .AddDefaultTokenProviders();

// This adds AuthenticationStateProvider for server-side
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

// Cascading auth state available to all components
builder.Services.AddCascadingAuthenticationState();
```

### App.razor
```razor
<CascadingAuthenticationState>
    <Router AppAssembly="typeof(App).Assembly">
        <Found Context="routeData">
            <AuthorizeRouteView RouteData="routeData"
                                DefaultLayout="typeof(Layout.MainLayout)">
                <NotAuthorized>
                    <RedirectToLogin />
                </NotAuthorized>
            </AuthorizeRouteView>
        </Found>
    </Router>
</CascadingAuthenticationState>
```

Or with root-level registration (preferred in .NET 8+):
```csharp
builder.Services.AddCascadingAuthenticationState();
```

## AuthorizeView

Conditional rendering based on auth state.

```razor
<AuthorizeView>
    <Authorized>
        <p>Hello, @context.User.Identity?.Name!</p>
        <a href="/logout">Logout</a>
    </Authorized>
    <NotAuthorized>
        <a href="/login">Login</a>
    </NotAuthorized>
    <Authorizing>
        <p>Checking auth...</p>
    </Authorizing>
</AuthorizeView>
```

### Role-Based
```razor
<AuthorizeView Roles="Admin,Manager">
    <Authorized>
        <button @onclick="DeleteAll">Admin Action</button>
    </Authorized>
</AuthorizeView>
```

### Policy-Based
```razor
<AuthorizeView Policy="CanEditContent">
    <Authorized>
        <EditButton />
    </Authorized>
</AuthorizeView>
```

## [Authorize] Attribute

Protect entire pages. **Only works on `@page` routed components.**

```razor
@page "/admin"
@attribute [Authorize]

<h1>Admin Page</h1>
```

```razor
@page "/admin"
@attribute [Authorize(Roles = "Admin")]

<h1>Admin Only</h1>
```

```razor
@page "/content/edit"
@attribute [Authorize(Policy = "ContentEditor")]
```

## Getting Current User in Interactive Components

### Via Cascading Parameter (Preferred)
```razor
@code {
    [CascadingParameter]
    private Task<AuthenticationState>? AuthState { get; set; }

    private string? userName;

    protected override async Task OnInitializedAsync()
    {
        if (AuthState is not null)
        {
            var state = await AuthState;
            userName = state.User.Identity?.Name;

            if (state.User.IsInRole("Admin"))
            {
                // Admin-specific logic
            }

            var userId = state.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        }
    }
}
```

### Via Injected AuthenticationStateProvider
```razor
@inject AuthenticationStateProvider AuthStateProvider

@code {
    protected override async Task OnInitializedAsync()
    {
        var state = await AuthStateProvider.GetAuthenticationStateAsync();
        var user = state.User;
    }
}
```

## Cookie Auth and SignalR Circuits

In Blazor Server / Interactive Server:

1. User navigates to the app → HTTP request with cookies
2. ASP.NET Core auth middleware validates the cookie
3. SignalR circuit is established, auth state captured from the HTTP context
4. Subsequent interactions go over WebSocket — no more HTTP requests
5. **Cookie expiration during active circuit**: The circuit continues to work even after the cookie expires. Auth state is re-evaluated on the next full page load/navigation.

**Implication**: If a user's roles change or they're banned, it won't take effect until the circuit is re-established (page refresh).

## Identity UI and Render Modes

The Blazor Identity template scaffolds auth pages (login, register, manage) as **Static SSR** components. This is intentional:

- Login/register pages POST form data and set cookies → requires HttpContext
- Account management pages read/write cookies → requires HttpContext
- These pages cannot work as Interactive Server or WASM

### The scaffolded pattern:
```razor
@page "/Account/Login"
@* No @rendermode — Static SSR *@

<EditForm Model="Input" method="post" OnValidSubmit="LoginUser" FormName="login">
    <!-- Identity form fields -->
</EditForm>

@code {
    [CascadingParameter]
    private HttpContext HttpContext { get; set; } = default!;

    // HttpContext works here because this is Static SSR
}
```

### When your app is globally interactive:
If you set `@rendermode InteractiveServer` on `<Routes>` in App.razor, Identity pages will break because they need Static SSR. The template handles this with:

```razor
@* App.razor *@
<Routes @rendermode="InteractiveServer" />
```

And Identity pages use `[ExcludeFromInteractiveRouting]` or are excluded from the interactive render mode via convention.

## Redirecting Unauthenticated Users

### RedirectToLogin Component Pattern
```razor
@* RedirectToLogin.razor *@
@inject NavigationManager Navigation

@code {
    protected override void OnInitialized()
    {
        Navigation.NavigateTo($"/Account/Login?returnUrl={Uri.EscapeDataString(Navigation.Uri)}", forceLoad: true);
    }
}
```

Used in AuthorizeRouteView:
```razor
<AuthorizeRouteView RouteData="routeData" DefaultLayout="typeof(MainLayout)">
    <NotAuthorized>
        <RedirectToLogin />
    </NotAuthorized>
</AuthorizeRouteView>
```

### Programmatic Check
```csharp
[CascadingParameter]
private Task<AuthenticationState>? AuthState { get; set; }

protected override async Task OnInitializedAsync()
{
    var state = await AuthState!;
    if (!state.User.Identity?.IsAuthenticated ?? true)
    {
        Navigation.NavigateTo("/Account/Login", forceLoad: true);
        return;
    }
}
```

## WASM Token-Based Auth

### JWT Pattern
```csharp
// Program.cs (Client)
builder.Services.AddAuthorizationCore();
builder.Services.AddScoped<AuthenticationStateProvider, JwtAuthStateProvider>();

// Add auth message handler to HttpClient
builder.Services.AddHttpClient("API", client =>
    client.BaseAddress = new Uri("https://api.example.com"))
    .AddHttpMessageHandler<AuthorizationMessageHandler>();
```

### Storing Tokens
```csharp
// After login - store in browser storage
await localStorage.SetItemAsync("authToken", response.Token);

// On HttpClient requests - attach as Bearer header
public class AuthTokenHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var token = await localStorage.GetItemAsync<string>("authToken");
        if (!string.IsNullOrEmpty(token))
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

        return await base.SendAsync(request, cancellationToken);
    }
}
```

## Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Injecting `IHttpContextAccessor` in interactive component | Null or throws | Use `AuthenticationStateProvider` |
| `[Authorize]` on non-`@page` component | Silently ignored | Only works on routable components |
| Identity pages with interactive render mode | Login doesn't work, cookies not set | Keep Identity pages as Static SSR |
| Not using `forceLoad: true` on login redirect | Navigation intercepted, cookie not read | `NavigateTo("/login", forceLoad: true)` |
| Checking auth in `OnInitialized` without null guard | NullReferenceException | Check `AuthState is not null` first |
| Expecting role changes to take effect immediately | User still has old roles during circuit | Roles update on next circuit (page refresh) |
| Global interactive mode breaking Identity pages | `HttpContext` null on login page | Use `[ExcludeFromInteractiveRouting]` or per-page render modes |
