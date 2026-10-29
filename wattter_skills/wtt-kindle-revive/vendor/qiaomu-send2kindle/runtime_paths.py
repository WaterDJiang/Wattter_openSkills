"""Machine-local state, independent of any client, vault or skill checkout."""
import os,sys
from pathlib import Path

def state_root():
    if sys.platform=='darwin': return Path.home()/'Library/Application Support/Qiaomu/Kindle'
    if sys.platform=='win32': return Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData/Local'))/'Qiaomu/Kindle'
    return Path(os.environ.get('XDG_CONFIG_HOME',Path.home()/'.config'))/'qiaomu-kindlesync'

def runtime_python():
    return state_root()/'runtime'/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python3')

SCRIPT_INTERFACE = "internal-module"

