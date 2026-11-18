# Executor Common Guidelines

> Narrative skeleton and visual aesthetic come from this deck's locked files under [`modes/`](./modes/_index.md) and [`visual-styles/`](./visual-styles/_index.md). Technical constraints are in shared-standards.md.

---

## 1. Template Adherence Rules

### 1.0 Pre-generation Batch Read

**Hard rule**: Read selected template/chart SVGs from the execution lock and project structure plan as needed. Reuse previously read sources while available. Reread a selected source if it changed or is no longer in context.

Before this batch read, run:

```bash
python3 ${SKILL_DIR}/scripts/template_page_catalog.py <project_path> validate-project
python3 ${SKILL_DIR}/scripts/validate_asset_usage.py <project_path> --preflight
```

Any error is a hard stop.

| Source list | Read path |
|---|---|
| `page_binding.route` + binding audit | `<project_path>/page_binding.json` |
| Chosen template's `design_spec.md` (when route selects one) | exact path recorded by the route |
| Chart selection audit + skin contract | `<project_path>/chart_selection.json` |
| Every distinct reference in `spec_lock.md page_layouts` | exact selected Deck/Layout package only |
| Every distinct chart name in `spec_lock.md page_charts` | `templates/charts/<chart_name>.svg` |
| HTML background manifest | Free Route only; Deck Route must not load it |

**Default — read each template once; re-read only on the mid-deck exception below**:
- Layout SVG already loaded in this batch
- Chart SVG already loaded in this batch

`locked_values.json` is the per-page re-read cache (§2.1).

**Exception**: user mid-deck adds pages or swaps templates introducing a basename/chart absent from the original batch → read the new file once, continue.

> Note: batched prefix reads stay in the cached prompt prefix; per-page `spec_lock.md` re-reads append below and benefit from that cache. Scattered on-demand reads of layout/chart SVGs would invalidate downstream cache and sit in the compression-vulnerable mid-context region.

**Background layer is route-aware**. Deck Route uses the selected Deck's locked shell/background assets; it must not introduce Layout or HTML Background assets. Free Route may use `spec_lock.html_backgrounds` (HTML-PNG/AI) and the layered architecture in shared-standards §4.

Resolve the per-page **content-layer** template SVG via `spec_lock.md page_layouts` (authoritative for content structure only — it no longer decides the background). The legacy page-type table below is a **last-resort fallback** for legacy decks where `page_layouts` is missing.

**Resolution order (per page — content layer):**

1. `spec_lock.md page_render_modes` has an entry → follow that page's `mirror` / `brand_shell` / `themed_rebuild` contract in §1.1. A deck-level `replication_mode: mirror` does not force an inexact page into mirror.
2. `spec_lock.md page_layouts` has `P<NN>: <reference>` for this page → after the pre-Executor validator confirms it, resolve the canonical reference to its file; catalog-less legacy templates treat it as a direct basename. Inherit the resolved SVG structure (already in context from §1.0).
3. `page_layouts` exists but **no entry** for this page → rebuild the content structure under the locked route. Deck Route still inherits the selected Deck's visual language and any locked shell; it does not become Free Route. Record the same-Deck visual reference and adaptation in the page realization plan without claiming an exact layout match.
4. `page_layouts` section absent (legacy deck) **and** `templates/` directory exists → fall back to the page-type table below, matching by SVG filename keyword (cover/chapter/content/ending/toc). Read the matched file at first use if §1.0 batch did not cover it.
5. No template at all → free design.

> Note: `page_layouts` disambiguates the multiple content variants modern templates ship (e.g., `graduation_defense` has 8); the legacy table cannot.

**Templates supply structure, not skin (non-mirror)**: a chart or layout template's gradients, drop-shadows, palette, and font families are placeholders. Inherit geometry, label / legend placement, relationship logic, and series encoding; re-skin every `fill` / `stroke` / `stop-color` / font / effect to the deck's `visual_style` + `spec_lock.colors` + `spec_lock.typography`. If a brand/layout/deck template was selected upstream, the lock already contains that template identity, so it always wins over the chart SVG. Forbidden — shipping a chart template's default `<linearGradient>` / `cardShadow` / color literals / font-family unchanged. Mirror templates are the exception: §1.1 preserves the selected mirror's own visuals verbatim.

When adapting a selected global chart/icon structure, wrap the adapted group with a provenance marker, for example `<g data-wtt-source="chart:flow-linear">`. Template shell/structure markers follow the exact value declared in `spec_lock.page_assets`. These markers are stripped only after `validate_asset_usage.py` passes.

### 1.1 Per-page template adaptation

`spec_lock.md page_render_modes` is the per-page authority. The three modes are deliberately different:

| Mode | What is locked | Executor behavior |
|---|---|---|
| `mirror` | Whole non-text SVG structure | Copy the canonical template SVG; edit visible `<text>/<tspan>` content only. Geometry, images, groups, effects, colors and element order stay byte-equivalent in meaning. |
| `brand_shell` | `page_shell_assets` + `page_shell_requirements` + template palette/type/brand chrome | Keep every required asset role. A required template background must be full-bleed; rebuild the content region so every locked `slide_text` item fits. |
| `themed_rebuild` | Visual tokens, semantic design language and declared teaching structures | Adapt proportions and composition while retaining source-backed features in page_realization.json; no claim of exact mirror fidelity. |

Rules:

1. `mirror` is legal only after Binder/Strategist confirms exact content-shape fit. It is never a request to approximate.
2. If item count, text capacity, image requirement or semantic structure does not fit, change the lock to `brand_shell` or `themed_rebuild` **before generating**. Never delete an item, rewrite the outline, or split/merge pages to preserve a template.
3. **同页降级（SAME-PAGE DEGRADATION）**: 已选定用途与结构适合的本地页因 mirror 容量条件不足而降级时，优先保留同一 canonical reference 的可验证品牌壳，按已有资产契约切到 `brand_shell`；无法满足必需资产角色则用 `themed_rebuild`。用途或槽位不合的页只能作为同 Deck 视觉参考，不能靠降级冒充精确匹配。保留特征与重建原因记录在课程逐页结构计划，详见 [Step 4](steps/step4-strategist.md#逐页模板落实deck-route)。
4. `brand_shell` reads both `page_shell_assets P<NN>` and `page_shell_requirements P<NN>`. Every required role must be represented by an exact locked filename. A required `background` asset must be full-bleed; when `forbid_unlocked_full_bleed=true`, generic HTML/AI backgrounds outside the lock are forbidden. If the package cannot supply every required role, use `themed_rebuild`.
5. **全局 Chart 借结构**: 无精确匹配的包内页时，执行 Step 4 的 Chart 闸口，采用已锁定的合格 `charts/` 结构并继承同 Deck 视觉语言；可与契约允许的同 Deck 壳组合。模式按实际保留程度与资产契约填写，不冒称 mirror。Deck Route 禁止借用其他 Deck、Layout 或 HTML Background；Executor 不自行重新选型。
6. `slide_text` is immutable when the handoff contract locks the outline. Layout adapts to content; content does not adapt to layout. For page-level visual intent, read the original intent and the locked per-page plan alongside content, then follow [composition realization](composition-realization.md); template binding alone does not fulfill that intent.
7. Mirror SVGs do not use `{{}}` substitution. Copy the selected source page and replace only visible text nodes.
8. Output names always follow the project sequence (`<NN>_<page_name>.svg`); the template reference is never the output page number.

**Backward compatibility**: if `page_render_modes` is absent, a template with deck-level `replication_mode: mirror` keeps the former all-mapped-pages mirror behavior. New specs must write per-page modes.

**Mirror + chart pages**: chart structures inside a mirror SVG are already drawn (axis, series, labels). Treat them as visual references — replace the data labels and series text content to match the project's chart spec, but do not redraw the chart from a `templates/charts/<name>.svg` baseline. A mirror template's `page_charts` entries are normally absent for this reason.

**Legacy fallback table** (used only when `page_layouts` is absent):

| Page Type | Corresponding Template | Adherence Rules |
|-----------|----------------------|-----------------|
| Cover | `01_cover.svg` | Inherit background, decorative elements, layout structure; replace placeholder content |
| Chapter | `02_chapter.svg` | Inherit numbering style, title position, decorative elements |
| Content | `03_content.svg` | Inherit header/footer styles; **content area may be freely laid out** |
| Ending | `04_ending.svg` | Inherit background, thank-you message position, contact info layout |
| TOC | `02_toc.svg` | **Optional**: Inherit TOC title, list styles |

### Page-Template Mapping Declaration (Required Output)

Before generating each page, output which template is used:

```
📝 **Template mapping**: `templates/<chosen_template>/03a_content_image_text.svg` (or "None (free design)")
🎯 **Adherence rules / layout strategy**: [specific description]
```

- **Content pages**: execute the locked per-page mode and retained structural features; `themed_rebuild` adapts geometry while preserving the declared teaching relationship. Follow [Step 6](steps/step6-executor.md#质量检查闸口强制) to complete source/adaptation/render evidence. A header/footer or palette alone is not proof of template use.
- **No template**: generate entirely per the Design Spec

---

## 2. Design Parameter Confirmation (Mandatory Step)

Before the first SVG page, output a confirmation listing: canvas dimensions, body font size, color scheme (primary/secondary/accent HEX), font plan. Prevents spec/execution drift.

### 2.1 Per-page locked_values re-read (Mandatory)

The cache keeps shared design values and full page tables on disk. The page query prints shared values and current-page mappings to limit repeated input.

**Before each SVG**, run `python3 ${SKILL_DIR}/scripts/extract_locked_values.py <project> --page <page_id>`. If context was compacted, reload the current page brief. Consult the full lock on the first page, when a value is missing, or when validation reports drift.

**Per-block expression**: render each `design_spec.md §IX Content` block in its written texture — a full-sentence block as wrapped prose, a fragment/label block as bullets/keywords. **Never split a full-sentence block into a bullet list** — splitting loses the information that the block was continuous reasoning, not a set of parallel points; not because a bullet lays out easier, and not because an inherited template slot is shaped as a list. If a block carries no clear texture, infer the mode from its wording and the page layout.

- **Prose render recipe**: one `<text>` per paragraph; wrap lines with sibling `<tspan>` that reset `x` to the block's left edge and advance `dy` by the font size × a line-height factor. **Default — line-height by density (may override per content fit)**: ~1.4–1.5× for dense / small-body blocks (CLReq comfortable minimum), 1.6–2.0× for large-type, sparse, or `breathing` blocks. Fit about width ÷ font-size CJK glyphs per line (Latin fits roughly twice that); the last line runs short. Use the body ramp size, not a new one.
- **Template precedence**: when an inherited template slot is a bullet list but the §IX block is prose, the prose wins — widen or reflow the container to hold the paragraph, or drop that card; do not pour the sentence back into the list slot.
- **Mode precedence**: the locked mode shapes voice / register, not §IX's authored titles or page order. When a `§IX` title is a user-authored topic label, keep it — do not upgrade it to an assertion just because the mode (e.g. `pyramid`) favors them; mode title-tendencies apply only to AI-drafted titles.

> Note: block-level phrasing, applied *within* the page's `page_rhythm` density (below), not against it.

**If `locked_values.json` is missing**: first check for `spec_lock.md` — if it exists, run `python3 ${SKILL_DIR}/scripts/extract_locked_values.py <project>` to regenerate the cache, then proceed. If both are absent: emit `warning: spec_lock.md / locked_values.json missing — generating without execution lock` once, then proceed using `design_spec.md` values. Expected only for legacy projects; new projects MUST have both (see [strategist.md](strategist.md) §6 step 4).

**Forbidden — values outside the lock**:

- Colors (fill / stroke / stop-color) MUST come from `colors`
- Icons MUST come from `icons.inventory`; library MUST equal `icons.library`
- Font family from `typography`: use role override (`title_family` / `body_family` / `emphasis_family` / `code_family`) if declared, else fall back to `font_family`
- Font sizes follow a **ramp anchored on `typography.body`**, not a closed menu. Use the declared slots when they fit. Intermediate sizes (e.g., 40px hero number, 13px annotation) are allowed if the ratio to `body` falls within the role's band (see `design_spec.md §IV ramp table`). Sizes outside every band require extending the lock first.
- Images MUST reference files listed under `images`; no invented filenames
- Formula PNGs are images with `Acquire Via: formula` / `Status: Rendered`; place them only from the listed file path and never recreate the formula as text.

If a page needs a value not in `spec_lock.md`, surface it — do not silently invent one.

**Per-page layout rhythm — `page_rhythm` section**:

Before drawing each page, look up its entry in `page_rhythm` (key format `P<NN>` matching the page index in §IX of `design_spec.md`) and apply the corresponding layout discipline:

| Tag | Layout discipline |
|-----|-------------------|
| `anchor` | Structural page (cover / chapter / TOC / ending). Follow the matching template verbatim. |
| `dense` | Information-heavy. Card grids, multi-column layouts, KPI dashboards, tables, and charts are all permitted. This is the baseline behavior. |
| `breathing` | Low-density impact page. Avoid **multi-card grid layouts** — do not organize content as multiple parallel rounded containers (3-card row, 4-card KPI grid, 2×2 matrix rendered as cards). Use naked text blocks, dividers, whitespace, or full-bleed imagery as the content structure. Single rounded visual elements (hero image corners, callouts, tags, one emphasis block) are fine — the rule is about grid structure, not about the `rx` attribute. Proportions follow information weight (not a preset ratio). Typical forms: hero quote, single large number with one-line interpretation, full-bleed image with floating caption, section transition. |

> Without rhythm variation, every page defaults to card grids (the "AI-generated" look). `page_rhythm` is the only narrative lever that survives context compression.

**Missing `page_rhythm` section** → emit `warning: spec_lock.md missing page_rhythm — defaulting all pages to dense` once, fall back to `dense` for all pages.

**Tag not found for current page** → emit `warning: spec_lock.md page_rhythm tag not found for P<NN> — falling back to dense` once per deck (aggregate; do not repeat per page), fall back to `dense`. Do not invent a tag.

**Per-page template lookup — `page_layouts` section**:

Before drawing each page, look up its entry in `page_layouts` to decide which basename to inherit (the SVG itself was loaded in §1.0):

- Entry present (e.g., `P04: 03a_content_image_text`) → inherit the corresponding SVG already in context. The canonical reference **must match** an actual file and, when present, `page_catalog.json`; otherwise emit `error: page_layouts P<NN> references invalid template page <reference>` and stop. Never silently or warning-only fall back to free design for an explicit reference.
- No entry for this page → no exact content-layout binding. **Not an error** — rebuild under the locked route and per-page mode. Deck Route still inherits the selected Deck's visual language and required shell assets; record the adaptation in the page realization plan. Absence never switches the page to Free Route.
- Whole section absent → see §1 fallback (legacy page-type matching).

Do **not** invent a layout entry, and do **not** assume an exact layout just because `templates/` exists. A missing entry removes only that content-layout binding, not the selected route or its locked identity/assets.

**Per-page chart reference — `page_charts` section**:

Before drawing each page, look up its entry in `page_charts` to decide which chart structure applies (the SVG itself was loaded in §1.0):

- Entry present (e.g., `P09: timeline`) → adapt the corresponding chart SVG already in context. Copy its structure only. Before drawing, map every source color/font/effect to semantic roles in `spec_lock.chart_skin`; no original chart palette may survive unless that exact value is independently present in `spec_lock.colors`.
- No entry for this page → either no chart on this page, or a chart that didn't match any catalog template (Strategist's `no-template-match` fallback). Design the visualization from scratch using `design_spec.md §VII` for guidance.
- Whole section absent → no catalog data-chart or structural-pattern pages in this deck.

**Per-page background — route first, then `html_backgrounds`**:

Deck Route follows the selected Deck and `page_render_modes/page_shell_assets/page_assets`: retain required assets, or use native shapes for an explicitly locked `themed_rebuild`. Do not load HTML Background assets or create `html_backgrounds` entries. The following HTML rules apply only to Free Route pages explicitly locked to an HTML background:

- Entry present (e.g., `P01: cover`) → **HTML path**: place `images/bg_<value>.png` as the full-bleed background `<image>` first child of `<svg>`, wrapped in `<g id="bg-<value>">`. For `cover` / `ending` / `chapter`, read that item's `text_slots` from `images/html_background_manifest.json` and place each `<text>` inside its slot rectangle (see §3.3). For `theme`, no text-slots — freely design the content layer.
- HTML background is explicitly required for this page but its entry/asset is missing → repair the lock or declared asset before drawing; do not silently add `theme` to other pages.
- Item status `Fallback-Solid` (HTML path only) → use `<rect>` background (see §3.3).

For other Free Route pages, use the declared background: a locked AI full-bleed photo follows `hero_page` / Primitive D without HTML text-slots; a native background remains native. Missing `html_backgrounds` does not imply an AI image or an error. HTML/AI backgrounds, when selected, are the bottom full-bleed image layer; native or Deck backgrounds follow their own locked structure.

---

### 2.2 Serial-with-state page-number source (Mandatory when serial-with-state is active)

> Complements §2.1. While §2.1 re-reads `locked_values.json` for *values*, this section fixes the *which page am I on* question to disk, not memory.

**Activation condition**: a single-agent run with `30 ≤ design_spec.md §IX total pages < 60` enters serial-with-state mode (per SKILL.md Step 6 path branch). The signal is the existence of `<project>/generation_state.json` with `parallel_mode = false` and `segments = []`.

**Hard rule**: when serial-with-state is active, the executor NEVER picks the next page number from §IX's literal ordering, NEVER increments a self-tracked counter in markdown, and NEVER trusts the previous turn's "now generating P<NN>" text.

The single source of page numbers is the JSON manifest. The procedure:

```bash
# Before each page — pull the authoritative page id from disk
P=$(python3 ${SKILL_DIR}/scripts/generation_state.py next-pending <project_path>)
# Output format: P<NN> (zero-padded) or '(none pending)' on stderr when done.

# Pin P<NN> at the top of the assistant response:
#   [Page P<NN> of N total | snapshot = spec_lock.md re-read @ <ISO>]
# This is the only place where this turn's target page appears in chat text.

# Mark generating → write svg_output/<NN>_<name>.svg → mark done
python3 ${SKILL_DIR}/scripts/generation_state.py mark-page <project_path> P<NN> generating
# … (write SVG) …
python3 ${SKILL_DIR}/scripts/generation_state.py mark-page <project_path> P<NN> done

# Pull the next id for the next turn (or "(none pending)" — deck complete)
Q=$(python3 ${SKILL_DIR}/scripts/generation_state.py next-pending <project_path>)
```

**Re-read spec_lock.md (§2.1) is unchanged** — values still come from disk; only the *page index* changed from "self-tracked" to "disk-tracked".

**Forbidden**:

- ❌ "I'll generate the next page, which is P<current+1>" derived from chat history alone.
- ❌ Skipping a `next-pending` call because the previous turn already declared the target.
- ❌ Generating `svg_output/<NN>_*.svg` without first running `mark-page ... generating` (the page may already be done if a previous attempt was interrupted — `next-pending` would skip it).
- ❌ Trusting a `-1`-staggered file count in `svg_output/`. The manifest, not `ls`, decides.

**Edge cases**:

| Symptom | Cause | Action |
|---|---|---|
| `next-pending` outputs `(none pending)` | All pages terminal (`done` or `needs-manual`) | Skip ahead to the §6 quality-check gate |
| `next-pending` outputs a page that the conversation has already covered | The previous turn crashed mid-write or the LLM context was compacted and lost the in-flight page | `read_file generation_state.json` to confirm; if `generating` and SVG missing, reset to `pending` (`mark-page ... pending`) and continue |
| Two pages appear `done` but `filename` doesn't match `design_spec.md §IX` title | Wrong `<name>` chosen | Rename the older SVG via `git mv` (if available) OR document a `note` entry before regenerating, so the trail stays auditable |
| A page stays `failed` after 3 retries | Out of repair budget | `mark-page ... needs-manual`. Do NOT block the deck on this page. |

**`note` checkpoints (≤ 30s to write, big readability payoff over 60-page runs)**:

```bash
python3 ${SKILL_DIR}/scripts/generation_state.py note <project_path> "checkpoint: P01-P10 done; re-read spec_lock §V/§VIII @ <ISO>"
```

Use `note` at every 10-page boundary (and at every 5-page boundary once total ≥ 30). `notes` is a list-of-strings-with-timestamps appended to the manifest; `status` reprints it implicitly via `last_updated`, but listing `notes` is the responsibility of the executor at checkpoint time. See `SKILL.md Step 6 §单代理 + 页级状态子模式 §阶段性 checkpoint` for the full schedule.

**What this section does NOT cover**: the segment-mode (parallel) counterpart is `SKILL.md § Step 6 §大规模并行路径` + `workflows/parallel-execute.md`. Serial-with-state does not consult `design_system.md` or enforce segment ownership. Teaching-content anchors follow page-realization.md independently of segmentation. The two modes are disjoint.

---

## 3. Execution Guidelines

- **Proximity**: group related elements with tight spacing; separate unrelated groups
- **Spec adherence**: follow color, layout, canvas format, and typography in the spec
- **Template structure**: if templates exist, inherit the visual framework
- **Main-agent ownership**: SVG generation must run in the main agent (not sub-agents) — pages share upstream context for cross-page visual continuity
- **Generation rhythm**: lock global design context first, then generate pages sequentially in one continuous context. No batched groups (e.g., 5 at a time).
- **No operational / CTA copy on slides**: pages teach, they do not sell. Slide `<text>` must not carry marketing conversion instructions. Necessary learning actions, material links, software controls and peer feedback stay visible when learners need them. See §3.4 for the full ban list and where such guidance belongs instead.
- **Phased batch generation** (recommended):
  1. **Visual Construction Phase**: generate all SVG pages sequentially for visual consistency. Use layout judgment for chart marks during the draft. **MUST embed plot-area markers** per §3.1 below on every chart page — coordinate calibration is a post-generation step (see [`workflows/verify-charts.md`](../workflows/verify-charts.md)) that depends on these markers.
  2. **Quality Check Gate**: run `python3 scripts/svg_quality_checker.py <project_path>` on `svg_output/`. Any `error` (banned features, viewBox mismatch, spec_lock drift, non-PPT-safe font, etc.) MUST be fixed on the offending page before proceeding — regenerate and re-check. Address `warning`s when straightforward. Do NOT defer to after `finalize_svg.py` — finalize rewrites SVG and masks some violations.
  3. **Logic Construction Phase**: after SVGs pass the quality check, batch-generate speaker notes for narrative continuity.

### 3.1 Chart Plot-Area Marker (MANDATORY on every chart page)

> The [`verify-charts`](../workflows/verify-charts.md) workflow enumerates chart pages from `design_spec.md §VII`, then reads each page's plot-area marker to feed `svg_position_calculator.py`. Missing marker → verify-charts has to re-derive the plot area from axis lines, paying the cost on every run.

**Hard rule**: every SVG page that contains a data visualization chart includes a plot-area marker inside `<g id="chartArea">`, placed **after axis lines** and **before the first data element** (bar, line, area, point).

**Rectangular plot area** (bar / horizontal_bar / grouped_bar / stacked_bar / line / area / stacked_area / scatter / waterfall / pareto / butterfly):

```xml
<!-- chart-plot-area: x_min,y_min,x_max,y_max -->
```

**Radial charts** (pie / donut / radar):

```xml
<!-- chart-plot-area: pie | center: cx,cy | radius: r -->
<!-- chart-plot-area: donut | center: cx,cy | outer-radius: r1 | inner-radius: r2 -->
<!-- chart-plot-area: radar | center: cx,cy | radius: r -->
```

**How to determine coordinate values**:

| Value | Derivation |
|-------|------------|
| `x_min` | X coordinate of the Y-axis line (leftmost data boundary) |
| `y_min` | Y coordinate of the topmost grid line (highest data boundary) |
| `x_max` | X coordinate of the rightmost axis endpoint or grid line |
| `y_max` | Y coordinate of the X-axis baseline |
| `cx, cy` | Center point of pie/donut/radar (accounting for `transform="translate()"`) |
| `r` | Outer radius of the chart |

**Per-page verification** — after writing each chart SVG, confirm the marker exists:

```bash
grep "chart-plot-area" <project_path>/svg_output/<current_page>.svg
```

> All chart templates in `templates/charts/` include this marker as a reference. If you are drawing a chart and the marker is absent, you have a bug.
- **Technical specs**: see [shared-standards.md](shared-standards.md) for SVG/PPT constraints
- **Card containers — use the documented patterns**: when a content page needs section cards (4 quadrants, parallel aspects, capability blocks, info cards), use the patterns codified in [`templates/charts/CHART_STYLE_GUIDE.md`](../templates/charts/CHART_STYLE_GUIDE.md) §11 — half-rounded section tab (§11.1), nested card border without stroke (§11.2), card-grid skeletons (§11.3), diagonal dashed connector for cross-quadrant relationships (§11.5), ground-anchor ellipse as a non-filter depth marker (§11.6), bidirectional interaction arrows for paired protocols (§11.7). Do not reinvent the "tinted full-rounded rect + white cover-rect to hide the bottom corners" hack; it survives in older templates but breaks SVG→PPTX color editing. Reference templates: [`labeled_card.svg`](../templates/charts/labeled_card.svg), [`quadrant_text_bullets.svg`](../templates/charts/quadrant_text_bullets.svg), [`kpi_cards.svg`](../templates/charts/kpi_cards.svg), [`matrix_2x2.svg`](../templates/charts/matrix_2x2.svg), [`team_roster.svg`](../templates/charts/team_roster.svg), [`client_server_flow.svg`](../templates/charts/client_server_flow.svg).
- **Reference — prefer semantic shapes over preset stacks (not a constraint)**: when a slide needs to express "ascending / converging / breaking through / stacking" — i.e., a relationship that goes beyond a generic arrow — prefer a single custom `<polygon>` or `<path>` that encodes the semantics geometrically, rather than stacking multiple preset arrows. A converging-tip path or a podium polygon reads faster than three arrows pointing at a label. Examples of this technique appear in many imported corporate decks; see `projects/01_template_import/svg_output/slide_01.svg` shape-158 for a reference (gradient-filled inward-pointing arrow). Do not codify these as templates — they are page-specific; the rule is just "consider polygon before stacking presets."
- **Reference — visual depth through restraint (not a constraint)**: layered depth comes from rhythm (flat vs lifted, dense vs spacious), not from shadows everywhere. Shadow typically suits 2-3 genuinely floating elements per page (cards on photos, primary CTA, overlays); keep peer-grid cards, dividers, body containers flat. Reach for typography weight, spacing, accent bars, subtle tints **before** shadow. Full rules in shared-standards.md §6.

### 3.2 Large-scale parallel path (page count ≥ 60)

When the deck's page count meets or exceeds the parallel-mode threshold (default 60) AND a `generation_state.json` with assigned segments exists in the project, the Executor switches to **segment mode**. This path is orchestrated by [`workflows/parallel-execute.md`](../workflows/parallel-execute.md); this section defines what a **segment agent** (one worktree session) does.

The §6/§7 single-agent rules in SKILL.md (no sub-agents, sequential, hand-written) are **conditionally relaxed** for segment mode — the relaxation holds only because `design_system.md` + anchor SVGs + `consistency_checker.py` together replace the cross-page coherence that a single agent's continuous context would otherwise provide. If any of those three is missing, segment mode is unavailable and the single-agent path applies unchanged.

**Segment agent read protocol** (replaces §1.0 + §2.1 for segment mode):

1. **At segment start (batch-read once)**:
   - `design_system.md` — the "how to combine" contract (skeleton fragments, motifs, spacing tokens, layout shells, anchor references)
   - every anchor SVG listed in `design_system.md §V` — the gold-standard pages to align to
   - `spec_lock.md` — values contract (colors / fonts / icons / images / page_rhythm / page_layouts / page_charts)
   - `design_spec.md §IX` slice for this segment's `P<NN>` range (the content briefs)
   - every template SVG referenced by `spec_lock.page_layouts` / `page_charts` for this segment's pages (same as §1.0, scoped to the segment)
2. **Before each page**: use the page query in §2.1.
3. **Generate the page**: inherit the matching layout shell from `design_system.md §IV`, paste skeleton fragments (§II) verbatim, fill content from the `§IX` slice, apply values from `spec_lock.md`. Align visual character to the anchor SVG of the same page type.
4. **After each page**: write the SVG to the **main project's** `svg_output/<NN>_<name>.svg` (not the worktree), then update `generation_state.json` via `python3 scripts/generation_state.py mark-page <project> P<NN> done --segment <seg_id>`.

**Segment disjointness**: a segment agent may only write pages listed in its own segment's `pages` array. `generation_state.py` enforces ownership — attempting to mark a page owned by another segment fails.

**Anchors are immutable**: segment agents Read anchor SVGs as references; they never edit them. If a segment agent finds an anchor genuinely wrong, it emits a `warning: anchor <file> appears incorrect for P<NN> — <reason>` and proceeds with the closest-fit interpretation; the orchestrating session decides whether to halt and revise the anchor.

**Per-segment quality gate** (before a segment is marked `done`):
```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>   # per-page spec_lock compliance
python3 ${SKILL_DIR}/scripts/consistency_checker.py <project_path> --segment <seg_id> --against-anchors
```
Any `error` from the quality checker, or a page flagged by the consistency checker (drift score > threshold), sends the page to the repair loop (≤3 retries; beyond that, `needs-manual` or segment degradation — see `parallel-execute.md` Step 4).

**§2.1 per-page spec_lock re-read remains the anti-drift core in both paths.** Segment mode adds the design_system + anchors layer on top; it does not replace the per-page re-read.

### 3.3 HTML Background text-slot Contract

> The HTML background PNG bakes NO editable text — all text is SVG overlay. The HTML template reserves text coordinates via `<!-- text-slot: name x1,y1 x2,y2 -->` comments; `html_render.py` extracts them, validates against `slots.json` (source of truth), and writes them to `images/html_background_manifest.json`'s `text_slots` field. The Executor reads `text_slots` and places `<text>` inside each slot rectangle. This mirrors the `<!-- chart-plot-area -->` marker contract in §3.1.
>
> **Applies ONLY to HTML-background structural pages** (those with a `cover` / `ending` / `chapter` entry in `html_backgrounds`). AI-background structural pages (`ai` path, no `html_backgrounds` entry) have no text-slots — text is placed per `hero_page`.

**Hard rule**: on `cover` / `ending` / `chapter` pages, every text-slot declared in the manifest's `text_slots` MUST have a corresponding `<text>` element whose glyphs fall inside the slot rectangle. The Executor does NOT invent slot coordinates — they come exclusively from the manifest.

**Slot placement**:

| Slot attribute | Derivation |
|---|---|
| `x` | slot `x1` (left-align) or slot horizontal center (center-align) |
| `y` | vertical center of the slot ≈ `(y1 + y2) / 2 + font-size × 0.35` (baseline tweak for visual centering) |
| `font-size` | fits the slot height: ≤ `(y2 - y1) × 0.7` for single-line slots; shrink for long content or wrap with `<tspan dy>` |
| `text-anchor` | `start` (left-align, x=slot.x1) / `middle` (center, x=slot center) / `end` (right-align, x=slot.x2) — match the page's design intent |

**Standard slot usage** (gradient-panel / geometric-mesh / editorial-rule share these slots — see [`../templates/html-background-styles/_index.md`](../templates/html-background-styles/_index.md)):

| Page type | Slot | Typical content |
|---|---|---|
| cover | `title` / `subtitle` / `author` / `date` | Deck title / subtitle / author / date |
| ending | `thanks` / `contact` | Closing line / contact info |
| chapter | `chapter_num` / `chapter_name` | Chapter number (large) / chapter title |
| theme | (none) | Content layer is free design |

**Fallback-Solid background**: when a manifest item's status is `Fallback-Solid` (HTML rendering unavailable), the Executor uses a bare full-canvas `<rect fill="<bg>" width="<canvas_w>" height="<canvas_h>">` as the background first child instead of `<image>`. The `text_slots` still apply (they are independent of the background render method), so text placement is unchanged.

**Per-page verification** — after writing each cover/ending/chapter SVG, confirm text falls in slots:
```bash
grep "text-slot\|<text" <project_path>/svg_output/<current_page>.svg
```

> The `svg_quality_checker.py` enforces slot occupancy — a declared slot with no `<text>` inside its rectangle is an `error`.

### SVG File Naming Convention

Format: `<NN>_<page_name>.svg` (two-digit number from 01; name matches the deck's language and the page title in the Design Spec).

Examples: `01_封面.svg` / `02_目录.svg` / `03_核心优势.svg`; `01_cover.svg` / `02_agenda.svg` / `03_key_benefits.svg`.

---

### 3.4 No operational / marketing copy on slides (content discipline)

Slides teach; they do not sell or convert. Per SKILL.md global discipline Rule 10, the visible `<text>` of every slide MUST NOT carry marketing conversion instructions. Required teaching operations are allowed and must not be removed. This is a content-level ban, enforced by `svg_quality_checker.py` check #12 (`_check_operational_copy`), which scans visible text (template `{{...}}` placeholders excluded) for instructional phrasing.

**Potential marketing phrases to review** (the checker's 8 warning groups; teaching context decides):

| Group | Example phrasing |
|---|---|
| 扫码 / 二维码 | 扫码进群 · 长按识别 · 扫描二维码 |
| 进群 / 加微信 | 发送到微信群 · 加客服微信 · 进交流群 |
| 关注 / 订阅 | 关注公众号 · 扫码关注 · 关注领资料 |
| 转发 / 朋友圈 | 请转发朋友圈 · 分享有礼 · 朋友圈集赞 |
| 报名 / 咨询 / 联系 | 立即报名 · 咨询热线 · 联系班主任 |
| 领取 / 福利 / 优惠 | 免费领取 · 限时优惠码 · 扫码领资料 |
| 点击链接 / 访问 | 点击链接 · 访问网址 · 立即体验 |
| 互动 / 点赞 | 点赞关注 · 一键三连 · 评论区留言 |

**Where such guidance belongs instead**:
- **讲者备注** (`notes/<NN>_*.md`) — the instructor says it aloud at the right moment; it is never rendered on the slide. This is the default.
- **讲师手册** (instructor manual, separate deliverable via `wtt-course-pptx-instructor-manual`) — for scripted CTAs with timing.
- **课后再发** — a separate non-slide asset (poster / handout / message template), not part of the PPTX.

**Topic vs CTA — the false-positive guard**: a course may legitimately *discuss* these verbs as subject matter (a growth-marketing module analyzing "转发率", a compliance course on "扫码诈骗防范"). The check is WARNING-level, not error: when it fires, read the context snippet it prints. If the phrase is **analytical/descriptive** (a metric, a case study, a threat description), keep it. If it directs a **necessary teaching action** (open the exercise, copy a demo link, click a tool control, submit work or share with a partner), retain the usable instruction. Only **marketing conversion** goes to notes; imperative wording alone is not a violation.

**Marketing exception**: a page may carry conversion copy only when the user has explicitly declared it a 转化/引流 page in `spec_lock.md` (e.g. `P40: conversion`). Undeclared pages get no exception.

When filling a placeholder like `{{TAGLINE}}` / `{{CALL_TO_ACTION}}` / `{{CONTACT}}` on an ending or closing page, write a **closing thought or course summary**, not a promo CTA. Example: `{{TAGLINE}}` → "把今天的练习，变成下周的工作习惯" ✓, not "扫码进群领模板" ✗.

---

## 4. Icon Usage

Strategist chooses the library and inventory; Executor only implements. Library details and one-library rule: [`../templates/icons/README.md`](../templates/icons/README.md). This section defines placeholder syntax.

**Built-in icons — Placeholder method (recommended)**:

```xml
<!-- chunk-filled (straight-line geometry, sharp corners, structured) -->
<use data-icon="chunk-filled/home" x="100" y="200" width="48" height="48" fill="#005587"/>

<!-- tabler-filled (bezier-curve forms, smooth & rounded contours) -->
<use data-icon="tabler-filled/home" x="100" y="200" width="48" height="48" fill="#005587"/>

<!-- tabler-outline (light, line-art style — screen-only decks) -->
<use data-icon="tabler-outline/home" x="100" y="200" width="48" height="48" fill="#005587"/>

<!-- phosphor-duotone (single color + 20% backplate — soft depth without solid weight) -->
<use data-icon="phosphor-duotone/house" x="100" y="200" width="48" height="48" fill="#005587"/>

<!-- simple-icons (brand logos — used alongside the deck's primary library, only for real company/product marks) -->
<use data-icon="simple-icons/github" x="100" y="200" width="48" height="48" fill="#181717"/>

<!-- tabler-outline with thin / bold stroke (stroke-style libraries only) -->
<use data-icon="tabler-outline/home" x="100" y="200" width="48" height="48" fill="#005587" stroke-width="1.5"/>
<use data-icon="tabler-outline/home" x="100" y="200" width="48" height="48" fill="#005587" stroke-width="3"/>
```

> ⚠️ **Color**: ALWAYS use `fill="#HEX"` on `<use data-icon="...">`. NEVER use `stroke` or `fill="none"`, even for stroke-style libraries.
>
> **stroke-width** (stroke-style libraries only, currently `tabler-outline`): allowed values `{1.5, 2, 3}`. If `spec_lock.md icons.stroke_width` is declared, all placeholders MUST use that value deck-wide. Default `2` if absent (legacy). Ignored on non-stroke libraries.
>
> Icons are auto-embedded by `finalize_svg.py` — no need to run `embed_icons.py` manually.

**Searching for icons** — use terminal, zero token cost:
```bash
ls ${SKILL_DIR}/templates/icons/chunk-filled/ | grep home
ls ${SKILL_DIR}/templates/icons/tabler-filled/ | grep home
ls ${SKILL_DIR}/templates/icons/tabler-outline/ | grep chart
ls ${SKILL_DIR}/templates/icons/phosphor-duotone/ | grep house
ls ${SKILL_DIR}/templates/icons/simple-icons/ | grep github
```

**Abstract concept → icon name** (names for `chunk-filled`; tabler libraries use their own equivalents — verify with `ls | grep`):

| Concept | chunk-filled | tabler-filled / tabler-outline |
|---------|-------|-------------------------------|
| Growth / Increase | `arrow-trend-up` | same |
| Decline / Decrease | `arrow-trend-down` | same |
| Success / Complete | `circle-checkmark` | `circle-check` |
| Warning / Risk | `triangle-exclamation` | `alert-triangle` |
| Innovation / Idea | `lightbulb` | `bulb` |
| Strategy / Goal | `target` | same |
| Efficiency / Speed | `bolt` | same |
| Collaboration / Team | `users` | same |
| Settings / Config | `cog` | `settings` |
| Security / Trust | `shield` | same |
| Money / Finance | `dollar` | `currency-dollar` |
| Time / Deadline | `clock` | same |
| Location / Region | `map-pin` | same |
| Communication | `comment` | `message` |
| Analysis / Data | `chart-bar` | same |
| Process / Flow | `arrows-rotate-clockwise` | `refresh` |
| Global / World | `globe` | `world` |
| Excellence / Award | `star` | same |
| Expand / Scale | `maximize` | same |
| Problem / Issue | `bug` | same |

> For self-evident names (home, user, file, search, arrow, etc.) — just `grep chunk-filled/` directly without consulting the table.

> ⚠️ **Icon validation**: only use icons from the Design Spec's approved inventory. Verify each via `ls | grep` before use. Mixing libraries within one deck is FORBIDDEN.

---

## 5. Visualization Reference

Chart SVGs referenced in **VII. Visualization Reference List** are loaded once via the §1.0 batch read. This section governs adaptation only.

**Hard rule**: adapt the loaded chart SVG; do not improvise from memory and do not replicate verbatim. Preserve structure, but rebuild the skin from the already selected deck/template theme.

**Adaptation rules**:
- **Preserve**: visualization type (bar/line/pie/timeline/process/framework…), geometry logic, label/legend placement, and series encoding
- **Adapt**: data, labels, dimensions, spacing, and all skin values
- **Semantic color remap**: dominant series/node → `colors.primary`; comparison → a locked secondary accent; highlight → `colors.accent`; axes/grid/secondary labels → locked neutral roles. For more categories than locked accents, distinguish with opacity, dash, or PPT-safe patterns based on locked colors—never invent another HEX.
- **Typography remap**: every chart label, legend, annotation, and number uses a declared `spec_lock.typography` family and the locked size ramp.
- **Effects remap**: `visual_style` decides whether gradients/shadows survive. Flat styles remove them; gradient/glass styles rebuild them only with locked colors.
- **Freely adjust**: composition, axis ranges, grid, legend, spacing, decoration — as long as the chart stays accurate and readable
- **Forbidden**: retaining the chart SVG's default palette/font/effects; changing visualization type without spec justification; omitting data points or structural elements from the outline

> Templates: `templates/charts/` (71 types). Index: `templates/charts/charts_index.json`

### 5.1 Chart Coordinate Calibration

Coordinate calibration runs as a **standalone post-generation workflow**, not inside the executor pipeline. After SVG generation completes, if the deck contains data charts, run [`workflows/verify-charts.md`](../workflows/verify-charts.md) before post-processing.

The executor's only obligation here is upstream: embed the `<!-- chart-plot-area ... -->` marker on every chart page during initial draft (§3.1). Verify-charts enumerates chart pages from `design_spec.md §VII` (authoritative deck plan) and uses the marker to feed `svg_position_calculator.py`.

> Do NOT run `svg_position_calculator.py` during the initial draft. The calculator calibrates already-generated SVGs against their declared plot areas; running it before the SVG exists has nothing to compare against.

---

## 6. Image Handling

Handle images by their status in the Design Spec's Image Resource List. Status enum and lifecycle: [`svg-image-embedding.md`](svg-image-embedding.md).

| Status | Source | Handling |
|--------|--------|----------|
| **Existing** | User-provided | Reference images directly from `../images/` directory |
| **Generated** | Generated by Image_Generator | Reference images directly from `../images/` directory |
| **Sourced** | Web-acquired by Image_Searcher | Reference from `../images/`. **Read [`image_sources.json`](image-searcher.md) to decide attribution** — see §6.1 below. |
| **Rendered** | Deterministic formula PNG | Reference from `../images/`; use `preserveAspectRatio="xMidYMid meet"` |
| **Needs-Manual** | Acquisition failed and file is absent | Use dashed border placeholder unless the expected file exists |
| **Placeholder** | Not yet prepared | Use dashed border placeholder |

**Reference syntax**: see [`svg-image-embedding.md`](svg-image-embedding.md).

**Placeholder**: Dashed border `<rect stroke-dasharray="8,4" .../>` + description text

**`no-crop` images**: when a `spec_lock.md images` entry ends with ` | no-crop`, size the container to the image's native ratio (from `analyze_images.py` or file dims) and use `preserveAspectRatio="xMidYMid meet"`. Untagged entries are croppable — default to `slice`.

**Formula images**: rows with `Acquire Via: formula` or `Type: Latex Formula` MUST be treated as no-crop even if a legacy `spec_lock.md` forgot the flag. Use the dimensions from `design_spec.md §VIII`, `image_analysis.csv`, or `images/formula_manifest.json`; do not normalize all formulas to one height unless the spec explicitly states that layout choice.

### 6.1 Inline Attribution for Sourced Images (web path)

Whenever the slide uses an image with `Status: Sourced`, look up the corresponding entry in `project/images/image_sources.json` and act on `license_tier`:

| `license_tier` | Action on this slide |
|---|---|
| `no-attribution` | Embed the `<image>` element only. **No credit element needed.** |
| `attribution-required` | Embed the `<image>` element **plus** a small inline `<text>` credit element per the visual spec in [image-searcher.md §7](./image-searcher.md). |

The credit text is **not** rendered by post-processing or export — it must be present in the SVG you produce. The shape of the credit element (size, position, color, multi-image source line, hero gradient overlay) is specified in [image-searcher.md §7](./image-searcher.md). Do not invent a different style.

Use `attribution_text` from the manifest entry as the **starting point**, then compress for the small-text constraint (drop URL, drop filename, keep "via Provider / License"). For CC0/PD images that landed in the `attribution-required` tier only because of upstream metadata quirks (rare), credits are still safe to render.

`svg_quality_checker.py` treats missing CC BY / CC BY-SA inline attribution as an **error**. Fix the offending SVG before post-processing.

**The manifest is the single source of truth for credits.** Do not duplicate license info into speaker notes or any other artifact.

---

## 7. Font Usage

Source of truth: `spec_lock.md typography`. Use `font_family` as default; override per role with `title_family` / `body_family` / `emphasis_family` / `code_family` if declared. LaTeX formulas that Strategist rendered are PNG images, not a `code_family` text role.

If `spec_lock.md` is absent, consult [`strategist.md`](strategist.md) §g — do not invent a stack.

**Hard rule**: every SVG `font-family` stack MUST end with a pre-installed family (Microsoft YaHei / SimHei / SimSun / Arial / Calibri / Segoe UI / Times New Roman / Georgia / Consolas / Courier New / Impact / Arial Black). PPTX has no runtime fallback — missing fonts degrade to Calibri.

---

## 8. Speaker Notes Generation Framework

### Task 1. Generate Complete Speaker Notes Document

课程有 `speaker_notes_ref` 时先逐页读取原备注，以 `python3 ${SKILL_DIR}/scripts/import_course_notes.py <bundle> <project>` 导入 `notes/total.md`，保留原口播、演示、学员动作与反馈；不要用本节通用摘要重新生成或压缩。引用缺失时列入 readiness.gaps 并修复路径。分镜阶段的简短提示可先嵌入样稿，标明完整讲稿待补；PPT 稳定后可由固定页补稿模式扩写，再导入和重新导出，不改可见页面。设计插入页必须先补齐实际导出页与备注映射，不能把基线备注错配给插入页。

Only when no upstream notes or teaching storyboard exists, write brief notes to `notes/total.md` after SVG pages are finalized. Batch-writing can preserve narrative continuity; this fallback is not a substitute for a full instructor script.

**课堂备注与音频分开**：课堂备注允许操作、等待、反馈和时间提示。有 TTS 请求时另提取纯口播，不为音频清洗删掉课堂指令。下列 2–5 句结构只适用于无上游讲稿的普通演示摘要，不限制课程讲稿长度。

**Per-page structure**: `# <number>_<page_title>` heading (the `#` heading line is the only thing stripped before TTS), pages separated by `---`. Body is 2–5 natural sentences carrying the page's core message. Page-to-page transitions live inside the opening sentence as natural prose ("接下来……" / "Having framed X, let's turn to Y") — no bracketed `[过渡]` / `[Transition]` tags.

**Concrete examples** — same shape applies to any language; just write naturally in that language.

中文 deck：

```
# 02_市场格局

在明确了行业背景之后，我们来看具体的市场格局。当前线上零售集中度持续上升，前三大平台合计份额已经达到百分之六十八，腰部玩家正在被快速挤压，留给新进入者的窗口期不超过十八个月。这意味着我们的策略必须聚焦，而不是铺开。
```

英文 deck：

```
# 02_market_landscape

Having framed the industry backdrop, let's look at the actual market landscape. Online retail concentration keeps rising — the top three platforms now hold sixty-eight percent of combined share, mid-tier players are being squeezed fast, and the window for new entrants is under eighteen months. This means our strategy has to focus, not spread.
```

> 日本語 / 한국어 / 其他语言：照搬同样的结构，用对应语言自然书写即可。

**Number readability**: TTS reads digits and symbols literally. Prefer fully-spelled forms in the language being spoken when literal pronunciation would be awkward (e.g. Chinese "百分之六十八" reads better than "68%"; "1-2分钟" reads as "一减二分钟"). Plain integers and percentages in English are fine as-is.

**Common mistakes to avoid**:
- Leaving any bracketed stage marker (`[过渡]` / `[Transition]` / `[Pause]` / `[Data]` / `[Scan Room]` / `[Interactive]` / `[Benchmark]` etc.) in the text — they will be read aloud literally.
- Adding `要点：① …` / `Key points: (1) …` / `时长：2分钟` / `Duration: 2 minutes` / `Flex: …` lines — TTS will speak "要点 一 …".
- Mixing languages within one deck's notes.

### Task 2. Split Into Per-Page Note Files

Auto-split `notes/total.md` into per-page files in `notes/`.

**Naming**: match SVG names (`01_cover.svg` → `notes/01_cover.md`); `slide01.md` also supported (legacy).

---

## 9. Next Steps After Completion

> **Auto-continuation**: After Visual Construction Phase (all SVG pages) and Logic Construction Phase (all notes) are complete, the Executor proceeds directly to the post-processing pipeline.

**Post-processing & Export** (same canonical pipeline as [shared-standards.md §5](shared-standards.md)):

```bash
# 1. Split speaker notes
python3 scripts/total_md_split.py <project_path>

# 2. SVG post-processing (auto-embed icons, images, etc.)
python3 scripts/finalize_svg.py <project_path>

# 3. Export PPTX
python3 scripts/svg_to_pptx.py <project_path>
# Output (default-flow mode):
#   exports/<project_name>_<timestamp>.pptx           ← native pptx (canonical output)
#   exports/<project_name>_<timestamp>.pptx.editability.json ← native-object audit
#   backup/<timestamp>/svg_output/                    ← Executor SVG source backup (always written)
#
# Add --svg-snapshot to additionally emit:
#   exports/<project_name>_<timestamp>_preview_noneditable.pptx ← non-editable visual preview
```
