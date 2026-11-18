# wtt-nine-image

多风格图片与封面技能。A–E将概念、流程、教学或人像创意转化为中文提示词；F「封面」按内容选四种风格，各生成一张真实候选后让用户选。

## 六个类别

| 风格 | 名称 | 格式 | 一句话描述 |
|:---|:---|:---|:---|
| A | 9号漫画 | 竖版长图（~720x2800） | 手绘黑白人物+荒诞比喻+一本正经用最俗的日常解释最高深的概念 |
| B | 信息图 | 横版 16:9（~1920x1080） | 手绘卡通风格信息图，突出关键词与核心概念 |
| C | 四格漫画 | 竖版 3:4（~1080x1440） | Q版可爱多格学习漫画，温暖治愈，10-20 页 |
| D | 线条人 | 横版 16:9（~1920x1080） | 极简单线条人 + 克莱因蓝点缀，New Yorker 风格概念插图 |
| E | 生活感人像 | 竖版 3:4 / 4:5（~1080x1440） | vibe 抓拍摄影风格，10 张成组，韩国 INS 网红主体 |
| F | 封面 | 按展示位；未指定默认16:9候选稿 | 内容选型，四种风格各生成一张，选中后深化 |

## 快速触发

- **9号漫画**：说 "9号漫画" / "恶搞科普" / "竖版长图" / "nine-comic"
- **信息图**：说 "信息图" / "infographic" / "横版卡通" / "16:9 infographic"
- **四格漫画**：说 "四格漫画" / "Q版漫画" / "Chiikawa漫画" / "学习漫画"
- **线条人**：说 "线条人" / "线人" / "克莱因蓝" / "纽约客风格"
- **生活感人像**：说 "生活感人像" / "vibe" / "vibeshot" / "韩国INS" / "胶片人像" / "lifestyle portrait"
- **封面**：说“做封面”/“公众号头图”/“文章封面”/“视频缩略图”/“cover”，直接进入F，不先问画风。

## 封面四选一

- 通读材料后，根据正文观点、标题长短、关键词和氛围，从[35个自有方向](references/cover-style-catalog.json)选四种。可用字做空间结构、让字物穿插、同材质成字或用主体围出字区。需要时选用有出处的真实元素。[图文融合规则](references/cover-type-composition.md)
- 支持完整标题、指定核心文案、预留字区与纯无字。独立尺寸套图按各自画幅重排。[展示位预设](references/cover-platform-presets.md)
- 默认交付四张独立图片；只要提示词或没有生图通道时明确未出图。选定后只深化所选。
- 明确风格、数量、标题、无字或参考图时遵从用户。“线条人封面”沿用D规则，其他方向不固定沐瑶/黑字/白底。
- 跨渠道首轮不自动乘成四风格×多平台；用户选定后适配所需展示位。详见[封面流程](references/style-f-cover.md)与[候选记录骨架](references/cover-prompt-skeleton.md)。

## 目录结构

```
wtt-nine-image/
├── SKILL.md                                    # 主技能定义，按用途/画风路由
├── README.md                                   # 本文件
├── CHANGELOG.md                                # 更新日志
├── assets/
│   └── nine-comic-character-ref.png            # 风格 A 角色参考图
└── references/                                  # 渐进式披露：详细内容按需加载
    ├── shared-mechanisms.md                     # 跨风格通用：N1-N7 + 主体一致性 + 比例锚定 + 文字渲染
    ├── style-a-nine-comic.md                    # 风格 A 完整参考
    ├── style-b-infographic.md                   # 风格 B 完整参考
    ├── style-c-four-panel.md                    # 风格 C 完整参考
    ├── style-d-line-figure.md                   # 风格 D 完整参考
    ├── style-e-vibe.md                          # 风格 E 完整参考
    ├── style-f-cover.md                         # 封面四候选流程
    ├── cover-style-catalog.json                 # 35个自有封面方向
    ├── cover-prompt-skeleton.md                 # 封面提示词与候选记录
    ├── nine-comic-prompt-skeleton.md            # 风格 A 提示词骨架
    ├── nine-comic-metaphor-catalog.md           # 风格 A 比喻实战目录
    ├── infographic-prompt-skeleton.md           # 风格 B 提示词骨架
    ├── four-panel-prompt-skeleton.md            # 风格 C 提示词骨架 + 视觉风格指令块模板
    ├── four-panel-character-archetypes.md       # 风格 C 角色原型 + IP 映射预设
    ├── line-figure-prompt-skeleton.md           # 风格 D 提示词骨架
    ├── vibe-prompt-skeleton.md                  # 风格 E 提示词骨架（中文 / 英文 + 3 示例 + 自检清单）
    ├── vibe-variable-catalog.md                 # 风格 E 12 个变量池 + 组合禁忌 + 实战经验
    ├── multi-page-handling.md                   # 多页拆分策略（A/B/C 适用；D/E 不适用）
    └── feedback-by-style.md                     # A–F各自的反馈处理
```

## 核心设计理念

- **抽奖，不是质检**：并行生成多个候选，让用户挑选，不做预筛选
- **按分支交付**：A–E保持原工作流；F默认实际生成四张候选后让用户选，指定生图通道的费用与确认约束继续有效。
- **风格铁律不可违反**：每种风格有不可变的视觉身份规则
- **实战经验沉淀**：每种风格都有从实际生成中总结的硬经验
- **共享机制分层**（v2 新增）：跨风格的通用机制（N1-N7 框架 + 主体一致性 + 比例锚定 + 文字渲染）集中在 `shared-mechanisms.md`，每个 style 章节通过机制编号引用
- **渐进式披露**（v2.1 新增）：SKILL.md 精简到 263 行，详细内容按需加载到 references/
- **vibe 摄影 12 池**（v2 新增风格 E）：表情 / 服装 / 场景 / 瞬间状态 / 景别 / 焦段 / 机位 / 构图 / 前景 / 光线 / 色彩 / 摄影状态 —— 默认 10 张成组 + 批次差异强制规则

## 加载指引

- 命中触发词 → 加载 SKILL.md；有封面制作意图直接进F
- 风格路由 → 加载对应的 **prompt-skeleton** 文件（取提示词模板）
- 实战经验 / 反馈处理 → 加载对应的 **style-X** 文件
- 跨风格通用规则 → 加载 `shared-mechanisms.md`

## 支持的 IP 预设（风格 C）

- Chiikawa（吉伊卡哇）
- Line Friends
- Sanrio（三丽鸥）
- WTT 原创角色：小九
- 自定义 IP（按模板映射）

## 版本

v2.7.0 —— 按风格设计标题与场景的关系，补齐文字模式、展示位和独立尺寸重排。详见 CHANGELOG.md。

## 线条人封面默认值

- 封面字体：沐瑶随心手写体；正文默认喜脉。先用 [本地解析器](scripts/resolve_font.py)定位真实TTF；沐瑶保存在独立用户目录，避免更新技能后丢失和重复下载。真实排字与来源见 [排字流程](references/font-typesetting.md)。
- 封面标题：按[原文焦点、逐段字号与图文关系](references/platform-cover-layouts.md#标题强调与图文关系)建立强调，完整标题仍按原序可读；不统一等大排版、不另造短口号，全部文字保持纯黑。
- 全部封面文字纯黑 `#000000`，含关键词与辅助文字；克莱因蓝仅用于插图。
- 先按内容构图，再根据无字图的实际负空间排字；四面留白，按 [平台封面规则](references/platform-cover-layouts.md) 导出。

线条人封面支持[16种构图策略](references/cover-composition-strategies.md)：按内容关系、阅读焦点、完整标题容量和展示位自动选择主策略，按需借用兼容技巧；用户指定方向优先。正文极小人规则不限制封面的全身尺度。

封面必须执行[字图干扰检查](references/font-typesetting.md#字图干扰检查按实际图层放行)：按实际文字层检查重叠与净空，再人工查看各尺寸，不能固定套用样张文字坐标。
