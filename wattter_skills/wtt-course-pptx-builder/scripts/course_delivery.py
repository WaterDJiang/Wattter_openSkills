"""Course source, split-note and OOXML delivery checks (standard library)."""
from __future__ import annotations

import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from course_pages import playback_pages
from import_course_notes import extract_note
from validate_content_fidelity import find_bundle, visible_leaf_paths

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'


def load_pages(project: Path) -> tuple[Path | None, list[dict]]:
    bundle = find_bundle(project)
    if bundle is None:
        return None, []
    return bundle, playback_pages(bundle)


def note_key(text: str) -> str:
    from svg_to_pptx.pptx_notes import markdown_to_plain_text
    # Only whitespace may change when Markdown is serialized into a:paragraphs.
    return re.sub(r'\s+', '', markdown_to_plain_text(text))


def check_split_notes(project: Path, svgs: list[Path], notes: dict[str, str],
                      enabled: bool = True) -> list[str]:
    bundle, pages = load_pages(project)
    required = bundle is not None or (project / 'notes/total.md').exists()
    if not required:
        return []
    errors = []
    if not enabled:
        errors.append('course/total.md export requires embedded notes; --no-notes is invalid')
    if pages and len(pages) != len(svgs):
        errors.append(f'course/SVG count mismatch: {len(pages)}/{len(svgs)}')
    for index, svg in enumerate(svgs):
        actual = notes.get(svg.stem, '')
        if not actual.strip():
            errors.append(f'{svg.stem}: missing split notes; run import_course_notes.py then total_md_split.py')
        if bundle and index < len(pages):
            page = pages[index]
            ref = page.get('speaker_notes_ref')
            if not isinstance(ref, str) or not ref:
                errors.append(f"{page['page_id']}: missing speaker_notes_ref")
                continue
            expected = extract_note(bundle, ref)
            if note_key(actual) != note_key(expected):
                errors.append(f'{svg.stem}: split notes differ from speaker_notes_ref')
    return errors


def rel_targets(package: zipfile.ZipFile, part: str) -> dict[str, tuple[str, str]]:
    folder, leaf = posixpath.split(part)
    relpath = posixpath.join(folder, '_rels', leaf + '.rels')
    if relpath not in package.namelist():
        return {}
    return {r.get('Id'): (r.get('Type', '').rsplit('/', 1)[-1],
            posixpath.normpath(posixpath.join(folder, r.get('Target', ''))).lstrip('/'))
            for r in ET.fromstring(package.read(relpath))
            if r.get('TargetMode') != 'External'}


def slide_parts(package: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(package.read('ppt/presentation.xml'))
    rels = rel_targets(package, 'ppt/presentation.xml')
    return [rels[e.get('{%s}id' % NS['r'])][1] for e in root.findall('p:sldIdLst/p:sldId', NS)]


def text_shapes(root: ET.Element, scale: tuple[float, float] = (1, 1)) -> list[dict]:
    """Read native text frames, including nested group transforms, in SVG pixels."""
    output = []

    def walk(parent, sx=1., sy=1., tx=0., ty=0.):
        for child in parent:
            tag = child.tag.rsplit('}', 1)[-1]
            if tag == 'grpSp':
                xf = child.find('p:grpSpPr/a:xfrm', NS)
                if xf is None:
                    walk(child, sx, sy, tx, ty)
                    continue
                off, ext = xf.find('a:off', NS), xf.find('a:ext', NS)
                co, ce = xf.find('a:chOff', NS), xf.find('a:chExt', NS)
                ax = int(ext.get('cx')) / max(1, int(ce.get('cx')))
                ay = int(ext.get('cy')) / max(1, int(ce.get('cy')))
                walk(child, sx*ax, sy*ay,
                     tx+sx*(int(off.get('x'))-ax*int(co.get('x'))),
                     ty+sy*(int(off.get('y'))-ay*int(co.get('y'))))
            elif tag == 'sp':
                body = child.find('p:txBody', NS)
                xf = child.find('p:spPr/a:xfrm', NS)
                if body is None or xf is None:
                    continue
                off, ext = xf.find('a:off', NS), xf.find('a:ext', NS)
                runs = body.findall('.//a:r', NS)
                output.append({'text': ''.join(body.itertext()) if not runs else
                    ''.join(r.findtext('a:t', '', NS) for r in runs),
                    'bounds': [(tx+sx*int(off.get('x')))/9525/scale[0],
                               (ty+sy*int(off.get('y')))/9525/scale[1],
                               sx*int(ext.get('cx'))/9525/scale[0],
                               sy*int(ext.get('cy'))/9525/scale[1]],
                    'name': child.find('p:nvSpPr/p:cNvPr', NS).get('name'),
                    'styles': [ET.tostring(r.find('a:rPr', NS), encoding='unicode')
                               for r in runs if r.find('a:rPr', NS) is not None]})
            else:
                walk(child, sx, sy, tx, ty)
    walk(root)
    return output


def check_pptx_notes(project: Path, pptx: Path, svgs: list[Path], notes: dict[str, str]) -> list[str]:
    errors = check_split_notes(project, svgs, notes)
    required = bool(notes) or find_bundle(project) is not None
    with zipfile.ZipFile(pptx) as z:
        parts = slide_parts(z)
        if len(parts) != len(svgs):
            errors.append('PPTX/SVG count mismatch')
        seen = set()
        for i, part in enumerate(parts):
            targets = [v[1] for v in rel_targets(z, part).values() if v[0] == 'notesSlide']
            if len(targets) != 1 or targets[0] not in z.namelist():
                if required:
                    errors.append(f'slide {i+1}: missing/unresolved notesSlide relationship')
                continue
            if targets[0] in seen:
                errors.append(f'slide {i+1}: shared notesSlide is invalid')
            seen.add(targets[0])
            root = ET.fromstring(z.read(targets[0]))
            texts = []
            for sp in root.findall('.//p:sp', NS):
                ph = sp.find('p:nvSpPr/p:nvPr/p:ph', NS)
                if ph is not None and ph.get('type') == 'body':
                    texts.extend(t.text or '' for t in sp.findall('.//a:t', NS))
            expected = notes.get(svgs[i].stem, '') if i < len(svgs) else ''
            if note_key(''.join(texts)) != note_key(expected):
                errors.append(f'slide {i+1}: embedded notes differ from source/split notes')
    return errors
