#!/usr/bin/env python3
"""统一路由到具体平台发布脚本。"""

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

PLATFORM_ENTRYPOINTS = {
    "wechat": SKILL_DIR / "platforms" / "wechat" / "scripts" / "wechat_draft_poster.py",
    "zhihu": SKILL_DIR / "platforms" / "zhihu" / "scripts" / "zhihu_poster.py",
}


def normalize_extra_args(extra_args):
    """清理透传给平台脚本的附加参数。"""
    if extra_args and extra_args[0] == "--":
        return extra_args[1:]
    return extra_args


def build_platform_command(platform, markdown_path, extra_args):
    """构建平台脚本执行命令。"""
    entrypoint = PLATFORM_ENTRYPOINTS[platform]
    command = [sys.executable, str(entrypoint), "-m", markdown_path]
    command.extend(extra_args)
    return command


def parse_args():
    """解析统一入口参数，并保留未知参数透传给平台脚本。"""
    parser = argparse.ArgumentParser(description="Post markdown content to multiple platforms.")
    parser.add_argument(
        "--platform",
        required=True,
        choices=sorted(PLATFORM_ENTRYPOINTS.keys()),
        help="Target platform to publish.",
    )
    parser.add_argument("-m", "--markdown", required=True, help="Path to the markdown file.")
    return parser.parse_known_args()


def main():
    """根据平台参数路由到独立发布脚本。"""
    args, extra_args = parse_args()
    normalized_extra_args = normalize_extra_args(extra_args)
    command = build_platform_command(args.platform, args.markdown, normalized_extra_args)
    completed = subprocess.run(command, check=False)
    sys.exit(completed.returncode)


if __name__ == "__main__":
    main()
