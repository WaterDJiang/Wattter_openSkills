"""WTT internal runtime layout; old paths are recognized only for migration/recovery."""
import re
from wtt_kindle import WttError
RUNTIME='WTT/Runtime/koreader'
EXTENSION='WTT/Runtime/extensions/koreader'
EVIDENCE='WTT/Runtime/Evidence'
LEGACY_ROOTS=('koreader','extensions/koreader')
ROOTS=(RUNTIME,EXTENSION)
LAYOUT='wtt-internal-v1'

def relocate(name):
    for old,new in zip(LEGACY_ROOTS,ROOTS):
        if name==old or name.startswith(old+'/'):return new+name[len(old):]
    return name

def runtime_for(record):
    return RUNTIME if any(n.startswith(RUNTIME+'/') for n in record.get('files',{})) else 'koreader'

def rewrite_paths(data):
    # A path prefix, not an arbitrary token/string substring.
    data=re.sub(rb'/mnt/us/extensions/koreader(?=[/\s\x00\"\'<>]|$)',('/mnt/us/'+EXTENSION).encode(),data)
    return re.sub(rb'/mnt/us/koreader(?=[/\s\x00\"\'<>]|$)',('/mnt/us/'+RUNTIME).encode(),data)

def adapt(name,data):
    if name.endswith('/bin/koreader-ext.sh'):
        return b'#!/bin/sh\necho "WTT Reader: use WTT Skill for verified updates and WTT settings for SSH."\nexit 1\n'
    if name.endswith('/libkohelper.sh') or name.endswith(('.lua','.lua.old','.json','.xml','.txt','.sh','.html')):
        try:data.decode('utf-8')
        except UnicodeDecodeError:
            if b'/mnt/us/koreader' in data:raise WttError('需审阅含旧绝对路径的非文本配置')
            return data
        data=rewrite_paths(data)
    if name==RUNTIME+'/koreader.sh':
        needle=b'ko_update_check() {\n'
        if data.count(needle)!=1:raise WttError('固定启动更新接口不匹配')
        data=data.replace(needle,needle+b'    # WTT owns internal runtime updates; never unpack an upstream OTA here.\n    return 0\n')
    if name==RUNTIME+'/frontend/ui/otamanager.lua':
        for needle,guard in [(b'function OTAManager:checkUpdate()\n',b'    return -1\n'),(b'function OTAManager:fetchAndProcessUpdate()\n',b'    UIManager:show(InfoMessage:new{ text = "WTT Reader: use WTT Skill for verified updates." })\n    return\n')]:
            # A return must end a Lua block; wrap guard in do/end before original body.
            if data.count(needle)!=1:raise WttError('固定OTA接口不匹配')
            data=data.replace(needle,needle+b'    do\n'+guard+b'    end\n')
    return data
