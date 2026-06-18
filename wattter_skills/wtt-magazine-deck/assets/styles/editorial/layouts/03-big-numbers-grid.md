---
layout_id: L03
name_zh: 数据大字报
name_en: Big Numbers Grid
style: editorial
---

## Layout 3: 数据大字报（Big Numbers Grid）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 3×2 网格 (grid-6) | 默认，6 个指标 |
| **B** | 2×2 大格 (grid-4) | 只有 4 个核心指标、想让数字更大 |
| **C** | 横向数据条 (grid-3) | 3 个指标横排一行，配大段说明 |

### 变体 A · 3×2 网格（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>数据 · Data</div>
    <div>Act I / Data · 02 / 25</div>
  </div>
  <div class="frame" style="padding-top:6vh">
    <div class="kicker">标题引导语</div>
    <h2 class="h-xl">数据页标题</h2>
    <p class="lead" style="margin-bottom:5vh">补充说明。</p>

    <div class="grid-6" style="margin-top:6vh">
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">64 <span class="stat-unit">天</span></div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">110K+</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">5,166</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">41K+</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">19</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">608+</div>
        <div class="stat-note">注释说明</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>项目 · 名称</div>
    <div>Act I · Data</div>
  </div>
</section>
```

**要点**：3×2 `grid-6`；每个 `stat-card` 固定 label→nb→note；数字 2-3 位用 K/M 简写；留 5vh 上方缓冲。

### 变体 B · 2×2 大格

```html
<section class="slide light">
  <div class="chrome">
    <div>数据 · Data</div>
    <div>Act I / Data · 02 / 25</div>
  </div>
  <div class="frame" style="padding-top:6vh">
    <div class="kicker">标题引导语</div>
    <h2 class="h-xl">数据页标题</h2>
    <p class="lead" style="margin-bottom:6vh">补充说明。</p>

    <div class="grid-4" style="margin-top:4vh">
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">110K+</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">5,166</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">41K+</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">19</div>
        <div class="stat-note">注释说明</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>项目 · 名称</div>
    <div>Act I · Data</div>
  </div>
</section>
```

**要点**：`grid-4` 是 2×2，CSS 已让 `.grid-4 .stat-card .stat-nb` 字号更大（9rem）；只有 3-4 个硬指标时用这个，数字更震撼。**同一个 deck 里不要 A、B 连用**——两者都是网格大字报，会雷同；要换就换成 C 或别的布局。

### 变体 C · 横向数据条

```html
<section class="slide light">
  <div class="chrome">
    <div>数据 · Data</div>
    <div>Act I / Data · 02 / 25</div>
  </div>
  <div class="frame grid-2-8-4" style="padding-top:6vh">
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:4vh">
      <div>
        <div class="kicker">标题引导语</div>
        <h2 class="h-xl">数据页标题</h2>
        <p class="lead" style="margin-top:3vh">补充说明段落，可以比 A/B 变体写得更长，讲清这三个数字背后的故事。</p>
      </div>
      <div class="callout">
        "一句话点破这三个数字的关系。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
    <div class="grid-3" style="gap:2.4rem 2rem; align-content:center">
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">110K+</div>
        <div class="stat-note">注释</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">5,166</div>
        <div class="stat-note">注释</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">19</div>
        <div class="stat-note">注释</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>项目 · 名称</div>
    <div>Act I · Data</div>
  </div>
</section>
```

**要点**：左文右数据，3 个 stat 横排一行（`grid-3`）；适合"数字少但要讲故事"的页——左边可以放大段说明 + callout。和 A/B 的纯网格构图完全不同。

---
