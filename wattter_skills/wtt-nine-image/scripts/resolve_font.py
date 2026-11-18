#!/usr/bin/env python3
"""离线解析风格D真实字体；可将已有沐瑶原文件登记到独立用户目录。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


FONT_INFO = {
    "cover": ("沐瑶随心手写体", "MuyaoPleased.ttf",
              "62ab940ead12688125ea63824d9b7c16a4f3ee13fe85a0375843dcbe07ef374a"),
    "body": ("喜脉喜欢体", "FontQuSmile-Regular.ttf",
             "3f8d7e25a4c44a39530feae176bc80161de7dab397a639cda3da92edb9662eae"),
}


def persistent_dir():
    return Path.home() / ".local/share/nine-image/fonts"


def verify(path, usage):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = FONT_INFO[usage][2]
    if digest != expected:
        raise ValueError(f"字体校验失败: {path}；SHA-256={digest}，预期={expected}。"
                         "请核对原文件，不改用其他字体或自动下载。")
    return digest


def install_cover(source, directory):
    """只登记用户已取得的本机原文件，不联网，不纳入分发包。"""
    source = source.expanduser().resolve()
    verify(source, "cover")
    directory = directory.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / FONT_INFO["cover"][1]
    if source == destination:
        return destination
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix=".muyao-", delete=False) as handle:
            temporary = Path(handle.name)
            with source.open("rb") as incoming:
                shutil.copyfileobj(incoming, handle)
        verify(temporary, "cover")
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination


def resolve_font(usage, skill_dir, directory=None):
    directory = (directory if directory is not None else persistent_dir()).expanduser().resolve()
    skill_dir = skill_dir.expanduser().resolve()
    name, filename, _ = FONT_INFO[usage]
    if usage == "cover":
        candidates = [(directory / filename, "persistent"),
                      (skill_dir / "assets/fonts/local" / filename, "legacy-local")]
    else:
        candidates = [(skill_dir / "assets/fonts" / filename, "bundled")]
    for path, source in candidates:
        if path.exists():
            return {"usage": usage, "font_name": name, "font_path": str(path),
                    "sha256": verify(path, usage), "source": source}
    searched = "；".join(str(path) for path, _ in candidates)
    raise ValueError(f"本地字体缺失（{name}），已检查: {searched}。"
                     "本脚本不会联网。先核对用途和已有本地原文件；"
                     "确认确实缺失后，按 assets/fonts/MUYAO-SOURCE.md 或 SOURCE.md 获取。")


def check_text(path, text):
    try:
        from fontTools.ttLib import TTFont
    except ImportError as error:
        raise ValueError("逐字检查需要 fontTools；字体路径解析无需此依赖。") from error
    characters = set(text) - set(character for character in text if character.isspace())
    with TTFont(path) as font:
        cmap = font.getBestCmap() or {}
    missing = sorted(character for character in characters if ord(character) not in cmap)
    if missing:
        raise ValueError("字体缺字: " + " ".join(f"{c} (U+{ord(c):04X})" for c in missing)
                         + "；保留原文，不能静默换字体。")
    return len(characters)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usage", choices=FONT_INFO, required=True)
    parser.add_argument("--install-cover-from", type=Path,
                        help="把已有沐瑶TTF校验后登记到独立本机目录，仅用于cover")
    parser.add_argument("--text", help="可选：检查本次完整文案的cmap，需fontTools")
    args = parser.parse_args()
    if args.install_cover_from is not None and args.usage != "cover":
        parser.error("--install-cover-from 仅用于 --usage cover；正文默认喜脉")
    try:
        if args.install_cover_from is not None:
            install_cover(args.install_cover_from, persistent_dir())
        result = resolve_font(args.usage, Path(__file__).resolve().parents[1])
        if args.text is not None:
            result["checked_characters"] = check_text(result["font_path"], args.text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        print(f"字体解析失败: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
