# Blazor Security Patterns

## The Core Problem: Security Varies by Render Mode

Blazor's multiple render modes each have different threat surfaces. A CSP that works for Static SSR will break Interactive Server. Antiforgery tokens are automatic for some render modes and absent for others. Skipping per-mode analysis is the root cause of most Blazor security bugs.

## CSRF and Antiforgery

### Which Render Modes Need Antiforgery Tokens?

| Render Mode | CSRF Risk | Token Mechanism | Notes |
|---|---|---|---|
| Static SSR (`EditForm`) | Yes | Auto-injected by `AddAntiforgery` + `UseAntiforgery` | Blazor injects the token; no manual work needed |
| Static SSR (plain `<form>`) | Yes | Manual: `<AntiforgeryToken />` inside the form | Blazor does not inject into raw HTML forms |
| Interactive Server | No (SignalR, not HTTP POST) | N/A | Circuit is already authenticated at connection time |
| Interactive WASM | No (API calls use bearer tokens or cookies) | N/A | API endpoints must have their own antiforgery or auth |
| Minimal API endpoints called from WASM | Yes if cookie-authenticated | `[ValidateAntiForgeryToken]` or use JWT bearer | Cookie-auth APIs are susceptible without token validation |

### Middleware Setup (Static SSR)

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddAntiforgery();
builder.Services.AddRazorComponents();

var app = builder.Build();

// Order matters: UseAntiforgery must come after UseRouting
app.UseRouting();
app.UseAntiforgery();

app.MapRazorComponents<App>();
```

`AddRazorComponents()` registers antiforgery internally. `UseAntiforgery()` validates tokens on all non-GET requests to Razor component endpoints. Together they cover all `EditForm` submissions in Static SSR automatically.

### `<AntiforgeryToken />` for Plain HTML Forms

Blazor does not inject antiforgery tokens into raw `<form>` elements — only into `<EditForm>`. Add the component manually:

```razor
@* ContactPage.razor — Static SSR *@
@page "/contact"

<form method="post" action="/contact/submit">
    <AntiforgeryToken />
    <input name="email" type="email" />
    <button type="submit">Send</button>
</form>
```

The `<AntiforgeryToken />` component renders a hidden input containing the request verification token. Omitting it causes a `400 Bad Request` when `UseAntiforgery()` is in the pipeline.

### Antiforgery for API Endpoints Called from Interactive Components

Interactive components call server APIs over `HttpClient` (WASM) or via injected services (Server). If those APIs use cookie authentication, protect them explicitly:

```csharp
// Program.cs — protect minimal API endpoint
app.MapPost("/api/comments", async (CommentRequest req, ICommentService svc) =>
{
    await svc.AddAsync(req);
    return Results.Ok();
})
.RequireAuthorization()
.AddEndpointFilter<AntiforgeryValidationEndpointFilter>(); // Microsoft.AspNetCore.Antiforgery
```

For endpoints that accept JWT bearer tokens (no cookies), CSRF is not applicable — bearer tokens are not sent automatically by the browser.

---

## XSS Prevention

### `MarkupString` — The Escape Hatch That Bypasses All Sanitization

Blazor HTML-encodes all string output by default. `MarkupString` is the explicit opt-out: it instructs the renderer to emit raw HTML without any escaping.

**Do not pass user-supplied content to `MarkupString` without sanitization.** An attacker who can control that content can execute arbitrary JavaScript in the browser.

```razor
@* DANGEROUS — never do this *@
@((MarkupString)userComment)

@* DANGEROUS — still raw HTML, same risk *@
@(new MarkupString(userComment))
```

### Sanitizing User Content with HtmlSanitizer

Install `Ganss.Xss` (HtmlSanitizer):

```
dotnet add package HtmlSanitizer
```

Register as a singleton (the sanitizer is thread-safe and expensive to construct):

```csharp
// Program.cs
builder.Services.AddSingleton<HtmlSanitizer>(_ =>
{
    var sanitizer = new HtmlSanitizer();
    // Allow only safe tags and attributes
    sanitizer.AllowedTags.Clear();
    sanitizer.AllowedTags.Add("p");
    sanitizer.AllowedTags.Add("strong");
    sanitizer.AllowedTags.Add("em");
    sanitizer.AllowedTags.Add("ul");
    sanitizer.AllowedTags.Add("li");
    sanitizer.AllowedTags.Add("a");
    sanitizer.AllowedAttributes.Add("href");
    sanitizer.AllowedSchemes.Add("https");
    return sanitizer;
});
```

### Reusable `SanitizedMarkup` Component

Encapsulate the sanitize-then-render pattern so it cannot be bypassed accidentally:

```razor
@* SanitizedMarkup.razor *@
@inject HtmlSanitizer Sanitizer

@((MarkupString)_safe)

@code {
    private string _safe = string.Empty;

    [Parameter, EditorRequired]
    public string RawHtml { get; set; } = string.Empty;

    protected override void OnParametersSet()
    {
        _safe = Sanitizer.Sanitize(RawHtml);
    }
}
```

Usage:

```razor
@* BlogPost.razor *@
<SanitizedMarkup RawHtml="@post.BodyHtml" />
```

**Never** use `MarkupString` directly for user-generated content outside this component.

### JS Interop Injection Risks

`IJSRuntime.InvokeVoidAsync` serializes arguments to JSON. If an argument is a user-supplied string that reaches a JavaScript function that uses `innerHTML`, `document.write`, or `eval`, XSS is possible.

```csharp
// DANGEROUS — if userInput contains </script><script>alert(1)</script>
await JS.InvokeVoidAsync("renderBio", userInput);
```

```javascript
// wwwroot/bio.js — DANGEROUS
export function renderBio(content) {
    document.getElementById('bio').innerHTML = content; // XSS
}
```

**Fix**: Set `textContent` instead of `innerHTML` for plain text, or sanitize server-side before passing to JS:

```javascript
// wwwroot/bio.js — safe
export function renderBio(content) {
    document.getElementById('bio').textContent = content; // No XSS
}
```

---

## Content Security Policy

### Per-Render-Mode CSP Directives

Each render mode requires different CSP directives. A single global policy must be the union of all required directives.

| Directive | Static SSR | Interactive Server | Interactive WASM | Reason |
|---|---|---|---|---|
| `script-src 'self'` | Yes | Yes | Yes | Baseline |
| `script-src 'wasm-unsafe-eval'` | No | No | **Yes** | Required for WASM bytecode execution |
| `connect-src wss:` | No | **Yes** | No | SignalR WebSocket connection |
| `connect-src 'self'` | No | Yes | Yes | Fetch/XHR back to origin |
| `style-src 'self'` | Yes | Yes | Yes | Baseline |
| `frame-ancestors 'none'` | Yes | Yes | Yes | Clickjacking protection |

**Full example for a Blazor Web App using all render modes:**

```csharp
// Program.cs
app.Use(async (context, next) =>
{
    context.Response.Headers.Append(
        "Content-Security-Policy",
        "default-src 'self'; " +
        "script-src 'self' 'wasm-unsafe-eval'; " +
        "connect-src 'self' wss:; " +
        "style-src 'self' 'unsafe-inline'; " +
        "img-src 'self' data:; " +
        "frame-ancestors 'none';");
    await next();
});
```

Inline styles generated by Blazor component isolation may require `'unsafe-inline'` for `style-src`. Evaluate whether nonces are worth the implementation cost for your threat model.

### Nonce Middleware for Inline Scripts

If you have inline `<script>` blocks that cannot be moved to external files, use nonces instead of `'unsafe-inline'`:

```csharp
// NonceMiddleware.cs
public class NonceMiddleware(RequestDelegate next)
{
    public const string NonceKey = "csp-nonce";

    public async Task InvokeAsync(HttpContext context)
    {
        var nonce = Convert.ToBase64String(RandomNumberGenerator.GetBytes(16));
        context.Items[NonceKey] = nonce;

        context.Response.Headers.Append(
            "Content-Security-Policy",
            $"default-src 'self'; script-src 'self' 'nonce-{nonce}'; frame-ancestors 'none';");

        await next(context);
    }
}
```

```csharp
// Program.cs
app.UseMiddleware<NonceMiddleware>();
```

```razor
@* _Host.razor or App.razor — inject nonce into inline script tags *@
@inject IHttpContextAccessor HttpContextAccessor

@{
    var nonce = HttpContextAccessor.HttpContext?.Items[NonceMiddleware.NonceKey]?.ToString();
}

<script nonce="@nonce">
    // inline initialization script
</script>
```

**Note**: Nonces only work for Static SSR. Interactive Server and WASM components run after the initial HTTP response, so nonces cannot be used for their runtime behavior.

---

## Secure Token Storage

### The localStorage Risk

Storing tokens in `localStorage` or `sessionStorage` is common in WASM apps but carries a specific risk: **any JavaScript running on the page can read localStorage**, including injected third-party scripts and XSS payloads.

| Storage | XSS Readable | CSRF Risk | Suitable For |
|---|---|---|---|
| `localStorage` | Yes | No | Low-sensitivity, short-lived tokens only |
| `sessionStorage` | Yes | No | Session tokens; cleared on tab close |
| `httpOnly` cookie | **No** | Yes (mitigate with SameSite) | Sensitive auth tokens |
| In-memory (JS variable) | No (normally) | No | Refresh tokens in secure WASM apps |

**If an attacker achieves XSS, tokens stored in localStorage are immediately exfiltrated.** The browser's cookie jar with `httpOnly` prevents this because JavaScript cannot read `httpOnly` cookies.

### httpOnly Cookie Pattern

The server sets the cookie after authentication. The browser sends it automatically on every request. JavaScript cannot read or modify it.

```csharp
// AccountController.cs or Login.razor code-behind (Static SSR)
Response.Cookies.Append("auth_token", jwtToken, new CookieOptions
{
    HttpOnly = true,
    Secure = true,         // HTTPS only
    SameSite = SameSiteMode.Strict,
    Expires = DateTimeOffset.UtcNow.AddHours(8)
});
```

Pair with `SameSite=Strict` or `SameSite=Lax` to mitigate CSRF. See the Antiforgery section for endpoint-level validation.

### BFF (Backend for Frontend) Pattern

In a BFF architecture, the Blazor WASM app never holds tokens. The ASP.NET Core server holds the tokens and proxies API calls, forwarding credentials internally.

```
Browser (WASM)          ASP.NET Core BFF        External API
      |                        |                      |
      |-- GET /api/orders ---->|                      |
      |   (httpOnly cookie)    |-- Bearer <token> --->|
      |                        |<-- 200 orders -------|
      |<-- 200 orders ---------|                      |
```

Minimal BFF proxy endpoint:

```csharp
// Program.cs
app.MapGet("/api/orders", async (HttpContext context, ITokenStore tokens, HttpClient client) =>
{
    // Token never leaves the server
    var token = await tokens.GetTokenAsync(context.User);
    client.DefaultRequestHeaders.Authorization =
        new AuthenticationHeaderValue("Bearer", token);

    var orders = await client.GetFromJsonAsync<Order[]>("https://internal-api/orders");
    return Results.Ok(orders);
})
.RequireAuthorization();
```

The WASM app calls `/api/orders` with a session cookie. The BFF resolves the token internally. The token never touches the browser.

---

## SignalR Circuit Security

Interactive Server components communicate over a persistent SignalR WebSocket. Without limits, a single user can exhaust server resources.

### Connection Limits Per User

```csharp
// Program.cs
builder.Services.AddSignalR(options =>
{
    // Default is 1; increase for legitimate parallel operations
    options.MaximumParallelInvocationsPerClient = 1;

    // Reject messages larger than this (bytes); default is 32KB
    options.MaximumReceiveMessageSize = 32 * 1024;

    // Close the circuit if keep-alive fails
    options.ClientTimeoutInterval = TimeSpan.FromSeconds(30);
    options.KeepAliveInterval = TimeSpan.FromSeconds(15);
});
```

### Rate Limiting Hub Methods

Apply ASP.NET Core rate limiting to the SignalR hub endpoint to prevent flooding:

```csharp
// Program.cs
builder.Services.AddRateLimiter(options =>
{
    options.AddSlidingWindowLimiter("signalr", opt =>
    {
        opt.Window = TimeSpan.FromSeconds(10);
        opt.SegmentsPerWindow = 5;
        opt.PermitLimit = 50;
        opt.QueueLimit = 0; // Reject immediately when limit exceeded
    });
});

var app = builder.Build();
app.UseRateLimiter();

// Apply to the Blazor hub endpoint
app.MapBlazorHub().RequireRateLimiting("signalr");
```

### Message Size Configuration

Large messages from a client can cause memory pressure. Set `MaximumReceiveMessageSize` to a value appropriate for your application's expected payloads. Exceeding the limit terminates the circuit connection.

```csharp
// Program.cs
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents(options =>
    {
        options.MaxBufferedUnacknowledgedRenderBatches = 10;
    });

builder.Services.AddSignalR(options =>
{
    options.MaximumReceiveMessageSize = 64 * 1024; // 64 KB
});
```

---

## Input Sanitization Patterns

### SanitizedMarkup Component (Complete)

See the XSS Prevention section above for the full `SanitizedMarkup.razor` implementation. Use it anywhere user-generated HTML must be rendered.

### File Upload Validation

File uploads have additional validation concerns: MIME type spoofing, path traversal, and excessively large files. For full file upload patterns including size limits and extension allowlists, see `10-event-handling-performance.md`.

Key rules:
- **Never trust the file name** from `IBrowserFile.Name` — sanitize or replace it entirely
- **Validate by content signature (magic bytes)**, not by extension alone
- **Enforce size limits** via `IBrowserFile.OpenReadStream(maxAllowedSize)` — this throws if the file exceeds the limit
- **Store outside wwwroot** to prevent direct web access to uploaded files

```razor
@* FileUpload.razor — enforce size and type *@
@code {
    private static readonly HashSet<string> AllowedTypes =
        ["image/jpeg", "image/png", "image/webp"];

    private const long MaxFileSize = 5 * 1024 * 1024; // 5 MB

    private async Task HandleFile(InputFileChangeEventArgs e)
    {
        var file = e.File;

        if (!AllowedTypes.Contains(file.ContentType))
        {
            errorMessage = "Only JPEG, PNG, and WebP images are allowed.";
            return;
        }

        // OpenReadStream throws if file exceeds maxAllowedSize
        await using var stream = file.OpenReadStream(MaxFileSize);
        var safeName = $"{Guid.NewGuid()}{Path.GetExtension(file.Name)}";
        // Write stream to secure storage, not wwwroot
        await storageService.SaveAsync(safeName, stream);
    }
}
```

---

## Common Mistakes

| Mistake | Symptom / Risk | Fix |
|---|---|---|
| Using `MarkupString` with unsanitized user input | Stored XSS: attacker executes arbitrary JS in other users' browsers | Always sanitize with `HtmlSanitizer` before wrapping in `MarkupString`; use `SanitizedMarkup` component |
| Omitting `<AntiforgeryToken />` in a plain `<form>` | `400 Bad Request` on submit, or token validation bypass if middleware is misconfigured | Add `<AntiforgeryToken />` as first child of every raw `<form method="post">` |
| No CSP header | Browser executes any injected script; no defense-in-depth | Add CSP middleware with directives appropriate for each render mode in use |
| Storing auth tokens in `localStorage` without understanding XSS exposure | Token theft via any XSS vector, including third-party scripts | Use `httpOnly` cookies or a BFF pattern; move tokens off the client entirely |
| Missing `wss:` in `connect-src` for Interactive Server | SignalR WebSocket blocked by CSP; app appears to load then hang | Add `connect-src 'self' wss:` to CSP |
| Missing `'wasm-unsafe-eval'` in `script-src` for WASM | WASM fails to load; browser console shows CSP violation | Add `script-src 'self' 'wasm-unsafe-eval'` |
| No SignalR connection limits | Single authenticated user can open many circuits or send large messages, exhausting server memory | Set `MaximumParallelInvocationsPerClient`, `MaximumReceiveMessageSize`; apply rate limiting to hub endpoint |
| Trusting `IBrowserFile.Name` or `ContentType` for file validation | Path traversal, MIME type spoofing, unexpected file storage locations | Replace the file name with a generated GUID; validate by magic bytes; enforce size via `OpenReadStream(maxAllowedSize)` |
| Passing user-controlled strings to JS `innerHTML` via interop | DOM-based XSS | Use `textContent` in JS, or sanitize the string server-side before passing it to JS |
| Calling `[ValidateAntiForgeryToken]`-less API endpoints from cookie-authenticated WASM | CSRF possible if endpoint performs state-changing operations | Add antiforgery validation or switch to bearer token auth for APIs called from WASM |
