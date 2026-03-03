# Cross-Platform & Platform Integration

## Supported Platforms

| Platform | Backend | Renderer | Status |
|----------|---------|----------|--------|
| Windows | Win32 | Skia | Full support |
| macOS | Cocoa | Skia | Full support |
| Linux X11 | X11 | Skia | Full support |
| Linux Wayland | Wayland | Skia | Experimental |
| iOS | UIKit | Skia | Full support |
| Android | Android | Skia | Full support |
| Browser | WASM | Skia | Full support |

Avalonia renders everything via Skia, so your UI looks **identical** across platforms. Platform-specific behavior is limited to window chrome, file dialogs, and input handling.

## Platform Detection

```csharp
if (OperatingSystem.IsWindows())
    // Windows-specific code
else if (OperatingSystem.IsMacOS())
    // macOS-specific code
else if (OperatingSystem.IsLinux())
    // Linux-specific code

// For mobile
if (OperatingSystem.IsAndroid())
    // Android-specific code
else if (OperatingSystem.IsIOS())
    // iOS-specific code
```

**Never** use `RuntimeInformation.IsOSPlatform()` for this -- `OperatingSystem.Is*()` is the modern .NET approach and works with trimming.

## File Pickers (IStorageProvider)

Avalonia 11 replaced the old `OpenFileDialog` with the `IStorageProvider` API. It works cross-platform, including in the browser.

```csharp
// Get the storage provider from the TopLevel (usually your Window)
var topLevel = TopLevel.GetTopLevel(this);
var storageProvider = topLevel!.StorageProvider;
```

### Open File

```csharp
var files = await storageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
{
    Title = "Select a File",
    AllowMultiple = false,
    FileTypeFilter = new[]
    {
        new FilePickerFileType("Text Files") { Patterns = new[] { "*.txt", "*.md" } },
        new FilePickerFileType("All Files") { Patterns = new[] { "*.*" } }
    }
});

if (files.Count > 0)
{
    var file = files[0];
    await using var stream = await file.OpenReadAsync();
    using var reader = new StreamReader(stream);
    var content = await reader.ReadToEndAsync();
}
```

### Save File

```csharp
var file = await storageProvider.SaveFilePickerAsync(new FilePickerSaveOptions
{
    Title = "Save Document",
    SuggestedFileName = "document.txt",
    DefaultExtension = "txt",
    FileTypeChoices = new[]
    {
        new FilePickerFileType("Text Files") { Patterns = new[] { "*.txt" } }
    }
});

if (file != null)
{
    await using var stream = await file.OpenWriteAsync();
    await using var writer = new StreamWriter(stream);
    await writer.WriteAsync("File contents here");
}
```

### Open Folder

```csharp
var folders = await storageProvider.OpenFolderPickerAsync(new FolderPickerOpenOptions
{
    Title = "Select Output Folder",
    AllowMultiple = false
});

if (folders.Count > 0)
{
    var folder = folders[0];
    var path = folder.Path.LocalPath;  // Full path on desktop; URI on browser
}
```

## Clipboard

Access via `TopLevel.Clipboard`:

```csharp
var topLevel = TopLevel.GetTopLevel(this);
var clipboard = topLevel!.Clipboard!;

// Text
await clipboard.SetTextAsync("Copied text");
var text = await clipboard.GetTextAsync();

// Rich content via DataObject
var dataObject = new DataObject();
dataObject.Set(DataFormats.Text, "Plain text fallback");
dataObject.Set("text/html", "<b>Rich</b> content");
await clipboard.SetDataObjectAsync(dataObject);
```

## Drag and Drop

### Accepting Drops

```xml
<Border Background="LightGray" Padding="32"
        DragDrop.AllowDrop="True">
    <TextBlock Text="Drop files here" />
</Border>
```

```csharp
// In code-behind or attached behavior
border.AddHandler(DragDrop.DropEvent, OnDrop);
border.AddHandler(DragDrop.DragOverEvent, OnDragOver);

private void OnDragOver(object? sender, DragEventArgs e)
{
    // Control the cursor icon
    e.DragEffects = e.Data.Contains(DataFormats.Files)
        ? DragDropEffects.Copy
        : DragDropEffects.None;
}

private void OnDrop(object? sender, DragEventArgs e)
{
    if (e.Data.Contains(DataFormats.Files))
    {
        var files = e.Data.GetFiles();
        // Process dropped files
    }
    else if (e.Data.Contains(DataFormats.Text))
    {
        var text = e.Data.GetText();
    }
}
```

### Initiating a Drag

```csharp
private async void OnPointerPressed(object? sender, PointerPressedEventArgs e)
{
    var dataObject = new DataObject();
    dataObject.Set(DataFormats.Text, "Dragged content");

    var result = await DragDrop.DoDragDrop(e, dataObject, DragDropEffects.Copy);
    // result indicates what the drop target did
}
```

## System Tray

```csharp
// In App.axaml or programmatically
var trayIcon = new TrayIcon
{
    Icon = new WindowIcon(AssetLoader.Open(new Uri("avares://MyApp/Assets/icon.ico"))),
    ToolTipText = "My Application",
    Menu = new NativeMenu
    {
        new NativeMenuItem("Show Window") { Command = ShowWindowCommand },
        new NativeMenuItemSeparator(),
        new NativeMenuItem("Exit") { Command = ExitCommand }
    }
};

trayIcon.Clicked += (s, e) => MainWindow?.Show();
```

Or declaratively in `App.axaml`:

```xml
<TrayIcon.Icons>
    <TrayIcons>
        <TrayIcon Icon="avares://MyApp/Assets/icon.ico" ToolTipText="My App">
            <TrayIcon.Menu>
                <NativeMenu>
                    <NativeMenuItem Header="Show" Click="ShowWindow_Click" />
                    <NativeMenuItemSeparator />
                    <NativeMenuItem Header="Exit" Click="Exit_Click" />
                </NativeMenu>
            </TrayIcon.Menu>
        </TrayIcon>
    </TrayIcons>
</TrayIcon.Icons>
```

## Native Menu (macOS Menu Bar)

macOS expects a top-level native menu bar. Set it on the `Application`:

```xml
<Application.Styles>
    <FluentTheme />
</Application.Styles>

<NativeMenu.Menu>
    <NativeMenu>
        <NativeMenuItem Header="File">
            <NativeMenu>
                <NativeMenuItem Header="Open" Gesture="Cmd+O" Command="{Binding OpenCommand}" />
                <NativeMenuItem Header="Save" Gesture="Cmd+S" Command="{Binding SaveCommand}" />
                <NativeMenuItemSeparator />
                <NativeMenuItem Header="Exit" Gesture="Cmd+Q" Command="{Binding ExitCommand}" />
            </NativeMenu>
        </NativeMenuItem>
    </NativeMenu>
</NativeMenu.Menu>
```

**Key**: On Windows and Linux, `NativeMenu` renders as a standard menu bar at the top of the window. On macOS it integrates into the system menu bar.

## Window Customization

### Frameless / Extended Client Area

```xml
<Window ExtendClientAreaToDecorationsHint="True"
        ExtendClientAreaChromeHints="NoChrome"
        ExtendClientAreaTitleBarHeightHint="-1"
        SystemDecorations="Full">
    <!-- Your custom title bar goes here -->
</Window>
```

### System Decorations

| Value | Behavior |
|-------|----------|
| `Full` | Standard title bar and borders |
| `BorderOnly` | Borders but no title bar |
| `None` | No window chrome at all |

### Transparency

```xml
<Window TransparencyLevelHint="AcrylicBlur"
        Background="Transparent">
    <Panel>
        <ExperimentalAcrylicBorder Material="{StaticResource AcrylicMaterial}" />
        <!-- Content on top of acrylic -->
    </Panel>
</Window>
```

| TransparencyLevelHint | Effect |
|----------------------|--------|
| `None` | Opaque window |
| `Transparent` | Fully transparent background |
| `Blur` | Background blur (platform-dependent) |
| `AcrylicBlur` | Acrylic material effect |

**Note**: Transparency support varies by platform and compositor. **Always** provide a solid fallback.

## Multi-Monitor

```csharp
var screens = window.Screens.All;
foreach (var screen in screens)
{
    var bounds = screen.Bounds;           // Full screen area
    var workArea = screen.WorkingArea;    // Excludes taskbar
    var scaling = screen.Scaling;         // DPI scale factor (1.0, 1.25, 1.5, 2.0)
    var isPrimary = screen.IsPrimary;
}
```

## Asset Loading

Avalonia uses the `avares://` URI scheme to load embedded resources.

```csharp
// Load from the current assembly
var stream = AssetLoader.Open(new Uri("avares://MyApp/Assets/logo.png"));

// Load an image for display
var bitmap = new Bitmap(AssetLoader.Open(new Uri("avares://MyApp/Assets/photo.jpg")));
```

In the `.csproj`, ensure assets have the correct build action:

```xml
<ItemGroup>
    <AvaloniaResource Include="Assets\**" />
</ItemGroup>
```

In XAML:

```xml
<Image Source="avares://MyApp/Assets/logo.png" Width="64" Height="64" />
<Window Icon="avares://MyApp/Assets/icon.ico" />
```

## Keyboard Shortcuts

```csharp
// Platform-aware modifier: Cmd on macOS, Ctrl on Windows/Linux
var gesture = new KeyGesture(Key.S, KeyModifiers.Meta);  // Meta = Cmd on macOS, Ctrl on Windows/Linux
```

```xml
<!-- In XAML -->
<Button Content="Save" HotKey="Ctrl+S" Command="{Binding SaveCommand}" />

<!-- KeyBindings on a window or control -->
<Window.KeyBindings>
    <KeyBinding Gesture="Ctrl+N" Command="{Binding NewCommand}" />
    <KeyBinding Gesture="Ctrl+Shift+S" Command="{Binding SaveAsCommand}" />
    <KeyBinding Gesture="F5" Command="{Binding RefreshCommand}" />
</Window.KeyBindings>
```

## DPI and Scaling

Avalonia handles DPI scaling automatically. **Always** use device-independent units (DIPs) for layout -- never raw pixels.

```csharp
// Get the current render scaling factor
var scaling = TopLevel.GetTopLevel(this)!.RenderScaling;
// 1.0 = 96 DPI, 1.5 = 144 DPI, 2.0 = 192 DPI

// Convert DIPs to pixels when needed (rare)
var pixelWidth = (int)(dipWidth * scaling);
```

**Never** hard-code pixel values for layout. A `Width="200"` means 200 DIPs, which Avalonia scales correctly on all displays.

## Font Considerations

System font availability differs across platforms:

| Font | Windows | macOS | Linux |
|------|---------|-------|-------|
| Segoe UI | Yes | No | No |
| San Francisco | No | Yes | No |
| DejaVu Sans | Sometimes | No | Usually |

**Key**: Avalonia resolves `$Default` to the platform's default font. Use it instead of hard-coding font families:

```xml
<TextBlock FontFamily="{StaticResource DefaultFontFamily}" Text="Cross-platform text" />
```

For consistent rendering across all platforms, embed a font as an Avalonia resource and reference it explicitly:

```xml
<!-- App.axaml -->
<Application.Resources>
    <FontFamily x:Key="InterFont">avares://MyApp/Assets/Fonts#Inter</FontFamily>
</Application.Resources>

<!-- Usage -->
<TextBlock FontFamily="{StaticResource InterFont}" Text="Consistent everywhere" />
```
