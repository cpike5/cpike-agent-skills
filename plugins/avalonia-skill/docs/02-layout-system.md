# Layout System

## Panel Types

Every layout starts with a panel. Pick the right one and you avoid fighting the framework.

| Panel | Behavior | When to Use |
|---|---|---|
| `StackPanel` | Stacks children vertically or horizontally | Lists, toolbars, simple forms |
| `Grid` | Row/column grid with sizing control | Most complex layouts |
| `DockPanel` | Docks children to edges, last fills remaining space | App shells (menu + sidebar + content) |
| `WrapPanel` | Flows children, wraps to next line | Tag clouds, button groups |
| `Canvas` | Absolute positioning via `Canvas.Left`/`Canvas.Top` | Diagrams, drawing surfaces |
| `UniformGrid` | Equal-sized cells in rows/columns | Calculators, grids of cards |
| `RelativePanel` | Position children relative to each other or panel edges | Adaptive layouts |
| `Panel` | Overlays all children on top of each other | Layered content, overlays |

## Grid — The Workhorse

Grid handles 80% of non-trivial layouts. Avalonia supports shorthand syntax that keeps your markup compact.

### Shorthand Syntax

```xml
<!-- Shorthand: comma-separated, inline -->
<Grid RowDefinitions="Auto,*,2*" ColumnDefinitions="200,*">
    <!-- Row 0: Auto-sized to content -->
    <!-- Row 1: Gets 1 share of remaining space -->
    <!-- Row 2: Gets 2 shares of remaining space -->
    <!-- Column 0: Fixed 200px -->
    <!-- Column 1: Takes remaining space -->
</Grid>

<!-- Verbose equivalent — use only when you need named rows or min/max constraints -->
<Grid>
    <Grid.RowDefinitions>
        <RowDefinition Height="Auto" />
        <RowDefinition Height="*" />
        <RowDefinition Height="2*" MinHeight="100" />
    </Grid.RowDefinitions>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="200" MinWidth="150" MaxWidth="300" />
        <ColumnDefinition Width="*" />
    </Grid.ColumnDefinitions>
</Grid>
```

### Row/Column Placement

```xml
<Grid RowDefinitions="Auto,*" ColumnDefinitions="200,*">
    <TextBlock Grid.Row="0" Grid.Column="0" Text="Sidebar Header" />
    <ListBox Grid.Row="1" Grid.Column="0" />

    <!-- Span across columns -->
    <TextBlock Grid.Row="0" Grid.Column="0" Grid.ColumnSpan="2" Text="Full-Width Header" />

    <!-- Span across rows -->
    <Border Grid.Row="0" Grid.Column="1" Grid.RowSpan="2" />
</Grid>
```

**Default is Row=0, Column=0** — omit them when placing content in the top-left cell.

### GridSplitter

Makes panes resizable at runtime:

```xml
<Grid ColumnDefinitions="200,Auto,*">
    <ListBox Grid.Column="0" />
    <!-- GridSplitter sits in its own column -->
    <GridSplitter Grid.Column="1" Width="4" ResizeDirection="Columns" />
    <ContentControl Grid.Column="2" />
</Grid>
```

**Always** give the `GridSplitter` its own `Auto`-sized row or column. Placing it inside a content cell causes erratic behavior.

## DockPanel

Children dock to edges in order. The **last child fills** the remaining space by default.

```xml
<DockPanel LastChildFill="True">
    <Menu DockPanel.Dock="Top" />
    <StatusBar DockPanel.Dock="Bottom" />
    <TreeView DockPanel.Dock="Left" Width="250" />
    <!-- Last child fills center -->
    <ContentControl />
</DockPanel>
```

Set `LastChildFill="False"` if you want the last child to dock normally instead of stretching.

## Sizing

| Property | Behavior |
|---|---|
| `Width="200"` | Fixed 200 device-independent pixels |
| `Width="NaN"` | Auto-size to content (same as not setting Width) |
| `MinWidth="100"` | Won't shrink below 100px |
| `MaxWidth="500"` | Won't grow beyond 500px |
| `Height="Auto"` | Same as NaN — size to content (Grid row/column syntax) |
| `Width="*"` | Proportional — only in Grid definitions |

**NaN is the default** for Width and Height. If a control has no explicit size, it sizes to its content or stretches to fill (depending on alignment).

## Margin and Padding

`Margin` is space **outside** the element's border. `Padding` is space **inside** the element's border.

Both use `Thickness` syntax:

| Syntax | Meaning |
|---|---|
| `Margin="10"` | 10px on all sides |
| `Margin="10,5"` | 10px left/right, 5px top/bottom |
| `Margin="10,5,10,5"` | Left, Top, Right, Bottom |

```xml
<!-- 8px external spacing, 16px internal padding -->
<Border Margin="8" Padding="16" Background="#1E1E1E" CornerRadius="8">
    <TextBlock Text="Padded content inside a bordered box" />
</Border>
```

## Alignment

| Property | Values | Default |
|---|---|---|
| `HorizontalAlignment` | `Left`, `Center`, `Right`, `Stretch` | `Stretch` |
| `VerticalAlignment` | `Top`, `Center`, `Bottom`, `Stretch` | `Stretch` |
| `HorizontalContentAlignment` | Same values | Depends on control |
| `VerticalContentAlignment` | Same values | Depends on control |

`HorizontalAlignment`/`VerticalAlignment` control how the element positions **itself** within its parent. `HorizontalContentAlignment`/`VerticalContentAlignment` control how the element positions **its content**.

```xml
<!-- Button stretches full width, but text is centered inside -->
<Button HorizontalAlignment="Stretch"
        HorizontalContentAlignment="Center"
        Content="Centered Text, Full-Width Button" />
```

## StackPanel.Spacing

Use `Spacing` instead of individual margins on children. It's cleaner and more maintainable:

```xml
<!-- Good: uniform spacing between items -->
<StackPanel Spacing="8">
    <TextBlock Text="First" />
    <TextBlock Text="Second" />
    <TextBlock Text="Third" />
</StackPanel>

<!-- Bad: margin on every child -->
<StackPanel>
    <TextBlock Text="First" Margin="0,0,0,8" />
    <TextBlock Text="Second" Margin="0,0,0,8" />
    <TextBlock Text="Third" />
</StackPanel>
```

## Spacing System

Stick to **4px increments** for all spacing values: 4, 8, 12, 16, 24, 32, 48. This ensures clean rendering at all display scale factors (100%, 125%, 150%, 200%) and creates visual consistency.

| Use Case | Recommended Value |
|---|---|
| Tight spacing (icon-to-text) | 4px |
| Default element spacing | 8px |
| Section spacing | 16px |
| Group/card spacing | 24px |
| Major section breaks | 32-48px |

## Responsive Patterns

Avalonia has **no CSS media queries**. Responsive behavior comes from layout panels and ViewModel-driven logic.

### Grid with Proportional Sizing

The simplest approach — proportional columns adapt to window size automatically:

```xml
<Grid ColumnDefinitions="*,2*">
    <!-- Sidebar always gets 1/3, content gets 2/3 -->
    <ListBox Grid.Column="0" />
    <ContentControl Grid.Column="1" />
</Grid>
```

### ViewModel-Driven Breakpoints

For layouts that need to structurally change at different sizes, bind to the window bounds:

```csharp
public partial class MainWindowViewModel : ObservableObject
{
    [ObservableProperty]
    private bool _isWideLayout;

    public void UpdateLayout(double windowWidth)
    {
        IsWideLayout = windowWidth > 800;
    }
}
```

```xml
<Panel>
    <!-- Show sidebar only in wide layout -->
    <Grid ColumnDefinitions="250,*" IsVisible="{Binding IsWideLayout}">
        <ListBox Grid.Column="0" />
        <ContentControl Grid.Column="1" />
    </Grid>

    <!-- Narrow layout: stacked, no sidebar -->
    <ContentControl IsVisible="{Binding !IsWideLayout}" />
</Panel>
```

## DPI Awareness

Avalonia handles DPI scaling automatically. All sizes are in **device-independent pixels** (DIPs). A `Width="100"` button will appear the same physical size on a 96 DPI monitor and a 192 DPI (200% scale) monitor — Avalonia renders it at 200 physical pixels on the latter.

**Never** calculate physical pixels manually unless you're doing custom rendering with Skia directly.

## Common Layouts

### Sidebar + Content

```xml
<DockPanel>
    <Menu DockPanel.Dock="Top">
        <MenuItem Header="File" />
    </Menu>
    <Grid ColumnDefinitions="250,Auto,*">
        <ListBox Grid.Column="0" />
        <GridSplitter Grid.Column="1" Width="4" />
        <ContentControl Grid.Column="2" Content="{Binding CurrentView}" />
    </Grid>
</DockPanel>
```

### Form Layout

```xml
<Grid RowDefinitions="Auto,Auto,Auto,Auto" ColumnDefinitions="Auto,*"
      Margin="16" VerticalAlignment="Top">
    <TextBlock Grid.Row="0" Grid.Column="0" Text="Name" VerticalAlignment="Center" Margin="0,0,12,8" />
    <TextBox Grid.Row="0" Grid.Column="1" Text="{Binding Name}" Margin="0,0,0,8" />

    <TextBlock Grid.Row="1" Grid.Column="0" Text="Email" VerticalAlignment="Center" Margin="0,0,12,8" />
    <TextBox Grid.Row="1" Grid.Column="1" Text="{Binding Email}" Margin="0,0,0,8" />

    <TextBlock Grid.Row="2" Grid.Column="0" Text="Role" VerticalAlignment="Center" Margin="0,0,12,8" />
    <ComboBox Grid.Row="2" Grid.Column="1" ItemsSource="{Binding Roles}" SelectedItem="{Binding SelectedRole}" Margin="0,0,0,8" />

    <!-- Buttons span both columns, right-aligned -->
    <StackPanel Grid.Row="3" Grid.Column="0" Grid.ColumnSpan="2"
                Orientation="Horizontal" HorizontalAlignment="Right" Spacing="8">
        <Button Content="Cancel" Command="{Binding CancelCommand}" />
        <Button Content="Save" Command="{Binding SaveCommand}" Classes="accent" />
    </StackPanel>
</Grid>
```

### Dashboard Grid

```xml
<UniformGrid Columns="3" Margin="16">
    <Border Margin="8" Padding="16" Background="#2D2D2D" CornerRadius="8">
        <StackPanel Spacing="4">
            <TextBlock Text="Users" FontSize="12" Foreground="#888" />
            <TextBlock Text="{Binding UserCount}" FontSize="28" FontWeight="Bold" />
        </StackPanel>
    </Border>
    <Border Margin="8" Padding="16" Background="#2D2D2D" CornerRadius="8">
        <StackPanel Spacing="4">
            <TextBlock Text="Revenue" FontSize="12" Foreground="#888" />
            <TextBlock Text="{Binding Revenue}" FontSize="28" FontWeight="Bold" />
        </StackPanel>
    </Border>
    <Border Margin="8" Padding="16" Background="#2D2D2D" CornerRadius="8">
        <StackPanel Spacing="4">
            <TextBlock Text="Orders" FontSize="12" Foreground="#888" />
            <TextBlock Text="{Binding OrderCount}" FontSize="28" FontWeight="Bold" />
        </StackPanel>
    </Border>
</UniformGrid>
```

## Anti-Patterns

- **Deeply nested panels (>5 levels)**: Each nesting level adds a layout pass. Flatten by using Grid with row/column spans instead of nesting StackPanels inside DockPanels inside Grids.
- **Excessive Auto sizing in Grids**: Every `Auto` row/column measures its content on each layout pass. Use `*` (proportional) when you don't need content-driven sizing.
- **Margin on every child instead of Spacing**: Use `StackPanel.Spacing` or `UniformGrid` margins. Individual margins are harder to maintain and easy to get inconsistent.
- **Canvas for general layout**: `Canvas` opts out of the layout system entirely. Reserve it for drawing surfaces and diagram editors, not forms or content.
