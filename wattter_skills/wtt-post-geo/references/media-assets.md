# 媒体资产与配图策略

> 任何目标平台需要封面、正文图、图文笔记、视频封面，或用户要求“配图/海报/插图/生成图”时加载此文件。

## 目标

先把图片资产做成稳定、可复用的本地文件，再按平台能力决定自动上传、浏览器粘贴、创建草稿后人工补图，或跳过。

不要把“生成图片”和“发布图片”混在同一步里。图片生成成功不等于平台已插入成功，必须分别校验。

## 输出目录

生成或整理后的图片统一落到稳定目录：

```text
~/Downloads/wtt-publish-assets/YYYYMMDD-article-slug/
```

不要把 `/tmp`、`/var/folders`、脚本临时目录、已清理的下载文件放进最终 payload。

只为本次实际目标平台准备素材。用户已排除公众号、Twitter 或小红书时，不生成它们的封面、卡片或配图。

## 默认尺寸

| 用途 | 默认尺寸 | 说明 |
|---|---:|---|
| 公众号封面 | 900x383 | 公众号常用 2.35:1 封面 |
| 公众号/知乎正文图 | 1920x1080 | 文章内说明图、流程图、概念图 |
| 微博配图 | 1200x900 | 信息卡或摘要海报 |
| 小红书图文 | 1080x1440 | 3:4 竖版图，建议 1-6 张 |
| 通用缩略图 | 1200x1200 | 方图备用 |

如果用户已提供平台指定尺寸，优先使用用户素材；否则按上表生成。

## 默认生成策略

配套图片生成不需要单独询问。只要目标平台需要封面、正文图、微博信息卡或小红书图文卡，默认直接用 **HTML -> Playwright -> PNG** 生成稳定图片文件，再进入平台上传/粘贴/人工补图判断。

生成路径优先级：

1. **HTML -> Playwright -> PNG**：默认可控路径。参考 `wtt-post-multi-platform` 的微信海报生成思路和 HTML 视觉风格，只借鉴其模板渲染成图片的能力；不要把该 skill 当作图片发布入口。
2. **已有本地图片**：检查绝对路径、文件存在、尺寸、大小和平台格式；用户素材优先于自动生成图。
3. **图片生成类 skill/API**：只有用户明确要求 AI 图、写实图、插画或视频封面时再调用，如 `wtt-jimeng-api`。
4. **提示词型图片 skill**：如只输出提示词，不能视为已获得可发布图片；必须等待用户提供落盘图片路径。

## 生成失败时的内置图片回退

文章专属 HTML -> PNG 生成不可用、渲染依赖缺失或产物尺寸不对时，使用 skill 内置的中性通用图：

| 用途 | 内置图 |
|---|---|
| 公众号封面 | `assets/default-images/weixin-cover.png` |
| 微博配图 | `assets/default-images/social-landscape.png` |
| 通用方图 | `assets/default-images/universal-square.png` |
| 小红书竖图 | `assets/default-images/xiaohongshu-portrait.png` |

选图必须通过脚本，不手工猜尺寸：

```bash
python3 scripts/select-publish-image.py \
  --use-case weixin_cover \
  --preferred /abs/generated/article-cover.png
```

返回 `source: article_specific` 表示文章专属图尺寸正确；返回 `source: bundled_default` 时，必须把 `fallback_reason` 写入 `media_plan`。内置图只解决“有稳定图片文件”，不代表平台已上传成功。

需要重建内置图时运行 `python3 scripts/generate-default-images.py`。输出必须与 `assets/default-images/manifest.json` 的尺寸一致。

HTML 渲染图应优先做信息型海报：标题、3-6 个要点、流程/对比/清单结构。不要生成只好看但无法承载文章信息的装饰图。

## HTML 视觉风格

默认参考 `wtt-post-multi-platform/platforms/wechat/templates/poster-templates.html` 的微信海报风格，同时吸收 `wtt-course-pptx-builder` 的 HTML 背景模板方法：先选风格模板，再注入主题色和内容结构，最后渲染为 PNG。

### 默认色彩

- 唯一点缀色：克莱因蓝 `#002FA7`。不得再引入红、橙、绿、紫、其他蓝色或彩色渐变作为点缀。
- 图片文字颜色：标题、正文、说明文字使用黑、深灰、灰等中性色；不要用第二种蓝色代替正文色。
- 背景：优先白、纸感白、浅灰或低饱和中性底；避免大面积纯蓝导致信息不可读。
- 点缀用法是硬约束：克莱因蓝必须极其克制，只用于标点符号、关键词、编号、短横线、细边框、角标、流程节点、小面积 icon 或微小几何标记。不得用作大面积底色、主背景、大块面板、整栏色块、全幅渐变或整张图的主视觉色。
- 面积约束：单张图中克莱因蓝可视面积建议低于 5%，最多不超过 10%。如果模板原本使用大面积钴蓝/蓝色块，必须改成白/浅灰/中性底，用克莱因蓝只保留边线、编号、标点或关键词。

### 基础视觉语言

- 模板类型：封面大标题、左右对比、时间线/流程。
- 视觉语言：中性纸感背景、深色主文字、克莱因蓝关键词/标点/编号、清晰数字编号、信息分组。
- 字体层级：大标题短而有力，副标题/说明控制在 1-3 行，要点列表每项尽量短。
- 版式约束：不要用纯装饰背景；每张图必须承载一个可读信息结构。
- 输出质量：PNG，清晰度优先，避免小字号密集正文。

### 配套模板库

生成配图时从下表选一个模板，不要所有文章都使用同一种卡片：

| 模板 | 借鉴来源 | 适合内容 | 结构 |
|---|---|---|---|
| `wechat-cover` | `wtt-post-multi-platform` 封面模板 | 公众号封面、文章核心观点 | 大标题 + 副标题 + 日期/标签，克莱因蓝短线或角标 |
| `wechat-compare` | `wtt-post-multi-platform` 对比模板 | 前后对比、方案对比、收益对比 | 左右双栏 + 编号列表 + 克莱因蓝关键词 |
| `wechat-timeline` | `wtt-post-multi-platform` 时间线模板 | 流程、发布步骤、路线图 | 纵向/横向时间线 + 节点说明 |
| `editorial-rule` | `wtt-course-pptx-builder` `editorial-rule` | 深度文章、学术/咨询、GEO 解释 | 大留白 + 顶部色带 + 发丝线 + 稳重标题 |
| `gradient-panel` | `wtt-course-pptx-builder` `gradient-panel` | 通用商务、方法论总结 | 中性浅底 + 内容面板 + 克莱因蓝角落几何强调；不得保留彩色渐变 |
| `geometric-mesh` | `wtt-course-pptx-builder` `geometric-mesh` | AI、SaaS、技术架构、工具教程 | 对角分割 + 网格/chevron motif + 强标题 |
| `cobalt-studio` | `wtt-course-pptx-builder` `cobalt-studio` | 产品故事、品牌发布、强观点封面 | 借其强对比结构和 edge bar，不照搬大面积蓝底；克莱因蓝只做局部标记 |
| `macaron-soft` | `wtt-course-pptx-builder` `macaron-soft` | 小红书、轻知识、生活方式 | 中性柔和底 + 顶部 pill chip；点缀仍只用克莱因蓝 |
| `bone-archival` | `wtt-course-pptx-builder` `bone-archival` | 档案感、历史脉络、纪实案例 | 骨色底 + 标签系统 + 复古编号/章标题 |

选择规则：

- 公众号封面默认 `wechat-cover` 或 `editorial-rule`。
- 公众号/知乎正文图默认 `editorial-rule`、`gradient-panel` 或 `geometric-mesh`。
- 微博摘要图默认 `wechat-compare` 或 `gradient-panel`。
- 小红书图文默认 `macaron-soft`；科技教程可以改 `geometric-mesh`。
- 产品发布、强观点、工具介绍可以用 `cobalt-studio`。
- 叙事、复盘、历史脉络可以用 `bone-archival` 或 `wechat-timeline`。

### 生成约束

- 借鉴 `wtt-course-pptx-builder` 的“模板变量注入”思路：模板结构和主题色分离，内容只填入标题、要点、标签、日期、来源。
- 借鉴 `wtt-course-pptx-builder` 的“图表只借结构、不借皮肤”原则：可以借用流程图/对比图/时间线结构，但必须统一改成当前媒体资产色板，默认以克莱因蓝为点缀。
- 借鉴其“anchor / dense / breathing”节奏：封面和章节图用 `anchor`，信息密集图用 `dense`，金句/观点图用 `breathing`。
- 每张图最多承载一个叙事目标。超过 6 个要点时拆成多张图，不要缩小字号硬塞。

## 图片发布能力分层

每个平台图片处理都必须先归类到以下能力之一：

```yaml
image_delivery:
  method: command_upload|browser_upload|browser_paste|api_upload|manual_asset_ready|unsupported
  status: ready|needs_probe|blocked|done
  evidence: []
```

- `command_upload`：OpenCLI 命令参数上传，如 `--images`、`--cover-image`。只有当前版本实测成功才使用。
- `browser_upload`：通过 `opencli browser <session> upload` 把绝对路径文件交给平台原生 file input。上传后必须用编辑器文本、预览或真实图片节点确认素材已插入正确位置。
- `browser_paste`：打开平台编辑器后，用浏览器复制粘贴图片、HTML 或富文本。执行前必须做最小能力探测，并在发布前用编辑器 extract/预览确认图片存在。注意 HTML 富文本粘贴成功不等于图片粘贴成功；图片要单独验证 `img` 数量或预览。
- `api_upload`：平台 API 上传素材并写入草稿。需要配置、凭证、IP 白名单和 API 返回值校验。
- `manual_asset_ready`：已生成稳定图片文件，但当前自动插入不通。创建文本/草稿后回报图片路径和人工补图动作。
- `unsupported`：当前平台或账号路径不支持该媒体类型。

## 浏览器上传/粘贴探测

当命令上传图片失败，且平台有网页编辑器时，可以探测 `browser_upload` 或 `browser_paste`，但不要绕过平台风控。

探测顺序：

1. 打开目标编辑器页面并确认登录账号。
2. 找到正文编辑器或上传控件。
3. 如果存在可识别的 file input，优先用 `opencli browser <session> upload <target> <absolute-path>`，并验证插入位置与平台托管 URL。
4. file input 不可用时，再尝试平台允许的粘贴方式：HTML 片段、富文本、或图片剪贴板。图片剪贴板优先用 `scripts/weixin-image-clipboard-js.mjs` 这类脚本把本地图片写入浏览器剪贴板，再通过 `Meta+V` / `Control+V` 触发平台原生粘贴上传。
5. 用 `opencli browser <session> extract`、页面预览、草稿列表或编辑器 DOM 确认图片出现。
6. 只有探测成功，才继续执行正式图片插入；否则降级为 `manual_asset_ready`。

遇到验证码、异常登录、频控、上传审核弹窗、权限拒绝时立刻停止，按 `已填写待确认` 或 `未完成` 回报。

## 一次性素材计划

全平台发布前，自动形成素材计划并直接生成缺失的 HTML PNG 配套图：

- 哪些平台缺图，已生成哪些尺寸和张数。
- 哪些平台会尝试自动插图。
- 哪些平台可能只创建草稿并要求人工补图。
- 哪些动作涉及外部写入或浏览器操作，需要用户确认后再执行：上传素材、打开浏览器编辑器探测粘贴、创建草稿、真实发布。

不要在每个平台执行到一半时反复追问素材生成策略。生成图片本身是本地文件准备动作，默认执行；平台写入动作仍按安全护栏处理。
