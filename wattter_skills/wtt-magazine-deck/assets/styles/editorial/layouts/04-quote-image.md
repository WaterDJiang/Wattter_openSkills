---
layout_id: L04
name_zh: 左文右图
name_en: Quote + Image
style: editorial
---

## Layout 4: 左文右图（Quote + Image）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 7:5 左字右图 | 默认，文字为主 |
| **B** | 5:7 左图右字（镜像） | 图为主、字为辅，或想打破"永远左字右图" |
| **C** | 全幅图 + 角落叠加 | 图就是页面、文字压角，最大视觉冲击 |

### 变体 A · 7:5 左字右图（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>主题标签 · Tag</div>
    <div>03 / 25</div>
  </div>
  <div class="frame grid-2-7-5" style="padding-top:6vh">
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:3vh">
      <div>
        <div class="kicker">BUT</div>
        <h2 class="h-xl" style="white-space:nowrap; font-size:7.2vw">
          标题文字。
        </h2>
        <p class="lead" style="margin-top:3vh">
          补充说明段落。
        </p>
      </div>
      <div class="callout">
        "引用文字。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
    <figure class="frame-img" style="aspect-ratio:16/10; max-height:56vh">
      <img src="images/example.png" alt="说明">
      <figcaption class="img-cap">图片说明</figcaption>
    </figure>
  </div>
  <div class="foot">
    <div>Page 03 · 说明</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：`grid-2-7-5`（7:5）；左列 flex column + `justify-content:space-between`；右列图用 16/10 + `max-height:56vh`，**不要** `align-self:end`。

### 变体 B · 5:7 左图右字（镜像）

```html
<section class="slide dark">
  <div class="chrome">
    <div>主题标签 · Tag</div>
    <div>03 / 25</div>
  </div>
  <div class="frame grid-2-5-7" style="padding-top:6vh">
    <figure class="frame-img" style="aspect-ratio:4/3; max-height:60vh">
      <img src="images/example.png" alt="说明">
      <figcaption class="img-cap">图片说明</figcaption>
    </figure>
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:3vh">
      <div>
        <div class="kicker">BUT</div>
        <h2 class="h-xl" style="font-size:6.4vw">
          标题文字。
        </h2>
        <p class="lead" style="margin-top:3vh">
          补充说明段落。
        </p>
      </div>
      <div class="callout">
        "引用文字。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 03 · 说明</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：`grid-2-5-7`（5:7）把图放左、字放右，图比例换 4/3 更竖；**和 A 是同一布局的镜像变体，同 deck 内两页都用 Layout 4 时必须一页 A 一页 B**。图为主时配 `dark` 主题也别有味道。

### 变体 C · 全幅图 + 角落叠加

```html
<section class="slide hero dark">
  <div class="chrome" style="position:relative; z-index:2">
    <div>主题标签 · Tag</div>
    <div>03 / 25</div>
  </div>
  <figure class="frame-img" style="position:absolute; inset:0; width:100%; height:100%; border-radius:0; z-index:0">
    <img src="images/example.png" alt="说明" style="object-position:center">
  </figure>
  <div class="bottom-left" style="z-index:2; max-width:46vw">
    <div class="kicker">BUT</div>
    <h2 class="h-xl" style="font-size:7vw; line-height:1.05">标题文字压角。</h2>
    <p class="lead" style="margin-top:2vh; max-width:40vw">补充说明。</p>
  </div>
  <div class="foot" style="position:relative; z-index:2">
    <div>Page 03 · 说明</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：图 `position:absolute;inset:0` 当全幅背景（不套 aspect-ratio / height:Nvh，是 Pre-flight B 的唯一例外），文字用 `.bottom-left` 压左下角；图必须 ≥1920px 宽、构图主体在右上（避开左下文字）。这是 hero 页，WebGL 遮罩很薄，图直接顶满。**同 deck 内全幅叠加页不要超过 2 个**，否则视觉过重。

---
