# AGENTS.md 模板与生成规范

## 目录

- [文件规范](#文件规范)
- [与 CLAUDE.md 的关系](#与-claudemd-的关系)
- [从其它工具规则文件迁移](#从其它工具规则文件迁移)
- [AGENTS.md 章节](#agentsmd-章节)
- [不包含的内容](#不包含的内容)
- [反模式：什么不该写](#反模式什么不该写)
- [嵌套 AGENTS.md：monorepo 决策](#嵌套-agentsmdmonorepo-决策)
- [AGENTS.md 示例](#agentsmd-示例)
  - [全栈应用（Maya）](#全栈应用maya)
  - [API 后端](#api-后端)
  - [CLI 工具 / 库](#cli-工具--库)
  - [Skill / 知识仓库（非开发）](#skill--知识仓库非开发项目)
- [质量检查（强制子流程）](#质量检查强制子流程)
- [何时回炉：防漂移](#何时回炉防漂移)

## 文件规范

- **是给 Agent 执行的指令集，不是给人看的 README**——写进去的命令会被真执行。用命令式语气（必须/禁止），不写愿景和倾向
- 纯 Markdown，无 frontmatter、无 `@import`、无特殊语法
- 20+ AI 工具支持（Codex、Cursor、Copilot、Jules、Aider 等）
- 子目录可嵌套 AGENTS.md，最近的文件优先
- 核心规则与 CLAUDE.md 保持一致

## 与 CLAUDE.md 的关系

Claude Code 读取 `CLAUDE.md`，不直接读 `AGENTS.md`。

| 桥接方式 | 适用场景 |
|----------|---------|
| `@AGENTS.md` 导入 | CLAUDE.md 只需追加 Claude 专属规则 |
| `ln -s AGENTS.md CLAUDE.md` | 两份完全相同 |
| 独立维护 | CLAUDE.md 需 Claude 专属功能（`@import`、路径规则等） |

### 谁是主文件（canonical source）

生成两份时先定主从，避免规则双份漂移：

| 团队用什么 | 主文件 | 另一份 |
|-----------|--------|--------|
| 只用 Codex / Cursor / Copilot 等（非 Claude） | AGENTS.md | 不生成 CLAUDE.md |
| 只用 Claude Code | CLAUDE.md | 不生成 AGENTS.md |
| Claude + 其它工具混用 | AGENTS.md | CLAUDE.md 用 `@AGENTS.md` 导入，只追加 Claude 专属规则 |

**判据**：通用规则只写一份，写在覆盖面最广的载体里。Claude 专属能力（`@import`、`.claude/rules/`、settings.json hooks）才单独进 CLAUDE.md。

## 从其它工具规则文件迁移

扫描常发现历史规则文件。AGENTS.md 是跨工具标准，目标是**单一来源**——通用规则只留一份，其余指向它或删除。

| 发现的文件 | 处理 |
|-----------|------|
| `.cursorrules` | 合并进 AGENTS.md 后删除（Cursor 现读 AGENTS.md / `.cursor/rules/`） |
| `.cursor/rules/*.mdc` | 保留（支持 path-scoped），但通用规则迁进 AGENTS.md，避免双份 |
| `.github/copilot-instructions.md` | 合并后删除，或改写成 `参见 AGENTS.md` |
| `.trae/rules/*.md` | 内容按是否 Claude 专属分流进 AGENTS.md / `.claude/rules/` |
| 子目录已有 AGENTS.md | 按「嵌套 AGENTS.md」判断保留还是合并回根 |

**原则**：同一规则只留一份，多份必然漂移，矛盾的规则比没规则更糟。合并时先核对范围、现有授权与显式替代关系；只有缺少依据的冲突才向用户提出具体取舍。

## AGENTS.md 章节

与 CLAUDE.md 共享核心内容，去掉 Claude 专属规则（如 `@import`、`.claude/rules/`、`CLAUDE.local.md` 等）。

### 必选章节

1. **项目概览** — 与 CLAUDE.md 相同
2. **开发环境** — 运行时、包管理、OS 支持
3. **构建命令** — install / dev / build / lint / format
4. **测试** — test / test single / 覆盖率 / CI 位置
5. **代码风格** — 缩进、引号、分号、命名、导入排序
6. **项目结构** — 目录树 + 用途注释

### 按需章节

7. **架构决策** — 关键选择、数据流、错误处理策略
8. **核心领域对象** — 项目心智模型
9. **组件化规则** — 划分、通信、共享组件、大小上限、抽离时机（前端组件 / 后端模块分层，按项目类型选）
10. **UI 规则** — 设计系统、响应式、主题、图标、间距
11. **UX 规则** — 操作反馈、表单校验、无障碍、错误提示
12. **安全约束** — 敏感文件、依赖安全、API 安全
13. **项目文档管理** — doc 分类（spec/plan/log/design/ref）、每个文件夹 INDEX 分片、渐进式按需读、spec→plan→log 执行闭环、变更协议（授权判断、局部替代、下游复核、检查点恢复）、截图留存（关键判断/失误修正的截图存 `doc/assets/` 并在 log 里引用）
14. **提交规范** — 格式、类型、PR 要求
15. **行为规则** — 从 [behavioral-rules.md](behavioral-rules.md) 选子集（简单优先、读后写、冲突按依据解决、测试、失败响亮等跨工具通用规则）

### 不包含的内容

- `@import` 语法
- `.claude/rules/` 引用
- `CLAUDE.local.md` 相关
- `settings.json` 相关
- Claude Code 专属指令

## 反模式：什么不该写

好的 AGENTS.md 是工作手册，不是文档。下面是让它腐烂的常见写法——都是内容层面，不是语法：

**冗余**
- **抄 README** — 产品介绍链 README 即可，这里只放"agent 怎么干活"
- **堆全量架构** — agent 干活不需要读完架构，需要可执行规则。大段架构放独立文档，AGENTS.md 只留决策结论
- **列到每个文件** — 目录结构给到"用途"层级（`src/components/` 是组件），不展开文件清单
- **重述可推断内容** — 不用告诉 agent"保持代码整洁""写注释"，它知道。实证：2026 年 ETH Zurich 研究（138 仓库 / 5,694 PR）发现 README 式 AGENTS.md 轻微**降低** agent 表现还多耗 token；有效的只有**窄而不可推断的指令**——构建命令、踩坑记录、验证步骤。只写 agent 从代码里看不出来的

**不可执行**
- **口号规则** — "写高质量代码""注意性能"无法判断违反与否。说不清"怎样算违反"的规则，删掉
- **描述而非命令** — ✗ "代码应该有测试" → ✓ "新功能必须附测试，命名 `{{source}}.test.{{ext}}`"

**危险**
- **密钥 / token / 内部 URL** — 永远不。AGENTS.md 进版本库，任何能看到仓库的人都能看到
- **与代码矛盾的规则** — AGENTS.md 说用 zustand、代码全是 redux，比没规则更糟。两套并存时选一个贯彻，别留错的

**易腐烂**
- **一次性 / 临时状态** — sprint 计划、TODO 清单、"暂时绕过 X"的说明，放 issue 或日志。AGENTS.md 是稳定约定，不是工作台
- **工具专属语法** — `@import`、frontmatter、HTML 注释，除非确认所有消费工具都支持。AGENTS.md 的价值在跨工具，别为单一工具破坏兼容

## 嵌套 AGENTS.md：monorepo 决策

子目录可放独立 AGENTS.md，**最近的文件优先**。但"可以"不等于"应该"——只在子路径需要与根规则**冲突或互不适用**时才嵌套。

### 什么时候嵌套

| 场景 | 嵌套？ | 理由 |
|------|--------|------|
| 子包技术栈不同（根是 TS monorepo，`packages/worker/` 是 Python） | ✓ | 命令、风格、测试全不一样 |
| 子包约定与根冲突（根用函数组件，子包用 class 组件） | ✓ | 冲突规则必须就近声明 |
| 子包独立发布、有自己的外部贡献者 | ✓ | 贡献者只关心这一层 |
| 子包只是目录划分，栈和约定都同根 | ✗ | 重复根规则，维护双份 |
| 子包规则是根的补充、不冲突 | ✗ | 写根里，别拆 |

**判据**：嵌套是为了让子路径的 agent 读到**不同**规则，不是为了"组织清晰"。规则不分化就别分文件。

### 各层放什么

- **根 AGENTS.md**：仓库级约定、monorepo 工具（turbo/nx/pnpm workspace）、包间依赖方向、跨包共享规则
- **嵌套 AGENTS.md**：只写与根**不同**的部分——栈、命令、风格、测试。**不重复根内容**，必要时 `参见根 AGENTS.md`

### 注意

子目录的 AGENTS.md 只对"主动读它的 agent"生效。Claude Code 读 CLAUDE.md 不读 AGENTS.md——若混用，嵌套的 AGENTS.md 要在对应子目录配 CLAUDE.md，或用 `@path/to/subdir/AGENTS.md` 导入。

## AGENTS.md 示例

按项目类型选最接近的示例（开发型：全栈 / 后端 / CLI；非开发型：Skill 仓库）。密度保持一致，按项目实际增删——不是照搬。

### 全栈应用（Maya）

```markdown
# Maya

多 Agent 工作管理台——管理工作目标、任务队列、审批、产物、IM 入口、云端/本地 Agent 执行环境。

## 开发环境

- **运行时**: Node.js 20+
- **包管理**: pnpm 9
- **OS**: macOS / Linux

## 构建命令

\`\`\`bash
pnpm install          # 安装依赖
pnpm dev              # 开发模式
pnpm build            # 构建
pnpm lint             # 代码检查
pnpm format           # 格式化
\`\`\`

## 测试

\`\`\`bash
pnpm test             # 运行全部测试
pnpm test -- --grep "xxx"  # 运行特定测试
\`\`\`

- 新代码覆盖率不低于 80%
- CI: GitHub Actions `.github/workflows/test.yml`

## 代码风格

- 2 空格缩进，单引号，无分号
- 变量/函数 camelCase，类型/接口 PascalCase，常量 UPPER_SNAKE_CASE
- 导入排序：外部库 → 内部模块 → 相对路径 → 类型 → 样式

## 项目结构

\`\`\`
maya/
├── src/
│   ├── app/           # Next.js App Router 页面
│   ├── components/    # React 组件
│   ├── lib/           # 工具函数和共享逻辑
│   ├── services/      # 业务服务层
│   └── types/         # TypeScript 类型定义
├── doc/               # 项目文档
└── 参考/              # 参考项目
\`\`\`

## 核心领域对象

Goal · Task · Task Run · Agent · Runtime/Worker · Skill Pack · Approval · Artifact

添加能力优先用这些概念，不引入不必要的新抽象。

## 架构决策

- API Server = 控制平面，不直接执行 CLI
- Runtime/Worker = 执行平面，队列认领任务
- 单向数据流，状态不可变

## 组件化规则

**先定边界再写实现**——组件是基本单位，单一职责、独立文件；变化优先用组合吸收，不复制、不轻易新增。

- 按功能域划分目录
- 组件通信：props down / events up
- 共享组件：`src/components/shared/`
- 单组件超过 300 行触发职责与耦合评审，按明确边界决定是否拆分
- 抽离时机：重复 JSX ≥ 2 次 / 条件嵌套 ≥ 3 层 / props > 5 才抽，不预先抽象

## UX 规则（D-S-T-E 体验四步曲）

### 诊断（用户卡在哪里？）
- 新功能上线前必须做盲测：找非专业用户走完核心流程
- 停顿 > 3 秒的步骤必须标注原因并优化

### 简化（砍掉多余步骤）
- 3-5 铁律：核心需求 ≤ 3 次点击，完整流程 ≤ 5 步
- 不是 100% 必须的输入框，删掉
- 能预填的字段自动填充

### 翻译（说人话）
- 所有文案必须非专业人员能看懂
- 占位符给具体指引，按钮写行动动词
- 错误提示必须可操作

### 升温（给体验加温度）
- 异步操作必有 loading 状态，超过 3 秒给进度提示
- 关键操作成功需正反馈
- 交互元素需 aria-label

## 提交规范

- Conventional Commits: type(scope): description
- 类型：feat / fix / docs / refactor / test / chore
- PR 需要 1 review + CI 通过

## 安全约束

- .env 文件禁止读取和提交
- 所有 API 输入需 schema 校验
- 仅使用参数化查询
```

### API 后端（Django / FastAPI / Go 等）

```markdown
# Orders API

订单域的内部 API——处理下单、支付、履约状态。被 Web 端和定时任务消费，不直接面向终端用户。

## 开发环境

- **运行时**: Python 3.12
- **包管理**: uv
- **数据库**: PostgreSQL 16
- **OS**: macOS / Linux

## 构建命令

\`\`\`bash
uv sync                              # 安装依赖
uv run python manage.py runserver    # 开发模式
uv run pytest                        # 测试
uv run ruff check .                  # lint
uv run ruff format .                 # 格式化
\`\`\`

## 测试

\`\`\`bash
uv run pytest tests/orders/ -k refund      # 单域/单用例
uv run pytest --cov=app --cov-report=term-missing
\`\`\`

- 新代码覆盖率不低于 80%
- CI: `.github/workflows/test.yml`

## 代码风格

- 4 空格缩进，行宽 100
- 函数 snake_case，类 PascalCase，常量 UPPER_SNAKE_CASE
- 导入顺序：标准库 → 第三方 → 本应用

## 项目结构

\`\`\`
orders-api/
├── app/
│   ├── handlers/      # HTTP 入口：入参校验、响应序列化
│   ├── services/      # 业务逻辑，不碰 HTTP
│   ├── repositories/  # 数据访问，不碰业务
│   ├── domain/        # 跨模块共享的领域模型与规则
│   └── schemas/       # 请求/响应 schema
└── tests/
\`\`\`

## 核心领域对象

Order · OrderLine · Payment · Fulfillment · Refund

## 架构决策

- 分层单向依赖：Handler → Service → Repository，下层不反向引用上层
- Service 之间通过接口通信，不直接 import 对方实现
- 外部输入在 Handler 用 schema 校验后才进 Service
- 事务边界在 Service，不在 Handler

## 组件化规则

**按层切职责、依赖单向**——Handler（入参校验/响应）→ Service（业务）→ Repository（数据），上层依赖下层，下层不反向引用上层。

- 共享领域逻辑放 `domain/`，不放 Handler
- 函数超过 80 行或参数超过 5 个触发职责与接口内聚性评审，不机械拆分或打包参数
- 抽离时机：同一校验在 ≥ 2 个 handler 出现 → 下沉 service/middleware；同一数据访问重复 → 抽 repository

## 安全约束

- `.env` 禁止读取和提交，密钥走环境变量
- 所有查询用 ORM/参数化，禁止拼接 SQL
- 所有端点鉴权，输入用 schema 校验
- 错误响应不泄漏内部结构（堆栈、SQL、字段名映射）

## 提交规范

- Conventional Commits: type(scope): description
- schema 变更必须附迁移文件
```

### CLI 工具 / 库

```markdown
# ftpulse

文件传输健康检查 CLI——轮询 SFTP/FTPS 站点，探测可达性与延迟，输出结构化报告。单二进制，零运行时依赖。

## 开发环境

- **语言**: Go 1.22
- **包管理**: Go modules
- **OS**: macOS / Linux / Windows

## 构建命令

\`\`\`bash
go build ./...              # 编译全部
go run ./cmd/ftpulse        # 本地运行
go test ./...               # 测试
go vet ./...                # lint
golangci-lint run           # 深度 lint
\`\`\`

## 测试

\`\`\`bash
go test ./...                           # 全部
go test ./internal/probe -run TestDial  # 单用例
go test -race ./...                     # 竞态检测
go test -cover ./internal/probe         # 覆盖率
\`\`\`

- 核心包覆盖率不低于 85%
- 公共 API 必须有表驱动测试
- CI 跑 Linux + macOS + Windows

## 代码风格

- gofmt + goimports，无配置
- 导出标识符必须有文档注释（`// Foo ...`）
- 错误用 `fmt.Errorf("probe %s: %w", host, err)` 包裹，保留调用链

## 项目结构

\`\`\`
ftpulse/
├── cmd/ftpulse/    # main：仅组装依赖，不放逻辑
├── internal/       # 不对外暴露的实现
│   ├── probe/      # 探测逻辑
│   ├── report/     # 报告生成
│   └── config/     # 配置解析
├── pkg/            # 对外稳定的库 API
└── README.md
\`\`\`

## 架构决策

- `cmd/` 只组装依赖，逻辑全在 `internal/`
- 对外稳定 API 只放 `pkg/`，破坏性变更走 semver 主版本
- 配置走显式结构体，不读全局变量
- 错误面向用户：可读信息 + 退出码，不裸抛堆栈

## 组件化规则

**`cmd/` 只组装、逻辑全进 `internal/`**——按职责分包（如 probe/report/config），包间走接口；对外稳定面只放 `pkg/`，`internal/` 不被外部 import。

- 抽离时机：同一探测模式重复 ≥ 2 次 → 抽到 `probe` 公共方法

## 行为规则

- **读后再写** — 改公共 API 前先读调用点，CLI 的兼容性靠这个
- **测试不是可选** — 公共 API 必须表驱动测试；为错的原因通过的测试比没有更糟
- **失败要响亮** — 探测失败给具体站点和原因，不静默返回空报告

## 提交规范

- Conventional Commits: type(scope): description
- 破坏性变更用 `feat!:` 或 footer `BREAKING CHANGE:`
- 发布打 tag `vX.Y.Z`，CI 构建多平台二进制
```

### Skill / 知识仓库（非开发项目）

非开发项目不谈组件化/构建命令，谈**业务立场**——这个仓库的"业务"是造和维护 skill。用「核心立场」节替代开发项目的组件化节。

```markdown
# My Skills

个人 AI Skill 仓库。N 个 skill，通过软链部署到 `~/.claude/skills/` 和 `~/.codex/skills/`。

## 部署

\`\`\`bash
./update-skills.sh     # 拉取/克隆 → 软链 skills/* → 清理孤儿软链
\`\`\`

## 核心立场

- **改优于写**：Skill 核心能力是"改"不是"写"——先解构高手 skill，再适配个人场景，不从零造
- **执行文件只写当前规则**：版本日志/升级说明/旧版对比移到独立 CHANGELOG.md；不被引用就不耗 token
- **可选参数不静默跳过**：可空/可选参数缺失时主动问用户，确认后再继续
- **价值优先、去营销化**：发布类 skill 的产出要去营销语气，避免被平台判广告

## 结构规则（skill 的"组件化"）

- 命名一致：`wtt-` 或 `wtt-course-` 开头，kebab-case；文件夹名 = SKILL.md 的 `name` 字段
- 新建/删除 skill 必须四处同步：CLAUDE.md、AGENTS.md、marketplace.json、skills/ 目录
- 分组归属：marketplace.json 分组 ↔ CLAUDE.md 清单一一对应

## Skill 优化验收

- 测试入口使用各 Skill 的 tests/evals/README.md；已有入口保留。缺少时先建立固定输入、评审标准及真实运行步骤。
- 每次只比较最近相邻两版：修改前最近一版 baseline 与修改后最新版 candidate，例如 v2→v3，下一轮 v3→v4。更早版本仅归档，不参与本轮比较；最近前版缺失时报告无法对照，不用更早版本顶替。首次创建只建首次基线；已有 Skill 的最近前版缺失时标明无法对照。
- 修改前冻结包含未提交改动的完整运行依赖、版本与哈希；窗口内各版在相同输入和模型配置下独立生成，至少覆盖本次影响用例与核心回归。新建 Skill 建首次基线。
- 用例和评审标准固定版本，每次新版真实输出按 Skill 版本与唯一运行 ID 追加，失败/退步也留存；不覆盖旧证据。
- 输出评审后才作为参考样例，失败补成回归用例；新增输入升测试集版本，下一轮窗口内各版同跑。
- 交付真实对比报告与原始输出链接，包含三版证据、改善、退步、硬失败和未运行项；无对照时报告“修改完成，生成验证未完成”。

## 验证

- 改完跑部署脚本，确认软链生效、无孤儿
- 引用链完整：SKILL.md 引用的 references/ 文件都存在
- 四处同步无遗漏
```

## AGENTS.md 质量检查（强制子流程）

本节已提升为独立的**强制核验子流程**——19 项检查 + 验证方法 + 门控协议，见 [agents-md-checklist.md](agents-md-checklist.md)。

调用：SKILL.md 第 4 步生成后强制执行（任一不达标回炉，全过才写入）；也可独立审计已有 AGENTS.md。

## 何时回炉：防漂移

AGENTS.md 会随代码腐烂。下列信号出现，就该更新（不是重写）：

- **Agent 反复犯同一个错** → 缺规则，补一条具体的（呼应"有名字的规则"）
- **技术栈 / 框架大版本升级** → 命令、约定、目录结构都可能变，重扫一遍
- **新增子包或大模块** → 判断是否需要嵌套 AGENTS.md
- **代码与文档矛盾**（按 AGENTS.md 干活却产出错误代码）→ 先区分文档过期、实现违规和已授权迁移；修正错误来源，不默认让文档迁就代码
- **合并了带不同约定的团队或代码** → 按适用范围、授权及替代关系重新对齐，未决取舍再询问

**反信号**：连续几个月没人需要改 AGENTS.md，要么项目静止，要么它已经没人读——后者说明规则太泛或太碎，该精简而不是加料。

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
