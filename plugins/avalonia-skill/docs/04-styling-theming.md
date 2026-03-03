# Styling & Theming

## The CSS-Like System

Avalonia's styling is **fundamentally different from WPF**. If you try to use WPF patterns (TargetType + Triggers), you'll fight the framework. Avalonia uses CSS-like selectors and pseudo-classes.

## WPF vs Avalonia Styling

| Concept | WPF | Avalonia |
|---|---|---|
| Targeting | `TargetType="Button"` on `<Style>` | Selector string: `Button` |
| Hover state | `<Trigger Property="IsMouseOver" Value="True">` | Pseudo-class: `Button:pointerover` |
| Press state | `<Trigger Property="IsPressed" Value="True">` | Pseudo-class: `Button:pressed` |
| Class-based | No equivalent | `Button.primary` (like CSS classes) |
| Name-based | No direct style equivalent | `TextBlock#Header` |
| Nesting | Complex `DataTrigger` / `MultiTrigger` chains | `ListBox TextBlock` (descendant) |
| Control template override | Implicit `ControlTemplate` style | `ControlTheme` with `^` self-reference |

## Selector Syntax

Selectors are strings that target controls. They compose just like CSS.

### By Type

```xml
<Style Selector="Button">
    <Setter Property="Background" Value="#2D2D2D" />
    <Setter Property="Foreground" Value="White" />
</Style>
```

Targets **all** `Button` controls in scope.

### By Class

```xml
<!-- Style definition -->
<Style Selector="Button.primary">
    <Setter Property="Background" Value="#0078D4" />
    <Setter Property="Foreground" Value="White" />
</Style>

<Style Selector="Button.danger">
    <Setter Property="Background" Value="#D41A1A" />
    <Setter Property="Foreground" Value="White" />
</Style>
```

```xml
<!-- Usage — multiple classes separated by spaces -->
<Button Classes="primary" Content="Save" />
<Button Classes="danger" Content="Delete" />
<Button Classes="primary large" Content="Big Save" />
```

**Classes are additive** — a control can have multiple classes, and all matching styles apply.

### By Name

```xml
<Style Selector="TextBlock#PageTitle">
    <Setter Property="FontSize" Value="28" />
    <Setter Property="FontWeight" Value="Bold" />
</Style>
```

```xml
<TextBlock Name="PageTitle" Text="Dashboard" />
```

### Pseudo-Classes

Pseudo-classes target control states. They replace WPF triggers entirely.

```xml
<!-- Hover -->
<Style Selector="Button:pointerover">
    <Setter Property="Background" Value="#3D3D3D" />
</Style>

<!-- Pressed -->
<Style Selector="Button:pressed">
    <Setter Property="Background" Value="#1D1D1D" />
    <Setter Property="RenderTransform" Value="scale(0.98)" />
</Style>

<!-- Focused -->
<Style Selector="TextBox:focus">
    <Setter Property="BorderBrush" Value="#0078D4" />
    <Setter Property="BorderThickness" Value="2" />
</Style>

<!-- Disabled -->
<Style Selector="Button:disabled">
    <Setter Property="Opacity" Value="0.5" />
</Style>
```

### Full Pseudo-Class Reference

| Pseudo-Class | Triggers When |
|---|---|
| `:pointerover` | Pointer hovers over the control |
| `:pressed` | Control is being pressed/clicked |
| `:focus` | Control has keyboard focus |
| `:focus-within` | Control or any descendant has focus |
| `:disabled` | `IsEnabled="False"` |
| `:checked` | `IsChecked="True"` (toggles, checkboxes, radio buttons) |
| `:unchecked` | `IsChecked="False"` |
| `:indeterminate` | `IsChecked="{x:Null}"` (three-state) |
| `:selected` | Item is selected (in `ListBox`, `TabControl`, etc.) |
| `:empty` | Control has no content/children |
| `:nth-child(n)` | Matches the nth child (1-based). Supports `odd`, `even`, `2n+1`. |
| `:not(selector)` | Negation — matches controls that don't match the inner selector |

### Child and Descendant Selectors

```xml
<!-- Direct child: only TextBlocks that are immediate children of Button -->
<Style Selector="Button > TextBlock">
    <Setter Property="FontWeight" Value="SemiBold" />
</Style>

<!-- Descendant: any TextBlock anywhere inside a ListBox -->
<Style Selector="ListBox TextBlock">
    <Setter Property="FontSize" Value="14" />
</Style>

<!-- Combination: primary buttons when hovered, target the inner content presenter -->
<Style Selector="Button.primary:pointerover /template/ ContentPresenter">
    <Setter Property="Background" Value="#1A8AD4" />
</Style>
```

The `/template/` selector crosses into a control's template. Use it when you need to style internal template parts (like `ContentPresenter`, `Border`, or `ScrollViewer` inside a control).

### Nth-Child

```xml
<!-- Alternate row backgrounds in a list -->
<Style Selector="ListBoxItem:nth-child(odd)">
    <Setter Property="Background" Value="#1A1A1A" />
</Style>

<Style Selector="ListBoxItem:nth-child(even)">
    <Setter Property="Background" Value="#222222" />
</Style>
```

## Custom Pseudo-Classes

Create your own pseudo-classes for ViewModel-driven states:

```csharp
public class StatusIndicator : ContentControl
{
    // Define the pseudo-class constants
    private static readonly string PC_Online = ":online";
    private static readonly string PC_Offline = ":offline";

    public static readonly StyledProperty<bool> IsOnlineProperty =
        AvaloniaProperty.Register<StatusIndicator, bool>(nameof(IsOnline));

    public bool IsOnline
    {
        get => GetValue(IsOnlineProperty);
        set => SetValue(IsOnlineProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == IsOnlineProperty)
        {
            // Toggle pseudo-classes based on state
            PseudoClasses.Set(PC_Online, IsOnline);
            PseudoClasses.Set(PC_Offline, !IsOnline);
        }
    }
}
```

```xml
<Style Selector="local|StatusIndicator:online">
    <Setter Property="Background" Value="Green" />
</Style>
<Style Selector="local|StatusIndicator:offline">
    <Setter Property="Background" Value="Red" />
</Style>
```

## Dynamic Classes

Toggle classes from bindings:

```xml
<!-- Single dynamic class -->
<Border Classes.active="{Binding IsActive}">
    <!-- 'active' class is added when IsActive is true, removed when false -->
</Border>

<!-- Multiple dynamic classes -->
<Button Classes.selected="{Binding IsSelected}"
        Classes.highlighted="{Binding IsHighlighted}"
        Content="Dynamic" />
```

## Built-in Themes

### Fluent Theme (Recommended)

```xml
<!-- App.axaml -->
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="MyApp.App">
    <Application.Styles>
        <FluentTheme />
    </Application.Styles>
</Application>
```

Fluent supports a density option for compact UIs:

```xml
<Application.Styles>
    <FluentTheme DensityStyle="Compact" />
</Application.Styles>
```

| Density | Effect |
|---|---|
| `Normal` | Default spacing and sizing |
| `Compact` | Reduced padding, smaller controls. Good for data-heavy desktop apps. |

### Simple Theme

Minimal styling — good as a base for fully custom designs:

```xml
<Application.Styles>
    <SimpleTheme />
</Application.Styles>
```

## Light/Dark Mode

### Application-Level

```xml
<!-- Force dark mode -->
<Application RequestedThemeVariant="Dark">
    <Application.Styles>
        <FluentTheme />
    </Application.Styles>
</Application>
```

| Value | Behavior |
|---|---|
| `Default` | Follows OS preference |
| `Light` | Force light mode |
| `Dark` | Force dark mode |

### Runtime Switching

```csharp
// Switch theme at runtime
Application.Current!.RequestedThemeVariant = ThemeVariant.Dark;
Application.Current!.RequestedThemeVariant = ThemeVariant.Light;
Application.Current!.RequestedThemeVariant = ThemeVariant.Default; // follow OS
```

### ThemeVariantScope

Override the theme for a subtree without affecting the rest of the app:

```xml
<!-- Main app is dark, but this section uses light -->
<ThemeVariantScope RequestedThemeVariant="Light">
    <StackPanel Spacing="8">
        <TextBlock Text="This is light-themed" />
        <Button Content="Light Button" />
    </StackPanel>
</ThemeVariantScope>
```

## Resources

Define reusable values (colors, brushes, thicknesses) in resource dictionaries:

```xml
<Application.Resources>
    <Color x:Key="AccentColor">#0078D4</Color>
    <SolidColorBrush x:Key="AccentBrush" Color="{StaticResource AccentColor}" />
    <SolidColorBrush x:Key="SurfaceBrush" Color="#1E1E1E" />
    <CornerRadius x:Key="CardRadius">8</CornerRadius>
    <x:Double x:Key="DefaultFontSize">14</x:Double>
    <Thickness x:Key="CardPadding">16</Thickness>
</Application.Resources>
```

```xml
<!-- Usage -->
<Border Background="{DynamicResource SurfaceBrush}"
        CornerRadius="{StaticResource CardRadius}"
        Padding="{StaticResource CardPadding}">
    <TextBlock FontSize="{StaticResource DefaultFontSize}" />
</Border>
```

**`DynamicResource`** re-evaluates when the resource changes (theme switch). **`StaticResource`** resolves once at load time.

**Rule of thumb**: Use `DynamicResource` for any brush or color that should change with light/dark mode. Use `StaticResource` for constants like corner radii and thicknesses.

### Theme-Variant Resources

Define different values for light and dark modes:

```xml
<Application.Resources>
    <ResourceDictionary>
        <ResourceDictionary.ThemeDictionaries>
            <ResourceDictionary x:Key="Light">
                <SolidColorBrush x:Key="SurfaceBrush" Color="#FFFFFF" />
                <SolidColorBrush x:Key="TextBrush" Color="#1E1E1E" />
            </ResourceDictionary>
            <ResourceDictionary x:Key="Dark">
                <SolidColorBrush x:Key="SurfaceBrush" Color="#1E1E1E" />
                <SolidColorBrush x:Key="TextBrush" Color="#FFFFFF" />
            </ResourceDictionary>
        </ResourceDictionary.ThemeDictionaries>
    </ResourceDictionary>
</Application.Resources>
```

## ControlTheme (v11+)

`ControlTheme` replaces WPF's implicit control template styles. It defines the entire visual structure and styling of a control type.

### The `^` Selector

Inside a `ControlTheme`, the `^` selector refers to the **templated control itself** (the control being themed). This is the Avalonia equivalent of `TemplatedParent`.

### Full Custom Button ControlTheme

```xml
<ControlTheme x:Key="PillButton" TargetType="Button">
    <!-- Default setters — base state -->
    <Setter Property="Background" Value="#2D2D2D" />
    <Setter Property="Foreground" Value="White" />
    <Setter Property="Padding" Value="16,8" />
    <Setter Property="CornerRadius" Value="20" />
    <Setter Property="Cursor" Value="Hand" />
    <Setter Property="HorizontalContentAlignment" Value="Center" />

    <!-- Control template — defines visual tree -->
    <Setter Property="Template">
        <ControlTemplate>
            <Border Background="{TemplateBinding Background}"
                    CornerRadius="{TemplateBinding CornerRadius}"
                    Padding="{TemplateBinding Padding}"
                    BorderBrush="{TemplateBinding BorderBrush}"
                    BorderThickness="{TemplateBinding BorderThickness}">
                <ContentPresenter Content="{TemplateBinding Content}"
                                  ContentTemplate="{TemplateBinding ContentTemplate}"
                                  HorizontalContentAlignment="{TemplateBinding HorizontalContentAlignment}"
                                  VerticalContentAlignment="{TemplateBinding VerticalContentAlignment}" />
            </Border>
        </ControlTemplate>
    </Setter>

    <!-- Pseudo-class styles using ^ (self) selector -->
    <Style Selector="^:pointerover">
        <Setter Property="Background" Value="#3D3D3D" />
    </Style>

    <Style Selector="^:pressed">
        <Setter Property="Background" Value="#1A1A1A" />
        <Setter Property="RenderTransform" Value="scale(0.97)" />
    </Style>

    <Style Selector="^:disabled">
        <Setter Property="Opacity" Value="0.4" />
    </Style>

    <!-- Nested: style the ContentPresenter inside the template when focused -->
    <Style Selector="^:focus /template/ Border">
        <Setter Property="BorderBrush" Value="#0078D4" />
        <Setter Property="BorderThickness" Value="2" />
    </Style>
</ControlTheme>
```

### Applying a ControlTheme

```xml
<!-- Apply by key -->
<Button Theme="{StaticResource PillButton}" Content="Rounded" />

<!-- Make it the default for ALL Buttons (no x:Key) -->
<ControlTheme TargetType="Button">
    <!-- This becomes the implicit theme for Button -->
</ControlTheme>
```

**Named themes** (with `x:Key`) are applied explicitly via `Theme="{StaticResource ...}"`. **Unnamed themes** (no `x:Key`) become the implicit default for that control type.

## Common Styling Patterns

### Accent Color System

```xml
<Application.Resources>
    <Color x:Key="AccentBase">#0078D4</Color>
    <Color x:Key="AccentLight">#1A8AD4</Color>
    <Color x:Key="AccentDark">#005A9E</Color>
    <SolidColorBrush x:Key="AccentBrush" Color="{StaticResource AccentBase}" />
    <SolidColorBrush x:Key="AccentHoverBrush" Color="{StaticResource AccentLight}" />
    <SolidColorBrush x:Key="AccentPressedBrush" Color="{StaticResource AccentDark}" />
</Application.Resources>

<Style Selector="Button.accent">
    <Setter Property="Background" Value="{DynamicResource AccentBrush}" />
    <Setter Property="Foreground" Value="White" />
</Style>
<Style Selector="Button.accent:pointerover">
    <Setter Property="Background" Value="{DynamicResource AccentHoverBrush}" />
</Style>
<Style Selector="Button.accent:pressed">
    <Setter Property="Background" Value="{DynamicResource AccentPressedBrush}" />
</Style>
```

### Disabled State Pattern

```xml
<!-- Apply consistently to all interactive controls -->
<Style Selector="Button:disabled">
    <Setter Property="Opacity" Value="0.4" />
</Style>
<Style Selector="TextBox:disabled">
    <Setter Property="Opacity" Value="0.4" />
</Style>
<Style Selector="ComboBox:disabled">
    <Setter Property="Opacity" Value="0.4" />
</Style>
```

### External Style Files

Keep styles organized by splitting them into separate `.axaml` files:

```xml
<!-- Styles/ButtonStyles.axaml -->
<Styles xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Style Selector="Button.primary">
        <Setter Property="Background" Value="#0078D4" />
        <Setter Property="Foreground" Value="White" />
    </Style>
    <Style Selector="Button.primary:pointerover">
        <Setter Property="Background" Value="#1A8AD4" />
    </Style>
</Styles>
```

```xml
<!-- App.axaml — import the style file -->
<Application.Styles>
    <FluentTheme />
    <StyleInclude Source="avares://MyApp/Styles/ButtonStyles.axaml" />
</Application.Styles>
```

The `avares://` protocol references embedded Avalonia resources. The path is `avares://AssemblyName/Path/To/File.axaml`.

## Style Precedence

Styles apply in this order (later wins):

1. Theme defaults (Fluent/Simple)
2. Application-level styles (`App.axaml`)
3. Included style files (`StyleInclude`)
4. Window/UserControl-level styles
5. Local styles (on the control's parent or the control itself)
6. Inline property values (always win)

**Inline values always override styles.** If you set `Background="Red"` directly on a `Button`, no style selector will override it. Use classes and styles instead of inline values when you want the styling system to remain in control.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Style doesn't apply | Inline property value overrides style | Remove inline value, use a class-based style instead |
| Hover/press states don't work | Styling `Button` instead of `Button:pointerover` | Add pseudo-class selector for each state |
| Template parts unstyled | Missing `/template/` in selector | Use `Button:pointerover /template/ ContentPresenter` |
| Theme resources don't update | Used `StaticResource` for theme-aware brushes | Switch to `DynamicResource` |
| ControlTheme nested styles broken | Using type name instead of `^` inside ControlTheme | Replace `Button:pointerover` with `^:pointerover` inside the ControlTheme |
| Style file not found | Wrong `avares://` path | Check assembly name matches exactly, path uses forward slashes |
