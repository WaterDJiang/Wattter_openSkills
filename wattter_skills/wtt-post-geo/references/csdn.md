# CSDN 博客发布流程

> 仅在用户明确点名「CSDN / CSDN 博客」或要求「全平台」发布时加载此文件。

## 目录

- [当前能力基线](#当前能力基线2026-07-15)
- [内容 payload 要求](#内容-payload-要求)
- [CSDN 内容适配](#csdn-内容适配)
- [写入前准备](#写入前准备)
- [主路径](#主路径opencli-浏览器--单段正文直接写入)
- [图片处理](#图片处理)
- [草稿路径](#草稿路径)
- [发布路径](#发布路径)
- [发布后校验](#发布后校验)
- [已验证边界](#已验证边界)

## 当前能力基线（2026-07-15）

- 当前 OpenCLI `1.8.6` 的 `opencli list -f json` 中没有 `csdn` 站点 adapter；不要虚构 `opencli csdn publish`、`opencli csdn draft` 等命令。
- 主路径使用 OpenCLI 浏览器会话驱动 CSDN 原生 Markdown 编辑器：`https://editor.csdn.net/md/`。
- 编辑器 UI 支持 `.md` 文件导入，前端限制为小于 5 MiB；但当前 OpenCLI 浏览器桥对该 file input 返回 `Not allowed`，不能把 UI 存在误报为自动导入可用。
- 2026-07-15 已验证单段纯文本正文可通过 `pre[contenteditable=true]` 直接写入并公开发布；多段 Markdown 经普通 `fill/type` 会丢失换行。升级后允许使用受控 contenteditable 写入器做一次探测，只有指纹、预览和重载回读都通过才继续。
- 发布对话框当前包含文章标签、分类专栏、文章类型、原文链接/授权、可见范围和创作声明。分类专栏最多选择 3 个。
- 编辑器前端存在带 cookie/CSRF 的私有保存接口，但本 skill 不直接调用。只走平台 UI 与 OpenCLI 浏览器能力，避免绕过登录、风控或平台确认。
- 除 `format_only` 外，进入浏览器前必须先检查 `opencli doctor`。daemon 或 extension 未连接时，不得尝试填充、保存草稿或发布；说明缺失项并询问用户是否允许修复后再继续。

## CSDN 发布后的跨平台同步

只有用户在本次确认中明确包含其他平台，且 CSDN 公开文章已经按本文件回读验证后，才进入跨平台阶段：

1. 保存 CSDN `articleId`、公开 URL、最终标题和已发布正文快照。
2. 按 `content-format.md` 为其他平台分别生成 HTML/Markdown/短帖 payload；不要直接抓取页面 DOM 后原样群发。
3. 按 `execution-routing.md` 为各平台生成 provider 回退链。
4. CSDN 发布成功后，只把它当作一个已验证源链接；其他平台继续消费各自的独立适配稿。
5. 按 `login-state-adapters.md` 和各平台 reference 逐个创建草稿，不安装、不调用 CSDN 同步助手。
6. adapter 返回草稿 ID/链接时先设为 `created_unverified`；超时、断连或报 `WRITE_UNKNOWN` 时设为 `unknown` 并对账。不得把 CSDN 已发布等同于其他平台已成功。

如果用户只要求发布 CSDN，不自动触发同步助手，也不读取其他平台 reference。

## 内容 payload 要求

```yaml
title: CSDN 文章标题，5～100 个字
body: 独立的 CSDN Markdown 正文
media:
  images: 图片绝对路径列表
  videos: 视频绝对路径列表
  posters: 稳定可读取的封面或配套图列表
media_plan:
  image_delivery:
    method: browser_upload|manual_asset_ready|unsupported
tags: 文章标签列表
links: 正文中保留的公开链接
geo:
  visible_urls: []
  github_urls: []
  source_urls: []
  citation_notes: []
  llms_txt_url: null
  sitemap_url: null
render_mode: markdown
mode: publish|draft|fill_and_confirm|format_only
platform_options:
  article_type: original|repost|translated|null
  original_url: null
  source_authorized: false
  visibility: public|private|fans|vip|null
  categories: []
  creation_statement: none|ai_assisted|web_remix|personal_opinion|null
```

所有模式都必须满足：

- 标题和正文已分离，正文第一行不重复同名 H1。
- 本地图片已有可验证的上传计划；不能把 `/tmp`、`/var/folders` 或本地绝对路径作为 Markdown 图片地址直接发布。

按模式判断 `ready`：

- `format_only`：标题、正文和本地图片清单完整即可；不检查浏览器或账号。
- `draft`：标题与正文通过填后校验即可保存；标签、文章类型、可见性、分类和创作声明可以保持 `null`，但不得把草稿默认值当成最终发布选择。
- `fill_and_confirm`：允许把发布字段留给用户在编辑器确认，状态应为 `needs_user_confirmation`，不是 `ready`。
- `publish`：`article_type`、`visibility`、`creation_statement` 必须确认。不能因为内容由用户提供就自动声明原创；`repost` 或 `translated` 必须提供有效 `original_url` 并确认授权；平台要求标签时至少有 1 个与主题一致的标签。
- 当前任务由 AI 参与生成时，`creation_statement` 默认候选为 `ai_assisted`，在真实写入前的汇总确认中明确展示。

## CSDN 内容适配

- 默认使用完整技术长文，不做短内容摘要。
- 多段 Markdown 应保留标题层级、列表、引用、代码块、表格和普通链接。先按 [browser-editor-fallback.md](browser-editor-fallback.md) 做一次覆盖式 contenteditable 注入探测；失败才由用户手动导入，导入后再回读校验。
- 单段纯文本可以走已验证的直接写入路径；不要把含标题、列表、代码块或多个段落的正文降级拼成一段后发布。
- 独立标题写入标题输入框。若正文第一行是同名 H1，删除该 H1 后再生成 `article.csdn.md`。
- GEO 链接可以进入正文末尾的「参考资料」「项目地址」或「延伸阅读」，不要把 llms.txt、sitemap 等机器入口堆在开头。
- 图片优先使用平台原生上传，让编辑器生成 CSDN 可访问的图片 URL。导入 Markdown 后只要还存在本地路径、`file://`、`/tmp` 或占位注释，就不得发布。
- 视频是否能自动插入必须按当前编辑器控件探测。未验证时按 `manual_asset_ready` 或 `unsupported` 回报，不把本地视频路径写入正文。
- 分类专栏不是通用必填项。只有用户指定，或已确认账号中存在明确匹配的专栏时才选择；最多 3 个，不自动新建专栏。
- 默认可见性候选为 `public`。`private`、`fans`、`vip` 会改变阅读边界，必须在发布前汇总确认。

创作声明映射：

| payload 值 | CSDN 当前 UI 文案 |
|---|---|
| `none` | 无声明 |
| `ai_assisted` | 部分内容由AI辅助生成 |
| `web_remix` | 内容来源网络，进行整合/再创作 |
| `personal_opinion` | 个人观点，仅供参考 |

## 写入前准备

为 CSDN 生成独立文件，不从 `payloads.md`、YAML 计划或执行日志截取正文：

```text
<output>/csdn/
├── article.csdn.md
└── assets/
    └── ...
```

先生成独立正文、标题和图片阻塞清单：

```bash
python3 scripts/prepare-csdn-markdown.py /abs/path/source.md \
  --output-dir /abs/path/output/csdn

test -f /abs/path/output/csdn/article.csdn.md
test "$(wc -c < /abs/path/output/csdn/article.csdn.md)" -lt 5242880
opencli --version
opencli list -f json
opencli doctor
```

`manifest.json` 的用途：

- `publish_ready: true` / `browser_entry_mode: direct_fill`：正文是无本地图片的单段内容，可以走已验证的直接写入路径。
- `browser_entry_mode: browser_injection_probe`：正文是无本地图片的多段 Markdown，可以用通用 `contenteditable-text` 写入器探测；写入器返回匹配不等于 publish ready，仍需预览与重载回读。
- `browser_entry_mode: manual_import_required`：正文含本地图片或不能安全注入，必须由用户手动导入，任务先标记为 `needs_user_confirmation`。
- `local_images` 非空：默认把 CSDN payload 改为 `needs_user_confirmation`，`image_delivery.method` 设为 `manual_asset_ready`。
- `missing_images` 非空：payload 设为 `blocked`，先修复素材路径。
- `title.txt` 是最终标题；`article.csdn.md` 已删除 frontmatter 与同名首个 H1。

如果 `opencli list` 没有 CSDN adapter，这是当前预期状态，继续走浏览器主路径；不要进入插件安装流程。只有用户明确要求创建 OpenCLI adapter 时，才加载 adapter author 工作流。

## 主路径：OpenCLI 浏览器 + 可校验正文写入

使用固定 session 名 `csdn`，同一轮命令不要切换到其他 session：

```bash
opencli browser csdn open https://editor.csdn.net/md/ --window foreground
opencli browser csdn state
opencli browser csdn get url
opencli browser csdn find --css 'input[placeholder="请输入文章标题（5~100个字）"],pre[contenteditable="true"],#import-markdown-file-input,.btn-publish' --limit 20 --text-max 120
```

登录检查：

- URL 如果跳到 `passport.csdn.net`，停止并让用户完成登录。
- 页面出现验证码、账号异常、发布限制或审核拦截时停止，不尝试绕过。
- 直接写入路径必须包含标题控件、`pre[contenteditable=true]` 和发布按钮；人工导入路径还必须包含 `#import-markdown-file-input`。缺少所需控件时按页面漂移处理，重新 `state/find`，不要沿用旧 ref。

填入标题和单段正文：

```bash
opencli browser csdn click 'input[placeholder="请输入文章标题（5~100个字）"]'
opencli browser csdn fill 'input[placeholder="请输入文章标题（5~100个字）"]' "<title>"
opencli browser csdn get value 'input[placeholder="请输入文章标题（5~100个字）"]'
opencli browser csdn fill 'pre[contenteditable="true"]' "<single-paragraph-body>"
opencli browser csdn wait time 2
opencli browser csdn get text 'pre[contenteditable="true"]'
opencli browser csdn state
```

只有 `manifest.json` 的 `direct_fill_ready` 为 `true` 才能执行上面的正文 `fill`。写入后必须核对标题、完整正文和预览；任何一项缺失时不要保存或发布。

多段 Markdown 路径：

- 不调用 `upload "#import-markdown-file-input" ...`；当前已验证会返回 `{"code":-32000,"message":"Not allowed"}`，同一动作不要重试。
- 不用普通 `fill/type` 注入多段 Markdown；当前会压缩换行并破坏标题、列表和段落。
- `manifest.browser_injection_ready: true` 时，按 [browser-editor-fallback.md](browser-editor-fallback.md) 生成 `contenteditable-text` 写入脚本，目标是 `pre[contenteditable=true]`。
- 写入器必须返回 `matches: true`；随后检查预览保留标题、段落、列表、引用和代码块，等待自动保存并再次回读。三项都通过后才把 `publish_ready` 提升为本轮运行时 true。
- 注入不匹配、预览结构损坏或重载丢内容时，先清空错误正文，再停在 `fill_and_confirm`，请用户点击「导入」选择 `article.csdn.md`。人工导入后重新抽样验证，再继续草稿或发布。

## 图片处理

涉及图片时先加载 `references/media-assets.md`。当前多图光标定位与占位替换尚未通过真实账号验证，因此默认只准备稳定图片，标记 `manual_asset_ready`，并把任务停在 `fill_and_confirm`。

只有用户明确允许做图片能力探测，而且已经在真实编辑器中确认当前光标位置，才对 1 张非生产测试图执行一次上传探测：

```bash
opencli browser csdn find --css "input[type=file]" --limit 20 --text-max 120
opencli browser csdn upload "#file-image__upload" /abs/path/output/csdn/assets/image.png
opencli browser csdn wait time 2
opencli browser csdn extract --selector ".layout__panel--editor" --chunk-size 5000
```

- 当前图片 input 声明支持 GIF、JPEG、PNG、BMP、WebP。
- 上传动作必须发生在预期插入位置；上传后检查 Markdown/预览中出现 CSDN 托管 URL 或真实图片节点。
- 如果隐藏 input 返回 `Not allowed`、图片位置错误或无法验证预览，停止自动图片处理，保持 `manual_asset_ready`。不要重复上传同一图片，也不要在正文留下本地路径。
- 真实文章含多张本地图片时，不要直接循环 `upload`。在定位/替换流程完成端到端验证前，让用户在编辑器中补图，或跳过 CSDN 的草稿/发布动作。

## 草稿路径

用户选择 `draft` 时，优先使用顶部「保存草稿」UI；如果发布对话框已打开，也可以选择「保存为草稿」。执行前仍需校验标题、正文和图片：

```bash
opencli browser csdn find --css ".btn-save,button" --limit 80 --text-max 120
opencli browser csdn state
opencli browser csdn click "<SAVE_DRAFT_BUTTON_REF>"
opencli browser csdn wait text "已成功保存至草稿箱" --timeout 15000
opencli browser csdn get url
opencli browser csdn open https://mp.csdn.net/mp_blog/manage/article
opencli browser csdn state
opencli browser csdn find --css "a" --limit 120 --text-max 160
opencli browser csdn get text "<MATCHED_TITLE_REF>"
opencli browser csdn get attributes "<MATCHED_TITLE_REF>"
```

上面的 `<..._REF>` 必须替换为本轮最新 `state/find` 返回的数字 ref；示例加引号是为了防止 shell 把未替换的尖括号解释为重定向，不能把占位符原样传给 OpenCLI。

草稿成功标准：

- 页面出现 `已成功保存至草稿箱` 或同义平台提示。
- 编辑器 URL 含 `articleId=<id>`，或页面能提取文章 id。
- 文章管理页能找到同一标题，且状态是草稿/未发布。

三项不能同时确认时，只报告 `已填写待确认`，不要报告 `已创建草稿`。

## 发布路径

点击顶部发布按钮，等待发布对话框，再填写平台选项：

```bash
opencli browser csdn click ".btn-publish"
opencli browser csdn wait selector ".modal__publish-article" --timeout 10000
opencli browser csdn state
opencli browser csdn find --css ".modal__publish-article input,.modal__publish-article button" --limit 120 --text-max 120
```

填写规则：

- 标签输入框可按占位文本 `请输入文字搜索，Enter键入可添加自定义标签` 查找。每填 1 个标签按 Enter，并检查已选标签节点。
- 如果页面提示「博客等级不满足三级，无法创建自定义标签」，不要继续按 Enter 或假定标签已加入。改从平台标签分类中选择现有子标签，并在弹层顶部回读已选标签；本次实测可用标签包括「人工智能」「测试工具」。
- 文章类型按 `#original`、`#repost`、`#translated` 选择。
- 可见性按 `#public`、`#private`、`#needfans`、`#needvip` 选择。
- 转载/翻译必须填写原文链接并勾选授权确认；缺授权时停止。
- 分类专栏只从现有列表选择，不自动创建。
- 创作声明必须与 `platform_options.creation_statement` 一致。
- 最终提交前再次 `state/extract` 核对标签、文章类型、可见性、来源授权和创作声明。

真实发布按钮是发布对话框 footer 内的「发布文章」，不要误点顶部同名按钮。使用最新 `state/find` 取得 ref 后点击：

```bash
opencli browser csdn find --css ".publish-article-modal__footer button" --limit 20 --text-max 120
opencli browser csdn click "<FINAL_PUBLISH_BUTTON_REF>"
opencli browser csdn wait time 3
opencli browser csdn get url
opencli browser csdn extract --chunk-size 5000
```

## 发布后校验

当前编辑器发布提交后会跳到：

```text
https://mp.csdn.net/mp_blog/creation/success/<article-id>
```

成功页可能同时显示「发布成功！正在审核中」。这只是提交成功证据，不直接判定失败或 `已发布`；继续从成功页或文章管理页取得公开链接，并校验：

```text
https://blog.csdn.net/<username>/article/details/<article-id>
```

成功标准：

- URL 中的 article id 与成功页/编辑器返回 id 一致。
- 公开文章页可访问，标题一致。
- 文章页能匹配正文开头、结尾、关键链接和图片状态。
- 文章管理页「已发布」列表存在同一标题和 article id，且「审核中/未通过」计数不包含该文章。

只有全部通过才报告 `已发布`。以下情况不得报告成功：

- 仍停留在编辑器或发布对话框。
- 只有 `creation/success/<id>`，但拿不到可访问的公开文章 URL。
- 公开文章页显示审核拦截、私密、已删除或内容不完整。
- 文章页标题存在但正文、链接或图片校验失败。

这些情况按事实报告 `已填写待确认` 或 `未完成`。不要为了确认状态重复点击发布。

## 已验证边界

- 2026-07-15 已完成真实账号单段正文发布：article id `162912276`，成功页、公开文章、标题/正文、标签和管理页 `已发布` 状态均已回读。
- CSDN 前端 DOM 和发布字段会漂移；每次真实执行都以最新 `state/find` 为准，不复用历史 ref。
- Markdown file input 自动上传已验证失败；多段 Markdown 普通 `fill/type` 已验证会丢换行。受控 contenteditable 注入属于实验性回退，必须通过指纹、预览和重载三重验证，否则仍回到人工导入。
- 图片 input 的自动上传与插入位置尚未在真实账号中验证；默认 `manual_asset_ready`，不能宣称图片已插入。
- 不把私有 `saveArticle` API 当作 fallback。浏览器路径失败时停在 `已填写待确认`，或在用户明确要求后另行开发正式 OpenCLI adapter。
