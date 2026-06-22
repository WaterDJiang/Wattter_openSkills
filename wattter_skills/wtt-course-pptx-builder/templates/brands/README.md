# Brand Identity Presets

This directory holds **brand-only templates**: identity bundles (color / typography / logo / voice / icon style) without an SVG page roster. Strategist locks the brand's identity segment as truth; Executor designs pages freely under those constraints.

Brand is one of three template kinds in the library — alongside [`layouts/`](../layouts/) (structure-only) and [`decks/`](../decks/) (full-PPT replica). Full data model: [`docs/zh/templates-architecture.md`](../../../../docs/zh/templates-architecture.md).

## How brands are consumed

Brand application is selected via the **three-flow gate at SKILL.md Step 1** (flow 1 = library template). After selection at Step 3 flow 1, the brand lands in the **same project directory** (`<project_path>/templates/`):

| User choice at SKILL.md Step 1 / Step 3 flow 1 | Behavior |
|---|---|
| Flow 1, pick a brand from the `brands_index.json` menu (or give an explicit brand path like `templates/brands/anthropic/`) | Copy `design_spec.md` + logo files + asset subdirectories into `<project_path>/templates/`; Strategist locks identity segment |
| Bare brand name only ("use anthropic brand"), brand mention without selection, or flow 3 (free build) | Skip — bare names never auto-select; user must pick via flow 1 menu or give a path |
| Brand + layout (both selected in flow 1) | Fuse into one `design_spec.md` — brand owns identity segment (color / typography / logo / voice / icon style); layout owns structure segment (canvas / page roster). See `SKILL.md` Step 3. |
| Brand + deck (both selected in flow 1) | Fuse — brand identity overrides deck identity; structure + middle segments come from deck |
| Brand + layout + deck (all selected in flow 1) | Three-way fuse — brand=identity, layout=structure, deck=middle |
| Two brands selected | Conflict resolution prompt before fusion — user picks per-segment source |

`brands_index.json` is discovery-only — it populates the flow 1 menu and answers "what brands exist?"; listing alone never advances the pipeline.

## Creating a new brand

Run the standalone workflow:

```
Read ${SKILL_DIR}/workflows/create-brand.md
```

Three input paths are supported: brand asset (logo / brand site URL / branded PPTX / brand PDF), verbal spec dictated in chat, or empty skeleton for the user to fill in later.

## Package structure

Every brand directory is self-contained:

```
templates/brands/<brand_id>/
├── design_spec.md            # required — brand identity spec (7 sections)
├── logo.<ext>                # optional — primary brand logo (single-lockup brands)
│   …or…
├── <brand>_wordmark.<ext>    # optional — wordmark variant (dual-lockup brands)
├── <brand>_mark.<ext>        # optional — symbol / icon variant (dual-lockup brands)
├── images/                   # optional — branded photos
├── illustrations/            # optional — branded illustrations
└── icons/                    # optional — branded icon overrides
```

Logo filenames are descriptive, not contractual — `design_spec.md` §IV lists the exact files and the contexts in which each is used. Single-lockup brands typically ship one `logo.<ext>`; dual-lockup brands (e.g. Google's wordmark + G mark) ship separately named files.

`design_spec.md` carries a YAML frontmatter block with `kind: brand` and is the single source of truth for the brand identity. The six required sections are: I Brand Overview / II Color Scheme / III Typography / IV Logo / V Voice & Tone / VI Icon Style.

## Discovery index

[brands_index.json](./brands_index.json) is a slim machine-readable map (`brand_id → { kind, path, summary, primary_color }`). It is refreshed by `register_template.py --kind brand <brand_id>` after a brand is created or edited.

Listing the index populates the SKILL.md Step 3 flow 1 menu; it does not by itself advance the pipeline. A brand is used only when the user picks it via flow 1 (or gives an explicit path), regardless of whether it appears in the index.
