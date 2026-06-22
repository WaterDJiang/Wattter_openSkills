---
description: 当用户只提供主题或需求而没有源文件时，通过网页搜索收集源材料。产出一份 Markdown 文档和一个图像文件夹，作为 SKILL.md Step 2 import-sources 的输入。
---

# 主题调研工作流

> 独立的预处理步骤。在 SKILL.md Step 1 之前运行，前提是用户只提供了主题或需求，没有任何源文件。产物是一份调研文档 + 一个图像文件夹，两者都按 `project_manager.py import-sources` 的直接输入形态组织。

本工作流**独立运行**：在没有现成文件时承担源材料获取职责；后续 SKILL.md 步骤以产出材料作为输入正常推进。

## 何时运行

| 用户提供的输入 | 操作 |
|---|---|
| 仅主题名（如 `"做一个关于宫崎骏的 PPT"`） | 运行本工作流 |
| 仅需求描述、无具体事实（如 `"介绍我们公司新产品"`） | 运行本工作流 |
| 对话中已有 ≥ 1 页实质性内容 | 跳过——把对话内容直接送入 SKILL.md Step 1 |
| 已附带源文件（PDF / DOCX / URL / Markdown） | 跳过——直接进入 SKILL.md Step 1 的源转换 |

---

## Step 1：确认主题

⛔ **BLOCKING**：以单一打包澄清问题确认范围。当用户的初始消息已覆盖时跳过。

| 项目 | 用户未指定时的默认值 |
|---|---|
| 主题 | （取自用户输入） |
| 范围 / 焦点 | 宽泛概述 |
| 深度 | 通用知识水平 |
| 输出语言 | 匹配用户输入 |
| 文件名 slug（`<topic_slug>`） | 由主题派生的 snake_case 英文标识 |

**禁止 —— 逐条确认**：不要逐项询问。一并打包澄清或干脆不问。

---

## Step 2：通过网页搜索收集

**工具** —— 使用当前 IDE 提供的网页搜索与抓取工具：

| IDE | 网页搜索 | 网页抓取 |
|---|---|---|
| Claude Code | `WebSearch` | `WebFetch` |
| Cursor / Codebuddy / VS Code + Copilot | 平台内等价的内置工具 | 平台内等价的内置工具 |
| 没有任何工具 | — | 见下方兜底方案 |

**无 IDE 网页工具时的兜底** —— 暂停，向用户索要 2–4 个权威 URL（Wikipedia / 官方网站 / 机构发布），然后逐个抓取：

```bash
python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>
```

**搜索策略**：

| 阶段 | 行动 |
|---|---|
| 全景扫描 | 一次宽泛搜索；识别权威来源 |
| 深入抓取 | 完整拉取 2–4 个信号最强的页面 |
| 定点补齐 | 针对深入抓取中浮现的子主题再做搜索 |

**来源优先级**：

| 层级 | 来源 |
|---|---|
| 1 | Wikipedia / Wikimedia Commons |
| 2 | 官方网站、机构发布 |
| 3 | 声誉良好的新闻 / 学术文章 |
| 避免 | 股票图库带水印图片、社交媒体无源转载 |

**停止条件**：当已收集的材料覆盖了概述 / 历史 / 关键面向 / 影响 / 来源，且包含具体事实和具名实体时停止。无止境的搜索只会产生噪音。

---

## Step 3：保存材料

两份产物落在 `projects/` 下：

| 产物 | 路径 |
|---|---|
| 调研文档 | `projects/<topic_slug>.md` |
| 图像文件夹 | `projects/<topic_slug>/` |

**硬规则 —— 命名**：文件名（不含 `.md`）与文件夹名必须一致。**硬规则 —— 位置**：必须落在 `projects/` 下，绝不能放在仓库根目录。

**文档结构** —— 章节布局按主题走：人物 → 生平 / 作品 / 影响；技术 → 背景 / 原理 / 应用 / 前景；公司 → 概述 / 产品 / 市场 / 文化。文件**必须**以 `## Sources` 章节结尾，列出使用的 URL。

**内容密度** —— 具体事实（日期、人名、数字、引语）。跳过填充式散文；最终幻灯片文案由策略师撰写。

**图像**：

| 决策 | 规则 |
|---|---|
| 数量 | 覆盖 deck 可能出现的场景（封面、关键面向、关键实体）；最终取舍由策略师决定 |
| 分辨率 | 优先原图。Wikimedia：去掉 URL 中的 `/thumb/` 与 `Npx-` 前缀以获取原分辨率 |
| 授权 | Wikimedia / 公有领域 / CC 授权；避免图库水印与无源上传 |
| 文件名 | 描述性英文 snake_case（`joe_hisaishi_concert.jpg`，而不是 `image1.jpg`） |

```bash
mkdir -p "projects/<topic_slug>"
curl -L -o "projects/<topic_slug>/<descriptive_name>.<ext>" "<image_url>"
```

---

## 交接

输出检查点，然后继续主流水线。产物直接喂给 Step 2 的 `import-sources`：

```markdown
## ✅ 主题调研完成
- [x] 文档：`projects/<topic_slug>.md`（N 个章节）
- [x] 图像：`projects/<topic_slug>/`（N 个文件）
- [ ] **下一步**：SKILL.md Step 2 →
  `project_manager.py init <project_name> --format <format>`
  `project_manager.py import-sources projects/<project_name> projects/<topic_slug>.md projects/<topic_slug>/*.* --move`
```

`<project_name>` 是用户选定的项目标识（通常为 `<format>_<topic_slug>`，如 `ppt169_joe_hisaishi`）；`--move` 会在导入完成后把位于 `projects/<topic_slug>` 的调研产物移除。