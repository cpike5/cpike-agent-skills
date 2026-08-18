---
name: html-reports
description: Write project reports — audits, scope reviews, status updates, findings, estimates, schedules, post-mortems, recommendations. Defaults to Markdown; produces a themed single-file HTML report when the user asks for HTML or when the content needs a Gantt chart, waterfall chart, KPI row, or other component Markdown cannot express. Use this skill whenever the user asks for a report, findings document, audit write-up, scope review, estimate, project schedule, or client-facing deliverable, even if they do not say the word "report" or specify a format — and use it for Markdown reports too, since the document structure and writing conventions here apply to both.
---

# Reports

Two formats, one set of conventions. Plan the document first, pick the format from
what the plan needs, then build.

## 1. Plan before writing

Always, in both formats. Write the outline into the conversation, not into a file:

1. **The job.** One sentence: what question does this document settle, and who acts on it?
2. **What it is not.** "Pre-quote review — not a quotation." Decide this now; it goes in the
   masthead and the footer.
3. **Sections.** The list, in order, each with the component it needs.
4. **The numbers.** Which figures go in the KPI row, and where each is derived in the body.
   A figure with no derivation in the body does not go in the KPI row.
5. **Format**, decided from step 3 (see below).

For **Markdown**, proceed straight from the outline to writing.

For **HTML**, show the outline to the user and get confirmation before building.
Restructuring a finished HTML report is expensive; changing a five-line outline is free.

## 2. Choosing the format

**Default to Markdown.** It is faster to produce, faster to review, and diffs cleanly.

Use HTML only when one of these is true:

- The user asked for HTML, a web page, or something to send to a client
- The content needs a **Gantt chart** — a schedule where the reader must see what runs in
  parallel and what waits
- The content needs a **waterfall chart** — a number that moved, and the movements that moved it
- The content needs hover detail, sortable columns, switchable scenarios, or a KPI row
- The document is a client-facing deliverable where presentation carries weight

A report that is headings, prose and three tables is a Markdown report even if the user said
"make it look good". Say so and offer HTML as a follow-up rather than assuming.

If unsure, write Markdown. Markdown converts to HTML cheaply later; the reverse is not true.

## 3. Building an HTML report

Read `${CLAUDE_PLUGIN_ROOT}/docs/01-html-workflow.md` before starting. It covers the full procedure. In summary:

1. **Ensure `.reports/` exists** at the repo root. If it does not, create it: copy `${CLAUDE_PLUGIN_ROOT}/assets/base.css`
   and `${CLAUDE_PLUGIN_ROOT}/assets/base.js` into it unchanged, and generate `theme.css` from the host application's
   palette (see step 2). This happens once per repository.
2. **Derive the theme automatically** — do not ask the user for colours. Find the application's
   palette in its stylesheets and run `${CLAUDE_PLUGIN_ROOT}/scripts/derive_theme.py`. Details and search order are in
   `${CLAUDE_PLUGIN_ROOT}/docs/02-theming.md`.
3. **Write the body fragment** to a scratch file — everything between `<body>` and `</body>`.
   Component markup is in `${CLAUDE_PLUGIN_ROOT}/docs/03-components.md`; start from
   `${CLAUDE_PLUGIN_ROOT}/assets/body.html`.
4. **Assemble** with `${CLAUDE_PLUGIN_ROOT}/scripts/build_report.py`, which inlines the theme, the stylesheet and the
   renderers into one portable file and refuses to write if anything is broken.
5. **Write it into the repository** and tell the user the path — see "Where the report goes"
   below.

Never hand-assemble the final HTML, and never link a stylesheet. Reports must survive being
emailed, archived, and opened from disk in two years. `build_report.py` enforces this.

### Where the report goes

**A report is a file in the repository, not a published Artifact.** `build_report.py --out`
writes it to a path under the working tree — `reports/dashboard-audit-2026-08-17.html` or
similar — and delivery means naming that path so the user can open, commit, or send it.

Do **not** publish the report as a Claude Artifact unless the user asks for one — "publish this",
"make it an artifact", "give me a link", "share it with the team". Only then call the Artifact
tool, and still write the local file first: the file is the deliverable, the Artifact is a copy
of it. The same applies to Markdown reports.

## 4. Writing conventions

These apply to **both formats** and matter more than any styling decision.

**Bold the claim, not the sentence.** A reader who reads only the bold text should still come
away with the findings.

> **Plots are files, not queries.** Every impedance plot form is computed once at ingest and
> written to disk. The view layer does no maths at all today.

**Lead with the conclusion, then the evidence.** Never build up to a finding across a paragraph.

**Every figure appears twice** — once as a headline number, once in the body with its
derivation. A number that cannot be defended in a meeting does not belong in the document.

**Say what the document is not.** "Pre-quote review — not a quotation." "Planning estimates, not
a quotation." "Read-only; no code was changed." Cheap to write, expensive to omit.

**Identifiers go in `code` formatting** — file paths, requirement IDs, table names, anything the
reader will search for.

**Name the cause, not the category.** "Claim UX built from nothing" beats "scope increase". The
label is the argument.

**Captions state what a visual proves**, not what it contains. "The audit replaced a guess with
six measured movements, three of which pushed down" — not "waterfall of estimate changes".

**Separate findings from disclosure.** Things discovered in passing that the reader should hear
but that are not in scope get their own section, explicitly marked as such.

**Ranges, not false precision.** "90–130 h, central ~110" is honest. "112 h" is not, and invites
an argument about the wrong thing.

## 5. Reference files

All paths are relative to `${CLAUDE_PLUGIN_ROOT}`.

| File | Read it when |
| --- | --- |
| `docs/01-html-workflow.md` | Before building any HTML report. The full procedure. |
| `docs/02-theming.md` | Setting up `.reports/` in a repo for the first time. |
| `docs/03-components.md` | Choosing and writing component markup. Has a selection table. |
| `assets/body.html` | The starting skeleton for a body fragment. |
| `assets/components.html` | Every component rendered, with its markup. Open in a browser. |
| `assets/base.css`, `assets/base.js` | Copied verbatim into `.reports/`. Do not edit per report. |
| `assets/theme.css` | The default palette, used unchanged when no app palette is found. |

## 6. Scripts

```bash
# once per repo — derive theme tokens from the app's palette
python3 "$CLAUDE_PLUGIN_ROOT/scripts/derive_theme.py" --primary "#7c3aed" > .reports/theme.css

# check a palette's legibility without writing anything
python3 "$CLAUDE_PLUGIN_ROOT/scripts/derive_theme.py" --primary "#7c3aed" --check

# per report — assemble the single-file output
python3 "$CLAUDE_PLUGIN_ROOT/scripts/build_report.py" --body draft-body.html \
    --title "Dashboard Audit — Findings" --out reports/dashboard-audit.html
```

`build_report.py` fails loudly rather than writing a broken report. It checks tag balance,
rejects external references, rejects literal hex colours in the body, and confirms every chart
target exists. Fix what it reports; do not work around it.
