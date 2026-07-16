#!/usr/bin/env python3
"""Maintain a per-platform publishing ledger and render the final result table."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


PLATFORM_LABELS = {
    "weixin": "微信公众号",
    "weibo": "微博",
    "zhihu": "知乎",
    "csdn": "CSDN",
    "juejin": "掘金",
    "baijiahao": "百家号",
    "cnblogs": "博客园",
    "xiaohongshu": "小红书",
    "twitter": "Twitter/X",
}

STATUS_LABELS = {
    "pending": "未完成",
    "published": "已发布",
    "draft": "已创建草稿",
    "filled": "已填写待确认",
    "failed": "未完成",
    "skipped": "已跳过",
}

ALLOWED_WRITE_STATES = {
    "pending": {"not_started"},
    "published": {"published_verified"},
    "draft": {"created_verified"},
    "filled": {"created_unverified", "published_unverified", "unknown"},
    "failed": {"confirmed_not_created", "unknown"},
    "skipped": {"not_started"},
}


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def save(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(f"结果账本不存在：{path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("platforms"), dict):
        raise ValueError("结果账本格式无效")
    return data


def task_status(rows: dict[str, dict[str, object]]) -> str:
    statuses = [str(row.get("status")) for row in rows.values()]
    if any(status == "pending" for status in statuses):
        return "running"
    if statuses and all(status == "failed" for status in statuses):
        return "failed"
    if any(status in {"failed", "filled"} for status in statuses):
        return "partial"
    return "completed"


def init_ledger(args: argparse.Namespace) -> int:
    if args.file.exists() and not args.force:
        raise ValueError(f"结果账本已存在：{args.file}；如需覆盖请加 --force")
    platform_ids = [item.strip() for item in args.platforms.split(",") if item.strip()]
    if not platform_ids:
        raise ValueError("至少指定一个平台")
    unknown = [item for item in platform_ids if item not in PLATFORM_LABELS]
    if unknown:
        raise ValueError(f"不支持的平台：{', '.join(unknown)}")
    if len(set(platform_ids)) != len(platform_ids):
        raise ValueError("平台列表不能重复")

    created_at = now()
    data: dict[str, object] = {
        "schema_version": 1,
        "task_id": args.task_id or f"publish_{uuid.uuid4().hex[:12]}",
        "task_status": "running",
        "created_at": created_at,
        "updated_at": created_at,
        "platforms": {
            platform: {
                "platform": platform,
                "label": PLATFORM_LABELS[platform],
                "status": "pending",
                "write_state": "not_started",
                "provider": None,
                "item_id": None,
                "link": None,
                "detail": None,
                "error": None,
                "evidence": [],
                "attempts": [],
                "fallback_reason": None,
                "updated_at": created_at,
            }
            for platform in platform_ids
        },
    }
    save(args.file, data)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def start_attempt(args: argparse.Namespace) -> int:
    data = load(args.file)
    rows = data["platforms"]
    if args.platform not in rows:
        raise ValueError(f"平台不在本次任务中：{args.platform}")
    started_at = now()
    attempt = {
        "attempt_id": args.attempt_id or f"attempt_{uuid.uuid4().hex[:10]}",
        "provider": args.provider,
        "started_at": started_at,
        "finished_at": None,
        "duration_ms": None,
        "status": "pending",
        "write_state": "not_started",
        "error": None,
        "evidence": list(args.evidence),
        "fallback_reason": None,
    }
    rows[args.platform]["attempts"].append(attempt)
    rows[args.platform]["updated_at"] = started_at
    data["updated_at"] = started_at
    save(args.file, data)
    print(json.dumps(attempt, ensure_ascii=False, indent=2))
    return 0


def finish_attempt(args: argparse.Namespace) -> int:
    data = load(args.file)
    rows = data["platforms"]
    if args.platform not in rows:
        raise ValueError(f"平台不在本次任务中：{args.platform}")
    attempts = rows[args.platform].get("attempts") or []
    attempt = next((item for item in attempts if item.get("attempt_id") == args.attempt_id), None)
    if attempt is None:
        raise ValueError(f"attempt 不存在：{args.attempt_id}")
    if attempt.get("finished_at") and not args.force:
        raise ValueError("attempt 已结束；如需修正请加 --force")
    finished_at = now()
    duration_ms = max(0, round((parse_time(finished_at) - parse_time(str(attempt["started_at"]))).total_seconds() * 1000))
    attempt.update(
        {
            "finished_at": finished_at,
            "duration_ms": duration_ms,
            "status": args.status,
            "write_state": args.write_state,
            "error": args.error,
            "fallback_reason": args.fallback_reason,
        }
    )
    if args.evidence:
        attempt["evidence"] = list(attempt.get("evidence") or []) + args.evidence
    if args.fallback_reason:
        rows[args.platform]["fallback_reason"] = args.fallback_reason
    rows[args.platform]["updated_at"] = finished_at
    data["updated_at"] = finished_at
    save(args.file, data)
    print(json.dumps(attempt, ensure_ascii=False, indent=2))
    return 0


def update_ledger(args: argparse.Namespace) -> int:
    data = load(args.file)
    rows = data["platforms"]
    if args.platform not in rows:
        raise ValueError(f"平台不在本次任务中：{args.platform}")
    if args.write_state not in ALLOWED_WRITE_STATES[args.status]:
        allowed = ", ".join(sorted(ALLOWED_WRITE_STATES[args.status]))
        raise ValueError(f"{args.status} 不允许 write_state={args.write_state}；允许值：{allowed}")
    if args.status == "published" and not args.link:
        raise ValueError("已发布必须提供可验证公开链接")
    if args.status == "draft" and not (args.link or args.item_id):
        raise ValueError("已创建草稿必须提供草稿链接或草稿 ID")

    current = rows[args.platform]
    if not args.force:
        if current.get("status") == "published" and (
            args.status != "published" or (args.link and args.link != current.get("link"))
        ):
            raise ValueError("已验证公开结果不能被降级或替换；如确认需要修正请加 --force")
        if current.get("status") == "draft" and args.status == "draft" and (
            args.link and current.get("link") and args.link != current.get("link")
        ):
            raise ValueError("同一平台已有已验证草稿，拒绝替换为另一草稿链接")

    updated_at = now()
    current.update(
        {
            "status": args.status,
            "write_state": args.write_state,
            "provider": args.provider,
            "item_id": args.item_id,
            "link": args.link,
            "detail": args.detail,
            "error": args.error,
            "updated_at": updated_at,
        }
    )
    if args.evidence:
        current["evidence"] = list(current.get("evidence") or []) + args.evidence
    data["task_status"] = task_status(rows)
    data["updated_at"] = updated_at
    save(args.file, data)
    print(json.dumps(current, ensure_ascii=False, indent=2))
    return 0


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def render_summary(args: argparse.Namespace) -> int:
    data = load(args.file)
    rows = data["platforms"]
    pending = [row["label"] for row in rows.values() if row.get("status") == "pending"]
    if pending and args.strict:
        raise ValueError(f"仍有平台未记录最终状态：{', '.join(pending)}")

    lines = ["| 平台 | 完成情况 | 链接 |", "|---|---|---|"]
    for row in rows.values():
        completion = STATUS_LABELS[str(row.get("status"))]
        detail = row.get("detail") or row.get("error")
        if detail:
            completion += f"：{escape_cell(str(detail))}"
        link = row.get("link")
        rendered_link = f"[打开]({link})" if link else "—"
        lines.append(
            f"| {escape_cell(str(row['label']))} | {escape_cell(completion)} | {rendered_link} |"
        )
    print("\n".join(lines))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="维护多平台发布结果账本")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="创建结果账本")
    init_parser.add_argument("--file", type=Path, required=True)
    init_parser.add_argument("--platforms", required=True, help="逗号分隔的平台 ID")
    init_parser.add_argument("--task-id")
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(handler=init_ledger)

    update_parser = subparsers.add_parser("update", help="更新单个平台结果")
    update_parser.add_argument("--file", type=Path, required=True)
    update_parser.add_argument("--platform", choices=tuple(PLATFORM_LABELS), required=True)
    update_parser.add_argument("--status", choices=tuple(STATUS_LABELS), required=True)
    update_parser.add_argument("--write-state", required=True)
    update_parser.add_argument("--provider")
    update_parser.add_argument("--item-id")
    update_parser.add_argument("--link")
    update_parser.add_argument("--detail")
    update_parser.add_argument("--error")
    update_parser.add_argument("--evidence", action="append", default=[])
    update_parser.add_argument("--force", action="store_true")
    update_parser.set_defaults(handler=update_ledger)

    attempt_start_parser = subparsers.add_parser("attempt-start", help="记录 provider attempt 开始")
    attempt_start_parser.add_argument("--file", type=Path, required=True)
    attempt_start_parser.add_argument("--platform", choices=tuple(PLATFORM_LABELS), required=True)
    attempt_start_parser.add_argument("--provider", required=True)
    attempt_start_parser.add_argument("--attempt-id")
    attempt_start_parser.add_argument("--evidence", action="append", default=[])
    attempt_start_parser.set_defaults(handler=start_attempt)

    attempt_finish_parser = subparsers.add_parser("attempt-finish", help="记录 provider attempt 结果和耗时")
    attempt_finish_parser.add_argument("--file", type=Path, required=True)
    attempt_finish_parser.add_argument("--platform", choices=tuple(PLATFORM_LABELS), required=True)
    attempt_finish_parser.add_argument("--attempt-id", required=True)
    attempt_finish_parser.add_argument("--status", choices=("accepted", "success", "failed", "unknown", "skipped"), required=True)
    attempt_finish_parser.add_argument("--write-state", choices=(
        "not_started", "confirmed_not_created", "created_unverified", "created_verified",
        "published_unverified", "published_verified", "unknown",
    ), required=True)
    attempt_finish_parser.add_argument("--error")
    attempt_finish_parser.add_argument("--fallback-reason")
    attempt_finish_parser.add_argument("--evidence", action="append", default=[])
    attempt_finish_parser.add_argument("--force", action="store_true")
    attempt_finish_parser.set_defaults(handler=finish_attempt)

    summary_parser = subparsers.add_parser("summary", help="输出最终三列表格")
    summary_parser.add_argument("--file", type=Path, required=True)
    summary_parser.add_argument("--strict", action="store_true")
    summary_parser.set_defaults(handler=render_summary)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"publish-result: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
