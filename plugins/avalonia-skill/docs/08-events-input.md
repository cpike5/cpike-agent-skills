# Events & Input Handling

## Routed Event System

Avalonia uses the same routed event model as WPF. Events travel through the visual tree in predictable ways.

| Strategy | Direction | Name Convention | When It Fires |
|----------|-----------|-----------------|---------------|
| Tunneling | Root down to source | `Preview*` (e.g., `PointerPressed`) | Before the bubbling phase |
| Bubbling | Source up to root | Standard name | After tunneling completes |
| Direct | Only on the source control | Varies | Does not propagate |

Tunneling and bubbling always come in pairs. The tunneling event fires first, giving ancestors a chance to intercept before the target handles it.

## Pointer Events

Avalonia unifies mouse, touch, and pen input into a single pointer model. **No separate `MouseDown`/`TouchDown` events.**

| Event | When |
|-------|------|
| `PointerPressed` | Pointer button pressed or touch contact begins |
| `PointerMoved` | Pointer moves while over the control |
| `PointerReleased` | Pointer button released or touch contact lifted |
| `PointerEntered` | Pointer enters the control bounds |
| `PointerExited` | Pointer leaves the control bounds |
| `PointerCaptureLost` | Control loses pointer capture |

### PointerEventArgs

```csharp
private void OnPointerPressed(object? sender, PointerPressedEventArgs e)
{
    var point = e.GetPosition(this);  // position relative to this control
    var properties = e.GetCurrentPoint(this).Properties;

    bool isLeftButton = properties.IsLeftButtonPressed;
    bool isRightButton = properties.IsRightButtonPressed;
    bool isMiddle = properties.IsMiddleButtonPressed;

    // Check modifiers
    KeyModifiers mods = e.KeyModifiers;
    bool ctrlHeld = mods.HasFlag(KeyModifiers.Control);
    bool shiftHeld = mods.HasFlag(KeyModifiers.Shift);

    // Pointer type
    PointerType type = e.Pointer.Type;  // Mouse, Touch, or Pen
}
```

### Pointer Capture

Capture the pointer to receive events even when the pointer moves outside the control:

```csharp
private void OnPointerPressed(object? sender, PointerPressedEventArgs e)
{
    e.Pointer.Capture(this);  // start capturing
}

private void OnPointerReleased(object? sender, PointerReleasedEventArgs e)
{
    e.Pointer.Capture(null);  // release capture
}
```

## Gesture Events

Higher-level events built on top of pointer events:

| Event | Trigger |
|-------|---------|
| `Tapped` | Quick press and release (click/tap) |
| `DoubleTapped` | Two quick taps |
| `Holding` | Long press (touch/pen only) |

```csharp
private void OnDoubleTapped(object? sender, TappedEventArgs e)
{
    var position = e.GetPosition(this);
    // Open editor, zoom in, etc.
}
```

For advanced gestures like pinch, pan, and rotate, use `Avalonia.Gestures` or handle raw pointer events with tracking logic.

## Keyboard Events

| Event | When |
|-------|------|
| `KeyDown` | Key pressed (fires repeatedly if held) |
| `KeyUp` | Key released |
| `TextInput` | Character input after key translation |

```csharp
private void OnKeyDown(object? sender, KeyEventArgs e)
{
    if (e.Key == Key.Enter)
    {
        SubmitForm();
        e.Handled = true;  // prevent further processing
    }

    if (e.Key == Key.Escape)
    {
        CancelEdit();
        e.Handled = true;
    }

    // Check modifier combinations
    if (e.Key == Key.S && e.KeyModifiers.HasFlag(KeyModifiers.Control))
    {
        SaveDocument();
        e.Handled = true;
    }
}
```

**Use `TextInput`** when you need the actual character typed (respects IME, dead keys, etc.). Use `KeyDown` for action keys and shortcuts.

## Focus Events

| Event | When |
|-------|------|
| `GotFocus` | Control receives keyboard focus |
| `LostFocus` | Control loses keyboard focus |

### Focus Management

```csharp
// Programmatically focus a control
myTextBox.Focus();

// Focus with navigation method specified
myTextBox.Focus(NavigationMethod.Tab);

// Check current focus
var focused = TopLevel.GetTopLevel(this)?.FocusManager?.GetFocusedElement();
```

### Tab Navigation

```xml
<!-- Control tab order explicitly -->
<TextBox TabIndex="0" />
<TextBox TabIndex="1" />
<Button TabIndex="2" />

<!-- Remove from tab sequence -->
<Image IsTabStop="False" />

<!-- Prevent focus entirely -->
<Panel Focusable="False" />
```

## Events vs Commands in MVVM

| Use | Mechanism | Example |
|-----|-----------|---------|
| User actions (save, delete, navigate) | `Command` binding | `Command="{Binding SaveCommand}"` |
| View-specific behavior (focus, scroll, animate) | Event handlers in code-behind | `GotFocus`, `PointerEntered` |
| Drag-and-drop | Event handlers | `PointerPressed` + `PointerMoved` |
| Keyboard shortcuts | `KeyBindings` | `KeyGesture` in AXAML |

**Never** put business logic in event handlers. Code-behind should only contain view-specific plumbing that delegates to the ViewModel.

## EventToCommandBehavior

Bridge events to commands without code-behind using `Avalonia.Xaml.Behaviors`:

```
dotnet add package Avalonia.Xaml.Behaviors
```

```xml
<TextBox>
    <Interaction.Behaviors>
        <EventTriggerBehavior EventName="KeyDown">
            <InvokeCommandAction Command="{Binding SearchCommand}" />
        </EventTriggerBehavior>
    </Interaction.Behaviors>
</TextBox>
```

This is useful for events that have no built-in `Command` property, like `GotFocus` or `DoubleTapped`.

## Custom Routed Events

Declare custom routed events in your controls:

```csharp
public class ColorPicker : TemplatedControl
{
    // Declare the routed event
    public static readonly RoutedEvent<ColorChangedEventArgs> ColorChangedEvent =
        RoutedEvent.Register<ColorPicker, ColorChangedEventArgs>(
            nameof(ColorChanged), RoutingStrategies.Bubble);

    // CLR event wrapper
    public event EventHandler<ColorChangedEventArgs> ColorChanged
    {
        add => AddHandler(ColorChangedEvent, value);
        remove => RemoveHandler(ColorChangedEvent, value);
    }

    // Raise it
    protected void OnColorChanged(Color oldColor, Color newColor)
    {
        RaiseEvent(new ColorChangedEventArgs(ColorChangedEvent, oldColor, newColor));
    }
}

// Custom event args
public class ColorChangedEventArgs : RoutedEventArgs
{
    public Color OldColor { get; }
    public Color NewColor { get; }

    public ColorChangedEventArgs(RoutedEvent routedEvent, Color oldColor, Color newColor)
        : base(routedEvent)
    {
        OldColor = oldColor;
        NewColor = newColor;
    }
}
```

## ClassHandler

Avalonia's `ClassHandler` registers a static event handler at the class level. This is how built-in controls handle events before any instance exists. It is an Avalonia-specific pattern with no direct WPF equivalent.

```csharp
public class ClickCounterPanel : Panel
{
    static ClickCounterPanel()
    {
        // Handle PointerPressed for ALL instances of this class
        PointerPressedEvent.AddClassHandler<ClickCounterPanel>(
            (panel, args) => panel.OnPanelPointerPressed(args),
            RoutingStrategies.Bubble,
            handledEvents: false);  // still fires even if e.Handled is true
    }

    private void OnPanelPointerPressed(PointerPressedEventArgs e)
    {
        // Runs for every instance, registered once at the type level
        ClickCount++;
    }

    public int ClickCount { get; private set; }
}
```

**Key**: The `handledEvents` parameter controls whether your handler fires even when a child has already marked the event as handled. Set to `true` when you need to observe all events regardless.

## Handled Flag

Stop event propagation by setting `Handled`:

```csharp
private void OnPointerPressed(object? sender, PointerPressedEventArgs e)
{
    // Process the event
    DoSomething();

    // Stop the event from bubbling further up the tree
    e.Handled = true;
}
```

**Be careful** with `Handled = true`. It suppresses all handlers further up the tree. Only set it when you're certain no ancestor needs to process the event.

## Keyboard Shortcuts with KeyBindings

Bind keyboard shortcuts directly in AXAML:

```xml
<Window xmlns="https://github.com/avaloniaui">
    <Window.KeyBindings>
        <KeyBinding Gesture="Ctrl+S" Command="{Binding SaveCommand}" />
        <KeyBinding Gesture="Ctrl+Z" Command="{Binding UndoCommand}" />
        <KeyBinding Gesture="Ctrl+Shift+Z" Command="{Binding RedoCommand}" />
        <KeyBinding Gesture="Delete" Command="{Binding DeleteCommand}" />
        <KeyBinding Gesture="F5" Command="{Binding RefreshCommand}" />
        <KeyBinding Gesture="Escape" Command="{Binding CancelCommand}" />
    </Window.KeyBindings>

    <!-- window content -->
</Window>
```

### KeyGesture Class

Create gestures programmatically:

```csharp
// Simple key
var escape = new KeyGesture(Key.Escape);

// Key + modifier
var save = new KeyGesture(Key.S, KeyModifiers.Control);

// Multi-modifier
var redo = new KeyGesture(Key.Z, KeyModifiers.Control | KeyModifiers.Shift);
```

### Platform-Aware Modifiers

Avalonia maps `Ctrl` to `Cmd` on macOS automatically for `KeyBindings` in AXAML. For programmatic handling:

```csharp
// Use KeyModifiers.Meta for Cmd on macOS
// Use KeyModifiers.Control for Ctrl on Windows/Linux
// Or check the platform:
private KeyModifiers PrimaryModifier =>
    OperatingSystem.IsMacOS() ? KeyModifiers.Meta : KeyModifiers.Control;
```

## Common Patterns

### Handle Escape to Close a Dialog

```csharp
public partial class DialogWindow : Window
{
    public DialogWindow()
    {
        InitializeComponent();
        KeyDown += OnKeyDown;
    }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        if (e.Key == Key.Escape)
        {
            Close(null);  // return null result
            e.Handled = true;
        }
    }
}
```

### Handle Enter to Submit a Form

```xml
<TextBox KeyDown="OnSearchKeyDown" />
```

```csharp
private void OnSearchKeyDown(object? sender, KeyEventArgs e)
{
    if (e.Key == Key.Enter && DataContext is SearchViewModel vm && vm.SearchCommand.CanExecute(null))
    {
        vm.SearchCommand.Execute(null);
        e.Handled = true;
    }
}
```

### Weak Event Patterns

Prevent memory leaks from long-lived event subscriptions:

```csharp
public class MyControl : Control
{
    private IDisposable? _subscription;

    protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
    {
        base.OnAttachedToVisualTree(e);

        // Subscribe when added to the tree
        _subscription = someService.SomeObservable.Subscribe(OnValueChanged);
    }

    protected override void OnDetachedFromVisualTree(VisualTreeAttachmentEventArgs e)
    {
        base.OnDetachedFromVisualTree(e);

        // Clean up when removed from the tree
        _subscription?.Dispose();
        _subscription = null;
    }
}
```

**Always** unsubscribe from events and dispose subscriptions in `OnDetachedFromVisualTree`. Failing to do so is the most common source of memory leaks in Avalonia apps.

For standard .NET events, unsubscribe explicitly:

```csharp
protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnAttachedToVisualTree(e);
    _someService.DataChanged += OnDataChanged;
}

protected override void OnDetachedFromVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnDetachedFromVisualTree(e);
    _someService.DataChanged -= OnDataChanged;
}
```
