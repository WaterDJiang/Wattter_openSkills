#!/usr/bin/env python3
"""Write fixed-page instructor notes into a new PPTX without rebuilding slides."""
from __future__ import annotations

import argparse
from copy import copy
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import zipfile

from lxml import etree
from pptx import Presentation

from course_delivery import NS, rel_targets, slide_parts
from import_course_notes import extract_note
from svg_to_pptx.pptx_notes import markdown_to_plain_text


def note_targets(package: zipfile.ZipFile, part: str, kind: str) -> list[str]:
    return [target for rel_kind, target in rel_targets(package, part).values() if rel_kind == kind]


def rel_path(part: str) -> str:
    path = PurePosixPath(part)
    return str(path.parent / "_rels" / (path.name + ".rels"))


def xml(package: zipfile.ZipFile, path: str):
    return etree.fromstring(package.read(path))


def append_notes_relationship(source, donor, updates, part, kind):
    rels_path = rel_path(part)
    proposed = xml(donor, rels_path)
    additions = [row for row in proposed if row.get("Type", "").endswith("/" + kind)]
    if len(additions) != 1:
        raise ValueError(f"{part}: expected one {kind} relationship")
    tree = xml(source, rels_path) if rels_path in source.namelist() else etree.Element(proposed.tag, nsmap=proposed.nsmap)
    addition = additions[0]
    known = {entry.get("Id") for entry in tree}
    if addition.get("Id") in known:
        index = 1
        while f"rId{index}" in known:
            index += 1
        addition.set("Id", f"rId{index}")
    tree.append(addition)
    updates[rels_path] = etree.tostring(tree)
    return addition.get("Id")


def rebuild_package(source, donor, output, note_updates):
    original_slides = slide_parts(source)
    donor_slides = slide_parts(donor)
    original_targets = [target for part in original_slides for target in note_targets(source, part, "notesSlide")]
    if len(set(original_targets)) != len(original_targets):
        raise ValueError("source PPTX shares a notes part between slides")
    updates = {}
    new_names = set(donor.namelist()) - set(source.namelist())
    for pos in note_updates:
        part = original_slides[pos]
        original_notes = note_targets(source, part, "notesSlide")
        donor_notes = note_targets(donor, donor_slides[pos], "notesSlide")
        if len(donor_notes) != 1 or len(original_notes) > 1:
            raise ValueError(f"page {pos + 1}: invalid notes relationship")
        donor_note = donor_notes[0]
        if original_notes:
            target = original_notes[0]
            original_note = xml(source, target)
            donor_tree = xml(donor, donor_note)
            body = './/p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody'
            current = original_note.xpath(body, namespaces=NS)
            replacement = donor_tree.xpath(body, namespaces=NS)
            if len(current) != 1 or len(replacement) != 1:
                raise ValueError(f"page {pos + 1}: notes body placeholder missing or duplicated")
            current[0].getparent().replace(current[0], replacement[0])
            updates[target] = etree.tostring(original_note)
        else:
            if original_slides != donor_slides or donor_note not in new_names:
                raise ValueError("cannot safely graft new notes: donor slide or notes identities changed")
            append_notes_relationship(source, donor, updates, part, "notesSlide")
            updates[donor_note] = donor.read(donor_note)
            updates[rel_path(donor_note)] = donor.read(rel_path(donor_note))
            master, = note_targets(donor, donor_note, "notesMaster")
            if master in new_names:
                updates[master] = donor.read(master)
                master_rels = rel_path(master)
                if master_rels in new_names:
                    updates[master_rels] = donor.read(master_rels)
                    for _, target in rel_targets(donor, master).values():
                        if target in new_names:
                            updates[target] = donor.read(target)
                if "ppt/presentation.xml" not in updates:
                    pres_part = "ppt/presentation.xml"
                    rel_id = append_notes_relationship(source, donor, updates, pres_part, "notesMaster")
                    pres = xml(source, pres_part)
                    tag = lambda name: f"{{{NS['p']}}}{name}"
                    prior = pres.find(tag("notesMasterIdLst"))
                    if prior is not None and len(prior):
                        raise ValueError("existing presentation notes master is inconsistent")
                    if prior is None:
                        prior = etree.Element(tag("notesMasterIdLst"))
                        after = int(len(pres) > 0 and pres[0].tag == tag("sldMasterIdLst"))
                        pres.insert(after, prior)
                    etree.SubElement(prior, tag("notesMasterId"), {f"{{{NS['r']}}}id": rel_id})
                    updates[pres_part] = etree.tostring(pres)

    added = set(updates) - set(source.namelist())
    if added:
        types = "[Content_Types].xml"
        tree = xml(source, types)
        existing = {(row.tag, row.get("PartName") or row.get("Extension")) for row in tree}
        for row in xml(donor, types):
            part = (row.get("PartName") or "").lstrip("/")
            extension = row.get("Extension")
            if part in added or (extension and any(n.endswith("." + extension) for n in added)):
                key = (row.tag, row.get("PartName") or extension)
                if key not in existing:
                    tree.append(row)
                    existing.add(key)
        updates[types] = etree.tostring(tree)

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as result:
        for entry in source.infolist():
            payload = updates.pop(entry.filename) if entry.filename in updates else source.read(entry)
            result.writestr(copy(entry), payload)
        for name, payload in updates.items():
            result.writestr(name, payload)


def write_notes(source: Path, baseline: Path, output: Path, only: set[str] | None = None) -> int:
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    data = json.loads(baseline.read_text(encoding="utf-8"))
    source_bytes = source.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != data.get("source_sha256"):
        raise ValueError("source PPTX SHA-256 differs from the fixed-page baseline")
    rows = data["pages"]
    presentation = Presentation(io.BytesIO(source_bytes))
    if len(rows) != len(presentation.slides):
        raise ValueError("fixed pages and source PPTX counts differ")
    ids = [row["page_id"] for row in rows]
    if len(set(ids)) != len(ids) or any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", pid) for pid in ids):
        raise ValueError("fixed page IDs must be unique filename-safe identifiers")
    if only and only - set(ids):
        raise ValueError(f"unknown page IDs: {sorted(only - set(ids))}")
    notes = {}
    home = baseline.parent.resolve()
    for index, (row, slide) in enumerate(zip(rows, presentation.slides)):
        if row.get("original_page") != index + 1:
            raise ValueError(f"{ids[index]}: fixed page order differs from PPTX")
        if only and ids[index] not in only:
            continue
        ref = row.get("notes_ref", f"notes/{ids[index]}.md")
        note = markdown_to_plain_text(extract_note(home, ref))
        if not note:
            raise ValueError(f"{ids[index]}: empty embedded notes")
        frame = slide.notes_slide.notes_text_frame
        if frame is None:
            raise ValueError(f"{ids[index]}: notes body placeholder missing")
        frame.text = note
        notes[index] = note
    if not notes:
        raise ValueError("no notes to write")

    buffer = io.BytesIO()
    presentation.save(buffer)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".pptx") as temp:
        with zipfile.ZipFile(io.BytesIO(source_bytes)) as original, zipfile.ZipFile(buffer) as donor:
            rebuild_package(original, donor, temp.name, notes)
            with zipfile.ZipFile(temp.name) as updated:
                parts = slide_parts(original)
                if parts != slide_parts(updated) or any(original.read(p) != updated.read(p) for p in parts):
                    raise ValueError("notes update changed slide XML or order")
        reread = Presentation(temp.name)
        for index, note in notes.items():
            if reread.slides[index].notes_slide.notes_text_frame.text != note:
                raise ValueError(f"{ids[index]}: embedded notes verification failed")
        os.link(temp.name, output)
    return len(notes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("fixed_pages", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--page", action="append", help="Stable page ID. Repeat to update a subset.")
    args = parser.parse_args()
    try:
        count = write_notes(args.pptx, args.fixed_pages, args.out, set(args.page or []))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, zipfile.BadZipFile, etree.XMLSyntaxError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: {count} notes updated; slide XML and order unchanged. {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
