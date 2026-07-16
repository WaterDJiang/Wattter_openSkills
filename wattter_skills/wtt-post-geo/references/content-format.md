# 内容格式适配协议

> 任何真实发布、草稿创建、跨平台改写、或仅为平台准备待发布内容时加载此文件。它只定义通用 payload 协议和确认边界；具体平台的文字、图片、视频、长度限制和发布命令放在对应平台 md 文件里。

## 目标

同一份原始内容不能直接投给所有平台。执行前先生成通用 `platform_payloads`，再读取目标平台 reference，把每个平台的 payload 填成该平台可执行的版本。

适配层必须解决这些问题：

- 原始内容、标题、链接、图片、视频等素材如何归一化。
- 每个平台 payload 是否完整，是否能进入写入命令。
- 原文超出平台实际限制时，是否需要摘要、拆条、草稿或跳过。
- 是否需要配图、封面、正文图、图文笔记图，以及图片是命令上传、浏览器粘贴、API 上传还是人工补图。
- GEO 友好的网址、GitHub、来源、llms.txt、sitemap 等信息在哪些平台可见、如何露出。
- 是否存在用户必须确认的有损变更，例如未被平台 reference 授权的删减、合并段落、转成多条发布。
- 源 Markdown 在目标平台是富文本、纯文本还是短内容，是否需要剥标题、降级格式或转 HTML。

## 输入

```yaml
source:
  title: 用户给定标题或从正文提炼的标题
  content: 原始正文
  media:
    images:
      - /absolute/path/to/image.png
    videos:
      - /absolute/path/to/video.mp4
    posters:
      - /absolute/path/to/stable-poster.png
  links:
    - https://example.com
  geo:
    visible_urls:
      - https://example.com
    github_urls:
      - https://github.com/org/repo
    source_urls: []
    citation_notes: []
    llms_txt_url: https://example.com/llms.txt
    sitemap_url: https://example.com/sitemap.xml
  desired_platforms:
    - weixin
    - weibo
    - zhihu
    - csdn
    - juejin
    - baijiahao
    - cnblogs
    - xiaohongshu
    - twitter
  mode: publish|draft|fill_and_confirm|format_only
```

所有媒体素材必须是绝对路径。相对路径先转换为绝对路径；找不到文件时按缺素材处理，不要猜测路径。

## 输出

```yaml
platform_payloads:
  <platform>:
    status: ready|needs_user_confirmation|blocked|skipped
    title: ...
    body: ...
    body_file: /absolute/path/to/platform/body.txt|null
    media:
      images: []
      videos: []
      posters: []
    media_plan:
      required: false
      generated: []
      requested_outputs: []
      image_delivery:
        method: command_upload|browser_upload|browser_paste|api_upload|manual_asset_ready|unsupported|null
        status: ready|needs_probe|blocked|done|null
        evidence: []
    tags: []
    links: []
    geo:
      visible_urls: []
      github_urls: []
      source_urls: []
      citation_notes: []
      llms_txt_url: null
      sitemap_url: null
    variant: short_post|longform|article|null
    render_mode: markdown|html|plain_text|rich_text|platform_native
    formatting_notes: []
    mode: publish|draft|fill_and_confirm|format_only
    platform_options: {}
    execution:
      selected_provider: null
      fallback_chain: []
      write_state: not_started
      circuit_breaker:
        max_confirmed_failures: 2
        confirmed_failures: 0
        open: false
      attempts: []
      verification:
        status: pending
        evidence: []
      fallback_reason: null
    result:
      status: pending|published|draft|filled|failed|skipped
      item_id: null
      link: null
      detail: null
      updated_at: null
    adaptation_notes:
      - ...
    user_confirmation_needed:
      - ...
```

只有 `status: ready` 的平台可以进入真实发布命令。`needs_user_confirmation` 必须先问用户；`blocked` 和 `skipped` 要在最终回报里说明原因。

## 通用适配规则

1. **保留原文**：不得覆盖或篡改 `source.content`。所有改写都写进对应平台 payload。
2. **平台细节下放**：本文件不写具体平台的长度、图片、视频、封面、标题规则；这些规则必须放在并读取对应平台 md。
3. **不静默截断**：超过平台长度或不适合平台形态时，先读取平台 reference。平台 reference 已声明默认摘要形态时，可直接生成摘要，但必须保留原文、输出独立 `body_file`、记录 `adaptation_notes`；没有默认摘要授权时才给用户选项，不能直接删掉核心段落。
4. **媒体独立维护**：图片和视频分别放入 `media.images` 与 `media.videos`，不要把视频当图片、不要把素材说明混入正文。
5. **媒体计划先行**：如果任何平台需要封面、正文图、小红书图文或视频封面，必须加载 `references/media-assets.md`，先形成 `media_plan`。缺失配套图默认直接用 HTML -> Playwright -> PNG 生成；只参考 `wtt-post-multi-platform` 的 HTML 生图风格与思路，不把它当作本 skill 的发布执行入口。
6. **图片发布能力分层**：图片生成成功不等于平台插入成功。每个平台必须标记 `image_delivery.method`：`command_upload`、`browser_upload`、`browser_paste`、`api_upload`、`manual_asset_ready` 或 `unsupported`。命令参数上传失败后，不要重复尝试同一失败命令，改走浏览器上传/粘贴探测、API 或人工补图。
7. **GEO 字段独立维护**：官网 URL、GitHub、source URL、llms.txt、sitemap 和引用说明进入 `geo` 字段。平台正文是否露出这些信息由平台 reference 决定；不要因为某平台不适合长链接就从源 payload 删除。
8. **标题分离**：需要标题的平台使用 `title` 字段；不需要或短内容平台不要把长标题重复塞进正文开头。
9. **平台专属选项隔离**：版权声明、转载授权、可见性、分类、创作声明等非通用字段写入 `platform_options`，具体键和值只由对应平台 reference 定义，不要提升成所有平台必填项。
10. **H1 剥离**：如果 `source.content` 第一行是与 `title` 相同或高度相似的 Markdown H1（例如 `# 标题`），且目标平台有独立标题字段，正文必须从 H1 后第一段开始。不要让平台标题和正文 H1 重复显示。
11. **平台正文独立落盘**：`payloads.md`、发布计划、YAML 摘要、执行日志只能作为给人看的报告，不能再被 `sed` / `awk` 截取后直接当平台正文。每个平台进入写入命令前必须有独立干净文件，例如 `weixin/article.wechat.html`、`weixin/article.plain.txt`、`weibo/body.txt`、`csdn/article.csdn.md`、`xhs/body.txt`。微博默认先生成摘要短帖到 `weibo/body.txt`；公众号必须从源 Markdown 转 HTML，不得从汇总报告中截正文。
12. **Markdown 渲染能力分流**：目标平台不保证渲染 Markdown。进入命令前必须明确 `render_mode`：
   - `markdown`：平台或适配器明确支持 Markdown。
   - `html`：平台支持粘贴或写入 HTML，且当前流程能保留富文本。
   - `plain_text`：平台只收纯文本，必须移除 `#`、`##`、`---`、`**` 等 Markdown 控制符，只保留可读文本。
   - `platform_native`：由平台编辑器或适配器处理，发布前必须抽样校验渲染结果。
13. **稳定媒体资产**：所有图片、视频、海报必须是发布时仍存在的稳定路径。不要引用 `/tmp`、`/var/folders`、脚本临时目录或已清理的生成文件。临时生成的海报必须先复制到稳定目录，或上传到平台/图床拿到可用 URL 后再进入 payload。
14. **填后校验**：浏览器自动化填入正文后，点击发布前必须用 `extract`、编辑器文本、预览页或草稿列表抽样校验开头、结尾、链接、关键段落和图片状态。无法校验时只允许按 `已填写待确认` 回报。
15. **平台能力漂移时再探测**：如果命令报 `usage`、`unknown option`、`unknown command`，用 `opencli <site> --help -f yaml` 或对应 command help 更新当前平台能力，再回到该平台 md 修正 payload。
16. **Provider 路由独立维护**：真实写入按 `references/execution-routing.md` 填写 `execution`。平台格式稿只生成一次，API/adapter/UI 回退都复用该稿，不得在回退时改变正文或媒体策略。
17. **不确定写入禁止回退**：超时、断连、响应解析失败或只收到受理结果时，设置 `write_state: unknown`，先查平台草稿/帖子；确认没有写入后才可设置 `confirmed_not_created`。
18. **有损回退重新确认**：执行过程中临时把长文改短帖、富文本改纯文本、带图改无图、公开发布改草稿，都属于内容或动作变化，必须把 payload 改为 `needs_user_confirmation`。平台 reference 在写入前已经声明并生成的默认形态不算回退；例如微博默认摘要短帖不需要再次确认。
19. **编辑器假失败先回读**：`fill.verified: false`、隐藏 textarea value 为空或按钮点击无跳转时，先读编辑器内部值/草稿列表。未确认空写入前禁止用 `type` 或第二个 provider 追加正文。
20. **结果账本同步**：每个平台结束后把 `result.status/item_id/link/detail` 与 execution evidence 同步到 `publish-results.json`。最终输出必须覆盖全部请求平台。

## 需要用户确认的情况

遇到以下任一情况，先停下来问用户：

- 目标平台要求图片或视频，但用户未提供可用素材。
- 用户未明确允许上传图片、打开浏览器探测图片粘贴、创建草稿或真实发布。仅本地 HTML -> PNG 配套图生成不需要询问。
- 目标平台需要海报图、正文图片或封面图，但素材只存在于临时目录、不可读取或无法复用。
- 目标平台不支持用户提供的媒体类型，需要转成其他形式、改为草稿或跳过。
- 任一平台需要执行未被平台 reference 明确授权的删减、摘要、拆多条，或从图文改成视频/从视频改成图文。微博默认摘要短帖属于已授权适配，不在此列。
- 任一平台需要把 Markdown 转成纯文本、HTML 或平台富文本，且转换会改变标题、层级、图片或链接呈现。
- 用户要求全平台发布，但某平台插件、登录态或账号身份缺失。
- OpenCLI 需要安装、升级、安装插件、重启 daemon、打开浏览器调试桥接。
- 公众号 API 路径缺少 appid/appsecret、access token、素材 media_id、服务器 IP 白名单或配置文件。
- 公众号需要封面和正文图片自动落入草稿，但只能使用 OpenCLI 浏览器路径；当前 OpenCLI 图片上传未验证为稳定能力，应降级为 API 配置确认或 `manual_asset_ready`。
- 公众号文章含 Markdown 标题、列表、代码块、引用或正文图片，但执行计划准备调用 `opencli weixin create-draft` 直接写入纯文本。除非用户明确接受“无排版/待人工重排”，否则必须改走 API 草稿箱或浏览器富文本编辑器路径。
- 平台实际返回的内容限制和本文件策略冲突。
- 平台出现验证码、异常登录、频控、账号风险、内容审核拦截或需要人工判断的弹窗。
- 用户要求加入绕过检测、伪装真人、规避风控、自动处理验证码等行为。

确认问题要短，直接给可执行选项，例如：

```text
这个平台需要指定素材格式。你要我使用已有图片/视频、生成新素材，还是跳过该平台？
```

## 最终回报中的适配信息

先按 [result-reporting.md](result-reporting.md) 输出「平台 / 完成情况 / 链接」三列表格，再补充必要的适配信息。

逐平台汇总时补充一行适配说明：

- 平台名：使用了什么适配稿，是否摘要/拆条/补图/补视频，原文是否被有损改写。
- 图片：图片是已自动插入、已生成待人工补图、还是因权限/平台能力未完成。
- GEO：哪些网址/GitHub/来源被放进正文，哪些因平台限制未露出。
