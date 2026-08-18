# HTML report workflow

The full procedure for producing a single-file HTML report. Read this before building one.

## Contents

1. Repository setup — the `.reports/` folder
2. Writing the body fragment
3. Assembling
4. Reviewing before delivery
5. Delivering the report
6. Failure modes

---

## 1. Repository setup

Check for `.reports/` at the repository root. If it exists, skip to section 2 — the theme is
already established and must not be regenerated for each report.

If it does not exist, create it once:

```
.reports/
  theme.css     <- generated; the only file that differs between projects
  base.css      <- copied verbatim from the plugin's assets/
  base.js       <- copied verbatim from the plugin's assets/
```

```bash
mkdir -p .reports
cp "$CLAUDE_PLUGIN_ROOT/assets/base.css" "$CLAUDE_PLUGIN_ROOT/assets/base.js" .reports/
python3 "$CLAUDE_PLUGIN_ROOT/scripts/derive_theme.py" --primary "#<app primary>" > .reports/theme.css
```

Finding the app's primary colour is covered in `${CLAUDE_PLUGIN_ROOT}/docs/02-theming.md`. Derive it automatically; do not
ask the user.

`base.css` and `base.js` are identical across every project. If a report needs a component the
library lacks, add it to `base.css` and to `${CLAUDE_PLUGIN_ROOT}/docs/03-components.md` so future reports inherit it — do not
add one-off CSS to a single report.

Commit `.reports/`. It is a source folder, not a build artefact.

## 2. Writing the body fragment

Write a scratch file containing only what sits between `<body>` and `</body>`. Start from
`${CLAUDE_PLUGIN_ROOT}/assets/body.html` and delete every component the outline did not call for.

Read `${CLAUDE_PLUGIN_ROOT}/docs/04-editorial.md` first — it covers the headline, the part structure, density and
accent use, which is most of what separates a report someone forwards from one they skim. Read
`${CLAUDE_PLUGIN_ROOT}/docs/05-plain-language.md` too: every sentence in the body is written in
simplified English by default.

Structure, in order:

1. `#theme-toggle` button — keep it unless the report will only ever be printed, or the theme was
   generated with `--mode light`/`--mode dark` to match a single-scheme application
2. `header.masthead` — eyebrow, title, sub, meta, and a `.banner` if the document is qualified
3. `.agenda` — one card per `h2`, same order, matching `id`s
4. A `.card` titled "The short version" — the findings, readable alone
5. The sections themselves
6. `footer` — provenance, what the document is not, confidentiality
7. `#tip` div if anything uses tooltips or charts

Rules while writing:

- **No literal colours.** Every colour comes from a token. `build_report.py` rejects hex values
  in the body. If you need a colour that is not a token, the token set is wrong — fix `theme.css`.
- **No external references.** No CDN scripts, no web fonts, no remote images. Rejected at build.
- **Charts go in a host element** that the script targets by id: `<div id="gt-plan"></div>`,
  then `Report.gantt("#gt-plan", …)`. The build checks the id exists.
- **Chart scripts use `DOMContentLoaded`**, because `base.js` is inlined after the body:

  ```html
  <script>
  document.addEventListener("DOMContentLoaded", function () {
    Report.gantt("#gt-plan", rows, opts);
  });
  </script>
  ```

- **Keep the agenda in sync** with the section list. A stale agenda is the most common defect.

## 3. Assembling

```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/build_report.py" \
    --body draft-body.html \
    --title "Dashboard Audit — Findings" \
    --out reports/dashboard-audit.html
```

Defaults look for `.reports/theme.css`, `.reports/base.css`, `.reports/base.js`. Pass `--no-js`
for a report with no charts and no interaction — it saves roughly 20 KB and the report stays
fully functional.

Name the output for its content and date, not for its version: `dashboard-audit-2026-08-17.html`,
not `report-final-v3.html`.

Delete the scratch body fragment afterwards, or keep it outside the delivered folder. Two files
that look like the report invite someone to send the wrong one.

## 4. Reviewing before delivery

Check, in this order:

1. **Both themes.** Toggle the button. Dark mode is not decoration — these get read on phones.
   (Single-scheme themes: check the one scheme, and check the toggle is absent.)
2. **Print preview.** Section headings should not strand at page bottoms; tables and figures
   should not split. The stylesheet handles this, but verify.
3. **Narrow viewport.** The Gantt label column collapses to 150px below 620px; tables scroll.
4. **Every KPI figure appears in the body** with its derivation.
5. **The agenda matches the sections.**
6. **The masthead and footer both say what the document is not.**
7. **The prose passes the simplified-English check** in
   `${CLAUDE_PLUGIN_ROOT}/docs/05-plain-language.md`. Longest sentence under 25 words, active
   voice, one term per concept, no padding words.

## 5. Delivering the report

The deliverable is the file `build_report.py --out` wrote. Deliver it by telling the user the
path — `reports/dashboard-audit-2026-08-17.html` — so they can open it, commit it, or attach it
to an email. That is the whole delivery step for the default case.

**Do not publish it as a Claude Artifact by default.** An Artifact is a hosted copy on
claude.ai; the report is a repository file that has to survive being emailed and archived, which
is exactly what the single-file build guarantees. Publishing is a separate action the user asks
for, in words like "publish this", "make it an artifact", "give me a link to share", or "put it
somewhere the team can see".

When they do ask:

1. Build the local file first, exactly as above. It stays the source of truth.
2. Publish that same file with the Artifact tool — do not rebuild or re-style for the Artifact.
3. Give the user both: the repo path and the Artifact URL.

If a report is republished after an edit, re-run `build_report.py` and publish the same file path
again so the Artifact updates in place rather than becoming a second, diverging copy.

## 6. Failure modes

| Symptom | Cause |
| --- | --- |
| `chart target #x has no matching element` | The host div is missing, or the id does not match the selector in the script call. |
| `external reference breaks portability` | A CDN link or remote image crept in. Inline it or remove it. |
| `literal colour #xxxxxx in the body` | Use a token. If none fits, add one to `theme.css`. |
| Chart renders blank | The script ran before `base.js` was defined. Wrap it in `DOMContentLoaded`. |
| Chart renders but is unstyled | The host div lacks its class — `Report.gantt` adds `.gt` itself, so this usually means the call threw. Check the browser console. |
| Bars illegible in dark mode | `theme.css` was hand-edited without updating the matching `--cN-ink` value. Re-run `derive_theme.py`. |
| Report looks nothing like the app | `theme.css` was generated from a guess. Re-derive from the app's actual stylesheet. |
| Report reads as dense and hard to follow | The prose skipped `docs/05-plain-language.md`. Split the long sentences, make the voice active, and use one term per concept. |
