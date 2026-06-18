# Layouts · Linear 科技型

Linear 科技型用于产品发布、AI 工作流、工程团队、路线图、任务系统和 SaaS 产品演示。视觉关键词：深色产品界面、玻璃面板、细边框、issue 列表、roadmap 网格、agent command。

## LNR-01 · Product System Cover

封面。必须让主题色成为第一视觉印象，可用 `hero dark` 或 `accent`。

```html
<section class="slide hero dark" data-layout="LNR-01" data-anim="fade-up">
  <div class="chrome"><div class="left"><span>Product System</span><span class="sep"></span><span>Linear Tech</span></div><div class="right">01</div></div>
  <div class="frame grid-2-7-5">
    <div class="col center" style="align-items:flex-start;text-align:left">
      <div class="kicker">OPERATING SYSTEM</div>
      <h1 class="h-hero fit-safe-text">把产品开发变成一套可运行的系统</h1>
      <p class="lead">从反馈、路线图、issue 到 agent 执行，所有工作在一个高速界面里流动。</p>
    </div>
    <div class="linear-window" data-anim="zoom-pop">
      <div class="linear-window-head"><span class="linear-dot accent"></span><span class="linear-dot"></span><span class="linear-dot"></span></div>
      <div class="linear-code"><b>ENG-2703</b> Render UI before sync<br><em>Status</em> In Progress<br><em>Agent</em> Draft PR awaiting review</div>
    </div>
  </div>
</section>
```

## LNR-02 · Issue Board

任务流 / 功能列表页。适合讲工作流、产品模块、优先级。

```html
<section class="slide dark" data-layout="LNR-02" data-anim="stagger-list">
  <div class="linear-shell">
    <aside class="linear-sidebar">
      <div class="linear-brand"><span class="linear-mark"></span><span>Workspace</span></div>
      <nav class="linear-nav"><span class="active">Inbox <b>8</b></span><span>My issues <b>24</b></span><span>Reviews <b>3</b></span></nav>
    </aside>
    <main class="linear-main">
      <div class="meta-row"><span>Cycle 144</span><span>Core Product</span></div>
      <div class="linear-list">
        <div class="linear-row"><span class="linear-key">ENG-2085</span><span class="linear-title">Reduce UI flicker during autonomy handoff</span><span class="linear-pill">P1</span></div>
        <div class="linear-row"><span class="linear-key">ENG-2094</span><span class="linear-title">Add buffering for agent event streams</span><span class="linear-pill">AI</span></div>
      </div>
    </main>
  </div>
</section>
```

## LNR-03 · Metrics Grid

三列指标页。适合展示速度、质量、效率和增长数据。

```html
<section class="slide dark" data-layout="LNR-03" data-anim="counter-up">
  <div class="chrome"><div class="left"><span>Pulse</span><span class="sep"></span><span>Metrics</span></div><div class="right">03</div></div>
  <div class="frame">
    <div class="kicker">SYSTEM HEALTH</div>
    <h2 class="h-xl fit-safe-text">每个指标都指向下一步动作</h2>
    <div class="linear-grid">
      <div class="linear-card"><div class="label">Cycle time</div><div class="nb">-34%</div><div class="copy">从需求进入到合并，关键等待时间被压缩。</div></div>
      <div class="linear-card"><div class="label">Review load</div><div class="nb">2.1x</div><div class="copy">agent 输出被结构化，评审优先级更清晰。</div></div>
      <div class="linear-card"><div class="label">Signal</div><div class="nb">88</div><div class="copy">团队能在同一界面看到风险、进展与阻塞。</div></div>
    </div>
  </div>
</section>
```

## LNR-04 · Roadmap Timeline

路线图页。适合产品阶段、计划、里程碑。

```html
<section class="slide dark" data-layout="LNR-04" data-anim="stagger-list">
  <div class="chrome"><div class="left"><span>Roadmap</span><span class="sep"></span><span>Plan</span></div><div class="right">04</div></div>
  <div class="frame grid-2-5-7">
    <div class="col">
      <div class="kicker">VISUAL PLANNING</div>
      <h2 class="h-xl fit-safe-text">把方向、节奏和责任放在同一张图上</h2>
      <p class="lead">路线图不是静态汇报，而是团队每天会更新的操作面板。</p>
    </div>
    <div class="linear-card">
      <div class="meta-row"><span>FEB</span><span>MAR</span><span>APR</span><span>MAY</span><span>JUN</span><span>JUL</span></div>
      <div class="linear-timeline"><span class="linear-tick"></span><span class="linear-tick"></span><span class="linear-tick"></span><span class="linear-tick"></span><span class="linear-tick"></span><span class="linear-tick"></span></div>
    </div>
  </div>
</section>
```

## LNR-05 · Agent Command

AI agent / 自动化页。适合展示人机协作、命令、执行闭环。

```html
<section class="slide accent" data-layout="LNR-05" data-anim="zoom-pop">
  <div class="frame center">
    <div class="linear-command">
      <span class="prompt">@Linear</span>
      <span class="txt">create urgent issues, assign owners, draft the first PR</span>
    </div>
    <h2 class="h-xl fit-safe-text" style="margin-top:5vh">人类给方向，系统推动工作</h2>
  </div>
</section>
```

## LNR-06 · Closing System

收束页。适合结尾口号和下一步。

```html
<section class="slide hero dark" data-layout="LNR-06" data-anim="rise-in">
  <div class="frame center">
    <div class="kicker">NEXT OPERATING MODEL</div>
    <h2 class="h-hero fit-safe-text">Build with momentum.</h2>
    <p class="lead">把复杂产品开发收束成清晰、快速、可追踪的执行系统。</p>
  </div>
</section>
```
