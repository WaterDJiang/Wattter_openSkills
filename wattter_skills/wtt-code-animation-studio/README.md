# 代码动画工坊

输入一个想法、主题、文章或剧本，生成中文剧本、分镜、前端动画、配音和 MP4。时长由内容和实际旁白决定，不固定为 30 秒。动画由前端代码逐帧绘制，经浏览器和 FFmpeg 导出。

## 在 Codex / Claude Code 中使用

把本目录完整放入工具支持的 skills 目录，保留 `SKILL.md`、`scripts`、`assets`、`config`、`references`。本仓库已有安装工具，批量安装方法见仓库根 README；单独使用本 skill 不需要安装所有技能。

在对话里输入：

> 使用 wtt-code-animation-studio，把“一个人第一次学会骑自行车”的故事做成动画。面向成年人，温暖幽默，横屏，时长按内容决定。先推荐画风让我选，配音使用本机可用声音。

也可以提供文章、现成剧本或参考视频。一般内容会改编为可视化剧本；要求保留的原文或现成剧本按你的约束处理。编剧后提供一个推荐风格和两个备选，由你选定；已明确指定风格就直接沿用。人物可以由沙粒、粉笔或粒子呈现。

> 使用 wtt-code-animation-studio，介绍我的开源项目。采用沙画，用我配置好的本地个人音色，配置文件在项目的 `.voice-local/voice.local.json`。先生成一段试音，采用后再做整片。

## 第一次使用：检查模型和个人音色

首次制作会读取你已有的声音配置，检查模型文件、默认音色、参考录音、对应文字和 `referenceTextVerified`。新项目 `init` 自动检查；缺项会提醒具体要补什么，配置齐全则默认使用 `defaultVoice`，无需再次选择。

也可以手动检查（在本 Skill 目录执行）：

```sh
python3 scripts/voice.py doctor --project /path/to/my-film
# 指定已有配置时：
python3 scripts/voice.py doctor --project /path/to/my-film --config /path/to/voice.local.json
```

配置顺序：`--config` → `CODE_ANIMATION_VOICE_CONFIG` → 项目 `.voice-local/voice.local.json` → 用户 `~/.config/wtt-code-animation-studio/voice.local.json`。`config/voice.example.json` 是公开模板，不能把模板存在当作模型/音色已配置。

缺少配置时，参考 [配音使用指南](references/voice.md)：将模板复制到项目或用户级私人目录，填写模型路径与清单、参考录音和逐字文本；核对文字后设置 `referenceTextVerified: true`，再运行 `voice.py check`。声音模型目录和模板仍使用下面已有的 config 文件，不新增另一套配置。

首次检测只读本地配置和所指文件，不下载、不合成、不上传录音，不显示录音正文。`configured-unverified` 表示配置与文件已找到，完整 SHA256、录音格式与平台校验仍在正式 check/合成时执行。缺项提示不阻塞编剧和画面；无需个人音色时可继续使用原系统/外部配音路线，已指定个人音色却配置无效时会明确报错。

## 依赖与生成流程

- 视频：Python 3、Node.js、FFmpeg/FFprobe、Playwright、Chrome/Chromium。
- 默认画法：Canvas 2D；按镜头可引入本地固定版本的 p5.js。新增画风需要写对应场景代码，目录标签不是自动绘图引擎。
- 默认配音：自动使用已配置的 `defaultVoice`；未配置时 macOS 用 `say`，其他系统接入外部配音。
- 可选个人音色：Qwen3-TTS MLX，当前实测环境为 Apple Silicon Mac。无需为了普通动画先下载声音模型。

`film.json` 保存内容；`timeline.json` 根据实际配音编译；字幕按标点和字数近似分配，并非逐字强制对齐。每段配音变化后，都重新锁定时间轴和导出。

手动操作时，从本 skill 目录开始：

```sh
python3 scripts/pipeline.py init /path/to/my-film
```

先由 agent 按剧本改写项目内的 `film.json`、`scenes.js`，并记录风格选择。然后在项目目录执行：

```sh
npm install --save-exact playwright
npx playwright install chromium
python3 tools/pipeline.py tts .
# 完成全部选材，填写 assets.json 的素材、来源、许可、使用依据与网页导流
python3 tools/asset_review.py seal .
python3 tools/pipeline.py timeline . --lock
python3 tools/pipeline.py mix .
node tools/render.cjs . --preview
node tools/render.cjs . --render
python3 tools/pipeline.py finish .
```

已有 Chrome 时可以跳过 Chromium 安装。`tts .` 自动读取声音配置，无配置才用系统声音；外部音频跳过此步。已有音轨按原规则保留，不反复生成。显式 `tts . --voice Tingting --rate 205` 表示本次改用系统声音。详细配置、依赖与故障入口见 [制作契约](references/production.md)。

## 素材管理

首次制作由 Codex 搜索、下载和选材，素材确定后锁定版本。以后内容一致直接重跑；更换素材、来源、许可或导流时，先展示旧值、新值、原因和影响。未确认只保存候选，确认后才提交新版并重新渲染验收。已明确指定本次替换对象和目标不重复确认，仍保留 diff。没有三档模式，也没有额外开场模式选择。

只改代码不触发素材确认。不要直接覆盖已有素材或重新 seal；候选提议、精确授权、历史保存和旧工程迁移命令见 [素材审阅说明](references/material-review.md)。`init` 会把该说明复制为项目的 `ASSETS.md`。

## 检索模型与配置个人音色

相关文件只有三个入口：

| 文件 | 用途 |
|---|---|
| [model-catalog.json](config/model-catalog.json) | 公开模型来源、固定版本、用途、平台和实测状态；可离线检索 |
| [voice.example.json](config/voice.example.json) | 多模型路径、多音色、默认音色与生成参数的模板；不包含任何人的录音 |
| [配音使用指南](references/voice.md) | 下载模型、配置音色、生成试音、按镜头配音，以及 Windows/Linux 外部音频接法 |

```sh
python3 scripts/voice.py catalog --query 克隆
python3 scripts/voice.py scan --root /path/to/existing/models
python3 scripts/voice.py voices --config /path/to/voice.local.json
python3 scripts/voice.py voices --config /path/to/voice.local.json --query 旁白
```

`catalog` 是维护过的目录检索，不会联网搜索所有模型；`scan` 只读指定目录，不扫描整台电脑。扫描结果是候选，`check` 才验证固定版本与文件哈希。音色 ID 是你自己给参考录音起的名字，与模型 ID 分开配置。

最短上手路径：按 [配音指南](references/voice.md) 安装独立环境 → 下载模型或填已有模型路径 → 放入参考录音和逐字文本 → 核对后设 `referenceTextVerified: true` → 检查配置/按需试音 → 批量配音。配置了 `defaultVoice` 后，Skill 默认使用该音色，不再每次询问或要求先试音。已有个人配置不会因切换主题而重新生成。

## 交付与开源范围

交付中文剧本、分镜、风格选择记录、可编辑源码、配音、MP4 和检查记录。声音检查分为“文件可用 / 正文核对 / 本人音色相似度”，最后一项由本人试听决定。

可分享本目录中的代码、目录与示例配置；个人 `voice.local.json`、录音、文字、模型权重和 `.venv` 保存在项目 `.voice-local/` 或仓库外，不放入技能安装目录。附带忽略规则只防 Git 误加；**手工压缩目录前仍需排除这些文件**。不要把自己的配置覆盖到 `voice.example.json`。

模型与第三方依赖各自遵循原许可证，模型来源链接保存在目录中。当前仓库尚未附代码 LICENSE，公开发布前由维护者确定；本次未擅自添加许可证。当前已接入 Qwen3-TTS MLX 本地克隆；云服务、其他克隆模型、Windows/Linux 本地推理尚未内置。可选 Whisper 目录项用于转录核对，不是配音音色。

agent 执行入口见 [SKILL.md](SKILL.md)。
