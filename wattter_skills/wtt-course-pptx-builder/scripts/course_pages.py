#!/usr/bin/env python3
"""Read the playback order of a course handoff without changing its baseline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_rows(root: Path, filename: str) -> list[dict]:
    if not isinstance(filename, str) or Path(filename).name != filename:
        raise ValueError(f"expected a local filename: {filename!r}")
    rows = [json.loads(line) for line in (root / filename).read_text(encoding="utf-8").splitlines()
            if line.strip()]
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{filename}: rows must be objects")
    return rows


def playback_pages(bundle: Path, contract: dict | None = None) -> list[dict]:
    if contract is None:
        contract = json.loads((bundle / "course_contract.json").read_text(encoding="utf-8"))
    pages = read_rows(bundle, contract.get("pages_file", "pages.jsonl"))
    if not pages or contract.get("page_count", len(pages)) != len(pages):
        raise ValueError("course page count mismatch")
    if any(type(page.get("sequence")) is not int or page["sequence"] != index
           for index, page in enumerate(pages, 1)):
        raise ValueError("course sequence must be contiguous and ordered")
    baseline_ids = [page.get("page_id") for page in pages]
    if any(not isinstance(pid, str) or not pid.strip() for pid in baseline_ids):
        raise ValueError("course page IDs must be non-empty strings")
    if len(set(baseline_ids)) != len(baseline_ids):
        raise ValueError("course page IDs must be unique")
    profile_path = bundle / "design_profile.json"
    if not profile_path.exists():
        return pages

    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    intents = read_rows(bundle, profile.get("page_intents_file", "page_intents.jsonl"))
    if [row.get("page_id") for row in intents if row.get("origin", "baseline") == "baseline"] != baseline_ids:
        raise ValueError("design baseline order differs from pages.jsonl")
    ids = [row.get("page_id") for row in intents]
    if len(set(ids)) != len(ids):
        raise ValueError("design page IDs must be unique")

    result = []
    seen_baseline = set()
    baseline = dict(zip(baseline_ids, pages))
    for sequence, row in enumerate(intents, 1):
        page_id = row["page_id"]
        origin = row.get("origin", "baseline")
        if origin == "baseline":
            seen_baseline.add(page_id)
            page = baseline[page_id]
        elif origin == "inserted":
            if contract.get("policies", {}).get("allow_page_count_change") is not True:
                raise ValueError(f"{page_id}: insertion not allowed by course policy")
            ref = row.get("baseline_ref")
            if ref not in seen_baseline:
                raise ValueError(f"{page_id}: insertion must follow its baseline page")
            content = row.get("ins_content")
            kind = row.get("ins_kind")
            if not isinstance(content, dict) or kind not in {"hero", "interaction", "case", "exercise"}:
                raise ValueError(f"{page_id}: invalid insertion content or kind")
            page = {
                "page_id": page_id,
                "section_id": baseline[ref].get("section_id"),
                "page_type": kind,
                "outline_title": content.get("title"),
                "display_title": None,
                "must_include": [],
                "slide_text": content,
                "evidence_refs": [],
                "speaker_notes_ref": row.get("speaker_notes_ref"),
            }
            if "teaching" in row:
                page["teaching"] = row["teaching"]
        else:
            raise ValueError(f"{page_id}: unsupported page origin {origin!r}")
        result.append(dict(page, sequence=sequence))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(playback_pages(args.bundle), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
