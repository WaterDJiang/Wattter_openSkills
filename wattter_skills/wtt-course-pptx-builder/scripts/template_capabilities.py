#!/usr/bin/env python3
"""Analyze editable/raster capabilities for every deck or layout template.

The analyzer is deterministic and read-only unless ``--write`` is supplied.
It never generates or modifies SVG files.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 3
CAPABILITY_FILE = "template_capabilities.json"
VECTOR_TAGS = {
    "path",
    "rect",
    "circle",
    "ellipse",
    "line",
    "polyline",
    "polygon",
    "use",
}
FRONTMATTER_MODE_RE = re.compile(
    r"(?m)^replication_mode:\s*(?P<mode>[a-z_-]+)\s*$"
)
DEFAULT_BACKGROUNDS_RE = re.compile(r"(?m)^default_background_assets:[ \t]*(.+)$")
NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?")
IDENTITY_ASSET_RE = re.compile(
    r"(?:brand|logo|lockup|wordmark|emblem|watermark|badge)",
    re.IGNORECASE,
)
BACKGROUND_ASSET_RE = re.compile(
    r"(?:background|backdrop|(?:^|[_-])bg(?:[_-]|$)|cloud|coast|texture|pattern)",
    re.IGNORECASE,
)
ILLUSTRATION_ASSET_RE = re.compile(
    r"(?:cutout|hero|illustration|figure|mascot|dove|train)",
    re.IGNORECASE,
)
DECORATIVE_ASSET_RE = re.compile(
    r"(?:glow|splash|streak|shadow|overlay|ornament|emblem|accent|blur|"
    r"signal|palm|leaf)",
    re.IGNORECASE,
)
PHOTO_ASSET_RE = re.compile(
    r"(?:photo|gallery|portrait|workers|platform|tunnel|corridor|depot|"
    r"building|team|flower|landscape|scene)",
    re.IGNORECASE,
)
IMPORTED_ATOM_GROUP_RE = re.compile(
    r"^(?:(?:layout|master)-)?shape-\d+$",
    re.IGNORECASE,
)
CHROME_GROUP_RE = re.compile(
    r"(?:^|[-_])(?:background|bg|decoration|decorations|decor|header|footer|"
    r"chrome|watermark|pagenumber|pagenum|nav|logo|rule)(?:[-_]|$)",
    re.IGNORECASE,
)
ASSET_ROLES = ("identity", "background", "chrome", "illustration")


def local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1]


def numeric(value: str | None) -> float | None:
    if value is None:
        return None
    match = NUMBER_RE.match(str(value).strip())
    return float(match.group(0)) if match else None


def href_value(element: ET.Element) -> str | None:
    for name, value in element.attrib.items():
        if local_name(str(name)) == "href":
            return str(value)
    return None


def replication_mode(template_dir: Path) -> str | None:
    spec = template_dir / "design_spec.md"
    if not spec.is_file():
        return None
    match = FRONTMATTER_MODE_RE.search(spec.read_text(encoding="utf-8")[:4000])
    return match.group("mode") if match else None


def canvas_size(root: ET.Element) -> tuple[float, float]:
    view_box = root.get("viewBox")
    if view_box:
        values = [numeric(part) for part in view_box.replace(",", " ").split()]
        if len(values) == 4 and values[2] and values[3]:
            return float(values[2]), float(values[3])
    return numeric(root.get("width")) or 1280.0, numeric(root.get("height")) or 720.0


def _effective_image_size(
    image: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
) -> tuple[float | None, float | None]:
    width = numeric(image.get("width"))
    height = numeric(image.get("height"))
    parent = parent_map.get(image)
    if (
        width is not None
        and height is not None
        and width <= 1.01
        and height <= 1.01
        and parent is not None
        and local_name(str(parent.tag)) == "svg"
    ):
        return numeric(parent.get("width")), numeric(parent.get("height"))
    return width, height


def _page_image_role(reference: str, *, full_bleed: bool) -> str:
    if IDENTITY_ASSET_RE.search(reference):
        return "identity"
    if full_bleed or BACKGROUND_ASSET_RE.search(reference):
        return "background"
    if DECORATIVE_ASSET_RE.search(reference):
        return "decoration"
    if ILLUSTRATION_ASSET_RE.search(reference) or PHOTO_ASSET_RE.search(reference):
        return "illustration"
    return "content_raster"


def analyze_svg(svg_path: Path) -> dict[str, Any]:
    root = ET.parse(svg_path).getroot()
    width, height = canvas_size(root)
    parent_map = {child: parent for parent in root.iter() for child in parent}
    counts = Counter(local_name(str(element.tag)) for element in root.iter())
    images = [
        element
        for element in root.iter()
        if local_name(str(element.tag)) == "image"
    ]
    texts = [
        element
        for element in root.iter()
        if local_name(str(element.tag)) in {"text", "tspan"}
    ]
    text_nodes = [
        element
        for element in root.iter()
        if local_name(str(element.tag)) == "text"
    ]
    source_texts = [
        "".join(element.itertext()).strip()
        for element in text_nodes
        if "".join(element.itertext()).strip()
    ]
    image_refs: list[str] = []
    full_bleed: list[str] = []
    image_instances: list[dict[str, Any]] = []
    for image in images:
        href = href_value(image)
        if href:
            reference = "embedded:data" if href.startswith("data:") else Path(href).name
            image_refs.append(reference)
        else:
            reference = "missing:href"
        image_width, image_height = _effective_image_size(image, parent_map)
        is_full_bleed = bool(
            image_width is not None
            and image_height is not None
            and image_width >= width * 0.88
            and image_height >= height * 0.88
        )
        if is_full_bleed:
            full_bleed.append(reference)
        coverage = 0.0
        if image_width is not None and image_height is not None and width and height:
            coverage = max(0.0, (image_width * image_height) / (width * height))
        image_instances.append(
            {
                "reference": reference,
                "role": _page_image_role(reference, full_bleed=is_full_bleed),
                "coverage_ratio": round(coverage, 6),
                "full_bleed": is_full_bleed,
            }
        )

    grouped_images: dict[str, dict[str, Any]] = {}
    for instance in image_instances:
        reference = instance["reference"]
        current = grouped_images.setdefault(
            reference,
            {
                "reference": reference,
                "role": instance["role"],
                "instances": 0,
                "max_coverage_ratio": 0.0,
                "full_bleed": False,
                "editable": False,
            },
        )
        current["instances"] += 1
        current["max_coverage_ratio"] = max(
            current["max_coverage_ratio"], instance["coverage_ratio"]
        )
        current["full_bleed"] = current["full_bleed"] or instance["full_bleed"]

    top_level_groups = [
        element
        for element in root
        if local_name(str(element.tag)) == "g"
    ]
    imported_group_count = sum(
        1
        for group in top_level_groups
        if IMPORTED_ATOM_GROUP_RE.fullmatch(group.get("id") or "")
    )
    chrome_group_count = sum(
        1
        for group in top_level_groups
        if CHROME_GROUP_RE.search(group.get("id") or "")
    )
    semantic_group_count = sum(
        1
        for group in top_level_groups
        if group.get("id")
        and not IMPORTED_ATOM_GROUP_RE.fullmatch(group.get("id") or "")
        and not CHROME_GROUP_RE.search(group.get("id") or "")
    )

    vector_elements = sum(counts[tag] for tag in VECTOR_TAGS)
    image_elements = len(images)
    text_elements = len(text_nodes)
    text_runs = max(counts["text"], counts["tspan"])
    if image_elements and text_elements <= 1 and vector_elements <= 5:
        composition = "raster_dominant"
    elif image_elements:
        composition = "hybrid"
    else:
        composition = "vector_dominant"

    image_assets = sorted(grouped_images.values(), key=lambda item: item["reference"])
    content_raster_refs = sorted(
        asset["reference"]
        for asset in image_assets
        if asset["role"] == "content_raster"
    )
    shell_raster_refs = sorted(
        asset["reference"]
        for asset in image_assets
        if asset["role"] in {"identity", "background", "decoration"}
    )
    illustration_refs = sorted(
        asset["reference"]
        for asset in image_assets
        if asset["role"] == "illustration"
    )
    editable_objects = vector_elements + text_elements
    object_total = editable_objects + image_elements
    editable_object_ratio = editable_objects / object_total if object_total else 0.0
    if not editable_objects and image_elements:
        editability_level = "raster_locked"
    elif content_raster_refs:
        editability_level = "mixed_content_raster"
    elif illustration_refs:
        editability_level = "editable_with_illustration"
    elif shell_raster_refs:
        editability_level = "editable_over_raster_shell"
    else:
        editability_level = "fully_editable"
    native_shape_ready = editable_objects > 0
    safe_for_mirror = text_elements > 0 and not content_raster_refs

    return {
        "file": svg_path.name,
        "composition_mode": composition,
        "image_elements": image_elements,
        "vector_elements": vector_elements,
        "text_elements": text_elements,
        "text_runs": text_runs,
        "source_text_chars": sum(len(text) for text in source_texts),
        "max_text_chars": max((len(text) for text in source_texts), default=0),
        "image_refs": sorted(set(image_refs)),
        "full_bleed_image_refs": sorted(set(full_bleed)),
        "image_assets": image_assets,
        "content_raster_refs": content_raster_refs,
        "native_editability": {
            "level": editability_level,
            "native_shape_ready": native_shape_ready,
            "editable_object_ratio": round(editable_object_ratio, 6),
            "top_level_groups": len(top_level_groups),
            "semantic_content_groups": semantic_group_count,
            "chrome_groups": chrome_group_count,
            "imported_atom_groups": imported_group_count,
            "direct_edit_strategy": "flatten_imported_single_child_groups",
        },
        "safe_for_mirror": safe_for_mirror,
        "recommended_fallback": (
            "brand_shell" if image_elements else "themed_rebuild"
        ),
    }


def analyze_template(template_dir: Path) -> dict[str, Any]:
    svg_files = sorted(template_dir.glob("*.svg"))
    if not svg_files:
        raise ValueError(f"no SVG files in template package: {template_dir}")
    pages = {path.stem: analyze_svg(path) for path in svg_files}
    asset_frequency = Counter(
        reference
        for page in pages.values()
        for reference in page["image_refs"]
        if not reference.startswith(("embedded:", "missing:"))
    )
    full_bleed_frequency = Counter(
        reference
        for page in pages.values()
        for reference in page["full_bleed_image_refs"]
        if not reference.startswith(("embedded:", "missing:"))
    )
    spec_path = template_dir / "design_spec.md"
    spec = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    parts = spec.split("---", 2)
    frontmatter = parts[1] if len(parts) == 3 and not parts[0].strip() else ""
    declaration = DEFAULT_BACKGROUNDS_RE.search(frontmatter)
    default_backgrounds = json.loads(declaration[1]) if declaration else []
    if not isinstance(default_backgrounds, list) or any(
        not isinstance(asset, str)
        or asset not in full_bleed_frequency
        or not (template_dir / asset).is_file()
        for asset in default_backgrounds
    ):
        raise ValueError("default_background_assets must list local full-bleed images")
    threshold = 1 if len(pages) == 1 else max(2, math.ceil(len(pages) * 0.5))
    shared_assets = sorted(
        reference
        for reference, count in asset_frequency.items()
        if count >= threshold or full_bleed_frequency[reference] >= 2
        or reference in default_backgrounds
    )
    full_bleed_assets = {
        reference
        for page in pages.values()
        for reference in page["full_bleed_image_refs"]
    }
    asset_roles: dict[str, list[str]] = {role: [] for role in ASSET_ROLES}
    for reference in shared_assets:
        if IDENTITY_ASSET_RE.search(reference):
            role = "identity"
        elif reference in full_bleed_assets or BACKGROUND_ASSET_RE.search(reference):
            role = "background"
        elif ILLUSTRATION_ASSET_RE.search(reference):
            role = "illustration"
        else:
            role = "chrome"
        asset_roles[role].append(reference)
    for page in pages.values():
        page["shared_asset_refs"] = sorted(
            set(page["image_refs"]) & set(shared_assets)
        )
        page["shared_asset_roles"] = {
            role: sorted(set(page["shared_asset_refs"]) & set(references))
            for role, references in asset_roles.items()
            if set(page["shared_asset_refs"]) & set(references)
        }
    required_roles = [
        role for role in ("identity", "background") if asset_roles[role]
    ]
    if not required_roles:
        required_roles = [
            role for role in ("chrome", "illustration") if asset_roles[role]
        ][:1]
    parent_kind = template_dir.parent.name
    return {
        "schema_version": SCHEMA_VERSION,
        "template_id": template_dir.name,
        "kind": parent_kind if parent_kind in {"decks", "layouts"} else "project",
        "replication_mode": replication_mode(template_dir),
        "page_count": len(pages),
        "shared_assets": shared_assets,
        **(
            {"default_background_assets": sorted(set(default_backgrounds))}
            if default_backgrounds else {}
        ),
        "asset_roles": asset_roles,
        "shell_contract": {
            "required_roles": required_roles,
            "forbid_unlocked_full_bleed": bool(asset_roles["background"]),
        },
        "pages": pages,
        "generated_by": "scripts/template_capabilities.py",
    }


def validate_capabilities(template_dir: Path, data: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    path = template_dir / CAPABILITY_FILE
    if data is None:
        if not path.is_file():
            return [f"missing {CAPABILITY_FILE} in {template_dir}"]
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return [f"invalid {path}: {exc}"]
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    # Library packages are keyed by their directory id. Project initialization
    # copies a selected package into the generic `<project>/templates/` folder;
    # preserve the source template_id there for provenance.
    if (
        template_dir.parent.name in {"decks", "layouts"}
        and data.get("template_id") != template_dir.name
    ):
        errors.append("template_id must equal package directory name")
    pages = data.get("pages")
    if not isinstance(pages, dict):
        return errors + ["pages must be an object keyed by SVG stem"]
    disk = {path.stem for path in template_dir.glob("*.svg")}
    declared = set(pages)
    for missing in sorted(disk - declared):
        errors.append(f"capability missing SVG: {missing}.svg")
    for orphan in sorted(declared - disk):
        errors.append(f"capability references missing SVG: {orphan}.svg")
    for reference, page in pages.items():
        prefix = f"pages.{reference}"
        if page.get("composition_mode") not in {
            "raster_dominant",
            "hybrid",
            "vector_dominant",
        }:
            errors.append(f"{prefix}.composition_mode is invalid")
        if page.get("recommended_fallback") not in {
            "brand_shell",
            "themed_rebuild",
        }:
            errors.append(f"{prefix}.recommended_fallback is invalid")
        for key in (
            "image_elements",
            "vector_elements",
            "text_elements",
            "text_runs",
            "source_text_chars",
            "max_text_chars",
        ):
            if not isinstance(page.get(key), int) or page[key] < 0:
                errors.append(f"{prefix}.{key} must be a non-negative integer")
        for key in ("image_refs", "full_bleed_image_refs", "shared_asset_refs"):
            value = page.get(key)
            if not isinstance(value, list) or any(
                not isinstance(item, str) for item in value
            ):
                errors.append(f"{prefix}.{key} must be an array of strings")
        image_assets = page.get("image_assets")
        if not isinstance(image_assets, list):
            errors.append(f"{prefix}.image_assets must be an array")
        else:
            for position, asset in enumerate(image_assets):
                asset_prefix = f"{prefix}.image_assets[{position}]"
                if not isinstance(asset, dict):
                    errors.append(f"{asset_prefix} must be an object")
                    continue
                if asset.get("role") not in {
                    "identity",
                    "background",
                    "decoration",
                    "illustration",
                    "content_raster",
                }:
                    errors.append(f"{asset_prefix}.role is invalid")
                if not isinstance(asset.get("instances"), int) or asset.get("instances", 0) < 1:
                    errors.append(f"{asset_prefix}.instances must be a positive integer")
                if not isinstance(asset.get("max_coverage_ratio"), (int, float)):
                    errors.append(f"{asset_prefix}.max_coverage_ratio must be numeric")
                if not isinstance(asset.get("full_bleed"), bool):
                    errors.append(f"{asset_prefix}.full_bleed must be boolean")
                if asset.get("editable") is not False:
                    errors.append(f"{asset_prefix}.editable must be false")
        content_raster_refs = page.get("content_raster_refs")
        if not isinstance(content_raster_refs, list) or any(
            not isinstance(item, str) for item in (content_raster_refs or [])
        ):
            errors.append(f"{prefix}.content_raster_refs must be an array of strings")
        native_editability = page.get("native_editability")
        if not isinstance(native_editability, dict):
            errors.append(f"{prefix}.native_editability must be an object")
        else:
            if native_editability.get("level") not in {
                "raster_locked",
                "mixed_content_raster",
                "editable_with_illustration",
                "editable_over_raster_shell",
                "fully_editable",
            }:
                errors.append(f"{prefix}.native_editability.level is invalid")
            if not isinstance(native_editability.get("native_shape_ready"), bool):
                errors.append(f"{prefix}.native_editability.native_shape_ready must be boolean")
            if not isinstance(native_editability.get("editable_object_ratio"), (int, float)):
                errors.append(f"{prefix}.native_editability.editable_object_ratio must be numeric")
            for key in (
                "top_level_groups",
                "semantic_content_groups",
                "chrome_groups",
                "imported_atom_groups",
            ):
                if not isinstance(native_editability.get(key), int) or native_editability.get(key, -1) < 0:
                    errors.append(f"{prefix}.native_editability.{key} must be a non-negative integer")
        for asset in page.get("image_refs", []):
            if asset.startswith(("embedded:", "missing:")) or "{{" in asset:
                continue
            if not (template_dir / asset).is_file():
                errors.append(f"{prefix}.image_refs missing asset: {asset}")
        shared_asset_roles = page.get("shared_asset_roles")
        if not isinstance(shared_asset_roles, dict):
            errors.append(f"{prefix}.shared_asset_roles must be an object")
        else:
            for role, assets in shared_asset_roles.items():
                if role not in ASSET_ROLES:
                    errors.append(f"{prefix}.shared_asset_roles has invalid role: {role}")
                if not isinstance(assets, list) or any(
                    not isinstance(item, str) for item in assets
                ):
                    errors.append(
                        f"{prefix}.shared_asset_roles.{role} must be an array of strings"
                    )
    shared_assets = data.get("shared_assets")
    if not isinstance(shared_assets, list) or any(
        not isinstance(item, str) for item in (shared_assets or [])
    ):
        errors.append("shared_assets must be an array of strings")
        shared_assets = []
    asset_roles = data.get("asset_roles")
    if not isinstance(asset_roles, dict):
        errors.append("asset_roles must be an object")
        asset_roles = {}
    for role in ASSET_ROLES:
        assets = asset_roles.get(role)
        if not isinstance(assets, list) or any(
            not isinstance(item, str) for item in (assets or [])
        ):
            errors.append(f"asset_roles.{role} must be an array of strings")
            continue
        for asset in assets:
            if asset not in shared_assets:
                errors.append(
                    f"asset_roles.{role} references non-shared asset: {asset}"
                )
    shell_contract = data.get("shell_contract")
    if not isinstance(shell_contract, dict):
        errors.append("shell_contract must be an object")
    else:
        required_roles = shell_contract.get("required_roles")
        if not isinstance(required_roles, list) or any(
            role not in ASSET_ROLES for role in (required_roles or [])
        ):
            errors.append("shell_contract.required_roles is invalid")
        else:
            for role in required_roles:
                if not asset_roles.get(role):
                    errors.append(
                        f"shell_contract.required_roles has no assets for role: {role}"
                    )
        if not isinstance(shell_contract.get("forbid_unlocked_full_bleed"), bool):
            errors.append("shell_contract.forbid_unlocked_full_bleed must be boolean")
    return errors


def write_capabilities(template_dir: Path, data: dict[str, Any]) -> Path:
    path = template_dir / CAPABILITY_FILE
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def package_dirs(templates_root: Path) -> list[Path]:
    result: list[Path] = []
    for kind in ("decks", "layouts"):
        root = templates_root / kind
        if not root.is_dir():
            continue
        result.extend(
            path
            for path in sorted(root.iterdir())
            if path.is_dir() and any(path.glob("*.svg"))
        )
    return result


def process_one(template_dir: Path, *, write: bool) -> tuple[dict[str, Any], list[str]]:
    data = analyze_template(template_dir)
    errors = validate_capabilities(template_dir, data)
    if not errors and write:
        write_capabilities(template_dir, data)
    return data, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "templates",
        help="One template package, or templates root with --all",
    )
    parser.add_argument("--all", action="store_true", help="Analyze all decks and layouts")
    parser.add_argument("--write", action="store_true", help=f"Write {CAPABILITY_FILE}")
    parser.add_argument("--validate", action="store_true", help="Validate existing sidecar only")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    targets = package_dirs(args.path) if args.all else [args.path]
    if not targets:
        print(f"ERROR: no template packages found under {args.path}", file=sys.stderr)
        return 1

    reports: list[dict[str, Any]] = []
    error_count = 0
    for target in targets:
        if args.validate:
            errors = validate_capabilities(target)
            data = None
        else:
            try:
                data, errors = process_one(target, write=args.write)
            except (OSError, ET.ParseError, ValueError) as exc:
                data, errors = None, [str(exc)]
        error_count += len(errors)
        reports.append(
            {
                "template": str(target),
                "ok": not errors,
                "page_count": data.get("page_count") if data else None,
                "errors": errors,
            }
        )
        if not args.json:
            if errors:
                for error in errors:
                    print(f"[ERROR] {target.name}: {error}")
            else:
                action = "wrote" if args.write else "analyzed"
                page_count = data.get("page_count") if data else "existing"
                print(f"[OK] {target.parent.name}/{target.name}: {action} {page_count} page(s)")
    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    if args.all and not args.json:
        print(f"[SUMMARY] templates={len(targets)} errors={error_count}")
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
