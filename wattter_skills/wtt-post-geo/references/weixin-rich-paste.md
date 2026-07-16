# 微信公众号浏览器富文本粘贴

> 仅在公众号 OpenCLI/API 图片或排版不可靠，或用户要求“先排好版再复制到公众号编辑器”时加载。

## 判断

`opencli weixin create-draft` 适合快速建草稿，但它容易把 Markdown 退化成纯文本，且 `--cover-image` / 正文图片在部分版本会被扩展权限拒绝。公众号需要排版时，优先走浏览器富文本编辑器路径：先把 Markdown 转成微信兼容的内联样式 HTML，再用 OpenCLI 控制浏览器把 HTML 插入公众号编辑器。

这个路径的目标是 `已填写待确认` 或 `已创建草稿/待检查`，不是自动群发。它必须保留排版；如果只得到纯文本，就算文本完整也不能报告“排版完成”。

2026-07-09 实测补充：

- `navigator.clipboard.write(text/html)` 在公众号编辑器上下文可能长时间不返回；不要把它当作唯一可用路径。
- 公众号编辑器可通过内部会话参数进入图文编辑器，可填写 `textarea#title`，正文主编辑器是 `.ProseMirror`。
- `.ProseMirror` 可用 `document.execCommand('insertHTML', false, html)` 插入微信内联 HTML；插入后必须校验开头、结尾、标题层级、Markdown 泄漏和图片占位。
- `opencli browser upload <input[type=file]> /abs/path.png` 对公众号隐藏文件输入返回 `Not allowed`；上传控件失败后可以继续探测“图片写入剪贴板 -> 编辑器 Meta+V 粘贴”。只有粘贴后能在编辑器 DOM / 预览 / 草稿里看到真实 `img`，才可宣称图片已插入；否则本地图片仍按 `manual_asset_ready` 回报。

## 核心依据

- 浏览器 Clipboard API 支持写入 `text/html` 和 PNG；但需要 HTTPS 安全上下文，且可能抛 `NotAllowedError`。
- OpenCLI browser 当前支持 `open`、`find`、`focus`、`eval`、`keys`、`upload`、`extract`、`screenshot`，足够完成“写剪贴板 -> 聚焦编辑器 -> 粘贴 -> 校验”的闭环。
- 本地已有先例：`wtt-post-multi-platform/platforms/zhihu/scripts/zhihu_poster.py` 使用 `navigator.clipboard.write([new ClipboardItem({"text/html": blob})])` 再按 `Meta+V` 粘贴；公众号路径采用同一类机制。

## 一、先排版成微信 HTML

不要把 Markdown 原文直接 `fill` 到公众号编辑器。先生成 `article.wechat.html`：

- H1：只保留标题字段；正文内不要重复同名 H1。
- H2：中性色标题 + 细分隔线；不要使用大面积蓝底。
- H3：中性色标题 + 克莱因蓝左侧细竖线。
- 段落：`line-height:1.8`，`letter-spacing:0.05em`，`text-align:justify`。
- 引用：浅中性底 + 克莱因蓝左边框。
- 行内代码：浅中性底、圆角，不用红色。
- 代码块：浅中性底 + 细边框，长行允许换行。
- 图片：`display:block;margin:1.5em auto;max-width:100%`。
- 链接：保留可读 URL；公众号编辑器是否转成可点击链接以预览为准。

可以参考 `wtt-post-multi-platform/platforms/wechat/scripts/markdown_converter.py` 的内联样式规则，但不要把该 skill 当作本次发布入口。

如果正文图来自本地稳定 PNG，必须在生成微信包时显式传入，而不是只把图片文件放在素材目录：

```bash
python3 scripts/prepare-weixin-rich-html.py /abs/path/article.md \
  --output-dir /abs/path/output/weixin-article \
  --cover-image /abs/path/assets/weixin_cover.png \
  --body-image /abs/path/assets/body_1.png \
  --body-image-title "知识库最小闭环"
```

该脚本会输出：

- `article.wechat.html`：公众号内联样式 HTML。
- `article.plain.txt`：校验和兜底用纯文本。
- `manifest.json`：封面、正文图、占位符和源路径，用于 API 上传替换。

## 二、图片处理策略

正文图片不能只靠 `<img src="file://...">`。分三种：

1. **远程 HTTPS 图片 URL**：可以放入 HTML 后粘贴，但仍要在编辑器里校验图片是否被公众号接收。
2. **本地生成 PNG**：先在 HTML 中放明显占位，例如 `【图 1：流程图】`；API 路径通过 `uploadimg` 换成公众号正文图片 URL；OpenCLI 路径先探测上传控件，再探测剪贴板粘贴图片。
3. **上传/粘贴都不可用**：保持排版正文，回报 `manual_asset_ready`，给出本地图片路径和对应占位位置。

如果页面存在 `input[type=file]`，优先用 OpenCLI 上传：

```bash
opencli browser weixin find --css "input[type=file]" --limit 20 --text-max 80
opencli browser weixin upload <input-ref> /abs/path/to/image.png
opencli browser weixin extract --chunk-size 4000
```

如果上传控件隐藏但按钮可见，先点击图片按钮，再重新 `find` 文件输入框。不要通过随机点击猜控件。若返回 `Not allowed`，不要继续重复上传同一路径，改探测剪贴板图片粘贴。

### 图片复制粘贴探测

公众号网页编辑器通常会把真实剪贴板里的图片当作用户粘贴上传处理。OpenCLI 路径可以用脚本把本地 PNG/JPG/WebP 写入浏览器 Clipboard API，再用 `Meta+V` 粘贴到正文占位处：

```bash
node scripts/weixin-image-clipboard-js.mjs \
  /abs/path/to/body-image.png \
  "【图 1：流程图】" > /tmp/weixin-image-clipboard.js
opencli browser weixin eval "$(cat /tmp/weixin-image-clipboard.js)"
opencli browser weixin keys Meta+V
opencli browser weixin extract --chunk-size 4000
opencli browser weixin screenshot /abs/path/to/weixin-after-image-paste.png
```

脚本会先尝试选中正文中的占位符，再把图片写入浏览器剪贴板。返回值中必须检查：

- `ok: true`：剪贴板写入成功。
- `placeholderMatched: true`：找到了要替换的占位符。
- 粘贴后编辑器 `imgCount` 增加，或 `extract` / 截图能看到图片。

如果 `clipboard_write_timeout`、`NotAllowedError`、粘贴后 `imgCount` 不变、或保存草稿后图片消失，按 `manual_asset_ready` 回报。不要把“图片已写入剪贴板”当作“公众号已接收图片”。

## 三、写入剪贴板并粘贴

先打开公众号编辑器并确认账号：

```bash
opencli browser weixin open https://mp.weixin.qq.com --window foreground
opencli browser weixin state
opencli browser weixin find --css "input,textarea,[contenteditable=true],iframe" --limit 80 --text-max 120
```

如果编辑器在 iframe 中，先用 `frames` 找 frame index，后续 `eval` / `find` / `focus` 带 `--frame <index>`。

默认先使用受控插入脚本，避免手写超长 HTML，也避免 Clipboard API 挂起：

```bash
node scripts/weixin-editor-insert-js.mjs /abs/path/to/article.wechat.html /abs/path/to/article.plain.txt > /tmp/weixin-insert.js
opencli browser weixin eval "$(cat /tmp/weixin-insert.js)"
opencli browser weixin extract --chunk-size 4000
opencli browser weixin screenshot /abs/path/to/weixin-after-insert.png
```

返回值必须至少检查 `ok`、`textLength`、`h2Count`、`h3Count`、`placeholderCount` 和 `markdownLeak`。`markdownLeak: true` 或 `h2Count/h3Count` 全为 0 时，不得报告排版成功。

如果当前环境已经确认 Clipboard API 可用，再尝试把 HTML 写入剪贴板：

```bash
node scripts/weixin-clipboard-js.mjs /abs/path/to/article.wechat.html /abs/path/to/article.plain.txt > /tmp/weixin-clipboard.js
opencli browser weixin eval "$(cat /tmp/weixin-clipboard.js)"
```

聚焦正文编辑器并粘贴：

```bash
opencli browser weixin focus <editor-ref>
opencli browser weixin keys Meta+V
opencli browser weixin extract --chunk-size 4000
opencli browser weixin screenshot /abs/path/to/weixin-after-paste.png
```

macOS 使用 `Meta+V`；Windows/Linux 使用 `Control+V`。

如果 `eval` 返回 `Clipboard API unavailable` 或 `NotAllowedError`，不要退回 `fill` 硬塞 Markdown。改用人工剪贴板、API 草稿箱，或只创建待人工编辑草稿。

如果剪贴板 API 挂起或不可用，继续使用受控插入作为 OpenCLI 富文本兜底：

```bash
opencli browser weixin fill "textarea#title" "<title>"
opencli browser weixin eval "(() => {
  const editor = document.querySelector('.ProseMirror');
  editor.focus();
  const selection = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(editor);
  range.deleteContents();
  selection.removeAllRanges();
  selection.addRange(range);
  const ok = document.execCommand('insertHTML', false, '<微信内联 HTML>');
  editor.dispatchEvent(new Event('change', {bubbles: true}));
  return {ok, textLen: editor.innerText.length, imgCount: editor.querySelectorAll('img').length};
})()"
```

这条路径必须使用脚本生成 JS，避免手写长 HTML。它只证明正文进入编辑器，不证明图片已上传或草稿可发表。

正文 HTML 插入完成后，若正文存在图片占位，按“图片复制粘贴探测”逐张尝试。每张图片最多执行一次剪贴板写入和一次 `Meta+V`；失败后记录证据并保留占位，不要反复粘贴导致重复图片或重复草稿。

## 四、校验

点击保存/草稿前必须校验：

- 标题字段已填写。
- 正文开头、正文结尾、1-2 个中段关键句存在。
- `##`、`**`、`---`、HTML 注释没有字面泄漏。
- H2/H3/引用/列表至少有一种样式在截图或 extract 中可见。
- 图片占位和实际图片数量一致；若已通过剪贴板粘贴成功，必须确认真实 `img` 数量增加且占位被替换或紧邻图片；若未插入图片，回报清楚哪些图片需要人工补。
- 关键链接或 GEO 信息存在。

校验不完整时只能回报 `已填写待确认`，不能宣称公众号草稿已经排版完成。

## 五、失败分支

- `fill` 只作为最后纯文本兜底，不用于正式排版路径。
- 剪贴板写入成功但粘贴后为空：重新 focus 编辑器，按一次 `Meta+A` 清空错误内容后再粘贴；最多一次。
- 粘贴后样式丢失但文本完整：标记为 `已填写待确认/样式需人工检查`。
- 图片上传失败：先探测剪贴板粘贴；粘贴也失败时保留图片路径和占位，不重复上传/粘贴多次。
