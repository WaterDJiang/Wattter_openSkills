---
layout_id: L14
name_zh: 三栏并列
name_en: Three Pillars
style: editorial
---

## Layout 14: 三栏并列（Three Pillars）

三个等宽支柱卡，序号/图标 + 标题 + 描述。适合三原则、三支柱、三角色、三步骤概念。

```html
<section class="slide light">
  <div class="chrome">
    <div>三支柱 · Three Pillars</div>
    <div>Act I · 06 / 25</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Three Pillars · 三个支柱</div>
    <h2 class="h-xl" style="margin-bottom:6vh">三支柱</h2>

    <div class="grid-3" style="gap:3.6rem 2.7rem">
      <div class="pillar">
        <div class="ic"><i data-lucide="compass"></i></div>
        <div class="t">判断力</div>
        <div class="d">决策和方向的权威。<br>取舍、品味、方向感。</div>
      </div>
      <div class="pillar">
        <div class="ic"><i data-lucide="hammer"></i></div>
        <div class="t">执行力</div>
        <div class="d">把判断落地的能力。<br>速度、质量、闭环。</div>
      </div>
      <div class="pillar">
        <div class="ic"><i data-lucide="users"></i></div>
        <div class="t">连接力</div>
        <div class="d">让别人愿意帮你的能力。<br>信任、叙事、共赢。</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 06 · 三支柱</div>
    <div>Three Pillars</div>
  </div>
</section>
```

**要点**：
- `.grid-3` + `.pillar`（`ic` 图标 / 序号 → `t` 标题 → `d` 描述）；`.ic` 可放 Lucide 图标或序号 01/02/03
- 图标必须用 Lucide（`<i data-lucide="...">`），不要用 emoji
- 想要带边框强调版：给 `.pillar` 加 `style="padding:3vh 1.5vw; border:1px solid currentColor; border-color:rgba(127,127,127,.25)"`（同 Layout 6-C）

---
