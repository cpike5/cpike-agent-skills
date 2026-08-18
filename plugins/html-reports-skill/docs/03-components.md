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
| Structure or flow — a schema, a pipeline, a service map | graph — `Report.graph()` in a `.svgbox` |
| A picture with no nodes and edges in it — a floor plan, a timeline sketch | hand-drawn inline `<svg>` in `.svgbox`, using the `s-*` classes. Read the warning below first. |
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

## The graph diagram

A schema, a pipeline, a service map, a state machine — anything whose content is **what
connects to what**. This is the most common visual in an audit or an architecture review, so it
has a renderer rather than a set of classes: you declare nodes and edges, and every coordinate,
arrowhead and self-loop is derived from them.

```js
Report.graph("#gph-schema", [
  { id: "org",   label: "Organisation", sub: "tenant root", cat: 0 },
  { id: "site",  label: "Site",         sub: "1 per address", cat: 1 },
  { id: "asset", label: "Asset",        sub: "serialised", cat: 2 },
  { id: "read",  label: "Reading",      sub: "append only", cat: 3 },
  { id: "user",  label: "User", cat: 4, col: 1, row: 1 }
], [
  { from: "org",   to: "site",  label: "1 : n" },
  { from: "site",  to: "asset", label: "1 : n" },
  { from: "asset", to: "read",  label: "1 : n" },
  { from: "asset", to: "asset", label: "parent asset" },      // self-loop
  { from: "user",  to: "read",  label: "recorded by", kind: "alt" }
], {
  label: "Data model",
  groups: [{ label: "Tenanted", nodes: ["org", "site", "user"] }]
});
```

**Node fields**

| Field | Meaning |
| --- | --- |
| `id` | Required. What the edges refer to. |
| `label` | Box text. Wraps to three lines, two when there is a `sub`. |
| `sub` | A smaller second line — a type, a store, a count. |
| `cat` | `0`–`5`. Tints the border from `--c0`…`--c5`. Encode something, or leave it off. |
| `col`, `row` | 0-based grid position. Omit both and the layout is derived; set them to override one node without hand-placing the rest. |
| `tip` | Tooltip HTML, shown when `#tip` is in the body. |

**Edge fields**

| Field | Meaning |
| --- | --- |
| `from`, `to` | Node ids. `from === to` draws a self-loop. |
| `label` | Sits on the line with a surface-coloured halo, so it stays readable over it. |
| `kind` | `"alt"` for the dashed accent style — a secondary or asynchronous relationship. |
| `dir` | `"both"` for a head at each end, `"none"` for a plain line. Default is one head at `to`. |

**Options**: `nodeW` / `nodeH` (default `168` × `56`), `colGap` / `rowGap` (`78` / `34`),
`groups` (`[{ label, nodes: [id, …] }]`, a dashed enclosure), `label` (the `aria-label`), and
`tidy: false` to keep returning edges straight instead of bowed.

Conventions:

- **Direction is the claim.** `{ from: "asset", to: "reading" }` says an asset has readings. Read
  every edge back as a sentence before you build. The renderer will not catch a reversed one.
- **Columns are derived by layering** — a node sits one column right of everything that points
  at it. Edges that close a cycle are held out of that calculation, so a feedback path bows back
  instead of dragging the chain sideways. Pin a node with `col`/`row` when the derived layout
  reads wrong.
- **Self-loops are automatic and identical everywhere.** An arc over the top of the box with its
  label above. Do not invent one: `{ from: "x", to: "x" }` is the whole convention.
- **Twelve nodes is the ceiling.** Past that, split the diagram by concern or move the detail
  into a table. A graph nobody can trace is a decoration.
- **Colour encodes, or it is absent.** `cat` should mean domain, owner or lifecycle. A rainbow of
  boxes that means nothing is worse than no colour.
- **The caption states what the diagram proves.** "Every reading reaches a site through an asset;
  nothing is tenant-scoped below `site`" — not "the data model".
- Needs the base `<script>`. If you strip the script block, replace the diagram with a table of
  `from`, `to`, `relationship`.

## Hand-drawn inline SVG

Sometimes the picture is not nodes and edges — a floor plan, a page layout, a shape sketch. Then
you draw it yourself in a `.svgbox` with the `s-*` classes: `.s-node`, `.s-lab`, `.s-sub`,
`.s-grp`, `.s-grplab`, `.s-edge`, `.s-edge-alt`, `.s-edgelab`, `.s-arrow`.

**Know what you are giving up.** Every other component here is either validated by
`build_report.py` or generated by a renderer. Hand-drawn SVG is neither. A reversed edge, an
arrowhead pointing the wrong way, a label sitting on top of a line and a shape 200 units off the
canvas are all perfectly well-formed HTML. The build cannot see any of them. **If a diagram has
nodes and edges in it, use `Report.graph()`** — this section is the exception, not the
alternative.

If you do draw one, rasterize the built report and look at it before delivering:

```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/rasterize.py" reports/audit.html
```

### Arrowheads

**Never draw an arrowhead as a second path.** `.s-edge` is `fill: none`, so a filled head has to
be its own shape, and its three coordinates then have to be kept in sync with an endpoint that
lives in a different string. That is the single most common defect in a hand-drawn diagram, and
`build_report.py` now rejects it: a closed path carrying `.s-edge` is an error.

Define one marker per document and point every edge at it:

```html
<div class="svgbox">
  <svg viewBox="0 0 520 140" role="img" aria-label="Ingest path">
    <defs>
      <marker id="arw" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path class="s-arrow" d="M0,0 L10,5 L0,10 Z"/>
      </marker>
    </defs>
    <rect class="s-node" x="8" y="40" width="150" height="48" rx="8"/>
    <text class="s-lab" x="83" y="69" text-anchor="middle">Queue</text>
    <path class="s-edge" d="M164,64 L246,64" marker-end="url(#arw)"/>
    <text class="s-edgelab" x="205" y="56" text-anchor="middle">batched</text>
    <rect class="s-node" x="252" y="40" width="150" height="48" rx="8"/>
    <text class="s-lab" x="327" y="69" text-anchor="middle">Validator</text>
  </svg>
</div>
```

- The head lands on the end of the line, whatever the line does afterwards. Move the path and the
  head follows.
- `orient="auto-start-reverse"` means the same marker works as `marker-start` on a two-way edge.
- `.s-arrow` fills from `--ink-muted`; `.s-arrow-alt` fills from `--c4` for a `.s-edge-alt` line.
- `markerWidth`/`markerHeight` are in stroke widths, so the head scales with the line.
- The build rejects a `marker-end` that names an id no `<marker>` defines. It cannot tell you the
  head is at the wrong end — only your eyes can.

### Self-loops

An edge from a thing to itself. Draw it the same way every time: a cubic arc over the top of the
box, from the left shoulder to the right shoulder, head landing back on the box, label above the
arc.

```html
<!-- box at x=90…210, y=60…108, inside a viewBox with room above it -->
<path class="s-edge" d="M124,57 C124,21 176,21 176,57" marker-end="url(#arw)"/>
<text class="s-edgelab" x="150" y="14" text-anchor="middle">parent asset</text>
```

Leave headroom in the `viewBox` for the arc and its label. A loop drawn off the top of the
canvas is invisible, and nothing but a rasterized screenshot will tell you.

`Report.graph()` draws exactly this shape for `{ from: "x", to: "x" }`. Match it so the two never
disagree inside one report.

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
| A graph diagram | `Report.graph(host, nodes, edges, opts)` — see below |

For report-specific code, append a second `<script>` after the base block and use
`window.Report.{$, $$, esc, bindTip, waterfall, gantt, graph}`. Escape any interpolated string with
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
