---
layout_id: L01
name_zh: 开场封面
name_en: Hero Cover
style: editorial
---

## Layout 1: 开场封面（Hero Cover）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 居中堆叠 | 默认，标题居中、信息对称 |
| **B** | 左下压角 | 杂志封面感，标题压左下、留大量负空间 |
| **C** | 中英对照双行 | 标题需要中英双语并置时 |

### 变体 A · 居中堆叠（默认）

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>A Talk · 2026.04.22</div>
    <div>Vol.01</div>
  </div>
  <div class="frame" style="display:grid; gap:4vh; align-content:center; min-height:80vh">
    <div class="kicker">分享会 · 演讲者</div>
    <h1 class="h-hero">标题</h1>
    <h2 class="h-sub">副标题</h2>
    <p class="lead" style="max-width:60vw">
      一段引语，概括整个分享的核心观点。
    </p>
    <div class="meta-row">
      <span>演讲者</span><span>·</span><span>身份 / 标签</span>
    </div>
  </div>
  <div class="foot">
    <div>一场关于 XX 的分享</div>
    <div>— 2026 —</div>
  </div>
</section>
```

**要点**：`hero dark` 让 WebGL 透出；`h-hero` 10vw；`min-height:80vh + align-content:center` 垂直居中。

### 变体 B · 左下压角

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>A Talk · 2026.04.22</div>
    <div>Vol.01</div>
  </div>
  <div class="frame" style="display:flex; flex-direction:column; justify-content:flex-end; min-height:80vh">
    <div class="kicker">分享会 · 演讲者</div>
    <h1 class="h-hero" style="font-size:11vw; line-height:.92">标题压角</h1>
    <h2 class="h-sub" style="margin-top:2vh">副标题</h2>
    <div class="meta-row" style="margin-top:4vh">
      <span>演讲者</span><span>·</span><span>身份 / 标签</span><span>·</span><span>2026.04</span>
    </div>
  </div>
  <div class="foot">
    <div>一场关于 XX 的分享</div>
    <div>— 2026 —</div>
  </div>
</section>
```

**要点**：用 `justify-content:flex-end` 把整组内容压到页面下方，上方留大面积负空间，更像杂志封面；标题可放到 11vw 更满。

### 变体 C · 中英对照双行

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>A Talk · 2026.04.22</div>
    <div>Vol.01</div>
  </div>
  <div class="frame" style="display:grid; gap:3vh; align-content:center; min-height:80vh">
    <div class="kicker">分享会 · 演讲者</div>
    <h1 class="h-hero">中文标题</h1>
    <p class="h-hero-en" style="font-family:var(--serif-en); font-style:italic; font-weight:500; font-size:5vw; opacity:.62; line-height:1.1; margin-top:-1vh">English Title Here</p>
    <div class="meta-row" style="margin-top:3vh">
      <span>演讲者</span><span>·</span><span>身份 / 标签</span>
    </div>
  </div>
  <div class="foot">
    <div>一场关于 XX 的分享</div>
    <div>— 2026 —</div>
  </div>
</section>
```

**要点**：中文 `h-hero` 衬线大字 + 下方英文 Playfair 斜体小一号、降透明度，制造中英对照层级；适合双语场合或英文是品牌名时。

---
