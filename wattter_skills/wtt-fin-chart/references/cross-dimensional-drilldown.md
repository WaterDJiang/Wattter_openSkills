# Cross-Dimensional and Drilldown Analysis

Use this file whenever the dataset has more than one categorical dimension or any hierarchy that can explain a financial number. The goal is to move beyond one-dimensional rankings.

## Core Rule

Do not stop at separate totals like:

- Cost by platform
- Cost by model
- Cost by user

Those are only Level 1 summaries. A strong financial chart asks: which combinations create the number, and where should management act?

## Analysis Ladder

Use this ladder for every report when data supports it:

| Level | Question | Output |
|---|---|---|
| 0. Headline | What is the core conclusion? | Thesis + KPI cards |
| 1. Concentration | Which dimensions dominate alone? | Ranked bars / Pareto |
| 2. Cross driver | Which combinations dominate? | Heatmap / matrix / bubble grid |
| 3. Drilldown | What path explains the biggest number? | Top pairs / nested table / decomposition tree |
| 4. Action | Who owns it and what lever changes it? | Owner-lever table / next data request |

If Level 2 and Level 3 are missing while the data supports them, the analysis is incomplete.

## Dimension Discovery

Classify columns before charting:

```text
Time dimensions: date, week, month, quarter, fiscal period
Entity dimensions: customer, user, owner, department, project, cost center
Product dimensions: product, model, SKU, plan, feature, workload
Channel dimensions: platform, vendor, region, source, campaign
Measures: cost, revenue, margin, count, usage, tokens, requests, units
```

Then generate candidate crosses:

```text
entity × product
entity × channel
product × channel
time × product
time × entity
segment × metric
```

Prioritize crosses that answer an operational question. For cost reports, `platform × user`, `model × user`, `project × model`, and `vendor × workload` are usually more useful than standalone totals.

## Required Cross-Dimensional Patterns

### Heatmap / Matrix

Use when two categorical dimensions explain a measure.

Examples:

- Platform × User cost
- Model × Project cost
- Region × Product revenue
- Customer segment × Month churn

Rules:

- Keep rows and columns to the top contributors; group the rest as Other.
- Color intensity by value or share.
- Show exact numbers in cells when space permits.
- Add a readout explaining which cells require action.

### Top Pair Table

Use after the heatmap to make action ownership explicit.

Columns:

```text
Dimension A | Dimension B | Measure | Share | Interpretation / owner
```

Examples:

- Google × 生图、生视频服务 -> cost owner and workload lever
- gpt-5.4 × Duke -> model governance target
- Region East × Product A -> revenue concentration risk

### Drilldown Path

Use when a total can be decomposed into nested drivers:

```text
Total spend
  -> Platform
    -> Model
      -> User
        -> Project / usage party
```

Represent this as:

- Decomposition tree
- Nested ranked list
- Sankey / alluvial flow
- Multi-level table
- Breadcrumb cards

The drilldown should end in a management action, not just a deeper label.

### Time × Dimension Small Multiples

Use when there is a real time dimension.

Examples:

- Daily spend by platform
- Monthly revenue by segment
- Weekly margin by product line

Rules:

- Do not invent time trends from filename ranges; use row-level dates.
- If only one date exists, explicitly label it as a snapshot.
- Use small multiples when each segment has a different trend shape.

### Contribution / Variance Matrix

Use when comparing actual vs plan, current vs prior, or before vs after.

Rows = drivers, columns = periods or scenarios. Show:

- Absolute variance
- Percent variance
- Contribution to total variance

This is often better than a waterfall when multiple dimensions contribute at once.

## Drilldown Data Contract

Store cross-dimensional data in `analysis.json`:

```json
{
  "heatmaps": [
    {
      "title": "Platform × User cost",
      "rows": ["Google", "Fal"],
      "columns": ["公共服务", "Rowland"],
      "cells": [
        { "row": "Google", "column": "公共服务", "value": 147.31, "share": 0.281 }
      ]
    }
  ],
  "topPairs": [
    { "dimensionA": "Google", "dimensionB": "生图、生视频服务", "value": 147.31, "share": 0.281, "action": "拆任务类型和失败率" }
  ],
  "drilldowns": [
    {
      "path": ["Total", "Google", "gemini-3.1-flash-preview", "生图、生视频服务"],
      "value": 108.95,
      "insight": "最大成本路径来自视觉生成输出。"
    }
  ]
}
```

Names can vary by report, but the HTML and PNG backup should both preserve these sections.

## Minimum Bar

For any dataset with at least two categorical dimensions and one measure, the report must include:

- One single-dimension concentration chart.
- One cross-dimensional heatmap or matrix.
- One top-pair or drilldown table.
- One action recommendation tied to a specific combination, not just a generic dimension.

For datasets with a time dimension, add:

- One time × dimension trend, small multiple, or heatmap.

## Anti-Patterns

- Three separate ranked bars with no cross-analysis.
- Heatmap without exact values or owner/action interpretation.
- “Top users” chart that does not show which product/model/platform caused the spend.
- “Top models” chart that does not show which user/project invoked them.
- Drilldown that stops at labels and does not produce an action or next data request.
