# 知乎发布流程

> 仅在用户明确点名「知乎」或要求「全平台」发布时加载此文件。

## 关键事实（实测）

- 知乎专栏文章主路径是浏览器自动化。知乎有 answer / comment 的 write 适配器，但通用专栏文章不一定有。
- 知乎专栏发布可能卡在 `/edit` 页面显示 `发布中...`；即便草稿内容已写入，也不算发布成功。
- 最多重试一次，反复点击会触发风控。
- OpenCLI `1.8+` 的 browser 命令需要显式 session 名，例如 `opencli browser zhihu state`。
- 执行前必须使用 `references/content-format.md` 生成的 `platform_payloads.zhihu`。标题进入标题字段，正文不要重复同一个 H1。
- 实测写文章编辑器入口是 `https://zhuanlan.zhihu.com/write`，标题控件是 textarea，正文控件是 Draft.js 的 `contenteditable` div（常见 class 包含 `notranslate public-DraftEditor-content`）。
- `opencli browser zhihu fill <editor-ref> "<body>"` 能一次性写入正文，但 Draft.js 不会自动把 Markdown 的 `#`、`##`、`**`、`---` 渲染成富文本。直接填 Markdown 会变成字面文本。
- `.md` 导入 file input 在当前浏览器桥可能返回 `Not allowed`。发生后不要重试上传；继续使用已经准备好的 HTML adapter 或 UI 草稿路径。
- 发布成功的硬证据是 URL 离开 `/write` 或 `/edit`，并匹配 `https://zhuanlan.zhihu.com/p/{id}`，其中 `{id}` 用 `/p/(\d{15,20})` 正则提取。
- 知乎适合保留 GEO 结构：官网、GitHub、来源链接、llms.txt、sitemap 等可以作为“参考与延伸阅读”露出，但必须用知乎可读格式处理。
- 涉及正文图时必须加载 `references/media-assets.md`。优先探测富文本/HTML 粘贴，其次图片上传/粘贴；不通时降级为纯文本文章并回报图片路径。

## 分层 Provider 路由

知乎专栏默认顺序：

```text
opencli_login_adapter (zhihu article-draft)
  -> opencli_ui
  -> manual_confirm
```

- `opencli zhihu article-draft` 使用 OpenCLI 浏览器登录态创建专栏 HTML 草稿，不需要 CSDN 插件。
- adapter 返回的 `draft_id/draft_url` 先记为 `created_unverified`。必须打开 `/p/<id>/edit` 核对标题、正文开头/结尾、关键段落和图片。
- 本次必须自动上传图片时，预检直接跳过当前 adapter 走 UI；adapter 明确未创建草稿时才回退。
- 已有草稿但内容或图片校验失败时修复现有草稿，或停在 `已填写待确认`。
- 知乎回答、评论仍使用对应 OpenCLI adapter，不走专栏长文 provider。

## 内容 payload 要求

```yaml
title: 知乎专栏标题
body: 完整正文
media:
  images: 正文图片绝对路径列表
  videos: 正文视频绝对路径列表
  posters: 稳定可读取的海报图片路径列表
media_plan:
  image_delivery:
    method: api_upload|browser_upload|browser_paste|manual_asset_ready|unsupported
geo:
  visible_urls: []
  github_urls: []
  source_urls: []
  citation_notes: []
  llms_txt_url: null
  sitemap_url: null
render_mode: html|plain_text|platform_native
mode: publish|draft|fill_and_confirm
execution:
  fallback_chain: [opencli_login_adapter, opencli_ui, manual_confirm]
  write_state: not_started
```

适配规则：

- 适合完整文章、解释型长文、观点论证。
- 保留完整结构和论证层次。
- 标题写入 title 字段，正文不要重复同一个 H1。若正文第一行是 `# <title>` 或与 `title` 高度相似，发布前必须剥掉该 H1，从下一段开始填正文。
- 不要把原始 Markdown 直接填进 Draft.js 编辑器。优先路径是转成知乎编辑器能保留的富文本/HTML 后粘贴；如果当前 OpenCLI 只支持纯文本填入，则把 Markdown 降级成可读纯文本：去掉 H1/H2 标记、`**`、`---` 等控制符，保留段落、列表语义和链接文本。
- 图片和视频都必须按当前知乎编辑器/适配器能力处理；不支持自动插入视频时，按 `已填写待确认` 或让用户人工补视频，不要把本地视频路径直接写进正文。
- `<!-- POSTER:... -->`、脚本临时生成图、本地 `/tmp` 或 `/var/folders/...` 海报路径不能直接用于知乎。海报必须先落盘到稳定目录，或上传到可复用图床/知乎图片 URL 后再插入；否则把图片缺失写入 `adaptation_notes` 并让用户确认纯文本发布或待人工补图。
- GEO 链接推荐在正文末尾用纯文本可读格式：`项目地址：URL`、`GitHub：URL`、`参考资料：标题 URL`。不要在 Draft.js 纯文本模式下依赖 Markdown 链接语法。
- 如果浏览器发布卡在 `/edit`，按校验规则回报为 `已填写待确认` 或 `已创建草稿`，不要算已发布。

## 主路径：登录态草稿 adapter

```bash
opencli zhihu article-draft \
  --title '<title>' \
  --file /abs/article.zhihu.html \
  --execute \
  -f json
```

命令返回的 `draft_id/draft_url` 先记为 `created_unverified`，再打开 `/p/<id>/edit` 完成目标平台回读。

## 回退：专栏文章浏览器自动化

```bash
opencli zhihu whoami -f json
opencli browser zhihu open https://zhuanlan.zhihu.com/write --window foreground
opencli browser zhihu state
opencli browser zhihu find --css "textarea,[contenteditable=true]" --limit 40 --text-max 80
opencli browser zhihu fill <title-ref> "<title>"
opencli browser zhihu fill <editor-ref> "<body>"
opencli browser zhihu extract --chunk-size 4000
opencli browser zhihu find --css "button" --limit 80 --text-max 80
opencli browser zhihu click <publish-button-ref>
opencli browser zhihu get url
```

控件识别：

- 标题通常是占位文本包含 `请输入标题（最多 100 个字）` 的 textarea。
- 正文通常是 `contenteditable=true` 的 Draft.js div，class 常包含 `notranslate public-DraftEditor-content`。
- 发布按钮通常是 `Button Button--primary Button--blue`，按钮文本包含 `发布`。不要只按按钮序号硬点，先用文本或 class 过滤确认。

### 富文本与图片粘贴探测

如果正文包含图片或需要保留较好层次，优先探测编辑器是否支持 HTML/富文本粘贴：

1. 将 Markdown 转为简洁 HTML，图片使用稳定本地路径或可访问 URL。
2. 使用浏览器剪贴板/页面 evaluate 粘贴 HTML 到 Draft.js 编辑器。
3. 用 `extract` 或 DOM 检查标题、正文层级、图片节点/占位是否存在。
4. 成功后再点击发布；失败则转纯文本正文。

如果图片无法自动插入，不要把本地图片路径写进正文。按 `manual_asset_ready` 回报图片路径，或让用户确认纯文本发布。

### 校验

```bash
opencli browser zhihu extract --chunk-size 4000
opencli browser zhihu get url
opencli browser zhihu extract --chunk-size 4000
```

成功标准：

- 填写后、点击发布前，`extract` 能读到标题、正文开头、正文结尾、关键链接和 1 到 2 个中段关键句。缺任何一项都不要点击发布，先按 `已填写待确认` 或修正 payload 处理。
- 点击发布后 URL 离开 `/write` 和 `/edit`。
- URL 匹配 `/p/(\d{15,20})`，能提取知乎专栏文章 id。URL 带 query string 或 redirect 时也必须先正则提取再判断。
- 发布后页面 `extract` 能匹配标题和正文关键片段。
- 公开页正文优先从 `.RichText.ztext.Post-RichText` 或最小的正文容器回读，不要对包含作者、广告、评论和热榜的整页节点计算正文指纹。
- 填写前后可使用长度/指纹校验；公开页富文本会引入不可见字符时，至少核对标题、首段、末句和 1～2 个中段关键句。

如果页面仍停在 `/edit`、显示 `草稿` 或按钮一直是 `发布中...`，按 `草稿已填写/发布未确认` 上报，**不能算成功**。最多重试一次，不要反复点击。

## Markdown 预处理建议

发布知乎前先生成 `platform_payloads.zhihu` 的正文版本：

1. 从 `source.title` 或正文第一个 H1 提取 `title`。
2. 如果正文第一行 H1 与 `title` 相同或高度相似，删除这一行。
3. 如果能保留富文本，Markdown 先转 HTML，再走支持 HTML/富文本粘贴的流程。
4. 如果只能 `fill` 纯文本，降级为纯文本：删除 Markdown 标题符号、水平线、加粗符号和 HTML 注释；链接保留为 `文本 URL` 或原始 URL。
5. 对 `<!-- POSTER:... -->` 只在图片文件稳定存在且可上传时插入；否则删除标记并在回报里说明缺图。

纯文本降级时，章节标题不要直接写成 `## 标题`，改用：

```text
『章节标题』

正文段落...
```

这样即使 Draft.js 不渲染 Markdown，读者仍能看到层级。

## 副路径：回答 / 评论

对于问题回答或文章评论，使用对应适配器，并且只在用户明确要求真实写入时才加 `--execute`：

```bash
opencli zhihu answer "<target>" "<content>" --execute -f json
opencli zhihu comment "<target>" "<content>" --execute -f json
```
