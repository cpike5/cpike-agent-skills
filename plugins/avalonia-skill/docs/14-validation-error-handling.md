# Validation & Error Handling

Use `ObservableValidator` from CommunityToolkit.Mvvm with `DataAnnotations` for form validation. Use structured error handling patterns for async operations. **Never** swallow exceptions silently.

---

## INotifyDataErrorInfo with ObservableValidator

`ObservableValidator` implements `INotifyDataErrorInfo` and integrates with `DataAnnotations`. Avalonia automatically renders validation errors when the ViewModel reports them.

```
dotnet add package CommunityToolkit.Mvvm
dotnet add package System.ComponentModel.Annotations
```

### Full ViewModel Example

```csharp
using System.ComponentModel.DataAnnotations;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public partial class UserFormViewModel : ObservableValidator
{
    [ObservableProperty]
    [NotifyDataErrorInfo]
    [Required(ErrorMessage = "Name is required")]
    [MinLength(2, ErrorMessage = "Name must be at least 2 characters")]
    [MaxLength(100, ErrorMessage = "Name cannot exceed 100 characters")]
    private string _name = string.Empty;

    [ObservableProperty]
    [NotifyDataErrorInfo]
    [Required(ErrorMessage = "Email is required")]
    [EmailAddress(ErrorMessage = "Invalid email format")]
    private string _email = string.Empty;

    [ObservableProperty]
    [NotifyDataErrorInfo]
    [Range(18, 120, ErrorMessage = "Age must be between 18 and 120")]
    private int _age;

    [ObservableProperty]
    [NotifyDataErrorInfo]
    [RegularExpression(@"^\+?[\d\s\-]{7,15}$", ErrorMessage = "Invalid phone number")]
    private string _phone = string.Empty;

    [ObservableProperty]
    private bool _isSaving;

    [RelayCommand(CanExecute = nameof(CanSubmit))]
    private async Task SubmitAsync()
    {
        // Validate everything before submitting
        ValidateAllProperties();
        if (HasErrors) return;

        IsSaving = true;
        try
        {
            await _userService.CreateUserAsync(Name, Email, Age, Phone);
        }
        finally
        {
            IsSaving = false;
        }
    }

    private bool CanSubmit => !IsSaving;

    private readonly IUserService _userService;

    public UserFormViewModel(IUserService userService)
    {
        _userService = userService;
    }
}
```

**Key**: The `[NotifyDataErrorInfo]` attribute triggers validation on the property **every time it changes**. Without it, validation only runs when you call `ValidateAllProperties()` or `ValidateProperty()`.

---

## DataAnnotation Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `[Required]` | Field must have a value | `[Required(ErrorMessage = "Required")]` |
| `[MinLength]` / `[MaxLength]` | String or collection length bounds | `[MinLength(2)]` |
| `[EmailAddress]` | Email format validation | `[EmailAddress]` |
| `[Range]` | Numeric range | `[Range(1, 100)]` |
| `[RegularExpression]` | Pattern match | `[RegularExpression(@"^\d{5}$")]` |
| `[StringLength]` | Min and max length in one attribute | `[StringLength(50, MinimumLength = 2)]` |
| `[Compare]` | Must match another property | `[Compare(nameof(Password))]` |
| `[CustomValidation]` | Delegate to a static method | See below |

---

## Custom Validation

### CustomValidation Attribute

For logic that does not fit a built-in attribute, use `[CustomValidation]` pointing to a static method.

```csharp
public partial class EventFormViewModel : ObservableValidator
{
    [ObservableProperty]
    [NotifyDataErrorInfo]
    private DateTime _startDate = DateTime.Today;

    [ObservableProperty]
    [NotifyDataErrorInfo]
    [CustomValidation(typeof(EventFormViewModel), nameof(ValidateEndDate))]
    private DateTime _endDate = DateTime.Today.AddDays(1);

    // Static validation method — signature is fixed by the framework
    public static ValidationResult? ValidateEndDate(DateTime endDate, ValidationContext context)
    {
        var vm = (EventFormViewModel)context.ObjectInstance;
        if (endDate <= vm.StartDate)
            return new ValidationResult("End date must be after start date");

        return ValidationResult.Success;
    }
}
```

### Cross-Property Validation

When changing one property should re-validate another, use `[NotifyPropertyChangedFor]` to trigger the dependent property's validation.

```csharp
[ObservableProperty]
[NotifyDataErrorInfo]
[NotifyPropertyChangedFor(nameof(EndDate))]  // re-validates EndDate when StartDate changes
private DateTime _startDate;

[ObservableProperty]
[NotifyDataErrorInfo]
[CustomValidation(typeof(EventFormViewModel), nameof(ValidateEndDate))]
private DateTime _endDate;
```

---

## Error Display in AXAML

Avalonia's `DataValidationErrors` adorner renders automatically when the bound ViewModel implements `INotifyDataErrorInfo`. No special markup needed for basic error display.

```xml
<!-- Errors appear automatically below the TextBox -->
<TextBox Text="{Binding Name}" Watermark="Full Name" />
<TextBox Text="{Binding Email}" Watermark="Email" />
```

### Customizing the Error Template

Override the `DataValidationErrors` template to change how errors appear.

```xml
<Style Selector="DataValidationErrors">
    <Setter Property="Template">
        <ControlTemplate>
            <DockPanel>
                <ContentPresenter Name="PART_ContentPresenter"
                                  Content="{TemplateBinding Owner}" />
                <!-- Error messages below the control -->
                <ItemsRepeater DockPanel.Dock="Bottom"
                               Items="{TemplateBinding Errors}">
                    <ItemsRepeater.ItemTemplate>
                        <DataTemplate>
                            <TextBlock Text="{Binding}"
                                       Foreground="{DynamicResource SystemFillColorCritical}"
                                       FontSize="11"
                                       Margin="0,2,0,0" />
                        </DataTemplate>
                    </ItemsRepeater.ItemTemplate>
                </ItemsRepeater>
            </DockPanel>
        </ControlTemplate>
    </Setter>
</Style>
```

### Error Border Styling

Highlight invalid fields with a colored border.

```xml
<Style Selector="TextBox:error /template/ Border#PART_BorderElement">
    <Setter Property="BorderBrush" Value="{DynamicResource SystemFillColorCritical}" />
    <Setter Property="BorderThickness" Value="2" />
</Style>
```

---

## Global Exception Handling

Desktop apps must catch unhandled exceptions to log them and exit gracefully. Wire these up in `Program.cs` **before** building the Avalonia app.

```csharp
using Serilog;

public static class Program
{
    [STAThread]
    public static void Main(string[] args)
    {
        // Configure Serilog early (see observability doc)
        Log.Logger = new LoggerConfiguration()
            .WriteTo.File("logs/app-.log", rollingInterval: RollingInterval.Day)
            .CreateLogger();

        // Catch all unhandled exceptions on any thread
        AppDomain.CurrentDomain.UnhandledException += (sender, e) =>
        {
            Log.Fatal((Exception)e.ExceptionObject, "Unhandled exception");
            Log.CloseAndFlush();
        };

        // Catch unobserved Task exceptions (fire-and-forget async)
        TaskScheduler.UnobservedTaskException += (sender, e) =>
        {
            Log.Error(e.Exception, "Unobserved task exception");
            e.SetObserved();  // prevent process crash
        };

        try
        {
            BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);
        }
        catch (Exception ex)
        {
            Log.Fatal(ex, "Application terminated unexpectedly");
            throw;
        }
        finally
        {
            Log.CloseAndFlush();
        }
    }

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .LogToTrace();
}
```

### ReactiveUI Exception Handler

If using ReactiveUI, also set `RxApp.DefaultExceptionHandler` to catch exceptions from reactive pipelines.

```csharp
RxApp.DefaultExceptionHandler = Observer.Create<Exception>(ex =>
{
    Log.Error(ex, "Unhandled exception in reactive pipeline");
});
```

---

## Async Error Patterns

### Command with Error State

Expose `IsLoading` and `ErrorMessage` properties so the view can display loading and error states.

```csharp
public partial class DataViewModel : ObservableObject
{
    [ObservableProperty]
    private bool _isLoading;

    [ObservableProperty]
    private string? _errorMessage;

    [ObservableProperty]
    private ObservableCollection<Item> _items = new();

    [RelayCommand]
    private async Task LoadAsync(CancellationToken cancellationToken)
    {
        IsLoading = true;
        ErrorMessage = null;

        try
        {
            var result = await _dataService.GetItemsAsync(cancellationToken);
            Items = new ObservableCollection<Item>(result);
        }
        catch (OperationCanceledException)
        {
            // User cancelled — not an error
        }
        catch (HttpRequestException ex)
        {
            ErrorMessage = "Unable to connect to server. Check your network connection.";
            Log.Warning(ex, "Failed to load items");
        }
        catch (Exception ex)
        {
            ErrorMessage = "An unexpected error occurred. Please try again.";
            Log.Error(ex, "Unexpected error loading items");
        }
        finally
        {
            IsLoading = false;
        }
    }

    private readonly IDataService _dataService;

    public DataViewModel(IDataService dataService)
    {
        _dataService = dataService;
    }
}
```

### View Binding

```xml
<DockPanel>
    <!-- Error banner -->
    <Border DockPanel.Dock="Top"
            Background="{DynamicResource SystemFillColorCriticalBackground}"
            Padding="12"
            IsVisible="{Binding ErrorMessage, Converter={x:Static StringConverters.IsNotNullOrEmpty}}">
        <DockPanel>
            <Button DockPanel.Dock="Right" Content="Retry"
                    Command="{Binding LoadCommand}" />
            <TextBlock Text="{Binding ErrorMessage}"
                       Foreground="{DynamicResource SystemFillColorCritical}"
                       VerticalAlignment="Center" />
        </DockPanel>
    </Border>

    <!-- Loading indicator -->
    <ProgressBar DockPanel.Dock="Top"
                 IsIndeterminate="True"
                 IsVisible="{Binding IsLoading}" />

    <!-- Content -->
    <ListBox Items="{Binding Items}" />
</DockPanel>
```

### CancellationToken Support

`[RelayCommand]` automatically generates a `CancellationToken` parameter and a cancel command when the method accepts one.

```csharp
// Source generator creates:
// - LoadCommand (IAsyncRelayCommand)
// - LoadCancelCommand (ICommand) — cancels the running operation
[RelayCommand]
private async Task LoadAsync(CancellationToken cancellationToken)
{
    await _service.LoadAsync(cancellationToken);
}
```

```xml
<Button Content="Load" Command="{Binding LoadCommand}" />
<Button Content="Cancel" Command="{Binding LoadCancelCommand}" />
```

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Not calling `ValidateAllProperties()` before submit | Untouched fields never validated | **Always** call in submit command |
| Missing `[NotifyDataErrorInfo]` on property | Validation only runs on manual call | Add attribute for live validation |
| Blocking UI thread with sync validation | Frozen UI during complex checks | Use async validation or background thread |
| Not showing errors inline | User doesn't know which field failed | Bind to `DataValidationErrors` (automatic with `INotifyDataErrorInfo`) |
| Swallowing exceptions with empty catch | Silent failures, impossible to debug | Log every exception, show user-friendly message |
| Generic error messages | User can't recover | Be specific: "Network error" vs "An error occurred" |
| Not handling `OperationCanceledException` | Cancelled operations show as errors | Catch separately, treat as non-error |
| Missing global exception handlers | App crashes without any log | Wire up `AppDomain` and `TaskScheduler` handlers in `Program.cs` |
