#!/usr/bin/env python3
"""Validate chart-library selection and handoff for a PPT Builder project.

The chart library is a structure source, never a visual-theme source. This
validator makes that contract machine-checkable before Executor generation:

- the full catalog read is recorded;
- selected keys and SVG files exist;
- chart_selection.json and spec_lock.md page_charts agree exactly;
- chart skin comes from the already locked deck theme;
- pages combining page_layouts + page_charts explicitly confirm compatibility.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from update_spec import parse_lock
except ImportError:  # pragma: no cover - supports direct module loading
    parse_lock = None


PAGE_RE = re.compile(r"^P\d{2,3}$")
EXPECTED_SKIN_POLICY = {
    "mode": "structure_only",
    "color_source": "spec_lock.colors",
    "typography_source": "spec_lock.typography",
    "effects_source": "spec_lock.visual_style",
}
EXPECTED_LOCK_SKIN = {
    "mode": "structure_only",
    "color_source": "colors",
    "typography_source": "typography",
    "effects_source": "visual_style",
}


def _load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required file: {path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path} must contain a JSON object")
        return {}
    return value


def _normalized_page(value: Any) -> str:
    return str(value or "").strip().upper()


def validate(project: Path, skill_root: Path) -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    stats = {"catalog": 0, "selected": 0, "fallbacks": 0, "runners_up": 0}

    catalog_path = skill_root / "templates" / "charts" / "charts_index.json"
    catalog_doc = _load_json(catalog_path, errors)
    charts = catalog_doc.get("charts", {})
    meta = catalog_doc.get("meta", {})
    if not isinstance(charts, dict):
        errors.append("charts_index.json: `charts` must be an object")
        charts = {}
    stats["catalog"] = len(charts)
    declared_total = meta.get("total")
    if declared_total != len(charts):
        errors.append(
            f"charts_index.json total mismatch: meta.total={declared_total}, actual={len(charts)}"
        )

    # Content-form dictionary (content_forms.json). Optional but, when a page
    # declares a `form`, the chosen template must serve it — catches the
    # classic "4 items" ambiguity (points_4 vs flow_4 vs matrix_2x2).
    cf_path = skill_root / "templates" / "charts" / "content_forms.json"
    chart_forms: dict[str, list[str]] = {}
    if cf_path.is_file():
        try:
            cf_doc = json.loads(cf_path.read_text(encoding="utf-8"))
            chart_forms = {
                cid: list(t.get("content_forms", []))
                for cid, t in cf_doc.get("chart_tags", {}).items()
            }
        except (OSError, ValueError) as exc:
            warnings.append(f"content_forms.json unreadable, form checks skipped: {exc}")

    selection_path = project / "chart_selection.json"
    selection = _load_json(selection_path, errors)
    design_spec_path = project / "design_spec.md"
    try:
        design_spec = design_spec_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing required file: {design_spec_path}")
        design_spec = ""
    except OSError as exc:
        errors.append(f"failed to read {design_spec_path}: {exc}")
        design_spec = ""

    read_audit = selection.get("catalog_read", {})
    if not isinstance(read_audit, dict):
        errors.append("chart_selection.json: `catalog_read` must be an object")
        read_audit = {}
    if read_audit.get("path") != "templates/charts/charts_index.json":
        errors.append(
            "chart_selection.json: catalog_read.path must be "
            "`templates/charts/charts_index.json`"
        )
    if read_audit.get("count") != len(charts):
        errors.append(
            "chart_selection.json: catalog_read.count must equal the live catalog "
            f"count ({len(charts)})"
        )
    if f"Catalog read: {len(charts)} templates" not in design_spec:
        errors.append(
            f"design_spec.md §VII must contain `Catalog read: {len(charts)} templates`"
        )

    skin_policy = selection.get("skin_policy", {})
    if skin_policy != EXPECTED_SKIN_POLICY:
        errors.append(
            "chart_selection.json: skin_policy must declare structure-only reuse "
            "with colors/typography/effects sourced from spec_lock"
        )

    lock_path = project / "spec_lock.md"
    if parse_lock is None:
        errors.append("cannot import scripts/update_spec.py parse_lock")
        lock: dict[str, dict[str, str]] = {}
    elif not lock_path.exists():
        errors.append(f"missing required file: {lock_path}")
        lock = {}
    else:
        try:
            lock = parse_lock(lock_path)
        except Exception as exc:  # pragma: no cover - defensive I/O guard
            errors.append(f"failed to parse {lock_path}: {exc}")
            lock = {}

    page_charts = lock.get("page_charts", {})
    page_layouts = lock.get("page_layouts", {})
    chart_skin = lock.get("chart_skin", {})

    pages = selection.get("pages", [])
    if not isinstance(pages, list):
        errors.append("chart_selection.json: `pages` must be an array")
        pages = []

    selected: dict[str, str] = {}
    selected_rows: dict[str, dict[str, Any]] = {}
    seen_pages: set[str] = set()
    for index, row in enumerate(pages):
        label = f"chart_selection.json pages[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        page = _normalized_page(row.get("page"))
        if not PAGE_RE.fullmatch(page):
            errors.append(f"{label}.page must match PNN or PNNN, got {page!r}")
            continue
        if page in seen_pages:
            errors.append(f"{label}: duplicate page {page}")
            continue
        seen_pages.add(page)

        template = row.get("template")
        if template is None:
            stats["fallbacks"] += 1
            if row.get("status") != "no-template-match":
                errors.append(f"{label}: null template requires status `no-template-match`")
            if not str(row.get("fallback") or "").strip():
                errors.append(f"{label}: no-template-match requires a fallback")
            if not str(row.get("reason") or "").strip():
                errors.append(f"{label}: no-template-match requires a reason")
            continue

        if not isinstance(template, str) or not template.strip():
            errors.append(f"{label}.template must be a chart key or null")
            continue
        template = template.strip()
        stats["selected"] += 1
        selected[page] = template
        selected_rows[page] = row

        chart_entry = charts.get(template)
        if not isinstance(chart_entry, dict):
            errors.append(f"{label}: unknown chart key `{template}`")
            continue

        # Content-form dimension check: if the page declares a `form`, the
        # chosen template must serve it. Declared forms live in
        # chart_selection.json rows (written by Strategist or match_content_forms.py).
        declared_form = row.get("form")
        if declared_form and chart_forms:
            served = chart_forms.get(template, [])
            if served and declared_form not in served:
                errors.append(
                    f"{label}: declared form `{declared_form}` not served by `{template}` "
                    f"(serves {served}) — form↔template 维度冲突，换 template 或改正声明的 form"
                )

        expected_path = f"templates/charts/{template}.svg"
        if row.get("path") != expected_path:
            errors.append(f"{label}.path must be `{expected_path}`")
        if not (skill_root / expected_path).is_file():
            errors.append(f"{label}: missing chart SVG `{expected_path}`")

        summary = str(chart_entry.get("summary") or "")
        quote = str(row.get("summary_quote") or "")
        if not quote or quote not in summary or not quote.startswith("Pick for "):
            errors.append(
                f"{label}.summary_quote must be a verbatim `Pick for ...` excerpt "
                "from charts_index.json"
            )
        if not str(row.get("usage") or "").strip():
            errors.append(f"{label}.usage is required")
        for required_text, field in (
            (page, "page"),
            (template, "template"),
            (expected_path, "path"),
            (quote, "summary_quote"),
        ):
            if required_text and required_text not in design_spec:
                errors.append(
                    f"design_spec.md §VII is missing {field} value "
                    f"from {label}: `{required_text}`"
                )

    normalized_lock_charts = {
        _normalized_page(page): str(template).strip()
        for page, template in page_charts.items()
    }
    for page, template in normalized_lock_charts.items():
        if not PAGE_RE.fullmatch(page):
            errors.append(f"spec_lock.md page_charts has invalid page key `{page}`")
        if template not in charts:
            errors.append(f"spec_lock.md page_charts {page}: unknown chart key `{template}`")
        elif not (skill_root / "templates" / "charts" / f"{template}.svg").is_file():
            errors.append(f"spec_lock.md page_charts {page}: missing `{template}.svg`")

    if selected != normalized_lock_charts:
        missing_in_lock = sorted(set(selected.items()) - set(normalized_lock_charts.items()))
        missing_in_selection = sorted(set(normalized_lock_charts.items()) - set(selected.items()))
        if missing_in_lock:
            errors.append(
                "selected chart rows missing/mismatched in spec_lock.page_charts: "
                + ", ".join(f"{p}={t}" for p, t in missing_in_lock)
            )
        if missing_in_selection:
            errors.append(
                "spec_lock.page_charts rows missing/mismatched in chart_selection.json: "
                + ", ".join(f"{p}={t}" for p, t in missing_in_selection)
            )

    if selected and chart_skin != EXPECTED_LOCK_SKIN:
        errors.append(
            "spec_lock.md: chart pages require `## chart_skin` with "
            "mode=structure_only, color_source=colors, "
            "typography_source=typography, effects_source=visual_style"
        )
    if selected and "spec_lock.colors + typography + visual_style" not in design_spec:
        errors.append(
            "design_spec.md §VII must declare Skin source "
            "`spec_lock.colors + typography + visual_style`"
        )

    for index, row in enumerate(pages):
        if not isinstance(row, dict) or row.get("template") is not None:
            continue
        page = _normalized_page(row.get("page"))
        matching_lines = [
            line for line in design_spec.splitlines()
            if page in line and "no-template-match" in line
        ]
        if not matching_lines:
            errors.append(
                f"design_spec.md §VII must record `{page}` with `no-template-match`"
            )

    overlap = sorted(set(selected) & {_normalized_page(p) for p in page_layouts})
    for page in overlap:
        row = selected_rows[page]
        if row.get("compatible_shell") is not True:
            errors.append(
                f"{page} uses both page_layouts and page_charts; set "
                "compatible_shell=true only after confirming the layout is a compatible shell"
            )
        if not str(row.get("compatibility_note") or "").strip():
            errors.append(
                f"{page} uses both page_layouts and page_charts; compatibility_note is required"
            )

    runners = selection.get("runners_up", [])
    if not isinstance(runners, list):
        errors.append("chart_selection.json: `runners_up` must be an array")
        runners = []
    stats["runners_up"] = len(runners)
    if selected and len(runners) < 3:
        errors.append("chart_selection.json: at least 3 runners_up are required")
    for index, row in enumerate(runners):
        label = f"chart_selection.json runners_up[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        template = str(row.get("template") or "").strip()
        page = _normalized_page(row.get("rejected_for"))
        if template not in charts:
            errors.append(f"{label}: unknown chart key `{template}`")
        if page not in seen_pages:
            errors.append(f"{label}.rejected_for must reference a page in `pages`")
        if not str(row.get("reason") or "").strip():
            errors.append(f"{label}.reason is required")

    if not selected and not pages:
        warnings.append(
            "No catalog template selected. This is valid only after all pages were "
            "semantically matched against the full catalog."
        )

    return errors, warnings, stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate chart selection, mapping, files, and deck-skin inheritance."
    )
    parser.add_argument("project_path", help="PPT Builder project directory")
    args = parser.parse_args()

    project = Path(args.project_path).expanduser().resolve()
    skill_root = Path(__file__).resolve().parent.parent
    errors, warnings, stats = validate(project, skill_root)

    print(
        "[chart-mapping] "
        f"catalog={stats['catalog']} selected={stats['selected']} "
        f"fallbacks={stats['fallbacks']} runners_up={stats['runners_up']}"
    )
    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")

    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASSED: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
