# Animations & Transitions

## Transitions (Implicit Animations)

Transitions animate property changes automatically. Set them on any control's `Transitions` collection and Avalonia handles the interpolation whenever the property value changes.

```xml
<Button Content="Hover Me" Background="Blue">
    <Button.Transitions>
        <Transitions>
            <DoubleTransition Property="Opacity" Duration="0:0:0.3" />
            <BrushTransition Property="Background" Duration="0:0:0.25" />
        </Transitions>
    </Button.Transitions>
</Button>
```

**Key**: Transitions fire on **any** property change -- binding updates, style triggers, pseudo-class changes. You declare the animation once and forget about it.

## Transition Types

| Transition Type | Animates | Example Properties |
|----------------|----------|-------------------|
| `DoubleTransition` | `double` values | `Opacity`, `Width`, `Height`, `FontSize` |
| `BrushTransition` | `IBrush` values | `Background`, `Foreground`, `BorderBrush` |
| `TransformOperationsTransition` | `TransformOperations` | `RenderTransform` |
| `ThicknessTransition` | `Thickness` values | `Margin`, `Padding`, `BorderThickness` |
| `CornerRadiusTransition` | `CornerRadius` values | `CornerRadius` |
| `ColorTransition` | `Color` values | Individual color properties |
| `BoxShadowsTransition` | `BoxShadows` values | `BoxShadow` |

```xml
<Border CornerRadius="4" Background="Gray" Padding="16">
    <Border.Transitions>
        <Transitions>
            <CornerRadiusTransition Property="CornerRadius" Duration="0:0:0.2" />
            <ThicknessTransition Property="Padding" Duration="0:0:0.15" />
        </Transitions>
    </Border.Transitions>
</Border>
```

## Easing Functions

Every transition accepts an `Easing` property. The default is linear.

| Easing | Behavior |
|--------|----------|
| `LinearEasing` | Constant speed, no acceleration |
| `CubicEaseIn` | Starts slow, accelerates |
| `CubicEaseOut` | Starts fast, decelerates |
| `CubicEaseInOut` | Slow start and end, fast middle |
| `QuadraticEaseIn` | Gentle acceleration |
| `QuadraticEaseOut` | Gentle deceleration |
| `BounceEaseOut` | Bounces at the end |
| `ElasticEaseOut` | Overshoots and springs back |
| `BackEaseIn` | Pulls back before moving forward |
| `BackEaseOut` | Overshoots then settles |
| `CircularEaseInOut` | Circular acceleration curve |

```xml
<DoubleTransition Property="Opacity" Duration="0:0:0.4" Easing="CubicEaseOut" />
<TransformOperationsTransition Property="RenderTransform" Duration="0:0:0.3" Easing="BackEaseOut" />
```

**Always** use `CubicEaseOut` or `QuadraticEaseOut` for UI element entrances. Linear easing looks mechanical.

## Keyframe Animations

For complex, multi-step animations, use keyframe animations inside `Style.Animations`. These are triggered by selectors and pseudo-classes.

```xml
<Style Selector="Button.pulse">
    <Style.Animations>
        <Animation Duration="0:0:1" IterationCount="INFINITE" PlaybackDirection="Alternate">
            <KeyFrame Cue="0%">
                <Setter Property="Opacity" Value="1.0" />
            </KeyFrame>
            <KeyFrame Cue="50%">
                <Setter Property="Opacity" Value="0.5" />
            </KeyFrame>
            <KeyFrame Cue="100%">
                <Setter Property="Opacity" Value="1.0" />
            </KeyFrame>
        </Animation>
    </Style.Animations>
</Style>
```

The `Cue` property sets the keyframe position as a percentage of the total duration. Use `0%` and `100%` to define start and end states.

## Animation Properties

| Property | Type | Values | Default |
|----------|------|--------|---------|
| `Duration` | `TimeSpan` | `"0:0:0.5"`, `"0:0:2"` | Required |
| `Delay` | `TimeSpan` | `"0:0:0.2"` | `0:0:0` |
| `IterationCount` | `IterationCount` | Number or `INFINITE` | `1` |
| `PlaybackDirection` | `PlaybackDirection` | `Normal`, `Reverse`, `Alternate`, `AlternateReverse` | `Normal` |
| `FillMode` | `FillMode` | `None`, `Forward`, `Backward`, `Both` | `None` |
| `Easing` | `Easing` | Any easing function | `LinearEasing` |

**FillMode matters**: `Forward` keeps the final keyframe values after the animation ends. `None` snaps back to the original values. Use `Forward` for entrance animations that should stick.

## Triggering Animations with Selectors

Animations activate when their selector matches. Pseudo-classes are the most common trigger:

```xml
<!-- Animate when the control gains the :pointerover pseudo-class -->
<Style Selector="Border.card:pointerover">
    <Style.Animations>
        <Animation Duration="0:0:0.2" FillMode="Forward">
            <KeyFrame Cue="100%">
                <Setter Property="ScaleTransform.ScaleX" Value="1.02" />
                <Setter Property="ScaleTransform.ScaleY" Value="1.02" />
            </KeyFrame>
        </Animation>
    </Style.Animations>
</Style>

<!-- Animate on class addition (toggle via code-behind or ViewModel) -->
<Style Selector="Panel.visible">
    <Style.Animations>
        <Animation Duration="0:0:0.3" FillMode="Forward">
            <KeyFrame Cue="0%">
                <Setter Property="Opacity" Value="0" />
            </KeyFrame>
            <KeyFrame Cue="100%">
                <Setter Property="Opacity" Value="1" />
            </KeyFrame>
        </Animation>
    </Style.Animations>
</Style>
```

## RenderTransform Animations

Avalonia supports CSS-like transform syntax through `TransformOperations`. This is the preferred way to animate transforms.

```xml
<Border Background="DodgerBlue" Width="100" Height="100"
        RenderTransform="scale(1)">
    <Border.Transitions>
        <Transitions>
            <TransformOperationsTransition Property="RenderTransform" Duration="0:0:0.3" Easing="CubicEaseOut" />
        </Transitions>
    </Border.Transitions>
</Border>
```

Supported transform functions:

| Function | Example | Description |
|----------|---------|-------------|
| `translate` | `translate(10px, 20px)` | Move X and Y |
| `translateX` | `translateX(50px)` | Move horizontal |
| `translateY` | `translateY(-20px)` | Move vertical |
| `scale` | `scale(1.1)` | Uniform scale |
| `scaleX` / `scaleY` | `scaleX(0.5)` | Axis scale |
| `rotate` | `rotate(45deg)` | Rotation |
| `skew` | `skew(10deg, 5deg)` | Skew |

Combine transforms in a single string:

```xml
<Border RenderTransform="scale(1.1) rotate(5deg) translateY(-4px)" />
```

## Page Transitions

For switching content with animated transitions, use `TransitioningContentControl` or `Carousel`.

### TransitioningContentControl

```xml
<TransitioningContentControl Content="{Binding CurrentPage}">
    <TransitioningContentControl.PageTransition>
        <CrossFade Duration="0:0:0.3" />
    </TransitioningContentControl.PageTransition>
</TransitioningContentControl>
```

### Built-In Page Transitions

| Transition | Description |
|-----------|-------------|
| `CrossFade` | Fades old content out, new content in |
| `PageSlide` | Slides content horizontally or vertically |
| `CompositePageTransition` | Combines multiple transitions |

```xml
<!-- Horizontal slide -->
<PageSlide Duration="0:0:0.4" Orientation="Horizontal" />

<!-- Vertical slide -->
<PageSlide Duration="0:0:0.3" Orientation="Vertical" />

<!-- Combined: fade + slide -->
<CompositePageTransition>
    <CrossFade Duration="0:0:0.3" />
    <PageSlide Duration="0:0:0.3" Orientation="Horizontal" />
</CompositePageTransition>
```

### Custom Page Transitions

Implement `IPageTransition` for full control:

```csharp
public class ScaleTransition : IPageTransition
{
    public TimeSpan Duration { get; set; } = TimeSpan.FromMilliseconds(300);

    public async Task Start(Visual? from, Visual? to, bool forward,
        CancellationToken cancellationToken)
    {
        if (from != null)
        {
            // Scale down and fade out the old content
            var fadeOut = new Animation
            {
                Duration = Duration,
                Children =
                {
                    new KeyFrame { Cue = new Cue(0), Setters = { new Setter(Visual.OpacityProperty, 1.0) } },
                    new KeyFrame { Cue = new Cue(1), Setters = { new Setter(Visual.OpacityProperty, 0.0) } }
                }
            };
            await fadeOut.RunAsync(from, cancellationToken);
            from.IsVisible = false;
        }

        if (to != null)
        {
            to.IsVisible = true;
            var fadeIn = new Animation
            {
                Duration = Duration,
                Children =
                {
                    new KeyFrame { Cue = new Cue(0), Setters = { new Setter(Visual.OpacityProperty, 0.0) } },
                    new KeyFrame { Cue = new Cue(1), Setters = { new Setter(Visual.OpacityProperty, 1.0) } }
                }
            };
            await fadeIn.RunAsync(to, cancellationToken);
        }
    }
}
```

## Composition Renderer

Avalonia 11 uses a composition renderer with a **server-side render thread**. Transitions and animations that target render properties (Opacity, RenderTransform) run on the render thread, not the UI thread. This means:

- Animations stay smooth even if the UI thread is busy
- **Prefer** `Opacity` and `RenderTransform` animations over `Width`/`Height`/`Margin` changes
- Layout-triggering property animations (Width, Height) run on the UI thread and can stutter

## Common Patterns

### Fade-in on Load

```xml
<Style Selector="UserControl.fadeIn">
    <Style.Animations>
        <Animation Duration="0:0:0.4" FillMode="Forward" Easing="CubicEaseOut">
            <KeyFrame Cue="0%">
                <Setter Property="Opacity" Value="0" />
                <Setter Property="TranslateTransform.Y" Value="20" />
            </KeyFrame>
            <KeyFrame Cue="100%">
                <Setter Property="Opacity" Value="1" />
                <Setter Property="TranslateTransform.Y" Value="0" />
            </KeyFrame>
        </Animation>
    </Style.Animations>
</Style>
```

### Hover Scale Effect

```xml
<Border Background="SlateBlue" CornerRadius="8" Padding="24"
        RenderTransformOrigin="50%,50%"
        RenderTransform="scale(1)">
    <Border.Transitions>
        <Transitions>
            <TransformOperationsTransition Property="RenderTransform" Duration="0:0:0.2" Easing="CubicEaseOut" />
        </Transitions>
    </Border.Transitions>
</Border>

<!-- Style to trigger the scale -->
<Style Selector="Border:pointerover">
    <Setter Property="RenderTransform" Value="scale(1.05)" />
</Style>
```

### Loading Spinner Rotation

```xml
<Style Selector="Path.spinner">
    <Style.Animations>
        <Animation Duration="0:0:1" IterationCount="INFINITE">
            <KeyFrame Cue="0%">
                <Setter Property="RotateTransform.Angle" Value="0" />
            </KeyFrame>
            <KeyFrame Cue="100%">
                <Setter Property="RotateTransform.Angle" Value="360" />
            </KeyFrame>
        </Animation>
    </Style.Animations>
</Style>
```

### Slide-in Navigation Panel

```xml
<Style Selector="Border.navPanel">
    <Setter Property="RenderTransform" Value="translateX(-250px)" />
    <Setter Property="Opacity" Value="0" />
</Style>

<Style Selector="Border.navPanel.open">
    <Setter Property="RenderTransform" Value="translateX(0)" />
    <Setter Property="Opacity" Value="1" />
</Style>

<!-- Transitions handle the animation between states -->
<Border Classes="navPanel" Width="250">
    <Border.Transitions>
        <Transitions>
            <TransformOperationsTransition Property="RenderTransform" Duration="0:0:0.3" Easing="CubicEaseOut" />
            <DoubleTransition Property="Opacity" Duration="0:0:0.2" />
        </Transitions>
    </Border.Transitions>
</Border>
```

## Performance Guidelines

- **Prefer transitions** over keyframe animations for simple property changes -- they are declarative and easier to maintain
- **Prefer** `Opacity` and `RenderTransform` over layout properties (`Width`, `Height`, `Margin`) for animations
- Keep animation durations between **150ms-400ms** for UI interactions; longer feels sluggish
- Use `IterationCount="INFINITE"` sparingly -- continuous animations consume GPU resources
- Set `RenderTransformOrigin="50%,50%"` explicitly when scaling or rotating to avoid unexpected pivot points
- **Never** animate `IsVisible` -- it is a boolean with no interpolation. Animate `Opacity` and toggle `IsVisible` at the boundaries
