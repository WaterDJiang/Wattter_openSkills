# 小红书发布流程

> 仅在用户明确点名「小红书」或要求「全平台」发布时加载此文件。

## 关键事实（实测）

- 小红书图文发布**必须有图**，视频笔记必须有视频素材；缺少对应素材时先确认，不要硬发。
- 用户明确跳过小红书时立刻停止所有小红书相关尝试。
- `opencli xiaohongshu publish` 自报成功但没通过 `creator-notes` 校验时，不能宣称成功。
- 执行前必须使用 `references/content-format.md` 生成的 `platform_payloads.xiaohongshu`。长文必须先转为图文笔记版，缺图必须先确认。

## 内容 payload 要求

```yaml
title: 小红书笔记标题
body: 短段落正文
media:
  images:
    - /abs/path/to/image.png
  videos:
    - /abs/path/to/video.mp4
tags:
  - 关键词
```

适配规则：

- 适合图文笔记、视频笔记、经验清单、短段落、强标题和标签。
- 图文模式必须至少有一张图片；视频模式必须至少有一个视频文件。
- 原文较长时，生成笔记版：开头一句场景钩子 + 3 到 6 个短要点 + 轻量结尾。
- 标签只保留少量高相关关键词。正文里可以包含少量高相关标签，但标签必须先在 `tags` 字段维护，避免堆砌无关话题。
- 如果用户只给视频，优先按视频笔记适配；如果当前 OpenCLI 只支持图文发布，先让用户选择提取封面/改图文/跳过，不要假装视频已发布。
- 如果用户允许生成图片或视频，可调用合适的生成类 skill 或让用户提供素材；确认前不要自动生成或上传。

## 主路径：publish 适配器

图文模式只有在至少有一张图片时才使用：

```bash
opencli xiaohongshu publish "<body>" --title "<title>" --images /abs/path/to/image.png -f json
```

视频模式先检查当前适配器是否支持视频参数：

```bash
opencli xiaohongshu publish --help
```

如果 help 明确支持视频，再使用当前版本给出的参数发布；如果不支持，按 `已填写待确认`、改图文、或跳过处理，不要宣称视频已发布。

## 缺素材分支

如果用户没提供目标模式需要的图片或视频，问用户三选一：

1. 生成或使用一份符合平台模式的图片/视频素材
2. 存为草稿（如果 OpenCLI 支持）
3. 跳过小红书，并在最终回报里标 `已跳过`

## 校验：creator notes

```bash
opencli xiaohongshu creator-notes --limit 5 -f json
```

成功标准：最新笔记里能匹配到新标题或正文片段。

如果最新笔记里没有新标题/内容，按 `未确认发布` 上报。
