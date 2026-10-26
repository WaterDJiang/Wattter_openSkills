# CONCEPT-EXPLAIN-01 验证记录

日期：2026-10-20。对象：当前工作区的 `wtt-concept-explainer` 初版。

## 初版结果与范围（CE-05 前的历史记录）

- 主指令 72 行；运行内容仅 `SKILL.md` 和 `references/adaptation.md`，无执行脚本、框架或模型 API 依赖。
- 已生成 [文字小样](text-smoke.md) 和 [单文件 HTML](cache-demo.html)。这是当前作者会话的小样，不是独立上下文评测，也不是跨模型对照。
- TEXT-01：人工核对木→火、水→木和参照点表述，无额外吉凶或强弱分数。留档文件由维护任务保存，原输入要求的回答形式仍是纯文字。
- HTML-01：Node 检查真实内联模型及 DOM 读数；桌面浏览器实际点击、键盘 Enter 和重置通过。
- SPACE-01 / LIMIT-01 / STATIC-01 / STACK-01：验收输入已定义，尚未实际生成；不得写成通过。
- 手机尺寸、其他浏览器、读屏软件与多个模型尚未实测。具备可移植指令结构，不等于这些环境的效果已验证。
- 未安装到全局运行目录，未提交、推送或部署；用户尚未确认采用。

## 可复跑检查

在仓库根目录：

```sh
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/wtt-concept-explainer
node skills/wtt-concept-explainer/tests/check-cache.cjs
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
git diff --check
```

第一条依赖维护机现有 `skill-creator` 检查器及 PyYAML，不是本 Skill 的运行依赖。

实际输出：

```text
Skill is valid!
PASS: 首次访问、命中不续期、到期边界、延迟重建、重复请求、重置及 DOM 读数
Registered skills: 49 Entrypoint lines: 72
```

注册核查调用现有 `scripts/deploy_skills.py` 的只读函数 `registered_skills(Path.cwd())`，校验目录存在、命名一致、无重复；未执行部署。相对链接与 README/marketplace 数量核对见规格执行记录。

## 浏览器证据

通过 Codex 内置浏览器访问本地预览，使用实际按钮和键盘输入：

| 操作后 | 可见结果 |
|---|---|
| 初次请求，推进 30 秒，再请求 | 版本 1；写入 0 秒；到期 60 秒；提示没有续期 |
| 再推进 30 秒 | 已到期；剩余 0 秒；等待下次请求 |
| 在请求按钮按 Enter | 版本 2；写入 60 秒；到期 120 秒 |
| 重置 | 时间 0 秒；空缓存；尚未写入 |

[桌面截图](cache-desktop.png)。已查看标题、状态块、按钮和解释文字，没有发现遮挡。页面可纵向滚动；未声称全部内容在一屏内。

## 保留的失败与环境限制

初次命令：

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory skills/wtt-concept-explainer/tests
```

原错误：`PermissionError: [Errno 1] Operation not permitted`。沙箱禁止监听本地端口；同一命令经工具权限审核后成功启动，只绑定回环地址。浏览器检查完成后停止服务。

本机项目未安装 Playwright，因此未新增该依赖，使用现有浏览器工具完成桌面检查。

服务日志另有浏览器自动请求 `/favicon.ico` 的 `404 File not found`；示例未配置站点图标，正文请求为 200，交互结果如上。服务已停止。

## CE-05 视觉修正结果

用户否定初版视觉效果。初版功能证据保留，不作为视觉验收通过或用户采用的证据。

- 主指令现为 78 行；增加视觉工艺参考与一个可选离线样例。运行资源现为 3 份 Markdown + 1 份 HTML，没有模型 API、CDN 或第三方库依赖。
- 已实际查看 Anatomy 官方 dial-indicator 截图，提取主体装置、细线、立体明暗、独立底座与仪表工艺；未复制图形源码。
- 新 [缓存装置](../assets/cache-apparatus.html) 包含底座、存储匣、数据源层板、刻度盘和独立路径；同一状态驱动读数、表盘、有效标记、存储匣开合与路径强调。
- [桌面截图](cache-crafted-desktop.png)、[390 px 截图](cache-crafted-mobile.png) 已实际查看。修复首轮表盘文字重叠、入口标注悬空和手机裁切。窄屏改为完整显示主体并将必要说明移到图外，微刻度仅作细节，准确数值由外部读数显示。
- 浏览器实际操作：30 秒命中不续期，60 秒到期；手机上按 Enter 请求后版本 2、到期 120 秒；自动演示最终返回“演示一轮”并到达版本 2 的正确状态。浏览器错误日志为空。
- 新 `node skills/wtt-concept-explainer/tests/check-crafted.cjs` 检查真实内联模型、SVG 属性及回放位置；验证自动演示定时任务与停止清理。输出：`PASS: 缓存边界、存储匣开合、表盘、有效标记、命中/回源路径、路径回放、重置、自动演示与停止`。
- 旧模型测试回归通过；`quick_validate.py` 与 `git diff --check` 通过。
- 等待自动演示时出现 `Playwright selector deadline exceeded` / `locator.waitFor(visible) timed out`，未以此记通过；随后独立读取 DOM 确认了正确终态。工具调用结束时间短于请求的 12 秒，具体超时机制未确定；未证明连续每帧均无问题。
- 这是当前会话设计和验证的第二版，未做独立模型生成对照；复杂管路、真实 3D、多个抽象主题的视觉质量仍未验证。观感是否达到用户预期，等待用户判断。

## CE-06 发动机复杂样例

- 产物：[四冲程发动机](../assets/four-stroke-engine.html)，自包含 SVG/CSS/JS，无外部库；可选示例已链接到主指令。
- `node skills/wtt-concept-explainer/tests/check-engine.cjs` 对实际内联模型采样，不另写替代模型。输出：`PASS: 1441 个相位；杆长最大误差 5.68e-14；气门/活塞最小净空 24.00 绘图单位；上下止点、气门相位、点火窗口与循环连续`。
- 浏览器真实操作与 [四相位读数](engine-phases.json)：90° 进气门开、270° 双阀关、450° 双阀关、630° 排气门开；固定杆长几何使四个中间相位行程均为 57.9%，并非错误地按时间百分比显示行程。
- 单步从 630° 到 645°；0.5× 选项生效；播放从 645° 推进并越过循环，暂停在 110°；滑杆 Home/ArrowRight 到 1°，原生滑杆设值到 370°，界面同步切为做功。复位回到 0° 止点。
- 外壳按钮实测遮住内部并改为“返回剖面”，再次点击恢复；气门部件按钮更新说明与强调。
- [桌面点火截图](engine-desktop.png)、[手机截图](engine-mobile.png)、[进气](engine-phase-0.png)、[压缩](engine-phase-1.png)、[做功](engine-phase-2.png)、[排气](engine-phase-3.png) 留档。已查看点火、进气、压缩、排气与手机画面；390 px 视口的文档宽也是 390 px，无横向溢出；浏览器 error 日志为空。
- 保留测试失败：`locator('#speed').selectOption('0.5')` 返回 `Playwright selector deadline exceeded` / `locator.selectOption failed for selector #speed`；实际选项值为 `.5`，修正测试值后成功。`locator('[data-part="valve"]').click()` 返回 `Timed out after 3000ms waiting for selector [data-part="valve"]` / `No element matched selector`；实际部件名为 `valves`，使用页面的 `[data-select="valves"]` 控件后成功。均为测试定位问题，未静默计为通过。
- 这是教学剖面与理想化相位，未实现真实配气提前/迟闭、完整驱动、润滑和冷却回路、燃烧热力学；未声称 CAD/工程仿真精度。单机浏览器与当前作者会话通过，不等于跨模型、跨浏览器或用户视觉认可。
- 最终模型复跑、Skill 结构检查、22 个 Markdown 相对链接及 `git diff --check` 通过。8766 预览服务已停止；正文请求 200，浏览器自动请求 `/favicon.ico` 返回 `404 File not found`，没有站点图标，不影响正文交互。

## CE-07 双输出与视频制作规则

- 当前入口 84 行，视频细节按需加载；README、marketplace 描述及规格索引已同步。未改变安装分组数量，也未改 code animation 的管线协议。
- VIDEO-01 实际编写 [发动机分镜小样](engine-storyboard.md)：六镜、估时 54 秒，覆盖旁白、相位、镜头、屏幕文案、具体文字效果与配音后的语义校时锚点；实际配音/帧时序未生成。
- 人工路由走查：形式未知时只问一次二选一；已指定页面或视频不重复问；纯文本/静态图保持原路线；双输出共用模型；已有外观沿用；没有下游技能仍可指导制作，缺配音/编码能力如实标注。这是指令一致性审查，不是独立模型执行结果。
- 复用核对：视频参考明确 `code-animation/v1` 的 `visual` 不自动生成主体、字符权重字幕不是逐字同步、原发动机页尚需帧接口适配；没有把设计字段伪装成下游已实现功能。
- `python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/wtt-concept-explainer`：`Skill is valid!`。`python3 -m json.tool .claude-plugin/marketplace.json > /dev/null` 及 `git diff --check` 通过。
- `node skills/wtt-concept-explainer/tests/check-engine.cjs`、`check-crafted.cjs`、`check-cache.cjs` 全部通过，原交互实现未改。
- 新增 OUTPUT-01 / VIDEO-01 / VIDEO-02 / VIDEO-LIMIT-01 / DUAL-01 验收输入；除 VIDEO-01 分镜小样及上述人工走查外，尚未端到端生成。未运行配音、视频帧接口、编码或试听，不宣称视频已实测、跨模型通过或用户采用。
- 本轮仅修改工作区技能与文档；未提交、推送或运行安装更新。

## CE-08：真实视频 Demo

- 用户要求“出一个视频的 demo”，实际产出 [发动机讲解 MP4](../../../outputs/concept-engine-demo/final.mp4)，对应 [锁时分镜](../../../outputs/concept-engine-demo/storyboard-timing.md) 与 [完整检查记录](../../../outputs/concept-engine-demo/review.md)。
- 60.967 秒、1,829 帧、1920×1080、30 fps、H.264/AAC；使用已配置默认音色，13 个配音句段。无背景音乐。
- 原 code animation 的 `asset_review seal` → `timeline --lock` → `mix` → `render --preview` → `render --render` → `finish` 实际运行通过；最终 delivery-check.json 为 passed=true，decodeErrors=[]，samplePeakDbfs=-3.0。
- 项目新增 SVG 帧入口，未改原发动机页面。程序抽取 68 个代表帧；5 个乱序重绘样本一致、浏览器错误为空。已查看关键阶段截图、最终帧及成片两秒连续抽帧；首轮问题与原截图保留。
- 首次 TTS 因沙箱无法访问 Metal 失败：`ImportError: [metal::load_device] No Metal device available`。权限审核后同一配音命令成功，原日志与成功日志在工程中保留。
- 本机当前组合的声音生成、视频渲染与技术合成已跑通。没有可用主观试听通道，发音/音色相似度及主观音画节奏未验收；字幕为整句显示、镜内事件为导演编排，不宣称词级强制对齐。用户采用与跨模型质量仍待确认。

## CE-10：用户选定 B 配色

- 主指令与视觉参考采用克莱因蓝 `#002FA7` / 冷白 `#F3F6FB` 默认；明确用户指定可覆盖默认。发动机页面已同步；旧缓存样例只借用结构，使用时按当前规则配色。
- 实际内联模型回归 1,441 个相位通过；网页进气 90°、做功 450°、排气 630° 状态正确。查看桌面及 390px 嵌入视口，主体与控件无可见遮挡；不等同真实手机测试。
- 17 个文字/背景配对最低 4.69:1；样式检查包含选中按钮与主按钮。气体浅橙和深橙文字分开配置。
- [蓝版成片](../../../outputs/concept-engine-demo-blue/final.mp4)：1,829 帧 / 60.967 秒，1920×1080、30 fps、H.264/AAC；完整解码通过、峰值 -3.0 dBFS。68 个程序抽帧、5 个乱序一致性样本通过，查看四阶段及编码后 28.9 秒截图。
- [检查记录](../../../outputs/concept-engine-demo-blue/review.md) 保留证据与限制：旁白沿用，未主观试听；B 色板为用户采用，新成片观感仍待用户判断。原 MP4 哈希未变，未安装或发布。
- Skill 验证、修改的 Markdown 相对链接、JS 语法与 `git diff --check` 通过。

## CE-11：制作前确认规则

- 入口、视觉参考和视频参考统一为：模型与方案设计 → 构图/主体样图及脚本确认 → 正式制作。确认前允许必要静态样图，不做配音或完整页面/动画/视频。
- 同步发动机分镜小样：记录待确认状态、历史主体截图的适用范围，以及正式发起确认前还需补充当前构图样图；未虚构样例获批。
- 人工对照 APPROVAL-01～08：未确认视频停止在方案；只选 B 保持其他项待确认；v2 全部批准后执行；无回复保持等待；主动换主体重审受影响内容；无图像工具说明限制后以文字草图确认；明确免确认时按用户要求执行；标签修复无需重审。这里只是当前作者对指令路径的走查，不是独立模型生成测试。
- `quick_validate.py` 输出 `Skill is valid!`；主指令 96 行。修改文档的相对链接及 `git diff --check` 检查通过。
- 仅修改技能规则、参考和测试文档；未改运行脚本、模型或素材，未重渲染 Demo，未运行安装更新、提交或推送。

## CE-12：玄学与宇宙题材表达扩展

- 入口改为先选解释策略，再设计画面；新增情境叙事、空间漫游、尺度变换、对照实验、象征意象、多视角观察。主体可为场景或事件，既有机械样例不再充当所有题材的默认路径。
- 适配参考扩展传统意象/八字阅读故事/房间漫游，以及宇宙尺度、视角、时间、观测与模型、思想实验；不提供未经核验的具体领域结论或数值。保留蓝白默认与 CE-11 制作前确认，确认方案增加解释策略。
- 人工走查 EXPRESSION-01～05：诗性题材可走意象而非拆解；房间探索保留未知口径；宇宙尺度保留参照与示意标识；观测/模型/艺术表达分开；无 3D 工具仍可设计分层和序列图。只证明指令路径可选，不代表已经生成或跨模型验证。
- Skill 结构、修改文档相对链接、`git diff --check` 检查通过；未改运行模型或管线，未新增图片/视频、安装、提交或发布。

## CE-13/14：八字意象案例真实生成

- 用户先批准 BAZI-01 v1 的脚本、构图与图例，再选择 B 视频；真实执行制作前确认。
- [本地成片](../../../outputs/concept-bazi-video/final.mp4)：41.100秒、1233帧、1920×1080、30fps、H.264/AAC；9句中文旁白、1张蓝白庭院图与原生文字动画。
- 42个抽样帧、5个乱序重绘样本一致，浏览器错误为空；完整解码通过，峰值-1.8 dBFS。已查看关键画面、编码后31秒画面和3秒连续抽样；修正过CSS加载和转场叠字，失败证据保留在[检查记录](../../../outputs/concept-bazi-video/review.md)。
- 解释策略使用庭院与树意象，区分传统术语与教学隐喻，未作个人预测。静态背景配二维镜头，不宣称真实3D漫游。
- 本机真实生成通过；未主观试听发音/音色，字幕非词级强制对齐，成片观感待用户确认，跨模型环境未验收。未安装或发布。

## CE-15：独立视频制作能力

- 本技能内置配音、素材锁、时间轴、混音、逐帧导出与检查，运行不依赖另一 Skill。保留兼容数据协议；共用第三方程序、权重和只读用户音色资料。
- 86项行为测试通过；独立安装副本完成6.7秒真实中文旁白MP4，默认PNG模板路径也通过。两条路径完整解码、5个乱序一致性样本各自通过；错误舞台尺寸按预期拒绝。
- [完整验证与失败记录](ce15-independent-video.md)区分真实生成、图像检查、未试听及未进行的跨模型验收。原 Skill 与旧成片保留；未执行安装更新。

## CE-16：癸水2027实际成片与混音回归

用户确认后完成171.733秒独立视频；新增长片响度归一化后的采样长度修复，全套87项测试通过。真实运行、失败尝试、成片和未验收边界见 [CE-16记录](ce16-gui-water-video.md)。

## CE-18 视频质量约束内置

- 将CE-17用户认可的修订方法转为独立质量参考、模板字号/溢出保护、最终成片证据生成与审阅记录校验。
- 101项Python回归、3种画幅浏览器正反例、5秒真实导出与review闭环通过；首轮竖版fixture错误及真实边界保留。详见[CE-18验证](ce18-video-quality.md)。
- 仅工作区，未安装/提交/发布；未用记录检查代替审美判断或主观试听。
