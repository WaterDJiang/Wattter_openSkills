---
layout_id: L15
name_zh: 双页跨页
name_en: Magazine Spread
style: editorial
---

## Layout 15: 双页跨页（Magazine Spread）

模拟杂志跨页：左右两页对照，中间竖线分隔，每侧独立的 kicker + 标题 + 内容。

```html
<section class="slide light">
  <div class="chrome">
    <div>跨页 · Spread</div>
    <div>Act II · 11 / 25</div>
  </div>
  <div class="frame" style="display:grid; grid-template-columns:1fr 1px 1fr; gap:0 3.6rem; align-items:stretch; padding-top:5vh">
    <!-- 左页 -->
    <div style="display:flex; flex-direction:column; gap:3vh">
      <div class="kicker">左页 · Left Page</div>
      <h2 class="h-xl" style="font-size:5vw">左侧标题</h2>
      <p class="lead" style="font-size:1.6rem">左侧正文段落，讲一个侧面。</p>
      <p style="font-family:var(--sans-zh); font-size:max(14px,1.1vw); line-height:1.75; opacity:.78; margin-top:auto">左侧补充说明，贴底。</p>
    </div>
    <!-- 中线 -->
    <div class="rule v" style="height:100%"></div>
    <!-- 右页 -->
    <div style="display:flex; flex-direction:column; gap:3vh">
      <div class="kicker">右页 · Right Page</div>
      <h2 class="h-xl" style="font-size:5vw">右侧标题</h2>
      <p class="lead" style="font-size:1.6rem">右侧正文段落，讲另一个侧面。</p>
      <div class="callout" style="margin-top:auto">
        "右侧引用压底。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 11 · 跨页</div>
    <div>Spread</div>
  </div>
</section>
```

**要点**：
- 内联 3 列网格 `1fr 1px 1fr`，中间一列放 `.rule.v` 竖线；左右两页各自 `flex column`，内容可不同结构（一侧文一侧图也行）
- 适合"两个对等概念并置但都不是'旧vs新'"的页（那样用 Layout 9）；跨页感来自中线 + 左右独立 kicker
- 标题字号比单页小（5vw），因为要容下两列

---
