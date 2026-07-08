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
- 发布成功的硬证据是 URL 离开 `/write` 或 `/edit`，并匹配 `https://zhuanlan.zhihu.com/p/{id}`，其中 `{id}` 用 `/p/(\d{15,20})` 正则提取。

## 内容 payload 要求

```yaml
title: 知乎专栏标题
body: 完整正文
media:
  images: 正文图片绝对路径列表
  videos: 正文视频绝对路径列表
  posters: 稳定可读取的海报图片路径列表
render_mode: html|plain_text|platform_native
mode: publish|draft|fill_and_confirm
```

适配规则：

- 适合完整文章、解释型长文、观点论证。
- 保留完整结构和论证层次。
- 标题写入 title 字段，正文不要重复同一个 H1。若正文第一行是 `# <title>` 或与 `title` 高度相似，发布前必须剥掉该 H1，从下一段开始填正文。
- 不要把原始 Markdown 直接填进 Draft.js 编辑器。优先路径是转成知乎编辑器能保留的富文本/HTML 后粘贴；如果当前 OpenCLI 只支持纯文本填入，则把 Markdown 降级成可读纯文本：去掉 H1/H2 标记、`**`、`---` 等控制符，保留段落、列表语义和链接文本。
- 图片和视频都必须按当前知乎编辑器/适配器能力处理；不支持自动插入视频时，按 `已填写待确认` 或让用户人工补视频，不要把本地视频路径直接写进正文。
- `<!-- POSTER:... -->`、脚本临时生成图、本地 `/tmp` 或 `/var/folders/...` 海报路径不能直接用于知乎。海报必须先落盘到稳定目录，或上传到可复用图床/知乎图片 URL 后再插入；否则把图片缺失写入 `adaptation_notes` 并让用户确认纯文本发布或待人工补图。
- 如果浏览器发布卡在 `/edit`，按校验规则回报为 `已填写待确认` 或 `已创建草稿`，不要算已发布。

## 主路径：专栏文章（浏览器自动化）

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

如果页面仍停在 `/edit`、显示 `草稿` 或按钮一直是 `发布中...`，按 `草稿已填写/发布未确认` 上报，**不能算成功**。最多重试一次，不要反复点击。

## Markdown 预处理建议

发布知乎前先生成 `platform_payloads.zhihu` 的正文版本：

1. 从 `source.title` 或正文第一个 H1 提取 `title`。
2. 如果正文第一行 H1 与 `title` 相同或高度相似，删除这一行。
3. 如果能保留富文本，Markdown 先转 HTML，再走支持 HTML/富文本粘贴的流程。
4. 如果只能 `fill` 纯文本，降级为纯文本：删除 Markdown 标题符号、水平线、加粗符号和 HTML 注释；链接保留为 `文本 URL` 或原始 URL。
5. 对 `<!-- POSTER:... -->` 只在图片文件稳定存在且可上传时插入；否则删除标记并在回报里说明缺图。

## 副路径：回答 / 评论

对于问题回答或文章评论，使用对应适配器，并且只在用户明确要求真实写入时才加 `--execute`：

```bash
opencli zhihu answer "<target>" "<content>" --execute -f json
opencli zhihu comment "<target>" "<content>" --execute -f json
```
