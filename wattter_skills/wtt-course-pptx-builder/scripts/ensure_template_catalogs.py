#!/usr/bin/env python3
"""Generate deterministic baseline page catalogs for built-in decks/layouts.

The generator never edits SVG files. Existing catalogs are preserved unless
``--force`` is supplied. Rich semantic hints come from the shared
``content_forms.json.page_variant_tags`` dictionary; filename parsing is the
fallback for structural/legacy pages.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from derive_content_forms import classify
from template_page_catalog import validate_catalog
from variant_selection import infer_variant_profile


SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
CONTENT_FORMS_PATH = TEMPLATES_DIR / "charts" / "content_forms.json"


PAGE_LABELS = {
    "cover": "封面",
    "toc": "目录",
    "chapter": "章节过渡",
    "content": "内容页",
    "ending": "封底",
}


def _page_type(stem: str) -> tuple[str, bool]:
    info = classify(stem)
    if info.get("page_type") in PAGE_LABELS:
        return str(info["page_type"]), False
    if "reference" in stem.lower():
        return "content", True
    match = re.search(r"(cover|toc|chapter|content|ending)", stem.lower())
    return (match.group(1) if match else "content"), False


def _layout_id(stem: str, page_type: str) -> str:
    match = re.match(
        r"^\d+[a-z]?_(cover|toc|chapter|content|ending)(?:_(.*))?$",
        stem.lower(),
    )
    suffix = match.group(2) if match else stem.lower()
    suffix = suffix or "default"
    value = re.sub(r"[^a-z0-9]+", "_", suffix).strip("_")
    return f"{page_type}_{value or 'default'}"


def _keywords(stem: str, page_type: str, forms: list[str]) -> list[str]:
    tokens = [
        token
        for token in re.split(r"[^a-z0-9\u4e00-\u9fff]+", stem.lower())
        if token and not token.isdigit()
    ]
    values = [PAGE_LABELS[page_type], page_type, *forms, *tokens]
    return list(dict.fromkeys(str(value) for value in values if value))


def _selection(
    stem: str,
    page_type: str,
    tag: dict[str, Any] | None,
    *,
    reference_only: bool,
) -> dict[str, Any]:
    tag = tag or {}
    forms = list(tag.get("content_forms") or [])
    dimensions = tag.get("dimensions") or {}
    info = classify(stem)
    item_count = dimensions.get("slots") or info.get("count")
    structure = forms[0] if forms else (
        f"{page_type} anchor" if page_type != "content" else "free content shell"
    )
    slots = {
        "cover": ["title", "subtitle"],
        "toc": ["title", "agenda"],
        "chapter": ["chapter_number", "title", "subtitle"],
        "content": ["title", "body"],
        "ending": ["closing_title", "closing_note"],
    }[page_type]
    result: dict[str, Any] = {
        "structure": structure,
        "content_slots": slots,
        "use_cases": [
            "视觉参考，不作为输出页候选"
            if reference_only
            else f"{PAGE_LABELS[page_type]}内容承载"
        ],
        "avoid_when": ["页面类型、内容关系或固定槽位与当前内容不匹配"],
        "keywords": _keywords(stem, page_type, forms),
        "visuals": ["继承当前模板的几何结构与视觉语言"],
        "image_requirements": ["按模板现有图片槽位；无图片槽位时不要求"],
        "content_density": (
            "low" if page_type in {"cover", "chapter", "ending"} else "medium"
        ),
        "content_forms": forms,
    }
    if page_type == "content" and not forms and not reference_only:
        result["generic_shell"] = True
    if isinstance(item_count, int):
        result["item_count"] = item_count
    result["variant_profile"] = infer_variant_profile(
        stem,
        selection=result,
        tag=tag,
    )
    return result


def build_catalog(template_dir: Path, kind: str) -> dict[str, Any]:
    content_forms = json.loads(CONTENT_FORMS_PATH.read_text(encoding="utf-8"))
    page_tags = content_forms.get("page_variant_tags") or {}
    pages: list[dict[str, Any]] = []
    for sequence, svg_path in enumerate(sorted(template_dir.glob("*.svg")), start=1):
        stem = svg_path.stem
        page_type, inferred_reference = _page_type(stem)
        reference_only = inferred_reference or stem == "reference_style"
        tag = page_tags.get(f"{kind}/{template_dir.name}/{stem}")
        pages.append(
            {
                "reference": stem,
                "file": svg_path.name,
                "source_slide": sequence,
                "page_type": page_type,
                "layout_id": _layout_id(stem, page_type),
                "label": f"{PAGE_LABELS[page_type]} · {stem}",
                "usage": "reference_only" if reference_only else "output",
                "aliases": [],
                "selection": _selection(
                    stem,
                    page_type,
                    tag,
                    reference_only=reference_only,
                ),
            }
        )
    return {
        "schema_version": 1,
        "selection_contract_version": 2,
        "template_id": template_dir.name,
        f"{'deck' if kind == 'decks' else 'layout'}_id": template_dir.name,
        "reference_format": "basename",
        "selection_policy": {
            "match_order": [
                "page_type",
                "content_forms",
                "item_count",
                "variant_profile",
                "content_density",
                "image_requirements",
            ],
            "fallback": "no-template-match",
        },
        "pages": pages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kind",
        choices=("decks", "layouts", "all"),
        default="all",
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    kinds = ("decks", "layouts") if args.kind == "all" else (args.kind,)
    generated = 0
    preserved = 0
    errors: list[str] = []
    for kind in kinds:
        root = TEMPLATES_DIR / kind
        for template_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            catalog_path = template_dir / "page_catalog.json"
            if catalog_path.exists():
                existing = json.loads(catalog_path.read_text(encoding="utf-8"))
                preserve = (
                    not args.force
                    or existing.get("reference_format")
                    != "basename"
                )
                if preserve:
                    preserved += 1
                    catalog_errors = validate_catalog(template_dir)
                    errors.extend(
                        f"{kind}/{template_dir.name}: {error}"
                        for error in catalog_errors
                    )
                    continue
            catalog = build_catalog(template_dir, kind)
            if args.write:
                catalog_path.write_text(
                    json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            generated += 1
            if args.write:
                catalog_errors = validate_catalog(template_dir)
                errors.extend(
                    f"{kind}/{template_dir.name}: {error}"
                    for error in catalog_errors
                )

    for error in errors:
        print(f"[ERROR] {error}")
    action = "generated" if args.write else "would-generate"
    print(
        f"[SUMMARY] {action}={generated} preserved={preserved} errors={len(errors)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
