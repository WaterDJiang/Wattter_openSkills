---
layout_id: L11
name_zh: 时间轴
name_en: Timeline · 纵向节点
style: editorial
---

## Layout 11: 时间轴（Timeline · 纵向节点）

适合发展历程、路线图、产品演进、个人/公司编年史。

```html
<section class="slide light">
  <div class="chrome">
    <div>历程 · Timeline</div>
    <div>Act I · 04 / 25</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Timeline · 编年</div>
    <h2 class="h-xl" style="margin-bottom:6vh">发展历程</h2>

    <div class="timeline">
      <div class="tl-node">
        <div class="tl-year">2019</div>
        <div>
          <div class="tl-title">起点</div>
          <div class="tl-desc">一个人、一台电脑，开始做这件事的描述。</div>
        </div>
      </div>
      <div class="tl-node">
        <div class="tl-year">2021</div>
        <div>
          <div class="tl-title">第一个转折</div>
          <div class="tl-desc">遇到了关键问题或机会的描述。</div>
        </div>
      </div>
      <div class="tl-node">
        <div class="tl-year">2023</div>
        <div>
          <div class="tl-title">规模化</div>
          <div class="tl-desc">从一个人变成一个体系的描述。</div>
        </div>
      </div>
      <div class="tl-node">
        <div class="tl-year">2026</div>
        <div>
          <div class="tl-title">现在</div>
          <div class="tl-desc">当下状态与下一步的描述。</div>
        </div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 04 · 历程</div>
    <div>Timeline</div>
  </div>
</section>
```

**要点**：
- 纵向时间轴，左列 `tl-year`（英文斜体年份）+ 右列 `tl-title`/`tl-desc`，节点间 `border-top` 分隔
- 节点数 4-6 个最稳，超过 6 个拆成两页或砍细节
- 想要横向时间轴？直接用 Layout 6 的 `.pipeline`，把 `step-nb` 换成年份即可——**不要**在同一 deck 里纵向横向都用，选一种

---
