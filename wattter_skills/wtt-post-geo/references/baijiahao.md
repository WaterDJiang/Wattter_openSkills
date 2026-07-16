# 百家号草稿流程

> 仅在用户明确点名「百家号 / baijiahao」或要求「全平台」时加载。

## 当前能力基线（2026-07-16）

- OpenCLI `1.8.6` 内置注册表没有百家号 adapter；本 skill 随附 `baijiahao article-draft`。
- adapter 使用 OpenCLI 已有登录 Cookie，动态从百家号编辑页取发布凭证，再创建 HTML 草稿，不需要 CSDN 插件。
- 当前 adapter 不上传本地图片，标记 `experimental`。
- 默认创建草稿；平台审核或公开发布状态必须另行回读。

## 内容 payload

```yaml
title: 百家号文章标题
body: 清洗后的 HTML 正文
media:
  images: []
  videos: []
  posters: []
cover_image: null
render_mode: html
mode: draft|fill_and_confirm|format_only
platform_options:
  article_type: news
  source_reprinted_allow: null
  category: null
execution:
  fallback_chain: [opencli_login_adapter, opencli_ui, manual_confirm]
  write_state: not_started
```

适配要求：

- 标题与正文分离，删除重复 H1。
- HTML 必须移除脚本、iframe、CSDN 编辑器控件、懒加载占位和无效 SVG。
- 表格、引用、公式和代码块按百家号编辑器可读格式转换；转换后必须预览抽样。
- 原创/转载授权、内容分类和声明写入 `platform_options`，没有用户确认不得猜测。
- 本地图片先按 `media-assets.md` 落到稳定路径。本次必须自动上图时跳过 adapter 走 UI。
- 视频能力未验证，不把本地视频路径写进 HTML。

## 分层 Provider 路由

### 主路径：OpenCLI 登录态 adapter

按 [login-state-adapters.md](login-state-adapters.md) 执行：

1. 预检 `baijiahao/article-draft`、OpenCLI 桥接和图片能力。
2. 传入标题和清洗 HTML。分类、转载授权和平台声明仍在草稿编辑页确认。
3. 记录 adapter 返回的 `draft_id/draft_url`，先记为 `created_unverified`。
4. 打开返回的编辑链接，对账账号、标题、正文首尾、中段关键句和图片数。

只有明确没有创建草稿，才能进入 OpenCLI UI 回退。

### 回退：OpenCLI 浏览器编辑器

```bash
opencli doctor
opencli browser baijiahao open https://baijiahao.baidu.com --window foreground
opencli browser baijiahao state
opencli browser baijiahao find --css 'input,textarea,[contenteditable=true],button,input[type=file]' --limit 100 --text-max 100
```

- 先从当前页面进入内容发布/草稿编辑器；不要依赖固定按钮序号。
- 登录账号不明确时停止并让用户确认。
- 标题使用 `data-testid=news-title-input` 下的 contenteditable；正文位于同源 `#ueditor_0` iframe。先把独立 Markdown 转为清洗 HTML fragment，再按 [browser-editor-fallback.md](browser-editor-fallback.md) 使用 `iframe-html` 写入器。
- 写入器返回的可见文本指纹必须匹配；再检查正文开头、结尾和至少一个中段句。不要把完整 HTML document、`style/script/iframe` 写进编辑器。
- 保存使用 `click --role button --name '存草稿'`，不得用历史数字 ref。保存后 URL 应含 `article_id=<id>`；重载同一 URL 后再次回读标题和正文首尾。
- 图片上传后检查缩略图、HTML `img` 或平台托管 URL；无法确认时停在 `manual_asset_ready`。
- 默认保存草稿。公开发布需要用户单独确认平台选项和审核影响。

## 校验与回报

- 草稿列表存在且内容匹配：`已创建草稿`。
- 编辑 URL 含 `article_id` 且重载后正文匹配，也可作为已创建草稿证据。
- 编辑器已填但草稿落库、图片或声明未确认：`已填写待确认`。
- 验证码、风险提醒、登录异常、频控或审核拦截：停止并报告 `未完成`。
- 主路径状态未知时不创建第二份草稿。
