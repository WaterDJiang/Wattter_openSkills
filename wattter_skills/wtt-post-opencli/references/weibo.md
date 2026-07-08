# 微博发布流程

> 仅在用户明确点名「微博」或要求「全平台」发布时加载此文件。

## 关键事实（实测）

- 优先使用 write 适配器；失败时回退到已验证的首页 UI 路径。
- UI 回退方案在已登录的网页端可用：填充首页 textarea、点击 `发送`、再用最新用户帖校验。
- 第一次发布未经验证确认失败前，不要点第二次，避免重复发。
- OpenCLI `1.8+` 的 browser 命令需要显式 session 名，例如 `opencli browser weibo state`。
- 执行前必须使用 `references/content-format.md` 生成的 `platform_payloads.weibo`。长文必须先摘要、拆条或让用户确认，不要直接塞入发布命令。

## 内容 payload 要求

```yaml
body: 微博短内容正文
media:
  images: 可选图片绝对路径列表
  videos: 可选视频绝对路径列表
overflow_strategy: original|summary|split|ask_user
```

适配规则：

- 适合短观点、摘要、发布通知、带链接的导流。
- 原文较短时可直接发布。
- 原文较长时，默认建议生成 `摘要发布`：一句钩子 + 3 到 5 个要点 + 链接或出处说明。
- 如果用户要求保留全文，建议 `拆成多条`，并在执行前让用户确认条数和顺序。
- 微博是短内容平台，不要把 Markdown H1、二级标题、`---`、`**` 或 HTML 注释直接塞进正文。长文改成摘要或 thread-like 多条时，先转成可读纯文本。
- 如果原文标题需要保留，改成自然首句或单独话题，不要保留 `# 标题` 这种 Markdown 字面格式；微博话题 `#话题#` 只用于真实话题标签。
- 图片和视频都作为 `media` 独立维护；发布命令是否支持视频要以当前 `weibo` help 为准，不支持时先让用户选择改成图文/纯文本/跳过。
- 如果 `overflow_strategy` 是 `summary` 或 `split`，最终回报要说明微博使用的是摘要版或拆条版。任何有损删减都要先确认。

## 主路径：write 适配器

```bash
opencli weibo whoami -f json
opencli weibo publish "<body>" -f json
```

## 校验：最新帖子

```bash
opencli weibo me -f json
opencli weibo user-posts <uid> --limit 3 -f json
```

成功标准：返回了新帖，或最新帖的文本与请求内容一致。最终回复里附上帖子 URL。

## 回退路径：浏览器 UI

仅当 publish 适配器失败但浏览器已登录时使用：

```bash
opencli browser weibo open https://weibo.com --window foreground
opencli browser weibo state
opencli browser weibo fill <textarea-ref> "<body>"
opencli browser weibo click <send-button-ref>
opencli weibo user-posts <uid> --limit 3 -f json
```

第一次发布未经验证确认失败前，不要点第二次。
