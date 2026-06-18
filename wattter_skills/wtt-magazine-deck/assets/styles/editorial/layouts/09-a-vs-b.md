---
layout_id: L09
name_zh: 并列对比
name_en: A vs B
style: editorial
---

## Layout 9: 并列对比（A vs B · 旧 vs 新）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 左右双列 | 默认，旧/新左右并置 |
| **B** | 上下堆叠 | 上旧下新，纵向演进 |
| **C** | 三段演进 (grid-3) | 旧 → 过渡 → 新，三段 |

### 变体 A · 左右双列（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>旧 vs 新 · The Shift</div>
    <div>12 / 25</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Before / After · 范式转变</div>
    <h2 class="h-xl" style="margin-bottom:4vh">对比标题</h2>

    <div class="grid-2-6-6" style="gap:5vw 4vh">
      <div style="padding:3vh 2vw; border-left:3px solid currentColor; opacity:.55">
        <div class="kicker" style="opacity:.9">Before · 旧模式</div>
        <h3 class="h-md" style="margin-top:2vh">旧模式标题</h3>
        <ul style="margin-top:3vh; padding-left:1.2em; display:flex; flex-direction:column; gap:1.4vh; font-family:var(--sans-zh); font-size:max(14px,1.1vw); line-height:1.55">
          <li>要点一</li>
          <li>要点二</li>
          <li>要点三</li>
          <li>要点四</li>
        </ul>
      </div>
      <div style="padding:3vh 2vw; border-left:3px solid currentColor">
        <div class="kicker" style="opacity:.9">After · 新模式</div>
        <h3 class="h-md" style="margin-top:2vh">新模式标题</h3>
        <ul style="margin-top:3vh; padding-left:1.2em; display:flex; flex-direction:column; gap:1.4vh; font-family:var(--sans-zh); font-size:max(14px,1.1vw); line-height:1.55">
          <li>要点一</li>
          <li>要点二</li>
          <li>要点三</li>
          <li>要点四</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 12 · 范式转变</div>
    <div>Before / After</div>
  </div>
</section>
```

**要点**：`grid-2-6-6`（1:1）；左列 `opacity:.55` 弱化旧、右列满亮度突出新；两列 `border-left:3px` + `padding-left` 做引用块感。

### 变体 B · 上下堆叠

```html
<section class="slide light">
  <div class="chrome">
    <div>旧 vs 新 · The Shift</div>
    <div>12 / 25</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Before / After · 范式转变</div>
    <h2 class="h-xl" style="margin-bottom:4vh">对比标题</h2>

    <div style="display:flex; flex-direction:column; gap:3vh">
      <div style="display:grid; grid-template-columns:auto 1fr; gap:3vw; padding:3vh 2vw; border-top:3px solid currentColor; opacity:.55">
        <div class="kicker" style="opacity:.9; align-self:center">Before · 旧</div>
        <div>
          <h3 class="h-md">旧模式标题</h3>
          <p class="lead" style="font-size:1.3rem; margin-top:1.5vh; opacity:.8">旧模式一句话描述。</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:auto 1fr; gap:3vw; padding:3vh 2vw; border-top:3px solid currentColor">
        <div class="kicker" style="align-self:center">After · 新</div>
        <div>
          <h3 class="h-md">新模式标题</h3>
          <p class="lead" style="font-size:1.3rem; margin-top:1.5vh">新模式一句话描述。</p>
        </div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 12 · 范式转变</div>
    <div>Before / After</div>
  </div>
</section>
```

**要点**：上旧下新纵向堆叠，每行 `border-top:3px` 分隔；适合"演进感"强于"并置感"的对比，要点少时比 A 更利落。

### 变体 C · 三段演进

```html
<section class="slide light">
  <div class="chrome">
    <div>演进 · The Shift</div>
    <div>12 / 25</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Before / During / After · 三段演进</div>
    <h2 class="h-xl" style="margin-bottom:5vh">演进标题</h2>

    <div class="grid-3" style="gap:3.6rem 2.7rem">
      <div style="padding-top:2vh; border-top:3px solid currentColor; opacity:.5">
        <div class="kicker" style="opacity:.9">01 · Before</div>
        <h3 class="h-md" style="margin-top:2vh">旧状态</h3>
        <p class="lead" style="font-size:1.2rem; margin-top:1.5vh; opacity:.8">旧状态描述。</p>
      </div>
      <div style="padding-top:2vh; border-top:3px solid currentColor; opacity:.72">
        <div class="kicker" style="opacity:.9">02 · During</div>
        <h3 class="h-md" style="margin-top:2vh">过渡</h3>
        <p class="lead" style="font-size:1.2rem; margin-top:1.5vh; opacity:.85">过渡描述。</p>
      </div>
      <div style="padding-top:2vh; border-top:3px solid currentColor">
        <div class="kicker" style="opacity:.9">03 · After</div>
        <h3 class="h-md" style="margin-top:2vh">新状态</h3>
        <p class="lead" style="font-size:1.2rem; margin-top:1.5vh">新状态描述。</p>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 12 · 演进</div>
    <div>Before / After</div>
  </div>
</section>
```

**要点**：`grid-3` 三段，透明度从 .5 → .72 → 1 递增，视觉上"从弱到强"演进；适合需要展示"中间过渡态"的对比，比二分更细腻。

---
