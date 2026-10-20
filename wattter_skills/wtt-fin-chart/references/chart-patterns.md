# Financial Chart Patterns

Use this file after the financial data has been audited. Start with the question, then choose the chart.

## Chart Selection Matrix

| Question | Best Chart | Use When | Avoid When |
|---|---|---|---|
| Is the business getting larger and better? | Bar + margin line combo | Revenue and margin move together | Periods are not comparable |
| What drove profit change? | Waterfall / bridge | Need cause and contribution | Drivers are not additive |
| Which segment is taking share? | Stacked bar or 100% stacked bar | Segment mix matters | Segment totals do not reconcile |
| Where is growth coming from? | Small multiples by segment | Different growth shapes | Too many tiny categories |
| Which combinations drive the number? | Heatmap / matrix | Two dimensions and one measure exist | Rows/columns are too sparse without grouping |
| Which owner-action pairs matter? | Top pair table | Need accountability and next action | Only one dimension is available |
| What is the dominant drilldown path? | Decomposition tree / nested table | Total can be broken into hierarchy | Hierarchy is inferred but not in data |
| Is the trend concentrated in certain segments? | Time x dimension heatmap / small multiples | Real row-level time exists | Filename implies time but rows do not |
| Is cash conversion improving? | FCF bar + FCF margin line | Cash matters as much as P&L | Working capital timing dominates |
| Are costs scaling efficiently? | Common-size P&L | Opex lines as % revenue | Absolute cost levels are the point |
| What does the income statement look like structurally? | P&L common-size stacked/negative bars | Need gross profit, opex, operating income as % revenue | Revenue base is missing or restated |
| Which expense category is consuming the most economics? | Donut / pie, max 5 slices | Final-period expense mix is the question | More than 5 categories or time trend is more important |
| Is the balance sheet asset-heavy or liability-heavy? | Balance-sheet structure stacked bars | Assets, liabilities, and equity reconcile | Balance sheet line items do not reconcile |
| Where did cash move this period? | CFO / investing / financing bar chart + net cash line | Cash-flow statement lines exist | Only FCF is available |
| Is financial health improving? | Ratio trend / small multiple bars | Liquidity, leverage, return, or turnover ratios are available | Ratios use inconsistent denominators |
| Is valuation rich or cheap versus peers? | Scatter plot | Peer group with consistent metrics | Peer set is weak or cherry-picked |
| Where are the anomalies? | Heatmap | Period x segment/operator matrix | Values need exact reading |
| How did guidance change? | Range band + actual line | Forecast/actual tracking | Guidance methodology changed |
| What changed between two periods? | Slopegraph | Few metrics, clear before/after | More than 8 lines |

## Required Readout Per Chart

Every chart panel needs a readout sentence:

```text
Readout: <what to look at> because <why it matters>.
```

Examples:

- Readout: Bars show scale; the margin line shows whether growth is translating into operating leverage.
- Readout: The bridge isolates contribution, so the audience can see whether profit growth came from revenue, margin, or cost discipline.
- Readout: Segment mix matters because the same revenue growth can have different durability depending on the source.

## Annotation Rules

Add annotations when:

- A metric crosses an important threshold.
- Growth changes direction.
- A one-time event distorts the series.
- A segment overtakes another.
- A margin gap opens or closes.

Keep annotations short. One chart should rarely have more than 2-3 callouts.

## Common Financial Visuals

### Revenue + Margin Combo

Use for board-level overview. Bars are revenue, lines are gross/operating/FCF margin.

Do:

- Use left axis for currency, right axis for margin.
- Label final values directly when possible.
- Keep no more than two margin lines.

Do not:

- Put too many lines over bars.
- Use dual axes for unrelated metrics.

### Waterfall / Bridge

Use for operating profit, EBITDA, FCF, ARR, or revenue bridge.

Do:

- Start and end with absolute totals.
- Use green for positive drivers and red for negative drivers.
- Ensure all intermediate values are additive.

Do not:

- Use a waterfall for percentages unless the math is additive percentage points.
- Hide "other" when the bridge does not reconcile.

### Mix Shift

Use stacked bars for absolute contribution; use 100% stacked bars for share.

Do:

- Sort segments by strategic importance or final-period size.
- Keep categories under 6; group the rest as "Other".

Do not:

- Use 100% bars when absolute growth is the actual story.

### Cross-Dimensional Heatmap

Use when the real question is not "which platform?" or "which user?", but "which platform-user combination?"

Do:

- Choose two dimensions that create accountability.
- Show exact values inside cells when possible.
- Sort rows and columns by total contribution.
- Use color intensity for share or value.
- Follow with a top-pair table so the insight becomes operational.

Do not:

- Use a heatmap as decoration.
- Hide the largest cells behind hover-only tooltips.
- Include too many low-value rows/columns; group the tail.

### Drilldown Table / Decomposition Tree

Use when the audience needs to understand where a total comes from.

Do:

- Start with the total and move through driver levels.
- End with a specific owner, lever, caveat, or next data request.
- Keep shares at each level visible.

Do not:

- Stop at separate summaries.
- Present a drilldown path if the source data does not contain the relationship.

### Common-Size P&L

Use when the question is operating leverage.

Do:

- Convert each cost line to percentage of revenue.
- Put revenue at 100% and show cost layers beneath.

Do not:

- Mix absolute and percentage cost lines in the same stacked chart.

### Expense Mix Donut

Use when the audience asks for a quick picture of where costs sit today.

Do:

- Keep it to 3-5 categories, grouping the tail as "Other".
- Label each slice with share, not only hover tooltip.
- Use the latest period unless the user asks for a specific period.

Do not:

- Use a pie/donut when the core question is trend over time.
- Split small categories until labels collide.

### Balance Sheet Structure

Use when the report needs a real financial dashboard, not only P&L.

Do:

- Show assets beside liabilities + equity, or clearly separate the two stacks.
- Keep current/non-current split visible when available.
- Add a caveat if assets do not equal liabilities plus equity.

Do not:

- Mix point-in-time balance-sheet values with quarterly flow metrics without labeling the period.

### Cash-Flow Statement Bars

Use when the audience needs CFO, investing cash flow, financing cash flow, and net cash movement.

Do:

- Keep outflows negative when source data is signed.
- Use a net cash change line or marker when the three sections reconcile.
- Show FCF separately if capex is material.

Do not:

- Flip capex to positive unless the label says "Capex outflow".

### Peer Valuation Scatter

Use when comparing public companies or business units.

Do:

- Put quality/growth on x-axis and valuation on y-axis.
- Size dots by revenue or market cap.
- Label the focal company and outliers.

Do not:

- Compare companies with incompatible business models without a caveat.

## Anti-Patterns

- Pie charts for financial mix with more than 3 categories.
- Dense tables as the hero visual.
- Separate one-dimensional ranking charts with no cross-dimensional view.
- 3D bars, bevels, drop shadows, decorative gauges.
- Unlabeled dual axes.
- Using red/green without also using labels or signs.
- Showing exact values when the insight is directional, or showing only direction when the board needs exact values.
