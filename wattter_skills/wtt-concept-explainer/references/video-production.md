# 独立视频工具契约

本技能自行提供 `scripts/pipeline.py`、`voice.py`、`asset_review.py`、`render.cjs` 和 `assets/starter/`。运行不读取其他 Skill。`code-animation/v1` 等名称是保留的兼容数据协议；沿用字段不等于调用另一技能。

## 依赖与初始化

- 核心：Python 3 标准库、Node.js、FFmpeg/FFprobe、Playwright、Chrome/Chromium。先检测现有安装；不复制二进制、node_modules 或环境目录。
- 配音：默认发现已有音色，详见 [声音入口](voice.md)。macOS 可显式用系统 `say`；其他 TTS/外部音频可直接接入。可选 MLX 后端仅适用于 Apple Silicon；本技能不强制下载模型或使用云服务。
- 选视频且方案已确认后初始化空目录。在本技能目录执行：

```sh
python3 scripts/pipeline.py init /path/to/new-project
```

初始化复制模板和本技能的四个工具到项目 `tools/`，并带入公开 config、requirements-voice.txt、VOICE.md、ASSETS.md、QUALITY.md；不复制实际用户配置、录音或权重。目录非空会失败，不覆盖已有作品。模板只是可运行帧接口，正式制作按批准分镜替换画面。

项目中保留 `storyboard.md` 的批准版本、完整旁白、每镜目的/构图/状态/文字效果。`film.json` 为内容来源，`timeline.json` 是真实声音校准后的整数帧时序，禁止手改。交互页无需使用这些视频依赖。

## 内容配置

```json
{
  "schema":"code-animation/v1",
  "title":"已确认的讲解标题",
  "width":1920,"height":1080,"fps":30,
  "scenes":[{
    "id":"opening","title":"本镜学习问题",
    "visualSeconds":4,"leadSeconds":0.2,"tailSeconds":0.3,
    "narration":"完整旁白。","voice":"audio/opening.wav",
    "director":{"focus":"目标对象"}
  }],
  "audioTracks":[]
}
```

- `id` 唯一；width/height 为正偶数，fps 正整数；visualSeconds 为动作/阅读最低秒数。镜头取它与真实语音加前后停顿的较大值。
- `director` / `visual` 等自定义字段原样透传，场景代码负责实现；上例 focus 字符串需自写主体，不能直接用于模板的数字 focus。编译器不会把描述自动转成动画。
- 语音段不是相机切镜指令；[连续镜头](video-layout.md#机械空间与路径类镜头)在场景代码里用全局绝对帧轨迹采样。同一视觉长镜可为相邻语音段设置相同`director.group`，在不同段各用`reviewAtSeconds`覆盖推进、局部动作和接力；此字段是审阅取样位置，不会自动生成相机或延长默认2秒窗口。长轨迹另补完整证据，保持现有数据格式。
- 空 narration 表示无旁白；非空时必须有实际音频。自带 TTS 保存文本与音频哈希旁车，旧文案/音频拒绝锁时。外部音频须人工核对台词，再标该镜 `externalVoiceVerified: true`；台词改变需撤销并重新核对。
- `maxSeconds` 仅在用户要求时设置；超限失败，不裁切或加速。字幕按标点分块和字符权重估时，不是词级强制对齐。
- audioTracks 接受 `file`、`startSeconds`、`gain`；不自动循环、裁切或压低配乐，超片尾报错。所有路径在项目内，所有固定媒体登记素材清单。
- 兼容可选 rhythm：bpm/offsetSeconds 或严格递增的 beatTimesSeconds 二选一，basis 说明依据，events 指定 id/action/整数 beat（从0开始），可选 sceneId；事件编译成绝对帧。它不是自动测拍或动作引擎。无配乐/节拍需求时省略；loop 只增加首尾抽样，不自动实现无缝循环。

## 配音、素材与导出

以下命令均在新工程目录执行：

```sh
python3 tools/pipeline.py tts .
# 完成图片、字体、声音及 .wav.json 旁车，填写 assets.json
python3 tools/asset_review.py seal .
python3 tools/pipeline.py timeline . --lock
python3 tools/pipeline.py mix .
node tools/render.cjs . --preview
# 查看 preview/ 中的首中尾、字幕、事件及转场帧后再导出
node tools/render.cjs . --render
python3 tools/pipeline.py finish .
python3 tools/pipeline.py review-init .
# 实际审阅生成的缩小图/连续片段，填写 visual-review.json；待审不能跳过
python3 tools/pipeline.py review .
```

- 已有 TTS 可生成本地 WAV 并登记，跳过 `tts`。默认声音缺配置与指定配置损坏是不同状态；后者报错，不静默回退。
- `assets.json` 声明 schema `code-animation-assets/v1`、assets 与 links。媒体逐项写 id/path/sourceUrl/license/useBasis；自制来源可为 null。首次 seal 生成版本锁，只执行一次；后续 check，变更走 [素材候选审阅](material-review.md)，不删锁重建。
- 不含外部素材的纯代码也用空清单。模型/参考录音保持外部私有目录；入片音轨和旁车纳入锁。
- 代码修改无需素材重审，但重新预览/渲染/finish；film 改动先重新锁时和混音。替换音频先候选审阅再锁时；不以旧报告充当新版通过。
- 浏览器外部媒体请求被阻断，先本地化并登记。Playwright 可由 `PLAYWRIGHT_MODULE=/absolute/path/to/playwright` 复用现有安装；Chrome 可由 CHROME_PATH 指定。变量指向第三方运行时，不指向其他 Skill。
- PNG 为默认输入；写实图片较慢时用 `node tools/render.cjs . --render --frame-format jpeg`，固定 quality=95。审阅/确定性检查仍用 PNG，最终仍为 H.264；查看编码后文字细节，不把有损输入称作无损。

## 页面接口

`#stage` 必须实际等于 width×height；可用 DOM/SVG/Canvas。样式加载错误、缩放导致尺寸不符会阻断。CSS/JPEG/WebP 支持本地加载，字体与图片完成后才置 ready。

```js
window.__filmMeta = {width, height, fps, totalFrames};
window.renderFrame = async frame => { /* 按绝对帧完整重建状态 */ };
window.__ready = true; // 字体、素材、首帧真实就绪后
```

导出查询参数 `?export=1` 时隐藏控件。模板 runtime.js 提供音频驱动的播放/暂停/拖动和字幕；自定义舞台可自行实现相同接口。禁止累计状态或实时动画漂移。用本地 HTTP 打开工程，不能依赖 file:// fetch。

## 验证与交付

- preview 保存实际帧索引、5个乱序一致性样本、浏览器错误和测速；自动通过不代表画面/内容通过。检查转场连续片段，特别是新旧文字叠加、主体跳变与字幕遮挡。
- finish 合并音轨并核验素材版本、源文件指纹、H.264/AAC、帧数/尺寸/帧率、音画时长、完整解码及采样峰值。缺/旧声音、过期时间轴、文件变化、不一致帧、浏览器错误不能绕过。
- 保留 final.mp4、源码、分镜/时间轴、技术报告及视觉记录。`finish`只表示技术通过；按[质量约束](video-quality.md)执行review-init与review。证据自动生成，视觉判断仍须真实审阅；结果绑定最终文件指纹，缺证据或旧记录拒绝。音频试听和用户采用独立记录，不自动置为通过。
- 不打包个人配置、录音、模型、环境与 node_modules。不将旧工程工具自动覆盖成新版；迁移先完整备份、核对协议和素材历史，再替换工具并重验。
