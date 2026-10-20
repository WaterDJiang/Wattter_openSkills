# Spreadsheet Ingestion

Use this file when the input is `.xlsx`, `.xls`, `.csv`, `.tsv`, or a workbook exported from billing/finance systems.

## Required Workflow

1. Inspect sheet names, shapes, columns, and first rows.
2. Identify the row-level detail sheet before using summary sheets.
3. Remove subtotal/total rows from detail analysis.
4. Parse date columns with `errors="coerce"` and keep only rows with real dates for time-series claims.
5. Reconcile totals across detail, summary, and pivot sheets.
6. Write the cleaned dataset and derived metrics to `data/analysis.json`.
7. Identify categorical dimensions and generate cross-dimensional candidates before choosing charts.

## Pandas Pattern

```python
import pandas as pd
from pathlib import Path

path = Path("input.xlsx")
xl = pd.ExcelFile(path)
print(xl.sheet_names)

for sheet in xl.sheet_names:
    df = pd.read_excel(path, sheet_name=sheet)
    print(sheet, df.shape, list(df.columns))
    print(df.head(8))

detail = pd.read_excel(path, sheet_name="汇总")
parsed = pd.to_datetime(detail["日期"], errors="coerce")
detail = detail[parsed.notna()].copy()
detail["日期"] = parsed[parsed.notna()].dt.strftime("%Y-%m-%d")
detail["费用(USD)"] = pd.to_numeric(detail["费用(USD)"], errors="coerce").fillna(0)
```

## Reconciliation Rules

- Detail total must match summary total within rounding tolerance.
- If summary has multiple blocks, parse each block explicitly; do not infer block membership from blank rows alone.
- Keep workbook-provided classifications when the detail sheet lacks the classification logic.
- If filename implies a range but detail rows only contain one date, report it as a single-date snapshot and write the mismatch into caveats.
- If a sheet contains "小计" or "总计", treat those rows as summary rows, not detail rows.

## Cost Report Derivations

For LLM/billing reports, consider deriving:

- Total spend.
- Platform spend and share.
- Model spend and share.
- User/project spend and share.
- Top-N concentration: top 2 models, top 5 models, top 3 users.
- Workload buckets, such as visual generation vs text/code, only when the mapping is explicit and documented.
- Platform x user heatmap for responsibility boundaries.
- Model x user, platform x model, project x model, or vendor x workload cross-tabs when columns exist.
- Top pair tables that connect cost/revenue to an owner or action.
- Drilldown paths such as total -> platform -> model -> user -> project.
- Caveats for missing request count, token count, job count, failure retries, or unit price.

## Output Data Contract

Write a JSON object such as:

```json
{
  "sourceFile": "input.xlsx",
  "periodLabel": "2026-05-20",
  "rowCount": 89,
  "total": 524.22,
  "kpis": [],
  "platform": [],
  "model": [],
  "user": [],
  "insights": [],
  "risks": [],
  "actions": []
}
```

This makes the HTML auditable and lets the same analysis be reused for screenshots, docs, or future reports.
