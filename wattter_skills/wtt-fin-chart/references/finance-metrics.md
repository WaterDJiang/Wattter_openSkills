# Finance Metrics Reference

Use this file when converting raw financial data into a reliable chart-ready dataset.

## Data Contract

Prefer one structured object:

```js
const FIN_DATA = {
  company: "Company",
  currency: "USD",
  unit: "million",
  periods: ["Q1 FY25", "Q2 FY25", "Q3 FY25", "Q4 FY25"],
  metrics: {
    revenue: [],
    grossProfit: [],
    operatingIncome: [],
    netIncome: [],
    operatingCashFlow: [],
    capex: [],
    fcf: []
  },
  segments: [
    { name: "Segment A", values: [] }
  ],
  source: "User-provided data",
  assumptions: []
};
```

Rules:

- Keep raw values in numbers, not formatted strings.
- Keep percentages as decimals (`0.42` for 42%).
- Keep signs intact. Do not convert losses, cash burn, or capex to positive values unless the label explicitly says "cash outflow".
- Preserve source notes and footnotes.
- If a value is missing, use `null`, not `0`.

## Core Formulas

Revenue growth:

```text
growth = revenue_t / revenue_t-1 - 1
```

CAGR:

```text
CAGR = (ending_value / beginning_value)^(1 / number_of_periods) - 1
```

Gross margin:

```text
gross_margin = gross_profit / revenue
```

Operating margin:

```text
operating_margin = operating_income / revenue
```

Net margin:

```text
net_margin = net_income / revenue
```

Free cash flow:

```text
FCF = operating_cash_flow - capex
```

FCF margin:

```text
FCF_margin = FCF / revenue
```

Rule of 40:

```text
rule_of_40 = revenue_growth_rate + FCF_margin
```

Segment share:

```text
segment_share = segment_revenue / total_revenue
```

## SaaS / Subscription Metrics

ARR:

```text
ARR = MRR * 12
```

Net revenue retention:

```text
NRR = (starting_ARR + expansion - contraction - churn) / starting_ARR
```

Gross revenue retention:

```text
GRR = (starting_ARR - contraction - churn) / starting_ARR
```

CAC payback:

```text
CAC_payback_months = sales_and_marketing_spend / new_ARR_gross_profit_per_month
```

Magic number:

```text
magic_number = net_new_ARR / prior_quarter_sales_and_marketing_spend
```

Use SaaS metrics only when the user provides the required inputs. Do not infer them from revenue alone.

## Data Audit Checklist

- Periods are comparable: same fiscal calendar and same duration.
- Currency and units are consistent.
- Revenue is net revenue unless explicitly gross revenue.
- Segment values reconcile to total revenue, or the difference is labeled "Other / rounding".
- Percent signs are parsed correctly.
- One-time items are not mixed into recurring operating metrics unless labeled.
- TTM/LTM values are not plotted beside quarterly values on the same axis without a clear label.
- Market data dates are explicit.
- If using public company data, source the specific filing/report date.

## Financial Analysis Cautions

- A chart can show a signal; it should not overclaim causality.
- Margin expansion may come from mix, pricing, cost discipline, capitalization, or accounting changes. Label the hypothesis.
- Free cash flow can be distorted by working capital timing.
- Revenue acceleration without retention/cohort data may hide churn.
- Segment mix can improve revenue quality while lowering short-term gross margin.
- Valuation multiples need market date, share count, net cash/debt, and price source.
