---
name: wtt-project-harness-generator
description: "根据具体项目生成 CLAUDE.md 和 AGENTS.md，包含组件化、规则、UI/UX 的 harness 要求。结合代码扫描和对话引导理解项目。Use when: (1) 为新项目或现有项目创建 CLAUDE.md 或 AGENTS.md，(2) 提到 harness、项目配置、AI规则、项目规范、agent配置，(3) 优化或重写已有 CLAUDE.md/AGENTS.md，(4) 生成 .claude/rules/ 路径规则或 settings.json"
---

# 项目 Harness 生成器

为具体项目生成 CLAUDE.md 和 AGENTS.md——不是填模板，是从项目 DNA 中提炼规则。

## 工作流

### 1. 扫描项目

读代码，不问用户能推断出的事。**先判断是新项目还是已有项目**（见 [harness-spec.md](references/harness-spec.md)「新项目 vs 已有项目」），决定走哪条分支：

#### 已有项目（有代码/配置可读）

1. 根目录文件结构 → 项目类型和规模
2. package.json / pyproject.toml / Cargo.toml / go.mod → 技术栈和依赖
3. 框架特征文件（next.config / vite.config / angular.json 等）→ 架构模式
4. 已有 AI 配置（CLAUDE.md / AGENTS.md / .cursorrules / .trae/rules/）→ 保留还是重写
5. 目录结构（src/ app/ components/ pages/ api/）→ 组件化模式
6. 样式方案（tailwind / CSS Modules / styled-components）→ UI 规范基线
7. 测试框架（jest / vitest / pytest / playwright）→ 测试命令和覆盖率
8. Monorepo 工具（pnpm-workspace / turbo / nx）→ 包间依赖方向；技术栈分化的子包需判断是否嵌套 AGENTS.md（见 [agents-md-templates.md](references/agents-md-templates.md)「嵌套」）
9. 开发文档（doc/ 下分类文件夹 spec/plan/log + 各 INDEX.md，或单文件）→ 文档管理约定，保留既有结构
10. Skill 创作/维护特征（单个 SKILL.md、marketplace.json 或多个 skill 文件夹）→ 按业务定调，并扫描现有测试输入、运行器、历史输出与版本约定；按 [Skill 对照测试](references/skill-evaluation.md) 补齐缺口。

#### 新项目（空文件夹 / 几乎无文件）

扫描读不到东西，改由**对话定义项目**（见 step 2 的新项目必问）。然后：

- 生成的规则是**规定性**的（"该怎么做"），不是已有项目的描述性（"现状是什么"）
- 顺手搭**文档骨架**：建 `doc/` 目录 + 各分类文件夹 + 空 INDEX（见 [harness-spec.md](references/harness-spec.md)「新项目脚手架」），让项目从第一天就有文档管理

推断规则详见 [references/harness-spec.md](references/harness-spec.md)。

### 2. 对话确认

扫描后只问扫描推断不了的事：

**已有项目仅补齐未知信息**（扫描或当前对话已明确的不重复问）：
1. 项目类型（扫描已识别则直接采用）
2. 团队规模（决定规范严格度）
3. 需要生成哪些文件

**新项目补齐信息**（优先采用当前对话已明确的内容，仅询问影响方案的缺口）：
1. 项目要做什么——一句话本质 + 目标用户
2. 已有哪些开源/同类方案？——产品构思先调研，能复用不自研（调研记 doc/ref/）
3. 技术栈选型——语言/框架/包管理（决定命令、目录结构、组件化模式）
4. 项目类型——开发型 / skill 仓库 / 内容创作（决定立场，见 [harness-spec.md](references/harness-spec.md)「立场定调」）
5. 团队规模、需要生成哪些文件
6. 是否搭 doc/ 文档骨架（见 [harness-spec.md](references/harness-spec.md)「新项目脚手架」）

**按需追问**（两种场景都适用）：
- 组件化偏好、设计系统、测试要求、部署方式、特殊约束
- 核心领域对象（项目的概念地图，如 Goal·Task·Approval·Artifact）
- 已有配置是否保留
- 实施记录/文档管理：项目是否用 doc 分类（spec/plan/log）+ INDEX 分片管理？路径是？（未检测到则建议建立，见 [doc-management.md](references/doc-management.md)）

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
7. **组件化规范** — 划分原则、通信方式、共享组件位置、组件大小上限、抽离时机（前端用组件模板，后端用模块模板，按项目类型选不混用）
8. **设计方向** — 具体 token 级别（如 8px 网格、3px 硬边框、0 圆角），不是泛泛"设计系统"
9. **UI 规范** — 设计系统、响应式、主题、图标、间距
10. **UX 规范** — 基于 D-S-T-E 体验四步曲生成：诊断·简化·翻译·升温（见下方详解）
11. **编码纪律** — 简单优先、不预设抽象、不顺手重构、死代码处理、测试先行
12. **输出精简** — 简短直接、不铺垫不总结、要点不用散文
13. **目标驱动执行** — 每种任务转化为可验证的成功标准
14. **项目文档管理** — doc 分类（spec/plan/log/design/ref）+ 每个文件夹 INDEX 分片 + 渐进式按需读 + spec→plan→log 执行闭环 + 变更协议（授权分级、局部替代、下游待复核、已有实现处置、检查点恢复）+ 截图留存（关键判断/失误修正的截图存 `doc/assets/` 并在 log 里引用）
15. **提交与部署** — 分支策略、提交格式、推送确认规则
16. **已知注意事项** — Claude 容易犯错的点、特殊约束

**项目类型决定哪些章节保留**：

| 章节 | Web 前端 | API 后端 | 全栈 | CLI/库 | 数据/ML |
|------|---------|---------|------|--------|---------|
| 设计方向 | ✓ | — | ✓ | — | — |
| UI 规范 | ✓ | — | ✓ | — | — |
| UX 规范 | ✓ | ✓ | ✓ | ✓(CLI版) | ✓(数据版) |
| 组件化 | ✓(组件) | ✓(模块) | ✓ | — | — |
| 架构原则 | ✓ | ✓ | ✓ | ✓ | ✓ |

「API 规范」「数据层」不单列章节——并入「架构原则」（如错误响应格式、schema 迁移纪律）。

模板参考见 [references/claude-md-templates.md](references/claude-md-templates.md)。

#### AGENTS.md 生成

- 纯 Markdown，无 frontmatter、无 `@import`
- 内容与 CLAUDE.md 核心规则一致，去掉 Claude 专属规则
- 按项目类型选最接近的示例（开发型：全栈 / API 后端 / CLI 库；非开发型：Skill 仓库），不照抄
- 避开反模式：不抄 README、不堆全量架构、不写口号规则、不塞密钥（见模板「反模式」）
- 如已有 AGENTS.md，CLAUDE.md 用 `@AGENTS.md` 导入

模板参考见 [references/agents-md-templates.md](references/agents-md-templates.md)。

#### Skill 创作与优化项目

无论单个 Skill 还是多 Skill 仓库，生成的 Harness 必须包含“Skill 优化验收”。按 [版本化对照测试协议](references/skill-evaluation.md) 写入长期规则，并建立或复用目标项目的测试入口：

- 每次只比较最近相邻两版：修改前最近一版 baseline 与修改后最新版 candidate，例如 v2→v3，下一轮 v3→v4。更早版本仅归档，不参与本轮比较；最近前版缺失时报告无法对照，不用更早版本顶替。
- 修改前冻结完整实际运行依赖；同输入、同配置、独立上下文生成窗口内各版结果，每次至少覆盖影响用例与核心回归。新建 Skill 建首次基线。
- Skill 版本、用例版本、测试集版本、运行 ID 分开标记；新版产物按版本追加到集合，保留失败和退步，参考样例须评审。
- 每轮交付窗口内各版真实输出与对比报告；未生成时明确“修改完成，生成验证未完成”。生成 Harness 结构通过不代表被管理 Skill 已通过测试。
- 没有测试系统时使用 [测试集骨架](assets/skill-eval-starter/README.md)，补具体输入与标准；有系统则原位扩展。测试历史不进入日常 Skill 加载链。

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
3. **AGENTS.md 强制过质量核验子流程**（[agents-md-checklist.md](references/agents-md-checklist.md)）：19 项逐条核验，任一不达标回炉修正，所有适用项 ✓ 且不适用项注明 N/A 原因后才能写入；CLAUDE.md 过同一套核验（除 #1 #2 的 AGENTS 专属语法——`@import`、路径规则在 CLAUDE.md 允许）
4. 展示生成结果；已有明确写入授权则验证后写入，不重复确认。仅审查/建议请求不覆盖目标文件；尚未授权覆盖时先展示可审阅结果。

## 生成原则

- **有名字的规则**：每条规则有编号 + 标题（"本地验证优先" > "要先验证"）
- **具体到可验证**："2 空格缩进" 不是 "格式化代码"；确切命令不是描述
- **项目 DNA 优先**：从代码推断 > 从模板复制 > 从用户询问
- **宁缺毋滥**：不适用于项目的章节直接跳过，不留空占位符
- **心智模型**：列出核心领域对象，让 Agent 用项目自己的概念思考
- **纪律犀利**：编码纪律和输出精简要像 Maya 指南一样直接——"有更简单做法时直接指出，不默默选复杂方案"
- **行为规则选子集**：编码纪律 / 输出精简 / 目标驱动执行从 [behavioral-rules.md](references/behavioral-rules.md) 的 12 条目录按项目类型选子集，不照搬全量；小团队可合并为前置"行为规则"章节
- **立场定调**：生成的文件要带一条项目业务的立场——开发项目进组件化节，非开发项目（skill 仓库、内容、课程）用「核心立场」节谈本领域态度（改写优先、去营销、教学法等）。立场带可验证约束，不写口号（见 [harness-spec.md](references/harness-spec.md)「立场定调」）
- **复用优先**：产品构思和新功能设计先调研开源/已有方案（记 doc/ref/），只有核心差异化才自研——特有规则默认含"先调研再自研"（决策级联：调研开源 → 查参考项目 → 才自研）
- **宪法层定位**：生成的 CLAUDE.md/AGENTS.md 是项目"宪法"——不变量与非协商约束，极少变更；频繁变化的内容（进度、临时决策）进 doc/log 和 doc/plan，不进宪法

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
- [AGENTS.md 质量核验](references/agents-md-checklist.md) — 强制核验子流程：19 项检查、验证方法、门控协议
- [项目文档管理](references/doc-management.md) — doc 分类、每文件夹 INDEX 分片、spec→plan→log 闭环、渐进式读写协议、截图留存
- [Harness 规范](references/harness-spec.md) — 架构总览、推断规则、UI/UX 规范生成、对话问题清单
- [Skill 版本化对照测试](references/skill-evaluation.md) — 改前快照、固定输入、新旧生成、版本化样例积累与报告
- [Agent 行为规则目录](references/behavioral-rules.md) — 12 条行为规则、规则→章节映射、按团队规模/项目类型选子集

## 持续开发生成要求

- AGENTS.md 放长期约束与读取入口；Spec 放有效行为和验收，Design 放设计系统与架构决策，Plan 放任务依赖与状态，Log 放变更原因及证据。复用项目路径，小任务可单文件分节。
- 按 [doc-management.md](references/doc-management.md) 生成变更协议：有效依据、影响分析、授权判断、局部替代、依赖复核、同步后实施和中断恢复。具体进度不写入 AGENTS.md。
- 开发项目的 Spec 按需包含组件与架构影响、UI 状态与设计引用、兼容迁移和回归证据；无 UI 项目省略 UI 字段。
- 组件阈值只作评审信号；共享修改检查调用方；详细 Token 定义只有一个有效来源。已授权迁移明确范围、过渡和完成条件。
- 授权内常规调整持续执行；用户已明确的变更不重复确认，未决取舍仅阻塞受影响工作。
- 审计/建议模式先报告现状、缺口和可执行建议；优化本 Skill 时同步入口、参考规范、模板和核验清单，避免新旧指令并存。
