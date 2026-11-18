#!/usr/bin/env python3
"""校验封面候选计划或本次本地图片；不判断审美、OCR或实际画风。"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image


CATALOG = Path(__file__).resolve().parents[1] / "references/cover-style-catalog.json"
PLACEHOLDER = re.compile(
    r"\{\{[^{}\n]+\}\}|\{(?:requested_ratio|generation_ratio|title|style_id|style_name|"
    r"title_or_topic|原标题|标题原文|主题|所选方向名称)\}")


def ratio(value):
    if not isinstance(value, str):
        raise ValueError("比例必须为正数w:h字符串")
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError("比例必须为正数w:h字符串")
    width, height = (Fraction(part) for part in parts)
    if width <= 0 or height <= 0:
        raise ValueError("比例必须大于零")
    return width / height


def local_file(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("未记录相对文件路径")
    relative = Path(value)
    path = (root / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError("文件须保存在本任务目录内，不能越界引用")
    if not path.is_file():
        raise ValueError(f"文件不存在: {value}")
    return path


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(data, root, stage, catalog):
    errors, pending, assets = [], [], []

    def report():
        status = "needs_revision" if errors else "needs_review" if pending else (
            "plan_pass" if stage == "plan" else "assets_pass")
        return {"status": status, "stage": stage, "errors": errors,
                "pending": pending, "assets": assets,
                "scope": "记录与本地资产检查；不代表字形、风格、审美或平台验收"}

    if not isinstance(data, dict) or not isinstance(catalog, dict):
        errors.append("记录与方向库须为JSON对象")
        return report()
    profiles = catalog.get("styles", [])
    if not isinstance(profiles, list) or any(not isinstance(p, dict) or not nonempty(p.get("id")) for p in profiles):
        errors.append("方向库缺少有效styles列表")
        return report()
    styles = {p["id"]: p for p in profiles}
    if not styles or len(styles) != len(profiles):
        errors.append("方向库为空或ID重复")
        return report()
    if data.get("mode") != "cover":
        errors.append("mode必须为cover")
    count = data.get("expected_count", 4)
    if type(count) is not int or count < 1:
        errors.append("expected_count须为正整数")
        return report()
    if count != 4 and not nonempty(data.get("count_override_reason")):
        errors.append("默认四张；其他数量须记录用户的count_override_reason")
    selection = data.get("selection_mode", "styles")
    if selection not in ("styles", "locked-style"):
        errors.append("selection_mode须为styles或locked-style")
    locked = data.get("locked_style_id")
    if selection == "locked-style" and (
        not isinstance(locked, str) or locked not in styles or not nonempty(data.get("style_constraint_reason"))
    ):
        errors.append("锁定画风须记录有效locked_style_id及用户style_constraint_reason")
    policy = data.get("text_policy", "title")
    title = data.get("title", "")
    if policy not in ("title", "reserved", "none") or not isinstance(title, str):
        errors.append("text_policy须为title/reserved/none，title须为字符串")
        return report()
    if policy == "title" and not nonempty(title):
        errors.append("含字封面缺少完整标题")
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        errors.append("candidates须为列表")
        return report()
    if len(candidates) != count:
        errors.append(f"需要{count}项候选，实际{len(candidates)}项")
    slots, used_styles, variants, prompts, images = set(), set(), set(), set(), set()
    for index, candidate in enumerate(candidates):
        label = f"候选{index+1}"
        if not isinstance(candidate, dict):
            errors.append(f"{label}: 记录须为对象")
            continue
        slot = candidate.get("slot")
        if not nonempty(slot) or slot in slots:
            errors.append(f"{label}: slot缺失或重复")
        slots.add(str(slot))
        label = str(slot or label)
        style_id = candidate.get("style_id")
        if not isinstance(style_id, str) or style_id not in styles:
            errors.append(f"{label}: 不存在的style_id")
            continue
        profile = styles[style_id]
        if selection == "styles" and style_id in used_styles:
            errors.append(f"{label}: 默认须为不同风格，不能仅换色重复同一style_id")
        used_styles.add(style_id)
        if selection == "locked-style":
            variant = candidate.get("variant_id")
            if style_id != locked or not nonempty(variant) or variant in variants:
                errors.append(f"{label}: 锁定画风须一致且variant_id独立")
            variants.add(str(variant))
        for field in ("reason", "visual_concept"):
            if not nonempty(candidate.get(field)):
                errors.append(f"{label}: 缺少{field}")
        segments = candidate.get("title_segments")
        if candidate.get("text_policy") != policy:
            errors.append(f"{label}: 文字政策与本轮要求不一致")
        if policy == "title":
            if profile.get("text_policy") == "none":
                errors.append(f"{label}: 未获无字要求时不能选择仅无字方向")
            if not isinstance(segments, list) or any(not isinstance(s, str) for s in segments) or "".join(segments) != title:
                errors.append(f"{label}: 标题片段须按原序还原完整原文")
        elif policy == "reserved":
            if segments != [] or not nonempty(candidate.get("title_area")) or profile.get("text_policy") == "none":
                errors.append(f"{label}: 预留字区须无可见标题片段、记录字区并使用可带标题的方向")
        elif policy == "none":
            if segments != [] or not profile.get("supports_text_free", False):
                errors.append(f"{label}: 无字候选须无标题片段且方向支持无字")
        actual_ratio = None
        for field in ("requested_ratio", "generation_ratio"):
            try:
                parsed = ratio(candidate.get(field))
                if field == "generation_ratio":
                    actual_ratio = parsed
            except (ValueError, ZeroDivisionError):
                errors.append(f"{label}: {field}不是有效正比例")
        try:
            path = local_file(root, candidate.get("prompt_file"))
            if path in prompts:
                errors.append(f"{label}: 各候选须保存独立提示词")
            prompts.add(path)
            prompt = path.read_text(encoding="utf-8")
            if not prompt.strip() or PLACEHOLDER.search(prompt.replace(title, "") if isinstance(title, str) else prompt):
                errors.append(f"{label}: 提示词为空或有未填写变量")
            if policy == "title" and title not in prompt and (
                not isinstance(segments, list) or not segments or
                any(not isinstance(s, str) or s not in prompt for s in segments)
            ):
                errors.append(f"{label}: 提示词未包含完整标题或其全部原序片段")
        except (OSError, ValueError) as error:
            errors.append(f"{label}: 提示词读取失败: {error}")
        status = candidate.get("status")
        if status not in ("planned", "generated", "inline", "failed"):
            errors.append(f"{label}: 未知status")
        if stage == "plan":
            continue
        if status != "generated":
            if status == "inline" and not nonempty(candidate.get("generation_ref")):
                errors.append(f"{label}: 内联图缺少本次工具返回标识")
            pending.append(f"{label}: {status}；{candidate.get('error', '尚无可检查的本地图片，须查看实际预览或继续生成')}")
            continue
        if not nonempty(candidate.get("generation_ref")):
            errors.append(f"{label}: 缺少本次generation_ref")
        try:
            image_path = local_file(root, candidate.get("image_file"))
            with Image.open(image_path) as picture:
                picture.load()
                size = list(picture.size)
            if size != candidate.get("dimensions"):
                errors.append(f"{label}: 记录尺寸与实际{size}不一致")
            if actual_ratio and abs(size[0] - float(actual_ratio)*size[1]) > max(1., float(actual_ratio)):
                errors.append(f"{label}: 实际图片比例与generation_ratio不一致")
            digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
            if digest in images:
                errors.append(f"{label}: 图片内容重复，不能将同图改名冒充多个候选")
            images.add(digest)
            assets.append({"slot": slot, "file": str(image_path), "dimensions": size, "sha256": digest})
        except (OSError, ValueError) as error:
            errors.append(f"{label}: 图片检查失败: {error}")
    return report()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--stage", choices=("plan", "images"), default="images")
    parser.add_argument("--catalog", type=Path, default=CATALOG,
                        help="默认使用随附方向库；自拟方向可保存本任务同结构目录并显式指定")
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        result = validate(data, args.manifest.resolve().parent, args.stage, catalog)
    except (OSError, ValueError) as error:
        result = {"status": "needs_revision", "errors": [str(error)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in ("plan_pass", "assets_pass") else 2


if __name__ == "__main__":
    sys.exit(main())
