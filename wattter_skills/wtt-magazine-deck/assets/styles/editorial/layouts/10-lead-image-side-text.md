---
layout_id: L10
name_zh: 图文混排
name_en: Lead Image + Side Text
style: editorial
---

## Layout 10: 图文混排（Lead Image + Side Text）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 8:4 左文右辅图 | 默认，正文为主、图为辅 |
| **B** | 4:8 左图右文（镜像） | 图为主、文为辅 |
| **C** | 图作背景叠加 | 图当背景、文字叠在上面 |

### 变体 A · 8:4 左文右辅图（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>Design First · 设计先行</div>
    <div>08 / 16</div>
  </div>
  <div class="frame grid-2-8-4" style="padding-top:6vh">
    <div>
      <div class="kicker">Phase 01 · 阶段</div>
      <h2 class="h-xl" style="margin-top:1vh; margin-bottom:3vh">页面标题</h2>

      <p class="lead" style="margin-bottom:3vh">
        核心段落说明。
      </p>

      <p style="font-family:var(--sans-zh); font-size:max(14px,1.15vw); line-height:1.75; opacity:.78; margin-bottom:2.4vh">
        补充说明段落。
      </p>

      <div class="callout" style="margin-top:3vh">
        "引用文字。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
    <figure class="frame-img" style="aspect-ratio:3/4; max-height:60vh">
      <img src="images/example.png" alt="说明">
      <figcaption class="img-cap">图片说明</figcaption>
    </figure>
  </div>
  <div class="foot">
    <div>Page 08 · 说明</div>
    <div>阶段标签</div>
  </div>
</section>
```

**要点**：`grid-2-8-4`（8:4）正文为主、图为辅；左列 kicker→大标题→lead→正文→callout 多层级；右图竖版 3:4。

### 变体 B · 4:8 左图右文（镜像）

```html
<section class="slide dark">
  <div class="chrome">
    <div>Design First · 设计先行</div>
    <div>08 / 16</div>
  </div>
  <div class="frame grid-2-4-8" style="padding-top:6vh">
    <figure class="frame-img" style="aspect-ratio:3/4; max-height:64vh">
      <img src="images/example.png" alt="说明">
      <figcaption class="img-cap">图片说明</figcaption>
    </figure>
    <div>
      <div class="kicker">Phase 01 · 阶段</div>
      <h2 class="h-xl" style="margin-top:1vh; margin-bottom:3vh">页面标题</h2>
      <p class="lead" style="margin-bottom:3vh">核心段落说明。</p>
      <p style="font-family:var(--sans-zh); font-size:max(14px,1.15vw); line-height:1.75; opacity:.78; margin-bottom:2.4vh">补充说明段落。</p>
      <div class="callout" style="margin-top:3vh">
        "引用文字。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 08 · 说明</div>
    <div>阶段标签</div>
  </div>
</section>
```

**要点**：`grid-2-4-8`（4:8）图在左、文在右；**和 A 是镜像变体，同 deck 两页都用 Layout 10 时必须一页 A 一页 B**。配 `dark` 主题换节奏。

### 变体 C · 图作背景叠加

```html
<section class="slide hero light">
  <div class="chrome" style="position:relative; z-index:2">
    <div>Design First · 设计先行</div>
    <div>08 / 16</div>
  </div>
  <figure class="frame-img" style="position:absolute; inset:0; width:100%; height:100%; border-radius:0; z-index:0">
    <img src="images/example.png" alt="说明" style="object-position:center">
  </figure>
  <div class="bottom-right" style="z-index:2; max-width:44vw; text-align:right">
    <div class="kicker">Phase 01 · 阶段</div>
    <h2 class="h-xl" style="font-size:6vw; line-height:1.05; margin-top:1vh">页面标题</h2>
    <p class="lead" style="margin-top:2vh; max-width:38vw; margin-left:auto">核心段落说明，压在图右上角。</p>
  </div>
  <div class="foot" style="position:relative; z-index:2">
    <div>Page 08 · 说明</div>
    <div>阶段标签</div>
  </div>
</section>
```

**要点**：图 `position:absolute;inset:0` 当背景（Pre-flight B 例外），文字用 `.bottom-right` 压右下；和 Layout 4-C 的区别是 4-C 文字压**左下**且偏 hero 冲击、本变体压**右下**且偏图文叙事。同 deck 全幅叠加页（4-C + 10-C）合计不要超过 2 个。

---
