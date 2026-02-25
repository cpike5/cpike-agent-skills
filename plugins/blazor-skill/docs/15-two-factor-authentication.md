# Two-Factor Authentication (TOTP)

## The Core Problem: QR Codes and Render Modes Don't Mix Naively

The default Blazor Identity scaffold generates 2FA setup pages as Static SSR. The moment you try to render a QR code, you face a choice: generate it server-side (works everywhere) or use a client-side JS library (breaks in Static SSR). Getting this wrong means either a blank QR code, a JavaScript error, or a page that silently fails to enable 2FA.

The second common failure is enabling 2FA without verifying the token first — the authenticator key is stored but the user never confirmed their app scanned it correctly.

---

## TOTP URI Format

Authenticator apps parse a `otpauth://` URI to configure a TOTP entry. Blazor Identity generates this URI to encode in the QR code.

```
otpauth://totp/{issuer}:{email}?secret={key}&issuer={issuer}&digits=6&period=30
```

| Parameter | Value | Purpose |
|---|---|---|
| `{issuer}` | App name (URL-encoded) | Label shown in the authenticator app |
| `{email}` | User's email (URL-encoded) | Account identifier in the app |
| `secret` | Base32-encoded shared key | The TOTP seed — keep this secret |
| `digits` | `6` | Code length (6 is standard) |
| `period` | `30` | Seconds each code is valid |

**The shared key** comes from `UserManager.GetAuthenticatorKeyAsync`. ASP.NET Identity generates and stores it — you only need to format it into the URI and encode it into the QR image.

Format the URI using `Uri.EscapeDataString` for both issuer and email:

```csharp
// Services/AuthenticatorUriService.cs
public static class AuthenticatorUriService
{
    public static string GenerateUri(string issuer, string email, string unformattedKey)
    {
        return $"otpauth://totp/{Uri.EscapeDataString(issuer)}:{Uri.EscapeDataString(email)}"
             + $"?secret={unformattedKey}&issuer={Uri.EscapeDataString(issuer)}&digits=6&period=30";
    }
}
```

---

## QR Code Generation — Two Approaches

### QRCoder (Server-Side, Recommended)

**NuGet**: `QRCoder`

Generates PNG bytes on the server, rendered as a base64 `data:image/png;base64,...` `<img>` tag. Works in all render modes including Static SSR because no JavaScript is involved.

```csharp
// Services/QrCodeService.cs
using QRCoder;

public static class QrCodeService
{
    public static string GeneratePngBase64(string content)
    {
        using var qrGenerator = new QRCodeGenerator();
        QRCodeData qrCodeData = qrGenerator.CreateQrCode(content, QRCodeGenerator.ECCLevel.Q);
        using var qrCode = new PngByteQRCode(qrCodeData);
        byte[] pngBytes = qrCode.GetGraphic(pixelsPerModule: 5);
        return Convert.ToBase64String(pngBytes);
    }
}
```

Render in Razor:

```razor
@* The base64 string is set during OnInitializedAsync *@
<img src="data:image/png;base64,@qrCodeBase64"
     alt="Authenticator QR code"
     width="200" height="200" />
```

### qrcodejs (Client-Side)

**Requires**: JS interop — only usable in Interactive Server or Interactive WASM render modes. Fails silently in Static SSR because `OnAfterRenderAsync` never fires.

CDN or local script reference in `App.razor` / the layout:

```html
<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
```

JS interop pattern:

```razor
@* Components/Pages/Account/EnableAuthenticator.razor — Interactive only *@
@inject IJSRuntime JS

<div id="qr-code-container"></div>

@code {
    private string? authenticatorUri;

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender && authenticatorUri is not null)
        {
            await JS.InvokeVoidAsync("generateQrCode",
                "qr-code-container", authenticatorUri);
        }
    }
}
```

```javascript
// wwwroot/js/qr.js
function generateQrCode(containerId, uri) {
    new QRCode(document.getElementById(containerId), {
        text: uri,
        width: 200,
        height: 200
    });
}
```

### Approach Comparison

| Approach | Render Mode Support | JS Dependency | Server Load | Recommendation |
|---|---|---|---|---|
| QRCoder (server PNG) | All modes (SSR, Server, WASM) | None | Minimal CPU on generation | **Preferred** |
| qrcodejs (client JS) | Interactive Server, WASM only | Required | None | Use only when SSR is ruled out |

---

## Authenticator Setup Flow

The setup follows seven steps. Each corresponds to a specific `UserManager` call.

1. **Generate the shared key** — call `GetAuthenticatorKeyAsync`. If it returns null, call `ResetAuthenticatorKeyAsync` first to create one.
2. **Format the TOTP URI** — combine issuer, email, and the key into the `otpauth://` URI.
3. **Display QR code and manual key** — show the QR image and the raw key formatted with spaces every 4 characters for manual entry fallback.
4. **User scans with authenticator app** — the app stores the TOTP entry.
5. **User enters 6-digit code** — submitted via a form.
6. **Verify the token** — call `VerifyTwoFactorTokenAsync` with the `TokenOptions.DefaultAuthenticatorProvider` provider name.
7. **Enable 2FA** — only after successful verification, call `SetTwoFactorEnabledAsync(user, true)`.

**Never skip step 6.** Enabling 2FA without verifying locks users out if their app scanned the wrong code.

---

## Complete EnableAuthenticator Page

Static SSR compatible. Uses QRCoder for QR image generation.

```razor
@* Components/Pages/Account/EnableAuthenticator.razor *@
@page "/Account/Manage/EnableAuthenticator"
@using Microsoft.AspNetCore.Identity
@using Microsoft.AspNetCore.Components.Authorization

@inject UserManager<ApplicationUser> UserManager
@inject SignInManager<ApplicationUser> SignInManager
@inject NavigationManager Navigation
@inject ILogger<EnableAuthenticator> Logger

<PageTitle>Configure Authenticator App</PageTitle>

<h2>Configure Authenticator App</h2>

@if (!string.IsNullOrEmpty(message))
{
    <div class="alert @(isError ? "alert-danger" : "alert-success")">@message</div>
}

@if (qrCodeBase64 is not null)
{
    <p>Scan the QR code below with your authenticator app, then enter the 6-digit code.</p>

    <img src="data:image/png;base64,@qrCodeBase64"
         alt="QR code for authenticator setup"
         width="200" height="200"
         class="mb-3" />

    <p>
        <strong>Manual entry key:</strong>
        <code>@formattedKey</code>
    </p>
}

<EditForm Model="Input" method="post" OnValidSubmit="OnValidSubmitAsync" FormName="EnableAuthenticator">
    <DataAnnotationsValidator />
    <ValidationSummary />

    <div class="mb-3">
        <label for="code" class="form-label">Verification Code</label>
        <InputText id="code"
                   @bind-Value="Input!.Code"
                   class="form-control"
                   autocomplete="one-time-code"
                   inputmode="numeric"
                   placeholder="6-digit code" />
        <ValidationMessage For="@(() => Input!.Code)" />
    </div>

    <button type="submit" class="btn btn-primary">Verify and Enable</button>
</EditForm>

@code {
    [CascadingParameter]
    private HttpContext HttpContext { get; set; } = default!;

    [SupplyParameterFromForm]
    private InputModel? Input { get; set; }

    private string? qrCodeBase64;
    private string? formattedKey;
    private string? message;
    private bool isError;

    protected override async Task OnInitializedAsync()
    {
        Input ??= new();

        var user = await UserManager.GetUserAsync(HttpContext.User);
        if (user is null)
        {
            Navigation.NavigateTo("/Account/Login", forceLoad: true);
            return;
        }

        // Retrieve or reset the authenticator key
        var unformattedKey = await UserManager.GetAuthenticatorKeyAsync(user);
        if (string.IsNullOrEmpty(unformattedKey))
        {
            await UserManager.ResetAuthenticatorKeyAsync(user);
            unformattedKey = await UserManager.GetAuthenticatorKeyAsync(user);
        }

        var email = await UserManager.GetEmailAsync(user) ?? string.Empty;
        const string issuer = "MyApp"; // Replace with your app name

        var uri = AuthenticatorUriService.GenerateUri(issuer, email, unformattedKey!);

        qrCodeBase64 = QrCodeService.GeneratePngBase64(uri);
        formattedKey = FormatKey(unformattedKey!);
    }

    private async Task OnValidSubmitAsync()
    {
        var user = await UserManager.GetUserAsync(HttpContext.User);
        if (user is null) return;

        // Strip spaces and hyphens the user might have typed
        var verificationCode = Input!.Code
            .Replace(" ", string.Empty)
            .Replace("-", string.Empty);

        var isValid = await UserManager.VerifyTwoFactorTokenAsync(
            user,
            UserManager.Options.Tokens.AuthenticatorTokenProvider,
            verificationCode);

        if (!isValid)
        {
            isError = true;
            message = "Verification code is invalid. Ensure your authenticator app is using the correct key.";
            return;
        }

        await UserManager.SetTwoFactorEnabledAsync(user, true);
        Logger.LogInformation("User {UserId} enabled 2FA.", user.Id);

        // Refresh sign-in to pick up the 2FA claim
        await SignInManager.RefreshSignInAsync(user);

        Navigation.NavigateTo("/Account/Manage/GenerateRecoveryCodes");
    }

    // Format key as groups of 4 characters: "ABCD EFGH IJKL ..."
    private static string FormatKey(string unformattedKey)
    {
        var result = new System.Text.StringBuilder();
        int currentPosition = 0;
        while (currentPosition + 4 < unformattedKey.Length)
        {
            result.Append(unformattedKey.AsSpan(currentPosition, 4)).Append(' ');
            currentPosition += 4;
        }
        if (currentPosition < unformattedKey.Length)
            result.Append(unformattedKey.AsSpan(currentPosition));

        return result.ToString().ToLowerInvariant();
    }

    public sealed class InputModel
    {
        [Required]
        [StringLength(7, ErrorMessage = "The code must be 6 or 7 digits.", MinimumLength = 6)]
        [DataType(DataType.Text)]
        [Display(Name = "Verification Code")]
        public string Code { get; set; } = string.Empty;
    }
}
```

---

## Recovery Codes

Recovery codes are single-use backup codes that let a user access their account if they lose their authenticator device. Generate them immediately after enabling 2FA.

### Generation

```csharp
// GenerateRecoveryCodes.razor — @code block
private IEnumerable<string>? recoveryCodes;

protected override async Task OnInitializedAsync()
{
    var user = await UserManager.GetUserAsync(HttpContext.User);
    if (user is null) return;

    // Generates 10 new codes; all previous codes are invalidated
    recoveryCodes = await UserManager.GenerateNewTwoFactorRecoveryCodesAsync(user, count: 10);
}
```

### Display Pattern — Show Once

```razor
@* Components/Pages/Account/GenerateRecoveryCodes.razor *@
@page "/Account/Manage/GenerateRecoveryCodes"

<div class="alert alert-warning">
    <strong>Save these codes now.</strong> They will not be shown again.
    Each code can only be used once. Store them in a secure password manager.
</div>

@if (recoveryCodes is not null)
{
    <div class="recovery-codes font-monospace">
        @foreach (var code in recoveryCodes)
        {
            <div>@code</div>
        }
    </div>
}
```

Key properties of recovery codes:

- **Single-use**: Each code is consumed on use and cannot be reused.
- **Regenerating invalidates all previous codes** — inform the user before they click regenerate.
- **Do not store in the component state beyond this page load** — the page is the display boundary; after navigation the codes are gone.
- **Count**: The Blazor Identity scaffold defaults to 10. Adjust for your threat model.

---

## Render Mode Considerations

All Identity 2FA pages should remain **Static SSR**. The table below shows what works where and why.

| Feature | Static SSR | Interactive Server | Interactive WASM |
|---|---|---|---|
| QR code display (QRCoder) | Yes | Yes | Yes (server renders PNG) |
| QR code display (qrcodejs) | **No** — JS never runs | Yes | Yes |
| Code verification form | Yes — via HTTP POST | Yes — via SignalR | Yes — via HTTP |
| `HttpContext` access | Yes | **No** | **No** |
| `UserManager` access | Yes (scoped per request) | Yes (scoped per circuit) | **No** (client-side has no DB) |
| Cookie write after enable | Yes | Requires `forceLoad` redirect | Requires API call |
| Page protection with `[Authorize]` | Yes — 302 redirect | Yes — component not rendered | Yes — component not rendered |

**The practical rule**: Keep 2FA pages at Static SSR (no `@rendermode` directive). WASM apps should expose a server API and call it from the client — the TOTP verification and `UserManager` calls stay on the server.

---

## Common Mistakes

| Mistake | Symptom / Risk | Fix |
|---|---|---|
| Not calling `ResetAuthenticatorKeyAsync` when `GetAuthenticatorKeyAsync` returns null | QR code URI has an empty `secret` parameter; authenticator app shows an error | Always check for null and reset before generating the URI |
| Enabling 2FA without calling `VerifyTwoFactorTokenAsync` first | User confirms setup but their app has the wrong code; they are locked out on next login | Only call `SetTwoFactorEnabledAsync` after a successful token verification |
| Using qrcodejs or other client-side QR libraries on a Static SSR page | QR container is empty; no error in console | Switch to QRCoder (server-side PNG) or change the page to Interactive Server |
| Not showing a manual entry key fallback alongside the QR code | Users with screen readers or accessibility tools cannot set up 2FA | Always display `formattedKey` in a `<code>` block next to the QR image |
| Not redirecting to recovery code generation after enabling 2FA | Users have no recovery path if they lose their device | After `SetTwoFactorEnabledAsync`, redirect to the recovery code display page |
| Regenerating recovery codes without warning the user | Old codes stop working silently; support requests spike | Show a confirmation page explaining that all existing codes will be invalidated |
| Storing the formatted authenticator key in `localStorage` or a cookie | Key leaks to client storage; attacker can derive TOTP codes | The key lives only in the server database; never write it to client-accessible storage |

---

See `11-authentication-authorization.md` for HttpContext vs render mode constraints that apply to all Identity pages.
See `03-forms-validation.md` for `EditForm`, `[SupplyParameterFromForm]`, and `FormName` requirements on SSR pages.
See `06-js-interop.md` for `OnAfterRenderAsync` and module isolation patterns if using the qrcodejs approach.
