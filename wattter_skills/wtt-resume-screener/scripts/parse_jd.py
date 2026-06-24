#!/usr/bin/env python3
"""JD 解析器：从 Job Description 文本中抽取结构化招聘需求。

输出：岗位级别、硬性条件（学历/经验/技能）、软性能力、薪资范围等。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from parse_resume import extract_skills  # type: ignore  # 复用同目录模块


# 岗位级别关键词（按优先级匹配，匹配到即返回）
LEVEL_PATTERNS: list[tuple[str, list[str]]] = [
    ("intern", ["实习生", "实习", "intern", "internship"]),
    ("fresh_grad", ["应届生", "校招", "毕业生", "2024届", "2025届", "2026届", "fresh", "campus"]),
    ("junior", ["初级", "助理", "junior", "entry", "0-1年", "1-3年"]),
    ("mid", ["中级", "senior 偏", "mid", "3-5年", "2-4年"]),
    ("senior", ["高级", "senior", "资深", "5-8年", "5-10年", "3-5年以上"]),
    ("staff", ["staff", "技术专家", "专家工程师"]),
    ("manager", ["经理", "主管", "leader", "lead", "manager", "team lead", "组长"]),
    ("director", ["总监", "director", "VP"]),
]


def detect_level(text: str) -> str:
    text_l = text.lower()
    for level, kws in LEVEL_PATTERNS:
        for kw in kws:
            if kw.lower() in text_l:
                return level
    return "mid"  # 默认中级


def detect_education(text: str) -> str:
    """返回最高学历要求关键词。"""
    if "博士" in text:
        return "博士"
    if "硕士" in text or "研究生" in text:
        return "硕士"
    if "本科" in text or "学士" in text:
        return "本科"
    if "大专" in text:
        return "大专"
    return "不限"


def detect_years(text: str) -> str:
    m = re.search(r"(\d+)\s*[-~到至]\s*(\d+)\s*年", text)
    if m:
        return f"{m.group(1)}-{m.group(2)}年"
    m = re.search(r"(\d+)\s*年\s*以上", text)
    if m:
        return f"{m.group(1)}年以上"
    m = re.search(r"(\d+)\s*\+?\s*years?", text, re.IGNORECASE)
    if m:
        return f"{m.group(1)}年以上"
    return ""


def detect_salary(text: str) -> str:
    """粗略抓取薪资区间。"""
    patterns = [
        r"(\d+)\s*[-~到至]\s*(\d+)\s*[kK千]",
        r"(\d+)\s*[-~到至]\s*(\d+)\s*万",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return f"{m.group(1)}-{m.group(2)}K"
    return ""


def detect_responsibilities(text: str) -> list[str]:
    """按行抓取『职责』『Requirements』段落中的短句。"""
    lines: list[str] = []
    capture = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.match(r"^[\s#>*\-]*(职责|Responsibilities|Requirements|要求|任职|Qualifications|JD|岗位描述)", line, re.IGNORECASE):
            capture = True
            continue
        if re.match(r"^[\s#>*\-]*(福利|Benefits|薪酬|加分|Plus)", line, re.IGNORECASE):
            capture = False
        if capture and (line.startswith(("•", "-", "·", "●")) or re.match(r"^\d+[.、)]", line)):
            cleaned = re.sub(r"^[\s•\-·●\d.、)]+", "", line).strip()
            if cleaned and len(cleaned) > 4:
                lines.append(cleaned)
    return lines[:20]


def parse_jd(text: str) -> dict[str, Any]:
    return {
        "level": detect_level(text),
        "education": detect_education(text),
        "years": detect_years(text),
        "salary": detect_salary(text),
        "skills": extract_skills(text),
        "responsibilities": detect_responsibilities(text),
        "raw": text,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="JD 解析器")
    parser.add_argument("--input", "-i", help="JD 文本文件路径（默认 stdin）")
    parser.add_argument("--text", "-t", help="直接传入 JD 文本（与 --input 互斥）")
    parser.add_argument("--output", "-o", default="-", help="输出 JSON 文件路径")
    args = parser.parse_args()

    if args.text:
        text = args.text
    elif args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    result = parse_jd(text)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        Path(args.output).write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
