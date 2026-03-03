# Framework Overview & Project Setup

## What Avalonia Is

Avalonia is a cross-platform .NET UI framework that renders pixel-identical interfaces on Windows, macOS, Linux, iOS, Android, and Browser (via WASM). It uses Skia for rendering instead of relying on platform-native widget toolkits, which means your UI looks the same everywhere. Think WPF concepts, but cross-platform with a modern styling system.

**Key distinction**: Avalonia is **not** a wrapper around native controls. It draws everything itself via Skia/SkiaSharp, giving you full control over every pixel.

## Avalonia vs WPF

If you're coming from WPF, this table covers the differences that will trip you up first:

| Feature | WPF | Avalonia |
|---|---|---|
| Markup extension | `.xaml` | `.axaml` |
| Default XMLNS | `http://schemas.microsoft.com/winfx/2006/xaml/presentation` | `https://github.com/avaloniaui` |
| Styling system | `Style` with `TargetType` + `Trigger` | CSS-like selectors + pseudo-classes |
| Rendering engine | DirectX (Windows only) | Skia (cross-platform) |
| Compiled bindings | Opt-in (`x:CompileBindings`) | Project-wide default supported |
| Platforms | Windows only | Windows, macOS, Linux, iOS, Android, Browser |
| DI approach | No built-in pattern | Manual via `IServiceCollection` in `App.axaml.cs` |
| Control theming | `ControlTemplate` + implicit styles | `ControlTheme` (v11+) |
| Triggers | `DataTrigger`, `EventTrigger`, `Trigger` | Pseudo-classes (`:pointerover`, `:pressed`) |
| Data templates | `DataTemplate` with `DataType` | `DataTemplate` with `DataType` (same concept) |
| Commands | `ICommand`, `RoutedCommand` | `ICommand` (use CommunityToolkit.Mvvm `RelayCommand`) |

## Project Templates

```bash
# Minimal app — no MVVM scaffolding
dotnet new avalonia.app -o MyApp

# MVVM app — includes ViewModels folder, ReactiveUI or CommunityToolkit.Mvvm
dotnet new avalonia.mvvm -o MyApp

# Cross-platform solution — desktop + mobile + browser projects
dotnet new avalonia.xplat -o MyApp
```

**Always prefer** `avalonia.mvvm` for real applications. The plain `avalonia.app` template is fine for spikes but lacks the structure you'll need.

## AppBuilder Setup

Every Avalonia app starts with the `AppBuilder` in `Program.cs`:

```csharp
using Avalonia;
using System;

class Program
{
    [STAThread]
    public static void Main(string[] args) => BuildAvaloniaApp()
        .StartWithClassicDesktopLifetime(args);

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()        // auto-detect OS and pick renderer
            .WithInterFont()            // bundles Inter as the default font
            .LogToTrace();              // logs to System.Diagnostics.Trace
}
```

**Never remove** `UsePlatformDetect()` unless you know exactly which platform backend you want. It handles Windows, macOS, and Linux automatically.

## .axaml File Conventions

Avalonia uses `.axaml` (Avalonia XAML) to avoid conflicts with WPF/UWP `.xaml` tooling. The root namespace is different from WPF:

```xml
<Window xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:vm="using:MyApp.ViewModels"
        x:Class="MyApp.Views.MainWindow"
        x:DataType="vm:MainWindowViewModel"
        Title="MyApp">
    <!-- x:DataType enables compiled bindings for this scope -->
</Window>
```

**Key points**:
- The Avalonia XMLNS is `https://github.com/avaloniaui`, not the Microsoft WPF namespace
- `x:DataType` sets the compiled binding context type for the scope
- Every `.axaml` file has a `.axaml.cs` code-behind counterpart

## Platform Targets and RIDs

Avalonia apps can target specific platforms using Runtime Identifiers:

| Platform | RID | Notes |
|---|---|---|
| Windows x64 | `win-x64` | Most common Windows target |
| Windows ARM | `win-arm64` | Surface Pro X, etc. |
| macOS Intel | `osx-x64` | Intel Macs |
| macOS Apple Silicon | `osx-arm64` | M1/M2/M3 Macs |
| Linux x64 | `linux-x64` | Ubuntu, Fedora, etc. |
| Linux ARM | `linux-arm64` | Raspberry Pi 4+, etc. |

```bash
# Publish self-contained for macOS Apple Silicon
dotnet publish -c Release -r osx-arm64 --self-contained

# Publish framework-dependent for Linux
dotnet publish -c Release -r linux-x64 --no-self-contained
```

## DI Registration with IServiceCollection

Avalonia has no built-in DI container, but the standard .NET `IServiceCollection` pattern works perfectly. Wire it up in `App.axaml.cs`:

```csharp
using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Microsoft.Extensions.DependencyInjection;

public partial class App : Application
{
    public static IServiceProvider Services { get; private set; } = null!;

    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        var services = new ServiceCollection();
        ConfigureServices(services);
        Services = services.BuildServiceProvider();

        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = new MainWindow
            {
                DataContext = Services.GetRequiredService<MainWindowViewModel>()
            };
        }

        base.OnFrameworkInitializationCompleted();
    }

    private static void ConfigureServices(IServiceCollection services)
    {
        // ViewModels
        services.AddTransient<MainWindowViewModel>();
        services.AddTransient<SettingsViewModel>();

        // Services
        services.AddSingleton<INavigationService, NavigationService>();
        services.AddSingleton<ISettingsService, SettingsService>();
        services.AddHttpClient<IApiClient, ApiClient>();
    }
}
```

**Access from ViewModels** by constructor injection. **Access from Views** (when needed) via `App.Services.GetRequiredService<T>()` — but prefer pushing dependencies through ViewModels instead.

## Project Structure

```
MyApp/
├── App.axaml                  # Application root, theme resources
├── App.axaml.cs               # DI setup, startup logic
├── Program.cs                 # AppBuilder entry point
├── Models/                    # Domain/data models
│   └── User.cs
├── ViewModels/                # MVVM ViewModels
│   ├── MainWindowViewModel.cs
│   └── SettingsViewModel.cs
├── Views/                     # .axaml views + code-behind
│   ├── MainWindow.axaml
│   ├── MainWindow.axaml.cs
│   └── SettingsView.axaml
├── Services/                  # Application services
│   ├── INavigationService.cs
│   └── NavigationService.cs
├── Converters/                # IValueConverter implementations
├── Assets/                    # Images, icons, fonts
└── Styles/                    # Shared .axaml style files
```

## Key NuGet Packages

| Package | Purpose |
|---|---|
| `Avalonia` | Core framework |
| `Avalonia.Desktop` | Desktop platform backend |
| `Avalonia.Themes.Fluent` | Fluent theme (recommended default) |
| `Avalonia.Themes.Simple` | Minimal theme, good base for custom designs |
| `Avalonia.Fonts.Inter` | Inter font family bundle |
| `CommunityToolkit.Mvvm` | Source-generated MVVM (`ObservableObject`, `RelayCommand`) |
| `Avalonia.Controls.DataGrid` | DataGrid control (separate package) |
| `Avalonia.Controls.TreeDataGrid` | High-performance hierarchical/flat data grid |
| `Avalonia.Diagnostics` | Dev tools overlay (Ctrl+F12 at runtime) |

```xml
<ItemGroup>
    <PackageReference Include="Avalonia" Version="11.*" />
    <PackageReference Include="Avalonia.Desktop" Version="11.*" />
    <PackageReference Include="Avalonia.Themes.Fluent" Version="11.*" />
    <PackageReference Include="Avalonia.Fonts.Inter" Version="11.*" />
    <PackageReference Include="CommunityToolkit.Mvvm" Version="8.*" />
    <!-- Dev tools — strip from release builds -->
    <PackageReference Include="Avalonia.Diagnostics" Version="11.*" Condition="'$(Configuration)'=='Debug'" />
</ItemGroup>
```

## Compiled Bindings Project-Wide

Compiled bindings catch binding errors at compile time instead of silently failing at runtime. **Always enable this**:

```xml
<!-- In your .csproj -->
<PropertyGroup>
    <AvaloniaUseCompiledBindingsByDefault>true</AvaloniaUseCompiledBindingsByDefault>
</PropertyGroup>
```

With this enabled, every binding in `.axaml` must resolve against the `x:DataType` in scope. If a binding path doesn't match a property on the data type, you get a **compile error** — not a silent runtime failure.

To opt out for a specific scope (e.g., when using dynamic data):

```xml
<StackPanel x:CompileBindings="False">
    <!-- Bindings here use reflection-based resolution -->
</StackPanel>
```

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Binding silently does nothing | No `x:DataType` set and compiled bindings enabled | Add `x:DataType="vm:YourViewModel"` to the root element |
| `InvalidOperationException` at startup | Missing `UsePlatformDetect()` in AppBuilder | Add `.UsePlatformDetect()` to the builder chain |
| App runs but window is blank | `AvaloniaXamlLoader.Load(this)` missing in `App.Initialize()` | Ensure `Initialize()` calls the loader |
| Styles don't apply | Wrong XMLNS (using WPF namespace) | Use `https://github.com/avaloniaui` |
| macOS app won't start | Missing `osx-arm64` or `osx-x64` RID in publish | Specify correct RID with `dotnet publish -r` |
