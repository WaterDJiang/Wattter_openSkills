---
layout_id: L06
name_zh: 两列流水线
name_en: Pipeline
style: editorial
---

## Layout 6: 两列流水线（Pipeline）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 双行分组 | 默认，两组流程（如文本侧/视觉侧） |
| **B** | 单行横向 | 只有一条线性流程，4-6 步 |
| **C** | 卡片分组式 | 流程要按阶段分卡、每卡带说明 |

### 变体 A · 双行分组（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>工作流 · Workflow</div>
    <div>Act II · 15 / 27</div>
  </div>
  <div class="frame">
    <div class="kicker">Pipeline · 流水线</div>
    <h2 class="h-xl">流程标题</h2>

    <div class="pipeline-section">
      <div class="pipeline-label">文本侧 · Text Pipeline</div>
      <div class="pipeline">
        <div class="step">
          <div class="step-nb">01</div>
          <div class="step-title">Draft</div>
          <div class="step-desc">起草初稿</div>
        </div>
        <div class="step">
          <div class="step-nb">02</div>
          <div class="step-title">Polish</div>
          <div class="step-desc">润色优化</div>
        </div>
        <div class="step">
          <div class="step-nb">03</div>
          <div class="step-title">Morph</div>
          <div class="step-desc">变形成多平台格式</div>
        </div>
        <div class="step">
          <div class="step-nb">04</div>
          <div class="step-title">Illustrate</div>
          <div class="step-desc">生成信息图</div>
        </div>
        <div class="step">
          <div class="step-nb">05</div>
          <div class="step-title">Distribute</div>
          <div class="step-desc">一键分发</div>
        </div>
      </div>
    </div>

    <div class="pipeline-section">
      <div class="pipeline-label">视觉侧 · Video Pipeline</div>
      <div class="pipeline">
        <div class="step">
          <div class="step-nb">06</div>
          <div class="step-title">Cut</div>
          <div class="step-desc">剪辑</div>
        </div>
        <div class="step">
          <div class="step-nb">07</div>
          <div class="step-title">Wrap</div>
          <div class="step-desc">包装</div>
        </div>
        <div class="step">
          <div class="step-nb">08</div>
          <div class="step-title">Cover</div>
          <div class="step-desc">生成封面</div>
        </div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 15 · 工作流</div>
    <div>Workflow</div>
  </div>
</section>
```

**要点**：`.pipeline-section` 分组 + `.pipeline-label` 组标题；单行 ≤5 步，否则换第二 pipeline。

### 变体 B · 单行横向

```html
<section class="slide light">
  <div class="chrome">
    <div>工作流 · Workflow</div>
    <div>Act II · 15 / 27</div>
  </div>
  <div class="frame" style="display:flex; flex-direction:column; justify-content:center">
    <div class="kicker">Pipeline · 流水线</div>
    <h2 class="h-xl">流程标题</h2>
    <p class="lead" style="margin:3vh 0 6vh; max-width:60vw">一段流程说明。</p>

    <div class="pipeline" data-cols="6" style="margin-top:2vh">
      <div class="step">
        <div class="step-nb">01</div>
        <div class="step-title">Draft</div>
        <div class="step-desc">起草</div>
      </div>
      <div class="step">
        <div class="step-nb">02</div>
        <div class="step-title">Polish</div>
        <div class="step-desc">润色</div>
      </div>
      <div class="step">
        <div class="step-nb">03</div>
        <div class="step-title">Morph</div>
        <div class="step-desc">变形</div>
      </div>
      <div class="step">
        <div class="step-nb">04</div>
        <div class="step-title">Illustrate</div>
        <div class="step-desc">配图</div>
      </div>
      <div class="step">
        <div class="step-nb">05</div>
        <div class="step-title">Distribute</div>
        <div class="step-desc">分发</div>
      </div>
      <div class="step">
        <div class="step-nb">06</div>
        <div class="step-title">Measure</div>
        <div class="step-desc">复盘</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 15 · 工作流</div>
    <div>Workflow</div>
  </div>
</section>
```

**要点**：单组 `.pipeline` + `data-cols="6"`（CSS 支持 3/4/6 列）；整页垂直居中，上方可放说明。只有一条线性流程时用，比 A 更聚焦。

### 变体 C · 卡片分组式

```html
<section class="slide light">
  <div class="chrome">
    <div>工作流 · Workflow</div>
    <div>Act II · 15 / 27</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Pipeline · 流水线</div>
    <h2 class="h-xl">三阶段流程</h2>

    <div class="grid-3" style="margin-top:6vh; gap:3.6rem 2.7rem">
      <div class="pillar" style="padding:3vh 1.5vw; border:1px solid currentColor; border-color:rgba(127,127,127,.25)">
        <div class="ic">01</div>
        <div class="t">输入</div>
        <div class="d">原料采集与结构化。<br>文档、数据、素材入库。</div>
      </div>
      <div class="pillar" style="padding:3vh 1.5vw; border:1px solid currentColor; border-color:rgba(127,127,127,.25)">
        <div class="ic">02</div>
        <div class="t">加工</div>
        <div class="d">润色、变形、配图。<br>多平台格式同时产出。</div>
      </div>
      <div class="pillar" style="padding:3vh 1.5vw; border:1px solid currentColor; border-color:rgba(127,127,127,.25)">
        <div class="ic">03</div>
        <div class="t">分发</div>
        <div class="d">一键多渠道发布。<br>数据回流复盘。</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 15 · 工作流</div>
    <div>Workflow</div>
  </div>
</section>
```

**要点**：用 `.pillar` 卡片（带边框）按阶段分组，每卡 ic 序号 + 标题 + 描述；适合"流程阶段少但每阶段要解释"的场景，和 A/B 的步骤条完全不同观感。

---
