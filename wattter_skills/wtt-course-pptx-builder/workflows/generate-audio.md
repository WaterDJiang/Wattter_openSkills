---
description: 使用 AI 推荐的音色为每张幻灯片生成旁白音频，并按需重新导出嵌入音频的 PPTX
---

# 旁白音频生成工作流

> 独立的导出后步骤。当用户提出 `"生成音频"` / `"录制旁白"` / `"narrated PPT"` / `"video export with voice"`，或在一份 deck 导出后主动提供此选项时运行。默认通过 `edge-tts` 为每张幻灯片产出一个音频文件；当用户选择高质量旁白或克隆音色时，可改用云端 TTS provider（`elevenlabs` / `minimax` / `qwen` / `cosyvoice`），完成后按需重新导出嵌入音频、并按音频时长设置每页自动停留的"可放映" PPTX。

本工作流**独立运行**：它只读取 `notes/*.md` 并查询所选 TTS 音色目录——不依赖任何上游会话上下文。可放心在新会话中调用。

## 何时运行

- `notes/total.md` 已存在并已按页拆分为 `notes/*.md`（后期处理 Step 7.1 已完成）。
- 默认模式：`edge-tts` 已安装（`python3 -m pip install edge-tts`）。
- 本工作流仅在页面粒度运行：一份 notes 文件产出一个音频文件。不要试图使用单一长音轨或自动拆分长音频。
- PPT 旁白资源必须是 PowerPoint 兼容的音频：`m4a`（AAC）、`mp3` 或 `wav`。内置 TTS 路径默认输出 `mp3`；provider 自身的格式（如 `pcm`、`opus`、`flac`）在嵌入前必须转码。
- PowerPoint 的"录制旁白"导出依赖 `ffprobe`，以便按实际音频时长写入页面停留时间。
- 高质量云端模式：使用前必须已设置 provider API key：
  - ElevenLabs：`ELEVENLABS_API_KEY`
  - MiniMax：`MINIMAX_API_KEY`
  - Qwen：`QWEN_API_KEY` 或 `DASHSCOPE_API_KEY`
  - CosyVoice：`COSYVOICE_API_KEY` 或 `DASHSCOPE_API_KEY`
  - 密钥可放在当前进程环境变量中，或按以下顺序找到的第一个 `.env`：当前工作目录、skill 目录（如 `~/.agents/${SKILL_DIR}/.env`）、clone 出的仓库根目录、`~/.ppt-master/.env`
- deck 内容以单一主导语言为主（混合语言 deck：选择主导语言——AI 用判断而非启发式）。

若 `notes/*.md` 缺失，先运行 `total_md_split.py <project_path>`。

---

## Step 1：确定 deck 语言

AI 在写 notes 时就已经知道 deck 的语言，无需额外的检测脚本。

- 从 notes 内容中识别主语言：`zh` / `en` / `ja` / `ko` 等。
- 混合语言 deck（如中文夹英文术语）：选择受众听到最多的那种语言。
- 中文具体场景：根据上下文选择 locale——`zh-CN`（大陆普通话，默认）、`zh-TW`（台湾普通话）、`zh-HK`（粤语）。仅当项目上下文不清晰时才向用户询问。

---

## Step 2：选择音频后端并拉取音色目录

**默认 edge**，除非用户明确要求云端 provider / 更高质量的云端旁白 / 克隆音色。

**edge 后端**：

```bash
python3 ${SKILL_DIR}/scripts/notes_to_audio.py --list-voices --locale <locale>
```

**ElevenLabs 后端**：

```bash
python3 ${SKILL_DIR}/scripts/notes_to_audio.py --provider elevenlabs --list-voices
```

**使用显式 voice ID/名称的云端 provider**：

```bash
python3 ${SKILL_DIR}/scripts/notes_to_audio.py --provider minimax --list-voices
python3 ${SKILL_DIR}/scripts/notes_to_audio.py --provider qwen --list-voices
python3 ${SKILL_DIR}/scripts/notes_to_audio.py --provider cosyvoice --list-voices
```

输出是该 provider 全部可用音色的扁平列表。AI 从中挑选 **3–6 个候选** 进行推荐，遵循以下规则：

- **覆盖两种性别**（当 locale 同时存在两种时）。
- **edge**：当 locale 已有 `COMMON_VOICES` 清单（由 `notes_to_audio.py` 内置筛选）时，优先使用其中音色——它们经过实战检验。
- **ElevenLabs**：优先选择用户账号下已有的音色；若用户给出了具体的 `voice_id`，不要覆盖它。
- **MiniMax / Qwen / CosyVoice**：若用户提供克隆 `voice_id`，直接使用；不要在本工作流内尝试做音色克隆。
- **贴合 deck 调性** —— 按风格选出最强推荐：
  - Consultant / data-driven / 财报 → 稳重男声（如 `zh-CN-YunjianNeural`）or 清晰女声（如 `zh-CN-XiaoxiaoNeural`）
  - General / 教学 / 产品介绍 → 明亮女声 / 年轻男声（如 `zh-CN-XiaoyiNeural` / `zh-CN-YunxiNeural`）
  - 发布会 / 播报 → 播报感男声（如 `zh-CN-YunyangNeural`）
  - English consultant deck → `en-US-GuyNeural`（沉稳）or `en-US-JennyNeural`（清晰）
  - Japanese / Korean → 从 `ja-JP-*` / `ko-KR-*` 神经音色中挑选，并标注性别与调性

对每个候选，撰写**一行中文描述**包含：性别 · 调性 · 适用场景。云端 provider 须原样写出 voice 名称/ID（与传给 `--voice-id` 的字符串一致）。

---

## Step 3：一次性向用户提问（强制）

向用户发送单条消息，把三个问题一次性抛出，每项附推荐值。**不要**分轮追问。

**克隆音色快速通道**：若用户在消息里同时提到了"克隆音色" / "复刻音色" / `"my own voice"` 并给出了 `voice_id`，跳过音色推荐列表——把 provider 设为用户指定的那个（`elevenlabs` / `minimax` / `qwen` / `cosyvoice`），锁定用户给的 `voice_id`，仅再确认语速 + 是否嵌入。

**消息模板**（中文；若用户聊天语言不同则翻译过去）：

> 检测到 notes 主语言为 **<语言>**（locale：`<locale>`）。基于 deck 调性（<风格>），我推荐以下配置：
>
> **生成模式**：⭐ 推荐 `<edge|elevenlabs|minimax|qwen|cosyvoice>`（理由：<一句话，如"无需配置，稳定生成"或"用户要求高质量云端音色">）。
>
> **音色**：
> - **[1] <ShortName>** — <性别·调性·适用场景> ⭐ **推荐**
> - [2] <ShortName> — <性别·调性·适用场景>
> - [3] <ShortName> — <性别·调性·适用场景>
> - [4] <ShortName> — <性别·调性·适用场景>
> - [5] <ShortName> — <性别·调性·适用场景>
> - 也可直接输入清单中的其他 ShortName。
>
> **语速/风格参数**：⭐ 推荐 `<rate 或 provider 默认>`（理由：<一句话，如"页均 2–3 句，正常语速听感最稳"或"ElevenLabs 默认 voice settings 保留音色原始表现最稳">）。
>
> **生成完是否重新导出嵌入音频的 PPTX**：⭐ 推荐 **是**（一次到位，自动按音频时长设页面停留）。
>
> 直接回"好"用全部推荐值，或告诉我想改的部分（如"音色 2，语速 -5%"或"用 MiniMax 的 voice_id xxx"）。

**推荐值规则**：
- 生成模式：默认 `edge`；当用户明确追求高质量云端音色或提供 cloud voice ID 时，按用户指定选 `elevenlabs` / `minimax` / `qwen` / `cosyvoice`。
- 音色：从 Step 2 候选里挑最贴合 deck 调性的那一个。
- 语速：edge 默认 `+0%`；notes 字数密集（页均 >4 句长句）建议 `-5%`；notes 简短紧凑建议 `+5%`；超出此范围需说明理由。云端 provider 默认使用 provider defaults，除非用户明确要调速或改风格。
- 嵌入：默认推荐"是"；除非用户已有定制 PPTX 不希望覆盖。

---

## Step 4：执行（不再追问）

按顺序执行——**不要**合并：

```bash
# 1A. 使用 edge 生成音频（默认）
python3 ${SKILL_DIR}/scripts/notes_to_audio.py <project_path> \
  --voice <chosen-ShortName> --rate <chosen-rate>

# 1B. 或使用 ElevenLabs 生成音频
python3 ${SKILL_DIR}/scripts/notes_to_audio.py <project_path> \
  --provider elevenlabs --voice-id <chosen-voice-id> \
  --elevenlabs-model eleven_multilingual_v2

# 1C. 或使用 MiniMax 生成音频
# 默认指向国内 endpoint；海外访问需设置 MINIMAX_TTS_BASE_URL=https://api.minimax.io/v1/t2a_v2
python3 ${SKILL_DIR}/scripts/notes_to_audio.py <project_path> \
  --provider minimax --voice-id <chosen-voice-id> \
  --minimax-model speech-2.8-hd

# 1D. 或使用 Qwen TTS 生成音频
python3 ${SKILL_DIR}/scripts/notes_to_audio.py <project_path> \
  --provider qwen --voice-id <chosen-voice> \
  --qwen-model qwen3-tts-flash --qwen-language-type Chinese

# 1E. 或使用 CosyVoice 生成音频
python3 ${SKILL_DIR}/scripts/notes_to_audio.py <project_path> \
  --provider cosyvoice --voice-id <chosen-voice> \
  --cosyvoice-model cosyvoice-v3-flash

# 2.（若用户选择嵌入）重新导出嵌入音频的 PPTX
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> \
  --recorded-narration audio
```

若 `notes_to_audio.py` 因依赖缺失或 provider API key 缺失而报错，请修复前置条件后重跑——**不要**吞掉错误。

`--recorded-narration audio` 会准备 PowerPoint 的录制时长与旁白：每张幻灯片都必须有匹配的支持音频文件，每段时长都必须能被 `ffprobe` 读取，且对象动画不能使用 `--animation-trigger on-click`。旁白/视频导出请使用 `after-previous` 或 `with-previous`。

---

## Step 5：完成报告

输出一份汇总块，列出：

- 生成的音频文件数量与位置（`<project_path>/audio/*`）。
- 实际使用的 provider、音色、语速/参数。
- （若嵌入）`<project_path>/exports/` 下新生成的带旁白 PPTX 路径。
- （若跳过嵌入）一行提示，告知后续如何嵌入：`python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> --recorded-narration audio`。