# HTML background style: forest-editorial

森林编辑部 —— 安静、文学气质。移植自 open-design `fs-editorial-forest`（林间编辑部），按色系主题改名。

## 1. 视觉特征

- 暖奶油纸面底（bg #efe7d4），森林绿 primary 竖色带贯穿全高（14px，全 deck 一致的结构锚）
- 尘粉 accent 装饰：顶部短色带 / 圆环描边（cover）/ 圆点（chapter·theme）/ 发丝线（顶/底/中段）
- 森林绿深色块作明暗混排节奏：cover 右下角块、chapter 右侧整高色块、ending 右上圆块
- Source Serif 4 衬线大字区 + JetBrains Mono 标签节奏（背景层不烘焙文字，仅留几何装饰与坐标）
- 大量留白，编辑型克制；适合文学/季评/品牌叙事/慢内容

## 2. text-slot 契约

见 [slots.json](slots.json)（本风格独立坐标，与起步 3 风格不同）：

| 模板 | slot | 坐标 (x1,y1 x2,y2) |
|---|---|---|
| cover | title | 96,250 1184,360 |
| cover | subtitle | 96,385 1184,440 |
| cover | author | 96,610 640,650 |
| cover | date | 660,610 1184,650 |
| ending | thanks | 96,260 1184,400 |
| ending | contact | 96,500 1184,620 |
| chapter | chapter_num | 96,200 880,400 |
| chapter | chapter_name | 96,440 880,520 |
| theme | （无） | Executor 自由设计内容层 |

## 3. 配色与变量

**风格固定色**（DNA，写死 `:root`，不被色板覆盖）：`--green-deep` #243a21 / `--green-lite` #3a5a36 / `--cream-2` #e6dcc4

**主题角色**（`{{var}}` 覆盖；不传 = 原生林间色）：
- `--primary` = #2e4a2a（森林绿，竖色带 / 色块）
- `--accent` = #e89cb1（尘粉，装饰线 / 圆环 / 圆点）
- `--bg` = #efe7d4（暖奶油，底）
- `--surface` = #e6dcc4（奶油2）
- `--text` = #1a1a17（墨，文字层用）

不传 variables 时渲染原汁原味林间色；传 theme_palette 的 primary/accent/bg 时主题色覆盖主角色，风格固定色（深绿/浅绿）保留。

## 4. 兼容色板

warm-earth ✓✓（气质最合：奶油+绿+粉同源）/ navy-trust ✓（primary 换海军蓝，accent 仍粉，可用）/ tech-cyan ✗（冷色与文学气质冲突）/ dark-cinematic ✗（暗底破坏奶油纸面感）

## 5. 模板文件

[cover.html](cover.html) · [ending.html](ending.html) · [chapter.html](chapter.html) · [theme.html](theme.html)
