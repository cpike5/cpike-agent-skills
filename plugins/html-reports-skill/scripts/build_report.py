#!/usr/bin/env python3
"""
build_report.py — assemble a single-file HTML report.

Takes a body fragment (everything from <body> to </body>, which is the only
part that differs between reports) and inlines the theme, the component
stylesheet and the renderers into one portable file with no external requests.

Usage
  python3 build_report.py \
      --body draft-body.html \
      --title "Dashboard Audit — Findings" \
      --theme .reports/theme.css \
      --base  .reports/base.css \
      --js    .reports/base.js \
      --out   reports/dashboard-audit.html

--theme, --base and --js default to .reports/ in the current directory.
--no-js omits the script block for a report with no charts or interaction.

Verifies before writing:
  * every tag balances
  * no external http(s) references survive in the output
  * no literal hex colour appears in the body (they must come from tokens)
  * chart hosts referenced by the script actually exist in the body
  * every marker an arrowhead points at is actually defined
  * no arrowhead is drawn as a closed .s-edge path

Warns about hand-drawn SVG, which nothing can validate. Rasterize the result
with rasterize.py and look at it before delivering.
"""

import argparse
import os
import re
import sys
from html.parser import HTMLParser

VOID = {"meta", "br", "hr", "img", "input", "link", "source", "path", "rect",
        "circle", "line", "use", "col", "polygon", "polyline", "ellipse", "stop"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        elif any(t == tag for t, _ in self.stack):
            while self.stack:
                t, ln = self.stack.pop()
                if t == tag:
                    break
                self.errors.append("<%s> opened at assembled-file line %d, never closed" % (t, ln))
        else:
            self.errors.append("stray </%s> at assembled-file line %d" % (tag, self.getpos()[0]))


def read(path, label):
    if not os.path.exists(path):
        sys.exit("error: %s not found at %s\n"
                 "       Copy the skill's assets into .reports/ first." % (label, path))
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def check(body, out_html):
    problems, warnings = [], []

    b = Balance()
    b.feed(out_html)
    problems += b.errors
    problems += ["<%s> opened at assembled-file line %d, never closed" % (t, ln) for t, ln in b.stack]

    for m in re.finditer(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', out_html):
        problems.append("external reference breaks portability: " + m.group(1))

    body_no_script = re.sub(r"<script\b.*?</script>", "", body, flags=re.S | re.I)
    for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b", body_no_script):
        token = m.group(0)
        if re.fullmatch(r"#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|#[0-9a-fA-F]{8}", token):
            warnings.append("literal colour %s in the body — use a token instead" % token)

    # Hand-drawn SVG is the one part of a report nothing here can validate: the
    # geometry is the author's, and a reversed edge or a stranded arrowhead is
    # perfectly well-formed HTML. Say so, loudly, every time.
    hand = re.sub(r"<svg\b[^>]*\bclass=[\"'][^\"']*\b(wf|gt|gph)\b", "", body)
    if re.search(r"<svg\b", hand, re.I):
        warnings.append("hand-drawn <svg> in the body — nothing here checks that it points the "
                        "right way. Prefer Report.graph() for nodes and edges. If it stays, "
                        "rasterize the built report and look at it (scripts/rasterize.py), or "
                        "tell the reader the visuals were not visually verified")

    for m in re.finditer(r'class\s*=\s*["\'][^"\']*\bs-edge\b[^"\']*["\'][^>]*\bd\s*=\s*["\']([^"\']+)', body):
        if re.search(r"[zZ]\s*$", m.group(1)):
            problems.append("a closed path carries .s-edge, which is fill:none — an arrowhead "
                            "drawn as a second path drifts from its line. Use "
                            "marker-end with the .s-arrow marker, or Report.graph()")

    markers = set(re.findall(r'<marker\b[^>]*\bid\s*=\s*["\']([\w-]+)["\']', body))
    for m in re.finditer(r'marker-(?:end|start|mid)\s*=\s*["\']url\(#([\w-]+)\)', body):
        if m.group(1) not in markers:
            problems.append("marker #%s is referenced but never defined — the arrowheads will "
                            "not draw" % m.group(1))

    hosts = set(re.findall(r'Report\.\w+\(\s*["\']#([\w-]+)["\']', body))
    ids = set(re.findall(r'id\s*=\s*["\']([\w-]+)["\']', body))
    for h in sorted(hosts - ids):
        problems.append('chart target #%s has no matching element' % h)

    return problems, warnings


def main():
    ap = argparse.ArgumentParser(description="Assemble a single-file HTML report.")
    ap.add_argument("--body", required=True, help="body fragment: content between <body> and </body>")
    ap.add_argument("--title", required=True, help="document title")
    ap.add_argument("--out", required=True, help="output path")
    ap.add_argument("--theme", default=".reports/theme.css")
    ap.add_argument("--base", default=".reports/base.css")
    ap.add_argument("--js", default=".reports/base.js")
    ap.add_argument("--no-js", action="store_true", help="omit the script block")
    ap.add_argument("--lang", default="en")
    args = ap.parse_args()

    body = read(args.body, "body fragment")
    theme = read(args.theme, "theme.css")
    base = read(args.base, "base.css")
    js = "" if args.no_js else read(args.js, "base.js")

    body = re.sub(r"^\s*<body[^>]*>", "", body.strip(), flags=re.I)
    body = re.sub(r"</body>\s*$", "", body, flags=re.I).strip()

    parts = [
        "<!DOCTYPE html>",
        '<html lang="%s">' % args.lang,
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % args.title,
        "<style>",
        theme.rstrip(),
        "",
        base.rstrip(),
        "</style>",
        "</head>",
        "<body>",
        body,
    ]
    if js:
        parts += ["<script>", js.rstrip(), "</script>"]
    parts += ["</body>", "</html>", ""]
    out_html = "\n".join(parts)

    problems, warnings = check(body, out_html)
    for w in warnings:
        print("warning: " + w, file=sys.stderr)
    if problems:
        for p in problems:
            print("error: " + p, file=sys.stderr)
        sys.exit("refusing to write %s — fix the errors above" % args.out)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(out_html)

    kb = len(out_html.encode("utf-8")) / 1024
    print("wrote %s (%.0f KB, self-contained)" % (args.out, kb))


if __name__ == "__main__":
    main()
