#!/usr/bin/env python3
"""Select an article-specific image or a bundled size-safe fallback asset."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "default-images"
MANIFEST = ASSETS / "manifest.json"


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def choose(use_case: str, preferred: Path | None) -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    profile = manifest["assets"].get(use_case)
    if profile is None:
        raise ValueError(f"不支持的图片用途：{use_case}")
    expected = (int(profile["width"]), int(profile["height"]))
    if preferred and preferred.is_file():
        actual = image_size(preferred)
        if actual == expected:
            return {
                "status": "ready", "source": "article_specific", "path": str(preferred.resolve()),
                "width": actual[0], "height": actual[1], "fallback_reason": None,
            }
    fallback = ASSETS / str(profile["file"])
    actual = image_size(fallback)
    if actual != expected:
        raise ValueError(f"内置图尺寸无效：{fallback} 实际 {actual[0]}x{actual[1]}，预期 {expected[0]}x{expected[1]}")
    return {
        "status": "ready", "source": "bundled_default", "path": str(fallback.resolve()),
        "width": actual[0], "height": actual[1],
        "fallback_reason": "preferred_missing" if preferred and not preferred.is_file() else "preferred_size_mismatch" if preferred else "article_image_unavailable",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="选择文章专属图或 skill 内置默认图")
    parser.add_argument("--use-case", required=True, choices=("weixin_cover", "weibo", "universal", "xiaohongshu"))
    parser.add_argument("--preferred", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(choose(args.use_case, args.preferred), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"select-publish-image: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

