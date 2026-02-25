# External Authentication Providers

## The Core Problem: OAuth Redirects Break Interactive Components

External auth (Google, Microsoft, GitHub, Discord) uses HTTP redirect flows — the browser navigates away, the provider authenticates the user, then redirects back with an authorization code. This is fundamentally incompatible with Interactive Server (SignalR) and Interactive WebAssembly (WASM) render modes. The challenge and callback endpoints **must** be handled by Static SSR middleware, not interactive components.

**Rule**: External auth pages have no `@rendermode`. Interactive components read auth state _after_ the redirect completes.

## Quick Reference

| Provider | NuGet Package | Extension Method | Default Callback Path |
|---|---|---|---|
| Google | `Microsoft.AspNetCore.Authentication.Google` | `.AddGoogle()` | `/signin-google` |
| Microsoft / Entra ID | `Microsoft.AspNetCore.Authentication.MicrosoftAccount` | `.AddMicrosoftAccount()` | `/signin-microsoft` |
| Entra ID (Azure AD) | `Microsoft.AspNetCore.Authentication.OpenIdConnect` | `.AddOpenIdConnect()` | `/signin-oidc` |
| GitHub | `AspNet.Security.OAuth.GitHub` | `.AddGitHub()` | `/signin-github` |
| Discord | `AspNet.Security.OAuth.Discord` | `.AddDiscord()` | `/signin-discord` |

## Secrets Management

**Never hardcode client secrets in source code.** Use .NET user secrets for development and environment variables (or Azure Key Vault) for production.

### Development: User Secrets

```bash
# From the project directory
dotnet user-secrets set "Authentication:Google:ClientId" "your-client-id"
dotnet user-secrets set "Authentication:Google:ClientSecret" "your-client-secret"
dotnet user-secrets set "Authentication:Microsoft:ClientId" "your-client-id"
dotnet user-secrets set "Authentication:Microsoft:ClientSecret" "your-client-secret"
dotnet user-secrets set "Authentication:GitHub:ClientId" "your-client-id"
dotnet user-secrets set "Authentication:GitHub:ClientSecret" "your-client-secret"
dotnet user-secrets set "Authentication:Discord:ClientId" "your-client-id"
dotnet user-secrets set "Authentication:Discord:ClientSecret" "your-client-secret"
```

### Production: Environment Variables

```
Authentication__Google__ClientId=...
Authentication__Google__ClientSecret=...
```

ASP.NET Core's configuration system maps `__` to `:` in environment variable names.

### Reading Configuration

```csharp
// Program.cs — consistent pattern across all providers
var googleClientId     = builder.Configuration["Authentication:Google:ClientId"];
var googleClientSecret = builder.Configuration["Authentication:Google:ClientSecret"];
```

## Common Setup Pattern (Program.cs)

Chain multiple providers off a single `.AddAuthentication()` call. The **external scheme** (`IdentityConstants.ExternalScheme`) is the temporary cookie that stores provider data between the redirect and account creation/login.

```csharp
// Program.cs
builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = IdentityConstants.ApplicationScheme;
    options.DefaultSignInScheme = IdentityConstants.ExternalScheme;
})
.AddIdentityCookies()
.AddGoogle(options =>
{
    options.ClientId     = builder.Configuration["Authentication:Google:ClientId"]!;
    options.ClientSecret = builder.Configuration["Authentication:Google:ClientSecret"]!;
})
.AddMicrosoftAccount(options =>
{
    options.ClientId     = builder.Configuration["Authentication:Microsoft:ClientId"]!;
    options.ClientSecret = builder.Configuration["Authentication:Microsoft:ClientSecret"]!;
})
.AddGitHub(options =>
{
    options.ClientId     = builder.Configuration["Authentication:GitHub:ClientId"]!;
    options.ClientSecret = builder.Configuration["Authentication:GitHub:ClientSecret"]!;
    options.Scope.Add("user:email");
})
.AddDiscord(options =>
{
    options.ClientId     = builder.Configuration["Authentication:Discord:ClientId"]!;
    options.ClientSecret = builder.Configuration["Authentication:Discord:ClientSecret"]!;
    options.Scope.Add("email");
});

builder.Services.AddIdentityCore<ApplicationUser>()
    .AddEntityFrameworkStores<ApplicationDbContext>()
    .AddSignInManager()
    .AddDefaultTokenProviders();
```

## Google OAuth

**Console setup**: Create an OAuth 2.0 Client ID at [console.cloud.google.com](https://console.cloud.google.com). Choose **Web application**, then add the redirect URI.

- **Redirect URI to register**: `https://yourdomain.com/signin-google`
- For local development: `https://localhost:7001/signin-google`

```csharp
// Program.cs
.AddGoogle(options =>
{
    options.ClientId     = builder.Configuration["Authentication:Google:ClientId"]!;
    options.ClientSecret = builder.Configuration["Authentication:Google:ClientSecret"]!;

    // Request additional scopes beyond the defaults (profile, openid)
    options.Scope.Add("email");

    // Map the picture claim from Google's token
    options.ClaimActions.MapJsonKey("picture", "picture");
})
```

Google provides `email`, `name`, `given_name`, `family_name`, and `picture` in the token by default when the `email` scope is included.

## Microsoft / Entra ID

Two separate packages cover different scenarios:

- **Personal Microsoft accounts** (`outlook.com`, `hotmail.com`, `live.com`): use `AddMicrosoftAccount()`
- **Organizational accounts / Azure AD / Entra ID**: use `AddOpenIdConnect()`

### Personal Microsoft Accounts

```csharp
// Program.cs
.AddMicrosoftAccount(options =>
{
    options.ClientId     = builder.Configuration["Authentication:Microsoft:ClientId"]!;
    options.ClientSecret = builder.Configuration["Authentication:Microsoft:ClientSecret"]!;
})
```

Register the app at [portal.azure.com](https://portal.azure.com) under **App registrations**. Set the redirect URI to `https://yourdomain.com/signin-microsoft`. Select **Personal Microsoft accounts only** as the supported account type.

### Entra ID (Azure AD) — Organizational Accounts

```csharp
// Program.cs
.AddOpenIdConnect("EntraId", options =>
{
    options.ClientId     = builder.Configuration["Authentication:EntraId:ClientId"]!;
    options.ClientSecret = builder.Configuration["Authentication:EntraId:ClientSecret"]!;

    // Single-tenant: use your tenant ID
    // Multi-tenant: use "organizations" or "common"
    options.Authority = $"https://login.microsoftonline.com/{builder.Configuration["Authentication:EntraId:TenantId"]}";

    options.CallbackPath            = "/signin-oidc";
    options.SignedOutCallbackPath    = "/signout-callback-oidc";
    options.ResponseType            = OpenIdConnectResponseType.Code;
    options.SaveTokens              = true;
    options.GetClaimsFromUserInfoEndpoint = true;
})
```

## GitHub OAuth

**NuGet**: `AspNet.Security.OAuth.GitHub`

**Developer settings**: Create an OAuth App at [github.com/settings/developers](https://github.com/settings/developers). Set the **Authorization callback URL** to `https://yourdomain.com/signin-github`.

```csharp
// Program.cs
.AddGitHub(options =>
{
    options.ClientId     = builder.Configuration["Authentication:GitHub:ClientId"]!;
    options.ClientSecret = builder.Configuration["Authentication:GitHub:ClientSecret"]!;

    // read:user is included by default; user:email is needed to access email
    options.Scope.Add("read:user");
    options.Scope.Add("user:email");
})
```

**Note**: GitHub does not include the user's email in the token if the email is marked private. The library fetches email separately via the GitHub API when `user:email` scope is present.

## Discord OAuth

**NuGet**: `AspNet.Security.OAuth.Discord`

**Developer portal**: Create an application at [discord.com/developers/applications](https://discord.com/developers/applications). Under **OAuth2**, add the redirect URI `https://yourdomain.com/signin-discord`.

```csharp
// Program.cs
.AddDiscord(options =>
{
    options.ClientId     = builder.Configuration["Authentication:Discord:ClientId"]!;
    options.ClientSecret = builder.Configuration["Authentication:Discord:ClientSecret"]!;

    // identify provides username/avatar; email is a separate scope
    options.Scope.Add("identify");
    options.Scope.Add("email");
})
```

## Claims Mapping

Different providers use different claim type names. Raw claims from each provider before normalization:

| Claim | Google | Microsoft | GitHub | Discord |
|---|---|---|---|---|
| Display name | `name` | `name` | `urn:github:name` | `urn:discord:username` |
| Email | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress` | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress` | `urn:github:email` | `urn:discord:email` |
| Profile picture | `picture` (custom mapped) | — | `urn:github:avatar_url` | `urn:discord:avatar` |
| Subject / ID | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier` | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier` | `urn:github:id` | `urn:discord:id` |

### Normalizing Claims with IClaimsTransformation

Use `IClaimsTransformation` to normalize provider-specific claim types into a consistent internal schema. This runs once after authentication, before the claims principal is stored.

```csharp
// NormalizedClaimsTransformation.cs
public class NormalizedClaimsTransformation : IClaimsTransformation
{
    public Task<ClaimsPrincipal> TransformAsync(ClaimsPrincipal principal)
    {
        var identity = (ClaimsIdentity)principal.Identity!;

        // Normalize email — try each provider's known email claim type
        if (!principal.HasClaim(c => c.Type == ClaimTypes.Email))
        {
            var email =
                principal.FindFirstValue("urn:github:email") ??
                principal.FindFirstValue("urn:discord:email");

            if (email is not null)
                identity.AddClaim(new Claim(ClaimTypes.Email, email));
        }

        // Normalize display name
        if (!principal.HasClaim(c => c.Type == ClaimTypes.Name))
        {
            var name =
                principal.FindFirstValue("urn:github:name") ??
                principal.FindFirstValue("urn:discord:username");

            if (name is not null)
                identity.AddClaim(new Claim(ClaimTypes.Name, name));
        }

        return Task.FromResult(principal);
    }
}
```

```csharp
// Program.cs — register the transformation
builder.Services.AddScoped<IClaimsTransformation, NormalizedClaimsTransformation>();
```

## Account Linking

When a user authenticates with an external provider, `SignInManager` looks for an existing local account linked to that provider. If no link exists, the app must create or link an account.

### Handling the External Login Callback (Static SSR Page)

```razor
@* Account/ExternalLoginCallback.razor *@
@page "/Account/ExternalLoginCallback"
@* No @rendermode — must be Static SSR *@

@inject SignInManager<ApplicationUser> SignInManager
@inject UserManager<ApplicationUser> UserManager
@inject NavigationManager Navigation

@code {
    [CascadingParameter]
    private HttpContext HttpContext { get; set; } = default!;

    protected override async Task OnInitializedAsync()
    {
        // Retrieve the external login info from the temporary external cookie
        var info = await SignInManager.GetExternalLoginInfoAsync();
        if (info is null)
        {
            Navigation.NavigateTo("/Account/Login?error=ExternalLoginFailed");
            return;
        }

        // Attempt to sign in with the existing linked account
        var result = await SignInManager.ExternalLoginSignInAsync(
            info.LoginProvider,
            info.ProviderKey,
            isPersistent: false,
            bypassTwoFactor: true);

        if (result.Succeeded)
        {
            Navigation.NavigateTo("/", forceLoad: true);
            return;
        }

        // No linked account — create one or prompt the user
        var email = info.Principal.FindFirstValue(ClaimTypes.Email);
        if (email is not null)
        {
            var user = await UserManager.FindByEmailAsync(email);
            if (user is null)
            {
                // Create a new local account and link it
                user = new ApplicationUser { UserName = email, Email = email };
                await UserManager.CreateAsync(user);
            }

            await UserManager.AddLoginAsync(user, info);
            await SignInManager.SignInAsync(user, isPersistent: false);
            Navigation.NavigateTo("/", forceLoad: true);
        }
    }
}
```

### Adding a Login Provider to an Existing Account

```csharp
// AccountController or managed account page
var info = await SignInManager.GetExternalLoginInfoAsync();
var user = await UserManager.GetUserAsync(HttpContext.User);

var result = await UserManager.AddLoginAsync(user, info);
if (result.Succeeded)
{
    await SignInManager.RefreshSignInAsync(user);
}
```

### Removing a Linked Provider

```csharp
var user   = await UserManager.GetUserAsync(HttpContext.User);
var result = await UserManager.RemoveLoginAsync(user, loginProvider, providerKey);

if (result.Succeeded)
{
    await SignInManager.RefreshSignInAsync(user);
}
```

### Listing Linked Providers

```csharp
var user   = await UserManager.GetUserAsync(HttpContext.User);
var logins = await UserManager.GetLoginsAsync(user);
// logins is IList<UserLoginInfo> — each has LoginProvider and ProviderDisplayName
```

## Blazor Render Mode Concerns

External auth is redirect-based HTTP. Render mode rules for auth pages are non-negotiable.

| Scenario | Correct Render Mode | Reason |
|---|---|---|
| Login page with external provider buttons | Static SSR (no `@rendermode`) | Issues the challenge redirect via HTTP |
| External login callback page | Static SSR (no `@rendermode`) | Reads the authorization code from query string, sets auth cookies |
| Account management (link/unlink providers) | Static SSR (no `@rendermode`) | Reads and writes cookies via `HttpContext` |
| Showing logged-in user details after auth | Any interactive mode | Reads `AuthenticationState`, no cookie writes needed |
| `AuthorizeView` on a dashboard | Any interactive mode | Reads cascading `AuthenticationState` |

### Initiating the OAuth Challenge

The challenge must originate from an HTTP GET to a Static SSR endpoint — not from a Blazor button click inside an interactive circuit.

```razor
@* Account/Login.razor — Static SSR *@
@page "/Account/Login"
@* No @rendermode *@

<form action="/Account/ExternalLogin" method="post">
    <AntiForgeryToken />
    <input type="hidden" name="provider" value="Google" />
    <input type="hidden" name="returnUrl" value="/" />
    <button type="submit">Sign in with Google</button>
</form>

<form action="/Account/ExternalLogin" method="post">
    <AntiForgeryToken />
    <input type="hidden" name="provider" value="GitHub" />
    <input type="hidden" name="returnUrl" value="/" />
    <button type="submit">Sign in with GitHub</button>
</form>
```

```csharp
// Account/ExternalLogin.razor.cs or minimal API endpoint
// Handles POST /Account/ExternalLogin, issues the challenge redirect
app.MapPost("/Account/ExternalLogin", (
    string provider,
    string returnUrl,
    SignInManager<ApplicationUser> signInManager) =>
{
    var redirectUrl = $"/Account/ExternalLoginCallback?returnUrl={Uri.EscapeDataString(returnUrl)}";
    var properties  = signInManager.ConfigureExternalAuthenticationProperties(provider, redirectUrl);
    return Results.Challenge(properties, [provider]);
});
```

### Global Interactive Mode and Auth Pages

When `<Routes>` in `App.razor` carries `@rendermode="InteractiveServer"`, all pages default to interactive. Auth callback pages must opt out explicitly.

```razor
@* Account/ExternalLoginCallback.razor *@
@page "/Account/ExternalLoginCallback"
@attribute [ExcludeFromInteractiveRouting]
@* ^ Forces this page to Static SSR even when Routes is globally interactive *@
```

### Reading Auth State in Interactive Components After Login

Once the redirect flow completes and a cookie is set, interactive components can read auth state normally via the cascading `AuthenticationState`.

```razor
@* Dashboard.razor *@
@page "/dashboard"
@rendermode InteractiveServer

@code {
    [CascadingParameter]
    private Task<AuthenticationState>? AuthState { get; set; }

    private string? providerName;
    private string? userEmail;

    protected override async Task OnInitializedAsync()
    {
        if (AuthState is not null)
        {
            var state = await AuthState;
            userEmail    = state.User.FindFirstValue(ClaimTypes.Email);

            // Determine which provider was used (stored by Identity in AspNetUserLogins)
            // For display purposes, read from claims or UserManager
        }
    }
}
```

## Common Mistakes

| Mistake | Symptom / Risk | Fix |
|---|---|---|
| Hardcoding `ClientSecret` in `appsettings.json` | Secret committed to version control; provider can be abused | Use `dotnet user-secrets` for dev; environment variables or Key Vault for prod |
| Wrong redirect URI registered with provider | `redirect_uri_mismatch` error from provider; auth fails completely | Register exact URI (scheme, host, port, path) in provider console; match `CallbackPath` in options |
| Missing scope for email | `ClaimTypes.Email` is null; can't find or create account | Add `"email"` scope for Google/Discord, `"user:email"` for GitHub |
| Placing the OAuth challenge inside an Interactive Server component | Challenge redirect fires inside SignalR circuit; browser navigation never happens, or `InvalidOperationException` is thrown | Route challenge through a Static SSR form POST or minimal API endpoint |
| Not using `[ExcludeFromInteractiveRouting]` on callback page | Callback page renders as Interactive Server; `HttpContext` is null; cannot read auth code or set cookies | Add `@attribute [ExcludeFromInteractiveRouting]` to all auth pages when using global interactive routing |
| Skipping `AddLoginAsync` after account creation | User can log in once but provider association is not stored; next login creates a duplicate account | Always call `UserManager.AddLoginAsync(user, externalLoginInfo)` before signing in |
| Not calling `GetExternalLoginInfoAsync` immediately in the callback | External cookie expires (short TTL); `ExternalLoginInfo` returns null; auth flow abandoned | Process the callback without any async delays before accessing `GetExternalLoginInfoAsync` |
| Treating all providers' claim types as identical | Email or name claim is missing because provider uses a non-standard type | Use `IClaimsTransformation` to normalize claims after authentication |

## Cross-References

- `11-authentication-authorization.md` — `AuthorizeView`, `[Authorize]`, `AuthenticationStateProvider`, Identity UI render mode rules
- `01-render-modes.md` — Why Static SSR is required for HTTP cookie operations and `[ExcludeFromInteractiveRouting]`
