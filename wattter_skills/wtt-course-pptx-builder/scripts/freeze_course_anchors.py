#!/usr/bin/env python3
"""Freeze approved real-content anchors; reuse a valid existing approval without rewriting it."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from validate_page_realization import sha, validate_anchor_lock, validate_render_review
from course_delivery import load_pages


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path)
    parser.add_argument('--selection',type=Path,help='JSON list of {page_id,covers}; select real content pages')
    parser.add_argument('--approval-ref',help='Actual user approval reference; never fabricate approval')
    args=parser.parse_args(); project=args.project
    try:
        lock=project/'anchors.json'
        if lock.exists():
            errors=validate_anchor_lock(project)
            if errors: raise ValueError('; '.join(errors)+'; preserve old approval and obtain approval for the affected revision')
            print('Existing anchor approval reused; hashes unchanged')
            return 0
        if not args.selection or not args.approval_ref:
            raise ValueError('new anchor freeze requires selection and actual approval-ref')
        review=json.loads((project/'render_review.json').read_text())
        manifest_path=project/review['manifest']; manifest=json.loads(manifest_path.read_text())
        _,pages=load_pages(project)
        errors=validate_render_review(project,Path(manifest['pptx']),pages,[])
        if errors: raise ValueError('; '.join(errors))
        selected=json.loads(args.selection.read_text()); entries=[]; coverage=set(); ids=set()
        from validate_content_fidelity import output_pages
        svgs,errors=output_pages(project/'svg_output')
        if errors: raise ValueError('; '.join(errors))
        for choice in selected:
            pid=choice['page_id']
            if pid in ids: raise ValueError('duplicate anchor page_id')
            ids.add(pid)
            i=next(i for i,p in enumerate(pages) if p['page_id']==pid)
            if pages[i]['page_type'] in {'cover','section_opener','ending','chapter','toc'}:
                raise ValueError(f'{pid}: structural page cannot represent teaching-content quality')
            svg=svgs[pages[i]['sequence']]; image=manifest_path.parent/manifest['pages'][i]['image']
            entries.append({'page_id':pid,'covers':choice['covers'],'svg':str(svg.relative_to(project)),
                            'svg_sha256':sha(svg),'image':str(image.relative_to(project)),
                            'image_sha256':sha(image)})
            coverage.update(choice['covers'])
        if not {'exercise','demo','long_compare','multi_step','rubric'}<=coverage:
            raise ValueError('selection must cover exercise/demo/long_compare/multi_step/rubric')
        lock.write_text(json.dumps({'version':1,'approval_ref':args.approval_ref,'pages':entries},ensure_ascii=False,indent=2))
        print(f'Frozen {len(entries)} approved real-content anchors: {lock}')
        return 0
    except (OSError,ValueError,KeyError,StopIteration) as e:
        parser.exit(1,f'ERROR: {e}\n')


if __name__=='__main__': raise SystemExit(main())
