#!/usr/bin/env python3
"""Preflight or render an actual PPTX; retain every attempt and its diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import shlex
import shutil
import subprocess
import sys
import traceback
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def resolve_soffice(value):
    if value:
        found = shutil.which(value)
        candidate = Path(found or value).expanduser()
        return str(candidate.resolve())
    found = shutil.which('soffice')
    if found:
        return str(Path(found).resolve())
    mac_app = Path('/Applications/LibreOffice.app/Contents/MacOS/soffice')
    return str(mac_app) if mac_app.is_file() else None


def pptx_page_count(pptx):
    with zipfile.ZipFile(pptx) as archive:
        root = ET.fromstring(archive.read('ppt/presentation.xml'))
    count = len(root.findall('{http://schemas.openxmlformats.org/presentationml/2006/main}sldIdLst/'
                             '{http://schemas.openxmlformats.org/presentationml/2006/main}sldId'))
    if not count:
        raise ValueError('PPTX has no slides')
    return count


def preflight(args, out):
    """Check the exact interpreter and renderer used by this invocation."""
    report = {'status': 'checking', 'python': sys.executable, 'python_version': sys.version,
              'skill_dir': str(Path(__file__).resolve().parents[1]), 'cwd': str(Path.cwd()),
              'out': str(out), 'invocation': shlex.join([sys.executable, *sys.argv]),
              'errors': [], 'fontconfig': None}
    module = None
    try:
        module = importlib.import_module('fitz')
        if not callable(getattr(module, 'open', None)) or not hasattr(module, 'TOOLS'):
            raise ImportError('fitz is not PyMuPDF; a different package may use this name')
        report['pymupdf_version'] = str(getattr(module, 'VersionBind', 'unknown'))
    except Exception:
        report['errors'].append({'check': 'pymupdf', 'detail': traceback.format_exc(),
                                 'remedy': shlex.join([sys.executable, '-m', 'pip', 'install', 'PyMuPDF>=1.23.0'])})
    soffice = resolve_soffice(args.soffice)
    report['soffice'] = soffice
    try:
        if not soffice or not Path(soffice).is_file() or not os.access(soffice, os.X_OK):
            raise FileNotFoundError(f'LibreOffice executable unavailable: {soffice}')
        probe = subprocess.run([soffice, '--version'], capture_output=True, text=True, timeout=15)
        report['soffice_probe'] = {'command': [soffice, '--version'], 'returncode': probe.returncode,
                                    'stdout': probe.stdout, 'stderr': probe.stderr}
        if probe.returncode:
            raise RuntimeError(f'LibreOffice version probe exited {probe.returncode}')
        if 'LibreOffice' not in probe.stdout + probe.stderr:
            raise RuntimeError('Executable did not identify itself as LibreOffice')
    except Exception:
        report['errors'].append({'check': 'soffice', 'detail': traceback.format_exc()})
    if args.pptx:
        try:
            pptx = args.pptx.expanduser().resolve()
            report['pptx'] = str(pptx)
            report['expected_pages'] = pptx_page_count(pptx)
            report['pptx_sha256'] = sha(pptx)
        except Exception:
            report['errors'].append({'check': 'pptx', 'detail': traceback.format_exc()})
    if args.fontconfig:
        try:
            config = args.fontconfig.expanduser().resolve()
            if ET.parse(config).getroot().tag != 'fontconfig':
                raise ValueError('Expected a fontconfig XML root')
            report['fontconfig'] = str(config)
            report['fontconfig_sha256'] = sha(config)
        except Exception:
            report['errors'].append({'check': 'fontconfig', 'detail': traceback.format_exc()})
    # Output directory was exclusively created by main; exercise actual content I/O.
    try:
        probe_path = out / '.write-probe'
        probe_path.write_bytes(b'render-preflight')
        if probe_path.read_bytes() != b'render-preflight':
            raise OSError('output readback mismatch')
        probe_path.unlink()
    except Exception:
        report['errors'].append({'check': 'output', 'detail': traceback.format_exc()})
    report['status'] = 'preflight_failed' if report['errors'] else 'preflight_passed'
    write_json(out / 'runtime.json', report)
    if report['errors']:
        raise RuntimeError('\n'.join(f"{e['check']}: {e['detail']}"
                                     + (f"\nUse this interpreter: {e['remedy']}" if e.get('remedy') else '')
                                     for e in report['errors']))
    return report, module


def log_text(value):
    return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')


def render(args, out, runtime, fitz):
    pptx = Path(runtime['pptx'])
    command = [runtime['soffice'], '-env:UserInstallation=' + (out / 'lo-profile').as_uri(),
               '--headless', '--convert-to', 'pdf', '--outdir', str(out), str(pptx)]
    env = os.environ.copy()
    if args.fontconfig:
        source = Path(runtime['fontconfig'])
        # Keep an unchanged snapshot. Use the original absolute path so relative
        # includes in a user-supplied fontconfig retain their original meaning.
        shutil.copyfile(source, out / 'fonts.conf')
        env['FONTCONFIG_FILE'] = str(source)
    record = {'renderer': 'LibreOffice', 'pptx': str(pptx),
              'pptx_sha256': runtime['pptx_sha256'], 'command': command,
              'fontconfig_sha256': runtime.get('fontconfig_sha256'),
              'python': runtime['python'], 'expected_pages': runtime['expected_pages'],
              'status': 'rendering', 'warnings': [], 'pages': []}
    write_json(out / 'command.json', record)
    try:
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired as error:
        (out / 'renderer.log').write_text(log_text(error.stdout) + '\n' + log_text(error.stderr), encoding='utf-8')
        raise
    (out / 'renderer.log').write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'LibreOffice exited {result.returncode}; see renderer.log')
    if result.stderr.strip():
        record['warnings'].append({'source': 'libreoffice', 'message': result.stderr.strip()})
    if args.fontconfig and sha(Path(runtime['fontconfig'])) != runtime['fontconfig_sha256']:
        raise RuntimeError('fontconfig changed during rendering; repeat with a stable configuration')
    pdf = out / (pptx.stem + '.pdf')
    if not pdf.is_file() or pdf.stat().st_size == 0:
        raise RuntimeError('LibreOffice returned success but produced no non-empty PDF')
    pdf_hash = sha(pdf)
    fitz.TOOLS.mupdf_warnings(reset=True)
    try:
        with fitz.open(pdf) as document:
            if len(document) != runtime['expected_pages']:
                raise RuntimeError(f"PDF page count mismatch: {len(document)} != {runtime['expected_pages']}")
            for i, page in enumerate(document, 1):
                image = out / f'P{i:03}.png'
                scale = 1280 / page.rect.width
                page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).save(image)
                errors = []
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines', []):
                        for span in line['spans']:
                            x0, y0, x1, y1 = span['bbox']
                            if x0 < -1 or y0 < -1 or x1 > page.rect.width + 1 or y1 > page.rect.height + 1:
                                errors.append('rendered text outside page: ' + span['text'])
                            if '\ufffd' in span['text']:
                                errors.append('replacement glyph: ' + span['text'])
                text = out / f'P{i:03}.txt'
                text.write_text(page.get_text(), encoding='utf-8')
                record['pages'].append({'sequence': i, 'image': image.name, 'image_sha256': sha(image),
                                        'pdf': pdf.name, 'pdf_sha256': pdf_hash,
                                        'text': text.name, 'text_sha256': sha(text), 'errors': errors})
    finally:
        warnings = fitz.TOOLS.mupdf_warnings(reset=True)
        if warnings:
            record['warnings'].append({'source': 'pymupdf', 'message': warnings})
        write_json(out / 'diagnostics.json', {'warnings': record['warnings'], 'visual_review': 'pending'})
    if sha(pptx) != runtime['pptx_sha256']:
        raise RuntimeError('PPTX changed during rendering; repeat with a stable input')
    record['status'] = 'rendered_requires_review'
    if any(page['errors'] for page in record['pages']):
        record['status'] = 'rendered_with_errors'
    write_json(out / 'manifest.json', record)
    if record['status'] == 'rendered_with_errors':
        raise RuntimeError('Rendered text checks failed; see manifest.json')
    print(f"Rendered {len(record['pages'])} actual PPTX pages: {out}/manifest.json; "
          f"warnings={len(record['warnings'])}; visual review required")


def positive_timeout(value):
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError('timeout must be finite and positive')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pptx', type=Path, nargs='?')
    parser.add_argument('--out', type=Path, required=True, help='New attempt directory; never overwrite')
    parser.add_argument('--check', action='store_true', help='Preflight only; PPTX is optional')
    parser.add_argument('--soffice', help='LibreOffice executable; otherwise discover on PATH/macOS')
    parser.add_argument('--fontconfig', type=Path, help='Verified fontconfig; preserve explicit mappings')
    parser.add_argument('--timeout', type=positive_timeout, default=120, help='Conversion timeout in seconds')
    args = parser.parse_args(argv)
    if not args.check and not args.pptx:
        parser.error('pptx is required unless --check is used')
    out = args.out.expanduser().absolute()
    # Do not resolve the last path component: an existing symlink is also occupied.
    try:
        out.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        print(f'ERROR: cannot create new attempt directory {out}: {error}', file=sys.stderr)
        return 1
    out = out.resolve()
    phase = 'preflight'
    try:
        runtime, fitz = preflight(args, out)
        if args.check:
            print(f'Preflight passed: {out}/runtime.json; python={sys.executable}')
            return 0
        phase = 'render'
        render(args, out, runtime, fitz)
        return 0
    except Exception as error:
        failure = traceback.format_exc()
        (out / 'failure.txt').write_text(failure, encoding='utf-8')
        write_json(out / 'failure.json', {'phase': phase, 'type': type(error).__name__,
                                         'message': str(error), 'python': sys.executable})
        print(f'ERROR [{phase}]: {error}\nEvidence: {out}/failure.txt', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
