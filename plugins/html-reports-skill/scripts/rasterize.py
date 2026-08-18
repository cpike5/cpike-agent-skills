#!/usr/bin/env python3
"""
rasterize.py — turn a built report into PNGs you can actually look at.

The build script checks that the HTML is well formed. It cannot check that a
diagram points the right way, that an arrowhead landed on the right box, or
that a label is sitting on top of a line. Only looking at the pixels does
that, and every hand-drawn or generated SVG needs it.

Usage
  python3 rasterize.py reports/audit.html                    # light + dark
  python3 rasterize.py reports/audit.html --theme dark
  python3 rasterize.py reports/audit.html --out-dir /tmp/shots --width 1280

Writes <name>-light.png / <name>-dark.png next to the report unless --out-dir
is given, and prints the paths. Open them, or read them with the Read tool.

Needs a Chromium or Chrome binary. It looks in PLAYWRIGHT_BROWSERS_PATH, then
on PATH, then in the usual system locations. If it finds none it says so and
exits non-zero — that is your cue to tell the reader, in the delivery message,
that the visuals were not visually verified.
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

CANDIDATES = [
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome",
]
SYSTEM_PATHS = [
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]


def find_browser():
    root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if root and os.path.isdir(root):
        for pat in ("chromium-*/chrome-linux/chrome",
                    "chromium_headless_shell-*/chrome-linux/headless_shell",
                    "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"):
            hits = sorted(glob.glob(os.path.join(root, pat)))
            if hits:
                return hits[-1]
    for name in CANDIDATES:
        found = shutil.which(name)
        if found:
            return found
    for path in SYSTEM_PATHS:
        if os.path.exists(path):
            return path
    return None


def themed_copy(report, theme, work_dir):
    """A copy of the report pinned to one theme via <html data-theme=…>.

    The theme is a media query plus a data-theme attribute, and headless
    Chrome has no reliable flag for the media query. Pinning the attribute is
    exactly what the toggle button does, so this checks the real thing.
    """
    with open(report, encoding="utf-8") as fh:
        html = fh.read()
    html = re.sub(r"<html\b[^>]*>", '<html lang="en" data-theme="%s">' % theme, html, count=1)
    out = os.path.join(work_dir, "%s-%s.html" % (os.path.basename(report), theme))
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out


def shoot(browser, page, out, width, height):
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--force-device-scale-factor=1",
            "--user-data-dir=" + profile,
            "--virtual-time-budget=3000",
            "--window-size=%d,%d" % (width, height),
            "--screenshot=" + out,
            "file://" + page,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(out):
        sys.stderr.write(proc.stderr[-2000:] + "\n")
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description="Screenshot a built report so its visuals can be checked.")
    ap.add_argument("report", help="path to the built HTML report")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--height", type=int, default=4000, help="tall window; raise it for long reports")
    ap.add_argument("--theme", choices=["light", "dark", "both"], default="both")
    args = ap.parse_args()

    report = os.path.abspath(args.report)
    if not os.path.exists(report):
        sys.exit("error: no report at %s" % report)

    browser = find_browser()
    if not browser:
        sys.exit("error: no Chromium or Chrome binary found.\n"
                 "       Install one, or say plainly in delivery that the visuals\n"
                 "       were not visually verified. Do not skip this silently.")

    out_dir = args.out_dir or os.path.dirname(report)
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(report))[0]
    themes = ["light", "dark"] if args.theme == "both" else [args.theme]

    failed = False
    with tempfile.TemporaryDirectory() as work:
        for theme in themes:
            out = os.path.join(out_dir, "%s-%s.png" % (stem, theme))
            page = themed_copy(report, theme, work)
            if shoot(browser, page, out, args.width, args.height):
                print("wrote %s (%.0f KB) — look at it" % (out, os.path.getsize(out) / 1024))
            else:
                failed = True
                print("error: screenshot failed for %s theme" % theme, file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
