# Interaction & UX Patterns

Desktop UX lives or dies on keyboard support and responsive feedback. **Every** interactive element must be reachable without a mouse. This doc covers keyboard design, accessibility, progress indicators, notifications, and common interaction patterns for Avalonia 11.x apps.

---

## Keyboard-First Design

### Tab Order

Follow visual reading order: left-to-right, top-to-bottom. Avalonia tabs through focusable controls in their declared order by default. Override only when the visual layout diverges from markup order.

| Property | Purpose |
|----------|---------|
| `TabIndex` | Explicit tab position (lower = earlier). **Avoid** unless layout order doesn't match visual order. |
| `IsTabStop="False"` | Removes element from tab sequence. Use for decorative or read-only controls. |
| `KeyboardNavigation.TabNavigation` | Controls tab behavior within containers: `Continue`, `Cycle`, `Once`, `Local`. |

```xml
<StackPanel KeyboardNavigation.TabNavigation="Cycle">
    <!-- Tab cycles within this panel instead of leaving it -->
    <TextBox TabIndex="0" Watermark="First Name" />
    <TextBox TabIndex="1" Watermark="Last Name" />
    <Button TabIndex="2" Content="Submit" />
</StackPanel>
```

### Accelerator Keys (Ctrl+Key)

Bind global shortcuts using `KeyBindings` on the window or top-level control.

```xml
<Window.KeyBindings>
    <KeyBinding Gesture="Ctrl+S" Command="{Binding SaveCommand}" />
    <KeyBinding Gesture="Ctrl+Z" Command="{Binding UndoCommand}" />
    <KeyBinding Gesture="Ctrl+Shift+Z" Command="{Binding RedoCommand}" />
    <KeyBinding Gesture="Ctrl+F" Command="{Binding FindCommand}" />
    <KeyBinding Gesture="F5" Command="{Binding RefreshCommand}" />
</Window.KeyBindings>
```

### Access Keys (Alt+Key)

Underlined mnemonics activated with Alt. Prefix the character with `_` in the `Header` or `Content` property.

```xml
<Menu>
    <MenuItem Header="_File">        <!-- Alt+F -->
        <MenuItem Header="_New" Command="{Binding NewCommand}" />    <!-- Alt+N -->
        <MenuItem Header="_Open" Command="{Binding OpenCommand}" />  <!-- Alt+O -->
        <MenuItem Header="_Save" Command="{Binding SaveCommand}" />  <!-- Alt+S -->
    </MenuItem>
    <MenuItem Header="_Edit">        <!-- Alt+E -->
        <MenuItem Header="_Undo" Command="{Binding UndoCommand}" />
    </MenuItem>
</Menu>
```

### Focus Management

Set initial focus on the primary action or input field. Use `FocusManager` or the `AttachedToVisualTree` event.

```csharp
// In code-behind (view only, not ViewModel)
protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnAttachedToVisualTree(e);
    // Focus the first input when the view loads
    this.FindControl<TextBox>("SearchBox")?.Focus();
}
```

**Always** provide visible focus indicators. Avalonia's default theme includes focus rectangles. If you use custom styles, ensure `:focus-visible` pseudo-class has a clear visual treatment.

```xml
<Style Selector="TextBox:focus-visible">
    <Setter Property="BorderBrush" Value="{DynamicResource SystemAccentColor}" />
    <Setter Property="BorderThickness" Value="2" />
</Style>
```

---

## Standard Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Copy |
| `Ctrl+X` | Cut |
| `Ctrl+V` | Paste |
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` or `Ctrl+Y` | Redo |
| `Ctrl+S` | Save |
| `Ctrl+F` | Find / Search |
| `Ctrl+P` | Print |
| `Ctrl+A` | Select all |
| `Ctrl+Tab` | Switch tab / next pane |
| `Ctrl+Shift+Tab` | Previous tab / pane |
| `Esc` | Dismiss dialog / cancel current operation |
| `F6` | Cycle between panes |
| `F1` | Help |

## Key Behaviors

| Key | Expected Behavior |
|-----|-------------------|
| `Space` | Invoke focused button, toggle checkbox/radio |
| `Enter` | Activate default button, open selected item, confirm dialog |
| `Escape` | Dismiss flyout/dialog, cancel edit, clear selection |
| `Home` / `End` | Jump to first / last item in list or text |
| `Page Up` / `Page Down` | Scroll one viewport in list or document |
| `Arrow keys` | Navigate within a control (list items, radio group, menu items) |
| `Shift+Arrow` | Extend selection range |
| `Ctrl+Click` | Toggle individual selection in multi-select list |

---

## Accessibility

### Screen Reader Support

Set `AutomationProperties.Name` on every actionable control that lacks visible text. Screen readers use this as the accessible label.

```xml
<!-- Button with icon only — screen reader needs a name -->
<Button Command="{Binding DeleteCommand}"
        AutomationProperties.Name="Delete selected item">
    <PathIcon Data="{StaticResource DeleteIcon}" />
</Button>

<!-- Image with descriptive text -->
<Image Source="/Assets/logo.png"
       AutomationProperties.Name="Company logo" />

<!-- Decorative image — hide from screen reader -->
<Image Source="/Assets/divider.png"
       AutomationProperties.Name=""
       IsHitTestVisible="False" />
```

Use `AutomationProperties.HelpText` for additional context when the name alone is insufficient.

### Visual Accessibility Requirements

| Requirement | Minimum |
|-------------|---------|
| Body text size | 12px Regular or 14px Semibold |
| Text contrast ratio (WCAG AA) | 4.5:1 against background |
| Large text contrast (18px+ or 14px bold) | 3:1 against background |
| Interactive element size | 32x32 px minimum touch target |

**Never** rely on color alone to convey information. Approximately 8% of men have red-green color blindness. Always pair color with shape, icon, or text.

```xml
<!-- Bad: only color differentiates status -->
<Ellipse Fill="{Binding StatusColor}" Width="12" Height="12" />

<!-- Good: icon + color + text -->
<StackPanel Orientation="Horizontal" Spacing="4">
    <PathIcon Data="{Binding StatusIcon}" Foreground="{Binding StatusColor}" />
    <TextBlock Text="{Binding StatusText}" />
</StackPanel>
```

### High Contrast Support

Avalonia supports `FluentTheme` with `RequestedThemeVariant`. Test your app with both `Light` and `Dark` variants. Use `DynamicResource` for all colors so they adapt to theme changes.

```xml
<!-- Always use dynamic resources, never hard-coded colors -->
<TextBlock Foreground="{DynamicResource TextFillColorPrimary}"
           Text="Adapts to theme automatically" />
```

---

## Progress Indicators

| Type | Control | When to Use |
|------|---------|------------|
| Determinate bar | `ProgressBar Value="60" Maximum="100"` | Duration known (file upload, batch processing) |
| Indeterminate bar | `ProgressBar IsIndeterminate="True"` | Duration unknown, user can continue working |
| Indeterminate ring | `ProgressRing IsActive="True"` | Duration unknown, blocks interaction on that area |
| Determinate ring | `ProgressRing Value="75" Maximum="100"` | Duration known, compact display |

```xml
<!-- File upload with progress -->
<StackPanel>
    <TextBlock Text="{Binding UploadStatus}" />
    <ProgressBar Value="{Binding UploadPercent}"
                 Maximum="100"
                 ShowProgressText="True" />
</StackPanel>

<!-- Loading data — user can still interact elsewhere -->
<ProgressBar IsIndeterminate="True"
             IsVisible="{Binding IsLoading}" />

<!-- Blocking spinner over content area -->
<Panel>
    <ListBox Items="{Binding Items}" />
    <ProgressRing IsActive="{Binding IsLoading}"
                  HorizontalAlignment="Center"
                  VerticalAlignment="Center" />
</Panel>
```

---

## Notifications and InfoBar

Use inline notifications for non-intrusive feedback. Use `ContentDialog` only for blocking messages that require user action.

### Severity Levels

| Severity | Use For |
|----------|---------|
| `Error` | Operation failed, data loss risk, action required |
| `Warning` | Potential problem, user should be aware |
| `Success` | Operation completed successfully |
| `Informational` | Neutral info, tips, status updates |

```xml
<!-- Inline notification bar (custom implementation or third-party) -->
<Border Background="{Binding NotificationBackground}"
        Padding="12"
        CornerRadius="4"
        IsVisible="{Binding HasNotification}">
    <DockPanel>
        <Button DockPanel.Dock="Right"
                Content="Dismiss"
                Command="{Binding DismissNotificationCommand}" />
        <TextBlock Text="{Binding NotificationMessage}"
                   VerticalAlignment="Center" />
    </DockPanel>
</Border>
```

### Confirmation vs Undo

**Prefer undo over confirmation dialogs.** Confirmation dialogs are speed bumps users click through without reading. Reserve them for irreversible, high-consequence actions only.

| Pattern | Use When | Example |
|---------|----------|---------|
| Undo (preferred) | Action is reversible | Delete email, move file, remove item from list |
| Confirmation dialog | Action is irreversible AND high-consequence | Permanently delete account, format disk, publish to production |
| No confirmation | Low-risk, easily repeated | Copy, sort, filter, navigate |

---

## Context Menus

```xml
<ListBox Items="{Binding Documents}">
    <ListBox.ContextMenu>
        <ContextMenu>
            <MenuItem Header="Open" Command="{Binding OpenCommand}"
                      InputGesture="Ctrl+O" />
            <MenuItem Header="Rename" Command="{Binding RenameCommand}"
                      InputGesture="F2" />
            <Separator />
            <MenuItem Header="Delete" Command="{Binding DeleteCommand}"
                      InputGesture="Delete" />
        </ContextMenu>
    </ListBox.ContextMenu>
</ListBox>
```

Show `InputGesture` text on menu items so users learn keyboard shortcuts over time.

---

## Selection Patterns

For multi-select lists, support standard desktop selection conventions:

| Interaction | Behavior |
|-------------|----------|
| Click | Select single item, deselect others |
| `Ctrl+Click` | Toggle selection on individual item |
| `Shift+Click` | Select range from anchor to clicked item |
| `Ctrl+A` | Select all items |
| `Shift+Arrow` | Extend selection one item at a time |

```xml
<ListBox Items="{Binding Items}"
         SelectionMode="Multiple"
         SelectedItems="{Binding SelectedItems}" />
```

---

## Drag and Drop

Prefer direct manipulation for visual operations (reordering, moving between containers). **Always** provide a keyboard alternative (move up/down buttons, cut/paste).

```csharp
// Basic drag-and-drop setup on a control
private void OnPointerPressed(object sender, PointerPressedEventArgs e)
{
    var data = new DataObject();
    data.Set("application/my-item", _viewModel.SelectedItem);
    DragDrop.DoDragDrop(e, data, DragDropEffects.Move);
}
```

---

## Empty States

**Never** show a blank screen when a list or view has no data. Provide helpful content that guides the user toward their next action.

```xml
<Panel>
    <ListBox Items="{Binding Tasks}"
             IsVisible="{Binding HasTasks}" />

    <!-- Empty state shown when no data -->
    <StackPanel IsVisible="{Binding !HasTasks}"
                HorizontalAlignment="Center"
                VerticalAlignment="Center"
                Spacing="8">
        <PathIcon Data="{StaticResource TaskListIcon}"
                  Width="48" Height="48"
                  Foreground="{DynamicResource TextFillColorSecondary}" />
        <TextBlock Text="No tasks yet"
                   Theme="{StaticResource SubtitleTextBlockStyle}" />
        <TextBlock Text="Create your first task to get started"
                   Foreground="{DynamicResource TextFillColorSecondary}" />
        <Button Content="New Task"
                Command="{Binding CreateTaskCommand}"
                HorizontalAlignment="Center" />
    </StackPanel>
</Panel>
```

---

## Error States

Show errors inline, close to the source. Provide recovery guidance, not just the error message.

```xml
<!-- Inline error after failed load -->
<StackPanel IsVisible="{Binding HasError}"
            HorizontalAlignment="Center"
            VerticalAlignment="Center"
            Spacing="8">
    <TextBlock Text="Unable to load data"
               Foreground="{DynamicResource SystemFillColorCritical}" />
    <TextBlock Text="{Binding ErrorMessage}"
               Foreground="{DynamicResource TextFillColorSecondary}" />
    <Button Content="Retry" Command="{Binding RetryCommand}" />
</StackPanel>
```

---

## Loading Patterns

| Pattern | When to Use |
|---------|------------|
| Skeleton screen | Known layout, data loading. Show placeholder shapes that match final content. |
| Progressive loading | Large datasets. Load and display first batch, fetch more on scroll. |
| Shimmer effect | Skeleton with animated gradient to signal activity. |
| Inline spinner | Single component loading within an otherwise interactive page. |

For skeleton screens, create a placeholder that matches the shape of your final UI:

```xml
<ItemsRepeater Items="{Binding SkeletonItems}"
               IsVisible="{Binding IsLoading}">
    <ItemsRepeater.ItemTemplate>
        <DataTemplate>
            <Border Padding="8" Margin="0,4">
                <StackPanel Spacing="4">
                    <!-- Placeholder rectangles mimicking text lines -->
                    <Border Background="{DynamicResource ControlFillColorSecondary}"
                            Height="16" Width="200" CornerRadius="4" />
                    <Border Background="{DynamicResource ControlFillColorSecondary}"
                            Height="12" Width="300" CornerRadius="4" />
                </StackPanel>
            </Border>
        </DataTemplate>
    </ItemsRepeater.ItemTemplate>
</ItemsRepeater>
```

**Key**: Always show something immediately. A blank screen with a spinner feels slower than a skeleton that appears instantly.
