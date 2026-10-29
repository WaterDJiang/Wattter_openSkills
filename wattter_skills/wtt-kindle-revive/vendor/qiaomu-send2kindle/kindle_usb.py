"""Physical pairing; only public identity material is written to the Kindle."""
import json,os,re,time,uuid
from pathlib import Path
from kindle_store import KindleError,new_key,parse_key,valid_id

MODES={'koreader':2222,'native':2223}
# WTT layout adapter; defaults preserve upstream standalone behavior.
RUNTIME_ROOT='koreader'
def mode_name(value):
    if value not in MODES:raise KindleError('mode','Choose koreader or native mode.')
    return value

def inside(root,relative):
    p=root/relative
    if not p.resolve().is_relative_to(root):raise KindleError('usb','A USB path leaves the Kindle drive.')
    return p

def verify_usb(raw,mode='koreader'):
    root=Path(raw).expanduser().resolve(strict=True)
    if root==Path(root.anchor):raise KindleError('usb','Choose the mounted Kindle drive, not a filesystem root.')
    marker=inside(root,'system/version.txt')
    if not marker.is_file() or marker.stat().st_size>4096 or not re.match(r'^Kindle\s+\d',marker.read_text()):raise KindleError('usb','This is not a recognized Kindle drive.')
    if not inside(root,'documents').is_dir():raise KindleError('usb','Kindle documents folder is missing.')
    if mode=='koreader':
        for name in [RUNTIME_ROOT+'/koreader.sh',RUNTIME_ROOT+'/settings.reader.lua']:
            if not inside(root,name).is_file():raise KindleError('usb','KOReader is missing on the selected Kindle.')
    return root

def find_usb(mode='koreader'):
    import sys
    roots=[]
    if sys.platform=='darwin':bases=[Path('/Volumes')]
    elif sys.platform=='win32':bases=[];roots=[Path(chr(i)+':/') for i in range(68,91)]
    else:bases=[Path('/media')/os.environ.get('USER',''),Path('/run/media')/os.environ.get('USER',''),Path('/mnt')]
    for base in bases:
        if base.is_dir():roots.extend(p for p in base.iterdir() if p.is_dir())
    found=[]
    for p in roots:
        try:found.append(str(verify_usb(p,mode)))
        except (OSError,ValueError,KindleError):pass
    return found

def lua_ssh_settings(source,port):
    if len(source)>2_000_000 or not re.match(r'^\s*(?:--[^\n]*\n\s*)*return\s*\{',source) or not source.rstrip().endswith('}'):raise KindleError('usb-settings','Unrecognized KOReader settings; nothing was replaced.')
    for key,value in {'SSH_port':json.dumps(str(port)),'SSH_allow_no_password':'false','SSH_key_only_auth':'true','SSH_autostart':'true'}.items():
        pattern=rf'^    \["{key}"\] = [^\n]+,\r?$'
        found=re.findall(pattern,source,re.M)
        if len(found)>1:raise KindleError('usb-settings','Ambiguous KOReader settings; nothing was replaced.')
        line=f'    ["{key}"] = {value},'
        source=re.sub(pattern,lambda _:line,source,flags=re.M) if found else re.sub(r'\}\s*$',line+'\n}\n',source)
    return source

def atomic_file(path,content):
    temp=path.with_name(path.name+'.qiaomu-'+uuid.uuid4().hex+'.tmp')
    try:
        with temp.open('xb') as f:f.write(content);f.flush();os.fsync(f.fileno())
        os.replace(temp,path)
        if path.read_bytes()!=content:raise KindleError('usb-settings','USB write verification failed.')
    finally:temp.unlink(missing_ok=True)

def pair(store,keys,volume,mode='koreader',host=None,port=None,device_id=None):
    from kindle_transport import validate_address
    mode=mode_name(mode);port=MODES[mode] if port is None else port
    validate_address(host or '192.168.0.1',port)
    root=verify_usb(volume,mode)
    if mode=='native':
        marker=inside(root,'qiaomu-kindle/receiver.json')
        if not marker.is_file() or marker.stat().st_size>4096:raise KindleError('receiver','Prepare the native receiver first with prepare-receiver, then pair and run its install item once on Kindle.')
        info=json.loads(marker.read_text())
        if info.get('protocol')!=1 or info.get('port')!=2223 or info.get('prepared') is not True:raise KindleError('receiver','Unsupported native receiver.')
        target=inside(root,'usbnetlite/etc/dropbear/authorized_keys');settings=None
    else:target=inside(root,RUNTIME_ROOT+'/settings/SSH/authorized_keys');settings=inside(root,RUNTIME_ROOT+'/settings.reader.lua')
    previous_keys=target.read_bytes() if target.exists() else None
    if previous_keys is not None and len(previous_keys)>1_000_000:raise KindleError('usb-settings','Unexpected authorized-key size.')
    previous_settings=settings.read_bytes() if settings else None
    next_settings=lua_ssh_settings(previous_settings.decode(),port).encode() if settings else None
    with store.edit() as data:
        selected=device_id or data.get('active_device') or 'kindle-'+uuid.uuid4().hex[:16]
        if not valid_id(selected):raise KindleError('device','Invalid device identifier.')
        device=data['devices'].get(selected)
        if device:
            identity=device['credential_id'];private=keys.get(identity)
            if not private:raise KindleError('credential-missing','The paired identity is missing; recover it before pairing. A new identity was not silently generated.')
            key=parse_key(private)
        else:
            identity='kindle-'+uuid.uuid4().hex;private,key=new_key();keys.put_new(identity,private)
            device={'credential_id':identity,'profiles':{}}
        public=key.get_name()+' '+key.get_base64()+' qiaomu-kindlesync'
        old=(previous_keys or b'').decode();needle=public.split()[:2]
        exists=any(any(parts[i:i+2]==needle for i in range(len(parts)-1)) for parts in [line.split() for line in old.splitlines() if not line.lstrip().startswith('#')])
        next_keys=previous_keys if exists else (old.rstrip()+ ('\n' if old.strip() else '')+public+'\n').encode()
        target.parent.mkdir(parents=True,exist_ok=True)
        inside(root,str(target.relative_to(root)))
        stamp=str(time.time_ns())
        for p,old_bytes in [(target,previous_keys),(settings,previous_settings)]:
            if p and old_bytes is not None:p.with_name(p.name+'.qiaomu-skill-backup-'+stamp).write_bytes(old_bytes)
        try:
            if (target.read_bytes() if target.exists() else None)!=previous_keys or settings and settings.read_bytes()!=previous_settings:raise KindleError('usb-settings','Device settings changed during pairing; retry after exiting KOReader.')
            atomic_file(target,next_keys)
            if settings:atomic_file(settings,next_settings)
        except BaseException:
            if previous_keys is None:target.unlink(missing_ok=True)
            else:atomic_file(target,previous_keys)
            if settings:atomic_file(settings,previous_settings)
            raise
        profile=device['profiles'].get(mode,{})
        device['profiles'][mode]={**profile,'host':host or profile.get('host',''),'port':port,'paired':True,'pending_trust':not bool(profile.get('fingerprint'))}
        data['devices'][selected]=device;data['active_device']=selected;data['default_mode']=mode
    return {'ok':True,'paired':True,'device':selected,'mode':mode,'port':port,'host_trust_pending':not bool(profile.get('fingerprint')),'installPending':mode=='native' and info.get('installed') is not True}

SCRIPT_INTERFACE = "internal-module"

