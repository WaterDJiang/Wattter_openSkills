# 微博发布流程

> 仅在用户明确点名「微博」或要求「全平台」发布时加载。

## 默认决策

- `platform_payloads.weibo.variant` 默认设为 `short_post`，无论源文是短内容还是长文章。
- 只有用户明确要求「微博长文」「头条文章」「全文发布」「longform」时，才设为 `longform`。
- 不得仅因源文很长、带标题或已有 HTML 就推断用户需要微博长文。
- 默认短帖是公开发布路径；长文是保留能力，不是默认回退。

```text
short_post: opencli_adapter (weibo/publish) -> opencli_ui -> manual_confirm
longform:   opencli_login_adapter (weibo/article-draft) -> opencli_ui_longform -> manual_confirm
```

## 默认短帖内容生成

从原文提炼一份独立、可直接发送的纯文本稿，保存到本次稳定输出目录的 `weibo/body.txt`。稳定输出目录沿用任务的 `publish-output/<run-id>/` 或用户指定目录，不能使用 `/tmp`。不要从 `payloads.md`、执行日志或原始 Markdown 临时截取。

默认生成结构：

1. 一句有判断力的钩子，直接给出核心观点。
2. 2 到 4 个紧凑信息点，保留关键证据、数字或方法。
3. 一个主要 GEO 链接；没有必须露出的链接时，用一句收束或提问结尾。

生成约束：

- 以 250–300 个可见字符作为保守内容预算；这是本 skill 的发布策略，不宣称是平台技术上限。
- 使用自然段或 `1/2/3` 短句，不使用 Markdown H1/H2、`**`、`---`、HTML 注释、代码围栏或原始列表控制符。
- 标题改写成自然首句，不保留 `# 标题`。微博话题 `#话题#` 只用于真实话题标签。
- 链接最多保留一个主 URL，优先官网或 GitHub；其余来源留在源文和 `geo.source_urls`。
- 不机械截取前 300 字。先理解原文，再重写钩子、要点和收束。
- 默认摘要转换已经由本 skill 约定授权，不再单独询问用户；必须保留 `source.content`，并在 `adaptation_notes` 和最终结果中写明「微博摘要短帖」。
- 如果核心观点无法在预算内表达，仍生成最完整的短帖版本；只有用户明确要求保留全文时才切换长文或拆条确认。

推荐 payload：

```yaml
body: 微博短帖纯文本
body_file: /absolute/stable-run-dir/weibo/body.txt
variant: short_post
title: null
media:
  images: []
  videos: []
geo:
  visible_urls: []
  github_urls: []
  source_urls: []
overflow_strategy: summary
render_mode: plain_text
adaptation_notes:
  - 微博摘要短帖
execution:
  fallback_chain: [opencli_adapter, opencli_ui, manual_confirm]
  write_state: not_started
```

## 短帖 Provider 预检

默认调用：

```bash
python3 scripts/provider-preflight.py \
  --platforms weibo \
  --weibo-variant short_post
```

成功预检应选择：

```yaml
variant: short_post
selected_provider: opencli_adapter
selected_command: weibo/publish
```

`weibo/article-draft` 即使已经安装，也不得参与默认短帖候选链。

## 短帖主路径

```bash
opencli weibo whoami -f json
opencli weibo publish "$(< /absolute/stable-run-dir/weibo/body.txt)" -f json
```

如果当前 shell 不适合安全读取文件，先把 `body.txt` 读入受控变量；不要把正文拼进未经检查的命令模板。

### 图片策略

- 微博短帖图片默认可选，不把封面作为发布硬门槛。
- 只有本次已验证图片上传能力可用时才带 `--images`。
- `weibo publish --images` 返回 `Not allowed`、权限拒绝或无法验证图片存在时，不要重复发送同一内容。
- 用户没有声明「必须带图」时，继续发布同一份纯文本摘要；在结果中记录图片未附带。
- 用户明确要求必须带图时，转浏览器上传探测；仍不可校验则停在 `已填写待确认`。

```bash
opencli weibo publish "$(< /absolute/stable-run-dir/weibo/body.txt)" \
  --images /abs/path/to/image.png \
  -f json
```

## 短帖 UI 回退

仅当 `weibo/publish` 明确没有产生写入时使用：

```bash
opencli browser weibo open https://weibo.com --window foreground
opencli browser weibo state
opencli browser weibo fill <textarea-ref> "<short_post_body>"
opencli browser weibo click <send-button-ref>
```

UI 回退必须复用 `weibo/body.txt`，不得重新使用原文。第一次发布状态不明时先对账，不得再次点击发送。

## 短帖校验

```bash
opencli weibo me -f json
opencli weibo user-posts <uid> --limit 3 -f json
```

成功标准：最新帖子正文与 `weibo/body.txt` 一致，且取得真实帖子 URL。最终完成情况写 `已发布：微博摘要短帖`。

## 显式长文分支

只有用户明确要求长文时才运行：

```bash
python3 scripts/provider-preflight.py \
  --platforms weibo \
  --weibo-variant longform

opencli weibo article-draft \
  --title '<title>' \
  --file /abs/article.weibo.html \
  --summary '<summary>' \
  --execute \
  -f json
```

- 长文草稿失败不得自动改成短微博；显式长文任务只能回退到 `card.weibo.com` 长文编辑器或人工确认。
- adapter 返回草稿 ID 只能记 `created_unverified`，必须回读标题、正文首尾、中段关键句、封面和阅读范围。
- 长文编辑器可能沿用旧封面，也可能默认开启「仅粉丝阅读全文」。发布前必须确认旧封面未被带入，并关闭非预期的「仅粉丝阅读全文」。
- 长文封面上传返回 `Not allowed` 时，不重试同一个 file input；保存完整草稿，按 `已创建草稿：待补封面` 回报。
- `WRITE_UNKNOWN` 或调用状态不明时，先查同标题草稿；确认不存在才能进入长文 UI 回退。

## 防重复与回报

- 短帖和长文是两种不同内容形态，不能互相作为静默回退。
- 发布超时、页面不跳转、adapter 响应解析失败时，先按标题指纹、正文开头和执行时间窗口查最近帖子/草稿。
- `overflow_strategy: summary` 必须在 `adaptation_notes` 和最终结果中披露，但不需要再次征求摘要授权。
- 图片、视频和正文分别维护；视频能力以当前 `opencli weibo --help` 为准。
