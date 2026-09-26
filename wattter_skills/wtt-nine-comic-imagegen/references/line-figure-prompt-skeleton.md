# 线条人 提示词骨架

风格 D 的完整提示词模板。**默认输出中文版**（中英术语对照），用户可直接复制到 ChatGPT / GPT-4o / 即梦 / 可灵 / 通义万相等平台。每次按场景替换 `{变量}`。

含字生成时提供 [喜脉喜欢体字形参考](../assets/ximai-xihuan-handwriting-ref.png)，只参考下方大字字形，不复制内容、背景、布局或顶部印刷体。识别封面/头图/cover 后先判断内容类型与标题来源，再采用封面变体（文章默认包含完整标题）；明确无字则移除全部文字段。

---

实际制作含字图默认采用 [真实字体排字流程](font-typesetting.md)：以下文字块作为排字参数，生图时替换为无字与对应区域留白要求，再加载 `assets/fonts/FontQuSmile-Regular.ttf` 排字。只有直接生图近似路径才把文字块交给图像模型。

## 模板 A：中文版（默认 · 推荐）

```text
纽约客杂志风格的单格概念编辑插图。极简单线条人手绘风格。

【整体规范】
- 纯白背景，无纸纹、无渐变、无阴影、无填充（克莱因蓝点缀除外）
- 唯一点缀色：国际克莱因蓝（International Klein Blue，色号 #002FA7）
- 必须是 IKB 标准的克莱因蓝，不要藏青、不要皇家蓝、不要钴蓝、不要天蓝
- 至少 40% 留白
- 比例：16:9 横版（1920x1080）
- 不写实、不 3D、不照片、不贴纸、不表情包

【线条人 IP】
一个极小的戴眼镜的线条小人，占画面 1/12 到 1/10，绝不能更大。
- 头部：一个简单的圆，无嘴、无鼻、无眉
- 眼镜（身份标识，必须保留）：两个**方框镜片** + 一根短横线
  贴着两镜片上缘、把镜片连成一个整体——这根横线是镜框的上边梁，
  属于眼镜，不是眉毛，共三笔。镜片高度约为
  头部圆的 1/4，宽度约为高度 × 1.2（横向略宽）。
  两镜片间距约等于一个镜片宽度。眼镜永远是黑线条，不填充、
  不上克莱因蓝、不要圆框、不要椭圆、不要菱形、
  不要美式粗框、不要鼻梁、不要镜腿、不要墨镜、不要护目镜
- 头部圆内除眼镜三笔外没有任何其他线条；额头不要画眉毛，
  眼镜上方不要再加任何笔画
- 眼睛：可省略；如需暗示眼位，在两镜片圆心各画一个极小黑点
- 身体：躯干必须是一根清晰可见、连续不断的黑色弧线：上端直接连接头部圆的底部，经颈部向下延伸至腰胯；躯干长度至少等于一个头部直径，不可省略或缩成一点。
- 完整性：全身从头顶到双脚完整入镜：两条手臂连接躯干中上部，末端各有简笔手；两条腿从腰胯分叉，末端各有脚。头、躯干与四肢连续相连，双臂双腿分别可辨；人物与道具错开，躯干和四肢不得被遮挡、裁切或与背景线重合。
- 手臂：从弧线中上部伸出的两根单线，肘部微弯，末端是简笔手形
- 腿：从弧线下端伸出的两根单线，膝盖微弯，末端是小椭圆脚
- 线条：手绘微抖，粗细一致约 1-2px，黑色墨水
- 不要给人物加衣服、帽子、徽章、任何填充色（眼镜除外）

【场景】
- {SCENE — 描述人物在做什么、与什么物件互动}
- 线条人极小，被 {LARGE_OBJECT} 衬托得渺小（物件是人物的 3-10 倍大）
- 空间方向：人在 {左/右/中}，物件在 {左/右/中}
- 用方位词明确写出来，不要模糊

【克莱因蓝点缀】
克莱因蓝（#002FA7，实色填充，无渐变）落在 {ELEMENT — 回答「这张图在
讲什么」的那个元素}。只有这一个元素是蓝色，其他全部是黑线条或纯白。

【文字（非封面，可选）】
统一使用「喜脉喜欢体」手写风格，参照随附字形参考图：细笔自然书写，字形修长舒展，轻微倾斜、大小错落、基线自然起伏，笔画有轻重、提按与少量连笔；清晰可读，不机械对齐，不用宋体、黑体或标准印刷体。
只参考随附「喜脉喜欢体」样张下方大字的笔触，不复制样张文案与排版。
金句：「{金句，可省略}」，默认右下角浅灰小字，每行尽量 ≤6 字。
说明文字：{逐条列出原文与位置；不需要则写“无”}。
说明按需 0–3 处，每处 1 行，必要时最多 2 行，每行尽量 ≤6 字。
所有文字用浅灰 #888888 或 #999999，字高约画面高度 1/40–1/30
（1080p 下约 27–36px），文字区域合计 ≤10%，保持至少 40% 留白。
说明贴近对应物件或留白，不遮挡人物全身和蓝色主体，不抢图意。
仅生成明确列出的文字，不添加其他文案。

【硬约束】
- 只有一个克莱因蓝元素，其他一律黑白
- 无阴影、无渐变、无填充（克莱因蓝实色除外）
- 至少 40% 留白
- 一图一意
- 线条人只有头部为空心圆轮廓，躯干与四肢为单线，无填充、无衣服、无配饰（眼镜除外）
- 弧线躯干连续连接头底与腰胯，双臂双腿及手脚齐全，全身可见；躯干不是线框、不是双线
- 人物占画面不超过 1/10
- 16:9 横版（1920x1080）
- 不要 emoji、不要贴纸、不要图标库素材
```

---

## 模板 B：英文版（备用 · 国际平台）

适合 Midjourney / DALL·E / Stable Diffusion 等英文为主的平台。

```text
New Yorker magazine style editorial illustration, single-panel conceptual
metaphor. Minimalist thin black ink line drawing on pure white background,
generous negative space (at least 40% empty white), no shading, no gradients,
no textures, no paper grain. Only one accent color: International Klein Blue
(hex #002FA7, exactly IKB, not navy, not royal blue, not cobalt).

Recurring IP character (线条人):
A TINY minimalist line-drawn figure wearing simple square eyeglasses (occupying
1/12 to 1/10 of the frame, never larger). Head: a single simple circle.
Eyeglasses (identity marker, MUST be present): two small square lenses plus
one short horizontal bar running along the TOP EDGE of the lenses, joining
them into a single frame — this bar is part of the eyeglass frame, NOT an
eyebrow. Three simple strokes total. Lens
height about 1/4 of head circle; lens width about 1.2× lens height; distance
between the two lenses equals one lens width. Nothing else inside the head
circle besides these three strokes: no eyebrows, no extra strokes above the
glasses. Eyeglasses are BLACK lines,
no fill, no Klein blue, NOT round frames, NOT oval, NOT diamond,
NOT thick frames, NOT American hipster style, no nose
bridge, no temple arms, not sunglasses, not goggles. Eyes: optional; if shown, one tiny black dot at each lens
center. Body: one clearly visible, continuous black curved TORSO line,
attached directly to the bottom of the head circle and extending through the
neck to the hips, at least one head diameter long. The torso MUST be drawn.
Exactly two arms branch from the upper torso, each ending in a simple hand;
exactly two legs branch from the hips, each ending in a small oval foot.
All body parts are connected; both arms and both legs remain individually
readable. FULL BODY visible from head to both feet, inside the frame.
Keep props and background lines clear of the torso and limbs: no occlusion,
no cropping, no floating head, no missing torso, no detached or missing limbs.
Minimal strokes mean simplified anatomy, never omitted body parts. Lines: hand-drawn ink, slightly wobbly, uniform 1-2px.

Scene: {SCENE — what the figure does, what object it interacts with}
- The figure is TINY, dwarfed by {LARGE_OBJECT} (3-10× figure size).
- Spatial layout: figure on {left/right/center}, object on {left/right/center}.

Klein blue accent:
ONE element is solid Klein blue (#002FA7, no gradient): {ELEMENT — the one
that answers "what is this image about?"}. Everything else is black line on
white.

Text (non-cover, optional):
ALL lettering uses the “喜脉喜欢体” (Ximai Xihuan) handwriting style.
Match the large handwritten sample in the attached font reference only:
slender, relaxed strokes, slightly tilted elongated characters, varied sizes,
natural baseline movement, pen pressure and occasional connected strokes;
legible, never mechanically aligned. Do not copy its text, background,
layout or small printed heading. No standard print, Song or Hei typefaces.
Caption: 「{金句, omit if unused}」, bottom-right by default.
Explanatory labels: {exact text and position of each label, or none}.
Use 0–3 labels only when needed, one line each (two at most), preferably
no more than 6 Chinese characters per line. Light gray #888888 or #999999,
letter height 1/40–1/30 of frame height, total text area at most 10%.
Place labels near their objects or in whitespace, clear of the full figure
and blue subject. Keep at least 40% whitespace. Render only listed text.

Constraints: single accent color only; no shading, no gradients, no fills
except the one Klein blue element; at least 40% empty white; only the head has a hollow circular outline; torso and limbs are single lines;
no clothing, no accessories except glasses; continuous torso joining head
to hips, two connected arms and two connected legs with hands and feet,
full body visible and unobstructed; no box torso or double outline;
16:9 horizontal format (1920x1080).
```

---

## 完整示例：四阶精炼（中文版）

> 主题：R·D·R·R 四阶精炼工序——每一次 AI 协作都是把粗糙业务诉求精炼为成品的四步。

```text
纽约客杂志风格的单格概念编辑插图。极简单线条人手绘风格。

【整体规范】
- 纯白背景，无纸纹、无渐变、无阴影、无填充（克莱因蓝点缀除外）
- 唯一点缀色：国际克莱因蓝（International Klein Blue，色号 #002FA7）
- 至少 40% 留白
- 比例：16:9 横版（1920x1080）

【线条人 IP】
一个极小的戴眼镜的线条小人，占画面 1/12，绝不能更大。
- 头部：一个简单的圆，无五官
- 眼镜：两个方框镜片 + 一根短横线贴着镜片上缘连成一体（镜框上边梁，非眉毛），共三笔，黑线条
- 身体：躯干必须是一根清晰可见、连续不断的黑色弧线：上端直接连接头部圆的底部，经颈部向下延伸至腰胯；躯干长度至少等于一个头部直径，不可省略或缩成一点。
- 完整性：全身从头顶到双脚完整入镜：两条手臂连接躯干中上部，末端各有简笔手；两条腿从腰胯分叉，末端各有脚。头、躯干与四肢连续相连，双臂双腿分别可辨；人物与道具错开，躯干和四肢不得被遮挡、裁切或与背景线重合。
- 手臂和腿：单线，肘膝微弯
- 线条：手绘微抖，黑色墨水

【场景】
极小的线条小人站在画面最左侧，身旁有一条横贯全图的水平基线。
基线右上方有一堆凌乱的黑墨涂鸦——重叠的箭头、漂浮的对话框、杂乱的
波浪线——代表未经精炼的原始业务诉求。

沿着基线从左到右排列四个越来越精炼的形状，每一个比前一个更小、更干净：
- 第 1 段（R1·定框架）：一团缠绕的黑线团
- 第 2 段（D·填素材）：一个清晰的虚线轮廓
- 第 3 段（R2·提要求）：一个实心黑色剪影
- 第 4 段（R3·改满意）：一个独立的克莱因蓝实心形状（一颗光滑的水滴）

所有文字统一喜脉喜欢体（参照字形图，细笔修长、轻微倾斜、自然提按），字高约画面高度 1/40–1/30，文字区域合计 ≤10%。本例无需额外说明文字，四个形状直接呈现精炼过程。
线条小人被整条精炼链衬托得极其渺小，约占画面宽度 1/12。

【克莱因蓝点缀】
克莱因蓝（#002FA7，实色填充）落在最右端的第 4 段（R3·改满意）。
只有这一个元素是蓝色。

【金句】
右下角小字浅灰色，喜脉喜欢体手写风格（参照字形图，修长舒展、轻微倾斜、笔画有提按）：「协作即精炼」。

【硬约束】
- 只有一个克莱因蓝元素
- 无阴影、无渐变、无填充（克莱因蓝实色除外）
- 至少 40% 留白
- 线条人无填充、无衣服、无配饰（眼镜除外）；连续躯干、双臂双腿及手脚齐全，全身可见
- 16:9 横版（1920x1080）
```

---

## 系列一致性：角色锁定块

如果生成一组多张配图（如一套原则图、一篇文章的 3 张配图），先用以下模板锁定线条人形象：

```text
【角色锁定 — 戴眼镜的线条人（本组所有图复用此段，不要修改）】
戴眼镜的线条人：极小的线条小人（占画面 1/12 到 1/10）。
- 头部：一个简单的圆轮廓（无嘴、无鼻、无眉）
- 眼镜：两个方框镜片 + 一根短横线贴着镜片上缘连成一体（镜框上边梁，非眉毛），共三笔，黑线条
- 眼睛：可省略（如需暗示眼位，在两镜片圆心各画一个极小黑点）
- 身体：躯干必须是一根清晰可见、连续不断的黑色弧线：上端直接连接头部圆的底部，经颈部向下延伸至腰胯；躯干长度至少等于一个头部直径，不可省略或缩成一点。
- 完整性：全身从头顶到双脚完整入镜：两条手臂连接躯干中上部，末端各有简笔手；两条腿从腰胯分叉，末端各有脚。头、躯干与四肢连续相连，双臂双腿分别可辨；人物与道具错开，躯干和四肢不得被遮挡、裁切或与背景线重合。
- 手臂：两根单线，自然下垂
- 腿：两根单线，行走中步幅
- 无衣服、无配饰（眼镜除外）
- 线宽 1.5px，手绘微抖
- 弧线身体前倾方向=运动方向
```

生成 4 个候选让用户挑（A/B/C/D 不同弧度/姿态），确认后所有图复用同一段。

---

## 负面约束清单（直接复制粘贴到提示词末尾）

```text
【负面约束】
- 不要照片、不要 3D 渲染、不要写实人物
- 不要阴影、不要渐变、不要纹理、不要噪点
- 除克莱因蓝（#002FA7）点缀外不要任何彩色
- 不要 emoji、不要贴纸、不要图标库素材
- 不要彩色背景、不要深色背景
- 不要超过一处克莱因蓝
- 不要把线条人画大（极小=≤1/10 画面）
- 不要省略躯干、不要悬浮头、不要手脚直接长在头上、不要断开的或缺失的四肢
- 不要用道具遮住身体、不要半身构图、不要裁掉手脚；全身必须完整可见
- 不要给线条人加五官、衣服、装饰
- 不要眉毛、不要抬头纹，眼镜上方不要有任何额外线条（横线是镜框上边梁，贴着镜片上缘）
- 不要可爱卡通、不要儿童插画、不要 PPT 图示
- 封面仅生成指定主文案；非封面只生成指定金句和按需短说明；无字模式不生成文字
- 所有文字统一喜脉喜欢体手写风格，参照字形图并写明笔触；禁止混用其他字体
```

---

## 多页变体（如需系列 PPT 配图）

```text
本页是第 X 页 / 共 Y 页

【复用首页的角色锁定块】
角色锁定 — 线条人：极小的线条小人（占画面 1/12 到 1/10）。
- 头部：一个简单的圆轮廓（无五官）
- 眼镜：两个方框镜片 + 一根短横线贴着镜片上缘连成一体（镜框上边梁，非眉毛），共三笔，黑线条
- 眼睛：两个极小黑点
- 身体：躯干必须是一根清晰可见、连续不断的黑色弧线：上端直接连接头部圆的底部，经颈部向下延伸至腰胯；躯干长度至少等于一个头部直径，不可省略或缩成一点。
- 完整性：全身从头顶到双脚完整入镜：两条手臂连接躯干中上部，末端各有简笔手；两条腿从腰胯分叉，末端各有脚。头、躯干与四肢连续相连，双臂双腿分别可辨；人物与道具错开，躯干和四肢不得被遮挡、裁切或与背景线重合。
- 手臂和腿：单线，肘膝微弯
- 线宽 1.5px，手绘微抖
- 无嘴、无衣服、无配饰

【场景】
{每页单独场景 — 与首页相同角色，不同动作/物件}

【克莱因蓝位置】
{每页克莱因蓝落在哪个元素 — 系列中可让克莱因蓝在不同元素间轮换}

【金句】
右下角小字浅灰，喜脉喜欢体手写风格（参照字形图，修长舒展、轻微倾斜、笔画有提按）：「{金句}」

【页间衔接】
- 仅连续阅读确有需要时添加衔接短字，统一喜脉喜欢体、浅灰小字，计入非封面说明的 0–3 处限额
- 正文说明按需加入：{原文与位置}；字高 1/40–1/30，文字区域合计 ≤10%，不遮挡人物
```

---

## 封面模式变体（先识别内容类型与标题）

先执行 [风格 D 封面决策](style-d-line-figure.md#封面模式先判断内容再确定标题)：读取相关素材判断文章/课程/播客/视频/其他；文章默认使用完整文章标题，其他内容使用对应名称。已有标题直接提取，仅缺失或冲突时补问。用户指定文案或无字要求优先。

先读取 [平台构图模式](platform-cover-layouts.md)，写出 `内容类型 / 标题来源 / 标题原文 / 平台与展示位 / layout_id / title_box / scene_box / 分行方案 / 目标比例`，再替换下面的变量。不得将占位符直接交给生图模型，也不得把文章标题缩成金句。

在模板 A 中，将整个【文字（非封面，可选）】段替换为以下段落，移除非封面的说明数量、小字尺寸及六字建议。英文模板同理替换整个 Text (non-cover, optional) 块。无字封面则移除文字段并明确 no text。

```text
【封面文案】
内容类型：{文章/课程/播客/视频/报告/其他}。
本图为该内容的封面，必须显示以下完整标题：
「{标题原文；文章使用完整文章标题，用户指定替代文案时按指定文案}」
分行方案：{逐行列出标题，拼回后与原文完全一致}。
不得删除、改写、缩短、翻译或用金句替代标题，保留标点和词序。
标题不受六字上限限制；默认只生成该标题，不加其他文字。

统一使用「喜脉喜欢体」手写风格，参照随附字形图下方大字：
细笔自然书写，修长舒展、轻微倾斜、大小错落、自然提按与少量连笔，
清晰可读，不复制参考样张文字、背景或布局，不用标准印刷体。
复用策略：跨渠道或未指定平台默认 D-U1，一个抽象母版；仅明确单平台优化用 D-C 模式。
平台/展示位：{platform / placement}；构图：{D-U1（跨渠道默认）/D-C1/D-C2/D-C3/D-C4}。
标题容器：{title_box}；场景容器：{scene_box}；标题对齐：{alignment}。
主标题默认近黑 #1A1A1A，字高按平台模式实测容器适配；辅助字用 #666666。
完整标题按语义分行，不拆词组，不遮挡人物；按目标缩略图检查可读性。

【硬约束（封面模式追加）】
- 目标比例：{本次实际输出比例和尺寸}；人物全身与完整标题均在画面内
- D-U1 把完整标题、完整人物与唯一蓝色物件组成一个核心单元，外围可有低显著性的环境线条或次要装饰，裁掉后不损失信息；不加平台 UI 或标识
- 记录目标比例集合与裁剪交集；各比例保持同一核心单元，按实际窗口与缩略图验收
- 使用所选模式的标题/场景容器与实际裁剪窗口；公众号同图双裁剪单独验收
- 标题对齐与位置按构图模式，统一喜脉喜欢体，不描边、不加阴影
- 长标题调整行数、字号与构图，不删字，不改成短金句
```

英文版（替换模板 B 的非封面文字块）：

```text
Cover content type: {article/course/podcast/video/report/other}.
Render this EXACT complete title: 「{verbatim title}」.
For an article cover, use its full article title unless the user explicitly
provides replacement cover text. Line breaks: {exact lines}.
Keep every character, punctuation mark and word in order. Do not shorten,
translate, truncate or replace the title with a slogan. The six-character
caption guideline does NOT apply to cover titles. No extra text by default.
Use “喜脉喜欢体” (Ximai Xihuan) handwriting matching the attached large-letter
sample: slender elongated characters, slight tilt, natural baseline and pen
pressure, clear and legible. Do not copy the sample text, background or layout.
For cross-channel or unspecified-platform covers, default to D-U1: ONE
abstract cover master, with the complete title above a single metaphor scene.
Keep the complete figure and blue object with the title as one central unit;
use expendable peripheral content: sparse environmental lines, distant
outlines or secondary motifs, visually subordinate to the core. The perimeter
need not be blank; preserve the white base and restrained line-art style.
Keep every essential relationship inside the core. Cropping away peripheral
content must not alter the meaning or remove any required text or body part. No platform logos, UI cards or extra slogans.
Record target crops and their intersection; fit the whole unit inside it.
Ratio exports crop peripheral content or extend the background, preserving the unit
and its internal layout. Validate legibility as well as crop containment.
Platform / placement: {platform / placement}. Layout: {D-U1/D-C1/D-C2/D-C3/D-C4}.
Title box: {title_box}; scene box: {scene_box}; alignment: {alignment}.
Main title near-black #1A1A1A; secondary text #666666. No outline or shadow.
Measure the real font to fit the selected layout; preserve semantic line
breaks and every title character. Do not force all covers into centered gray text.
Target aspect ratio and size: {actual ratio and dimensions}.
Validate the actual crop and thumbnail legibility; preserve the complete figure.
WeChat wide and square crops need separate checks. X Article cropping follows
the current editor, not the profile-banner specification.
```

---

## 文章交付提醒

若本次为公众号或 Twitter/X 完整文章准备配图，生成配图之外还需按 [文末素材规则](article-footer.md) 直接复用个人介绍图，放在文章最后并去重。该图不使用本文件的角色、字体与封面约束，不送入生图模型重绘。

## 快速复用清单

写提示词前确认（每个独立模板与系列页都必须完整保留身体描述，不以“同上”代替）：

- [ ] 连续躯干连接头底与腰胯，长度至少一个头部直径；双臂双腿和手脚数量、连接位置写全了吗？
- [ ] 从头到脚完整入镜，躯干与四肢无遮挡、不与背景线重合了吗？

- [ ] 比喻的张力是什么？（多 vs 一？连 vs 断？深 vs 浅？）
- [ ] 克莱因蓝落在哪个元素上？（回答「这张图在讲什么」的那个）
- [ ] 线条人占画面多少？（目标 1/12 到 1/10）
- [ ] 物件比人大几倍？（目标 3-10×）
- [ ] 空间方向写清楚了吗？（人在哪、物件在哪）
- [ ] 金句位置写了吗？（默认右下角）
- [ ] 封面内容类型与标题来源已确定？文章完整标题已逐字填入，未被六字限制缩写？无字/指定文案等用户要求已优先处理？
- [ ] 长标题分行后拼回与原文一致，实际目标比例下标题和完整人物均可见？
- [ ] 用作封面吗？→ 改用「封面模式变体」并选择平台/展示位与构图；检查缩略图和实际裁剪，不套统一中央区
- [ ] 所有文字写明「喜脉喜欢体」并附字形参考与笔触描述了吗？封面尺寸是否替换了非封面小字尺寸？
- [ ] 留白够 40% 吗？
- [ ] 负面约束都写了吗？
- [ ] 中文版还是英文版？（默认中文，国内平台用）