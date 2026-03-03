# Desktop UI Design Principles

Desktop apps are not web apps. They live in persistent windows, respond to keyboard and mouse, and coexist with the host operating system's design language. This doc covers the design decisions that make desktop UIs feel native, dense, and professional.

## Information Density

Desktop users sit at arm's length with large screens. They expect **more information per screen** than mobile or web users. Do not port a mobile layout to desktop -- it wastes space and forces unnecessary navigation.

- Show data inline instead of hiding it behind clicks
- Use multi-column layouts to fill horizontal space
- Reserve whitespace for **grouping**, not decoration
- Side panels, status bars, and toolbars are expected -- use them

## Spacing System

Use a **4px base unit**. Every spacing value should be a multiple of 4.

| Context | Spacing | Example |
|---------|---------|---------|
| Between related controls | 8px | Label above input |
| Between individual controls | 24px | Two text fields in a form |
| Between control groups | 48px | Form section to form section |
| Gutters (panel edges) | 12-24px | Content padding inside panels |
| Inline element spacing | 4-8px | Icon next to text |

```xml
<!-- Group spacing example -->
<StackPanel Spacing="24" Margin="24">
    <!-- Personal info group -->
    <StackPanel Spacing="8">
        <TextBlock Text="Personal Information" FontWeight="SemiBold" FontSize="16" />
        <TextBox Watermark="First Name" />
        <TextBox Watermark="Last Name" />
        <TextBox Watermark="Email" />
    </StackPanel>

    <!-- 48px gap between groups via additional margin -->
    <StackPanel Spacing="8" Margin="0,24,0,0">
        <TextBlock Text="Address" FontWeight="SemiBold" FontSize="16" />
        <TextBox Watermark="Street" />
        <TextBox Watermark="City" />
        <TextBox Watermark="Postal Code" />
    </StackPanel>
</StackPanel>
```

## Navigation Patterns

| Pattern | When to Use | Implementation |
|---------|-------------|----------------|
| Left Navigation | 5+ top-level sections, infrequent switching | `SplitView` with `NavigationView` |
| Top Navigation | All options visible at once, fewer than 7 items | `TabStrip` or custom horizontal panel |
| Tab View | User-managed documents or workspaces | `TabControl` with closeable tabs |
| Menu Bar | Deep command hierarchies (File, Edit, View, etc.) | `Menu` or `NativeMenu` |
| Breadcrumb | 3+ levels of hierarchical navigation | Custom breadcrumb control |
| Master-Detail | Frequent item switching with preview | `SplitView` or `Grid` with `ListBox` + `ContentControl` |

### Left Navigation

The most common desktop pattern. Use when you have 5+ sections and users switch infrequently.

```xml
<SplitView IsPaneOpen="{Binding IsPaneOpen}" DisplayMode="CompactInline"
           CompactPaneLength="48" OpenPaneLength="250">
    <SplitView.Pane>
        <StackPanel Spacing="4" Margin="0,8">
            <ListBox ItemsSource="{Binding NavItems}" SelectedItem="{Binding SelectedNav}">
                <ListBox.ItemTemplate>
                    <DataTemplate>
                        <StackPanel Orientation="Horizontal" Spacing="12">
                            <PathIcon Data="{Binding Icon}" Width="16" Height="16" />
                            <TextBlock Text="{Binding Label}" />
                        </StackPanel>
                    </DataTemplate>
                </ListBox.ItemTemplate>
            </ListBox>
        </StackPanel>
    </SplitView.Pane>
    <SplitView.Content>
        <TransitioningContentControl Content="{Binding CurrentPage}">
            <TransitioningContentControl.PageTransition>
                <CrossFade Duration="0:0:0.2" />
            </TransitioningContentControl.PageTransition>
        </TransitioningContentControl>
    </SplitView.Content>
</SplitView>
```

### Master-Detail

Best for lists where users frequently switch between items.

```xml
<Grid ColumnDefinitions="350,Auto,*">
    <ListBox Grid.Column="0" ItemsSource="{Binding Items}"
             SelectedItem="{Binding SelectedItem}" />
    <GridSplitter Grid.Column="1" Width="1" Background="Gray" />
    <ContentControl Grid.Column="2" Content="{Binding SelectedItem}" Margin="16" />
</Grid>
```

## Typography

Use the platform's default font. Avalonia resolves `$Default` to the system font on each platform.

### Type Ramp

| Level | Size | Line Height | Use For |
|-------|------|-------------|---------|
| Caption | 12px | 16px | Timestamps, secondary labels, footnotes |
| Body | 14px | 20px | Default text, descriptions, form labels |
| Subtitle | 20px | 28px | Section headers, card titles |
| Title | 28px | 36px | Page headers |
| Display | 68px | 92px | Hero numbers, splash screens |

```xml
<Application.Resources>
    <x:Double x:Key="CaptionFontSize">12</x:Double>
    <x:Double x:Key="BodyFontSize">14</x:Double>
    <x:Double x:Key="SubtitleFontSize">20</x:Double>
    <x:Double x:Key="TitleFontSize">28</x:Double>
    <x:Double x:Key="DisplayFontSize">68</x:Double>
</Application.Resources>
```

**Always** use sentence case for UI text. Title Case Looks Dated. ALL CAPS is for tiny labels only (status badges, column headers in data grids).

Keep body text to **50-60 characters per line**. Longer lines are hard to track. Use `MaxWidth` or column constraints to enforce this.

## Color and Theming

### Light/Dark Mode

Support both. Avalonia's `FluentTheme` handles this out of the box:

```xml
<FluentTheme />
<!-- Or force a mode -->
<FluentTheme RequestedThemeVariant="Dark" />
```

Detect and respond to theme changes:

```csharp
Application.Current!.ActualThemeVariantChanged += (s, e) =>
{
    var isDark = Application.Current.ActualThemeVariant == ThemeVariant.Dark;
};
```

### Accent Colors

Use accent colors **sparingly** -- primary actions, selected states, and active indicators only. **Never** use accent color for large surfaces.

### Material Surfaces

| Material | Use For | Avalonia |
|----------|---------|----------|
| Mica | Base window surface | `Background="{DynamicResource ApplicationPageBackgroundThemeBrush}"` |
| Acrylic | Flyouts, transient surfaces, side panels | `ExperimentalAcrylicBorder` |
| Solid | Cards, elevated surfaces | `Background="{DynamicResource CardBackgroundFillColorDefaultBrush}"` |

### Semantic Colors

| Meaning | Color | Use For |
|---------|-------|---------|
| Error | Red | Validation failures, destructive actions |
| Warning | Yellow/Amber | Non-blocking alerts |
| Success | Green | Completion confirmations |
| Info | Blue | Neutral information |

```xml
<Application.Resources>
    <Color x:Key="ErrorColor">#E74856</Color>
    <Color x:Key="WarningColor">#FCB827</Color>
    <Color x:Key="SuccessColor">#16C60C</Color>
    <Color x:Key="InfoColor">#0078D4</Color>
</Application.Resources>
```

## Form Layout

### Labels Above Inputs

**Always** place labels above inputs, not beside them. Side labels break on narrow windows and are harder to scan.

```xml
<StackPanel Spacing="16">
    <StackPanel Spacing="4">
        <TextBlock Text="Email address" FontSize="12" Foreground="Gray" />
        <TextBox Watermark="user@example.com" />
    </StackPanel>
    <StackPanel Spacing="4">
        <TextBlock Text="Password" FontSize="12" Foreground="Gray" />
        <TextBox PasswordChar="*" Watermark="Enter password" />
    </StackPanel>
</StackPanel>
```

Many Avalonia controls support `Header` directly:

```xml
<TextBox Header="Email address" Watermark="user@example.com" />
<ComboBox Header="Country" PlaceholderText="Select a country" />
```

### Required Field Indicators

```xml
<StackPanel Orientation="Horizontal" Spacing="2">
    <TextBlock Text="Email" FontSize="12" />
    <TextBlock Text="*" Foreground="Red" FontSize="12" />
</StackPanel>
```

### Multi-Column Forms

Use `Grid` with responsive column definitions:

```xml
<Grid ColumnDefinitions="*,24,*" RowDefinitions="Auto,16,Auto">
    <TextBox Grid.Row="0" Grid.Column="0" Header="First Name" />
    <TextBox Grid.Row="0" Grid.Column="2" Header="Last Name" />
    <TextBox Grid.Row="2" Grid.Column="0" Header="City" />
    <TextBox Grid.Row="2" Grid.Column="2" Header="Postal Code" />
</Grid>
```

### Submit Button State

**Always** disable the submit button until the form is valid:

```xml
<Button Content="Save" Command="{Binding SaveCommand}"
        Classes="accent"
        IsEnabled="{Binding IsFormValid}"
        HorizontalAlignment="Right" />
```

## Geometry

| Element | Corner Radius | Example |
|---------|---------------|---------|
| Top-level containers | 8px | Windows, flyouts, dialogs |
| In-page elements | 4px | Buttons, inputs, cards |
| Maximized windows | 0px | No rounding when maximized |
| Circular elements | 50% | Avatars, status dots |

```xml
<Style Selector="Button">
    <Setter Property="CornerRadius" Value="4" />
</Style>
<Style Selector="Border.card">
    <Setter Property="CornerRadius" Value="8" />
</Style>
```

## Data-Heavy Interfaces

| Control | Layout | Use For |
|---------|--------|---------|
| `ListBox` / `ListView` | Vertical list | Vertical scrolling, item selection |
| `ItemsRepeater` + `UniformGridLayout` | Tile grid | Card grids, image galleries |
| `DataGrid` | Table | Tabular data with sorting and editing |
| `TreeDataGrid` | Hierarchical table | File trees, nested data |

**Always** virtualize. If you have more than 50 items, use virtualized controls. `ListBox` virtualizes by default. `ItemsRepeater` virtualizes when inside a `ScrollViewer`.

## App Silhouettes

These are the standard desktop app layouts. Pick one and stick with it.

### Left Nav + Content

```
+-------+----------------------------+
| Nav   | Content                    |
|       |                            |
|       |                            |
|       |                            |
+-------+----------------------------+
```

The default for most productivity apps. `SplitView` with `NavigationView`.

### Top Nav + Content

```
+------------------------------------+
| Nav Item 1 | Nav Item 2 | Nav 3   |
+------------------------------------+
| Content                            |
|                                    |
+------------------------------------+
```

Best for apps with fewer than 7 top-level sections. `TabStrip` above a `ContentControl`.

### Menu Bar + CommandBar + Content

```
+------------------------------------+
| File  Edit  View  Help             |
+------------------------------------+
| [Toolbar buttons]                  |
+------------------------------------+
| Content                            |
|                                    |
+------------------------------------+
```

Traditional desktop apps (text editors, IDEs). `Menu` + `ToolBar` + content area.

### TabView + Content

```
+------------------------------------+
| [Tab 1] [Tab 2] [Tab 3] [+]       |
+------------------------------------+
| Tab content                        |
|                                    |
+------------------------------------+
```

Document-centric apps (browsers, editors). `TabControl` with dynamic tab management.

## Desktop vs Web Design

| Aspect | Desktop | Web |
|--------|---------|-----|
| Window lifecycle | Persistent, no page loads | Navigate between pages |
| Information density | High -- fill the screen | Lower -- scrolling is primary |
| Primary input | Keyboard + mouse | Touch-first on mobile, mixed on desktop |
| Navigation | Side nav, menu bar, tabs | Top nav, hamburger menu |
| Platform chrome | Title bar, system tray, taskbar | Browser chrome |
| State persistence | In-memory, instant | HTTP round-trips, local storage |
| Typography scale | Smaller base (14px body) | Larger base (16px body) |
| Drag and drop | Expected and common | Rare outside file upload |
| Keyboard shortcuts | Expected for all actions | Optional, power-user feature |
| Context menus | Right-click is standard | Uncommon, mobile-unfriendly |

**Key**: Desktop users expect **keyboard-first** interaction. Every action reachable by mouse should also be reachable by keyboard. Tab order, focus indicators, and shortcut keys are not optional.
