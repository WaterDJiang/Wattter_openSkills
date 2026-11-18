# HTML background style: gradient-panel

现代渐变面板 + 几何强调。企业通用，克制现代。

## 1. 视觉特征

- 全幅极浅渐变背景（bg → surface），层次微妙、不抢内容
- 左侧 60px primary→accent 渐变竖面板（本风格得名），贯穿全高
- 顶部 accent 细色带（cover/chapter）或装饰短线（ending）
- 右上角 primary→accent 渐变圆角强调块 + 装饰圆环（cover/chapter）
- 底部 primary→accent 渐变带（ending）或 accent 细条（cover 左下）
- theme 仅顶/底色带 + 极淡左侧面板 + 右上角描边方块，最大化内容留白

## 2. text-slot 契约

见 [slots.json](slots.json)（3 风格共享坐标）：

| 模板 | slot | 坐标 (x1,y1 x2,y2) |
|---|---|---|
| cover | title | 80,280 1200,380 |
| cover | subtitle | 80,400 1200,455 |
| cover | author | 80,625 640,665 |
| cover | date | 660,625 1200,665 |
| ending | thanks | 80,290 1200,400 |
| ending | contact | 80,560 1200,650 |
| chapter | chapter_num | 80,200 460,380 |
| chapter | chapter_name | 80,420 1200,490 |
| theme | （无） | Executor 自由设计内容层 |

## 3. 兼容色板

navy-trust ✓✓ / tech-cyan ✓✓ / warm-earth ✓ / dark-cinematic ✓

> dark-cinematic 下 bg 为深色，浅渐变变为「深 → 更深」，强调块的金色 accent 仍醒目，可用。

## 4. 模板文件

[cover.html](cover.html) · [ending.html](ending.html) · [chapter.html](chapter.html) · [theme.html](theme.html)
