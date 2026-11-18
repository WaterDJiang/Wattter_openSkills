#!/usr/bin/env python3
"""Validate template-route isolation and declared page-asset provenance.

Decks are explicit, isolated visual systems. Free routes must never reference
``templates/decks``. A Deck route may reference only its selected Deck plus
global chart/icon structures. New projects may additionally declare
``spec_lock.page_assets``; those rows require matching ``data-wtt-source``
markers in pre-final SVG output.
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
    from course_pages import playback_pages
    from validate_content_fidelity import find_bundle, output_pages
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from update_spec import parse_lock
    from course_pages import playback_pages
    from validate_content_fidelity import find_bundle, output_pages


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _parse_asset_row(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for part in value.split("|"):
        key, separator, raw = part.partition("=")
        if separator:
            result[key.strip()] = raw.strip()
    return result


def _source_marker(asset: str) -> str | None:
    if asset.startswith("charts/"):
        return f"chart:{asset.split('/', 1)[1]}"
    if asset.startswith("icons/"):
        return f"icon:{asset.split('/', 1)[1]}"
    if asset in {"local", "free", "none"}:
        return None
    return asset


def _handoff_sequences(project_dir: Path) -> dict[str, int] | None:
    bundle = find_bundle(project_dir)
    if bundle is None:
        return None
    contract = _load_json(bundle / "course_contract.json")
    return {page["page_id"]: page["sequence"] for page in playback_pages(bundle, contract)}


def validate_project(project_dir: Path, preflight: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": True,
        "skipped": False,
        "checked_pages": 0,
        "errors": [],
    }
    binding_path = project_dir / "page_binding.json"
    lock_path = project_dir / "spec_lock.md"
    sections = parse_lock(lock_path) if lock_path.exists() else {}
    if not binding_path.exists() and not sections.get("route"):
        result["skipped"] = True
        return result
    binding: dict[str, Any] = {}
    if binding_path.exists():
        try:
            binding = _load_json(binding_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            result["errors"].append(f"page_binding read failed: {exc}")
            result["ok"] = False
            return result

    route = binding.get("route") or sections.get("route") or {}
    if not route:
        result["skipped"] = True
        return result
    route_kind = route.get("kind")
    if route_kind not in {"deck", "free"}:
        result["errors"].append("page_binding.route.kind must be deck or free")
        result["ok"] = False
        return result
    primary = route.get("primary_source")
    pages = binding.get("pages") or []
    if not isinstance(pages, list):
        result["errors"].append("page_binding.pages must be an array")
        pages = []

    if route_kind == "free":
        if isinstance(primary, str) and primary.startswith("decks/"):
            result["errors"].append("free route primary_source must not be a Deck")
        for page in pages:
            reference = str(page.get("layout_reference") or "")
            if "templates/decks/" in reference:
                result["errors"].append(
                    f"{page.get('page_id')}: free route references Deck layout {reference}"
                )
        for path in (lock_path,):
            if path.exists() and "templates/decks/" in path.read_text(
                encoding="utf-8"
            ):
                result["errors"].append(
                    f"free route contains Deck reference in {path.name}"
                )
    else:
        if not isinstance(primary, str) or not primary.startswith("decks/"):
            result["errors"].append("deck route primary_source must be decks/<id>")
        selected = primary.split("/", 1)[1] if isinstance(primary, str) and "/" in primary else ""
        binding_template = binding.get("template") or {}
        if binding and binding_template.get("package") != selected:
            result["errors"].append(
                "deck route primary_source does not match template.package"
            )
        for page in pages:
            reference = str(page.get("layout_reference") or "")
            if "templates/decks/" in reference and not reference.startswith(
                f"templates/decks/{selected}/"
            ):
                result["errors"].append(
                    f"{page.get('page_id')}: cross-Deck reference {reference}"
                )
            if reference.startswith("templates/layouts/"):
                result["errors"].append(
                    f"{page.get('page_id')}: Deck route must not mix Layout {reference}"
                )

    if lock_path.exists():
        lock_route = sections.get("route", {})
        if lock_route and binding:
            if lock_route.get("kind") != route_kind:
                result["errors"].append(
                    "spec_lock.route.kind does not match page_binding.route.kind"
                )
            if lock_route.get("primary_source") != (primary or "none"):
                result["errors"].append(
                    "spec_lock.route.primary_source does not match page_binding route"
                )
        lock_text = lock_path.read_text(encoding="utf-8")
        if route_kind == "deck":
            selected_prefix = f"templates/decks/{selected}/"
            for reference in re.findall(r"templates/decks/[^\\s|,)]+", lock_text):
                if not reference.startswith(selected_prefix):
                    result["errors"].append(
                        f"spec_lock contains cross-Deck reference {reference}"
                    )
            if "templates/layouts/" in lock_text:
                result["errors"].append(
                    "Deck route spec_lock must not reference layouts"
                )
            if "templates/html-background-styles/" in lock_text:
                result["errors"].append(
                    "Deck route spec_lock must not reference html-background-styles"
                )
        page_assets = sections.get("page_assets", {})
        if page_assets and not preflight:
            svg_dir = project_dir / "svg_output"
            page_files, page_errors = output_pages(svg_dir)
            result["errors"].extend(page_errors)
            try:
                sequences = _handoff_sequences(project_dir)
            except (OSError, ValueError) as exc:
                result["errors"].append(f"course handoff read failed: {exc}")
                result["ok"] = False
                return result
            for page_id, raw in page_assets.items():
                if sequences is not None:
                    if page_id not in sequences:
                        result["errors"].append(
                            f"page_assets {page_id}: page_id missing from course handoff"
                        )
                        continue
                    sequence = sequences[page_id]
                else:
                    match = re.search(r"(\d+)$", page_id)
                    if not match:
                        result["errors"].append(f"invalid page_assets key: {page_id}")
                        continue
                    sequence = int(match.group(1))
                svg_path = page_files.get(sequence)
                if svg_path is None:
                    result["errors"].append(
                        f"page_assets {page_id}: output SVG missing"
                    )
                    continue
                values = _parse_asset_row(raw)
                declared = [
                    marker
                    for key in ("shell", "structure")
                    if (marker := _source_marker(values.get(key, "")))
                ]
                if not declared:
                    continue
                svg_text = svg_path.read_text(encoding="utf-8")
                result["checked_pages"] += 1
                for marker in declared:
                    if f'data-wtt-source="{marker}"' not in svg_text:
                        result["errors"].append(
                            f"page_assets {page_id}: missing data-wtt-source={marker}"
                        )

    result["ok"] = not result["errors"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", type=Path)
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Validate route declarations before SVG output exists",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate_project(args.project_path, preflight=args.preflight)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["skipped"]:
        print("[SKIP] no page_binding.json; asset route gate does not apply")
    elif result["ok"]:
        print(
            f"[OK] asset route isolated; "
            f"{result['checked_pages']} page asset declaration(s) verified"
        )
    else:
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(result['errors'])} error(s)", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
