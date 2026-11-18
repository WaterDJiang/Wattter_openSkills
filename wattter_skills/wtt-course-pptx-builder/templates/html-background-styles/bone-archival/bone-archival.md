# HTML background style: bone-archival

骨纸档案 —— 镂空、工业档案、复古军工。移植自 open-design `html-ppt-zhangzara-stencil-tablet`(模板平板),按色系主题改名。

## 1. 视觉特征

- 骨色底 (#E2DCC9) + 纸色备用 (#F4EFE0) + 墨 #0A0A0A
- **Stardos Stencil 镂空字**(最签名 device)+ Barlow Condensed 标签 + Inter 数字
- 7 大地色(地球色):sienna #A06A3C / magenta #C73B7A / orange #EE7A2E / teal #2D7E73 / blue #3F73B7 / mustard #D8A93B / olive #6F7A2E
- cover 右上 teal 抽象图形(空心圆 + 实心方块旋转 + 短线)+ 底部小橙色圆角 mark
- chapter 巨大 stencil 数字 + 右上 label
- ending 左右撞色对(teal 左 + orange 右)+ 3 步骤 stencil 数字
- 适合工业/军工/建筑/纪实/品牌档案/产品发布/复古海报/电影海报

## 2. text-slot 契约

见 [slots.json](slots.json)(本风格独立坐标):

| 模板 | slot | 坐标 (x1,y1 x2,y2) |
|---|---|---|
| cover | super | 50,80 1000,110 |
| cover | title | 50,160 950,440 |
| cover | subtitle | 50,460 950,530 |
| cover | author | 530,640 780,680 |
| cover | date | 900,640 1200,680 |
| ending | thanks | 50,120 590,460 |
| ending | contact | 50,490 590,580 |
| chapter | chapter_num | 460,140 800,580 |
| chapter | chapter_name | 820,220 1200,540 |
| theme | (无) | Executor 自由设计内容层 |

## 3. 配色与变量

**风格固定色**(DNA,写死 `:root`,不被色板覆盖):
- 底: `--bone` #E2DCC9 / `--paper` #F4EFE0
- 墨: `--ink` #0A0A0A
- 7 大地色: sienna / magenta / orange / teal / blue / mustard / olive(全部写死,作风格 DNA)

**主题角色**(`{{var}}` 覆盖;不传 = 原生骨纸档案):
- `--primary` = #2D7E73(teal,主色)
- `--accent` = #C73B7A(magenta,装饰)
- `--bg` = #E2DCC9(骨底)
- `--surface` = #F4EFE0(纸色)
- `--text` = #0A0A0A(墨)

不传 variables 时渲染原汁原味骨纸档案 7 大地色;传 theme_palette 时主题色覆盖主角色,7 大地色保留(它们是风格 DNA)。

## 4. 兼容色板

warm-earth ✓✓(气质最合:骨色+大地色同源) / dark-cinematic ✓(墨+骨色,适合 industrial) / navy-trust ✗(海军蓝破坏大地色节奏) / tech-cyan ✗(冷色与镂空复古气质冲突)

## 5. 模板文件

[cover.html](cover.html) · [ending.html](ending.html) · [chapter.html](chapter.html) · [theme.html](theme.html)
