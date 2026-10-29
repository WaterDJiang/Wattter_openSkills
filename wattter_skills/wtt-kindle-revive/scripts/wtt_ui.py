"""Install the isolated WTT UI add-on; never overwrite KOReader or legacy WTT."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

from wtt_kindle import PACKAGE_ROOT, WttError, digest, load_json, private_dir, relative_file, timestamp, write_json
from wtt_install import appledouble, assert_backup, identity, target, tree_hashes
import wtt_koreader as ki

VERSION = '0.2.4'
from wtt_layout import RUNTIME
PLUGIN = RUNTIME+'/plugins/wttui.koplugin'
LEGACY_PLUGIN = 'koreader/plugins/wttui.koplugin'
def plugin_for(d):
    return LEGACY_PLUGIN if any(n.startswith(LEGACY_PLUGIN+'/') for n in d['files']) else PLUGIN
OLD_LAUNCHER = 'documents/WTT-Reader-KO.sh'
PREVIOUS_LAUNCHER = 'documents/WTT-Reader-02.sh'
LAUNCHER = 'documents/WTT-Reader-03.sh'

def launcher_for(version):
    return OLD_LAUNCHER if version == '0.1.0' else PREVIOUS_LAUNCHER if version == '0.2.0' else LAUNCHER
ROOTS = (PLUGIN, LAUNCHER)
RECEIPT = 'WTT/Integration/wtt-ui.json'
OLD_SOURCE_FILES = ('main.lua', '_meta.lua', 'wttui/library.lua', 'LICENSE', 'ORIGIN.json')
SOURCE_FILES = (*OLD_SOURCE_FILES, 'wtt-icon.svg', 'wtt-icon.png')


def payload(root=PACKAGE_ROOT):
    folder = Path(root)/'device/wttui.koplugin'
    data = {PLUGIN+'/'+n: relative_file(folder, n).read_bytes() for n in SOURCE_FILES}
    data[LAUNCHER] = relative_file(Path(root), 'device/wttui-launcher.sh').read_bytes()
    return data


def read_record(device, state=None):
    d = load_json(relative_file(device, RECEIPT))
    tid = d.get('transaction_id', '')
    source_files = OLD_SOURCE_FILES if d.get('version') == '0.1.0' else SOURCE_FILES
    launcher = launcher_for(d.get('version'))
    expected = {plugin_for(d)+'/'+n for n in source_files} | {launcher}
    if (d.get('version') not in {'0.1.0','0.2.0','0.2.1','0.2.2','0.2.3',VERSION} or d.get('device_id') != identity(device) or not re.fullmatch('[0-9a-f]{32}', tid)
            or d.get('stage') != 'WTT/Integration/ui-stage-'+tid or set(d.get('files', {})) != expected
            or not all(re.fullmatch('[0-9a-f]{64}', v) for v in d['files'].values())):
        raise WttError('WTT界面收据身份或路径无效')
    if state is not None:
        pc = load_json(private_dir(state)/'wtt-ui-install.json')
        if any(pc.get(k) != d.get(k) for k in ('transaction_id','device_id','serial_sha256','stage','files')):
            raise WttError('电脑与设备WTT界面所有权不匹配')
    return d


def inspect(device, require_mount=True):
    device, _ = target(device, require_mount)
    if not relative_file(device, RECEIPT).exists():
        return {'ok': True, 'installed': False, 'device_written': False}
    d = read_record(device)
    bad = [n for n, h in d['files'].items() if not relative_file(device, n).is_file() or digest(relative_file(device, n)) != h]
    extra = []
    plugin_name=plugin_for(d)
    plugin = relative_file(device, plugin_name)
    if plugin.exists():
        actual = tree_hashes(plugin)
        extra = [plugin_name+'/'+n for n in actual if plugin_name+'/'+n not in d['files']]
    return {'ok': not bad and not extra and d['status'] == 'committed', 'installed': d['status'] == 'committed',
            'version': d['version'], 'changed_files': bad, 'extra_files': extra,
            'transaction_id': d['transaction_id'], 'device_written': False, 'hardware_verified': False}


def install(device, state, backup, confirmed=False, require_mount=True, root=PACKAGE_ROOT):
    if not confirmed: raise WttError('先核对设备，再 --confirm-device')
    import wtt_bootstrap as boot
    state = private_dir(state)
    device, session = boot.require_execution(Path(device), state, require_mount=require_mount)
    device, _ = target(device, require_mount)
    # This add-on is coupled to a fixed tested backend, not a universal KOReader theme.
    backend = ki.inspect(device, require_mount)
    if (not backend.get('installed') or not backend.get('receipt_matches_payload') or backend.get('version') != 'v2026.07.1'
            or backend.get('startup_branding') != 'wtt-conditional-v1'):
        raise WttError('先检查已锁定KOReader底座；不在界面安装中重装底座')
    receipt = relative_file(device, RECEIPT)
    files = payload(root)
    hashes = {n: hashlib.sha256(b).hexdigest() for n,b in files.items()}
    prior = None
    if receipt.exists():
        d = read_record(device, state)
        checked = inspect(device, require_mount)
        if checked['ok'] and d['files'] == hashes:
            return {**checked, 'status': 'already_installed'}
        if d['status'] != 'rolled_back':
            raise WttError('已有界面事务或不同版本；先检查/回滚，不覆盖')
        prior = d
    assert_backup(device, backup)
    for n in ROOTS:
        if relative_file(device, n).exists(): raise WttError('已有未知界面路径，保留: '+n)
    if shutil.disk_usage(device).free < sum(map(len, files.values())) + 1024*1024:
        raise WttError('设备空间不足')
    if prior:
        archived = relative_file(device, 'WTT/Integration/ui-rollback-'+prior['transaction_id']+'.json')
        if archived.exists(): raise WttError('旧界面事务归档冲突，保留检查')
        receipt.rename(archived)
    tid = uuid.uuid4().hex
    stage_name = 'WTT/Integration/ui-stage-'+tid
    stage = relative_file(device, stage_name)
    stage.mkdir(parents=True)
    d = {'schema_version': 1, 'device_id': identity(device), 'serial_sha256': session['serial_sha256'],
         'transaction_id': tid, 'stage': stage_name, 'version': VERSION, 'status': 'preparing',
         'at': timestamp(), 'files': hashes, 'committed_roots': []}
    write_json(receipt, d); write_json(state/'wtt-ui-install.json', d)
    for n, data in files.items():
        p = relative_file(stage, n); p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
        p.chmod(0o755 if n == LAUNCHER else 0o644)
        if digest(p) != hashes[n]: raise WttError('界面暂存读回不一致')
    if tree_hashes(stage) != hashes: raise WttError('界面暂存出现未知文件')
    d['status'] = 'committing'; write_json(receipt, d)
    for n in ROOTS:
        p = relative_file(device, n)
        if p.exists(): raise WttError('界面提交目标冲突')
        p.parent.mkdir(parents=True, exist_ok=True)
        relative_file(stage, n).rename(p)
        d['committed_roots'].append(n); write_json(receipt, d)
    d['status'] = 'committed'; write_json(receipt, d); write_json(state/'wtt-ui-install.json', d)
    checked = inspect(device, require_mount)
    if not checked['ok']: raise WttError('界面最终读回不一致，保留事务')
    return {**checked, 'status': 'installed_files', 'device_written': True, 'reader_started': False,
            'next': '安全弹出后点WTT Reader；底座保留，旧UI与多余入口按收据处理'}


def rollback(device, state, confirmed=False, require_mount=True):
    if not confirmed: raise WttError('回滚前核对设备，再 --confirm-device')
    device, _ = target(device, require_mount)
    d = read_record(device, state)
    stage = relative_file(device, d['stage'])
    roots = (plugin_for(d), launcher_for(d['version']))
    # Validate every owned root first, including partial commits; unknown changes block deletion.
    for n in roots:
        for base in (device, stage):
            p = relative_file(base, n)
            if not p.exists(): continue
            if p.is_dir():
                wanted = {k[len(n)+1:]: v for k,v in d['files'].items() if k.startswith(n+'/')}
                actual = tree_hashes(p)
                # A failed rollback may already have removed some owned files.
                matches = all(wanted.get(k) == v for k,v in actual.items())
                if not matches: raise WttError('界面目录已变化，保留并停止')
            elif digest(p) != d['files'][n]: raise WttError('界面入口已变化，保留并停止')
    # Validate metadata before removing companions: FAT/macOS may remove it
    # automatically when a companion is unlinked. Never recurse-delete unknowns.
    metadata = []
    for n in roots:
        for base in (device, stage):
            p = relative_file(base, n)
            if p.is_dir():
                metadata.extend((q, digest(q)) for q in p.rglob('*') if q.is_file() and appledouble(q))
    for p, expected in metadata:
        if p.exists() and digest(p) != expected: raise WttError('界面元数据在回滚时变化，保留')
        p.unlink(missing_ok=True)
    for n, expected in d['files'].items():
        for base in (device, stage):
            p = relative_file(base, n)
            if p.exists() and (not p.is_file() or digest(p) != expected): raise WttError('界面文件在回滚时变化，保留')
            p.unlink(missing_ok=True)
    for n in roots:
        for base in (device, stage):
            p = relative_file(base, n)
            if p.is_dir():
                for child in sorted((q for q in p.rglob('*') if q.is_dir()), key=lambda q:len(q.parts), reverse=True):
                    child.rmdir()
                p.rmdir()
    d['status'] = 'rolled_back'; write_json(relative_file(device, RECEIPT), d)
    return {'ok': True, 'status': 'rolled_back', 'device_written': True, 'koreader_preserved': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state-dir', type=Path, required=True)
    parser.add_argument('command', choices=('install','inspect','rollback'))
    parser.add_argument('--device', type=Path, required=True)
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--confirm-device', action='store_true')
    a = parser.parse_args()
    try:
        if a.command == 'inspect': r = inspect(a.device)
        elif a.command == 'install': r = install(a.device, a.state_dir, a.backup, a.confirm_device)
        else: r = rollback(a.device, a.state_dir, a.confirm_device)
        print(json.dumps(r, ensure_ascii=False, indent=2)); return 0 if r['ok'] else 3
    except (WttError, OSError, ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e), 'next': '只检查本次界面事务；不重置、不重越狱、不重装底座'}, ensure_ascii=False)); return 2


if __name__ == '__main__': sys.exit(main())
