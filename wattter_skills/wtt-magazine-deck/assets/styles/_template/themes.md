# Themes · STYLE_NAME

本文件描述 `STYLE_ID` 的主题色。新增风格至少保留一个 `default.css`，如果支持 T 键切换，必须提供 2 套以上预设主题，并让模板的 `body[data-theme-list]` 与文件名一致。

## 使用方法

1. 预设主题：复制全部主题 CSS 到 deck 的 `css/`，并让 `theme-link` 指向具体主题文件，例如 `css/default.css`。
2. 明确品牌/主题色：使用 `scripts/make-custom-theme.mjs` 或新风格自己的生成脚本输出 deck 专属 `css/theme.css`；此时 T 键应锁定，避免覆盖品牌色。
3. 不要在 HTML 里散写 hex；所有颜色通过 CSS 变量进入 `style.css` 和组件。

## 必需变量

- `--ink` / `--ink-rgb`
- `--paper` / `--paper-rgb`
- `--paper-tint` / `--ink-tint`
- `--accent` / `--accent-rgb`
- `--accent-2`
- `--accent-on`
- `--grey-1` / `--grey-2` / `--grey-3`

## 主题清单

| 主题 ID | 文件 | 适合 | 说明 |
|---|---|---|---|
| `default` | `themes/default.css` | 默认 | 复制后替换为真实主题 |

## 禁止

- 不要一份 deck 混用多个主题。
- 不要把其他风格的主题文件复制进本风格。
- 不要只改 accent 而忘记首页要体现该主题的第一印象。
