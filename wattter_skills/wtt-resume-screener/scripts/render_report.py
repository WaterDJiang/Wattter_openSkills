#!/usr/bin/env python3
"""将 screener 输出的 JSON 渲染为 Markdown 报告（不含 AI 点评）。

AI 点评由调用方基于 assets/prompts/dual_role_review.md 模板生成后，
追加到本脚本生成的骨架报告里。

用法：
  python3 scripts/screener.py --jd ./jd.txt --resume a.pdf b.docx > ctx.json
  python3 scripts/render_report.py ctx.json --output report.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


RECOMMEND_EMOJI = {
    "强烈推荐": "🟢🟢🟢",
    "推荐": "🟢🟢",
    "待定": "🟡",
    "不推荐": "🔴",
}


def render_summary(ctx: dict) -> str:
    level_std = ctx["level_standard"]
    jd = ctx["jd"]["parsed"]
    candidates = ctx["candidates"]
    thresholds = ctx["thresholds"]

    lines: list[str] = []
    lines.append("# 简历筛选报告")
    lines.append("")
    lines.append(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**评估岗位级别**：`{ctx['level']}` — {level_std.get('description', '')}")
    lines.append(f"**简历总数**：{len(candidates)}")
    lines.append("")
    lines.append("## JD 摘要")
    lines.append("")
    if jd.get("level"):
        lines.append(f"- **岗位级别**：{jd['level']}")
    if jd.get("education"):
        lines.append(f"- **学历要求**：{jd['education']}")
    if jd.get("years"):
        lines.append(f"- **经验要求**：{jd['years']}")
    if jd.get("salary"):
        lines.append(f"- **薪资范围**：{jd['salary']}")
    if jd.get("skills"):
        lines.append(f"- **关键技能**：{', '.join(jd['skills'])}")
    if jd.get("responsibilities"):
        lines.append("- **主要职责**：")
        for r in jd["responsibilities"][:6]:
            lines.append(f"  - {r}")
    lines.append("")
    lines.append("## 评估标准")
    lines.append("")
    lines.append("| 维度 | 权重 |")
    lines.append("| --- | --- |")
    for dim, w in level_std.get("weights", {}).items():
        lines.append(f"| {dim} | {w}% |")
    lines.append("")
    if level_std.get("hard_requirements"):
        lines.append("**硬性条件**：")
        for h in level_std["hard_requirements"]:
            lines.append(f"- {h}")
        lines.append("")
    if level_std.get("ignore_or_relax"):
        lines.append("**可放宽项**：")
        for h in level_std["ignore_or_relax"]:
            lines.append(f"- {h}")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_candidate_list(ctx: dict) -> str:
    lines: list[str] = ["## 候选人总览", ""]
    lines.append("| 排名 | 姓名 | 综合分 | 推荐结论 | 学历 | 经验数 | 技能命中 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for i, c in enumerate(ctx["candidates"], 1):
        edu = c.get("education", [{}])
        parts = []
        for e in edu[:2]:
            deg = e.get("degree", "")
            sch = e.get("school", "")
            if sch and "大学" in sch and deg == "本科":
                parts.append(sch)
            else:
                parts.append(f"{deg} {sch}".strip())
        edu_str = "; ".join(p for p in parts if p) or "—"
        rec_emoji = RECOMMEND_EMOJI.get(c["recommendation"], "")
        lines.append(
            f"| {i} | {c['name'] or '—'} | {c['overall_score']} | "
            f"{rec_emoji} {c['recommendation']} | {edu_str[:30]} | "
            f"{c['experience_count']} | {len(c['skill_overlap'])}/{len(c.get('missing_skills', [])) + len(c['skill_overlap'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_candidate_detail(c: dict) -> str:
    lines: list[str] = []
    lines.append(f"### {c['name'] or '未识别姓名'}")
    lines.append("")
    basics = c.get("basics", {}) or {}
    contact = " / ".join(filter(None, [basics.get("email", ""), basics.get("phone", "")]))
    lines.append(f"- **联系方式**：{contact or '—'}")
    lines.append(f"- **综合匹配度**：**{c['overall_score']}** / 100")
    lines.append(f"- **推荐结论**：{RECOMMEND_EMOJI.get(c['recommendation'], '')} {c['recommendation']}")
    lines.append(f"- **来源文件**：`{Path(c['source_file']).name}`")
    lines.append("")
    # 维度得分
    lines.append("**各维度得分**：")
    weights = c.get("weights", {})
    lines.append("")
    lines.append("| 维度 | 权重 | 得分 |")
    lines.append("| --- | --- | --- |")
    for dim, score in sorted(c.get("dimension_scores", {}).items(), key=lambda x: -weights.get(x[0], 0)):
        lines.append(f"| {dim} | {weights.get(dim, 0)}% | {score} |")
    lines.append("")
    # 技能
    if c.get("skill_overlap"):
        lines.append(f"**技能命中**：{', '.join(c['skill_overlap'])}")
    if c.get("missing_skills"):
        lines.append(f"**可能短板**：{', '.join(c['missing_skills'])}")
    if c.get("skills"):
        lines.append(f"**候选人掌握的技能**：{', '.join(c['skills'])}")
    lines.append("")
    # 教育/经验
    if c.get("education"):
        lines.append("**教育背景**：")
        for e in c["education"]:
            tag = " · ".join(filter(None, [e.get("period", ""), e.get("degree", ""), e.get("school", "")]))
            lines.append(f"- {tag or e.get('raw', '')}")
        lines.append("")
    lines.append("<!-- AI_REVIEW_HERE -->")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_report(ctx: dict) -> str:
    parts = [render_summary(ctx), render_candidate_list(ctx), "## 候选人详情", ""]
    for c in ctx["candidates"]:
        parts.append(render_candidate_detail(c))
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="渲染 Markdown 报告")
    parser.add_argument("input", help="screener.py 输出的 JSON 文件")
    parser.add_argument("--output", "-o", default="-", help="输出 Markdown 路径")
    args = parser.parse_args()
    ctx = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = render_report(ctx)
    if args.output == "-":
        print(report)
    else:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"[OK] report -> {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
