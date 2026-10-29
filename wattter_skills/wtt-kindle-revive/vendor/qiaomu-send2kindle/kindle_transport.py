"""Pinned SSH/SFTP, bounded local discovery and verified no-overwrite delivery."""
from __future__ import annotations
import concurrent.futures,contextlib,hashlib,ipaddress,io,json,socket,stat,time,uuid
from pathlib import Path
import paramiko
from kindle_store import KindleError,parse_key
RFC1918=tuple(ipaddress.ip_network(x) for x in ['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16'])
FOLDER='/mnt/us/documents'
# WTT may supply an explicit exec-channel SFTP opener for an internal runtime.
def open_sftp(transport):return paramiko.SFTPClient.from_transport(transport)

def validate_address(host,port):
    try:ip=ipaddress.IPv4Address(host)
    except (ValueError,TypeError):raise KindleError('address','Use the Kindle private LAN IPv4 address.') from None
    if not any(ip in net for net in RFC1918) or type(port)!=int or not 1<=port<=65535:raise KindleError('address','Invalid private LAN address or port.')
    return str(ip),port

def profile_for(store,device_id=None,mode=None):
    device_id,device=store.device(device_id);mode=mode or store.load().get('default_mode','koreader')
    profile=device.get('profiles',{}).get(mode)
    if not profile or not profile.get('paired'):raise KindleError('not-paired','Pair this Kindle in the requested reading mode first.')
    return device_id,device,mode,profile

@contextlib.contextmanager
def session(profile,private,trust=False,timeout=6):
    host,port=validate_address(profile.get('host'),profile.get('port'))
    expected=profile.get('fingerprint','')
    if expected and (len(expected)!=64 or any(c not in '0123456789abcdef' for c in expected)):raise KindleError('host-key','Invalid pinned device identity; recover the configuration.')
    if not expected and not (trust and profile.get('pending_trust')):raise KindleError('trust-required','First connection requires connect --host ADDRESS --trust-new-device after physical USB pairing. Later connections keep the pinned identity.')
    transport=sftp=sock=None;phase='network'
    try:
        key=parse_key(private)
        sock=socket.create_connection((host,port),timeout=timeout)
        transport=paramiko.Transport(sock);transport.banner_timeout=timeout;transport.auth_timeout=timeout
        transport.start_client(timeout=timeout)
        actual=hashlib.sha256(transport.get_remote_server_key().asbytes()).hexdigest()
        # Verify identity before any private-key authentication attempt.
        if expected and actual!=expected:raise KindleError('host-key','Kindle identity changed. Authentication was stopped; verify the device instead of disabling identity checks.')
        phase='auth';transport.auth_publickey('root',key)
        if not transport.is_authenticated():raise KindleError('auth','The Kindle rejected the paired identity.')
        phase='sftp';sftp=open_sftp(transport);sftp.get_channel().settimeout(20)
        if sftp.normalize(FOLDER)!=FOLDER or not stat.S_ISDIR(sftp.stat(FOLDER).st_mode):raise KindleError('folder','The expected Kindle documents folder is unavailable.')
        yield transport,sftp,actual
    except KindleError:raise
    except paramiko.AuthenticationException:raise KindleError('auth','The Kindle rejected the paired identity; keep existing keys and repair pairing over USB.') from None
    except (OSError,EOFError,paramiko.SSHException):raise KindleError(phase,'Kindle '+phase+' connection failed or timed out; wake it and check Wi-Fi before retrying.') from None
    finally:
        if sftp:
            with contextlib.suppress(Exception):sftp.close()
        if transport:transport.close()
        if sock:sock.close()

def protocol_command(transport,command):
    if command not in {'qiaomu-receiver-v1','qiaomu-scan-v1'}:raise KindleError('receiver','Unsupported receiver command.')
    channel=transport.open_session(timeout=5);channel.settimeout(15)
    try:
        channel.exec_command(command);data=bytearray()
        while True:
            chunk=channel.recv(1024)
            if not chunk:break
            data.extend(chunk)
            if len(data)>4096:raise KindleError('receiver','Oversized receiver response.')
        deadline=time.monotonic()+15
        while not channel.exit_status_ready():
            if time.monotonic()>=deadline:raise KindleError('receiver','Native receiver response timed out.')
            time.sleep(.05)
        if channel.recv_exit_status()!=0:raise KindleError('receiver','Native receiver is not ready.')
        return data.decode().strip()
    finally:channel.close()

def private_for(keys,device):
    private=keys.get(device['credential_id'])
    if not private:raise KindleError('credential-missing','The system credential is missing. Recover or migrate it; a replacement identity was not generated.')
    return private

def save_profile(store,device_id,mode,profile,identity):
    with store.edit() as data:
        device=data['devices'].get(device_id)
        if not device or device.get('credential_id')!=identity:raise KindleError('changed','Device configuration changed; reconnect before sending.')
        device['profiles'][mode]=profile

def connect(store,keys,device_id=None,mode=None,host=None,port=None,trust=False):
    did,device,mode,profile=profile_for(store,device_id,mode)
    target={**profile,'host':host or profile.get('host'),'port':profile.get('port') if port is None else port}
    with session(target,private_for(keys,device),trust) as (transport,sftp,actual):
        if mode=='native':
            try:capability=json.loads(protocol_command(transport,'qiaomu-receiver-v1'))
            except (ValueError,KindleError):raise KindleError('receiver','Start the native receiver and complete its one-time installation on Kindle.') from None
            if capability.get('protocol')!=1 or capability.get('scan') is not True:raise KindleError('receiver','Incompatible native receiver.')
    save_profile(store,did,mode,{**target,'fingerprint':actual,'pending_trust':False},device['credential_id'])
    return {'ok':True,'ready':True,'device':did,'mode':mode,'host':target['host'],'port':target['port'],'fingerprint':actual}

def local_hosts():
    import psutil
    result=set()
    for rows in psutil.net_if_addrs().values():
        for row in rows:
            if row.family!=socket.AF_INET or not row.netmask:continue
            try:
                ip,_=validate_address(row.address,2222)
                interface=ipaddress.ip_interface(ip+'/'+row.netmask)
                subnet=ipaddress.ip_network(ip+'/'+str(max(24,interface.network.prefixlen)),strict=False)
                for host in subnet.hosts():
                    if str(host)!=ip:result.add(str(host))
                    if len(result)>=512:return sorted(result)
            except (ValueError,KindleError):continue
    return sorted(result)

def discover(store,keys,device_id=None,mode=None):
    did,device,mode,profile=profile_for(store,device_id,mode)
    if not profile.get('fingerprint'):raise KindleError('trust-required','Connect to the physically paired device once before automatic discovery.')
    private=private_for(keys,device);deadline=time.monotonic()+20
    def probe(host):
        if time.monotonic()>deadline:return
        try:
            with socket.create_connection((host,profile['port']),timeout=.4) as sock:
                sock.settimeout(.5)
                if not sock.recv(256).startswith(b'SSH-2.0-'):return
            if time.monotonic()>deadline:return
            with session({**profile,'host':host},private,timeout=3) as (transport,sftp,fp):
                if mode=='native':
                    cap=json.loads(protocol_command(transport,'qiaomu-receiver-v1'))
                    if cap.get('protocol')!=1 or cap.get('scan') is not True:return
                return host
        except (OSError,KindleError,ValueError):return
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        futures=[pool.submit(probe,host) for host in local_hosts()]
        for future in concurrent.futures.as_completed(futures):
            host=future.result()
            if host:
                deadline=0
                for f in futures:f.cancel()
                save_profile(store,did,mode,{**profile,'host':host},device['credential_id'])
                return {'ok':True,'device':did,'mode':mode,'host':host,'fingerprint':profile['fingerprint']}
    raise KindleError('not-found','No device matching the paired identity was found on directly attached private subnets.')

def send_file(profile,private,path,name,expected_digest=None):
    path=Path(path);before=path.stat()
    if not path.is_file() or not 0<before.st_size<=512*1024*1024:raise KindleError('size','Book size must be between 1 byte and 512 MiB.')
    if not name or len(name)>180 or name in {'.','..'} or any(c in name for c in '/\\') or any(ord(c)<32 or ord(c)==127 for c in name):raise KindleError('file','Invalid ebook filename.')
    with session(profile,private) as (transport,sftp,fp):
        stem,ext=Path(name).stem,Path(name).suffix
        target=None
        for i in range(1000):
            candidate=FOLDER+'/'+(name if i==0 else f'{stem} ({i+1}){ext}')
            try:sftp.lstat(candidate)
            except OSError as e:
                if e.errno==2:target=candidate;break
                raise
        if target is None:raise KindleError('conflict','No free filename on Kindle; existing books were preserved.')
        temp=FOLDER+'/.qiaomu-'+uuid.uuid4().hex+'.part';complete=False
        try:
            digest=hashlib.sha256();sent=0
            with path.open('rb') as source,sftp.open(temp,'wx') as remote:
                while chunk:=source.read(65536):remote.write(chunk);digest.update(chunk);sent+=len(chunk)
            after=path.stat();local_hash=digest.hexdigest()
            if (before.st_size,before.st_mtime_ns,before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino) or sent!=before.st_size or expected_digest and local_hash!=expected_digest:raise KindleError('changed','The local book changed during transfer; no book was finalized.')
            if sftp.stat(temp).st_size!=sent:raise KindleError('verify','Uploaded byte count did not match; no book was finalized.')
            verify=hashlib.sha256();read=0
            with sftp.open(temp,'rb') as remote:
                while chunk:=remote.read(65536):verify.update(chunk);read+=len(chunk)
            if read!=sent or verify.hexdigest()!=local_hash:raise KindleError('verify','Device readback did not match the source; no book was finalized.')
            sftp.rename(temp,target);complete=True
            return {'path':target,'bytes':sent,'sha256':local_hash,'fingerprint':fp}
        finally:
            if not complete:
                with contextlib.suppress(Exception):sftp.remove(temp)

def scan_native(profile,private):
    with session(profile,private) as (transport,sftp,fp):
        status=protocol_command(transport,'qiaomu-scan-v1')
    if status not in {'scan-requested','scan-pending'}:raise KindleError('index','Native scan status is unknown; do not resend the book.')
    return {'scanRequested':status=='scan-requested','scanPending':status=='scan-pending'}

SCRIPT_INTERFACE = "internal-module"

