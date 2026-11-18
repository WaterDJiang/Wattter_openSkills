#!/usr/bin/env python3
"""
backfill_knowledge_date.py — 存量 wiki 批量回填 knowledge_date（知识发生时间）

用法：
    python3 backfill_knowledge_date.py {target_dir} --dry-run   # 先看计划（必跑）
    python3 backfill_knowledge_date.py {target_dir}             # 正式执行，幂等可重跑

推断优先级（references/knowledge-freshness.md 第 3 节）：
    1. source_files 中 raw 文件名的日期前缀（YYYYMMDD_ / YYYY-MM-DD）取最早 → exact，不写 basis
    2. raw 文件实际存在 → 文件修改时间 → approximate
    3. frontmatter 已有 created / last_compiled / date → approximate
    4. 都没有 → 跳过，进"无法推断"清单

流程铁律：--dry-run 看清单 → 抽查 2-3 个文件的实际 diff → 正式执行 → 再抽查。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

INLINE_LIST_RE = re.compile(r"^\w+:\s*\[.*\]\s*$")

# 知识卡片识别：按目录归类，note 卡用已有 date，不回填
KNOWLEDGE_DIRS = ("kps", "cases", "models", "concepts", "materials")
NOTE_DIRS = ("notes",)


def read_fm_lines(text: str) -> list[str] | None:
    """返回 frontmatter 内容行（不含两道 ---）；无 frontmatter 返回 None。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None


def parse_fm_dict(fm_lines: list[str]) -> dict:
    """极简解析：支持行内 list 与块 list（source_files 常见两种写法都要认）。"""
    fm: dict = {}
    current_key = None
    for line in fm_lines:
        stripped = line.strip()
        if stripped.startswith("- ") and current_key:
            fm[current_key].append(stripped[2:].strip().strip('"').strip("'"))
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value == "":
            fm[key] = []
            current_key = key
            continue
        current_key = None
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            fm[key] = [v.strip().strip('"').strip("'") for v in inner.split(",")] if inner else []
        else:
            fm[key] = value.strip('"').strip("'")
    return fm


def extract_dates_from_name(name: str) -> list[str]:
    """从文件名抽 YYYYMMDD / YYYY-MM-DD，统一为 YYYY-MM-DD。"""
    out = []
    for m in re.finditer(r"(\d{8})", name):
        out.append(f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}")
    for m in re.finditer(r"(\d{4}-\d{2}-\d{2})", name):
        out.append(m.group(1))
    return out


def infer_date(fm: dict, f: Path, target: Path) -> tuple[str, str] | None:
    """返回 (date, basis) 或 None。"""
    # 1. source_files 文件名日期前缀，取最早 → exact
    candidates: list[str] = []
    raw_paths = fm.get("source_files", [])
    if isinstance(raw_paths, str):
        raw_paths = [raw_paths]
    for rp in raw_paths:
        candidates.extend(extract_dates_from_name(Path(str(rp)).name))
    if candidates:
        return min(candidates), "exact"
    # 2. raw 文件 mtime → approximate
    for rp in raw_paths:
        raw_file = target / str(rp)
        if raw_file.exists():
            mtime = datetime.fromtimestamp(raw_file.stat().st_mtime)
            return mtime.strftime("%Y-%m-%d"), "approximate"
    # 3. 已有时间字段兜底 → approximate
    for key in ("created", "last_compiled", "date"):
        v = fm.get(key)
        if v and re.match(r"^\d{4}-\d{2}-\d{2}", str(v)):
            return str(v)[:10], "approximate"
    return None


def insert_field(fm_lines: list[str], entries: list[str]) -> list[str]:
    """在 knowledge_type 行（或 *_name 行，或 fm 开头）之后插入字段，只加行不动行。"""
    anchor = None
    for i, line in enumerate(fm_lines):
        if re.match(r"^knowledge_type:", line):
            anchor = i
            break
    if anchor is None:
        for i, line in enumerate(fm_lines):
            if re.match(r"^\w*name:", line):
                anchor = i
                break
    pos = (anchor + 1) if anchor is not None else 0
    return fm_lines[:pos] + entries + fm_lines[pos:]


def main() -> int:
    parser = argparse.ArgumentParser(description="批量回填 knowledge_date")
    parser.add_argument("target", type=Path, help="目标目录（含 wiki/）")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不写文件")
    args = parser.parse_args()

    target = args.target.resolve()
    wiki_dir = target / "wiki"
    if not wiki_dir.exists():
        print(json.dumps({"error": f"未找到 {wiki_dir}"}, ensure_ascii=False))
        return 2

    today = datetime.now(timezone.utc).date()
    plan, skipped, unresolvable, invalid = [], [], [], []
    for f in sorted(wiki_dir.rglob("*.md")):
        if f.name.startswith("_") or f.name == "index.md" or "indexes" in f.parts:
            continue
        if not any(d in f.parts for d in KNOWLEDGE_DIRS + NOTE_DIRS):
            continue
        if any(d in f.parts for d in NOTE_DIRS):
            skipped.append((str(f.relative_to(target)), "note 卡用 date，不回填"))
            continue
        fm_lines = read_fm_lines(f.read_text(encoding="utf-8"))
        if fm_lines is None:
            skipped.append((str(f.relative_to(target)), "无 frontmatter"))
            continue
        fm = parse_fm_dict(fm_lines)
        if fm.get("knowledge_date"):
            skipped.append((str(f.relative_to(target)), "已有 knowledge_date"))
            continue
        inferred = infer_date(fm, f, target)
        rel = str(f.relative_to(target))
        if inferred is None:
            unresolvable.append(rel)
            continue
        date, basis = inferred
        if basis == "exact" and datetime.strptime(date, "%Y-%m-%d").date() > today:
            invalid.append((rel, date, "文件名日期晚于今天，疑笔误，跳过"))
            continue
        plan.append((rel, date, basis))

    exact = [(r, d) for r, d, b in plan if b == "exact"]
    approx = [(r, d) for r, d, b in plan if b == "approximate"]

    print(f"回填计划：{len(plan)} 个文件（精确 {len(exact)} / 近似 {len(approx)}），"
          f"跳过 {len(skipped)}，无法推断 {len(unresolvable)}，可疑跳过 {len(invalid)}\n")

    print("== 精确推断（来源文件名日期前缀，不写 basis）==")
    for r, d in exact:
        print(f"  {d}  {r}")
    print("\n== 近似推断（兜底，写入 knowledge_date_basis: approximate）==")
    for r, d in approx:
        print(f"  {d}  {r}")
    if unresolvable:
        print("\n== 无法推断（需手工补）==")
        for r in unresolvable:
            print(f"  {r}")
    if invalid:
        print("\n== 可疑跳过 ==")
        for r, d, why in invalid:
            print(f"  {d}  {r}  — {why}")

    if args.dry_run:
        # 抽查示例：打印前 2 个文件将产生的 frontmatter 预览
        print("\n== 抽查示例（前 2 个文件的插入位置预览）==")
        for r, d, b in plan[:2]:
            fm_lines = read_fm_lines((target / r).read_text(encoding="utf-8"))
            if fm_lines is None:
                continue
            entries = ["knowledge_date: " + d]
            if b == "approximate":
                entries.append("knowledge_date_basis: approximate")
            print(f"--- {r} ---")
            print("\n".join(["---"] + insert_field(fm_lines, entries) + ["---"]))
        print("\n(dry-run 结束，未写入任何文件。请人工抽查上方插入位置后去掉 --dry-run 执行)")
        return 0

    changed = 0
    for r, d, b in plan:
        f = target / r
        lines = f.read_text(encoding="utf-8").splitlines()
        fm_lines = read_fm_lines("\n".join(lines))
        if fm_lines is None:
            continue
        entries = ["knowledge_date: " + d]
        if b == "approximate":
            entries.append("knowledge_date_basis: approximate")
        close = 1 + len(fm_lines)
        new_lines = ["---"] + insert_field(fm_lines, entries) + ["---"] + lines[close + 1:]
        f.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        changed += 1

    print(f"\n完成：写入 {changed} 个文件。请抽查 2-3 个文件确认无格式问题，"
          f"然后跑 python3 scan_wiki.py {target} --check L17 验证。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
