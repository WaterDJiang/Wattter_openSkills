---
description: 在 `templates/brands/<id>/` 下生成一个仅含识别段的模板——一份 design_spec.md，记录用户的配色 / 字体 / Logo / 语气 / 图标风格，不含 SVG 页面清单；后续 PPT 项目可继承品牌识别，同时保持页面版式自由。
---

# 创建品牌工作流

> 独立的预设创建工作流。产出是位于 `${SKILL_DIR}/templates/brands/<brand_id>/` 的品牌模板包。结构上，品牌就是不含 SVG 页面清单的模板——策略师把品牌的配色 / 字体 / Logo / 语气锁定为权威；执行器在这些约束下自由设计页面。

本工作流编辑的是全局品牌库，而非任何具体的 `projects/<x>/`。消费方式与版式模板遵循同一条显式路径规则（见末尾的 [下游消费](#downstream-consumption-informational)）。

> 配套工作流：[`create-template.md`](./create-template.md) 生成带 SVG 页面的完整模板。当用户希望"识别段锁定 + 页面版式自由"时使用 `create-brand.md`。

## 何时运行

| 用户信号 | 操作 |
|---|---|
| `"set up brand"` / `"extract brand from this logo"` / 建立品牌 / 做品牌规范 | 运行本工作流 |
| 用户提供了品牌资产（Logo / 品牌官网 / 带品牌的 PPTX / 品牌 PDF），并希望跨未来项目锁定 | 运行本工作流 |
| 用户只为单个 deck 提了一次品牌色或字体 | 跳过——通过策略师 h.5 内联处理 |
| `templates/brands/<requested_id>/` 已存在 | 询问：更新 / 替换 / 换新 id——绝不静默覆盖 |

⛔ 永不自动触发。品牌创建是用户主动调用的识别设置；空 `templates/brands/` 不是创建它的邀请。

---

## Step 1：检测输入类型

| 类型 | 用户提供的输入 | 路径 |
|---|---|---|
| **A** 品牌资产 | Logo（SVG/PNG/JPG）、品牌官网、带品牌的 PPTX、品牌 PDF | Step 2A —— 资产抽取 |
| **B** 口头规范 | 用户在聊天中直接口述 HEX / 字体 / 语气 | Step 2B —— 口头采集 |
| **C** 空白 | 用户希望建立品牌，但既无资产也无规范 | Step 2C —— 空白骨架 |

---

## Step 2A：资产抽取

直接用现有转换器读取资产——没有专用的抽取脚本。

| 资产格式 | 读取方式 | 可抽取字段 |
|---|---|---|
| SVG Logo | `Read` 该 SVG；grep `fill=` / `stroke=` 取 HEX | 配色（精确）、Logo 文件 |
| PNG/JPG Logo | `Read`（多模态）；AI 视觉识别主色 | 配色（近似 HEX，标 `[approx]`）、Logo 文件 |
| 品牌官网 URL | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>`，再 `Read` 结果 | 配色引用、字体引用、语气/口吻 |
| 带品牌 PPTX | `python3 ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py <file>`，再读 theme XML | 配色、字体（精确） |
| 品牌 PDF | `python3 ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` | 语气/口吻；偶有配色/字体引用 |

识别资产未覆盖的（配色 / 字体 / Logo / 语气 / 图标风格）哪一项，然后进入 Step 3 处理其余项。多数单资产只能高质量覆盖 1–2 类。

草稿 `design_spec.md` 中每个字段的**来源标签**：
- `[fact]` —— 直接抽取（SVG fill HEX、PPTX theme XML）
- `[approx]` —— 视觉估算（PNG/JPG 取色）
- `[user]` —— 在 Step 3 通过聊天补全

---

## Step 2B：口头规范采集

一次性打包提问（**不要**逐条询问）。匹配用户的语言。打包提问示例：

> "我会记录以下内容：主色 / 辅色 / 强调色 HEX、标题字体、正文字体、Logo 路径（可选）、语气（正式 / 中性 / 轻松）、是否允许使用 emoji。你想现在锁定哪些？"

用户给的内容都标 `[user]`。除非用户明确要求扩展更多字段，否则跳过 Step 3。

---

## Step 2C：空白骨架

写入 `templates/brands/<brand_id>/design_spec.md`，保留完整 schema，每个值都写成 TODO 注释。告诉用户文件在哪。之后不再追问——后续由用户自己接管。

---

## Step 3：聊天补全（仅 Type A）

对资产未覆盖的字段，用一条打包消息向用户提问。跳过与用户意图无关的字段。

| 字段 | 何时提问 |
|---|---|
| primary / secondary / accent HEX | 始终 |
| text / bg HEX | 仅在提到深色模式或反色方案时 |
| title / body 字体 | 资产未给出字体引用时 |
| Logo 用法 | 提供了 Logo 文件时 |
| 语气 & 口吻 | 提及受众或正式程度时 |
| 图标风格偏好 | 提到图标一致性时 |

---

## Step 4：落地品牌包

创建包目录：

```bash
mkdir -p "${SKILL_DIR}/templates/brands/<brand_id>"
```

### 必需：`design_spec.md`

```markdown
---
brand_id: <slug>
kind: brand
summary: <one-line use case, e.g. "ACME Corp marketing decks">
keywords: [<3-5 short tags>]
primary_color: "#XXXXXX"
---

# <Display Name> Brand Specification

> Identity-only preset. No SVG page roster — pages are composed freely under these constraints.

## I. Brand Overview
| Property | Value |
|---|---|
| Brand Name | <display name> |
| Use Cases | <summary> |
| Tone | <one-line tone summary> |

## II. Color Scheme
| Role | HEX | Provenance |
|---|---|---|
| primary | #XXXXXX | fact \| approx \| user |
| secondary | #XXXXXX | |
| accent | #XXXXXX | |
| text | #XXXXXX | optional, default `#1A1A1A` |
| bg | #XXXXXX | optional, default `#FFFFFF` |

## III. Typography
| Role | Family | Weight |
|---|---|---|
| title | <family> | <weight> |
| body | <family> | <weight> |
| mono | <family> | optional |

## IV. Logo
- File: `./logo.<ext>` (relative to this design_spec.md)
- Usage: cover-only \| every-page \| never

## V. Voice & Tone
- Formality: formal \| neutral \| casual
- Person: informal-you \| formal-you \| we \| none
- Emoji: allowed \| forbidden
- Abbreviations: spell-out-first \| common-abbrev-allowed

## VI. Icon Style
- Preference: linear \| filled \| duotone   # optional, drives icon library search

## VII. Visual Assets (optional)
- Images: `./images/`               # branded photos, prioritised before AI image generation
- Illustrations: `./illustrations/` # branded illustrations, prioritised before AI generation
- Icons: `./icons/`                 # branded icon overrides; falls back to `templates/icons/`
```

**章节范围规则**：
- 版式 / 画布 / 间距 / 圆角 / 阴影 / 页面清单 / 标志性设计元素**不在**品牌范围内。这些内容属于版式 / 完整 Deck 模板（`templates/layouts/<id>/design_spec.md` 或 `templates/decks/<id>/design_spec.md`）或 `shared-standards.md`。**不要**在这里添加这些章节。
- HEX 必须为 `#RRGGBB`
- 字体名为自由字符串，不会与本机已安装字体做校验
- §VII 完全可选——只列出实际存在的目录

### 可选：Logo 文件

若用户提供了 Logo，复制到 `templates/brands/<brand_id>/logo.<ext>`（保留源扩展名）。

### 可选：视觉资产目录

若用户提供了品牌照片 / 插画 / 图标目录，以 `images/` / `illustrations/` / `icons/` 复制到 `templates/brands/<brand_id>/` 下，并在 `design_spec.md` 的 §VII 引用每个。若都不存在则跳过整个 §VII。

### 这里**不**创建

不含 SVG 页面清单。不含画布规范。不含标志性设计元素。后续若用户希望"品牌 + 页面模板"，跑 `create-template.md`，把这个品牌作为风格参考。

---

## Step 5：注册并交接

更新 `templates/brands/brands_index.json`，加入新条目（若文件不存在则创建）：

```json
{
  "<brand_id>": {
    "summary": "<from design_spec.md frontmatter>",
    "keywords": [...],
    "primary_color": "#XXXXXX"
  }
}
```

输出确认卡：

```markdown
## ✅ 品牌已保存
- 路径：`${SKILL_DIR}/templates/brands/<brand_id>/`
- 文件：`design_spec.md`、可选 `logo.<ext>`、可选 `images/` / `illustrations/` / `icons/`
- 已锁定字段：<列表>
- 来源标签：<fact / approx / user 数量>

在项目中使用：
- 在 Step 3 输入里附上品牌目录的显式路径——例如："做一个 Q4 总结 PPT，用 `${SKILL_DIR}/templates/brands/<brand_id>/` 这个品牌"
- 与版式模板遵循同一条显式路径规则：裸品牌名不会触发
- 可与版式模板路径一同提供；Step 3 把两者融合成单一 `design_spec.md`（品牌在识别段胜出，版式在页面结构胜出）——见 `SKILL.md` Step 3
- 查看可用品牌：打开 `templates/brands/brands_index.json`
- 编辑：直接修改 `templates/brands/<brand_id>/design_spec.md`，然后重跑 `python3 ${SKILL_DIR}/scripts/register_template.py --kind brand <brand_id>`
```

---

## 下游消费（信息性）

品牌应用发生在 [`SKILL.md` Step 3](../SKILL.md)，遵循与版式模板**同一条显式路径规则**：

| SKILL.md Step 3 的用户输入 | 行为 |
|---|---|
| 提供了品牌目录显式路径 | Step 3 把品牌复制进 `<project_path>/templates/`（与版式模板的目标一致）；策略师在 Step 4 把配色 / 字体 / Logo / 语气锁定为权威 |
| 裸品牌名、未带路径的品牌提及、或沉默 | 跳过——不要基于目录数量或任何其他隐含信号做自动应用 |
| 同一条消息里同时给出品牌路径与版式模板路径 | Step 3 把两者融合成 `<project_path>/templates/` 内一份 `design_spec.md`（品牌在识别段胜出，版式在结构段胜出）。见 `SKILL.md` Step 3 的字段优先级表与两个可能引发澄清问题的冲突闸口 |

`brands_index.json` 仅用于发现（语义镜像 `layouts_index.json`）；列出品牌永远不会推进流水线。

---

## 备注

1. **品牌是识别，不是版式** —— 只含配色 / 字体 / Logo / 语气 / 图标风格。页面清单、画布规范、标志性设计元素归版式模板；不要在这里重复。
2. **自包含包** —— 所有品牌资产（Logo、图像、插画、图标）都位于 `templates/brands/<brand_id>/` 内。绝不外泄到工作区根或 `projects/`。
3. **无脚本依赖** —— Step 2A 复用现有转换器与 AI 内联读取。除非未来用户反馈需要批处理或对栅格 Logo 做精确取色，否则不会引入专门的 `brand_extract.py`。
4. **多品牌支持** —— `templates/brands/` 接受任意数量的品牌；适合代理 / 自由职业 / 多客户工作流。
5. **优先级规则** —— 当品牌与版式模板同时生效时，Step 3 融合成一份 `design_spec.md`：品牌胜在配色 / 字体 / Logo / 语气 / 图标风格；版式胜在画布 / 页面清单 / 间距 / 字号层级 / 标志性视觉元素。见 `SKILL.md` Step 3 的完整优先级表。