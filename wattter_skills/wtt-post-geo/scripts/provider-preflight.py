#!/usr/bin/env python3
"""Resolve extension-free provider routes before any platform write begins."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "adapters" / "manifest.json"
PLATFORMS = (
    "weixin", "weibo", "zhihu", "csdn", "juejin", "baijiahao",
    "cnblogs", "xiaohongshu", "twitter",
)

BUILTIN_COMMANDS = {
    "weixin": "weixin/create-draft",
    "weibo": "weibo/publish",
    "xiaohongshu": "xiaohongshu/publish",
    "twitter": "twitter/post",
}


def run_json(command: list[str]) -> object:
    completed = subprocess.run(command, text=True, capture_output=True, check=False, timeout=20)
    if completed.returncode != 0:
        raise ValueError(f"{' '.join(command)} 失败：{completed.stderr.strip() or completed.stdout.strip()}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{' '.join(command)} 未返回 JSON") from exc


def read_registry(path: Path | None) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8")) if path else run_json(["opencli", "list", "-f", "json"])
    if not isinstance(data, list):
        raise ValueError("OpenCLI 注册表必须是数组")
    return [item for item in data if isinstance(item, dict)]


def doctor_ok(path: Path | None, skip: bool) -> tuple[bool, str]:
    if skip:
        return True, "skipped_by_flag"
    if path:
        output = path.read_text(encoding="utf-8")
        return "Everything looks good!" in output or "[OK] Connectivity" in output, "fixture"
    completed = subprocess.run(["opencli", "doctor"], text=True, capture_output=True, check=False, timeout=20)
    output = f"{completed.stdout}\n{completed.stderr}"
    return completed.returncode == 0 and ("Everything looks good!" in output or "[OK] Connectivity" in output), "live"


def account_name(data: object) -> str | None:
    if isinstance(data, list):
        for item in data:
            found = account_name(item)
            if found:
                return found
    if isinstance(data, dict):
        for key in ("account", "name", "user_name", "screen_name", "url_token", "username", "user_id", "uid", "account_id"):
            value = data.get(key)
            if value:
                return str(value)
        for value in data.values():
            found = account_name(value)
            if found:
                return found
    return None


def explicitly_unauthenticated(data: object) -> bool:
    if isinstance(data, list):
        return any(explicitly_unauthenticated(item) for item in data)
    if isinstance(data, dict):
        if data.get("logged_in") is False:
            return True
        return any(explicitly_unauthenticated(value) for value in data.values())
    return False


def probe_account(command: str) -> dict[str, object]:
    site, name = command.split("/", 1)
    try:
        completed = subprocess.run(
            ["opencli", site, name, "-f", "json"],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return {"status": "failed", "command": command, "account": None, "error": "account_probe_timeout"}
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).replace("\n", " ").strip()[:240]
        return {"status": "failed", "command": command, "account": None, "error": message or "account_probe_failed"}
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"status": "failed", "command": command, "account": None, "error": "account_probe_invalid_json"}
    account = account_name(data)
    if explicitly_unauthenticated(data) or not account:
        return {"status": "failed", "command": command, "account": None, "error": "account_not_identified"}
    return {"status": "authenticated", "command": command, "account": account, "error": None}


def probe_accounts(platforms: list[str], bundled: dict[str, object], registered: set[str]) -> dict[str, dict[str, object]]:
    results: dict[str, dict[str, object]] = {}
    jobs: dict[object, str] = {}
    with ThreadPoolExecutor(max_workers=min(5, max(1, len(platforms)))) as executor:
        for platform in platforms:
            profile = bundled.get(platform) or {}
            command = profile.get("auth_command")
            if not command:
                results[platform] = {"status": "not_configured", "command": None, "account": None, "error": None}
            elif command not in registered:
                results[platform] = {"status": "failed", "command": command, "account": None, "error": "auth_command_not_registered"}
            else:
                jobs[executor.submit(probe_account, str(command))] = platform
        for future in as_completed(jobs):
            results[jobs[future]] = future.result()
    return results


def resolve(args: argparse.Namespace) -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    bundled = manifest["commands"]
    registry = read_registry(args.registry_file)
    registered = {str(item.get("command")): item for item in registry}
    healthy, doctor_source = doctor_ok(args.doctor_file, args.skip_doctor)
    requested = [item.strip() for item in args.platforms.split(",") if item.strip()]
    unknown = [item for item in requested if item not in PLATFORMS]
    if unknown:
        raise ValueError(f"不支持的平台：{', '.join(unknown)}")
    require_images = {item.strip() for item in args.require_images.split(",") if item.strip()}
    do_account_checks = healthy and not args.skip_account_check and args.registry_file is None
    account_checks = probe_accounts(requested, bundled, set(registered)) if do_account_checks else {
        platform: {"status": "skipped", "command": (bundled.get(platform) or {}).get("auth_command"), "account": None, "error": None}
        for platform in requested
    }
    rows: dict[str, dict[str, object]] = {}
    weibo_variant = args.weibo_variant

    for platform in requested:
        candidates: list[dict[str, object]] = []
        if platform == "weixin" and args.weixin_official_api_ready:
            candidates.append({"provider": "official_api", "available": True, "command": "scripts/weixin_api_draft.py"})

        if platform in bundled and (platform != "weibo" or weibo_variant == "longform"):
            profile = bundled[platform]
            command = str(profile["command"])
            missing_images = platform in require_images and not bool(profile.get("images"))
            account_ready = account_checks[platform]["status"] in {"authenticated", "skipped", "not_configured"}
            candidates.append({
                "provider": "opencli_login_adapter",
                "command": command,
                "available": command in registered and healthy and not missing_images and account_ready,
                "reason": (
                    "missing_capability:images" if missing_images else
                    "adapter_not_registered" if command not in registered else
                    "opencli_bridge_unhealthy" if not healthy else
                    "account_not_authenticated" if not account_ready else None
                ),
            })

        builtin = BUILTIN_COMMANDS.get(platform)
        if platform == "weibo" and weibo_variant == "longform":
            builtin = None
        if builtin:
            missing_builtin_images = platform == "weibo" and platform in require_images
            candidates.append({
                "provider": "opencli_adapter",
                "command": builtin,
                "available": builtin in registered and healthy and not missing_builtin_images,
                "reason": (
                    "missing_capability:images" if missing_builtin_images else
                    "adapter_not_registered" if builtin not in registered else
                    "opencli_bridge_unhealthy" if not healthy else None
                ),
            })

        ui_command = f"opencli browser {platform}"
        if platform == "weibo" and weibo_variant == "longform":
            ui_command = "opencli browser weibo open https://card.weibo.com/article/v5/editor"
        candidates.append({
            "provider": "opencli_ui",
            "command": ui_command,
            "available": healthy,
            "reason": None if healthy else "opencli_bridge_unhealthy",
        })
        candidates.append({"provider": "manual_confirm", "command": None, "available": True, "reason": None})
        selected = next(candidate for candidate in candidates if candidate["available"])
        skipped_reasons = [candidate["reason"] for candidate in candidates if not candidate["available"] and candidate.get("reason")]
        rows[platform] = {
            "variant": weibo_variant if platform == "weibo" else None,
            "selected_provider": selected["provider"],
            "selected_command": selected["command"],
            "fallback_reason": skipped_reasons[0] if skipped_reasons else None,
            "account_check": account_checks.get(platform),
            "candidates": candidates,
        }

    return {
        "schema_version": 1,
        "extension_required": False,
        "opencli_bridge_healthy": healthy,
        "doctor_source": doctor_source,
        "platforms": rows,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成无 CSDN 插件的发布 provider 预检路由")
    parser.add_argument("--platforms", required=True, help="逗号分隔的平台 ID")
    parser.add_argument("--require-images", default="", help="本次必须自动处理图片的平台 ID")
    parser.add_argument(
        "--weibo-variant",
        choices=("short_post", "longform"),
        default="short_post",
        help="微博发布形态；默认 short_post，只有用户明确要求长文时使用 longform",
    )
    parser.add_argument("--weixin-official-api-ready", action="store_true")
    parser.add_argument("--registry-file", type=Path, help="测试用 OpenCLI 注册表 JSON")
    parser.add_argument("--doctor-file", type=Path, help="测试用 doctor 输出")
    parser.add_argument("--skip-doctor", action="store_true", help="仅用于离线规划，真实写入前禁止使用")
    parser.add_argument("--skip-account-check", action="store_true", help="仅用于离线规划，真实写入前禁止使用")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        print(json.dumps(resolve(args), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"provider-preflight: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
