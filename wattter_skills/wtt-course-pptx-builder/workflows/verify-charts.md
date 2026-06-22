---
description: 使用 svg_position_calculator.py 把图表坐标与设计规范做对照
---

# 图表校准工作流

> 独立的生成后步骤。运行时机：在一份含数据图表的 deck 完成 SVG 生成之后、后期处理与导出之前。专门捕捉 AI 模型把数据映射到像素位置时常常引入的 10–50 px 坐标错误。

本工作流**独立运行**：读取 `design_spec.md` 与已生成的 SVG，然后跑计算器脚本——无需上游会话上下文。可放心在新会话中调用。

## 何时运行

- deck 含一张或多张数据可视化图表，其 SVG 几何由源数值驱动：柱长/高、点位、弧角、多边形顶点、连接端点、气泡中心/半径、或流宽度/路径。
- SVG 已生成到 `<project_path>/svg_output/` 且 `svg_quality_checker.py` 已通过。
- 后期处理（`finalize_svg.py`、`svg_to_pptx.py`）**尚未**运行。

计算器为简单柱状、折线/散点、饼图/环形、雷达、网格版式提供了直接的 CLI 形态。复合/派生图表**并非自动排除在外**：如果其几何可化归为多次直接计算，则纳入 `decomposable-calc`；如果计算器没有版式模型但 SVG 几何仍由数据驱动，则纳入 `manual-verify`，避免被静默跳过。

---

## Step 1：从设计规范构建页面清单

读取 `<project_path>/design_spec.md` §VII 可视化参考清单（权威的 deck 计划；与 §IX 页面大纲交叉核对），把 SVG 几何由数据值驱动的每一页都纳入。把每张纳入页面精确分到一个 mode：

| Mode | `charts_index.json` key | 备注 |
|------|--------------------------|-------|
| `direct-calc` | `bar_chart`、`horizontal_bar_chart` | 用 `calc bar`；水平柱加 `--horizontal`。 |
| `direct-calc` | `line_chart`、`area_chart`、`scatter_chart` | 用 `calc line`；面积图把折线输出作为上边界，再合到 `y_max`。 |
| `direct-calc` | `pie_chart`、`donut_chart` | 用 `calc pie`；环形图传 `--inner-radius`。 |
| `direct-calc` | `radar_chart` | 用 `calc radar`；独立子命令，不在 `calc pie` 之下。 |
| `decomposable-calc` | `stacked_bar_chart`、`stacked_area_chart`、`grouped_bar_chart`、`dumbbell_chart`、`pareto_chart`、`dual_axis_line_chart`、`bullet_chart`、`butterfly_chart`、`waterfall_chart`、`box_plot_chart`、`gantt_chart` | 通过多次直接计算来校准；见下文各 recipe。 |
| `partial-calc` | `bubble_chart` | 用 `calc line` 校准 `cx/cy`；只有当尺寸比例显式时才校准半径。 |
| `formula-verify` | `progress_bar_chart`、`gauge_chart`、`funnel_chart` | 一行算式；把公式和算出的长度/角度/宽度记入收据，无需调用计算器。 |
| `manual-verify` | `sankey_chart`、`heatmap_chart`、`treemap_chart` | 数据驱动的几何存在，但当前计算器没有完整的版式模型。人工检视并报告；不要静默跳过。 |

**不在范围**（除非页面在版式中嵌入了数据驱动子图，否则不要纳入收据）：

- 纯文字/数字看板：`kpi_cards`。
- 表格：`comparison_table`、`basic_table`、`consulting_table`、`project_schedule_table`、`financial_statement_table`、`feature_matrix_table`、`harvey_balls_table`。
- 信息图 / 框架图 / 示意图，其位置由版式而非数值驱动：如 `hub_spoke`、`hub_inward_arrows`、`quadrant_text_bullets`、`quadrant_bubble_scatter`（BCG 风格的四象限文字网格——视觉气泡是装饰，不是数值映射的点位）、`matrix_2x2`（固定的象限格子加文字卡）、`mind_map`、`process_flow`、`numbered_steps`、`timeline`、`roadmap_vertical`、`layered_architecture`、`module_composition`、`pipeline_with_stages`、`client_server_flow`、`top_down_tree`、`journey_map`、`agenda_list`。若某 deck 确实把这些当作数据驱动的散点（罕见——把数值映射到真实的 `cx/cy`），则提升为 `partial-calc` 并在收据里说明。

得到的清单形如：

```
P03 03_market_share.svg  type=bar        mode=direct-calc
P07 07_growth.svg        type=line       mode=direct-calc
P11 11_share_split.svg   type=pie        mode=direct-calc
P15 15_pareto.svg        type=pareto     mode=decomposable-calc
```

如果 §VII 缺失（旧项目 / 自由结构 deck），跳过本工作流并报告："design_spec.md 没有 §VII——图表页无法被权威枚举，verify-charts 已跳过"。**不要**退回到"根据 SVG 内容猜"——那会重新引入本工作流正是为消除的"静默跳过"故障。

如果筛出的清单为空，输出 `verify-charts: spec declares no data-driven chart geometry, nothing to verify` 并停止。

---

## Step 2：逐页 —— 读 SVG、跑计算器、对照、更新

对 Step 1 清单中的每页：

1. 读取 `<project_path>/svg_output/<page>.svg`。
2. 定位绘图区定义：
   - 优先：执行器放置的 `<!-- chart-plot-area: ... -->` 标记（见 [executor-base.md §3.1](../references/executor-base.md)）。直接读出坐标。
   - 缺失时：从 SVG 的轴线（矩形图表）或中心/半径元素（径向图表）反推绘图区。然后**把该标记回填到 SVG**，让后续运行不必再付一次这个成本。
3. 从 SVG 的 `<text>` 标签/值元素读出数据系列。
4. **为每个基于轴的图表读轴刻度标签。** 定位沿值轴排列的 `<text>` 元素——横向柱为 X 轴标签，竖向柱为 Y 轴标签，折线类图为 Y 轴标签。提取首尾刻度值以确定轴范围（如 `0%` 到 `120%` → 范围 `0,120`）。按需作为 `--value-range`、`--y-range` 或 `--x-range` 传入。雷达图用 `--max-value` 而非范围：读最外环的刻度值并把它作为 `--max-value` 传入。如果 SVG 没有显式刻度标签（只有数据标签，没有网格），省略范围让计算器自动归一——但要在收据里标 `scale=auto (no ticks)`。

   **局部坐标 vs 绝对坐标。** 许多图表模板把图表内容包在 `<g transform="translate(cx, cy)">` 之类的分组里，于是子 `<circle>` / `<polygon>` / `<rect>` 的坐标是相对该原点的（如雷达多边形在 `0,-198`、环形图路径在平移 `<g>` 内从 `0,0` 起步、dumbbell 圆在按行平移的 `<g>` 内位于 `cy="0"`）。计算器输出的是**绝对** SVG 坐标。对照前，要么把外包 translate 的偏移加到 SVG 坐标，要么从计算器输出里减去该偏移——任选一个方向并保持一致。
5. 运行对应的计算器命令：

   ```bash
   # bar_chart / horizontal_bar_chart（后者加 --horizontal）
   # 重要：务必从轴刻度标签传入 --value-range（步骤 4）
   python3 ${SKILL_DIR}/scripts/svg_position_calculator.py calc bar \
     --data "Label1:Value1,Label2:Value2" --area "x_min,y_min,x_max,y_max" \
     --bar-width 120 --value-range "0,axis_max"

   # line_chart / area_chart / scatter_chart — 面积图把折线输出作为上边界，再合到 y_max
   python3 ${SKILL_DIR}/scripts/svg_position_calculator.py calc line \
     --data "x1:y1,x2:y2,..." --area "x_min,y_min,x_max,y_max" --y-range "0,max"

   # pie_chart — 默认 start angle 为 -90（12 点钟方向）；仅当 SVG 从别的角度起步时才传 --start-angle
   python3 ${SKILL_DIR}/scripts/svg_position_calculator.py calc pie \
     --data "Slice1:Value1,Slice2:Value2" --center "cx,cy" --radius 200 --start-angle -90

   # donut_chart（pie + inner-radius）
   python3 ${SKILL_DIR}/scripts/svg_position_calculator.py calc pie \
     --data "Slice1:Value1,Slice2:Value2" --center "cx,cy" --radius 200 --inner-radius 120 --start-angle -90

   # radar_chart（独立子命令）— --max-value 取自最外环刻度
   python3 ${SKILL_DIR}/scripts/svg_position_calculator.py calc radar \
     --data "Dim1:Value1,Dim2:Value2,Dim3:Value3" --center "cx,cy" --radius 200 --max-value 100
   ```

   面积图的填充路径闭合到绘图区下边缘：

   ```svg
   M first_x,first_y ... L last_x,last_y L last_x,y_max L first_x,y_max Z
   ```

6. **尺度感知对照。** 把计算器输出与 SVG 已有坐标对照。在判定不匹配之前，先确认每次计算器调用都用了与 SVG 视觉上声明的同一组轴范围、绘图区、中心/半径、起始角度或尺寸比例。对 `calc bar`，输出头部在 SVG 含显式刻度时必须显示 `Value scale: axis ticks (...)`；若显示 `auto (max*1.1)`，回到步骤 4 用正确的 `--value-range` 重跑。**不要**用尺度不匹配的输出去更新 SVG。只有在确认尺度一致、且坐标确实不同时才更新 SVG 属性。手工更新（**不要**用正则 / 批量替换——坐标是按位置的，很容易写错）。

更新任何一页后，重跑项目的质量检查器，确认没有破坏：

```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>
```

---

## 堆叠 recipe

`stacked_bar_chart` 与 `stacked_area_chart` 不是单次调用，但能干净地化归为对既有原型的多次调用。操作员本来就得算累计值才能画 SVG——verify-charts 直接复用它们。

**堆叠柱**——对同一组 x 分类上的 N 条堆叠系列，运行 `calc bar` N 次。把每段的**高度**作为数据值传入，并把 `--area` 的 `y_max` 按该分类下方所有段的像素高度总和上移。把每段的 `(x, y, width, height)` 与 SVG 对照。

```bash
# 示例：分类 "Q1" 上的两系列堆叠，bottom=30、top=20，绘图区 y 从 100 到 500
# 第 1 次运行 — 底段（origin = 基线）
python3 ${SKILL_DIR}/scripts/svg_position_calculator.py calc bar \
  --data "Q1:30,Q2:..." --area "x_min,100,x_max,500" \
  --bar-width 80 --value-range "0,axis_max"
# 第 2 次运行 — 顶段（origin 按底段像素高度上移）
python3 ${SKILL_DIR}/scripts/svg_position_calculator.py calc bar \
  --data "Q1:20,Q2:..." --area "x_min,100,x_max,<500 - bottom_height_px>" \
  --bar-width 80 --value-range "0,axis_max"
```

**堆叠面积**——对 N 条堆叠系列，对**累计** y 值（系列 1 原值；系列 2 = 系列 1 + 系列 2；……）运行 `calc line` N 次。每次调用产出一条带的顶边界。每个带的 SVG 路径闭合到**上一带**的顶边界（而非 `y_max`）。

若某个堆叠页的段位置不能化归到这套 recipe（如负段、占比堆叠且总和不等于 100），在收据里标 `manual-verify` 并人工检视——不要静默放过。

---

## 可分解 recipe

把这些 recipe 用于 `decomposable-calc` 与 `partial-calc` 页。每条 recipe 都必须产出一条收据行；若某页不能干净地化归，则改标 `manual-verify` 并写明原因，不要直接跳过。

**Dumbbell 图**——跨分类的"前/后"或"两态"值。两个端点是**点**，不是柱端——`calc bar --horizontal` 总是锚定到 `x_min`，那只匹配右端点。改用 `calc line` × 2，把分类索引视作 y 轴：

1. 把分类编号为 `0.5, 1.5, …, N-0.5`，让每行的 y 落在对应行中心；设 `--y-range "0,N"`。同样的约定也适用于纵向 dumbbell（轴对调）。
2. 把 `--x-range` 设为从刻度读出的共享值轴范围。
3. 用相同的 `--area`、`--x-range`、`--y-range` 对每条端点系列各跑一次 `calc line`。每个输出 `(SVG_X, SVG_Y)` 就是对应端点圆的 `(cx, cy)`。
4. 把两个端点圆和连接线（`x1=cx_left, x2=cx_right, y1=y2=cy`）分别与两套计算点对照。

```bash
# 横向 dumbbell，3 分类，值轴 0–100，绘图区 (100,100)–(700,460)。
# 用分类索引作为 y 值：行 1 → 0.5，行 2 → 1.5，行 3 → 2.5。
python3 ${SKILL_DIR}/scripts/svg_position_calculator.py calc line \
  --data "42:0.5,55:1.5,37:2.5" --area "100,100,700,460" \
  --x-range "0,100" --y-range "0,3"
python3 ${SKILL_DIR}/scripts/svg_position_calculator.py calc line \
  --data "68:0.5,71:1.5,49:2.5" --area "100,100,700,460" \
  --x-range "0,100" --y-range "0,3"
```

**Pareto 图**——拆成降序柱加累计折线：

1. 用从刻度读出的柱轴范围，对降序的分类值跑 `calc bar`。
2. 按分类顺序预计算累计百分比。
3. 用 `0.5:cum1,1.5:cum2,...,N-0.5:cumN` 跑 `calc line`，传 `--x-range "0,N"`、右侧百分比轴作为 `--y-range`（通常 `0,100`）、并与柱图相同的 `--area`。`n - 0.5` 的偏移让每个累计点落在对应柱的中心；用 `1,2,…,N` 会把折线左移半根柱宽。
4. 分别对照柱矩形、累计折线路径和累计标记点。

**双轴折线图**——按轴拆分：

1. 分别读取左右 Y 轴的刻度范围。
2. 用各自对应的 `--y-range` 对每条系列跑一次 `calc line`；两图共用 `--x-range` 与绘图区。
3. 把每条系列的折线/路径点与对应的轴尺度对照。**绝不**把左轴尺度用到右轴系列，反之亦然。

**Bullet 图**——性能带 + 实际柱 + 目标标记，全部锚定在同一 `x_min`。各带位于**同一** y 行（它们视觉上叠在一起，而非按分类堆叠），所以对每条带各跑一次 `calc bar --horizontal`，单数据点——多分类调用会把 y 散到多行：

1. 从带边缘读值轴范围（最宽带的右边缘 = 轴上限）。
2. 对每条带运行 `calc bar --horizontal --data "<band_name>:<right_edge_value>" --area "<x_min>,<band_y>,<x_max>,<band_y+band_height>" --bar-width <band_height>`。每次调用返回位于共享 `(x_min, band_y)`、按值映射宽度的矩形。与带矩形对照。
3. 用单数据点对实际值跑 `calc bar --horizontal`，使用实际柱的内嵌绘图区（`y` 与 `bar-width` 缩小，使带仍可见）。与实际矩形对照。
4. 目标标记是一条 `<line>`，位于 `x = x_min + target/axis_max × area_width`，跨整个带高。手工计算并对照。

**Butterfly 图**——以竖直中心线 `cx` 为轴对称的横向柱：

1. 从 SVG 读值轴范围与中心线 `cx`。
2. 对每侧各跑一次 `calc bar --horizontal`，绘图区 `x_min = cx`、`x_max = cx + side_width`。右侧柱的 `x` 与 `width` 直接对应。
3. 左侧复用同一计算输出再镜像：左侧柱 `x = cx - width`，`width` 不变。与左侧矩形对照。
4. 分类 `y` 在两侧共享——确认左侧与右侧各行在相同的 `y + height/2` 上对齐。

**分组柱图**——N 条系列共用同一组 x 分类，并排而非堆叠：

1. 读取值轴范围与绘图区。
2. 计算组内间距：若有 `N` 条系列、每个分类的可视组宽度为 `W`，则每条系列柱的宽度为 `W/N`，它在组内的 x 偏移为 `(i - 1) × W/N`。从 SVG 读这些值（第一个分类的柱同时给出两者）。
3. 对每条系列各跑一次 `calc bar`，**共用** `--area` 与 `--value-range`，但每次的 `--bar-width` 设为该内宽。calc 给出的逐分类中心 X 是**组**中心；每条系列柱的实际 `x = group_center - W/2 + (i-1) × W/N`。与 SVG 对照。

**箱线图**——Q1/Q3 箱体 + 中位线 + 须线。五个量都是同一轴上的 y 值：

1. 读 y 轴范围与绘图区。对每个分类，五个值是 min / Q1 / median / Q3 / max。
2. 把每个分类的箱体（Q3 − Q1）当作合成"堆叠"段跑一次 `calc bar`，把绘图区的 `y_max` 上移到 `y_axis_top - Q1 × pixels_per_unit`（即 Q1 基线）。输出的 `y, height` 应匹配箱矩形。
3. 中位 y = `y_axis_top + (axis_max - median) × pixels_per_unit`。须端点（min、max）套用同式。分别与 SVG 的 `<line>` 的 y1/y2 和 `<rect>` 的 y/height 对照。

**甘特图**——任务柱，其中每根柱的 `x` 与 `x + width` 是时间线轴上的起止位置：

1. 读时间线刻度位置（表头行每日期单位的 x 坐标）。pixels-per-unit = `(x_unit_n - x_unit_1) / (n - 1)`。
2. 对每个任务的 `start_index:row_y` 跑一次 `calc line`——输出 `SVG_X` 就是柱的 `x`。再对 `end_index:row_y` 跑一次——输出 `SVG_X` 就是 `x + width`。相减得宽度。
3. 把每根任务矩形的 `(x, width)` 与算出的起止对照。行 y 可直接读出（分类不由数值驱动）。

**瀑布图**——通过累计总额相连的悬浮柱。每根柱的顶边与底边对应同一值轴上的两个点（`cum_before`、`cum_after`）：

1. 读 y 轴刻度范围与绘图区；按分类顺序算累计（`cum[0] = base_value`；增量 `cum[i] = cum[i-1] + delta[i]`；减量 `cum[i] = cum[i-1] - delta[i]`；合计重置为 delta）。
2. 构造两条虚拟系列：`top[i] = max(cum_before, cum_after)`、`bot[i] = min(cum_before, cum_after)`。用相同的 `--area`、`--bar-width`、`--value-range` 跑两次 `calc bar`。`top` 跑的 `Y` 即柱的 `y`；该索引的 `height = bot.Y - top.Y`。
3. 把每根瀑布柱的 `(x, y, width, height)` 与算出的这一对值对照。连接线应从 `(x + width, top_or_bot[i].Y)` 到 `(x_next, top_or_bot[i+1].Y)`，并落在对应的共享累计值上。
4. 合计柱（首尾满高的）用 `bot = 0`，化归为标准 `calc bar` recipe。

**气泡图 / 象限气泡散点**——计算器部分支持：

1. 用 `calc line` 从 X/Y 数值与轴刻度校准气泡中心（`cx/cy`）。
2. 仅当 `design_spec.md`、`spec_lock.md` 或 SVG 注释里声明了尺寸比例（如 `radius = sqrt(value) * k` 或显式的最小/最大半径映射）时才校准半径。
3. 若尺寸比例缺失，在收据里记 `radius=manual (scale missing)` 并人工检视相对排序。

**进度条 / 仪表盘 / 漏斗 — 公式验证**（无需调用 calc）：

- 进度条：`fill_width = value / max × track_width`。从 SVG 读 `value`、`max`、`track_width`；算出来与填充矩形的 `width` 对照。
- 仪表盘：`needle_angle = start_angle + value / max × sweep_angle`。从 SVG 的弧形路径读 `start_angle` 与 `sweep_angle`（如半圆 `start_angle=-180`、`sweep_angle=180`）。与指针 `transform="rotate(α ...)"` 的值（最常见形态）对照；若指针画成显式的线/路径，则与端点 `(cx + L·cos α, cy + L·sin α)` 对照。
- 漏斗：每个梯形的 `top_width = prev.bottom_width`、`bottom_width = top_width × next_value / curr_value`。逐段走查来验证：对段 `i`，`(top_left_x, top_right_x) → bottom_x_inset = (top_width - bottom_width) / 2`。第一段的顶宽取自设计的外框。
- 收据应引用公式和算得的值（如 `formula=value/max×track_width=0.92×700=644px`，或 `formula=600×850/1000=510 bottom width`）。

**Sankey / 热力图 / 树图 — 人工验证：**

- Sankey：没有节点堆叠、连线路由或流宽归一化的版式模型。校验连接宽度与流值成比例、节点两侧总额一致（入 = 出）。
- 热力图：单元格位置是固定网格（不由数值驱动）；由数值驱动的是值到颜色的分箱。校验每个单元格的颜色落在与该数字匹配的箱内、且高/低极值使用图例的高/低颜色。
- 树图：矩形面积反映值的比例，但递归 squarify 版式没有对应的计算器。校验顶层格的 `width × height ≈ total_area × value / sum(values)`，且嵌套格之和等于其父格。

---

## Step 3：逐页收据

对 Step 1 清单中的每页输出一行。收据条数**必须**等于 Step 1 清单长度——这就是收尾的物证。

```
verify-charts: 03_market_share.svg | type=bar | mode=direct-calc | scale=0-100 (from ticks) | calc=ran | svg=updated
verify-charts: 07_growth.svg | type=line | mode=direct-calc | scale=0-120 (from ticks) | calc=ran | svg=unchanged (already accurate)
verify-charts: 11_share_split.svg | type=pie | mode=direct-calc | scale=N/A | calc=ran | svg=updated | marker=added (was missing)
verify-charts: 14_revenue_mix.svg | type=stacked-bar | mode=decomposable-calc | scale=0-200 (from ticks) | calc=ran×3 | svg=updated (per stacked recipe)
verify-charts: 15_unit_economics.svg | type=stacked-area | mode=manual-verify | scale=N/A | reason=percent-stacked, recipe does not apply
verify-charts: 16_before_after.svg | type=dumbbell | mode=decomposable-calc | scale=0-100 (from ticks) | calc=ran×2 | svg=unchanged
verify-charts: 17_drivers_pareto.svg | type=pareto | mode=decomposable-calc | scale=left 0-80 / right 0-100 | calc=ran×2 | svg=updated
verify-charts: 18_market_bubbles.svg | type=bubble | mode=partial-calc | xy=ran | radius=manual (scale missing) | svg=unchanged
verify-charts: 20_quota_attainment.svg | type=bullet | mode=decomposable-calc | scale=0-120 (from ticks) | calc=ran×3 (bands+actual+target) | svg=updated
verify-charts: 21_inflow_outflow.svg | type=butterfly | mode=decomposable-calc | scale=0-500 (from ticks) | calc=ran×2 + mirror | svg=unchanged
verify-charts: 22_profit_bridge.svg | type=waterfall | mode=decomposable-calc | scale=0-500 (from ticks) | calc=ran×2 (top/bot) | svg=updated
verify-charts: 23_quarterly_progress.svg | type=progress | mode=formula-verify | formula=68/100×800=544px | svg=unchanged
verify-charts: 24_capacity_gauge.svg | type=gauge | mode=formula-verify | formula=-180+72/100×180=-50.4° | svg=updated
verify-charts: 25_conversion_funnel.svg | type=funnel | mode=formula-verify | formula=600×850/1000=510 (seg2 bottom width) | svg=unchanged
verify-charts: 26_regional_compare.svg | type=grouped-bar | mode=decomposable-calc | scale=0-500 (from ticks) | calc=ran×3 | svg=updated
verify-charts: 27_release_plan.svg | type=gantt | mode=decomposable-calc | scale=Week1-Week24 (24 ticks, 40px/unit) | calc=ran×2 (start/end) | svg=unchanged
verify-charts: 28_score_distribution.svg | type=boxplot | mode=decomposable-calc | scale=0-100 (from ticks) | calc=ran×4 (Q1/Q3/whiskers) | svg=updated
verify-charts: 19_flow.svg | type=sankey | mode=manual-verify | link widths consistent with values | svg=unchanged
```

---

## 校验之后

继续进入后期处理与导出（[SKILL.md Step 7](../SKILL.md)）：

```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
```
