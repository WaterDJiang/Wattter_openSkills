#!/usr/bin/env python3
"""Install or check the extension-free OpenCLI draft adapters bundled with this skill."""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "adapters"
DEFAULT_TARGET = Path.home() / ".opencli" / "clis"


def source_files() -> list[Path]:
    return sorted(path for path in SOURCE.rglob("*.js") if path.is_file())


def relative_entries(target: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in source_files():
        relative = source.relative_to(SOURCE)
        destination = target / relative
        if not destination.exists():
            status = "missing"
        elif filecmp.cmp(source, destination, shallow=False):
            status = "current"
        else:
            status = "different"
        rows.append({"file": str(relative), "destination": str(destination), "status": status})
    return rows


def install(target: Path, force: bool) -> list[dict[str, object]]:
    rows = relative_entries(target)
    conflicts = [row for row in rows if row["status"] == "different"]
    if conflicts and not force:
        names = ", ".join(str(row["file"]) for row in conflicts)
        raise ValueError(f"目标存在不同文件：{names}；确认替换请加 --force")
    for row in rows:
        source = SOURCE / str(row["file"])
        destination = Path(str(row["destination"]))
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        row["status"] = "installed"
    return rows


def registered_commands() -> list[str]:
    completed = subprocess.run(
        ["opencli", "list", "-f", "json"],
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )
    if completed.returncode != 0:
        return []
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return []
    manifest = json.loads((SOURCE / "manifest.json").read_text(encoding="utf-8"))
    expected = {
        value[field]
        for value in manifest["commands"].values()
        for field in ("command", "auth_command")
        if value.get(field)
    }
    return sorted(str(item.get("command")) for item in data if item.get("command") in expected)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="安装/检查 wtt-post-geo 登录态草稿 adapter")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="只检查，不写入")
    action.add_argument("--install", action="store_true", help="安装到 OpenCLI 私有 adapter 目录")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--force", action="store_true", help="替换目标中同名但不同的文件")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        rows = install(args.target, args.force) if args.install else relative_entries(args.target)
        result = {
            "target": str(args.target),
            "mode": "install" if args.install else "check",
            "files": rows,
            "registered_commands": registered_commands() if args.install else [],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"install-opencli-adapters: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
