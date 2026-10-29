"""PW1 bootstrap orchestration. Host never executes the platform jailbreak script."""
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import uuid
import urllib.request
import zipfile

from wtt_kindle import PACKAGE_ROOT, WttError, digest, load_json, private_dir, relative_file, timestamp, write_json, verify_backup
from wtt_install import assert_backup, target

JB_SHA = "cfe16df16effaa3be04dcddc63b542db57b6146820936d4098f8326d58fbbc02"
JB_URL = "https://github.com/KindleModding/jb.sh/releases/download/v2.4.0/jb.sh"
WB_SHA = "9e85970902a1f2af6b4c3243755d80595dd36404b85083f8be8c65a69d04cfdf"
MIB = 1024 * 1024


def fetch(state):
    """Download reviewed platform assets to private host cache, never execute them."""
    state = private_dir(state)
    cache = state / "platform-cache"
    cache.mkdir(exist_ok=True, mode=0o700)
    sources = [("jb-v2.4.0.sh", JB_URL, JB_SHA),
               ("wb2-v1.1.0.zip", "https://github.com/KindleModding/Winterbreak2/releases/download/v1.1.0/wb2.zip", WB_SHA)]
    for name, url, sha in sources:
        final = relative_file(cache, name)
        if final.exists():
            if digest(final) != sha:
                raise WttError("缓存摘要不符，不覆盖: " + name)
            continue
        part = relative_file(cache, name + ".part")
        if part.exists():
            raise WttError("上次下载留下 .part；核对后移走再继续")
        with urllib.request.urlopen(url, timeout=25) as response, part.open("xb") as out:
            total = 0
            while True:
                data = response.read(MIB)
                if not data:
                    break
                total += len(data)
                if total > 20*MIB:
                    raise WttError("平台文件超过已审阅大小上限")
                out.write(data)
        if digest(part) != sha:
            raise WttError("官方下载摘要不符；保留 .part 供核对，不执行")
        part.rename(final)
    return {"ok": True, "command": "bootstrap-fetch", "device_written": False,
            "jb": str(cache / sources[0][0]), "wb": str(cache / sources[1][0])}


def trigger_handler(token, event=None):
    if not re.fullmatch(r"[0-9a-f]{8}", token):
        raise WttError("触发页会话编号无效")

    ready = set()
    class Trigger(BaseHTTPRequestHandler):
        # Protocol reproduced from WinterBreak2 api/index.js (Scam.Net/Penguins184).
        # Upstream placeholder.mobi is an empty file; no book is downloaded here.
        def do_GET(self):
            client = (self.client_address[0], self.headers.get("User-Agent", "")[:256])
            if event:
                event({"at": timestamp(), "path": self.path[:128], "user_agent": client[1]})
            if self.path in ("/", "/" + token, "/" + token + "/check"):
                body = ("<!doctype html><meta charset=utf-8><title>WTT Kindle</title>"
                        '<h1>WTT CHECK 082</h1><h2>HTTP OK</h2>'
                        '<h2 id="js">JS OFF</h2><p id="net">Connection: checking</p>'
                        '<noscript>Enable JavaScript in Browser Settings.</noscript>'
                        '<button id="go" disabled onclick="this.disabled=true;location.href=\'/' + token + '/start\'">Start Kindle setup</button>'
                        '<script>document.getElementById("js").innerHTML="JS ON";'
                        'window.wttCheck=new XMLHttpRequest();wttCheck.onreadystatechange=function(){'
                        'if(wttCheck.readyState===4){if(wttCheck.status===200){document.getElementById("net").innerHTML="Connection: OK";'
                        'document.getElementById("go").disabled=false;}else{document.getElementById("net").innerHTML="Connection: failed";}}};'
                        'wttCheck.open("GET","/' + token + '/js-ready",true);wttCheck.send(null);</script>').encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
            elif self.path == "/" + token + "/js-ready":
                if len(ready) >= 32 and client not in ready:
                    self.send_error(503)
                    return
                ready.add(client)
                body = bytes.fromhex("47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b")
                self.send_response(200)
                self.send_header("Content-Type", "image/gif")
            elif self.path == "/" + token + "/start":
                if client not in ready:
                    self.send_error(403, "JavaScript check required")
                    return
                body = b""
                name = ('<script>(window.kindle||top.kindle).messaging.sendMessage("com.lab126.pillow",'
                        '"customDialog",{name:"../../../../mnt/us/winterbreak2/dialoger"})</script>WTT.mobi')
                self.send_response(200)
                self.send_header("Content-Type", "application/x-mobipocket-ebook")
                self.send_header("Content-Disposition", "attachment; filename=" + name)
            else:
                self.send_error(404)
                return
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    return Trigger


def serve(state, bind, port=80, timeout=900):
    ip = ipaddress.ip_address(bind)
    if ip.version != 4 or not ip.is_private or ip.is_loopback or ip.is_unspecified or ip.is_link_local:
        raise WttError("仅绑定电脑当前局域网 IPv4；不绑定公网或 0.0.0.0")
    if not 1 <= port <= 65535 or not 10 <= timeout <= 1800:
        raise WttError("触发页端口或有效时间超出范围")
    state = private_dir(state)
    session = load_json(state / "bootstrap.json")
    if session.get("stage") != "prepared" or not re.fullmatch(r"[0-9a-f]{32}", session.get("challenge", "")):
        raise WttError("先完成当前设备 bootstrap-prepare")
    token = session["challenge"][:8]
    class Listener(HTTPServer):
        def get_request(self):
            connection, address = super().get_request()
            connection.settimeout(5)
            return connection, address

    def event(row):
        path = state / "trigger-events.jsonl"
        if path.is_symlink():
            raise WttError("事件记录不能是软链接")
        with path.open("a") as stream:
            path.chmod(0o600)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    with Listener((bind, port), trigger_handler(token, event)) as server:
        server.timeout = 1
        url = "http://" + bind + (":" + str(port) if port != 80 else "") + "/"
        print(json.dumps({"ok": True, "command": "bootstrap-serve", "stage": "waiting_browser",
                          "url": url, "expires_seconds": timeout, "device_written": False}), flush=True)
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            server.handle_request()
    return {"ok": True, "command": "bootstrap-serve", "stage": "server_closed", "device_written": False}


def usb_identity():
    """Keep the serial only in process memory. Refuse ambiguous USB devices."""
    result = subprocess.run(["/usr/sbin/ioreg", "-p", "IOUSB", "-l", "-w", "0"],
                            capture_output=True, text=True, timeout=15, check=True)
    found = []
    for block in re.split(r"\+-o ", result.stdout):
        if not re.search(r'"USB Product Name"\s*=\s*"[^"]*[Kk]indle[^"]*"', block):
            continue
        serial = re.search(r'"USB Serial Number"\s*=\s*"([A-Za-z0-9]+)"', block)
        if serial:
            value = serial.group(1)
            found.append({"serial_prefix": value[:4], "serial_sha256": hashlib.sha256(value.encode()).hexdigest()})
    if len(found) != 1:
        raise WttError("USB Kindle 身份缺失或不唯一；不选择设备")
    return found[0]


def route(device, require_mount=True, identity_fn=usb_identity):
    device, info = target(device, require_mount)
    identity = identity_fn()
    if identity["serial_prefix"] != "B024" or info["firmware_hint"] != "5.6.1.1":
        raise WttError("当前执行适配仅 PW1 Wi-Fi / B024 / 5.6.1.1；其它设备先独立适配")
    return device, identity


def session_read(device, state, require_mount=True, identity_fn=usb_identity):
    device, ident = route(device, require_mount, identity_fn)
    session = load_json(Path(state) / "bootstrap.json")
    if session["serial_sha256"] != ident["serial_sha256"] or session["device"] != str(device):
        raise WttError("当前设备与引导会话身份不符")
    if not re.fullmatch(r"[0-9a-f]{32}", session["challenge"]):
        raise WttError("引导 challenge 无效")
    return device, session


def plan(device, state, backup=None, require_mount=True, identity_fn=usb_identity):
    device, identity = route(device, require_mount, identity_fn)
    blockers = []
    if not backup:
        blockers.append("verified_backup_required")
    elif not (Path(state) / "bootstrap.json").exists():
        assert_backup(device, backup)
    updates = sorted(p.name for p in device.iterdir() if p.name.lower().endswith((".bin", ".partial", ".bin.tmp")))
    if updates:
        blockers.append("root_update_files_require_review")
    if not (Path(state) / "bootstrap.json").exists():
        for name in ("jb.sh.debug", "jb.sh.runmode0", "jb.sh.runmode1", "jb.sh.runmode2", "emergency.sh", "libkh", "extensions"):
            if relative_file(device, name).exists():
                blockers.append("existing_platform_requires_review:" + name)
    return {"ok": True, "command": "bootstrap-plan", "model": "PW1 Wi-Fi (2012)", "firmware": "5.6.1.1",
            "route": "WinterBreak2 + jb.sh v2.4.0", "serial_prefix": identity["serial_prefix"],
            "blockers": blockers, "can_prepare": not blockers, "device_written": False,
            "factory_reset": False, "upstream_system_changes": ["KMC/sh_integration", "OTA blocker", "boot persistence and developer keys"],
            "system_image_backup": False, "hardware_verified": False}


def owned_write(device, state, session, name, data):
    """Journal intent before writing. Resume only our complete matching files."""
    path = relative_file(device, name)
    sha = hashlib.sha256(data).hexdigest()
    prior = session["files"].get(name)
    if path.exists():
        if prior != sha or not path.is_file() or digest(path) != sha:
            raise WttError("引导路径已存在或内容变化，不覆盖: " + name)
        return
    session["files"][name] = sha
    write_json(state / "bootstrap.json", session)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())
    if digest(path) != sha:
        raise WttError("引导文件读回校验失败: " + name)


def fill_storage(device, state, session, reserve=70*MIB):
    # A dedicated, session-owned directory. Never truncate files elsewhere.
    base = relative_file(device, "WTT/bootstrap/filler")
    base.mkdir(parents=True, exist_ok=True)
    for name, size in session["filler"].items():
        if not re.fullmatch(r"WTT/bootstrap/filler/fill-[0-9]{4}\.bin", name) or not isinstance(size, int) or not 0 < size <= 64*MIB:
            raise WttError("占位清单越界")
        p = relative_file(device, name)
        if p.exists():
            if not p.is_file() or p.stat().st_size > size:
                raise WttError("占位文件大小变化")
            with p.open("rb") as stream:
                if any(any(block) for block in iter(lambda: stream.read(MIB), b"")):
                    raise WttError("占位文件已被修改，不继续写入")
            # A partial file from an interrupted write is recoverable.
            remaining = size - p.stat().st_size
        else:
            remaining = size
        if remaining:
            with p.open("ab") as stream:
                while remaining:
                    count = min(remaining, MIB)
                    stream.write(bytes(count))
                    remaining -= count
                stream.flush()
                os.fsync(stream.fileno())
    while shutil.disk_usage(device).free > reserve + MIB:
        n = len(session["filler"])
        name = "WTT/bootstrap/filler/fill-%04d.bin" % n
        size = min(64*MIB, shutil.disk_usage(device).free - reserve)
        if relative_file(device, name).exists():
            raise WttError("未登记占位文件，不覆盖")
        session["filler"][name] = size
        write_json(state / "bootstrap.json", session)
        with relative_file(device, name).open("xb") as out:
            left = size
            while left:
                count = min(left, MIB)
                out.write(bytes(count))
                left -= count
            out.flush()
            os.fsync(out.fileno())
    free = shutil.disk_usage(device).free
    if not 50*MIB <= free <= 90*MIB:
        raise WttError("防更新可用空间不在 50–90 MiB，保持飞行模式")
    return free


def helper_name(data):
    return "wtt-tools-" + hashlib.sha256(data).hexdigest()[:12]


def run_bytes(helper="wtt-sha256", system_dirs=("/usr/sbin", "/usr/bin", "/sbin", "/bin")):
    if not re.fullmatch(r"wtt-sha256|wtt-tools-[0-9a-f]{12}", helper):
        raise WttError("引导工具名称无效")
    if not system_dirs or any(not re.fullmatch(r"/[A-Za-z0-9_./-]+", p) or ".." in Path(p).parts for p in system_dirs):
        raise WttError("系统命令目录无效")
    dirs = " ".join("'" + p + "'" for p in system_dirs)
    suffix = ":".join(system_dirs)
    return ("#!/bin/sh\nset -eu\n"
            "base=/mnt/us/WTT/bootstrap\nexec >> \"$base/entry.log\" 2>&1\n"
            "temp_dir=\ncleanup() { r=$?; if [ -n \"$temp_dir\" ]; then rm -f \"$temp_dir/base64\" \"$temp_dir/wtt-sha256\"; rmdir \"$temp_dir\"; fi; echo exit=$r; sync || :; }\ntrap cleanup EXIT\n"
            "PATH=\"${PATH:+$PATH:}" + suffix + "\"; export PATH\n"
            "have_tool() {\n command -v \"$1\" >/dev/null 2>&1 && return 0\n type \"$1\" >/dev/null 2>&1 && return 0\n"
            " if [ -n \"$temp_dir\" ] && [ -x \"$temp_dir/$1\" ]; then return 0; fi\n"
            " for location in " + dirs + "; do [ ! -x \"$location/$1\" ] || return 0; done\n return 1\n}\n"
            "echo stage=entered\ncd \"$base\"\nuid=$(id -u)\necho uid=$uid\n"
            "[ \"$uid\" = 0 ] || { echo error=requires_root; exit 2; }\n"
            "echo stage=hash_check\n"
            "if [ -f \"$base/" + helper + "\" ]; then\n"
            " old_umask=$(umask); umask 077\n temp_dir=/tmp/wtt-hash-$$\n mkdir \"$temp_dir\" || { temp_dir=; exit 3; }\n"
            " cp \"$base/" + helper + "\" \"$temp_dir/wtt-sha256\"\n chmod 700 \"$temp_dir/wtt-sha256\"\n"
            " if ! have_tool base64; then ln -s wtt-sha256 \"$temp_dir/base64\"; PATH=\"$temp_dir:$PATH\"; export PATH; fi\n"
            " umask \"$old_umask\"\nfi\n"
            "if [ -n \"$temp_dir\" ]; then\n echo hash_tool=wtt-sha256\n hash=$(\"$temp_dir/wtt-sha256\" ./jb.sh)\n"
            "elif have_tool sha256sum; then\n"
            " hash=$(sha256sum ./jb.sh | cut -d ' ' -f 1)\n"
            "elif have_tool openssl; then\n"
            " hash=$(openssl dgst -sha256 ./jb.sh | awk '{print $NF}')\n"
            "else echo error=sha256_tool_missing; exit 3; fi\n"
            "echo sha256=$hash\n"
            "[ \"$hash\" = '" + JB_SHA + "' ] || { echo error=sha256_mismatch; exit 3; }\n"
            "echo stage=prerequisites\nmissing=\n"
            "echo path=$PATH\n"
            "if ! have_tool cp || ! have_tool cut; then echo error=lookup_unavailable; exit 4; fi\n"
            "for tool in uname base64 xz tar df du cut tr chown chmod cp ln mkdir rm mv md5sum sqlite3 grep cat mount stop killall logger chattr eips find touch sleep; do\n"
            " if ! have_tool \"$tool\"; then echo missing_tool=$tool; missing=1; fi\ndone\n"
            "[ -z \"$missing\" ] || { echo error=platform_tools_missing; exit 4; }\n"
            "[ \"$(printf Zm9v | base64 -d)\" = foo ] || { echo error=base64_selftest_failed; exit 3; }\n"
            "echo base64_selftest=ok\n"
            "echo stage=platform_start\n"
            "JB_HEADER='WinterBreak2 / WTT pinned platform' JB_SH_DEBUG=0 sh ./jb.sh > platform.log 2>&1\n"
            "echo stage=platform_returned\n").encode()


def hash_helper(root=PACKAGE_ROOT):
    metadata = load_json(Path(root) / "assets/hash-release.json")
    path = relative_file(Path(root), metadata["artifact"])
    data = path.read_bytes()
    if len(data) > 512*1024 or len(data) < 52 or digest(path) != metadata["sha256"]:
        raise WttError("校验工具摘要或大小不符")
    if data[:6] != b"\x7fELF\x01\x01" or int.from_bytes(data[18:20], "little") != 40:
        raise WttError("校验工具不是 ARM ELF32")
    offset, size, count = int.from_bytes(data[28:32], "little"), int.from_bytes(data[42:44], "little"), int.from_bytes(data[44:46], "little")
    if not 0 < count <= 64 or size < 32 or offset+size*count > len(data):
        raise WttError("校验工具 ELF 段无效")
    if any(int.from_bytes(data[offset+i*size:offset+i*size+4], "little") == 3 for i in range(count)):
        raise WttError("校验工具必须静态链接")
    return data


def repair(device, state, confirmed=False, airplane=False, require_mount=True, identity_fn=usb_identity, root=PACKAGE_ROOT):
    if not confirmed or not airplane:
        raise WttError("入口修复须确认设备与当前飞行模式")
    device, session = session_read(device, state, require_mount, identity_fn)
    state = private_dir(state)
    if session["stage"] != "prepared" or any((device / name).exists() for name in
            ("documents/JAILBROKEN.txt", "WTT/bootstrap/probe.meta")):
        raise WttError("已有平台/执行进展，先检查证据，不重复修复或触发")
    platform_log = relative_file(device, "WTT/bootstrap/platform.log")
    if platform_log.exists():
        entry = relative_file(device, "WTT/bootstrap/entry.log")
        prerequisite_stop = (entry.is_file() and entry.stat().st_size <= 65536
                             and entry.read_text().rstrip().endswith("exit=4")
                             and "stage=prerequisites" in entry.read_text().split("stage=entered")[-1]
                             and "stage=platform_start" not in entry.read_text().split("stage=entered")[-1])
        if (platform_log.stat().st_size > 2*1024*1024 or not entry.is_file() or entry.stat().st_size > 65536
                or "base64: not found" not in platform_log.read_text(errors="replace")
                or "/tmp/kmc MISSING" not in platform_log.read_text(errors="replace")
                or not (entry.read_text().rstrip().endswith("exit=1") or prerequisite_stop)):
            raise WttError("存在其它平台运行记录；须先分析，不能重复修复")
    if not verify_backup(session["backup"])["ok"]:
        raise WttError("原备份校验未通过")
    for name, sha in session["files"].items():
        if digest(relative_file(device, name)) != sha:
            raise WttError("暂存文件已变化，停止修复: " + name)
    helper = hash_helper(root)
    filename = helper_name(helper)
    helper_path = relative_file(device, "WTT/bootstrap/" + filename)
    helper_added = not helper_path.exists()
    owned_write(device, state, session, "WTT/bootstrap/" + filename, helper)
    p = relative_file(device, "WTT/bootstrap/run-platform.sh")
    data = run_bytes(filename)
    new_hash = hashlib.sha256(data).hexdigest()
    if digest(p) == new_hash:
        return {"ok": True, "command": "bootstrap-repair", "status": "already_updated", "device_written": helper_added}
    old_hash = digest(p)
    archive = state / ("entry-before-" + old_hash + ".sh")
    if not archive.exists():
        archive.write_bytes(p.read_bytes())
        archive.chmod(0o600)
    if digest(archive) != old_hash:
        raise WttError("入口备份摘要不符")
    temporary = relative_file(device, "WTT/bootstrap/run-platform.new")
    if temporary.exists():
        raise WttError("入口修复留有暂存文件，先核对")
    write_json(state / "entry-repair.json", {"status": "preparing", "old_hash": old_hash, "new_hash": new_hash, "backup": str(archive)})
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    if digest(temporary) != new_hash:
        raise WttError("入口修复暂存读回失败")
    os.replace(temporary, p)
    if digest(p) != new_hash:
        raise WttError("入口替换读回失败，保留修复记录")
    session["files"]["WTT/bootstrap/run-platform.sh"] = new_hash
    write_json(state / "bootstrap.json", session)
    write_json(state / "entry-repair.json", {"status": "committed", "old_hash": old_hash, "new_hash": new_hash, "backup": str(archive)})
    return {"ok": True, "command": "bootstrap-repair", "device_written": True, "factory_reset": False,
            "writes": ["WTT/bootstrap/run-platform.sh", "WTT/bootstrap/" + filename], "filler_recreated": False, "next": "安全弹出后打开诊断页，先确认 JS ON 和 Connection: OK，再点击一次"}


def prepare(device, state, backup, jb, wb, confirmed=False, airplane=False,
            require_mount=True, identity_fn=usb_identity, root=PACKAGE_ROOT, fill=True):
    if not confirmed or not airplane:
        raise WttError("须确认 Kindle 和当前飞行模式，再传 --confirm-device --airplane-confirmed")
    device, ident = route(device, require_mount, identity_fn)
    state = private_dir(state)
    for p, sha in ((jb, JB_SHA), (wb, WB_SHA)):
        if digest(p) != sha:
            raise WttError("平台发布文件摘要不符；不使用其它版本")
    with zipfile.ZipFile(wb) as z:
        html = z.read("winterbreak2/dialoger.html").decode()
    old = "sh -c 'curl -L https://kindlemodding.org/jb.sh | JB_HEADER=\\\"Winterbreak2 Jailbreak\\\" sh'"
    command = "sh /mnt/us/WTT/bootstrap/run-platform.sh"
    if old not in html:
        raise WttError("官方触发模板与审阅版本不符")
    html = html.replace(old, command)
    session_path = state / "bootstrap.json"
    if session_path.exists():
        _, session = session_read(device, state, require_mount, identity_fn)
        if session["stage"] != "prepared":
            raise WttError("已进入执行阶段；使用 bootstrap-check，不重复准备")
        if session.get("probe_kind") != "shell_execution_v2":
            raise WttError("旧准备会话需按原有探测文件接续；不自动覆盖为新探测")
        for name, sha in session["files"].items():
            p = relative_file(device, name)
            if p.exists() and digest(p) != sha:
                raise WttError("既有引导文件被修改")
    else:
        report = plan(device, state, backup, require_mount, identity_fn)
        if report["blockers"]:
            raise WttError("引导受阻: " + ";".join(report["blockers"]))
        # Verify a prior private identity binding if this is a resumed project.
        prior = state / "device-assessment-20261028.json"
        if prior.exists() and load_json(prior).get("serial_sha256") != ident["serial_sha256"]:
            raise WttError("既有备份设备身份与当前 USB 不一致")
        for name in ("WTT/bootstrap", "winterbreak2", "documents/WTT-Probe.sh"):
            if relative_file(device, name).exists():
                raise WttError("未登记引导路径已存在: " + name)
        session = {"schema_version": 1, "at": timestamp(), "device": str(device), **ident,
                   "challenge": uuid.uuid4().hex, "stage": "prepared", "backup": str(Path(backup).resolve()),
                   "files": {}, "filler": {}, "jb_sha256": JB_SHA, "probe_kind": "shell_execution_v2"}
        write_json(session_path, session)
    helper = hash_helper(root)
    filename = helper_name(helper)
    run = run_bytes(filename)
    probe = (Path(root) / "device/probe.sh").read_text().replace("@CHALLENGE@", session["challenge"])
    # Stage an independent native probe before shell permissions are available.
    payload = {"WTT/bootstrap/jb.sh": Path(jb).read_bytes(),
               "WTT/bootstrap/" + filename: helper,
               "winterbreak2/dialoger.html": html.encode(), "WTT/bootstrap/run-platform.sh": run,
               "documents/WTT-Probe.sh": probe.encode()}
    for name, data in payload.items():
        owned_write(device, state, session, name, data)
    free = fill_storage(device, state, session) if fill else None
    write_json(session_path, session)
    return {"ok": True, "command": "bootstrap-prepare", "stage": "waiting_device_browser",
            "device_written": True, "factory_reset": False, "free_bytes": free,
            "next": "安全弹出并拔USB；仅在本次bootstrap-serve返回的当前局域网URL确认JS/连接后触发一次，下载不等于执行。等待安装/重启，再飞行模式运行WTT Probe并接USB做bootstrap-check；无变化先读日志，不重复准备或重置。"}


def check(device, state, require_mount=True, identity_fn=usb_identity, framework_mode="restart"):
    if framework_mode not in ("restart", "keep"):
        raise WttError("未知 framework_mode")
    device, session = session_read(device, state, require_mount, identity_fn)
    meta = relative_file(device, "WTT/bootstrap/probe.meta")
    if not meta.is_file():
        return {"ok": True, "command": "bootstrap-check", "stage": "waiting_device_probe",
                "execution_verified": False, "device_written": False, "next": "在 Kindle 主页运行 WTT Probe，再连接 USB；JAILBROKEN.txt 不替代执行验证"}
    if meta.stat().st_size > 4096:
        raise WttError("探测收据过大")
    lines = meta.read_text().splitlines()
    data = dict(line.split("=", 1) for line in lines)
    if len(lines) != len(data) or data.get("challenge") != session["challenge"] or data.get("serial_sha256") != session["serial_sha256"]:
        raise WttError("探测收据 challenge/设备身份不匹配")
    if data.get("uid") != "0" or data.get("firmware") != "5.6.1.1" or data.get("probe_exit") != "0":
        raise WttError("设备执行权限、固件或探测失败，保留原始日志")
    if data.get("ota_blocked") != "1":
        raise WttError("设备自动更新阻断未确认；保持飞行模式，不清理占位")
    native = load_json(relative_file(device, "WTT/bootstrap/probe.json"))
    if session.get("probe_kind") == "shell_execution_v2":
        if (native.get("probe_kind") != "shell_execution_v2" or native.get("ok") is not True
                or not re.fullmatch(r"arm[A-Za-z0-9_.-]*", str(native.get("machine", "")))):
            raise WttError("执行探测版本或machine不符，不能伪造显示/输入能力")
        state = private_dir(state)
        receipt = {"schema_version": 2, "probe_kind":"shell_execution_v2", "challenge":session["challenge"],
                   "serial_sha256":session["serial_sha256"], "firmware":"5.6.1.1", "execution_verified":True,
                   "ota_blocked":True, "probe_sha256":digest(meta), "native_probe_sha256":digest(device/"WTT/bootstrap/probe.json"),
                   "at":timestamp(), "hardware_reading_verified":False, "display_input_verified":False}
        write_json(state/"execution.json",receipt)
        session["stage"]="execution_verified";write_json(state/"bootstrap.json",session)
        return {"ok":True,"command":"bootstrap-check","stage":"execution_verified","execution_verified":True,
                "device_written":False,"hardware_reading_verified":False,"display_input_verified":False,
                "probe_kind":"shell_execution_v2","next":"保持飞行模式，按收据回收占位并取当前备份，再部署固定KOReader/WTT UI；显示/触控和阅读须分别真机验收。"}
    if native.get("probe_kind") == "shell_execution_v2":
        raise WttError("旧会话不能替换为新执行探测，先核对原会话收据")
    fb = native.get("framebuffer") or {}
    inputs = native.get("inputs", [])
    if not native.get("ok") or not str(native.get("machine", "")).startswith("arm") or fb.get("bpp") != 8 or fb.get("rotate") not in (0, 3) or len(inputs) != 1:
        raise WttError("显示或触摸探测不符合当前适配，不能猜配置")
    if fb.get("rotate") == 3 and (fb.get("width"), fb.get("height")) != (758, 1024):
        raise WttError("PW1 rotate=3 仅适配实测 758x1024 竖屏")
    font = data.get("font", "")
    if not font or not re.fullmatch(r"/dev/input/event[0-9]{1,2}", inputs[0].get("path", "")):
        raise WttError("缺少可信字体/输入，先查看设备探测")
    state = private_dir(state)
    receipt = {"schema_version": 1, "challenge": session["challenge"], "serial_sha256": session["serial_sha256"],
               "firmware": "5.6.1.1", "execution_verified": True, "ota_blocked": True,
               "probe_sha256": digest(meta), "native_probe_sha256": digest(device / "WTT/bootstrap/probe.json"),
               "at": timestamp(), "hardware_reading_verified": False}
    profile = {"schema_version": 1, "platform": "kindle-linux-armel-mxcfb-legacy", "model": "PW1 Wi-Fi (B024)",
               "model_confirmed_by_user": True, "firmware": "5.6.1.1", "authorized_shell_confirmed": True,
               "bits_per_pixel": 8, "framebuffer_rotation": fb["rotate"], "input": inputs[0]["path"], "font": font, "refresh": "legacy",
               "takeover_framework": True, "framework_mode": framework_mode, "swap_xy": False, "flip_x": False, "flip_y": False,
               "execution_challenge": session["challenge"], "touch_orientation_verified": False}
    from wtt_install import profile_read
    write_json(state / "device-profile.json", profile)
    profile_read(state / "device-profile.json", "5.6.1.1")
    receipt["profile_sha256"] = digest(state / "device-profile.json")
    write_json(state / "execution.json", receipt)
    session["stage"] = "execution_verified"
    write_json(state / "bootstrap.json", session)
    return {"ok": True, "command": "bootstrap-check", "stage": "execution_verified", "execution_verified": True,
            "device_written": False, "hardware_reading_verified": False, "profile": str(state / "device-profile.json"),
            "next": "保持飞行模式，bootstrap-cleanup 回收占位；因平台修改重新保存用户分区备份，再按当前成熟底座/UI工作流部署，不能调用旧install/launcher-install。触摸方向须真机验收。"}


def require_execution(device, state, profile=None, require_mount=True, identity_fn=usb_identity):
    device, session = session_read(device, state, require_mount, identity_fn)
    receipt = load_json(Path(state) / "execution.json")
    if receipt.get("execution_verified") is not True or receipt.get("challenge") != session["challenge"] or receipt.get("serial_sha256") != session["serial_sha256"]:
        raise WttError("缺少当前设备真实执行收据；先 bootstrap-check")
    from wtt_layout import EVIDENCE
    prefix = "WTT/bootstrap" if relative_file(device,"WTT/bootstrap/probe.meta").exists() else EVIDENCE
    if digest(relative_file(device,prefix+"/probe.meta")) != receipt["probe_sha256"] or digest(relative_file(device,prefix+"/probe.json")) != receipt["native_probe_sha256"]:
        raise WttError("设备执行收据发生变化")
    if profile and digest(profile) != receipt.get("profile_sha256"):
        raise WttError("配置与设备实际探测生成版本不同；先验证适配变更")
    return device, session


def cleanup(device, state, confirmed=False, require_mount=True, identity_fn=usb_identity):
    if not confirmed:
        raise WttError("清理仅限核对当前设备后 --confirm-device")
    device, session = require_execution(device, state, require_mount=require_mount, identity_fn=identity_fn)
    # Validate every file first; never delete a modified file or unrelated directory.
    for name, size in session["filler"].items():
        if not re.fullmatch(r"WTT/bootstrap/filler/fill-[0-9]{4}\.bin", name) or not isinstance(size, int) or not 0 < size <= 64*MIB:
            raise WttError("占位清理清单越界")
        p = relative_file(device, name)
        if not p.exists():
            continue
        if p.stat().st_size != size:
            raise WttError("占位文件大小改变，不删除")
        with p.open("rb") as stream:
            if any(any(block) for block in iter(lambda: stream.read(MIB), b"")):
                raise WttError("占位文件内容改变，不删除")
    for name in session["filler"]:
        relative_file(device, name).unlink(missing_ok=True)
    return {"ok": True, "command": "bootstrap-cleanup", "device_written": True,
            "removed_filler_files": len(session["filler"]), "free_bytes": shutil.disk_usage(device).free,
            "next": "保存平台修改后的用户分区备份，再安装应用；原始备份保留"}


def launcher(device, state, confirmed=False, require_mount=True, identity_fn=usb_identity):
    raise WttError("旧C阅读入口已退役，当前入口使用wtt_ui.py并先核对现有安装")
