# 项目契约与复跑

## 文件与依赖

制作前按 [风格选择](style-selection.md) 完成用户决定并保存候选/选择记录。`style-choice.md` 由执行者核对，当前 Python/JS 管线不解析对话、不自动强制这个交互门槛；不能把能运行导出命令当作用户已确认。

初始化脚本把 `assets/starter/` 和两个工具复制到一个空项目目录。已有项目不能覆盖初始化。新片先 init，再在该目录保存剧本/风格候选与选择记录；init 是不依赖风格的准备，不代表选用了示例风格，也不能提前把示例导出为用户成片。已有工程直接沿用，不为补充选择记录重新 init。制作产物与 skill 源码分离。

```text
project/
  brief.md, script.md, storyboard.md  执行者编写
  style-options.md, style-choice.md   风格候选、用户决定与依据（agent 编写）
  film.json                         内容与配置来源
  timeline.json                     工具编译；不要手改
  index.html, runtime.js, scenes.js  前端舞台与绘制代码
  tools/pipeline.py, tools/render.cjs
  audio/                            配音、配乐、音效、混音及指纹
  preview/                          边界与代表帧
  silent.mp4, final.mp4
  render-report.json, media-info.json, delivery-check.json
```

必需 Node.js、Python 3、FFmpeg/FFprobe、Playwright 和 Chrome/Chromium。Python 工具仅用标准库。macOS 本机配音使用 `say`，其他系统接入已有 TTS 或外部配音。

先检查现有运行时：`node --version`、`python3 --version`、`ffmpeg -version`、`ffprobe -version`。在产物目录安装项目依赖可用 `npm install --save-exact playwright`，保存生成的 package.json/lockfile；Chrome 缺失时可运行 `npx playwright install chromium`。网络或运行权限失败按当前环境申请所需权限，不修改全局 registry 来绕过错误。

`PLAYWRIGHT_MODULE` 可指向已有 Playwright 模块；`CHROME_PATH` 指定浏览器可执行文件；`PYTHON` 指定 Python 命令。默认自动使用本机 macOS Chrome，否则使用 Playwright Chromium。不要复制某次会话里的绝对依赖路径。

模板没有联网依赖。使用 p5.js 等库时固定版本、下载到项目内、保留其许可并注明版本与来源；首次读当前官方 API 文档。外部图片/字体需等待解码。只加载本片所需资源。

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

在初始化后的项目目录执行。先完成剧本、用户风格选择及分镜，再由执行者改写 `film.json` 和 `scenes.js`：

```sh
python3 tools/pipeline.py timeline .
node tools/render.cjs . --preview
```

估时时间轴可预览，不能完整导出。做完旁白后：

```sh
python3 tools/pipeline.py tts . --voice Tingting --rate 205
python3 tools/pipeline.py timeline . --lock
python3 tools/pipeline.py mix .
node tools/render.cjs . --preview
node tools/render.cjs . --render
python3 tools/pipeline.py finish .
```

外部 TTS 直接保存实际声音文件并核对登记，跳过本机 `tts` 命令。语音可跨镜头连续叙述时，先切成镜头声音段并核对断句，或明确扩展时间轴契约，不把整段配音硬塞到第一镜。

前端播放可以在项目目录执行 `python3 -m http.server 8765 --bind 127.0.0.1` 后访问本机端口；`file://` 不能可靠加载 JSON。生成混音后，网页播放会使用 `mix-master.wav`。模板导出只截 `#stage`，不截播放按钮。

生产脚本默认重建同名产物，所以要保留重要版本时使用不同项目版本目录。台词改变后重新 TTS→锁时→混音→渲染；画面代码改变后重新预览/渲染→合成。最终合成会拒绝已变化的已加载源文件、视频、音频或时间轴。

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

`--preview` 生成每镜首、中、尾帧、每条字幕中点和全片首尾；代表帧重画前插入其他帧，验证 5 个样本是否一致。它不证明所有帧都没有瑕疵。先看图，再正式渲染。

`finish` 自动调用技术检查，也可单独运行 `python3 tools/pipeline.py validate .`。检查 H.264/AAC、宽高/fps、实际帧数、音画时长、完整解码和采样峰值。`delivery-check.json` 的视觉检查与用户确认初始为 pending；真实查看后另写 `review.md`，记审查时间、帧号、问题修正和未检查项。

- 浏览器报错、HTTP 素材缺失或不一致帧：保存 `render-failure.json`，先修页面再导出。
- 缺配音/旧配音/过期时间轴：按错误提示更新源头，不删检查逻辑。
- TTS 不可用：保留原错误，使用环境中可用服务或用户音频；无法拿到声音时说明受影响交付，不能把静音成功当带声音成功。
- 编码失败：保留 `render-ffmpeg.log`；未结束的 `silent.mp4` 不是完整成片。
- 重画明显闪烁：检查随机数、累积透明度、粒子状态、CSS/GSAP ticker 和没有重置的绘制状态。
- 长片渲染时间依尺寸、粒子数、阴影和素材复杂度变化；根据实际预览测速估计，不沿用历史短片耗时承诺。
