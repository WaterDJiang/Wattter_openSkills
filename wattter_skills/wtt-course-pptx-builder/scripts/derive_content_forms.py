#!/usr/bin/env python3
"""
PPT Master - 页面变体内容形态派生器（layouts + decks）。

扫描 templates/layouts/ + templates/decks/ 的所有页面 SVG，从文件名关键词 +
（可选）page_catalog.json 的 item_count 信号，自动推断 page_type 与 content_form。
输出供人工复核，复核后并入 content_forms.json 的 page_variant_tags。

不是最终选型——是把"手标 181 个"降到"规则派生 + 人工复核"。

用法：
    python3 scripts/derive_content_forms.py            # 扫描 + 打印汇总
    python3 scripts/derive_content_forms.py --json     # 输出 JSON 到 stdout
    python3 scripts/derive_content_forms.py --out content_forms.page_variants.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from project_utils import SKILL_DIR  # type: ignore
except Exception:
    SKILL_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = SKILL_DIR / "templates"

# 数字词 → 数值（用于 points_N 的 N）
NUM_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10, "dual": 2, "double": 2}

# 资产类（非页面变体）—— 跳过
ASSET_PATTERNS = re.compile(r"photo_embedded|reference_style|_bg$|_logo$")

# 结构页 page_type（从文件名前缀/关键词）
STRUCTURAL = [
    (re.compile(r"cover"), "cover"),
    (re.compile(r"toc|agenda(?=.*chapter)|目录"), "toc"),
    (re.compile(r"chapter"), "chapter"),
    (re.compile(r"ending|thanks"), "ending"),
]

# 内容形态规则（有序，首匹配赢）。每条 (regex, form, base_confidence)。
# 顺序敏感：更具体的（compare/swimlane/orbit）在前，兜底（points/free）在后。
CONTENT_FORM_RULES = [
    (re.compile(r"compare|_vs_|vs_comparison|dual_circle|dual_checklist"), "compare_2col", "high"),
    (re.compile(r"swimlane"), "flow_linear", "high"),
    (re.compile(r"workflow|process_flow|_flow$|_flow_"), "flow_linear", "high"),
    (re.compile(r"_loop$|_loop_|cycle|operation_loop"), "flow_cycle", "high"),
    (re.compile(r"stage|step|chain|track|workflow"), "flow_linear", "medium"),
    (re.compile(r"orbit|radial|hub_spoke|ecosystem|segments|spoke"), "hub_spoke", "high"),
    (re.compile(r"\bgantt\b"), "gantt", "high"),
    (re.compile(r"timeline|milestone|roadmap|schedule|calendar"), "timeline", "high"),
    (re.compile(r"matrix|quadrant"), "matrix_2x2", "high"),
    (re.compile(r"org_chart|hierarchy_tree|branch_map|\btree\b"), "tree", "high"),
    (re.compile(r"layer.*stack|layered"), "pyramid", "medium"),
    (re.compile(r"kpi|gauge|dashboard|stats"), "kpi_metrics", "high"),
    (re.compile(r"agenda"), "agenda", "high"),
    (re.compile(r"team|mentor|roster"), "team", "high"),
    (re.compile(r"data_table|table"), "table", "high"),
    (re.compile(r"bullets|points|list|items|cards|grid|wall|scene|gallery|award|honor|module_grid"), "points", "medium"),
    (re.compile(r"blank|canvas|text_canvas|overview_panel|split"), "free", "low"),
]


def parse_count(name: str) -> int | None:
    """从文件名解析要点数。按 token（_ / 数字 分割）匹配数字词，避免 'content' 含 'ten' 误匹配。"""
    low = name.lower()
    tokens = re.split(r"[\W_]+|\d+", low)
    for tok in tokens:
        if tok in NUM_WORDS:
            return NUM_WORDS[tok]
    # 无数字词时，找独立的 2-9 数字（如 _4_ / _4col）
    m = re.search(r"(?<![0-9])([2-9])(?![0-9])", low)
    return int(m.group(1)) if m else None


def classify(name: str) -> dict:
    """文件名（无扩展名）→ {page_type, content_form, count, confidence}。"""
    if ASSET_PATTERNS.search(name):
        return {"page_type": "asset", "content_form": None, "skip": True}

    # 结构页
    for rx, ptype in STRUCTURAL:
        if rx.search(name):
            return {"page_type": ptype, "content_form": None, "confidence": "high"}

    # 内容页
    if "content" not in name:
        return {"page_type": "unknown", "content_form": None, "confidence": "low"}

    for rx, form, conf in CONTENT_FORM_RULES:
        if rx.search(name):
            count = parse_count(name)
            # points 形态带 N：points_3 / points_4 ...（无 count 则泛 points）
            if form == "points" and count:
                form = f"points_{count}"
            return {"page_type": "content", "content_form": form, "count": count, "confidence": conf}
    return {"page_type": "content", "content_form": "free", "confidence": "low"}


def scan() -> list[dict]:
    rows = []
    for kind in ("layouts", "decks"):
        root = TEMPLATES / kind
        if not root.is_dir():
            continue
        for pkg in sorted(p for p in root.iterdir() if p.is_dir()):
            for svg in sorted(pkg.glob("*.svg")):
                stem = svg.stem  # e.g. 04b_content_flow
                info = classify(stem)
                if info.get("skip"):
                    continue
                rows.append({
                    "key": f"{kind}/{pkg.name}/{stem}",
                    "path": f"templates/{kind}/{pkg.name}/{svg.name}",
                    "package": pkg.name,
                    "kind": kind,
                    "file": stem,
                    **info,
                })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="输出 JSON 到 stdout")
    ap.add_argument("--out", default=None, help="写入指定 JSON 文件")
    args = ap.parse_args()

    rows = scan()

    if args.out:
        Path(args.out).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {len(rows)} entries → {args.out}")

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    # 汇总打印
    from collections import Counter
    by_form = Counter(r["content_form"] for r in rows)
    by_ptype = Counter(r["page_type"] for r in rows)
    by_conf = Counter(r.get("confidence") for r in rows)
    print(f"# 派生 {len(rows)} 个页面变体\n")
    print("## 按 page_type:", dict(by_ptype))
    print("## 按 content_form:", dict(sorted(by_form.items(), key=lambda x: -x[1])))
    print("## 按 confidence:", dict(by_conf))
    print("\n## 低置信（需人工复核）:")
    for r in rows:
        if r.get("confidence") == "low":
            print(f"  {r['key']:50s} → {r['content_form']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
