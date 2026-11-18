#!/usr/bin/env python3
"""Bind Course Handoff design intents to one local template package and chart library.

The result is an auditable proposal. It never writes spec_lock.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from course_backgrounds import apply_backgrounds, background_role, load_background_catalog
from template_capabilities import (
    CAPABILITY_FILE,
    analyze_template,
)
from course_pages import playback_pages
from validate_course_handoff import validate_bundle
from variant_selection import (
    DEFAULT_VARIANT_POLICY,
    infer_variant_profile,
    local_variant_precision,
    requested_variant_profile,
    select_controlled_variant,
)

SKILL_DIR = Path(__file__).resolve().parent.parent
CONTENT_FORMS_PATH = SKILL_DIR / "templates" / "charts" / "content_forms.json"
CHARTS_INDEX_PATH = SKILL_DIR / "templates" / "charts" / "charts_index.json"
PAGE_TYPE_MAP = {
    "cover": "cover",
    "toc": "toc",
    "section_opener": "chapter",
    "content": "content",
    "hero": "content",
    "case": "content",
    "exercise": "content",
    "interaction": "content",
    "summary": "content",
    "closer": "ending",
}
LEGACY_PAGE_FILES = {
    "cover": ("01_cover.svg", "001_cover.svg"),
    "toc": ("02_toc.svg", "002_toc.svg"),
    "chapter": ("02_chapter.svg", "002_chapter.svg", "03_chapter.svg", "003_chapter.svg"),
    "content": ("03_content.svg", "003_content.svg", "04_content.svg", "004_content.svg"),
    "ending": ("04_ending.svg", "004_ending.svg", "05_ending.svg", "005_ending.svg"),
}
RELATIONSHIP_MAP = {
    "comparison": "parallel",
    "temporal": "sequence",
    "composition": "hierarchy",
    "correlation": "special",
    "distribution": "special",
    "none": "special",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def visible_leaves(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [str(value)]
    if isinstance(value, list):
        return [leaf for item in value for leaf in visible_leaves(item)]
    if isinstance(value, dict):
        return [leaf for item in value.values() for leaf in visible_leaves(item)]
    return []


def content_shape(page: dict[str, Any]) -> dict[str, int]:
    leaves = visible_leaves(page.get("slide_text") or {})
    return {
        "visible_leaf_count": len(leaves),
        "total_chars": sum(len(value) for value in leaves),
        "max_chars": max((len(value) for value in leaves), default=0),
    }


def load_template_capabilities(template_dir: Path) -> dict[str, Any]:
    path = template_dir / CAPABILITY_FILE
    if path.is_file():
        return load_json(path)
    return analyze_template(template_dir)


def shell_requirements(
    template_capabilities: dict[str, Any],
    page_capability: dict[str, Any] | None,
) -> dict[str, Any]:
    """Resolve role-aware shell requirements for one brand_shell page."""
    if page_capability is None:
        role_catalog = template_capabilities.get("asset_roles") or {}
        page_refs = set(template_capabilities.get("shared_assets") or []) - set(
            template_capabilities.get("default_background_assets") or []
        )
    else:
        role_catalog = page_capability.get("shared_asset_roles") or {}
        page_refs = set(page_capability.get("shared_asset_refs") or [])
    contract = template_capabilities.get("shell_contract") or {}
    page_full_bleed = set(
        (page_capability or {}).get("full_bleed_image_refs") or []
    )
    role_assets: dict[str, list[str]] = {}
    for role in contract.get("required_roles", []):
        if not isinstance(role, str):
            continue
        local_assets = [
            asset for asset in (role_catalog.get(role) or [])
            if isinstance(asset, str) and asset in page_refs
        ]
        if role == "background":
            local_full_bleed = [
                asset for asset in local_assets if asset in page_full_bleed
            ]
            candidates = local_full_bleed or local_assets
        else:
            candidates = local_assets
        if candidates:
            role_assets[role] = sorted(set(candidates))
    return {
        "required_roles": list(role_assets),
        "role_assets": role_assets,
        "forbid_unlocked_full_bleed": bool(
            contract.get("forbid_unlocked_full_bleed")
        ),
    }


def mirror_eligibility(
    page: dict[str, Any],
    intent: dict[str, Any],
    layout: dict[str, Any] | None,
    capability: dict[str, Any] | None,
) -> tuple[bool, list[str]]:
    if layout is None:
        return False, ["no exact canonical page selected"]
    declared_mode = layout.get("render_mode")
    if declared_mode in {"brand_shell", "themed_rebuild"}:
        return False, [f"template page declares render_mode={declared_mode}"]
    if not capability:
        return False, ["template capability metadata unavailable"]
    if not capability.get("safe_for_mirror"):
        return False, ["template page is not safe_for_mirror"]
    native_editability = capability.get("native_editability") or {}
    if native_editability and not native_editability.get("native_shape_ready"):
        return False, ["template page has no native editable content objects"]
    if capability.get("content_raster_refs"):
        return False, [
            "template page locks core content in raster assets: "
            + ", ".join(str(item) for item in capability["content_raster_refs"])
        ]
    wanted_count = intent.get("item_count")
    actual_count = (layout.get("selection") or {}).get("item_count")
    if wanted_count is not None:
        if actual_count is None:
            return False, ["mirror page has no declared item_count"]
        if wanted_count != actual_count:
            return False, [
                f"mirror item_count mismatch: wanted={wanted_count}, actual={actual_count}"
            ]

    shape = content_shape(page)
    text_runs = max(
        int(capability.get("text_runs") or 0),
        int(capability.get("text_elements") or 0),
    )
    source_chars = int(capability.get("source_text_chars") or 0)
    max_source_chars = int(capability.get("max_text_chars") or 0)
    leaf_capacity = max(1, text_runs)
    total_capacity = max(source_chars * 2, leaf_capacity * 18)
    line_capacity = max(max_source_chars * 2, 32)
    reasons = [
        f"content leaves={shape['visible_leaf_count']}/{leaf_capacity}",
        f"content chars={shape['total_chars']}/{total_capacity}",
        f"max text={shape['max_chars']}/{line_capacity}",
    ]
    if shape["visible_leaf_count"] > leaf_capacity:
        return False, reasons + ["visible leaf count exceeds mirror text-run capacity"]
    if shape["total_chars"] > total_capacity:
        return False, reasons + ["visible text exceeds mirror total capacity"]
    if shape["max_chars"] > line_capacity:
        return False, reasons + ["visible text exceeds mirror line capacity"]
    return True, reasons + ["mirror content capacity accepted"]


def build_legacy_catalog(template_dir: Path, package: str) -> dict[str, Any] | None:
    """Adapt standard pre-catalog layout packages without changing the package.

    This intentionally recognizes only the historical five-file convention.
    Arbitrary filenames still require an explicit page_catalog.json so the
    binder never invents semantic references.
    """
    pages: list[dict[str, Any]] = []
    for page_type, candidates in LEGACY_PAGE_FILES.items():
        file_name = next(
            (candidate for candidate in candidates if (template_dir / candidate).is_file()),
            None,
        )
        if not file_name:
            continue
        pages.append(
            {
                "reference": Path(file_name).stem,
                "file": file_name,
                "page_type": page_type,
                "selection": {
                    "content_density": "medium" if page_type in {"toc", "content"} else "low",
                    "image_requirements": [],
                    "legacy_generic": page_type == "content",
                },
            }
        )
    required = {"cover", "chapter", "content", "ending"}
    if not required.issubset({page["page_type"] for page in pages}):
        return None
    return {
        "schema_version": 1,
        "selection_contract_version": 2,
        "template_id": package,
        "reference_format": "legacy-standard-basename",
        "selection_policy": {"fallback": "no-template-match"},
        "pages": pages,
        "generated_adapter": True,
    }


def resolve_template_dir(args: argparse.Namespace) -> tuple[Path, str, str, str]:
    if args.template_dir:
        template_dir = args.template_dir.resolve()
        package = template_dir.name
        parent_kind = template_dir.parent.name
        if parent_kind in {"decks", "layouts"}:
            kind = parent_kind
            reference_prefix = f"templates/{kind}/{package}"
        else:
            kind = "project"
            reference_prefix = template_dir.name
    else:
        kind = args.template_kind
        package = args.template_package
        template_dir = SKILL_DIR / "templates" / kind / package
        reference_prefix = f"templates/{kind}/{package}"
    if not template_dir.is_dir():
        raise ValueError(f"template package not found: {template_dir}")
    return template_dir, kind, package, reference_prefix


def template_replication_mode(template_dir: Path) -> str | None:
    design_spec = template_dir / "design_spec.md"
    if not design_spec.is_file():
        return None
    head = design_spec.read_text(encoding="utf-8")[:4000]
    match = re.search(r"(?m)^replication_mode:\s*([a-z_-]+)\s*$", head)
    return match.group(1) if match else None


def semantic_text(page: dict[str, Any], intent: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("outline_title", "display_title"):
        value = page.get(key)
        if isinstance(value, str):
            values.append(value)
    for key in ("must_include", "slide_text"):
        value = page.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        elif isinstance(value, str):
            values.append(value)
        elif isinstance(value, dict):
            values.extend(visible_leaves(value))
    for key in ("visual_description", "content_form_hint", "story_role"):
        value = intent.get(key)
        if isinstance(value, str):
            values.append(value)
    alternatives = intent.get("content_form_alternatives")
    if isinstance(alternatives, list):
        values.extend(str(item) for item in alternatives if isinstance(item, str))
    composition = intent.get("composition")
    if isinstance(composition, dict):
        values.extend(visible_leaves(composition))
    return " ".join(values).lower()


def semantic_gate(
    selection: dict[str, Any],
    page_text: str,
) -> tuple[bool, list[str]]:
    required = selection.get("semantic_require_any") or []
    excluded = selection.get("semantic_exclude_any") or []
    compact_page_text = re.sub(r"\s+", "", page_text)

    def matches(term: Any) -> bool:
        needle = str(term).lower()
        return needle in page_text or re.sub(r"\s+", "", needle) in compact_page_text

    if required and not any(matches(term) for term in required):
        return False, [f"missing semantic_require_any={required}"]
    hits = [str(term) for term in excluded if matches(term)]
    if hits:
        return False, [f"matched semantic_exclude_any={hits}"]
    reasons = ["semantic_require_any matched"] if required else []
    return True, reasons


def choose_form(
    intent: dict[str, Any], forms: dict[str, Any]
) -> tuple[str | None, str, list[str]]:
    # Rubric scores are source row values, not a quantitative correlation plot.
    contract = intent.get("visual_contract")
    kind = (contract or {}).get("relation", {}).get("kind") if isinstance(contract, dict) else None
    if kind == "rubric":
        if "table" in forms:
            return "table", "high", ["visual_contract rubric preserves dimension/score/standard rows"]
        return None, "low", ["no table form for source-backed rubric; do not infer a correlation chart"]
    reasons: list[str] = []
    hint = intent.get("content_form_hint")
    if kind == "practice":
        # Task material, instructions and deliverables do not imply hierarchy.
        # A supplied sequence hint can still bind a dedicated exercise layout.
        if (intent.get("relationship") == "sequence" and hint in forms
                and forms[hint].get("relationship") == "sequence"
                and forms[hint].get("has_data") == intent.get("has_data")):
            return hint, "high", ["practice with explicit sequence"]
        return None, "high", ["practice: match local teaching purpose; no inferred chart"]
    if hint in forms:
        definition = forms[hint]
        if definition.get("has_data") == intent.get("has_data"):
            stated = intent.get("content_form_confidence")
            confidence = stated if stated in {"low", "medium", "high"} else "high"
            return hint, confidence, ["accepted valid content_form_hint"]
        reasons.append(f"ignored hint {hint}: has_data mismatch")
    alternatives = intent.get("content_form_alternatives")
    if isinstance(alternatives, list):
        for alternative in alternatives[:3]:
            if alternative in forms:
                definition = forms[alternative]
                if definition.get("has_data") == intent.get("has_data"):
                    return alternative, "medium", [
                        "accepted content_form_alternative"
                    ]

    relationship = RELATIONSHIP_MAP.get(intent.get("relationship"), intent.get("relationship"))
    composition = intent.get("composition")
    if relationship in {None, "special"} and isinstance(composition, dict):
        relationship = {
            "sequence": "sequence",
            "radial": "hierarchy",
            "layered": "hierarchy",
            "split": "parallel",
            "grid": "parallel",
        }.get(composition.get("topology"), relationship)
    count = intent.get("item_count")
    ranked: list[tuple[int, str]] = []
    for form, definition in forms.items():
        score = 0
        if definition.get("relationship") == relationship:
            score += 30
        else:
            continue
        if definition.get("has_data") == intent.get("has_data"):
            score += 25
        else:
            continue
        if count is not None:
            if definition.get("count") == count:
                score += 35
            elif isinstance(definition.get("count_range"), list):
                low, high = definition["count_range"]
                if low <= count <= high:
                    score += 25
            elif definition.get("count") is None:
                score += 8
        ranked.append((score, form))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    if not ranked:
        return None, "low", reasons + ["no local content form match"]
    score, form = ranked[0]
    confidence = "high" if score >= 80 else "medium" if score >= 55 else "low"
    return form, confidence, reasons + [f"inferred from relationship={relationship}, count={count}"]


def variant_files_for_form(
    content_forms: dict[str, Any], form: str | None, package: str, page_type: str
) -> set[str]:
    if not form:
        return set()
    result: set[str] = set()
    for tag in content_forms.get("page_variant_tags", {}).values():
        if tag.get("package") != package or tag.get("page_type") != page_type:
            continue
        if form in tag.get("content_forms", []):
            file_name = tag.get("file")
            if isinstance(file_name, str):
                result.add(file_name if file_name.endswith(".svg") else f"{file_name}.svg")
    return result


def choose_layout(
    catalog: dict[str, Any],
    builder_type: str,
    intent: dict[str, Any],
    variant_files: set[str],
    *,
    page_text: str,
    strict_slot_count: bool,
    page_id: str = "P000",
    variant_seed: str = "",
    variant_history: list[dict[str, str]] | None = None,
    rotation_enabled: bool = False,
    variant_policy: dict[str, Any] | None = None,
) -> tuple[
    dict[str, Any] | None,
    int,
    list[str],
    list[dict[str, Any]],
    dict[str, Any],
]:
    variant_candidates: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []
    for position, page in enumerate(catalog.get("pages", [])):
        if page.get("usage", "output") == "reference_only":
            continue
        if page.get("page_type") != builder_type:
            continue
        if builder_type == "content" and variant_files and page.get("file") not in variant_files:
            continue
        selection = page.get("selection") or {}
        if "strict_item_count" in selection and not isinstance(
            selection["strict_item_count"], bool
        ):
            audit.append(
                {
                    "reference": page.get("reference"),
                    "file": page.get("file"),
                    "status": "rejected",
                    "score": None,
                    "reasons": ["strict_item_count must be boolean"],
                }
            )
            continue
        strict_for_page = page.get("render_mode") == "mirror" or (
            page.get("render_mode") is None and strict_slot_count
        )
        strict_item_count = selection.get("strict_item_count") is True
        score = 20
        reasons = [f"page_type={builder_type}"]
        allowed, gate_reasons = semantic_gate(selection, page_text)
        if not allowed:
            audit.append(
                {
                    "reference": page.get("reference"),
                    "file": page.get("file"),
                    "status": "rejected",
                    "score": None,
                    "reasons": gate_reasons,
                }
            )
            continue
        reasons.extend(gate_reasons)
        if selection.get("semantic_require_any"):
            score += 45
            reasons.append("purpose-specific local page")
        if page.get("file") in variant_files:
            score += 70
            reasons.append("content form tagged page variant")
        wanted_count = intent.get("item_count")
        actual_count = selection.get("item_count")
        if strict_item_count and (wanted_count is None or actual_count is None):
            audit.append(
                {
                    "reference": page.get("reference"),
                    "file": page.get("file"),
                    "status": "rejected",
                    "score": None,
                    "reasons": [
                        "strict_item_count requires declared page and intent item_count"
                    ],
                }
            )
            continue
        if wanted_count is not None and actual_count is not None:
            if wanted_count == actual_count:
                score += 25
                reasons.append("item_count exact")
            elif strict_for_page or strict_item_count:
                audit.append(
                    {
                        "reference": page.get("reference"),
                        "file": page.get("file"),
                        "status": "rejected",
                        "score": None,
                        "reasons": [
                            f"mirror fixed slot count mismatch: wanted={wanted_count}, actual={actual_count}"
                        ],
                    }
                )
                continue
            else:
                score -= min(90, abs(wanted_count - actual_count) * 30)
        if selection.get("content_density") == intent.get("density"):
            score += 10
            reasons.append("density exact")
        image_requirements = selection.get("image_requirements") or []
        hard_image_requirements = [
            item
            for item in image_requirements
            if not any(marker in str(item) for marker in ("不要求", "无需", "可选"))
        ]
        if intent.get("image_need") == "none" and hard_image_requirements:
            if strict_for_page:
                audit.append(
                    {
                        "reference": page.get("reference"),
                        "file": page.get("file"),
                        "status": "rejected",
                        "score": None,
                        "reasons": [
                            "mirror page requires image assets but page intent image_need=none"
                        ],
                    }
                )
                continue
            score -= 8
        elif intent.get("image_need") == "required" and hard_image_requirements:
            score += 8
            reasons.append("image slot available")
        profile = infer_variant_profile(
            str(page.get("file") or page.get("reference") or ""),
            selection=selection,
        )
        variant_candidates.append(
            {
                "id": page.get("file"),
                "base_score": score,
                "profile": profile,
                "payload": page,
                "reasons": reasons,
                "position": position,
            }
        )
        audit.append(
            {
                "reference": page.get("reference"),
                "file": page.get("file"),
                "status": "candidate",
                "score": score,
                "variant_profile": profile,
                "reasons": reasons,
            }
        )
    if not variant_candidates:
        return (
            None,
            0,
            ["no semantically eligible page in package"],
            audit,
            {
                "enabled": rotation_enabled,
                "requested_profile": requested_variant_profile(intent),
                "selected_profile": None,
                "equivalent_pool": [],
                "reason": "no local layout candidates",
            },
        )
    selected, variant_audit = select_controlled_variant(
        variant_candidates,
        page_id=page_id,
        seed=variant_seed,
        requested_profile=requested_variant_profile(intent),
        history=variant_history,
        enabled=rotation_enabled,
        policy=variant_policy,
    )
    assert selected is not None
    page = selected["payload"]
    score = int(variant_audit.get("semantic_score") or selected["base_score"])
    reasons = list(selected["reasons"])
    reasons.append(str(variant_audit["reason"]))
    structural = builder_type != "content"
    selection = page.get("selection") or {}
    legacy_generic = bool(selection.get("legacy_generic"))
    generic_shell = bool(selection.get("generic_shell"))
    if not structural and score < 35 and not legacy_generic and not generic_shell:
        return (
            None,
            score,
            reasons + ["score below content-page threshold"],
            audit,
            variant_audit,
        )
    for item in audit:
        if item.get("reference") == page.get("reference"):
            item["status"] = "selected"
            item["semantic_score"] = variant_audit.get("semantic_score")
            item["rotation_adjustment"] = variant_audit.get(
                "rotation_adjustment"
            )
            item["deterministic_tiebreak"] = variant_audit.get(
                "deterministic_tiebreak"
            )
    return page, score, reasons, audit, variant_audit


def route_contract(
    *,
    template_kind: str | None,
    package: str | None,
    free_route: str | None,
) -> dict[str, Any]:
    if template_kind == "decks":
        assert package
        primary = f"decks/{package}"
        return {
            "kind": "deck",
            "primary_source": primary,
            "allowed_asset_scopes": [primary, "charts", "icons"],
            "forbidden_asset_scopes": [
                f"decks/* except {package}",
                "layouts",
                "html-background-styles",
            ],
        }
    primary = f"layouts/{package}" if template_kind == "layouts" and package else None
    return {
        "kind": "free",
        "strategy": free_route or ("layout-led" if primary else "full-free"),
        "primary_source": primary,
        "allowed_asset_scopes": [
            *([primary] if primary else []),
            "layouts",
            "html-background-styles",
            "charts",
            "icons",
        ],
        "forbidden_asset_scopes": ["decks"],
    }


def choose_chart(
    content_forms: dict[str, Any],
    charts_index: dict[str, Any],
    form: str | None,
    item_count: int | None,
    *,
    intent: dict[str, Any] | None = None,
    page_text: str = "",
    page_id: str = "P000",
    variant_seed: str = "",
    variant_history: list[dict[str, str]] | None = None,
    rotation_enabled: bool = False,
    variant_policy: dict[str, Any] | None = None,
) -> tuple[str | None, list[str], dict[str, Any]]:
    if not form:
        return (
            None,
            ["no resolved content form"],
            {
                "enabled": rotation_enabled,
                "requested_profile": requested_variant_profile(intent or {}),
                "selected_profile": None,
                "equivalent_pool": [],
                "reason": "no resolved content form",
            },
        )
    indexed = charts_index.get("charts", {})
    candidates: list[dict[str, Any]] = []
    rejected: list[str] = []
    compact_page_text = re.sub(r"\s+", "", page_text.lower())
    for chart_id, tag in content_forms.get("chart_tags", {}).items():
        if chart_id not in indexed or form not in tag.get("content_forms", []):
            continue
        dimensions = tag.get("dimensions") or {}
        min_items = dimensions.get("min_items")
        max_items = dimensions.get("max_items")
        if min_items is not None and (item_count is None or item_count < min_items):
            rejected.append(f"{chart_id}: below min_items={min_items}")
            continue
        if max_items is not None and (item_count is None or item_count > max_items):
            rejected.append(f"{chart_id}: above max_items={max_items}")
            continue
        if dimensions.get("requires_data") is True and (intent or {}).get("has_data") is not True:
            rejected.append(f"{chart_id}: requires_data=true")
            continue
        cues = dimensions.get("requires_cue_any") or []
        cue_matched = bool(cues) and any(
            re.sub(r"\s+", "", str(cue).lower()) in compact_page_text
            for cue in cues
        )
        if cues and not cue_matched:
            rejected.append(f"{chart_id}: missing requires_cue_any={cues}")
            continue
        slots = dimensions.get("slots")
        score = 10 + (20 if cue_matched else 0)
        if item_count is not None:
            if slots == item_count:
                score += 20
            elif slots is None:
                score += 8
        candidates.append(
            {
                "id": chart_id,
                "base_score": score,
                "profile": infer_variant_profile(chart_id, tag=tag),
                "payload": chart_id,
                "reasons": [
                    f"chart tagged for form={form}",
                    f"eligibility score={score}",
                    *(["required cue matched"] if cue_matched else []),
                ],
                "position": len(candidates),
            }
        )
    if not candidates:
        reason = (
            f"no eligible chart for form={form}"
            if rejected else f"no chart tagged for form={form}"
        )
        return (
            None,
            [reason, *rejected],
            {
                "enabled": rotation_enabled,
                "requested_profile": requested_variant_profile(intent or {}),
                "selected_profile": None,
                "equivalent_pool": [],
                "reason": reason,
            },
        )
    selected, variant_audit = select_controlled_variant(
        candidates,
        page_id=page_id,
        seed=variant_seed,
        requested_profile=requested_variant_profile(intent or {}),
        history=variant_history,
        enabled=rotation_enabled,
        policy=variant_policy,
    )
    assert selected is not None
    return (
        str(selected["payload"]),
        list(selected["reasons"]) + [str(variant_audit["reason"])],
        variant_audit,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bind Course Handoff v1 intents to a local template package and charts."
    )
    parser.add_argument("bundle", type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--template-package", help="Package name under templates/decks or layouts")
    source.add_argument("--template-dir", type=Path, help="Direct path to one template package")
    source.add_argument(
        "--free-route",
        choices=("full-free", "html-led"),
        help="No Deck/Layout package. Bind only global chart intent for a free route.",
    )
    parser.add_argument("--template-kind", choices=("decks", "layouts"), default="decks")
    parser.add_argument("--out", type=Path, help="Default: <bundle>/page_binding.json")
    parser.add_argument(
        "--variant-mode",
        choices=("controlled_rotation", "stable"),
        default="controlled_rotation",
        help="Rotate only among semantically equivalent SVGs; mirror pages stay stable.",
    )
    args = parser.parse_args()

    validation = validate_bundle(args.bundle, require_design=True)
    if not validation["ok"]:
        for error in validation["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.free_route:
        template_dir = None
        kind = "free"
        package = ""
        reference_prefix = ""
    else:
        try:
            template_dir, kind, package, reference_prefix = resolve_template_dir(args)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    contract = load_json(args.bundle / "course_contract.json")
    try:
        pages = playback_pages(args.bundle, contract)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    profile = load_json(args.bundle / "design_profile.json")
    intents = load_jsonl(args.bundle / profile.get("page_intents_file", "page_intents.jsonl"))
    catalog_path = template_dir / "page_catalog.json" if template_dir else None
    if catalog_path and catalog_path.exists():
        catalog = load_json(catalog_path)
    elif template_dir is None:
        catalog = {"pages": []}
    else:
        assert template_dir is not None
        catalog = build_legacy_catalog(template_dir, package)
        if catalog is None:
            print(
                f"ERROR: missing page_catalog.json and no complete legacy five-file layout "
                f"convention in {template_dir}",
                file=sys.stderr,
            )
            return 1
        print(
            f"NOTICE: using legacy five-file catalog adapter for {template_dir}",
            file=sys.stderr,
        )
    if args.template_dir and catalog.get("template_id"):
        package = catalog["template_id"]
    if args.template_dir and template_dir and template_dir.parent.name not in {
        "decks",
        "layouts",
    }:
        kind = "decks"
    replication_mode = (
        template_replication_mode(template_dir) if template_dir else None
    )
    template_capabilities = (
        load_template_capabilities(template_dir) if template_dir else {}
    )
    try:
        background_variants = load_background_catalog(template_dir) if template_dir else []
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    background_requests: dict[str, tuple[str, str]] = {}
    default_backgrounds = set(template_capabilities.get("default_background_assets") or [])
    shared_assets = [
        asset for asset in (template_capabilities.get("shared_assets") or [])
        if asset not in default_backgrounds
    ]
    template_shell_contract = template_capabilities.get("shell_contract") or {}
    content_forms = load_json(CONTENT_FORMS_PATH)
    charts_index = load_json(CHARTS_INDEX_PATH)
    forms = content_forms.get("forms", {})
    variant_policy = {
        **DEFAULT_VARIANT_POLICY,
        "mode": args.variant_mode,
    }
    variant_seed = (
        f"{contract['outline']['hash']}|{kind}|{package or args.free_route or 'free'}"
    )
    layout_variant_history: list[dict[str, str]] = []
    chart_variant_history: list[dict[str, str]] = []

    bindings: list[dict[str, Any]] = []
    for design_sequence, (intent, page) in enumerate(zip(intents, pages, strict=True), 1):
        # Only explicit relationship arrays are countable. A mixed
        # body_points array may contain actions, conditions and explanations.
        declared_count = intent.get('item_count')
        explicit_arrays = [value for key, value in page.get('slide_text', {}).items()
                           if key in {'items', 'steps', 'options', 'rows', 'pairs', 'lines'}
                           and isinstance(value, list)]
        if not intent.get("visual_contract") and isinstance(declared_count, int) and len(explicit_arrays) == 1:
            actual_count = len(explicit_arrays[0])
            if declared_count != actual_count:
                print(f"ERROR: {page['page_id']}: storyboard count {declared_count} "
                      f"differs from source items {actual_count}; do not delete items", file=sys.stderr)
                return 1
        preference = intent.get("binding_preference")
        role = (
            background_role(page)
            if background_variants and preference not in {"free", "chart"}
            else None
        )
        builder_type = "break" if role == "break" else PAGE_TYPE_MAP[page["page_type"]]
        rotation_enabled = (
            args.variant_mode == "controlled_rotation"
            and builder_type == "content"
            and replication_mode != "mirror"
        )
        if builder_type == "content":
            form, form_confidence, form_reasons = choose_form(intent, forms)
        else:
            form, form_confidence, form_reasons = None, "medium", ["structural page; form binding skipped"]
        page_text = semantic_text(page, intent)
        variant_files = variant_files_for_form(content_forms, form, package, builder_type)
        (
            layout,
            layout_score,
            layout_reasons,
            layout_candidates,
            layout_variant_selection,
        ) = choose_layout(
            catalog,
            builder_type,
            intent,
            variant_files,
            page_text=page_text,
            strict_slot_count=replication_mode == "mirror",
            page_id=page["page_id"],
            variant_seed=variant_seed,
            variant_history=layout_variant_history,
            rotation_enabled=rotation_enabled,
            variant_policy=variant_policy,
        )
        local_precise, local_fit_reasons = local_variant_precision(
            layout, intent, variant_files
        )
        layout_reasons.extend(local_fit_reasons)
        chart_id: str | None = None
        chart_reasons: list[str] = []
        chart_variant_selection: dict[str, Any] = {
            "enabled": rotation_enabled,
            "requested_profile": requested_variant_profile(intent),
            "selected_profile": None,
            "equivalent_pool": [],
            "reason": "global chart selection not needed",
        }
        if role != "break" and preference in {"auto", "chart", "hybrid"} and (
            intent.get("has_data")
            or preference in {"chart", "hybrid"}
            or layout is None
            or (form is not None and not local_precise)
        ):
            chart_id, chart_reasons, chart_variant_selection = choose_chart(
                content_forms,
                charts_index,
                form,
                intent.get("item_count"),
                intent=intent,
                page_text=page_text,
                page_id=page["page_id"],
                variant_seed=variant_seed,
                variant_history=chart_variant_history,
                rotation_enabled=rotation_enabled,
                variant_policy=variant_policy,
            )
        if preference == "chart":
            layout = None
            layout_reasons.append("binding_preference=chart")
        elif preference == "auto" and chart_id and form is not None and not local_precise:
            if layout and (layout.get("selection") or {}).get("generic_shell"):
                layout_reasons.append(
                    "kept local generic shell and added global chart structure"
                )
            else:
                if layout:
                    for candidate in layout_candidates:
                        if candidate.get("file") == layout.get("file"):
                            candidate["status"] = "superseded_by_chart"
                layout = None
                layout_reasons.append(
                    "package layout was not a precise content fit; used global chart"
                )
        if preference == "free":
            layout = None
            chart_id = None
            layout_reasons = ["binding_preference=free"]

        layout_reference = None
        capability: dict[str, Any] | None = None
        if layout:
            layout_reference = f"{reference_prefix}/{layout['file']}"
            if not (template_dir / layout["file"]).is_file():
                print(f"ERROR: catalog layout missing on disk: {layout_reference}", file=sys.stderr)
                return 1
            capability = (template_capabilities.get("pages") or {}).get(
                Path(layout["file"]).stem
            )
        page_shell_assets = (
            [
                asset for asset in (capability.get("shared_asset_refs") or [])
                if isinstance(asset, str)
            ]
            if capability is not None else shared_assets
        )
        chart_reference = f"templates/charts/{chart_id}.svg" if chart_id else None
        if chart_reference and not (SKILL_DIR / chart_reference).is_file():
            print(f"ERROR: indexed chart missing on disk: {chart_reference}", file=sys.stderr)
            return 1

        if builder_type == "content" and layout:
            selected_profile = layout_variant_selection.get("selected_profile") or {}
            layout_variant_history.append(
                {
                    "id": str(layout.get("file")),
                    "topology": str(selected_profile.get("topology", "standard")),
                }
            )
        if builder_type == "content" and chart_id:
            selected_profile = chart_variant_selection.get("selected_profile") or {}
            chart_variant_history.append(
                {
                    "id": chart_id,
                    "topology": str(selected_profile.get("topology", "standard")),
                }
            )

        eligible, eligibility_reasons = mirror_eligibility(
            page,
            intent,
            layout,
            capability,
        )
        selected_mode = layout.get("render_mode") if layout else None
        requested_mirror = selected_mode == "mirror" or (
            selected_mode is None and replication_mode == "mirror"
        )
        can_use_brand_shell = bool(page_shell_assets) and bool(
            template_shell_contract.get("required_roles")
            or template_capabilities.get("schema_version") == 1
        )
        fallback_reason: str | None = None
        if preference == "free":
            page_render_mode = "themed_rebuild"
        elif selected_mode == "themed_rebuild":
            page_render_mode = "themed_rebuild"
        elif requested_mirror and eligible:
            page_render_mode = "mirror"
        elif can_use_brand_shell:
            page_render_mode = "brand_shell"
            if requested_mirror:
                fallback_reason = "; ".join(eligibility_reasons)
        else:
            page_render_mode = "themed_rebuild"
            if requested_mirror or selected_mode == "brand_shell":
                fallback_reason = "; ".join(eligibility_reasons)
        if chart_reference and not local_precise and not fallback_reason:
            fallback_reason = (
                "selected template has no precise local page variant; "
                "used global chart structure"
                if template_dir
                else "free route used global chart structure"
            )

        if page_render_mode == "brand_shell" and requested_mirror:
            status = "fallback"
            confidence = "medium"
        elif page_render_mode == "brand_shell":
            status = "matched"
            confidence = "medium"
        elif layout_reference or chart_reference:
            status = "matched"
            confidence = "high" if form_confidence == "high" and layout_score >= 45 else "medium"
        else:
            status = "no-template-match"
            confidence = "low"
        if role and (page_render_mode == "brand_shell" or role == "break"):
            background_requests[page["page_id"]] = (role, page_text)
        used_variant_selection: dict[str, Any] = {}
        if layout:
            used_variant_selection["layout"] = layout_variant_selection
        if chart_id:
            used_variant_selection["chart"] = chart_variant_selection
        bindings.append(
            {
                "page_id": page["page_id"],
                "sequence": design_sequence,
                "page_type": page["page_type"],
                "origin": intent.get("origin", "baseline"),
                "ins_kind": intent.get("ins_kind") if intent.get("origin") == "inserted" else None,
                "resolved_form": form,
                "layout_reference": layout_reference,
                "chart_reference": chart_reference,
                "render_mode": page_render_mode,
                "mirror_eligible": eligible,
                "fallback_reason": fallback_reason,
                "content_shape": content_shape(page),
                "realization_status": "pending_executor_evidence",
                "template_capability": capability,
                "shell_assets": page_shell_assets if page_render_mode == "brand_shell" else [],
                "shell_requirements": (
                    shell_requirements(template_capabilities, capability)
                    if page_render_mode == "brand_shell"
                    else None
                ),
                "binding_preference": preference,
                "variant_selection": used_variant_selection,
                "source_scope": (
                    "local+global"
                    if layout_reference and chart_reference
                    else "local"
                    if layout_reference
                    else "global"
                    if chart_reference
                    else "free"
                ),
                "fallback_used": bool(
                    chart_reference and not local_precise
                ),
                "skin_source": (
                    f"decks/{package}"
                    if kind == "decks"
                    else f"layouts/{package}"
                    if kind == "layouts"
                    else None
                ),
                "reuse_mode": (
                    "structure_only"
                    if chart_reference
                    else page_render_mode
                ),
                "status": status,
                "confidence": confidence,
                "reasons": (
                    form_reasons
                    + layout_reasons
                    + chart_reasons
                    + eligibility_reasons
                ),
                "layout_candidates": layout_candidates,
            }
        )

    if background_requests:
        apply_backgrounds(bindings, background_requests, background_variants)

    result = {
        "protocol": "wtt.course-page-binding",
        "version": 2,
        "shell_contract_version": 2,
        "source_outline_hash": contract["outline"]["hash"],
        "template": {
            "kind": kind,
            "package": package or None,
            "replication_mode": replication_mode,
        },
        "route": route_contract(
            template_kind=kind if kind in {"decks", "layouts"} else None,
            package=package or None,
            free_route=args.free_route,
        ),
        "variant_policy": variant_policy,
        "render_mode": profile["render_mode"],
        "pages": bindings,
        "summary": {
            "total": len(bindings),
            "matched": sum(item["status"] == "matched" for item in bindings),
            "fallback": sum(item["status"] == "fallback" for item in bindings),
            "no_template_match": sum(item["status"] == "no-template-match" for item in bindings),
            "render_modes": {
                mode: sum(item["render_mode"] == mode for item in bindings)
                for mode in ("mirror", "brand_shell", "themed_rebuild")
            },
        },
        "notice": "Proposal only. Strategist must review before writing spec_lock.md.",
    }
    out = args.out or args.bundle / "page_binding.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: wrote {out} ({result['summary']['matched']}/{len(bindings)} matched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
