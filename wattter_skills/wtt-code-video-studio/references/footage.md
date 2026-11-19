# 纪录片素材、片段与逐帧接入

## 先找材料，再落实镜头

用户提供的真实材料优先；按剧本列缺口，由执行者使用当前可用搜索、浏览器或下载工具补齐。不是要求用户备齐全部视频，也不是固定素材库自动配片。已有明确素材选择沿用，不增加开场模式或重复许可询问。

- 在 `source-plan.md` 写镜头 ID、所需画面/证据、已有文件、缺口、搜索方向和结果；同一素材可供多镜复用。优先原始发布机构、官方档案和明确许可的素材库。
- 每个候选记录原页面 URL、直接下载 URL、作者/机构、许可原文或截图路径、检索日期、具体使用依据和所用时间码；最终文件按 [素材审阅](material-review.md) 登记。下载地址变化不自动替换锁定文件；网络失败报告实际原因，不能绕过登录/访问限制。
- 版权未知就如实标记待核实，不猜许可证，不将源码 MIT 套用视频。用户提供文件也记录“用户提供”及其已说明的授权范围，不要求把私人文件上传到互联网。
- `facts.md` 将旁白/字幕的重要事实对应到镜头 ID、原始出处和证据位置；区分事实、推断、示意。网上搜索命中并不等于核实。原片裁切、变速和重排不得制造与来源相反的因果。
- 装饰缺口可用程序图形；缺少事实证据则收窄表达或标明未确定。生成重建、示意图、异时照片都明确标注，不能冒充现场或精确同步机位。

## 四类导演配方

| 类型 | 镜头动作与材料 | 声音与关键边界 |
|---|---|---|
| 档案纪录片 | 原片、报刊、照片；标题卡、虹膜转场、冻结标记；画面层做颗粒/抖动，文字层保持可读 | 旁白与年代声响分层；代码随机数固定，不用抖动掩盖低清材料 |
| 视觉调查 | 报告原页、地图、照片、视频；圈注、同像素放大、证据并排、来源指向示意模型 | 关键原声保留字幕；分别标注已知、推断、未解决，时间压缩明确说明 |
| 新闻播报 | 标题导视、新闻条、图表、引文卡、来源与日期；已有画面和程序图形组合 | 人声优先，字幕区与新闻条避让；AI 示意背景标明性质，不伪造采访 |
| 多机位事件回顾 | 一个事件时钟、机位切换、分屏展开/合并；每机位记录时间对应和同步证据 | 优先现场声音推动切镜；无精确同步依据标“同一时段”，不声称实时直播/推流 |

它们是制作类型，可与沙画、黑白档案、扁平信息图等画风组合；放进既有五候选，不固定每次必须出现。镜头组件由本片 `scenes.js` 实现，表中的配方不是已内置的自动模板。建议先用一个关键镜头验证布局和同步，再扩展全片。

## 原镜和代码画面怎么接

做解说混剪时，在既有分镜逐条写「旁白要说明的事｜用哪段原镜或怎样由代码画出｜接点」。原镜保留举证所需的完整动作、反应或对白，注明源时间码。代码承担原镜难以同时展示的内容，例如并排让两次动作可比较，用路径说明顺序，用翻页表现改编新增的一段。字幕只补充需要读的信息。

用同一物件、动作方向、构图或声音节点把两种画面接起来，连续看一次接入前、接入时和切出后。静帧停留时写清观众需要读到什么。四帧里选到原镜、关键代码画面与收尾，必要时附含接点的短试剪。自绘的象征性画面按理解需要标明示意，原镜来源、成片使用范围和公开分发许可按[素材审阅](material-review.md)记录。

## 预抽帧：已实现的本地工具

`tools/footage.py` 只处理项目内视频，不代替互联网搜索；新项目 init 已携带。它按源视频入点截取、正向变速、等比缩放，再输出恒定 fps 的 PNG。支持不同源帧率；不含抠像、自动多机位对齐、音频变速或网络直播。多机位先人工核对事件基准，把每机位源入点和全片起始帧写明；`syncBasis` 是依据记录，不是自动认证。

准备 `footage.recipe.json`，示例只演示字段，实际时码根据本片填写：

```json
{
  "schema": "code-animation-footage/v1",
  "fps": 30,
  "clips": [{
    "id": "camera-a",
    "sourcePath": "media/source.mp4",
    "inSeconds": 2,
    "startFrame": 0,
    "durationFrames": 60,
    "speed": 1,
    "width": 1280,
    "syncBasis": "原片 2 秒对应本片 0 帧，已核对倒计时画面；此处填实际依据",
    "audio": "mute",
    "provenance": {
      "sourceUrl": "https://example.org/original",
      "license": "填入核对后的实际许可；示例不授予素材使用权",
      "useBasis": "填入镜头用途及许可核对依据",
      "landingUrl": null
    }
  }]
}
```

`startFrame` 是全片整数帧，不是场景内帧；`durationFrames` 是输出帧数；源使用区间为 `[inSeconds, inSeconds + durationFrames/fps*speed)`。speed=2 表示两倍速。当前只等比缩放，裁切可由 Canvas drawImage 完成；如另做预处理，将处理记录和中间文件也登记。宽度为正整数，工具自动输出偶数高度。

首次、尚未锁定：

```sh
python3 tools/footage.py prepare . --recipe footage.recipe.json --out media/footage-v1
```

输出目录必须全新；失败留下 `FAILED.txt`，保留证据并换新目录重试。`assets.fragment.json` 是待合并的派生资产条目，不是当前锁，不会自动改 assets.json。把原视频、来源证据、原始 recipe 和 fragment 的条目并入现有 assets.json，保留原有声音和 links。在 film.json 增加 `"footageManifest": "media/footage-v1/manifest.json"`。manifest 已保存实际生效参数、FFmpeg 版本、源哈希及每帧哈希，不含候选输入路径。

全部材料确定后沿原 seal → timeline --lock → mix → preview → render → finish 流程。原片、清单及每个 PNG 都必须登记；预览、渲染、锁时、混音和最终验收检查来源/派生关系。可独立运行：

```sh
python3 tools/footage.py check .
```

全量资产锁校验已有文件哈希；额外的视频检查拒绝原片虽经确认更换但序列仍指向旧哈希、缺帧、未登记、fps 不符、片段超片尾。确认新版清单不等于成片已验收。

## 锁定后的重处理与替换

先 check 当前版本。新文件只能进入候选，输出声明引用新的最终版本目录：

```sh
python3 tools/footage.py prepare . \
  --recipe .asset-review/candidates/reedit/recipe.json \
  --out .asset-review/candidates/reedit/frames \
  --target media/footage-v2
```

如替换原片，在该 recipe 保留最终 `sourcePath`，增加 `inputPath` 指向 `.asset-review/candidates/reedit/new-source.mp4`；源条目也在完整 proposal 中设置 candidatePath。工具读取候选原片，manifest 保留最终 sourcePath 与新文件哈希。不得改当前原片后再调用工具。

合并新派生 fragment、源片/证据/recipe 变更到完整 proposal；保留全部未变条目，不把 fragment 当完整声明。显示 diff，按已有授权规则 propose/accept，保留旧版与记录。接受后将 film.footageManifest 指向新版，再重锁时和渲染；此引用切换本身是代码配置，但所引用素材必须已获授权并锁定。源片不变、只改裁切布局的 Canvas 代码无需素材确认。

## 前端使用

新模板已加载 `footage.js`；runtime 将已打开的加载器传给 `drawScene`。按需要异步绘制：

```js
window.drawScene = async (ctx, {frame, footage, width, height}) => {
  const image = await footage.image('camera-a', frame);
  ctx.drawImage(image, 0, 0, width, height);
  // 再叠加本片标题、证据标记等；实际项目按源比例使用 contain 或裁切。
};
```

片段只在 `[startFrame, startFrame + durationFrames)` 可取帧；分镜代码须判断活动区间，越界不自动停在最后一帧。每次绘制等待图片解码，缓存默认 24 项、乱序取帧一致；不能通过自动播放 video 标签驱动导出。异步绘制串行，预览拖动的旧请求不能覆盖新状态。长片 PNG 与版本历史较大，按实际镜头裁取并选合理分辨率，不自动删锁定历史。

## 原声、配音和验证

片段工具仅处理画面。需要原声时，执行者用 FFmpeg 按相同源入点提取独立 WAV，记录源哈希/区间/变速参数并登记；按全片位置写 audioTracks。变速原声要另处理节奏与音高并试听，不能把 speed 参数误当作已同步音频。旁白进入时降低音乐/原声，重要现场发言处让旁白避让；当前 mixer 不自动 duck，可先生成已处理音轨再登记，或按项目编写混音代码。

新类型验收加看：首尾源帧、机位共同事件、冻结/放大是否同一证据、缺帧与接缝、标题条/字幕避让、来源标识、原声与旁白关系。结构校验不能证明事实正确或素材许可有效。没有播放音频就写未试听。

旧项目迁移：备份后同步五个 tools 脚本及 footage.js；自定义页面保留原设计，只补脚本加载和异步 await。使用默认 runtime 才同步新版 runtime.js。film 不使用 footageManifest 时无视频新字段/素材要求；另一技能 concept-explainer 的独立工具不自动更新。

参考来源：lemo-opuscar 的 [视觉调查](https://github.com/lemomo-ai/lemo-opuscar/blob/main/styles/visual-investigation/DEMO.md)、[倒计时](https://github.com/lemomo-ai/lemo-opuscar/blob/main/styles/countdown/DEMO.md)、[档案影片](https://github.com/lemomo-ai/lemo-opuscar/blob/main/styles/newsreel/DEMO.md)、[新闻包装](https://github.com/lemomo-ai/lemo-opuscar/blob/main/styles/news-package/DEMO.md)。采用材料组织和导演方法，示例故事、品牌签名、素材与下载构建不直接复制。
