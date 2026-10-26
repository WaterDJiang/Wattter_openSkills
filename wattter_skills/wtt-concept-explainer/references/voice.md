# 配音与外部音色资源

本技能 `voice.py` 提供配置发现、模型检查、本地合成和模型目录管理；不调用另一 Skill。下面命令在初始化工程中执行；从本技能执行时将 `tools/` 改为 `scripts/`。

## 优先沿用已有配置

发现顺序：显式 `--config` / `--voice-config` → `CONCEPT_EXPLAINER_VOICE_CONFIG`（未设置时兼容 CODE_ANIMATION_VOICE_CONFIG）→ 项目 `.voice-local/voice.local.json` → 用户 `~/.config/wtt-concept-explainer/voice.local.json` → 可选兼容 `~/.config/wtt-code-animation-studio/voice.local.json`。

最后一个是已有用户数据路径，不是代码依赖。只读，不迁移、不覆盖；只安装本技能仍可独立配置新音色。配置中的模型/录音/文字路径相对**配置文件所在目录**，支持绝对路径和 `~`，不展开 shell 变量。

```sh
python3 tools/voice.py doctor --project .
python3 tools/pipeline.py tts .
```

- `defaultVoice` 有效时直接沿用，不逐片重新询问。可用 `--voice-id narrator-b` 临时选择已有音色；`--voice-config /path/to/voice.local.json` 显式指定数据入口。
- 默认选择配置旁 `.venv/bin/python`，否则用当前解释器。共用已有 Python 环境、权重和参考素材；不复制进 Skill 或公开工程。
- 坏配置、缺默认音色/权重或未核对参考文字会失败，不跳过高优先级配置或静默改声音。
- 没有任何配置时，macOS 可用系统 Tingting。显式系统声音：`python3 tools/pipeline.py tts . --voice Tingting --rate 205`；不能与克隆音色参数混用。非 macOS 没有系统 say 时按外部音频路线接入。

`doctor` 只读轻量检测：missing-config / needs-setup / configured-unverified；缺项仍可退出0，自动化须读取 status/issues。它不做推理、主观音色判断或完整大文件哈希验证，不代表声音已经可用。正式 check/合成执行严格验证。

## 配置一个新音色（仅缺少时）

本地克隆后端是 Qwen3-TTS Base / MLX，仅适用于支持 Metal 的 Apple Silicon。其他系统可接已有 TTS；不强制安装本后端。先复用已有虚拟环境和权重，缺少时才准备：

```sh
mkdir -p .voice-local/voices/my-voice
python3.12 -m venv .voice-local/.venv
.voice-local/.venv/bin/python -m pip install -r requirements-voice.txt
cp config/voice.example.json .voice-local/voice.local.json
```

模板沿用 `code-animation-voice/v1` 数据协议：models 填权重 path/manifest；voices 填模型 ID、referenceAudio、referenceTextFile、language；defaultVoice 指定默认音色。多音色可以指向同一份权重。

- 参考录音选单人、无配乐的完整语句；脚本接受3–30秒 PCM WAV。需要时用 FFmpeg 转为单声道24kHz；裁剪边界按实际句子决定，不套固定起止时间。
- referenceTextFile 写录音**实际说出的文字**，核对后才设 referenceTextVerified=true；不得用未照读的预设文案冒充。
- generation 支持 seed、temperature、maxTokens；Base 路线不接受 speed/instruct。达到 token 上限会报错，拆句或调整上限，不截断语音冒充完成。
- 不把实际配置/录音放到 Skill 的 assets/tests。新工程 .gitignore 排除 .voice-local、voice.local.json、模型与音频；分享前还需排除自定义位置的私人文件。

## 模型与验证

```sh
python3 tools/voice.py catalog --query 克隆
python3 tools/voice.py scan --root /path/to/existing/models
python3 tools/voice.py check --config .voice-local/voice.local.json --voice my-voice
```

已有权重和可靠 model-manifest.json 直接引用。scan 只发现候选；check 核对固定版本、文件哈希、平台、参考录音编码/时长和文字，不验证主观噪声或音色相似度。仅配置模型目录项不会增加推理后端；不能把 CustomVoice/VoiceDesign 权重冒充 Base。

确需下载时使用已有模型目录中的固定 revision：

```sh
.voice-local/.venv/bin/python tools/voice.py download --model qwen3-tts-1.7b-base-mlx --root .voice-local/models
```

下载命令只取公共模型文件，核对上游哈希并生成清单，不接收个人录音；不手写 verified 代替真实校验。依赖和模型继续遵循各自许可证。

## 合成与接入

整片 `pipeline.py tts .` 一次加载模型，按最终 narration 逐镜生成 WAV 与 `.wav.json` 文本/音频指纹。正式制作前完成脚本/构图确认；空旁白镜头跳过。可选单段试音：

```sh
.voice-local/.venv/bin/python tools/voice.py synthesize --config .voice-local/voice.local.json --voice my-voice --text-file /path/to/script.txt --out .voice-local/auditions/take-01.wav
```

本地合成开启离线并阻止 Python socket.connect；依赖/权重缺失时报错，不临时联网补下载。旁车记录版本与哈希，不写入私人参考逐字稿。输出拒绝覆盖；已有锁时先生成候选，不写当前音轨。

其他 TTS 或真人声音：保存每镜本地 WAV，填写 voice 路径，人工核对台词后标该镜 externalVoiceVerified=true；台词改变时撤销并重验。已有旧旁车不得冒充新声音；替换遵循素材审阅。

首次声音齐备后，将 WAV 与旁车登记 assets.json → seal → timeline --lock → mix → preview → render → finish。已有锁先 check；改音色/台词时生成候选并审阅后重锁。详见本技能 references/material-review.md，初始化项目对应 ASSETS.md。

技术检查与主观试听分别记录；不能把可解码写成音色/发音通过。没有真实声音时交付标为待配音，不将静音片当作带旁白成片。
