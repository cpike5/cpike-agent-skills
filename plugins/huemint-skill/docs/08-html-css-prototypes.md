# HTML/CSS Prototypes

After generating a palette with Huemint, build an HTML/CSS prototype to showcase the colors in context.

## CSS Custom Properties Setup

Map palette results to semantic CSS custom properties:

```css
:root {
  /* Huemint palette result */
  --color-bg: #F8F9FA;
  --color-surface: #FFFFFF;
  --color-text: #1A1A2E;
  --color-primary: #2563EB;
  --color-accent: #F59E0B;

  /* Derived values */
  --color-text-muted: color-mix(in srgb, var(--color-text) 60%, transparent);
  --color-primary-hover: color-mix(in srgb, var(--color-primary) 85%, black);
  --color-surface-elevated: color-mix(in srgb, var(--color-surface) 95%, var(--color-primary));
}
```

Always use custom properties so the palette can be swapped by changing a few values.

## Color Swatch Grid

Display the palette with labeled swatches:

```html
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; padding: 24px;">

  <div style="text-align: center;">
    <div style="background: var(--color-bg); width: 100%; height: 80px; border-radius: 12px; border: 1px solid #e0e0e0;"></div>
    <code style="font-size: 13px; margin-top: 8px; display: block;">Background<br>#F8F9FA</code>
  </div>

  <div style="text-align: center;">
    <div style="background: var(--color-surface); width: 100%; height: 80px; border-radius: 12px; border: 1px solid #e0e0e0;"></div>
    <code style="font-size: 13px; margin-top: 8px; display: block;">Surface<br>#FFFFFF</code>
  </div>

  <div style="text-align: center;">
    <div style="background: var(--color-text); width: 100%; height: 80px; border-radius: 12px;"></div>
    <code style="font-size: 13px; margin-top: 8px; display: block;">Text<br>#1A1A2E</code>
  </div>

  <div style="text-align: center;">
    <div style="background: var(--color-primary); width: 100%; height: 80px; border-radius: 12px;"></div>
    <code style="font-size: 13px; margin-top: 8px; display: block;">Primary<br>#2563EB</code>
  </div>

  <div style="text-align: center;">
    <div style="background: var(--color-accent); width: 100%; height: 80px; border-radius: 12px;"></div>
    <code style="font-size: 13px; margin-top: 8px; display: block;">Accent<br>#F59E0B</code>
  </div>

</div>
```

## Component Showcase

### Buttons

```html
<div style="display: flex; gap: 12px; flex-wrap: wrap; padding: 24px;">
  <button style="background: var(--color-primary); color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer;">
    Primary Action
  </button>
  <button style="background: transparent; color: var(--color-primary); border: 2px solid var(--color-primary); padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer;">
    Secondary
  </button>
  <button style="background: var(--color-accent); color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer;">
    Accent Action
  </button>
</div>
```

### Cards

```html
<div style="background: var(--color-surface); border-radius: 16px; padding: 24px; max-width: 360px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
  <div style="background: var(--color-primary); height: 8px; border-radius: 4px; margin-bottom: 16px; width: 60px;"></div>
  <h3 style="color: var(--color-text); margin: 0 0 8px 0; font-size: 18px;">Card Title</h3>
  <p style="color: var(--color-text-muted); margin: 0 0 16px 0; font-size: 14px; line-height: 1.5;">
    This card demonstrates text readability and surface contrast with your palette.
  </p>
  <button style="background: var(--color-primary); color: white; border: none; padding: 8px 20px; border-radius: 6px; font-size: 14px; cursor: pointer;">
    Learn More
  </button>
</div>
```

### Badges

```html
<div style="display: flex; gap: 8px; flex-wrap: wrap; padding: 24px;">
  <span style="background: var(--color-primary); color: white; padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: 600;">
    Primary
  </span>
  <span style="background: var(--color-accent); color: white; padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: 600;">
    Accent
  </span>
  <span style="background: var(--color-surface); color: var(--color-text); padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: 600; border: 1px solid var(--color-text-muted);">
    Neutral
  </span>
</div>
```

## Hero Section

```html
<section style="background: var(--color-bg); padding: 80px 24px; text-align: center;">
  <h1 style="color: var(--color-text); font-size: 48px; margin: 0 0 16px 0; font-weight: 800;">
    Your Headline Here
  </h1>
  <p style="color: var(--color-text-muted); font-size: 20px; margin: 0 0 32px 0; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.6;">
    A brief description that demonstrates body text readability against the background.
  </p>
  <div style="display: flex; gap: 12px; justify-content: center;">
    <button style="background: var(--color-primary); color: white; border: none; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer;">
      Get Started
    </button>
    <button style="background: transparent; color: var(--color-primary); border: 2px solid var(--color-primary); padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer;">
      Learn More
    </button>
  </div>
</section>
```

## Dashboard Mockup

```html
<div style="display: grid; grid-template-columns: 240px 1fr; min-height: 400px; font-family: system-ui, sans-serif;">
  <!-- Sidebar -->
  <nav style="background: var(--color-text); padding: 24px 16px;">
    <div style="color: white; font-weight: 700; font-size: 18px; margin-bottom: 32px;">Dashboard</div>
    <div style="color: rgba(255,255,255,0.6); padding: 8px 12px; border-radius: 6px; margin-bottom: 4px; font-size: 14px;">Overview</div>
    <div style="background: var(--color-primary); color: white; padding: 8px 12px; border-radius: 6px; margin-bottom: 4px; font-size: 14px;">Analytics</div>
    <div style="color: rgba(255,255,255,0.6); padding: 8px 12px; border-radius: 6px; margin-bottom: 4px; font-size: 14px;">Settings</div>
  </nav>
  <!-- Main content -->
  <main style="background: var(--color-bg); padding: 24px;">
    <h2 style="color: var(--color-text); margin: 0 0 24px 0;">Analytics</h2>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
      <div style="background: var(--color-surface); padding: 20px; border-radius: 12px;">
        <div style="color: var(--color-text-muted); font-size: 13px;">Total Users</div>
        <div style="color: var(--color-text); font-size: 28px; font-weight: 700;">12,453</div>
        <div style="color: var(--color-primary); font-size: 13px;">+12.5%</div>
      </div>
      <div style="background: var(--color-surface); padding: 20px; border-radius: 12px;">
        <div style="color: var(--color-text-muted); font-size: 13px;">Revenue</div>
        <div style="color: var(--color-text); font-size: 28px; font-weight: 700;">$48.2K</div>
        <div style="color: var(--color-accent); font-size: 13px;">+8.1%</div>
      </div>
      <div style="background: var(--color-surface); padding: 20px; border-radius: 12px;">
        <div style="color: var(--color-text-muted); font-size: 13px;">Conversion</div>
        <div style="color: var(--color-text); font-size: 28px; font-weight: 700;">3.24%</div>
        <div style="color: var(--color-primary); font-size: 13px;">+0.4%</div>
      </div>
    </div>
  </main>
</div>
```

## Full Page Template

Combine all sections into a complete showcase page:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Palette Showcase</title>
  <style>
    :root {
      --color-bg: #F8F9FA;
      --color-surface: #FFFFFF;
      --color-text: #1A1A2E;
      --color-primary: #2563EB;
      --color-accent: #F59E0B;
      --color-text-muted: color-mix(in srgb, var(--color-text) 60%, transparent);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: system-ui, -apple-system, sans-serif; background: var(--color-bg); color: var(--color-text); }
  </style>
</head>
<body>
  <!-- Insert swatch grid, hero, cards, dashboard sections here -->
  <!-- Update :root values with actual Huemint API results -->
</body>
</html>
```

## Workflow

1. Generate palette via Huemint API
2. Map result colors to semantic roles (background, surface, text, primary, accent)
3. Set CSS custom properties with the hex values
4. Build prototype using the component snippets above
5. Present to user for feedback
6. If adjustments needed, regenerate with locked colors and rebuild
