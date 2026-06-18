---
layout_id: L12
name_zh: 单数字大字
name_en: Single Hero Number
style: editorial
---

## Layout 12: 单数字大字（Single Hero Number）

一个巨型数字占满页面 + 一句注解。比 Layout 3 更聚焦——只讲一个数字。

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>核心数据 · The Number</div>
    <div>02 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:4vh; align-content:center; min-height:80vh">
    <div class="kicker">The Number · 一个数字</div>
    <div class="big-num" style="font-size:22vw; line-height:.85">1,284</div>
    <p class="lead" style="max-width:50vw">
      一句话讲清这个数字意味着什么。
    </p>
    <div class="meta-row">
      <span>来源 · 出处</span><span>·</span><span>截至 2026.04</span>
    </div>
  </div>
  <div class="foot">
    <div>Page 02 · 核心数据</div>
    <div>The Number</div>
  </div>
</section>
```

**要点**：
- 用 `.big-num`（Playfair 800）放一个数字，inline `font-size:22vw` 顶满；数字 ≤ 5 字符最稳（千分位逗号算 1 字符）
- 配 `hero dark`，WebGL 透出让数字漂浮感更强
- 适合"开场第二个硬数据"或"转折页抛一个惊人数字"
- 数字可加单位：`1,284<em style="font-size:.32em; opacity:.5; font-style:normal"> 次</em>`

---
