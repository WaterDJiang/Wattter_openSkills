# 模型检索与个人音色配置

本指南从一个已 `init` 的动画项目根目录执行，工具在 `tools/voice.py`。直接在 skill 根目录执行时将 `tools/voice.py` 替换为 `scripts/voice.py`。旧项目不会自动更新：可以直接用新版 skill 的脚本，`--project` 指向旧项目的新版本目录。

## 配置后默认使用

只要配置有效并设置 `defaultVoice`，Skill 自动使用它，不再逐片询问是否采用，也不强制重复试音。用户本次明确指定其他声音、外部音频或无旁白时按本次要求执行。

配置发现顺序（先找到者生效）：

- 显式 `--config`（voice.py）或 `--voice-config`（pipeline.py）。
- 环境变量 `CODE_ANIMATION_VOICE_CONFIG` 指向的配置。
- 项目 `.voice-local/voice.local.json`。
- 用户级 `~/.config/wtt-code-animation-studio/voice.local.json`。

项目配置只管该项目；在用户级路径保存一份有效配置，新项目即可默认沿用。也可将现有配置的绝对路径设为环境变量，避免移动录音。迁移配置文件位置时重新核对相对路径；不要将实际个人配置写回 Skill。

```sh
python3 tools/pipeline.py tts .
```

此命令自动选择 `defaultVoice`，优先用配置同目录 `.venv/bin/python`，否则用当前 Python（须安装声音依赖）。没有任何配置才使用系统 Tingting；发现坏配置、缺默认音色或缺权重时直接报错，不悄悄更换声音。克隆模式不接受系统专用 `--rate`。

本次覆盖而不修改默认设置：

```sh
python3 tools/pipeline.py tts . --voice-id narrator-b
python3 tools/pipeline.py tts . --voice Tingting --rate 205
```

第一条改用配置中另一克隆音色；第二条明确使用系统音色。两者不能同时指定。已有同名音轨仍按保护规则处理，切换声音使用新版本目录。旧工程的 tools 不会自动升级，可直接调用新版 Skill 的 pipeline.py。

## 选择配音路线

| 需求 | 路线 |
|---|---|
| 先做一支有声动画 | macOS `python3 tools/pipeline.py tts . --voice Tingting --rate 205`，不下载模型 |
| 用本人的声音，录音只在本地处理 | 本指南的 Qwen3-TTS 1.7B Base MLX；macOS Apple Silicon |
| Windows/Linux 或其他已有 TTS | 自行生成每镜 WAV，按下文外部音频入口接入；本脚本不自动切到云端 |

本地克隆是“参考录音 + 对应文字”条件合成，不是训练专属模型，也不需要为每个人重新下载一份权重。一个模型可配置多份音色。当前只接入目录中明确标为 TTS 的 Qwen3-TTS **Base**；不能用 CustomVoice/VoiceDesign 权重替换目录冒充同一能力。

## 准备隔离环境

先检查 `python3.12 --version`、`ffmpeg -version`、`ffprobe -version`。MLX 路线需要 Apple Silicon 和可访问的 Metal；单次 M1 Max / 64GB 实测峰值约 10.14GB，不代表最低内存要求或所有机器性能。

```sh
mkdir -p .voice-local/voices/my-voice
python3.12 -m venv .voice-local/.venv
.voice-local/.venv/bin/python -m pip install -r requirements-voice.txt
cp config/voice.example.json .voice-local/voice.local.json
```

目录结构：

```text
.voice-local/                    私有，不提交
  .venv/
  voice.local.json               从模板复制后修改
  models/qwen3-tts-1.7b-base-mlx/
    model-manifest.json
  voices/my-voice/
    reference.wav
    reference.txt
  auditions/
```

项目附带 `.gitignore` 排除这些数据。旧工程或单独复制脚本时，先在自己的忽略规则加入 `.voice-local/`、`voice.local.json`；其他位置的个人配置也须自行排除。不要把录音放入 skill 的 assets 或 tests。

## 检索、下载或复用模型

```sh
python3 tools/voice.py catalog --query 克隆
python3 tools/voice.py scan --root /path/to/existing/models
.voice-local/.venv/bin/python tools/voice.py download \
  --model qwen3-tts-1.7b-base-mlx --root .voice-local/models
```

下载约 4.54GB，使用目录中的固定 commit，下载后校验上游 LFS SHA256 / Git blob 并保存 `model-manifest.json`；下载失败会非零退出，保留下载缓存，重新运行同一命令继续。`download` 仅接收模型 ID 和保存目录，不接收录音或声音配置；模型下载需要联网，合成不需要。

已有模型可跳过下载，在配置 `models` 中填写实际 `path` 和 `manifest`。`scan` 仅报告包含 Qwen3-TTS config 的候选，不确认完整性；`check` 校验后才能使用。旧试音准备目录已有同格式清单时可直接复用；没有可靠清单时用下载命令建立固定版本副本，不手写“verified”假装通过。

目录来源：[MLX 模型页](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16)、[上游 Qwen 模型](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)、[MLX-Audio 使用说明](https://github.com/Blaizzy/mlx-audio/blob/main/docs/models/tts/qwen3-tts.md)。添加目录项前核对格式、许可证、参考音频支持及所需运行时；仅添加 JSON 不会自动添加新推理后端。

## 录音与配置

在安静环境录制正常说话的 20–40 秒原素材，然后选 10–20 秒完整连续句子。脚本接受 3–30 秒参考段，这是本工作流的检查范围。单人、无配乐、无变声；音量过低可适度增益，无须做强降噪。以下只转换格式，不改语速和音高：

```sh
ffmpeg -i /path/to/your-recording.m4a -ss 1.2 -t 15 \
  -ac 1 -ar 24000 -c:a pcm_s16le .voice-local/voices/my-voice/reference.wav
```

把 `-ss` 和 `-t` 改成实际句子边界，不能机械照用这两个数字。扩展名叫 wav 不代表实际为 PCM；命令会执行真正转换。将该片段**实际说出的每个字**保存为 UTF-8 `reference.txt`，试听核对后，把 `referenceTextVerified` 改为 `true`。不要把预先拟定但没有照读的稿子直接当参考文字。

可用录音文案：“最近，我在尝试把脑子里的想法做成动画。给它一个主题，它会先写剧本，再根据内容推荐画风，最后生成带声音的视频。”

配置中的路径相对于 **voice.local.json 所在目录**，不是执行命令的当前目录；也支持你自己的绝对路径和 `~`，不展开 shell 变量。模板中：

- `models`：模型 ID 对应权重目录及哈希清单；目录的固定 repo/revision 是版本依据。
- `voices`：音色 ID 对应模型、参考录音、参考文字和语言。复制 `my-voice` 条目可增加 `narrator-b` 等音色；共享同一模型路径。
- `defaultVoice`：配置后就是 Skill 的默认音色，不传覆盖参数时自动使用；不从其他项目猜音色。
- `generation`：固定 `seed`、`temperature`、`maxTokens`。不提供虚假的语速、情绪参数；本 Base 路线不接受 `speed`、`instruct`。达到 token 上限会报错，应拆分长镜头台词或调整上限。

```sh
python3 tools/voice.py voices --config .voice-local/voice.local.json
python3 tools/voice.py voices --config .voice-local/voice.local.json --query 旁白
python3 tools/voice.py check --config .voice-local/voice.local.json --voice my-voice
```

`check` 验证平台、配置、模型哈希、录音编码/时长和文字非空，不验证 GPU 加载、录音噪声或本人音色相似度；这些由下一步真实试音检查。缺文件、未核对文字、版本不符都会明确失败。可选 Whisper 只做辅助转录；历史测试遇到静音幻觉/重复标点，必须与录音核对，本入口不自动运行 ASR。

## 可选试音与整片配音

创建 `.voice-local/audition.txt`，写一段参考录音里**没有**的新文案：

> 这段声音来自本地合成。以后，只要修改剧本，就能为新的动画配上我的声音。

```sh
.voice-local/.venv/bin/python tools/voice.py synthesize \
  --config .voice-local/voice.local.json --voice my-voice \
  --text-file .voice-local/audition.txt --out .voice-local/auditions/take-01.wav
```

输出 WAV 和同名 `.wav.json`，记录模型版本、参考素材哈希、参数、时长与网络尝试，不把参考录音路径和逐字稿写入旁车。脚本设置 HF/Transformers offline 并阻止 Python socket.connect；遇到缺依赖、缺 tokenizer 或权重错误会失败，不自动联网补下载或上传音频。模型仍需已有的本地依赖才能运行。

试听音色、漏字、重复、停顿；技术检查不能代替主观判断。音量做静态峰值归一化至 -3 dBFS；视频最终响度由 `mix` 处理。第二次试音用 `take-02.wav`，命令拒绝覆盖旧文件。

新建音色可先试听再调整；已经配置默认音色就直接使用。确认 `film.json` 已是最终台词，在**尚无同名配音的新版本工程**中按镜头生成：

```sh
python3 tools/pipeline.py tts .
python3 tools/pipeline.py timeline . --lock
python3 tools/pipeline.py mix .
node tools/render.cjs . --preview
node tools/render.cjs . --render
python3 tools/pipeline.py finish .
```

一次载入模型，逐镜按 `narration` 和 `voice` 生成；空台词镜头跳过，缺省位置为 `audio/<镜头id>.wav`。生成的旁车与现有管线兼容，台词或声音文件变化会触发过期检查。先检查每镜配音再渲染。多角色需求可逐段 `--text-file/--out/--voice` 配音，同一轮 `--project` 使用同一个音色。

改音色/模型/参考录音/参数后生成**新的**配音与成片版本。拒绝覆盖是为了保留旧成果；部分镜头生成失败时已成功片段及记录保留，修复后可逐段补缺，不把整段语音塞进第一镜，也不强行加速匹配旧时间轴。

## 外部配音与发布

Windows/Linux 或其他 TTS：将每镜 WAV 放入项目，填写对应 `voice` 路径，核对台词后设置该镜 `externalVoiceVerified: true`。如已有旧 `.wav.json`，先备份旧音频及记录再登记新素材，不能让旧指纹冒充新配音。之后执行 `timeline --lock → mix → preview → render → finish`。

分享代码时保留示例配置，排除 `.voice-local`、其他个人配置、模型、录音及环境目录。给观众的视频和给开发者的源码包是不同交付物：带个人配音的成片按本人意愿发布；克隆参考素材不随开源包公开。模型与依赖遵循各自原许可证。

## 已锁定项目的声音变更

首次选材前可正常生成配音；WAV 和 `.wav.json` 旁车一并登记到 assets.json 再 seal。已经锁定的项目不能重新生成并覆盖当前 audio 文件；在 `.asset-review/candidates/批次/` 用 `synthesize --text-file ... --out ...` 生成候选，音频与旁车一起 propose。按素材审阅记录授权后 accept，再重锁时间轴、混音、渲染和验收。用户已明确指定音色/片段替换目标，记录该授权，不重复询问，仍展示 diff。

完整命令见 Skill 的 references/material-review.md，初始化项目内对应 ASSETS.md。模型和私人参考音色配置保留原目录，不复制进公共素材；入片音频才纳入版本历史。

## 首次使用检测

新项目 init 自动检查；已有项目执行 `python3 tools/voice.py doctor --project .`，或在 Skill 目录执行 `python3 scripts/voice.py doctor --project /path/to/project`。可加 `--config` 指定已有配置；优先级和 defaultVoice 规则保持不变。

- `missing-config`：未发现私人配置，按本指南从公开模板建立配置、填写模型和音色。
- `needs-setup`：配置存在问题或资源缺失，issues 列出模型、默认音色、录音/文字或核对标记的缺项。
- `configured-unverified`：默认音色对应的模型文件及参考文件存在；轻量检查核对模型清单版本、文件集合和大小，不读取大权重计算哈希，不解码参考录音。完整校验仍执行 `voice.py check`；同大小篡改由该命令及正式合成拒绝。

检测只看实际选中的默认音色及其模型，不要求配置里的其他备用音色全部可用。doctor 是提示命令，缺项也返回退出码 0，自动化程序读取 status/ issues；不能将退出码 0 当作可合成验收。已存在但无效的声音配置不会被跳过或降级。init 不写首次使用标记，避免陈旧缓存掩盖配置变化；同一会话未变化不重复提醒，修改配置后可再次运行。
