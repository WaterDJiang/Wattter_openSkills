"""Pinned upstream KOReader/WeRead installation. No custom reader or network service."""
import argparse
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import uuid
import zipfile
from wtt_kindle import PACKAGE_ROOT, WttError, digest, inventory, load_json, private_dir, relative_file, timestamp, write_json
from wtt_install import appledouble, assert_backup, identity, target, tree_hashes

from wtt_layout import ROOTS, RUNTIME, EXTENSION, LEGACY_ROOTS, LAYOUT, relocate, runtime_for, adapt

def record_roots(d):
    return ROOTS if runtime_for(d)==RUNTIME else LEGACY_ROOTS
RECEIPT = 'WTT/Integration/koreader.json'
LEGACY_LAUNCHER = 'documents/KOReader-ASAP.sh'
LAUNCHER = 'WTT/Integration/recovery/KOReader-ASAP.sh'
STARTUP_SHA = '99135d6711d96ac6c0c13aabb9c80b59292bd370ff527a9920de9aa37770bb51'


def branded_startup(original, root=PACKAGE_ROOT):
    if hashlib.sha256(original).hexdigest()!=STARTUP_SHA: raise WttError('固定启动脚本摘要不符，不能派生')
    needle=b'    eips_print_bottom_centered "Starting KOReader . . ." 1'
    replacement=b'''    if [ "${WTT_READER_UI}" = "1" ]; then
        eips_print_bottom_centered "Starting WTT Reader . . ." 1
    else
        eips_print_bottom_centered "Starting KOReader . . ." 1
    fi'''
    if original.count(needle)!=1: raise WttError('启动文案位置不唯一')
    result=original.replace(needle,replacement)
    if relative_file(Path(root),'device/koreader-start-wtt.sh').read_bytes()!=result:
        raise WttError('WTT启动派生源码不是声明的最小变更')
    return result


def locked(root=PACKAGE_ROOT):
    return load_json(Path(root)/'assets/reuse-lock.json')


def fetch(state, root=PACKAGE_ROOT):
    state = private_dir(state); cache=state/'upstream'; cache.mkdir(exist_ok=True)
    rows=[]
    for component, spec in locked(root).items():
        if component == 'schema_version': continue
        file=relative_file(cache,spec['name']); expected=spec['sha256'].removeprefix('sha256:')
        if file.exists() and digest(file)!=expected: raise WttError('缓存摘要不符，保留检查: '+file.name)
        if not file.exists():
            temp=file.with_name(file.name+'.download-'+uuid.uuid4().hex)
            result=subprocess.run(['curl','--fail','--location','--proto','=https','--max-time','240','--output',str(temp),spec['url']],capture_output=True,text=True)
            if result.returncode: raise WttError('下载失败: '+file.name+' '+result.stderr[-500:])
            if temp.stat().st_size!=spec['size'] or digest(temp)!=expected: raise WttError('下载大小/摘要不匹配，未采用')
            temp.rename(file)
        rows.append({'component':component,'file':file.name,'sha256':expected})
    return {'ok':True,'command':'fetch','files':rows,'device_written':False}


def zip_payload(file, allowed):
    payload={}
    with zipfile.ZipFile(file) as z:
        infos=z.infolist()
        if len(infos)>12000 or sum(x.file_size for x in infos)>256*1024*1024: raise WttError('上游归档超限')
        seen=set()
        for item in infos:
            name=item.filename; rel=PurePosixPath(name)
            canonical=unicodedata.normalize("NFC",name.rstrip("/")).casefold()
            if (canonical in seen or rel.is_absolute() or '..' in rel.parts or '\\' in name or any(ord(c)<32 for c in name)
                    or str(rel)!=name.rstrip('/') or not any(str(rel)==a or str(rel).startswith(a+'/') for a in allowed)
                    or stat.S_ISLNK(item.external_attr>>16) or item.flag_bits&1 or item.file_size>64*1024*1024):
                raise WttError('上游归档含非法/重复/链接路径')
            seen.add(canonical)
            if not item.is_dir(): payload[name]=z.read(item)
    return payload


def payload(state, root=PACKAGE_ROOT):
    lock=locked(root); cache=Path(state)/'upstream'
    for name in ['koreader','weread','launcher']:
        p=relative_file(cache,lock[name]['name'])
        if digest(p)!=lock[name]['sha256'].removeprefix('sha256:'): raise WttError('先fetch并核验官方组件')
    files=zip_payload(cache/lock['koreader']['name'],LEGACY_ROOTS)
    if lock['koreader']['version']=='v2026.07.1':
        files['koreader/koreader.sh']=branded_startup(files['koreader/koreader.sh'],root)
    plugin=zip_payload(cache/lock['weread']['name'],('weread.koplugin',))
    for name,data in plugin.items(): files['koreader/plugins/'+name]=data
    files[LAUNCHER]=(cache/lock['launcher']['name']).read_bytes()
    files['koreader/settings.reader.lua']=b'''return {
    ["language"] = "zh_CN",
    ["home_dir"] = "/mnt/us/WTT/Books",
    ["lastdir"] = "/mnt/us/WTT/Books",
    ["start_with"] = "filemanager",
    ["SSH_port"] = "2222",
    ["SSH_allow_no_password"] = false,
    ["SSH_key_only_auth"] = true,
    ["SSH_autostart"] = false,
}
'''
    files={relocate(n):adapt(relocate(n),b) for n,b in files.items()}
    files[LAUNCHER]=files[LAUNCHER].replace(b'/mnt/us/koreader',('/mnt/us/'+RUNTIME).encode())
    return files


def inspect(device, require_mount=True):
    device,_=target(device,require_mount); receipt=relative_file(device,RECEIPT)
    if not receipt.exists():return {'ok':True,'installed':False,'device_written':False}
    d=load_json(receipt); bad=[]
    if d.get('device_id')!=identity(device):raise WttError('KOReader收据设备身份不匹配')
    for name,expected in d['files'].items():
        p=relative_file(device,name)
        if not p.is_file() or digest(p)!=expected:bad.append(name)
    # Configuration can change legitimately after first launch/pairing; report it separately.
    immutable=[x for x in bad if x!=runtime_for(d)+'/settings.reader.lua']
    return {'ok':not immutable,'installed':d['status']=='committed','receipt_matches_payload':not immutable,
            'configuration_changed':runtime_for(d)+'/settings.reader.lua' in bad,'changed_payload':immutable,
            'transaction_id':d['transaction_id'],'version':d['koreader_version'],
            'startup_branding':d.get('startup_branding'),'install_mode':d.get('install_mode','new_paths'),
            'runtime_root':runtime_for(d),'layout':d.get('layout','legacy'),'device_written':False}


def install(device,state,backup,confirmed=False,require_mount=True,identity_fn=None,root=PACKAGE_ROOT):
    if not confirmed:raise WttError('安装须核对目标设备后 --confirm-device')
    state=private_dir(state)
    import wtt_bootstrap as boot
    kwargs={'require_mount':require_mount}
    if identity_fn is not None:kwargs['identity_fn']=identity_fn
    device,session=boot.require_execution(Path(device),state,**kwargs)
    device,_=target(device,require_mount)
    existing=relative_file(device,RECEIPT)
    if existing.exists():
        result=inspect(device,require_mount)
        if result['installed'] and result['receipt_matches_payload']:return {**result,'status':'already_installed'}
        raise WttError('已有集成事务/文件变化，先inspect/rollback，不覆盖')
    assert_backup(device,backup)
    for name in [*ROOTS,*LEGACY_ROOTS,LAUNCHER]:
        p=relative_file(device,name)
        if p.exists():raise WttError('已有未知路径，保留并停止: '+name)
    files=payload(state,root); total=sum(map(len,files.values()))
    if shutil.disk_usage(device).free<total+16*1024*1024:raise WttError('设备空间不足')
    tid=uuid.uuid4().hex; stage=relative_file(device,'WTT/Integration/stage-'+tid)
    if stage.exists():raise WttError('安装暂存冲突')
    stage.mkdir(parents=True)
    record={'schema_version':1,'transaction_id':tid,'device_id':identity(device),'serial_sha256':session['serial_sha256'],
            'status':'preparing','at':timestamp(),'koreader_version':locked(root)['koreader']['version'],
            'weread_version':locked(root)['weread']['version'],'stage':str(stage.relative_to(device)),
            'files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()},'committed_roots':[]}
    record['layout']=LAYOUT
    record['startup_branding']='wtt-conditional-v1' if b'Starting WTT Reader' in files.get(RUNTIME+'/koreader.sh',b'') else None
    write_json(existing,record);write_json(state/'koreader-install.json',record)
    for name,data in files.items():
        p=relative_file(stage,name);p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        p.chmod(0o755 if data.startswith((b'\x7fELF',b'#!')) else 0o644)
        if digest(p)!=record['files'][name]:raise WttError('设备暂存读回不一致')
    if tree_hashes(stage)!=record['files']:raise WttError('暂存出现未知内容')
    record['status']='committing';write_json(existing,record)
    for name in ROOTS:
        p=relative_file(device,name);p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():raise WttError('目标提交冲突，不覆盖')
        relative_file(stage,name).rename(p);record['committed_roots'].append(name);write_json(existing,record)
    entry=relative_file(device,LAUNCHER)
    entry.parent.mkdir(parents=True,exist_ok=True)
    if entry.exists():raise WttError('启动入口提交冲突')
    relative_file(stage,LAUNCHER).rename(entry);record['committed_roots'].append(LAUNCHER)
    record['status']='committed';write_json(existing,record);write_json(state/'koreader-install.json',record)
    checked=inspect(device,require_mount)
    if not checked['receipt_matches_payload']:raise WttError('最终读回不一致，保留事务')
    return {'ok':True,'status':'installed_files','transaction_id':tid,'files':len(files),'bytes':total,
            'device_written':True,'reader_started':False,'weread_authenticated':False,'next':'同一Skill安装WTT界面后安全弹出，主页仅点WTT Reader验机；恢复入口不在主页' }


def rebuild(device,state,backup,cleanup_plan,confirmed=False,require_mount=True,root=PACKAGE_ROOT):
    """Reconstruct only removed runtime files after this PC's reviewed cleanup."""
    if not confirmed: raise WttError('重建前核对设备，再 --confirm-device')
    import wtt_bootstrap as boot
    state=private_dir(state);device,session=boot.require_execution(Path(device),state,require_mount=require_mount)
    device,_=target(device,require_mount)
    receipt=relative_file(device,RECEIPT)
    if receipt.exists():
        d=load_json(receipt);checked=inspect(device,require_mount)
        if d.get('install_mode')=='preserved_state_overlay' and checked['ok'] and checked['installed']:
            return {**checked,'status':'already_installed'}
        raise WttError('已有安装或部分事务，先inspect/rollback，不重复重建')
    plan=load_json(cleanup_plan);pid=plan.get('plan_id','')
    if not re.fullmatch('[0-9a-f]{32}',pid): raise WttError('清理计划编号无效')
    saved=load_json(state/('cleanup-'+pid)/'plan.json');result=load_json(state/('cleanup-'+pid)/'result.json')
    if saved!=plan or not result.get('ok') or result.get('planned_files')!=len(plan.get('files',[])):
        raise WttError('缺少同电脑已成功清理的冻结收据')
    if plan.get('device_id')!=identity(device) or plan.get('serial_sha256')!=session['serial_sha256']:
        raise WttError('清理收据与当前设备身份不符')
    assert_backup(device,backup)
    current_backup=load_json(Path(backup)/'manifest.json')
    old_backup=load_json(Path(plan['backup'])/'manifest.json')
    removed={r['path'] for r in plan['files']}
    retained={r['path'] for r in old_backup['files']} - removed
    in_roots=lambda n:any(n.startswith(r+'/') for r in ROOTS)
    current={r['path']:r['sha256'] for r in current_backup['files'] if in_roots(r['path'])}
    for n in current:
        if n not in retained:
            p=relative_file(device,n)
            if not appledouble(p): raise WttError('状态目录出现未登记路径，保留并停止')
    files=payload(state,root)
    # The only payload file allowed to pre-exist is the retained reader configuration.
    for n in list(files):
        p=relative_file(device,n)
        if p.exists():
            if n==RUNTIME+'/settings.reader.lua' and n in current:
                files.pop(n)
            else: raise WttError('程序目标已存在，保留并停止')
    if shutil.disk_usage(device).free<sum(map(len,files.values()))+16*1024*1024: raise WttError('设备空间不足')
    tid=uuid.uuid4().hex;stage_name='WTT/Integration/stage-'+tid;stage=relative_file(device,stage_name)
    stage.mkdir(parents=True)
    d={'schema_version':1,'transaction_id':tid,'device_id':identity(device),'serial_sha256':session['serial_sha256'],
       'status':'preparing','at':timestamp(),'koreader_version':locked(root)['koreader']['version'],
       'weread_version':locked(root)['weread']['version'],'stage':stage_name,'install_mode':'preserved_state_overlay',
       'startup_branding':'wtt-conditional-v1' if b'Starting WTT Reader' in files.get(RUNTIME+'/koreader.sh',b'') else None,
       'files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()},'preserved_paths':sorted(current),
       'cleanup_plan_id':pid,'committed_roots':[]}
    write_json(receipt,d);write_json(state/'koreader-install.json',d)
    for n,data in files.items():
        p=relative_file(stage,n);p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as f: f.write(data);f.flush();os.fsync(f.fileno())
        p.chmod(0o755 if data.startswith((b'#!',b'\x7fELF')) else 0o644)
        if digest(p)!=d['files'][n]: raise WttError('重建暂存摘要不符')
    if tree_hashes(stage)!=d['files']:raise WttError('重建暂存出现未知内容')
    d['status']='committing';write_json(receipt,d)
    for n in files:
        p=relative_file(device,n)
        if p.exists():raise WttError('重建提交冲突，保留事务')
        p.parent.mkdir(parents=True,exist_ok=True);relative_file(stage,n).rename(p)
    if any(digest(relative_file(device,n))!=h for n,h in current.items()):raise WttError('重建后保留状态校验失败')
    d['status']='committed';write_json(receipt,d);write_json(state/'koreader-install.json',d)
    if not inspect(device,require_mount)['ok']:raise WttError('重建最终读回失败')
    return {'ok':True,'status':'rebuilt_files','files':len(files),'state_files_preserved':len(current),
            'device_written':True,'reader_started':False,'account_configuration_preserved':True}


def rollback(device,state,confirmed=False,require_mount=True):
    if not confirmed:raise WttError('回滚须核对设备后 --confirm-device')
    device,_=target(device,require_mount);p=relative_file(device,RECEIPT);d=load_json(p)
    if d.get('device_id')!=identity(device):raise WttError('事务身份不匹配')
    tid=d.get('transaction_id','')
    if not isinstance(tid,str) or not re.fullmatch('[0-9a-f]{32}',tid) or d.get('stage')!='WTT/Integration/stage-'+tid:
        raise WttError('事务暂存路径无效')
    pc=load_json(private_dir(state)/'koreader-install.json')
    if any(d.get(k)!=pc.get(k) for k in ['transaction_id','device_id','serial_sha256','stage','files','install_mode','preserved_paths']):raise WttError('电脑与设备安装所有权收据不一致，不删除')
    if any(n not in {LAUNCHER,LEGACY_LAUNCHER} and not any(n.startswith(r+'/') for r in record_roots(d)) for n in d['files']):raise WttError('事务文件范围无效')
    stage=relative_file(device,d['stage'])
    if d.get('install_mode')=='preserved_state_overlay':
        # Delete owned new runtime files only; never recurse into retained state trees.
        known=set(d['files']) | set(d.get('preserved_paths',[]))
        for root in record_roots(d):
            folder=relative_file(device,root)
            if not folder.exists():continue
            names,issues=inventory(folder)
            if issues:raise WttError('重建目录存在不可读/链接内容')
            for name in names:
                n=root+'/'+name
                rt=runtime_for(d)
                state_path=n.startswith((rt+'/settings/',rt+'/cache/')) or n in {rt+'/'+x for x in ('settings.reader.lua','settings.reader.lua.old','history.lua','history.lua.old','crash.log')}
                if n not in known and not state_path and not appledouble(relative_file(device,n)):
                    raise WttError('重建目录有新增非状态文件，保留并先处理依赖组件')
        for n,h in d['files'].items():
            for base in (device,stage):
                p=relative_file(base,n)
                if p.exists() and (not p.is_file() or digest(p)!=h):raise WttError('重建文件已修改，保留并停止')
        if stage.exists():
            actual=tree_hashes(stage)
            if any(d['files'].get(n)!=h for n,h in actual.items()):raise WttError('重建暂存出现未知文件')
        for n in d['files']:
            for base in (device,stage):
                p=relative_file(base,n)
                if p.exists():p.unlink()
        d['status']='rolled_back';write_json(relative_file(device,RECEIPT),d)
        return {'ok':True,'status':'rolled_back','device_written':True,'books_preserved':True,'retained_state_preserved':True}
    roots=[*record_roots(d),*[n for n in (LAUNCHER,LEGACY_LAUNCHER) if n in d['files']]]
    # Inspect all owned destinations before deleting anything. Pairing/settings edits block rollback.
    for name in roots:
        dst=relative_file(device,name);src=relative_file(stage,name)
        for folder in [dst,src]:
            if not folder.exists():continue
            expected={n[len(name)+1:]:sha for n,sha in d['files'].items() if n.startswith(name+'/')}
            if folder.is_dir():
                if tree_hashes(folder)!=expected:raise WttError('回滚路径已修改或含未知文件，保留')
            elif folder.is_symlink() or digest(folder)!=d['files'].get(name):raise WttError('回滚文件已修改，保留')
    for name in roots:
        for folder in [relative_file(device,name),relative_file(stage,name)]:
            if folder.is_dir():shutil.rmtree(folder)
            elif folder.exists():folder.unlink()
    d['status']='rolled_back';write_json(p,d)
    return {'ok':True,'status':'rolled_back','device_written':True,'books_preserved':True}



def hide_legacy_entry(device,state,backup,confirmed=False,require_mount=True):
    """Relocate only our hash-owned launcher; a split receipt can resume safely."""
    if not confirmed: raise WttError('先核对设备，再 --confirm-device')
    import wtt_bootstrap as boot
    state=private_dir(state)
    device,_=boot.require_execution(Path(device),state,require_mount=require_mount)
    d=load_json(relative_file(device,RECEIPT));pc=load_json(state/'koreader-install.json')
    if d.get('device_id')!=identity(device) or d.get('status')!='committed':raise WttError('底座收据身份/状态不符')
    expected=d.get('files',{}).get(LEGACY_LAUNCHER) or d.get('files',{}).get(LAUNCHER)
    if not expected or not re.fullmatch('[0-9a-f]{64}',expected):raise WttError('缺少拥有的原生入口')
    # Apart from this single declared relocation, both owner records must match.
    def normalized(record):
        copy=json.loads(json.dumps(record))
        files=copy.get('files',{})
        h=files.pop(LEGACY_LAUNCHER,None) or files.get(LAUNCHER)
        if h:files[LAUNCHER]=h
        copy['committed_roots']=[LAUNCHER if n==LEGACY_LAUNCHER else n for n in copy.get('committed_roots',[])]
        return copy
    if normalized(d)!=normalized(pc):raise WttError('电脑与设备入口所有权不匹配')
    old=relative_file(device,LEGACY_LAUNCHER);new=relative_file(device,LAUNCHER)
    if new.exists() and (not new.is_file() or digest(new)!=expected):raise WttError('恢复入口冲突，保留')
    if old.exists() and (not old.is_file() or digest(old)!=expected):raise WttError('主页原生入口已变化，保留')
    if old.exists() and new.exists():raise WttError('入口源与恢复目录同时存在，先检查')
    if not old.exists() and not new.exists():raise WttError('拥有的入口丢失，先检查')
    if old.exists():
        assert_backup(device,backup)
        new.parent.mkdir(parents=True,exist_ok=True)
        old.rename(new)
    result=normalized(d)
    write_json(relative_file(device,RECEIPT),result);write_json(state/'koreader-install.json',result)
    return {'ok':True,'status':'recovery_entry_hidden','device_written':True,'backend_preserved':True,'visible_legacy_entry':False}


def main():
    p=argparse.ArgumentParser();p.add_argument('--state-dir',type=Path,required=True)
    p.add_argument('command',choices=['fetch','install','rebuild','inspect','hide-legacy-entry','rollback']);p.add_argument('--device',type=Path);p.add_argument('--backup',type=Path);p.add_argument('--cleanup-plan',type=Path);p.add_argument('--confirm-device',action='store_true');a=p.parse_args()
    try:
        if a.command=='fetch':r=fetch(a.state_dir)
        elif a.command=='install':r=install(a.device,a.state_dir,a.backup,a.confirm_device)
        elif a.command=='rebuild':r=rebuild(a.device,a.state_dir,a.backup,a.cleanup_plan,a.confirm_device)
        elif a.command=='inspect':r=inspect(a.device)
        elif a.command=='hide-legacy-entry':r=hide_legacy_entry(a.device,a.state_dir,a.backup,a.confirm_device)
        else:r=rollback(a.device,a.state_dir,a.confirm_device)
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['ok'] else 3
    except (OSError,ValueError,TypeError,KeyError,WttError,zipfile.BadZipFile) as e:
        print(json.dumps({'ok':False,'error':str(e),'device_written':'unknown' if a.command in ['install','rebuild','rollback'] else False,'next':'先检查集成收据和本次暂存，不盲目重装'},ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
