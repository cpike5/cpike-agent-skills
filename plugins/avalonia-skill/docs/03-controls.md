# Core Controls Reference

## Input Controls

| Control | Description |
|---|---|
| `Button` | Standard click button. Content can be text, icons, or any visual tree. |
| `RepeatButton` | Fires `Click` continuously while held down. Good for increment/decrement. |
| `ToggleButton` | Two-state button. Bind to `IsChecked` (bool?). |
| `RadioButton` | Exclusive selection within a `GroupName`. Bind to `IsChecked`. |
| `CheckBox` | Three-state toggle (`IsThreeState="True"` for null/true/false). |
| `TextBox` | Text input. Supports `Watermark`, `RevealPassword`, inner content slots. |
| `MaskedTextBox` | Text input with format mask (phone numbers, dates). |
| `AutoCompleteBox` | Text input with filtered suggestion dropdown. |
| `NumericUpDown` | Numeric input with increment/decrement buttons and range constraints. |
| `Slider` | Drag-to-select numeric value. `Minimum`, `Maximum`, `Value`. |
| `ToggleSwitch` | On/off switch (Avalonia-specific, not in WPF). Bind to `IsChecked`. |
| `CalendarDatePicker` | Date picker with calendar dropdown. |
| `DatePicker` | Spinning-wheel style date selector. |
| `TimePicker` | Spinning-wheel style time selector. |
| `ColorPicker` | Full color selection with spectrum, sliders, hex input. |

### TextBox Details

`TextBox` is the most feature-rich input control. Key properties beyond basic text:

```xml
<!-- Watermark (placeholder text) -->
<TextBox Watermark="Enter your email..." />

<!-- Password input with reveal button -->
<TextBox PasswordChar="*" RevealPassword="True" />

<!-- Inner content slots — put icons or buttons inside the text box -->
<TextBox Watermark="Search...">
    <TextBox.InnerLeftContent>
        <PathIcon Data="{StaticResource SearchIcon}" Width="16" Margin="8,0,0,0" />
    </TextBox.InnerLeftContent>
    <TextBox.InnerRightContent>
        <Button Content="X" Command="{Binding ClearSearchCommand}"
                Classes="transparent" Padding="8,0" />
    </TextBox.InnerRightContent>
</TextBox>

<!-- Multiline -->
<TextBox AcceptsReturn="True" TextWrapping="Wrap" Height="100" />
```

## Selection and List Controls

| Control | Description |
|---|---|
| `ComboBox` | Dropdown selection. `SelectedItem`, `SelectedIndex`, `ItemTemplate`. |
| `ListBox` | Scrollable selection list. Supports single/multi-select via `SelectionMode`. |
| `DataGrid` | Tabular data with sorting, resizing, editing. **Separate NuGet**: `Avalonia.Controls.DataGrid`. |
| `TreeView` | Hierarchical tree with expand/collapse. Bind `ItemsSource` recursively. |
| `TreeDataGrid` | High-performance flat or hierarchical grid. **Separate NuGet** and **Avalonia-specific**. |
| `TabControl` | Tabbed content regions. `TabStripPlacement` for tab position. |
| `Carousel` | Animated content switching. One child visible at a time with transitions. |
| `ItemsRepeater` | Virtualizing layout repeater (from WinUI concept). No built-in selection. |

### ListBox with ItemTemplate

```xml
<ListBox ItemsSource="{Binding Users}" SelectedItem="{Binding SelectedUser}"
         SelectionMode="Single">
    <ListBox.ItemTemplate>
        <DataTemplate x:DataType="models:User">
            <StackPanel Orientation="Horizontal" Spacing="8">
                <Border Width="32" Height="32" CornerRadius="16"
                        Background="{Binding AvatarColor}">
                    <TextBlock Text="{Binding Initials}"
                               HorizontalAlignment="Center"
                               VerticalAlignment="Center" />
                </Border>
                <StackPanel Spacing="2" VerticalAlignment="Center">
                    <TextBlock Text="{Binding Name}" FontWeight="SemiBold" />
                    <TextBlock Text="{Binding Email}" FontSize="12" Foreground="#888" />
                </StackPanel>
            </StackPanel>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

**SelectionMode options**: `Single` (default), `Multiple`, `Toggle`, `AlwaysSelected`.

### DataGrid Basic Setup

Requires the `Avalonia.Controls.DataGrid` NuGet package.

```xml
<!-- Add namespace -->
<Window xmlns:dg="using:Avalonia.Controls"
        ...>

<dg:DataGrid ItemsSource="{Binding Orders}" AutoGenerateColumns="False"
             IsReadOnly="True" CanUserSortColumns="True"
             GridLinesVisibility="Horizontal">
    <dg:DataGrid.Columns>
        <dg:DataGridTextColumn Header="Order #" Binding="{Binding OrderNumber}" Width="100" />
        <dg:DataGridTextColumn Header="Customer" Binding="{Binding CustomerName}" Width="*" />
        <dg:DataGridTextColumn Header="Total" Binding="{Binding Total, StringFormat=C}" Width="120" />
        <dg:DataGridCheckBoxColumn Header="Shipped" Binding="{Binding IsShipped}" Width="80" />
        <dg:DataGridTemplateColumn Header="Actions" Width="100">
            <dg:DataGridTemplateColumn.CellTemplate>
                <DataTemplate>
                    <Button Content="View" Command="{Binding $parent[dg:DataGrid].((vm:OrderListViewModel)DataContext).ViewCommand}"
                            CommandParameter="{Binding}" Classes="compact" />
                </DataTemplate>
            </dg:DataGridTemplateColumn.CellTemplate>
        </dg:DataGridTemplateColumn>
    </dg:DataGrid.Columns>
</dg:DataGrid>
```

**Note**: `$parent[DataGrid]` is Avalonia's binding syntax for walking up the visual tree to find an ancestor of a specific type. This is how you reach the parent DataContext from inside a cell template.

## Display Controls

| Control | Description |
|---|---|
| `TextBlock` | Read-only text display. Supports `FontWeight`, `FontSize`, `TextWrapping`, `TextTrimming`. |
| `SelectableTextBlock` | Text that users can select and copy. **Avalonia-specific**. |
| `Label` | Lightweight label. `Target` property focuses the linked control on click. |
| `Image` | Displays bitmaps. `Source` from resources or URI. `Stretch` mode. |
| `Border` | Decorative wrapper: `Background`, `BorderBrush`, `BorderThickness`, `CornerRadius`. |
| `Viewbox` | Scales a single child to fit available space. Good for icons/SVG. |
| `ContentControl` | Displays a single content item. Base class for many controls. |
| `ToolTip` | Hover popup. Set via `ToolTip.Tip` attached property. |
| `ProgressBar` | Determinate or indeterminate (`IsIndeterminate="True"`) progress indicator. |
| `Expander` | Collapsible content section with header. `IsExpanded` bindable. |
| `PathIcon` | Vector icon from geometry path data. |

### Common Display Patterns

```xml
<!-- Image with fallback size -->
<Image Source="/Assets/logo.png" Width="48" Height="48" Stretch="Uniform" />

<!-- ToolTip on any control -->
<Button Content="Save" ToolTip.Tip="Save changes to disk (Ctrl+S)" />

<!-- Indeterminate progress bar for loading states -->
<ProgressBar IsIndeterminate="True" IsVisible="{Binding IsLoading}" Height="4" />

<!-- SelectableTextBlock — users can copy this text -->
<SelectableTextBlock Text="{Binding ErrorDetails}" TextWrapping="Wrap" />

<!-- Border as a card container -->
<Border Background="#1E1E1E" CornerRadius="8" Padding="16" Margin="8"
        BorderBrush="#333" BorderThickness="1">
    <StackPanel Spacing="8">
        <TextBlock Text="{Binding Title}" FontWeight="Bold" FontSize="16" />
        <TextBlock Text="{Binding Description}" TextWrapping="Wrap" Foreground="#AAA" />
    </StackPanel>
</Border>
```

## Navigation and Structure Controls

| Control | Description |
|---|---|
| `Menu` / `MenuItem` | Top-level menu bar. Supports `InputGesture` for keyboard shortcuts. |
| `ContextMenu` | Right-click menu. Attach via `ContextMenu` property on any control. |
| `NativeMenu` | macOS-specific global menu bar. Falls back to regular `Menu` elsewhere. |
| `SplitView` | Side panel that can be pinned or overlay. `IsPaneOpen`, `DisplayMode`. |
| `Flyout` | Popup content attached to a control. `ShowMode`: Standard, Transient, TransientWithDismissOnPointerMoveAway. |
| `MenuFlyout` | Flyout containing menu items. Useful for context-style menus on buttons. |
| `ScrollViewer` | Scrollable content wrapper. `HorizontalScrollBarVisibility`, `VerticalScrollBarVisibility`. |
| `SplitButton` | Button with dropdown arrow for secondary actions. **Avalonia-specific**. |
| `DropDownButton` | Button that always opens a flyout. **Avalonia-specific**. |

### Menu with Keyboard Shortcuts

```xml
<Menu DockPanel.Dock="Top">
    <MenuItem Header="_File">
        <MenuItem Header="_New" Command="{Binding NewCommand}"
                  InputGesture="Ctrl+N" />
        <MenuItem Header="_Open" Command="{Binding OpenCommand}"
                  InputGesture="Ctrl+O" />
        <Separator />
        <MenuItem Header="E_xit" Command="{Binding ExitCommand}"
                  InputGesture="Alt+F4" />
    </MenuItem>
    <MenuItem Header="_Edit">
        <MenuItem Header="_Undo" Command="{Binding UndoCommand}"
                  InputGesture="Ctrl+Z" />
    </MenuItem>
</Menu>
```

The underscore prefix (`_File`) marks the access key (Alt+F).

### SplitView (Navigation Pattern)

```xml
<SplitView IsPaneOpen="{Binding IsSidebarOpen}"
           DisplayMode="CompactInline"
           CompactPaneLength="48"
           OpenPaneLength="250">
    <SplitView.Pane>
        <ListBox ItemsSource="{Binding NavItems}" SelectedItem="{Binding SelectedNavItem}">
            <ListBox.ItemTemplate>
                <DataTemplate>
                    <StackPanel Orientation="Horizontal" Spacing="12">
                        <PathIcon Data="{Binding IconData}" Width="16" />
                        <TextBlock Text="{Binding Label}" />
                    </StackPanel>
                </DataTemplate>
            </ListBox.ItemTemplate>
        </ListBox>
    </SplitView.Pane>

    <!-- Main content area -->
    <ContentControl Content="{Binding CurrentPage}" />
</SplitView>
```

## Dialog and Overlay Controls

| Control | Description |
|---|---|
| `Window` | Top-level window. `ShowDialog()` for modal, `Show()` for modeless. |
| `Popup` | Floating overlay positioned relative to a placement target. |
| `NotificationManager` | Toast-style notifications. **Avalonia-specific**, no WPF equivalent. |
| `ThemeVariantScope` | Overrides light/dark theme for a subtree. **Avalonia-specific**. |

### Window Dialogs

```csharp
// Show modal dialog — awaits until dialog closes
var dialog = new SettingsWindow
{
    DataContext = new SettingsViewModel()
};
var result = await dialog.ShowDialog<bool>(parentWindow);
if (result)
{
    // User confirmed
}
```

```csharp
// In the dialog ViewModel or code-behind — close with result
window.Close(true);   // returns true to ShowDialog<bool>()
window.Close(false);  // returns false
```

### NotificationManager

```csharp
// Setup in your main window or a service
var notificationManager = new WindowNotificationManager(topLevel)
{
    Position = NotificationPosition.BottomRight,
    MaxItems = 3
};

// Show a notification
notificationManager.Show(new Notification(
    "Success",                              // title
    "File saved successfully.",             // message
    NotificationType.Success,               // type: Info, Success, Warning, Error
    TimeSpan.FromSeconds(3)                 // auto-close duration
));
```

### File Dialogs

Avalonia uses the platform's native file dialogs via the `StorageProvider` API:

```csharp
// Get StorageProvider from the TopLevel (Window)
var storage = TopLevel.GetTopLevel(this)?.StorageProvider;
if (storage is null) return;

// Open file picker
var files = await storage.OpenFilePickerAsync(new FilePickerOpenOptions
{
    Title = "Select a file",
    AllowMultiple = false,
    FileTypeFilter = new[]
    {
        new FilePickerFileType("Text Files") { Patterns = new[] { "*.txt", "*.csv" } },
        new FilePickerFileType("All Files") { Patterns = new[] { "*.*" } }
    }
});

if (files.Count > 0)
{
    await using var stream = await files[0].OpenReadAsync();
    // read the file
}
```

## Avalonia-Specific Controls (Not in WPF)

These controls exist in Avalonia but have **no WPF equivalent**:

| Control | Purpose |
|---|---|
| `ToggleSwitch` | iOS/Android-style on/off toggle |
| `SplitButton` | Button with primary action + dropdown for alternatives |
| `DropDownButton` | Button that always opens a flyout menu |
| `SelectableTextBlock` | Text that supports user selection and copy |
| `TreeDataGrid` | High-performance hierarchical/flat data grid (separate NuGet) |
| `NotificationManager` | Toast-style notification system |
| `ThemeVariantScope` | Override light/dark theme for a subtree |
| `ItemsRepeater` | Virtualizing layout repeater (ported from WinUI) |
