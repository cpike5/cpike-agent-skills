# Testing & Deployment

Test ViewModels with xUnit, Views with Avalonia.Headless, and ship cross-platform with dotnet publish, Velopack, or platform-specific packaging tools.

---

## ViewModel Unit Testing

ViewModels are plain C# classes. Test them with xUnit, mock dependencies with NSubstitute or Moq.

```
dotnet add package xunit
dotnet add package NSubstitute
dotnet add package FluentAssertions
```

### Testing Commands

```csharp
public class DataViewModelTests
{
    private readonly IDataService _dataService = Substitute.For<IDataService>();
    private readonly DataViewModel _sut;

    public DataViewModelTests()
    {
        _sut = new DataViewModel(_dataService);
    }

    [Fact]
    public async Task LoadCommand_PopulatesItems()
    {
        // Arrange
        var expected = new List<Item>
        {
            new("Item 1"),
            new("Item 2")
        };
        _dataService.GetItemsAsync(Arg.Any<CancellationToken>())
            .Returns(expected);

        // Act
        await _sut.LoadCommand.ExecuteAsync(null);

        // Assert
        _sut.Items.Should().HaveCount(2);
        _sut.Items.Should().BeEquivalentTo(expected);
        _sut.ErrorMessage.Should().BeNull();
    }

    [Fact]
    public async Task LoadCommand_SetsErrorMessage_OnFailure()
    {
        _dataService.GetItemsAsync(Arg.Any<CancellationToken>())
            .ThrowsAsync(new HttpRequestException("Connection refused"));

        await _sut.LoadCommand.ExecuteAsync(null);

        _sut.ErrorMessage.Should().NotBeNullOrEmpty();
        _sut.Items.Should().BeEmpty();
    }

    [Fact]
    public async Task LoadCommand_SetsIsLoading_DuringExecution()
    {
        var tcs = new TaskCompletionSource<List<Item>>();
        _dataService.GetItemsAsync(Arg.Any<CancellationToken>())
            .Returns(tcs.Task);

        var task = _sut.LoadCommand.ExecuteAsync(null);

        _sut.IsLoading.Should().BeTrue();  // still running

        tcs.SetResult(new List<Item>());
        await task;

        _sut.IsLoading.Should().BeFalse();  // completed
    }
}
```

### Testing Validation

```csharp
public class UserFormViewModelTests
{
    private readonly UserFormViewModel _sut;

    public UserFormViewModelTests()
    {
        _sut = new UserFormViewModel(Substitute.For<IUserService>());
    }

    [Fact]
    public void EmptyName_HasValidationError()
    {
        _sut.Name = "";
        _sut.ValidateAllProperties();

        _sut.HasErrors.Should().BeTrue();
        _sut.GetErrors(nameof(_sut.Name)).Should().NotBeEmpty();
    }

    [Fact]
    public void ValidForm_HasNoErrors()
    {
        _sut.Name = "Alice";
        _sut.Email = "alice@example.com";
        _sut.Age = 30;
        _sut.Phone = "+1 555 1234";

        _sut.ValidateAllProperties();

        _sut.HasErrors.Should().BeFalse();
    }
}
```

### Testing Property Changed Notifications

```csharp
[Fact]
public void Setting_Name_RaisesPropertyChanged()
{
    using var monitor = _sut.Monitor();

    _sut.Name = "Bob";

    monitor.Should().RaisePropertyChangeFor(x => x.Name);
}
```

---

## UI Testing with Avalonia.Headless

Run UI tests in memory without creating visible windows. **Requires** the `Avalonia.Headless.XUnit` package.

```
dotnet add package Avalonia.Headless.XUnit
```

### Setup

```csharp
[assembly: AvaloniaTestApplication(typeof(TestAppBuilder))]

public class TestAppBuilder
{
    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UseHeadless(new AvaloniaHeadlessPlatformOptions());
}
```

### Headless Test Example

```csharp
public class MainWindowTests
{
    [AvaloniaTest]
    public void SearchBox_Appears_OnLoad()
    {
        var window = new MainWindow
        {
            DataContext = new MainViewModel()
        };
        window.Show();

        var searchBox = window.FindControl<TextBox>("SearchBox");
        searchBox.Should().NotBeNull();
        searchBox!.IsVisible.Should().BeTrue();
    }

    [AvaloniaTest]
    public void ClickButton_InvokesCommand()
    {
        var vm = new MainViewModel();
        var window = new MainWindow { DataContext = vm };
        window.Show();

        var button = window.FindControl<Button>("SubmitButton");
        button!.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

        // Assert expected state change on ViewModel
        vm.IsSubmitted.Should().BeTrue();
    }
}
```

### Snapshot Testing with Verify

Capture rendered output and compare against baselines.

```
dotnet add package Verify.Avalonia
```

```csharp
[AvaloniaTest]
public Task MainWindow_MatchesSnapshot()
{
    var window = new MainWindow { DataContext = new MainViewModel() };
    window.Show();
    return Verify(window);
}
```

---

## Publishing Commands

### Core Options

| Flag | Effect |
|------|--------|
| `--self-contained` | Bundles .NET runtime. No runtime install needed on target. |
| `--no-self-contained` | Framework-dependent. Smaller output, requires runtime on target. |
| `-p:PublishSingleFile=true` | Single executable (excludes native libs on some platforms). |
| `-p:PublishTrimmed=true` | Removes unused IL. Reduces size. Requires testing. |
| `-p:PublishAot=true` | Ahead-of-time compilation. Fastest startup, no JIT. |

### Common Publish Commands

```bash
# Framework-dependent (smallest, requires .NET on target)
dotnet publish -c Release --no-self-contained -r win-x64

# Self-contained single file
dotnet publish -c Release --self-contained -r win-x64 -p:PublishSingleFile=true

# Trimmed self-contained (smaller, test thoroughly)
dotnet publish -c Release --self-contained -r win-x64 -p:PublishSingleFile=true -p:PublishTrimmed=true

# NativeAOT (fastest startup, see AOT section)
dotnet publish -c Release -r win-x64 -p:PublishAot=true
```

### Common Runtime Identifiers

| RID | Target |
|-----|--------|
| `win-x64` | Windows x86-64 |
| `win-arm64` | Windows ARM64 |
| `osx-x64` | macOS Intel |
| `osx-arm64` | macOS Apple Silicon |
| `linux-x64` | Linux x86-64 |
| `linux-arm64` | Linux ARM64 |

---

## Windows Packaging

### MSIX

Microsoft's modern packaging format. Supports auto-update via App Installer, sandboxed install, clean uninstall.

### Velopack (Recommended for Auto-Updates)

Velopack provides installer creation and auto-update for Windows, macOS, and Linux.

```bash
# Install the CLI tool
dotnet tool install -g vpk

# Publish the app first
dotnet publish -c Release --self-contained -r win-x64 -o publish/win

# Pack into installer + update packages
vpk pack \
    --packId "MyApp" \
    --packVersion "1.0.0" \
    --packDir publish/win \
    --mainExe "MyApp.exe"
```

### Velopack Update Check in App

```csharp
using Velopack;

public partial class App : Application
{
    public override void OnFrameworkInitializationCompleted()
    {
        // Check for updates on startup
        _ = CheckForUpdatesAsync();
        base.OnFrameworkInitializationCompleted();
    }

    private async Task CheckForUpdatesAsync()
    {
        var mgr = new UpdateManager("https://releases.myapp.com");
        if (!mgr.IsInstalled) return;  // dev mode, skip

        var newVersion = await mgr.CheckForUpdatesAsync();
        if (newVersion is not null)
        {
            await mgr.DownloadUpdatesAsync(newVersion);
            // Apply on next restart, or prompt user
        }
    }
}
```

---

## macOS Packaging

### .app Bundle Structure

```
MyApp.app/
  Contents/
    Info.plist
    MacOS/
      MyApp          # main executable
    Resources/
      MyApp.icns     # app icon
```

### Info.plist (Minimum)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>MyApp</string>
    <key>CFBundleIdentifier</key>
    <string>com.mycompany.myapp</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleExecutable</key>
    <string>MyApp</string>
    <key>CFBundleIconFile</key>
    <string>MyApp.icns</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
</dict>
</plist>
```

### DMG Creation

```bash
# Create a DMG from the .app bundle
hdiutil create -volname "MyApp" \
    -srcfolder MyApp.app \
    -ov -format UDZO \
    MyApp-1.0.0.dmg
```

---

## Linux Packaging

### PupNet Deploy

PupNet Deploy generates AppImage, Flatpak, DEB, and RPM packages from a single configuration.

```bash
dotnet tool install -g KuiperZone.PupNet

# Generate AppImage
pupnet --kind appimage --runtime linux-x64

# Generate DEB package
pupnet --kind deb --runtime linux-x64
```

### Package Formats

| Format | Distribution Method | Auto-Update |
|--------|-------------------|-------------|
| AppImage | Single file download | Manual or AppImageUpdate |
| Flatpak | Flathub or self-hosted | Built-in via Flatpak |
| Snap | Snap Store | Built-in via snapd |
| DEB | APT repository or direct download | Via APT |

---

## NativeAOT Considerations

NativeAOT produces a fully native binary with no JIT. Fastest cold startup, smallest memory footprint. **Requires** compiled bindings and careful trimming.

### Required .csproj Settings

```xml
<PropertyGroup>
    <PublishAot>true</PublishAot>

    <!-- Required: AOT cannot resolve reflection-based bindings -->
    <AvaloniaUseCompiledBindingsByDefault>true</AvaloniaUseCompiledBindingsByDefault>

    <!-- Suppress trim warnings from Avalonia internals -->
    <SuppressTrimAnalysisWarnings>true</SuppressTrimAnalysisWarnings>
</PropertyGroup>
```

### AOT Restrictions

| Feature | AOT Compatible | Notes |
|---------|---------------|-------|
| Compiled bindings (`{CompiledBinding}`) | Yes | **Required** for AOT |
| Reflection bindings (`{Binding}`) | No | Will fail silently at runtime |
| `x:DataType` on views | Yes, required | Enables compiled bindings |
| CommunityToolkit.Mvvm source generators | Yes | Source gen, not reflection |
| `Activator.CreateInstance` in ViewLocator | No | Use DI-based view resolution |
| XAML `x:Type` with generics | No | Use non-generic alternatives |

**Always** test with AOT before shipping. Reflection-based code that works in JIT mode will fail silently or crash at runtime under AOT.

### Compiled Bindings in AXAML

```xml
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:vm="using:MyApp.ViewModels"
             x:DataType="vm:HomeViewModel">

    <!-- These are compiled bindings — AOT safe -->
    <TextBlock Text="{Binding Name}" />
    <Button Command="{Binding SaveCommand}" />
</UserControl>
```

The `x:DataType` attribute on the root element enables compile-time binding resolution for all child elements. Missing or incorrect `x:DataType` will cause build errors with `AvaloniaUseCompiledBindingsByDefault`, which is what you want.
