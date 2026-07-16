# 微信公众号（公众号）发布流程

> 仅在用户明确点名「公众号」或要求「全平台」发布时加载此文件。

## 关键事实（实测）

- 公众号要稳定跑通“标题 + 正文排版 + 封面 + 正文图”，默认必须优先走 API 草稿箱：需要用户提供公众号 `appid` / `appsecret`、可用 access token 或配置文件，并且调用机器 IP 已加入微信公众平台白名单。
- 如果 API 配置缺失、白名单不通、素材上传失败或用户不想配置 API，再回退到 OpenCLI 浏览器填充或 `weixin` 适配器**创建草稿**；此时不能承诺自动补图。
- OpenCLI `weixin create-draft` 只创建草稿，并不会直接推送给关注者；它不是公众号富文本排版路径。
- 纯文本草稿可能被标记为 `图文内容不完整`，需要补封面图 / 标题 / 正文才能发表。
- 当前 OpenCLI 图片参数能力需要谨慎：`create-draft --cover-image` 在部分版本会因浏览器扩展权限返回 `Not allowed`。命令上传失败后不要反复重试同一参数，转入剪贴板图片粘贴探测、API 素材上传或人工补图。
- OpenCLI `fill` 或 `create-draft` 对 Markdown 排版不可靠：容易把 `##`、`**`、代码块、表格和图片退化成纯文本。需要排版时必须加载 `references/weixin-rich-paste.md`，先转微信内联样式 HTML，再通过 API 或浏览器编辑器插入。
- 2026-07-09 实测：OpenCLI 浏览器可进入公众号编辑器、填标题、用 ProseMirror `insertHTML` 插入富文本正文；但 `navigator.clipboard.write(text/html)` 可能挂起，`opencli browser upload` 对公众号隐藏 `input[type=file]` 返回 `Not allowed`。因此 OpenCLI 路径默认只能报 `已填写待确认` 或 `manual_asset_ready`，除非剪贴板粘贴图片探测后能在编辑器/草稿中确认真实图片。
- 2026-07-10 实测：OpenCLI 浏览器富文本正文可保存到草稿箱；页面含多个 `.ProseMirror`，插入脚本必须优先选择正文主编辑器，否则会污染标题字段。`create-draft --cover-image` 与 `browser upload` 仍返回 `Not allowed`。
- OpenCLI 如果落到了小程序号而不是公众号后台，需要用浏览器切号。
- 切号时若列表只显示 `gh_...` id、看不到名称，要么把可选项列给用户，要么用用户指定的账号。
- 执行前必须使用 `references/content-format.md` 生成的 `platform_payloads.weixin`，不要直接拿原始正文创建草稿。
- 涉及封面、正文图或海报时，必须加载 `references/media-assets.md`，优先把图片生成/整理到稳定目录。

## 分层 Provider 路由

公众号草稿默认顺序：

```text
official_api
  -> opencli_adapter (weixin create-draft)
  -> opencli_ui (富文本编辑器)
  -> manual_confirm
```

- `official_api`：配置、白名单和素材上传可用时优先，格式与图片闭环最好。
- `opencli_adapter`：当前 `weixin create-draft` 是 `COOKIE` 草稿 adapter，可作为低成本回退；如果正文富文本或图片不能保真，不得把返回 ID 当成完整图文成功。
- `opencli_ui`：按 `weixin-rich-paste.md` 写入现有编辑器；无法确认图片时停在 `已填写待确认`。
- API/adapter 超时或断连时先运行 `opencli weixin drafts -f json`。只有确认没有同标题草稿，才能进入下一 provider。
- 已有草稿但缺封面、缺正文图或排版异常时修复该草稿，不创建第二份。

## 内容 payload 要求

```yaml
title: 公众号草稿标题
body: 完整正文
media:
  images: 正文图片绝对路径列表
  videos: 正文视频绝对路径列表
cover_image: /abs/path/to/cover.png/or/null
media_plan:
  image_delivery:
    method: api_upload|browser_upload|browser_paste|command_upload|manual_asset_ready
geo:
  visible_urls: []
  github_urls: []
  source_urls: []
mode: draft
execution:
  fallback_chain: [official_api, opencli_adapter, opencli_ui, manual_confirm]
  write_state: not_started
```

适配规则：

- 适合完整文章、草稿沉淀、需要后续人工检查的图文内容。
- 默认创建草稿，不宣称已发表。
- 保留完整正文结构，但不要把 Markdown 原文直接写入公众号。正式排版路径必须先转为微信兼容 HTML；只有纯文本兜底才允许降级。
- 公众号正文必须从源 Markdown 或平台正文独立文件生成，不能从 `payloads.md`、发布计划、日志片段里截取；否则 YAML、说明文字、代码围栏会混入正文。
- 如果正文第一行是与 `title` 相同的 H1，优先剥掉 H1，避免公众号草稿标题和正文标题重复。除非用户明确希望正文内保留同名标题。
- Markdown、HTML、图片在公众号草稿里的实际呈现必须以 `drafts` 或后台预览为准；如果适配器只创建纯文本草稿，要在最终回报里说明富文本样式可能需要人工调整。
- 没有封面图时可以继续创建草稿，但最终回报必须提示可能被标记为 `图文内容不完整`，需要用户在公众号后台补封面后才能发表。
- 封面图、海报图和正文图片必须来自稳定路径。不要引用脚本临时目录、已清理的海报文件或不可访问路径。
- 公众号封面默认生成或要求 `900x383`；正文信息图默认 `1920x1080`。如果只有 16:9 封面图，先生成 2.35:1 版本或提示需要裁剪。
- GEO 信息可以放在文末“参考资料/延伸阅读”：官网、GitHub、原文链接、llms.txt 或 sitemap。不要堆砌过多裸链；保留对读者有用的 1-5 条。
- 如果用户提供视频，先检查当前 `weixin` 适配器是否支持视频上传或视频素材引用；不支持时不要把视频路径塞进正文，按 `已创建草稿/待人工补视频` 或 `未完成` 回报。
- 如果用户要求直接发表，先说明当前主路径只创建草稿，除非当前适配器明确支持发表且校验可闭环。

## 主路径 A：API 草稿箱（配置可用时优先）

API 路径适合需要封面、正文图和 HTML 排版的公众号文章。只有在配置完整且白名单可用时才执行；否则不要硬造 API 请求。

前置条件：

- 公众号 `appid`、`appsecret` 或已有 access token。
- 当前调用机器 IP 已在微信公众平台 IP 白名单。
- 封面图已上传为永久素材并得到 `thumb_media_id`。
- 正文图片已上传到微信素材或可用于公众号正文的图片 URL。
- HTML 内容已转换为公众号可接受的内联样式。

执行原则：

- 可参考 `wtt-post-multi-platform` 的 HTML 生图与公众号 HTML 转换思路，但本 skill 的发布状态仍必须自己校验。
- 默认使用本 skill 自带脚本创建 API 草稿：

```bash
python3 scripts/prepare-weixin-rich-html.py /abs/path/article.md --output-dir /abs/path/output/weixin-article
python3 scripts/weixin_api_draft.py \
  --config /abs/path/weixin-config.json \
  --title "$(cat /abs/path/output/weixin-article/title.txt)" \
  --html /abs/path/output/weixin-article/article.wechat.html \
  --cover-image /abs/path/output/weixin-article/poster_cover_xxx.png \
  --manifest /abs/path/output/weixin-article/manifest.json
```

如果封面图或正文图是外部生成的稳定 PNG，先显式挂入微信包，避免只生成了图片却没有进入正文替换清单：

```bash
python3 scripts/prepare-weixin-rich-html.py /abs/path/article.md \
  --output-dir /abs/path/output/weixin-article \
  --cover-image /abs/path/assets/weixin_cover.png \
  --body-image /abs/path/assets/body_1.png \
  --body-image-title "知识库最小闭环"
python3 scripts/weixin_api_draft.py \
  --config /abs/path/weixin-config.json \
  --title "$(cat /abs/path/output/weixin-article/title.txt)" \
  --html /abs/path/output/weixin-article/article.wechat.html \
  --cover-image /abs/path/assets/weixin_cover.png \
  --manifest /abs/path/output/weixin-article/manifest.json
```

`weixin-config.json` 只放本地，不提交到仓库。格式：

```json
{
  "appid": "公众号 appid",
  "appsecret": "公众号 appsecret",
  "author": "可选作者名"
}
```

也可以传已有 `access_token`：

```json
{
  "access_token": "已有 token",
  "author": "可选作者名"
}
```

- `scripts/weixin_api_draft.py` 会把 manifest 中的本地正文图先通过 `uploadimg` 换成公众号正文图片 URL；也会扫描 HTML 里已有的本地 `<img src="/abs/path.png">` 或 `data:image/...` 并替换为微信 URL；再把封面图上传为 `thumb_media_id`，最后调用草稿箱创建草稿。
- API 返回草稿 media_id 后，仍要通过草稿列表、后台预览或 API 返回值确认标题、正文、封面和关键链接。
- API 配置缺失、白名单失败、素材上传失败时，回退到 OpenCLI 草稿，不要把 API 失败报告成发布成功。

## 主路径 B：OpenCLI 浏览器富文本粘贴（API 不通时优先）

如果 API 不可用，但需要保留排版、代码块、表格或引用样式，使用 [weixin-rich-paste.md](weixin-rich-paste.md)。注意：当前 OpenCLI 路径不保证本地图片自动上传，正文图和封面默认按 `manual_asset_ready` 回报。

1. Markdown 转微信内联样式 HTML，生成 `article.wechat.html` 和 `article.plain.txt`。
2. 打开公众号后台图文编辑器，确认当前账号是目标公众号。
3. 优先用 `scripts/weixin-editor-insert-js.mjs` 生成受控插入脚本，通过 ProseMirror `insertHTML` 写入内联 HTML；如果当前环境确认 Clipboard API 可用，再用 `scripts/weixin-clipboard-js.mjs` 剪贴板粘贴。不要退回 Markdown `fill`。
4. 对本地图片，正文中保留 `【图 n：标题】` 占位，并把 PNG 路径写入回报；先尝试 `browser upload`，若返回 `Not allowed`，再用 `scripts/weixin-image-clipboard-js.mjs` 把图片写入剪贴板并 `Meta+V` 粘贴。只有粘贴后能校验真实 `img`，才替换为真实图片。
5. 用编辑器 DOM / `extract` / `screenshot` 校验正文开头、结尾、标题层级、关键链接和图片占位，再保存草稿或停在待确认。

成功语义通常是 `已填写待确认`；只有能校验草稿列表或后台保存成功，才可报 `已创建草稿`。

## 主路径 C：OpenCLI 纯文本草稿兜底（必须显式降级）

```bash
opencli weixin create-draft "<body>" --title "<title>" -f json
opencli weixin drafts -f json
```

仅当用户明确接受纯文本草稿、或富文本粘贴/API 都不可用且本次目标允许无排版时使用。文章包含 Markdown 章节、引用、代码块、表格、封面或正文图时，不得自动从主路径 B 降级到这里；否则会得到“正文没有排版 / 图文内容不完整”的草稿。成功语义：只能报告 `草稿已创建`，**不能**报 `已发表`。如果 drafts 列表显示 `图文内容不完整`，必须告诉用户补齐（通常需要先加封面）才能发表。

### OpenCLI 图片处理

不要默认把 `--cover-image` 当成可用能力。只有当前版本经过最小探测并成功，才使用：

```bash
opencli weixin create-draft "<body>" --title "<title>" --cover-image /abs/path/to/cover.png -f json
opencli weixin drafts -f json
```

如果返回 `Not allowed`、权限拒绝或草稿列表无法确认封面存在：

1. 标记 `image_delivery.method: command_upload` 为 `blocked`。
2. 对正文图尝试剪贴板粘贴探测；封面图优先尝试从正文选择或人工补图，因为封面要求平台素材状态更严格。
3. 如果上传和剪贴板粘贴都不通，继续创建无图草稿或停在已填写待确认，并按 `manual_asset_ready` 回报封面和正文图路径，要求用户在公众号后台补图。

## 回退路径：浏览器切号

仅当 OpenCLI 落在错误账号（小程序号而不是公众号）时使用：

```bash
opencli browser weixin open https://mp.weixin.qq.com --window foreground
opencli browser weixin state
```

只有在账号身份明确时才切换目标公众号，否则把可选项列给用户或使用用户指定的账号。

## 回退路径：浏览器粘贴/上传图片探测

富文本粘贴和正文图片处理的详细路径见 [weixin-rich-paste.md](weixin-rich-paste.md)。仅当用户允许打开公众号后台，且 OpenCLI 命令图片上传不可用时使用：

```bash
opencli browser weixin open https://mp.weixin.qq.com --window foreground
opencli browser weixin state
opencli browser weixin extract --chunk-size 4000
```

找到图文编辑器后再尝试平台允许的图片上传、图片剪贴板粘贴或富文本插入。探测成功前不要宣称图片已插入；探测失败时保留草稿和稳定图片路径，按 `已创建草稿/待人工补图` 回报。

## 校验手段

- `opencli weixin drafts -f json`：核对草稿是否落库、是否标记 `图文内容不完整`。
- 校验草稿标题、正文开头、正文结尾、关键链接、封面/图片状态；如果样式或图片无法自动确认，按 `已创建草稿/待人工检查样式` 回报，不要宣称可直接发表。
- 若需要进一步操作（如上传封面、群发），必须由用户在公众号后台手工完成；skill 不自动代发。
