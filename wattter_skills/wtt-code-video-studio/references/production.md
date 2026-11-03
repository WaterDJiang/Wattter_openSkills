# 项目契约与复跑

## 文件与依赖

制作前按 [风格选择](style-selection.md) 完成用户决定并保存候选/选择记录。`style-choice.md` 由执行者核对，当前 Python/JS 管线不解析对话、不自动强制这个交互门槛；不能把能运行导出命令当作用户已确认。

初始化脚本把 `assets/starter/`、六个工具、声音配置模板/模型目录、声音依赖文件及 `VOICE.md`、`ASSETS.md`、`FOOTAGE.md`、`QUALITY.md`、`PREVIEW.md` 复制到一个空项目目录。已有项目不能覆盖初始化。新片先 init，再在该目录保存剧本/风格候选与选择记录；init 是不依赖风格的准备，不代表选用了示例风格，也不能提前把示例导出为用户成片。已有工程直接沿用，不为补充选择记录重新 init。制作产物与 skill 源码分离。

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
  config/model-catalog.json, config/voice.example.json
  requirements-voice.txt, VOICE.md, ASSETS.md   可选个人音色的依赖与说明
  .voice-local/                     用户私有声音配置、录音、模型；不打包
  audio/                            配音、配乐、音效、混音及指纹
  preview/                          边界与代表帧
  silent.mp4, final.mp4
  render-report.json, media-info.json, delivery-check.json
```

必需 Node.js、Python 3、FFmpeg/FFprobe、Playwright 和 Chrome/Chromium。核心 pipeline.py 仅用标准库。默认配音先自动发现已配置的 defaultVoice；未配置时 macOS 使用 `say`，其他系统接入已有 TTS 或外部配音。可选 `voice.py` 克隆路线的额外依赖单独安装，见 [配音指南](voice.md)；不影响普通动画路线。

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
- `narration` 空字符串表示无旁白。默认旁白路径是 `audio/<id>.wav`；所有媒体路径必须在项目目录内。
- 自带的 TTS 会生成文本、声音参数与文件哈希旁车记录；不依赖文件名判断可复用。已有外部配音手动核对台词后可设 `externalVoiceVerified: true`，修改台词时撤销这个标记并重新核对。若替换了带旁车记录的语音，先备份旧音频与记录，再登记新素材。
- `audioTracks` 是可选背景音乐或音效列表，起点基于全片秒数。当前脚本不会自动循环、裁切或 duck；在声音设计阶段做好长度与音量，必要时先生成带 duck 的配乐文件。素材越过片尾会报错，不能依赖合成阶段截掉它。
- 字幕自动来自 narration，按标点/22 字分块后按字符长度近似分配。成片审查需要核对实际发音和文字出现时间；它不是逐字转录系统。

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

外部 TTS 直接保存实际声音文件并核对登记，跳过本机 `tts` 命令。语音可跨镜头连续叙述时，先切成镜头声音段并核对断句，或明确扩展时间轴契约，不把整段配音硬塞到第一镜。

`pipeline.py tts .` 默认使用已配置个人音色，配置旁存在 `.venv/bin/python` 时自动使用该解释器，否则使用当前 Python。配置发现顺序见配音指南；坏配置明确失败，不回退系统声音。`--voice-config` 覆盖配置，`--voice-id` 覆盖 defaultVoice；原 `--voice Tingting --rate 205` 保留为显式系统音色覆盖。也可用安装声音依赖的 Python 运行 `voice.py synthesize --project .` 自动发现配置。新入口逐镜输出 WAV 和兼容的 `text/audioSha256` 旁车，锁时/混音/渲染契约不变。切换模型或参考音频后生成新版本声音，不覆盖旧输出。旧工程可直接调用新版 skill 的 voice.py，无须重新 init；详见配音指南。交付源码时排除 `.voice-local/`、其他私人配置与模型/录音，不能把整个项目无过滤打包。

前端播放可以在项目目录执行 `python3 -m http.server 8765 --bind 127.0.0.1` 后访问本机端口；`file://` 不能可靠加载 JSON。生成混音后，网页播放会使用 `mix-master.wav`。模板导出只截 `#stage`，不截播放按钮。

派生视频/报告仍会重建；保留成片版本时使用项目备份目录，完整保留 .asset-review。素材文件不能直接覆盖，先提议与确认再提交新版。四帧确认单独绑定当前实际画面，变更失效不能冒用旧批准。台词改变后候选 TTS→素材审阅提交→锁时→混音→四帧确认→渲染；仅画面代码改变且素材/导流不变时重新预览→新版四帧确认→渲染/合成，不触发素材确认。最终合成会拒绝已变化的已加载源文件、视频、音频或时间轴。

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

用户给音乐拍点、BPM、事件或循环要求时才读[节拍配置](rhythm.md)。保留原rhythm/loop字段含义；普通无节拍任务不必读该schema。

## 可选视频片段

film.json 可选 `footageManifest` 指向项目内已登记的帧序列清单；timeline 原样携带路径，锁时检查帧率、片长和完整源/派生哈希关系。未使用该字段时原接口不变。预览/渲染执行前及 finish/validate 的 locked 校验都会检查；不能只登记 MP4 而漏登记派生帧。

准备、候选审阅、原声及浏览器调用见 [视频素材接入](footage.md)。新 init 附 footage.py、footage.js 和 FOOTAGE.md；旧工程升级须同步五个 tools，默认 runtime 支持 await drawScene，自定义 runtime 要自行等待。原 schema、声音配置与素材锁格式保持不变。

## 统一版补充

声音仍兼容两个旧环境变量与用户目录，冲突规则以[声音指南](voice.md)为准。五个核心工具独立随 init 复制，原 schema 不变。

- JPEG 导出：`node tools/render.cjs . --render --frame-format jpeg`；默认PNG，抽帧/确定性始终PNG。检查舞台实际尺寸，CSS/JPEG/WebP具备正确MIME。
- 最终 MP4 后 `python3 tools/pipeline.py review-init .` 生成绑定成片哈希的缩小图和动作窗口；实际观察后填写 `visual-review.json`，再 `python3 tools/pipeline.py review .`。未填、缺证据、过期、素材变化均不通过。见[质量规则](video-quality.md)。
- 连续镜头跨旁白段时用 `director.group`；关键运动位置用 `director.reviewAtSeconds`，不把配音段当强制切镜。
- 混音以总帧数计算最终样本长度，在响度处理后补齐被重采样缩短的静音尾；输入音轨超界仍拒绝，不裁旁白。
