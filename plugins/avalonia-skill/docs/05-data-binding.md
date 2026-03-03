# Data Binding

## Standard Binding Syntax

Avalonia bindings look familiar if you know WPF, but the syntax has key differences. The basic form:

```xml
<TextBlock Text="{Binding UserName}" />
<TextBlock Text="{Binding User.Address.City}" />  <!-- dot-path for nested properties -->
```

## Binding Modes

| Mode | Description | Default For |
|------|-------------|-------------|
| `OneWay` | Source to target only | Most controls |
| `TwoWay` | Source and target sync both directions | `TextBox.Text`, `CheckBox.IsChecked`, `Slider.Value` |
| `OneTime` | Source to target once, then disconnects | Static display data |
| `OneWayToSource` | Target to source only | Rare, specialized scenarios |
| `Default` | Uses the mode defined by the property | Varies by property |

```xml
<TextBox Text="{Binding Name, Mode=TwoWay}" />
<TextBlock Text="{Binding CreatedDate, Mode=OneTime}" />
```

**Key**: You rarely need to specify `Mode` explicitly. Avalonia picks the right default for each property.

## String Format

Format bound values directly in markup:

```xml
<TextBlock Text="{Binding Price, StringFormat='Price: {0:C}'}" />
<TextBlock Text="{Binding Progress, StringFormat='{}{0:P0}'}" />  <!-- {} escapes leading { -->
<TextBlock Text="{Binding DueDate, StringFormat='Due: {0:yyyy-MM-dd}'}" />
```

**Always** wrap `StringFormat` values in single quotes when they contain special characters.

## FallbackValue and TargetNullValue

```xml
<!-- Shown when the binding path is invalid or source is missing -->
<TextBlock Text="{Binding MissingProp, FallbackValue='N/A'}" />

<!-- Shown when the bound value is null -->
<TextBlock Text="{Binding MiddleName, TargetNullValue='(none)'}" />
```

`FallbackValue` fires on binding errors. `TargetNullValue` fires when the value resolves to `null`. Use both together for defensive UI.

## Element Binding

Avalonia uses the `#` prefix to reference other named controls. **No `ElementName` property exists.**

```xml
<Slider x:Name="MySlider" Minimum="0" Maximum="100" />
<TextBlock Text="{Binding #MySlider.Value, StringFormat='Value: {0:F0}'}" />

<TextBox x:Name="SearchBox" />
<TextBlock Text="{Binding #SearchBox.Text}" />
```

## Self Binding

Reference the current control with `$self`:

```xml
<Border Width="200" Height="{Binding $self.Width}" />  <!-- square border -->
<TextBlock Text="{Binding $self.Tag}" />
```

## Parent / Ancestor Binding

Walk up the visual tree with `$parent`:

```xml
<!-- Immediate parent -->
<TextBlock Text="{Binding $parent.Tag}" />

<!-- Find ancestor by type -->
<TextBlock Text="{Binding $parent[Window].Title}" />
<TextBlock Text="{Binding $parent[ListBox].SelectedItem}" />

<!-- Index-based parent (0 = immediate, 1 = grandparent) -->
<TextBlock Text="{Binding $parent[1].DataContext.Name}" />
```

**Never** use `RelativeSource AncestorType` syntax from WPF. Use `$parent[Type]` instead.

## Compiled Bindings

Compiled bindings are the **recommended** approach for Avalonia 11. They give you compile-time errors, better performance, and AOT compatibility.

### Enable Per-File

```xml
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:vm="using:MyApp.ViewModels"
             x:DataType="vm:MainViewModel"
             x:CompileBindings="True">
    <!-- All bindings in this file are now compiled -->
    <TextBlock Text="{Binding UserName}" />
</UserControl>
```

### Enable Project-Wide (Recommended)

Add to your `.csproj`:

```xml
<PropertyGroup>
    <AvaloniaUseCompiledBindingsByDefault>true</AvaloniaUseCompiledBindingsByDefault>
</PropertyGroup>
```

With this setting, **every** AXAML file uses compiled bindings by default. You still need `x:DataType` on each file to tell the compiler what type to expect.

### Benefits

| Benefit | Details |
|---------|---------|
| Compile-time errors | Typos in property names caught at build |
| Performance | No reflection at runtime |
| AOT compatible | Works with NativeAOT and trimming |
| IntelliSense | Full autocomplete on binding paths |

### Opting Out

Sometimes you need reflection bindings (dynamic data, untyped scenarios):

```xml
<!-- Opt out for a single binding -->
<TextBlock Text="{ReflectionBinding DynamicProp}" />

<!-- Opt out for a section by nulling the DataType -->
<StackPanel x:DataType="{x:Null}">
    <TextBlock Text="{Binding SomeProp}" />  <!-- reflection binding here -->
</StackPanel>
```

## Value Converters

### IValueConverter

```csharp
public class BoolToColorConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        return value is true ? Brushes.Green : Brushes.Red;
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        throw new NotSupportedException(); // one-way only
    }
}
```

Register as a resource and use:

```xml
<UserControl.Resources>
    <local:BoolToColorConverter x:Key="BoolToColor" />
</UserControl.Resources>

<Border Background="{Binding IsActive, Converter={StaticResource BoolToColor}}" />
```

### IMultiValueConverter

Combine multiple values into one:

```csharp
public class FullNameConverter : IMultiValueConverter
{
    public object? Convert(IList<object?> values, Type targetType, object? parameter, CultureInfo culture)
    {
        if (values.Count == 2 && values[0] is string first && values[1] is string last)
            return $"{first} {last}";
        return null;
    }
}
```

```xml
<TextBlock>
    <TextBlock.Text>
        <MultiBinding Converter="{StaticResource FullName}">
            <Binding Path="FirstName" />
            <Binding Path="LastName" />
        </MultiBinding>
    </TextBlock.Text>
</TextBlock>
```

### Built-in Converters

Avalonia ships useful converters so you don't have to write boilerplate:

| Converter | Namespace | Purpose |
|-----------|-----------|---------|
| `BoolConverters.Not` | `Avalonia.Data.Converters` | Inverts a bool |
| `BoolConverters.And` | `Avalonia.Data.Converters` | Multi-value AND |
| `BoolConverters.Or` | `Avalonia.Data.Converters` | Multi-value OR |
| `StringConverters.IsNotNullOrEmpty` | `Avalonia.Data.Converters` | Returns true if string has content |
| `ObjectConverters.IsNull` | `Avalonia.Data.Converters` | Returns true if value is null |
| `ObjectConverters.IsNotNull` | `Avalonia.Data.Converters` | Returns true if value is not null |

```xml
<!-- Use directly without declaring a resource -->
<Button IsVisible="{Binding Name, Converter={x:Static StringConverters.IsNotNullOrEmpty}}" />
<Panel IsVisible="{Binding SelectedItem, Converter={x:Static ObjectConverters.IsNotNull}}" />
<CheckBox IsChecked="{Binding IsDisabled, Converter={x:Static BoolConverters.Not}}" />
```

## DataContext Flow

`DataContext` is inherited down the visual tree. Set it once at the top and everything below can bind to it.

```xml
<Window DataContext="{Binding MainViewModel}">
    <!-- All children inherit MainViewModel as their DataContext -->
    <StackPanel>
        <TextBlock Text="{Binding Title}" />  <!-- binds to MainViewModel.Title -->
    </StackPanel>
</Window>
```

Typically you set `DataContext` on the `Window` or top-level `UserControl`, either in AXAML or in code-behind:

```csharp
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        DataContext = new MainViewModel();
    }
}
```

### Design-Time DataContext

For AXAML previewer support:

```xml
<UserControl xmlns:d="https://github.com/avaloniaui/d"
             xmlns:vm="using:MyApp.ViewModels"
             d:DataContext="{d:DesignInstance vm:MainViewModel}">
    <!-- Previewer uses a default-constructed MainViewModel -->
</UserControl>
```

This only affects the designer. It has no runtime effect.

## WPF vs Avalonia Binding Comparison

| Feature | WPF | Avalonia |
|---------|-----|----------|
| Element binding | `{Binding ElementName=slider, Path=Value}` | `{Binding #slider.Value}` |
| Self binding | `{Binding RelativeSource={RelativeSource Self}, Path=Width}` | `{Binding $self.Width}` |
| Ancestor binding | `{Binding RelativeSource={RelativeSource AncestorType=Window}, Path=Title}` | `{Binding $parent[Window].Title}` |
| Templated parent | `{TemplateBinding Background}` | `{TemplateBinding Background}` (same) |
| Compiled bindings | x:Bind (UWP/WinUI only) | `x:CompileBindings="True"` + `x:DataType` |
| Fallback | `FallbackValue` | `FallbackValue` (same) |
| Null handling | `TargetNullValue` | `TargetNullValue` (same) |
| Converter parameter | `ConverterParameter` | `ConverterParameter` (same) |

**Key takeaway**: Avalonia's binding syntax is shorter and more readable. The `#`, `$self`, and `$parent` shortcuts replace verbose WPF constructs.
