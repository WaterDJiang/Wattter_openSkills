# HTML background style: cream-confident

奶油撞色 —— 复古撞色、neobrutalism、宣言式。移植自 open-design `html-ppt-zhangzara-creative-mode`(Creative Mode),按色系主题改名。

## 1. 视觉特征

- 奶油底 (#EFE9D9) + 4px 厚黑边 + 偏移阴影(14-16px 黑色 box-shadow,**neobrutalism 签名**)
- 5 撞色 DNA:**绿 #1F8A4C / 粉 #F06CA8 / 橙 #E85A1F / 黄 #F5C518 / 奶油2 #E4DCC4**;墨 #0F0F0F
- Archivo Black 大字 uppercase(超粗极黑)+ JetBrains Mono 等宽标签 + Space Grotesk 正文
- 装饰 device:cover 是绿色 panel 套粉色开关 + 黄色圆 + 橙色偏移阴影;chapter 是绿色 ix 方块 + 黄色内圆;ending 是绿底 + 旋转粉色圆形 stamp
- 适合潮牌/品牌发布/创意营销/产品发布/活动宣发/音乐节/教育(醒目风)

## 2. text-slot 契约

见 [slots.json](slots.json)(本风格独立坐标,与起步 3 风格不同;cover 用 4 槽 title/subtitle/author/date):

| 模板 | slot | 坐标 (x1,y1 x2,y2) |
|---|---|---|
| cover | title | 50,200 770,500 |
| cover | subtitle | 50,520 770,580 |
| cover | author | 50,640 380,680 |
| cover | date | 410,640 770,680 |
| ending | thanks | 50,180 700,460 |
| ending | contact | 50,500 800,620 |
| chapter | chapter_num | 50,260 700,460 |
| chapter | chapter_name | 50,500 800,560 |
| theme | (无) | Executor 自由设计内容层 |

## 3. 配色与变量

**风格固定色**(DNA,写死 `:root`,不被色板覆盖):
- 底: `--cream` #EFE9D9 / `--cream-2` #E4DCC4
- 5 撞色: `--green` #1F8A4C / `--pink` #F06CA8 / `--orange` #E85A1F / `--yellow` #F5C518
- 墨: `--ink` #0F0F0F(黑边、阴影、墨字)

**主题角色**(`{{var}}` 覆盖;不传 = 原生撞色):
- `--primary` = #1F8A4C(绿,主色)
- `--accent` = #F06CA8(粉,装饰)
- `--bg` = #EFE9D9(奶油底)
- `--surface` = #E4DCC4(奶油2,备用)
- `--text` = #0F0F0F(墨)

不传 variables 时渲染原汁原味 5 色撞色 + 黑边阴影;传 theme_palette 的 primary/accent/bg/text 时主题色覆盖主角色,4 撞色装饰色 + 4px 黑边/偏移阴影保留(它们是 neobrutalism 风格 DNA,不能变)。

## 4. 兼容色板

warm-earth ✓(气质合:奶油+多色同源) / dark-cinematic ✓(墨+多色,适合 bold) / navy-trust ✗(海军蓝破坏绿/橙/黄撞色节奏) / tech-cyan ✗(冷色与撞色气质冲突)

## 5. 模板文件

[cover.html](cover.html) · [ending.html](ending.html) · [chapter.html](chapter.html) · [theme.html](theme.html)
