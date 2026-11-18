# HTML background style: editorial-rule

顶部色带 + 发丝线 + 大量留白。高端咨询、学术、编辑型克制。

## 1. 视觉特征

- 纯 bg 底色（不用渐变），最大化留白与呼吸感
- 顶部 primary 色带（cover/ending/chapter 高 14px；theme 高 8px）
- accent 发丝强调线（短，96px 宽）置于 title / thanks / chapter_num 上方，作为「栏目标」
- border 发丝线（1px，横贯）作为内容区分隔（页脚上方 / contact 上方 / chapter_name 上方）
- theme 仅顶/底色带 + 右侧极淡发丝线，极简
- 全靠色带与发丝线定义结构，零色块填充——最克制的编辑型美学

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

navy-trust ✓✓ / warm-earth ✓✓ / tech-cyan ✓ / dark-cinematic ✗

> dark-cinematic 深底会丧失 editorial 靠「白底大量留白」建立的克制感，不推荐。

## 4. 模板文件

[cover.html](cover.html) · [ending.html](ending.html) · [chapter.html](chapter.html) · [theme.html](theme.html)
