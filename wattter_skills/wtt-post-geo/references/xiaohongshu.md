# 小红书发布流程

> 仅在用户明确点名「小红书」或要求「全平台」发布时加载此文件。

## 关键事实（实测）

- 小红书图文发布**必须有图**，视频笔记必须有视频素材；缺少图文素材时默认先生成 1-6 张 3:4 竖版 HTML PNG 图文卡，不需要单独询问。
- 缺图时不要默认跳过。默认按文章摘要生成 1-6 张 3:4 竖版图；用户明确跳过才跳过。
- 用户明确跳过小红书时立刻停止所有小红书相关尝试。
- `opencli xiaohongshu publish` 自报成功但没通过 `creator-notes` 校验时，不能宣称成功。
- 执行前必须使用 `references/content-format.md` 生成的 `platform_payloads.xiaohongshu`。长文必须先转为图文笔记版，缺图默认先生成 HTML PNG 图文卡。
- 涉及图文笔记时必须加载 `references/media-assets.md`，默认生成 `1080x1440` 竖版图片。

## 内容 payload 要求

```yaml
title: 小红书笔记标题
body: 短段落正文
media:
  images:
    - /abs/path/to/image.png
  videos:
    - /abs/path/to/video.mp4
media_plan:
  requested_outputs:
    - xhs_vertical_cards
  image_delivery:
    method: command_upload|browser_paste|manual_asset_ready
geo:
  visible_urls: []
  github_urls: []
  source_urls: []
tags:
  - 关键词
```

适配规则：

- 适合图文笔记、视频笔记、经验清单、短段落、强标题和标签。
- 图文模式必须至少有一张图片；视频模式必须至少有一个视频文件。
- 原文较长时，生成笔记版：开头一句场景钩子 + 3 到 6 个短要点 + 轻量结尾。
- 缺图时默认生成图文卡片：1 张封面 + 2 到 5 张要点卡。每张图只承载一个观点或步骤，避免把长文塞进图片。
- 小红书正文必须是短段落纯文本，不要保留 Markdown H1、`##`、`**`、`---`、HTML 注释或长链接堆叠。标题进入 `title` 字段，正文不要重复同名 H1。
- 标签只保留少量高相关关键词。正文里可以包含少量高相关标签，但标签必须先在 `tags` 字段维护，避免堆砌无关话题。
- 图片、封面和海报必须来自稳定可读路径；脚本临时目录或已清理的生成图不能作为发布素材。
- GEO 露出策略要克制：可以保留项目名、官网或 GitHub 字符串，但不要堆叠多条裸链。若平台发布后隐藏或拦截链接，最终回报应说明。
- 如果用户只给视频，优先按视频笔记适配；如果当前 OpenCLI 只支持图文发布，先让用户选择提取封面/改图文/跳过，不要假装视频已发布。
- 图文缺图时自动生成 HTML PNG 卡片；如果用户要求 AI 图、视频、写实图或插画，再调用合适的生成类 skill 或让用户提供素材。上传或发布前仍需按安全护栏确认。

## 主路径：publish 适配器

图文模式只有在至少有一张图片时才使用：

```bash
opencli xiaohongshu publish "<body>" --title "<title>" --images /abs/path/to/image.png \
  --trace retain-on-failure --keep-tab true -f json
```

视频模式先检查当前适配器是否支持视频参数：

```bash
opencli xiaohongshu publish --help
```

如果 help 明确支持视频，再使用当前版本给出的参数发布；如果不支持，按 `已填写待确认`、改图文、或跳过处理，不要宣称视频已发布。

## 缺素材分支

如果用户没提供图文模式需要的图片，默认直接生成 1-6 张 1080x1440 图文卡，再进入发布能力判断。

如果用户没提供视频模式需要的视频，或明确不希望自动生成图文卡，再问用户三选一：

1. 改成图文模式并生成 1080x1440 图文卡
2. 存为草稿（如果 OpenCLI 支持）
3. 跳过小红书，并在最终回报里标 `已跳过`

生成图文卡后仍要进入发布能力判断：OpenCLI `--images`、浏览器上传/粘贴、或 `manual_asset_ready`。如果图片已生成但自动上传失败，不能宣称小红书已发布。

## 校验：creator notes

```bash
opencli xiaohongshu creator-notes --limit 5 -f json
```

成功标准：最新笔记里能匹配到新标题或正文片段。

如果最新笔记里没有新标题/内容，按 `未确认发布` 上报。

### “发布成功但无法验证”分支

适配器出现 `发布成功 could not be verified`、提交后无跳转或图片桥警告时：

1. 本轮不再调用 `publish`，避免重复笔记。
2. 先查 `creator-notes`；同标题新作品存在并可回读才算 `已发布`。
3. 没有新作品时查 `drafts -f json`，匹配标题、图片数量和执行时间。
4. 找到草稿后执行 `draft-open <id>`；如果接口正文为空，继续用保留的发布 tab/浏览器编辑器核对正文，不能只凭标题与图片数算完整草稿。
5. 草稿标题和图片存在但正文无法回读时，结果记为 `filled/unknown`，用户看到 `已填写待确认`；不得记为 `已创建草稿`，也不得重试。

图片总 payload 触发浏览器桥/CDP 版本警告时，先保留失败 trace 和 tab，再按上面流程对账。升级浏览器桥属于工具变更，需要用户确认，不在发布中途自动升级。
