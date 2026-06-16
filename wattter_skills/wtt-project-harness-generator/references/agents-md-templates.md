# AGENTS.md 模板与生成规范

## 文件规范

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
9. **组件化规则** — 划分、通信、共享组件、大小上限
10. **UI 规则** — 设计系统、响应式、主题、图标、间距
11. **UX 规则** — 操作反馈、表单校验、无障碍、错误提示
12. **安全约束** — 敏感文件、依赖安全、API 安全
13. **提交规范** — 格式、类型、PR 要求

### 不包含的内容

- `@import` 语法
- `.claude/rules/` 引用
- `CLAUDE.local.md` 相关
- `settings.json` 相关
- Claude Code 专属指令

## AGENTS.md 示例

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

- 按功能域划分，单一职责，一个组件一个文件
- 组件通信：props down / events up
- 共享组件：`src/components/shared/`
- 单组件 < 300 行，超过则拆分

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
