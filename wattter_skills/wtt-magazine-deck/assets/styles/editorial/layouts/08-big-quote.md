---
layout_id: L08
name_zh: 大引用页
name_en: Big Quote · 衬线金句
style: editorial
---

## Layout 8: 大引用页（Big Quote · 衬线金句）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 居中 | 默认，金句居中 + 出处 |
| **B** | 左对齐大引号 | 引言靠左、巨型引号装饰 |
| **C** | 全屏一句 | 无出处、纯一句最大字号冲击 |

### 变体 A · 居中（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>The Takeaway · 核心金句</div>
    <div>18 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:5vh; align-content:center; min-height:80vh">
    <div class="kicker">Quote · 金句</div>
    <blockquote style="font-family:var(--serif-zh); font-weight:700; font-size:5.8vw; line-height:1.2; letter-spacing:-.01em; max-width:72vw">
      "引用文字，<br>分行排列。"
    </blockquote>
    <p class="lead" style="max-width:55vw; opacity:.65">
      英文原文或补充说明。
    </p>
    <div class="meta-row">
      <span>— 出处</span><span>·</span><span>日期</span>
    </div>
  </div>
  <div class="foot">
    <div>Page 18 · 金句</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：整页留白，一个大引用 + 出处；`<blockquote>` 用 inline style 放大（5-6vw），不要用 `h-hero`；下方 lead（opacity .65）+ meta-row 出处。

### 变体 B · 左对齐大引号

```html
<section class="slide dark">
  <div class="chrome">
    <div>The Takeaway · 核心金句</div>
    <div>18 / 25</div>
  </div>
  <div class="frame" style="display:grid; grid-template-columns:auto 1fr; gap:2vw; align-content:center; min-height:80vh">
    <span style="font-family:var(--serif-en); font-weight:900; font-size:18vw; line-height:.7; opacity:.18; align-self:start">"</span>
    <div style="display:flex; flex-direction:column; gap:4vh">
      <blockquote style="font-family:var(--serif-zh); font-weight:700; font-size:5.2vw; line-height:1.2; max-width:30vw">
        引用文字，<br>分行排列。
      </blockquote>
      <div class="meta-row">
        <span>— 出处</span><span>·</span><span>日期</span>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 18 · 金句</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：左侧巨型引号（18vw、低透明度）作装饰，引言靠左；`dark` 主题配引号更有质感。和居中变体的对称感完全不同。

### 变体 C · 全屏一句

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>The Takeaway · 核心金句</div>
    <div>18 / 25</div>
  </div>
  <div class="frame" style="display:grid; align-content:center; min-height:80vh">
    <blockquote style="font-family:var(--serif-zh); font-weight:900; font-size:8.5vw; line-height:1.1; letter-spacing:-.02em; max-width:88vw">
      一句话，<br>顶一万句。
    </blockquote>
  </div>
  <div class="foot">
    <div>Page 18 · 金句</div>
    <div>— · —</div>
  </div>
</section>
```

**要点**：无 kicker、无出处、无 lead，纯一句超大字号（8.5vw）顶满；hero dark 让 WebGL 透出。**只用于全 deck 最关键的那一句**（通常收尾），多用就滥了。

---
