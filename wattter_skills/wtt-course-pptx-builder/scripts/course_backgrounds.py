"""Match a deck's optional image catalog to distinct course pages."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

CATALOG_FILE = "background_catalog.json"
ROLE_BY_PAGE_TYPE = {"cover": "cover", "section_opener": "chapter", "closer": "ending"}
TEXT_AREA_BY_ROLE = {
    "cover": "left_light",
    "chapter": "right_dark",
    "break": "left_light",
    "ending": "left_light",
}
BREAK_TITLE = re.compile(
    r"^(?:中场休息|课间休息|短暂休息|休息(?:一下|$|\s|[0-9])|intermission\b|(?:coffee|short) break\b)",
    re.IGNORECASE,
)


def load_background_catalog(template_dir: Path) -> list[dict[str, Any]]:
    path = template_dir / CATALOG_FILE
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    variants = data.get("variants") if isinstance(data, dict) else None
    if not isinstance(variants, list) or not variants:
        raise ValueError(f"{path}: variants must be a non-empty list")
    seen: set[str] = set()
    for variant in variants:
        if not isinstance(variant, dict):
            raise ValueError(f"{path}: each variant must be an object")
        file = variant.get("file")
        role = variant.get("role")
        keywords = variant.get("keywords")
        if (
            not isinstance(file, str) or Path(file).name != file
            or not file.endswith(".png") or file in seen
            or not (template_dir / file).is_file()
            or not isinstance(role, str) or role not in TEXT_AREA_BY_ROLE
            or variant.get("text_area") != TEXT_AREA_BY_ROLE[role]
            or not isinstance(variant.get("subject"), str)
            or not isinstance(keywords, list)
            or any(not isinstance(word, str) or not word.strip() for word in keywords)
            or not (keywords or variant.get("fallback") is True)
        ):
            raise ValueError(f"{path}: invalid variant {variant}")
        seen.add(file)
    return variants


def background_role(page: dict[str, Any]) -> str | None:
    page_type = page["page_type"]
    if page_type in ROLE_BY_PAGE_TYPE:
        return ROLE_BY_PAGE_TYPE[page_type]
    if page_type == "content" and (page.get("teaching") or {}).get("mode") == "transition":
        title = (page.get("slide_text") or {}).get("title") or page.get("display_title") or ""
        if isinstance(title, str) and BREAK_TITLE.match(title.strip()):
            return "break"
    return None


def _normalized(text: str) -> str:
    return re.sub(r"\s+", "", text.casefold())


def assign_backgrounds(
    requests: dict[str, tuple[str, str]],
    variants: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Reserve semantic matches before spending generic fallbacks, without repeats."""
    matches = []
    for page_order, (page_id, (role, text)) in enumerate(requests.items()):
        text = _normalized(text)
        for variant_order, variant in enumerate(variants):
            if variant["role"] != role:
                continue
            words = {_normalized(word) for word in variant["keywords"]}
            score = sum(len(word) for word in words if word in text)
            if score:
                matches.append((-score, page_order, variant_order, page_id))
    chosen: dict[str, dict[str, Any]] = {}
    used: set[str] = set()
    for _, _, variant_order, page_id in sorted(matches):
        variant = variants[variant_order]
        if page_id not in chosen and variant["file"] not in used:
            chosen[page_id] = variant
            used.add(variant["file"])
    for page_id, (role, _) in requests.items():
        if page_id in chosen:
            continue
        for variant in variants:
            if variant["role"] == role and variant.get("fallback") is True and variant["file"] not in used:
                chosen[page_id] = variant
                used.add(variant["file"])
                break
    return chosen


def apply_backgrounds(
    bindings: list[dict[str, Any]],
    requests: dict[str, tuple[str, str]],
    variants: list[dict[str, Any]],
) -> None:
    chosen = assign_backgrounds(requests, variants)
    for row in bindings:
        page_id = row["page_id"]
        if page_id not in requests:
            continue
        shell = row["shell_requirements"] or {}
        roles = dict(shell.get("role_assets") or {})
        previous = roles.pop("background", [])
        assets = [asset for asset in row["shell_assets"] if asset not in previous]
        variant = chosen.get(page_id)
        if variant:
            file = variant["file"]
            assets.append(file)
            roles["background"] = [file]
            row["background_variant"] = {
                key: variant[key] for key in ("file", "role", "subject", "text_area")
            }
            if row["render_mode"] != "brand_shell":
                row.update(source_scope="local", status="matched", confidence="medium")
        else:
            row["fallback_reason"] = "no unused compatible deck background; use native shapes"
        mode = "brand_shell" if assets else "themed_rebuild"
        row.update(
            render_mode=mode,
            reuse_mode=mode,
            shell_assets=assets,
            shell_requirements={
                "required_roles": list(roles),
                "role_assets": roles,
                "forbid_unlocked_full_bleed": True,
            } if assets else None,
        )
