#!/usr/bin/env python3
"""Validate that mirror-mode pages preserve their selected template structure.

Mirror pages may edit text content only. Element order, attributes, geometry,
images, and decorative structure must remain unchanged.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

try:
    from template_page_catalog import CatalogError, load_catalog, resolve_reference
    from update_spec import parse_lock
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from template_page_catalog import CatalogError, load_catalog, resolve_reference
    from update_spec import parse_lock


PAGE_FILE_RE = re.compile(r"^(?P<number>\d+)(?:[_\-.]|$)")
RENDER_MODES = {"mirror", "brand_shell", "themed_rebuild"}
FRONTMATTER_MODE_RE = re.compile(
    r"(?m)^replication_mode:\s*(?P<mode>[a-z_-]+)\s*$"
)


def local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1]


def replication_mode(template_dir: Path) -> str | None:
    path = template_dir / "design_spec.md"
    if not path.is_file():
        return None
    match = FRONTMATTER_MODE_RE.search(path.read_text(encoding="utf-8")[:4000])
    return match.group("mode") if match else None


def normalize_attr(name: str, value: str) -> str:
    if local_name(name) == "href" and not value.startswith("data:"):
        return Path(value).name
    return value


def structural_signature(path: Path) -> list[tuple[str, str, tuple[tuple[str, str], ...]]]:
    root = ET.parse(path).getroot()
    signature: list[tuple[str, str, tuple[tuple[str, str], ...]]] = []

    def walk(element: ET.Element, location: str) -> None:
        tag = local_name(str(element.tag))
        attrs = tuple(
            sorted(
                (local_name(str(name)), normalize_attr(str(name), str(value)))
                for name, value in element.attrib.items()
            )
        )
        signature.append((location, tag, attrs))
        child_counts: dict[str, int] = {}
        for child in list(element):
            child_tag = local_name(str(child.tag))
            child_counts[child_tag] = child_counts.get(child_tag, 0) + 1
            walk(child, f"{location}/{child_tag}[{child_counts[child_tag]}]")

    walk(root, f"/{local_name(str(root.tag))}[1]")
    return signature


def first_difference(
    expected: list[tuple[str, str, tuple[tuple[str, str], ...]]],
    actual: list[tuple[str, str, tuple[tuple[str, str], ...]]],
) -> str:
    for index, (left, right) in enumerate(zip(expected, actual)):
        if left != right:
            return f"element[{index}] expected={left} actual={right}"
    if len(expected) != len(actual):
        return f"element count expected={len(expected)} actual={len(actual)}"
    return "unknown structural difference"


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


def resolve_template_svg(
    template_dir: Path,
    catalog: dict[str, Any] | None,
    reference: str,
) -> Path:
    needle = Path(reference).name
    if needle.endswith(".svg"):
        needle = needle[:-4]
    if catalog is not None:
        page = resolve_reference(catalog, needle)
        return template_dir / page["file"]
    return template_dir / f"{needle}.svg"


def validate_project(project_dir: Path) -> dict[str, Any]:
    template_dir = project_dir / "templates"
    mode = replication_mode(template_dir)
    result: dict[str, Any] = {
        "ok": True,
        "skipped": mode != "mirror",
        "replication_mode": mode,
        "checked": 0,
        "errors": [],
    }
    if mode != "mirror":
        lock_path = project_dir / "spec_lock.md"
        if lock_path.is_file():
            render_modes = parse_lock(lock_path).get("page_render_modes", {})
            illegal = sorted(
                page_id
                for page_id, render_mode in render_modes.items()
                if render_mode == "mirror"
            )
            if illegal:
                result["ok"] = False
                result["skipped"] = False
                result["errors"].append(
                    "page_render_modes declares mirror for a non-mirror template: "
                    + ", ".join(illegal)
                )
        return result

    lock_path = project_dir / "spec_lock.md"
    svg_dir = project_dir / "svg_output"
    if not lock_path.is_file():
        result["errors"].append(f"missing spec_lock.md in {project_dir}")
    if not svg_dir.is_dir():
        result["errors"].append(f"missing svg_output in {project_dir}")
    if result["errors"]:
        result["ok"] = False
        result["skipped"] = False
        return result

    catalog: dict[str, Any] | None = None
    if (template_dir / "page_catalog.json").is_file():
        try:
            catalog = load_catalog(template_dir)
        except CatalogError as exc:
            result["errors"].append(str(exc))

    sections = parse_lock(lock_path)
    layouts = sections.get("page_layouts", {})
    render_modes = sections.get("page_render_modes", {})
    result["render_modes"] = {
        mode_name: sum(1 for value in render_modes.values() if value == mode_name)
        for mode_name in sorted(RENDER_MODES)
    }
    for page_id, render_mode in render_modes.items():
        if render_mode not in RENDER_MODES:
            result["errors"].append(
                f"page_render_modes {page_id}: invalid mode {render_mode!r}; "
                f"expected one of {sorted(RENDER_MODES)}"
            )
        if render_mode == "mirror" and page_id not in layouts:
            result["errors"].append(
                f"page_render_modes {page_id}: mirror requires page_layouts entry"
            )
    if render_modes:
        for page_id in sorted(set(layouts) - set(render_modes)):
            result["errors"].append(
                f"page_layouts {page_id}: missing page_render_modes entry"
            )

    pages, page_errors = output_pages(svg_dir)
    result["errors"].extend(page_errors)
    for page_id, reference in layouts.items():
        # Backward compatibility: projects without page_render_modes preserve
        # the former deck-level mirror behavior and validate every mapped page.
        # Once page modes exist, only exact-fit mirror pages are structurally
        # locked. brand_shell/themed_rebuild are validated by their own gates.
        if render_modes and render_modes.get(page_id) != "mirror":
            continue
        match = re.search(r"(\d+)$", page_id)
        if not match:
            result["errors"].append(f"invalid page_layouts key: {page_id}")
            continue
        number = int(match.group(1))
        output_path = pages.get(number)
        if output_path is None:
            result["errors"].append(
                f"page_layouts {page_id}: missing svg_output page sequence {number}"
            )
            continue
        try:
            template_path = resolve_template_svg(template_dir, catalog, reference)
        except CatalogError as exc:
            result["errors"].append(f"page_layouts {page_id}: {exc}")
            continue
        if not template_path.is_file():
            result["errors"].append(
                f"page_layouts {page_id}: missing template SVG {template_path.name}"
            )
            continue
        try:
            expected = structural_signature(template_path)
            actual = structural_signature(output_path)
        except (ET.ParseError, OSError) as exc:
            result["errors"].append(f"page_layouts {page_id}: XML read failed: {exc}")
            continue
        result["checked"] += 1
        if expected != actual:
            result["errors"].append(
                f"page_layouts {page_id}: mirror structure drift "
                f"({template_path.name} -> {output_path.name}): "
                f"{first_difference(expected, actual)}"
            )

    result["skipped"] = False
    result["ok"] = not result["errors"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hard-fail mirror projects whose output changed non-text template structure."
    )
    parser.add_argument("project_path", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = validate_project(args.project_path)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["skipped"]:
        print(
            f"[SKIP] replication_mode={result['replication_mode'] or 'unset'}; "
            "mirror fidelity does not apply"
        )
    elif result["ok"]:
        print(f"[OK] mirror fidelity: {result['checked']} mapped page(s)")
    else:
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"FAILED: {len(result['errors'])} error(s), "
            f"{result['checked']} mapped page(s) checked",
            file=sys.stderr,
        )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
