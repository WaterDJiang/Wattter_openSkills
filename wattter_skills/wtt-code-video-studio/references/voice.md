# 个人音色、角色与逐句表演

以下命令以已有工程及其`tools/voice.py`为例；在Skill根目录执行时使用`scripts/voice.py`。单句试音不需要初始化视频工程，纯声音小样也不执行视频四帧门。旧项目工具不会自动更新，升级须同时带上`speech.py`，见[兼容说明](migration.md#多人配音迁移)。

## 配置后默认使用

只要配置有效并设置 `defaultVoice`，Skill 自动使用它，不再逐片询问是否采用，也不强制重复试音。用户本次明确指定其他声音、外部音频或无旁白时按本次要求执行。

配置发现顺序（高优先级无效必须报错，不跳过）：

- 显式 `--config`（voice.py）或 `--voice-config`（pipeline.py）。
- `CODE_VIDEO_VOICE_CONFIG`。
- 兼容 `CODE_ANIMATION_VOICE_CONFIG` / `CONCEPT_EXPLAINER_VOICE_CONFIG`；同时设置却指向不同文件时报冲突。
- 项目 `.voice-local/voice.local.json`。
- 用户 `~/.config/wtt-code-video-studio/voice.local.json`。
- 旧用户目录 `~/.config/wtt-code-animation-studio/voice.local.json` 或 `~/.config/wtt-concept-explainer/voice.local.json`。同时存在不同文件时报冲突；不会根据内容猜用户更喜欢哪个音色。

存在冲突时用显式路径或新环境变量选定；兼容发现只读旧配置，不自动移动录音、权重或写回旧文件。用户授权的路径修复按下方恢复流程另行备份执行。两个路径解析为同一文件可继续。

项目配置只管该项目；在用户级路径保存一份有效配置，新项目即可默认沿用。也可将现有配置的绝对路径设为环境变量，避免移动录音。迁移配置文件位置时重新核对相对路径；不要将实际个人配置写回 Skill。

```sh
python3 tools/pipeline.py tts .
```

此命令自动选择`defaultVoice`，优先用配置同目录`.venv/bin/python`，否则用当前Python（须安装声音依赖）。旧单旁白工程没有任何配置才使用系统Tingting；发现坏配置、缺默认音色或缺权重时直接报错，不悄悄更换声音。多角色项目缺配置或显式选择系统say时拒绝执行，不能静默降成一个声音。本地Qwen路线不接受系统专用`--rate`。

本次覆盖而不修改默认设置：

```sh
python3 tools/pipeline.py tts . --voice-id narrator-b
python3 tools/pipeline.py tts . --voice Tingting --rate 205
```

第一条覆盖默认音色，显式cast绑定仍按各角色执行；第二条明确使用系统音色，仅适用于旧单旁白。两者不能同时指定。已有同名音轨仍按保护规则处理，切换声音使用新版本目录。旧工程的tools不会自动升级，可从完整新版Skill调用pipeline.py，或按兼容说明同步依赖。

## 配置存在但路径失效

- 先运行`python3 tools/voice.py doctor --project .`；缺路径只说明原路径不可用，不断言文件已删除。doctor检查相邻.venv及失效软链，但不加载模型或认证当前Python依赖。`Path.exists()`不识别失效软链，查环境时同时用`is_symlink()`或`ls -ld`，不直接在原软链上执行venv创建。
- 用户要求查找或本次恢复需要时，先查配置的原目录、用户配置/数据目录、相关旧项目和已知模型缓存，再按用户提供的范围扩展Downloads/Documents/外接卷；逐次指定目录，不每次做片全盘扫描。模型用`voice.py scan --root /path/to/models`找候选，录音/文字先按旧配置、原文件名和旧TTS旁车追溯，不打印私人逐字稿。
- 用旧成功TTS旁车中的referenceAudioSha256、referenceTextSha256核对找到的录音和逐字稿，匹配后再认定同一参考。仅文件名/声音标签相同不足以认定；无旧哈希则核对录音对应文字和本人身份，仍有多个候选不能确定时只询问未决项。保持referenceTextVerified的真实依据。
- 找到模型先check固定repo/revision、完整文件和哈希，不拿ASR/CustomVoice替代Base。确认搜索范围内没找到可复用权重后，再按已授权的本地声音恢复任务显式执行原模型固定revision下载；普通init/doctor不下载、不上传录音。下载失败保留日志/缓存，不手写清单冒充通过。
- 长期用户资源可放`~/.local/share/wtt-code-video-studio/`下的models、voices和.venv；不依赖易清理的outputs或安装副本。参考录音若另存稳定位置须保持SHA一致，原文件保留。先备份原配置及软链本身，再只更新已确定的模型/参考路径或环境指向；保留defaultVoice、生成参数和已核对标记，不另建冲突的高优先级配置。
- 修复后doctor→完整check→真实短句合成，分别报告路径完整、模型哈希通过、实际生成成功、听感待判断。重用既有获批画面时按[纯音轨修订](audio-revision.md)，不用恢复音色的授权扩大成画面改动或发布。

## 选择配音路线

| 需求 | 路线 |
|---|---|
| 先做单旁白有声动画 | macOS `python3 tools/pipeline.py tts . --voice Tingting --rate 205`，不下载模型 |
| 用本人的声音，录音只在本地处理 | 本指南的 Qwen3-TTS 1.7B Base MLX；macOS Apple Silicon |
| 两个虚构角色、逐句语气变化 | Qwen3-TTS 1.7B CustomVoice MLX；固定speaker和逐句instruct，不要求参考录音 |
| Windows/Linux 或其他已有 TTS | 自行生成每镜 WAV，按下文外部音频入口接入；本脚本不自动切到云端 |

Base本地克隆使用“参考录音+对应文字”，不是训练专属模型；一个模型可配置多份音色。当前Base路线不接受非空instruct，不承诺靠一段平静录音就能稳定执行强情绪指令。

CustomVoice使用固定speaker，逐句接受自然语言instruct。同一角色绑定同一voiceId，语气改变时不换speaker。两种权重各用自己的目录和模型ID，不能互相替换冒充同一能力。VoiceDesign、IndexTTS及其他路线不属于本轮已接入能力；模型参数支持和实际听感效果分别核对。

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
  models/qwen3-tts-1.7b-customvoice-mlx/  选择固定角色声线时配置
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
python3 tools/voice.py catalog --query CustomVoice
python3 tools/voice.py scan --root /path/to/existing/models
.voice-local/.venv/bin/python tools/voice.py download \
  --model qwen3-tts-1.7b-base-mlx --root .voice-local/models
```

需要固定角色声线时，将下载命令中的model改为`qwen3-tts-1.7b-customvoice-mlx`。Base下载约4.54GB，各模型的固定commit与大小以[模型目录](../config/model-catalog.json)为准。下载后校验上游LFS SHA256/Git blob并保存`model-manifest.json`；下载失败非零退出，保留缓存，重新运行同一命令继续。`download`不接收录音或声音配置；模型下载需要联网，合成不需要。

已有模型可跳过下载，在配置 `models` 中填写实际 `path` 和 `manifest`。`scan` 仅报告包含 Qwen3-TTS config 的候选，不确认完整性；`check` 校验后才能使用。旧试音准备目录已有同格式清单时可直接复用；没有可靠清单时用下载命令建立固定版本副本，不手写“verified”假装通过。

目录来源：[MLX 模型页](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16)、[上游 Qwen 模型](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)、[MLX-Audio 使用说明](https://github.com/Blaizzy/mlx-audio/blob/main/docs/models/tts/qwen3-tts.md)。添加目录项前核对格式、许可证、参考音频支持及所需运行时；仅添加 JSON 不会自动添加新推理后端。

## Base参考录音与配置

在安静环境录制正常说话的 20–40 秒原素材，然后选 10–20 秒完整连续句子。脚本接受 3–30 秒参考段，这是本工作流的检查范围。单人、无配乐、无变声；音量过低可适度增益，无须做强降噪。以下只转换格式，不改语速和音高：

```sh
ffmpeg -i /path/to/your-recording.m4a -ss 1.2 -t 15 \
  -ac 1 -ar 24000 -c:a pcm_s16le .voice-local/voices/my-voice/reference.wav
```

把 `-ss` 和 `-t` 改成实际句子边界，不能机械照用这两个数字。扩展名叫 wav 不代表实际为 PCM；命令会执行真正转换。将该片段**实际说出的每个字**保存为 UTF-8 `reference.txt`，试听核对后，把 `referenceTextVerified` 改为 `true`。不要把预先拟定但没有照读的稿子直接当参考文字。

可用录音文案：“最近，我在尝试把脑子里的想法做成动画。给它一个主题，它会先写剧本，再根据内容推荐画风，最后生成带声音的视频。”

配置中的路径相对于 **voice.local.json 所在目录**，不是执行命令的当前目录；也支持你自己的绝对路径和 `~`，不展开 shell 变量。模板中：

- `models`：模型 ID 对应权重目录及哈希清单；目录的固定 repo/revision 是版本依据。
- `voices`：Base音色条目包含参考录音、参考文字、核对标记；CustomVoice条目包含speaker，例如`vivian`或`uncle_fu`，不要求referenceAudio/referenceTextFile。两者均填写model、label、language；同模型可共享权重路径。
- `defaultVoice`：配置后就是 Skill 的默认音色，不传覆盖参数时自动使用；不从其他项目猜音色。
- `generation`：只配置seed、temperature、maxTokens；不要塞入speed、emotion或instruct。逐句表演放在话轮的performance.instruct中，Base遇到非空指令会报错。达到token上限时拆分台词或调整上限，不交付被截断的声音。

[公开配置示例](../config/voice.example.json)保留defaultVoice=my-voice，并演示actor-a/Vivian、actor-b/Uncle Fu。只复制到私人配置再填写本机路径，不将个人录音、模型或实际私人路径写回Skill。未使用的备用角色不要求全部配置完毕；使用前核对其模型和声线。

```sh
python3 tools/voice.py voices --config .voice-local/voice.local.json
python3 tools/voice.py voices --config .voice-local/voice.local.json --query 旁白
python3 tools/voice.py check --config .voice-local/voice.local.json --voice my-voice
```

`check`验证平台、配置与模型哈希；Base另查参考录音编码/时长及文字，CustomVoice查speaker及对应模型能力。它不证明GPU加载、音色相似度或情绪听感通过；缺文件、未核对参考文字、未知speaker或版本不符均失败。可选Whisper只做辅助转录，不能代替本人核对，本入口不自动运行ASR。

## 角色绑定与表演计划

先从剧本识别谁真正发声，再建立cast；只出镜的角色不额外配音。旁白默认沿用本人音色，其他角色按剧情中的声线身份、年龄感、质感和说话习惯匹配已配置voiceId，不逐句随机换声。

每句话分开记录text与performance。instruct是实际交给CustomVoice的表演提示；intent只是编剧记录，不能当作模型已执行的情绪参数。先定一段的情绪变化，再在转折句安排变化，不机械为每句追加夸张标签。未知角色、未配置音色或不支持的指令都明确失败，不忽略参数、不悄悄换回旁白。

约10秒的三声四话轮示例，写入film.json中一个镜头；完整字段与互斥规则见[制作契约](production.md#角色与逐句话轮)：

```json
{
  "cast": {
    "narrator": {"label": "旁白"},
    "a": {"voiceId": "actor-a", "label": "角色A"},
    "b": {"voiceId": "actor-b", "label": "角色B"}
  },
  "scenes": [{
    "id": "encounter",
    "visualSeconds": 10,
    "utterances": [
      {"id": "opening", "speakerId": "narrator", "text": "听，故事开口了。", "voice": "audio/opening.wav", "pauseAfterSeconds": 0.2},
      {"id": "a-question", "speakerId": "a", "text": "是你吗？", "voice": "audio/a-question.wav", "performance": {"instruct": "轻声询问，带一点疑问。", "intent": "确认来人身份"}, "pauseAfterSeconds": 0.2},
      {"id": "b-answer", "speakerId": "b", "text": "是我，别怕。", "voice": "audio/b-answer.wav", "performance": {"instruct": "低沉温和，安慰对方。"}, "pauseAfterSeconds": 0.2},
      {"id": "a-joy", "speakerId": "a", "text": "太好了！", "voice": "audio/a-joy.wav", "performance": {"instruct": "由释然转为欣喜，自然地说。"}}
    ]
  }]
}
```

这个片段是内容预算，不承诺任意机器合成都正好10秒。以实际WAV安排停顿和收尾；不足可补自然停顿/尾部，超出时缩短台词生成新take，不加速或裁剪台词。同一角色A的两句使用同一voiceId，只有表演指令变化。纯音频交付WAV、逐句来源/参数与试听状态，不为它创建四个视频时间点。

同镜多人对白按utterances顺序合成与锁时，不要求换说话人就切镜；初版不支持抢话或重叠。字幕带speakerId/utteranceId，并在各句实际声音区间内按字符近似定位。runtime提供activeSpeakerId/activeUtteranceId供场景决定角色高亮或表情，未实现嘴部动画时不声称精确口型。

## 可选试音与整片配音

创建 `.voice-local/audition.txt`，写一段参考录音里**没有**的新文案：

> 这段声音来自本地合成。以后，只要修改剧本，就能为新的动画配上我的声音。

```sh
.voice-local/.venv/bin/python tools/voice.py synthesize \
  --config .voice-local/voice.local.json --voice my-voice \
  --text-file .voice-local/audition.txt --out .voice-local/auditions/take-01.wav
```

单句CustomVoice可显式给表演指令；actor-a.txt只写实际台词，不写表演标签：

```sh
.voice-local/.venv/bin/python tools/voice.py synthesize \
  --config .voice-local/voice.local.json --voice actor-a \
  --instruct '轻声询问，带一点疑问。' \
  --text-file .voice-local/actor-a.txt --out .voice-local/auditions/actor-a-question.wav
```

项目模式从各话轮performance读取指令，不使用全局--instruct。

输出WAV和同名`.wav.json`，记录模型版本、声线、实际参数、时长与网络尝试；Base另记参考素材哈希，不把私人参考录音路径和逐字稿写入旁车。新话轮记录speakerId、utteranceId、performance及speechRequestSha256，完整TTS配置指纹用于复用校验。脚本设置HF/Transformers offline并阻止Python socket.connect；缺依赖、tokenizer或权重时失败，不自动联网补下载或上传音频。

试听音色身份、漏字、重复、停顿和情绪转折，技术检查不能代替主观判断。只有峰值超过-3dBFS时才衰减到上限，不把每句音量统一抬升；最终混音另行处理，音量变化不等于情绪变化。第二次不同试音用take-02.wav，不覆盖旧take；完整请求和参数一致时可复用已核对输出。

新建角色或调整表演时可做短声音小样；已有默认音色直接使用，不新增每片强制试听审批。film.json确定后，在新版本工程中生成：

```sh
python3 tools/pipeline.py tts .
```

旧单旁白按narration与voice生成；新对白按cast与utterances逐句选声线和指令，不把一个全局音色套给所有角色。同一权重可复用，参考/声线按角色切换。新增话轮seed由稳定id派生，不依赖句子在列表中的位置。

改文本、角色、声线、表演、模型/版本、参考素材或生成参数后，旧音轨不得误当新请求。更换输出文件路径或句后停顿不改变原WAV的请求指纹；停顿变化仍会改变时间轴。已有输出只有请求、完整配置和音频指纹均一致才复用，否则保留旧文件并生成新版本。

视频继续执行[制作流程](production.md#常用命令)：登记音频/旁车并锁素材→按真实声音锁时→混音→四帧预览→用户确认→完整渲染与最终审阅。纯音频只做必要合成、实际时长安排、混音与音频检查，不进入视频四帧/渲染流程，也不要求安装浏览器。

改音色/模型/参考录音/参数后生成**新的**配音与成片版本。拒绝覆盖是为了保留旧成果；部分镜头生成失败时已成功片段及记录保留，修复后可逐段补缺，不把整段语音塞进第一镜，也不强行加速匹配旧时间轴。

## 外部配音与发布

Windows/Linux或其他TTS：将实际WAV放入项目，填写旧镜头voice或新话轮voice路径，无旁车时核对台词后设置对应externalVoiceVerified=true。已有旁车必须通过文本、音频及新话轮请求指纹检查，不能用此标记盖过错误记录；替换旧声音仍经素材候选审阅。视频随后按制作契约锁时、混音、四帧确认与导出；本地入口不自动转云端。

分享代码时保留示例配置，排除 `.voice-local`、其他个人配置、模型、录音及环境目录。给观众的视频和给开发者的源码包是不同交付物：带个人配音的成片按本人意愿发布；克隆参考素材不随开源包公开。模型与依赖遵循各自原许可证。

## 已锁定项目的声音变更

首次选材前正常生成配音，WAV与`.wav.json`旁车一并登记assets.json再seal。已经锁定的项目不能覆盖当前audio：新声音先生成到`.asset-review/candidates/批次/`，话轮绑定与表演记录保持一致，候选音频/旁车一起propose。新对白的instruct来自话轮声明，不能用只含text的单句命令丢掉表演要求。accept后重锁时间轴、混音及受影响验收；用户已明确指定音色/片段替换目标，记录授权、不重复问，仍展示diff。

完整命令见 Skill 的 references/material-review.md，初始化项目内对应 ASSETS.md。模型和私人参考音色配置保留原目录，不复制进公共素材；入片音频才纳入版本历史。

## 首次使用检测

新项目 init 自动检查；已有项目执行 `python3 tools/voice.py doctor --project .`，或在 Skill 目录执行 `python3 scripts/voice.py doctor --project /path/to/project`。可加 `--config` 指定已有配置；优先级和 defaultVoice 规则保持不变。

- `missing-config`：未发现私人配置，按本指南从公开模板建立配置、填写模型和音色。
- `needs-setup`：配置或资源缺项；Base列模型/参考录音/文字/核对标记，CustomVoice列模型及speaker问题。
- `configured-unverified`：选中默认音色所需的模型与声线条件已找到；轻量检查核对模型清单、文件集合与大小，不读取大权重计算哈希、不解码参考录音。完整校验仍执行voice.py check；同大小篡改由正式校验拒绝。

检测只看实际选中的默认音色及其模型，不要求配置里的其他备用音色全部可用。doctor 是提示命令，缺项也返回退出码 0，自动化程序读取 status/ issues；不能将退出码 0 当作可合成验收。已存在但无效的声音配置不会被跳过或降级。init 不写首次使用标记，避免陈旧缓存掩盖配置变化；同一会话未变化不重复提醒，修改配置后可再次运行。

## 中文角色试音

先从剧本里标出谁真的开口。单旁白沿用 defaultVoice；多人对白为每个开口角色选声，优先考虑人物关系、语言地域和说话姿态。安静陪伴也可以只靠动作和环境声表达。

以下命令在 Skill 根目录执行。在初始化后的工程使用 tools/voice.py。

```sh
python3 scripts/voice.py presets
python3 scripts/voice.py presets --query 祖母
```

返回值中 `voiceId` 放入 `cast.<角色>.voiceId`；`instruct` 是可编辑的表演参考，按该场情绪写入 `utterances[].performance.instruct`。同一人跨镜保留 voiceId，同场两位需要听辨的角色优先选不同的基础 speaker。两套 Serena 演法用于备选，年龄感由试听判断。官方未标注儿童或老年女性专用声线。

预设使用固定版本 Qwen3-TTS 1.7B CustomVoice。已经有私人配置时，角色可以直接绑定 `public-vivian` 等公开 ID，旁白继续使用原默认声线。同名本地定义优先。首次使用只有公开声线时，在工程 `.voice-local/voice.local.json` 写入：

```json
{"schema":"code-animation-voice/v1","defaultVoice":"public-vivian","voices":{},"models":{}}
```

在装好本页 MLX 依赖的 Apple Silicon 环境中，按需下载一次并校验：

```sh
python scripts/voice.py download --model qwen3-tts-1.7b-customvoice-mlx --root ~/.local/share/wtt-code-video-studio/models
python scripts/voice.py check --config .voice-local/voice.local.json --voice public-vivian
```

公开角色默认在上述缓存路径解析，移动模型可通过私有配置中的 models 指定路径和 manifest。后续合成在本机完成，无需录音或 API 订阅。权重与预设来自标注 Apache-2.0 的模型；这里的角色和演法是项目自行设计的试配方向。[官方声线表](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice) · [MLX 权重](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16)
