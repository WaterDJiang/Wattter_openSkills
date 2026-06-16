---
name: wtt-project-harness-generator
description: "根据具体项目生成 CLAUDE.md 和 AGENTS.md，包含组件化、规则、UI/UX 的 harness 要求。结合代码扫描和对话引导理解项目。Use when: (1) 为新项目或现有项目创建 CLAUDE.md 或 AGENTS.md，(2) 提到 harness、项目配置、AI规则、项目规范、agent配置，(3) 优化或重写已有 CLAUDE.md/AGENTS.md，(4) 生成 .claude/rules/ 路径规则或 settings.json"
---

# 项目 Harness 生成器

为具体项目生成 CLAUDE.md 和 AGENTS.md——不是填模板，是从项目 DNA 中提炼规则。

## 工作流

### 1. 扫描项目

读代码，不问用户能推断出的事：

1. 根目录文件结构 → 项目类型和规模
2. package.json / pyproject.toml / Cargo.toml / go.mod → 技术栈和依赖
3. 框架特征文件（next.config / vite.config / angular.json 等）→ 架构模式
4. 已有 AI 配置（CLAUDE.md / AGENTS.md / .cursorrules / .trae/rules/）→ 保留还是重写
5. 目录结构（src/ app/ components/ pages/ api/）→ 组件化模式
6. 样式方案（tailwind / CSS Modules / styled-components）→ UI 规范基线
7. 测试框架（jest / vitest / pytest / playwright）→ 测试命令和覆盖率
8. Monorepo 工具（pnpm-workspace / turbo / nx）→ 包间依赖方向

推断规则详见 [references/harness-spec.md](references/harness-spec.md)。

### 2. 对话确认

扫描后只问扫描推断不了的事：

**必问**：
1. 项目类型（扫描已识别则确认即可）
2. 团队规模（决定规范严格度）
3. 需要生成哪些文件

**按需追问**（扫描结果不明确时才问）：
- 组件化偏好、设计系统、测试要求、部署方式、特殊约束
- 核心领域对象（项目的概念地图，如 Goal·Task·Approval·Artifact）
- 已有配置是否保留

### 3. 生成

不填模板。从项目实际提炼规则，参考模板结构但不照搬。

#### 生成的 CLAUDE.md 结构

按需组合以下章节，宁缺毋滥：

1. **项目概览** — 一句话本质 + 关键文档路径
2. **特有规则** — 编号 + 标题，每条规则有名字（如"参考项目优先"、"本地验证优先"）
3. **核心领域对象** — 项目的心智模型，列出关键概念，不引入不必要的新抽象
4. **技术栈** — 语言、框架、包管理，具体到版本
5. **构建与测试** — 确切命令，不描述
6. **架构原则** — 分层、数据流、控制平面 vs 执行平面
7. **组件化规范** — 划分原则、通信方式、共享组件位置、组件大小上限
8. **设计方向** — 具体 token 级别（如 8px 网格、3px 硬边框、0 圆角），不是泛泛"设计系统"
9. **UI 规范** — 设计系统、响应式、主题、图标、间距
10. **UX 规范** — 基于 D-S-T-E 体验四步曲生成：诊断·简化·翻译·升温（见下方详解）
11. **编码纪律** — 简单优先、不预设抽象、不顺手重构、死代码处理、测试先行
12. **输出精简** — 简短直接、不铺垫不总结、要点不用散文
13. **目标驱动执行** — 每种任务转化为可验证的成功标准
14. **提交与部署** — 分支策略、提交格式、推送确认规则
15. **已知注意事项** — Claude 容易犯错的点、特殊约束

**项目类型决定哪些章节保留**：

| 章节 | Web 前端 | API 后端 | 全栈 | CLI/库 | 数据/ML |
|------|---------|---------|------|--------|---------|
| 设计方向 | ✓ | — | ✓ | — | — |
| UI 规范 | ✓ | — | ✓ | — | — |
| UX 规范 | ✓ | ✓ | ✓ | ✓(CLI版) | ✓(数据版) |
| 组件化 | ✓ | — | ✓ | — | — |
| 架构原则 | ✓ | ✓ | ✓ | ✓ | ✓ |
| API 规范 | — | ✓ | ✓ | — | — |
| 数据层 | — | ✓ | ✓ | — | ✓ |

模板参考见 [references/claude-md-templates.md](references/claude-md-templates.md)。

#### AGENTS.md 生成

- 纯 Markdown，无 frontmatter、无 `@import`
- 内容与 CLAUDE.md 核心规则一致，去掉 Claude 专属规则
- 如已有 AGENTS.md，CLAUDE.md 用 `@AGENTS.md` 导入

模板参考见 [references/agents-md-templates.md](references/agents-md-templates.md)。

#### .claude/rules/ 路径规则

团队 ≥ 5 人或用户要求时生成，按需拆分：

- `code-style.md` — 无条件加载
- `testing.md` — 无条件加载
- `api/endpoints.md` — 路径范围
- `components/rules.md` — 路径范围

#### 规范严格度

| 团队规模 | 输出 |
|----------|------|
| 1人 | 核心规则，精简章节 |
| 2-5人 | 标准章节 |
| 5-20人 | 全部章节 + 路径规则 |
| 20+人 | 全部 + settings.json hooks |

### 4. 验证与写入

1. CLAUDE.md < 200 行，超出拆到 `.claude/rules/` 或 `@import`
2. AGENTS.md 无特殊语法
3. 展示生成结果，用户确认后写入

## 生成原则

- **有名字的规则**：每条规则有编号 + 标题（"本地验证优先" > "要先验证"）
- **具体到可验证**："2 空格缩进" 不是 "格式化代码"；确切命令不是描述
- **项目 DNA 优先**：从代码推断 > 从模板复制 > 从用户询问
- **宁缺毋滥**：不适用于项目的章节直接跳过，不留空占位符
- **心智模型**：列出核心领域对象，让 Agent 用项目自己的概念思考
- **纪律犀利**：编码纪律和输出精简要像 Maya 指南一样直接——"有更简单做法时直接指出，不默默选复杂方案"

## UX 规范生成：D-S-T-E 体验四步曲

生成 UX 规范时，使用 **D-S-T-E**（Diagnose-Simplify-Translate-Emotify）四步闭环模型。不是罗列泛泛的 UX 条目，而是按诊断→简化→翻译→升温提炼规则。

```
诊断（盲测）→ 简化（3-5铁律）→ 翻译（说人话）→ 升温（微交互+AI）
     ↑                                                    ↓
     └────────────── 形成闭环，持续迭代 ──────────────────┘
```

> **口诀**："盲三点，简三五，翻译说人话，升温微交AI"

四步详解、各项目类型适配表、生成示例 → [references/harness-spec.md](references/harness-spec.md) 的「D-S-T-E 体验四步曲」和「关键方法速查」。
各项目类型的 UX 规范模板 → [references/claude-md-templates.md](references/claude-md-templates.md) 的「10. UX 规范」。

## 参考文档

- [CLAUDE.md 模板](references/claude-md-templates.md) — 各项目类型模板、路径规则模板、settings.json 模板
- [AGENTS.md 模板](references/agents-md-templates.md) — 各项目类型模板、与 CLAUDE.md 的桥接方式
- [Harness 规范](references/harness-spec.md) — 架构总览、推断规则、UI/UX 规范生成、对话问题清单
