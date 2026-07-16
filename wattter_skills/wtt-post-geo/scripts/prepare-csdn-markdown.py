#!/usr/bin/env python3
"""Prepare a clean CSDN Markdown payload and a validation manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
TITLE_RE = re.compile(r"^title\s*:\s*(?P<title>.+?)\s*$", re.MULTILINE)
H1_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$", re.MULTILINE)
IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<target>[^)]+)\)")
REMOTE_PREFIXES = ("http://", "https://", "data:")
MAX_BYTES = 5 * 1024 * 1024


def clean_title(value: str) -> str:
    value = value.strip().strip('"\'')
    return re.sub(r"\s+", " ", value)


def comparable(value: str) -> str:
    value = unicodedata.normalize("NFKC", clean_title(value)).casefold()
    return re.sub(r"[\W_]+", "", value, flags=re.UNICODE)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    title_match = TITLE_RE.search(match.group("body"))
    title = clean_title(title_match.group("title")) if title_match else None
    return title, text[match.end() :]


def resolve_image(source: Path, target: str) -> dict[str, object]:
    raw_target = target.strip().split(maxsplit=1)[0].strip("<>\"'")
    if raw_target.startswith(REMOTE_PREFIXES):
        return {"target": raw_target, "kind": "remote"}

    file_target = raw_target[7:] if raw_target.startswith("file://") else raw_target
    path = Path(file_target).expanduser()
    if not path.is_absolute():
        path = source.parent / path
    path = path.resolve()
    return {
        "target": raw_target,
        "kind": "local",
        "absolute_path": str(path),
        "exists": path.is_file(),
    }


def prepare(source: Path, output_dir: Path, explicit_title: str | None) -> dict[str, object]:
    text = source.read_text(encoding="utf-8-sig")
    frontmatter_title, body = split_frontmatter(text)
    first_h1 = H1_RE.search(body)
    h1_title = clean_title(first_h1.group("title")) if first_h1 else None
    title = clean_title(explicit_title or frontmatter_title or h1_title or "")

    if not title:
        raise ValueError("缺少标题：请提供 --title、frontmatter title 或正文首个 H1")
    if not 5 <= len(title) <= 100:
        raise ValueError(f"CSDN 标题必须为 5～100 个字符，当前为 {len(title)}")

    stripped_duplicate_h1 = False
    if first_h1 and comparable(first_h1.group("title")) == comparable(title):
        body = body[: first_h1.start()] + body[first_h1.end() :]
        stripped_duplicate_h1 = True

    body = body.strip() + "\n"
    if not body.strip():
        raise ValueError("正文不能为空")

    encoded = body.encode("utf-8")
    if len(encoded) >= MAX_BYTES:
        raise ValueError(f"CSDN Markdown 必须小于 5 MiB，当前为 {len(encoded)} 字节")

    images: list[dict[str, object]] = []
    for index, match in enumerate(IMAGE_RE.finditer(body), start=1):
        item = resolve_image(source, match.group("target"))
        item.update({"index": index, "alt": match.group("alt")})
        images.append(item)

    local_images = [item for item in images if item["kind"] == "local"]
    missing_images = [item for item in local_images if not item["exists"]]
    body_text = body.rstrip("\n")
    is_single_paragraph = "\n" not in body_text
    direct_fill_ready = is_single_paragraph and not local_images
    browser_injection_ready = not is_single_paragraph and not local_images

    blocking_reasons = (
        ["local_images_require_verified_csdn_upload"] if local_images else []
    ) + (["missing_local_images"] if missing_images else [])
    warnings = []
    if browser_injection_ready:
        warnings.append("multiline_markdown_requires_verified_browser_injection")

    output_dir.mkdir(parents=True, exist_ok=True)
    article_path = output_dir / "article.csdn.md"
    title_path = output_dir / "title.txt"
    manifest_path = output_dir / "manifest.json"

    article_path.write_text(body, encoding="utf-8")
    title_path.write_text(title + "\n", encoding="utf-8")

    manifest: dict[str, object] = {
        "source": str(source.resolve()),
        "title": title,
        "article_path": str(article_path.resolve()),
        "title_path": str(title_path.resolve()),
        "body_chars": len(body),
        "body_bytes": len(encoded),
        "stripped_frontmatter": frontmatter_title is not None,
        "stripped_duplicate_h1": stripped_duplicate_h1,
        "images": images,
        "local_images": local_images,
        "missing_images": missing_images,
        "browser_entry_mode": (
            "direct_fill"
            if direct_fill_ready
            else "browser_injection_probe"
            if browser_injection_ready
            else "manual_import_required"
        ),
        "direct_fill_ready": direct_fill_ready,
        "browser_injection_ready": browser_injection_ready,
        "automation_candidate": direct_fill_ready or browser_injection_ready,
        "publish_ready": direct_fill_ready,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    manifest["manifest_path"] = str(manifest_path.resolve())
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="生成独立 CSDN Markdown、title.txt 与校验 manifest"
    )
    parser.add_argument("source", type=Path, help="源 Markdown 文件")
    parser.add_argument("--output-dir", type=Path, required=True, help="输出目录")
    parser.add_argument("--title", help="显式标题；默认读取 frontmatter 或首个 H1")
    args = parser.parse_args()

    try:
        if not args.source.is_file():
            raise ValueError(f"源文件不存在：{args.source}")
        result = prepare(args.source.resolve(), args.output_dir.resolve(), args.title)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"prepare-csdn-markdown: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
