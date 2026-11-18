#!/usr/bin/env python3
"""Import existing per-page course notes without rewriting their instructional content."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from course_pages import playback_pages


def extract_note(bundle: Path, ref: str) -> str:
    name, _, anchor = ref.partition("#")
    if not name or "://" in name or Path(name).is_absolute():
        raise ValueError(f"local notes file required: {ref}")
    path = (bundle / name).resolve()
    if not path.is_relative_to(bundle.resolve()):
        raise ValueError(f"notes must be inside the handoff: {ref}")
    lines = path.read_text(encoding="utf-8").splitlines()
    if anchor:
        matches = [(i, len(m.group(1))) for i, line in enumerate(lines)
                   if (m := re.match(r"^(#{1,6})\s+", line)) and anchor in line]
        if len(matches) != 1:
            raise ValueError(f"notes anchor must match one heading: {ref}")
        start, level = matches[0]
        end = next((i for i in range(start + 1, len(lines))
                    if (m := re.match(r"^(#{1,6})\s+", lines[i])) and len(m.group(1)) <= level), len(lines))
        lines = lines[start + 1:end]
    # Legacy Scriptwriter pages mix slide copy/design metadata with the actual notes.
    spoken = next((i for i, line in enumerate(lines)
                   if re.match(r"^#{1,6}\s+(?:逐字稿|讲者备注|讲师口播|口播)\s*$", line)), None)
    if spoken is not None:
        lines = lines[spoken + 1:]
    elif lines and re.match(r"^#{1,6}\s+", lines[0]):
        lines = lines[1:]
    while lines and (not lines[-1].strip() or lines[-1].strip() == "---"):
        lines.pop()
    body = "\n".join(lines).strip()
    if not body:
        raise ValueError(f"empty speaker notes: {ref}")
    return body


def import_notes(bundle: Path, project: Path) -> Path:
    pages = playback_pages(bundle)
    stems: dict[int, str] = {}
    for svg in (project / "svg_output").glob("*.svg"):
        match = re.match(r"^(\d+)(?:[_\-.]|$)", svg.stem)
        if match:
            number = int(match[1])
            if number in stems:
                raise ValueError(f"duplicate SVG sequence: {number}")
            stems[number] = svg.stem
    if set(stems) != set(range(1, len(pages) + 1)):
        raise ValueError("SVG sequences must match course playback sequences")
    output: list[str] = []
    for i, page in enumerate(pages, 1):
        ref = page.get("speaker_notes_ref")
        if not isinstance(ref, str) or not ref:
            raise ValueError(f"missing speaker_notes_ref: {page.get('page_id')}")
        output.append(f"# {stems[i]}\n\n{extract_note(bundle, ref)}")
    target = project / "notes/total.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n\n---\n\n".join(output) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    try:
        print(import_notes(args.bundle, args.project))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
