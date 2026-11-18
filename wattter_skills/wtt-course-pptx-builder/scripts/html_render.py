#!/usr/bin/env python3
"""
PPT Master - HTML Background Renderer

Render Strategist-declared HTML background templates to PNG assets via headless
Chromium (Playwright). Part of the layered architecture: an HTML-PNG background
layer + an SVG text overlay → PPTX. The script reads an explicit manifest
declared by the Strategist; it never scans spec_lock.md or source content.

The rendered PNG is later referenced as a full-bleed <image> (first child of
<svg>) by the Executor, and flows through the existing finalize_svg /
svg_to_pptx native pipeline UNCHANGED — z-order is guaranteed by SVG document
order, so the background <image> naturally becomes the bottom PPT layer while
SVG text shapes stay editable on top.

HTML templates render ONLY visual elements (gradients, color blocks, geometric
decor, logo mark). All editable text (title / subtitle / author / date /
chapter name / page number) is reserved as `<!-- text-slot: name x1,y1 x2,y2 -->`
coordinate comments and placed by the Executor in the SVG text layer — keeping
PPT text fully editable.

Usage:
    python3 scripts/html_render.py <project_path>
    python3 scripts/html_render.py <project_path> --manifest images/html_background_manifest.json
    python3 scripts/html_render.py <project_path> --dry-run
    python3 scripts/html_render.py <project_path> --fallback-solid
    python3 scripts/html_render.py <project_path> --render-md

Exit codes:
    0 — all background items rendered
    1 — configuration / manifest error (or dry-run validation failure)
    2 — one or more render failures (details in stderr)
    3 — Playwright + Chromium missing or unable to launch (non-fallback mode)

Dependencies:
    Pillow (fallback-solid pure-color PNG generation + dimension measurement)
    Playwright + Chromium (HTML→PNG rendering; NOT needed for --fallback-solid)
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:
    Image = None


DEFAULT_MANIFEST = "images/html_background_manifest.json"
DEFAULT_CANVAS = (1280, 720)
DEFAULT_DEVICE_SCALE_FACTOR = 2
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
VALID_TEMPLATES = ("cover", "ending", "chapter", "theme")
VALID_FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*\.png$")
# <!-- text-slot: name x1,y1 x2,y2 -->
TEXT_SLOT_RE = re.compile(
    r"<!--\s*text-slot:\s*([A-Za-z_][A-Za-z0-9_]*)\s+"
    r"(\d+),(\d+)\s+(\d+),(\d+)\s*-->"
)
# An <img> tag whose class attribute contains the token `logo`.
LOGO_IMG_RE = re.compile(r'<img[^>]*class="[^"]*\blogo\b[^"]*"[^>]*>', re.IGNORECASE)

# Skill root = parent of the scripts/ directory.
SKILL_DIR = Path(__file__).resolve().parent.parent
STYLES_DIR = SKILL_DIR / "templates" / "html-background-styles"


def _safe_print(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _project_relative(path: Path, project_path: Path) -> str:
    """Return a POSIX-style path relative to the project."""
    return path.relative_to(project_path).as_posix()


def _load_manifest(path: Path) -> dict[str, Any]:
    """Load a JSON HTML-background manifest."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"Cannot read manifest: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Manifest is not valid JSON: {path} ({exc})") from exc

    if not isinstance(data, dict):
        raise RuntimeError("Manifest root must be a JSON object.")
    items = data.get("items")
    if not isinstance(items, list):
        raise RuntimeError("Manifest must contain an `items` array.")
    return data


def _safe_filename(item: dict[str, Any], index: int) -> str:
    """Resolve and validate the output PNG filename for one background."""
    filename = item.get("filename")
    if filename is None:
        item_id = str(item.get("id") or f"bg_{index:03d}")
        filename = f"{item_id}.png"
    filename = str(filename)
    if "/" in filename or "\\" in filename or not VALID_FILENAME_RE.match(filename):
        raise RuntimeError(
            f"Invalid background filename `{filename}`. Use a simple PNG filename "
            "such as `bg_cover.png`."
        )
    return filename


def _parse_canvas(value: Any) -> tuple[int, int]:
    """Parse a canvas spec like '1280x720' or [1280, 720]."""
    if not value:
        return DEFAULT_CANVAS
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return (int(value[0]), int(value[1]))
    if isinstance(value, str):
        parts = [p for p in re.split(r"[x×*,\s]+", value.strip()) if p]
        if len(parts) == 2:
            return (int(parts[0]), int(parts[1]))
    raise RuntimeError(f"Invalid canvas value: {value!r}. Expected e.g. '1280x720'.")


def _normalize_hex(color: Any, default: str) -> str:
    """Normalize an optional HEX color to an uppercase #RRGGBB string."""
    if not color:
        return default
    value = str(color).strip()
    if not value.startswith("#"):
        value = "#" + value
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        raise RuntimeError(f"Invalid HEX color: {color!r}")
    return value.upper()


def _style_dir(style: str) -> Path:
    """Locate a style directory under templates/html-background-styles/."""
    path = STYLES_DIR / style
    if not path.is_dir():
        available: list[str] = []
        if STYLES_DIR.is_dir():
            available = sorted(p.name for p in STYLES_DIR.iterdir() if p.is_dir())
        raise RuntimeError(
            f"HTML background style `{style}` not found at {path}. "
            f"Available styles: {', '.join(available) or '(none)'}."
        )
    return path


def _template_path(style: str, template: str) -> Path:
    """Locate <style>/<template>.html, validating the template name first."""
    if template not in VALID_TEMPLATES:
        raise RuntimeError(
            f"Invalid template `{template}`. Must be one of: {', '.join(VALID_TEMPLATES)}."
        )
    path = _style_dir(style) / f"{template}.html"
    if not path.is_file():
        raise RuntimeError(f"Template HTML not found: {path}")
    return path


def _load_slots(style: str) -> dict[str, dict[str, list[int]]]:
    """Load slots.json for a style: {template: {slot_name: [x1,y1,x2,y2]}}."""
    path = _style_dir(style) / "slots.json"
    if not path.is_file():
        raise RuntimeError(f"slots.json not found for style `{style}`: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"slots.json is not valid JSON: {path} ({exc})") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"slots.json root must be an object: {path}")
    return data


def _extract_text_slots(html: str) -> dict[str, list[int]]:
    """Extract `<!-- text-slot: name x1,y1 x2,y2 -->` comments from HTML source."""
    slots: dict[str, list[int]] = {}
    for match in TEXT_SLOT_RE.finditer(html):
        name = match.group(1)
        coords = [int(match.group(i)) for i in range(2, 6)]
        slots[name] = coords
    return slots


def _validate_slots(
    extracted: dict[str, list[int]],
    slots_entry: dict[str, list[int]] | None,
    template: str,
    style: str,
) -> None:
    """Ensure HTML-extracted slots match slots.json (the source of truth)."""
    expected = slots_entry or {}
    extracted_names = set(extracted.keys())
    expected_names = set(expected.keys())
    if extracted_names != expected_names:
        missing = expected_names - extracted_names
        extra = extracted_names - expected_names
        parts: list[str] = []
        if missing:
            parts.append(f"missing in HTML: {sorted(missing)}")
        if extra:
            parts.append(f"extra in HTML: {sorted(extra)}")
        raise RuntimeError(
            f"text-slot mismatch for `{style}/{template}` ({'; '.join(parts)}). "
            "HTML comments and slots.json must agree; slots.json is the source of truth."
        )
    for name in expected_names:
        if extracted[name] != list(expected[name]):
            raise RuntimeError(
                f"text-slot `{name}` coords differ for `{style}/{template}`: "
                f"HTML={extracted[name]} slots.json={list(expected[name])}."
            )


def _validate_slot_geometry(
    slots_entry: dict[str, list[int]],
    canvas: tuple[int, int],
    template: str,
    style: str,
) -> None:
    """Sanity-check slot coordinates against the canvas (slots.json is the source
    of truth, but it can still carry typos — out-of-canvas or inverted slots, or
    slots so overlapping they'd stack text). Catches authoring errors that
    `_validate_slots` (which only checks HTML↔json parity) cannot."""
    canvas_w, canvas_h = canvas
    items = [(name, coords) for name, coords in slots_entry.items() if coords]
    # 1. Each slot is a positive-area rectangle inside the canvas.
    for name, coords in items:
        try:
            x1, y1, x2, y2 = (int(c) for c in coords)
        except (TypeError, ValueError):
            raise RuntimeError(
                f"text-slot `{name}` for `{style}/{template}` has non-integer "
                f"coords: {coords}."
            )
        if x2 <= x1 or y2 <= y1:
            raise RuntimeError(
                f"text-slot `{name}` for `{style}/{template}` is not a positive-area "
                f"rectangle: [{x1},{y1} {x2},{y2}] (need x2>x1 and y2>y1)."
            )
        if x1 < 0 or y1 < 0 or x2 > canvas_w or y2 > canvas_h:
            raise RuntimeError(
                f"text-slot `{name}` for `{style}/{template}` extends outside the "
                f"canvas ({canvas_w}x{canvas_h}): [{x1},{y1} {x2},{y2}]."
            )

    # 2. No two slots overlap by more than half the smaller slot's area — that
    # would stack their text. Adjacent/nesting-by-design slots touch at edges
    # only, which this threshold permits.
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            n1, c1 = items[i]
            n2, c2 = items[j]
            ix1 = max(c1[0], c2[0])
            iy1 = max(c1[1], c2[1])
            ix2 = min(c1[2], c2[2])
            iy2 = min(c1[3], c2[3])
            if ix2 <= ix1 or iy2 <= iy1:
                continue  # no overlap
            overlap = (ix2 - ix1) * (iy2 - iy1)
            a1 = (c1[2] - c1[0]) * (c1[3] - c1[1])
            a2 = (c2[2] - c2[0]) * (c2[3] - c2[1])
            smaller = min(a1, a2)
            if smaller > 0 and overlap > smaller * 0.5:
                raise RuntimeError(
                    f"text-slots `{n1}` and `{n2}` for `{style}/{template}` overlap "
                    f"by {int(overlap)}px² (>50% of the smaller slot) — their text "
                    f"would collide. Adjust slots.json."
                )


def _logo_data_uri(logo: dict[str, Any] | None, project_path: Path) -> str | None:
    """Resolve a logo reference to a data URI, or None if no usable logo."""
    if not logo:
        return None
    href = logo.get("href")
    if not href:
        return None
    path = Path(href)
    if not path.is_absolute():
        path = project_path / href
    if not path.is_file():
        _safe_print(f"[WARN] logo not found, skipping: {path}")
        return None
    suffix = path.suffix.lower()
    mime_map = {".svg": "image/svg+xml", ".png": "image/png",
                ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
    mime = mime_map.get(suffix)
    if mime is None:
        _safe_print(f"[WARN] unsupported logo type `{suffix}`, skipping: {path}")
        return None
    data = path.read_bytes()
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def _inject_variables(
    html: str, variables: dict[str, Any], logo_data_uri: str | None
) -> str:
    """Replace {{var}} placeholders and inject the logo (or strip its <img>)."""
    out = html
    for key, value in variables.items():
        out = out.replace("{{" + str(key) + "}}", str(value))
    if logo_data_uri:
        out = out.replace("{{logo_href}}", logo_data_uri)
    else:
        # Remove any <img class="logo" ...> tag and clear stray placeholder.
        out = LOGO_IMG_RE.sub("", out)
        out = out.replace("{{logo_href}}", "")
    return out


def _render_html_to_png(
    html: str, canvas: tuple[int, int], device_scale_factor: int
) -> bytes:
    """Render HTML to PNG bytes via Playwright/Chromium."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "playwright not installed. Install with:\n"
            "    pip install playwright\n"
            "    python3 -m playwright install chromium\n"
            "(see ${SKILL_DIR}/requirements.txt)"
        )

    width, height = canvas
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:  # noqa: BLE001 — browser launch failure
            raise RuntimeError(
                f"Chromium failed to launch: {type(exc).__name__}: {exc}\n"
                "try:  python3 -m playwright install chromium"
            ) from exc
        try:
            context = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=device_scale_factor,
            )
            page = context.new_page()
            page.set_content(html, wait_until="domcontentloaded")
            # Wait for fonts to actually load (deterministic) instead of a blind
            # fixed delay. system fonts resolve immediately; this matters most if
            # a template ever adds @font-face / web fonts. Fall back to a short
            # fixed wait if the fonts API is unavailable or stalls.
            try:
                page.wait_for_function(
                    "document.fonts && document.fonts.status === 'loaded'",
                    timeout=2000,
                )
            except Exception:  # noqa: BLE001 — fonts.ready unavailable or timed out
                page.wait_for_timeout(200)
            # One extra frame for any post-font reflow before capture.
            page.wait_for_timeout(50)
            png_bytes = page.screenshot(
                type="png",
                clip={"x": 0, "y": 0, "width": width, "height": height},
            )
        finally:
            browser.close()

    if not png_bytes.startswith(PNG_SIGNATURE):
        raise RuntimeError("Playwright did not return PNG data.")
    return png_bytes


def _render_fallback_solid(
    variables: dict[str, Any], canvas: tuple[int, int], device_scale_factor: int
) -> bytes:
    """Generate a solid-color PNG without Playwright (--fallback-solid)."""
    if Image is None:
        raise RuntimeError(
            "Pillow is required for --fallback-solid. Run: pip install Pillow"
        )
    color = _normalize_hex(variables.get("bg"), "#FFFFFF")
    width, height = canvas
    img = Image.new(
        "RGB",
        (width * device_scale_factor, height * device_scale_factor),
        color,
    )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _image_dimensions(path: Path) -> tuple[int, int]:
    """Read PNG dimensions."""
    if Image is None:
        raise RuntimeError(
            "Pillow is required to measure PNG dimensions. Run: pip install Pillow"
        )
    with Image.open(path) as img:
        return img.size


def _process_item(
    item: dict[str, Any],
    index: int,
    project_path: Path,
    output_dir: Path,
    defaults: dict[str, Any],
    dry_run: bool,
    fallback_solid: bool,
) -> dict[str, Any]:
    """Render one manifest item and return its updated record."""
    template = str(item.get("template") or "").strip().lower()
    if template not in VALID_TEMPLATES:
        raise RuntimeError(
            f"Background item #{index} has invalid `template`: {template!r}. "
            f"Must be one of: {', '.join(VALID_TEMPLATES)}."
        )
    style = str(item.get("style") or defaults.get("style") or "").strip().lower()
    if not style:
        raise RuntimeError(f"Background item #{index} is missing `style`.")

    filename = _safe_filename(item, index)
    output_path = output_dir / filename
    variables = {**(defaults.get("variables") or {}), **(item.get("variables") or {})}
    if not isinstance(variables, dict):
        raise RuntimeError(f"Background item #{index} `variables` must be an object.")
    canvas = _parse_canvas(item.get("canvas") or defaults.get("canvas"))
    dsf = int(
        item.get("device_scale_factor")
        or defaults.get("device_scale_factor")
        or DEFAULT_DEVICE_SCALE_FACTOR
    )
    logo = item.get("logo") if item.get("logo") is not None else defaults.get("logo")

    # Locate template + slots contract (also validates style/template existence).
    tpl_path = _template_path(style, template)
    slots_all = _load_slots(style)
    slots_entry = slots_all.get(template)
    if slots_entry is None:
        raise RuntimeError(
            f"slots.json for style `{style}` has no entry for template `{template}`. "
            f"Known templates: {', '.join(sorted(slots_all.keys()))}."
        )

    html_source = tpl_path.read_text(encoding="utf-8")
    extracted_slots = _extract_text_slots(html_source)
    _validate_slots(extracted_slots, slots_entry, template, style)
    _validate_slot_geometry(slots_entry, canvas, template, style)
    # slots.json is the source of truth for the manifest's text_slots.
    text_slots = {name: list(coords) for name, coords in slots_entry.items()}

    updated = dict(item)
    updated["filename"] = filename
    updated["file"] = _project_relative(output_path, project_path)
    updated["template"] = template
    updated["style"] = style
    updated["canvas"] = f"{canvas[0]}x{canvas[1]}"
    updated["device_scale_factor"] = dsf
    updated["text_slots"] = text_slots

    if dry_run:
        updated["status"] = item.get("status") or "Pending"
        return updated

    try:
        if fallback_solid:
            data = _render_fallback_solid(variables, canvas, dsf)
            updated["renderer"] = "fallback-solid"
            updated["status"] = "Fallback-Solid"
        else:
            logo_uri = _logo_data_uri(logo, project_path)
            # Expose canvas dimensions as {{canvas_w}} / {{canvas_h}} so a single
            # template adapts to any canvas format (16:9, 4:3, portrait, …).
            inject_vars = dict(variables)
            inject_vars["canvas_w"] = canvas[0]
            inject_vars["canvas_h"] = canvas[1]
            html = _inject_variables(html_source, inject_vars, logo_uri)
            data = _render_html_to_png(html, canvas, dsf)
            updated["renderer"] = "playwright-chromium"
            updated["status"] = "Rendered-HTML"
        output_path.write_bytes(data)
        width, height = _image_dimensions(output_path)
        updated["pixel_width"] = width
        updated["pixel_height"] = height
        updated.pop("error", None)
    except RuntimeError as exc:
        updated["status"] = "Failed"
        updated["error"] = str(exc)

    return updated


def _render_md_sidecar(manifest: dict[str, Any], project_path: Path) -> Path:
    """Write images/html_backgrounds.md audit sidecar."""
    lines: list[str] = ["# HTML Backgrounds", ""]
    lines.append(f"- style: `{manifest.get('style')}`")
    lines.append(f"- theme_palette: `{manifest.get('theme_palette')}`")
    lines.append("")

    for item in manifest.get("items", []):
        lines.append(f"## {item.get('id') or item.get('filename')}")
        lines.append(f"- template: `{item.get('template')}`")
        lines.append(f"- style: `{item.get('style')}`")
        lines.append(f"- filename: `{item.get('filename')}`")
        lines.append(f"- status: `{item.get('status')}`")
        slots = item.get("text_slots") or {}
        if slots:
            lines.append("- text-slots:")
            for name, coords in slots.items():
                lines.append(
                    f"  - `{name}`: {coords[0]},{coords[1]} {coords[2]},{coords[3]}"
                )
        if item.get("error"):
            lines.append(f"- error: {item['error']}")
        lines.append("")

    out = project_path / "images" / "html_backgrounds.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def render_manifest(
    project_path: Path,
    manifest_path: Path,
    *,
    dry_run: bool = False,
    fallback_solid: bool = False,
    render_md: bool = False,
) -> int:
    """Render all HTML backgrounds declared in a manifest."""
    manifest = _load_manifest(manifest_path)
    output_dir = project_path / "images"
    renderer_cfg = manifest.get("renderer") or {}
    canvas = _parse_canvas(renderer_cfg.get("canvas"))
    dsf = int(renderer_cfg.get("device_scale_factor") or DEFAULT_DEVICE_SCALE_FACTOR)
    defaults = {
        "canvas": f"{canvas[0]}x{canvas[1]}",
        "device_scale_factor": dsf,
        "variables": manifest.get("variables") or {},
        "logo": manifest.get("logo"),
        "style": manifest.get("style"),
    }

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Pre-flight: detect Playwright availability in non-fallback, non-dry-run mode.
    if not dry_run and not fallback_solid:
        try:
            import playwright.sync_api  # noqa: F401
        except ImportError:
            _safe_print(
                "playwright not installed. Install with:\n"
                "    pip install playwright\n"
                "    python3 -m playwright install chromium\n"
                "(or re-run with --fallback-solid for a solid-color background)"
            )
            return 3

    updated_items: list[dict[str, Any]] = []
    failures = 0
    for index, raw_item in enumerate(manifest["items"], 1):
        if not isinstance(raw_item, dict):
            _safe_print(f"Error: background item #{index} must be an object.")
            return 1
        try:
            updated = _process_item(
                raw_item, index, project_path, output_dir,
                defaults, dry_run, fallback_solid,
            )
        except RuntimeError as exc:
            # Validation error (bad template/style/slots) — mark failed, continue.
            updated = dict(raw_item)
            updated["status"] = "Failed"
            updated["error"] = str(exc)
            failures += 1
            label = updated.get("id") or updated.get("filename") or f"item #{index}"
            _safe_print(f"Failed: {label} -> {exc}")
            updated_items.append(updated)
            continue

        updated_items.append(updated)
        status = updated.get("status")
        label = updated.get("id") or updated.get("filename")
        _safe_print(f"{status}: {label} -> {updated.get('file')}")
        if status == "Failed":
            failures += 1
            _safe_print(f"  {updated.get('error')}")

    if dry_run:
        if failures:
            _safe_print(
                f"Dry run: {failures} validation failure(s) among "
                f"{len(updated_items)} item(s)."
            )
            return 1
        _safe_print(f"Dry run: {len(updated_items)} background item(s) parsed OK.")
        return 0

    manifest["items"] = updated_items
    manifest.setdefault("renderer", {})
    manifest["renderer"]["engine"] = "fallback-solid" if fallback_solid else "playwright-chromium"
    manifest["renderer"]["canvas"] = f"{canvas[0]}x{canvas[1]}"
    manifest["renderer"]["device_scale_factor"] = dsf
    manifest["renderer"]["output_dir"] = _project_relative(output_dir, project_path)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if render_md:
        sidecar = _render_md_sidecar(manifest, project_path)
        _safe_print(f"sidecar: {_project_relative(sidecar, project_path)}")

    if failures:
        _safe_print(f"HTML background rendering completed with {failures} failure(s).")
        return 2
    _safe_print(f"HTML background rendering complete: {len(updated_items)} item(s).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Render Strategist-declared HTML background templates to PNG assets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_path", type=Path, help="Project directory.")
    parser.add_argument(
        "--manifest", type=Path, default=None,
        help=f"HTML background manifest path. Default: <project>/{DEFAULT_MANIFEST}",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate manifest, templates, and slot contracts without rendering.",
    )
    parser.add_argument(
        "--fallback-solid", action="store_true",
        help="Skip Playwright; emit solid-color PNGs (emergency fallback).",
    )
    parser.add_argument(
        "--render-md", action="store_true",
        help="Also write images/html_backgrounds.md audit sidecar.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    project_path = args.project_path.resolve()
    if not project_path.is_dir():
        _safe_print(f"Error: project directory not found: {project_path}")
        return 1

    manifest_path = args.manifest
    if manifest_path is None:
        manifest_path = project_path / DEFAULT_MANIFEST
    elif not manifest_path.is_absolute():
        manifest_path = project_path / manifest_path
    manifest_path = manifest_path.resolve()

    if not manifest_path.is_file():
        _safe_print(f"Error: manifest not found: {manifest_path}")
        return 1

    try:
        return render_manifest(
            project_path, manifest_path,
            dry_run=args.dry_run,
            fallback_solid=args.fallback_solid,
            render_md=args.render_md,
        )
    except RuntimeError as exc:
        _safe_print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
