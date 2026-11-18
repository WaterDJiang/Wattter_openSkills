# Theme Palettes · 主题色板索引

> HTML 背景层 + SVG 文字层的**真实 HEX 色源**。与 [image-palettes](../image-palettes/_index.md)（描述 AI 图色彩行为、不含 HEX）正交——这里携带可直接注入 HTML 模板与 SVG 的 HEX 种子。Strategist 在八项确认 e（配色）环节选一个作为种子，**brand HEX 优先于此**（用户/模板色为真相）。

## 色板清单（最小起步）

| 色板 | 定位 | primary | accent | bg | 推荐风格 |
|---|---|---|---|---|---|
| [navy-trust](navy-trust.md) | 稳重权威（咨询/金融/政务/学术） | #003366 | #C9A961 | #FFFFFF | gradient-panel / editorial-rule |
| [tech-cyan](tech-cyan.md) | 创新前瞻（科技/SaaS/AI） | #1565C0 | #00BCD4 | #F8FAFC | geometric-mesh / gradient-panel |
| [warm-earth](warm-earth.md) | 温润亲和（教育/文化/培训） | #A0522D | #6B8E5A | #FAF6F0 | editorial-rule / gradient-panel |
| [dark-cinematic](dark-cinematic.md) | 戏剧高端（产品发布/奢侈品） | #0E1116 | #D4AF37 | #0E1116 | gradient-panel / geometric-mesh |

## 自动选择表（内容/行业 → 推荐色板）

| 场景 | 推荐色板 |
|---|---|
| 咨询报告 / 金融年报 / 政务汇报 / 学术答辩 | navy-trust |
| 科技产品 / SaaS / AI / 架构方案 | tech-cyan |
| 教育培训 / 文化传播 / 生活方式 | warm-earth |
| 产品发布 / 奢侈品 / 娱乐 / 高端品牌 | dark-cinematic |
| 通用商务（无明显行业倾向） | navy-trust（默认） |

## 与 HTML 背景风格的兼容矩阵

见 [html-background-styles/_index.md](../../templates/html-background-styles/_index.md) 的兼容矩阵。Strategist 选色板后交叉验证风格兼容性（`✓✓` 优先）。

## 色板文件结构

每个色板文件含：name / temperament / **HEX 表**（7 角色：primary / accent / bg / surface / border / text / text_secondary）/ neutral 色阶 / 适配场景 / HTML 背景风格 hint。

HEX 值即为 `spec_lock.colors` 各角色的种子；HTML 模板通过 manifest `variables` 注入对应 CSS 变量（`{{primary}}` `{{accent}}` `{{bg}}` `{{surface}}` `{{border}}` `{{text}}` `{{text_secondary}}`）。

## 自定义色板

用户可指定自定义色板：在 `<project>/templates/theme-palettes/<custom>.md` 写同结构文件，`spec_lock.colors.theme_palette` 填 `<custom>`。Strategist 读取时先查 `references/theme-palettes/`，再查 `<project>/templates/theme-palettes/`。
