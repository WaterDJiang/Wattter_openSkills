---
layout_id: L02
name_zh: 章节幕封
name_en: Act Divider
style: editorial
---

## Layout 2: 章节幕封（Act Divider）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 居中极简 | 默认，纯文字幕封 |
| **B** | ghost 序号 | 想用巨型背景数字制造章节感 |
| **C** | 横向编号带 | 多幕结构里用"01 / 04"进度条式幕封 |

### 变体 A · 居中极简（默认）

```html
<section class="slide hero light">
  <div class="chrome">
    <div>第一幕 · 标签</div>
    <div>Act I · 01 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:6vh; align-content:center; min-height:80vh">
    <div class="kicker">Act I</div>
    <h1 class="h-hero" style="font-size:8.5vw">章节名</h1>
    <p class="lead" style="max-width:55vw">
      一句引语。
    </p>
  </div>
  <div class="foot">
    <div>章节说明</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：极简，kicker + 大标题 + 一行引语；两个幕的封面交替 `hero light` / `hero dark`。

### 变体 B · ghost 序号

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>第一幕 · 标签</div>
    <div>Act I · 01 / 25</div>
  </div>
  <div class="ghost" style="right:-4vw; top:-10vh; font-size:46vw; opacity:.08">01</div>
  <div class="frame" style="display:grid; gap:5vh; align-content:center; min-height:80vh; position:relative; z-index:2">
    <div class="kicker">Act I</div>
    <h1 class="h-hero" style="font-size:8.5vw">章节名</h1>
    <p class="lead" style="max-width:50vw">
      一句引语。
    </p>
  </div>
  <div class="foot">
    <div>章节说明</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：用 `.ghost` 巨型序号（01/02/03）作背景装饰，内容加 `z-index:2` 压在上面；多个幕封用不同序号，天然不雷同。

### 变体 C · 横向编号带

```html
<section class="slide hero light">
  <div class="chrome">
    <div>第一幕 · 标签</div>
    <div>Act I · 01 / 25</div>
  </div>
  <div class="frame" style="display:flex; flex-direction:column; justify-content:center; gap:5vh; min-height:80vh">
    <div class="meta-row" style="font-size:1rem; opacity:.5">
      <span style="opacity:1">01</span><span>—</span><span>02</span><span>—</span><span>03</span><span>—</span><span>04</span>
    </div>
    <div class="rule" style="margin:0"></div>
    <div class="kicker">Act I</div>
    <h1 class="h-hero" style="font-size:8vw">章节名</h1>
    <p class="lead" style="max-width:50vw">一句引语。</p>
  </div>
  <div class="foot">
    <div>章节说明</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：顶部一行 `01 — 02 — 03 — 04` 进度带，当前幕加亮，下方一条 `.rule` 分隔；适合 3-4 幕的长 deck，让听众知道进度。

---
