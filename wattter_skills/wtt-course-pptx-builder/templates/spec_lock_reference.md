# Execution Lock

> **⚠️ Skeleton for Strategist — do NOT copy verbatim into a project.** When producing `<project_path>/spec_lock.md`, emit only `##` sections with filled-in `-` data lines. Do NOT carry over any `>` blockquote guidance, HARD-rule notes, or override examples — those are author-time guidance, not runtime data. Every output line must be parseable data.
>
> Machine-readable execution contract and sole authority. Executor reads it on the first page and when the compact cache lacks a field; before every SVG page it re-reads `locked_values.json`. Values not listed here must NOT appear in SVGs. For design narrative (rationale, audience, style), see `design_spec.md`.
>
> After SVG generation begins, this is the canonical source for color / font / icon / image values. Modifications should go through `scripts/update_spec.py` to keep this file and generated SVGs in sync.

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

> Strategist: fill viewBox and format for the chosen canvas. Common values: `0 0 1280 720` (PPT 16:9), `0 0 1024 768` (PPT 4:3), `0 0 1242 1660` (Xiaohongshu), `0 0 1080 1080` (WeChat Moments), `0 0 1080 1920` (Story).

## mode
- mode: pyramid

> Strategist: the deck's narrative skeleton, locked at confirmation `d` Layer 1. One of `pyramid` / `narrative` / `instructional` / `showcase` / `briefing` — see [`references/modes/_index.md`](../references/modes/_index.md). Executor reads only the locked mode's file. Deck-wide. Or the literal `custom` for a bespoke direction no preset captures (a special cadence, a multi-mode fusion, a particular posture) — user-requested or Strategist-recommended (user confirms, like every lock). Then add a sibling `- mode_behavior:` paragraph (how the argument advances, title voice, page rhythm, register) that the Executor follows in place of a preset file. One deck locks one value; don't default to `custom` when a preset fits.

## visual_style
- visual_style: swiss-minimal

> Strategist: the deck's visual aesthetic, locked at confirmation `d` Layer 2. A preset name from [`references/visual-styles/_index.md`](../references/visual-styles/_index.md), **or** the literal `custom`. Reference intent (shape / decoration / whitespace / texture) — **not a whitelist**, and **carries no HEX** (color truth stays in `colors`). Executor reads only the locked style's file.
>
> **`custom`** — add a sibling `- visual_style_behavior:` row with a one-paragraph aesthetic description (shape language, decoration density, whitespace, typographic character, texture); no HEX, no color names. Tail-case, not a default.

## colors
- bg: #FFFFFF
- primary: #......
- accent: #......
- secondary_accent: #......
- text: #......
- text_secondary: #......
- border: #......
- image_rendering: vector-illustration
- image_palette: cool-corporate
- theme_palette: navy-trust

> Strategist: fill only colors actually used. Add extra rows as needed; delete unused rows rather than leave as `#......`.
>
> **`image_rendering` and `image_palette`** — required only when `images` section below contains `ai`-sourced files. Values MUST be valid names from `references/image-renderings/_index.md` and `references/image-palettes/_index.md`, **or** the literal string `custom`. Image_Generator reads these and applies them deck-wide. Omit both rows when the deck has no AI-generated images.
>
> **`custom` escape hatch.** When set to `custom`, add a sibling `*_behavior` row carrying a one-paragraph prose description. Image_Generator splices the prose into the prompt in place of the preset file's fewshot snippet. Tail-case only — see [`image-renderings/_index.md`](../references/image-renderings/_index.md) §1.5 / [`image-palettes/_index.md`](../references/image-palettes/_index.md) §2 for invocation rules.
>
> ```
> - image_rendering: custom
> - image_rendering_behavior: "Hand-screened poster aesthetic — slightly misregistered halftone overlays, 3 flat ink colors with visible dot pattern at 12% opacity, no gradients, no anti-aliased edges; reads as silkscreen print."
> - image_palette: custom
> - image_palette_behavior: "Primary deep aubergine `#4C1D95` anchors ~35% of canvas; secondary warm cream `#FEF3C7` carries ~55% as breathing field; accent burnished gold `#D4AF37` in 5-10% as ceremonial accents. No fourth color."
> ```
>
> **`theme_palette`** — Free Route 的可选 HEX 种子与 provenance；使用 HTML Background 时必填。Deck Route 直接锁定所选 Deck 的颜色角色，不得用通用 palette 覆盖品牌色；可省略本字段或写该 Deck 自身的 provenance。

## typography
- font_family: "Microsoft YaHei", Arial, sans-serif
- title_family: Georgia, SimSun, serif
- body_family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif
- emphasis_family: Georgia, SimSun, serif
- code_family: Consolas, "Courier New", monospace
- body: 22
- title: 32
- subtitle: 24
- annotation: 14

> **All five family lines are listed explicitly** so Strategist considers every role — `code_family` and `emphasis_family` are easily forgotten. In a real `spec_lock.md`:
> - Keep any `*_family` whose role genuinely differs from `font_family`.
> - **Omit** any `*_family` equal to `font_family` — Executor falls back to `font_family` for missing roles, so writing it twice is noise. (Exception: keep `code_family` even when equal — monospace is conceptually distinct.)
> - `code_family` applies to code snippets only. LaTeX formulas rendered by `latex_render.py` are PNG image assets and must be listed under `images`.
>
> `font_family` is the default fallback. Every declared family is a CSS font-stack string.
>
> **Source**: copy verbatim from the *Per-role font stacks* list in `design_spec.md §IV Font Plan`. Stack **order** encodes browser-rendering intent (Latin-led vs. CJK-led) that the breakdown table cannot — strings here must match character-for-character. See `design_spec.md §IV` for the explainer.
>
> Sizes (`body` / `title` / etc.) are in px, matching SVG units. `body` is the **required baseline anchor** — all other sizes derive as ratios of it (ramp table: `design_spec_reference.md §IV`).
>
> **Size slots are anchors, not a closed menu.** Common slots (`title` / `subtitle` / `annotation`) cover frequent cases. Add role-specific slots (e.g. `cover_title: 72`, `hero_number: 48`, `chart_annotation: 13`) when needed — common for cover-heavy decks, consulting-style hero numbers, dense pages. Executor may use intermediate sizes as long as the ratio to `body` sits in the role's ramp band.
>
> **⚠️ PPT-safe stack discipline (HARD rule).** PPTX stores one `typeface` per run with no runtime fallback. Every stack MUST end with a cross-platform pre-installed font: `"Microsoft YaHei", sans-serif` / `SimSun, serif` / `Arial, sans-serif` / `"Times New Roman", serif` / `Consolas, "Courier New", monospace`. Non-preinstalled fonts (Inter / Google Fonts / brand typefaces) may lead the stack only when the Design Spec notes the font-install or embedding requirement.
>
> **Stack length discipline.** 3-4 fonts per stack is the sweet spot. Converter only writes the **first** Latin and **first** CJK font into PPTX — everything after is silently dropped. macOS-only families (`Songti SC`, `Menlo`, `Monaco`, `Helvetica`) are auto-mapped to Windows equivalents via `FONT_FALLBACK_WIN` (see `scripts/svg_to_pptx/drawingml_utils.py`); stacking both is redundant. Lead with Windows-preinstalled fonts (`Microsoft YaHei` / `SimSun` / `Arial` / `Georgia` / `Consolas`); keep at most **one** macOS-exclusive family (typically `"PingFang SC"`) as a browser-preview nicety.

## icons
- library: chunk-filled
- brand_library: simple-icons
- inventory: target, bolt, shield, users, chart-bar, lightbulb

> `library` MUST be exactly one of `chunk-filled` / `tabler-filled` / `tabler-outline` / `phosphor-duotone` — mixing is forbidden. `brand_library: simple-icons` is optional; include only when the deck uses real company / product brand marks, otherwise omit. `inventory` lists approved icon names (no library prefix); Executor may only use icons from this list.
>
> **`stroke_width` (stroke-style libraries only)** — required when `library` is stroke-based (currently `tabler-outline`); allowed values `1.5` / `2` / `3`. Executor MUST apply this value to every `<use data-icon="...">` placeholder via `stroke-width`, deck-wide. Omit for non-stroke libraries (`chunk-filled` / `tabler-filled` / `phosphor-duotone`) — ignored there. For heavier weight switch library; do not exceed `3` (at 24×24 strokes merge and the icon stops reading as line art).
>
> Example for stroke-style libraries:
> ```
> - library: tabler-outline
> - stroke_width: 2
> - inventory: home, chart-bar, users, bulb
> ```

## images
- cover_bg: images/cover_bg.jpg
- q3_revenue_chart: images/q3_revenue.png | no-crop
- formula_001: images/formula_001.png | no-crop

> One entry per image file used. Append ` | no-crop` only for images that must not lose pixels (data screenshots, charts, certificates, rendered LaTeX formulas) — Executor will size the container to native ratio and use `preserveAspectRatio="xMidYMid meet"`. Untagged entries default to croppable (`slice`). Remove the section entirely if no images.

## page_rhythm
- P01: anchor
- P02: dense
- P03: breathing
- P04: dense
- P05: dense
- P06: breathing
- P07: anchor

> One entry per page. Key: `P<NN>` (zero-padded, matching `§IX Content Outline` in `design_spec.md`). Value: one of the three rhythm tags. Executor reads per page and applies the tag's layout discipline — breaks the "every page looks the same" pattern.
>
> **Vocabulary** (exactly these three values):
> - `anchor` — Structural pages (cover / chapter opener / TOC / ending). Follow the template as-is.
> - `dense` — Information-heavy pages (data, KPIs, comparisons, multi-point lists). Card grids, multi-column layouts, tables, charts all permitted.
> - `breathing` — Low-density pages (single concept, hero quote, big image + caption, section transition). Avoid **multi-card grid layouts** (multiple parallel rounded containers as the primary structure); organize via naked text, dividers, whitespace, or full-bleed imagery. Single rounded elements (hero image corners, callouts, tags, one emphasis block) are fine. Proportions follow information weight — not a preset ratio menu.
>
> **Rhythm follows narrative**: `breathing` pages appear where narrative genuinely pauses — section transitions, a single argument worth standalone emphasis, a deliberate stop after a dense sequence. A data briefing or consulting analysis may legitimately be nearly all `dense` — **do not invent filler pages** to pad rhythm. Validation: every `breathing` page must answer "what independent thing is this page saying?".
>
> **Missing or empty section** → Executor falls back to `dense` for every page (legacy pre-rhythm behavior). Remove the section only for legacy decks; new decks MUST fill it.

## route
- kind: free
- primary_source: none
- strategy: layout-led
- allowed_asset_scopes: layouts, html-background-styles, charts, icons
- forbidden_asset_scopes: decks

> 新项目必填。`kind=deck` 只在用户明确指定 Deck 时合法；`primary_source=decks/<id>`，允许范围只能是该 Deck、charts、icons，禁止其他 Deck/layouts/html-background-styles。用户未指定模板时写 `kind=free` + `strategy=layout-led|html-led|full-free`，不得引用 `templates/decks/`。具体逐页来源写入 `page_assets`。

## variant_policy
- mode: controlled_rotation
- repeat_window: 3
- max_same_topology_run: 2
- equivalence_score_delta: 10
- deterministic_seed: outline_hash

> 新项目默认采用确定性受控轮换。Binder 先满足 `content_form / item_count / composition / density / image_requirements`，再仅在与最高语义分相差不超过 `equivalence_score_delta` 的候选中轮换。明确的 `composition.topology/emphasis` 优先；最近 `repeat_window` 个同域候选避免重复；同一 topology 最多连续 `max_same_topology_run` 次。`deterministic_seed=outline_hash` 保证同一输入重复运行结果一致。`replication_mode=mirror`、结构页和唯一候选页自动稳定，不参与轮换。需要完全固定时写 `mode: stable`。
>
> 本节只控制 Strategist/Binder 的候选决策。最终 `page_layouts/page_charts` 一旦写入 `spec_lock.md` 即锁定，Executor 不得在逐页生成时再次随机选择。

## page_layouts
- P01: 01_cover
- P03: 02a_chapter
- P04: 009_content_vs_comparison

> One entry per page **that uses a template SVG**. Key: `P<NN>` matching §IX. Value: the template's canonical SVG reference without extension (e.g., `01_cover`, `03a_content_image_text`, `009_content_vs_comparison`). When `page_catalog.json` exists, select by its `use_cases` / `structure` / item count / `content_slots` / density / image requirements, reject `avoid_when` matches, and write `reference`. Modern templates ship many content-page variants, so the page-type → single-file mapping in `executor-base.md §1` no longer covers them; this section is the per-page truth.
>
> **No entry for a page** → that page is free design (no template inheritance). Mixed decks are supported: e.g., cover/chapter pages inherit a template while content pages are free.
>
> **Hard rule**: Use both `page_layouts` and `page_charts` for the same page only when the layout template is a compatible shell for the chart. Do not assign a conflicting layout just to fill every page: a waterfall chart should not inherit a timeline layout, and KPI cards should not inherit a circle-diagram layout unless that is the intended visual structure. When no compatible layout exists, omit the page from `page_layouts`.
>
> **Whole section omitted** → entire deck is free design. Equivalent to no rows but cleaner; do this when zero pages reference a template.
>
> **Strategist source**: `page_binding.json` 的受控轮换结果；需要人工复核时，用 `page_catalog.json` 或 `template_page_catalog.py search --compact --topology ... --emphasis ...` 查看紧凑候选。没有 Binder 时回退 `design_spec.md §VI Page Roster`（或 §IX outline）。New specs write only canonical references; never write a bare `content` type or an alias. Resolve uncertain values with `scripts/template_page_catalog.py`, then run `<project_path> validate-project`; missing files and aliases are hard failures before Executor.

## page_render_modes
- P01: themed_rebuild
- P02: brand_shell
- P03: mirror

> 可选，使用 deck/layout 模板时建议写入。`mirror` 只允许替换文字；`brand_shell` 保留品牌壳并重建正文；`themed_rebuild` 仅继承主题语言。旧项目缺失本段时，mirror 模板继续按整本 mirror 的旧行为执行。

## page_shell_assets
- P02: brand_header.png, footer_texture.png

> 仅为 `brand_shell` 页面声明可用的锁定模板资产，逗号分隔。优先使用 `page_binding.json` 的 `shell_assets`；未逐页声明时，schema v1 校验器回退到 `template_capabilities.json.shared_assets`。没有可锁定资产时使用 `themed_rebuild`，不得伪装成品牌壳。

## page_shell_requirements
- P02: identity=brand_header.png | background=footer_texture.png | forbid_unlocked_full_bleed=true

> schema v2 的 `brand_shell` 必填。直接继承 `page_binding.json.shell_requirements`：用 `|` 分隔角色，角色内多个候选文件用逗号分隔。页面必须命中每个必需角色；`background` 至少一个候选必须以 full-bleed 方式使用。`forbid_unlocked_full_bleed=true` 时，页面不得再使用未锁定的通用全幅背景。

## html_backgrounds
- P01: cover
- P02: theme
- P03: theme
- P04: chapter
- P10: ending

> One entry per page. Key: `P<NN>` matching §IX. Value: the HTML background template name — one of `cover` / `ending` / `chapter` / `theme`. Executor resolves it to `images/bg_<value>.png` (rendered by [`html_render.py`](../scripts/html_render.py)) and places it as the full-bleed background `<image>` first child of `<svg>` (see [shared-standards.md §4 Layered Background Structure](../references/shared-standards.md)).
>
> **Free Route only**: `html-led` 通常为内容页写 `theme`；`layout-led` 可按需使用；`full-free` 可省略。Deck Route 禁止本节，背景必须来自选中 Deck 的 `page_shell_assets/page_assets`。
>
> **No entry for a page** → 当前 route 不使用 HTML Background，或该页使用 route 允许的其他背景来源。
>
> **Strategist source**: Free Route 的背景策略与 page roster。所选 style/theme_palette 写在 `images/html_background_manifest.json` 顶层。

## page_charts
- P05: bar_chart
- P09: timeline
- P12: quadrant_bubble_scatter

> One entry per page **that adapts a `templates/charts/` data-chart OR structural-pattern template**. This includes comparisons, point diagrams, processes, matrices, agendas, teams, journeys, and strategic frameworks—not only numeric charts. Key: `P<NN>` matching §IX. Value: chart template basename without `.svg` (must match a key in `templates/charts/charts_index.json`).
>
> **No entry for a page** → no library visualization on that page, or an explicit `no-template-match` fallback recorded in `chart_selection.json`. Do not silently omit a catalog match.
>
> **Whole section omitted** → 渐进式查询后没有页面选择全局 chart 结构。
>
> **Strategist source**: copy from `design_spec.md §VII` and `<project_path>/chart_selection.json`—only rows whose path points to a real `templates/charts/` SVG. Pages marked `no-template-match` MUST NOT appear here.

## page_assets
- P05: shell=04b_content_flow | structure=local | source_scope=local | reuse_mode=brand_shell
- P09: structure=charts/pyramid_chart | source_scope=global | reuse_mode=structure_only

> 新项目按需填写。`shell` 记录选中的本地页面结构，`structure` 记录全局 chart/icon 结构；没有外部结构时可以写 `local`。声明外部结构的页面，在生成前 SVG 中必须给对应 `<g>` 写 `data-wtt-source="chart:<id>"` 或 `data-wtt-source="icon:<id>"`，由 `validate_asset_usage.py` 验收。旧项目缺失本段时保持兼容。

## chart_skin
- mode: structure_only
- color_source: colors
- typography_source: typography
- effects_source: visual_style

> Required whenever `page_charts` exists. The chart SVG supplies only structure: visualization type, geometry, relationship logic, label/legend placement, and series encoding. Its original colors, fonts, gradients, shadows, and effects are untrusted placeholders.
>
> Executor must re-skin every chart from the already selected deck/template identity:
> - primary series / dominant node → `colors.primary`
> - comparison series → `colors.secondary_accent` or another explicitly locked accent
> - semantic highlight → `colors.accent`
> - axes / grid / dividers / secondary labels → locked neutral roles such as `colors.grid`, `colors.border`, `colors.text_secondary`
> - additional series → opacity, dash, or PPT-safe pattern variants of locked colors; never invent a new HEX
> - all chart text → role-appropriate values from `typography`
>
> `visual_style` decides whether gradients/shadows exist. A flat selected template strips them; a gradient/glass template rebuilds them using locked colors. Never retain a chart template's original `<linearGradient>`, `fill`, `stroke`, or font family just because the geometry was reused.

## forbidden
- Mixing icon libraries
- rgba()
- `<style>`, `class`, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<script>`, `<iframe>`, `<symbol>`+`<use>`
- `<g opacity>` (set opacity on each child element individually)
- HTML named entities in text (`&nbsp;`, `&mdash;`, `&copy;`, `&ndash;`, `&reg;`, `&hellip;`, `&bull;` …) — write as raw Unicode (`—`, `©`, `→`, NBSP, etc.); XML reserved chars `& < > " '` must be escaped as `&amp; &lt; &gt; &quot; &apos;`. See shared-standards.md §1.0
