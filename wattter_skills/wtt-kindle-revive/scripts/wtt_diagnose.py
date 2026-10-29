"""Read-only triage. Never creates runtime state, connects to a network, or echoes logs."""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from wtt_kindle import WttError, relative_file

LIMIT = 256*1024
CATALOG = {
 'lookup_unavailable': ('引导命令查找器不可用，不能据此判断所有工具都缺失', 'inspect_entry_and_lookup_before_any_retry'),
 'sha256_tool_missing': ('缺少可用摘要工具，不能跳过校验', 'inspect_pinned_helper_and_entry'),
 'sha256_mismatch': ('载荷摘要不匹配', 'stop_and_verify_original_asset'),
 'base64_missing': ('旧环境Base64解码缺失或自检失败', 'inspect_bound_helper_and_failed_stage'),
 'busybox_dirname': ('旧BusyBox不接受dirname --', 'inspect_posix_launcher_not_reader_engine'),
 'usb_state_query': ('USB状态接口不可用或仍处存储模式', 'inspect_actual_device_usb_interface_without_bypass'),
 'menusorter_failure': ('菜单注册/排序失败，原菜单表可能已被部分消耗', 'inspect_menu_ids_and_use_bounded_ui_recovery'),
 'native_fallback_failed': ('原生菜单回退未成功，不能报告已切换', 'keep_safe_continue_exit_not_broken_menu'),
 'appledouble_rollback': ('删除伴随主文件后AppleDouble元数据消失', 'verify_remaining_owned_files_then_resume_bounded_rollback'),
 'document_open_failed': ('文档未能打开，不等于没有该格式支持', 'validate_file_and_independent_known_good_sample'),
 'legacy_tls_pairing': ('旧自研TLS配对问题，当前路线不再使用', 'stay_transfer_and_inspect_current_ssh_profile'),
 'network_address': ('网络地址/会话可能失效', 'check_current_network_and_existing_session_not_reinstall'),
 'unknown_error': ('存在未归类错误，保留原始私有日志', 'inspect_recent_stage_without_repeating_install'),
}
PATTERNS = {
 'lookup_unavailable': r'lookup_unavailable',
 'sha256_tool_missing': r'sha256_tool_missing',
 'sha256_mismatch': r'sha256_mismatch',
 'base64_missing': r'base64_selftest_failed|missing_tool=base64|base64[^\n]{0,60}(?:not found|missing)',
 'busybox_dirname': r'Usage: dirname|dirname[^\n]{0,100}(?:invalid|illegal|unrecognized|unsupported|Usage:)',
 'usb_state_query': r'lipcErrNoSuchSource|USB storage mode',
 'menusorter_failure': r'menusorter\.lua:\d+',
 'native_fallback_failed': r'WTT native menu fallback failed',
 'appledouble_rollback': r'FileNotFoundError[^\n]*\._|No such file or directory[^\n]*\._',
 'document_open_failed': r'cannot\s*open\s*document|cannot opendocument|Cre error loading file|Error reading EPUB document',
 'legacy_tls_pairing': r'配对临时目录冲突|pairing temporary directory conflict',
 'network_address': r'Connection refused|No route to host|Connection timed out',
}


def _bounded(path, limit=LIMIT, tail=False):
    path = Path(path)
    if any(p.is_symlink() for p in [path,*path.parents]): raise WttError('read_path_link_rejected')
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
    with os.fdopen(fd,'rb') as stream:
        info=os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode): raise WttError('read_regular_file_required')
        size = info.st_size
        if size > limit and not tail: raise WttError('read_size_limit')
        if size > limit: stream.seek(-limit,os.SEEK_END)
        return stream.read(limit).decode('utf-8','replace'), size > limit


def _record(root, name, issues):
    if root is None: return None
    try:
        p = relative_file(root,name)
        if not p.exists(): return None
        value = json.loads(_bounded(p)[0])
        if not isinstance(value,dict): raise ValueError()
        return value
    except (OSError,ValueError,TypeError,WttError):
        issues.append('record_unreadable_or_untrusted');return None


def log_findings(path):
    text,truncated = _bounded(path,tail=True)
    boundaries = list(re.finditer(r'(?m)^.*launching\.\.\..*$|^stage=entered\s*$|^entry start\s*$',text))
    if boundaries: text=text[boundaries[-1].start():]
    found = [code for code,pattern in PATTERNS.items() if re.search(pattern,text,re.I)]
    if not found and re.search(r'(?i)\bERROR\b|stack traceback|Traceback \(most recent call last\)',text): found=['unknown_error']
    return found, {'recent_session_only':bool(boundaries),'tail_truncated':truncated,
                   'normal_exit_observed':bool(re.search(r'Tearing down UIManager with exit code: 0|(?m:^exit=0\s*$)',text))}


def diagnose(state=None, device=None, log=None, mode='auto', require_mount=True, identity_fn=None):
    if mode not in {'auto','revive','transfer'}: raise WttError('invalid_mode')
    issues=[];records={};state=Path(state).expanduser() if state else None
    if state:
        for key,name in {'execution':'execution.json','backend':'koreader-install.json','ui':'wtt-ui-install.json',
                         'checkpoint':'current-checkpoint.json','weread':'weread-user-validation.json'}.items():
            records[key]=_record(state,name,issues)
    checkpoint=records.get('checkpoint') or {};we=records.get('weread') or {}
    report={'ok':True,'command':'diagnose','read_only':True,'device_written':False,'state_written':False,'network_used':False,
            'mode':mode,'evidence_scope':'stored_records_only','live_identity_verified':False,
            'records_present':{k:bool(v) for k,v in records.items()},'findings':[],
            'user_reported':{'weread_body':we.get('body_open_page_turn_verified') is True or checkpoint.get('weread_body_hardware_verified') is True,
                             'settings':checkpoint.get('current_ui_settings_user_verified') is True},
            'log':None,'device':None,'raw_private_values_included':False,
            'stored_ui_version':None}
    version=(records.get('ui') or {}).get('version')
    if isinstance(version,str) and re.fullmatch(r'[0-9]+(?:\.[0-9]+){2}',version):report['stored_ui_version']=version
    if device:
        try:
            d=Path(device).expanduser()
            if d.is_symlink() or not d.is_dir() or (require_mount and not os.path.ismount(d)): raise WttError('not_device_mount')
            relative_file(d,'WTT/device.json')
            firmware_text=_bounded(relative_file(d,'system/version.txt'),16384)[0]
            match=re.search(r'\b5(?:\.\d+){1,5}\b',firmware_text)
            firmware=match.group() if match else None
            report['device']={'firmware_hint':firmware,'profile_supported':False,'execution_verified':False,'ui_integrity':None}
            if require_mount or identity_fn is not None:
                import wtt_bootstrap as boot
                lookup=identity_fn or boot.usb_identity;ident=lookup()
                report['device']['profile_supported']=ident.get('serial_prefix')=='B024' and firmware=='5.6.1.1'
                if not report['device']['profile_supported']: issues.append('device_profile_unsupported')
                execution=records.get('execution') or {};session=_record(state,'bootstrap.json',issues)
                if session and execution:
                    boot.require_execution(d,state,require_mount=require_mount,identity_fn=lambda:ident)
                    report['live_identity_verified']=True;report['evidence_scope']='bound_current_device'
                    report['device']['execution_verified']=True
                    import wtt_ui
                    checked=wtt_ui.inspect(d,require_mount)
                    report['device']['ui_integrity']='match' if checked.get('ok') and checked.get('installed') else 'missing_or_changed'
                    if report['device']['ui_integrity']!='match':issues.append('ui_missing_or_changed')
        except (OSError,ValueError,KeyError,TypeError,WttError,subprocess.SubprocessError): issues.append('device_identity_or_receipt_not_verified')
    codes=[]
    if log:
        try: codes,report['log']=log_findings(log)
        except (OSError,ValueError,WttError): issues.append('log_unreadable_or_untrusted')
    for code in codes:
        title,next_action=CATALOG[code]
        report['findings'].append({'code':code,'summary':title,'next_check':next_action})
    report['input_issues']=sorted(set(issues))
    report['needs_attention']=bool(codes or issues)
    report['automatic_actions']=[]
    if mode=='transfer': report['next']='只核对SSH配对/当前地址/固定身份；不执行复活、整机备份或重装。'
    elif report['needs_attention']:report['next']='按最近会话的原因码做定向检查；本命令未修复或改写任何内容。'
    else: report['next']='未发现已知故障；这不证明触屏/格式或账号成功。按意图和已有用户验收继续，不重复安装。'
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--state-dir',type=Path);p.add_argument('--device',type=Path);p.add_argument('--log',type=Path)
    p.add_argument('--mode',choices=['auto','revive','transfer'],default='auto');a=p.parse_args()
    print(json.dumps(diagnose(a.state_dir,a.device,a.log,a.mode),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
