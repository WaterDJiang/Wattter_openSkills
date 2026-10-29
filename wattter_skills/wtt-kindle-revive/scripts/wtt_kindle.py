#!/usr/bin/env python3
"""WTT Kindle host tools: preparation, routing and backed-up application deployment."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone, timedelta
import uuid
import zipfile

if __name__ == "__main__":
    sys.modules["wtt_kindle"] = sys.modules[__name__]

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.15.0"
LEGACY_ACTIONS = {"wifi-pair","wifi-status","wifi-send","wifi-cancel","install-plan","install","inspect-install","rollback","recover-install","launcher-install"}
AVAILABLE = ["scan","backup","verify-backup","status","plan","verify-package","diagnose",
             "bootstrap-fetch","bootstrap-serve","bootstrap-plan","bootstrap-prepare","bootstrap-repair","bootstrap-check","bootstrap-cleanup"]


class WttError(Exception):
    pass


def timestamp():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def private_dir(path):
    path = Path(path).expanduser()
    resolved = path.resolve()
    if resolved in (Path("/"), Path.home().resolve()) or contained(PACKAGE_ROOT, resolved) or contained(Path("/Volumes"), resolved):
        raise WttError("运行目录必须是电脑上的独立私有目录，不能是根目录、个人目录本身、技能包或设备盘")
    # Do not follow an existing symlink when placing private runtime data.
    for item in [path, *path.parents]:
        if item.is_symlink():
            raise WttError("运行目录不能包含符号链接")
    if path.exists() and not (path / ".wtt-state").is_file() and any(path.iterdir()):
        raise WttError("运行目录已有其它文件；请选择新的 WTT 专用目录")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)
    marker = path / ".wtt-state"
    if not marker.exists():
        fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
    return path.resolve()


def write_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def load_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def contained(root, target):
    return Path(target).resolve().is_relative_to(Path(root).resolve())


def relative_file(root, name):
    rel = PurePosixPath(name)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts or "\\" in name:
        raise WttError("清单含无效相对路径")
    target = Path(root).joinpath(*rel.parts)
    if not contained(root, target) or any(p.is_symlink() for p in [target, *target.parents] if contained(root, p)):
        raise WttError("清单路径越界或包含符号链接")
    return target


def inspect_volume(path):
    path = Path(path)
    evidence = []
    firmware_hint = None
    version_file = path / "system" / "version.txt"
    if version_file.is_file() and not version_file.is_symlink() and contained(path, version_file):
        with version_file.open("rb") as stream:
            text = stream.read(16384).decode("utf-8", "replace")
        if "kindle" in text.lower():
            evidence.append("system/version.txt 包含 Kindle 标识")
            match = re.search(r"\b(5(?:\.\d+){1,5})\b", text)
            firmware_hint = match.group(1) if match else None
    if "kindle" in path.name.lower():
        evidence.append("卷名包含 Kindle（仅为线索）")
    return {"mount": str(path), "label": path.name, "is_mount": os.path.ismount(path),
            "kindle_hint": bool(evidence), "evidence": evidence,
            "model": None, "firmware_hint": firmware_hint, "firmware_verified": False,
            "free_bytes": shutil.disk_usage(path).free}


def scan(state, volumes_root=None):
    report = {"ok": True, "command": "scan", "at": timestamp(), "host": platform.system(),
              "device_found": False, "candidates": [], "usb_devices": [], "diagnostics": []}
    if platform.system() != "Darwin":
        report["diagnostics"].append("当前自动扫描仅验证 macOS；其它主机待适配")
    else:
        volumes = Path(volumes_root) if volumes_root is not None else Path("/Volumes")
        if volumes.exists():
            for path in sorted(volumes.iterdir()):
                if path.is_symlink() or not path.is_dir() or not os.path.ismount(path):
                    continue
                try:
                    candidate = inspect_volume(path)
                    if candidate["kindle_hint"]:
                        report["candidates"].append(candidate)
                except OSError as exc:
                    report["diagnostics"].append({"command": "inspect mounted volume", "error": str(exc)})
        command = ["system_profiler", "SPUSBDataType", "-json"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=20)
            if result.returncode:
                report["diagnostics"].append({"command": " ".join(command), "error": result.stderr.strip(), "exit_code": result.returncode})
            else:
                def walk(item):
                    if isinstance(item, dict):
                        fields = ("_name", "manufacturer", "vendor_id", "product_id")
                        label = " ".join(str(item.get(k, "")) for k in fields).lower()
                        if any(s in label for s in ("kindle", "amazon", "0x1949")):
                            report["usb_devices"].append({k: item[k] for k in fields if k in item})
                        for value in item.values():
                            walk(value)
                    elif isinstance(item, list):
                        for value in item:
                            walk(value)
                walk(json.loads(result.stdout))
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            report["diagnostics"].append({"command": " ".join(command), "error": str(exc)})
    report["device_found"] = bool(report["candidates"] or report["usb_devices"])
    report["next"] = "核对实际型号/固件与 USB 文件访问方式" if report["device_found"] else "等待 Kindle 充电开机，确认数据线与 USB 文件连接后重扫"
    write_json(private_dir(state) / "scan.json", report)
    return report


MACOS_VOLUME_METADATA = (".Spotlight-V100", ".fseventsd", ".Trashes", ".DS_Store")


def inventory(source, exclude_roots=()):
    records, issues = {}, []
    def onerror(exc):
        issues.append({"error": str(exc)})
    for folder, directories, names in os.walk(source, followlinks=False, onerror=onerror):
        parent = Path(folder)
        if parent == source:
            directories[:] = [n for n in directories if n not in exclude_roots]
            names = [n for n in names if n not in exclude_roots]
        for name in list(directories):
            item = parent / name
            if item.is_symlink():
                directories.remove(name)
                issues.append({"path": item.relative_to(source).as_posix(), "error": "symlink directory skipped"})
        for name in names:
            item = parent / name
            rel = item.relative_to(source).as_posix()
            try:
                info = item.lstat()
                if not stat.S_ISREG(info.st_mode) or not contained(source, item):
                    issues.append({"path": rel, "error": "symlink/special/outside file skipped"})
                    continue
                records[rel] = (info.st_size, info.st_mtime_ns, info.st_ino)
            except OSError as exc:
                issues.append({"path": rel, "error": str(exc)})
    return records, issues


def backup_device(source, state, confirmed=False, require_mount=True):
    source = Path(source).expanduser()
    if not confirmed:
        raise WttError("必须先核对目标为用户的 Kindle，再提供 --confirm-device")
    if source.is_symlink() or not source.is_dir() or source.resolve() == Path("/"):
        raise WttError("源设备目录无效")
    source = source.resolve()
    if require_mount and not os.path.ismount(source):
        raise WttError("源不是已挂载设备；MTP/其它协议尚未实现，不能当普通目录备份")
    state_path = Path(state).expanduser()
    if contained(source, state_path):
        raise WttError("运行目录/备份目的地不能位于源设备内")
    state_path = private_dir(state_path)
    before, issues = inventory(source, exclude_roots=MACOS_VOLUME_METADATA)
    needed = sum(item[0] for item in before.values())
    if shutil.disk_usage(state_path).free < needed + 16 * 1024 * 1024:
        raise WttError("电脑备份空间不足：需用户分区文件总量加 16 MiB 余量")
    backup_root = state_path / ("backup-" + datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
    backup_root.mkdir(mode=0o700)
    data_root = backup_root / "data"
    data_root.mkdir(mode=0o700)
    files = []
    for rel, original in sorted(before.items()):
        try:
            src = relative_file(source, rel)
            target = data_root.joinpath(*PurePosixPath(rel).parts)
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            fd = os.open(src, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            h = hashlib.sha256()
            size = 0
            with os.fdopen(fd, "rb") as inp, target.open("xb") as out:
                target.chmod(0o600)
                for block in iter(lambda: inp.read(1024 * 1024), b""):
                    out.write(block)
                    h.update(block)
                    size += len(block)
                out.flush()
                os.fsync(out.fileno())
                current = os.fstat(inp.fileno())
            if (current.st_size, current.st_mtime_ns, current.st_ino) != original or size != original[0]:
                raise WttError("source changed while copying")
            if digest(target) != h.hexdigest():
                raise WttError("backup readback hash mismatch")
            files.append({"path": rel, "size": size, "sha256": h.hexdigest()})
        except (OSError, WttError) as exc:
            issues.append({"path": rel, "error": str(exc)})
    after, after_issues = inventory(source, exclude_roots=MACOS_VOLUME_METADATA)
    issues.extend(after_issues)
    if before != after:
        issues.append({"error": "source inventory changed during backup"})
    complete = not issues and len(files) == len(before)
    manifest = {"schema_version": 1, "at": timestamp(), "scope": "accessible_user_partition_files_only",
                "excluded_roots": list(MACOS_VOLUME_METADATA),
                "not_preserved": ["system_partitions", "original_permissions", "empty_directories", "extended_attributes", "macos_volume_metadata"],
                "complete": complete, "source": str(source), "files": files, "issues": issues}
    write_json(backup_root / "manifest.json", manifest)
    result = {"ok": complete, "command": "backup", "backup_complete": complete,
              "backup": str(backup_root), "files": len(files), "bytes": sum(f["size"] for f in files),
              "issues": len(issues), "system_image": False}
    write_json(state_path / "backup.json", result)
    return result


def verify_backup(folder):
    folder = Path(folder).expanduser()
    if folder.is_symlink() or (folder / "manifest.json").is_symlink():
        raise WttError("备份目录或清单不能是符号链接")
    manifest = load_json(folder / "manifest.json")
    errors = []
    seen = set()
    for item in manifest["files"]:
        try:
            if item["path"] in seen:
                raise WttError("duplicate manifest path")
            seen.add(item["path"])
            target = relative_file(folder / "data", item["path"])
            if target.stat().st_size != item["size"] or digest(target) != item["sha256"]:
                raise WttError("size/hash mismatch")
        except (OSError, WttError) as exc:
            errors.append({"path": item["path"], "error": str(exc)})
    return {"ok": manifest["complete"] and not errors, "command": "verify-backup",
            "backup_complete": manifest["complete"], "verified_files": len(manifest["files"]) - len(errors),
            "errors": errors, "system_image": False}


def package_components(root=PACKAGE_ROOT):
    manifest = load_json(Path(root) / "components.json")
    missing = []
    for component in manifest["components"]:
        if not component.get("required_for_revival"):
            continue
        ready = component.get("status") == "verified" and bool(component.get("verified_devices"))
        artifact = component.get("artifact")
        if ready and artifact:
            try:
                ready = digest(relative_file(root, artifact)) == component.get("sha256")
            except (OSError, WttError):
                ready = False
        else:
            ready = False
        if not ready:
            missing.append(component["id"])
    return manifest, missing


def workflow_route(state, mode, missing):
    if mode not in ("auto", "revive", "transfer"):
        raise WttError("无效工作模式")
    record_path = Path(state).expanduser() / "device.json"
    if record_path.is_symlink():
        raise WttError("设备记录不能是符号链接")
    record = load_json(record_path) if record_path.is_file() else {}
    if not isinstance(record, dict):
        raise WttError("设备记录必须为对象")
    pairing = record.get("wifi_pairing", {})
    if not isinstance(pairing, dict):
        raise WttError("无线配对记录格式无效")
    identity = record.get("device_id")
    valid = record.get("schema_version") == 1 and isinstance(identity, str) and bool(identity.strip())
    initialized = valid and record.get("initialization_verified") is True
    paired = (valid and pairing.get("device_id") == identity and pairing.get("status") == "paired"
              and isinstance(pairing.get("peer_fingerprint"), str) and bool(pairing["peer_fingerprint"].strip()))
    selected = mode if mode != "auto" else ("transfer" if initialized or paired else "choose")
    blockers = []
    if selected == "transfer":
        requirements = ["wifi-transfer"]
        actions = ["check_book_file", "check_pairing", "discover_device", "verify_live_device_identity",
                   "check_receiver", "send_temporary_file", "verify_sha256", "refresh_library"]
        if not paired:
            blockers.append("pairing_required")
        next_step = "只检查现有配对与无线接收；模块/连接缺失时停止传书，不转入复活或重置"
    elif selected == "revive":
        requirements = ["device-reader", "weread-integration", "wifi-transfer", "device-deployment"]
        actions = (["inspect_existing_installation", "verify_existing_capabilities"] if initialized else
                   ["scan_usb", "backup", "verify_backup", "match_device", "prepare_components", "deploy", "pair", "verify_reading"])
        next_step = ("已有初始化记录，先检查现有安装，不默认重新部署或清空" if initialized else
                     "执行复活准备：扫描、备份与适配；组件未齐全时停止部署")
    else:
        requirements, actions = [], []
        next_step = "请选择首次复活/修复，还是给现有 Kindle Wi-Fi 传书；不会自动重置"
    missing_for_mode = [name for name in requirements if name in missing]
    blockers.extend(missing_for_mode)
    return {"requested_mode": mode, "mode": selected, "requires_mode_choice": selected == "choose",
            "initialization_record_verified": bool(initialized), "pairing_record_present": bool(paired),
            "required_components_for_mode": requirements, "missing_components_for_mode": missing_for_mode,
            "planned_actions": actions, "blockers": blockers, "reset_allowed": False,
            "live_identity_verified": False, "next": next_step}


def status(state, root=PACKAGE_ROOT, mode="auto"):
    components, missing = package_components(root)
    state = Path(state).expanduser()
    scan_report = load_json(state / "scan.json") if (state / "scan.json").is_file() else None
    backup_report = load_json(state / "backup.json") if (state / "backup.json").is_file() else None
    route = workflow_route(state, mode, missing)
    payloads = {}
    for item in components.get("components", []):
        if item.get("id") in ("device-reader", "device-deployment") and item.get("artifact"):
            try:
                payloads[item["id"]] = digest(relative_file(root, item["artifact"])) == item.get("sha256")
            except (OSError, WttError):
                payloads[item["id"]] = False
    application_available = payloads.get("device-reader", False) and payloads.get("device-deployment", False)
    return {"ok": True, "version": VERSION, "command": "status", "available_actions": AVAILABLE,
            "preparation_ready": True, "revival_ready": False, "deployment_supported": application_available,
            "deployment_scope": "pinned_koreader_wtt_ui", "device_application_available": application_available and not components.get("upstream_fetch_required", False), "upstream_fetch_required": components.get("upstream_fetch_required", False), "implementation_route": components.get("implementation_route", "legacy_native"),
            "deployment_requires_device_profile": False, "deployment_requires_verified_execution": True, "hardware_verified": False,
            "device_scan_recorded": scan_report is not None,
            "backup_recorded_complete": bool(backup_report and backup_report.get("backup_complete")),
            "missing_components": missing, "missing_components_semantics": "global_hardware_verification_not_missing_installation_files", "package_stage": components["package_stage"],
            "transfer_supported": False, "transfer_client_available": (Path(root)/"scripts/wtt_transfer.py").is_file(), "live_transfer_requires_handshake": True, "route": route, "next": route["next"]}


def verify_package(root=PACKAGE_ROOT):
    root = Path(root)
    manifest = load_json(root / "package-manifest.json")
    expected = {row["path"] for row in manifest["files"]}
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and p.relative_to(root).as_posix() != "package-manifest.json"
              and p.name != ".DS_Store" and "__pycache__" not in p.parts}
    if expected != actual:
        raise WttError("包文件清单与当前文件不一致")
    for row in manifest["files"]:
        if digest(relative_file(root, row["path"])) != row["sha256"]:
            raise WttError("包文件摘要不一致: " + row["path"])
    return {"ok": True, "command": "verify-package", "verified_files": len(expected),
            "note": "仅验证内容完整性，不表示设备功能已实现或来源签名认证"}


def main():
    parser = argparse.ArgumentParser(description="WTT Kindle 单 Skill 包：设备只读扫描、用户分区备份与就绪检查")
    parser.add_argument("--state-dir", type=Path, default=Path.home() / "Library/Application Support/WTT/Kindle")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    for command in ("scan", "verify-package", "bootstrap-fetch"):
        commands.add_parser(command)
    for command in ("status", "plan"):
        mode_parser = commands.add_parser(command)
        mode_parser.add_argument("--mode", choices=("auto", "revive", "transfer"), default="auto")
    diag = commands.add_parser("diagnose")
    diag.add_argument("--device",type=Path);diag.add_argument("--log",type=Path)
    diag.add_argument("--mode",choices=("auto","revive","transfer"),default="auto")
    backup = commands.add_parser("backup")
    backup.add_argument("--device", type=Path, required=True)
    backup.add_argument("--confirm-device", action="store_true")
    verify = commands.add_parser("verify-backup")
    verify.add_argument("--backup", type=Path, required=True)
    server = commands.add_parser("bootstrap-serve")
    server.add_argument("--bind", required=True)
    server.add_argument("--port", type=int, default=80)
    server.add_argument("--timeout", type=int, default=900)
    for command in ("bootstrap-plan", "bootstrap-prepare", "bootstrap-repair", "bootstrap-check", "bootstrap-cleanup", "launcher-install"):
        item = commands.add_parser(command)
        item.add_argument("--device", type=Path, required=True)
        if command == "bootstrap-check":
            item.add_argument("--framework-mode", choices=("restart", "keep"), default="restart")
        if command in ("bootstrap-plan", "bootstrap-prepare"):
            item.add_argument("--backup", type=Path, required=command == "bootstrap-prepare")
        if command in ("bootstrap-prepare", "bootstrap-repair", "bootstrap-cleanup", "launcher-install"):
            item.add_argument("--confirm-device", action="store_true")
        if command == "bootstrap-repair":
            item.add_argument("--airplane-confirmed", action="store_true")
        if command == "bootstrap-prepare":
            item.add_argument("--airplane-confirmed", action="store_true")
            item.add_argument("--jb", type=Path, required=True)
            item.add_argument("--wb", type=Path, required=True)
    for command in ("install-plan", "install", "inspect-install", "rollback", "recover-install"):
        item = commands.add_parser(command)
        item.add_argument("--device", type=Path, required=True)
        if command in ("install", "install-plan"):
            item.add_argument("--profile", type=Path, required=command == "install")
            item.add_argument("--backup", type=Path, required=command == "install")
        if command in ("install", "rollback", "recover-install"):
            item.add_argument("--confirm-device", action="store_true")
        if command == "install":
            item.add_argument("--allow-experimental", action="store_true")
        if command in ("rollback", "recover-install"):
            item.add_argument("--transaction", required=True)
    pair = commands.add_parser("wifi-pair")
    pair.add_argument("--device", type=Path, required=True)
    pair.add_argument("--confirm-device", action="store_true")
    for command in ("wifi-status", "wifi-send", "wifi-cancel"):
        item = commands.add_parser(command)
        item.add_argument("--host")
        item.add_argument("--port", type=int)
        item.add_argument("--task", required=command == "wifi-cancel")
        if command == "wifi-send":
            item.add_argument("--file", type=Path, required=True)
            item.add_argument("--name")
    args = parser.parse_args()
    try:
        if args.command in LEGACY_ACTIONS:
            result={"ok":False,"command":args.command,"code":"legacy_route_removed","device_written":False,
                    "next":"旧C/TLS路线已归档。当前安装/修复使用wtt_koreader.py或wtt_ui.py，传书使用wtt_transfer.py；先diagnose，不自动迁移或执行。"}
        elif args.command == "diagnose":
            from wtt_diagnose import diagnose
            result=diagnose(args.state_dir,args.device,args.log,args.mode)
        elif args.command == "scan":
            result = scan(args.state_dir)
        elif args.command == "backup":
            result = backup_device(args.device, args.state_dir, args.confirm_device)
        elif args.command == "verify-backup":
            result = verify_backup(args.backup)
        elif args.command == "verify-package":
            result = verify_package()
        elif args.command.startswith("bootstrap-") or args.command == "launcher-install":
            import wtt_bootstrap as boot
            if args.command == "bootstrap-fetch":
                result = boot.fetch(args.state_dir)
            elif args.command == "bootstrap-serve":
                result = boot.serve(args.state_dir, args.bind, args.port, args.timeout)
            elif args.command == "bootstrap-plan":
                result = boot.plan(args.device, args.state_dir, args.backup)
            elif args.command == "bootstrap-prepare":
                verify_package()
                result = boot.prepare(args.device, args.state_dir, args.backup, args.jb, args.wb,
                                      args.confirm_device, args.airplane_confirmed)
            elif args.command == "bootstrap-check":
                result = boot.check(args.device, args.state_dir, framework_mode=args.framework_mode)
            elif args.command == "bootstrap-repair":
                verify_package()
                result = boot.repair(args.device, args.state_dir, args.confirm_device, args.airplane_confirmed)
            elif args.command == "bootstrap-cleanup":
                result = boot.cleanup(args.device, args.state_dir, args.confirm_device)
            else:
                verify_package()
                result = boot.launcher(args.device, args.state_dir, args.confirm_device)
        else:
            result = status(args.state_dir, mode=args.mode)
            result["command"] = args.command
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 3
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, WttError) as exc:
        print(json.dumps({"ok": False, "command": args.command, "error": str(exc),
                          "device_written": None if args.command in ("install", "rollback", "recover-install", "bootstrap-prepare", "bootstrap-repair", "bootstrap-cleanup", "launcher-install", "wifi-pair", "wifi-send", "wifi-cancel") else False,
                          "next": "先 inspect-install 核对事务；不能由错误退出推断设备完全未写入" if args.command in ("install", "rollback", "recover-install") else "检查错误原因"}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
