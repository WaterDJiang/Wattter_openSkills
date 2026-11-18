# CLAUDE.md 模板与生成规范

## 目录

- [文件规范](#文件规范)
- [项目扫描清单](#项目扫描清单)
- [CLAUDE.md 章节](#claudemd-章节)
- [CLAUDE.md 示例](#claudemd-示例)
- [路径规则模板](#路径规则模板)
- [settings.json 模板](#settingsjson-模板)

## 文件规范

- 纯 Markdown，< 200 行
- 超出部分拆到 `.claude/rules/`（路径范围规则）或 `@import`（递归最大 4 跳）
- HTML 注释注入上下文前会剥离，可用于人类备注不花 token
- `@path/to/file` 导入额外文件

### 位置层级

| 范围 | 位置 | 用途 |
|------|------|------|
| 托管策略 | `/Library/Application Support/ClaudeCode/CLAUDE.md` | 组织级 |
| 用户 | `~/.claude/CLAUDE.md` | 跨项目个人偏好 |
| 项目 | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 团队共享 |
| 本地 | `./CLAUDE.local.md` | 个人偏好（.gitignore） |

## 项目扫描清单

扫描以下内容自动推断项目属性：

- 项目根文件：`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`
- 框架特征：`next.config.*`, `nuxt.config.*`, `vite.config.*`, `angular.json`, `django/`, `spring/`
- 已有 AI 配置：`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.trae/rules/`
- 开发文档：`doc/plan/`、`doc/log/`（文件夹 + INDEX 分片）或 `doc/plan.md`/`doc/log.md`（单文件）、`CHANGELOG.md` → 实施记录约定（保留既有结构）
- 目录结构：`src/`, `lib/`, `app/`, `components/`, `pages/`, `api/`, `services/`
- 样式方案：`tailwind.config.*`, `*.module.css`, `styled-components`
- 测试框架：`jest`, `vitest`, `pytest`, `playwright`
- CI/CD：`.github/workflows/`, `.gitlab-ci.yml`
- Monorepo：`pnpm-workspace.yaml`, `turbo.json`, `nx.json`
- Lint/Format：`.eslintrc*`, `.prettierrc*`, `ruff.toml`

## CLAUDE.md 章节

根据项目类型选用，不适用则跳过，不留空占位符。

### 1. 项目概览

一句话本质 + 关键文档路径。不讲功能列表，讲"这是什么"。

```markdown
# {{项目名}}

{{一句话本质描述}}

**关键文档：** 产品计划 `doc/xxx.md` · 架构设计 `doc/yyy.md`
```

### 2. 特有规则

编号 + 标题。每条规则有名字，不是无编号的列表项。

```markdown
## 特有规则

### 1. 先调研再自研
开发任何能力前，先调研开源/已有方案——包管理生态搜一遍、看同类产品用了什么。能直接用或改造的不自研；只有构成产品**核心差异化**的能力才从零实现。调研记 `doc/ref/`，"自研 vs 复用"选型写进 spec，结论记 log。

### 2. 参考项目优先
开发底层能力前，先检查 {{参考目录}} 是否已有实现。有则迁移/改写；无覆盖或迁移破坏产品边界时才从零实现。

### 3. 本地验证优先，推送需确认
先本地验证（typecheck、lint、test）。GitHub 推送/PR/Release 必须等用户明确指令。

### 4. {{规则名}}
{{规则内容}}
```

### 3. 核心领域对象

项目的心智模型。列出关键概念，一句话说明，不引入不必要的新抽象。

```markdown
## 核心领域对象

Goal · Task · Task Run · Agent · Approval · Artifact
```

### 4. 技术栈

具体到版本。

```markdown
## 技术栈

- **语言**: TypeScript 5.x
- **框架**: Next.js 14 (App Router)
- **包管理**: pnpm 9
- **数据库**: PostgreSQL 16 + Prisma
```

### 5. 构建与测试

确切命令，不描述。

```markdown
## 构建与测试

\`\`\`bash
pnpm install          # 安装依赖
pnpm dev              # 开发模式
pnpm build            # 构建
pnpm test             # 测试
pnpm lint             # Lint
\`\`\`
```

### 6. 架构原则

分层、数据流、控制平面 vs 执行平面。每条原则一句话。

```markdown
## 架构原则

- API Server = 控制平面，不直接执行 CLI
- Runtime/Worker = 执行平面，队列认领任务
- IM 是一等任务入口
```

### 7. 组件化规范

划分原则、通信方式、大小上限，以及**何时抽离**。具体可验证。前端用组件模板，后端用模块模板——按项目类型选，不混用。

#### 前端（React / Vue / Next 等）

```markdown
## 组件化规范

**先定边界再写实现**——组件是开发的基本单位，单一职责、独立文件；变化优先用组合（props/variant/size/className）吸收，不复制、不轻易新增。

- 按功能域划分目录
- 组件通信：props down / events up，避免 prop drilling
- 共享组件：`src/components/shared/`，必须有 JSDoc
- 单组件超过 300 行触发职责与耦合评审，按明确边界决定是否拆分
- 抽离时机（命中任一才抽，不预先抽象）：
  - 同一段 JSX/模板重复 ≥ 2 次 → 检查业务语义与变化方向一致后决定复用
  - 条件渲染嵌套 ≥ 3 层 → 评审状态模型与职责边界
  - Props > 5 个 → 评审接口内聚性，不为规避数量合并配置对象
  - 同一状态逻辑在 ≥ 2 个组件出现 → 确认语义与生命周期一致后提取 Hook/Composable
```

#### 后端（Django / Spring / Go / API 服务）

```markdown
## 组件化规范

**按层切职责、依赖单向**——Handler（入参校验/响应）→ Service（业务）→ Repository（数据），上层依赖下层，下层不反向引用上层。

- Service 之间通过明确接口通信，不直接 import 对方实现
- 共享领域逻辑放 `domain/` 或 `core/`，不放 Controller
- 函数超过 80 行或参数超过 5 个触发职责与接口内聚性评审，不机械拆分或打包参数
- 抽离时机（命中任一才抽，不预先抽象）：
  - 同一业务校验在 ≥ 2 个 handler 出现 → 下沉 service/middleware
  - 同一数据访问模式重复 → 抽 repository
  - 一个类承担 > 1 个变更原因 → 按职责拆分
```

### 8. 设计方向

具体到 token 级别，不是泛泛的"使用设计系统"。

```markdown
## 设计方向

遵循 `{{设计系统路径}}`。{{设计风格名}}——{{具体 token}}。

{{风格名}}——8px 网格 · 3px 硬边框 · 0 圆角 · 硬质偏移阴影 · 高对比强调色。Space Mono → 标题/标签/状态；Hanken Grotesk → 正文/表单/日志。

设计 token 和共享样式沉淀到设计系统。优先通过 props/variant/size/className/组合扩展已有组件，无法表达时才新增。
```

### 9. UI 规范

具体可执行。

```markdown
## UI 规范

- 设计系统：shadcn/ui，禁止自定义基础组件
- 响应式：mobile-first，断点 640/768/1024/1280/1536px
- 主题：CSS 变量控制，支持 light/dark
- 图标：Lucide Icons，统一 20px
- 间距：4px 基础栅格
```

### 10. UX 规范

按 D-S-T-E 体验四步曲生成，不是泛泛罗列 UX 条目。

```markdown
## UX 规范

### 诊断（用户卡在哪里？）
- 新功能上线前必须做盲测：找非专业用户走完核心流程
- 停顿 > 3 秒的步骤必须标注原因并优化
- 需要"跳出产品找帮助"的步骤视为体验缺陷

### 简化（砍掉多余步骤）
- 3-5 铁律：核心需求 ≤ 3 次点击，完整流程 ≤ 5 步
- 不是 100% 必须的输入框，删掉
- 能预填的字段自动填充，能预判的操作主动提示

### 翻译（说人话）
- 用户是邻居大妈，不是同事——所有文案必须非专业人员能看懂
- 占位符给具体指引（"1000 元起购，1 元递增"），按钮写行动动词（"立即拿钱"）
- 错误提示必须可操作：告诉用户出了什么问题 + 能怎么办
- 专业术语用用户语言替换

### 升温（给体验加温度）
- 异步操作必有 loading 状态，超过 3 秒必须给出进度提示或安抚内容
- 关键操作成功需正反馈动效
- 等待时给确定性预期（时间预估 / 进度百分比）
- 交互元素需 aria-label，颜色对比度 ≥ 4.5:1
```

#### 后端项目的 UX 规范（D-S-T-E 适配版）

```markdown
## UX 规范

### 诊断
- API 响应时间 > 500ms 的端点必须标注并优化
- 4xx/5xx 错误率 > 1% 的端点视为体验缺陷

### 简化
- API 参数提供合理默认值，最少必须参数
- 支持批量操作，减少重复调用

### 翻译（说人话）
- 错误响应必须包含可操作的修复建议
  - ✗ `{"code": "VALIDATION_ERROR"}`
  - ✓ `{"code": "INVALID_EMAIL", "message": "邮箱格式不正确，请检查是否缺少 @", "suggestion": "示例：user@example.com"}`
- HTTP 状态码 + 业务错误码 + 人类可读 message

### 升温
- 长时间操作返回进度信息（轮询端点或 SSE）
- 健康检查端点给出各依赖服务状态摘要
- API 文档可交互（Swagger UI / Playground）
```

#### CLI 项目的 UX 规范（D-S-T-E 适配版）

```markdown
## UX 规范

### 诊断
- 命令失败率 > 5% 的命令必须优化提示

### 简化
- 最少 flag 完成核心操作，复杂场景用交互式引导
- 常见操作提供 short alias

### 翻译（说人话）
- 错误输出人类可读，带修复建议
- 成功输出结构化、带颜色区分

### 升温
- 长时间操作显示进度条
- 输出带颜色（绿=成功、黄=警告、红=错误）
- 支持 --quiet / --verbose 模式切换
```

### 11. 编码纪律

犀利直接，像团队里最靠谱的工程师在说。规则从 [behavioral-rules.md](behavioral-rules.md) 的 12 条目录按项目类型选子集，不照搬全量。

```markdown
## 编码纪律

- 有更简单做法时直接指出，不默默选复杂方案
- 不为一次性需求或"万一需要"创建抽象。200 行能写 50 行就重写
- 不顺手改进相邻代码；不重构正常工作的部分；匹配现有风格，哪怕你的方式更好
- 写新文件前先读相邻文件——没读过的代码写不出兼容代码
- 代码库自相矛盾时选一个模式贯彻，别折中出两套
- 能确定化的决策写代码，别路由给模型判断
- 自己引入的死代码删除；预先存在的死代码提出但不删
- 修 bug → 写重现测试再修；加验证 → 写失败测试再实现；重构 → 确保测试全过
- 出了问题大声说：摆出跳过的记录、失败的断言、部分结果，不静默吞掉
```

> 小团队（≤5 人）可把编码纪律 / 输出精简 / 目标驱动执行合并成一个前置 **## 行为规则** 章节，渲染模板见 [behavioral-rules.md](behavioral-rules.md)。

### 12. 输出精简

```markdown
## 输出精简

- 回复简短直接，不铺垫、不总结、不重复用户已知内容
- 变更说明用要点，不用段落散文
- 不解释"我做了什么"的每一步，只说关键决策和结果
- 代码注释只在必要时加，不写叙述性注释
```

### 13. 目标驱动执行

```markdown
## 目标驱动执行

- 定义清晰的成功标准再开始
- "修复 bug" → 写重现测试，让它通过
- "添加验证" → 写失败测试，然后实现
- "重构 X" → 确保重构前后测试都通过
- 多步骤任务先给简短计划，每步带验证方式
```

### 14. 项目文档管理

项目文档（spec / plan / log / 设计决策等）分类管理，执行过程统一记录，且**每个文件夹用「索引 + 分片 + 按需读」**——文件日益增长，但 LLM 每次只读 INDEX + 需要的分片，不全量加载。完整规范见 [doc-management.md](doc-management.md)。

```markdown
## 项目文档管理

文档分类放、执行过程统一记、每个文件夹渐进式读。不靠记忆，靠文件——工作前读 INDEX，工作后写分片。

### 分类

\`\`\`
doc/
├── INDEX.md          # 总索引：列所有分类 + 当前焦点
├── spec/             # 规格（需求/产品定义/契约）
├── plan/             # 计划（实施/迭代计划）
├── log/              # 执行日志（每日/每次工作）
├── design/           # 设计决策（ADR/技术选型）
├── ref/              # 选型调研、外部资料
└── assets/           # 截图等附件（log 引用，日期命名）
\`\`\`

分类按项目增删；每个文件夹都有自己的 `INDEX.md`。

**命名**：内容文件用 `YYYY-MM-DD-{标识}.md`（日期在前，按时间排序）；`INDEX.md` 不加日期。

### 执行闭环：spec → plan → log

每次工作串起来——读 spec（做什么）→ 读 plan（怎么做）→ 读 log 顶部（最近做了啥）→ 开工 → 验证 → 追加 log + 更新各 INDEX。

### 截图留存

log 记录**关键判断或失误修正**且有截图（错误现场、复现步骤、验证结果、前后对比）时，截图一并存档：存 `doc/assets/`（命名 `YYYY-MM-DD-{标识}.png`），log 条目用相对路径引用。文字会丢细节，现场截图不会；与判断/修正无关的过程截图不存。

### 计划变更纪律

- 开始或恢复时读取有效 Spec、设计依据和当前计划，核对依赖、阻塞与下一条可执行任务。
- 同一范围只保留一套有效约定；按授权和显式替代关系判断，不凭日期选择。Plan 不改写 Spec，Log 的行为决策同步回有效文档。
- 授权范围内只改实现或顺序，更新计划后继续；用户明确改变需求时先同步 Spec。未决的产品范围、验收、兼容性取舍只暂停受影响任务。
- 任务用稳定 ID；局部变化只替代相关任务，下游及已完成的受影响任务标为待复核，明确代码保留、修改、迁移或移除。
- 实施前同步相关 Spec、Design、Plan 和索引，记录原因及替代关系；完成以当前验收证据为准，旧测试通过不能直接沿用。
- 中断时记录当前依据、任务状态、阻塞项与下一步；恢复后不执行已替代、已废弃或依赖未满足的任务。

### 渐进式读取（每个文件夹通用）

1. 进任何文件夹先读它的 `INDEX.md`——几十行看全貌和最近结论
2. INDEX 指向哪个分片要细看，再读那 1-2 个
3. 不读历史全部，除非回溯某个具体决策
4. 写完更新所属 INDEX 的指针和结论

**铁律**：INDEX 只放指针和一句话结论，细节进分片——INDEX 永远小，这是按需读取的前提。
```

### 15. 提交与部署

```markdown
## 提交与部署

- 分支策略：feature/* 开发，main 发布
- 提交格式：Conventional Commits — type(scope): description
- 推送需确认：用户说"推送 GitHub"视为确认，只做轻量检查
```

### 16. 已知注意事项

Claude 容易犯的错、特殊约束——**价值密度最高的一节**：AI 反复犯同一个错，就记进来。

```markdown
## 已知注意事项

- API 路由在 /api/v2/ 而非 /api/（AI 常默认 v1）
- 数据库迁移必须通过 `prisma migrate dev` 生成迁移文件，禁止手改表结构
- 后端时间一律存 UTC，展示层才转时区

坑的格式：**坑 → 为什么踩 → 正确做法**，命令式语气（必须/禁止），不写"我们倾向于"。
```

## CLAUDE.md 示例

以下是一个完整的多 Agent 工作台项目的 CLAUDE.md 示例，展示各章节如何组合：

```markdown
# Maya 项目 Agent 开发指南

## 项目概览

Maya 是多 Agent 工作管理台——管理工作目标、任务队列、审批、产物、IM 入口、云端/本地 Agent 执行环境。

**关键文档：** 计划 `doc/plan/INDEX.md` · 执行日志 `doc/log/INDEX.md`

## 特有规则

### 1. 先调研再自研
开发任何能力前，先调研开源/已有方案，能直接用或改造的不自研；只有构成产品核心差异化的能力才从零实现。调研记 `doc/ref/`，选型结论记 spec 和执行日志。

### 2. 参考项目优先
开发底层能力前，先检查 `参考/multica-0.3.17` 是否已有实现。有则迁移/改写为 Maya 语义；无覆盖时才从零实现。

### 3. 工作平台而非聊天产品
聊天/IM 是任务入口，持久状态沉淀到 Goal、Task、Approval、Artifact 和执行日志。

### 4. 开始前必读
实现任务前读产品计划和执行日志。若请求改变方向或顺序，先更新计划/日志再编码。

### 5. 本地验证优先，推送需确认
先本地验证（typecheck、lint、test、Docker smoke）。GitHub 推送/PR/Release 必须等用户明确指令。

### 6. 执行日志
每次工作追加 `doc/log/{日期}.md` 并更新 `log/INDEX.md`：目标、变更、决策、验证、缺口。关键判断/失误修正有截图时，存 `doc/assets/` 并在 log 里引用。不流水账。

## 核心领域对象

Goal · Task · Task Run · Agent · Runtime/Worker · Skill Pack · Approval · Artifact · Channel Connection · Secret Credential

添加能力优先用这些概念，不引入不必要的新抽象。

## 设计方向

遵循 `参考/设计文件/agentpixel_design_system/DESIGN.md`。

AgentPixel Digital Brutalism——8px 网格 · 3px 硬边框 · 0 圆角 · 硬质偏移阴影 · 高对比强调色。Space Mono → 标题/标签/状态；Hanken Grotesk → 正文/表单/日志。像素风是品牌层，不损害状态可扫描性。

设计 token 和共享样式沉淀到设计系统。优先通过 props/variant/size/className/组合扩展已有组件，无法表达时才新增。

## 编码纪律

- 有更简单做法时直接指出，不默默选复杂方案。
- 不为一次性需求或"万一需要"创建抽象和配置。200 行能写 50 行就重写。
- 不顺手改进相邻代码；不重构正常工作的部分。
- 自己引入的死代码删除；预先存在的死代码提出但不删。
- 修 bug → 写重现测试再修；加验证 → 写失败测试再实现；重构 → 确保测试全过。

## 输出精简

- 回复简短直接，不铺垫、不总结、不重复用户已知内容。
- 变更说明用要点，不用段落散文。
- 不解释"我做了什么"的每一步，只说关键决策和结果。
- 代码注释只在必要时加，不写叙述性注释。
```

## 路径规则模板

### `.claude/rules/api-rules.md`

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "app/api/**/*.ts"
---

# API 开发规范

- 所有 API 端点必须包含输入校验
- 使用标准错误响应格式
- API 路由文件命名：`route.ts`（Next.js）或 `{{resource}}.ts`
```

### `.claude/rules/component-rules.md`

```markdown
---
paths:
  - "src/components/**/*.tsx"
  - "src/components/**/*.ts"
---

# 组件开发规范

- 组件文件必须包含 JSDoc 注释
- Props 使用 TypeScript interface 定义
- 事件处理器命名：`on{{Action}}`
- 每个组件一个文件，文件名 = 组件名
```

### `.claude/rules/testing-rules.md`

```markdown
# 测试规范

- 新功能必须附带测试
- 测试文件命名：`{{source}}.test.{{ext}}`
- 最小覆盖率：{{如：80%}}
- Mock 外部依赖，不 mock 内部模块
```

## settings.json 模板

### `.claude/settings.json`

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(pnpm install)",
      "Bash(pnpm test *)",
      "Bash(pnpm lint)",
      "Bash(pnpm build)"
    ],
    "deny": [
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  },
  "autoMemoryEnabled": true
}
```

### `.claude/settings.local.json`（.gitignore）

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git push *)",
      "Bash(git commit *)"
    ]
  }
}
```

## 持续开发规则片段（开发项目按需纳入）

将路径替换为项目真实路径；小任务可单文件分节。无 UI 项目省略 UI 条目。详细流程见 [doc-management.md](doc-management.md)，生成到目标项目时须将必要规则写入目标文档或链接项目内已有规范，不能只链接本 Skill。

```markdown
## 变更与持续推进

- 开始或恢复时读取有效 Spec、设计依据和当前计划，核对依赖、阻塞与下一条可执行任务。
- 同一范围只保留一套有效约定；按授权和显式替代关系判断，不凭日期选择。Plan 不改写 Spec，Log 的行为决策同步回有效文档。
- 授权范围内只改实现或顺序，更新计划后继续；用户明确改变需求时先同步 Spec。未决的产品范围、验收、兼容性取舍只暂停受影响任务。
- 任务用稳定 ID；局部变化只替代相关任务，下游及已完成的受影响任务标为待复核，明确代码保留、修改、迁移或移除。
- 实施前同步相关 Spec、Design、Plan 和索引，记录原因及替代关系；完成以当前验收证据为准，旧测试通过不能直接沿用。
- 中断时记录当前依据、任务状态、阻塞项与下一步；恢复后不执行已替代、已废弃或依赖未满足的任务。

## 组件与设计约束

- 新增前检索现有组件与模块，在功能 Spec 记录复用、扩展或新建的理由；定义职责、状态归属与依赖方向。
- 基础 UI、业务组件、页面编排按职责划分；基础 UI 不依赖业务页面，业务逻辑与数据访问遵守项目既定边界。
- 修改共享组件前列出受影响调用方，兼容策略及回归范围写入 Spec；不因外观相似强行合并不同业务语义。
- 颜色、字体、间距引用项目设计 Token；优先扩展既有组件变体，例外记录原因与范围。设计系统详细定义只维护一份。
- 涉及 UI 的 Spec 引用设计依据，列出适用的加载、空、错误、成功、禁用状态，以及响应式、键盘和焦点验收。
- 行数、Props 数、重复次数仅触发评审；根据职责混杂、状态耦合和独立变化决定拆分，不用配置对象隐藏复杂度。
```

## Skill 项目的测试验收

创作/优化 Skill 的项目必须采用 [Skill 版本化对照测试](skill-evaluation.md) 的规则片段，包含改前快照、固定用例、最近相邻两版独立生成、按版本追加样例及真实对比报告。已有 AGENTS.md 时只桥接，避免维护第二份规则；详细测试入口放目标项目内，不能只引用本 Skill 的内部文件。新建 Skill 建首次基线，不伪造旧版。每次只比较最近相邻两版：修改前最近一版 baseline 与修改后最新版 candidate，例如 v2→v3，下一轮 v3→v4。更早版本仅归档，不参与本轮比较；最近前版缺失时报告无法对照，不用更早版本顶替。
