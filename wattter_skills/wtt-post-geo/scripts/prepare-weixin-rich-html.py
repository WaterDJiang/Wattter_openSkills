#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path

import markdown
from bs4 import BeautifulSoup


POSTER_SCRIPT_DIR = Path("/Users/water/.wattter-skills/skills/wtt-post-multi-platform/platforms/wechat/scripts")
if str(POSTER_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(POSTER_SCRIPT_DIR))

from poster_generator import extract_poster_markers, generate_poster  # noqa: E402


STYLE = {
    "primary": "#1F1F1F",
    "accent": "#002FA7",
    "text": "#2A2A2A",
    "muted": "#666666",
    "border": "#E6E6E6",
    "surface": "#F7F7F7",
    "code_bg": "#F2F2F2",
}


def peel_frontmatter(markdown_text: str) -> tuple[dict[str, str], str]:
    if not markdown_text.startswith("---\n"):
        return {}, markdown_text
    end = markdown_text.find("\n---", 4)
    if end == -1:
        return {}, markdown_text
    frontmatter_text = markdown_text[4:end].strip()
    body = markdown_text[end + len("\n---") :].lstrip("\n")
    frontmatter: dict[str, str] = {}
    for raw in frontmatter_text.splitlines():
        if ":" not in raw or raw.startswith((" ", "\t", "-")):
            continue
        key, value = raw.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter, body


def strip_title_and_noise(markdown_text: str) -> tuple[str, str, list[str]]:
    notes = []
    frontmatter, markdown_text = peel_frontmatter(markdown_text)
    if frontmatter:
        notes.append("removed YAML frontmatter")
    lines = markdown_text.splitlines()
    if lines and lines[0].strip() == "完全":
        lines = lines[1:]
        notes.append("removed leading standalone line: 完全")

    title = frontmatter.get("title")
    body_lines = []
    for line in lines:
        if title is None and line.startswith("# "):
            title = line[2:].strip()
            continue
        body_lines.append(line)

    if not title:
        title = "未命名公众号草稿"
    return title, "\n".join(body_lines).strip() + "\n", notes


def replace_posters(markdown_text: str, output_dir: Path, start_index: int = 1) -> tuple[str, list[dict]]:
    posters = extract_poster_markers(markdown_text)
    generated = []
    processed = markdown_text

    for index, poster in enumerate(posters, start=start_index):
        poster_type = poster["type"]
        image_path = generate_poster(poster, str(output_dir))
        label = poster["config"].get("title") or f"{poster_type} poster"
        placeholder = f"\n\n【图 {index}：{label}】\n\n"
        processed = processed.replace(poster["original"], placeholder)
        generated.append(
            {
                "index": index,
                "type": poster_type,
                "title": label,
                "path": image_path,
                "placeholder": placeholder.strip(),
            }
        )
    return processed, generated


def normalize_body_images(paths: list[str], titles: list[str]) -> list[dict]:
    images = []
    for index, raw_path in enumerate(paths, start=1):
        image_path = Path(raw_path).expanduser()
        if not image_path.is_absolute():
            image_path = image_path.resolve()
        title = titles[index - 1] if index - 1 < len(titles) else f"正文配图 {index}"
        placeholder = f"【图 {index}：{title}】"
        images.append(
            {
                "index": index,
                "type": "body-image",
                "title": title,
                "path": str(image_path),
                "placeholder": placeholder,
                "source": "explicit-body-image",
            }
        )
    return images


def inject_body_image_placeholders(markdown_text: str, images: list[dict], position: str) -> str:
    if not images:
        return markdown_text
    block = "\n\n" + "\n\n".join(image["placeholder"] for image in images) + "\n\n"
    if position == "top":
        return block + markdown_text
    if position == "end":
        return markdown_text.rstrip() + block

    lines = markdown_text.splitlines()
    paragraph_breaks = 0
    for idx, line in enumerate(lines):
        if not line.strip():
            paragraph_breaks += 1
        if paragraph_breaks >= 2:
            return "\n".join(lines[: idx + 1]) + block + "\n".join(lines[idx + 1 :])
    return markdown_text.rstrip() + block


def markdown_to_wechat_html(markdown_text: str) -> str:
    html = markdown.markdown(markdown_text, extensions=["fenced_code", "tables", "nl2br", "extra"])
    soup = BeautifulSoup(html, "html.parser")

    wrapper = soup.new_tag(
        "section",
        style=(
            "font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','PingFang SC',"
            "'Hiragino Sans GB','Microsoft YaHei',Arial,sans-serif;"
            f"color:{STYLE['text']};font-size:16px;line-height:1.8;"
        ),
    )
    for child in list(soup.contents):
        wrapper.append(child.extract())
    soup.append(wrapper)

    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        if tag.name == "h1":
            tag["style"] = (
                "margin:2.2em 8px 1.2em;font-size:1.32em;line-height:1.35;"
                f"color:{STYLE['primary']};font-weight:700;text-align:left;"
                f"border-left:4px solid {STYLE['accent']};padding-left:12px;"
            )
        elif tag.name == "h2":
            tag["style"] = (
                "margin:2.4em 8px 1em;padding:0 0 0.25em;"
                f"font-size:1.18em;line-height:1.35;color:{STYLE['primary']};"
                f"font-weight:700;border-bottom:1px solid {STYLE['border']};"
            )
        elif tag.name == "h3":
            tag["style"] = (
                f"margin:2em 8px 0.8em;padding-left:10px;border-left:3px solid {STYLE['accent']};"
                f"font-size:1.06em;color:{STYLE['primary']};font-weight:700;line-height:1.35;"
            )
        else:
            tag["style"] = f"margin:1.8em 8px 0.7em;color:{STYLE['primary']};font-weight:700;"

    for tag in soup.find_all("p"):
        text = tag.get_text(strip=True)
        if re.fullmatch(r"【图\s+\d+：.+】", text):
            tag["style"] = (
                f"margin:1.8em 8px;padding:0.85em 1em;border:1px dashed {STYLE['border']};"
                f"border-left:3px solid {STYLE['accent']};border-radius:6px;"
                f"background:{STYLE['surface']};color:{STYLE['muted']};font-size:0.95em;"
            )
        else:
            tag["style"] = (
                "margin:1.35em 8px;letter-spacing:0.03em;"
                f"color:{STYLE['text']};line-height:1.85;text-align:justify;"
            )

    for tag in soup.find_all("a"):
        tag["style"] = f"color:{STYLE['accent']};text-decoration:none;border-bottom:1px solid rgba(0,47,167,.22);"

    for tag in soup.find_all(["strong", "b"]):
        tag["style"] = f"font-weight:700;color:{STYLE['accent']};"

    for tag in soup.find_all("blockquote"):
        tag["style"] = (
            f"margin:1.5em 8px;padding:1em 1.1em;border-left:3px solid {STYLE['accent']};"
            f"background:{STYLE['surface']};border-radius:6px;color:{STYLE['text']};"
        )
        for p in tag.find_all("p"):
            p["style"] = f"margin:0;color:{STYLE['text']};line-height:1.8;"

    for tag in soup.find_all(["ul", "ol"]):
        tag["style"] = f"margin:1.4em 8px;padding-left:1.4em;color:{STYLE['text']};line-height:1.75;"
    for tag in soup.find_all("li"):
        tag["style"] = "margin:0.45em 0;letter-spacing:0.02em;"

    for code in soup.find_all("code"):
        if code.parent and code.parent.name == "pre":
            continue
        code["style"] = (
            "font-family:Menlo,Monaco,Consolas,'Courier New',monospace;font-size:0.9em;"
            f"color:{STYLE['primary']};background:{STYLE['code_bg']};padding:2px 5px;border-radius:4px;"
        )

    for pre in soup.find_all("pre"):
        pre["style"] = (
            "display:block;margin:1.6em 8px;padding:1em;line-height:1.5;"
            f"color:{STYLE['text']};background:{STYLE['surface']};border:1px solid {STYLE['border']};border-radius:8px;overflow-x:auto;"
            "font-size:0.88em;white-space:pre-wrap;word-break:break-word;"
        )
        code = pre.find("code")
        if code:
            code["style"] = "font-family:Menlo,Monaco,Consolas,monospace;color:inherit;background:transparent;"

    for hr in soup.find_all("hr"):
        hr["style"] = f"border:none;border-top:1px solid {STYLE['border']};margin:2em 8px;"

    for img in soup.find_all("img"):
        img["style"] = "max-width:100%;height:auto;display:block;margin:1.6em auto;border-radius:6px;"

    return str(soup)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--cover-image", help="Stable cover image path for API draft creation")
    parser.add_argument(
        "--body-image",
        action="append",
        default=[],
        help="Stable body image path to insert as a visible placeholder and upload through API",
    )
    parser.add_argument(
        "--body-image-title",
        action="append",
        default=[],
        help="Title for the matching --body-image entry",
    )
    parser.add_argument(
        "--body-image-position",
        choices=["after-intro", "top", "end"],
        default="after-intro",
    )
    args = parser.parse_args()

    source = Path(args.source)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = source.read_text(encoding="utf-8")
    title, body, notes = strip_title_and_noise(raw)
    explicit_images = normalize_body_images(args.body_image, args.body_image_title)
    body = inject_body_image_placeholders(body, explicit_images, args.body_image_position)
    body_with_placeholders, posters = replace_posters(body, output_dir, start_index=len(explicit_images) + 1)
    body_images = explicit_images + posters
    html = markdown_to_wechat_html(body_with_placeholders)

    (output_dir / "article.wechat.html").write_text(html, encoding="utf-8")
    (output_dir / "article.plain.txt").write_text(
        BeautifulSoup(html, "html.parser").get_text("\n"), encoding="utf-8"
    )
    (output_dir / "title.txt").write_text(title, encoding="utf-8")
    manifest = {
        "title": title,
        "source": str(source),
        "cover_image": str(Path(args.cover_image).expanduser().resolve()) if args.cover_image else "",
        "notes": notes or ["none"],
        "body_images": body_images,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    manifest_lines = [f"title: {title}", "notes:"]
    manifest_lines.extend([f"  - {note}" for note in notes] or ["  - none"])
    if args.cover_image:
        manifest_lines.append(f"cover_image: {manifest['cover_image']}")
    manifest_lines.append("posters:")
    for poster in body_images:
        manifest_lines.append(f"  - index: {poster['index']}")
        manifest_lines.append(f"    type: {poster['type']}")
        manifest_lines.append(f"    title: {poster['title']}")
        manifest_lines.append(f"    path: {poster['path']}")
        manifest_lines.append(f"    placeholder: {poster['placeholder']}")
    (output_dir / "manifest.yaml").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(output_dir)


if __name__ == "__main__":
    main()
