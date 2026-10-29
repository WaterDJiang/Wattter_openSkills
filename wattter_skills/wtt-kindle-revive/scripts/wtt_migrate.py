"""Transactional internal-runtime migration. Private plan, exact hashes, explicit hardware gate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import uuid
from wtt_kindle import WttError, digest, inventory, load_json, private_dir, relative_file, timestamp, write_json, PACKAGE_ROOT
from wtt_install import assert_backup, identity, target, appledouble
import wtt_bootstrap as boot
import wtt_koreader as ki
import wtt_ui as ui
from wtt_layout import RUNTIME, EXTENSION, EVIDENCE, LAYOUT, relocate, adapt
RECEIPT='WTT/Integration/runtime-migration.json'
SOURCES=('koreader','extensions/koreader','winterbreak2','WTT/bootstrap')
CHECKS={'local_read_turn_font_return_exit_resume','weread_existing_login_body_turn','existing_notes_bookmarks_progress'}

def sha(data):return hashlib.sha256(data).hexdigest()
def hashes(root):
    rows,issues=inventory(root)
    if issues:raise WttError('迁移树不可读或含链接')
    return {n:digest(relative_file(root,n)) for n in rows if not appledouble(relative_file(root,n))}
def exact_files(device,prefixes):
    result={}
    for prefix in prefixes:
        p=relative_file(device,prefix)
        if p.exists():result.update({prefix+'/'+n:h for n,h in hashes(p).items()})
    return result

def sqlite_paths(data,old=b'/mnt/us/koreader',new=None):
    """SQLite values are updated through SQLite, never by byte-offset replacement."""
    if old not in data:return data
    new=new or ('/mnt/us/'+RUNTIME).encode()
    import tempfile
    with tempfile.TemporaryDirectory(prefix='wtt-rm-sql-') as t:
        p=Path(t)/'cache.sqlite3';p.write_bytes(data)
        with sqlite3.connect(p) as db:
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise WttError('迁移SQLite完整性失败')
            quote=lambda n:'"'+n.replace('"','""')+'"'
            tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
            for table in tables:
                for col in db.execute('PRAGMA table_info('+quote(table)+')').fetchall():
                    c=quote(col[1]);q=quote(table)
                    db.execute(f'UPDATE {q} SET {c}=replace({c},?,?) WHERE typeof({c})=\'text\' AND instr({c},?)>0',(old.decode(),new.decode(),old.decode()))
            db.commit()
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise WttError('迁移SQLite结果失败')
        return p.read_bytes()

def transformed(name,data):
    if data.startswith(b'SQLite format 3\0'):return sqlite_paths(data)
    # Do not rewrite binaries: compiled SSH paths are bypassed by an explicit exec-channel SFTP adapter.
    if data.startswith(b'\x7fELF'):return data
    return adapt(name,data).replace(b'/mnt/us/libkh/bin',b'/mnt/us/WTT/Runtime/Platform/libkh/bin')

def context(device,state,require_mount=True):
    device,session=boot.require_execution(Path(device),Path(state),require_mount=require_mount)
    return device,private_dir(state),session

def read_plan(state):
    marker=load_json(Path(state)/'runtime-migration.json');tid=marker['transaction_id']
    if not re.fullmatch('[0-9a-f]{32}',tid):raise WttError('迁移编号无效')
    folder=relative_file(Path(state),'migration-'+tid);p=load_json(folder/'plan.json')
    if digest(folder/'plan.json')!=marker['plan_sha256']:raise WttError('迁移计划发生变化')
    for n,h in p['new_files'].items():
        if digest(relative_file(folder/'payload',n))!=h:raise WttError('迁移载荷变化')
    return p,folder,marker

def write_status(device,state,marker,status):
    receipt=relative_file(device,RECEIPT)
    if receipt.exists():
        prior=load_json(receipt)
        if any(prior.get(k)!=marker.get(k) for k in ('transaction_id','plan_sha256')):raise WttError('设备有其它迁移所有权，停止')
    marker={**marker,'status':status,'at':timestamp()}
    write_json(relative_file(device,RECEIPT),marker);write_json(Path(state)/'runtime-migration.json',marker)
    return marker

def validate_identity(device,p,session):
    if identity(device)!=p['device_id'] or session['serial_sha256']!=p['serial_sha256']:raise WttError('迁移身份不匹配')
def old_unchanged(device,p,allow_missing=False):
    actual=exact_files(device,SOURCES)
    if any(p['old_files'].get(n)!=h for n,h in actual.items()):raise WttError('旧树出现未知/变化文件，停止迁移或清理')
    if not allow_missing and actual!=p['old_files']:raise WttError('旧树文件缺失，先检查')
def new_unchanged(device,p,immutable_only=False):
    expected=p['immutable_files'] if immutable_only else p['new_files']
    for n,h in expected.items():
        if not relative_file(device,n).is_file() or digest(relative_file(device,n))!=h:raise WttError('新路径摘要不符，保留现场')

def plan(device,state,backup,require_mount=True,root=PACKAGE_ROOT):
    device,state,session=context(device,state,require_mount)
    if (state/'runtime-migration.json').exists():raise WttError('已有迁移事务，先inspect/resume/rollback')
    if not ki.inspect(device,require_mount).get('receipt_matches_payload') or not ui.inspect(device,require_mount).get('ok'):raise WttError('现有底座/UI不匹配，先定位')
    kd=load_json(device/ki.RECEIPT);ud=ui.read_record(device,state)
    if kd!=load_json(state/'koreader-install.json') or ki.runtime_for(kd)!='koreader':raise WttError('只迁移本电脑拥有的旧布局')
    for n in (RUNTIME,EXTENSION,EVIDENCE):
        if relative_file(device,n).exists():raise WttError('新运行目录已存在，保留检查')
    for n in ('koreader/ota/koreader.updated.tar','koreader/ota/koreader.installed.tar'):
        if relative_file(device,n).exists():raise WttError('存在未完成原生更新，先审阅')
    assert_backup(device,backup)
    tid=uuid.uuid4().hex;folder=state/('migration-'+tid);folder.mkdir(mode=0o700)
    # A verified full backup is the immutable archive, not an uninstall/reinstall.
    snapshot=Path(backup)/'data';old=exact_files(device,SOURCES);out={};derivations=[]
    for n,h in old.items():
        b=relative_file(snapshot,n).read_bytes()
        if sha(b)!=h:raise WttError('归档与源不匹配')
        if n.startswith(('koreader/','extensions/koreader/')):
            new=relocate(n);data=transformed(new,b);out[new]=data
            if data!=b:derivations.append({'source':n,'target':new,'before':h,'after':sha(data)})
        elif n in {'WTT/bootstrap/probe.meta','WTT/bootstrap/probe.json'}:out[EVIDENCE+'/'+Path(n).name]=b
    # Keep a WTT-internal copy; the platform-owned compatibility copy remains outside WTT.
    platform=exact_files(device,('libkh',))
    for n,h in platform.items():out['WTT/Runtime/Platform/'+n]=relative_file(snapshot,n).read_bytes()
    out.update(ui.payload(root))
    recovery=relative_file(snapshot,ki.LAUNCHER).read_bytes()
    recovery=recovery.replace(b'/mnt/us/koreader',('/mnt/us/'+RUNTIME).encode())
    recovery=recovery.replace(b'#!/bin/sh',('#!/bin/sh\nexport KOREADER_DIR=/mnt/us/'+RUNTIME+'\nexport KO_HOME=/mnt/us/'+RUNTIME).encode(),1)
    switches={ki.LAUNCHER:recovery,ui.LAUNCHER:ui.payload(root)[ui.LAUNCHER]}
    # The launcher is switched only in activate, never in deploy.
    out.pop(ui.LAUNCHER)
    newkd=json.loads(json.dumps(kd));newkd['files']={relocate(n):sha(out[relocate(n)]) if relocate(n) in out else sha(switches[n]) for n in kd['files']}
    newkd.update({'layout':LAYOUT,'migration_id':tid,'committed_roots':[relocate(n) for n in kd.get('committed_roots',[])]})
    newud=json.loads(json.dumps(ud));newud.update({'version':ui.VERSION,'files':{n:sha(b) for n,b in ui.payload(root).items()},'migration_id':tid,'committed_roots':[ui.PLUGIN,ui.LAUNCHER]})
    for name,d in ((ki.RECEIPT,newkd),(ui.RECEIPT,newud)):switches[name]=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
    for n,b in {**out,**{'switches/'+k:v for k,v in switches.items()}}.items():
        q=relative_file(folder/'payload',n);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);q.chmod(0o600)
    # All installed program ownership, but not mutable account/history/cache data.
    immutable={n:sha(out[n]) for n in newkd['files'] if n in out and not n.endswith('/settings.reader.lua')}
    immutable.update({n:h for n,h in newud['files'].items() if n!=ui.LAUNCHER})
    p={'schema_version':1,'transaction_id':tid,'device_id':identity(device),'serial_sha256':session['serial_sha256'],'backup':str(Path(backup).resolve()),'old_files':old,'new_files':{n:sha(b) for n,b in out.items()},'immutable_files':immutable,'switches':{n:{'old':digest(relative_file(device,n)),'new':sha(b)} for n,b in switches.items()},'platform_files':platform,'derivations':derivations,'old_backend':kd,'old_ui':ud,'checks':sorted(CHECKS),'platform_exceptions':['libkh/bin/fbink: platform-owned sh_integration ABI, not removed through USB; WTT has internal copy'],'at':timestamp()}
    write_json(folder/'plan.json',p);marker={'transaction_id':tid,'plan_sha256':digest(folder/'plan.json'),'status':'planned'};write_json(state/'runtime-migration.json',marker)
    return {'ok':True,'status':'planned','transaction_id':tid,'archive_verified':True,'source_files':len(old),'new_files':len(out),'derived_text_or_database_files':len(derivations),'device_written':False,'platform_exceptions':p['platform_exceptions']}

def deploy(device,state,require_mount=True):
    device,state,session=context(device,state,require_mount);p,folder,m=read_plan(state);validate_identity(device,p,session)
    if m['status'] not in ('planned','deploying','deployed'):raise WttError('当前迁移阶段不可deploy')
    old_unchanged(device,p)
    # Unknown content anywhere in owned new roots stops the whole operation.
    actual=exact_files(device,(RUNTIME,EXTENSION,EVIDENCE,'WTT/Runtime/Platform'))
    if any(p['new_files'].get(n)!=h for n,h in actual.items()):raise WttError('迁移目标有未知或变化文件')
    if shutil.disk_usage(device).free < sum(relative_file(folder/'payload',n).stat().st_size for n in p['new_files'] if n not in actual)+8*1024*1024:raise WttError('迁移空间不足')
    m=write_status(device,state,m,'deploying')
    for n,h in p['new_files'].items():
        q=relative_file(device,n)
        if q.exists():continue
        q.parent.mkdir(parents=True,exist_ok=True);b=relative_file(folder/'payload',n).read_bytes()
        with q.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
        q.chmod(0o755 if b.startswith((b'#!',b'\x7fELF')) else 0o644)
        if digest(q)!=h:raise WttError('迁移写入读回失败')
    new_unchanged(device,p);write_status(device,state,m,'deployed')
    return {'ok':True,'status':'deployed','files_verified':len(p['new_files']),'old_tree_retained':True,'entry_switched':False}

def activate(device,state,require_mount=True):
    device,state,session=context(device,state,require_mount);p,folder,m=read_plan(state);validate_identity(device,p,session)
    if m['status'] not in ('deployed','activating','awaiting_hardware'):raise WttError('先完成新树部署')
    if m['status']=='awaiting_hardware':return {'ok':True,'status':'awaiting_hardware','device_written':False}
    old_unchanged(device,p);new_unchanged(device,p)
    for n,h in p['switches'].items():
        if digest(relative_file(device,n)) not in (h['old'],h['new']):raise WttError('拥有的启动/收据已变化')
        if digest(relative_file(folder/'payload','switches/'+n))!=h['new']:raise WttError('切换载荷变化')
    write_status(device,state,m,'activating')
    for n,h in p['switches'].items():
        q=relative_file(device,n);b=relative_file(folder/'payload','switches/'+n).read_bytes();tmp=q.with_name(q.name+'.wtt-rm-'+p['transaction_id'])
        if tmp.exists() and digest(tmp)!=h['new']:raise WttError('切换临时文件冲突')
        tmp.write_bytes(b);os.replace(tmp,q)
        if digest(q)!=h['new']:raise WttError('切换读回失败')
    write_json(state/'koreader-install.json',load_json(device/ki.RECEIPT));write_json(state/'wtt-ui-install.json',load_json(device/ui.RECEIPT))
    write_json(state/'ssh-runtime-layout.json',{'runtime_root':RUNTIME,'sftp':'exec_channel','migration_id':p['transaction_id']})
    write_status(device,state,m,'awaiting_hardware')
    return {'ok':True,'status':'awaiting_hardware','old_tree_retained':True,'account_or_ssh_reset':False,'reader_started':False}

def record_validation(state,checks):
    p,folder,m=read_plan(state)
    if m['status']!='awaiting_hardware' or set(checks)!=CHECKS:raise WttError('必须本次真机全部验收后记录，不能由文件送达代替')
    write_json(folder/'validation.json',{'transaction_id':p['transaction_id'],'plan_sha256':m['plan_sha256'],'checks':sorted(CHECKS),'source':'explicit_user_hardware_feedback','at':timestamp()})
    return {'ok':True,'status':'user_validation_recorded','device_written':False}

def remove_exact(device,files):
    # Check every file before the first deletion. Missing owned files are resumable.
    for n,h in files.items():
        q=relative_file(device,n)
        if q.exists() and (not q.is_file() or digest(q)!=h):raise WttError('精确清理文件变化')
    # Metadata companions are removed first; the OS may delete them with the main file.
    for n in sorted(files,key=lambda n:(not Path(n).name.startswith('._'),n)):
        relative_file(device,n).unlink(missing_ok=True)

def finalize(device,state,require_mount=True):
    device,state,session=context(device,state,require_mount);p,folder,m=read_plan(state);validate_identity(device,p,session)
    if m['status']=='finalized':return {'ok':True,'status':'finalized','device_written':False}
    if m['status'] not in ('awaiting_hardware','cleaning'):raise WttError('当前阶段不可清理')
    v=load_json(folder/'validation.json')
    if v.get('transaction_id')!=p['transaction_id'] or v.get('plan_sha256')!=m['plan_sha256'] or set(v.get('checks',[]))!=CHECKS:raise WttError('缺少绑定本次事务的用户真机验收')
    old_unchanged(device,p,allow_missing=m['status']=='cleaning');new_unchanged(device,p,True)
    if not ki.inspect(device,require_mount)['ok'] or not ui.inspect(device,require_mount)['ok']:raise WttError('新底座/UI变更，暂不删旧树')
    cleanup=folder/'cleanup.json'
    if cleanup.exists():
        removals=load_json(cleanup)['files']
    else:
        removals={**p['old_files']}
        for prefix in SOURCES:
            q=relative_file(device,prefix)
            if q.exists():
                rows,issues=inventory(q)
                if issues:raise WttError('旧目录不可读')
                for n in rows:
                    f=relative_file(q,n)
                    if appledouble(f):removals[prefix+'/'+n]=digest(f)
            meta=q.with_name('._'+q.name)
            if meta.exists():
                if not appledouble(meta):raise WttError('未知卷根伴随文件')
                removals[str(meta.relative_to(device))]=digest(meta)
        # Archive every exact cleanup byte, including metadata generated after the full backup.
        for n,h in removals.items():
            b=relative_file(device,n).read_bytes()
            if sha(b)!=h:raise WttError('清理归档期间源变化')
            q=relative_file(folder/'cleanup-archive',n);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
        write_json(cleanup,{'transaction_id':p['transaction_id'],'files':removals})
    for n,h in removals.items():
        if digest(relative_file(folder/'cleanup-archive',n))!=h:raise WttError('清理归档变化，不能删除')
    write_status(device,state,m,'cleaning');remove_exact(device,removals)
    for prefix in SOURCES:
        q=relative_file(device,prefix)
        if q.is_dir():
            for d in sorted([d for d in q.rglob('*') if d.is_dir()],key=lambda x:len(x.parts),reverse=True):d.rmdir()
            q.rmdir()
    extensions=relative_file(device,'extensions')
    if extensions.is_dir() and not any(extensions.iterdir()):extensions.rmdir()
    boot.require_execution(device,state,require_mount=require_mount)
    write_status(device,state,m,'finalized')
    return {'ok':True,'status':'finalized','old_koreader_root_removed':not (device/'koreader').exists(),'removed_files':len(removals),'platform_exceptions':p['platform_exceptions']}

def rollback(device,state,require_mount=True):
    """Restore old layout while carrying forward current state; never use stale login/history."""
    device,state,session=context(device,state,require_mount);p,folder,m=read_plan(state);validate_identity(device,p,session)
    if m['status']=='rolled_back':return {'ok':True,'status':'rolled_back','device_written':False}
    if m['status'] not in ('deploying','deployed','activating','awaiting_hardware','finalized'):raise WttError('中断清理/回滚先核对事务，不自动扩大恢复')
    if m['status'] in ('deploying','deployed'):
        old_unchanged(device,p)
        actual=exact_files(device,(RUNTIME,EXTENSION,EVIDENCE,'WTT/Runtime/Platform'))
        if any(p['new_files'].get(n)!=h for n,h in actual.items()):raise WttError('部分部署出现未知内容，停止回滚')
        remove_exact(device,actual)
        for prefix in (RUNTIME,EXTENSION,EVIDENCE,'WTT/Runtime/Platform'):
            q=relative_file(device,prefix)
            if q.exists():
                for d in sorted([d for d in q.rglob('*') if d.is_dir()],key=lambda x:len(x.parts),reverse=True):d.rmdir()
                q.rmdir()
        write_status(device,state,m,'rolled_back')
        return {'ok':True,'status':'rolled_back','old_tree_untouched':True}
    new_unchanged(device,p,True);old_unchanged(device,p,allow_missing=m['status']=='finalized')
    for n,h in p['switches'].items():
        q=relative_file(device,n)
        if q.exists() and digest(q) not in (h['old'],h['new']):raise WttError('回滚入口/收据有未知修改')
    live=folder/'rollback-live'
    if live.exists():raise WttError('已有回滚现场归档，先核对，不覆盖')
    live.mkdir(mode=0o700);stage={}
    for old,new in zip(('koreader','extensions/koreader'),(RUNTIME,EXTENSION)):
        for n,h in hashes(relative_file(device,new)).items():
            data=relative_file(device,new+'/'+n).read_bytes();q=relative_file(live,new+'/'+n);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
            if data.startswith(b'SQLite format 3\0'):data=sqlite_paths(data,('/mnt/us/'+RUNTIME).encode(),b'/mnt/us/koreader')
            elif not data.startswith(b'\x7fELF'):
                try:data.decode('utf-8');data=data.replace(('/mnt/us/'+RUNTIME).encode(),b'/mnt/us/koreader')
                except UnicodeDecodeError:pass
            stage[old+'/'+n]=data
    original=Path(p['backup'])/'data'
    # Restore only original program files. Every other current file is user state.
    program={**p['old_backend']['files'],**p['old_ui']['files']}
    for n,h in program.items():
        if n.startswith(('koreader/','extensions/koreader/')):
            if n=='koreader/settings.reader.lua':continue
            b=relative_file(original,n).read_bytes()
            if sha(b)!=h:raise WttError('恢复程序原始归档变化')
            stage[n]=b
    for n,b in stage.items():
        q=relative_file(folder/'rollback-stage',n);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
        if digest(q)!=sha(b):raise WttError('恢复暂存失败')
    # Before destructive old-tree replacement, every remaining old file must still match.
    old_unchanged(device,p,allow_missing=m['status']=='finalized')
    for prefix in ('koreader','extensions/koreader'):
        q=relative_file(device,prefix)
        if q.exists():
            # Preserve old tree inside private recovery rather than deleting it here.
            retained=relative_file(device,'WTT/Integration/rollback-retained-'+p['transaction_id']+'/'+prefix)
            retained.parent.mkdir(parents=True,exist_ok=True);q.rename(retained)
        for n,b in stage.items():
            if n.startswith(prefix+'/'):
                q=relative_file(device,n);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
    for prefix in ('winterbreak2','WTT/bootstrap'):
        for n,h in p['old_files'].items():
            if n.startswith(prefix+'/'):
                q=relative_file(device,n)
                if not q.exists():q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(relative_file(original,n),q)
    for n,h in p['switches'].items():
        q=relative_file(device,n)
        if q.exists() and digest(q) not in (h['old'],h['new']):raise WttError('回滚入口/收据有未知修改')
        shutil.copyfile(relative_file(original,n),q)
    write_json(state/'koreader-install.json',p['old_backend']);write_json(state/'wtt-ui-install.json',p['old_ui'])
    (state/'ssh-runtime-layout.json').unlink(missing_ok=True)
    write_status(device,state,m,'rolled_back')
    return {'ok':True,'status':'rolled_back','new_state_carried_forward':True,'new_tree_retained_for_recovery':True,'account_reset':False}

def inspect(device,state,require_mount=True):
    device,state,session=context(device,state,require_mount);p,folder,m=read_plan(state);validate_identity(device,p,session)
    return {'ok':True,'status':m['status'],'transaction_id':p['transaction_id'],'old_root_present':(device/'koreader').is_dir(),'internal_root_present':(device/RUNTIME).is_dir(),'platform_exceptions':p['platform_exceptions'],'device_written':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--state-dir',type=Path,required=True);p.add_argument('command',choices=('plan','deploy','activate','inspect','record-validation','finalize','rollback'));p.add_argument('--device',type=Path);p.add_argument('--backup',type=Path);p.add_argument('--confirm-device',action='store_true');p.add_argument('--checks',nargs='+');a=p.parse_args()
    try:
        if a.command=='record-validation':r=record_validation(a.state_dir,a.checks or [])
        else:
            if a.command!='inspect' and not a.confirm_device:raise WttError('先核对设备再--confirm-device')
            r=plan(a.device,a.state_dir,a.backup) if a.command=='plan' else globals()[a.command](a.device,a.state_dir)
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0
    except (WttError,OSError,ValueError,KeyError,TypeError,sqlite3.Error) as e:
        print(json.dumps({'ok':False,'error_type':type(e).__name__,'error':str(e),'next':'保留本次迁移与备份；不重新安装/登录/越狱，先检查再按本事务恢复'},ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
