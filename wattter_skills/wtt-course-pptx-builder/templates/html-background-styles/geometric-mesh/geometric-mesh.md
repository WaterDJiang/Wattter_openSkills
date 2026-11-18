# HTML background style: geometric-mesh

大色块对角分割 + 网格/chevron motif。科技、产品、活力，醒目有力。

## 1. 视觉特征

- 顶部 primary 大色块（左下斜切 `clip-path`），叠 accent 网格点阵 motif
- 中部 chevron 装饰（右指箭头，title 与 author 之间安全区）
- 底部 primary→accent 色块斜切（ending）或 accent 细条（cover）
- theme 仅顶/底斜切色块 + 左侧极淡网格点阵，最大化内容留白
- 装饰严格落在 slot 之间的安全区，文字 slot 区保持浅渐变留白可读

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

tech-cyan ✓✓ / navy-trust ✓ / dark-cinematic ✓ / warm-earth ✗

> warm-earth 的暖色调与几何切割的冷峻科技感气质冲突，不推荐。

## 4. 模板文件

[cover.html](cover.html) · [ending.html](ending.html) · [chapter.html](chapter.html) · [theme.html](theme.html)
