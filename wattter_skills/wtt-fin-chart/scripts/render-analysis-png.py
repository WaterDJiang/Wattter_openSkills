#!/usr/bin/env python3
"""Render a long PNG backup from a wtt-fin-chart analysis.json file."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PALETTE = {
    "paper": "#f5f0e7",
    "panel": "#fffaf0",
    "line": "#d7cec0",
    "ink": "#151515",
    "muted": "#696258",
    "growth": "#0f8b6f",
    "profit": "#b7791f",
    "cash": "#3b6ea8",
    "structure": "#6f5aa7",
    "risk": "#b64242",
}

COLORS = [
    PALETTE["growth"],
    PALETTE["profit"],
    PALETTE["cash"],
    PALETTE["structure"],
    PALETTE["risk"],
    "#8b6f47",
    "#2f6f73",
    "#8a4f7d",
]


def font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if serif:
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/Songti.ttc",
                "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            ]
        )
    candidates.extend(
        [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


FONT = {
    "h1": font(74, bold=True, serif=True),
    "h2": font(42, bold=True, serif=True),
    "h3": font(28, bold=True, serif=True),
    "body": font(22),
    "small": font(17),
    "mono": font(15),
}


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def blend(foreground: str, background: str, alpha: float) -> tuple[int, int, int]:
    fg = hex_to_rgb(foreground)
    bg = hex_to_rgb(background)
    alpha = max(0, min(1, alpha))
    return tuple(int(bg[i] * (1 - alpha) + fg[i] * alpha) for i in range(3))


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        candidate = current + ch
        if ch == "\n":
            lines.append(current)
            current = ""
        elif text_size(draw, candidate, fnt)[0] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


class Canvas:
    def __init__(self, width: int = 1600) -> None:
        self.width = width
        self.height = 9000
        self.image = Image.new("RGB", (self.width, self.height), PALETTE["paper"])
        self.draw = ImageDraw.Draw(self.image)
        self.y = 56
        self.margin = 56
        self._grid()

    def _grid(self) -> None:
        for x in range(0, self.width, 48):
            self.draw.line((x, 0, x, self.height), fill="#ece5d8", width=1)
        for y in range(0, self.height, 48):
            self.draw.line((0, y, self.width, y), fill="#ece5d8", width=1)

    def text(self, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, fill: str = PALETTE["ink"]) -> None:
        self.draw.text(xy, text, font=fnt, fill=fill)

    def wrapped(self, x: int, y: int, text: str, fnt: ImageFont.FreeTypeFont, width: int, fill: str = PALETTE["ink"], line_gap: int = 10) -> int:
        for line in wrap_text(self.draw, text, fnt, width):
            self.text((x, y), line, fnt, fill)
            y += text_size(self.draw, line, fnt)[1] + line_gap
        return y

    def panel(self, x: int, y: int, w: int, h: int) -> None:
        self.draw.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=PALETTE["panel"], outline=PALETTE["line"], width=2)

    def crop(self, bottom_padding: int = 60) -> Image.Image:
        return self.image.crop((0, 0, self.width, min(self.height, self.y + bottom_padding)))


def draw_metric(canvas: Canvas, x: int, y: int, w: int, h: int, item: dict) -> None:
    canvas.panel(x, y, w, h)
    canvas.text((x + 26, y + 26), str(item["label"]).upper(), FONT["mono"], PALETTE["muted"])
    canvas.text((x + 26, y + 68), str(item["display"]), FONT["h2"], PALETTE["ink"])
    canvas.text((x + 26, y + 138), str(item["delta"]), FONT["body"], PALETTE["growth"])
    canvas.wrapped(x + 26, y + 178, str(item["note"]), FONT["small"], w - 52, PALETTE["muted"], 8)


def draw_bar_list(canvas: Canvas, title: str, subtitle: str, items: list[dict], x: int, y: int, w: int, max_rows: int = 10, color: str = PALETTE["growth"]) -> int:
    rows = items[:max_rows]
    h = 122 + len(rows) * 48
    canvas.panel(x, y, w, h)
    canvas.text((x + 26, y + 24), title, FONT["h3"], PALETTE["ink"])
    canvas.wrapped(x + 26, y + 62, subtitle, FONT["small"], w - 52, PALETTE["muted"], 6)
    max_value = max((row["value"] for row in rows), default=1)
    yy = y + 116
    name_w = 330
    value_w = 170
    track_w = w - 52 - name_w - value_w - 24
    for row in rows:
        canvas.wrapped(x + 26, yy - 3, row["name"], FONT["small"], name_w, PALETTE["ink"], 0)
        canvas.draw.rounded_rectangle((x + 26 + name_w, yy, x + 26 + name_w + track_w, yy + 22), radius=11, fill=PALETTE["line"])
        fill_w = int(track_w * row["value"] / max_value)
        canvas.draw.rounded_rectangle((x + 26 + name_w, yy, x + 26 + name_w + fill_w, yy + 22), radius=11, fill=color)
        canvas.text((x + w - value_w - 26, yy - 2), f"{money(row['value'])} · {pct(row['share'])}", FONT["mono"], PALETTE["muted"])
        yy += 48
    return y + h


def draw_stacked(canvas: Canvas, title: str, items: list[dict], x: int, y: int, w: int) -> int:
    h = 150 + len(items) * 34
    canvas.panel(x, y, w, h)
    canvas.text((x + 26, y + 24), title, FONT["h3"], PALETTE["ink"])
    sx, sy, sw, sh = x + 26, y + 78, w - 52, 42
    cursor = sx
    for i, item in enumerate(items):
        seg_w = int(sw * item["share"])
        canvas.draw.rectangle((cursor, sy, cursor + seg_w, sy + sh), fill=COLORS[i % len(COLORS)])
        if seg_w > 90:
            label = pct(item["share"])
            tw, th = text_size(canvas.draw, label, FONT["small"])
            canvas.text((cursor + max(8, (seg_w - tw) // 2), sy + (sh - th) // 2 - 2), label, FONT["small"], "#ffffff")
        cursor += seg_w
    yy = y + 138
    for i, item in enumerate(items):
        canvas.draw.rectangle((x + 26, yy + 4, x + 40, yy + 18), fill=COLORS[i % len(COLORS)])
        canvas.text((x + 50, yy), item["name"], FONT["small"], PALETTE["ink"])
        canvas.text((x + w - 220, yy), f"{money(item['value'])} · {pct(item['share'])}", FONT["mono"], PALETTE["muted"])
        yy += 34
    return y + h


def draw_heatmap(canvas: Canvas, heatmap: dict, x: int, y: int, w: int) -> int:
    platforms = heatmap["platforms"]
    users = heatmap["users"]
    lookup = {(cell["platform"], cell["user"]): cell["value"] for cell in heatmap["cells"]}
    max_value = max(lookup.values(), default=1)
    first_w = 270
    col_w = (w - 52 - first_w) // len(users)
    header_h = 86
    row_h = 66
    h = 154 + header_h + len(platforms) * row_h
    canvas.panel(x, y, w, h)
    canvas.text((x + 26, y + 24), "PLATFORM × USER HEATMAP", FONT["mono"], PALETTE["muted"])
    canvas.text((x + 26, y + 62), "费用责任并不模糊，几个平台-使用人组合已经很清楚", FONT["h3"], PALETTE["ink"])
    canvas.text((x + 26, y + 104), "Readout: 深色格子就是最优先追踪的预算责任点。", FONT["body"], PALETTE["muted"])

    tx = x + 26
    ty = y + 150
    table_w = first_w + col_w * len(users)
    table_h = header_h + row_h * len(platforms)
    canvas.draw.rectangle((tx, ty, tx + table_w, ty + table_h), outline=PALETTE["line"], width=2)
    canvas.draw.rectangle((tx, ty, tx + table_w, ty + header_h), fill="#f8f1e6", outline=PALETTE["line"], width=2)
    canvas.text((tx + 18, ty + 28), "Platform / User", FONT["body"], PALETTE["ink"])
    for j, user in enumerate(users):
        cx = tx + first_w + j * col_w
        canvas.draw.line((cx, ty, cx, ty + table_h), fill=PALETTE["line"], width=2)
        lines = wrap_text(canvas.draw, user, FONT["small"], col_w - 18)
        yy = ty + 16
        for line in lines[:3]:
            canvas.text((cx + 10, yy), line, FONT["small"], PALETTE["muted"])
            yy += 20

    for i, platform in enumerate(platforms):
        ry = ty + header_h + i * row_h
        canvas.draw.line((tx, ry, tx + table_w, ry), fill=PALETTE["line"], width=2)
        canvas.text((tx + 18, ry + 20), platform, FONT["body"], PALETTE["ink"])
        for j, user in enumerate(users):
            cx = tx + first_w + j * col_w
            value = lookup.get((platform, user), 0)
            if value:
                strength = 0.16 + 0.68 * (value / max_value)
                fill = blend(PALETTE["growth"], PALETTE["panel"], strength)
            else:
                fill = hex_to_rgb(PALETTE["panel"])
            canvas.draw.rectangle((cx + 1, ry + 1, cx + col_w - 1, ry + row_h - 1), fill=fill)
            label = money(value) if value else "-"
            tw, th = text_size(canvas.draw, label, FONT["body"])
            color = "#ffffff" if value / max_value > 0.65 else PALETTE["ink"]
            canvas.text((cx + col_w - tw - 14, ry + (row_h - th) // 2 - 2), label, FONT["body"], color)

    return y + h


def draw_table(canvas: Canvas, title: str, subtitle: str, rows: list[dict], columns: list[tuple[str, str]], x: int, y: int, w: int, max_rows: int = 8) -> int:
    rows = rows[:max_rows]
    row_h = 46
    h = 128 + 52 + len(rows) * row_h
    canvas.panel(x, y, w, h)
    canvas.text((x + 26, y + 24), title, FONT["h3"], PALETTE["ink"])
    canvas.wrapped(x + 26, y + 62, subtitle, FONT["small"], w - 52, PALETTE["muted"], 6)
    tx = x + 26
    ty = y + 126
    table_w = w - 52
    widths = [int(table_w * 0.34), int(table_w * 0.28), int(table_w * 0.20), table_w - int(table_w * 0.34) - int(table_w * 0.28) - int(table_w * 0.20)]
    cursor = tx
    for idx, (_, label) in enumerate(columns):
        canvas.text((cursor + 8, ty + 12), label.upper(), FONT["mono"], PALETTE["muted"])
        cursor += widths[idx]
    canvas.draw.line((tx, ty + 42, tx + table_w, ty + 42), fill=PALETTE["line"], width=2)
    yy = ty + 52
    for row in rows:
        cursor = tx
        for idx, (key, _) in enumerate(columns):
            raw = row[key]
            if key == "value":
                value = money(raw)
            elif key == "share":
                value = pct(raw)
            else:
                value = str(raw)
            fill = PALETTE["ink"] if idx < 2 else PALETTE["muted"]
            max_width = widths[idx] - 12
            lines = wrap_text(canvas.draw, value, FONT["small"], max_width)
            canvas.text((cursor + 8, yy), lines[0], FONT["small"], fill)
            cursor += widths[idx]
        canvas.draw.line((tx, yy + row_h - 10, tx + table_w, yy + row_h - 10), fill=PALETTE["line"], width=1)
        yy += row_h
    return y + h


def render(data: dict, out: Path) -> None:
    c = Canvas()
    x = c.margin
    width = c.width - c.margin * 2

    c.text((x, c.y), "LLM COST INSIGHT", FONT["mono"], PALETTE["muted"])
    c.text((c.width - 260, c.y), data.get("periodLabel", ""), FONT["body"], PALETTE["ink"])
    c.y += 42
    c.y = c.wrapped(x, c.y, data["title"], FONT["h1"], width - 260, PALETTE["ink"], 12)
    c.y += 22
    c.y = c.wrapped(x, c.y, data["subtitle"], FONT["body"], width - 180, "#38312a", 10)
    c.y += 36
    c.draw.line((x, c.y, c.width - x, c.y), fill=PALETTE["ink"], width=2)
    c.y += 32

    left_w = 780
    right_w = width - left_w - 24
    thesis_h = 500
    c.panel(x, c.y, left_w, thesis_h)
    c.text((x + 28, c.y + 28), "CORE READ", FONT["mono"], PALETTE["muted"])
    c.wrapped(x + 28, c.y + 76, "控费入口不是“所有模型平均砍”，而是先治理两个成本发动机。", FONT["h2"], left_w - 56, PALETTE["ink"], 10)
    c.wrapped(x + 28, c.y + 260, "这份数据呈现的是单日成本快照。费用主要由视觉生成链路和 GPT-5.4/Gemini 3.1 两个模型簇牵引；如果要降低支出，应优先把调用场景、任务规格和责任单元拆清楚。", FONT["body"], left_w - 56, "#38312a", 10)
    metric_w = (right_w - 16) // 2
    metric_h = 238
    for i, item in enumerate(data["kpis"][:4]):
        mx = x + left_w + 24 + (i % 2) * (metric_w + 16)
        my = c.y + (i // 2) * (metric_h + 18)
        draw_metric(c, mx, my, metric_w, metric_h, item)
    c.y += thesis_h + 28

    for insight in data["insights"]:
        c.panel(x, c.y, width, 190)
        c.text((x + 28, c.y + 24), insight["label"].upper(), FONT["mono"], PALETTE["muted"])
        c.text((x + 28, c.y + 58), insight["title"], FONT["h3"], PALETTE["ink"])
        c.wrapped(x + 28, c.y + 100, insight["body"], FONT["body"], width - 56, "#38312a", 10)
        c.y += 210

    bottom = draw_bar_list(c, "平台成本排序", "Readout: 平台排序决定控费入口；先处理高占比平台，才有足够预算影响。", data["platform"], x, c.y, width, 8, PALETTE["growth"])
    c.y = bottom + 24
    bottom = draw_bar_list(c, "模型 Pareto", "Readout: 前两个模型解释过半费用，前五个模型解释 72.7%。", data["model"], x, c.y, width, 12, PALETTE["profit"])
    c.y = bottom + 24

    col_w = (width - 24) // 2
    left_bottom = draw_bar_list(c, "使用人 / 服务集中度", "Readout: 前三个责任单元占 68.9%。", data["user"], x, c.y, col_w, 10, PALETTE["cash"])
    right_y = draw_stacked(c, "工作负载拆分", data["workload"], x + col_w + 24, c.y, col_w)
    right_y = draw_stacked(c, "内部 / 外部用户", data["internalExternal"], x + col_w + 24, right_y + 24, col_w)
    c.y = max(left_bottom, right_y) + 24

    c.y = draw_heatmap(c, data["heatmap"], x, c.y, width) + 24

    left_table = draw_table(
        c,
        "Top platform-user pairs",
        "具体到平台和使用人，才能形成可执行的预算责任点。",
        data["platformUserTop"],
        [("platform", "Platform"), ("user", "User"), ("value", "Cost"), ("share", "Share")],
        x,
        c.y,
        col_w,
        8,
    )
    right_table = draw_table(
        c,
        "Top model-user pairs",
        "模型治理不能只看模型名，也要落到具体使用人。",
        data["modelUserPairs"],
        [("model", "Model"), ("user", "User"), ("value", "Cost"), ("share", "Share")],
        x + col_w + 24,
        c.y,
        col_w,
        8,
    )
    c.y = max(left_table, right_table) + 24

    c.panel(x, c.y, width, 320)
    c.text((x + 28, c.y + 24), "CAVEATS", FONT["mono"], PALETTE["muted"])
    yy = c.y + 66
    for risk in data["risks"]:
        c.text((x + 28, yy), "•", FONT["body"], PALETTE["risk"])
        yy = c.wrapped(x + 58, yy, risk, FONT["body"], width - 86, "#38312a", 10) + 8
    c.y += 344

    c.panel(x, c.y, width, 360)
    c.text((x + 28, c.y + 24), "ACTIONS", FONT["mono"], PALETTE["muted"])
    yy = c.y + 66
    for i, action in enumerate(data["actions"], 1):
        c.text((x + 28, yy), f"{i}.", FONT["body"], PALETTE["profit"])
        yy = c.wrapped(x + 70, yy, action, FONT["body"], width - 98, "#38312a", 10) + 8
    c.y += 386

    c.draw.line((x, c.y, c.width - x, c.y), fill=PALETTE["ink"], width=2)
    c.y += 20
    footer = f"Source: {data.get('sourceFile', '')} · Rows: {data.get('rowCount', '')} · Generated by wtt-fin-chart"
    c.wrapped(x, c.y, footer, FONT["mono"], width, PALETTE["muted"], 6)
    c.y += 40

    out.parent.mkdir(parents=True, exist_ok=True)
    c.crop().save(out)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: render-analysis-png.py <analysis.json> <output.png>", file=sys.stderr)
        return 2
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    render(data, Path(sys.argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
