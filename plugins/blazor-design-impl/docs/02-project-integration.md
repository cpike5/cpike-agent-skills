# Project Integration

The skill works in any Blazor project. Before writing any files, explore the target project to understand its structure.

## Step 1: Detect the Project Layout

Run these checks in the target directory:

### Find the static files root
Look for a `wwwroot/` folder. This is where token CSS files go.
- In a standard Blazor app: `wwwroot/css/`
- In a Razor class library being used as a host: same
- If no `wwwroot/` exists yet: create it

### Find the HTML host file
This is where the `<link>` tag for the design system stylesheet goes. Look for (in priority order):
1. `Pages/_Host.cshtml` — Blazor Server (pre-.NET 8 or explicit)
2. `Components/App.razor` or `App.razor` — .NET 8+ Blazor Web App with `<HeadContent>` or inline `<link>`
3. `wwwroot/index.html` — Blazor WebAssembly
4. A `_Layout.cshtml` that wraps everything

Read the file to understand the current CSS loading order and where to insert the new link.

### Find the component location
Look for where existing `.razor` components live:
- `Components/` folder — most common in .NET 8+ apps
- `Shared/` folder — older Blazor Server convention
- Alongside pages in `Pages/` — less common
- A separate class library project — if the user has a dedicated component project

**Ask the user** if there's ambiguity about where to put components. If no components exist yet, default to `Components/` (create it).

### Find `_Imports.razor`
There may be multiple (one per project, one per folder). Find the one closest to the component location — new `@using` statements go there.

### Determine the component namespace
Read the `.csproj` to find `<RootNamespace>` (or derive from the project name). Components go in `{RootNamespace}.Components` (or wherever they're placed — the folder structure determines the namespace with implicit usings).

---

## Step 2: Place the Design System CSS

### Token files
Copy the token CSS files from the design export's `tokens/` directory into the project.

**Recommended target:** `wwwroot/css/{design-name}/tokens/` or `wwwroot/css/tokens/` if there's nothing else there.

Use the design system's name (from `_ds_manifest.json` `namespace` field, simplified) as the subfolder name to avoid collisions with existing CSS.

Copy these files verbatim — they are production-ready:
`fonts.css`, `colors.css`, `typography.css`, `spacing.css`, `radius.css`, `shadows.css`, `motion.css`, `base.css`

### Entry point stylesheet
Create a `styles.css` (or `{design-name}.css`) in `wwwroot/css/` that imports the tokens in the order specified by `globalCssPaths` in the manifest:

```css
@import "tokens/fonts.css";
@import "tokens/colors.css";
@import "tokens/typography.css";
@import "tokens/spacing.css";
@import "tokens/radius.css";
@import "tokens/shadows.css";
@import "tokens/motion.css";
@import "tokens/base.css";
```

If you used a named subfolder, adjust paths: `@import "{design-name}/tokens/colors.css"`.

### App-level token overrides
Create `wwwroot/css/app-tokens.css` (only if one doesn't already exist):

```css
/*
  App-level design token overrides.
  Redefine any custom property here to customize the design system.

  Examples:
    --accent: #2563eb;                      swap brand accent to blue
    --radius-md: 8px;                       rounder corners app-wide
    --font-sans: "Inter", sans-serif;       swap the typeface
*/
```

---

## Step 3: Wire CSS into the Host File

Add the design system link **before** any existing app CSS (tokens must be declared before components that use them), and add the app-tokens override **after** it:

### `Pages/_Host.cshtml` (Blazor Server)
```html
<link rel="stylesheet" href="css/styles.css" />
<link rel="stylesheet" href="css/app-tokens.css" />
```
Insert after any framework CSS (Bootstrap etc.) but before the app's `site.css` and the scoped bundle.

Also add `data-theme="light"` to `<html>` if dark mode support is needed:
```html
<html lang="en" data-theme="light">
```

### `App.razor` (.NET 8+ Blazor Web App)
If the app uses a root `App.razor` with a `<HeadOutlet>`, add links to the `<head>`:
```razor
<head>
    ...
    <link rel="stylesheet" href="css/styles.css" />
    <link rel="stylesheet" href="css/app-tokens.css" />
    ...
</head>
```

### `wwwroot/index.html` (Blazor WASM)
```html
<link href="css/styles.css" rel="stylesheet" />
<link href="css/app-tokens.css" rel="stylesheet" />
```

### `_Layout.cshtml`
Same pattern as `_Host.cshtml`.

---

## Step 4: Add `@using` for Components

After placing component files, add a `@using` to the nearest `_Imports.razor`:

```razor
@using {Namespace.Of.Components.Folder}
```

If components are placed directly in the project root or a `Components/` folder, the namespace is typically `{RootNamespace}` or `{RootNamespace}.Components`. Derive it from the project structure.

---

## Decision Guide: Where to Put Components

| Scenario | Recommendation |
|---|---|
| Standalone Blazor app, `Components/` exists | Add `.razor` files there |
| Standalone Blazor app, no components yet | Create `Components/`, add there |
| App references a separate class library for UI | Add to the class library project, not the app |
| Existing design system / component library in repo | Ask the user — they may want a separate folder or a new project |
| Multi-app solution | Create a shared class library; add as project reference |

When uncertain, ask the user before placing files.
