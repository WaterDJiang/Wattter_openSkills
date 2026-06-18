# 必须组件契约

组件库做减法：所有 deck 生成只围绕 6 个内容组件组织。其他看起来像新组件的东西，先归入这 6 个组件的变体；只有无法归入且复用价值明确时，才新增组件类别。

本文件是语义契约，不改变现有 UI。已有 class、layout 和风格组件继续保留；生成新 deck 时用下面 6 个组件作为选择入口。

可直接使用的 CSS class 已在 `assets/core/components.css` 中实现。它们会随 `base.css` 一起进入生成结果，不需要额外复制文件。

## 1. `title-block` 标题组

**解决什么**：这一页到底讲什么。

**包含**：kicker / title / subtitle / lead / meta。

**现有映射**：
- Editorial：`.kicker` + `.h-hero/.h-xl/.h-md` + `.lead` + `.meta-row`
- Swiss：`.t-cat/.h-hero/.h-xl/.t-body` 等标题角色
- Linear：`.kicker` + `.h-hero/.h-xl` + `.lead` + `.meta-row`

**规则**：每页只能有一个主 `title-block`。如果一页需要两个主标题，通常说明应该拆页。

```html
<div class="title-block hero">
  <div class="title-kicker">SYSTEM SHIFT</div>
  <h1 class="title-heading fit-safe-text">把复杂工作变成可运行的系统</h1>
  <p class="title-lead">标题组负责定义本页唯一主命题，后续组件只服务这个命题。</p>
  <div class="title-meta"><span>01</span><span>Operating Model</span></div>
</div>
```

## 2. `figure-frame` 图像/截图框

**解决什么**：放图片、产品截图、网页截图、图像证据，并提供说明。

**包含**：image / screenshot / caption / source / annotation。

**现有映射**：
- Editorial：`.tile`、`.frame-img`、`.frame-cap`、`.img-slot`
- Swiss：`.swiss-img-split`、`.swiss-img-grid`、`.swiss-img-caption`、`.image-hero-*`
- Linear：`.linear-window`、`.linear-code`、产品界面截图容器

**规则**：截图标注、图片对比、产品窗口都属于 `figure-frame` 变体，不新增 `screenshot-callout` 一类组件。

```html
<figure class="figure-frame">
  <div class="figure-media" style="height:42vh">
    <img src="images/01-product.png" alt="产品界面截图">
  </div>
  <figcaption class="figure-caption">
    <strong>产品界面</strong>
    <span>Source · 2026</span>
  </figcaption>
  <p class="figure-note">截图说明只写必要上下文，不写成长段正文。</p>
</figure>
```

## 3. `metric-block` 指标块

**解决什么**：表达数字、变化、结果、关键 KPI。

**包含**：label / number / unit / delta / note。

**现有映射**：
- Editorial：`.stat`、`.stat-card`
- Swiss：`.kpi-*`、`.num-mega`、`.spec-kpi`、`.image-hero-stats`
- Linear：`.linear-card .nb/.label/.copy`

**规则**：数字必须带口径或解释；没有口径时，用 `evidence-strip` 补充来源、时间范围或计算方式。

```html
<div class="metric-block">
  <div class="metric-label">Cycle Time</div>
  <div class="metric-value">-34<span class="metric-unit">%</span></div>
  <div class="metric-delta">QoQ</div>
  <p class="metric-note">从需求进入到合并，关键等待时间被压缩。</p>
</div>
```

## 4. `comparison-block` 对比块

**解决什么**：表达 A vs B、过去 vs 现在、方案 1 vs 方案 2、优先级取舍。

**包含**：2-4 个对象 / 维度 / 差异 / 结论。

**现有映射**：
- Editorial：`.rowline`、A/B 版式、pillar 变体
- Swiss：`.duo-compare`、`.split-half`、`.sub-grid-3-2`
- Linear：`.linear-row` 列表、issue 优先级、panel 对照

**规则**：`decision-matrix`、`risk-register`、定价表、方案表都先归入 `comparison-block`；不要为每种业务表单新增组件。

```html
<div class="comparison-block" data-cols="3">
  <article class="comparison-item">
    <div class="comparison-label">Option A</div>
    <h3 class="comparison-title">继续手工协作</h3>
    <p class="comparison-body">成本低，但上下文丢失和等待时间持续累积。</p>
    <div class="comparison-result">Risk · High</div>
  </article>
  <article class="comparison-item accent">
    <div class="comparison-label">Option B</div>
    <h3 class="comparison-title">系统化工作流</h3>
    <p class="comparison-body">把反馈、任务、执行和复盘放入同一闭环。</p>
    <div class="comparison-result">Recommend</div>
  </article>
  <article class="comparison-item">
    <div class="comparison-label">Option C</div>
    <h3 class="comparison-title">外包执行</h3>
    <p class="comparison-body">短期吞吐增加，但知识沉淀仍然断裂。</p>
    <div class="comparison-result">Limited</div>
  </article>
</div>
```

## 5. `sequence-block` 序列块

**解决什么**：表达步骤、流程、时间线、路线图、行动清单。

**包含**：step / order / state / owner / next action。

**现有映射**：
- Editorial：`.pipeline`、`.step`、`.timeline`
- Swiss：`.timeline-v`、`.timeline-h`、`.loop-diagram`、`.stacked-ledger`
- Linear：`.linear-timeline`、roadmap、agent workflow、issue 状态流

**规则**：`action-checklist`、roadmap、流程图、执行计划都属于 `sequence-block` 变体。能按时间或顺序读，就不要新增组件。

```html
<div class="sequence-block" data-orientation="horizontal" data-cols="3">
  <div class="sequence-step">
    <span class="sequence-index">01</span>
    <div>
      <h3 class="sequence-title">收集信号</h3>
      <p class="sequence-body">把客户反馈、内部阻塞和产品数据收束到同一个入口。</p>
      <div class="sequence-meta">Input</div>
    </div>
  </div>
  <div class="sequence-step">
    <span class="sequence-index">02</span>
    <div>
      <h3 class="sequence-title">生成任务</h3>
      <p class="sequence-body">明确 owner、优先级、验收标准和执行路径。</p>
      <div class="sequence-meta">Plan</div>
    </div>
  </div>
  <div class="sequence-step">
    <span class="sequence-index">03</span>
    <div>
      <h3 class="sequence-title">闭环复盘</h3>
      <p class="sequence-body">保留决策依据，让下一轮执行更快。</p>
      <div class="sequence-meta">Review</div>
    </div>
  </div>
</div>
```

## 6. `evidence-strip` 证据/注释条

**解决什么**：让信息可信，说明来源、口径、限制和适用范围。

**包含**：source / date / sample / caveat / method。

**现有映射**：
- Editorial：`.callout-src`、`.meta-row`、figure caption
- Swiss：`.t-meta`、caption、source row
- Linear：`.meta-row`、窗口头、issue key、command context

**规则**：数据页、观点页、案例页都应该有证据或口径入口。不要把来源说明塞进正文长段落。

```html
<div class="evidence-strip">
  <span class="evidence-item"><b>Source</b><span>Internal dashboard</span></span>
  <span class="evidence-item"><b>Window</b><span>2026 Q2</span></span>
  <span class="evidence-item"><b>Sample</b><span>128 tasks</span></span>
  <p class="evidence-note">口径：只统计已完成且有完整状态流转记录的任务。</p>
</div>
```

## 不再新增的顶层组件

这些名称可以作为变体说明，但不要作为新的顶层组件加入组件库：

- `decision-matrix` → `comparison-block`
- `risk-register` → `comparison-block`
- `pricing-table` → `comparison-block`
- `screenshot-callout` → `figure-frame`
- `roadmap-lanes` → `sequence-block`
- `action-checklist` → `sequence-block`
- `source-strip` → `evidence-strip`
- `persona-card` → 根据用途归入 `comparison-block` 或 `figure-frame`
- `architecture-stack` → 根据表达方式归入 `sequence-block` 或 `comparison-block`

## 新增组件判断

新增组件类别必须同时满足：

1. 不能自然归入 6 个必须组件。
2. 至少能覆盖 3 种不同 deck 场景。
3. 能在 editorial / swiss / linear 三种风格里换皮，而不是绑定某一种审美。
4. 有稳定结构和可校验 class，不依赖每页 inline style。

否则，只能作为 6 个组件之一的变体写入对应风格的 layouts 或 examples。
