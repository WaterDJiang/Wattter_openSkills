#!/usr/bin/env python3
"""Check optional teaching provenance and local delivery resources, not pedagogy quality."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

MODES = {"explain", "demo", "practice", "feedback", "transition"}


def _strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value)


def _local_file(root: Path, ref: Any) -> Path | None:
    if not isinstance(ref, str) or not ref.strip() or "://" in ref:
        return None
    name = ref.split("#", 1)[0]
    if not name or Path(name).is_absolute():
        return None
    candidate = root / name
    if not candidate.resolve().is_relative_to(root.resolve()):
        return None
    return candidate if candidate.is_file() and candidate.stat().st_size > 0 else None


def validate_teaching(root: Path, contract: dict, pages: list[dict], *,
                      ready_for_class: bool = False) -> dict:
    """Return errors for malformed contracts and warnings for unfinished draft resources."""
    errors: list[str] = []
    warnings: list[str] = []
    delivery_issues: list[str] = []
    teaching = contract.get("teaching_contract")
    result = {"ok": True, "errors": errors, "warnings": warnings,
              "teaching_contract_present": teaching is not None,
              "semantic_review": "REQUIRED: compare original requirements with actual slides, demonstrations and feedback"}
    if teaching is None:
        message = "teaching_contract absent: legacy content handoff is valid; classroom readiness is unverified"
        (errors if ready_for_class else warnings).append(message)
        result["ok"] = not errors
        return result
    if not isinstance(teaching, dict) or teaching.get("version") != 1:
        errors.append("teaching_contract.version: expected version 1 object")
        result["ok"] = False
        return result

    source = teaching.get("source_outline")
    if not isinstance(source, dict):
        errors.append("teaching_contract.source_outline: object required")
    else:
        path = _local_file(root, source.get("path"))
        if path is None:
            errors.append("teaching_contract.source_outline.path: existing relative file required")
        elif not path.resolve().is_relative_to(root.resolve()):
            errors.append("teaching_contract.source_outline.path: original copy must be inside the bundle")
        elif source.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("teaching_contract.source_outline.sha256: original source hash mismatch")

    page_ids = [p.get("page_id") for p in pages]
    order = {pid: i for i, pid in enumerate(page_ids) if isinstance(pid, str)}
    if not pages:
        errors.append("pages: non-empty array required")
    if any(not isinstance(pid, str) or not pid.strip() for pid in page_ids):
        errors.append("pages: non-empty string page_id required")
    if len(order) != len(page_ids):
        errors.append("pages: unique page_id required")
    requirements = teaching.get("requirements")
    requirements = requirements if isinstance(requirements, list) else []
    if not requirements:
        errors.append("teaching_contract.requirements: non-empty array required")
    mapping: dict[str, set[str]] = {}
    for i, req in enumerate(requirements):
        prefix = f"teaching_contract.requirements[{i}]"
        if not isinstance(req, dict):
            errors.append(f"{prefix}: object required")
            continue
        rid = req.get("id")
        if not isinstance(rid, str) or not rid.strip():
            errors.append(f"{prefix}.id: non-empty string required")
            continue
        if rid in mapping:
            errors.append(f"{prefix}.id: duplicate requirement {rid}")
        if not isinstance(req.get("text"), str) or not req["text"].strip():
            errors.append(f"{prefix}.text: original requirement required")
        ids = req.get("page_ids")
        if not _strings(ids) or not ids:
            errors.append(f"{prefix}.page_ids: requirement has no mapped page")
            ids = []
        elif len(set(ids)) != len(ids):
            errors.append(f"{prefix}.page_ids: duplicate page")
        unknown = [pid for pid in ids if pid not in order]
        if unknown:
            errors.append(f"{prefix}.page_ids: unknown pages {unknown}")
        mapping[rid] = set(ids)

    total = 0
    times_valid = True
    for i, page in enumerate(pages):
        pid = page.get("page_id", f"row{i + 1}")
        if not isinstance(pid, str) or not pid:
            errors.append(f"row{i + 1}.page_id: non-empty string required")
            continue
        data = page.get("teaching")
        if not isinstance(data, dict):
            errors.append(f"{pid}.teaching: object required")
            times_valid = False
            continue
        mode = data.get("mode")
        if not isinstance(mode, str) or mode not in MODES:
            errors.append(f"{pid}.teaching.mode: expected one of {sorted(MODES)}")
        refs = data.get("requirement_ids")
        if not _strings(refs):
            errors.append(f"{pid}.teaching.requirement_ids: string array required")
            refs = []
        if mode != "transition" and not refs:
            errors.append(f"{pid}.teaching.requirement_ids: teaching page must map to a source requirement")
        if len(set(refs)) != len(refs):
            errors.append(f"{pid}.teaching.requirement_ids: duplicate requirement")
        for rid in refs:
            if rid not in mapping or pid not in mapping[rid]:
                errors.append(f"{pid}: inconsistent requirement mapping for {rid}")
        for rid, mapped in mapping.items():
            if pid in mapped and rid not in refs:
                errors.append(f"{pid}: missing reciprocal requirement {rid}")
        seconds = data.get("duration_seconds")
        if type(seconds) is not int or seconds < 0:
            errors.append(f"{pid}.teaching.duration_seconds: non-negative integer required")
            times_valid = False
        else:
            total += seconds
        for field in ("learner_action", "instructor_action"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                errors.append(f"{pid}.teaching.{field}: concrete action required")
        materials = data.get("material_refs")
        if not _strings(materials):
            errors.append(f"{pid}.teaching.material_refs: string array required")
            materials = []
        for ref in materials:
            if _local_file(root, ref) is None:
                delivery_issues.append(f"{pid}: missing local teaching material {ref!r}")
        reveal = data.get("reveal_after")
        if "reveal_after" not in data:
            errors.append(f"{pid}.teaching.reveal_after: null or earlier question page required")
        elif reveal is not None and (not isinstance(reveal, str) or reveal not in order or order[reveal] >= i):
            errors.append(f"{pid}.teaching.reveal_after: must reference an earlier page")
        note = page.get("speaker_notes_ref")
        note_file = _local_file(root, note)
        if note_file is None:
            delivery_issues.append(f"{pid}: missing local speaker notes reference")
        else:
            try:
                lines = note_file.read_text(encoding="utf-8").splitlines()
                if "#" in note:
                    fragment = note.split("#", 1)[1]
                    matches = [(n, len(m.group(1))) for n, line in enumerate(lines)
                               if (m := re.match(r"^(#{1,6})\s+", line)) and fragment in line]
                    if not fragment or len(matches) != 1:
                        delivery_issues.append(f"{pid}: notes fragment must match exactly one heading: {note}")
                        lines = []
                    else:
                        start, level = matches[0]
                        end = next((n for n in range(start + 1, len(lines))
                                    if (m := re.match(r"^(#{1,6})\s+", lines[n])) and len(m.group(1)) <= level), len(lines))
                        lines = lines[start + 1:end]
                spoken = next((n for n, line in enumerate(lines) if re.match(
                    r"^#{1,6}\s+(?:逐字稿|讲者备注|讲师口播|口播)\s*$", line)), None)
                if spoken is not None:
                    lines = lines[spoken + 1:]
                if not any(line.strip() and not line.lstrip().startswith("#") and line.strip() != "---" for line in lines):
                    delivery_issues.append(f"{pid}: empty speaker notes body: {note}")
            except (UnicodeError, OSError):
                delivery_issues.append(f"{pid}: notes reference is not readable UTF-8: {note}")

    course = contract.get("course")
    if not isinstance(course, dict):
        errors.append("course: object required for teaching duration")
        course = {}
    minutes = course.get("duration_minutes")
    if type(minutes) not in (int, float) or not math.isfinite(minutes) or minutes <= 0:
        errors.append("course.duration_minutes: finite positive number required")
    elif times_valid:
        if abs(total - minutes * 60) > 0.01:
            errors.append(f"teaching duration mismatch: pages={total}s, course={minutes * 60:g}s")
    result["duration_seconds"] = total
    coverage = root / "source_coverage.md"
    if not coverage.is_file() or not coverage.read_text(encoding="utf-8").strip():
        delivery_issues.append("source_coverage.md missing: original-to-delivery semantic review is pending")
    readiness_path = root / "readiness.json"
    if not readiness_path.is_file():
        delivery_issues.append("readiness.json missing: resource readiness is unrecorded")
    else:
        try:
            readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            errors.append(f"readiness.json: {exc}")
            readiness = {}
        if not isinstance(readiness, dict):
            errors.append("readiness.json: object required")
        else:
            if readiness.get("status") not in ("draft", "ready"):
                errors.append("readiness.status: draft or ready required")
            gaps = readiness.get("gaps")
            if not _strings(gaps):
                errors.append("readiness.gaps: string array required")
            else:
                delivery_issues.extend(f"readiness gap: {gap}" for gap in gaps)
                if gaps and readiness.get("status") == "ready":
                    errors.append("readiness.status cannot be ready while gaps remain")
            if readiness.get("status") == "draft":
                delivery_issues.append("readiness.status is draft")
    (errors if ready_for_class else warnings).extend(delivery_issues)
    result["ok"] = not errors
    return result


def validate_bundle(bundle: Path | str, *, ready_for_class: bool = False) -> dict:
    root = Path(bundle)
    try:
        contract = json.loads((root / "course_contract.json").read_text(encoding="utf-8"))
        if not isinstance(contract, dict):
            raise ValueError("course_contract.json must be an object")
        name = contract.get("pages_file", "pages.jsonl")
        if not isinstance(name, str) or Path(name).name != name:
            raise ValueError("pages_file must be a local filename")
        pages = [json.loads(line) for line in (root / name).read_text(encoding="utf-8").splitlines() if line.strip()]
        if not all(isinstance(page, dict) for page in pages):
            raise ValueError("pages.jsonl rows must be objects")
        return validate_teaching(root, contract, pages, ready_for_class=ready_for_class)
    except (OSError, ValueError, UnicodeError) as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": []}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--ready-for-class", action="store_true", help="Fail on unfinished resources; semantic review is still required")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate_bundle(args.bundle, ready_for_class=args.ready_for_class)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{'PASS' if result['ok'] else 'FAIL'}: teaching contract {args.bundle}")
        for label in ("errors", "warnings"):
            for message in result[label]:
                print(f"{label.upper()}: {message}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
