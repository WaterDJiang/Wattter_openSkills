# 内容格式适配协议

> 任何真实发布、草稿创建、跨平台改写、或仅为平台准备待发布内容时加载此文件。它只定义通用 payload 协议和确认边界；具体平台的文字、图片、视频、长度限制和发布命令放在对应平台 md 文件里。

## 目标

同一份原始内容不能直接投给所有平台。执行前先生成通用 `platform_payloads`，再读取目标平台 reference，把每个平台的 payload 填成该平台可执行的版本。

适配层必须解决四类问题：

- 原始内容、标题、链接、图片、视频等素材如何归一化。
- 每个平台 payload 是否完整，是否能进入写入命令。
- 原文超出平台实际限制时，是否需要摘要、拆条、草稿或跳过。
- 是否存在用户必须确认的有损变更，例如删减、生成配图、合并段落、转成多条发布。
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
  desired_platforms:
    - weixin
    - weibo
    - zhihu
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
    media:
      images: []
      videos: []
      posters: []
    tags: []
    links: []
    variant: short_post|longform|article|null
    render_mode: markdown|html|plain_text|rich_text|platform_native
    formatting_notes: []
    mode: publish|draft|fill_and_confirm|format_only
    adaptation_notes:
      - ...
    user_confirmation_needed:
      - ...
```

只有 `status: ready` 的平台可以进入真实发布命令。`needs_user_confirmation` 必须先问用户；`blocked` 和 `skipped` 要在最终回报里说明原因。

## 通用适配规则

1. **保留原文**：不得覆盖或篡改 `source.content`。所有改写都写进对应平台 payload。
2. **平台细节下放**：本文件不写具体平台的长度、图片、视频、封面、标题规则；这些规则必须放在并读取对应平台 md。
3. **不静默截断**：超过平台长度或不适合平台形态时，先给用户选项。可推荐一个默认选项，但不能直接删掉核心段落。
4. **媒体独立维护**：图片和视频分别放入 `media.images` 与 `media.videos`，不要把视频当图片、不要把素材说明混入正文。
5. **标题分离**：需要标题的平台使用 `title` 字段；不需要或短内容平台不要把长标题重复塞进正文开头。
6. **H1 剥离**：如果 `source.content` 第一行是与 `title` 相同或高度相似的 Markdown H1（例如 `# 标题`），且目标平台有独立标题字段，正文必须从 H1 后第一段开始。不要让平台标题和正文 H1 重复显示。
7. **Markdown 渲染能力分流**：目标平台不保证渲染 Markdown。进入命令前必须明确 `render_mode`：
   - `markdown`：平台或适配器明确支持 Markdown。
   - `html`：平台支持粘贴或写入 HTML，且当前流程能保留富文本。
   - `plain_text`：平台只收纯文本，必须移除 `#`、`##`、`---`、`**` 等 Markdown 控制符，只保留可读文本。
   - `platform_native`：由平台编辑器或适配器处理，发布前必须抽样校验渲染结果。
8. **稳定媒体资产**：所有图片、视频、海报必须是发布时仍存在的稳定路径。不要引用 `/tmp`、`/var/folders`、脚本临时目录或已清理的生成文件。临时生成的海报必须先复制到稳定目录，或上传到平台/图床拿到可用 URL 后再进入 payload。
9. **填后校验**：浏览器自动化填入正文后，点击发布前必须用 `extract`、编辑器文本、预览页或草稿列表抽样校验开头、结尾、链接和关键段落。无法校验时只允许按 `已填写待确认` 回报。
10. **平台能力漂移时再探测**：如果命令报 `usage`、`unknown option`、`unknown command`，用 `opencli <site> --help -f yaml` 或对应 command help 更新当前平台能力，再回到该平台 md 修正 payload。

## 需要用户确认的情况

遇到以下任一情况，先停下来问用户：

- 目标平台要求图片或视频，但用户未提供可用素材。
- 目标平台需要海报图、正文图片或封面图，但素材只存在于临时目录、不可读取或无法复用。
- 目标平台不支持用户提供的媒体类型，需要转成其他形式、改为草稿或跳过。
- 任一平台需要删减、摘要、拆多条或从图文改成视频/从视频改成图文。
- 任一平台需要把 Markdown 转成纯文本、HTML 或平台富文本，且转换会改变标题、层级、图片或链接呈现。
- 用户要求全平台发布，但某平台插件、登录态或账号身份缺失。
- OpenCLI 需要安装、升级、安装插件、重启 daemon、打开浏览器调试桥接。
- 平台实际返回的内容限制和本文件策略冲突。
- 平台出现验证码、异常登录、频控、账号风险、内容审核拦截或需要人工判断的弹窗。
- 用户要求加入绕过检测、伪装真人、规避风控、自动处理验证码等行为。

确认问题要短，直接给可执行选项，例如：

```text
这个平台需要指定素材格式。你要我使用已有图片/视频、生成新素材，还是跳过该平台？
```

## 最终回报中的适配信息

逐平台汇总时补充一行适配说明：

- 平台名：使用了什么适配稿，是否摘要/拆条/补图/补视频，原文是否被有损改写。
