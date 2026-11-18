# HTML background style: cobalt-studio

钴蓝工作室 —— 醒目、工业感、宣言式。移植自 open-design `fs-electric-studio`(钴蓝工作室),按色系主题改名。

## 1. 视觉特征

- **签名 device: 50/50 上下分割 + 黑色 9px edge bar 接缝**(整套 deck 强一致)
- 上半区白底(`#fff`)放下大字号宣言型标题;下半区钴蓝(`#4361ee`)放 lede / 联系信息
- 4 角品牌 mark(TL/TR/BL/BR),Manrope 800 uppercase + 钴蓝小色块 chip,信息密度低、识别度高
- 全 Manrope 字体(800 display / 400 body),大量负空间,强对比
- 适合品牌发布、产品发布、产品故事、企业汇报开场

## 2. text-slot 契约

见 [slots.json](slots.json)(本风格独立坐标,与起步 3 风格不同;cover 用 5 槽 kicker/title/subtitle/author/date):

| 模板 | slot | 坐标 (x1,y1 x2,y2) |
|---|---|---|
| cover | kicker | 80,160 600,210 |
| cover | title | 80,230 1200,340 |
| cover | subtitle | 80,400 1200,500 |
| cover | author | 80,640 640,690 |
| cover | date | 660,640 1200,690 |
| ending | thanks | 80,180 1200,460 |
| ending | contact | 80,500 1200,620 |
| chapter | chapter_num | 240,140 1040,500 |
| chapter | chapter_name | 80,540 1200,620 |
| theme | (无) | Executor 自由设计内容层 |

## 3. 配色与变量

**风格固定色**(DNA,写死 `:root`,不被色板覆盖):`--near-black` #0a0a0a(edge bar + 4 角 mark 用)

**主题角色**(`{{var}}` 覆盖;不传 = 原生钴蓝白):
- `--primary` = #4361ee(钴蓝,下半 panel 底)
- `--accent` = #4361ee(钴蓝,装饰用,等同 primary)
- `--bg` = #ffffff(白,上半 panel 底)
- `--surface` = #f5f5f5(微灰,备用)
- `--text` = #0a0a0a(近黑,白底上的文字)

不传 variables 时渲染原汁原味钴蓝白对比;传 theme_palette 的 primary(主)+bg(白底)时主题色覆盖——注意 edge bar 的 `--near-black` 永远写死(签名 device 不能变)。

## 4. 兼容色板

navy-trust ✓✓(气质最合:navy 替换钴蓝,仍强对比) / tech-cyan ✓(primary 换青,反差大) / warm-earth ✗(奶油+钴蓝气质冲突) / dark-cinematic ✗(暗底破坏白上半 panel 的高对比)

## 5. 模板文件

[cover.html](cover.html) · [ending.html](ending.html) · [chapter.html](chapter.html) · [theme.html](theme.html)
