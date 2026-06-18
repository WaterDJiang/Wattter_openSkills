# Layouts · 瑞士国际主义（Swiss Style）

22 个登记版式（S01-S22）+ 1 个扩展组件（S08 + MapLibre）+ 2 个 ASCII 变体。**严格登记，禁止发明**。

> **生成前必读** [`swiss-layout-lock.md`](swiss-layout-lock.md) — 硬约束、禁止清单、图片规则全在里面。

---

## 通用约束（所有 S01-S22 适用）

- 每个 `<section class="slide">` 必写 `data-layout="Sxx"` 或 `SWISS-COVER-ASCII` / `SWISS-CLOSING-ASCII`
- 顶部中文标题**左对齐贴近左上内容轴**（`S03/S09/S10` / ASCII 封面/收尾除外）
- 主体 padding 必须为 0；页面安全边距来自 `.slide` 的 `--slide-pad`，`.canvas-card` 只负责 100% 内容框
- 高密度内容页在 `.canvas-card` 内包 `.fit-shell`；长标题加 `.fit-safe-text`，出现 `内容过密` 标记时删减/拆页/换低密度版式
- kicker 必须在 title 上方（`flex-direction:column;gap:1.4vh`）
- 大字号双约束 `font-size:min(Xvw, Yvh)`，Y ≥ X × 1.6
- 主内容最低处必须停在 `--nav-safe-bottom:8vh` 上方
- 每个 `<section>` 写 `data-animate="..."`，命中下方 22 个 recipe 名之一

---

## S01 · Index Cover · 封面 / 章节首页

**用途**：纯文字封面 / 章节首页 / 主题宣言  
**关键 class**：`slide.accent` `.ascii-bg` `.chrome-min` `min(11.6vw,19vh)`  
**主题要求**：首页必须让所选主题色成为主视觉。无论使用预设主题还是自定义品牌色，封面都应大面积呈现 `--accent`；不要用 `slide grey` / `slide light` 做 Swiss 首页。
**动效**：`hero`（ASCII 呼吸 + fade-up 序列）

```html
<section class="slide accent" data-layout="S01" data-animate="hero">
  <div class="canvas-card">
    <canvas class="ascii-bg" data-ascii="SWISS"></canvas>
    <div class="chrome-min"><div class="l">[必填] Deck 标题</div><div class="r">SS · YY.MM.DD · 01/NN</div></div>
    <div class="fit-shell" style="display:grid;grid-template-rows:auto 1fr auto;gap:2.6vh">
      <div class="t-meta">SECTION EN</div>
      <h1 class="fit-safe-text" style="font-weight:200;font-size:min(11.6vw,19vh);line-height:.94;letter-spacing:-.025em">
        [必填] 主标题<br/><span style="font-style:italic;font-weight:300">italic</span>
      </h1>
      <div data-anim="bottom" style="border-top:1px solid rgba(255,255,255,.22);padding-top:2vh">
        <div class="lead">副标引子</div>
        <div>meta · → swipe</div>
      </div>
    </div>
  </div>
</section>
```

---

## S02 · Vertical Timeline + KPI · 纵向时间轴

**用途**：演化对比 / 年代变迁 / 版本迭代（2-5 个量化节点）  
**关键 class**：`.timeline-v` `.tl-node` `.timeline-v::before`（竖虚线轴） `.kpi-row-4` `.kpi-cell`  
**动效**：`progression`（节点 dot pop + multi scale + KPI stagger）

```html
<section class="slide" data-layout="S02" data-animate="progression">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">[章节] · 演化</div><div class="r">04/NN</div></div>
    <h2 class="h-xl-zh">演化对比标题</h2>
    <div class="timeline-v">
      <div class="tl-node">
        <span class="dot"></span>
        <span class="yr">2023</span>
        <span class="multi">1×</span>
        <p class="desc">Prompt Engineering Era</p>
      </div>
      <!-- 4-5 个 tl-node -->
    </div>
    <div class="kpi-row-4">
      <div class="kpi-cell"><span class="kpi-thin-sm">4</span><span class="t-meta">SKILLS</span></div>
      <!-- 4 个 -->
    </div>
  </div>
</section>
```

---

## S03 · Split Statement · 极简陈述

**用途**：中心论点 / 章节起始 / 口号  
**关键 class**：`.slide.split` `.split-half` `.half.b-grey`  
**动效**：`statement`（左右两半屏顺序入场）  
**特殊**：标题可居中

```html
<section class="slide split" data-layout="S03" data-animate="statement">
  <div class="canvas-card">
    <div class="split-half">
      <div class="half" style="padding:5.6vh 3.6vw 4.4vh">
        <h2 class="h-hero" style="font-weight:200">[必填] 一句陈述</h2>
        <span class="t-meta">— Statement 03</span>
      </div>
      <div class="half b-grey" style="padding:5.6vh 3.6vw 4.4vh">右侧注脚/上下文</div>
    </div>
  </div>
</section>
```

---

## S04 · Six Cells · 六格定义

**用途**：6 个并列概念定义  
**关键 class**：`.sub-grid-3-2` `.sub-card` `.nb-corner`  
**动效**：`grid-reveal`（6 卡 z 形延迟）

```html
<section class="slide" data-layout="S04" data-animate="grid-reveal">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <h2 class="h-xl-zh fit-safe-text">六格定义标题</h2>
    <div class="sub-grid-3-2 fit-shell">
      <div class="sub-card">
        <span class="nb-corner">01</span>
        <i data-lucide="square-stack"></i>
        <h4 class="ttl">Skill File</h4>
        <p class="desc">...</p>
      </div>
      <!-- 6 个 -->
    </div>
  </div>
</section>
```

---

## S05 · Three Layers · 三层架构

**用途**：3 个对等概念 / 三层堆叠  
**关键 class**：`.stack-row` `.stack-block.b-grey/.b-accent/.b-ink` `.layer-ttl` `.layer-tag`  
**动效**：`stack-build`（中间先入 → 上下推入）

```html
<section class="slide" data-layout="S05" data-animate="stack-build">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <h2 class="h-xl-zh">三层架构标题</h2>
    <div class="stack-row">
      <div class="stack-block b-grey">LAYER 01 + 图标 + 标题 + 描述</div>
      <div class="stack-block b-accent">LAYER 02 + ...</div>
      <div class="stack-block b-ink">LAYER 03 + ...</div>
    </div>
  </div>
</section>
```

---

## S06 · KPI Tower · 不等高柱状 KPI

**用途**：4 项可比量化数据的高度对比  
**关键 class**：`.bar-towers` `.bar-tower` `.body-block.h-1/2/3/4` `.body-block.b-accent`  
**动效**：`measure-up`（tower scaleY 0→1 + cap pop）

```html
<section class="slide" data-layout="S06" data-animate="measure-up">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <div class="grid-2-7-5">
      <div><span class="t-cat">KPI METRICS</span><h2 class="h-xl">标题</h2></div>
      <div>右侧说明</div>
    </div>
    <div class="bar-towers">
      <div class="bar-tower">
        <div class="cap"><i data-lucide="layers"></i></div>
        <div class="body-block h-3"><span class="lbl">Skills</span><span class="nb">90<small>K</small></span><span class="sub">说明</span></div>
      </div>
      <!-- 4 个 body-block.h-1/2/3/4 -->
    </div>
  </div>
</section>
```

---

## S07 · Horizontal Bar · 横向条形图

**用途**：5-10 项排名比较 / 占比对比  
**关键 class**：`.h-bar-chart` `.row-lbl` `.row-track` `.row-fill` `.row-fill.accent`  
**动效**：`bar-grow`（hairline scaleX + bar width 0→target）

```html
<section class="slide" data-layout="S07" data-animate="bar-grow">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <h2 class="h-xl-zh">横向条形图标题</h2>
    <div class="h-bar-chart">
      <div>
        <span class="row-lbl">标签</span>
        <div class="row-track"><div class="row-fill" style="width:84%"></div></div>
        <span class="row-val">84</span>
      </div>
      <!-- 5-10 行 -->
    </div>
  </div>
</section>
```

---

## S08 · Duo Compare · 双轨对照

**用途**：Before/After / A vs B 对比  
**关键 class**：`.duo-compare` `.col` `.col.accent` `.vrule` `.col-list li::before`  
**动效**：`duo-mirror`（vrule scaleY + 左右镜像入场）  
**扩展**：可加 Map 组件，详见 [swiss-map-component.md](swiss-map-component.md)

```html
<section class="slide" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <h2 class="h-xl-zh">对比标题</h2>
    <div class="duo-compare">
      <div class="col">
        <span class="col-tag"><span class="num">A</span>BEFORE</span>
        <h2 class="col-ttl">交给模型</h2>
        <p class="col-desc">说明</p>
        <ul class="col-list"><li>要点</li>...</ul>
      </div>
      <span class="vrule"></span>
      <div class="col accent">
        <span class="col-tag"><span class="num">B</span>AFTER</span>
        <h2 class="col-ttl">交给代码</h2>
        <p class="col-desc">说明</p>
        <ul class="col-list"><li>要点</li>...</ul>
      </div>
    </div>
  </div>
</section>
```

---

## S09 · Dot Matrix Statement · 点阵宣言

**用途**：第二张陈述页 / 章节切换 / 视觉透气页  
**关键 class**：`.h-hero`（200） `.dot-mat` `.ring-mat` `.cross-mat`  
**动效**：`matrix-statement`（逐行入 + mask-position 推动）  
**特殊**：标题可居中

```html
<section class="slide" data-layout="S09" data-animate="matrix-statement">
  <div class="canvas-card">
    <span class="ring-mat" style="left:5vw;bottom:5vh"></span>
    <h1 class="h-hero" style="font-weight:200;align-self:center;text-align:center">Build a thin harness.<br/>Write fat skills.<br/>Codify everything.</h1>
    <span class="dot-mat" style="right:0;top:0"></span>
  </div>
</section>
```

---

## S10 · Split Closing · 收尾

**用途**：deck 终结收束（每 deck 仅 1 次）  
**关键 class**：`.slide.split` `.half.b-accent` `.ascii-bg`  
**动效**：`split-statement`  
**特殊**：标题可居中

```html
<section class="slide split" data-layout="S10" data-animate="split-statement">
  <div class="canvas-card">
    <div class="split-half">
      <div class="half b-accent" style="position:relative">
        <canvas class="ascii-bg"></canvas>
        <div class="chrome-min">...</div>
        <div class="t-meta">MANIFESTO</div>
        <h2 style="font-weight:200;font-size:min(8vw,14vh)">Build a model.<br/>Run forever.</h2>
      </div>
      <div class="half" style="padding:5.6vh 3.6vw 4.4vh">
        <div class="chrome-min">TAKEAWAYS · 03 RULES</div>
        <div>3 条 takeaway（最后 1 条用 var(--accent)）</div>
      </div>
    </div>
  </div>
</section>
```

---

## S11 · Horizontal Timeline · 横向时间线

**用途**：多步骤流程（4-7 步）/ 时间演进  
**关键 class**：`.timeline-h` `.th-node` `.th-node .dot`（8px 实心圆）`.label`  
**动效**：`timeline-walk`（dot scale + label 错峰）

```html
<section class="slide" data-layout="S11" data-animate="timeline-walk">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <h2 class="h-xl-zh">横向演化</h2>
    <div class="timeline-h">
      <div class="tl-row">
        <div class="th-node"><div class="dot"></div><div class="label"><span class="yr">2023</span><span class="name">Investigate</span></div></div>
        <!-- 4-7 个 th-node -->
      </div>
    </div>
  </div>
</section>
```

---

## S12 · Manifesto + Ink Banner · 宣言 + 通栏

**用途**：阶段性结论 / 章节封底  
**关键 class**：`.manifesto-top` `.ink-banner-full`（`margin:0 -5vw -4.4vh` 取消父级 padding）  
**动效**：`manifesto`（大字错峰 + ink 条 scaleX）

```html
<section class="slide" data-layout="S12" data-animate="manifesto">
  <div class="canvas-card">
    <div class="manifesto-top">
      <span class="t-cat">FORM & FOUND</span>
      <h2 style="font-weight:200">标题</h2>
      <p>右侧短段说明</p>
    </div>
    <div class="ink-banner-full" style="background:var(--ink);color:var(--paper);margin:0 -5vw -4.4vh;padding:5vh 5vw">
      反白短句 + lucide 图标矩阵
    </div>
  </div>
</section>
```

---

## S13 · Three Forces Cards · 三力卡片小报

**用途**：3 个对等概念深化  
**关键 class**：`.grid-2-8-4` `.hero-ink-col` `.card-fill` `.force-num`（9.2vw accent 色）  
**动效**：`three-forces`

```html
<section class="slide" data-layout="S13" data-animate="three-forces">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <div class="grid-2-8-4">
      <div class="hero-ink-col">
        <span class="t-cat">THREE FORCES</span>
        <h2 class="h-xl">4 行宣言</h2>
        <span class="dot-mat"></span>
      </div>
      <div class="stack-cards">
        <article class="force-card">
          <span class="force-num">01</span>
          <div><h4>标题</h4><p>双列描述</p></div>
        </article>
        <!-- 3 张 -->
      </div>
    </div>
  </div>
</section>
```

---

## S14 · Loop Form · 闭环流程图

**用途**：自学闭环 / 自动化循环（3-5 步循环）  
**关键 class**：`.loop-diagram` `.loop-steps` `.loop-svg` `.step.accent-top`  
**动效**：`loop-form`（左侧步骤纵向 + 右侧环 stroke-dashoffset 描线）  
**硬规则**：SVG 不含 `<text>` 可见标签

```html
<section class="slide" data-layout="S14" data-animate="loop-form">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <div class="grid-2-8-4">
      <div class="loop-steps">
        <div class="step accent-top"><span class="step-nb">01</span><span class="step-title">Plan</span><p>...</p></div>
        <!-- 4 步 -->
      </div>
      <div class="loop-diagram">
        <svg class="loop-svg" viewBox="0 0 400 400">
          <circle cx="200" cy="200" r="180" stroke="..." fill="none"/>
          <!-- 4 节点 + 箭头 + 中心 LOOP -->
        </svg>
      </div>
    </div>
  </div>
</section>
```

---

## S15 · Matrix + Hero Stat · 矩阵 + 大字底注

**用途**：8-12 项同类展示 + 总数据收束  
**关键 class**：`.matrix-fill` `.matrix-cell`（`.card-fill` 灰底） `.hero-stat-bottom` `.kpi-thin`  
**动效**：`matrix-fill`（12 格对角线波 stagger + 巨数 count-up）  
**图片规则**：多图同组统一 `21:9`（`.frame-img.r-21x9` + `data-image-slot="s15-grid-21x9"`）

```html
<section class="slide" data-layout="S15" data-animate="matrix-fill">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <h2 class="h-xl-zh fit-safe-text" style="margin-bottom:9vh">标题</h2>
    <div class="matrix-fill fit-shell" data-anim="up" style="display:grid;grid-template-columns:repeat(4,1fr);gap:1.4vh 1.4vw">
      <article class="card-fill matrix-cell" style="height:12vh;padding:2vh"><h4>...</h4></article>
      <!-- 12 卡 -->
    </div>
    <div class="hero-stat-bottom" style="margin-top:auto">
      <span class="kpi-thin">20,000</span>
      <span class="t-meta">TOTAL SKILLS</span>
    </div>
  </div>
</section>
```

---

## S16 · Multi-card Brief · 微卡小报

**用途**：6 项轻量短讯 / tip 集合  
**关键 class**：`.brief-grid` `.brief-card`（`.card-fill` 灰底） `.brief-card.is-accent`（单焦点）  
**动效**：`field-notes`（6 卡 z 形乱序）  
**图片规则**：多图同组统一 `21:9`

```html
<section class="slide" data-layout="S16" data-animate="field-notes">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <h2 class="h-xl-zh fit-safe-text" style="margin-bottom:9vh">标题</h2>
    <div class="brief-grid fit-shell" style="display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:1.4vh 1.4vw">
      <article class="card-fill brief-card" style="padding:2.4vh 1.6vw"><h4>主文</h4><p>小字</p></article>
      <!-- 6 卡 -->
    </div>
  </div>
</section>
```

---

## S17 · System Diagram · 同心圆系统图

**用途**：三层嵌套（core / middle / outer）  
**关键 class**：`.system-diagram` `.sys-svg`  
**动效**：`system-diagram`（同心圆 scale 入 + 注释列）  
**硬规则**：SVG 不含 `<text>` 可见标签

```html
<section class="slide" data-layout="S17" data-animate="system-diagram">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <div class="grid-2-7-5">
      <div>
        <span class="t-cat">SYSTEM</span>
        <h2 class="h-xl">层级标题</h2>
        <p>说明</p>
      </div>
      <div class="system-diagram">
        <svg viewBox="0 0 400 400">
          <circle cx="200" cy="200" r="60" fill="var(--ink)"/>   <!-- core -->
          <circle cx="200" cy="200" r="120" fill="var(--grey-1)"/>
          <circle cx="200" cy="200" r="180" fill="none"/>
        </svg>
      </div>
    </div>
    <div class="grid-3">
      <div><span class="t-cat">01 CORE</span><p>...</p></div>
      <div><span class="t-cat">02 MIDDLE</span><p>...</p></div>
      <div><span class="t-cat">03 OUTER</span><p>...</p></div>
    </div>
  </div>
</section>
```

---

## S18 · Why Now · 三列递进 + 巨数

**用途**：三论点 + 各自支撑数据  
**关键 class**：`.why-now-grid` `.why-col` `.why-num-bottom`（8.4vw weight 200）  
**动效**：`why-now`

```html
<section class="slide" data-layout="S18" data-animate="why-now">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <h2 class="h-xl-zh">为什么是现在</h2>
    <div class="why-now-grid grid-3">
      <div class="why-col">
        <span class="t-cat">SIGNAL 01</span>
        <h4>论点 1</h4>
        <p>描述</p>
        <span class="why-num-bottom">87%</span>
      </div>
      <div class="why-col accent"><span class="why-num-bottom">12×</span></div>
    </div>
  </div>
</section>
```

---

## S19 · Four Cards · 四列均分卡

**用途**：4 项等权特性  
**关键 class**：`.four-cards` `.fc-col`；顶部 80px 高 accent 蓝线  
**动效**：`four-cards`（顶线 scaleX 0→1 + 4 卡下推）

```html
<section class="slide" data-layout="S19" data-animate="four-cards">
  <div class="canvas-card">
    <div data-anim="line">
      <div style="height:80px;background:var(--accent)"></div>
      <h2 class="h-xl-zh">大字双行标题</h2>
    </div>
    <div class="grid-4" style="margin-top:9vh">
      <div class="fc-col">
        <span class="t-meta">— 01 / SLASH</span>
        <h4>特性 1</h4>
        <p>段落描述</p>
      </div>
      <!-- 4 列 -->
    </div>
  </div>
</section>
```

---

## S20 · Stacked KPI Ledger · 纵向账单 KPI

**用途**：4-6 行核心数据账单  
**关键 class**：`.stacked-ledger` `.ledger-row`（`border-bottom:1px solid var(--border-subtle)`） `.ledger-num`（限高 `min(13vw,16vh)`）  
**中文/长标签**：数字用 `.ledger-num`；中文短词用 `.ledger-num ledger-num-text`；长编号/长标签用 `.ledger-num ledger-num-sm`。不要用 inline font-size 覆盖。
**动效**：`stacked-ledger`

```html
<section class="slide" data-layout="S20" data-animate="stacked-ledger">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <h2 class="h-xl-zh fit-safe-text">账单式标题</h2>
    <div class="stacked-ledger fit-shell" data-anim="ledger">
      <div class="ledger-row">
        <span class="ledger-num">$48M</span>
        <span class="ledger-label">标签</span>
        <i data-lucide="trending-up" class="ledger-icon"></i>
      </div>
      <div class="ledger-row">
        <span class="ledger-num ledger-num-text">三可</span>
        <span class="ledger-label">中文短标签示例</span>
        <i data-lucide="users" class="ledger-icon"></i>
      </div>
      <!-- 4-6 行 -->
    </div>
  </div>
</section>
```

---

## S21 · Tech Spec Sheet · 规格说明书

**用途**：产品规格 / benchmark / 性能基线  
**关键 class**：`.spec-title-col` `.spec-kpi-grid` `.spec-bars` `.vbar`  
**动效**：`tech-spec`（KPI 顶线 scaleX + 巨数 pop + 竖线 scaleY）

```html
<section class="slide" data-layout="S21" data-animate="tech-spec">
  <div class="canvas-card">
    <div class="chrome-min">...</div>
    <div data-anim="up">
      <div class="grid-2-7-5">
        <div class="spec-title-col">
          <h2 class="h-xl">4 行大标题</h2>
          <p>说明</p>
        </div>
        <div class="spec-kpi-grid grid-3">
          <div class="spec-kpi"><span class="t-meta">CPU</span><span class="kpi-num">3.4<small>×</small></span></div>
          <!-- 3 KPI -->
        </div>
      </div>
    </div>
    <div data-anim="hero" style="margin-top:auto;display:grid;grid-template-columns:7fr 5fr;gap:3vw">
      <div class="bottom-hero">
        <span class="kpi-thin" style="font-size:min(20vw,28vh)">99.97%</span>
        <span class="t-meta">Yearly goal</span>
        <div class="grid-3">
          <span class="tag">LOW LATENCY</span>
          <span class="tag">SLA</span>
          <span class="tag">MULTI-REGION</span>
        </div>
      </div>
      <div>
        <span class="t-meta">MP-XX · 21/NN</span>
        <div data-anim="bars" class="spec-bars">
          <div class="vbar" style="background:var(--grey-1);height:30%"></div>
          <!-- 9 根竖线 -->
        </div>
      </div>
    </div>
  </div>
</section>
```

---

## S22 · Image Hero · 图文混排封面

**用途**：案例展示 / 产品图 + 数据落地 / 章节封面带图  
**关键 class**：`.image-hero` `.image-hero-body` `.image-hero-stats` `.hero-overlay-block`  
**动效**：`image-hero`（img scale 1.06→1 + 白块 scaleX + 3 KPI 顶线画出）  
**图片规则**（强制）：
- 主图必须 `21:9`（`data-image-slot="s22-hero-21x9"`）
- `object-fit:cover;object-position:center 35%`（**禁止 `top center`**）
- 关键主体放中央安全区

```html
<section class="slide" data-layout="S22" data-animate="image-hero">
  <div class="canvas-card" style="padding:0;display:flex;flex-direction:column;overflow:hidden">
    <div data-anim="img" style="position:relative;flex:0 0 60%;overflow:hidden;background:var(--grey-1)">
      <img src="images/22-product-scene.png" data-image-slot="s22-hero-21x9" alt="..."
           style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 35%">
      <div class="chrome-min" style="position:absolute;top:0;left:0;right:0;color:rgba(255,255,255,.9);padding:5.6vh 5vw 0">
        <div class="l">Section · Case</div><div class="r">22/NN</div>
      </div>
      <div data-anim="title-block" class="hero-overlay-block">
        <div class="h-title">Image<br>Evidence</div>
      </div>
    </div>
    <div data-anim="kpi" class="image-hero-body">
      <div>1-2 行解释（max-width:48ch）</div>
      <div class="image-hero-stats">
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">Metric 01</div><div>12×</div><p class="body-sm">...</p></div>
        <!-- 3 列 -->
      </div>
    </div>
  </div>
</section>
```

---

## ASCII 变体（封面 / 收尾 专用）

仅 S01（封面）和 S10（收尾）可用的 ASCII 呼吸场变体。与 S01/S10 的区别：使用全屏 ASCII canvas 渲染 swiss 主题字符。

```html
<section class="slide accent" data-layout="SWISS-COVER-ASCII" data-animate="hero">
  <!-- 同 S01 但 ascii-bg 覆盖全屏 -->
</section>
```

---

## 完整类名速查（22 个版式 + 装饰）

| 类别 | 类名 | 用途 |
|---|---|---|
| 标题 | `.h-hero` / `.h-hero-zh` / `.h-xl` / `.h-xl-zh` / `.h-md` / `.h-sub` | 6 级标题，font-weight 200-300 |
| KPI 巨数 | `.kpi-hero` (22vw 800) / `.kpi-big` (11vw 800) / `.kpi-mid` (6vw 700) / `.kpi-thin` (14vw 200) / `.kpi-thin-sm` (5.6vw 250) | 数字 |
| 编号 | `.num-mega` / `.name-mega` (9vw 200) | 封面/收尾巨编号 |
| 文本角色 | `.t-cat` / `.t-meta` / `.t-helper` / `.t-body-sm` / `.t-body` / `.t-body-emp` / `.t-h-prod` | 替代 opacity 等级 |
| 装饰 | `.rule` / `.dots` / `.dot-mat` / `.ring-mat` / `.cross-mat` / `.hatch` | 1px hairline + 点阵 |
| 块 | `.accent-block` / `.ink-block` / `.grey-block` / `.card-fill` / `.card-ink` / `.card-accent` / `.card-outlined` | 块容器 |
| 高亮 | `.mark` / `.mark.ink` / `.underline-accent` | 文字高亮 |
| 网格 | `.grid-12` + `.span-2..12` / `.grid-2-7-5/6-6/8-4/4-8` / `.grid-3/3-3/4/6` | 12 栏 + 固定比例 |
| 时间线 | `.timeline-v` + `.tl-node` / `.timeline-h` + `.th-node` | 纵/横时间线 |
| 图表 | `.h-bar-chart` + `.row-fill` / `.v-bar-chart` + `.col-bar` / `.bar-towers` + `.body-block.h-1/2/3/4` | 条形图 |
| 卡片 | `.sub-card` / `.force-card` / `.why-col` / `.fc-col` / `.ledger-row` | 6 类卡 |
| 工艺 | `.stack-row` + `.stack-block` / `.duo-compare` + `.col` | 三层堆 + 双轨对照 |
| 图片 | `.frame-img.r-21x9/16x9/16x10/4x3/3x2/3x4/1x1` + `.h-16..32` | 6 种比例 + 6 种高度 |
| 主题 | `.slide.grey/dark/accent/hero/split` + `.canvas-card` | 5 个主题修饰 |

---

**详见** [swiss-layout-lock.md](swiss-layout-lock.md)（硬约束）/ [themes-swiss.md](themes-swiss.md)（9 套主题色值）/ [swiss-map-component.md](swiss-map-component.md)（S08 扩展）。
