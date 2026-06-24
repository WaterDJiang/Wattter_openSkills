#!/usr/bin/env python3
"""简历筛选协调器：加载 JD + 简历，输出供 AI Agent 使用的结构化数据。

本脚本本身不调用 LLM，AI 评估由调用方（Claude/Trae 等）按
assets/prompts/dual_role_review.md 模板完成。

输出 JSON 包含：
- jd：结构化招聘需求
- candidates[]：每位候选人的基础信息、提取的技能、建议维度得分（0-100）
- evaluation_standard：当前岗位级别对应的权重、硬性条件、双视角差异
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from parse_jd import parse_jd  # type: ignore
from parse_resume import parse_resume  # type: ignore


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def get_level_standard(standards: dict[str, Any], level: str) -> dict[str, Any]:
    if level in standards:
        return {"_level": level, **standards[level]}
    # 兜底：找最接近的级别
    fallback_order = ["mid", "junior", "senior", "fresh_grad", "intern", "manager", "staff", "director"]
    for lv in fallback_order:
        if lv in standards:
            return {"_level": lv, **standards[lv]}
    return {"_level": level}


# 维度关键词（用于按段落粗估基础分；最终分由 AI 综合）
DIMENSION_HINTS = {
    "education_background": ["大学", "学院", "University", "学历", "专业", "本科", "硕士", "博士", "GPA", "排名"],
    "basic_skills": ["语言", "工具", "框架", "熟练", "掌握", "Python", "Java", "SQL", "Skills"],
    "internship": ["实习", "intern", "Internship"],
    "work_experience": ["工作", "任职", "就职", "担任", "负责", "Work"],
    "projects": ["项目", "Project", "实现", "开发", "设计"],
    "learning_ability": ["自学", "Kaggle", "开源", "GitHub", "博客", "学习"],
    "leadership": ["带", "管理", "leader", "lead", "主持", "组长", "经理"],
    "attitude": ["积极", "主动", "抗压", "责任心"],
    "stability": ["稳定", "长期", "同城", "可到岗"],
    "technical_skills": ["架构", "性能优化", "高并发", "算法", "源码", "原理"],
}


def estimate_dimensions(resume: dict[str, Any], jd: dict[str, Any], standards: dict[str, Any]) -> dict[str, int]:
    """为每个评估维度粗估一个 0-100 分。AI 在此基础上做最终调整。"""
    text = resume.get("text", "")
    text_l = text.lower()
    candidate_skills = {s.lower() for s in resume.get("skills", [])}
    jd_skills = {s.lower() for s in jd.get("skills", [])}

    skill_overlap = len(candidate_skills & jd_skills)
    skill_total = max(len(jd_skills), 1)
    skill_ratio = skill_overlap / skill_total  # 0-1

    exp_count = len(resume.get("experience", []))
    edu_count = len(resume.get("education", []))

    # 各维度初始估算
    scores: dict[str, int] = {}

    for dim, hints in DIMENSION_HINTS.items():
        if dim not in standards.get("weights", {}):
            continue
        hit = sum(1 for h in hints if h.lower() in text_l)
        base = min(100, 40 + hit * 12)
        if dim in {"basic_skills", "technical_skills"}:
            base = int(40 + skill_ratio * 55)
        if dim == "education_background" and edu_count:
            base = min(100, 55 + edu_count * 15)
        if dim in {"work_experience", "internship", "projects"} and exp_count:
            base = min(100, 45 + min(exp_count, 5) * 10)
        if dim == "learning_ability" and ("github" in text_l or "开源" in text):
            base += 10
        scores[dim] = min(100, max(20, base))

    # 兜底：未命中的维度给中性分
    for dim in standards.get("weights", {}):
        scores.setdefault(dim, 55)
    return scores


def compute_overall(scores: dict[str, int], weights: dict[str, int]) -> int:
    total = 0
    weight_sum = 0
    for dim, score in scores.items():
        w = weights.get(dim, 0)
        total += w * score
        weight_sum += w
    if weight_sum == 0:
        return 0
    return round(total / weight_sum)


def recommend(overall: int, thresholds: dict[str, int]) -> str:
    if overall >= thresholds.get("strong_recommend", 85):
        return "强烈推荐"
    if overall >= thresholds.get("recommend", 70):
        return "推荐"
    if overall >= thresholds.get("hold", 55):
        return "待定"
    return "不推荐"


def build_candidate_card(
    resume: dict[str, Any],
    jd: dict[str, Any],
    standards: dict[str, Any],
    thresholds: dict[str, int],
) -> dict[str, Any]:
    scores = estimate_dimensions(resume, jd, standards)
    weights = standards.get("weights", {})
    overall = compute_overall(scores, weights)
    basics = resume.get("basics", {})
    return {
        "name": basics.get("name", "") or Path(resume.get("source_file", "")).stem,
        "basics": basics,
        "source_file": resume.get("source_file", ""),
        "skills": resume.get("skills", []),
        "education": resume.get("education", []),
        "experience_count": len(resume.get("experience", [])),
        "dimension_scores": scores,
        "weights": weights,
        "overall_score": overall,
        "recommendation": recommend(overall, thresholds),
        "skill_overlap": sorted(
            {s for s in resume.get("skills", []) if s.lower() in {x.lower() for x in jd.get("skills", [])}}
        ),
        "missing_skills": sorted(
            {s for s in jd.get("skills", []) if s.lower() not in {x.lower() for x in resume.get("skills", [])}}
        )[:10],
    }


def build_screening_context(
    jd_path: Path | None,
    jd_text: str | None,
    resume_paths: list[Path],
    config_path: Path,
    standards_path: Path,
    force_level: str | None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path)
    standards = load_yaml(standards_path)
    thresholds = standards.get("recommendation_thresholds", cfg["defaults"]["thresholds"])

    jd_text_final = jd_text or (jd_path.read_text(encoding="utf-8") if jd_path else "")
    if not jd_text_final:
        raise SystemExit("[ERROR] JD is empty. Provide --jd or --jd-text.")
    jd = parse_jd(jd_text_final)
    level = force_level or jd.get("level") or cfg["defaults"]["default_level"]
    level_std = get_level_standard(standards, level)

    resumes = [parse_resume(p) for p in resume_paths]
    candidates = [build_candidate_card(r, jd, level_std, thresholds) for r in resumes]

    # 排序：综合分降序
    candidates.sort(key=lambda c: c["overall_score"], reverse=True)

    return {
        "config": cfg,
        "level": level,
        "level_standard": level_std,
        "thresholds": thresholds,
        "jd": {
            "text": jd_text_final,
            "parsed": {k: v for k, v in jd.items() if k != "raw"},
        },
        "candidates": candidates,
        "evaluation_prompt_path": str(Path(__file__).parent.parent / "assets" / "prompts" / "dual_role_review.md"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="简历筛选协调器（结构化数据输出）")
    parser.add_argument("--jd", help="JD 文本文件路径")
    parser.add_argument("--jd-text", help="直接传入 JD 文本")
    parser.add_argument("--resume", nargs="+", required=True, help="一个或多个简历文件")
    parser.add_argument("--level", help="强制指定岗位级别（覆盖 JD 推断）")
    parser.add_argument("--config", default="config/screener_config.yaml")
    parser.add_argument("--standards", default="config/evaluation_standards.yaml")
    parser.add_argument("--output", "-o", default="-", help="输出 JSON 文件路径")
    args = parser.parse_args()

    base = Path(__file__).parent.parent
    ctx = build_screening_context(
        jd_path=Path(args.jd) if args.jd else None,
        jd_text=args.jd_text,
        resume_paths=[Path(r) for r in args.resume],
        config_path=base / args.config,
        standards_path=base / args.standards,
        force_level=args.level,
    )
    payload = json.dumps(ctx, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(
            f"[OK] {len(ctx['candidates'])} candidates / level={ctx['level']} -> {args.output}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
