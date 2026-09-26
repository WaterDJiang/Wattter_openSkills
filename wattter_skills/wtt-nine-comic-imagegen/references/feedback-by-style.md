# 风格反馈处理（按风格分类）

每个风格特有的反馈处理表。通用反馈处理（标题不对、太像品牌、文字糊等）见 [shared-mechanisms.md](shared-mechanisms.md) 的"通用迭代规则"。

每次迭代后，输出修改后的完整提示词，用户可重新用于图片生成。

---

## 风格 A: 9号漫画

| 反馈 | 处理方式 |
|:---|:---|
| "边框太多" | 写「不要矩形边框、不要分镜框、不要卡片边框」 |
| "太挤" | 写「每段之间大面积留白，段间距明显拉宽，整体不要紧凑」 |
| "不够滑稽" | 增加荒诞比喻、夸张表情、反差吐槽 |
| "太模板" | 改版式骨架，改阅读路径、标题区、底部总结和主题物件 |
| "不够好笑/太正经" | 把比喻再降一级——从"公司管理"降到"菜市场大妈管摊位" |
| "比喻太高深" | 换成不识字的老太太也能秒懂的日常场景 |
| "人物风格不统一" | 在提示词开头强化人物特征描述，建议用户上传参考图 |

---

## 风格 B: 信息图

| 反馈 | 处理方式 |
|:---|:---|
| "太密集/太满" | 加大留白，减少每层信息量，关键词用高亮而非堆砌 |
| "不够卡通/太写实" | 强调「所有元素必须手绘/插画风格，禁止照片和3D渲染」 |
| "信息层级不清" | 重新做信息分层，加大标题与正文的字号对比 |
| "配色不协调" | 按配色方案重新指定主色/强调色/文字色 |

---

## 风格 C: 四格漫画

| 反馈 | 处理方式 |
|:---|:---|
| "不够可爱" | 强调Q版比例（头身比2:1-3:1）、圆润造型、大眼睛 |
| "角色出戏" | 检查角色行为是否符合原型性格，重新对齐功能分工 |
| "太说教" | 把知识讲解改成角色对话和互动场景，减少旁白 |
| "格子太密" | 减少每页格数（从4格减到2-3格），增加格间距 |
| "整体太冷" | 调整配色方案，增加暖色比例，使用推荐的暖色底色 |

---

## 风格 D: 线条人

| 反馈 | 处理方式 |
|:---|:---|
| "克莱因蓝偏色" | 强化色号 `#002FA7`，加写「exactly International Klein Blue IKB, not navy, not royal blue, not cobalt」 |
| "线条人太大" | 强化「占画面 1/12 到 1/10」+「TINY human figure dwarfed by ...」+「if the figure fills more than a tenth of the frame it is too big」 |
| "身体缺失/只有头和脚/四肢不全" | 重写角色块：连续弧线躯干从头底连接至腰胯，长度至少一个头部直径；双臂接躯干中上部，双腿从腰胯分叉，手脚齐全；调整道具与姿态，确保全身无遮挡、不裁切。 |
| "身体是线框不是弧线" | 强化「continuous curved torso connecting the head to the hips, no box torso, no double outline」 |
| "加了五官/衣服" | 强化「head is just a circle, no mouth, no nose, no eyebrows, no clothing」 |
| "眼镜缺失/换皮了" | 强化「a tiny figure wearing simple square eyeglasses (a short bar along the tops of the lenses joining them + two small squares), the ONLY face detail」+「draw the square eyeglasses clearly visible」 |
| "额头上多一笔（眉毛/眼镜上方多线条）" | 横线被写成了「眉线」——改为「镜框上边梁：一根短横线贴着两镜片上缘连成一体」+「the bar is part of the frame, NOT an eyebrow; no strokes above the glasses」 |
| "眼镜画成墨镜/加粗/护目镜" | 强化「no thick frame, no sunglasses, no goggles, no nose bridge, no temple arms」+「three simple strokes only」 |
| "眼镜被克莱因蓝染色" | 强化「eyeglasses are BLACK lines, NOT Klein blue」+「Klein blue is reserved for scene accent only」 |
| "有阴影/渐变" | 强化「no shading, no gradients, no fills on any element except the single Klein blue accent」 |
| "多处克莱因蓝" | 强化「one Klein blue accent only, the rest pure white」+ 描述哪个元素是克莱因蓝 |
| "字体不统一/不像图一" | 所有文字统一喜脉喜欢体，附字形参考并补充修长舒展、轻微倾斜、笔画提按等描述；不只写“手写体”。 |
| "非封面需要说明文字" | 按需添加 0–3 处短说明，统一字体与浅灰小字，贴近物件、不遮挡人物；删除旧版“除金句外无字”约束。 |
| "金句抢戏" | 非封面维持浅灰小字；封面标题允许作为阅读入口，减少额外说明，按平台模式保留完整标题与单一蓝色视觉锚点。 |
| "封面文字被裁掉" | 按实际目标比例检查完整标题与人物；使用中央安全区起稿，必要时重排或制作对应比例版本，不删标题。 |
| "文章封面没标题/标题变金句" | 重新读取文章主标题，逐字填入封面文案；取消六字与单行硬限制，长标题语义换行。 |
| "封面文字太小/还在右下角" | 按 platform-cover-layouts.md 重新选标题容器与字号，主标题近黑并检查缩略图；不把非封面小字规则带入封面。 |
| "比喻需要解释" | 换比喻，回到 D2 重新生成 2-3 个候选 |

---

## 风格 E: 生活感人像

| 反馈 | 处理方式 |
|:---|:---|
| "太精修/太商业" | 加强 N4「真实生活摄影感」+ 加写「保留皮肤纹理」+ 「不要磨皮」|
| "机位太平" | 写「至少 3 张非常规机位（极低 / 高俯 / 肩上 / 倾斜）」|
| "光线太单调" | 写「10 张至少 4 种光线，禁止全是黄金时刻」|
| "前景缺失" | 写「前景必须有散焦的{树叶/玻璃反光/雨滴}，遮挡画面 1/3」|
| "画成公众人物" | 加写「不画成任何具体公众人物的相似脸（避免肖像权）」|
| "服装同质化" | 写「10 张至少 6 种不同服装风格」|
| "表情都看镜头" | 写「至少 5 张主体不直视镜头（看别处/闭眼/低头/抬伞）」|
| "棚拍感" | 写「禁止棚拍白底、禁止完美对称、禁止标准 pose」|
