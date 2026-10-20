# Delivery and Verification

Use this file before final delivery. The report must be useful even when shared outside the coding environment.

## Required Artifacts

Every finished report folder should contain:

```text
report/
├── index.html
├── data/
│   └── analysis.json
├── css/
├── js/
├── screenshot-full.png
└── screenshot-1440.png      # optional preview
```

`screenshot-full.png` is required unless the user explicitly asks for HTML only.

## Long Screenshot Rules

- Capture the full page, not only the first viewport.
- Use a desktop width around `1440px`.
- Verify the PNG height is larger than the viewport height for long reports.
- The screenshot must include the footer/source/assumptions area.
- The backup PNG must preserve the same analytical story as the HTML, especially cross-dimensional sections such as heatmaps, platform-user tables, model-user tables, cohort matrices, or segment x period views.
- If the page is interactive, open all default-visible sections before capture.

## Preferred Capture Methods

### Codex in-app browser

When the Browser plugin is available and the report is already open, use the current tab and capture with `fullPage: true`. Save the bytes to the report folder as `screenshot-full.png`.

### Playwright

Use Playwright when a browser executable is available:

```js
await page.goto(`file://${reportPath}/index.html`, { waitUntil: "load" });
await page.screenshot({ path: `${reportPath}/screenshot-full.png`, fullPage: true });
```

If the bundled Playwright browser is missing, try the system browser only if allowed by the environment. Do not silently fall back to a viewport screenshot and call it full-page.

### Chrome CLI

Chrome CLI `--screenshot` is acceptable for a preview image, but it is often viewport-only. Treat it as `screenshot-1440.png` unless you verify the final PNG height covers the full report.

### Direct PNG Renderer

If browser screenshot is blocked or unavailable, render the backup PNG from `data/analysis.json`:

```bash
python3 <SKILL_ROOT>/scripts/render-analysis-png.py "$DIR/data/analysis.json" "$DIR/screenshot-full.png"
```

This image is not a pixel-exact browser screenshot, but it is a safe long PNG backup from the same analysis data. Use it when browser policy, missing Playwright browsers, or local GUI restrictions prevent full-page capture.

Direct-rendered PNGs must not drop high-value analysis panels. If the HTML includes heatmaps or cross-dimensional tables, the renderer must include them too.

## Verification Commands

Run:

```bash
rg "{{|必填|TODO|ExampleCo" "$DIR"
node --check "$DIR/js/report.js"
python3 -m json.tool "$DIR/data/analysis.json" >/dev/null
```

Then verify in browser:

- No console errors.
- No blank charts.
- No horizontal overflow.
- Text does not overlap.
- `screenshot-full.png` exists and has full-page height.

## If Full Screenshot Fails

Do not hide the failure. Deliver the HTML and explain:

- Which screenshot method failed.
- Whether a viewport screenshot was still produced.
- What command or browser capability is needed to produce the full-page backup.
