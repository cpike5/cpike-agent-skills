# Dependency Injection

## Service Lifetimes

| Lifetime | Blazor Server | Blazor WASM |
|---|---|---|
| **Singleton** | Shared across ALL users/circuits. Dangerous for user state. | One instance per browser tab (safe). |
| **Scoped** | Scoped to the circuit (SignalR connection). Recommended for user state. | Treated as Singleton (WASM has no scope concept). |
| **Transient** | New instance per request. **Avoid disposable transients** — DI container holds refs, causing memory leaks. | Same issue — avoid disposable transients. |

### Scoped Lifetime Details (Server)
- Created when circuit is established
- NOT recreated during in-app navigation
- Recreated on: browser refresh, new tab, close/reopen

### CRITICAL Rule
**Never use Singleton for user-specific state on Blazor Server** — it leaks between users.

## @inject Directive

```razor
@inject NavigationManager Navigation
@inject IWeatherService WeatherService
@inject ILogger<WeatherPage> Logger
```

**Warning**: In Blazor Web Apps, avoid injecting services in the top-level `Components/_Imports.razor` — it resolves two instances. Use `Components/Pages/_Imports.razor` instead.

## [Inject] Attribute

Use in code-behind files and base classes.

```csharp
// Counter.razor.cs
public partial class Counter
{
    [Inject]
    private NavigationManager Navigation { get; set; } = default!;

    [Inject]
    private IWeatherService WeatherService { get; set; } = default!;
}
```

Base class injection:
```csharp
public abstract class AppComponentBase : ComponentBase
{
    [Inject]
    protected NavigationManager Navigation { get; set; } = default!;
}
```

Primary constructor injection (C# 12):
```csharp
public partial class Counter(NavigationManager navigation, IWeatherService service)
{
    private void GoHome() => navigation.NavigateTo("/");
}
```

## OwningComponentBase

Creates a DI scope tied to the **component lifetime** (not the circuit). Use when you need a fresh scoped service per component instance (especially DbContext).

```razor
@inherits OwningComponentBase

@code {
    private IMyService myService = default!;

    protected override void OnInitialized()
    {
        myService = ScopedServices.GetRequiredService<IMyService>();
    }
}
```

Single-service shorthand:
```razor
@inherits OwningComponentBase<AppDbContext>

@* Service property is typed as AppDbContext, scoped to component *@
<p>Users: @Service.Users.Count()</p>
```

Key rules:
- Services resolved via `ScopedServices` are component-scoped
- Services via `@inject` on an `OwningComponentBase` are still circuit-scoped
- The component's scope is disposed when the component is destroyed

## Keyed Services (.NET 8+)

```csharp
// Registration
builder.Services.AddKeyedSingleton<IMessageService, EmailService>("email");
builder.Services.AddKeyedSingleton<IMessageService, SmsService>("sms");
```

```csharp
// Injection — @inject does NOT support keys, use [Inject]
[Inject(Key = "email")]
public IMessageService EmailService { get; set; } = default!;
```

## HttpClient

| | Blazor Server | Blazor WASM |
|---|---|---|
| Default registration | Not registered | Scoped, preconfigured to origin |
| Transport | .NET HTTP stack | Browser Fetch API |
| CORS | Not subject | Subject to browser CORS |

### Named Clients
```csharp
builder.Services.AddHttpClient("WeatherAPI", client =>
    client.BaseAddress = new Uri("https://api.weather.example.com/"));
```

```razor
@inject IHttpClientFactory ClientFactory

@code {
    var client = ClientFactory.CreateClient("WeatherAPI");
    var data = await client.GetFromJsonAsync<MyData[]>("endpoint");
}
```

### Typed Clients
```csharp
public class ForecastClient(HttpClient http)
{
    public async Task<Forecast[]> GetAsync()
        => await http.GetFromJsonAsync<Forecast[]>("forecast") ?? [];
}
```

```csharp
builder.Services.AddHttpClient<ForecastClient>(client =>
    client.BaseAddress = new Uri("https://api.example.com/"));
```

### JSON Helpers
```csharp
var items = await Http.GetFromJsonAsync<Item[]>("api/items");
await Http.PostAsJsonAsync("api/items", newItem);
await Http.PutAsJsonAsync($"api/items/{id}", item);
await Http.DeleteAsync($"api/items/{id}");
```

### Disposal Rules
- Always dispose `HttpResponseMessage` and `HttpRequestMessage` (use `using`)
- Never dispose `HttpClient` from `ClientFactory.CreateClient()`
