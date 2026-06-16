# Harness 规范与推断规则

## 目录

- [Harness 架构](#harness-架构)
- [组件选用决策](#组件选用决策)
- [技术栈推断](#技术栈推断)
- [组件化推断](#组件化推断)
- [UI/UX 规范推断](#uiux-规范推断)
- [对话引导问题](#对话引导问题)

## Harness 架构

```
项目根目录/
├── CLAUDE.md                  # 核心项目指令（< 200 行）
├── CLAUDE.local.md            # 个人偏好（.gitignore）
├── AGENTS.md                  # 跨工具通用指令
├── .claude/
│   ├── settings.json          # 共享项目设置
│   ├── settings.local.json    # 个人设置（.gitignore）
│   └── rules/                 # 模块化路径范围规则
│       ├── code-style.md      # 无条件规则
│       └── api/
│           └── endpoints.md   # 路径范围规则
└── .mcp.json                  # 项目级 MCP 服务器
```

### 组件强制性

| 组件 | 强制性 | 说明 |
|------|--------|------|
| CLAUDE.md | 指导性 | 上下文塑造行为，不保证 100% 遵守 |
| .claude/rules/ | 指导性 | 按需加载，节省上下文 |
| settings.json permissions | 强制性 | deny 优先于 allow |
| settings.json hooks | 强制性 | 确定性执行，不管 LLM 决定什么 |

## 组件选用决策

| 场景 | 使用 |
|------|------|
| Claude 两次犯同一约定错误 | CLAUDE.md 规则 |
| 规则仅适用部分文件 | .claude/rules/ + paths frontmatter |
| 每次都必须执行某操作 | Hook（非提示指令） |
| 重复输入相同提示 | Skill |
| 限制/允许特定命令 | settings.json permissions |

**关键**：必须保留的规则用 hook，不用提示指令。

## 技术栈推断

| 检测到文件/目录 | 推断 |
|----------------|------|
| `next.config.*` + `app/` | Next.js App Router |
| `next.config.*` + `pages/` | Next.js Pages Router |
| `nuxt.config.*` | Nuxt.js |
| `vite.config.*` + `vue` | Vue 3 + Vite |
| `angular.json` | Angular |
| `django/` / `settings.py` | Django |
| `flask/` / `app.py` | Flask |
| `pom.xml` / `spring` | Spring Boot |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pnpm-workspace.yaml` | pnpm Monorepo |
| `turbo.json` | Turborepo Monorepo |
| `nx.json` | Nx Monorepo |

## 组件化推断

| 项目类型 | 组件化模式 |
|----------|-----------|
| React 前端 | 函数组件 + Hooks，按功能域分目录 |
| Vue 前端 | SFC + Composables，按功能域分目录 |
| Angular | Module/Component/Service 三层 |
| Next.js 全栈 | App Router 路由组 + Server Components |
| Django | App 分模块，MTV 模式 |
| Spring Boot | Controller/Service/Repository 三层 |
| Go | Handler/Service/Repository + 接口抽象 |
| Monorepo | Packages 分包，apps 消费 packages |

### 状态管理推断

| 检测到依赖 | 推荐 |
|------------|------|
| `zustand` | Zustand store |
| `redux` / `@reduxjs/toolkit` | Redux Toolkit |
| `pinia` | Pinia store |
| `@tanstack/query` | Server State: Query, Client State: Zustand/Pinia |
| 无状态管理库 | Context + useReducer 或按需引入 |

### 样式方案推断

| 检测到 | 样式方案 |
|--------|---------|
| `tailwind.config.*` | Tailwind CSS |
| `*.module.css` | CSS Modules |
| `styled-components` | styled-components |
| `@emotion/*` | Emotion |
| `uno.config.*` | UnoCSS |

## UI/UX 规范推断

### D-S-T-E 体验四步曲

所有项目的 UX 规范按 D-S-T-E 四步闭环生成：

```
诊断（盲测）→ 简化（3-5铁律）→ 翻译（说人话）→ 升温（微交互+AI）
     ↑                                                    ↓
     └────────────── 形成闭环，持续迭代 ──────────────────┘
```

**口诀**："盲三点，简三五，翻译说人话，升温微交AI"

- 盲三（点）：盲测发现 3 秒停顿点
- 简三五（步）：3 步点击，5 步操作
- 说人话：翻译成用户语言
- 微交 AI：微交互 + AI 升温

### 按项目类型适配 D-S-T-E

**Web 应用**：

| D-S-T-E | 生成内容 |
|---------|---------|
| D 诊断 | 盲测法则 + 用户情绪地图 + 3 秒停顿检测 |
| S 简化 | 3-5 铁律 + 奥卡姆剃刀 + 预判需求 + 预填写 |
| T 翻译 | 黑话扫雷 + 占位符指引 + 按钮行动化 + 错误提示可操作 |
| E 升温 | 微交互动效 + 安抚机制 + 无障碍 + 确定性预期 |

**API 后端**：

| D-S-T-E | 生成内容 |
|---------|---------|
| D 诊断 | API 响应时间监控 + 错误率热点 |
| S 简化 | 最少必须参数 + 合理默认值 + 批量操作 |
| T 翻译 | 可操作错误信息（code + message + suggestion）|
| E 升温 | 长操作进度反馈 + 健康检查摘要 + 可交互文档 |

**CLI/库**：

| D-S-T-E | 生成内容 |
|---------|---------|
| D 诊断 | 命令失败率监控 |
| S 简化 | 最少 flag + short alias + 交互式引导 |
| T 翻译 | 人类可读错误 + 修复建议 |
| E 升温 | 进度条 + 彩色输出 + quiet/verbose 模式 |

**数据/ML**：

| D-S-T-E | 生成内容 |
|---------|---------|
| D 诊断 | 数据异常检出 + 输入 schema 校验 |
| S 简化 | 自动推断 schema + 合理默认参数 |
| T 翻译 | 图表标题/轴标签/图例 + 异常给出具体行号字段 |
| E 升温 | 训练 metrics 可视化 + 进度预估 |

### D-S-T-E 关键方法速查

**诊断方法**：
- 盲测法则：找非专业用户测试，卡住就是产品不合格
- 3 秒停顿：用户操作停顿超过 3 秒的步骤，必须标注原因
- 跳出率热点：用户需要跳出产品找帮助的步骤，视为缺陷
- 恐惧点：用户"怕填错"的犹豫，需要安抚或简化

**简化方法**：
- 3-5 铁律：核心需求 ≤ 3 次点击，完整流程 ≤ 5 步
- 奥卡姆剃刀：不是 100% 必须的输入框就删掉
- 预判需求：用户复制卡号→弹转账提示；连续输错→提示找回密码
- 预填写：能自动填充的字段绝不手动输入

**翻译方法**：
- 黑话扫雷：专业术语→用户语言（借记卡→储蓄卡，签约→开通）
- 占位符指引：别只写"请输入"→写"1000 元起购，1 元递增"
- 按钮行动化：别只写"确定"→写"立即拿钱"
- 错误可操作：✗"代码 9908" → ✓"余额不足，可用余额 xx 元，先转这么多？"

**升温方法**：
- 微交互：成功动效、成就反馈
- 安抚机制：加载 > 3 秒别只转圈圈，给有趣动画或有用信息
- 确定性预期：等待时告诉用户"还需要约 30 秒"
- AI 辅助：用 AI 工具快速生成整改原型

### 按团队规模

| 规模 | 严格度 | 覆盖范围 |
|------|--------|---------|
| 1人 | 宽松 | 命名 + 测试 |
| 2-5人 | 中等 | 命名 + 组件化 + UI/UX + 测试 |
| 5-20人 | 严格 | 全部章节 + 路径规则 |
| 20+人 | 最严格 | 全部 + hooks + CI gates |

## 对话引导问题

### 必问（扫描推断不了时）

1. **项目类型**：Web 应用 / API 服务 / CLI 工具 / 库 / 数据/ML / 全栈 / 其他
2. **团队规模**：1人 / 2-5人 / 5-20人 / 20+人
3. **输出范围**：CLAUDE.md / AGENTS.md / .claude/rules/ / settings.json

### 按需追问

4. **核心领域对象**：项目有哪些关键概念？（如 Goal·Task·Approval·Artifact）
5. **特有规则**：有什么是 Agent 容易犯错、必须遵守的硬规则？
6. **设计系统**：项目有设计系统或风格指南吗？具体 token 是什么？
7. **参考项目**：是否有参考项目可以优先复用？
8. **已有配置**：是否已有 CLAUDE.md 或 AGENTS.md？保留还是重写？
9. **部署方式**：Docker / K8s / Serverless / 传统？
10. **测试要求**：覆盖率目标？CI 位置？
