# 代码视频工作室

输入一个想法、主题、文章或剧本，生成中文剧本、分镜、前端动画、配音和 MP4。时长由内容和实际旁白决定，不固定为 30 秒。动画由前端代码逐帧绘制，经浏览器和 FFmpeg 导出。

## 在 Codex / Claude Code 中使用

把本目录完整放入工具支持的 skills 目录，保留 `SKILL.md`、`scripts`、`assets`、`config`、`references`。本仓库已有安装工具，批量安装方法见仓库根 README；单独使用本 skill 不需要安装所有技能。

在对话里输入：

> 使用 wtt-code-video-studio，把“一个人第一次学会骑自行车”的故事做成动画。面向成年人，温暖幽默，横屏，时长按内容决定。先推荐画风让我选，配音使用本机可用声音。

也可以提供文章、现成剧本或参考视频。一般内容会改编为可视化剧本；要求保留的原文或现成剧本按你的约束处理。编剧后提供五种风格方案（一个首选推荐和四个不同备选），由你选定；已明确指定风格就直接沿用。人物可以由沙粒、粉笔或粒子呈现。

> 使用 wtt-code-video-studio，介绍我的开源项目。采用沙画，用我配置好的本地个人音色，配置文件在项目的 `.voice-local/voice.local.json`。先生成一段试音，采用后再做整片。

## 分类与完整风格库

- 六类用途：知识、故事、产品、纪实、数据、创意。
- 参考目录完整覆盖11组66条；与本库原有风格去重后，共81项方法（含15项本库补充）。这与用途数量、样片数量分别统计。
- 打开[完整风格库](assets/gallery/styles.html)，可按用途、风格组和关键词筛选；每条都有中文适配、完整方法原文、来源与验收要点。方法已收录不代表81项全部已有本库成片测试，原画廊样片为6片，新增地图模板另有20秒工程测试。
- 五方向从全库按剧本筛选；指定“黑板粉笔”“产品拆解”等可直接定位，不需要层层选目录。
- 方法原文按MIT许可保留来源和声明，见[第三方归属](THIRD_PARTY_NOTICES.md)。媒体仍全部使用自有示例，不搬运参考仓库样片。

```sh
python3 scripts/catalog.py list --purpose documentary
python3 scripts/catalog.py list --query 水墨
```

## 原创样片

从[六类导航](references/classification.md)查看“用途 → 形式 → 风格 → 技术”的完整路径，打开[原创样片画廊](assets/gallery/index.html)观看六个新制短片及静帧。一般调用自动识别用途，编剧后只进行一次五方向选择，不增加开场分类问卷。

原概念解释能力已经合入：文字、静态SVG、交互HTML仍可单独输出；调用同一个 Skill，说明想要的产物即可。两个旧入口的配置和项目兼容见[迁移说明](references/migration.md)。

## 可以制作哪些类型

除原有角色/沙画/粒子动画，还可以按内容设计界面连续变形、像素动作循环、贯穿母题的历史/科普影像、真人素材与代码合成、公式机制推演。它们是制作配方，可从完整风格库选择并组合；新增画面仍按片实现，外部 3D、抠像、Manim 等路线需要单独适配与验证，不能只改配置就生成。

例如：“介绍我的待办产品，沿用已选的黑白 UI 风格，让同一个组件从新增任务变成进度与完成状态。按我提供的 120 BPM 音乐排动作，先检查关键动作前后的画面。”

新增节奏配置支持 BPM 或已核对的拍点，把动作事件和音效定位到同一帧；不内置自动测拍，也不会为了卡点裁切旁白。预览会输出 `preview/index.html`，可看带时间码的边界/事件帧；循环请求增加首尾连续帧供审查，报告不自动宣称无缝。

详见 [制作类型与导演方案](references/video-formats.md) 和 [节奏配置](references/production.md#节拍与动作事件可选)。已有个人音色、素材审阅和一次风格选择规则保持不变。

## 用寓言讲清一个概念

编剧时可以采用“先故事、后揭示、再解释”的写法；分镜会标明伏笔、揭示点和解释镜头。它不限定画风，也不会把所有内容都强制改成寓言。研究生水平只在你要求时采用，已有主题或剧本优先。

> 使用 wtt-code-video-studio，从机器学习领域选择一个研究生水平的概念，面向有基础的读者写一个寓言动画剧本。不要开头点破概念，用行动和后果铺设线索，接近故事结尾再揭示；故事结束后解释准确含义、情节对应关系和类比边界。先交付剧本和粗分镜，时长按内容决定，这次不制作视频。

需要成片时改为“制作动画视频，先推荐画风让我选”。故事后的解释也计入总时长；寓言是虚构的机制说明，不作为真实案例或理论证明。详细写法与提示词见 [编剧参考](references/story-and-timing.md#可选写法寓言式概念揭示)。

## 第一次使用：检查模型和个人音色

首次制作会读取你已有的声音配置，检查模型文件、默认音色、参考录音、对应文字和 `referenceTextVerified`。新项目 `init` 自动检查；缺项会提醒具体要补什么，配置齐全则默认使用 `defaultVoice`，无需再次选择。

也可以手动检查（在本 Skill 目录执行）：

```sh
python3 scripts/voice.py doctor --project /path/to/my-film
# 指定已有配置时：
python3 scripts/voice.py doctor --project /path/to/my-film --config /path/to/voice.local.json
```

配置顺序：显式 `--config`/`--voice-config` → `CODE_VIDEO_VOICE_CONFIG` → 旧环境变量（两者并存须指向同一配置）→ 项目 `.voice-local/voice.local.json` → 用户 `~/.config/wtt-code-video-studio/voice.local.json` → 旧用户目录。兼容 `CODE_ANIMATION_VOICE_CONFIG`、`CONCEPT_EXPLAINER_VOICE_CONFIG` 与两个旧 Skill 用户目录；旧目录同时存在不同配置时报告冲突，用显式路径选定，不自动换音色。`config/voice.example.json` 是公开模板，不能把模板存在当作模型/音色已配置。

缺少配置时，参考 [配音使用指南](references/voice.md)：将模板复制到项目或用户级私人目录，填写模型路径与清单、参考录音和逐字文本；核对文字后设置 `referenceTextVerified: true`，再运行 `voice.py check`。声音模型目录和模板仍使用下面已有的 config 文件，不新增另一套配置。

首次检测只读本地配置和所指文件，不下载、不合成、不上传录音，不显示录音正文。`configured-unverified` 表示配置与文件已找到，完整 SHA256、录音格式与平台校验仍在正式 check/合成时执行。缺项提示不阻塞编剧和画面；无需个人音色时可继续使用原系统/外部配音路线，已指定个人音色却配置无效时会明确报错。

## 依赖与生成流程

- 视频：Python 3、Node.js、FFmpeg/FFprobe、Playwright、Chrome/Chromium。
- 默认画法：Canvas 2D；按镜头可引入本地固定版本的 p5.js。新增画风需要写对应场景代码，目录标签不是自动绘图引擎。
- 默认配音：自动使用已配置的 `defaultVoice`；未配置时 macOS 用 `say`，其他系统接入外部配音。
- 可选个人音色：Qwen3-TTS MLX，当前实测环境为 Apple Silicon Mac。无需为了普通动画先下载声音模型。

`film.json` 保存内容；`timeline.json` 根据实际配音编译；字幕按标点和字数近似分配，并非逐字强制对齐。每段配音变化后，都重新锁定时间轴和导出。

手动操作时，从本 skill 目录开始：

```sh
python3 scripts/pipeline.py init /path/to/my-film
```

先由 agent 按剧本改写项目内的 `film.json`、`scenes.js`，并记录风格选择。然后在项目目录执行：

```sh
npm install --save-exact playwright
npx playwright install chromium
python3 tools/pipeline.py tts .
# 完成全部选材，填写 assets.json 的素材、来源、许可、使用依据与网页导流
python3 tools/asset_review.py seal .
python3 tools/pipeline.py timeline . --lock
python3 tools/pipeline.py mix .
node tools/render.cjs . --preview
node tools/render.cjs . --render
python3 tools/pipeline.py finish .
```

已有 Chrome 时可以跳过 Chromium 安装。`tts .` 自动读取声音配置，无配置才用系统声音；外部音频跳过此步。已有音轨按原规则保留，不反复生成。显式 `tts . --voice Tingting --rate 205` 表示本次改用系统声音。详细配置、依赖与故障入口见 [制作契约](references/production.md)。

## 素材管理

首次制作由 Codex 搜索、下载和选材，素材确定后锁定版本。以后内容一致直接重跑；更换素材、来源、许可或导流时，先展示旧值、新值、原因和影响。未确认只保存候选，确认后才提交新版并重新渲染验收。已明确指定本次替换对象和目标不重复确认，仍保留 diff。没有三档模式，也没有额外开场模式选择。

只改代码不触发素材确认。不要直接覆盖已有素材或重新 seal；候选提议、精确授权、历史保存和旧工程迁移命令见 [素材审阅说明](references/material-review.md)。`init` 会把该说明复制为项目的 `ASSETS.md`。

## 检索模型与配置个人音色

相关文件只有三个入口：

| 文件 | 用途 |
|---|---|
| [model-catalog.json](config/model-catalog.json) | 公开模型来源、固定版本、用途、平台和实测状态；可离线检索 |
| [voice.example.json](config/voice.example.json) | 多模型路径、多音色、默认音色与生成参数的模板；不包含任何人的录音 |
| [配音使用指南](references/voice.md) | 下载模型、配置音色、生成试音、按镜头配音，以及 Windows/Linux 外部音频接法 |

```sh
python3 scripts/voice.py catalog --query 克隆
python3 scripts/voice.py scan --root /path/to/existing/models
python3 scripts/voice.py voices --config /path/to/voice.local.json
python3 scripts/voice.py voices --config /path/to/voice.local.json --query 旁白
```

`catalog` 是维护过的目录检索，不会联网搜索所有模型；`scan` 只读指定目录，不扫描整台电脑。扫描结果是候选，`check` 才验证固定版本与文件哈希。音色 ID 是你自己给参考录音起的名字，与模型 ID 分开配置。

最短上手路径：按 [配音指南](references/voice.md) 安装独立环境 → 下载模型或填已有模型路径 → 放入参考录音和逐字文本 → 核对后设 `referenceTextVerified: true` → 检查配置/按需试音 → 批量配音。配置了 `defaultVoice` 后，Skill 默认使用该音色，不再每次询问或要求先试音。已有个人配置不会因切换主题而重新生成。

## 交付与开源范围

交付中文剧本、分镜、风格选择记录、可编辑源码、配音、MP4 和检查记录。声音检查分为“文件可用 / 正文核对 / 本人音色相似度”，最后一项由本人试听决定。

可分享本目录中的代码、目录与示例配置；个人 `voice.local.json`、录音、文字、模型权重和 `.venv` 保存在项目 `.voice-local/` 或仓库外，不放入技能安装目录。附带忽略规则只防 Git 误加；**手工压缩目录前仍需排除这些文件**。不要把自己的配置覆盖到 `voice.example.json`。

模型与第三方依赖各自遵循原许可证，模型来源链接保存在目录中。当前仓库尚未附代码 LICENSE，公开发布前由维护者确定；本次未擅自添加许可证。当前已接入 Qwen3-TTS MLX 本地克隆；云服务、其他克隆模型、Windows/Linux 本地推理尚未内置。可选 Whisper 目录项用于转录核对，不是配音音色。

agent 执行入口见 [SKILL.md](SKILL.md)。


## 用真实素材制作纪录片、新闻或多机位视频

可以只给主题，也可以附上录屏、实拍、图片或报告。Skill 先盘点用户材料，按剧本缺口自主检索互联网材料，记录来源和许可依据；已锁定材料沿原审阅规则复用。找不到证据不会生成假现场充当证据。五个推荐方向仍按内容决定，可组合制作类型与沙画、手绘等画风，不固定每次同一组。

- “用我提供的发布会录像做一段新闻播报，保留关键原声，缺少的官方资料自行检索。”
- “把这份调查报告做成视觉调查短片，区分事实和推断，时长按内容决定。”
- “将这几个机位做成倒计时事件回顾；没有同步依据的画面明确标记。”

本地工具现支持视频入点、正向变速、预抽帧和等待解码后逐帧绘制；原视频、处理清单及每帧纳入资产锁。不是自动全网配片、抠像、实时直播或自动多机位对齐。具体命令、候选替换、原声与迁移见 [视频素材接入](references/footage.md)。下载/选材由执行者使用现有搜索工具进行，不要求单独安装下载服务。

## 重新制作本轮原创示例

在本 skill 目录执行。输出必须使用新目录，不重跑/覆盖既有作品；不需要 TTS，不读取私人参考音频来合成。所有短片带新合成的事件音，无旁白。

```sh
python3 scripts/make_examples.py --out /path/to/new-original-examples --render
python3 scripts/catalog.py check
```

视频会经真实 Chrome/Playwright、FFmpeg 和素材门禁导出；依赖来自项目安装或 `PLAYWRIGHT_MODULE`，浏览器可用 `CHROME_PATH` 指定。`--render`会收集待审证据，**不自动写视觉通过**；正式使用先查看代表帧，再完整制作。分类和画廊只从 `config/capabilities.json` 生成，改元数据后运行 `python3 scripts/catalog.py build`。

## 最终成片检查

`finish`是技术验收。实际成片的视觉证据用下列命令建立：

```sh
python3 tools/pipeline.py review-init .
# 查看 quality-review 的图/动作片段，填写 visual-review.json 的实际观察
python3 tools/pipeline.py review .
```

审阅缺失、成片/证据过期、素材发生未批准变化均不能标成片验收通过。JPEG逐帧导出可用 `node tools/render.cjs . --render --frame-format jpeg`；抽帧/确定性检查仍使用PNG。

个人风格可显式保存在库外用户目录，见[风格包](references/style-pack.md)。本版没有自动ASR、ducking、多worker、个人风格市场；Three.js等是可接入路线，不是全部预装的后端。

## 两项本库新增能力

- [季节地图明信片](references/seasonal-map.md)：地点/季节/乡村城市可配置；默认20秒、1080方形、30fps，鲜明粉彩，同一支片内俯视→两侧斜俯视→回俯视，连续循环。共享frame(i)，Node+node-canvas导出PNG；正式音乐/环境声按地点研究，Python八音盒/8bit作原创示范或兜底；含未遮罩世界和编码视频接缝工具。完整代码在assets/map-postcard，运行命令见配方。
- [手绘电影式角色动画](references/handpainted-cinema.md)：默认沿《晚风来信》V2纯Canvas工艺：形体内笔触、暗前景/亮远林、衣料明暗、接地步态、手腕/道具共享状态和叙事镜头。[原创源码示例](assets/handpainted-cinema/README.md)随Skill提供；先审静帧、再测动作。12秒仅为工程示例，正式时长按内容/配音确定；不宣称原参考同等画质或其他引擎已测。

地图首次使用默认是示意小镇；正式地点中英文、坐标和真实地图要求先核对。已指定本配方不重复五选。其20秒参数不影响其他视频的自适应时长。

## 手绘电影按V2效果起步

```sh
python3 scripts/handpainted.py /path/to/new-handpainted-project
```

这是手绘示例的初始化入口，内部复用pipeline.init、声音doctor与后续素材/声音/验收工具，不要再对同一目录重复init。示例只复制自有绘图源码和工具，不复制旧素材锁、私人音色、模型、参考片或旧成功报告，不自动生成声音/渲染通过。

V2的笔触、主光、前中远景、衣料和接地方法，以及实际色值表见[手绘电影配方](references/handpainted-cinema.md)。已有主题、剧本和已选风格优先；按新角色/场景重画，不把所有内容做成同一支12秒信使视频。需要旁白且配置了个人音色时仍默认使用它。

新工程可先 `node tools/keyframes.cjs art-v001` 输出静帧；先审美术再测最高风险动作，例如 `node tools/motion_preview.cjs 120 120 motion-v001` 生成本例4–8秒的无声动作片段。仅复现示例时运行compose/锁时/混音/渲染，完整命令见[示例说明](assets/handpainted-cinema/README.md)。compose遇到锁、已有音频或素材记录会拒绝覆盖；正式声音替换沿原候选/diff/确认。技术通过、观感、参考画质、声音试听和用户采用分别记录。

## 明信片默认沿用兰州V2的配色与单片多视角

新明信片默认鲜明粉彩，同一个几何世界在20秒内从俯视过渡到左、右斜俯视，再回到俯视。建筑的高度、侧面、屋顶随投影变化；静态标签单独保持可读。默认连续展示，不新增开场选择；已指定固定视角、柔和色板或开合效果则沿用用户要求。

config.json中这些字段已经接入浏览器和Node绘图，复制完整map-postcard目录即可运行：

```json
{"viewProfile":"multi-angle","palette":"vivid","paletteOverrides":{},"reveal":false}
```

可显式使用top-down（固定俯视）、isometric（固定等距）、scroll-top-down（原1440世界下移），soft（柔和色板）或reveal:true（墨点开合）。旧工程自带代码不自动升级。颜色按功能和季节统一解析：纸白#FDFDF9、轮廓#4D6170、普通示意河#65BDE4，粉/紫/蓝/绿墙面与黄/紫/浅蓝屋顶；春配嫩绿/油菜黄/樱粉，秋配银杏黄/暖橙/雾蓝。完整色值见[地图美术与相机](references/map-art-direction.md)。

真实地点依据优先：兰州V2的黄河赭金色可用paletteOverrides.river:#DDBA4E保留，不能把所有地方统一套成蓝河或樱花。参数只选择画法，不会自动创建白塔/桥梁等地标；仍先研究地点并重写原创构图。音乐按地点匹配，模板八音盒仅示范/兜底。

[模板说明](assets/map-postcard/README.md)包含实际文件与运行方法。默认乡村/城市示意场景用于工程验证，不能仅改名称就冒称真实城市地图；旧兰州、广州和已有配乐不重跑。

## 地图先研究、再出构图

真实地点调用顺序：**地点与季节 → Google/百度按网络可用性查阅概览 → 独立核对当地地理与特色建筑 → 原创构图SVG和说明 → 按已授权方向画地标与制作视频**。已选地图风格不重复五选。

```sh
python3 scripts/map_access.py --place 你的地点 --preferred auto
python3 scripts/map_plan.py /path/to/research.json --out /path/to/new-composition
```

auto只检测入口可达性，实际地图和缩略图仍须查看确认；支持google/baidu偏好与失败回退，不自动开通API计费。两者均不可用可记录并使用授权本地参考。源坐标系必须记录，WGS84/GCJ-02/BD-09不能直接混用。

地图平台内容按当次条款使用；原创建筑/地理构图依据从可复用的独立资料核对，不默认抓平台截图去署名转绘。详见[地点研究与构图指南](references/map-research.md)。当前提供连通性检测和构图交接工具，未提供静态地图下载或坐标转换后端。

## 每个地点都做声音匹配

城市、县镇、村落都先核对当地音乐传统、生活声景、季节与片中场景，再选音乐和环境声。大城市找与本片片区有关的声音；小众地点依次扩大到文化区域、省域、相似地景，最后可用原创配乐。回退会写明原因和实际来源，外地水声不标作当地实录，也不靠“亚洲风”标签判断地域。

> 做一段不知名河谷小镇的秋季地图明信片。音乐和环境声按当地特点研究，免费优先；本地找不到就按文化区域与地景匹配，写清依据，不要冒充当地实录。

选材记录保存为sound-plan.json，空模板见[sound-plan.example.json](assets/map-postcard/sound-plan.example.json)，方法见[地点声音选材](references/location-sound.md)。首选和必要备选并入原方案，不新增音乐开场题；明确指定或委托代选就继续。公开展示不等于可用于配乐；具体录音的许可、费用、署名与原文件能否随开源项目分发分别核对。付费采购和已锁素材替换沿原授权/审阅规则执行。

当前由agent使用可用搜索工具检索、核对并选材，没有自动地域音乐识别器或全网下载器。map_music.py仍可合成固定20秒八音盒/8bit示范，不能称某种真实地方乐器演奏；正式地点不再固定套它。最终音频技术检查、实际试听和循环接缝分别记录；已有工程不会因规则更新自动替换配乐。
