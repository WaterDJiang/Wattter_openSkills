---
layout_id: L07
name_zh: 悬念收束 / 问题页
name_en: Hero Question
style: editorial
---

## Layout 7: 悬念收束 / 问题页（Hero Question）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 居中 | 默认，一个问题居中 |
| **B** | 左下发问 | 问题压左下，留大量负空间 |
| **C** | 巨型问号 ghost | 用巨型"?"背景制造悬念 |

### 变体 A · 居中（默认）

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>留给你的问题</div>
    <div>24 / 27</div>
  </div>
  <div class="frame" style="display:grid; gap:8vh; align-content:center; min-height:80vh">
    <div class="kicker">The Question</div>
    <h1 class="h-hero" style="font-size:7vw; line-height:1.15">
      你的核心问题，<br>
      分行排列。
    </h1>
    <p class="lead" style="max-width:50vw">
      一句点破。
    </p>
  </div>
  <div class="foot">
    <div>Page 24 · The Question</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：Hero 页留白越多越好；`h-hero` 字号视长度调（7vw 适合 3 行，10vw 适合 1 行）；`<br>` 手工断行。

### 变体 B · 左下发问

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>留给你的问题</div>
    <div>24 / 27</div>
  </div>
  <div class="frame" style="display:flex; flex-direction:column; justify-content:flex-end; min-height:80vh">
    <div class="kicker">The Question</div>
    <h1 class="h-hero" style="font-size:7.5vw; line-height:1.1; margin-top:2vh">
      你的核心问题，<br>分行压角。
    </h1>
    <p class="lead" style="max-width:46vw; margin-top:3vh">一句点破。</p>
  </div>
  <div class="foot">
    <div>Page 24 · The Question</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：`justify-content:flex-end` 把问题压到页面下方，上方大面积留白制造"悬而未决"的张力；和居中变体观感明显不同。

### 变体 C · 巨型问号 ghost

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>留给你的问题</div>
    <div>24 / 27</div>
  </div>
  <div class="ghost" style="right:-2vw; top:-14vh; font-size:52vw; opacity:.09; font-style:italic">?</div>
  <div class="frame" style="display:grid; gap:6vh; align-content:center; min-height:80vh; position:relative; z-index:2">
    <div class="kicker">The Question</div>
    <h1 class="h-hero" style="font-size:6.5vw; line-height:1.15">
      你的核心问题，<br>分行排列。
    </h1>
    <p class="lead" style="max-width:50vw">一句点破。</p>
  </div>
  <div class="foot">
    <div>Page 24 · The Question</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：用 `.ghost` 巨型"?"作背景（opacity .09），内容 `z-index:2` 压上；问号本身就在暗示"这是问题"，仪式感最强。

---
