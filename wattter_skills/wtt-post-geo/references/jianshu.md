# 简书草稿流程

> 仅在用户明确点名「简书 / jianshu」或要求「全平台」时加载。

## 当前能力基线（2026-07-21）

- 简书**没有可用的全文 HTTP 写入 API**。草稿容器的 HTTP 创建端点（`POST /author/notes`）必须从**页面同源**发起——service-worker / OpenCLI 纯 `fetch` 会被简书协商成 HTML 响应导致空笔记无法创建。本 skill 当前不随附简书的登录态 adapter。
- 按分层路由原则，简书正确地以 `opencli_ui`（浏览器编辑器）为首选。
- 登录检查 `GET https://www.jianshu.com/settings/basic.json`，缺少 `data.data.nickname` 时判定未登录。
- 标题与正文写入简书 writer 原生编辑器（Kalamu），依赖平台自动保存，再 `GET /author/notes/<id>/content` 服务端回读。
- 默认目标是 `draft`，**不点击公开发布**。

## 内容 payload

```yaml
title: 简书文章标题
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
- 用户没有文集时提示「请先在简书创建一个文集」，不得自动创建文集。
- 本地图片必须先形成稳定资产；正文图走简书 writer 原生 `editor.exec('insertImgs')`。

## 分层 Provider 路由

### 主路径：OpenCLI 浏览器编辑器

```bash
opencli doctor
opencli browser jianshu open https://www.jianshu.com/writer --window foreground
opencli browser jianshu state
opencli browser jianshu find --css 'input,textarea,[contenteditable=true],button,input[type=file]' --limit 80 --text-max 100
```

容器创建的两步必须在页面主世界同源执行（OpenCLI 纯 fetch 不行）：

1. 在 writer 页面内 `GET /author/notebooks`（`Accept: application/json`）取首个文集 ID。
2. 以 `Accept: application/json`、`Content-Type: application/json` 请求 `POST /author/notes`（`{notebook_id, title, at_bottom:false}`）取得 noteId；返回 HTML、登录页或缺少 noteId 时明确失败，不尝试写正文。
3. 切换到 `https://www.jianshu.com/writer#/notebooks/<nb>/notes/<noteId>` 后**完整重载一次**，等新笔记载入前端实体缓存再查找标题/正文/编辑器。

正文写入：

- 标题写入 `input._24i7u`（哈希类名，配 `input[class*="title"]`、`input[placeholder*="标题"]` 语义回退）。
- 富文本模式经页面暴露的 `Symbol(jianshu_editor)` 原生 Kalamu 实例更新 `.kalamu-area`：调用 `updateNote(noteId, title, content)` 后**必须**用 `GET /author/notes/<noteId>/content` 回读服务端正文；只改 DOM、等 `updateNote` 返回值或复用「已保存」文案都不得判定成功。
- 简书 `props.updateNote` 是 Redux dispatch，返回 action 而非网络保存 Promise；不得对其返回值 `await` 当完成证据。
- 图片必须两阶段保存：先移除全部 `<img>` 写纯文本正文并 `updateNote`，轮询服务端正文文本匹配；成功后才 `editor.exec('insertImgs', { images: [{ file }] })`，等 `.image-package` 托管图数达标、`isUploadingImage()` 返回 false 且无 `.upload-error-msg`；再把封面作首图、正文图按原顺序替换回完整 HTML，第二次 `updateNote` 并回读。
- 自动保存后重载同一 noteId，回读标题、正文首尾、托管图片数量和首图。

### 回退：人工确认

编辑器结构漂移、`window[*jianshu_editor*]` 全局缺失、登录异常或风控时，按 `已填写待确认` 或 `未完成` 回报。

## 校验与回报

- `已创建草稿`：`GET /author/notes/<id>/content` 服务端正文匹配，重载后标题、正文首尾、图片数一致。
- `已填写待确认`：编辑器已写入，但服务端回读未确认。
- `未完成`：登录、风控、写入或校验失败。图片阶段失败时返回失败和半成品草稿链接，但草稿必须保留第一阶段已保存的文本正文。
