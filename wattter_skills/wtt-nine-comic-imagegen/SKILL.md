---
name: wtt-nine-comic-imagegen
version: "2.2.8"
description: >
  多风格漫画与信息图提示词生成（中文优先）。Use when the user mentions "9号漫画" / "恶搞科普" / "竖版长图" / "竖版漫画长图" / "nine-comic" / "parody explainer" / "搞笑科普" / "那个搞笑的竖图" for Style A;
  "信息图" / "infographic" / "横版卡通" / "手绘信息图" / "16:9 infographic" / "卡通信息图" / "横版卡通图" for Style B;
  "四格漫画" / "Q版漫画" / "Chiikawa漫画" / "学习漫画" / "cute comic" / "多格可爱漫画" / "可爱漫画" / "分格故事" for Style C;
  "线条人" / "线人" / "克莱因蓝" / "极简插画" / "editorial插图" / "概念配图" / "line illustration" / "Klein blue" / "纽约客风格" / "New Yorker style" for Style D;
  "生活感人像" / "vibe" / "vibeshot" / "INS人像" / "韩国INS" / "抓拍人像" / "胶片人像" / "生活摄影" / "lifestyle portrait" / "candid portrait" / "Korean influencer" / "street portrait" for Style E.
  支持五种风格——9号漫画（中文恶搞科普竖版长图）、信息图（手绘卡通横版16:9信息图）、四格漫画（Q版可爱多格学习漫画）、线条人（极简单线条人+克莱因蓝点缀横版概念插图）、生活感人像（vibe 摄影风格·韩国INS网红主体·10 张成组）。
  默认中文输出图片生成提示词，可直接复制到 ChatGPT / GPT-4o / 即梦 / Midjourney 等平台使用。
  Works with any image generation tool that accepts text prompts.
---

# 多风格漫画与信息图生成（含生活感人像）

本技能支持五种视觉风格，将内容转化为漫画/信息图/人像写真形式的**图片生成提示词**。**默认输出中文提示词**（中英术语对照），用户可复制到 ChatGPT / GPT-4o / 即梦 / Midjourney 等支持图片生成的平台使用。

## 核心原则

- **风格选择优先**：触发本技能后，先确认用户想要哪种风格，再进入对应工作流。
- **输出即提示词**：无论哪种风格，最终都输出完整的图片生成提示词。提示词可直接复制到 ChatGPT / GPT-4o 等平台使用。
- **可变与锚点分离**：每种风格都有"识别锚点"（不可变的风格标识）和"可变变量"（每次生成可调整的元素），避免版式固化。
- **共享机制分层**：跨风格的通用规则（上下文控制 / 负面提示 / 比例锚定 / 文字渲染）集中在 [shared-mechanisms.md](references/shared-mechanisms.md)，每个风格章节通过机制编号引用，避免重复。

## 固定文末素材

为公众号或 Twitter/X 的完整文章准备配图时，默认将 [个人介绍图](assets/article-footer-profile.png) 作为文章最后一张配图，仅保留一次。直接复用原图，不重新生成或改字体；按 [文末素材交付规则](references/article-footer.md) 复制到文章 assets 并使用相对路径。单独封面、普通短帖与其他平台不自动追加。

## 风格路由表

| 用户意图 | 典型说法 | 路由目标 | 必需信息 |
|:---|:---|:---|:---|
| 恶搞科普长图 | "9号漫画"、"恶搞科普"、"竖版漫画长图"、"那个搞笑的竖图" | 风格 A: 9号漫画 | 主题 |
| 手绘信息图 | "信息图"、"infographic"、"横版卡通图"、"手绘信息图"、"16:9" | 风格 B: 信息图 | 主题 |
| 多格可爱漫画 | "四格漫画"、"多格漫画"、"可爱漫画"、"Q版漫画"、"分格故事"、"Chiikawa"、"学习漫画" | 风格 C: 四格漫画 | 主题；可选：角色/IP 偏好 |
| 极简概念插图 | "线条人"、"线人"、"克莱因蓝"、"极简插画"、"editorial插图"、"概念配图"、"line illustration"、"Klein blue"、"纽约客风格"、"New Yorker style" | 风格 D: 线条人 | 主题；可选：金句/配文 |
| 生活感抓拍人像 | "生活感人像"、"vibe"、"vibeshot"、"INS人像"、"韩国INS"、"抓拍人像"、"胶片人像"、"生活摄影"、"lifestyle portrait"、"candid portrait" | 风格 E: 生活感人像 | 主题/数量（默认 10 张）；可选：指定场景/服装/焦段/机位 |

### 未指定风格时的补问规则

- 若用户只说了主题没指定风格，问一句："你想用哪种风格？**A.** 9号漫画（恶搞竖版科普长图）**B.** 手绘信息图（横版卡通16:9）**C.** 四格漫画（可爱分格故事）**D.** 线条人（极简横版概念插图，克莱因蓝点缀）**E.** 生活感人像（vibe 抓拍人像，10 张成组）"
- 若用户描述的内容天然适合某种风格（如明确说了"横版"、"竖版"、"多格"、"抓拍"、"胶片"），可主动推荐但仍需确认。
- 若用户提到了特定 IP/角色（如 Chiikawa、Line Friends），推荐风格 C 并询问是否沿用该 IP 风格。

---

## 共享工作流速览（完整内容见 references）

跨 5 种风格通用的实战机制，集中在 [references/shared-mechanisms.md](references/shared-mechanisms.md)。每种风格的"实战经验"以"机制编号 + 风格关键句"两层结构引用，避免跨章重复。

**5 大机制群**：

1. **通用生成哲学**——抽奖不是质检，并行生成多个候选让用户挑，不做预筛选
2. **主体一致性控制**（适用于 A/C/D/E 四个有 IP 角色的风格）——锚点描述写开头 + 必须上传参考图 + 多页复用 prompt 块 + 首轮 2-4 候选
3. **比例与版式锚定**（所有风格通用）——具体像素 + 方向双锚定：A 720x2800 / B 1920x1080 / C 1080x1440 / D 1920x1080 / E 1080x1440 或 1080x1350
4. **文字/字体渲染通用规则**（涉及画面文字的 B/D）——物理书写动作词 + ≤6 字 + 后期叠加退路
5. **通用负面提示框架 N1-N7**——机制编号速查表，覆盖"写两遍 / 单写禁止 / 枚举禁止变体 / 程度副词 / 物理书写 / ≤6 字 / 后期叠加" 7 类通用规律

通用反馈规则（标题不对 / 太像品牌 / 文字糊 / 单页太长 等）也见 shared-mechanisms.md。

---

## 风格 A: 9号漫画（恶搞科普竖版长图）

中文恶搞科普竖版长图——手绘黑白人物、荒诞表情、一本正经用最俗的日常琐事解释最高深的概念。**默认使用御用主角参考图** `{SKILL_DIR}/assets/nine-comic-character-ref.png`。

**风格铁律**：
- 手机竖版长图，约 **720x2800**，米白纸张背景
- 手绘黑白线稿 + 荒诞表情 + 短句气泡 + 红色标注箭头 + **无分镜边框**
- 比喻铁律：用最俗的东西解释最玄的（菜市场、厕所、泡面、相亲……）

**典型工作流（详细见 [style-a-nine-comic.md](references/style-a-nine-comic.md)）**：

1. 拆参考图（识别锚点 + 主题形态）
2. 把主题变成滑稽比喻（高深概念 ≈ 菜市场级别日常）
3. 组织长图结构（选版式骨架：标准/对照/路线/解剖/黑板/剧场）
4. 加入主题物件和物理草图
5. 按 [nine-comic-prompt-skeleton.md](references/nine-comic-prompt-skeleton.md) 写提示词

**关键引用**：
- 角色判断标准（4 个 pass/fail 测试）：见风格 A 详细参考
- 实战经验 5 条：[N4] 表情夸张 / [共享文字] 手写批注 / [N1] 边框写两遍 / [共享主体] 上传参考图 / [共享比例] 写具体像素
- 比喻实战目录（成功/失败/渲染问题）：[nine-comic-metaphor-catalog.md](references/nine-comic-metaphor-catalog.md)
- 特有反馈处理：见 [feedback-by-style.md](references/feedback-by-style.md) §风格 A

---

## 风格 B: 信息图（手绘卡通横版16:9）

手绘卡通横版信息图——突出关键词与核心概念，简洁易懂，一眼抓住重点。

**风格铁律（不可违反）**：
1. 所有元素必须手绘/插画风格（禁止照片、3D、写实）
2. 严格 **1920x1080** 横版（16:9），不可偏移
3. 卡通元素不可省略（每个核心论点必须有手绘图标）
4. 大面积留白，信息精炼
5. 语言跟随输入
6. 公众人物画卡通替代（特征夸张但不丑化）

**典型工作流（详细见 [style-b-infographic.md](references/style-b-infographic.md)）**：

1. 解析主题（≤5-7 个核心信息点 + 判断关系）
2. 信息分层（标题/核心论点/细节/装饰 四层）
3. 选择版式骨架（流程/对比/层级/时间线/数据）
4. 分配卡通元素
5. 按 [infographic-prompt-skeleton.md](references/infographic-prompt-skeleton.md) 写提示词

**关键引用**：
- 实战经验 4 条：[N2] 手绘元素单写约束 / 明确信息点数量 / [共享比例] 写具体像素 / [N5] 关键词手写体加粗
- 配色方案：浅米色背景 + 暖色主调 + 亮黄/亮粉高亮 + 深棕深灰文字
- 特有反馈处理：见 [feedback-by-style.md](references/feedback-by-style.md) §风格 B

---

## 风格 C: 四格漫画（Q版可爱多格学习漫画）

Q版可爱多格学习漫画——用可爱角色和简洁视觉语言解释知识，让学习轻松有趣。

**风格铁律（不可违反）**：
1. Q版比例严格 **头身比 2:1-3:1**（大眼睛、小身体、圆润造型）
2. 严格 **3:4 竖版**（如 1080x1440）
3. 每页 **2-4 格**，不可超过
4. 温暖治愈基调（冲突温和、结局暖心，禁止暗黑/恐怖/暴力）
5. **三角色分工不可缺**（好奇者 + 活泼者 + 引导者），可换皮（IP替换），不可换骨
6. 暖色配色 + 深色文字确保可读

**典型工作流（详细见 [style-c-four-panel.md](references/style-c-four-panel.md)）**：

1. 解析主题与角色分配（10-20 个学习点）
2. 生成视觉风格指令块（**只输出一次**，作为独立代码块）
3. 规划页面（封面 + 内容页 + 结尾页 + 每页 1-2 个学习点）
4. **输出页面大纲表让用户确认**（必备步骤，避免多轮返工）
5. 每页按 4 段式结构（学习目标/故事情节/分格设计/视觉重点）写提示词
6. 按 [four-panel-prompt-skeleton.md](references/four-panel-prompt-skeleton.md) 模板填充
7. 分块输出：每生成 3-5 页暂停确认方向

**关键引用**：
- 默认三角色原型（Protagonist / Companion / Guide）+ IP 映射预设：[four-panel-character-archetypes.md](references/four-panel-character-archetypes.md)（Chiikawa、Line Friends、Sanrio、WTT 原创角色"小九"）
- 实战经验 4 条：Q版头身比具体数字 / [N2] 圆角格子边框 / 提示词必须包含页码 / [N4] 封面与内容页区分
- 配色方案：奶油色暖底 + 柔蓝薄荷浅珊瑚强调 + 深棕文字 + 圆角气泡
- 特有反馈处理：见 [feedback-by-style.md](references/feedback-by-style.md) §风格 C

---

## 风格 D: 线条人（极简横版概念插图）

极简单线条人横版概念插图——细黑墨线 + 纯白留白 + **唯一克莱因蓝 `#002FA7`** 点缀色。给文章、原则、封面生成有空白感的概念配图。

**风格铁律（不可变识别锚点）**：
- 细黑墨线、手绘微抖（New Yorker 单格漫画质感）
- 纯白背景，无纸纹/渐变/阴影
- **唯一点缀色：克莱因蓝 `#002FA7`**（International Klein Blue, IKB）
- ≥40% 留白（空白是构图的一部分）
- 人物**永远极小**（占画面 **1/12 到 1/10**）
- 正文概念图默认 **16:9 横版（1920x1080）**；平台封面按展示位比例与构图模式输出

**角色定义 — 线条人**（IP 身份标识）：
- 头部：一个简单圆，无嘴鼻眉
- **眼镜（必须保留）**：两个**方框镜片** + 一根短横线贴着镜片上缘连成一体（镜框上边梁，非眉毛），共三笔；镜片是唯一装饰，眼镜上方不得另画线条
- 身体：**完整且不可省略的单弧躯干**。躯干必须是一根清晰可见、连续不断的黑色弧线：上端直接连接头部圆的底部，经颈部向下延伸至腰胯；躯干长度至少等于一个头部直径，不可省略或缩成一点。
- 手腿：单线，肘膝微弯。全身从头顶到双脚完整入镜：两条手臂连接躯干中上部，末端各有简笔手；两条腿从腰胯分叉，末端各有脚。头、躯干与四肢连续相连，双臂双腿分别可辨；人物与道具错开，躯干和四肢不得被遮挡、裁切或与背景线重合。
- 每张提示词均保留上述身体完整性描述，不能压缩为“单根弧线身体”；极简只简化笔画，不省略身体部位。

**真实字体排字**：已配备 [喜脉喜欢体 TTF](assets/fonts/FontQuSmile-Regular.ttf)。实际制作含字图时，默认先生成无字插图，再加载此字体排标题/说明，详见 [排字流程](references/font-typesetting.md)。TTF 不会因写进提示词而自动被生图模型加载；直接生图的文字仅属近似。

**文字规范**：统一使用「喜脉喜欢体」手写风格，参照随附字形参考图：细笔自然书写，字形修长舒展，轻微倾斜、大小错落、基线自然起伏，笔画有轻重、提按与少量连笔；清晰可读，不机械对齐，不用宋体、黑体或标准印刷体。
- 字形参考：[喜脉喜欢体](assets/ximai-xihuan-handwriting-ref.png)。生成含字图片时随提示词提供，仅参考下方大字的字形，不复制样张文案、背景或排版。
- 识别到“封面/头图/cover”用途，先从当前对话与素材判断内容类型（文章/课程/播客/视频/其他），再确定封面文字。**文章封面默认必须包含完整文章标题**，直接提取已有标题，不用金句替代；只在类型或标题缺失、冲突时补问。用户明确无字或指定封面文案时遵从用户。
- 同一内容跨渠道发布或未指定平台时，默认使用 [D-U1 跨渠道抽象母版](references/platform-cover-layouts.md)：完整标题 + 单一抽象场景组成中央图文单元，外围为可裁剪的次要内容区；需要比例稿时整体适配，不默认逐平台重做。明确单平台优化才选 D-C1–D-C4。保留真实喜脉喜欢体与完整标题，并检查裁剪交集和缩略图可读性。
- 非封面可按需增加 1–3 处短说明；统一字体、灰色小字，贴近对应物件且不遮挡人物，详见风格 D 文字系统。

**典型工作流（详细见 [style-d-line-figure.md](references/style-d-line-figure.md)）**：

1. 拆解主题 → 找张力（多 vs 一？空 vs 暖？）
2. 设计 2-3 个候选比喻（动作场景优先于抽象符号 + 一图一意）
3. 写提示词：默认中文为主中英术语对照，按 [line-figure-prompt-skeleton.md](references/line-figure-prompt-skeleton.md) 模板填充
4. 多张系列：先锁角色（4 个候选挑 1）→ 抽角色 prompt 块 → 复用只换场景

**关键引用**：
- 角色判断标准（6 个 pass/fail 测试）+ 比喻设计原则：见风格 D 详细参考
- 实战经验 14 条（最丰富）：尺度差两次 / 克莱因蓝色号 / 无阴影渐变填充 / 唯一点缀色 / 弧线身体 / 空间方向 / 金句位置 / 引号包裹中文 / [N3] 眼镜三笔 + 禁止变体含眉毛 / 眉线字面污染（横线叫镜框上边梁） / [N5-N7] 手写字 + ≤6 字 + 后期叠加
- 系列一致性：4 候选 → 角色锁定块复用
- 配色与金句系统 + 封面模式（文字居中放大、中央安全区适配多比例裁剪）：见风格 D 详细参考
- 特有反馈处理：见 [feedback-by-style.md](references/feedback-by-style.md) §风格 D（含"克莱因蓝偏色/线条人太大/眼镜换皮/金句抢戏"等 11 条）

---

## 风格 E: 生活感人像（vibe 摄影 · 10 张成组）

vibe 摄影——真实生活摄影感、偶然抓拍感、非常规机位、强烈空间层次。**默认每次输出 10 张成组提示词**（用户可指定 1-30 张）。

**主体锚点**（不可变）：一位极具镜头感的韩国 INS 网红，皮肤白皙，身材傲人，五官精致但不网红脸，自然有生活感（22-28 岁）。
**禁止项**：画成动漫/插画/3D 渲染；过度美颜的"完美脸"；**任何具体公众人物的相似脸**（肖像权）。

**12 个变量池**（每张图各抽 1-2 个值组合）：

| # | 变量 | # | 变量 |
|:---|:---|:---|:---|
| 1 | 表情 | 7 | 机位 |
| 2 | 服装 | 8 | 构图 |
| 3 | 场景 | 9 | 前景 |
| 4 | 瞬间状态 | 10 | 光线 |
| 5 | 景别 | 11 | 色彩 |
| 6 | 镜头焦段 | 12 | 摄影状态 |

完整取值清单见 [vibe-variable-catalog.md](references/vibe-variable-catalog.md)（每个池 ≥6-30 个值）。

**批次差异强制规则**（避免 10 张同质化）：
- 景别 ≥3 种 / 焦段 ≥4 种 / 非常规机位 ≥3 张
- 室内/室外各 ≥3 张 / 光线 ≥4 种 / 服装 ≥6 种
- 相邻两张共用变量 ≤6 个

**典型工作流（详细见 [style-e-vibe.md](references/style-e-vibe.md)）**：

1. 抽取 12 个变量各 1-2 个值（用户指定的字段锁定最高优先级）
2. 用"12 池 × 10 张差异矩阵"自检多样性（每列 unique ≥4）
3. 按 8 步公式自然融合为 80-150 字一段中文摄影提示词（**不要结构化罗列**）
4. 按 [vibe-prompt-skeleton.md](references/vibe-prompt-skeleton.md) 模板填充（含中文+英文两版）

**8 步自然融合公式**：机位+焦段 → 场景 → 主体+服装 → 动作 → 表情 → 光线 → 前景+景别+构图 → 摄影状态+色彩

**关键引用**：
- 实战经验 10 条：[N4] 真实生活感 + 偶然抓拍感 / 焦段具体数字 / 非常规机位 / 光线多样性 / 前景必写 / 摄影质感品牌名 / 服装风格标签 / 场景"地点+氛围" / [N1] 批次差异自检
- 4 种用户指定锁定模式（完全/字段/风格/计数）：见风格 E 详细参考
- 适用场景：小红书/INS 头像、生活类公众号配图、摄影作品集、模特卡片、约拍 prompt
- 特有反馈处理：见 [feedback-by-style.md](references/feedback-by-style.md) §风格 E（含"太精修/机位太平/光线太单调/前景缺失/画成公众人物/服装同质化/表情都看镜头/棚拍感"等 8 条）

---

## 多页处理

当内容过长无法在单张图片中清晰呈现时，应拆分为多页。**D/E 不适用**（D 是单格概念图，E 默认一次出 10 张已成组）。完整拆分阈值表 + 3 种拆分策略 + 多页提示词要点见 [multi-page-handling.md](references/multi-page-handling.md)。

---

## 资源清单

### references（共 13 个文件）

**共享机制（1 个）**
- [shared-mechanisms.md](references/shared-mechanisms.md) — 通用生成哲学 + 主体一致性 + 比例锚定 + 文字渲染 + N1-N7 框架 + 通用迭代规则

**风格专属完整参考（5 个）**
- [style-a-nine-comic.md](references/style-a-nine-comic.md)
- [style-b-infographic.md](references/style-b-infographic.md)
- [style-c-four-panel.md](references/style-c-four-panel.md)
- [style-d-line-figure.md](references/style-d-line-figure.md)
- [style-e-vibe.md](references/style-e-vibe.md)

**提示词骨架 + 视觉库（6 个）**
- [nine-comic-prompt-skeleton.md](references/nine-comic-prompt-skeleton.md)
- [nine-comic-metaphor-catalog.md](references/nine-comic-metaphor-catalog.md)（成功/失败比喻实战目录）
- [infographic-prompt-skeleton.md](references/infographic-prompt-skeleton.md)
- [four-panel-prompt-skeleton.md](references/four-panel-prompt-skeleton.md)
- [four-panel-character-archetypes.md](references/four-panel-character-archetypes.md)（三角色原型 + Chiikawa/Line Friends/Sanrio/WTT 小九 IP 映射）
- [line-figure-prompt-skeleton.md](references/line-figure-prompt-skeleton.md)
- [vibe-prompt-skeleton.md](references/vibe-prompt-skeleton.md)
- [vibe-variable-catalog.md](references/vibe-variable-catalog.md)（12 池完整取值 + 组合禁忌 + 实战经验）

**流程与反馈（2 个）**
- [multi-page-handling.md](references/multi-page-handling.md)
- [feedback-by-style.md](references/feedback-by-style.md)

### assets

- [ximai-xihuan-handwriting-ref.png](assets/ximai-xihuan-handwriting-ref.png) — 风格 D 喜脉喜欢体字形参考（用户图一，非字体文件）
- [nine-comic-character-ref.png](assets/nine-comic-character-ref.png) — 风格 A 御用主角参考图（必须上传以锁定人物风格）

---

## 加载指引

- 看到触发词 → 命中 frontmatter → 加载本文件（SKILL.md，约 200 行）
- 风格路由 → 进入对应风格的 **skeleton** 文件（取提示词模板填充）
- 实战经验/反馈处理 → 进入对应风格的 **style-X** 文件（看实战经验和反馈表）
- 跨风格通用规则 → [shared-mechanisms.md](references/shared-mechanisms.md)
