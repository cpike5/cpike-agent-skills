# MVVM & Application Architecture

## CommunityToolkit.Mvvm (Recommended)

CommunityToolkit.Mvvm is the **recommended** MVVM framework for Avalonia. It uses source generators to eliminate boilerplate. No Avalonia-specific dependency required.

```
dotnet add package CommunityToolkit.Mvvm
```

### ViewModel Example

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public partial class MainViewModel : ObservableObject
{
    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(FullName))]  // raises PropertyChanged for FullName too
    [NotifyCanExecuteChangedFor(nameof(SaveCommand))]  // re-evaluates CanSave
    private string _firstName = string.Empty;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(FullName))]
    private string _lastName = string.Empty;

    [ObservableProperty]
    private bool _isBusy;

    public string FullName => $"{FirstName} {LastName}".Trim();

    [RelayCommand(CanExecute = nameof(CanSave))]
    private async Task SaveAsync()
    {
        IsBusy = true;
        try
        {
            await _repository.SaveAsync(FirstName, LastName);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanSave => !string.IsNullOrWhiteSpace(FirstName)
                         && !string.IsNullOrWhiteSpace(LastName)
                         && !IsBusy;

    private readonly IRepository _repository;

    public MainViewModel(IRepository repository)
    {
        _repository = repository;
    }
}
```

### Key Attributes

| Attribute | Purpose |
|-----------|---------|
| `[ObservableProperty]` | Generates property with `OnPropertyChanged` from a field |
| `[RelayCommand]` | Generates `ICommand` from a method |
| `[NotifyPropertyChangedFor]` | Also raises `PropertyChanged` for dependent properties |
| `[NotifyCanExecuteChangedFor]` | Re-evaluates `CanExecute` on the named command |
| `ObservableObject` | Base class providing `INotifyPropertyChanged` |
| `ObservableValidator` | Base class adding `INotifyDataErrorInfo` for validation |

### Validation with ObservableValidator

```csharp
public partial class RegistrationViewModel : ObservableValidator
{
    [ObservableProperty]
    [Required(ErrorMessage = "Email is required")]
    [EmailAddress(ErrorMessage = "Invalid email")]
    private string _email = string.Empty;

    [RelayCommand]
    private void Submit()
    {
        ValidateAllProperties();
        if (HasErrors) return;
        // proceed
    }
}
```

## ReactiveUI Alternative

ReactiveUI is a mature alternative with deeper reactive programming support.

```
dotnet add package Avalonia.ReactiveUI
```

```csharp
public class SearchViewModel : ReactiveObject
{
    private string _query = string.Empty;
    public string Query
    {
        get => _query;
        set => this.RaiseAndSetIfChanged(ref _query, value);
    }

    // Read-only property driven by an observable
    private readonly ObservableAsPropertyHelper<bool> _hasResults;
    public bool HasResults => _hasResults.Value;

    public ReactiveCommand<Unit, Unit> SearchCommand { get; }

    public SearchViewModel(ISearchService searchService)
    {
        var canSearch = this.WhenAnyValue(x => x.Query, q => !string.IsNullOrWhiteSpace(q));

        SearchCommand = ReactiveCommand.CreateFromTask(
            async () => { /* search logic */ },
            canSearch);

        _hasResults = this.WhenAnyValue(x => x.Query)
            .Select(q => !string.IsNullOrEmpty(q))
            .ToProperty(this, x => x.HasResults);
    }
}
```

**Use CommunityToolkit.Mvvm** unless you need reactive pipelines (`WhenAnyValue`, throttle, merge). Most apps don't.

## ViewLocator Pattern

A `ViewLocator` maps ViewModels to Views by naming convention, so you never manually wire them.

```csharp
public class ViewLocator : IDataTemplate
{
    public Control? Build(object? param)
    {
        if (param is null) return null;

        // MyApp.ViewModels.HomeViewModel → MyApp.Views.HomeView
        var vmName = param.GetType().FullName!;
        var viewName = vmName.Replace("ViewModel", "View");
        var viewType = Type.GetType(viewName);

        if (viewType != null)
            return (Control)Activator.CreateInstance(viewType)!;

        return new TextBlock { Text = $"View not found: {viewName}" };
    }

    public bool Match(object? data) => data is ObservableObject;
}
```

Register it in `App.axaml`:

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:local="using:MyApp">
    <Application.DataTemplates>
        <local:ViewLocator />
    </Application.DataTemplates>
</Application>
```

## DI Setup with IServiceCollection

Wire up dependency injection in `App.axaml.cs`. This pattern works for `IClassicDesktopStyleApplicationLifetime`.

```csharp
public partial class App : Application
{
    private ServiceProvider? _serviceProvider;

    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        var services = new ServiceCollection();
        ConfigureServices(services);
        _serviceProvider = services.BuildServiceProvider();

        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = new MainWindow
            {
                DataContext = _serviceProvider.GetRequiredService<MainViewModel>()
            };
        }

        base.OnFrameworkInitializationCompleted();
    }

    private static void ConfigureServices(IServiceCollection services)
    {
        // Services
        services.AddSingleton<INavigationService, NavigationService>();
        services.AddSingleton<IDialogService, DialogService>();
        services.AddSingleton<IRepository, SqliteRepository>();

        // ViewModels — transient so each navigation gets a fresh instance
        services.AddTransient<MainViewModel>();
        services.AddTransient<SettingsViewModel>();
        services.AddTransient<HomeViewModel>();
    }
}
```

### Service Registration Patterns

| Lifetime | Use For | Example |
|----------|---------|---------|
| `AddSingleton` | Shared app state, navigation, settings | `INavigationService`, `AppState` |
| `AddTransient` | Per-view ViewModels, short-lived services | `HomeViewModel`, `IFileExporter` |
| `AddScoped` | Rarely used in desktop apps | Per-operation contexts |

## Navigation Service Pattern

Use a `ContentControl` as a shell with `DataTemplate`-based view resolution.

### Interface

```csharp
public interface INavigationService
{
    ViewModelBase CurrentViewModel { get; }
    void NavigateTo<T>() where T : ViewModelBase;
    bool CanGoBack { get; }
    void GoBack();
}
```

### Implementation

```csharp
public class NavigationService : ObservableObject, INavigationService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly Stack<ViewModelBase> _backStack = new();

    [ObservableProperty]
    private ViewModelBase _currentViewModel = default!;

    public bool CanGoBack => _backStack.Count > 0;

    public NavigationService(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }

    public void NavigateTo<T>() where T : ViewModelBase
    {
        if (CurrentViewModel is not null)
            _backStack.Push(CurrentViewModel);

        CurrentViewModel = _serviceProvider.GetRequiredService<T>();
    }

    public void GoBack()
    {
        if (_backStack.TryPop(out var previous))
            CurrentViewModel = previous;
    }
}
```

### Shell View

```xml
<Window xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        x:Class="MyApp.Views.MainWindow">
    <DockPanel>
        <Menu DockPanel.Dock="Top">
            <MenuItem Header="Back" Command="{Binding GoBackCommand}" />
        </Menu>

        <!-- ContentControl resolves View from ViewModel via ViewLocator -->
        <ContentControl Content="{Binding NavigationService.CurrentViewModel}" />
    </DockPanel>
</Window>
```

## DataTemplate-Based View Resolution

Define explicit mappings in `App.axaml` when you want fine-grained control instead of a ViewLocator:

```xml
<Application.DataTemplates>
    <DataTemplate DataType="{x:Type vm:HomeViewModel}">
        <views:HomeView />
    </DataTemplate>
    <DataTemplate DataType="{x:Type vm:SettingsViewModel}">
        <views:SettingsView />
    </DataTemplate>
</Application.DataTemplates>
```

This approach and the `ViewLocator` approach both work. Pick one and stay consistent.

## Dialog Service Abstraction

ViewModels should **never** reference `Window` or any UI type. Abstract dialogs behind an interface.

```csharp
public interface IDialogService
{
    Task<string?> ShowOpenFileDialogAsync(string title, string filter);
    Task<bool> ShowConfirmationAsync(string title, string message);
    Task ShowMessageAsync(string title, string message);
}
```

```csharp
public class DialogService : IDialogService
{
    private readonly Func<Window> _getMainWindow;

    public DialogService(Func<Window> getMainWindow)
    {
        _getMainWindow = getMainWindow;
    }

    public async Task<bool> ShowConfirmationAsync(string title, string message)
    {
        // Implementation uses the platform window handle
        var window = _getMainWindow();
        // Show dialog using Avalonia's dialog APIs
        // Return true/false based on user choice
    }
}
```

## Command Binding in AXAML

```xml
<Button Content="Save"
        Command="{Binding SaveCommand}" />

<Button Content="Delete"
        Command="{Binding DeleteCommand}"
        CommandParameter="{Binding SelectedItem}" />

<!-- Disable button automatically when command can't execute -->
<Button Content="Submit"
        Command="{Binding SubmitCommand}"
        IsEnabled="{Binding SubmitCommand.CanExecute}" />  <!-- automatic with ICommand -->
```

**Key**: When using `[RelayCommand]`, the generated command automatically disables the button when `CanExecute` returns false. No extra `IsEnabled` binding needed.

## Anti-Patterns

| Anti-Pattern | Problem | Do This Instead |
|-------------|---------|-----------------|
| Business logic in code-behind | Untestable, tightly coupled | Put logic in ViewModel or services |
| ViewModel references `Window` | Breaks testability, couples to UI | Use `IDialogService` abstraction |
| Creating ViewModels in XAML | No constructor injection possible | Resolve from DI container |
| Static mutable state | Race conditions, test pollution | Use singleton services via DI |
| Blocking UI thread with `.Result` | Frozen UI, potential deadlock | Use `async/await` throughout |
| Fat ViewModels (500+ lines) | Hard to maintain and test | Extract logic into services |
| Manual `PropertyChanged` everywhere | Error-prone, verbose | Use `[ObservableProperty]` source gen |
