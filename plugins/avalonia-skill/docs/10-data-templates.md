# Data Templates & Collections

## DataTemplate Basics

A `DataTemplate` defines how a data object renders in the UI. Place it inline on any items control:

```xml
<ListBox ItemsSource="{Binding People}">
    <ListBox.ItemTemplate>
        <DataTemplate>
            <StackPanel Orientation="Horizontal" Spacing="8">
                <TextBlock Text="{Binding Name}" FontWeight="Bold" />
                <TextBlock Text="{Binding Email}" Foreground="Gray" />
            </StackPanel>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

**Key**: Without a `DataTemplate`, Avalonia calls `ToString()` on each item. You almost always want an explicit template.

## DataType Matching

Set `DataType` on a `DataTemplate` to auto-match by view model type. Avalonia walks up the visual tree looking for a template whose `DataType` matches the bound object's type.

```xml
<DataTemplate DataType="{x:Type vm:PersonViewModel}">
    <StackPanel Orientation="Horizontal" Spacing="8">
        <TextBlock Text="{Binding FullName}" />
        <TextBlock Text="{Binding Age}" Foreground="DimGray" />
    </StackPanel>
</DataTemplate>
```

Register these in `Application.DataTemplates` so they apply globally:

```xml
<Application.DataTemplates>
    <DataTemplate DataType="{x:Type vm:PersonViewModel}">
        <Border Padding="8" Background="WhiteSmoke" CornerRadius="4">
            <TextBlock Text="{Binding FullName}" />
        </Border>
    </DataTemplate>
    <DataTemplate DataType="{x:Type vm:OrderViewModel}">
        <StackPanel>
            <TextBlock Text="{Binding OrderNumber}" FontWeight="Bold" />
            <TextBlock Text="{Binding Total, StringFormat='Total: {0:C}'}" />
        </StackPanel>
    </DataTemplate>
</Application.DataTemplates>
```

When a `ContentControl` or items control encounters an object, it searches for a matching `DataType` template in this order: local resources, parent resources, application-level `DataTemplates`.

## IDataTemplate Interface

For programmatic template logic, implement `IDataTemplate`:

```csharp
public interface IDataTemplate
{
    bool Match(object? data);              // Does this template handle this data?
    Control? Build(object? data);          // Create the visual tree
}
```

## FuncDataTemplate

Quick inline templates in code, useful for prototyping or dynamic scenarios:

```csharp
var template = new FuncDataTemplate<PersonViewModel>((person, scope) =>
    new TextBlock { [!TextBlock.TextProperty] = new Binding("FullName") });
```

## Custom Template Selector

When you need different templates for different data types in the same list, implement `IDataTemplate` as a selector:

```csharp
public class AnimalTemplateSelector : IDataTemplate
{
    // Define inner templates as properties so they can be set in XAML
    public IDataTemplate? DogTemplate { get; set; }
    public IDataTemplate? CatTemplate { get; set; }

    public bool Match(object? data) => data is AnimalViewModel;

    public Control? Build(object? data)
    {
        return data switch
        {
            DogViewModel => DogTemplate?.Build(data),
            CatViewModel => CatTemplate?.Build(data),
            _ => new TextBlock { Text = "Unknown animal" }
        };
    }
}
```

Use it in XAML:

```xml
<UserControl.DataTemplates>
    <local:AnimalTemplateSelector>
        <local:AnimalTemplateSelector.DogTemplate>
            <DataTemplate DataType="{x:Type vm:DogViewModel}">
                <StackPanel Orientation="Horizontal" Spacing="8">
                    <PathIcon Data="{StaticResource DogIcon}" />
                    <TextBlock Text="{Binding Name}" />
                    <TextBlock Text="{Binding Breed}" Foreground="Gray" />
                </StackPanel>
            </DataTemplate>
        </local:AnimalTemplateSelector.DogTemplate>
        <local:AnimalTemplateSelector.CatTemplate>
            <DataTemplate DataType="{x:Type vm:CatViewModel}">
                <StackPanel Orientation="Horizontal" Spacing="8">
                    <PathIcon Data="{StaticResource CatIcon}" />
                    <TextBlock Text="{Binding Name}" />
                    <TextBlock Text="{Binding Indoor}" Foreground="Orange" />
                </StackPanel>
            </DataTemplate>
        </local:AnimalTemplateSelector.CatTemplate>
    </local:AnimalTemplateSelector>
</UserControl.DataTemplates>
```

## ItemsRepeater

`ItemsRepeater` is a virtualized, flexible items host ported from WinUI. It gives you **maximum layout control** with no built-in selection, scrolling, or chrome.

```xml
<ScrollViewer>
    <ItemsRepeater ItemsSource="{Binding Items}">
        <ItemsRepeater.Layout>
            <UniformGridLayout MinItemWidth="200" MinItemHeight="150"
                               MinRowSpacing="8" MinColumnSpacing="8" />
        </ItemsRepeater.Layout>
        <ItemsRepeater.ItemTemplate>
            <DataTemplate>
                <Border Background="White" CornerRadius="8" Padding="16" BoxShadow="0 2 8 0 #20000000">
                    <StackPanel Spacing="4">
                        <TextBlock Text="{Binding Title}" FontWeight="Bold" />
                        <TextBlock Text="{Binding Description}" TextWrapping="Wrap" />
                    </StackPanel>
                </Border>
            </DataTemplate>
        </ItemsRepeater.ItemTemplate>
    </ItemsRepeater>
</ScrollViewer>
```

**Always** wrap `ItemsRepeater` in a `ScrollViewer`. It does not provide its own scrolling.

### Layout Strategies

| Layout | Behavior | Use For |
|--------|----------|---------|
| `StackLayout` | Vertical or horizontal stack | Simple lists, chat messages |
| `UniformGridLayout` | Grid with equal-sized cells | Card grids, image galleries |
| `WrapLayout` | Wraps items to the next row/column | Tag clouds, chip lists |

```xml
<!-- Horizontal wrapping layout -->
<ItemsRepeater.Layout>
    <WrapLayout Orientation="Horizontal" HorizontalSpacing="8" VerticalSpacing="8" />
</ItemsRepeater.Layout>
```

### When to Use ItemsRepeater vs ListBox

| Scenario | Use |
|----------|-----|
| Need built-in selection | `ListBox` |
| Need custom grid/wrap layout | `ItemsRepeater` |
| No selection needed | `ItemsRepeater` |
| Maximum layout control | `ItemsRepeater` |
| Simple vertical list with selection | `ListBox` |

## Virtualization

Virtualization creates UI elements only for visible items, recycling them as the user scrolls. **Always virtualize lists with 50+ items.**

`ListBox` virtualizes by default. Confirm with:

```xml
<ListBox VirtualizationMode="Simple" ItemsSource="{Binding LargeCollection}" />
```

| VirtualizationMode | Behavior |
|-------------------|----------|
| `Simple` | Creates/destroys items as they scroll in/out |
| `None` | Creates all items up front -- use only for small lists |

`ItemsRepeater` virtualizes automatically when inside a `ScrollViewer`.

## TreeDataGrid

The official hierarchical data grid for Avalonia. Install the NuGet package:

```
dotnet add package Avalonia.Controls.TreeDataGrid
```

### Flat (Tabular) Data

```csharp
public class MainViewModel : ViewModelBase
{
    public FlatTreeDataGridSource<PersonViewModel> People { get; }

    public MainViewModel()
    {
        People = new FlatTreeDataGridSource<PersonViewModel>(_people)
        {
            Columns =
            {
                new TextColumn<PersonViewModel, string>("Name", x => x.Name),
                new TextColumn<PersonViewModel, int>("Age", x => x.Age),
                new CheckBoxColumn<PersonViewModel>("Active", x => x.IsActive),
            }
        };
    }
}
```

```xml
<TreeDataGrid Source="{Binding People}" />
```

### Hierarchical Data

```csharp
public class FileTreeViewModel : ViewModelBase
{
    public HierarchicalTreeDataGridSource<FileNodeViewModel> Files { get; }

    public FileTreeViewModel()
    {
        Files = new HierarchicalTreeDataGridSource<FileNodeViewModel>(_roots)
        {
            Columns =
            {
                new HierarchicalExpanderColumn<FileNodeViewModel>(
                    new TextColumn<FileNodeViewModel, string>("Name", x => x.Name),
                    x => x.Children),  // child selector
                new TextColumn<FileNodeViewModel, long>("Size", x => x.Size),
            }
        };
    }
}
```

### Column Types

| Column Type | Purpose |
|-------------|---------|
| `TextColumn<TModel, TValue>` | Text display and editing |
| `CheckBoxColumn<TModel>` | Boolean toggle |
| `HierarchicalExpanderColumn<TModel>` | Wraps another column with expand/collapse |
| `TemplateColumn<TModel>` | Custom cell template via `DataTemplate` |

## ObservableCollection

Use `ObservableCollection<T>` for lists that change at runtime. It notifies the UI on Add, Remove, and Clear.

```csharp
public ObservableCollection<TaskViewModel> Tasks { get; } = new();

public void AddTask(string title)
{
    Tasks.Add(new TaskViewModel { Title = title });
    // UI updates automatically -- no PropertyChanged needed for the collection itself
}
```

**Key**: `ObservableCollection` notifies on collection changes (add/remove), not on property changes within items. Each item must implement `INotifyPropertyChanged` independently.

For bulk operations, use `AddRange` via `System.Collections.ObjectModel` or consider `AvaloniaList<T>` which supports range operations natively.

## DataGrid

The classic data grid. Install the NuGet package:

```
dotnet add package Avalonia.Controls.DataGrid
```

```xml
<DataGrid ItemsSource="{Binding Employees}" AutoGenerateColumns="False"
          CanUserSortColumns="True" CanUserResizeColumns="True"
          IsReadOnly="False">
    <DataGrid.Columns>
        <DataGridTextColumn Header="Name" Binding="{Binding Name}" Width="*" />
        <DataGridTextColumn Header="Department" Binding="{Binding Department}" Width="150" />
        <DataGridCheckBoxColumn Header="Active" Binding="{Binding IsActive}" Width="80" />
        <DataGridTemplateColumn Header="Actions" Width="100">
            <DataGridTemplateColumn.CellTemplate>
                <DataTemplate>
                    <Button Content="Edit" Command="{Binding $parent[DataGrid].((vm:EmployeeListViewModel)DataContext).EditCommand}"
                            CommandParameter="{Binding}" />
                </DataTemplate>
            </DataGridTemplateColumn.CellTemplate>
        </DataGridTemplateColumn>
    </DataGrid.Columns>
</DataGrid>
```

**Never** use `AutoGenerateColumns="True"` in production. It exposes every public property, including ones not meant for display.

## Common Patterns

### Master-Detail

```xml
<Grid ColumnDefinitions="300,*">
    <!-- Master list -->
    <ListBox Grid.Column="0" ItemsSource="{Binding Items}"
             SelectedItem="{Binding SelectedItem}">
        <ListBox.ItemTemplate>
            <DataTemplate>
                <TextBlock Text="{Binding Title}" />
            </DataTemplate>
        </ListBox.ItemTemplate>
    </ListBox>

    <!-- Detail pane -->
    <ContentControl Grid.Column="1" Content="{Binding SelectedItem}"
                    Margin="16,0,0,0">
        <ContentControl.DataTemplates>
            <DataTemplate DataType="{x:Type vm:ItemViewModel}">
                <StackPanel Spacing="8">
                    <TextBlock Text="{Binding Title}" FontSize="24" FontWeight="Bold" />
                    <TextBlock Text="{Binding Description}" TextWrapping="Wrap" />
                    <TextBlock Text="{Binding CreatedDate, StringFormat='Created: {0:d}'}" Foreground="Gray" />
                </StackPanel>
            </DataTemplate>
        </ContentControl.DataTemplates>
    </ContentControl>
</Grid>
```

### Card Grid with ItemsRepeater

```xml
<ScrollViewer>
    <ItemsRepeater ItemsSource="{Binding Products}">
        <ItemsRepeater.Layout>
            <UniformGridLayout MinItemWidth="250" MinItemHeight="200"
                               MinRowSpacing="12" MinColumnSpacing="12"
                               ItemsJustification="Start" />
        </ItemsRepeater.Layout>
        <ItemsRepeater.ItemTemplate>
            <DataTemplate>
                <Border Background="{DynamicResource CardBackgroundFillColorDefaultBrush}"
                        CornerRadius="8" Padding="16"
                        BoxShadow="0 2 8 0 #20000000">
                    <StackPanel Spacing="8">
                        <TextBlock Text="{Binding Name}" FontWeight="SemiBold" FontSize="16" />
                        <TextBlock Text="{Binding Price, StringFormat='{}{0:C}'}" />
                        <TextBlock Text="{Binding Description}" TextWrapping="Wrap"
                                   MaxLines="3" TextTrimming="CharacterEllipsis" />
                    </StackPanel>
                </Border>
            </DataTemplate>
        </ItemsRepeater.ItemTemplate>
    </ItemsRepeater>
</ScrollViewer>
```
