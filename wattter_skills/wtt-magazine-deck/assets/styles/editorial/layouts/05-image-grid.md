---
layout_id: L05
name_zh: 图片网格
name_en: Image Grid
style: editorial
---

## Layout 5: 图片网格（多图对比）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 3×2 网格 (grid-3-3) | 默认，6 张图对比 |
| **B** | 2×2 大图 | 4 张关键截图，每张更大更清晰 |
| **C** | 1 大 + 多小（非对称） | 1 张主图 + 3-4 张细节辅图 |

### 变体 A · 3×2 网格（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>实证 · Proof</div>
    <div>Act I · 05 / 27</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Proof · 实证</div>
    <h2 class="h-xl">6 张截图</h2>

    <div class="grid-3-3" style="margin-top:4vh">
      <figure class="frame-img" style="height:26vh">
        <img src="images/01.png" alt="说明1">
        <figcaption class="img-cap">说明1</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/02.png" alt="说明2">
        <figcaption class="img-cap">说明2</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/03.png" alt="说明3">
        <figcaption class="img-cap">说明3</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/04.png" alt="说明4">
        <figcaption class="img-cap">说明4</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/05.png" alt="说明5">
        <figcaption class="img-cap">说明5</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/06.png" alt="说明6">
        <figcaption class="img-cap">说明6</figcaption>
      </figure>
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>Page 05 · 实证</div>
  </div>
</section>
```

**要点**：每个 `frame-img` 写死 `height:26vh`（不用 aspect-ratio）；`grid-3-3`（3×2）承载。

### 变体 B · 2×2 大图

```html
<section class="slide light">
  <div class="chrome">
    <div>实证 · Proof</div>
    <div>Act I · 05 / 27</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Proof · 实证</div>
    <h2 class="h-xl">4 张关键截图</h2>

    <div class="grid-4" style="margin-top:4vh">
      <figure class="frame-img" style="height:34vh">
        <img src="images/01.png" alt="说明1">
        <figcaption class="img-cap">说明1</figcaption>
      </figure>
      <figure class="frame-img" style="height:34vh">
        <img src="images/02.png" alt="说明2">
        <figcaption class="img-cap">说明2</figcaption>
      </figure>
      <figure class="frame-img" style="height:34vh">
        <img src="images/03.png" alt="说明3">
        <figcaption class="img-cap">说明3</figcaption>
      </figure>
      <figure class="frame-img" style="height:34vh">
        <img src="images/04.png" alt="说明4">
        <figcaption class="img-cap">说明4</figcaption>
      </figure>
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>Page 05 · 实证</div>
  </div>
</section>
```

**要点**：`grid-4` 2×2，每张 `height:34vh` 比 A 更大；4 张图够用时优先这个，单图更清晰。和 A 都是"等分网格"，**同 deck 不要 A、B 连用**。

### 变体 C · 1 大 + 多小（非对称）

```html
<section class="slide light">
  <div class="chrome">
    <div>实证 · Proof</div>
    <div>Act I · 05 / 27</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Proof · 实证</div>
    <h2 class="h-xl">主图 + 细节</h2>

    <div style="display:grid; grid-template-columns:5fr 4fr; gap:2.4rem 2.7rem; margin-top:4vh">
      <figure class="frame-img" style="height:54vh">
        <img src="images/01-hero.png" alt="主图">
        <figcaption class="img-cap">主图说明</figcaption>
      </figure>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:2.4rem 2.7rem">
        <figure class="frame-img" style="height:26vh">
          <img src="images/02.png" alt="说明2">
          <figcaption class="img-cap">说明2</figcaption>
        </figure>
        <figure class="frame-img" style="height:26vh">
          <img src="images/03.png" alt="说明3">
          <figcaption class="img-cap">说明3</figcaption>
        </figure>
        <figure class="frame-img" style="height:26vh">
          <img src="images/04.png" alt="说明4">
          <figcaption class="img-cap">说明4</figcaption>
        </figure>
        <figure class="frame-img" style="height:26vh">
          <img src="images/05.png" alt="说明5">
          <figcaption class="img-cap">说明5</figcaption>
        </figure>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>Page 05 · 实证</div>
  </div>
</section>
```

**要点**：左大图（5fr、54vh）+ 右 2×2 小图（各 26vh），非对称构图；适合"一张总览 + 多张细节"的展示，比等分网格更有叙事。内联 grid 是允许的（Pre-flight A：自定义用 inline）。

---
