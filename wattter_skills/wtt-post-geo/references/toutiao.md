# 今日头条号草稿流程

> 仅在用户明确点名「今日头条号 / 头条号 / toutiao」或要求「全平台」时加载。

## 当前能力基线（2026-07-21）

- 今日头条号**没有可用的全文 HTTP 写入 API**。按分层路由原则，正确地以 `opencli_ui`（浏览器编辑器）为首选，不为本平台凭空构造 provider。
- 登录检查用 `mp.toutiao.com` 会话 Cookie（`sessionid`）+ 请求原生图文编辑页判断；跳转登录页、验证码或手机号界面时判定未登录。
- 正文使用针对头条号清洗过的 HTML，标题限制 30 个 Unicode 字符。
- 正文图优先走头条号原生图片上传取得托管 URL，再写入图文编辑器；封面只有用户显式提供时才上传。
- 默认目标是 `draft`，只点「存草稿/保存草稿」或等待平台自动保存，**不点击「预览并发布」「定时发布」「发布」**。

## 内容 payload

```yaml
title: 头条号文章标题（≤30 Unicode 字符）
body: 独立 HTML 正文
media:
  images: []
  videos: []
  posters: []
cover_image: null
render_mode: html
mode: draft|fill_and_confirm|format_only
platform_options: {}
execution:
  fallback_chain: [opencli_ui, manual_confirm]
  write_state: not_started
```

适配要求：

- 标题与正文分离，剥掉重复 H1。
- 写作语气与链接方式遵循 [content-style.md](content-style.md) 的去营销化清单（禁绝对化卖货词/标题党、链接自然化、移除硬 CTA；通用，不在此重复）。
- 保留标题、段落、列表、引用、代码与图片语义；移除危险标签与不兼容属性。
- 本地图片必须先形成稳定资产与上传计划；头条号正文图走编辑器原生图片入口逐张插入。
- 普通正文首图不得被误当封面；只有统一文章模型中的显式 `cover` 才进入封面上传。

## 分层 Provider 路由

### 主路径：OpenCLI 浏览器编辑器

头条号没有官方写 API，也没有本 skill 随附的登录态 adapter。直接走原生图文编辑器：

```bash
opencli doctor
opencli browser toutiao open https://mp.toutiao.com/profile_v4/graphic/publish --window foreground
opencli browser toutiao state
opencli browser toutiao find --css 'input,textarea,[contenteditable=true],button,input[type=file]' --limit 80 --text-max 100
```

- URL 跳转 `/auth/`、登录页或验证码时停止，让用户登录或处理风控。
- 先识别标题（`input[placeholder*="标题"],textarea[placeholder*="标题"]`）与正文（`.ProseMirror[contenteditable="true"]` 等），不按旧序号盲点。
- 正文图：头条号工具栏的图片按钮是 SVG 图标（含 `circle` + 特定 `rect`）；点击后等待 `.mp-ic-img-drawer,.pgc-ic-image-tab-scope input[type=file][accept*=image][multiple]`，一次上传全部正文图，再轮询正文 `<img src>` 出现托管 URL，按别名替换。
- 正文 HTML 用 `document.execCommand('insertHTML')` 或 [browser-editor-fallback.md](browser-editor-fallback.md) 的 contenteditable 写入器覆盖式写入。
- 封面：语义查找 `input[type=file]`（id/name/class/aria-label 含 `封面|cover|thumbnail`），或点 `.article-cover-add` 等待 `.byte-drawer .upload-image-panel input[type=file]`。
- 只点「存草稿/保存草稿/暂存」按钮；页面显示「草稿将自动保存」时等待自动保存再进入草稿箱回读。禁止点「预览」「定时发布」「发布」。
- 取得草稿 ID：从保存后 URL 的 `pgc_id` 或 `draft_id` 参数、或 `/edit/<id>`、`/draft/<id>` 路径解析。

### 回退：人工确认

编辑器结构漂移、登录异常或风控拦截时，按 `已填写待确认` 或 `未完成` 回报，说明需要用户在平台侧处理。

## 校验与回报

- 保存后重载草稿地址，回读标题、正文首尾与正文图片数。
- 若只到草稿列表，先精确匹配标题与封面，点该卡片唯一的「编辑」进入 `graphic/publish?pgc_id=<id>` 编辑页，再次回读标题、正文与正文图。
- `已创建草稿`：草稿列表/编辑 URL 存在，标题与正文关键片段、图片数匹配。
- `已填写待确认`：编辑器内容已写入，但封面、图片或草稿落库未确认。
- `未完成`：登录、风控、写入或校验失败。状态无法确认时返回失败，不重复创建草稿。
