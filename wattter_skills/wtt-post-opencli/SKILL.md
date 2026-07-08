---
name: wtt-post-opencli
description: 通过 OpenCLI 一键发布内容到微信公众号、微博、知乎专栏、小红书、Twitter/X 等多个平台。统一处理真实账号的发布/草稿创建、媒体素材约束、状态校验与精确回报。当用户需要通过 OpenCLI 发布、发送、跨发、创建平台草稿，或把内容同时发布到公众号/微博/知乎/小红书/Twitter 时使用。
---

# OpenCLI 多平台发布（入口）

通过 `opencli` 把同一份内容发布到一个或多个中文内容平台。所有动作都是真实账号的外部写操作，必须在平台侧验证通过后才能报告成功，绝不能"自欺欺人"地宣称已发布。

## 渐进式披露（必读）

平台细节分别放在 references/ 子文件里，**不要默认全量加载**：

| 平台 | 子文件 | 触发词 |
|------|--------|--------|
| 内容格式适配协议 | [references/content-format.md](references/content-format.md) | 任何真实发布、草稿创建、跨平台改写任务都必须加载 |
| 微信公众号 | [references/weixin.md](references/weixin.md) | 公众号、微信、weixin、微信公众平台 |
| 微博 | [references/weibo.md](references/weibo.md) | 微博、weibo |
| 知乎专栏 | [references/zhihu.md](references/zhihu.md) | 知乎、zhihu |
| 小红书 | [references/xiaohongshu.md](references/xiaohongshu.md) | 小红书、xhs、xiaohongshu |
| Twitter/X | [references/twitter.md](references/twitter.md) | Twitter、推特、X、x.com、twitter |

加载规则：

- **格式协议必读**：只要本次任务会真实写入平台、创建草稿、或为平台准备待发布内容，先读 `references/content-format.md`。它只定义通用 payload 协议；具体平台的文字、图片、视频、长度和草稿/发布规则放在对应平台子文件里。
- **默认按点名加载**：用户只提一个平台（如"发到微博"），就只读对应子文件，其他平台不要读。
- **全量触发**：只有用户明确说"全量"、"全平台"、"全部平台"、"所有平台"、"都发一遍"等表述时，才一次性把平台 references 全部加载并按全部平台执行。
- **跨发顺序**：全量触发时默认按 公众号 → 微博 → 知乎 → 小红书 → Twitter/X 的顺序执行（除非用户另行指定）；按次汇总、互不阻塞。

> 反例：用户只说"发到公众号"，不要去读 weibo.md / zhihu.md / xiaohongshu.md / twitter.md。
> 反例：用户说"发布到社交媒体"含糊不清时，先口头确认是要哪几个平台，再决定加载哪些子文件。

## 适用场景

- 用户需要把同一段文本/文章发布到一个或多个平台（公众号、微博、知乎、小红书、Twitter/X）
- 用户希望创建平台草稿（如公众号草稿箱）而非直接发表
- 用户希望走 OpenCLI 统一接口管理多平台发布链路

## 激活与任务前置（通用部分）

0. **工具激活检查**（每次会真实写入前至少检查一次）：
   - 先检查 OpenCLI 是否存在：

```bash
command -v opencli
opencli --version
```

   - 如果 `opencli` 不存在，先停止执行并询问用户是否允许安装。用户确认后才可执行安装命令，默认建议：

```bash
npm install -g opencli
```

   - 安装后必须继续运行 `opencli --version` 和 `opencli doctor`，确认 CLI、浏览器桥接、账号会话状态。
   - 如果目标平台命令不存在、插件缺失或 `unknown command/site`，先用 `opencli --help`、`opencli plugin --help`、`opencli <site> --help -f yaml` 判断当前 OpenCLI 的插件安装方式；向用户说明缺失项并征得确认后，才自动安装对应插件或适配器。
   - 不要在未确认的情况下安装全局 npm 包、OpenCLI 插件、浏览器扩展或修改浏览器启动方式。

1. **归一化请求**（每个发布任务开始时一次性确认）：
   - `content`：要发布的完整正文
   - `title`：需要标题的平台的简短标题（短测试文本可用 `测试发送`）
   - `platforms`：本次要触发的平台列表
   - `media`：图片、视频等素材绝对路径及类型；平台是否需要、支持什么格式，由对应平台 reference 决定
   - `mode`：`publish`、`draft`、`fill_and_confirm` 或 `format_only`
2. **判断加载模式**：
   - 全量触发词（"全平台/全部/所有平台/都发"）→ 全部加载平台 references
   - 否则 → 只加载用户点名的平台子文件
3. **OpenCLI 健康检查**（仅一次）：

```bash
opencli --version
opencli doctor
```

4. **平台格式适配**：
   - 先按 [references/content-format.md](references/content-format.md) 建立通用 `platform_payload` 结构。
   - 再按已加载的平台 reference 填入该平台自己的标题、正文、图片、视频、话题、链接和草稿/发布动作。
   - 后续所有平台命令都必须使用适配后的标题、正文、媒体、话题、链接和草稿/发布动作，不要直接把原始内容硬塞到所有平台。
   - 适配不得静默丢弃关键信息；涉及删减、拆条、生成配图、跳过平台时，先让用户确认。

5. **浏览器连接失败时按错误处理**，常见修复：

```bash
opencli daemon restart
opencli doctor
```

6. **不要每次都跑大盘点**（`opencli list`、各平台 help、DOM 探索）。只在以下情况查最新帮助：
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
4. 小红书 → 读 [references/xiaohongshu.md](references/xiaohongshu.md)
5. Twitter/X → 读 [references/twitter.md](references/twitter.md)

每个平台独立校验、独立回报，不要因为某个平台失败而中止其他平台。

## 内容适配协议（通用）

真实执行前必须先形成如下内部结构，并在最终回报中说明哪些平台使用了改写、摘要、拆条或补图策略：

```yaml
source_content: 原始内容，不直接覆盖
platform_payloads:
  <platform>:
    status: ready|needs_user_confirmation|blocked|skipped
    title: ...
    body: ...
    media:
      images: []
      videos: []
      posters: []
    tags: []
    links: []
    render_mode: markdown|html|plain_text|rich_text|platform_native
    formatting_notes: []
    mode: publish|draft|fill_and_confirm|format_only
    adaptation_notes: []
    user_confirmation_needed: []
```

通用适配原则：

- 具体平台适合长文、短内容、图文、视频还是草稿，必须读对应平台 reference 后再决定。
- 有硬性素材要求的平台先检查素材。素材包括图片和视频，路径必须是绝对路径。
- 有独立标题字段的平台必须先处理标题分离：正文第一行如果是同名 Markdown H1，剥掉 H1 后再进入平台正文。
- 进入平台前必须确认 `render_mode`。不支持 Markdown 的平台要先转成纯文本、HTML 或平台原生富文本，不要把 `#`、`##`、`---`、`**` 等控制符原样发出去。
- 临时海报、脚本生成图、`/tmp` 或 `/var/folders` 下的素材不能直接作为跨平台素材；先落到稳定目录或上传到可复用 URL。
- 内容长度可能超限时，不要静默截断。先给出 `摘要发布`、`拆成多条`、`只创建草稿/待确认`、`跳过该平台` 四类处理选择。
- 平台标题、正文、话题、媒体、链接要分开维护；哪些字段写入命令、哪些字段进入正文，由对应平台 reference 决定。
- 如果用户只要求 `format_only`，只输出平台适配稿，不调用任何真实发布命令。

## 状态回报（通用）

最终回报对每个被请求的平台给出精确状态，使用以下固定术语：

- `已发布`：已验证的实时帖子/文章存在。
- `已创建草稿`：草稿已存但尚未公开。
- `已填写待确认`：内容已写入编辑器但需要人工操作或最终校验。
- `未完成`：命令失败、平台拦截、或校验没通过。
- `已跳过`：用户明确跳过该平台。

最终回复应包含紧凑的逐平台汇总、已验证帖子的链接、以及任何需要用户补做的动作。仅当 OpenCLI 修复影响了本次任务时才提及修复过程。

## 安全护栏（通用）

- 所有写入必须经过平台状态、最新帖子列表、草稿列表、URL 变化、页面文本等手段校验
- 上传必须用绝对路径
- 不要删除测试帖，除非用户明确要求
- 不要为了"补偿"不确定性而重复发布相同内容
- 如果某个平台需要已登录的浏览器，优先用 `opencli doctor` + browser session，不要自己造 API 调用

## 账号安全与合规护栏

- 不要加入用于规避平台检测的"模拟真人"动作，包括随机鼠标轨迹、随机点击、随机打字延迟、伪装用户行为、绕过验证码、绕过风控弹窗或隐藏自动化痕迹。
- 如果平台出现验证码、异常登录、账号风险提醒、频率限制、二次确认、内容审核拦截或需要人工判断的弹窗，立刻停止自动发布，按 `已填写待确认` 或 `未完成` 回报，并说明需要用户在平台侧处理。
- 发布节奏要保守：同一平台不要连续重复发布相同或高度相似内容；批量跨发时按平台逐个执行、逐个校验，失败平台不要自动重试多次。
- 允许的账号安全措施是透明和合规的：发布前确认账号身份、使用平台允许的 API 或 OpenCLI 适配器、降低批量频率、保留人工确认点、记录返回的帖子/草稿 URL。
- 不要把"像真人"作为目标。目标是可追溯、低频、用户明确授权、平台侧可验证的发布。
