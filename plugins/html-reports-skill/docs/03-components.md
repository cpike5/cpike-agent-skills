# Component reference

Every component in `base.css` and `base.js`. Open `${CLAUDE_PLUGIN_ROOT}/assets/components.html` in a browser to see
them rendered with their markup.

Never invent a class. If nothing here fits, add the component to `base.css` and to this file so
future reports inherit it.

## Choosing a component

| The content is… | Use |
| --- | --- |
| Who wrote this, when, on what authority | `header.masthead` + `.meta` |
| A status that qualifies the whole document (draft, internal, not a quote) | `.banner` in the masthead |
| A table of contents | `.agenda` |
| The conclusions, read on their own | `.card` titled "The short version" |
| Headline counts | `.kpis` / `.kpi` |
| A point that must not be skimmed past | `.note` (`.risk`, `.good`, `.info`, `.plain`) |
| Two sides of one judgement | `.cols` with two `.note`s |
| More than three comparable rows | `.tablewrap` + `<table>` |
| A status on a row | `.pill` (`warn`, `flag`, `good`, `info`, `muted`) |
| A fixed set of categories (milestones, owners, streams) | `--c0`…`--c5` via `.chip` / `.swatch` |
| Actions with an owner | `ul.checklist` |
| Several comparable things scored on the same few axes | `.scorecard` + `.sc` |
| Recommendations in priority order | `.ranked` + `.item`, in `.tier`s if they group |
| What to do in what order, and why that order | `.seq` + `.step` |
| A schedule with dependencies | Gantt — `Report.gantt()` |
| Why a number moved between two versions | waterfall — `Report.waterfall()` in a `.svgbox` |
| Structure or flow | inline `<svg>` in `.svgbox`, using the `s-*` classes |
| Provenance and the limits of the claims | `<footer>` |

## Scorecard

Ten rooms, six services, four vendors — anything where the reader's question is *which of these
is finished?* Denser than a table, and the shape of a weak entity is visible before any of it is
read.

```html
<div class="scorecard">
  <article class="sc" style="--hue: var(--c2)">
    <div class="sc-top"><span class="sc-name">The Kitchen</span><span class="sc-key">kitchen</span></div>
    <div class="sc-axes">
      <div class="axis"><span class="k">Prompt</span><span class="bar" data-fill="full"><i></i></span></div>
      <div class="axis"><span class="k">Tools · 16</span><span class="bar" data-fill="full"><i></i></span></div>
      <div class="axis"><span class="k">Digest</span><span class="bar" data-fill="none"><i></i></span></div>
    </div>
    <p class="sc-note"><em>Complete.</em> The reference implementation.</p>
  </article>
</div>
```

- **The same axes on every card, in the same order.** A scorecard where the axes vary is a set of
  unrelated cards, and the eye cannot compare down a column.
- **Four axes, five at the outside.** More and the card becomes a table with worse alignment.
- **`data-fill` is `none` / `low` / `mid` / `full`** — four steps, no numbers. A count that
  matters goes in the axis label (`Tools · 16`), a judgement goes in `.sc-note`. Bars are for the
  shape of the row, not for measurement; if the reader needs the exact figures, use a table.
- **`--hue` per card** picks the accent from the series tokens. Use it to encode something —
  domain, owner, status — or set it once for the whole grid. Never pick a hue for prettiness.
- **`.sc-note` carries the sentence you would say out loud** about that entity: `strong` for what
  is missing, `em` for what is done. Add `.is-weak` to the card to outline the ones in trouble.
- Follow the grid with a `.legend` explaining what a full bar means. Four fill levels are not
  self-evident.

## Ranked items

Recommendations, in the order you would do them. The rank badge means the order is a claim you
are making — if the order does not matter, this is a list.

```html
<div class="tier">
  <div class="tier-head"><h3>Do these first</h3><p>Small, mechanical, visible everywhere</p></div>
  <div class="ranked">
    <article class="item">
      <div class="item-head">
        <span class="rank">01</span>
        <h3>Delete nine tabs that promise views nobody built</h3>
        <div class="markers"><span class="pill muted">an afternoon</span><span class="pill info">every room</span></div>
      </div>
      <p>The finding, with the evidence in the same breath.</p>
      <p class="small">The secondary detail — how, and what it costs.</p>
    </article>
  </div>
</div>
```

- **The heading is the recommendation**, phrased as an action with its object. "Five digest
  providers over data that already exists" — not "Digests".
- **Sizing and impact go in `.pill` markers**, never in the heading. Two markers: what it costs,
  what it unlocks.
- **`.tier`s group by kind of work**, not by theme — do-these-first, nearly-there, the big bet.
  The tier's own `p` says what the tier has in common.
- A `.cols` pair of `.note good` / `.note risk` inside an item is the have/need split: what
  already exists against what is missing. It is the fastest way to show that a recommendation is
  a fifth copy of something rather than new ground.
- Numbering is `01`, `02`, … and is referenced elsewhere in the document ("item 02"), so it has
  to stay stable once written.

## Sequence

The running order. Use it once, near the end, after the recommendations have been argued.

```html
<div class="seq">
  <div class="step">
    <span class="step-n">01</span>
    <div>
      <h4>Stop advertising the nine tabs</h4>
      <p>Why this is first, in one sentence.</p>
      <span class="when">an afternoon · item 01</span>
    </div>
  </div>
</div>
```

- **Each step says why it is in that position** — what it makes cheaper for the step after it. A
  sequence that is just the recommendations re-listed adds nothing.
- **`.when` carries duration and a back-reference** to the item that argues for it.
- Use `ul.checklist` instead when the rows need owners and tick-boxes; use a Gantt when they run
  in parallel and depend on each other. `.seq` is for a strictly ordered list of moves.

## The scripts

All opt-in. A static report can delete the whole `<script>` block.

| Behaviour | Turned on by |
| --- | --- |
| Theme toggle | `<button id="theme-toggle">` |
| Tooltips | `<div id="tip">` present, plus `data-tip="…"` on any element |
| Sortable column | `<th data-sort="text">` or `<th data-sort="num">` in a `<thead>` |
| Agenda highlights current section | `.agenda a[href="#id"]` matching an `h2[id]` |
| Today's date rendered | `data-now` on any element (prefer a hard-coded date on archived documents) |

| A waterfall chart | `Report.waterfall(host, steps, opts)` — see below |
| A Gantt chart | `Report.gantt(host, rows, opts)` — see below |

For report-specific code, append a second `<script>` after the base block and use
`window.Report.{$, $$, esc, bindTip, waterfall, gantt}`. Escape any interpolated string with
`esc()` before it reaches `innerHTML`.

## The waterfall chart

Use it for one job: showing **why a number moved**. An opening value, the movements that acted on
it, a closing value. If the number did not move, or moved for one reason, a sentence is better.

```js
Report.waterfall("#wf-1", [
  { label: "Prior central estimate", total: true },   // bar drawn from zero
  { label: "Claim UX built from nothing", delta: 12 },
  { label: "EF already in a DAL",         delta: -6 },
  { label: "Post-audit central estimate", total: true }
], { start: 80, unit: " h", polarity: "cost" });
```

| Option | Meaning |
| --- | --- |
| `start` | The value the first `delta` applies to. Default `0`. |
| `unit` | Appended to every figure — `" h"`, `"k"`, `"%"`. Include the leading space if you want one. |
| `polarity` | `"cost"` (default): a positive delta is red, because more hours or more spend is bad news. `"value"`: a positive delta is green. Pick the one that matches what the reader wants the number to do. |
| `height` | SVG height in user units. Default `400`. Raise it if the labels crowd. |
| `ticks` | Approximate y-axis tick count. Default `5`. |
| `note` | `fn(step)` returning an extra tooltip line, for sourcing a movement. |

Conventions:

- **The axis starts at zero.** Deltas will look small next to a large opening bar, and that is
  honest — the movement genuinely is small relative to the total. Do not truncate the axis to
  make the story look bigger.
- **Label each movement with its cause, not its category.** "Claim UX built from nothing" beats
  "Scope increase". The label is the argument.
- **The caption states the conclusion.** The bars show that the number moved; the caption says
  what that means.
- **Six to nine bars.** Beyond that the labels collide and the reader stops counting. Aggregate
  the small movements into one bar and explain it in the body.
- Needs the base `<script>`. If you strip the script block, replace the chart with a table —
  there is no CSS-only fallback.

## The Gantt chart

Use it when the reader needs to see **what runs in parallel and what waits on what**. A list of
start and end dates with no dependencies between them is a table, not a Gantt.

```js
Report.gantt("#gt-1", [
  { group: "Gateway" },                                     // heading row
  { label: "Sinks and queue handoff", ids: "G1–G6", owner: "A",
    cat: "M1", from: "2026-09-07", to: "2026-09-28" },      // bar
  { label: "Contracts frozen", at: "2026-09-11",
    cat: "M0", milestone: true }                            // diamond
], {
  cats: { M1: { label: "Pipeline", c: 1 } },
  caption: "Two developers",
  marks: [{ at: "2026-09-11", label: "Contracts frozen" }],
  bands: [{ from: "2026-09-28", to: "2026-10-12" }],
  today: "2026-10-20"
});
```

`from`, `to` and `at` take either ISO date strings or plain numbers (weeks from project start).
Do not mix the two forms in one chart. Numeric axes label themselves with `opts.unit`, e.g.
`"Week"`.

| Option | Meaning |
| --- | --- |
| `cats` | `{ KEY: { label, c } }`. A row's `cat` picks its colour from `--c0`–`--c5` and its legend entry. The legend is generated from this; pass `legend: false` to suppress it. |
| `from`, `to` | Domain bounds. Defaults to the extent of the data. |
| `unit` | Axis noun for numeric charts. Ignored for dates. |
| `today` | Draws a red vertical rule. Omit on documents that will be read months later. |
| `bands` | `[{ from, to }]` shaded regions — a reconciliation window, a freeze, a holiday. |
| `marks` | `[{ at, label }]` callouts in a lane above the bars, so they never collide with them. |
| `lines` | `[{ at }]` plain dashed rules — milestone boundaries. |
| `caption` | Small text above the label column, usually the scenario name. |

Behaviour worth knowing:

- **Bar labels place themselves.** Inside the bar when it is wide enough, otherwise in whatever
  clear space exists to the right or left. Sizing assumes the chart is at its 780px minimum, so
  labels stay legible on a phone at the cost of occasionally sitting outside a bar that would
  have fitted them on a desktop.
- **Ticks pick their own interval** — weekly under two months, monthly under seven, quarterly
  beyond. You do not set them.
- **Everything is a percentage**, so the chart is responsive inside its scroller and prints
  correctly. Bar fills carry `print-color-adjust: exact` so they survive a PDF export.
- **Row order is your order.** There is no sorting or automatic layout — if the critical path
  should read top to bottom, put it in that order.

Conventions:

- **Group rows carry the structure**, not colour. Colour should encode a milestone or phase, so
  the reader can see a milestone's work scattered across several groups.
- **One scenario per chart.** If you are comparing a solo plan against a two-developer plan,
  render two charts, or drive one from a `.seg` control — do not overlay them.
- **Twenty-five rows is the ceiling.** Past that, aggregate to workstream level and put the
  detail in a table beneath.

---

Writing conventions live in `SKILL.md` and apply to both formats. The `--cN-ink` mechanism that
keeps bar labels legible is explained in `${CLAUDE_PLUGIN_ROOT}/docs/02-theming.md`.
