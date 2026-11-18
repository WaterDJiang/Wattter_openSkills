#!/usr/bin/env python3
"""Check actual illustration pixels against a separately rendered text layer.

This is a collision/clearance gate, not semantic or thumbnail approval.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def text_regions(alpha):
    """Find line-like regions from actual alpha, including rotated lettering."""
    ink = np.asarray(alpha) > 32
    rows = np.flatnonzero(ink.any(axis=1))
    if not len(rows):
        return []
    groups = []
    start = last = int(rows[0])
    for row in rows[1:]:
        row = int(row)
        if row - last > 8:
            groups.append((start, last + 1))
            start = row
        last = row
    groups.append((start, last + 1))
    regions = []
    for y0, y1 in groups:
        xs = np.flatnonzero(ink[y0:y1].any(axis=0))
        regions.append([int(xs[0]), y0, int(xs[-1]) + 1, y1])
    return regions


def convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 2:
        return points
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for seq, target in [(points, lower), (reversed(points), upper)]:
        for pt in seq:
            while len(target) >= 2 and cross(target[-2], target[-1], pt) <= 0:
                target.pop()
            target.append(pt)
    return lower[:-1] + upper[:-1]


def clearance_polygons(ink, box, gap):
    x0, y0, x1, y1 = box
    points = []
    for y in range(y0, y1):
        xs = np.flatnonzero(ink[y, x0:x1])
        if len(xs):
            points.extend([(int(xs[0])+x0, y), (int(xs[-1])+x0, y)])
    hull = convex_hull(points)
    # Expand the actual ink hull, not its axis-aligned rectangle.
    expanded = convex_hull([(x+dx, y+dy) for x, y in hull
                            for dx, dy in [(-gap,-gap),(-gap,gap),(gap,-gap),(gap,gap)]])
    return hull, expanded


def inspect_layers(base, text_layer, min_gap=None):
    if base.size != text_layer.size:
        raise ValueError('base and text layer must have identical dimensions')
    if 'A' not in text_layer.getbands():
        raise ValueError('text layer must have a real alpha channel')
    width, height = base.size
    gap = max(1, round(min(width, height) * .02)) if min_gap is None else min_gap
    if gap < 0:
        raise ValueError('min_gap must be nonnegative')
    rgb = np.asarray(base.convert('RGB'))
    foreground = rgb.min(axis=2) < 220
    alpha = text_layer.getchannel('A')
    ink = np.asarray(alpha) > 32
    regions = text_regions(alpha)
    if not regions:
        raise ValueError('text layer contains no visible lettering')
    result = []
    for box in regions:
        x0, y0, x1, y1 = box
        expanded = [max(0, x0-gap), max(0, y0-gap),
                    min(width, x1+gap), min(height, y1+gap)]
        a, b, c, d = expanded
        overlap = int((foreground[y0:y1, x0:x1] & ink[y0:y1, x0:x1]).sum())
        hull, polygon = clearance_polygons(ink, box, gap)
        mask = Image.new('L', base.size)
        ImageDraw.Draw(mask).polygon(polygon, fill=255)
        nearby = int((foreground[b:d, a:c] & (np.asarray(mask)[b:d, a:c] > 0)).sum())
        result.append(dict(ink_box=box, ink_polygon=hull, clearance_polygon=polygon, clearance_box=expanded,
                           glyph_overlap_pixels=overlap,
                           foreground_in_clearance_pixels=nearby))
    failed = any(r['foreground_in_clearance_pixels'] for r in result)
    return dict(status='needs_revision' if failed else 'geometry_pass',
                dimensions=[width, height], min_gap_px=gap,
                foreground_threshold=220, alpha_threshold=32, regions=result,
                visual_review_required=True,
                limitations='Pixel geometry only; does not approve semantic grouping, '
                            'title completeness, figure identity or thumbnail legibility.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--text-layer', required=True, type=Path)
    parser.add_argument('--min-gap', type=int)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--overlay', type=Path,
                        help='Diagnostic copy with text/clearance boxes; never a deliverable cover.')
    args = parser.parse_args()
    with Image.open(args.base) as base, Image.open(args.text_layer) as text:
        report = inspect_layers(base, text, args.min_gap)
        report.update(base=str(args.base), text_layer=str(args.text_layer))
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2))
        if args.overlay:
            preview = Image.alpha_composite(base.convert('RGBA'), text.convert('RGBA'))
            draw = ImageDraw.Draw(preview)
            for region in report['regions']:
                color = '#d42525' if region['foreground_in_clearance_pixels'] else '#008060'
                draw.line(region['clearance_polygon']+[region['clearance_polygon'][0]], fill=color, width=3)
                draw.rectangle(region['ink_box'], outline='#d48600', width=2)
            args.overlay.parent.mkdir(parents=True, exist_ok=True)
            preview.convert('RGB').save(args.overlay)
    print(json.dumps(dict(status=report['status'], report=str(args.report),
                          min_gap_px=report['min_gap_px'])))
    return 2 if report['status'] == 'needs_revision' else 0


if __name__ == '__main__':
    raise SystemExit(main())
