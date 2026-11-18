#!/usr/bin/env python3
"""Page-level generation state for large-deck parallel execution.

Models the per-page / per-segment progress of a PPT project as a single
JSON manifest at ``<project>/generation_state.json``. This is the
coordination primitive between the orchestrating session and segment
sessions in the parallel-execute workflow (see
``workflows/parallel-execute.md``).

Schema (top level)::

    {
      "project": "<name>",
      "total_pages": 500,
      "threshold": 60,
      "parallel_mode": true,
      "anchors": {"approved": false, "pages": ["01_cover", ...]},
      "segments": [
        {"id": "seg_01", "pages": ["P01", ..., "P28"],
         "worktree": ".claude/worktrees/seg_01",
         "status": "pending", "pages_done": 0,
         "pages_failed": [], "attempts": 0,
         "assigned_session": null}
      ],
      "pages": {"P01": "pending", "P02": "done", ...},
      "last_updated": "<iso8601>"
    }

Page status state machine::

    pending -> generating -> done | failed -> needs-manual

Segment status: ``pending`` / ``generating`` / ``done`` / ``degraded`` /
``failed``.

The manifest is the single source of truth for progress. Any session can
read it; only the segment owning a page may mark that page. Segment
page sets MUST be disjoint — enforced on ``add-segment``.

Atomic writes (tmp + rename) mirror ``image_gen.save_manifest`` so
concurrent segment sessions do not corrupt the file.

Usage::

    python3 scripts/generation_state.py init <project> --total 500
    python3 scripts/generation_state.py add-segment <project> --pages P01-P28
    python3 scripts/generation_state.py approve-anchors <project>
    python3 scripts/generation_state.py mark-page <project> P01 done
    python3 scripts/generation_state.py mark-segment <project> seg_01 done
    python3 scripts/generation_state.py status <project>
    python3 scripts/generation_state.py next-pending <project>
    python3 scripts/generation_state.py resume <project>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

STATE_FILENAME = "generation_state.json"

PAGE_STATUSES = ("pending", "generating", "done", "failed", "needs-manual")
SEGMENT_STATUSES = ("pending", "generating", "done", "degraded", "failed")
TERMINAL_PAGE = {"done", "needs-manual"}
RETRYABLE_PAGE = {"failed"}


# ---------------------------------------------------------------------------
# Page-range parsing
# ---------------------------------------------------------------------------

def _parse_pages(spec: str) -> list[str]:
    """Parse a page spec like 'P01-P28' or 'P01,P03,P05' into ['P01', ...].

    Zero-pads to at least 2 digits. Supports a single range (P01-P28) or a
    comma list (P01,P03,P05). Mixing range and list in one spec is allowed:
    'P01-P05,P10,P12'.
    """
    spec = spec.strip()
    if not spec:
        raise ValueError("empty page spec")
    out: list[str] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"P?(\d+)-P?(\d+)", part, re.IGNORECASE)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            if lo > hi:
                raise ValueError(f"range {part}: lo > hi")
            for n in range(lo, hi + 1):
                out.append(f"P{n:02d}")
            continue
        m = re.fullmatch(r"P?(\d+)", part, re.IGNORECASE)
        if m:
            out.append(f"P{int(m.group(1)):02d}")
            continue
        raise ValueError(f"bad page token: {part!r}")
    if not out:
        raise ValueError("page spec produced no pages")
    # dedupe preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


# ---------------------------------------------------------------------------
# I/O (atomic, mirrors image_gen.save_manifest)
# ---------------------------------------------------------------------------

def state_path(project: str) -> Path:
    return Path(project) / STATE_FILENAME


def load_state(project: str) -> dict:
    p = state_path(project)
    if not p.exists():
        raise FileNotFoundError(
            f"no {STATE_FILENAME} in {project} — run `init` first"
        )
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {p}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{p}: top level must be an object")
    return data


def save_state(project: str, data: dict) -> None:
    p = state_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat(timespec="seconds")
    fd, tmp = tempfile.mkstemp(prefix=p.stem + ".", suffix=".tmp", dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, p)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Disjointness enforcement
# ---------------------------------------------------------------------------

def _all_assigned_pages(data: dict, exclude_seg: str | None = None) -> set[str]:
    out: set[str] = set()
    for seg in data.get("segments", []):
        if exclude_seg and seg["id"] == exclude_seg:
            continue
        out.update(seg.get("pages", []))
    return out


def _ensure_disjoint(data: dict, seg_id: str, pages: list[str]) -> None:
    existing = _all_assigned_pages(data, exclude_seg=seg_id)
    clash = existing & set(pages)
    if clash:
        raise ValueError(
            f"segment {seg_id!r} pages overlap existing segments: "
            f"{sorted(clash)} — segments must be disjoint"
        )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(project: str, total: int, threshold: int) -> dict:
    p = state_path(project)
    if p.exists():
        raise SystemExit(f"{p} already exists — refusing to overwrite")
    if total <= 0:
        raise ValueError("--total must be positive")
    data = {
        "project": Path(project).name,
        "total_pages": total,
        "threshold": threshold,
        "parallel_mode": total >= threshold,
        "anchors": {"approved": False, "pages": []},
        "segments": [],
        "pages": {f"P{n:02d}": "pending" for n in range(1, total + 1)},
    }
    save_state(project, data)
    print(f"[init] {project}: {total} pages, threshold={threshold}, "
          f"parallel_mode={data['parallel_mode']}")
    return data


def cmd_add_segment(project: str, seg_id: str, pages_spec: str,
                    worktree: str | None) -> dict:
    data = load_state(project)
    pages = _parse_pages(pages_spec)
    if any(seg["id"] == seg_id for seg in data["segments"]):
        raise ValueError(f"segment {seg_id!r} already exists")
    _ensure_disjoint(data, seg_id, pages)
    # every page must be within total
    known = set(data["pages"].keys())
    unknown = [p for p in pages if p not in known]
    if unknown:
        raise ValueError(f"pages out of range: {unknown}")
    data["segments"].append({
        "id": seg_id,
        "pages": pages,
        "worktree": worktree or "",
        "status": "pending",
        "pages_done": 0,
        "pages_failed": [],
        "attempts": 0,
        "assigned_session": None,
    })
    save_state(project, data)
    print(f"[add-segment] {seg_id}: {len(pages)} pages ({pages[0]}..{pages[-1]})")
    return data


def cmd_approve_anchors(project: str, pages: list[str] | None) -> dict:
    data = load_state(project)
    data["anchors"]["approved"] = True
    if pages:
        data["anchors"]["pages"] = pages
    save_state(project, data)
    print(f"[approve-anchors] anchors frozen: {data['anchors']['pages']}")
    return data


def cmd_mark_page(project: str, page_id: str, status: str,
                  seg_id: str | None) -> dict:
    if status not in PAGE_STATUSES:
        raise ValueError(f"status must be one of {PAGE_STATUSES}")
    data = load_state(project)
    if page_id not in data["pages"]:
        raise ValueError(f"unknown page {page_id}")
    # enforce ownership: page must belong to a segment (parallel mode) or be
    # unassigned (serial mode). In parallel mode, seg_id must own the page.
    if data.get("parallel_mode") and data["segments"]:
        owner = next((s for s in data["segments"] if page_id in s["pages"]), None)
        if owner is None:
            raise ValueError(
                f"{page_id} not assigned to any segment — cannot mark"
            )
        if seg_id and seg_id != owner["id"]:
            raise ValueError(
                f"{page_id} belongs to segment {owner['id']!r}, not {seg_id!r}"
            )
    data["pages"][page_id] = status
    _refresh_segment(data, page_id)
    save_state(project, data)
    print(f"[mark-page] {page_id}: {status}")
    return data


def _refresh_segment(data: dict, page_id: str) -> None:
    """Update segment aggregates after a page status change."""
    seg = next((s for s in data["segments"] if page_id in s["pages"]), None)
    if seg is None:
        return
    done = sum(1 for p in seg["pages"] if data["pages"].get(p) in TERMINAL_PAGE)
    failed = [p for p in seg["pages"] if data["pages"].get(p) == "failed"]
    seg["pages_done"] = done
    seg["pages_failed"] = failed
    if done == len(seg["pages"]) and not failed:
        seg["status"] = "done"
    elif done > 0:
        seg["status"] = "generating"


def cmd_mark_segment(project: str, seg_id: str, status: str,
                     session: str | None) -> dict:
    if status not in SEGMENT_STATUSES:
        raise ValueError(f"status must be one of {SEGMENT_STATUSES}")
    data = load_state(project)
    seg = next((s for s in data["segments"] if s["id"] == seg_id), None)
    if seg is None:
        raise ValueError(f"unknown segment {seg_id!r}")
    seg["status"] = status
    if session:
        seg["assigned_session"] = session
    if status == "degraded":
        seg["attempts"] = seg.get("attempts", 0) + 1
    save_state(project, data)
    print(f"[mark-segment] {seg_id}: {status}")
    return data


def cmd_status(project: str) -> int:
    data = load_state(project)
    pages = data["pages"]
    counts: dict[str, int] = {}
    for st in PAGE_STATUSES:
        counts[st] = sum(1 for v in pages.values() if v == st)
    total = len(pages)
    done = counts["done"] + counts["needs-manual"]
    print(f"project: {data['project']}  total: {total}  "
          f"parallel_mode: {data.get('parallel_mode')}")
    print(f"anchors approved: {data['anchors']['approved']}  "
          f"anchor pages: {data['anchors']['pages']}")
    print(f"segments: {len(data['segments'])}")
    for seg in data["segments"]:
        print(f"  {seg['id']}: {seg['status']}  "
              f"{seg['pages_done']}/{len(seg['pages'])} done  "
              f"failed={seg['pages_failed']}  attempts={seg['attempts']}")
    print(f"pages: done={counts['done']}  needs-manual={counts['needs-manual']}  "
          f"generating={counts['generating']}  failed={counts['failed']}  "
          f"pending={counts['pending']}  ({done}/{total} terminal)")
    return 0 if (done == total) else 1


def cmd_next_pending(project: str, seg_id: str | None) -> int:
    data = load_state(project)
    if seg_id:
        seg = next((s for s in data["segments"] if s["id"] == seg_id), None)
        if seg is None:
            raise ValueError(f"unknown segment {seg_id!r}")
        pool = seg["pages"]
    else:
        pool = list(data["pages"].keys())
    for p in pool:
        if data["pages"][p] in ("pending", "failed"):
            print(p)
            return 0
    print("(none pending)", file=sys.stderr)
    return 1


def cmd_failed_pages(project: str, seg_id: str | None) -> int:
    """List pages that failed validation and need repair work.

    Prints one page id per line for every page whose status is ``failed`` or
    ``needs-manual``. Optional ``seg_id`` restricts to that segment's page
    range. Returns 0 if any such pages exist (so a repair worktree session
    receives a non-empty target list), 1 otherwise — mirroring
    :func:`cmd_next_pending` so callers can branch on exit code.
    """
    data = load_state(project)
    if seg_id:
        seg = next((s for s in data["segments"] if s["id"] == seg_id), None)
        if seg is None:
            raise ValueError(f"unknown segment {seg_id!r}")
        pool = seg["pages"]
    else:
        pool = list(data["pages"].keys())
    found = [p for p in pool if data["pages"][p] in ("failed", "needs-manual")]
    for p in found:
        print(p)
    return 0 if found else 1


def cmd_note(project: str, message: str) -> dict:
    """Append a checkpoint note to the state manifest.

    Useful for serial-with-state progress: every checkpoint write records
    a timestamped message (e.g. 'page 10 done — checkpoint re-read spec_lock'),
    so compaction recovery can scan the trail without reading the LLM's chat
    history. Schema is additive — older manifests without a `notes` field
    are tolerated via setdefault.
    """
    data = load_state(project)
    data.setdefault("notes", []).append({
        "at": datetime.now().astimezone().isoformat(),
        "message": message,
    })
    save_state(project, data)
    print(f"[note] {message}")
    return data


def cmd_resume(project: str) -> int:
    """Print a resume plan: which segments/pages still need work."""
    data = load_state(project)
    print(f"# resume plan for {data['project']}")
    incomplete = [s for s in data["segments"]
                  if s["status"] not in ("done",)]
    if not incomplete and data.get("parallel_mode"):
        # check unassigned pages
        unassigned = [p for p, st in data["pages"].items()
                      if st in ("pending", "failed", "generating")
                      and not any(p in s["pages"] for s in data["segments"])]
        if unassigned:
            print(f"unassigned pages need work: {unassigned}")
        else:
            print("all segments done — proceed to stitch + export")
            return 0
    for seg in incomplete:
        pending = [p for p in seg["pages"]
                   if data["pages"][p] in ("pending", "failed", "generating")]
        print(f"segment {seg['id']} ({seg['status']}): {len(pending)} pages "
              f"remaining → {pending[:10]}{'...' if len(pending) > 10 else ''}")
    return 0 if incomplete else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Page-level generation state for large-deck parallel execution."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize generation_state.json")
    p_init.add_argument("project")
    p_init.add_argument("--total", type=int, required=True)
    p_init.add_argument("--threshold", type=int, default=60)

    p_add = sub.add_parser("add-segment", help="Add a segment with a page range")
    p_add.add_argument("project")
    p_add.add_argument("--id", required=True, dest="seg_id")
    p_add.add_argument("--pages", required=True, help="e.g. P01-P28 or P01,P03,P05")
    p_add.add_argument("--worktree", default=None)

    p_anchor = sub.add_parser("approve-anchors", help="Mark anchors as approved (frozen)")
    p_anchor.add_argument("project")
    p_anchor.add_argument("--pages", nargs="*", default=None,
                          help="anchor page ids, e.g. 01_cover 05_dense_repr")

    p_mark = sub.add_parser("mark-page", help="Update a page's status")
    p_mark.add_argument("project")
    p_mark.add_argument("page_id")
    p_mark.add_argument("status", choices=PAGE_STATUSES)
    p_mark.add_argument("--segment", default=None, dest="seg_id")

    p_mseg = sub.add_parser("mark-segment", help="Update a segment's status")
    p_mseg.add_argument("project")
    p_mseg.add_argument("seg_id")
    p_mseg.add_argument("status", choices=SEGMENT_STATUSES)
    p_mseg.add_argument("--session", default=None)

    p_status = sub.add_parser("status", help="Print progress summary")
    p_status.add_argument("project")

    p_next = sub.add_parser("next-pending", help="Print next pending/failed page id")
    p_next.add_argument("project")
    p_next.add_argument("--segment", default=None, dest="seg_id")

    p_failed = sub.add_parser(
        "failed-pages",
        help="List pages needing repair (status failed/needs-manual), one per line",
    )
    p_failed.add_argument("project")
    p_failed.add_argument("seg_id", nargs="?", default=None,
                          help="optional segment id to scope the listing")

    p_resume = sub.add_parser("resume", help="Print a resume plan")
    p_resume.add_argument("project")

    p_note = sub.add_parser(
        "note",
        help="Append a checkpoint note (used by serial-with-state progress)",
    )
    p_note.add_argument("project")
    p_note.add_argument(
        "message",
        help="Free-text checkpoint message, e.g. 'page 10 done'",
    )

    args = parser.parse_args()

    try:
        if args.cmd == "init":
            cmd_init(args.project, args.total, args.threshold)
        elif args.cmd == "add-segment":
            cmd_add_segment(args.project, args.seg_id, args.pages, args.worktree)
        elif args.cmd == "approve-anchors":
            cmd_approve_anchors(args.project, args.pages)
        elif args.cmd == "mark-page":
            cmd_mark_page(args.project, args.page_id, args.status, args.seg_id)
        elif args.cmd == "mark-segment":
            cmd_mark_segment(args.project, args.seg_id, args.status, args.session)
        elif args.cmd == "status":
            return cmd_status(args.project)
        elif args.cmd == "next-pending":
            return cmd_next_pending(args.project, args.seg_id)
        elif args.cmd == "failed-pages":
            return cmd_failed_pages(args.project, args.seg_id)
        elif args.cmd == "resume":
            return cmd_resume(args.project)
        elif args.cmd == "note":
            cmd_note(args.project, args.message)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
