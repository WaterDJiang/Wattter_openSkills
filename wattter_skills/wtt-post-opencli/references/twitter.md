# Twitter/X 发布流程

> 仅在用户明确点名「Twitter / 推特 / X / x.com」或要求「全平台」发布时加载此文件。

## 关键事实

- 默认只发布短文（short post）。除非用户明确说「长文」「longform」「X Article」「发布文章」，否则不要走长文分支。
- Twitter/X 的账号权限、字数上限、长文/Articles 入口和 OpenCLI 适配器能力都可能随账号和版本变化。遇到长文、媒体或命令参数不确定时，先查当前帮助和页面状态，不要硬猜。
- 执行前必须使用 `references/content-format.md` 生成的 `platform_payloads.twitter`。长内容默认先做短文摘要；任何有损摘要、拆 thread 或长文发布都要让用户确认。
- 如果本机 OpenCLI 只有 `x` 站点而没有 `twitter` 站点，使用当前可用的站点 id 执行，但 payload key 仍统一记为 `twitter`。
- OpenCLI `1.8.6` 实测 Twitter 写入命令是 `post <text>`，不是 `publish`。`article` 是读取 Twitter Article 的命令，不是长文写入命令。
- 长正文可能被当前账号/平台作为单条 long post 发布，也可能由适配器拆成 thread。不要按「长文请求」推断最终形态，必须用返回的 `id/url` 做发布后校验。

## 内容 payload 要求

```yaml
body: Twitter/X 短文正文或长文摘要
media:
  images: 可选图片绝对路径列表
  videos: 可选视频绝对路径列表
links: 可选链接
variant: short_post|longform|article
overflow_strategy: original|summary|thread|longform|ask_user
mode: publish|draft|fill_and_confirm|format_only
```

适配规则：

- `variant` 默认是 `short_post`。短文适合观点、发布通知、摘要、链接导流和轻量 thread 开头。
- 短文默认使用保守长度预算。正文明显过长时，推荐生成「一句钩子 + 2 到 4 个要点 + 链接/出处」的摘要版，并把 `overflow_strategy` 设为 `summary`。
- 用户明确要求保留完整内容但没点名长文时，优先建议拆成 thread；执行前确认条数、顺序和每条内容。
- 用户明确选择长文时，才把 `variant` 设为 `longform` 或 `article`。如果当前 OpenCLI 或账号不支持可校验的长文发布，只能按 `已填写待确认` 或 `未完成` 回报，不能宣称已发布。
- 图片、视频独立放在 `media`。当前适配器不支持某类媒体时，先让用户选择纯文本、改素材、浏览器待确认或跳过。
- 标题通常不写入短文正文；长文/Article 入口如果需要标题，再使用 payload 的 `title` 字段。

## 能力探测

第一次执行 Twitter/X 或遇到 unknown command 时，按当前 OpenCLI 能力选择站点 id：

```bash
opencli twitter --help -f yaml
opencli x --help -f yaml
opencli browser twitter state
opencli browser x state
```

只要其中一个站点 id 可用，后续命令使用可用 id；如果两个都不可用，先说明缺少 Twitter/X 适配器并征得用户确认后再安装或配置。

## 主路径：短文 post 适配器

短文发布优先使用当前可用站点 id 的 `post` 命令。以下示例以 `twitter` 为站点 id；如果实际可用的是 `x`，把命令里的 `twitter` 替换为 `x`：

```bash
opencli twitter whoami -f json
opencli twitter post "<body>" -f json
```

带图片或视频时，先看当前帮助确认参数名：

```bash
opencli twitter post --help
```

不要把本地媒体路径直接拼进正文。适配器不支持媒体上传时，改走浏览器待确认、纯文本或跳过。

## 长文 / Article 分支

仅在用户明确要求长文时执行：

```bash
opencli twitter --help -f yaml
opencli twitter article --help
opencli twitter longform --help
opencli twitter post --help
```

如果当前版本明确提供长文/Article 写入命令，并且能通过列表或 URL 校验，再执行对应命令。否则用 `post` 发送长正文，让适配器和平台决定是 long post 还是 thread：

```bash
opencli twitter post "<body>" -f json
```

如果 `post` 不支持当前长文形态，或发布过程需要人工介入，再使用浏览器写入并停在待确认：

```bash
opencli browser twitter open https://x.com/compose/post --window foreground
opencli browser twitter state
opencli browser twitter find --css "textarea,[contenteditable=true],button" --limit 80 --text-max 120
opencli browser twitter fill <editor-ref> "<body>"
```

长文分支成功标准必须高于「编辑器里有文字」：需要写入命令返回 `id/url`，并且平台读取结果能匹配。否则只能报 `已填写待确认` 或 `未完成`。

## 校验

```bash
opencli twitter whoami -f json
opencli twitter tweets <handle> --limit 5 -f json
opencli twitter thread <tweet-id-or-url> --limit 5 -f json
```

成功标准：

- 写入命令返回 `status: success`、`id` 和 `url`。
- `opencli twitter tweets <handle> --limit 5 -f json` 的最新结果里出现同一个 `id` 或同一个 `url`。
- 读取结果的 `text` 能匹配正文关键片段，链接可能被平台改写成 `t.co`，因此链接校验用 card/domain 或原始 URL 展开信息辅助判断。
- 如果发送的是长正文，再用 `opencli twitter thread <id-or-url> --limit 5 -f json` 判断最终是单条 long post 还是 thread；只要返回内容里有同一个 `id/url` 并匹配正文，即可确认发布。
- `has_media`、`media_urls` 和 `media_posters` 要与 payload 中的媒体预期一致。无媒体发布时，`has_media: false` 是正常结果。

如果发布命令返回成功但 `tweets` 或 `thread` 读取不到同一条内容，按 `未完成` 或 `未确认发布` 上报；不要重复点击或重复发布同一条内容。

## 回退路径：浏览器短文

仅当 `post` 适配器失败但浏览器已登录时使用：

```bash
opencli browser twitter open https://x.com/compose/post --window foreground
opencli browser twitter state
opencli browser twitter find --css "textarea,[contenteditable=true],button" --limit 80 --text-max 120
opencli browser twitter fill <editor-ref> "<body>"
opencli browser twitter click <post-button-ref>
opencli twitter tweets <handle> --limit 5 -f json
```

第一次发布未经验证确认失败前，不要点第二次。浏览器 UI 只填入但未校验公开内容时，回报为 `已填写待确认`。
