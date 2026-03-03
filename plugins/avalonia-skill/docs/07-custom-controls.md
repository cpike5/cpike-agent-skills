# Custom Controls

## UserControl vs TemplatedControl

| Criteria | UserControl | TemplatedControl |
|----------|-------------|------------------|
| Visual definition | AXAML file (composition) | ControlTheme in a resource |
| Restylable by consumers | No — layout is fixed | Yes — full template replacement |
| When to use | App-specific composite controls | Reusable library controls |
| Learning curve | Low | Medium-high |
| Has code-behind AXAML | Yes | No |
| Supports template parts | No | Yes (PART_ convention) |
| Typical examples | `AddressForm`, `SearchBar` | `RatingControl`, `TagInput` |

**Rule of thumb**: If the control is only used in your app, make it a `UserControl`. If it ships in a library or needs full restyling, make it a `TemplatedControl`.

## UserControl

### Basic UserControl

Create a composite control with its own AXAML and bindable properties.

```xml
<!-- LabeledInput.axaml -->
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="MyApp.Controls.LabeledInput">
    <StackPanel Spacing="4">
        <TextBlock Text="{Binding Label, RelativeSource={RelativeSource AncestorType=UserControl}}"
                   FontWeight="SemiBold" />
        <TextBox Text="{Binding Value, RelativeSource={RelativeSource AncestorType=UserControl}, Mode=TwoWay}"
                 Watermark="{Binding Placeholder, RelativeSource={RelativeSource AncestorType=UserControl}}" />
    </StackPanel>
</UserControl>
```

```csharp
// LabeledInput.axaml.cs
public partial class LabeledInput : UserControl
{
    public static readonly StyledProperty<string> LabelProperty =
        AvaloniaProperty.Register<LabeledInput, string>(nameof(Label), "Label");

    public static readonly StyledProperty<string> ValueProperty =
        AvaloniaProperty.Register<LabeledInput, string>(nameof(Value), string.Empty,
            defaultBindingMode: BindingMode.TwoWay);  // two-way by default for input controls

    public static readonly StyledProperty<string> PlaceholderProperty =
        AvaloniaProperty.Register<LabeledInput, string>(nameof(Placeholder), string.Empty);

    public string Label
    {
        get => GetValue(LabelProperty);
        set => SetValue(LabelProperty, value);
    }

    public string Value
    {
        get => GetValue(ValueProperty);
        set => SetValue(ValueProperty, value);
    }

    public string Placeholder
    {
        get => GetValue(PlaceholderProperty);
        set => SetValue(PlaceholderProperty, value);
    }

    public LabeledInput()
    {
        InitializeComponent();
    }
}
```

Usage:

```xml
<controls:LabeledInput Label="Email" Value="{Binding Email}" Placeholder="you@example.com" />
```

## TemplatedControl

A `TemplatedControl` has no AXAML file. Its visual is defined entirely through a `ControlTheme`, so consumers can restyle it.

### Step 1: The Control Class

```csharp
public class RatingControl : TemplatedControl
{
    public static readonly StyledProperty<int> ValueProperty =
        AvaloniaProperty.Register<RatingControl, int>(nameof(Value), 0,
            coerce: (_, v) => Math.Clamp(v, 0, 5));  // clamp between 0 and max

    public static readonly StyledProperty<int> MaximumProperty =
        AvaloniaProperty.Register<RatingControl, int>(nameof(Maximum), 5);

    public static readonly StyledProperty<bool> IsReadOnlyProperty =
        AvaloniaProperty.Register<RatingControl, bool>(nameof(IsReadOnly), false);

    public int Value
    {
        get => GetValue(ValueProperty);
        set => SetValue(ValueProperty, value);
    }

    public int Maximum
    {
        get => GetValue(MaximumProperty);
        set => SetValue(MaximumProperty, value);
    }

    public bool IsReadOnly
    {
        get => GetValue(IsReadOnlyProperty);
        set => SetValue(IsReadOnlyProperty, value);
    }

    // Template part — the panel containing star items
    private ItemsControl? _starItems;

    protected override void OnApplyTemplate(TemplateAppliedEventArgs e)
    {
        base.OnApplyTemplate(e);

        // Always null-check template parts
        _starItems = e.NameScope.Find<ItemsControl>("PART_Stars");
    }
}
```

### Step 2: The ControlTheme

Define the theme in a resource dictionary (typically `Themes/RatingControlTheme.axaml`):

```xml
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    xmlns:controls="using:MyApp.Controls">

    <ControlTheme x:Key="{x:Type controls:RatingControl}" TargetType="controls:RatingControl">
        <Setter Property="Template">
            <ControlTemplate>
                <Border Background="{TemplateBinding Background}"
                        BorderBrush="{TemplateBinding BorderBrush}"
                        BorderThickness="{TemplateBinding BorderThickness}"
                        CornerRadius="4"
                        Padding="{TemplateBinding Padding}">
                    <ItemsControl x:Name="PART_Stars">
                        <ItemsControl.ItemsPanel>
                            <ItemsPanelTemplate>
                                <StackPanel Orientation="Horizontal" Spacing="2" />
                            </ItemsPanelTemplate>
                        </ItemsControl.ItemsPanel>
                    </ItemsControl>
                </Border>
            </ControlTemplate>
        </Setter>

        <!-- Pseudo-class style for read-only state -->
        <Style Selector="^:readonly">
            <Setter Property="Opacity" Value="0.6" />
        </Style>
    </ControlTheme>
</ResourceDictionary>
```

Include it in `App.axaml`:

```xml
<Application.Styles>
    <FluentTheme />
    <StyleInclude Source="avares://MyApp/Themes/RatingControlTheme.axaml" />
</Application.Styles>
```

## Property System

Avalonia's property system has three property types. Choose the right one.

### StyledProperty

The general-purpose property. Supports binding, styling, animation, and value inheritance.

```csharp
public static readonly StyledProperty<double> SpacingProperty =
    AvaloniaProperty.Register<MyControl, double>(nameof(Spacing), 8.0);

public double Spacing
{
    get => GetValue(SpacingProperty);
    set => SetValue(SpacingProperty, value);
}
```

### DirectProperty

CLR-backed for performance-sensitive reads. Supports binding but **not** styling or animation.

```csharp
private string _status = "Ready";

public static readonly DirectProperty<MyControl, string> StatusProperty =
    AvaloniaProperty.RegisterDirect<MyControl, string>(
        nameof(Status),
        o => o.Status,       // getter
        (o, v) => o.Status = v);  // setter (optional, omit for read-only)

public string Status
{
    get => _status;
    set => SetAndRaise(StatusProperty, ref _status, value);
}
```

### AttachedProperty

Set on other controls. Think `Grid.Row` or `DockPanel.Dock`.

```csharp
public class Hint : AvaloniaObject
{
    public static readonly AttachedProperty<string> TextProperty =
        AvaloniaProperty.RegisterAttached<Hint, Control, string>("Text", string.Empty);

    public static string GetText(Control element) => element.GetValue(TextProperty);
    public static void SetText(Control element, string value) => element.SetValue(TextProperty, value);
}
```

```xml
<TextBox local:Hint.Text="Enter your name" />
```

### Property Comparison

| Feature | StyledProperty | DirectProperty |
|---------|---------------|----------------|
| Binding | Yes | Yes |
| Styling | Yes | **No** |
| Animation | Yes | **No** |
| Storage | Avalonia value store | CLR field |
| Read performance | Lookup from store | Direct field access |
| Inheritance | Supported | Not supported |
| Typical use | Most properties | High-frequency reads (e.g., `Bounds`) |

**Always** start with `StyledProperty`. Only use `DirectProperty` when profiling shows you need faster reads.

## Template Parts Convention

Template parts follow the `PART_` prefix convention. Access them in `OnApplyTemplate`:

```csharp
protected override void OnApplyTemplate(TemplateAppliedEventArgs e)
{
    base.OnApplyTemplate(e);

    // Unsubscribe from old parts (important for template re-application)
    if (_submitButton != null)
        _submitButton.Click -= OnSubmitClick;

    _submitButton = e.NameScope.Find<Button>("PART_SubmitButton");
    _contentHost = e.NameScope.Find<ContentPresenter>("PART_ContentHost");

    // Always null-check — the consumer's custom template might omit parts
    if (_submitButton != null)
        _submitButton.Click += OnSubmitClick;
}
```

**Never** throw if a template part is missing. Consumers may provide a custom template that omits optional parts. Design your control to degrade gracefully.

## Custom Pseudo-Classes

Add custom visual states targetable by style selectors:

```csharp
public class StatusIndicator : TemplatedControl
{
    public static readonly StyledProperty<bool> IsOnlineProperty =
        AvaloniaProperty.Register<StatusIndicator, bool>(nameof(IsOnline));

    public bool IsOnline
    {
        get => GetValue(IsOnlineProperty);
        set => SetValue(IsOnlineProperty, value);
    }

    // Update pseudo-class when property changes
    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);

        if (change.Property == IsOnlineProperty)
        {
            PseudoClasses.Set(":online", change.GetNewValue<bool>());
        }
    }
}
```

Target in styles:

```xml
<Style Selector="local|StatusIndicator:online">
    <Setter Property="Background" Value="Green" />
</Style>
<Style Selector="local|StatusIndicator:not(:online)">
    <Setter Property="Background" Value="Gray" />
</Style>
```

## TemplateBinding

Forward properties from the control into its template:

```xml
<ControlTemplate>
    <Border Background="{TemplateBinding Background}"
            Padding="{TemplateBinding Padding}"
            CornerRadius="{TemplateBinding CornerRadius}">
        <ContentPresenter Content="{TemplateBinding Content}"
                          ContentTemplate="{TemplateBinding ContentTemplate}" />
    </Border>
</ControlTemplate>
```

`TemplateBinding` is always one-way from control to template. For two-way scenarios, use a regular `Binding` with `RelativeSource={RelativeSource TemplatedParent}`.

## Common Patterns

### Wrapping a Third-Party Control

```csharp
public class EnhancedTextBox : TemplatedControl
{
    // Add a character count property on top of standard TextBox behavior
    public static readonly DirectProperty<EnhancedTextBox, int> CharCountProperty =
        AvaloniaProperty.RegisterDirect<EnhancedTextBox, int>(
            nameof(CharCount), o => o.CharCount);

    private int _charCount;
    public int CharCount
    {
        get => _charCount;
        private set => SetAndRaise(CharCountProperty, ref _charCount, value);
    }

    protected override void OnApplyTemplate(TemplateAppliedEventArgs e)
    {
        base.OnApplyTemplate(e);
        var textBox = e.NameScope.Find<TextBox>("PART_TextBox");
        if (textBox != null)
        {
            textBox.GetObservable(TextBox.TextProperty)
                .Subscribe(text => CharCount = text?.Length ?? 0);
        }
    }
}
```

### Creating a Composite Input Control

```csharp
// A UserControl combining a TextBox with a clear button
public partial class ClearableTextBox : UserControl
{
    public static readonly StyledProperty<string> TextProperty =
        AvaloniaProperty.Register<ClearableTextBox, string>(nameof(Text), string.Empty,
            defaultBindingMode: BindingMode.TwoWay);

    public string Text
    {
        get => GetValue(TextProperty);
        set => SetValue(TextProperty, value);
    }

    // Expose a Clear command that consumers can also bind to
    public void Clear() => Text = string.Empty;
}
```
