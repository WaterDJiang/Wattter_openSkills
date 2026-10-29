"""OS credentials and locked, atomic non-secret device metadata. No file fallback."""
from __future__ import annotations
import io,json,os,re,sys,uuid
from pathlib import Path
from contextlib import contextmanager
from filelock import FileLock
from runtime_paths import state_root

class KindleError(Exception):
    def __init__(self,code,message):super().__init__(message);self.code=code

def valid_id(value):return isinstance(value,str) and re.fullmatch(r'[a-z0-9-]{1,64}',value) is not None

class SystemKeys:
    SERVICE='ai.qiaomu.kindlesync'
    def __init__(self):
        try:
            if sys.platform=='darwin':
                from keyring.backends.macOS import Keyring
            elif sys.platform=='win32':
                from keyring.backends.Windows import WinVaultKeyring as Keyring
            elif sys.platform.startswith('linux'):
                from keyring.backends.SecretService import Keyring
            else:raise RuntimeError('unsupported platform')
            self.backend=Keyring()
            if self.backend.priority<=0:raise RuntimeError('unavailable')
        except Exception:raise KindleError('credential-unavailable','System credential storage is unavailable or locked; unlock it and retry. No plaintext fallback is used.') from None
    def get(self,identity):
        if not valid_id(identity):raise KindleError('config','Invalid credential reference.')
        try:return self.backend.get_password(self.SERVICE,identity)
        except Exception:raise KindleError('credential-unavailable','System credential storage is unavailable, locked or access was denied; unlock/allow access and retry.') from None
    def put_new(self,identity,value):
        existing=self.get(identity)
        if existing is not None:
            if existing!=value:raise KindleError('credential-conflict','An existing device identity cannot be overwritten. Keep its pairing or explicitly pair a new device.')
            return
        try:self.backend.set_password(self.SERVICE,identity,value)
        except Exception:raise KindleError('credential-unavailable','Could not save the identity to system credential storage.') from None
        if self.get(identity)!=value:raise KindleError('credential-save','Credential readback failed; device pairing was not changed.')

def parse_key(value):
    import paramiko
    if not isinstance(value,str) or len(value)>16384:raise KindleError('credential-invalid','Invalid device identity.')
    for kind in [paramiko.ECDSAKey,paramiko.Ed25519Key,paramiko.RSAKey]:
        try:return kind.from_private_key(io.StringIO(value))
        except (ValueError,paramiko.SSHException):pass
    raise KindleError('credential-invalid','The saved identity is invalid or encrypted in an unsupported format; it was not replaced.')

def new_key():
    import paramiko
    key=paramiko.ECDSAKey.generate(bits=256);stream=io.StringIO();key.write_private_key(stream)
    return stream.getvalue(),key

class ConfigStore:
    def __init__(self,root=None):
        self.root=Path(root) if root is not None else state_root()
        if self.root.is_symlink():raise KindleError('config','The configuration directory must not be a symbolic link.')
        self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        if os.name!='nt':self.root.chmod(0o700)
        self.path=self.root/'devices.json'
    def load(self):
        if self.path.is_symlink():raise KindleError('config','Device metadata must not be a symbolic link.')
        if not self.path.exists():return {'version':2,'default_mode':'koreader','devices':{}}
        if self.path.stat().st_size>1024*1024:raise KindleError('config','Device metadata is too large.')
        try:
            data=json.loads(self.path.read_text())
            if data.get('version')!=2 or not isinstance(data.get('devices'),dict):raise ValueError()
            # A private key must never be serialized into this metadata store.
            if any(x in self.path.read_text() for x in ['PRIVATE KEY','privateKey','private_key']):raise ValueError()
            return data
        except (ValueError,AttributeError):raise KindleError('config','Device metadata is invalid; it was preserved for recovery.') from None
    @contextmanager
    def edit(self):
        lock_path=self.root/'devices.lock'
        if lock_path.is_symlink():raise KindleError('config','Invalid metadata lock path.')
        with FileLock(str(lock_path),timeout=10):
            if os.name!='nt':lock_path.chmod(0o600)
            data=self.load();yield data;self.write(data)
    def write(self,data):
        value=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
        if any(x in value for x in ['PRIVATE KEY','privateKey','private_key']):raise KindleError('config','Refusing to store a credential in device metadata.')
        if len(value.encode('utf-8'))>1024*1024:raise KindleError('config','Device metadata is too large.')
        temp=self.root/('.devices-'+uuid.uuid4().hex+'.tmp')
        try:
            with temp.open('x',encoding='utf-8') as f:
                if os.name!='nt':os.fchmod(f.fileno(),0o600)
                f.write(value);f.flush();os.fsync(f.fileno())
            if self.path.is_symlink():raise KindleError('config','Invalid metadata target.')
            os.replace(temp,self.path)
        finally:temp.unlink(missing_ok=True)
    def device(self,device_id=None):
        data=self.load();device_id=device_id or data.get('active_device')
        if not valid_id(device_id) or device_id not in data['devices']:raise KindleError('not-paired','Pair this Kindle over USB first, or explicitly migrate an existing paired identity.')
        device=data['devices'][device_id]
        if not valid_id(device.get('credential_id')):raise KindleError('config','Invalid device credential reference.')
        return device_id,device

SCRIPT_INTERFACE = "internal-module"

