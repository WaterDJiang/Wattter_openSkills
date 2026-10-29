"""WTT orchestration over attributed upstream SSH/SFTP modules, no receiver implementation."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import venv
import traceback
from wtt_kindle import PACKAGE_ROOT,WttError,digest,load_json,private_dir,relative_file,timestamp,write_json
from wtt_layout import RUNTIME

def internal_sftp(transport):
    import paramiko
    channel=transport.open_session(timeout=6);channel.settimeout(20)
    try:
        channel.exec_command("/mnt/us/"+RUNTIME+"/sftp-server")
        return paramiko.SFTPClient(channel)
    except BaseException:
        channel.close();raise

VENDOR=PACKAGE_ROOT/'vendor/qiaomu-send2kindle'


def setup(state):
    state=private_dir(state);runtime=state/'koreader-runtime'
    if runtime.is_symlink():raise WttError('运行环境不能是链接')
    python=runtime/'bin/python3'
    if not python.exists():venv.EnvBuilder(with_pip=True).create(runtime)
    p=subprocess.run([str(python),'-m','pip','install','--disable-pip-version-check','--retries','1','--timeout','30','-r',str(PACKAGE_ROOT/'assets/ssh-runtime-lock.txt')],capture_output=True,text=True)
    (state/'ssh-runtime-setup.log').write_text(p.stdout+p.stderr)
    if p.returncode:raise WttError('隔离依赖安装失败: '+p.stderr[-700:])
    return {'ok':True,'runtime_ready':True,'device_written':False}


def modules(state):
    needed=['paramiko','keyring','filelock','psutil']
    if any(importlib.util.find_spec(n) is None for n in needed):
        runtime=state/'koreader-runtime/bin/python3'
        if runtime.is_file() and Path(sys.executable).absolute()!=runtime.absolute():os.execv(str(runtime),[str(runtime),str(Path(__file__).resolve()),*sys.argv[1:]])
        raise WttError('先运行本工具setup准备固定版本隔离依赖，不在传书时隐式安装')
    sys.path.insert(0,str(VENDOR))
    import kindle_store as ks
    import kindle_usb as ku
    import kindle_transport as kt
    # Small WTT configuration adapters. Upstream source files remain unmodified.
    kt.FOLDER='/mnt/us/WTT/Books'
    if (state/'ssh-runtime-layout.json').is_file():kt.open_sftp=internal_sftp
    else:kt.open_sftp=kt.paramiko.SFTPClient.from_transport
    class Keys(ks.SystemKeys):SERVICE='tech.wtt.kindle.ssh'
    return ks,ku,kt,ks.ConfigStore(state/'ssh'),Keys()


def pair(state,device,confirmed=False):
    if not confirmed:raise WttError('USB配对须核对设备后 --confirm-device')
    import wtt_bootstrap as boot
    import wtt_koreader as ki
    device,session=boot.require_execution(Path(device),state)
    if not ki.inspect(device)['receipt_matches_payload']:raise WttError('先核对KOReader安装收据')
    runtime=ki.inspect(device).get('runtime_root',RUNTIME)
    for rel in [runtime+'/settings/SSH/authorized_keys',runtime+'/settings.reader.lua']:relative_file(device,rel)
    ks,ku,kt,store,keys=modules(state)
    ku.RUNTIME_ROOT=runtime
    result=ku.pair(store,keys,str(device),'koreader',device_id='wtt-'+load_json(device/'WTT/device.json')['device_id'])
    settings=relative_file(device,runtime+'/settings.reader.lua');data=settings.read_text()
    line='    ["SSH_autostart"] = true,'
    if data.count(line)!=1:raise WttError('SSH设置未按固定上游接口生成，停止检查')
    ku.atomic_file(settings,data.replace(line,'    ["SSH_autostart"] = false,').encode())
    if runtime==RUNTIME:write_json(state/'ssh-runtime-layout.json',{'runtime_root':RUNTIME,'sftp':'exec_channel'})
    write_json(state/'ssh-usb-identity.json',{'device_id':load_json(device/'WTT/device.json')['device_id'],'serial_sha256':session['serial_sha256'],'at':timestamp()})
    return {**result,'command':'ssh-pair','device_written':True,'autostart':False,'next':'安全弹出，KOReader中手动开启SSH服务；首次给定屏幕IP并明确trust-new-device，成功后固定身份'}


def connect(state,host=None,trust=False):
    ks,ku,kt,store,keys=modules(state);did,device,mode,profile=kt.profile_for(store,mode='koreader')
    target={**profile,'host':host or profile.get('host')}
    with kt.session(target,kt.private_for(keys,device),trust) as (transport,sftp,fp):
        channel=transport.open_session(timeout=5);channel.settimeout(5)
        try:
            channel.exec_command('cat /proc/usid');serial=bytearray()
            while True:
                chunk=channel.recv(128)
                if not chunk:break
                serial.extend(chunk)
                if len(serial)>128:raise WttError('设备身份响应超限')
            actual=hashlib.sha256(bytes(serial).rstrip(b'\0\r\n')).hexdigest();serial.clear()
            if actual!=load_json(state/'ssh-usb-identity.json')['serial_sha256']:raise WttError('SSH设备与USB配对身份不符，未保存新信任')
        finally:channel.close()
    kt.save_profile(store,did,'koreader',{**target,'fingerprint':fp,'pending_trust':False},device['credential_id'])
    identity=load_json(state/'ssh-usb-identity.json')['device_id']
    record={'schema_version':1,'device_id':identity,'initialization_verified':False,'wifi_pairing':{'device_id':identity,'status':'paired','peer_fingerprint':fp,'transport':'ssh-sftp'}}
    write_json(state/'device.json',record)
    return {'ok':True,'command':'ssh-connect','host':target['host'],'port':target['port'],'identity_verified':True,'device_written':False,'reader_opened':False}


def remote_matches(sftp,name,size,sha):
    try:st=sftp.lstat(name)
    except OSError as e:
        if e.errno==2:return None
        raise
    import stat
    if not stat.S_ISREG(st.st_mode) or st.st_size!=size:return False
    h=hashlib.sha256()
    with sftp.open(name,'rb') as f:
        while chunk:=f.read(65536):h.update(chunk)
    return h.hexdigest()==sha


def send(state,file):
    ks,ku,kt,store,keys=modules(state)
    file=Path(file).expanduser();name=file.name
    if file.is_symlink() or not file.is_file() or file.suffix.lower() not in {'.epub','.pdf','.txt','.mobi','.azw3'} or len(name.encode())>240 or len(name)>180 or name.startswith('.') or any(ord(c)<32 or ord(c)==127 for c in name):raise WttError('选择普通无DRM书籍文件及安全叶文件名')
    before=file.stat();sha=digest(file);size=before.st_size
    if not 0<size<=512*1024*1024:raise WttError('书籍为空或超过512MiB')
    did,device,mode,profile=kt.profile_for(store,mode='koreader');private=kt.private_for(keys,device)
    from filelock import FileLock
    with FileLock(str(state/'ssh-transfer.lock'),timeout=1):
        target=kt.FOLDER+'/'+name
        with kt.session(profile,private) as (_,sftp,_):prior=remote_matches(sftp,target,size,sha)
        if prior is False:raise WttError('已有同名不同内容/链接文件，不覆盖；请选择新名称')
        if prior is True:receipt={'path':target,'bytes':size,'sha256':sha};already=True
        else:
            try:receipt=kt.send_file(profile,private,str(file),name,sha);already=False
            except ks.KindleError:
                # A lost reply after rename must not create a second book.
                with kt.session(profile,private) as (_,sftp,_):done=remote_matches(sftp,target,size,sha)
                if not done:raise
                receipt={'path':target,'bytes':size,'sha256':sha};already=True
        after=file.stat()
        if file.is_symlink() or (before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns):raise WttError('源文件已变化，旧内容可能已送达；先查询原文件，不能宣称当前版本成功')
        if receipt['bytes']!=size or receipt['sha256']!=sha:raise WttError('送达收据不匹配')
        result={'ok':True,'command':'ssh-send','status':'delivered','already_delivered':already,'receipt':receipt,'book_opened':False,'device_written':not already,'at':timestamp()}
        write_json(state/'ssh-last-delivery.json',result);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--state-dir',type=Path,required=True);p.add_argument('command',choices=['setup','pair','connect','status','send','discover']);p.add_argument('--device',type=Path);p.add_argument('--confirm-device',action='store_true');p.add_argument('--host');p.add_argument('--trust-new-device',action='store_true');p.add_argument('--file',type=Path);a=p.parse_args()
    try:
        state=private_dir(a.state_dir)
        if a.command=='setup':r=setup(state)
        elif a.command=='pair':r=pair(state,a.device,a.confirm_device)
        elif a.command=='connect':r=connect(state,a.host,a.trust_new_device)
        elif a.command=='send':r=send(state,a.file)
        else:
            ks,ku,kt,store,keys=modules(state)
            r=kt.discover(store,keys,mode='koreader') if a.command=='discover' else {'ok':True,'metadata':store.load(),'credential_store':'operating-system','live_identity_verified':False}
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0
    except Exception as e:
        # Only fixed upstream/own public errors are shown; raw keychain/key parsing data stays private.
        safe=isinstance(e,WttError) or e.__class__.__name__=='KindleError'
        if 'state' in locals():write_json(state/'ssh-error.json',{'at':timestamp(),'command':a.command,'exception_type':type(e).__name__,'frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(e.__traceback__)]})
        print(json.dumps({'ok':False,'error':str(e) if safe else '本地依赖或SSH操作失败: '+type(e).__name__+'；查看私有ssh-error.json，保留现有身份','device_written':'unknown' if a.command in ['pair','send'] else False},ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
