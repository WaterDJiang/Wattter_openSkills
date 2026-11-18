# HTML background style: macaron-soft

柔光马卡龙 —— 柔和、生活气息、慢内容。移植自 open-design `html-ppt-xhs-pastel-card`(Xhs 柔和马卡龙卡片),按色系主题改名。

## 1. 视觉特征

- 奶油底 (#fef8f1) + 3 个马卡龙径向渐变 blob(桃/薄荷/紫)+ 微模糊(2px)制造柔光氛围
- 顶部药丸 chip(白底圆角 + 彩色小圆点 + 大写短词)+ 右侧页码
- Playfair Display 衬线斜体大字 + Inter sans 正文,中文用 Noto Serif SC / Noto Sans SC
- 底部脚注条(by Brand · pastel edition) 签名节奏
- 适合小红书、Instagram、品牌内容、生活方式、个人随笔、慢生活、节庆

## 2. text-slot 契约

见 [slots.json](slots.json)(本风格独立坐标,cover 6 槽 kicker/title/divider/subtitle/author/date,divider 是 4px 高的细线):

| 模板 | slot | 坐标 (x1,y1 x2,y2) |
|---|---|---|
| cover | kicker | 60,140 600,170 |
| cover | title | 60,180 1200,400 |
| cover | divider | 60,420 150,424 |
| cover | subtitle | 60,440 1200,520 |
| cover | author | 60,650 600,690 |
| cover | date | 660,650 1200,690 |
| ending | thanks | 60,200 1200,460 |
| ending | contact | 60,500 1200,620 |
| chapter | chapter_num | 60,160 1200,440 |
| chapter | chapter_name | 60,460 1200,540 |
| theme | (无) | Executor 自由设计内容层 |

## 3. 配色与变量

**风格固定色**(DNA,写死 `:root`,不被色板覆盖):
- 底: `--xp-bg` #fef8f1(暖奶油)
- 文字墨: `--xp-ink` #2a2340 / `--xp-ink2` #5b5470 / `--xp-muted` #9089a8
- 6 马卡龙对(浅+深): peach #ffd8c2 / #f48b5c、mint #c8ecd8 / #2e9d70、sky #c9dcfb / #4e7ed6、lilac #ddd0f5 / #7b5dc4、lemon #fdf0b2 / #c8910a、rose #fcd0dd / #c94673

**主题角色**(`{{var}}` 覆盖;不传 = 原生马卡龙色):
- `--primary` = #f48b5c(peach-d,blob 桃)
- `--accent` = #c94673(rose-d,装饰)
- `--bg` = #fef8f1(奶油底)
- `--surface` = #fff(药丸 chip 底)
- `--text` = #2a2340(墨)

不传 variables 时渲染原汁原味 6 色马卡龙;传 theme_palette 的 primary/accent/bg/text 时主题色覆盖主角色,6 马卡龙装饰色保留(它们是风格 DNA)。

## 4. 兼容色板

warm-earth ✓✓(气质最合:奶油+多色同源) / navy-trust ✓(墨色加深,bg 仍奶油) / tech-cyan ✗(冷色与柔光气质冲突) / dark-cinematic ✗(暗底破坏奶油柔光)

## 5. 模板文件

[cover.html](cover.html) · [ending.html](ending.html) · [chapter.html](chapter.html) · [theme.html](theme.html)
