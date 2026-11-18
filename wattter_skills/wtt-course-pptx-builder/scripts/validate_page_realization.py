#!/usr/bin/env python3
"""Check source-backed teaching structures, field placement and final PPT evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from course_delivery import NS, load_pages, slide_parts, text_shapes, check_pptx_notes
from validate_content_fidelity import visible_leaf_paths, output_pages
from validate_pptx_editability import analyze_pptx
from svg_to_pptx.pptx_discovery import find_notes_files


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(text: str) -> str:
    # Preserve punctuation, scores and Latin word boundaries except layout whitespace.
    return re.sub(r'\s+', '', text)


def inside(inner, outer, tolerance=3):
    x,y,w,h = inner; a,b,c,d = outer
    return x >= a-tolerance and y >= b-tolerance and x+w <= a+c+tolerance and y+h <= b+d+tolerance


def intersects(a, b):
    return min(a[0]+a[2],b[0]+b[2]) > max(a[0],b[0])+3 and min(a[1]+a[3],b[1]+b[3]) > max(a[1],b[1])+3


def value_at(page, path):
    value = page
    for token in re.findall(r'[^.\[\]]+', path):
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def relation_errors(rel, regions, shapes):
    kind = rel['kind']; ids = rel['regions']; boxes = [regions[i]['bounds'] for i in ids]
    errors = []
    if kind in {'parallel', 'sequential', 'neutral_compare'}:
        if len(boxes) < 2 or any(intersects(a,b) for i,a in enumerate(boxes) for b in boxes[i+1:]):
            errors.append(f'{kind}: regions must be distinct and non-overlapping')
        horizontal = max(b[1] for b in boxes)-min(b[1] for b in boxes) < 8
        vertical = max(b[0] for b in boxes)-min(b[0] for b in boxes) < 8
        if not (horizontal or vertical):
            errors.append(f'{kind}: regions must share a reading axis')
        if kind == 'sequential':
            coords = [b[0] if horizontal else b[1] for b in boxes]
            if coords != sorted(coords):
                errors.append('sequential: source order differs from reading order')
    elif kind in {'main_sidebar', 'branch'}:
        if len(boxes) != 2 or intersects(*boxes):
            errors.append(f'{kind}: main and independent side region required')
        elif kind == 'main_sidebar' and boxes[0][2]*boxes[0][3] <= boxes[1][2]*boxes[1][3]:
            errors.append('main_sidebar: document must be the main display area')
    elif kind in {'paired_rows', 'rubric'}:
        columns = rel.get('columns', 2 if kind == 'paired_rows' else 3)
        if len(boxes) % columns or len(boxes) < columns:
            errors.append(f'{kind}: incomplete rows')
        else:
            for start in range(0,len(boxes),columns):
                row = boxes[start:start+columns]
                if max(b[1] for b in row)-min(b[1] for b in row)>3 or [b[0] for b in row]!=sorted(b[0] for b in row):
                    errors.append(f'{kind}: row/column alignment lost')
            for col in range(columns):
                xs = [b[0] for b in boxes[col::columns]]
                if max(xs)-min(xs)>3:
                    errors.append(f'{kind}: column {col} drifts')
    else:
        errors.append(f'unknown relationship: {kind}')
    if kind == 'neutral_compare':
        if len(boxes) != 2 or any(abs(boxes[0][i]-boxes[1][i])>3 for i in (2,3)):
            errors.append('neutral_compare: equal area required')
        if shapes:
            signatures = []
            for box in boxes:
                styles = [s['styles'] for s in shapes if inside(s['bounds'],box)]
                # Typography/color/weight identical, independent of the actual words.
                signatures.append(sorted(set(st for group in styles for st in group)))
            if not signatures[0] or signatures[0]!=signatures[1]:
                errors.append('neutral_compare: unequal text color/weight/font/size')
    return errors


def validate(project: Path, pptx: Path | None = None, delivery=False) -> dict:
    errors=[]; evidence=[]
    bundle,pages = load_pages(project)
    if bundle is None:
        raise ValueError('course-handoff required for course realization gate')
    plan = json.loads((project/'page_realization.json').read_text())
    if plan.get('version') != 1:
        raise ValueError('unsupported page_realization version')
    rows = plan['pages']
    if [r['page_id'] for r in rows] != [p['page_id'] for p in pages]:
        errors.append('realization page IDs/order differ from course source')
    outputs, output_errors = output_pages(project/'svg_output'); errors += output_errors
    if len(outputs)!=len(pages): errors.append('SVG/source page count mismatch')
    package = zipfile.ZipFile(pptx) if pptx else None
    parts = slide_parts(package) if package else []
    if pptx:
        svgs = [outputs[i] for i in sorted(outputs)]
        errors += check_pptx_notes(project,pptx,svgs,find_notes_files(project,svgs))
        edit = analyze_pptx(pptx)
        errors += edit['errors']
        if edit['picture_only_pages']: errors.append('course delivery forbids every picture-only page')
        if len(parts)!=len(pages): errors.append('PPT/source page count mismatch')
    for index,(page,row) in enumerate(zip(pages,rows)):
        pid=page['page_id']; issues=[]
        if row.get('sequence')!=page['sequence']: issues.append('sequence differs from source')
        svg=outputs.get(page['sequence'])
        if svg is None: errors.append(f'{pid}: SVG missing'); continue
        root=ET.parse(svg).getroot()
        canvas=[float(v) for v in root.get('viewBox','0 0 1280 720').split()]
        source=project/row['source_template']['path']
        if not source.resolve().is_relative_to((project/'templates').resolve()):
            issues.append('source template must be a copied asset within project/templates')
        if sha(source)!=row['source_template']['sha256']: issues.append('source template hash changed')
        source_root=ET.parse(source).getroot()
        source_ids={e.get('id'):e for e in source_root.iter() if e.get('id')}
        target_ids={e.get('id'):e for e in root.iter() if e.get('id')}
        if not row.get('capacity_reason') or row.get('reuse_mode') not in {'mirror','adapt_structure','themed_rebuild'}:
            issues.append('capacity reason and actual reuse mode required')
        regions={r['id']:r for r in row['regions']}
        if len(regions)!=len(row['regions']): issues.append('duplicate region IDs')
        all_fields=dict(visible_leaf_paths(page['slide_text']))
        allocated=[]
        shapes=[]
        native_root=None
        if package and index<len(parts):
            presentation=ET.fromstring(package.read('ppt/presentation.xml'))
            sz=presentation.find('p:sldSz',NS)
            scale=(int(sz.get('cx'))/9525/canvas[2],int(sz.get('cy'))/9525/canvas[3])
            native_root=ET.fromstring(package.read(parts[index]))
            shapes=text_shapes(native_root,scale)
            for s in shapes:
                if not inside(s['bounds'],canvas): issues.append(f'PPT text frame outside canvas: {s["name"]}')
        for rid,region in regions.items():
            bounds=region['bounds']
            if len(bounds)!=4 or bounds[2]<=0 or bounds[3]<=0 or not inside(bounds,canvas):
                issues.append(f'{rid}: invalid region bounds')
            elem=target_ids.get(rid)
            if elem is None: issues.append(f'{rid}: missing actual SVG region'); continue
            svg_text=exact(''.join(t for e in elem.iter() if e.tag.rsplit('}',1)[-1]=='text' for t in e.itertext()))
            native_text=exact(''.join(s['text'] for s in shapes if inside(s['bounds'],bounds)))
            for field in region['fields']:
                allocated.append(field)
                if field not in all_fields: issues.append(f'{rid}: unknown source field {field}'); continue
                text=exact(all_fields[field])
                if text not in svg_text: issues.append(f'{rid}: SVG field missing {field}')
                if package and text not in native_text: issues.append(f'{rid}: native PPT field missing/misplaced {field}')
        if set(allocated)!=set(all_fields) or len(allocated)!=len(set(allocated)):
            issues.append('each source field must be allocated exactly once')
        features=row.get('required_features',[])
        if not features: issues.append('required template structures missing')
        for feature in features:
            if not feature.get('reason') or not feature.get('source_ids'):
                issues.append('feature must identify source structure and adaptation')
            for sid in feature['source_ids']:
                e=source_ids.get(sid)
                if e is None or not any(c.tag.rsplit('}',1)[-1] in {'rect','path','line','polygon','circle','ellipse'} for c in e.iter()):
                    issues.append(f'source feature missing/non-structural: {sid}')
            structure_ids=feature.get('output_structure_ids',[])
            if not structure_ids:
                issues.append('actual output structural objects required; source markers alone are insufficient')
            for tid in structure_ids:
                target=target_ids.get(tid)
                if target is None or not any(c.tag.rsplit('}',1)[-1] in {'rect','path','line','polygon','circle','ellipse'} for c in target.iter()):
                    issues.append(f'output structure missing/non-structural: {tid}')
                if native_root is not None:
                    group=next((g for g in native_root.findall('.//p:grpSp',NS)
                        if g.find('p:nvGrpSpPr/p:cNvPr',NS).get('name')==tid),None)
                    if group is None or not any(s.find('p:txBody',NS) is None for s in group.findall('.//p:sp',NS)):
                        issues.append(f'native structural objects missing: {tid}')
            if feature.get('require_connectors'):
                elements=[target_ids[t] for t in structure_ids if t in target_ids]
                if not any(e.tag.rsplit('}',1)[-1] in {'line','path','polyline'} for g in elements for e in g.iter()):
                    issues.append('required SVG relationship connector missing')
            issues += relation_errors(feature,regions,shapes)
        for relation in features+row.get('relationships',[]):
            if relation['kind']=='neutral_compare':
                colors=[]
                for rid in relation['regions']:
                    g=target_ids.get(rid)
                    colors.append(sorted(set(e.get('fill','') for e in g.iter()
                        if e.tag.rsplit('}',1)[-1]!='text')) if g is not None else [])
                if len(colors)!=2 or colors[0]!=colors[1]:
                    issues.append('neutral_compare: unequal region skin')
        for relation in row.get('relationships',[]):
            issues += relation_errors(relation,regions,shapes)
            if 'items_path' in relation:
                items=value_at(page,relation['items_path'])
                if not isinstance(items,list) or len(items)!=relation['count']:
                    issues.append(f'relationship/source count conflict at {relation["items_path"]}')
                divisor=relation.get('columns',3 if relation['kind']=='rubric' else 2 if relation['kind']=='paired_rows' else 1)
                if len(relation['regions']) != relation['count']*divisor:
                    issues.append('relationship count differs from actual region count')
        evidence.append({'page_id':pid,'source':str(source),'svg':str(svg),'errors':issues})
        errors += [f'{pid}: {i}' for i in issues]
    if package: package.close()
    errors += validate_anchor_lock(project)
    if delivery:
        if pptx is None: errors.append('delivery requires actual PPTX')
        else: errors += validate_render_review(project,pptx,pages,rows)
    return {'ok':not errors,'checked':len(evidence),'errors':errors,'pages':evidence}


def validate_render_review(project,pptx,pages,rows):
    errors=[]
    path=project/'render_review.json'
    if not path.exists(): return ['missing actual PPT render_review.json']
    review=json.loads(path.read_text()); manifest_path=project/review['manifest']
    manifest=json.loads(manifest_path.read_text())
    if manifest['pptx_sha256']!=sha(pptx): errors.append('PPT changed: rerender and re-review affected pages')
    if manifest.get('renderer') not in {'LibreOffice','PowerPoint','Keynote'}: errors.append('actual Office renderer required')
    if len(manifest['pages'])!=len(pages) or len(review['pages'])!=len(pages): errors.append('render/review page count mismatch')
    for i,(render,check) in enumerate(zip(manifest['pages'],review['pages'])):
        if check.get('page_id')!=pages[i]['page_id']: errors.append(f'render page {i+1}: source order differs')
        for key in ['font','wrapping','occlusion','cropping','bounds','structure']:
            if check.get(key)!='pass': errors.append(f'render page {i+1}: {key} unverified/failed')
        if not check.get('observation'): errors.append(f'render page {i+1}: actual observation required')
        for key in ['image','pdf','text']:
            file=manifest_path.parent/render[key]
            if not file.is_file() or sha(file)!=render[key+'_sha256']: errors.append(f'render page {i+1}: stale/missing {key}')
        if render.get('errors'): errors += [f'render page {i+1}: {s}' for s in render['errors']]
        text=exact((manifest_path.parent/render['text']).read_text())
        for field,value in visible_leaf_paths(pages[i]['slide_text']):
            if exact(value) not in text:
                errors.append(f'render page {i+1}: actual rendered text missing {field}')
    return errors


def validate_anchor_lock(project):
    errors=[]
    # Approval is optional until actual approval exists; absence never fabricates one.
    anchors=project/'anchors.json'
    if anchors.exists():
        lock=json.loads(anchors.read_text())
        if not lock.get('approval_ref'): errors.append('anchor freeze lacks user approval reference')
        coverage=set()
        for a in lock['pages']:
            coverage.update(a['covers'])
            for field in ['svg','image']:
                file=project/a[field]
                if sha(file)!=a[field+'_sha256']: errors.append(f'anchor changed: {a["page_id"]}/{field}')
        if not {'exercise','demo','long_compare','multi_step','rubric'}<=coverage:
            errors.append('anchors do not cover real teaching content difficulties')
    return errors


def write_usage_view(project: Path, evidence: list[dict], target: Path, delivery: bool) -> None:
    """Derive the human review view from the structure plan and actual evidence."""
    rows = json.loads((project / 'page_realization.json').read_text())['pages']
    screenshots = {}
    if delivery:
        review = json.loads((project / 'render_review.json').read_text())
        manifest_path = project / review['manifest']
        manifest = json.loads(manifest_path.read_text())
        screenshots = {check['page_id']: manifest_path.parent / page['image']
                       for check, page in zip(review['pages'], manifest['pages'])}

    def cell(value) -> str:
        return str(value).replace('|', r'\|').replace('\n', ' ').replace('\r', '')

    lines = [
        '# 逐页模板使用记录',
        '',
        '由页面结构计划和验证证据生成。',
        '',
        '| 页 ID | 源 SVG | 复用方式 | 容量与适配 | 保留结构 | 成品 SVG | Office 渲染 |',
        '|---|---|---|---|---|---|---|',
    ]
    for row, check in zip(rows, evidence):
        pid = row['page_id']
        features = '、'.join(
            f"{', '.join(feature['source_ids'])} → {', '.join(feature['output_structure_ids'])}（{feature['reason']}）"
            for feature in row['required_features']
        )
        fields = [pid, row['source_template']['path'], row['reuse_mode'],
                  row['capacity_reason'], features, check['svg'], screenshots.get(pid, '待成品复核')]
        lines.append('| ' + ' | '.join(map(cell, fields)) + ' |')
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path); parser.add_argument('--pptx',type=Path)
    parser.add_argument('--delivery',action='store_true'); parser.add_argument('--out',type=Path)
    parser.add_argument('--summary-only', action='store_true', help='Print status and errors; --out retains the full JSON report')
    parser.add_argument('--usage-md', type=Path, help='Write the derived template review after successful validation')
    args=parser.parse_args()
    try:
        result=validate(args.project,args.pptx,args.delivery)
        if result['ok'] and args.usage_md:
            write_usage_view(args.project, result['pages'], args.usage_md, args.delivery)
    except (OSError,ValueError,KeyError,TypeError,IndexError,ET.ParseError,zipfile.BadZipFile) as e:
        result={'ok':False,'errors':[str(e)]}
    if args.out:
        if args.out.exists(): parser.error('evidence path already exists; use a new attempt path')
        args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    if args.summary_only:
        status = 'PASS' if result['ok'] else 'FAIL'
        print(f"{status}: page realization checked={result.get('checked', 0)} errors={len(result['errors'])}")
        for error in result['errors']:
            print(f"  {error}")
        if args.out:
            print(f"Report: {args.out}")
    else:
        print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['ok'] else 1


if __name__=='__main__': raise SystemExit(main())
