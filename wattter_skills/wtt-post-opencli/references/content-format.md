# 内容格式适配协议

> 任何真实发布、草稿创建、跨平台改写、或仅为平台准备待发布内容时加载此文件。它只定义通用 payload 协议和确认边界；具体平台的文字、图片、视频、长度限制和发布命令放在对应平台 md 文件里。

## 目标

同一份原始内容不能直接投给所有平台。执行前先生成通用 `platform_payloads`，再读取目标平台 reference，把每个平台的 payload 填成该平台可执行的版本。

适配层必须解决四类问题：

- 原始内容、标题、链接、图片、视频等素材如何归一化。
- 每个平台 payload 是否完整，是否能进入写入命令。
- 原文超出平台实际限制时，是否需要摘要、拆条、草稿或跳过。
- 是否存在用户必须确认的有损变更，例如删减、生成配图、合并段落、转成多条发布。

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
  links:
    - https://example.com
  desired_platforms:
    - weixin
    - weibo
    - zhihu
    - xiaohongshu
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
    tags: []
    links: []
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
6. **平台能力漂移时再探测**：如果命令报 `usage`、`unknown option`、`unknown command`，用 `opencli <site> --help -f yaml` 或对应 command help 更新当前平台能力，再回到该平台 md 修正 payload。

## 需要用户确认的情况

遇到以下任一情况，先停下来问用户：

- 目标平台要求图片或视频，但用户未提供可用素材。
- 目标平台不支持用户提供的媒体类型，需要转成其他形式、改为草稿或跳过。
- 任一平台需要删减、摘要、拆多条或从图文改成视频/从视频改成图文。
- 用户要求全平台发布，但某平台插件、登录态或账号身份缺失。
- OpenCLI 需要安装、升级、安装插件、重启 daemon、打开浏览器调试桥接。
- 平台实际返回的内容限制和本文件策略冲突。

确认问题要短，直接给可执行选项，例如：

```text
这个平台需要指定素材格式。你要我使用已有图片/视频、生成新素材，还是跳过该平台？
```

## 最终回报中的适配信息

逐平台汇总时补充一行适配说明：

- 平台名：使用了什么适配稿，是否摘要/拆条/补图/补视频，原文是否被有损改写。
