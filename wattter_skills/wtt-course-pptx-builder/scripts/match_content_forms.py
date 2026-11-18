#!/usr/bin/env python3
"""
PPT Master - 内容形态 → 模板匹配器（确定性查表，不调 LLM）。

把"Strategist 读 71 段散文猜模板"升级成"按内容形态词表查表"。
词表与 chart 标注的单一事实源：templates/charts/content_forms.json。

子命令：
    resolve <form> [--count N]   列出服务某形态的 chart 模板（目录查询）
    project <project_path>       读项目的 chart_selection.json，反查每页模板→形态，
                                  报告 confidence，标记低置信/未标注（审计）

    --write  (仅 project) 把反查到的 form 字段写回 chart_selection.json（默认 dry-run）

匹配是确定性的：form → content_forms.json 的 chart_tags 反查 → 候选排序。
无 LLM、无网络、幂等。声明形态来自 markdown（v2）或 Strategist 推理后写入
chart_selection.json 的 form 字段；本脚本负责查表与审计。

示例：
    python3 scripts/match_content_forms.py resolve flow_linear
    python3 scripts/match_content_forms.py resolve points_5 --count 5
    python3 scripts/match_content_forms.py project projects/mydeck
    python3 scripts/match_content_forms.py project projects/mydeck --write
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from project_utils import SKILL_DIR  # type: ignore
except Exception:
    # 脚本被从仓库根或 scripts/ 调用时都能定位
    SKILL_DIR = Path(__file__).resolve().parent.parent

CONTENT_FORMS_PATH = SKILL_DIR / "templates" / "charts" / "content_forms.json"


def load_content_forms() -> dict:
    if not CONTENT_FORMS_PATH.exists():
        raise FileNotFoundError(f"content_forms.json 不存在：{CONTENT_FORMS_PATH}")
    return json.loads(CONTENT_FORMS_PATH.read_text(encoding="utf-8"))


def _form_def(cf: dict, form: str) -> dict:
    if form not in cf["forms"]:
        avail = ", ".join(sorted(cf["forms"]))
        raise SystemExit(f"[ERROR] 未知形态 '{form}'。可用：{avail}")
    return cf["forms"][form]


def resolve(cf: dict, form: str, count: int | None = None) -> list[dict]:
    """返回服务该形态的 **chart** 候选（全局共享库），按 slots 命中度排序。"""
    fdef = _form_def(cf, form)
    want_slots = count if count is not None else fdef.get("count")
    candidates = []
    for cid, tag in cf["chart_tags"].items():
        if form not in tag.get("content_forms", []):
            continue
        dimensions = tag["dimensions"]
        if dimensions.get("requires_data") and not fdef.get("has_data"):
            continue
        if want_slots is not None:
            minimum = dimensions.get("min_items")
            maximum = dimensions.get("max_items")
            if minimum is not None and want_slots < minimum:
                continue
            if maximum is not None and want_slots > maximum:
                continue
        entry = {"chart": cid, "dimensions": dimensions}
        # 命中度：声明 count 时优先 slots 精确匹配
        if want_slots is not None:
            tag_slots = dimensions.get("slots")
            in_range = dimensions.get("min_items") is not None or dimensions.get("max_items") is not None
            entry["slots_match"] = (
                "exact" if tag_slots == want_slots else "range" if in_range
                else "flex" if not tag_slots else "other"
            )
        candidates.append(entry)
    if want_slots is not None:
        order = {"exact": 0, "range": 1, "flex": 2, "other": 3}
        candidates.sort(key=lambda c: order.get(c.get("slots_match", "other"), 3))
    return candidates


def resolve_variants(cf: dict, form: str, package: str, page_type: str | None = None) -> list[dict]:
    """返回服务该形态的 **页面变体** 候选，限定在选定模板包内（intra-package）。

    关键作用域规则：charts 是全局共享库；但 page_layouts 是"选定哪个模板包，
    就在那个包自己的变体里选页"。所以页面变体匹配必须 --package 限定，不能跨包。
    """
    _form_def(cf, form)  # 校验 form 合法
    candidates = []
    for key, tag in cf.get("page_variant_tags", {}).items():
        if tag.get("package") != package:
            continue
        if form not in tag.get("content_forms", []):
            continue
        if page_type and tag.get("page_type") != page_type:
            continue
        candidates.append({"key": key, "path": f"templates/{key}.svg",
                           "page_type": tag["page_type"], "file": tag["file"]})
    return candidates


def cmd_resolve(args) -> int:
    cf = load_content_forms()
    fdef = _form_def(cf, args.form)
    print(f"# 形态 {args.form}")
    print(f"  relationship={fdef['relationship']}  count={fdef.get('count', fdef.get('count_range', '?'))}  has_data={fdef['has_data']}")
    print(f"  when: {fdef['when']}")
    print(f"  not_when: {fdef['not_when']}")

    # 1) chart 候选（全局共享库）
    cands = resolve(cf, args.form, args.count)
    print(f"\n# chart 候选（全局 charts 库，{len(cands)}）:")
    if not cands:
        print("  （无打标 chart 服务此形态）")
    for c in cands:
        slot_info = f"  [slots:{c.get('slots_match','?')}]" if args.count else ""
        cue_terms = c["dimensions"].get("requires_cue_any") or []
        cue_info = f"  [正文需含: {'/'.join(cue_terms)}]" if cue_terms else ""
        print(f"  - {c['chart']}{slot_info}{cue_info}")

    # 2) 页面变体候选（限定选定模板包内——intra-package）
    if args.package:
        variants = resolve_variants(cf, args.form, args.package, page_type="content")
        print(f"\n# 页面变体候选（限定包 `{args.package}`，{len(variants)}）:")
        if not variants:
            print(f"  （该包无变体服务 {args.form}——可能需在该包内加变体，或改用全局 chart 库）")
        for v in variants:
            print(f"  - {v['file']}  → {v['path']}")
    else:
        print("\n# 页面变体候选：略（页面变体匹配是 intra-package，需 --package <选定模板包> 限定）")
        print("  charts 是全局共享库；page_layouts 选页发生在选定模板包内部")
    return 0


def _load_chart_selection(project: Path) -> list[dict]:
    """读项目的 chart_selection.json 的 pages 数组（兼容顶层或嵌套）。"""
    cs = project / "chart_selection.json"
    if not cs.exists():
        return []
    data = json.loads(cs.read_text(encoding="utf-8"))
    return data.get("pages", []) if isinstance(data, dict) else []


def cmd_project(args) -> int:
    cf = load_content_forms()
    project = Path(args.project)
    pages = _load_chart_selection(project)
    if not pages:
        print(f"[INFO] {project} 无 chart_selection.json 或 pages 为空——无 chart 页可审计。")
        return 0

    # form → charts 反查表
    form_to_charts: dict[str, list[str]] = {}
    for cid, tag in cf["chart_tags"].items():
        for f in tag.get("content_forms", []):
            form_to_charts.setdefault(f, []).append(cid)

    rows = []
    updates = {}
    for p in pages:
        page = p.get("page", "?")
        tmpl = p.get("template")
        if not tmpl:
            print(f"  {page}: 无 template（{p.get('status', '?')}）")
            continue
        tag = cf["chart_tags"].get(tmpl)
        if not tag:
            print(f"  {page}: {tmpl} — ⚠ 未在 content_forms.json 打标（跳过）")
            continue
        forms = tag["content_forms"]
        # 若 page 已声明 form，校验 template 是否服务它
        declared = p.get("form")
        if declared and declared not in forms:
            conf = "mismatch"
            note = f"❌ 声明 {declared} 但 {tmpl} 服务 {forms}"
        elif declared:
            conf = "high"
            note = f"声明 {declared} ✓"
        elif len(forms) == 1:
            conf = "medium"
            note = f"推断 {forms[0]}（唯一形态）"
            updates[page] = forms[0]
        else:
            conf = "low"
            note = f"歧义：{tmpl} 服务 {forms}——需声明 form 消歧"
        rows.append((page, tmpl, conf, note))

    print(f"# 项目 {project.name} chart 形态审计（{len(rows)} 页）")
    for page, tmpl, conf, note in rows:
        icon = {"high": "✓", "medium": "~", "low": "?", "mismatch": "✗"}[conf]
        print(f"  {icon} {page} {tmpl} [{conf}] {note}")

    if args.write and updates:
        cs_path = project / "chart_selection.json"
        data = json.loads(cs_path.read_text(encoding="utf-8"))
        for p in data.get("pages", []):
            if p.get("page") in updates and "form" not in p:
                p["form"] = updates[p["page"]]
        cs_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[write] 已为 {len(updates)} 页补 form 字段 → {cs_path}")
    elif updates:
        print(f"\n[hint] {len(updates)} 页可自动补 form（加 --write）")

    # 退出码：有 mismatch 视为需修复
    return 1 if any(r[2] == "mismatch" for r in rows) else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("resolve", help="列出服务某形态的 chart 模板（全局）+ 页面变体（需 --package 限定）")
    pr.add_argument("form")
    pr.add_argument("--count", type=int, default=None, help="声明要点数（精确匹配 slots）")
    pr.add_argument("--package", default=None, help="选定模板包名（如 平安知鸟）；给则同时查该包内的页面变体候选")

    pp = sub.add_parser("project", help="审计项目的 chart 形态选型")
    pp.add_argument("project")
    pp.add_argument("--write", action="store_true", help="把推断的 form 写回 chart_selection.json")

    args = ap.parse_args()
    if args.cmd == "resolve":
        return cmd_resolve(args)
    if args.cmd == "project":
        return cmd_project(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
