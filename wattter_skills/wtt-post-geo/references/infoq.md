# InfoQ 草稿流程

> 仅在用户明确点名「InfoQ / infoq」或要求「全平台」时加载。

## 当前能力基线（2026-07-21）

- InfoQ 有**干净的 HTTP 草稿创建端点**（`POST https://xie.infoq.cn/api/v1/draft/create` → `data.id`），但**正文写入仍依赖编辑器**（`.gk-editor` ProseMirror + 平台自动保存），没有全文 HTTP 写入 API。
- 因此 InfoQ 不随附「一次写正文」的登录态 adapter（不符合现有 adapter 契约）。HTTP 创建端点记录在此，供未来 adapter 或「建容器→编辑器写正文」两阶段流程使用。
- 按分层路由原则，InfoQ 当前以 `opencli_ui`（浏览器编辑器）为首选。
- 登录检查 `POST https://www.infoq.cn/public/v1/user/get_user`：`code === 0` 且有 `data.uid` 为已登录；同时要求 `data.is_author >= 2` 才具备创作者权限，单纯登录不足。
- 默认目标是 `draft`，**不点击公开发布**。

## 内容 payload

```yaml
title: InfoQ 文章标题
body: 独立 Markdown 正文
media:
  images: []
  videos: []
  posters: []
cover_image: null
render_mode: markdown
mode: draft|fill_and_confirm|format_only
platform_options: {}
execution:
  fallback_chain: [opencli_ui, manual_confirm]
  write_state: not_started
```

适配要求：

- 标题与正文分离，剥掉重复 H1；保留标准 Markdown。
- 写作语气与链接方式遵循 [content-style.md](content-style.md) 的去营销化清单（禁绝对化卖货词/标题党、链接自然化、移除硬 CTA；通用，不在此重复）。
- 正文图可随 Markdown 一起经 InfoQ 原生 `.md` 导入入口转存（把图片以 `data:` URI 别名预注入 Markdown，InfoQ 导入器负责上传）。
- 创作者权限未开通（`is_author < 2` 或页面出现「申请入驻」）时直接阻塞，提示用户先完成入驻。

## 分层 Provider 路由

### 主路径：OpenCLI 浏览器编辑器

```bash
opencli doctor
opencli browser infoq open https://xie.infoq.cn/draft/<draftId> --window foreground
opencli browser infoq state
opencli browser infoq find --css 'input,textarea,[contenteditable=true],button,input[type=file]' --limit 80 --text-max 100
```

草稿容器可由代码层创建（端点见上），或直接打开编辑器新建。正文写入：

- 标题写入 `input[placeholder*="标题"], .title-input input, input.article-title`（原生 setter + InputEvent）。
- 正文优先经 `.gk-editor` 的 ProseMirror `editorAPI.editor.view` 清空后，查找 `input[type=file][accept=.md]`：把整篇 Markdown 打包成 `File` 经 `DataTransfer` 赋值并派发 `change`，由 InfoQ 原生导入器解析并转存内嵌图片。
- 没有 `.md` 导入入口时，降级 `document.execCommand('insertText')` 写纯文本（此路径不支持图片；需要图时必须回到 `.md` 导入）。
- 依赖平台自动保存：轮询页面「已保存/保存成功」文案 + 正文托管图片数。

Vue 实例路径或 ProseMirror view 结构变化属于上线微调项，不视为缺陷；选择器漂移时用 [browser-editor-fallback.md](browser-editor-fallback.md) 的 contenteditable 写入器。

### 回退：人工确认

编辑器结构漂移、创作者权限缺失、登录异常或风控时，按 `已填写待确认` 或 `未完成` 回报。

## 校验与回报

- 重载同一 draftId，回读标题、正文首尾（去掉 Markdown 控制符后比较）与图片节点数。
- `已创建草稿`：草稿 URL 存在，标题与正文关键片段、图片数匹配。
- `已填写待确认`：编辑器已写入，但自动保存或图片转存未确认。
- `未完成`：登录、风控、写入或校验失败。状态无法确认时返回失败，不重复创建草稿。
