#!/usr/bin/env python3
"""Rebuild the unchanged SHA/Base64 helper from bundled corresponding source."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def source_tree(cache):
    lock = json.loads((ROOT.parent/'assets/hash-source.json').read_text())
    archive = ROOT.parent/lock['archive']
    if sha(archive) != lock['sha256']: raise ValueError('SHA source archive checksum mismatch')
    destination = Path(cache)/('sha-source-'+lock['sha256'][:16])
    destination.mkdir(parents=True, exist_ok=True)
    expected = lock['files']
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        names = set()
        for m in members:
            rel = PurePosixPath(m.name)
            if (m.name in names or m.name not in expected or not m.isfile() or rel.is_absolute()
                    or '..' in rel.parts or '\\' in m.name): raise ValueError('Unsafe SHA source member')
            names.add(m.name)
            p = destination/m.name
            if not p.resolve().is_relative_to(destination.resolve()) or any(q.is_symlink() for q in [p,*p.parents]):
                raise ValueError('SHA source path contains a link')
        if names != set(expected): raise ValueError('Incomplete corresponding SHA source')
        for m in members:
            p = destination/m.name
            if not p.exists():
                p.parent.mkdir(parents=True, exist_ok=True)
                data = tar.extractfile(m).read()
                if hashlib.sha256(data).hexdigest() != expected[m.name]: raise ValueError('SHA source member mismatch')
                with p.open('xb') as f: f.write(data)
            if sha(p) != expected[m.name]: raise ValueError('Cached SHA source changed; preserve and inspect')
    return destination/lock['prefix'], lock


def build(output, deps, zig=None):
    output = Path(output).resolve(); output.parent.mkdir(parents=True, exist_ok=True)
    cache = Path(deps).resolve(); cache.mkdir(parents=True, exist_ok=True)
    source, lock = source_tree(cache)
    cc = [str(Path(zig).resolve()), 'cc', '-target', 'arm-linux-musleabi', '-mcpu=arm1176jzf_s', '-mfloat-abi=soft', '-static', '-s'] if zig else ['cc']
    env = dict(os.environ)
    env['ZIG_GLOBAL_CACHE_DIR'] = str(cache/'hash-zig-cache-global')
    env['ZIG_LOCAL_CACHE_DIR'] = str(cache/'hash-zig-cache-local')
    command = cc+['-std=c11','-Os','-I',str(source/'include'),str(ROOT/'hash.c'),str(source/'source/fitz/crypt-sha2.c'),'-o',str(output)]
    subprocess.run(command,env=env,check=True,capture_output=True,text=True)
    record = {'target':'kindle-armel' if zig else 'host','sha256':sha(output),'source_archive_sha256':lock['sha256'],
              'original_source_archive_sha256':lock['original_archive_sha256'],'source':'unchanged MuPDF 1.28.5 source/fitz/crypt-sha2.c','device_verified':False}
    output.with_suffix(output.suffix+'.build.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--deps-dir',required=True);p.add_argument('--zig');a=p.parse_args()
    try: print(json.dumps(build(a.output,a.deps_dir,a.zig),indent=2))
    except subprocess.CalledProcessError as exc: raise SystemExit(json.dumps({'command':exc.cmd,'exit_code':exc.returncode,'stderr':exc.stderr}))
