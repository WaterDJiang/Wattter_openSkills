#!/usr/bin/env python3
"""
PPT Master - spec_lock → locked_values.json extractor

Distills a project's spec_lock.md (the full execution contract, ~190 lines)
into a compact JSON cache (~30-50 lines) that the Executor re-reads before
every SVG page instead of the full markdown — same anti-drift guarantee at
~1/6 the per-page token cost. See SKILL.md global discipline Rule 8.

Usage:
    python3 scripts/extract_locked_values.py <project_path> [--page P001]

Writes <project_path>/locked_values.json. Re-run after any spec_lock.md edit
( Strategist calls this right after generating spec_lock.md in §6.2 step 4 ).

The JSON is a faithful subset of spec_lock.md — it adds no new decisions.
If a field the Executor needs is absent here, that is the signal to re-read
the full spec_lock.md (per Rule 8 fallback clause).
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from update_spec import parse_lock
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from update_spec import parse_lock


# Sections whose entire {key: value} dict is carried verbatim — these are the
# per-page lookup tables the Executor consults on every page. `images` MUST be
# here: image pages need the filename + `| no-crop` crop directive per page, and
# omitting it would force a fallback to full spec_lock.md on every image page
# (defeating the token saving) or cause image drift on long decks.
_PASS_THROUGH_SECTIONS = (
    "route",
    "variant_policy",
    "images",
    "page_rhythm",
    "page_layouts",
    "page_render_modes",
    "page_shell_assets",
    "page_shell_requirements",
    "page_charts",
    "page_assets",
    "html_backgrounds",
)


def _canvas_format_from_viewbox(viewbox: str) -> str:
    """Map a viewBox to the canonical canvas_format slug."""
    vb_to_fmt = {
        "0 0 1280 720": "ppt169",
        "0 0 1024 768": "ppt43",
        "0 0 1242 1660": "xiaohongshu",
        "0 0 1080 1080": "moments",
        "0 0 1080 1920": "story",
    }
    return vb_to_fmt.get(viewbox.strip(), "unknown")


def extract(project_path: str | Path) -> dict:
    """Build the locked-values dict from <project>/spec_lock.md."""
    project = Path(project_path)
    lock_path = project / "spec_lock.md"
    if not lock_path.exists():
        raise FileNotFoundError(
            f"spec_lock.md not found at {lock_path} — run Strategist §6.2 first."
        )

    sections = parse_lock(lock_path)

    out: dict = {"_source": "spec_lock.md", "_note": "Compact anti-drift cache. Re-read full spec_lock.md only if a needed field is absent."}

    # canvas
    canvas = sections.get("canvas", {})
    if "viewBox" in canvas:
        out["canvas"] = {"viewbox": canvas["viewBox"], "format": _canvas_format_from_viewbox(canvas["viewBox"])}

    # mode / visual_style — carry the WHOLE section dict so sibling behavior
    # paragraphs (mode_behavior / visual_style_behavior) come along. These are
    # required when the value is `custom`; dropping them would lose the aesthetic
    # intent the Executor follows per page.
    for sec in ("mode", "visual_style"):
        if sec in sections and sections[sec]:
            out[sec] = dict(sections[sec])

    # colors — carry the whole role dict (drop non-HEX advisory keys)
    if "colors" in sections:
        out["colors"] = dict(sections["colors"])

    # typography — split font families vs size ramp
    if "typography" in sections:
        typo = sections["typography"]
        fam_keys = ("font_family", "title_family", "body_family", "emphasis_family", "code_family")
        families = {k: typo[k] for k in fam_keys if k in typo}
        # size ramp: keys whose value parses as a number
        ramp = {k: float(v) if re.fullmatch(r"\d+(\.\d+)?", v) else v
                for k, v in typo.items() if k not in fam_keys and re.fullmatch(r"\d+(\.\d+)?", v)}
        if families:
            out["fonts"] = families
        if ramp:
            out["font_size_ramp"] = ramp

    # icons
    if "icons" in sections:
        out["icons"] = dict(sections["icons"])

    # per-page lookup tables — verbatim
    for sec in _PASS_THROUGH_SECTIONS:
        if sec in sections and sections[sec]:
            out[sec] = dict(sections[sec])

    return out


def page_values(data: dict, page_id: str) -> dict:
    """Keep shared locks and only the requested page's entries."""
    result = {"page_id": page_id}
    for key, value in data.items():
        if key.startswith("page_") or key == "html_backgrounds":
            if page_id in value:
                result[key] = {page_id: value[page_id]}
        elif key == "images":
            result[key] = {
                name: asset for name, asset in value.items()
                if name == page_id or name.startswith(page_id + "_")
                or not re.match(r"^P\d+(?:_|$)", name)
            }
        else:
            result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the execution cache or print its current-page view.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--page", metavar="PAGE_ID", help="Print shared and current-page locks without rewriting files")
    args = parser.parse_args()
    project = args.project
    out_path = project / "locked_values.json"
    try:
        if args.page:
            data = json.loads(out_path.read_text(encoding="utf-8"))
            print(json.dumps(page_values(data, args.page), ensure_ascii=False, separators=(",", ":")))
            return 0
        data = extract(project)
    except (OSError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    # One-line confirmation: fields + byte size (the win over full spec_lock.md)
    size = out_path.stat().st_size
    lock_size = (Path(project) / "spec_lock.md").stat().st_size
    print(f"[locked_values] wrote {out_path} — {len(data)} top-level fields, "
          f"{size} bytes (spec_lock.md is {lock_size} bytes, "
          f"{round((1 - size / lock_size) * 100)}% smaller)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
