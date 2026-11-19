# 项目契约与复跑

只需文本、局部镜头工程、或组装分别完成的镜头时，从[分段创作与组装命令](staged-creation.md)进入。以下是完整视频工程契约。

## 文件与依赖

制作前按 [风格选择](style-selection.md) 完成用户决定并保存候选/选择记录。`style-choice.md` 由执行者核对，当前 Python/JS 管线不解析对话、不自动强制这个交互门槛；不能把能运行导出命令当作用户已确认。

初始化脚本把`assets/starter/`、制作工具与speech.py语音协议模块、声音配置模板/模型目录、声音依赖文件及`VOICE.md`、`ASSETS.md`、`FOOTAGE.md`、`QUALITY.md`、`PREVIEW.md`复制到空项目目录。已有项目不能覆盖初始化。新视频先init，再保存剧本/方向记录；init不代表采用示例风格或获准完整导出。纯音频只使用必要语音工具，不强制初始化/渲染视频。制作产物与Skill源码分离。

```text
project/
  brief.md, script.md, storyboard.md  执行者编写
  style-options.md, style-choice.md   风格候选、用户决定与依据（agent 编写）
  film.json                         内容与配置来源
  assets.json                       当前素材/来源/许可/使用依据与导流声明
  .asset-review/                    版本化清单、原素材、候选、diff 与授权
  timeline.json                     工具编译；不要手改
  index.html, runtime.js, scenes.js, footage.js  前端舞台与绘制代码
  tools/pipeline.py, tools/render.cjs, tools/voice.py, tools/asset_review.py, tools/footage.py, tools/preview_review.py
  tools/speech.py                   角色/话轮协议；voice与pipeline共同依赖
  config/model-catalog.json, config/voice.example.json
  requirements-voice.txt, VOICE.md, ASSETS.md   可选个人音色的依赖与说明
  .voice-local/                     用户私有声音配置、录音、模型；不打包
  audio/                            配音、配乐、音效、混音及指纹
  preview/                          边界与代表帧
  silent.mp4, final.mp4
  render-report.json, media-info.json, delivery-check.json
```

完整视频需Node.js、Python 3、FFmpeg/FFprobe、Playwright和Chrome/Chromium。核心pipeline.py与speech.py使用标准库。旁白自动发现defaultVoice；旧单旁白未配置时macOS可用say，其他系统接外部配音。新多角色项目缺配置或显式使用系统say时拒绝，不降为单音色。Base克隆/CustomVoice角色的额外依赖见[配音指南](voice.md)；纯音频不依赖浏览器。

先检查现有运行时：`node --version`、`python3 --version`、`ffmpeg -version`、`ffprobe -version`。在产物目录安装项目依赖可用 `npm install --save-exact playwright`，保存生成的 package.json/lockfile；Chrome 缺失时可运行 `npx playwright install chromium`。网络或运行权限失败按当前环境申请所需权限，不修改全局 registry 来绕过错误。

`PLAYWRIGHT_MODULE` 可指向已有 Playwright 模块；`CHROME_PATH` 指定浏览器可执行文件；`PYTHON` 指定 Python 命令。默认自动使用本机 macOS Chrome，否则使用 Playwright Chromium。不要复制某次会话里的绝对依赖路径。

模板没有联网依赖。使用 p5.js 等库时固定版本、下载到项目内、保留其许可并注明版本与来源；首次读当前官方 API 文档。外部图片/字体需等待解码。只加载本片所需资源。

## 首次声音预检

`init` 自动调用 `voice.py doctor`，沿现有优先级发现配置并提示缺少的模型/个人音色文件。已有工程首次使用运行 `python3 tools/voice.py doctor --project .`；旧 tools 无此命令时用当前 Skill 的 scripts/voice.py，不为检查重新 init。检测不写私人配置或素材，不触发素材版本更新；不是完整 SHA256 或音频质量验收。缺项提醒、配置方法和轻量检测边界见 [配音指南](voice.md)。

## film.json v1

```json
{
  "schema": "code-animation/v1",
  "title": "主题",
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "seed": 42,
  "speechCharsPerSecond": 3.8,
  "scenes": [
    {
      "id": "opening",
      "visual": {
        "subject": {"id": "seed-hero", "type": "seed-character"},
        "style": "sand",
        "motion": {"action": "hop", "effect": "reveal"},
        "renderer": "canvas2d"
      },
      "title": "画面短标题",
      "visualSeconds": 7.2,
      "leadSeconds": 0.3,
      "tailSeconds": 0.6,
      "narration": "这一镜的中文旁白。",
      "voice": "audio/opening.wav"
    }
  ],
  "audioTracks": [
    {"file": "audio/music.wav", "startSeconds": 0, "gain": 0.16}
  ]
}
```

- 风格目录 ID 是设计标签，不会自动注册新画法。比如用户选 chalk，须先按分镜实现对应 scenes.js，再将实现支持的值写入 visual；不能只改字符串。风格选择记录不改变 code-animation/v1 时间轴字段含义。
- `visual` 是新模板的组合约定：`subject.id/type` 指向主体身份与几何；`style` 指向外观；`motion.action/effect` 分别指向动作和出现/变化效果；`renderer` 指向实现技术。编译器原样透传，场景代码负责实现与校验，不会自动理解这些词并生成图形。
- 模板实作 `seed-character`、`flat/sand/particles`、`sway/hop`、`none/reveal/assemble` 与 `canvas2d` 的组合；其余主体/画法须改写 scenes.js。没有默认降级；未实现值报错。同一 subject.id 的 type 必须一致。
- `assemble` 当前示例把完整主体采样为点后聚合，聚合完成再落到所选 style；它是效果，不把最终 style 强制改成 particles。`reveal` 则逐步显露所选画法。复杂关节动作须对共享 rig 采样或变形，本模板的整体轻摆/跳跃不代表已实现步行。
- 兼容 `code-animation/v1` 的旧 `kind: character/sand/particles` 配置，保留其旧示例行为；新配置不使用 kind。visual 与 kind 同时存在时模板报错，不猜优先级。已有自定义 kind 由原项目 scenes.js 负责。
- 原有工程不会自动升级。迁移至组合模板时同步替换 scenes.js、改 film.json，重新编译时间轴/预览/渲染/合成；台词未变且指纹匹配可复用配音。runtime、字幕、混音及导出接口保持不变。
- width/height 必须正偶数，fps 正整数。为实际画幅重排，不用修改 JSON 假装支持竖屏。
- `visualSeconds` 必填且 >0；其他时间为秒。`maxSeconds` 可选，仅在用户给最大长度时设置；超限明确失败。
- 旧式`narration`空字符串表示无旁白；未使用utterances时保持原行为。旧默认旁白路径是`audio/<id>.wav`；voice始终是文件路径，不是voiceId，所有媒体路径须在项目内。
- 自带的 TTS 会生成文本、声音参数与文件哈希旁车记录；不依赖文件名判断可复用。已有外部配音手动核对台词后可设 `externalVoiceVerified: true`，修改台词时撤销这个标记并重新核对。若替换了带旁车记录的语音，先备份旧音频与记录，再登记新素材。
- `audioTracks` 是可选背景音乐或音效列表，用全片秒数、拍号或命名事件定位。线性 gain 控制整轨，gainEnvelope 按命名节点调整相对音量；自动识别人声、循环和裁切需在源轨另行处理。素材越过片尾会报错，不能依赖合成阶段截掉它。
- 旧字幕来自narration；新对白分别在每个话轮的实际声音区间内按标点/字符近似分配，并携带speakerId/utteranceId。不是逐字转录系统，仍需核对实际发音与字幕。

## 角色与逐句话轮

保持code-animation/v1；新项目可在film.json增加cast，并在同一scene中使用utterances。具体配置和四话轮示例见[声音指南](voice.md#角色绑定与表演计划)，不把人物换材质或换说话人强制变成切镜。

| 声明 | 含义与约束 |
|---|---|
| cast | kebab-case speakerId到角色条目的映射；条目只接受voiceId、label、description。仅narrator可省略voiceId，表示使用已发现的defaultVoice/显式默认覆盖 |
| utterances[].id | 项目内唯一、稳定的kebab-case话轮ID，用于派生seed和局部复用，不使用列表序号充当身份 |
| speakerId / text | 必须声明的角色和实际台词；除可沿默认音色的narrator外，角色须存在于cast。text不混入“惊讶地说”等表演标签 |
| voice | 该句WAV在项目内的输出路径，与voiceId分开；缺省audio/<scene-id>-<utterance-id>.wav，不同话轮不能争用同一文件 |
| performance.instruct | 传给支持该能力后端的逐句自然语言表演；当前CustomVoice可用，Base不接受非空值 |
| performance.intent | 创作意图记录，不作为模型已经执行的参数；缺省为空串 |
| pauseAfterSeconds | 句后停顿，默认0，按fps向上量化为整数帧；计入镜头长度 |
| externalVoiceVerified | 仅无旁车的外部WAV在核对台词后可显式设true；不能覆盖已有错误旁车 |

使用utterances时不再同时写非空narration或scene.voice；两种输入并用报错，不猜优先级。第一版只按列表顺序说话，不支持重叠/抢话。未知角色、音色、speaker、字段或不支持的instruct明确失败，不静默忽略或改成默认旁白。

脚本通过speech.scene_utterances(film, scene)规范化语音任务。新话轮旁车用speechRequestSha256绑定id/speakerId/voiceId/text/performance；完整TTS配置指纹另含模型、参考素材与生成参数。路径和句后停顿不改变原WAV请求，但改变停顿必须重编时间轴；改声音或表演不能只凭同名文件、相同文字复用。旧单旁白继续兼容原text/audioSha256旁车；导出不要求读取私人模型/录音配置。

仅当项目包含新utterances时，timeline新增顶层speech，平铺全部实际语音段，包括其中旧旁白的单段表示。每段记录voice、voiceStartFrame、voiceFrames、speakerId、utteranceId及量化停顿；新对白镜头的scene.voice=None、voiceFrames=0，不伪装成一个WAV。纯旧项目的timeline/字幕结构保持原样。

每句按真实WAV向上取整voiceFrames，顺序推进“声音+句后停顿”；新镜头帧数为`max(ceil(visualSeconds*fps), leadFrames + Σ(voiceFrames+pauseFrames) + tailFrames)`。字幕不跨句后的停顿，换角色准确到话轮边界；句内字符定位仍是近似值。mix优先从speech收集声音，只有旧timeline没有speech字段时才消费原scene.voice，避免双重混音。

runtime在每帧公开activeSpeakerId/activeUtteranceId，并传给drawScene；停顿或无台词时清空。场景可据此做角色高亮、表情或已实现的嘴部动作，不声称自动生成精确口型。保持原绝对帧绘制与媒体就绪约束。

## 常用命令

完整渲染之前必须先按[四帧审阅](preview-review.md)展示当前代码四帧拼图并得到确认。方向选择不等于拼图确认；没有真实用户原话时只能preview，不能照抄命令中的占位说明冒用批准。预览可用`--review-frames 20,90,170,260`指定本片四个关键时刻。

在初始化后的项目目录执行。先完成剧本、用户风格选择及分镜，再由执行者改写 `film.json` 和 `scenes.js`：

素材统一采用 [审阅机制](material-review.md)，没有三档或开场模式选择。首次选材/下载自主进行，来源与使用依据写入 assets.json；所有素材与声音确定后 seal。已有锁时先 check，变化仅存候选并审阅。纯代码估时可先执行 `python3 tools/pipeline.py timeline .`；浏览器预览必须绑定素材锁，已有 timeline 时首次 seal 需如实填写 --migration-note。

```sh
python3 tools/pipeline.py tts .
# 完成所有素材及声音，填写 assets.json（包括旁车、许可与导流）
python3 tools/asset_review.py seal .
python3 tools/pipeline.py timeline . --lock
python3 tools/pipeline.py mix .
node tools/render.cjs . --preview
# 展示输出的四帧拼图并等待用户确认，使用实际版本和用户原话
python3 tools/preview_review.py approve . --version v0001 --message '用户对该拼图的明确原话'
node tools/render.cjs . --render
python3 tools/pipeline.py finish .
```

重跑不再次 seal：先 `python3 tools/asset_review.py check .`，未变直接执行；已锁后需改变音频时，在候选目录生成并审阅，再锁时。首次素材未最终确定的预览也建立当次锁，后续改动按同一审阅流程处理。

外部TTS保存实际WAV并核对登记，跳过本机tts；新对白使用话轮上的externalVoiceVerified规则。同镜多角色直接使用utterances；旧跨镜旁白可按director.group保持视觉连续，不把整段配音硬塞进第一镜。

`pipeline.py tts .`默认使用已配置个人旁白；显式cast按各角色voiceId选声线。配置旁有`.venv/bin/python`时自动使用，否则使用当前Python。`--voice-config`覆盖配置，`--voice-id`覆盖未显式绑定的默认声音；旧`--voice Tingting --rate 205`仅用于单旁白。声音配置发现、逐句表演及复用边界维护在[配音指南](voice.md)。切换模型、参考、角色或表演时保留旧声音，按候选审阅生成新版本。旧工程可直接调用完整新版Skill中的脚本，无须重init；复制到tools时必须带speech.py及相关工具。交付源码排除`.voice-local`、私人配置、模型、录音和环境，不能无过滤打包整个项目。

前端播放可以在项目目录执行 `python3 -m http.server 8765 --bind 127.0.0.1` 后访问本机端口；`file://` 不能可靠加载 JSON。生成混音后，网页播放会使用 `mix-master.wav`。模板导出只截 `#stage`，不截播放按钮。

派生视频/报告仍会重建；保留成片版本时使用项目备份目录，完整保留 .asset-review。素材文件不能直接覆盖，先提议与确认再提交新版。四帧确认单独绑定当前实际画面，变更失效不能冒用旧批准。台词改变后候选 TTS→素材审阅提交→锁时→混音→四帧确认→渲染；仅画面代码改变且素材/导流不变时重新预览→新版四帧确认→渲染/合成，不触发素材确认。最终合成会拒绝已变化的已加载源文件、视频、音频或时间轴。

已完成的通用成片只换声音，且字幕/画面/时序全部保持时，另走[纯音轨修订](audio-revision.md)工具与独立版本目录；保留原工程有效批准及回执，不改变finish/check_render的绑定规则。工具校验原批准和新素材锁，显式映射新音轨、复制原画面流、核对全部帧一致；不通过重新渲染或手改哈希绕过四帧。声音长度无法落在原窗口时回到完整制作流程。

## 封面与首帧交付

从已确认的旁白和画面选封面主题。标题回答观众为什么值得点开，封面用片中可以辨认的一幕或一组对照呈现同一问题。用户指定用 `wtt-insight-topic-finder` 时，使用该 Skill 的标题/封面分支，先核对片中哪一段兑现标题。按实际画幅出独立图片，以小尺寸检查主标题和关键画面。涉及外部图像的封面同时登记来源与许可。

明确指定「放在首帧」且正片已验收时，可将一帧封面接在母片前，作为独立的交付版本。保留母片、原工程和验收回执，同时交付独立封面。单帧时长为 `1/fps` 秒，口播与画面一同顺延。交付前从 MP4 解码确认首帧为封面，正文逐帧与母片一致，核对音轨内容与一帧时间偏移，再验证完整解码。记录母片、封面和交付文件 SHA256、帧数及实际时长。平台有封面上传字段时可直接使用独立图片；首帧的保留与平台如何抓取缩略图分别核对。

单帧交付版使用独立的核验记录。更改正文画面、镜头或字幕时序，按[四帧审片](preview-review.md)提交新版。想让观众在播放中读完片头标题时，将标题当作片内镜头编排，按真实阅读时长审片。

## 浏览器接口

页面必须暴露：

```js
window.__filmMeta = {width, height, fps, totalFrames};
window.renderFrame = async (frame) => { /* 将舞台完整设为这个时刻；等待实际绘制完成 */ };
window.__ready = true; // 所有资产、字体、首帧就绪后
```

`#stage` 为唯一输出区域，像素尺寸等于 timeline 配置。适配 DOM 或 WebGL 时可替换 canvas；必须保证同帧绘制不依赖前一帧。渲染器逐帧 await，输出 PNG 流给 FFmpeg，使用背压控制，不把所有帧读到内存。

脚本记录每个被加载的本地资源哈希。网络资源不能被这套本地指纹完整锁定，因此生产前本地化。跨平台字体/GPU 差异需重新视觉检查，不承诺跨机器逐字节一致。

## 验证和故障

`--preview` 生成每镜首、中、尾帧、每条字幕中点和全片首尾；代表帧重画前插入其他帧，验证 5 个样本是否一致。它不证明所有帧都没有瑕疵。先自查看图和关键动作，再展示四帧拼图；用户明确确认后才正式渲染。

`finish` 自动调用技术检查，也可单独运行 `python3 tools/pipeline.py validate .`。先校验当前素材锁、时间轴/混音/渲染/合成回执的素材版本绑定，再检查 H.264/AAC、宽高/fps、实际帧数、音画时长、完整解码和采样峰值。`delivery-check.json` 的视觉检查与用户确认初始为 pending；之后执行review-init，实际查看最终编码证据并填写visual-review.json，再运行review；字段与状态只维护在[视频质量](video-quality.md)。

- 浏览器报错、HTTP 素材缺失或不一致帧：保存 `render-failure.json`，先修页面再导出。
- 缺配音/旧配音/过期时间轴：按错误提示更新源头，不删检查逻辑。
- TTS 不可用：保留原错误，使用环境中可用服务或用户音频；无法拿到声音时说明受影响交付，不能把静音成功当带声音成功。
- 编码失败：保留 `render-ffmpeg.log`；未结束的 `silent.mp4` 不是完整成片。
- 重画明显闪烁：检查随机数、累积透明度、粒子状态、CSS/GSAP ticker 和没有重置的绘制状态。
- 长片渲染时间依尺寸、粒子数、阴影和素材复杂度变化；根据实际预览测速估计，不沿用历史短片耗时承诺。

## 节拍与动作事件（可选）

有配乐、关键拟音或需要给对白让位时，在分镜阶段读[声音设计与节拍](rhythm.md)，先写节点再写动作；仅有连贯旁白时沿实际句段时长。

## 可选视频片段

film.json 可选 `footageManifest` 指向项目内已登记的帧序列清单；timeline 原样携带路径，锁时检查帧率、片长和完整源/派生哈希关系。未使用该字段时原接口不变。预览/渲染执行前及 finish/validate 的 locked 校验都会检查；不能只登记 MP4 而漏登记派生帧。

准备、候选审阅、原声及浏览器调用见[视频素材接入](footage.md)。新init附footage工具与说明；旧工程须按[迁移](migration.md)成套同步工具和依赖。默认runtime支持await drawScene，自定义runtime自行等待；原素材锁格式保持。

## 统一版补充

声音仍兼容两个旧环境变量与用户目录，冲突规则以[声音指南](voice.md)为准。制作工具及speech.py随init复制；旧接口保持，新角色/话轮字段按本页约定扩展。

- JPEG 导出：`node tools/render.cjs . --render --frame-format jpeg`；默认PNG，抽帧/确定性始终PNG。检查舞台实际尺寸，CSS/JPEG/WebP具备正确MIME。
- 最终 MP4 后 `python3 tools/pipeline.py review-init .` 生成绑定成片哈希的缩小图和动作窗口；实际观察后填写 `visual-review.json`，再 `python3 tools/pipeline.py review .`。未填、缺证据、过期、素材变化均不通过。见[质量规则](video-quality.md)。
- 连续镜头跨旁白段时用 `director.group`；关键运动位置用 `director.reviewAtSeconds`，不把配音段当强制切镜。
- 混音以总帧数计算最终样本长度，在响度处理后补齐被重采样缩短的静音尾；输入音轨超界仍拒绝，不裁旁白。
