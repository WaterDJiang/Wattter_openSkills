---
name: wtt-code-video-studio
description: 代码视频工作室。把想法、文章或剧本制作成前端代码动画与MP4，也可只交剧本、分镜、提示词、对白字幕或指定片段，支持逐镜选风格后组装；按内容推荐五方向，先展示四帧拼图，经用户确认再完整渲染。支持概念解释、个人宣传、产品教程、纪实、数据、地理推演与地图明信片，以及文字/SVG/交互输出、默认个人音色、角色对白和素材版本审阅。
---

# 代码视频工作室

内容和实际旁白决定时长；风格标签不是自动绘图引擎。共用流程是内容→方向→真实代码小样→四帧拼图→用户确认→完整渲染→最终审阅。

## 先按任务进入

| 当前请求 | 必要读取与动作 |
|---|---|
| 只交某阶段、指定段落/镜头，或分镜后分别选风格再组装 | 先识别本次交付物与镜头范围，按[分段创作](references/staged-creation.md)直接从已有稿接手。分镜可先于风格；文字到稿即停，进入镜头或全片制作才走对应审片门 |
| 新想法/主题/文章做片 | [编剧与时长](references/story-and-timing.md)；先构思内容，再识别具体用法（含下行地理推演），用目录筛选，按[方向选择](references/style-selection.md)给五种完整方向 |
| 战役/迁徙/贸易路线/疆域或传播的空间演变 | 前置识别为`geographic-explainer`，运行`catalog.py list --use-case 地理推演 --view summary`；读[地理叙事](references/geographic-storytelling.md)的路线判断，按空间因果推荐五方向。以地方氛围/景观展示为主则走地图明信片；已选风格、纯文字或局部修订仍按对应范围执行 |
| 已指定/已选风格、明确委托代选 | 沿现有决定，读取该风格STYLE及已有的固定SOURCE或原创专项方法和[风格保真](references/style-fidelity.md)；免重复五选，制作镜头或整片视频时须四帧审片 |
| 已有工程改字号/遮挡等 | 读当前选择/代码/素材锁及[制作契约](references/production.md)受影响阶段；不重init/编剧/选五种/生成未变配音。画面变更出新版拼图，原样重跑沿有效确认 |
| 已有获批成片只换声音 | 读[纯音轨修订](references/audio-revision.md)；独立修订目录完成素材diff与锁定，流复制画面并验证全部帧一致；不改字幕/时序或伪造新四帧批准 |
| 只要文字/剧本/静态图/交互页/纯音频 | 在用户范围交付；概念任务读[解释模型](references/explanation.md)，纯音频读[配音](references/voice.md)。纯文字不init/doctor/五选；静态图和纯音频不套视频四帧门 |
| 维护本Skill | 读局部AGENTS和对应Spec/测试索引；不把维护历史加载到普通做片上下文 |

## 目录先摘要，选定再深入

- 六类用途为知识、故事、产品、纪实、数据、创意；24种具体用法与114项风格多对多映射。先根据内容目的识别用法，地理推演可跨知识/纪实/数据/故事，不新增开场分类问卷。用户要全目录时展示[分类](references/classification.md)/[风格库](assets/gallery/styles.html)，普通任务不全量读取JSON、映射表或SOURCE。
- 按内容运行 `python3 scripts/catalog.py list --use-case 个人宣传 --view summary`（也可`--purpose knowledge`/`--query 水墨`），候选细查 `python3 scripts/catalog.py show desktop-flythrough --use-case 个人宣传`，再读相关STYLE。分页不是推荐排名，不拿源目录前五项直接当五方向。
- 新主题比较至多三种有意义的内容结构并择优，保存script.md；已锁剧本不重编。五方向比较同一关键镜头，说明内容动作→媒介机制→可见结果、素材/声音、依赖与实测边界，不能固定五名字换字。
- 用途、叙事策略、画风、主体/效果、技术、输出分别判断。角色可由沙画或粒子构成；Three.js/Remotion是技术。方法收录、单片实测、可复用脚手架、通用后端分开标识。
- 参考热门作品时才读[案例选型](references/case-driven-techniques.md)，用 `catalog.py cases --use-case 概念解释`检索依据；区分原作披露、复现建议与未知，不凭画风猜代码。

## 两个明确的用户节点

- **方向选择**：新视频对未定范围提供五方向（1首选+4备选）；已指定/已选/明确委托直接记录style-choice.md，不重复提问。没有决定保持pending；原文、既有授权与用户本次要求优先。
- **四帧审片**：新视频与会改变画面的修订在完整渲染前，先展示来自当前真实代码的2×2四张样帧拼图，包含帧号/时码；选能判断构图、关键变化和收尾的时刻，避开全白首尾。高风险动作另做短序列自查，四静帧不证明动作通过。获批画面只换声音限上述专用修订入口。
- 等用户明确确认该拼图，再记录原话及版本并继续。风格选择、自动检查通过、普通“继续”不替代四帧确认。无需再设脚本/配音等审批站；多版本可同批展示并确认，记录覆盖的版本。
- [四帧审阅](references/preview-review.md)规定指纹、确认命令和变化失效；代码/时序/素材/拼图变化不能冒用旧批准。完全一致重跑复用记录。素材变更仍独立走下述版本审阅，代码变化不触发素材确认。

## 按内容读专项

| 内容/画面需要 | 读取 |
|---|---|
| 原理、机制、反事实；寓言后揭示 | [解释模型](references/explanation.md)、[编剧](references/story-and-timing.md)；故事结束后解释映射和边界，不强迫所有科普用寓言 |
| 纪录片/档案/新闻/多机位 | [制作形式](references/video-formats.md)、[视频素材](references/footage.md)；用户材料优先、互联网补缺，来源/事实/推断/示意分开，直播外观不冒充直播 |
| 季节地图/地方明信片 | [地图模板](references/seasonal-map.md)→[地点研究](references/map-research.md)、[配色与相机](references/map-art-direction.md)、[地点声音](references/location-sound.md)；含孟菲斯微缩配方，按地方/季节/氛围选色，同色系也可，不锁示例色卡 |
| 地形地图/历史战役/迁徙贸易路线/地球镜头 | [地理叙事](references/geographic-storytelling.md)；先区分真实地理、虚构插画与真实三维，再用`catalog.py libraries --route terrain-2d --view summary`等检索[库功能](references/frontend-libraries.md)，选定后细读；库研究不是预装后端 |
| 手绘电影、原创角色表演 | [手绘电影动画](references/handpainted-cinema.md)；形体笔触、景层、接地和道具关系落实到本片 |
| 产品/机械/路径连续镜头 | 适用时读[镜头排布](references/video-layout.md)，通用工艺见[视觉工艺](references/visual-craft.md)；不让产品版式覆盖其他画风 |
| 绘图库适配/风格沉淀 | [画法选型](references/visual-recipes.md)、[风格保真](references/style-fidelity.md)；用户要求保存个人风格时读[风格包](references/style-pack.md) |

## 生产与不可省略的边界

读[制作契约](references/production.md)，在独立空目录init；按剧本重写场景，不把起步模板当成片。逐镜混搭先按[连续动作与画法交接](references/style-continuity.md)确定跨镜锚点，能共用动作与相机时只改变画法，预览时密采切点。只在需要时读取声音/素材详细操作：

- init轻量检测声音配置，缺项直接读[音色配置](references/voice.md)，不自动下载模型。有效defaultVoice默认沿用；路径失效按该指南先搜索/核验原资源，不能断言已删除或换系统声。多人对白先绑定角色与逐句表演，按实际后端能力执行，不把角色全套成旁白。坏配置报错；私人录音、模型与凭据不入开源包。
- [素材审阅](references/material-review.md)：首次可搜索下载选材并记录来源/许可/使用依据；seal锁定ID、路径、URL、许可、SHA256与导流。重跑check一致直接执行；变化先可读diff，未确认只存候选，不覆盖当前素材/清单或验收。明确替换对象与目标视为授权，仍保留diff；禁止重下载同名文件或重建锁绕过。
- 以film.json为内容源，timeline由真实配音编译为整数帧；超时回到内容取舍，不裁音/加速。字幕字符权重是近似定位，不称ASR逐字对齐；音乐/动作按内容编排。
- 每帧从帧号/seed/资产重建，await素材就绪，暂停/拖动/导出共用状态；真实小样保留材质/造型/空间/原生动作。新增库固定版本、本地化并保留许可，未运行不称支持。
- 素材锁→时间轴/混音→preview及四帧拼图→用户确认→render→finish。地图等专项导出也不能绕过四帧；旧工程tools不自动升级，迁移见[兼容说明](references/migration.md)。
- 最终MP4后按[视频质量](references/video-quality.md)执行review-init、实看缩小图/连续片段、填写visual-review.json、review。技术检查、图像审阅、主观试听、用户采用分别报告，不能把确认样帧当作成片验收。

视频交付MP4、剧本/分镜、选择与四帧确认、可复跑代码、素材锁和检查证据；待确认只交预览并说清状态。没有发布/部署授权不对外发布。

参考片复现交付说明实际来源：外部数据/素材、代码自绘、图像生成及原片音画分别列明；不把真实底图处理说成全部代码生成，也不把风格参考说成复用原帧。
