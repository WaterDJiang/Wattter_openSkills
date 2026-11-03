# 外部作品与技术依据

由config/capabilities.json的referenceCases生成。只存研究信息，不搬运媒体；均为research-only，不是本库渲染验收。

热度来自注明来源的索引快照，不是实时播放量、全网排名或效果保证。作者未公开或本次未读到的库保持未知；复现建议与原片实际技术分开。选择时配合[案例驱动选型](case-driven-techniques.md)和[用法映射](use-case-mapping.md)。

```sh
python3 scripts/catalog.py cases --use-case 概念解释
python3 scripts/catalog.py cases --query p5
```

| 案例 | 形态 | 对应用法 | 关注依据 |
|---|---|---|---|
| [P(doom) 原版代码绘制MV](#pdoom-code) | 视频 | 音乐视觉与循环氛围 | 未核实热度；技术/用法参考 |
| [Claude Pop 五分钟混合重制](#claude-pop-hybrid) | 生成素材与代码混合 | 音乐视觉与循环氛围 | 20,000,000次播放（索引快照） |
| [同一个形状连续变成多种UI状态](#ui-morph) | 视频 | 动态设计作品集与品牌片头 / 产品发布与能力介绍 / 品牌与广告 | 1,200,000次播放（索引快照） |
| [低分辨率像素巫师施法循环](#pixel-wizard) | 视频 | 动态设计作品集与品牌片头 / 音乐视觉与循环氛围 | 456,500次播放（索引快照） |
| [两分钟沙画叙述历史](#sand-history) | 视频 | 传统文化与历史叙事 | 未核实热度；技术/用法参考 |
| [可拖动对焦环的镜头实验](#lens-lab) | 交互作品的演示 | 交互实验与科学演示 / 概念解释与机制科普 | 3,200,000次播放（索引快照） |
| [交互式火箭发动机拆解](#raptor-lab) | 交互作品的演示 | 交互实验与科学演示 / 概念解释与机制科普 | 1,200,000次播放（索引快照） |
| [推理创业公司发布片](#startup-launch) | 视频 | 品牌与广告 / 产品发布与能力介绍 | 349,000次播放（索引快照） |
| [Danny Stuart 应用与素材包宣传片](#remotion-promo) | 视频 | 品牌与广告 / 产品发布与能力介绍 | 未核实热度；技术/用法参考 |
| [五分钟历史战役程序化重建](#austerlitz-code) | 视频 | 传统文化与历史叙事 / 纪录片与真实事件 | 未核实热度；技术/用法参考 |
| [配方逐步装入杯中的图解](#recipe-negroni) | 视频 | 配方与实物步骤图解 | 78,861次播放（索引快照） |
| [口播保留原声并补线稿解释画面](#talkinghead-broll) | 原视频与代码补画 | 口播播客与课程可视化补画 | 未核实热度；技术/用法参考 |
| [七分钟代码库与查询执行讲解](#sqlite-tour) | 视频 | 代码库与系统架构讲解 | 未核实热度；技术/用法参考 |
| [Manim 导数概念教学](#manim-derivative) | 视频 | 概念解释与机制科普 | 未核实热度；技术/用法参考 |
| [调用Runway的超智能纪录片](#runway-documentary) | 生成素材与代码混合 | 纪录片与真实事件 | 未核实热度；技术/用法参考 |
| [WebGL2玻璃金箔拼片短片](#glass-mosaic) | 视频 | 音乐视觉与循环氛围 / 动态设计作品集与品牌片头 | 未核实热度；技术/用法参考 |
| [Blender黏土外观角色演示](#blender-clay) | 视频 | 儿童故事与启蒙 / 幽默与喜剧短片 | 未核实热度；技术/用法参考 |

<a id="pdoom-code"></a>

## P(doom) 原版代码绘制MV

[原作或作者入口](https://github.com/johnheibel/pdoomvideo)。有完整源码的代表案例；热度未单独核实。

- 已披露或可查的做法：p5.js + p5.brush绘图；Puppeteer驱动Chrome，FFmpeg编码，已有歌曲混入。
- 尚不确定：未在本库复现；不与后续混合重制版混同。
- 本库复现候选：p5js；不是原片依赖认定或已适配声明。

- [源码已查看](https://github.com/johnheibel/pdoomvideo/blob/fa546a38092e75f2b079e6a86d6abc54dd525d17/studio.html)：入口实际加载p5与p5.brush。
- [源码已查看](https://github.com/johnheibel/pdoomvideo/blob/fa546a38092e75f2b079e6a86d6abc54dd525d17/render.mjs)：实际导入puppeteer-core并调用FFmpeg。
- [作者制作记录](https://github.com/johnheibel/pdoomvideo/blob/fa546a38092e75f2b079e6a86d6abc54dd525d17/README.md)：作者说明原有歌曲与代码画面的来源，不是全部音频原创合成。

<a id="claude-pop-hybrid"></a>

## Claude Pop 五分钟混合重制

[原作或作者入口](https://x.com/anabology/status/2103534482930491441)。高关注索引快照；不能当纯代码证明。

- 已披露或可查的做法：作者提示包含角色图、Seedance底片及JavaScript重绘/歌词覆盖。
- 尚不确定：提示词不证明每步均按计划完成；没有核对最终源码。
- 本库复现候选：canvas2d；不是原片依赖认定或已适配声明。
- [热度来源](https://clawshelf.com/zh/ai-videos/opus-5-5/elaborate-overnight-scene-shared-prompt)：20,000,000次播放；指标日期：索引日期未显示；检索日期：2026-11-03。

- [作者陈述的公开转引](https://clawshelf.com/zh/ai-videos/opus-5-5/elaborate-overnight-scene-shared-prompt)：公开转引作者要求调用图像/视频模型并叠加JS动画；原帖本次未直接读取。

<a id="ui-morph"></a>

## 同一个形状连续变成多种UI状态

[原作或作者入口](https://x.com/twoclipping/status/2103273003555402193)。高关注索引快照。

- 已披露或可查的做法：作者公开方案为单HTML、seek(t)、解析弹簧、Playwright多子帧及FFmpeg运动模糊。
- 尚不确定：最终采用DOM/SVG/Canvas的具体比例没有源码确认；不把索引svg标签当实测。
- 本库复现候选：svg-html / gsap；不是原片依赖认定或已适配声明。
- [热度来源](https://clawshelf.com/zh/ai-videos/opus-5-5/code-based-ui-motion-design-showreel)：1,200,000次播放；指标日期：索引日期未显示；检索日期：2026-11-03。

- [作者陈述的公开转引](https://clawshelf.com/zh/ai-videos/opus-5-5/code-based-ui-motion-design-showreel)：公开转引作者制作规格；包括纯时间函数与多子帧渲染。

<a id="pixel-wizard"></a>

## 低分辨率像素巫师施法循环

[原作或作者入口](https://x.com/majidmanzarpour/status/2102476258948927543)。高关注索引快照。

- 已披露或可查的做法：作者公开规格明确原生JavaScript和Canvas2D，128×96逻辑画布整数倍放大。
- 尚不确定：未核对最终实现与实际帧率。
- 本库复现候选：canvas2d；不是原片依赖认定或已适配声明。
- [热度来源](https://clawshelf.com/zh/ai-videos/opus-5-5/animated-pixel-art-wizard-casting-spell)：456,500次播放；指标日期：索引日期未显示；检索日期：2026-11-03。

- [作者陈述的公开转引](https://clawshelf.com/zh/ai-videos/opus-5-5/animated-pixel-art-wizard-casting-spell)：转引原始规格明确禁用外部资产与库。

<a id="sand-history"></a>

## 两分钟沙画叙述历史

[原作或作者入口](https://x.com/Michaelzsguo/status/2102592355165782312)。早期传播代表；热度数字未核实。

- 已披露或可查的做法：作者自述代码沙画，未用Blender或Three.js。
- 尚不确定：具体绘图库未披露；不能确定是p5.js、Canvas或shader。
- 本库复现候选：canvas2d / webgl；不是原片依赖认定或已适配声明。

- [作者陈述的公开转引](https://github.com/X-RayLuan/awesome-opus-5-5-video-prompts/blob/b9524552dfcf96c4bf3569fa1145f94b63bc2a76/README.md#michaelzsguo-us-history-sand-animation)：作者陈述由合集转引；只能确认其披露边界。

<a id="lens-lab"></a>

## 可拖动对焦环的镜头实验

[原作或作者入口](https://lens.lab.sael.net)。高关注索引快照。

- 已披露或可查的做法：拖动对焦环改变镜片和清晰平面；本体为交互实验。
- 尚不确定：作者未披露具体库；演示视频不等于离线逐帧渲染。
- 本库复现候选：threejs / webgl；不是原片依赖认定或已适配声明。
- [热度来源](https://claudevideo.org/videos/interactive-lab-explains-focus-with-an-exploded-camera-lens)：3,200,000次播放；指标日期：2026-10-07（索引时）；检索日期：2026-11-03。

- [索引描述](https://claudevideo.org/videos/interactive-lab-explains-focus-with-an-exploded-camera-lens)：索引明确注明作者未命名工具，链接可交互原作。

<a id="raptor-lab"></a>

## 交互式火箭发动机拆解

[原作或作者入口](https://airsup.ai/rocket-engine)。高关注索引快照。

- 已披露或可查的做法：公开陈述包含拆解、流路观察与节流操作。
- 尚不确定：具体库没有源码核验；索引Three.js/shader标签只作线索。
- 本库复现候选：threejs / webgl；不是原片依赖认定或已适配声明。
- [热度来源](https://clawshelf.com/zh/ai-videos)：1,200,000次播放；指标日期：索引日期未显示；检索日期：2026-11-03。

- [作者陈述的公开转引](https://clawshelf.com/zh/ai-videos)：首页转引作者目标并链接原作；详情本次抓取超时。

<a id="startup-launch"></a>

## 推理创业公司发布片

[原作或作者入口](https://x.com/deedydas/status/2102787937482252537)。高关注索引快照。

- 已披露或可查的做法：公开案例为短时长排版、图表与界面发布片。
- 尚不确定：原片具体库未披露；后来的开源复刻不能证明原片使用相同技术。
- 本库复现候选：svg-html / gsap / remotion；不是原片依赖认定或已适配声明。
- [热度来源](https://clawshelf.com/zh/ai-videos/opus-5-5/ai-inference-startup-launch-video)：349,000次播放；指标日期：索引日期未显示；检索日期：2026-11-03。

- [作者陈述的公开转引](https://github.com/X-RayLuan/awesome-opus-5-5-video-prompts/blob/b9524552dfcf96c4bf3569fa1145f94b63bc2a76/README.md#deedydas-startup-launch-video)：作者的简短任务被公开转引；合集另列的是后续复刻仓库。

<a id="remotion-promo"></a>

## Danny Stuart 应用与素材包宣传片

[原作或作者入口](https://dannystuart.substack.com/p/claude-code-opus-remotion-agentic-promo-video)。技术或用法补充。

- 已披露或可查的做法：作者文章明确使用Remotion/React，第二支接入自己已有图片与视频素材。
- 尚不确定：未获取完整工程或复现；不沿用其成本和耗时保证。
- 本库复现候选：remotion / svg-html；不是原片依赖认定或已适配声明。

- [作者制作记录](https://dannystuart.substack.com/p/claude-code-opus-remotion-agentic-promo-video)：第一人称制作记录明确框架与用户资产来源。

<a id="austerlitz-code"></a>

## 五分钟历史战役程序化重建

[原作或作者入口](https://github.com/WinterArc21/Battle-of-Austerlitz-Film)。技术或用法补充。

- 已披露或可查的做法：自写WebGL2/GLSL，地形与精灵系统，Playwright/FFmpeg；作者说明Kokoro旁白和合成音乐。
- 尚不确定：本轮未渲染、未核验全部历史事实；不能把重建画面称现场档案。
- 本库复现候选：webgl；不是原片依赖认定或已适配声明。

- [源码已查看](https://github.com/WinterArc21/Battle-of-Austerlitz-Film/blob/86dae32d20f0a0f2395e7dc8938846fd51e355a6/web/engine/renderer.js)：检查到独立GL渲染器实现。
- [源码已查看](https://github.com/WinterArc21/Battle-of-Austerlitz-Film/blob/86dae32d20f0a0f2395e7dc8938846fd51e355a6/tools/render.mjs)：实际导入Playwright并调用FFmpeg。
- [作者制作记录](https://github.com/WinterArc21/Battle-of-Austerlitz-Film/blob/86dae32d20f0a0f2395e7dc8938846fd51e355a6/README.md)：作者列明地形、WebGL2、GLSL、Kokoro及事实简化。

<a id="recipe-negroni"></a>

## 配方逐步装入杯中的图解

[原作或作者入口](https://x.com/Ror_Fly/status/2102853258582880547)。较高关注且有公开制作规格的用法补充。

- 已披露或可查的做法：作者公开任务为HTML/JavaScript，从参考图生成连续配方演示。
- 尚不确定：具体库未披露；不是流体求解器证明。
- 本库复现候选：canvas2d / svg-html；不是原片依赖认定或已适配声明。
- [热度来源](https://createmotion.io/motions/ror-fly-9950f1/)：78,861次播放；指标日期：2026-10-15；检索日期：2026-11-03。

- [作者陈述的公开转引](https://createmotion.io/motions/ror-fly-9950f1/)：转引作者配方演示说明及输入范围。

<a id="talkinghead-broll"></a>

## 口播保留原声并补线稿解释画面

[原作或作者入口](https://x.com/AxtonLiu/status/2102827887732932956)。技术或用法补充。

- 已披露或可查的做法：作者规格保留原声、字幕、时长，人物画中画和概念补画。
- 尚不确定：最终绘图库未披露；未核对对齐或抠像结果。
- 本库复现候选：canvas2d / svg-html；不是原片依赖认定或已适配声明。

- [作者陈述的公开转引](https://github.com/X-RayLuan/awesome-opus-5-5-video-prompts/blob/b9524552dfcf96c4bf3569fa1145f94b63bc2a76/README.md#axtonliu-talking-head-to-line-art)：公开转引作者的原声保留和画中画要求。

<a id="sqlite-tour"></a>

## 七分钟代码库与查询执行讲解

[原作或作者入口](https://x.com/deedydas/status/2104391577091407965)。技术或用法补充。

- 已披露或可查的做法：作者陈述按代码地图、查询生命期、抽象和执行轨迹组织，提及外部TTS。
- 尚不确定：具体画面库未披露；不能据索引推断执行轨迹已验证。
- 本库复现候选：svg-html / canvas2d；不是原片依赖认定或已适配声明。

- [作者陈述的公开转引](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/92aee2f586ac0715cb3cbcb6384834f98a33383d/data/videos.json)：索引保留作者帖子说明；本轮未直接访问原帖。

<a id="manim-derivative"></a>

## Manim 导数概念教学

[原作或作者入口](https://x.com/LinearUncle/status/2103128559174971663)。技术或用法补充。

- 已披露或可查的做法：作者公开任务明确Manim和edge-tts。
- 尚不确定：本轮仅读转引任务，未取得或执行源码。
- 本库复现候选：独立外部渲染路线，按指南评估；不是原片依赖认定或已适配声明。

- [作者陈述的公开转引](https://github.com/X-RayLuan/awesome-opus-5-5-video-prompts/blob/b9524552dfcf96c4bf3569fa1145f94b63bc2a76/README.md#linearuncle-derivative-lesson-manim)：具体Python路线来自作者任务，不表示所有科普都用Manim。

<a id="runway-documentary"></a>

## 调用Runway的超智能纪录片

[原作或作者入口](https://x.com/gavinpurcell/status/2103304514329854102)。技术或用法补充。

- 已披露或可查的做法：作者披露提供Runway MCP访问，代理统筹纪录片。
- 尚不确定：完整剪辑链和具体生成步骤未核实；不能归为全片代码绘制。
- 本库复现候选：canvas2d / remotion；不是原片依赖认定或已适配声明。

- [作者陈述的公开转引](https://github.com/X-RayLuan/awesome-opus-5-5-video-prompts/blob/b9524552dfcf96c4bf3569fa1145f94b63bc2a76/README.md#gavinpurcell-superintelligence-documentary)：公开转引作者工具访问陈述。

<a id="glass-mosaic"></a>

## WebGL2玻璃金箔拼片短片

[原作或作者入口](https://x.com/LCSlates/status/2102503027340988559)。技术或用法补充。

- 已披露或可查的做法：作者公开规格明确WebGL2/原生JavaScript和浏览器声音合成。
- 尚不确定：任务描述不等于已核对全部源码与材质实现。
- 本库复现候选：webgl；不是原片依赖认定或已适配声明。

- [作者陈述的公开转引](https://github.com/X-RayLuan/awesome-opus-5-5-video-prompts/blob/b9524552dfcf96c4bf3569fa1145f94b63bc2a76/README.md#lcslates-glass-mosaic-film)：转引作者要求，具体库声明与视觉效果分开。

<a id="blender-clay"></a>

## Blender黏土外观角色演示

[原作或作者入口](https://x.com/alexalbert__/status/2102458348511879448)。技术或用法补充。

- 已披露或可查的做法：公开演示记录为Claude驱动Blender。
- 尚不确定：作者未分享提示词；未核实Python脚本、具体渲染器或源码。
- 本库复现候选：独立外部渲染路线，按指南评估；不是原片依赖认定或已适配声明。

- [索引描述](https://github.com/X-RayLuan/awesome-opus-5-5-video-prompts/blob/b9524552dfcf96c4bf3569fa1145f94b63bc2a76/README.md#alexalbert-blender-claymation)：仅作为外部3D路线案例，不声称本库可直接运行。
