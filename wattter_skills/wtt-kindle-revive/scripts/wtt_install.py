#!/usr/bin/env python3
"""WTT application deployment. Does not jailbreak, flash or factory-reset a Kindle."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import struct
import uuid
import zipfile

from wtt_kindle import (PACKAGE_ROOT, WttError, contained, digest, inspect_volume, inventory,
                        load_json, private_dir, relative_file, timestamp, verify_backup, write_json)

PLATFORM = "kindle-linux-armel-mxcfb-legacy"
NOISE = {".DS_Store", ".fseventsd", ".Spotlight-V100", ".Trashes"}


def ignored(name):
    return PurePosixPath(name).parts[0] in NOISE or PurePosixPath(name).parts[0] == "WTT"


def target(path, require_mount=True):
    path = Path(path).expanduser()
    if path.is_symlink() or not path.is_dir() or path.resolve() in (Path("/"), Path.home()):
        raise WttError("目标必须为 Kindle 用户分区")
    path = path.resolve()
    if require_mount and not os.path.ismount(path):
        raise WttError("目标不是已挂载设备")
    info = inspect_volume(path)
    if not info["firmware_hint"]:
        raise WttError("缺少可读 Kindle 固件线索；不猜设备路线")
    for name in ("WTT", "WTT/app", "WTT/Books", "WTT/State", "WTT/.transactions", "WTT/device.json"):
        p = relative_file(path, name)
        if p.exists() and name != "WTT/device.json" and not p.is_dir():
            raise WttError("WTT 路径已被非目录占用: " + name)
    return path, info


def profile_read(path, firmware):
    p = load_json(path)
    if p.get("schema_version") != 1 or p.get("platform") != PLATFORM:
        raise WttError("不支持的设备适配配置")
    if not isinstance(p.get("model"), str) or p["model"].lower() in ("", "unknown", "待确认") or p.get("model_confirmed_by_user") is not True:
        raise WttError("先由用户核实设备型号，不能从固件版本推断型号")
    if p.get("firmware") != firmware:
        raise WttError("适配配置与当前固件线索不匹配")
    if p.get("authorized_shell_confirmed") is not True:
        raise WttError("原生应用需要已确认的设备 shell 执行权限；USB 文件复制不提供该权限")
    if p.get("refresh") != "legacy" or p.get("bits_per_pixel") != 8:
        raise WttError("当前后端仅有 legacy MXCFB / 8-bit 灰度；禁止猜测其它 ABI")
    rotation = p.setdefault("framebuffer_rotation", 0)
    if type(rotation) is not int or rotation not in (0, 3) or (rotation == 3 and (p["model"] != "PW1 Wi-Fi (B024)" or firmware != "5.6.1.1")):
        raise WttError("未适配的屏幕方向或机型")
    if not re.fullmatch(r"/dev/input/event[0-9]{1,2}", p.get("input", "")):
        raise WttError("输入设备必须来自设备实际探测")
    font = p.get("font", "")
    if not isinstance(font, str) or not font.startswith(("/usr/java/lib/fonts/", "/usr/share/fonts/")) or any(c in font for c in "\n\r\0=") or ".." in PurePosixPath(font).parts:
        raise WttError("字体必须是设备上已有的可信系统字体路径")
    if not isinstance(p.get("takeover_framework"), bool):
        raise WttError("必须明确是否接管 framework；该值不是清空设备授权")
    mode = p.setdefault("framework_mode", "restart")
    if mode not in ("restart", "keep") or (mode == "keep" and (p["model"] != "PW1 Wi-Fi (B024)" or firmware != "5.6.1.1" or rotation != 3 or not p["takeover_framework"])):
        raise WttError("keep 模式仅限已验证 PW1/5.6.1.1 且明确接管；其它配置保持 restart")
    for key in ("swap_xy", "flip_x", "flip_y"):
        if not isinstance(p.get(key), bool):
            raise WttError("触摸方向须由设备验证: " + key)
    return p


def release_read(root=PACKAGE_ROOT):
    root = Path(root)
    metadata = load_json(root / "assets/device-release.json")
    archive = relative_file(root, metadata["archive"])
    if digest(archive) != metadata["sha256"]:
        raise WttError("设备安装包摘要不一致")
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        if len(infos) > 32 or len({i.filename for i in infos}) != len(infos):
            raise WttError("设备包条目过多或重复")
        if sum(i.file_size for i in infos) > 64 * 1024 * 1024:
            raise WttError("设备包总量超过64MiB")
        for info in infos:
            rel = PurePosixPath(info.filename)
            if (info.is_dir() or rel.is_absolute() or ".." in rel.parts or "\\" in info.filename
                    or not rel.parts or stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1
                    or info.file_size > 32 * 1024 * 1024):
                raise WttError("设备包含非法条目")
        manifest = json.loads(z.read("release.json"))
        if manifest.get("schema_version") != 1 or manifest.get("platform") != PLATFORM or manifest.get("experimental") is not True:
            raise WttError("设备包平台/实验状态不匹配")
        rows = manifest["files"]
        expected = {r["path"] for r in rows}
        if len(expected) != len(rows) or expected | {"release.json"} != {i.filename for i in infos}:
            raise WttError("设备包清单与文件不一致")
        files = {}
        for row in rows:
            # Current application payload is deliberately flat and bounded.
            name = row["path"]
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,80}", name):
                raise WttError("设备应用文件名无效")
            data = z.read(name)
            if len(data) != row["size"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise WttError("设备文件摘要不一致: " + name)
            files[name] = data
        elf = files.get("wtt-reader", b"")
        if len(elf) < 52 or elf[:6] != b"\x7fELF\x01\x01" or int.from_bytes(elf[18:20], "little") != 40:
            raise WttError("阅读器不是 ARM little-endian ELF32")
        files["release.json"] = z.read("release.json")
    return metadata, manifest, files


def assert_backup(device, backup):
    result = verify_backup(backup)
    if not result["ok"]:
        raise WttError("备份不完整或读回校验失败")
    manifest = load_json(Path(backup) / "manifest.json")
    if Path(manifest["source"]).resolve() != device:
        raise WttError("备份源不是当前目标设备")
    expected = {r["path"]: r for r in manifest["files"] if not ignored(r["path"])}
    current, issues = inventory(device)
    if issues or {n for n in current if not ignored(n)} != set(expected):
        raise WttError("设备文件清单已变化或不可读；先重新备份")
    for name, row in expected.items():
        p = relative_file(device, name)
        if p.stat().st_size != row["size"] or digest(p) != row["sha256"]:
            raise WttError("设备内容与备份不一致，先重新备份: " + name)
    return result


def appledouble(path):
    """Recognize bounded macOS FAT metadata; never exempt arbitrary dot files."""
    if not path.name.startswith("._") or path.is_symlink():
        return False
    info = path.lstat()
    companion = path.with_name(path.name[2:])
    if not stat.S_ISREG(info.st_mode) or not 26 <= info.st_size <= 128*1024 or not companion.exists() or companion.is_symlink():
        return False
    data = path.read_bytes()
    if data[:8] != bytes.fromhex("0005160700020000"):
        return False
    count = int.from_bytes(data[24:26], "big")
    end = 26 + 12*count
    if not 1 <= count <= 32 or end > len(data):
        return False
    for i in range(count):
        _, offset, size = struct.unpack_from(">III", data, 26+12*i)
        if offset < end or offset+size > len(data):
            return False
    return True


def tree_hashes(folder):
    if not folder.exists():
        return None
    records, issues = inventory(folder)
    if issues:
        raise WttError("应用目录含不可读文件/链接")
    return {name: digest(relative_file(folder, name)) for name in sorted(records) if not appledouble(relative_file(folder, name))}


def identity(device):
    p = device / "WTT/device.json"
    if not p.exists():
        return None
    value = load_json(p)
    if value.get("schema_version") != 1 or not re.fullmatch(r"[0-9a-f]{32}", value.get("device_id", "")):
        raise WttError("设备身份记录无效")
    return value["device_id"]


def transaction(device, transaction_id):
    if not re.fullmatch(r"[0-9a-f]{32}", transaction_id):
        raise WttError("事务编号无效")
    folder = relative_file(device, "WTT/.transactions/" + transaction_id)
    journal = load_json(relative_file(folder, "journal.json"))
    if journal.get("transaction_id") != transaction_id or journal.get("device_id") != identity(device):
        raise WttError("事务与当前设备身份不匹配")
    return folder, journal


def pending_transactions(device):
    base = device / "WTT/.transactions"
    pending = []
    if base.is_dir():
        for p in base.iterdir():
            if appledouble(p):
                continue
            if p.is_symlink() or not p.is_dir():
                raise WttError("事务目录含非法路径")
            _, j = transaction(device, p.name)
            if j["status"] not in ("committed", "rolled_back", "aborted"):
                pending.append(p.name)
    return pending


def install_plan(device, profile, backup, root=PACKAGE_ROOT, require_mount=True):
    device, info = target(device, require_mount)
    _, release, _ = release_read(root)
    blockers = []
    p = None
    try:
        p = profile_read(profile, info["firmware_hint"]) if profile else None
        if not p:
            blockers.append("device_profile_required")
    except (OSError, ValueError, WttError) as exc:
        blockers.append(str(exc))
    try:
        if backup:
            assert_backup(device, backup)
        else:
            blockers.append("verified_backup_required")
    except (OSError, ValueError, KeyError, WttError) as exc:
        blockers.append(str(exc))
    pending = pending_transactions(device)
    if pending:
        blockers.append("pending_transaction_requires_recovery")
    return {"ok": True, "command": "install-plan", "version": release["version"], "platform": PLATFORM,
            "can_deploy_experimentally": not blockers, "blockers": blockers, "pending_transactions": pending,
            "writes": ["WTT/app", "WTT/.transactions/<id>", "WTT/device.json", "WTT/Books (create only)", "WTT/State (create only)"],
            "preserves": ["documents", "system", "WTT/Books", "WTT/State"], "factory_reset": False,
            "device_verified": False, "device_written": False, "profile_valid": p is not None}


def config_bytes(profile):
    keys = ("input", "font", "refresh", "takeover_framework", "swap_xy", "flip_x", "flip_y", "framebuffer_rotation", "framework_mode")
    return ("\n".join(k + "=" + (str(profile[k]).lower() if isinstance(profile[k], bool) else str(profile[k])) for k in keys) + "\n").encode()


def deploy(device, state, profile, backup, confirmed=False, experimental=False, root=PACKAGE_ROOT, require_mount=True, fail_at=None):
    if not confirmed or not experimental:
        raise WttError("安装需要核对 Kindle 后 --confirm-device，并明确 --allow-experimental；不表示真机已验证")
    device, info = target(device, require_mount)
    if contained(device, state):
        raise WttError("电脑运行记录不能在设备内")
    plan = install_plan(device, profile, backup, root, require_mount)
    if plan["blockers"]:
        raise WttError("安装受阻: " + "; ".join(plan["blockers"]))
    settings = profile_read(profile, info["firmware_hint"])
    metadata, release, files = release_read(root)
    files["device.conf"] = config_bytes(settings)
    if shutil.disk_usage(device).free < sum(len(data) for data in files.values()) + 8 * 1024 * 1024:
        raise WttError("设备剩余空间不足：新应用加 8 MiB 事务余量")
    expected = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    old_hashes = tree_hashes(device / "WTT/app")
    if old_hashes == expected:
        return {"ok": True, "command": "install", "status": "already_installed", "device_written": False,
                "version": release["version"], "device_verified": False}
    if old_hashes is not None:
        marker = device / "WTT/app/release.json"
        if not marker.is_file() or load_json(marker).get("application") != "wtt-reader":
            raise WttError("WTT/app 已有非 WTT 文件；不覆盖")
        # Only a previously committed, unmodified WTT installation may be replaced.
        known = False
        base = device / "WTT/.transactions"
        for folder in base.iterdir() if base.exists() else []:
            if appledouble(folder):
                continue
            _, journal = transaction(device, folder.name)
            if journal["status"] == "committed" and journal["new_hashes"] == old_hashes:
                known = True
        if not known:
            raise WttError("现有应用无匹配事务或已修改，先检查，禁止覆盖")
    state = private_dir(state)
    wtt = device / "WTT"
    wtt.mkdir(exist_ok=True)
    for name in ("Books", "State", ".transactions"):
        (wtt / name).mkdir(exist_ok=True)
    device_id = identity(device)
    if not device_id:
        device_id = uuid.uuid4().hex
        write_json(wtt / "device.json", {"schema_version": 1, "device_id": device_id})
    txid = uuid.uuid4().hex
    folder = wtt / ".transactions" / txid
    folder.mkdir()
    journal = {"schema_version": 1, "transaction_id": txid, "device_id": device_id, "status": "preparing",
               "at": timestamp(), "version": release["version"], "archive_sha256": metadata["sha256"],
               "old_hashes": old_hashes, "new_hashes": expected, "device_verified": False}
    write_json(folder / "journal.json", journal)
    stage = folder / "new-app"
    try:
        stage.mkdir()
        for name, data in files.items():
            path = stage / name
            with path.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            path.chmod(0o755 if name in ("wtt-reader", "start.sh") else 0o644)
        if tree_hashes(stage) != expected:
            raise WttError("暂存应用读回校验失败")
        if fail_at == "staged":
            raise OSError("injected staged failure")
        journal["status"] = "swapping"
        write_json(folder / "journal.json", journal)
        if old_hashes is not None:
            os.rename(wtt / "app", folder / "old-app")
        if fail_at == "old_moved":
            raise OSError("injected swap failure")
        os.rename(stage, wtt / "app")
        if tree_hashes(wtt / "app") != expected:
            raise WttError("安装后应用摘要不一致")
        journal["status"] = "committed"
        write_json(folder / "journal.json", journal)
    except (OSError, WttError):
        recover(device, txid, confirmed=True, require_mount=require_mount)
        raise
    result = {"ok": True, "command": "install", "status": "installed_files", "transaction_id": txid,
              "version": release["version"], "device_written": True, "device_verified": False,
              "reader_started": False, "factory_reset": False, "next": "安全弹出 USB 后，用已授权设备 shell 执行 sh /mnt/us/WTT/app/start.sh；真机验收另行记录"}
    write_json(state / ("install-" + txid + ".json"), {**result, "device_id": device_id})
    # A USB deployment receipt alone must not switch auto routing to transfer.
    return result


def restore(device, folder, journal):
    app = device / "WTT/app"
    current = tree_hashes(app)
    old = journal["old_hashes"]
    saved = folder / "old-app"
    if current is not None and current not in (journal["new_hashes"], old):
        raise WttError("部署后应用被修改，停止恢复，避免覆盖用户内容")
    if saved.exists():
        if tree_hashes(saved) != old:
            raise WttError("旧应用回滚副本摘要不一致")
        if app.exists():
            if (folder / "removed-app").exists():
                raise WttError("回滚暂存位置冲突")
            os.rename(app, folder / "removed-app")
        os.rename(saved, app)
    elif old is None:
        if app.exists():
            os.rename(app, folder / "removed-app")
    elif current != old:
        raise WttError("旧应用副本缺失，不能恢复")
    if tree_hashes(app) != old:
        raise WttError("恢复后摘要与原应用不一致")
    journal["status"] = "rolled_back"
    write_json(folder / "journal.json", journal)
    return {"ok": True, "command": "rollback", "transaction_id": journal["transaction_id"],
            "status": "rolled_back", "device_written": True, "books_preserved": True, "factory_reset": False}


def recover(device, txid, confirmed=False, require_mount=True):
    if not confirmed:
        raise WttError("恢复需核对目标后 --confirm-device")
    device, _ = target(device, require_mount)
    folder, journal = transaction(device, txid)
    if journal["status"] == "rolled_back":
        return {"ok": True, "status": "already_rolled_back", "device_written": False}
    if journal["status"] not in ("preparing", "swapping", "committed"):
        raise WttError("事务状态不能恢复")
    return restore(device, folder, journal)


def inspect_install(device, require_mount=True):
    device, info = target(device, require_mount)
    current = tree_hashes(device / "WTT/app")
    pending = pending_transactions(device)
    matches = []
    base = device / "WTT/.transactions"
    for folder in base.iterdir() if base.exists() else []:
        if appledouble(folder):
            continue
        _, journal = transaction(device, folder.name)
        if journal["status"] == "committed" and journal["new_hashes"] == current:
            matches.append(journal["transaction_id"])
    return {"ok": True, "command": "inspect-install", "installed_files": current is not None,
            "receipt_matches_files": bool(matches), "transactions": matches, "pending_transactions": pending,
            "firmware_hint": info["firmware_hint"], "device_verified": False, "reader_started": False, "device_written": False}
