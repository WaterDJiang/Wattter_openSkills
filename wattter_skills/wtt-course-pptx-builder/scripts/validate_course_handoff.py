#!/usr/bin/env python3
"""Validate a Course Handoff v1 bundle using only the Python standard library."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from validate_teaching_contract import validate_teaching
from visual_contract import inserted_source_page, validate_visual

PROTOCOL = "wtt.course-handoff"
DESIGN_PROTOCOL = "wtt.course-design-intent"
DESIGN_VERSIONS = {1, 1.1, 1.2}
PAGE_TYPES = {
    "cover", "toc", "section_opener", "content", "case", "exercise", "interaction", "summary", "closer",
}
INS_KINDS = {"hero", "interaction", "case", "exercise"}
ACTIVITY_PAGE_TYPES = {"interaction", "exercise"}
RELATIONSHIPS = {
    "none", "parallel", "sequence", "orthogonal", "hierarchy", "cycle",
    "comparison", "temporal", "composition", "correlation", "distribution", "causal",
}
CTA_RE = re.compile(r"扫码|二维码|进群|加微信|关注公众号|领取福利|点击链接|一键三连|长按识别")
TIMEBOX_RE = re.compile(
    r"(?:\d+(?:\.\d+)?\s*(?:秒|分钟|分)|\b\d+(?:\.\d+)?\s*(?:s|sec(?:onds)?|min(?:utes)?)\b)",
    re.IGNORECASE,
)
PRIVATE_TEMPLATE_KEYS = {
    "template_id", "template_path", "layout_id", "layout_path",
    "deck_id", "deck_path", "chart_id", "chart_path",
    "svg", "svg_path", "page_catalog_ref",
}
PRIVATE_TEMPLATE_VALUE_RE = re.compile(
    r"(?:^|/)templates/(?:decks|layouts|charts)/|\.svg(?:$|[?#])",
    re.IGNORECASE,
)


def canonical_outline_hash(outline: dict[str, Any]) -> str:
    payload = copy.deepcopy(outline)
    payload.pop("hash", None)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.name}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name}: invalid JSON at line {exc.lineno}: {exc.msg}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name}: root must be an object")
        return {}
    return value


def _read_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        errors.append(f"missing file: {path.name}")
        return []
    rows: list[dict[str, Any]] = []
    for number, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(row, dict):
            errors.append(f"{path.name}:{number}: row must be an object")
            continue
        rows.append(row)
    return rows


def _choice(value: Any, allowed: set[str], label: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{label}: expected one of {sorted(allowed)}, got {value!r}")


def _has_positive_timebox(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    for match in TIMEBOX_RE.finditer(value):
        if match.start() and value[match.start() - 1] == "-":
            continue
        number = float(re.search(r"\d+(?:\.\d+)?", match.group()).group())
        if math.isfinite(number) and number > 0:
            return True
    return False


def _check_activity_timing(
    content: dict[str, Any], teaching: Any,
    content_label: str, teaching_label: str, errors: list[str],
) -> None:
    duration = teaching.get("duration_seconds") if isinstance(teaching, dict) else None
    has_duration = isinstance(teaching, dict) and "duration_seconds" in teaching
    valid_duration = (
        not isinstance(duration, bool) and isinstance(duration, (int, float))
        and duration > 0 and (isinstance(duration, int) or math.isfinite(duration))
    )
    if has_duration and not valid_duration:
        errors.append(f"{teaching_label}.duration_seconds: positive finite number required for activity pages")
    visible = content.get("timebox")
    if visible is not None and not _has_positive_timebox(visible):
        errors.append(f"{content_label}.timebox: concrete number and unit with a positive value required when displayed")
    elif visible is None and not valid_duration and not _has_positive_timebox(
        json.dumps(content, ensure_ascii=False)
    ):
        errors.append(
            f"{content_label}.timebox: activity pages require a positive internal "
            f"{teaching_label}.duration_seconds or a concrete visible timebox"
        )


def _check_template_independence(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_label = f"{label}.{key}"
            if key in PRIVATE_TEMPLATE_KEYS:
                errors.append(f"{child_label}: private template field is forbidden")
            _check_template_independence(child, child_label, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_template_independence(child, f"{label}[{index}]", errors)
    elif isinstance(value, str) and PRIVATE_TEMPLATE_VALUE_RE.search(value):
        errors.append(f"{label}: private template/SVG reference is forbidden")


def validate_bundle(bundle: Path | str, require_design: bool = False) -> dict[str, Any]:
    root = Path(bundle)
    errors: list[str] = []
    warnings: list[str] = []
    if not root.is_dir():
        return {"ok": False, "errors": [f"bundle is not a directory: {root}"], "warnings": []}

    contract = _read_json(root / "course_contract.json", errors)
    if contract.get("protocol") != PROTOCOL:
        errors.append(f"course_contract.json: protocol must be {PROTOCOL!r}")
    if contract.get("version") != 1:
        errors.append("course_contract.json: version must be 1")

    producer = contract.get("producer")
    if not isinstance(producer, dict) or not producer.get("skill") or not producer.get("version"):
        errors.append("course_contract.json: producer.skill and producer.version are required")

    course = contract.get("course")
    if not isinstance(course, dict):
        errors.append("course_contract.json: course must be an object")
        course = {}
    for field in ("id", "title", "audience"):
        if not isinstance(course.get(field), str) or not course.get(field, "").strip():
            errors.append(f"course.{field}: non-empty string required")
    duration = course.get("duration_minutes")
    if type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0:
        errors.append("course.duration_minutes: positive number required")
    if not isinstance(course.get("learning_objectives"), list):
        errors.append("course.learning_objectives: array required")

    outline = contract.get("outline")
    if not isinstance(outline, dict):
        errors.append("course_contract.json: outline must be an object")
        outline = {}
    expected_hash = canonical_outline_hash(outline)
    if outline.get("hash") != expected_hash:
        errors.append(f"outline.hash mismatch: expected {expected_hash}")
    if not isinstance(outline.get("locked"), bool):
        errors.append("outline.locked: boolean required")
    sections = outline.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("outline.sections: non-empty array required")
        sections = []

    section_ids: list[str] = []
    outlined_page_ids: list[str] = []
    for index, section in enumerate(sections, 1):
        if not isinstance(section, dict):
            errors.append(f"outline.sections[{index}]: object required")
            continue
        section_id = section.get("section_id")
        if not isinstance(section_id, str) or not section_id:
            errors.append(f"outline.sections[{index}].section_id: non-empty string required")
        else:
            section_ids.append(section_id)
        if section.get("order") != index:
            errors.append(f"outline.sections[{index}].order: expected {index}")
        if not isinstance(section.get("title"), str) or not section.get("title"):
            errors.append(f"outline.sections[{index}].title: non-empty string required")
        page_ids = section.get("page_ids")
        if not isinstance(page_ids, list) or not all(isinstance(item, str) and item for item in page_ids):
            errors.append(f"outline.sections[{index}].page_ids: string array required")
        else:
            outlined_page_ids.extend(page_ids)
    if len(section_ids) != len(set(section_ids)):
        errors.append("outline.sections: duplicate section_id")

    pages_file = contract.get("pages_file", "pages.jsonl")
    if not isinstance(pages_file, str) or Path(pages_file).name != pages_file:
        errors.append("pages_file: must be a local filename")
        pages_file = "pages.jsonl"
    pages = _read_jsonl(root / pages_file, errors)
    if contract.get("page_count") != len(pages):
        errors.append(f"page_count mismatch: contract={contract.get('page_count')!r}, rows={len(pages)}")

    page_ids: list[str] = []
    policies = contract.get("policies") if isinstance(contract.get("policies"), dict) else {}
    for field in ("allow_reorder", "allow_page_count_change", "allow_scope_expansion", "allow_operational_cta"):
        if field not in policies or not isinstance(policies.get(field), bool):
            errors.append(f"policies.{field}: boolean required")
    for index, page in enumerate(pages, 1):
        prefix = f"{pages_file}:{index}"
        page_id = page.get("page_id")
        if not isinstance(page_id, str) or not page_id:
            errors.append(f"{prefix}.page_id: non-empty string required")
        else:
            page_ids.append(page_id)
        if page.get("sequence") != index:
            errors.append(f"{prefix}.sequence: expected {index}")
        if page.get("section_id") not in section_ids:
            errors.append(f"{prefix}.section_id: unknown section {page.get('section_id')!r}")
        _choice(page.get("page_type"), PAGE_TYPES, f"{prefix}.page_type", errors)
        if not isinstance(page.get("outline_title"), str) or not page.get("outline_title"):
            errors.append(f"{prefix}.outline_title: non-empty string required")
        if page.get("display_title") is not None and not isinstance(page.get("display_title"), str):
            errors.append(f"{prefix}.display_title: string or null required")
        for field in ("must_include", "evidence_refs"):
            if not isinstance(page.get(field), list):
                errors.append(f"{prefix}.{field}: array required")
        if not isinstance(page.get("slide_text"), dict):
            errors.append(f"{prefix}.slide_text: object required")
        elif page.get("page_type") in ACTIVITY_PAGE_TYPES:
            _check_activity_timing(
                page["slide_text"], page.get("teaching"),
                f"{prefix}.slide_text", f"{prefix}.teaching", errors,
            )
        if page.get("speaker_notes_ref") is not None and not isinstance(page.get("speaker_notes_ref"), str):
            errors.append(f"{prefix}.speaker_notes_ref: string or null required")
        if not policies.get("allow_operational_cta", False):
            visible = json.dumps(page.get("slide_text", {}), ensure_ascii=False)
            if CTA_RE.search(visible):
                warnings.append(
                    f"{prefix}.slide_text: possible CTA requires semantic review; retain necessary "
                    "teaching operations/material access, remove unauthorized marketing conversion"
                )
    if len(page_ids) != len(set(page_ids)):
        errors.append(f"{pages_file}: duplicate page_id")
    if page_ids != outlined_page_ids:
        errors.append("outline.sections[].page_ids must exactly match pages.jsonl order")

    design_path = root / "design_profile.json"
    design_present = design_path.exists()
    intents: list[dict[str, Any]] = []
    if require_design and not design_present:
        errors.append("missing file: design_profile.json")
    if design_present:
        design = _read_json(design_path, errors)
        if design.get("protocol") != DESIGN_PROTOCOL:
            errors.append(f"design_profile.json: protocol must be {DESIGN_PROTOCOL!r}")
        if design.get("version") not in DESIGN_VERSIONS:
            errors.append("design_profile.json: version must be 1, 1.1 or 1.2")
        if design.get("source_outline_hash") != outline.get("hash"):
            errors.append("design_profile.source_outline_hash must match outline.hash")
        _choice(design.get("render_mode"), {"svg", "image", "hybrid"}, "design_profile.render_mode", errors)
        _choice(design.get("asset_image_policy"), {"off", "selective", "aggressive"}, "design_profile.asset_image_policy", errors)
        if not isinstance(design.get("emit_image_prompt_pack"), bool):
            errors.append("design_profile.emit_image_prompt_pack: boolean required")
        if design.get("render_mode") == "svg" and design.get("emit_image_prompt_pack") is not False:
            errors.append("design_profile: svg mode requires emit_image_prompt_pack=false")
        if not isinstance(design.get("style_intent"), dict):
            errors.append("design_profile.style_intent: object required")
        _check_template_independence(design, "design_profile", errors)
        intents_file = design.get("page_intents_file", "page_intents.jsonl")
        if not isinstance(intents_file, str) or Path(intents_file).name != intents_file:
            errors.append("page_intents_file: must be a local filename")
            intents_file = "page_intents.jsonl"
        intents = _read_jsonl(root / intents_file, errors)
        if design.get("version") in {1, 1.1}:
            warnings.append("legacy design v1/v1.1: visual scope/count/content synchronization not verified; migrate to v1.2 before design updates")
        pages_by_id = {page.get("page_id"): page for page in pages}
        intent_ids: list[str] = []
        material_hashes: dict[Path, str | None] = {}
        for index, intent in enumerate(intents, 1):
            prefix = f"{intents_file}:{index}[{intent.get('page_id', 'unknown')}]"
            intent_ids.append(intent.get("page_id"))
            origin = intent.get("origin", "baseline")
            _choice(origin, {"baseline", "inserted"}, f"{prefix}.origin", errors)
            if origin == "inserted":
                _choice(intent.get("ins_kind"), INS_KINDS, f"{prefix}.ins_kind", errors)
                baseline_ref = intent.get("baseline_ref")
                if not isinstance(baseline_ref, str) or not baseline_ref:
                    errors.append(f"{prefix}.baseline_ref: non-empty string required for inserted pages")
                ins_content = intent.get("ins_content")
                if not isinstance(ins_content, dict):
                    errors.append(f"{prefix}.ins_content: object required for inserted pages")
                elif not isinstance(ins_content.get("title"), str) or not ins_content.get("title", "").strip():
                    errors.append(f"{prefix}.ins_content.title: non-empty string required for inserted pages")
                elif intent.get("ins_kind") in ACTIVITY_PAGE_TYPES:
                    _check_activity_timing(
                        ins_content, intent.get("teaching"),
                        f"{prefix}.ins_content", f"{prefix}.teaching", errors,
                    )
            _choice(intent.get("relationship"), RELATIONSHIPS, f"{prefix}.relationship", errors)
            if intent.get("item_count") is not None and (
                not isinstance(intent.get("item_count"), int) or intent.get("item_count") < 0
            ):
                errors.append(f"{prefix}.item_count: non-negative integer or null required")
            if not isinstance(intent.get("has_data"), bool):
                errors.append(f"{prefix}.has_data: boolean required")
            _choice(intent.get("density"), {"low", "medium", "high"}, f"{prefix}.density", errors)
            _choice(intent.get("image_need"), {"none", "optional", "required"}, f"{prefix}.image_need", errors)
            _choice(
                intent.get("editable_requirement"),
                {"required", "preferred", "not_required"},
                f"{prefix}.editable_requirement",
                errors,
            )
            _choice(intent.get("visual_priority"), {"low", "medium", "high"}, f"{prefix}.visual_priority", errors)
            _choice(
                intent.get("binding_preference"),
                {"auto", "template", "chart", "hybrid", "free"},
                f"{prefix}.binding_preference",
                errors,
            )
            if intent.get("content_form_hint") is not None and not isinstance(
                intent.get("content_form_hint"), str
            ):
                errors.append(f"{prefix}.content_form_hint: string or null required")
            if intent.get("content_form_confidence") is not None:
                _choice(
                    intent.get("content_form_confidence"),
                    {"low", "medium", "high"},
                    f"{prefix}.content_form_confidence",
                    errors,
                )
            alternatives = intent.get("content_form_alternatives")
            if alternatives is not None and (
                not isinstance(alternatives, list)
                or len(alternatives) > 3
                or not all(isinstance(item, str) and item for item in alternatives)
            ):
                errors.append(
                    f"{prefix}.content_form_alternatives: up to 3 non-empty strings required"
                )
            if intent.get("story_role") is not None and (
                not isinstance(intent.get("story_role"), str)
                or not intent.get("story_role").strip()
            ):
                errors.append(f"{prefix}.story_role: non-empty string required")
            composition = intent.get("composition")
            if composition is not None:
                if not isinstance(composition, dict):
                    errors.append(f"{prefix}.composition: object required")
                else:
                    for field in ("topology", "emphasis"):
                        if field in composition and (
                            not isinstance(composition[field], str)
                            or not composition[field].strip()
                        ):
                            errors.append(
                                f"{prefix}.composition.{field}: non-empty string required"
                            )
                    reading_order = composition.get("reading_order")
                    if reading_order is not None and (
                        not isinstance(reading_order, list)
                        or not all(isinstance(item, str) and item.strip() for item in reading_order)
                    ):
                        errors.append(
                            f"{prefix}.composition.reading_order: string array required"
                        )
            if intent.get("data_shape") is not None and not isinstance(
                intent.get("data_shape"), dict
            ):
                errors.append(f"{prefix}.data_shape: object required")
            if design.get("version") == 1.1:
                description = intent.get("visual_description")
                has_composition = isinstance(composition, dict) and (
                    any(
                        isinstance(composition.get(field), str) and composition[field].strip()
                        for field in ("topology", "emphasis")
                    )
                    or (
                        isinstance(composition.get("reading_order"), list)
                        and bool(composition["reading_order"])
                        and all(
                            isinstance(item, str) and item.strip()
                            for item in composition["reading_order"]
                        )
                    )
                )
                if not (
                    isinstance(description, str) and description.strip()
                ) and not has_composition:
                    errors.append(
                        f"{prefix}: v1.1 requires non-empty visual_description or composition"
                    )
            if design.get("version") == 1.2:
                if origin == "inserted":
                    page = inserted_source_page(intent)
                else:
                    page = pages_by_id.get(intent.get("page_id"), {})
                errors.extend(validate_visual(intent, page, pages, root, material_hashes))
            _check_template_independence(intent, prefix, errors)
        baseline_intent_ids = [
            intent.get("page_id")
            for intent in intents
            if intent.get("origin", "baseline") == "baseline"
        ]
        inserted = [
            intent for intent in intents if intent.get("origin", "baseline") == "inserted"
        ]
        if baseline_intent_ids != page_ids:
            errors.append(
                "page_intents baseline page_id order must exactly match pages.jsonl "
                "(inserted pages excluded)"
            )
        if len(intent_ids) != len(set(intent_ids)):
            errors.append(f"{intents_file}: duplicate page_id")
        if inserted:
            if not policies.get("allow_page_count_change", False):
                errors.append(
                    f"page_intents contains {len(inserted)} inserted page(s) "
                    "but policies.allow_page_count_change is false"
                )
            page_id_set = set(page_ids)
            seen_baseline: set[str] = set()
            for intent in intents:
                if intent.get("origin", "baseline") == "baseline":
                    seen_baseline.add(intent.get("page_id"))
                    continue
                pid = intent.get("page_id") or ""
                ref = intent.get("baseline_ref")
                if ref not in page_id_set:
                    errors.append(
                        f"page_intents {pid}: baseline_ref {ref!r} not found in pages.jsonl"
                    )
                elif ref not in seen_baseline:
                    errors.append(
                        f"page_intents {pid}: inserted before its baseline_ref {ref!r}"
                    )
                expected_prefix = f"{ref}-ins"
                suffix = pid[len(expected_prefix):] if pid.startswith(expected_prefix) else None
                if suffix is None or not suffix.isdigit() or not suffix:
                    errors.append(
                        f"page_intents {pid}: inserted page_id must be '{{baseline_ref}}-insN' format"
                    )
            if page_ids and len(inserted) > len(page_ids) / 3:
                warnings.append(
                    f"inserted pages ({len(inserted)}) exceed 1/3 of baseline ({len(page_ids)}): "
                    "breathing pages should serve content, not dominate"
                )
    elif not require_design:
        warnings.append("design_profile.json not present; content-only handoff is valid")

    teaching_result = validate_teaching(root, contract, pages)
    errors.extend(teaching_result["errors"])
    warnings.extend(teaching_result["warnings"])

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "page_count": len(pages),
        "design_intent_count": len(intents),
        "outline_hash": outline.get("hash"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Course Handoff v1 directory.")
    parser.add_argument("bundle", type=Path, help="Directory containing course_contract.json")
    parser.add_argument("--require-design", action="store_true", help="Require design_profile and page intents")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable JSON")
    args = parser.parse_args()
    result = validate_bundle(args.bundle, args.require_design)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"{status}: {args.bundle} ({result.get('page_count', 0)} pages)")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
