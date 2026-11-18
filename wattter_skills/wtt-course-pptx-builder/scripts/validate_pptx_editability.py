#!/usr/bin/env python3
"""Validate that a PPTX contains editable DrawingML content, not page snapshots."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"p": P_NS, "a": A_NS}
SLIDE_RE = re.compile(r"^ppt/slides/slide(?P<number>\d+)\.xml$")
DEFAULT_MAX_PICTURE_ONLY_RATIO = 0.5


def _slide_number(name: str) -> int:
    match = SLIDE_RE.match(name)
    return int(match.group("number")) if match else 0


def analyze_slide(xml_bytes: bytes, *, slide_number: int) -> dict[str, Any]:
    root = ET.fromstring(xml_bytes)
    shape_nodes = root.findall(".//p:sp", NS)
    connector_nodes = root.findall(".//p:cxnSp", NS)
    graphic_nodes = root.findall(".//p:graphicFrame", NS)
    group_nodes = root.findall(".//p:grpSp", NS)
    picture_nodes = root.findall(".//p:pic", NS)
    text_shapes = sum(
        1 for shape in shape_nodes if shape.find(".//a:t", NS) is not None
    )
    editable_leaf_objects = (
        len(shape_nodes) + len(connector_nodes) + len(graphic_nodes)
    )
    picture_only = bool(picture_nodes) and editable_leaf_objects == 0
    blank = not picture_nodes and editable_leaf_objects == 0
    return {
        "slide": slide_number,
        "editable_leaf_objects": editable_leaf_objects,
        "text_shapes": text_shapes,
        "shape_objects": len(shape_nodes),
        "connector_objects": len(connector_nodes),
        "graphic_objects": len(graphic_nodes),
        "group_objects": len(group_nodes),
        "picture_objects": len(picture_nodes),
        "picture_only": picture_only,
        "blank": blank,
    }


def analyze_pptx(
    pptx_path: Path,
    *,
    max_picture_only_ratio: float = DEFAULT_MAX_PICTURE_ONLY_RATIO,
) -> dict[str, Any]:
    pptx_path = Path(pptx_path)
    if not pptx_path.is_file():
        raise FileNotFoundError(pptx_path)
    if not 0 <= max_picture_only_ratio <= 1:
        raise ValueError("max_picture_only_ratio must be between 0 and 1")

    with zipfile.ZipFile(pptx_path) as archive:
        slide_names = sorted(
            (name for name in archive.namelist() if SLIDE_RE.match(name)),
            key=_slide_number,
        )
        pages = [
            analyze_slide(
                archive.read(name),
                slide_number=_slide_number(name),
            )
            for name in slide_names
        ]

    picture_only_pages = [page["slide"] for page in pages if page["picture_only"]]
    blank_pages = [page["slide"] for page in pages if page["blank"]]
    page_count = len(pages)
    picture_only_ratio = len(picture_only_pages) / page_count if page_count else 1.0
    errors: list[str] = []
    warnings: list[str] = []
    if not pages:
        errors.append("PPTX contains no slide XML")
    if picture_only_ratio > max_picture_only_ratio:
        errors.append(
            "picture-only slide ratio exceeds threshold: "
            f"{len(picture_only_pages)}/{page_count} "
            f"({picture_only_ratio:.0%}) > {max_picture_only_ratio:.0%}"
        )
    elif picture_only_pages:
        warnings.append(
            "picture-only slides require manual confirmation: "
            + ", ".join(f"P{number:02d}" for number in picture_only_pages)
        )
    if blank_pages:
        warnings.append(
            "blank slides detected: "
            + ", ".join(f"P{number:02d}" for number in blank_pages)
        )

    return {
        "schema_version": 1,
        "pptx": str(pptx_path),
        "ok": not errors,
        "page_count": page_count,
        "picture_only_pages": picture_only_pages,
        "picture_only_ratio": round(picture_only_ratio, 6),
        "max_picture_only_ratio": max_picture_only_ratio,
        "totals": {
            "editable_leaf_objects": sum(
                page["editable_leaf_objects"] for page in pages
            ),
            "text_shapes": sum(page["text_shapes"] for page in pages),
            "group_objects": sum(page["group_objects"] for page in pages),
            "picture_objects": sum(page["picture_objects"] for page in pages),
        },
        "pages": pages,
        "warnings": warnings,
        "errors": errors,
        "generated_by": "scripts/validate_pptx_editability.py",
    }


def write_report(report: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument(
        "--max-picture-only-ratio",
        type=float,
        default=DEFAULT_MAX_PICTURE_ONLY_RATIO,
    )
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = analyze_pptx(
            args.pptx,
            max_picture_only_ratio=args.max_picture_only_ratio,
        )
    except (FileNotFoundError, OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"ERROR: editability validation failed: {exc}", file=sys.stderr)
        return 1

    if args.json_out:
        write_report(report, args.json_out)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        totals = report["totals"]
        print(
            "PPTX editability: "
            f"pages={report['page_count']}, "
            f"editable={totals['editable_leaf_objects']}, "
            f"text={totals['text_shapes']}, "
            f"pictures={totals['picture_objects']}, "
            f"picture-only={len(report['picture_only_pages'])}"
        )
        for warning in report["warnings"]:
            print(f"WARN: {warning}")
        for error in report["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

