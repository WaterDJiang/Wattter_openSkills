#!/usr/bin/env python3
"""
Jimeng (即梦) image generation backend.

Shells out to the sibling `wtt-jimeng-api` skill's CLI
(`scripts/jimeng_api.py image "prompt" ...`), which handles session auth,
auto-starts the Jimeng backend Docker container if it is down, downloads the
result, and writes it to `--output`. This backend then renames the downloaded
`jimeng_<ts>_<i>.png` to the requested filename stem.

Designed for the sequential fallback chain in `image_gen.py`: it is fail-fast
(one attempt, no internal retry loop) so that a slow or unavailable Jimeng
service yields quickly to the next chain entry (e.g. minimax, zhipu, pexels).

Credentials: the CLI reads `JIMENG_SESSION_ID` from the environment (inherited
from the parent process, which loads `.env`) or `session_id` from
`wtt-jimeng-api/config.json`. If neither is set the CLI exits non-zero and this
backend raises — the chain moves on.

Env knobs:
  JIMENG_API_SCRIPT  Absolute path override for jimeng_api.py (else auto-detected
                     as the sibling skill at ../../../wtt-jimeng-api/scripts/).
  JIMENG_TIMEOUT     Subprocess timeout in seconds (default 180; first call may
                     need to pull/start the Docker backend, so raise if needed).
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    from image_backends.backend_common import MAX_RETRIES  # noqa: F401
except ImportError:
    MAX_RETRIES = 3

DEFAULT_MODEL = "jimeng-5.0"

# image_gen.py image_size -> jimeng --resolution
_SIZE_TO_RESOLUTION = {
    "512px": "1k",
    "1K": "1k",
    "1k": "1k",
    "2K": "2k",
    "2k": "2k",
    "4K": "4k",
    "4k": "4k",
}

# Ratios jimeng accepts directly.
_SUPPORTED_RATIOS = {"1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3", "21:9"}


def _resolve_jimeng_script() -> str:
    override = os.environ.get("JIMENG_API_SCRIPT", "").strip()
    if override and os.path.isfile(override):
        return override
    # scripts/image_backends/backend_jimeng.py -> ../../../wtt-jimeng-api/scripts/jimeng_api.py
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.normpath(
        os.path.join(here, "..", "..", "..", "wtt-jimeng-api", "scripts", "jimeng_api.py")
    )
    return candidate


def _map_resolution(image_size: str) -> str:
    if not image_size:
        return "2k"
    return _SIZE_TO_RESOLUTION.get(image_size, "2k")


def _normalize_ratio(aspect_ratio: str) -> str:
    if aspect_ratio in _SUPPORTED_RATIOS:
        return aspect_ratio
    # Fall back to a safe default for ratios jimeng does not accept.
    return "4:3"


def _find_and_rename(output_dir: str, target_stem: str, started_at: float) -> str:
    """Find the newest jimeng_*.png created after `started_at` and rename it."""
    out = Path(output_dir)
    candidates = [
        p for p in out.glob("jimeng_*.png")
        if p.stat().st_mtime >= started_at - 1
    ]
    if not candidates:
        raise RuntimeError(
            f"jimeng CLI did not produce a jimeng_*.png file in {output_dir}"
        )
    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    target = out / f"{target_stem}.png"
    if target.exists():
        target.unlink()
    shutil.move(str(newest), str(target))
    return str(target)


def generate(prompt: str,
             aspect_ratio: str = "1:1", image_size: str = "1K",
             output_dir: str = None, filename: str = None,
             model: str = None, max_retries: int = MAX_RETRIES) -> str:
    """Generate one image via the wtt-jimeng-api skill CLI.

    Returns the saved file path on success, raises RuntimeError on failure.

    Note: `max_retries` is intentionally ignored — this backend is fail-fast
    (single attempt) so the acquisition chain can fall through to the next
    backend quickly. The chain itself is the resilience layer.
    """
    del max_retries  # fail-fast by design; chain handles fallback

    script = _resolve_jimeng_script()
    if not os.path.isfile(script):
        raise RuntimeError(
            f"jimeng_api.py not found at {script}. Set JIMENG_API_SCRIPT to its "
            f"absolute path, or ensure the wtt-jimeng-api skill is installed as a "
            f"sibling of this skill."
        )

    out_dir = output_dir or "."
    os.makedirs(out_dir, exist_ok=True)
    target_stem = filename or "jimeng_image"

    resolved_model = model or os.environ.get("JIMENG_MODEL") or DEFAULT_MODEL
    ratio = _normalize_ratio(aspect_ratio)
    resolution = _map_resolution(image_size)

    # Global flags (--output, --no-auto-start omitted to keep auto-start ON)
    # must precede the `image` subcommand; subcommand flags follow it.
    cmd = [
        sys.executable, script,
        "--output", out_dir,
        "image", prompt,
        "--model", resolved_model,
        "--ratio", ratio,
        "--resolution", resolution,
        "--format", "b64_json",
    ]

    timeout = int(os.environ.get("JIMENG_TIMEOUT", "180"))
    started_at = time.time()
    try:
        proc = subprocess.run(
            cmd, timeout=timeout, check=False,
            capture_output=True, text=True,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"jimeng CLI timed out after {timeout}s (first call may pull the "
            f"Docker backend; raise JIMENG_TIMEOUT if needed)"
        )

    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-400:]
        raise RuntimeError(f"jimeng CLI exited {proc.returncode}: {tail}")

    return _find_and_rename(out_dir, target_stem, started_at)


if __name__ == "__main__":
    #流水线外一次性测试: python3 backend_jimeng.py "a serene mountain lake at dawn" 16:9 2K ./out cover_bg
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        print("Test usage: python3 backend_jimeng.py <prompt> [aspect_ratio] [image_size] [output_dir] [filename]")
        sys.exit(0)
    p = args[0]
    ar = args[1] if len(args) > 1 else "1:1"
    sz = args[2] if len(args) > 2 else "2K"
    od = args[3] if len(args) > 3 else "./out"
    fn = args[4] if len(args) > 4 else "jimeng_test"
    path = generate(prompt=p, aspect_ratio=ar, image_size=sz, output_dir=od, filename=fn)
    print(f"Saved: {path}")
