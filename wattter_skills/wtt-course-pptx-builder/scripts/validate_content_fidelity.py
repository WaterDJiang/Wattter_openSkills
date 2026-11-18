#!/usr/bin/env python3
"""Validate that locked course slide_text survives in generated SVG pages."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from course_pages import playback_pages


PAGE_FILE_RE = re.compile(r"^(?P<number>\d+)(?:[_\-.]|$)")
AUTHOR_METADATA_KEYS = {"raw_markdown"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"[\s:：,，。；;、!?！？·•\-—_]+", "", value)


def visible_leaf_paths(value: Any, path: str = "slide_text") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)] if value.strip() else []
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [(path, str(value))]
    if isinstance(value, list):
        return [
            leaf
            for index, item in enumerate(value)
            for leaf in visible_leaf_paths(item, f"{path}[{index}]")
        ]
    if isinstance(value, dict):
        return [
            leaf
            for key, item in value.items()
            if key not in AUTHOR_METADATA_KEYS
            for leaf in visible_leaf_paths(item, f"{path}.{key}")
        ]
    return []


def output_pages(svg_dir: Path) -> tuple[dict[int, Path], list[str]]:
    pages: dict[int, Path] = {}
    errors: list[str] = []
    for path in sorted(svg_dir.glob("*.svg")):
        match = PAGE_FILE_RE.match(path.name)
        if not match:
            continue
        number = int(match.group("number"))
        if number in pages:
            errors.append(
                f"duplicate SVG sequence {number}: {pages[number].name}, {path.name}"
            )
        else:
            pages[number] = path
    return pages, errors


def svg_visible_text(path: Path) -> str:
    root = ET.parse(path).getroot()
    text_parts: list[str] = []

    def walk(element: ET.Element, inherited_hidden: bool = False) -> None:
        style = str(element.get("style") or "").replace(" ", "").lower()
        opacity = str(element.get("opacity") or "").strip()
        hidden = inherited_hidden or (
            str(element.get("display") or "").lower() == "none"
            or str(element.get("visibility") or "").lower() in {"hidden", "collapse"}
            or opacity in {"0", "0.0", "0.00"}
            or "display:none" in style
            or "visibility:hidden" in style
            or re.search(r"(?:^|;)opacity:0(?:[.;]|$)", style) is not None
        )
        tag = str(element.tag).rsplit("}", 1)[-1]
        if tag == "text" and not hidden:
            text = "".join(element.itertext())
            if text.strip():
                text_parts.append(text)
            return
        for child in list(element):
            walk(child, hidden)

    walk(root)
    return normalize(" ".join(text_parts))


def find_bundle(project_dir: Path, explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        return explicit
    candidates = (
        project_dir / "sources" / "course-handoff",
        project_dir / "sources",
        project_dir / "course-handoff",
        project_dir,
    )
    return next(
        (
            candidate
            for candidate in candidates
            if (candidate / "course_contract.json").exists()
            or (candidate / "pages.jsonl").exists()
        ),
        None,
    )


def validate_project(
    project_dir: Path,
    *,
    bundle_dir: Path | None = None,
) -> dict[str, Any]:
    bundle = find_bundle(project_dir, bundle_dir)
    result: dict[str, Any] = {
        "ok": True,
        "skipped": bundle is None,
        "locked": None,
        "checked": 0,
        "errors": [],
        "warnings": [],
        "pages": [],
    }
    if bundle is None:
        return result
    try:
        contract = load_json(bundle / "course_contract.json")
        if not isinstance(contract, dict):
            raise ValueError("course_contract.json must be an object")
        pages = playback_pages(bundle, contract)
        if not all(isinstance(page.get("slide_text"), dict) for page in pages):
            raise ValueError("slide_text must be an object")
        if not isinstance(contract.get("outline"), dict):
            raise ValueError("course_contract.outline must be an object")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result["errors"].append(f"course handoff read failed: {exc}")
        result["ok"] = False
        result["skipped"] = False
        return result

    locked = bool((contract.get("outline") or {}).get("locked"))
    result["locked"] = locked
    svg_dir = project_dir / "svg_output"
    if not svg_dir.is_dir():
        result["errors"].append(f"missing svg_output in {project_dir}")
        result["ok"] = False
        result["skipped"] = False
        return result
    outputs, output_errors = output_pages(svg_dir)
    result["errors"].extend(output_errors)
    if len(outputs) != len(pages):
        result["errors"].append(
            f"page count mismatch: handoff={len(pages)}, svg_output={len(outputs)}"
        )

    for page in pages:
        sequence = page.get("sequence")
        page_id = page.get("page_id")
        output = outputs.get(sequence) if isinstance(sequence, int) else None
        page_result = {
            "page_id": page_id,
            "sequence": sequence,
            "output": output.name if output else None,
            "required": 0,
            "missing": [],
        }
        if output is None:
            message = f"{page_id}: missing SVG sequence {sequence}"
            result["errors"].append(message)
            result["pages"].append(page_result)
            continue
        try:
            visible = svg_visible_text(output)
        except (OSError, ET.ParseError) as exc:
            result["errors"].append(f"{page_id}: SVG read failed: {exc}")
            result["pages"].append(page_result)
            continue
        leaves = visible_leaf_paths(page.get("slide_text") or {})
        if "raw_markdown" in page.get("slide_text", {}):
            result["warnings"].append(
                f"{page_id}: legacy slide_text.raw_markdown ignored as author metadata; "
                "structured visible fields are still checked"
            )
        page_result["required"] = len(leaves)
        for path, text in leaves:
            expected = normalize(text)
            if expected and expected not in visible:
                page_result["missing"].append({"path": path, "text": text})
        if page_result["missing"]:
            message = (
                f"{page_id}: {len(page_result['missing'])}/{len(leaves)} "
                "slide_text leaf value(s) missing"
            )
            if locked:
                result["errors"].append(message)
            else:
                result["warnings"].append(message)
        result["checked"] += 1
        result["pages"].append(page_result)

    result["skipped"] = False
    result["ok"] = not result["errors"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", type=Path)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate_project(args.project_path, bundle_dir=args.bundle)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["skipped"]:
        print("[SKIP] no course handoff content contract")
    elif result["ok"]:
        print(
            f"[OK] content fidelity: {result['checked']} page(s), "
            f"{len(result['warnings'])} warning(s)"
        )
    else:
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        for page in result["pages"]:
            for missing in page["missing"]:
                print(
                    f"  {page['page_id']} {missing['path']}: {missing['text']}",
                    file=sys.stderr,
                )
        print(
            f"FAILED: {len(result['errors'])} error(s), "
            f"{result['checked']} page(s) checked",
            file=sys.stderr,
        )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
