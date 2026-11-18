# SVG Visualization Template Library

This directory contains the standardized SVG visualization templates used by PPT Master — charts, infographics, process diagrams, relationship diagrams, and strategic frameworks. The directory name `charts/` is kept for backward compatibility; the library scope is broader than charts.

## Source of truth

[`charts_index.json`](./charts_index.json) is the single source of truth for inventory and human-readable selection summaries. Runtime selection first queries `content_forms.json.chart_tags`; the model receives only compact candidates instead of reading all 71 entries.

Every indexed SVG receives a runtime `variant_profile` from explicit tags or deterministic filename inference. When multiple charts serve the same form and slot count, `variant_selection.py` rotates only inside the semantic-equivalence pool using an outline-hash seed. Explicit composition topology/emphasis wins; mirror and unique-candidate paths remain stable.

## Style rules

See [`CHART_STYLE_GUIDE.md`](./CHART_STYLE_GUIDE.md) for color palette, typography, and SVG authoring conventions all templates must follow.

## Usage

Before generating a chart page, open the corresponding `<key>.svg` file to read its structure and layout. Files are named after the `key` field in `charts_index.json` (e.g. `bar_chart.svg`, `quadrant_bubble_scatter.svg`). Templates are named by visual structure, not by business-model name — keywords like SWOT, BCG, PEST, OKR, Porter's Five Forces, Value Chain are matched via each template's `summary` field.
