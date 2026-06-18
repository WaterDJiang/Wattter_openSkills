# Themes · Linear 科技型

4 套深色产品界面主题。所有主题都保留暗底、玻璃面板和高对比 accent，适合科技产品、AI workflow、SaaS 发布和工程团队汇报。

## 使用方法

1. 预设主题：复制全部主题 CSS 到 deck 的 `css/`，并让 `theme-link` 指向具体主题文件，例如 `css/linear-dark.css`。
2. `body[data-theme-list]` 必须与 `registry.json` 的 `availableThemes` 一致，T 键和右上角 T 按钮会在当前风格内热切换。
3. 明确品牌色使用：
   ```bash
   node <SKILL_ROOT>/scripts/make-custom-theme.mjs linear "#RRGGBB" "$DIR/css/theme.css" --name="brand-name"
   ```
   如果生成器尚未为 `linear` 做专属分支，优先选预设主题或复制本目录主题为一次性 deck theme。

## 主题表

| 主题 | 主色 | 适合 |
|---|---|---|
| `linear-dark` | `#5E6AD2` | 默认，最接近 Linear 式紫蓝科技感 |
| `linear-aurora` | `#8B5CF6` | AI、agent、自动化、发布会视觉 |
| `linear-graphite` | `#94A3B8` | 严肃产品汇报、工程质量、系统架构 |
| `linear-solar` | `#F59E0B` | 增长、行动、优先级、决策节点 |

## 使用原则

- 首页建议使用 `LNR-01` + `hero dark`，让产品界面面板和 accent 光感成为第一印象。
- 内容页优先使用深色页，浅色页只用于反差或截图讲解。
- 不要混入 Swiss 的纯平面直角语汇；Linear 科技型允许 14-22px 圆角、玻璃面板和发光边界。
- 不要混入 Editorial 的衬线标题和杂志引用墙；本风格以产品 UI、issue row、roadmap、agent command 为主要视觉资产。
