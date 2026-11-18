#!/usr/bin/env python3
"""Copy explicitly selected font bytes into a new directory; never copy OS metadata."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import traceback
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(fonts, out):
    # Exclusive directory creation also rejects existing symlinks. Failures remain
    # in this attempt; callers must use a new directory to retry.
    out.mkdir(parents=True, exist_ok=False)
    records = []
    try:
        for font in fonts:
            source = font.expanduser().resolve(strict=True)
            if not source.is_file() or source.suffix.lower() not in {'.ttf', '.ttc', '.otf', '.otc'}:
                raise ValueError(f'Expected a readable font file: {source}')
            digest = sha(source)
            target = out / f'{len(records) + 1:03}-{source.name}'
            shutil.copyfile(source, target)
            if sha(target) != digest or sha(source) != digest:
                raise OSError(f'Font content hash mismatch: {source}')
            records.append({'source': str(source), 'file': target.name, 'sha256': digest})
        (out / 'manifest.json').write_text(json.dumps({'fonts': records}, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        (out / 'failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fonts', type=Path, nargs='+', help='Explicit font files; no family substitution')
    parser.add_argument('--out', type=Path, required=True, help='New font directory')
    args = parser.parse_args(argv)
    out = args.out.expanduser().absolute()
    try:
        records = prepare(args.fonts, out)
    except Exception as error:
        print(f'ERROR: {error}; inspect {out} for failure evidence if created', file=sys.stderr)
        return 1
    print(f'Copied and hash-verified {len(records)} fonts: {out}/manifest.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
