---
name: avalonia
description: "Use this skill when building Avalonia or WPF desktop applications, creating cross-platform desktop UI, or working with .axaml files. Covers Avalonia 11.x framework setup, layout system (Grid, StackPanel, DockPanel, WrapPanel, Canvas), core controls (Button, TextBox, ComboBox, DataGrid, TreeView, TreeDataGrid, ItemsRepeater, ToggleSwitch, SplitButton), CSS-like styling and theming (Fluent theme, Simple theme, light/dark mode, ControlThemes, style selectors, pseudo-classes), data binding (compiled bindings, x:DataType, element/self/parent binding, converters), MVVM architecture (CommunityToolkit.Mvvm, ReactiveUI, ViewLocator, DI setup, navigation patterns, dialog services), custom controls (UserControl, TemplatedControl, StyledProperty, DirectProperty, AttachedProperty), events and input handling (routed events, pointer events, keyboard events, gestures, focus management), animations and transitions (implicit transitions, keyframe animations, page transitions, easing functions), data templates and collections (DataTemplate, IDataTemplate, template selectors, virtualization, TreeDataGrid), cross-platform integration (IStorageProvider file dialogs, clipboard, drag-drop, system tray, NativeMenu, window customization, avares:// assets), desktop UI design principles (information density, navigation patterns, typography, color/theming, Fluent Design, form layout, geometry), interaction and UX patterns (keyboard-first design, accessibility, progress indicators, notifications, confirmation/undo), validation and error handling (INotifyDataErrorInfo, ObservableValidator, DataAnnotations, global exception handling), testing and deployment (ViewModel unit testing, Avalonia.Headless, publishing, MSIX, DMG, AppImage, Velopack, NativeAOT), and desktop observability (Serilog for desktop, crash reporting, performance diagnostics, offline telemetry). Invoke when: creating or modifying .axaml files, building desktop applications with Avalonia or WPF, implementing MVVM patterns for desktop, configuring Avalonia styling or theming, working with Avalonia controls or custom controls, setting up cross-platform desktop deployment, debugging Avalonia-specific issues (binding errors, styling not applying, platform differences), designing desktop UI layouts, or when the user asks about Avalonia or WPF patterns."
---

# Avalonia Desktop Development Knowledge Base

You are building a cross-platform desktop application with Avalonia. Read the relevant reference docs below based on what you're building. **Always use compiled bindings** and **always set up DI properly** — these are the foundation of a well-structured Avalonia app.

## Design Thinking

Desktop apps have different constraints than web or mobile. Embrace **keyboard-first interaction**, **higher information density**, and **platform integration**. Support light/dark mode from day one. Use the Fluent theme as your starting point and customize from there. See `12-desktop-ui-design.md` for navigation patterns, typography, spacing, and layout guidance specific to desktop.

## Quick Decision: Which MVVM Framework?

- Need simplicity and source generators? → **CommunityToolkit.Mvvm** (recommended)
- Need reactive streams and complex async chains? → **ReactiveUI**
- Need modular app with regions and navigation? → **Prism.Avalonia**

If bindings don't work, CHECK COMPILED BINDINGS FIRST — ensure `x:DataType` is set on the view and properties exist on the ViewModel.

## Reference Documentation

Read the relevant docs based on your task:

### Always Read First
- ${CLAUDE_PLUGIN_ROOT}/docs/01-framework-overview.md — Project setup, Avalonia vs WPF differences, DI registration, compiled bindings configuration
- ${CLAUDE_PLUGIN_ROOT}/docs/04-styling-theming.md — CSS-like selectors, themes, light/dark mode, ControlThemes. Styling works fundamentally differently from WPF.

### Core Development (read as needed)
- ${CLAUDE_PLUGIN_ROOT}/docs/02-layout-system.md — Panels, Grid shorthand, sizing, alignment, spacing system, responsive patterns
- ${CLAUDE_PLUGIN_ROOT}/docs/03-controls.md — Complete control reference by category with Avalonia-specific controls highlighted
- ${CLAUDE_PLUGIN_ROOT}/docs/05-data-binding.md — Binding syntax, compiled bindings, element/parent bindings, converters, DataContext
- ${CLAUDE_PLUGIN_ROOT}/docs/06-mvvm-architecture.md — CommunityToolkit.Mvvm, ReactiveUI, ViewLocator, DI, navigation, dialog services

### Advanced Patterns
- ${CLAUDE_PLUGIN_ROOT}/docs/07-custom-controls.md — UserControl vs TemplatedControl, StyledProperty vs DirectProperty, template parts, custom pseudo-classes
- ${CLAUDE_PLUGIN_ROOT}/docs/08-events-input.md — Routed events, pointer/keyboard/gesture events, focus management, ClassHandler, event-to-command patterns
- ${CLAUDE_PLUGIN_ROOT}/docs/09-animations-transitions.md — Transitions, keyframe animations, page transitions, easing, RenderTransform animations
- ${CLAUDE_PLUGIN_ROOT}/docs/10-data-templates.md — DataTemplate, IDataTemplate, template selectors, ItemsRepeater, virtualization, TreeDataGrid

### Platform & Integration
- ${CLAUDE_PLUGIN_ROOT}/docs/11-platform-integration.md — File dialogs, clipboard, drag-drop, system tray, NativeMenu, window customization, asset loading, multi-monitor

### Design & UX
- ${CLAUDE_PLUGIN_ROOT}/docs/12-desktop-ui-design.md — Navigation patterns, typography, color/theming, form layout, geometry, Fluent Design principles, desktop-specific design guidance
- ${CLAUDE_PLUGIN_ROOT}/docs/13-interaction-ux.md — Keyboard-first design, accessibility, progress indicators, notifications, confirmation/undo, selection patterns

### Quality & Ship
- ${CLAUDE_PLUGIN_ROOT}/docs/14-validation-error-handling.md — INotifyDataErrorInfo, ObservableValidator, DataAnnotations, global exception handling, async error patterns
- ${CLAUDE_PLUGIN_ROOT}/docs/15-testing-deployment.md — ViewModel testing, Avalonia.Headless, publishing, platform packaging (MSIX, DMG, AppImage), Velopack, NativeAOT
- ${CLAUDE_PLUGIN_ROOT}/docs/16-observability-integration.md — Serilog for desktop, crash reporting, performance diagnostics, offline telemetry, privacy. For foundational observability patterns, see the observability-skill plugin.

## Critical Rules

1. **Use compiled bindings everywhere** — Set `<AvaloniaUseCompiledBindingsByDefault>true</AvaloniaUseCompiledBindingsByDefault>` in the project. Always set `x:DataType` on views. Compiled bindings catch errors at build time and are required for AOT.
2. **Never block the UI thread** — Use `async/await` for all I/O. Use `Task.Run()` for CPU-bound work. Never call `.Result` or `.Wait()` from the UI thread.
3. **Always virtualize large lists** — Use `ItemsRepeater` or `ListBox` with virtualization for 50+ items. Never use `StackPanel` inside `ScrollViewer` for large collections.
4. **Styling uses CSS-like selectors, not WPF triggers** — There are no `DataTrigger` or `EventTrigger` in Avalonia. Use style selectors with pseudo-classes (`:pointerover`, `:pressed`, `:disabled`) or bindings with converters.
5. **ControlTheme replaces implicit ControlTemplate** — In Avalonia 11, use `ControlTheme` for custom control appearance, not WPF-style implicit styles with templates.
6. **DI over service locators** — Register services in `IServiceCollection`. Inject via constructor. ViewModels should never reference View types.
7. **Use avares:// for embedded assets** — Not `pack://` (WPF). Set build action to `AvaloniaResource`.
8. **IStorageProvider for file dialogs** — The old `OpenFileDialog` is obsolete. Use `TopLevel.StorageProvider` for cross-platform file/folder access.
9. **Support light and dark mode** — Use `DynamicResource` for theme-aware colors. Test both variants. Use `ThemeVariantScope` for per-subtree overrides.
10. **Keyboard accessibility is mandatory** — Every interactive element must be reachable via Tab. Provide keyboard shortcuts for common actions. Support high-contrast themes.
11. **Dispose event subscriptions** — Unsubscribe from events to prevent memory leaks. Use `CompositeDisposable` with ReactiveUI. Implement `IDisposable` on ViewModels that hold subscriptions.
12. **Platform-test on all targets** — Keyboard shortcuts, fonts, window chrome, and file dialogs behave differently on Windows, macOS, and Linux. Test cross-platform or guard with `OperatingSystem.Is*()`.
