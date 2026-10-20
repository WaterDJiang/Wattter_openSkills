# Visual System

Use this file when choosing the look and interaction model for a financial HTML chart.

## Default Aesthetic

The default is "editorial finance": restrained, high-density, board-ready, but still beautiful.

Characteristics:

- Warm paper or soft neutral background.
- Strong black typography.
- Serif headlines for conclusions, sans-serif for body, mono for metadata.
- Thin rules, compact panels, no decorative blobs.
- Color is semantic, not ornamental.
- Each screen should feel like an analyst's argument, not a generic dashboard.

## Semantic Colors

Recommended tokens:

| Semantic | Token | Use |
|---|---|---|
| Growth / improvement | `--growth` | Revenue growth, positive drivers |
| Profit / margin | `--profit` | Gross/operating margin, contribution |
| Risk / decline | `--risk` | Negative drivers, misses, burn |
| Cash / liquidity | `--cash` | FCF, cash balance, working capital |
| Structure / mix | `--structure` | Segment mix, product categories |
| Ink | `--ink` | Text and final totals |
| Muted | `--muted` | Secondary labels |

Never rely on color alone. Use signs, labels, and annotations.

## Output Modes

### 1. Board Snapshot

Best for executive review.

- One core thesis at the top.
- 3-5 KPI cards.
- 2-4 chart panels.
- Clear source and assumptions footer.
- Minimal animation.

### 2. Investor Narrative

Best for fundraising, IR, or public storytelling.

- More editorial title hierarchy.
- Stronger readout copy.
- Segment mix and durability signals.
- Carefully labeled caveats.

### 3. Operating Dashboard

Best for internal metric review.

- Denser layout.
- Trends, thresholds, and variance callouts.
- Optional filters if the data supports them.
- Tables only below charts or in expandable detail.

### 4. Market Monitor

Best for valuation, comps, or trading data.

- Darker or higher-contrast palette is acceptable.
- Timestamp is mandatory.
- Data recency and source must be prominent.
- Avoid implying live data unless it is actually live.

## Typography Rules

- Page H1 is a conclusion, not a label.
- Chart H3 is also a conclusion.
- Use mono text for periods, source, units, tick-like metadata.
- Do not scale text with viewport width except for true page-level headings.
- Long Chinese titles should be manually broken into lines.

## Layout Rules

- Do not put cards inside cards.
- Keep chart panels at 8px radius or less.
- Use consistent panel padding.
- KPI cards should not dominate more than one-third of the first viewport.
- Every chart needs enough height to read axis labels.
- Mobile layout should become one column with charts stacked in reading order.

## Interaction Rules

Add interaction only when it helps analysis:

- Tooltip for exact values.
- Legend toggle for multi-series charts.
- Segment selector when the dataset is too wide.
- Scenario toggle for forecast/base/upside cases.

Avoid interaction when:

- The output is meant for screenshot/PDF.
- The user only needs a board-ready static chart.
- Interactions hide important assumptions.

## Copy Rules

Good chart title:

```text
Revenue growth is now converting into operating leverage
```

Weak chart title:

```text
Revenue and Margin Chart
```

Good readout:

```text
Readout: The revenue bar shows scale; the margin line shows whether each incremental dollar is becoming more profitable.
```

Weak readout:

```text
This chart shows revenue and margin.
```
