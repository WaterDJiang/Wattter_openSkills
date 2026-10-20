# wtt-fin-chart Checklist

Run this before final delivery.

## Data Integrity

- Source is shown on the page.
- Currency and unit are shown.
- Period labels are explicit.
- Filename date ranges and detail-row dates are reconciled; mismatches are stated as caveats.
- Percentages are decimals in code and formatted as percentages in UI.
- Missing values are `null`, not `0`.
- Segment totals reconcile to total, or the gap is labeled.
- Workbook summary totals reconcile with detail totals.
- Any derived metric formula is defensible.
- Assumptions are written in the footer or notes.
- Public-company "latest" data is verified against authoritative sources.

## Insight Quality

- The H1 states a conclusion.
- The page has one core thesis.
- KPI cards are limited to the metrics that support the thesis.
- If the dataset has 2+ categorical dimensions, the report includes at least one cross-dimensional chart.
- If the dataset has a hierarchy or owner/action fields, the report includes at least one drilldown or top-pair module.
- Separate one-dimensional rankings are not treated as a complete analysis.
- Every chart panel answers a specific financial question.
- Every chart has a readout sentence.
- There is at least one caveat, risk, or next-data request when the data is incomplete.
- The output avoids investment advice unless the user explicitly asked for a properly caveated investment memo.

## Chart Quality

- Axis labels are readable.
- Dual axes are labeled and used only for related metrics.
- Heatmaps or matrices show exact values, not only color.
- Top-pair/drilldown tables include measure, share, and interpretation/action.
- Margin lines are formatted as percentages.
- Currency values use compact notation with unit context.
- Positive and negative bridge items are visually distinct.
- Annotations highlight real inflection points, not decoration.
- Legends are short and do not wrap badly.
- Tooltips show exact values.

## Visual Quality

- No emoji icons.
- No 3D chart effects.
- No decorative blobs/orbs.
- No card inside card.
- Panel radius is 8px or less.
- Text does not overflow on desktop or mobile.
- Mobile view stacks charts in a logical narrative order.
- The page can be understood from a screenshot.

## HTML Verification

Run:

```bash
rg "{{|必填|TODO|ExampleCo" <output-dir>
node --check <output-dir>/js/report.js
python3 -m json.tool <output-dir>/data/analysis.json >/dev/null
```

Then open `index.html` or use Playwright/browser screenshot checks:

- 1440x900
- 1920x1080
- 390x844

Confirm:

- No console errors.
- ECharts loads or a local fallback is used.
- No blank charts.
- Tooltips work.
- Resize does not break layout.
- Source and assumptions remain visible.
- `screenshot-full.png` exists as a full-page backup, not only a first-screen preview.
- `screenshot-full.png` includes cross-dimensional analysis panels from the HTML, such as heatmaps and top pair tables.
