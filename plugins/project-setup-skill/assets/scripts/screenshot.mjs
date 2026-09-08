// scripts/screenshot.mjs — deterministic screenshots of the running app at both
// breakpoints. The common agent task: prove a UI change renders, and attach the
// evidence to the PR's Verification section.
//
//   node scripts/screenshot.mjs /room/library library
//
// Writes .screenshots/library-desktop.png and .screenshots/library-mobile.png.
//
// Assumes the app is already running (see docs/local-dev-environment.md).
// Everything here is deliberate; see the project-setup skill's 07-testing.md for why.

// A global CommonJS playwright install has no named ESM exports — import the
// default and destructure. Adjust the path, or use `import { chromium } from
// 'playwright'` when it is a local dependency.
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;

import { mkdir } from 'node:fs/promises';

const BASE_URL = process.env.APP_URL ?? 'http://127.0.0.1:5250';
const OUT_DIR = '.screenshots';

// Both breakpoints, always. A responsive shell hides or relocates whole regions
// on the phone, so these are two different layouts and not one at two widths.
const VIEWPORTS = {
  desktop: { width: 1440, height: 1000 },
  mobile: { width: 390, height: 844 },
};

const [route = '/', name = 'page'] = process.argv.slice(2);

// The selector that proves the thing you care about is actually on screen.
// Waiting for this — not for a clock, and not for network idle — is what makes
// the shot reliable.
const READY_SELECTOR = process.env.READY_SELECTOR ?? 'main';

async function shoot(browser, label, viewport) {
  // One context per screenshot: contexts carry viewport, routes and storage
  // state, and reusing one leaks configuration between shots.
  const ctx = await browser.newContext({
    viewport,
    // Pin these so a machine's locale/timezone can't reorder or reformat content.
    locale: 'en-US',
    timezoneId: 'UTC',
    reducedMotion: 'reduce',
    deviceScaleFactor: 2,
  });

  // --- Authentication -----------------------------------------------------
  // Replace with storageState when the app's real sign-in can be driven
  // locally. This interception path is for providers (Google OAuth, SSO) that
  // simply are not configurable in a sandbox.
  //
  // This matters more than it looks: an anonymous principal often carries no
  // user id, so every per-user API answers 404 and the panel renders its empty
  // state. Nothing throws, and the screenshot looks plausible — which is how a
  // change gets "verified" against a component that never rendered.
  await ctx.route('**/api/auth/me', r => r.fulfill({
    json: { isAuthenticated: true, isAnonymous: false, isAdmin: true, name: 'Test User' },
  }));

  // Stub the page's own data here too, shaped like its DTO, so the shot doesn't
  // depend on whatever happens to be in the database:
  // await ctx.route('**/api/books**', r => r.fulfill({ json: { items: FIXTURE } }));

  const page = await ctx.newPage();

  // domcontentloaded, never networkidle: networkidle waits for *every* request
  // to settle, so one blocked CDN font or one long-lived connection hangs it
  // for the full timeout. (It is deprecated for this reason.)
  await page.goto(`${BASE_URL}${route}`, { waitUntil: 'domcontentloaded' });

  // A client-rendered app on a cold cache is genuinely slow to boot; a default
  // 5s failure here reads as a broken app rather than a slow one.
  await page.waitForSelector(READY_SELECTOR, { timeout: 60_000 });

  // A shot taken mid font-swap catches the fallback face and diffs against
  // every later run.
  await page.evaluate(() => document.fonts.ready);

  await page.screenshot({
    path: `${OUT_DIR}/${name}-${label}.png`,
    fullPage: true,
    // An in-flight transition is the single most common source of a spurious
    // diff; a blinking caret is the second.
    animations: 'disabled',
    caret: 'hide',
    // Paint over anything you can't control — avatars, live data, embeds:
    // mask: [page.locator('.avatar')],
  });

  console.log(`${OUT_DIR}/${name}-${label}.png`);
  await ctx.close();
}

const browser = await chromium.launch();
try {
  await mkdir(OUT_DIR, { recursive: true });
  // Serially: parallel contexts contend for CPU and make the ~10s-per-shot
  // budget unpredictable.
  for (const [label, viewport] of Object.entries(VIEWPORTS)) {
    await shoot(browser, label, viewport);
  }
} finally {
  await browser.close();
}
