# Forms and Validation

## EditForm

Blazor's primary form component. Creates an `EditContext` internally to track field values, modification state, and validation.

### Key Parameters

| Parameter | Description |
|---|---|
| `Model` | Object to bind. Mutually exclusive with `EditContext`. |
| `EditContext` | Direct access to context. Mutually exclusive with `Model`. |
| `OnValidSubmit` | Called when submitted and all validation passes |
| `OnInvalidSubmit` | Called when submitted with validation errors |
| `OnSubmit` | Called unconditionally — you call `editContext.Validate()` yourself |
| `FormName` | **Required** unique name for SSR form handling |
| `Enhance` | Enables enhanced form posting (SPA-like on SSR) |

### Basic Form

```razor
@page "/edit-user"

<EditForm Model="Model" OnValidSubmit="Submit" FormName="EditUser">
    <DataAnnotationsValidator />
    <ValidationSummary />

    <label>
        Name:
        <InputText @bind-Value="Model!.Name" />
        <ValidationMessage For="@(() => Model!.Name)" />
    </label>

    <button type="submit">Submit</button>
</EditForm>

@code {
    [SupplyParameterFromForm]
    private UserModel? Model { get; set; }

    protected override void OnInitialized() => Model ??= new();

    private void Submit() => Logger.LogInformation("Name = {Name}", Model?.Name);
}
```

### SSR Form Requirements

1. Always add `FormName` — used for routing POST data
2. Use `[SupplyParameterFromForm]` on the model property
3. Initialize model with null-coalescing: `Model ??= new()`
4. For plain HTML `<form>`, add `<AntiforgeryToken />` manually
5. Client-side field validation is NOT available — all validation on server after submit

### Enhanced Form Handling (SSR)

Intercepts POST, applies DOM diff instead of full page reload:

```razor
<EditForm ... Enhance>
    ...
</EditForm>

<!-- Or for HTML forms -->
<form ... data-enhance>
    ...
</form>
```

## Input Components

All inherit `InputBase<TValue>`, integrate with `EditContext`, emit CSS classes `valid`/`invalid`/`modified`.

| Component | HTML Element | Value Type |
|---|---|---|
| `InputText` | `<input type="text">` | `string` |
| `InputNumber<T>` | `<input type="number">` | numeric |
| `InputDate<T>` | `<input type="date">` | `DateTime`, `DateOnly` |
| `InputSelect<T>` | `<select>` | enum or any |
| `InputCheckbox` | `<input type="checkbox">` | `bool` |
| `InputTextArea` | `<textarea>` | `string` |
| `InputRadio<T>` | `<input type="radio">` | any |
| `InputRadioGroup<T>` | container | groups `InputRadio` |
| `InputFile` | `<input type="file">` | `IBrowserFile` |

All bind via `@bind-Value` and accept additional HTML attributes (class, placeholder, disabled, etc.).

```razor
<InputText @bind-Value="Model.Name" placeholder="Enter name" class="form-control" />
<InputNumber @bind-Value="Model.Age" />
<InputSelect @bind-Value="Model.Category">
    <option value="">Select...</option>
    <option value="A">Category A</option>
</InputSelect>
<InputCheckbox @bind-Value="Model.IsActive" />
```

## DataAnnotationsValidator

Wires up `System.ComponentModel.DataAnnotations` validation. Two-phase: field validation on blur, model validation on submit.

```csharp
public class ContactModel
{
    [Required(ErrorMessage = "Name is required.")]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;

    [Required, EmailAddress]
    public string Email { get; set; } = string.Empty;

    [Range(1, 120)]
    public int Age { get; set; }

    [MinLength(8)]
    public string Password { get; set; } = string.Empty;

    [Compare(nameof(Password), ErrorMessage = "Passwords do not match.")]
    public string ConfirmPassword { get; set; } = string.Empty;
}
```

**Note**: `[Remote]` attribute is NOT supported in Blazor.

### Nested Object Validation (.NET 10+)

```csharp
// Program.cs
builder.Services.AddValidation();

// Model (must be in .cs file, not .razor)
[ValidatableType]
public class Order
{
    public Customer Customer { get; set; } = new();
    public List<OrderItem> Items { get; set; } = [];
}
```

## ValidationSummary and ValidationMessage

```razor
<!-- All validation messages -->
<ValidationSummary />

<!-- Messages for specific field -->
<ValidationMessage For="@(() => Model!.Name)" />
```

## EditContext — Advanced Scenarios

Use `EditContext` directly for manual validation, custom validators, or server-side validation errors.

### Key Members

| Member | Description |
|---|---|
| `Validate()` | Run all validators, returns bool |
| `IsValid(fieldIdentifier)` | Check if field is valid |
| `IsModified(fieldIdentifier)` | Check if field was modified |
| `OnFieldChanged` | Event when any field changes |
| `OnValidationRequested` | Event when validation triggers |
| `NotifyFieldChanged(field)` | Manually signal field change |
| `NotifyValidationStateChanged()` | Re-display validation messages |
| `MarkAsUnmodified()` | Reset modification state |

### Custom Validator Component

```csharp
public class CustomValidation : ComponentBase
{
    private ValidationMessageStore? messageStore;

    [CascadingParameter]
    private EditContext? CurrentEditContext { get; set; }

    protected override void OnInitialized()
    {
        if (CurrentEditContext is null)
            throw new InvalidOperationException("Requires EditContext");

        messageStore = new(CurrentEditContext);
        CurrentEditContext.OnValidationRequested += (s, e) => messageStore?.Clear();
        CurrentEditContext.OnFieldChanged += (s, e) =>
            messageStore?.Clear(e.FieldIdentifier);
    }

    public void DisplayErrors(Dictionary<string, List<string>> errors)
    {
        foreach (var err in errors)
            messageStore?.Add(CurrentEditContext!.Field(err.Key), err.Value);
        CurrentEditContext!.NotifyValidationStateChanged();
    }

    public void ClearErrors()
    {
        messageStore?.Clear();
        CurrentEditContext?.NotifyValidationStateChanged();
    }
}
```

Usage with server API validation:

```razor
<EditForm Model="Model" OnValidSubmit="Submit">
    <DataAnnotationsValidator />
    <CustomValidation @ref="customValidation" />
    <ValidationSummary />
    <!-- fields... -->
</EditForm>

@code {
    private CustomValidation? customValidation;

    private async Task Submit()
    {
        var response = await Http.PostAsJsonAsync("api/validate", Model);
        if (response.StatusCode == HttpStatusCode.BadRequest)
        {
            var errors = await response.Content
                .ReadFromJsonAsync<Dictionary<string, List<string>>>();
            customValidation?.DisplayErrors(errors!);
        }
    }
}
```

## Custom Input Components

Inherit from `InputBase<T>` for full EditContext integration.

### Quick Override (change bind event)

```razor
@* CustomInputText.razor — validates on every keystroke *@
@inherits InputText

<input @attributes="AdditionalAttributes"
       class="@CssClass"
       @bind="CurrentValueAsString"
       @bind:event="oninput" />
```

### Full Custom Input

```razor
@inherits InputBase<int>
@* Star rating input *@

@for (int i = 1; i <= 5; i++)
{
    var star = i;
    <span class="@(star <= CurrentValue ? "filled" : "empty")"
          @onclick="() => CurrentValue = star">&#9733;</span>
}

@code {
    protected override bool TryParseValueFromString(
        string? value, out int result, out string? validationErrorMessage)
    {
        if (int.TryParse(value, out result))
        {
            validationErrorMessage = null;
            return true;
        }
        validationErrorMessage = "Invalid rating.";
        result = 0;
        return false;
    }
}
```

## IValidatableObject (Cross-Field Validation)

Runs only after all field-level validations pass.

```csharp
public class Registration : IValidatableObject
{
    [Required] public string? Classification { get; set; }
    public string? Description { get; set; }

    public IEnumerable<ValidationResult> Validate(ValidationContext ctx)
    {
        if (Classification == "Defense" && string.IsNullOrEmpty(Description))
            yield return new ValidationResult(
                "Defense requires a description.", new[] { nameof(Description) });
    }
}
```

## Form Handling by Render Mode

| Render Mode | Field Validation | Submit Validation | Notes |
|---|---|---|---|
| Static SSR | Server-side only (on submit) | Yes | Requires `FormName`, `[SupplyParameterFromForm]` |
| Interactive Server | Real-time (active circuit) | Yes | Full client-side experience |
| Interactive WASM | Real-time (in browser) | Yes | Runs in browser WASM |
| Auto | Once interactive | Yes | May start static, transitions |

## Key Gotchas

1. `FormName` is **mandatory** for SSR forms — without it, Blazor can't dispatch the POST
2. `[SupplyParameterFromForm]` must be on a **property**, not a field
3. Never use both `Model` and `EditContext` on the same `EditForm`
4. Custom validation attributes must include `validationContext.MemberName` in results
5. Always unsubscribe from `EditContext` events in `Dispose`
6. For SSR: use a separate DTO to prevent overposting (don't bind entities directly)
