---
layout_id: L13
name_zh: 引用墙
name_en: Quote Wall · 多条短引言
style: editorial
---

## Layout 13: 引用墙（Quote Wall · 多条短引言）

3-6 条短引言密集排列，每条带出处。适合用户评价、多方观点、口碑墙。

```html
<section class="slide light">
  <div class="chrome">
    <div>口碑 · Voices</div>
    <div>Act II · 09 / 25</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Voices · 他们说</div>
    <h2 class="h-xl" style="margin-bottom:5vh">六条评价</h2>

    <div class="quote-wall" data-cols="3">
      <div class="qw-item">
        <div class="qw-text">"第一条短引言，浓缩成一个观点。"</div>
        <span class="qw-cite">— 出处 A · 角色</span>
      </div>
      <div class="qw-item">
        <div class="qw-text">"第二条短引言，角度不同。"</div>
        <span class="qw-cite">— 出处 B · 角色</span>
      </div>
      <div class="qw-item">
        <div class="qw-text">"第三条短引言。"</div>
        <span class="qw-cite">— 出处 C · 角色</span>
      </div>
      <div class="qw-item">
        <div class="qw-text">"第四条短引言。"</div>
        <span class="qw-cite">— 出处 D · 角色</span>
      </div>
      <div class="qw-item">
        <div class="qw-text">"第五条短引言。"</div>
        <span class="qw-cite">— 出处 E · 角色</span>
      </div>
      <div class="qw-item">
        <div class="qw-text">"第六条短引言。"</div>
        <span class="qw-cite">— 出处 F · 角色</span>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 09 · 口碑</div>
    <div>Voices</div>
  </div>
</section>
```

**要点**：
- `.quote-wall` 默认 2 列，`data-cols="3"` 三列、`data-cols="1"` 单列；引言 4-6 条最稳
- 每条 `qw-item`：`qw-text`（衬线）+ `qw-cite`（等宽出处），顶部细线分隔
- **和 Layout 8 大引用的区别**：8 是一条巨型金句、13 是多条短引言密集——同一 deck 两者可共存，但不要相邻

---
