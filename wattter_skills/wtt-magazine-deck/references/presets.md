# 预设方案参考（Presets）

4 个命名预设，在 Step 1 需求澄清时选择。也可以自定义布局序列，不局限于预设。

**重要**：每个预设现在提供 **主序列 + 备选序列** 两套布局排列。选了预设不等于锁死流程——两套序列任选其一，或在主序列上增删页面、换变体。预设是起点，不是牢笼。

---

## § 组合硬规则（所有预设与自定义序列都必须遵守）

### A. 主题节奏（沿用 layouts.md）

- 每页 `<section>` 必须带 `light` / `dark` / `hero light` / `hero dark` 之一
- ❌ 连续 3 页以上同主题
- ❌ 6 页以上 deck 没有 ≥1 `hero dark` + ≥1 `hero light`
- ❌ 整 deck 只有 `light` 正文页、没有任何 `dark` 正文页
- ✅ 每 3-4 页插 1 个 hero

### B. 变体变换（核心 · 防版式雷同）

- **同布局重复必须换变体**：Layout 4 出现两次 → 第二次必须 A→B 或 A→C，不允许两页同变体
- **相邻页构图不得相同**：相邻 slide 的 grid 比例 / 方向 / 结构至少一项不同
- **grid 比例有意混用**：不要全 deck 都是 `grid-2-7-5`；7:5 / 5:7 / 8:4 / 6:6 / 3 栏穿插
- **等分类不连用**：3-A 与 3-B、5-A 与 5-B 不相邻（都是等分网格，会雷同）
- **全幅叠加克制**：4-C / 10-C 合计 ≤ 2 个
- **hero 不堆叠**：hero 与正文 2-3:1 交错，不连续 2 页 hero（封面+幕封除外）

### C. 动效标注

- 每页至少一个 `data-anim`（即使只 `fade-up`）
- hero 页用 `spotlight` / `ripple-reveal`（加在 `<section>`）
- 列表/网格/数据用 `stagger-list`
- 沉浸模式 FX 全 deck ≤ 2 种

---

## 预设总览

| 预设 | 页数 | 特点 | 适用场景 |
|---|---|---|---|
| **minimal** | 6 | 最少布局种类，快速出活 | 短闪电演讲、5 分钟内 |
| **presentation** | 10 | 布局种类丰富，展示全能力 | 标准演讲、默认推荐 |
| **data-report** | 8 | 多数据 + pipeline + rowline + 对比 | 季度汇报、数据分享 |
| **image-showcase** | 8 | 多大视觉 + grid + kenburns | 作品集、产品展示 |

下文每个预设给出 **主序列** 和 **备选序列**。备选用不同布局/变体，解决"选了预设就千篇一律"的问题——两套都合规，挑更贴合内容的那套，或在主序列上局部替换。

---

## minimal（6 页 · 5 分钟闪电演讲）

### 主序列

| 页 | Layout · 变体 | 主题 | data-anim |
|---|---|---|---|
| 1 | Layout 1 · A 居中 | hero dark | spotlight |
| 2 | Layout 2 · A 居中 | hero light | ripple-reveal |
| 3 | Layout 3 · B 2×2 大格 | light | stagger-list |
| 4 | Layout 4 · A 7:5 左字右图 | dark | fade-up |
| 5 | Layout 7 · A 居中 | hero dark | spotlight |
| 6 | Layout 8 · A 居中 | hero light | fade-up |

### 备选序列（更偏故事/金句）

| 页 | Layout · 变体 | 主题 | data-anim |
|---|---|---|---|
| 1 | Layout 1 · B 左下压角 | hero dark | spotlight |
| 2 | Layout 12 · 单数字大字 | hero dark | rise-in |
| 3 | Layout 4 · B 5:7 左图右字 | light | fade-up |
| 4 | Layout 10 · A 8:4 左文右图 | dark | fade-up |
| 5 | Layout 7 · C 巨型问号 ghost | hero dark | spotlight |
| 6 | Layout 8 · C 全屏一句 | hero dark | rise-in |

**沉浸模式 FX 推荐**：封面 `constellation`，收束 `sparkle-trail`，单数字页 `counter-explosion`

---

## presentation（10 页 · 10-20 分钟标准演讲）

### 主序列

| 页 | Layout · 变体 | 主题 | data-anim |
|---|---|---|---|
| 1 | Layout 1 · A 居中 | hero dark | spotlight |
| 2 | Layout 2 · A 居中 | hero light | ripple-reveal |
| 3 | Layout 3 · A 3×2 网格 | light | stagger-list + counter-up |
| 4 | Layout 4 · A 7:5 左字右图 | light | fade-up |
| 5 | Layout 5 · A 3×2 网格 | dark | stagger-list |
| 6 | Layout 6 · A 双行 pipeline | light | stagger-list |
| 7 | Layout 7 · A 居中 | hero dark | spotlight |
| 8 | Layout 8 · A 居中 | light | rise-in |
| 9 | Layout 9 · A 左右双列 | dark | stagger-list |
| 10 | Layout 8 · C 全屏一句 | hero light | fade-up |

### 备选序列（换布局 + 换变体，避免与主序列雷同）

| 页 | Layout · 变体 | 主题 | data-anim |
|---|---|---|---|
| 1 | Layout 1 · C 中英对照 | hero dark | spotlight |
| 2 | Layout 2 · B ghost 序号 | hero light | ripple-reveal |
| 3 | Layout 12 · 单数字大字 | hero dark | rise-in |
| 4 | Layout 4 · B 5:7 左图右字 | dark | fade-up |
| 5 | Layout 11 · 时间轴 | light | stagger-list |
| 6 | Layout 6 · B 单行横向 | light | stagger-list |
| 7 | Layout 7 · B 左下发问 | hero dark | spotlight |
| 8 | Layout 13 · 引用墙 | light | stagger-list |
| 9 | Layout 9 · C 三段演进 | dark | stagger-list |
| 10 | Layout 8 · B 左对齐大引号 | hero light | rise-in |

**沉浸模式 FX 推荐**：封面 `constellation`，单数字/悬念页 `particle-burst`，Pipeline 页 `chain-react`

注意主/备选的对比：主序列第 4 页是 4-A（左字右图），备选是 4-B（左图右字）——**同布局换变体**；主序列第 3 页是 3-A（3×2），备选换成 Layout 12（单数字）——**换布局**。两种手法都是合规的"防雷同"操作。

---

## data-report（8 页 · 数据报告）

### 主序列

| 页 | Layout · 变体 | 主题 | data-anim |
|---|---|---|---|
| 1 | Layout 1 · A 居中 | hero dark | spotlight |
| 2 | Layout 3 · A 3×2 网格 | light | stagger-list + counter-up |
| 3 | Layout 6 · A 双行 pipeline | dark | stagger-list |
| 4 | Rowline 表格布局（见 components.md） | light | stagger-list |
| 5 | Layout 4 · A 7:5 左字右图 | dark | fade-up |
| 6 | Layout 9 · A 左右双列 | light | stagger-list |
| 7 | Layout 7 · A 居中 | hero dark | spotlight |
| 8 | Layout 8 · A 居中 | hero light | fade-up |

### 备选序列（数据呈现换形态）

| 页 | Layout · 变体 | 主题 | data-anim |
|---|---|---|---|
| 1 | Layout 1 · B 左下压角 | hero dark | spotlight |
| 2 | Layout 12 · 单数字大字 | hero dark | rise-in |
| 3 | Layout 3 · C 横向数据条 | light | stagger-list + counter-up |
| 4 | Layout 11 · 时间轴 | dark | stagger-list |
| 5 | Layout 4 · B 5:7 左图右字 | light | fade-up |
| 6 | Layout 9 · B 上下堆叠 | dark | stagger-list |
| 7 | Layout 7 · C 巨型问号 ghost | hero dark | spotlight |
| 8 | Layout 8 · B 左对齐大引号 | hero light | rise-in |

**沉浸模式 FX 推荐**：封面 `constellation`，金句页 `particle-burst`，数据流水线 `data-stream`

---

## image-showcase（8 页 · 视觉展示）

### 主序列

| 页 | Layout · 变体 | 主题 | data-anim |
|---|---|---|---|
| 1 | Layout 1 · A 居中 | hero dark | spotlight |
| 2 | 大视觉页（全幅图 + bottom-left 叠加） | hero light | kenburns |
| 3 | Layout 5 · A 3×2 网格 | light | stagger-list |
| 4 | Layout 4 · A 7:5 左字右图 | dark | fade-up |
| 5 | 大视觉页（全幅图 + bottom-right 叠加） | hero dark | kenburns |
| 6 | Layout 10 · A 8:4 左文右图 | light | fade-up |
| 7 | Layout 8 · A 居中 | hero light | rise-in |
| 8 | Layout 8 · C 全屏一句 | hero dark | fade-up |

### 备选序列（图占比更高、用新布局）

| 页 | Layout · 变体 | 主题 | data-anim |
|---|---|---|---|
| 1 | Layout 1 · B 左下压角 | hero dark | spotlight |
| 2 | Layout 4 · C 全幅图+角落叠加 | hero dark | kenburns |
| 3 | Layout 5 · B 2×2 大图 | light | stagger-list |
| 4 | Layout 10 · B 4:8 左图右文 | dark | fade-up |
| 5 | Layout 5 · C 1 大+多小 | light | stagger-list |
| 6 | Layout 15 · 双页跨页 | dark | fade-up |
| 7 | Layout 13 · 引用墙 | hero light | stagger-list |
| 8 | Layout 8 · C 全屏一句 | hero dark | rise-in |

**沉浸模式 FX 推荐**：大视觉页 `gradient-blob`，收束 `sparkle-trail`，图片网格页 `galaxy-swirl`

注意：大视觉页（全幅图 + 叠加标题）本质就是 Layout 4-C / 10-C 的全幅叠加变体。备选序列里把"大视觉页"直接写成 Layout 4-C，更明确。整个 deck 全幅叠加页控制在 2 个以内。

---

## § 变体选择规则（生成时逐页决策）

挑布局时不要只记 Layout 编号，要连变体一起记。决策流程：

1. **先定布局**：根据这一页的信息类型选 Layout（数据→3/12，故事→4/10，流程→6，历程→11，金句→8/13…）
2. **再定变体**：看这一页的图/文比重和上下文：
   - 图为主 → 4-B / 10-B / 4-C / 10-C
   - 文为主 → 4-A / 10-A
   - 指标多 → 3-A；指标少但关键 → 3-B / 12
   - 要叙事不要并置 → 9-B / 11
3. **回头查重复**：本布局在本 deck 出现过吗？出现过就**强制换变体**（A→B→C 轮换）。
4. **查相邻**：上一页用了什么 grid/方向？这页不能一样。

### 变体轮换速查（同布局第二次出现时）

| 布局 | 第 1 次 | 第 2 次 | 第 3 次（若需） |
|---|---|---|---|
| 1 封面 | A | B | C |
| 2 幕封 | A | B | C |
| 3 大字报 | A | B | C |
| 4 左文右图 | A | B | C |
| 5 图片网格 | A | B | C |
| 6 Pipeline | A | B | C |
| 7 问题页 | A | B | C |
| 8 大引用 | A | B | C |
| 9 对比 | A | B | C |
| 10 图文混排 | A | B | C |

---

## § 如何避免雷同（生成后自检）

```bash
# 1. 主题节奏：确认 light/dark/hero 交错，无 3 连同色
grep 'class="slide' index.html

# 2. grid 比例混用：不应只有一个值反复出现
grep -oE 'grid-2-[0-9]+-[0-9]+|grid-[0-9]+' index.html | sort | uniq -c

# 3. 同布局重复检查：列出每页用的 layout（靠 chrome/foot 标注或人工对照大纲）
#    人工目视：两页构图是否几乎一样？一样就换变体。
```

**雷同高发场景**（特别留意）：
- 全 deck 正文页都是 Layout 4-A（左字右图 7:5）→ 至少一半换成 4-B / 10-A / 10-B
- 多个数据页都是 3-A（3×2）→ 穿插 3-C / 12 / rowline
- 多个金句页都是 8-A（居中）→ 换 8-B / 8-C

---

## 自定义布局序列

如果 4 个预设都不合适，可以自定义。步骤：

1. **确定页数**（参考 SKILL.md 的"时长与页数对照"）
2. **从 layouts.md 的 15 种布局中逐页选择**，连变体一起定（如"Layout 4 · B"）
3. **画主题节奏表**（每页写清 hero dark / hero light / light / dark）
4. **画变体表**（每页写清 Layout · 变体），确认同布局不重复同变体、相邻页构图不同
5. **遵守上方「组合硬规则」A/B/C 三组**
6. **填入 `assets/styles/editorial/template.html` 的 `{{LAYOUT_SECTIONS}}` 位置**

自定义时特别注意：
- 每页必须有 `data-anim` 声明（即使只写 `data-anim="fade-up"`）
- 主题节奏必须遵循 layouts.md 的硬规则
- 布局骨架从 layouts.md 拷贝（含变体），不要从零手写
- **生成后跑一遍「如何避免雷同」自检**
