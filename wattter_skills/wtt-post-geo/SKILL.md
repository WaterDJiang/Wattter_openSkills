---
name: wtt-post-geo
description: 多平台 GEO 内容发布助手。通过官方 API/浏览器登录态适配器优先、OpenCLI UI 回退的分层路由，把 Markdown 发布或创建草稿到微信公众号、微博、知乎专栏、CSDN、掘金、百家号、博客园、小红书、Twitter/X；微博默认生成并发布摘要短帖，只有用户明确要求时才走长文。统一处理平台格式、GEO 链接、媒体素材、防重复回退、状态校验与最终链接回报。用于多平台发布、全量发布、跨发、创建平台草稿或 GEO 内容分发。
---

# wtt-post-geo：无 CSDN 插件的多平台 GEO 发布

把同一份内容发布到一个或多个内容平台。默认优先使用已验证的官方 API 或 OpenCLI 登录态写 adapter；主路径明确没有产生写入后，再回退 OpenCLI UI/浏览器路径。不安装、不探测、不调用 CSDN 同步助手。所有写入必须在目标平台回读验证后才能报告成功。

## 渐进式披露（必读）

平台细节分别放在 references/ 子文件里，**不要默认全量加载**：

| 平台 | 子文件 | 触发词 |
|------|--------|--------|
| 内容格式适配协议 | [references/content-format.md](references/content-format.md) | 任何真实发布、草稿创建、跨平台改写任务都必须加载 |
| 分层执行路由 | [references/execution-routing.md](references/execution-routing.md) | 任何真实发布、草稿创建、编辑器写入都必须加载 |
| 浏览器编辑器可靠写入 | [references/browser-editor-fallback.md](references/browser-editor-fallback.md) | `fill` 假失败、CodeMirror、iframe、contenteditable、`Not allowed` 回退 |
| 发布结果与最终回报 | [references/result-reporting.md](references/result-reporting.md) | 任何真实发布、草稿创建、全平台任务都必须加载 |
| OpenCLI 登录态草稿 Adapter | [references/login-state-adapters.md](references/login-state-adapters.md) | 显式微博长文/知乎/掘金/百家号/博客园草稿、adapter 安装/预检 |
| CSDN 同步助手静态参考 | [references/csdn-sync-extension.md](references/csdn-sync-extension.md) | 仅维护 skill 或对照参考实现时加载，不是运行时 provider |
| 媒体资产与配图策略 | [references/media-assets.md](references/media-assets.md) | 配图、封面、海报、正文图、小红书图文、图片上传/粘贴 |
| 微信公众号 | [references/weixin.md](references/weixin.md) | 公众号、微信、weixin、微信公众平台 |
| 微信公众号富文本粘贴 | [references/weixin-rich-paste.md](references/weixin-rich-paste.md) | 公众号排版、Markdown 转微信 HTML、富文本粘贴、正文图片 |
| 微博 | [references/weibo.md](references/weibo.md) | 微博、weibo |
| 知乎专栏 | [references/zhihu.md](references/zhihu.md) | 知乎、zhihu |
| CSDN 博客 | [references/csdn.md](references/csdn.md) | CSDN、CSDN 博客、csdn.net |
| 掘金 | [references/juejin.md](references/juejin.md) | 掘金、juejin |
| 百家号 | [references/baijiahao.md](references/baijiahao.md) | 百家号、baijiahao |
| 博客园 | [references/cnblogs.md](references/cnblogs.md) | 博客园、cnblogs |
| 小红书 | [references/xiaohongshu.md](references/xiaohongshu.md) | 小红书、xhs、xiaohongshu |
| Twitter/X | [references/twitter.md](references/twitter.md) | Twitter、推特、X、x.com、twitter |

加载规则：

- **格式协议必读**：只要本次任务会真实写入平台、创建草稿、或为平台准备待发布内容，先读 `references/content-format.md`。它只定义通用 payload 协议；具体平台的文字、图片、视频、长度和草稿/发布规则放在对应平台子文件里。
- **执行路由必读**：除 `format_only` 外，必须读 `references/execution-routing.md`。主路径超时、断连、响应解析失败、缺少对应平台结果或只返回受理态时，先对账，禁止直接用 OpenCLI 重建草稿。
- **结果账本必读**：除 `format_only` 外，必须读 `references/result-reporting.md`，在第一次写入前初始化 `publish-results.json`，每个平台结束后立即更新，任务完成后用 `--strict` 生成最终三列表格。
- **编辑器回退按需读**：浏览器编辑器出现隐藏 textarea、CodeMirror、iframe、contenteditable、`fill.verified: false` 或文件上传 `Not allowed` 时，读 `references/browser-editor-fallback.md`。先回读编辑器内部值，禁止直接追加第二次写入。
- **登录态 adapter 按需读**：只有用户明确要求微博长文时才为微博加载；知乎专栏、掘金、百家号或博客园草稿任务仍必须读 `references/login-state-adapters.md`。默认微博短帖不加载长文 adapter 文档。`references/csdn-sync-extension.md` 只用于维护取证，真实发布任务不加载。
- **媒体策略按需读**：只要本次任务涉及图片、封面、海报、正文插图、小红书图文、视频封面、或用户要求补图，必须读 `references/media-assets.md`。先生成/整理稳定图片资产，再按平台能力决定命令上传、浏览器粘贴、API 上传或人工补图。
- **公众号排版按需读**：公众号任务如果要求保留 Markdown 排版、正文图片、富文本样式，或 OpenCLI create-draft 生成的草稿排版不合格，必须读 `references/weixin-rich-paste.md`。公众号要稳定跑通封面和正文图，默认走 API 草稿路径；API 不通时才走“Markdown -> 微信内联 HTML -> 浏览器编辑器填入/待确认”。需要排版或图片时，不得自动降级为 `opencli weixin create-draft` 纯文本草稿，除非用户明确接受无排版/待人工重排；图片先探测命令上传，再探测剪贴板图片粘贴，仍失败才按 `manual_asset_ready` 回报。
- **默认按点名加载**：用户只提一个平台（如"发到微博"），就只读对应子文件，其他平台不要读。
- **全量触发**：只有用户明确说"全量"、"全平台"、"全部平台"、"所有平台"、"都发一遍"等表述时，才一次性把平台 references 全部加载并按全部平台执行。
- **跨发顺序**：全量触发时默认按 公众号 → 微博 → 知乎 → CSDN → 掘金 → 百家号 → 博客园 → 小红书 → Twitter/X 的顺序执行（除非用户另行指定）；按次汇总、互不阻塞。

> 反例：用户只说"发到公众号"，不要去读其他平台 reference。
> 反例：用户说"发布到社交媒体"含糊不清时，先口头确认是要哪几个平台，再决定加载哪些子文件。

## 适用场景

- 用户需要把同一段文本/文章发布到一个或多个平台（公众号、微博、知乎、CSDN、掘金、百家号、博客园、小红书、Twitter/X）
- 用户希望创建平台草稿（如公众号草稿箱）而非直接发表
- 用户希望走 OpenCLI 统一接口管理多平台发布链路

## 激活与任务前置（通用部分）

0. **Provider 与工具检查**（每次会真实写入前至少检查一次）：
   - 先按 `references/execution-routing.md` 为每个平台生成 `fallback_chain`。
   - 只有路由包含 OpenCLI adapter/UI 或 `opencli browser` 时，才检查 OpenCLI。先检查命令存在，再读取当前注册表，不能凭记忆硬编码：

```bash
command -v opencli
opencli --version
opencli list -f json
```

   - 如果 `opencli` 不存在，先停止执行并询问用户是否允许安装。用户确认后才可执行安装命令，默认建议：

```bash
npm install -g @jackwener/opencli
```

   - 安装后必须继续运行 `opencli --version` 和 `opencli doctor`，确认 CLI、浏览器桥接、账号会话状态。
   - 用户明确要求微博长文时，才检查微博 `article-draft`；知乎、掘金、百家号、博客园仍按草稿任务检查。命令缺失时用 `scripts/install-opencli-adapters.py --check` 确认。只有用户授权写入 `~/.opencli/clis/` 后才运行 `--install`；不安装 CSDN 同步助手。
   - CSDN 是已知例外：当前 OpenCLI `1.8.6` 没有 `csdn` adapter，默认直接按 `references/csdn.md` 走浏览器路径；不要把它误判成需要安装插件。
   - 不要在未确认的情况下安装全局 npm 包、OpenCLI 插件、浏览器扩展或修改浏览器启动方式。

1. **归一化请求**（每个发布任务开始时一次性确认）：
   - `content`：要发布的完整正文
   - `title`：需要标题的平台的简短标题（短测试文本可用 `测试发送`）
   - `platforms`：本次要触发的平台列表
   - `media`：图片、视频等素材绝对路径及类型；平台是否需要、支持什么格式，由对应平台 reference 决定
   - `geo`：需要露出的官网、GitHub、llms.txt、sitemap、来源引用和可公开 URL
   - `mode`：`publish`、`draft`、`fill_and_confirm` 或 `format_only`
   - `platform_options.weibo.variant`：默认 `short_post`；只有用户明确说微博长文、头条文章、全文发布或 `longform` 时设为 `longform`
   - `asset_strategy`：默认生成 HTML PNG 配套图；外部写入时再决定尝试浏览器粘贴、只准备图片待人工补图、或跳过缺图平台
2. **判断加载模式**：
   - 全量触发词（"全平台/全部/所有平台/都发"）→ 全部加载平台 references
   - 否则 → 只加载用户点名的平台子文件
3. **执行 Provider 健康检查**（按需一次）：

   - `official_api` 只检查对应配置和平台 reference 的前置条件。
   - 先运行 `python3 scripts/provider-preflight.py --platforms <ids>`，把 adapter 未注册、图片能力不足和桥接不健康变成写入前的快速回退。
   - `COOKIE` / `HEADER` / `INTERCEPT` / `UI` adapter 或 `opencli browser` 路径运行：

```bash
opencli --version
opencli doctor
```

4. **平台格式适配**：
   - 先按 [references/content-format.md](references/content-format.md) 建立通用 `platform_payload` 结构。
   - 再按已加载的平台 reference 填入该平台自己的标题、正文、图片、视频、话题、链接和草稿/发布动作。
   - 微博默认从原文重写“一句钩子 + 2 到 4 个信息点 + 一个主链接/收束句”的摘要短帖，保存为 `weibo/body.txt`；不要把全文交给长文编辑器。
   - 如果任何平台需要图片，按 [references/media-assets.md](references/media-assets.md) 先形成 `media_plan` 和稳定图片文件，再进入平台命令。配图唯一点缀色只允许克莱因蓝 `#002FA7`，且只用于标点、关键词、编号、细线、角标等小面积元素；图片正文和标题用中性色。
   - 每个平台进入命令前必须有独立干净正文文件或 HTML 文件；`payloads.md`、YAML 计划、执行日志不能被截取后当正文。公众号必须使用 `scripts/prepare-weixin-rich-html.py` 从源 Markdown 生成 `article.wechat.html`，再按 `references/weixin.md` 选择 API 或浏览器编辑器路径。
   - 后续所有平台命令都必须使用适配后的标题、正文、媒体、话题、链接和草稿/发布动作，不要直接把原始内容硬塞到所有平台。
   - 适配不得静默丢弃关键信息。微博默认摘要短帖属于已声明的平台适配，不需要为摘要再次确认，但必须保留原文并在 `adaptation_notes`/最终结果中披露；其他删减、拆条、跳过平台、上传素材、打开浏览器或真实写入仍按原确认边界执行。本地 HTML PNG 配套图默认生成，不需要单独询问。

5. **一次性发布前确认**：
   - 全平台发布时，不要边做边问。先按媒体策略直接生成缺失的 HTML PNG 配套图；微博默认摘要短帖直接进入汇总，不单独询问。执行真实写入前再汇总：已生成图片尺寸/张数、其他平台长文摘要/拆条策略、GEO 链接露出方式、需要用户补配置或人工确认的平台。
   - 用户确认后再逐个平台执行；执行中只有遇到验证码、账号异常、权限拒绝、平台漂移或未预期风险时才再次中断。

6. **逐平台执行与回退**：
   - 第一次真实写入前按 `references/result-reporting.md` 初始化结果账本。
   - 每个平台先用 `publish-result.py attempt-start` 记录 attempt，再调用选中的 provider；结束立即用 `attempt-finish` 记录耗时、状态、错误和回退原因。
   - 只有 `write_state: not_started|confirmed_not_created` 才能进入下一 provider。
   - `unknown|created_unverified|published_unverified` 必须先对账或人工确认，不得自动重试。
   - 同一 provider 本轮连续 2 次确定性失败后熔断。
   - 每个平台对账结束后立即把状态、provider、ID、链接、错误和证据写入结果账本；未知状态也必须落账。

7. **浏览器连接失败时按错误处理**，常见修复：

```bash
opencli daemon restart
opencli doctor
```

8. **不要每次都跑大盘点**（各平台 help、DOM 探索）。只在以下情况查最新帮助：
   - 已知命令因 usage/unknown-option 报错
   - OpenCLI 主版本行为看起来有变化
   - 用户要求的平台或动作不在 references 覆盖范围
   - 目标页面结构已经漂移

```bash
opencli <site> --help -f yaml
opencli <site> <command> --help
```

## 全量发布时的默认顺序

如果用户说"全平台/全部"，默认按以下顺序执行（用户另行指定则按指定顺序）：

1. 公众号 → 读 [references/weixin.md](references/weixin.md)
2. 微博 → 读 [references/weibo.md](references/weibo.md)
3. 知乎 → 读 [references/zhihu.md](references/zhihu.md)
4. CSDN → 读 [references/csdn.md](references/csdn.md)
5. 掘金 → 读 [references/juejin.md](references/juejin.md)
6. 百家号 → 读 [references/baijiahao.md](references/baijiahao.md)
7. 博客园 → 读 [references/cnblogs.md](references/cnblogs.md)
8. 小红书 → 读 [references/xiaohongshu.md](references/xiaohongshu.md)
9. Twitter/X → 读 [references/twitter.md](references/twitter.md)

每个平台独立校验、独立回报，不要因为某个平台失败而中止其他平台。

全部平台结束后必须运行 `scripts/publish-result.py summary --strict`，最终回复包含「平台 / 完成情况 / 链接」三列表格。没有链接写 `—`，不得省略失败、待确认或跳过的平台。

## 内容适配协议（通用）

真实执行前必须先形成如下内部结构，并在最终回报中说明哪些平台使用了改写、摘要、拆条或补图策略：

```yaml
source_content: 原始内容，不直接覆盖
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
      image_delivery:
        method: command_upload|browser_upload|browser_paste|api_upload|manual_asset_ready|unsupported|null
        status: ready|needs_probe|blocked|done|null
    tags: []
    links: []
    geo:
      visible_urls: []
      github_urls: []
      source_urls: []
      citation_notes: []
      llms_txt_url: null
      sitemap_url: null
    render_mode: markdown|html|plain_text|rich_text|platform_native
    formatting_notes: []
    mode: publish|draft|fill_and_confirm|format_only
    platform_options: {}
    execution:
      selected_provider: null
      fallback_chain: []
      write_state: not_started
      attempts: []
      verification: {}
      fallback_reason: null
    result:
      status: pending|published|draft|filled|failed|skipped
      item_id: null
      link: null
      detail: null
    adaptation_notes: []
    user_confirmation_needed: []
```

通用适配原则：

- 具体平台适合长文、短内容、图文、视频还是草稿，必须读对应平台 reference 后再决定。
- 有硬性素材要求的平台先检查素材。素材包括图片和视频，路径必须是绝对路径。
- 有独立标题字段的平台必须先处理标题分离：正文第一行如果是同名 Markdown H1，剥掉 H1 后再进入平台正文。
- 进入平台前必须确认 `render_mode`。不支持 Markdown 的平台要先转成纯文本、HTML 或平台原生富文本，不要把 `#`、`##`、`---`、`**` 等控制符原样发出去。
- 临时海报、脚本生成图、`/tmp` 或 `/var/folders` 下的素材不能直接作为跨平台素材；先落到稳定目录或上传到可复用 URL。缺失配图默认用 HTML -> PNG 本地生成，不需要单独询问。
- 图片上传能力必须分层判断：OpenCLI 命令参数上传、浏览器文件上传、浏览器图片剪贴板粘贴、平台 API 上传、只准备图片待人工补图。命令参数失败时不要反复试同一命令，转入浏览器上传/粘贴探测或降级策略。
- 公众号图片能力的当前默认判断：API 上传是可自动补图主路径；OpenCLI 浏览器路径能填标题和正文富文本，`browser upload` 已出现 `Not allowed`，应继续探测图片剪贴板粘贴；只有编辑器/预览/草稿确认真实 `img` 后，才能宣称图片已插入。
- OpenCLI 能力探测以 `opencli list` 和具体命令 help 为准，不以 `opencli plugin list` 是否为空为准；很多站点能力可能是内置适配器而不是 plugin。
- GEO 友好内容要分平台露出：可公开的网址、GitHub、llms.txt、sitemap 和引用来源进入 `geo` 字段；最终是否放进正文、评论、草稿或不露出，由平台 reference 决定。
- 内容长度可能超限时，不要静默截断。微博默认摘要短帖按 `references/weibo.md` 直接生成并披露；其他平台先给出 `摘要发布`、`拆成多条`、`只创建草稿/待确认`、`跳过该平台` 四类处理选择。
- 平台标题、正文、话题、媒体、链接要分开维护；哪些字段写入命令、哪些字段进入正文，由对应平台 reference 决定。
- 如果用户只要求 `format_only`，只输出平台适配稿，不调用任何真实发布命令。
- Provider 回退必须复用同一份平台适配稿；不得在 API 失败后把原始 Markdown 直接塞进 OpenCLI。
- 主路径状态不明时先查最近草稿/帖子。只有确认没有写入，才能执行下一 provider。

## 状态回报（通用）

最终回报对每个被请求的平台给出精确状态，使用以下固定术语：

- `已发布`：已验证的实时帖子/文章存在。
- `已创建草稿`：草稿已存但尚未公开。
- `已填写待确认`：内容已写入编辑器但需要人工操作或最终校验。
- `未完成`：命令失败、平台拦截、或校验没通过。
- `已跳过`：用户明确跳过该平台。

最终回复应包含紧凑的逐平台汇总、已验证帖子的链接、以及任何需要用户补做的动作。仅当 OpenCLI 修复影响了本次任务时才提及修复过程。
发生 provider 回退时，还要说明最终成功 provider、主路径错误和 `fallback_reason`。

最终回复的固定收尾格式：

```markdown
| 平台 | 完成情况 | 链接 |
|---|---|---|
| 知乎 | 已发布 | [打开](https://example.com) |
| 小红书 | 已填写待确认：正文无法回读 | — |
```

必须从 `publish-results.json` 生成，不能凭对话记忆手写遗漏平台。完整规则见 [references/result-reporting.md](references/result-reporting.md)。

## 安全护栏（通用）

- 所有写入必须经过平台状态、最新帖子列表、草稿列表、URL 变化、页面文本等手段校验
- 上传必须用绝对路径
- 如果确实需要通路测试帖或测试草稿，标题/正文必须带 `[TEST]` 前缀，且测试动作必须先征得用户确认。不要用真实正文做未确认的测试帖。
- 不要删除测试帖，除非用户明确要求
- 不要为了"补偿"不确定性而重复发布相同内容
- 如果某个平台需要已登录的浏览器，优先使用已注册 OpenCLI adapter 或 `opencli doctor` + browser session；不要在任务中临时拼接私有接口，也不要回到 CSDN 同步助手。

## 账号安全与合规护栏

- 不要加入用于规避平台检测的"模拟真人"动作，包括随机鼠标轨迹、随机点击、随机打字延迟、伪装用户行为、绕过验证码、绕过风控弹窗或隐藏自动化痕迹。
- 如果平台出现验证码、异常登录、账号风险提醒、频率限制、二次确认、内容审核拦截或需要人工判断的弹窗，立刻停止自动发布，按 `已填写待确认` 或 `未完成` 回报，并说明需要用户在平台侧处理。
- 发布节奏要保守：同一平台不要连续重复发布相同或高度相似内容；批量跨发时按平台逐个执行、逐个校验，失败平台不要自动重试多次。
- 允许的账号安全措施是透明和合规的：发布前确认账号身份、使用平台允许的 API 或 OpenCLI 适配器、降低批量频率、保留人工确认点、记录返回的帖子/草稿 URL。
- 不要把"像真人"作为目标。目标是可追溯、低频、用户明确授权、平台侧可验证的发布。
