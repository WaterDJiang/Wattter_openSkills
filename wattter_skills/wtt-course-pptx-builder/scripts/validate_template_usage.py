#!/usr/bin/env python3
"""Validate per-page template adaptation modes beyond exact mirror pages.

`validate_mirror_fidelity.py` owns exact structural comparison. This validator
ensures every `brand_shell` page satisfies the locked asset roles, so a flexible
rebuild cannot pass by adding one logo while retaining an unrelated background.
Projects without `page_render_modes` remain backward compatible and are skipped.
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
    from course_backgrounds import load_background_catalog
    from template_capabilities import analyze_svg, analyze_template
    from update_spec import parse_lock
    from validate_mirror_fidelity import output_pages
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from course_backgrounds import load_background_catalog
    from template_capabilities import analyze_svg, analyze_template
    from update_spec import parse_lock
    from validate_mirror_fidelity import output_pages


def local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1]


def image_refs(svg_path: Path) -> set[str]:
    root = ET.parse(svg_path).getroot()
    refs: set[str] = set()
    for element in root.iter():
        if local_name(str(element.tag)) != "image":
            continue
        for name, value in element.attrib.items():
            if local_name(str(name)) != "href":
                continue
            href = str(value)
            refs.add("embedded:data" if href.startswith("data:") else Path(href).name)
    return refs


def split_assets(value: str) -> list[str]:
    return [
        Path(item.strip().strip("`")).name
        for item in re.split(r"[,，]", value)
        if item.strip()
    ]


def parse_shell_requirement(value: str) -> tuple[dict[str, list[str]], bool | None]:
    roles: dict[str, list[str]] = {}
    forbid_full_bleed: bool | None = None
    for part in value.split("|"):
        key, separator, raw = part.partition("=")
        if not separator:
            continue
        key = key.strip()
        raw = raw.strip()
        if key == "forbid_unlocked_full_bleed":
            if raw.lower() in {"true", "yes", "1"}:
                forbid_full_bleed = True
            elif raw.lower() in {"false", "no", "0"}:
                forbid_full_bleed = False
            continue
        assets = split_assets(raw)
        if assets:
            roles[key] = assets
    return roles, forbid_full_bleed


def load_capabilities(template_dir: Path) -> dict[str, Any]:
    path = template_dir / "template_capabilities.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return analyze_template(template_dir)


def validate_project(project_dir: Path) -> dict[str, Any]:
    lock_path = project_dir / "spec_lock.md"
    template_dir = project_dir / "templates"
    svg_dir = project_dir / "svg_output"
    result: dict[str, Any] = {
        "ok": True,
        "skipped": False,
        "checked": 0,
        "errors": [],
    }
    for required in (lock_path, template_dir, svg_dir):
        if not required.exists():
            result["errors"].append(f"missing required path: {required}")
    if result["errors"]:
        result["ok"] = False
        return result

    sections = parse_lock(lock_path)
    render_modes = sections.get("page_render_modes", {})
    try:
        background_catalog = load_background_catalog(template_dir)
    except (OSError, ValueError) as exc:
        result["ok"] = False
        result["errors"].append(f"background catalog read failed: {exc}")
        return result
    if not render_modes and not background_catalog:
        result["skipped"] = True
        return result
    shell_assets = sections.get("page_shell_assets", {})
    shell_requirements = sections.get("page_shell_requirements", {})
    pages, page_errors = output_pages(svg_dir)
    result["errors"].extend(page_errors)
    if background_catalog:
        catalog_files = {variant["file"] for variant in background_catalog}
        used: dict[str, Path] = {}
        for _, page_path in sorted(pages.items()):
            try:
                full_bleed = set(analyze_svg(page_path)["full_bleed_image_refs"])
            except (OSError, ET.ParseError) as exc:
                result["errors"].append(f"{page_path.name}: XML read failed: {exc}")
                continue
            for asset in sorted(full_bleed & catalog_files):
                first = used.setdefault(asset, page_path)
                if first != page_path:
                    result["errors"].append(
                        f"duplicate course background {asset}: {first.name}, {page_path.name}"
                    )

    try:
        capabilities = load_capabilities(template_dir)
    except (OSError, ValueError, json.JSONDecodeError, ET.ParseError) as exc:
        result["errors"].append(f"template capability read failed: {exc}")
        capabilities = {}
    package_assets = [
        Path(value).name for value in capabilities.get("shared_assets", [])
    ]
    capability_schema = int(capabilities.get("schema_version") or 1)
    asset_roles = {
        role: [Path(value).name for value in values]
        for role, values in (capabilities.get("asset_roles") or {}).items()
        if isinstance(values, list)
    }
    shell_contract = capabilities.get("shell_contract") or {}
    contract_required_roles = [
        role
        for role in shell_contract.get("required_roles", [])
        if isinstance(role, str)
    ]

    for page_id, mode in render_modes.items():
        if mode != "brand_shell":
            continue
        match = re.search(r"(\d+)$", page_id)
        if not match:
            result["errors"].append(f"invalid page_render_modes key: {page_id}")
            continue
        number = int(match.group(1))
        output_path = pages.get(number)
        if output_path is None:
            result["errors"].append(
                f"page_render_modes {page_id}: missing svg_output page sequence {number}"
            )
            continue
        required_assets = split_assets(shell_assets.get(page_id, ""))
        if not required_assets:
            required_assets = package_assets
        if not required_assets:
            result["errors"].append(
                f"page_render_modes {page_id}: brand_shell has no locked shared asset; "
                "use themed_rebuild or declare page_shell_assets"
            )
            continue
        try:
            actual_assets = image_refs(output_path)
            actual_full_bleed = {
                Path(value).name
                for value in analyze_svg(output_path).get(
                    "full_bleed_image_refs", []
                )
                if not value.startswith(("embedded:", "missing:"))
            }
        except (OSError, ET.ParseError) as exc:
            result["errors"].append(
                f"page_render_modes {page_id}: XML read failed: {exc}"
            )
            continue
        result["checked"] += 1
        has_page_contract = page_id in shell_requirements
        requirement_roles, page_forbid_full_bleed = parse_shell_requirement(
            shell_requirements.get(page_id, "")
        )
        strict_roles = capability_schema >= 2 or bool(requirement_roles)
        if not strict_roles and not actual_assets.intersection(required_assets):
            result["errors"].append(
                f"page_render_modes {page_id}: brand shell asset missing; "
                f"expected one of {required_assets}, found {sorted(actual_assets)}"
            )
            continue
        if not strict_roles:
            continue

        role_assets = requirement_roles if has_page_contract else asset_roles
        required_roles = (
            list(requirement_roles)
            if has_page_contract else list(dict.fromkeys(contract_required_roles))
        )
        for role in required_roles:
            expected = set(role_assets.get(role) or [])
            if not expected:
                result["errors"].append(
                    f"page_render_modes {page_id}: required shell role {role} "
                    "has no locked assets"
                )
                continue
            if not actual_assets.intersection(expected):
                result["errors"].append(
                    f"page_render_modes {page_id}: required shell role {role} missing; "
                    f"expected one of {sorted(expected)}, found {sorted(actual_assets)}"
                )

        expected_backgrounds = set(role_assets.get("background") or [])
        if "background" in required_roles and not actual_full_bleed.intersection(
            expected_backgrounds
        ):
            result["errors"].append(
                f"page_render_modes {page_id}: locked template background is not full-bleed; "
                f"expected one of {sorted(expected_backgrounds)}, "
                f"found full-bleed {sorted(actual_full_bleed)}"
            )
        forbid_full_bleed = (
            page_forbid_full_bleed
            if page_forbid_full_bleed is not None
            else bool(shell_contract.get("forbid_unlocked_full_bleed"))
        )
        if forbid_full_bleed and (has_page_contract or expected_backgrounds):
            unlocked = actual_full_bleed - expected_backgrounds
            if unlocked:
                result["errors"].append(
                    f"page_render_modes {page_id}: unlocked full-bleed background(s) "
                    f"{sorted(unlocked)}; allowed {sorted(expected_backgrounds)}"
                )

    result["ok"] = not result["errors"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hard-fail brand_shell pages that lose required template asset roles."
    )
    parser.add_argument("project_path", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate_project(args.project_path)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["skipped"]:
        print("[SKIP] no page_render_modes; template usage gate does not apply")
    elif result["ok"]:
        print(f"[OK] template usage: {result['checked']} brand_shell page(s)")
    else:
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"FAILED: {len(result['errors'])} error(s), "
            f"{result['checked']} brand_shell page(s) checked",
            file=sys.stderr,
        )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
