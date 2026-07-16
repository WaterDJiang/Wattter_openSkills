# 掘金草稿流程

> 仅在用户明确点名「掘金 / juejin」或要求「全平台」时加载。

## 当前能力基线（2026-07-16）

- OpenCLI `1.8.6` 内置注册表只有 `juejin hot`、`juejin recommend`；本 skill 随附 `juejin article-draft` 登录态写 adapter。
- adapter 使用 OpenCLI Chrome 桥接的已有 Cookie 和动态 CSRF token 创建 Markdown 草稿，不需要 CSDN 插件。
- 当前 adapter 支持分类、标签和已托管封面 URL，不上传本地图片，标记 `experimental`。
- 默认目标是 `draft`。没有公开文章 URL 和正文回读证据时不得报告 `已发布`。

## 内容 payload

```yaml
title: 掘金文章标题
body: 独立 Markdown 正文
media:
  images: []
  videos: []
  posters: []
cover_image: null
tags: []
render_mode: markdown
mode: draft|fill_and_confirm|format_only
platform_options:
  category_id: null
  tag_ids: []
execution:
  fallback_chain: [opencli_login_adapter, opencli_ui, manual_confirm]
  write_state: not_started
```

适配要求：

- 标题与正文分离，剥掉重复 H1。
- 保留 Markdown 标题、列表、引用、代码块、表格和普通链接。
- 删除 CSDN 编辑器 UI、隐藏代码按钮、iframe、视频占位和不可复用脚本。
- 分类和标签是平台专属字段。账号中不存在的分类/标签不得猜测或自动创建。
- 本地图片必须先形成稳定资产与上传计划；本次必须自动上图时跳过 adapter 走 UI。
- 视频能力未验证，默认 `unsupported` 或 `manual_asset_ready`。

## 分层 Provider 路由

### 主路径：OpenCLI 登录态 adapter

按 [login-state-adapters.md](login-state-adapters.md) 执行：

1. 预检 `juejin/article-draft`、OpenCLI 桥接和图片能力。
2. 传入独立 Markdown、标题、摘要、`category-id`、`tag-ids` 和可选的已托管封面 URL。
3. 记录 adapter 返回的 `draft_id/draft_url`，先标记 `created_unverified`。
4. 打开 `/editor/drafts/<id>`，核对标题、正文首尾、代码块、关键链接、分类/标签和图片。
5. 验证通过后设置 `created_verified`，报告 `已创建草稿`。

adapter 明确失败且草稿列表确认没有同标题新草稿时，才设置 `confirmed_not_created` 并进入回退。

### 回退：OpenCLI 浏览器编辑器

登录态 adapter 不可用、缺图片能力或明确未创建草稿时，使用原生编辑器：

```bash
opencli doctor
opencli browser juejin open https://juejin.cn/editor/drafts/new --window foreground
opencli browser juejin state
opencli browser juejin find --css 'input,textarea,[contenteditable=true],button,input[type=file]' --limit 80 --text-max 100
```

- URL 跳转登录页时停止，让用户登录。
- 先识别标题、Markdown 编辑器、分类、标签、封面和保存草稿控件，不按旧序号盲点。
- 掘金 Markdown 编辑器是 CodeMirror 5。隐藏 textarea 的 `get value` 可能为空，`fill` 可能返回 `verified: false`，但正文已经写入。此时先读取 `document.querySelector('.CodeMirror')?.CodeMirror?.getValue()`，不得直接追加 `type`。
- 多段 Markdown 使用 [browser-editor-fallback.md](browser-editor-fallback.md) 的 `codemirror5` 写入器覆盖式 `setValue()`，比较独立正文文件与 CodeMirror 内部值的长度/指纹。
- 自动保存后取得 `/editor/drafts/<id>`，等待保存并重载同一 URL；标题、正文长度和指纹仍匹配才算 `created_verified`。
- 如果历史错误操作导致正文重复，先用 CodeMirror `setValue('')` 清空，再只执行一次通用写入器；不要用多次退格或追加写入修复。
- 图片上传后必须出现平台托管 URL 或真实图片节点；失败时标记 `manual_asset_ready`，不静默删图。
- 只保存草稿，不点击公开发布，除非用户明确要求且发布字段已经确认。

## 校验与回报

- `已创建草稿`：草稿列表/编辑 URL 存在，标题与正文关键片段匹配。
- `已填写待确认`：编辑器内容已写入，但分类、标签、图片或草稿落库未确认。
- `未完成`：登录、风控、写入或校验失败。
- adapter 状态未知时先对账；不得用浏览器再创建一份同标题草稿。
