# 页面布局库（Layouts）

本文档收录 **15 种**页面布局骨架，每种布局提供 **2-3 个构图变体**（A 默认 / B / C），直接替换文案/图片即可使用。**变体是本库的核心**：同一种布局在不同页重复出现时，必须换变体，避免版式雷同（见文末「变体变换规则」）。

---

## ⚠️ 生成前必读（Pre-flight）

### A. 类名必须来自 base.css

layouts.md 使用的所有类（`h-hero` / `h-xl` / `h-sub` / `h-md` / `lead` / `meta-row` / `stat-card` / `stat-label` / `stat-nb` / `stat-unit` / `stat-note` / `pipeline-section` / `pipeline-label` / `pipeline` / `step` / `step-nb` / `step-title` / `step-desc` / `grid-2-7-5` / `grid-2-6-6` / `grid-2-8-4` / `grid-2-5-7` / `grid-2-4-8` / `grid-3-3` / `grid-6` / `grid-3` / `grid-4` / `frame` / `frame-img` / `img-cap` / `callout` / `callout-src` / `kicker` / `timeline` / `tl-node` / `tl-year` / `tl-title` / `tl-desc` / `quote-wall` / `qw-item` / `qw-text` / `qw-cite` / `pillar` / `big-num` / `mid-num` / `bottom-left` / `bottom-right` / `rule`）都在 `css/base.css` 里预定义。

**不要发明新类名**。如果必须自定义，用 `style="..."` inline 写。生成前若不确定某个类是否存在，grep base.css 确认。

### A2. 动效标注（微动/沉浸模式）

每个布局骨架下方新增了推荐的 `data-anim` 和 `data-fx` 属性。静态模式可忽略这些属性。详见 `references/motions.md`。

### B. 图片比例规范（非常重要）

**永远用标准比例**，不要用原图 `aspect-ratio: 2592/1798` 这种奇葩比例：

| 场景 | 推荐比例 | 写法 |
|------|---------|------|
| 左文右图 主图 | 16:10 或 4:3 | `aspect-ratio:16/10; max-height:54vh` |
| 图片网格（多图对比） | 统一 | **固定 `height:26vh`，不用 aspect-ratio** |
| 左小图 + 右文字 | 1:1 或 3:2 | `aspect-ratio:1/1; max-width:40vw` |
| 全屏主视觉 | 16:9 | `aspect-ratio:16/9; max-height:64vh` |
| 图文混排小插图 | 3:2 | `aspect-ratio:3/2; max-width:30vw` |

图片必须包在 `<figure class="frame-img">` 里，里面的 `<img>` 会自动 `object-fit:cover + object-position:top center`，只裁底部，不裁顶/左/右。

**唯一例外**：全幅图叠加变体（Layout 4-C / 10-C）用 `position:absolute;inset:0` 把图当背景，此时**不套** `aspect-ratio` 也不套 `height:Nvh`，但图必须 ≥1920px 宽且构图中心在文字反方向。

### C. 图片定位准则（避免图片堆到页面最底部、被浏览器工具栏遮挡）

**错误做法**（已踩坑，不要再犯）：
- 在非 grid 容器里用 `align-self:end`：`align-self` 在 flex/grid 之外完全无效，图片会掉到文档流末尾堆底
- 用 `position:absolute + bottom:0` 把图"固定"到底：会被底部 `.foot` 和 `#nav` 圆点遮挡
- 单张图片只写 `height:N vh` 不限 `max-height`：在低分屏会撑出视口

**正确做法**：
- 图文混排**必须用 `.frame.grid-2-7-5`**（或 `.grid-2-6-6` / `.grid-2-8-4` / 镜像 `.grid-2-5-7` / `.grid-2-4-8`）的 grid 结构
- grid 容器默认 `align-items:start`（已在 template 中设置），图片自然贴到 cell 顶端
- 如果需要"图片底对齐左列 callout"：**左列用 flex column + `justify-content:space-between`**（让 callout 自己贴左列底），**右列 figure 直接保持 align-items:start 即可**，不要加 `align-self:end`
- 所有 grid 父容器建议加 inline `style="padding-top:6vh"`，给标题区留呼吸空间

### D. 主题色与主题节奏

- 主题色从 `references/themes.md` 的 5 套预设里选一套,不允许自定义 hex 值
- 主题节奏(每页用 light / dark / hero light / hero dark 哪一个)在下文"主题节奏规划"一节有硬规则,生成前必读
- 两件事都要在挑布局之前决定,避免返工

---

## 0. 基础结构（所有 slide 都一样）

```html
<section class="slide [light|dark|hero light|hero dark]">
  <div class="chrome">
    <div>上下文标签 · 子标签</div>
    <div>ACT · 页号 / 总页数</div>
  </div>
  <!-- 主内容 -->
  <div class="foot">
    <div>页码说明 · Page Description</div>
    <div>— · —</div>
  </div>
</section>
```

- 非 hero 页建议加 `light` 或 `dark` 主题；hero 页加 `hero light` 或 `hero dark`（参与 WebGL 主题插值）
- `chrome` 和 `foot` 是可选但推荐保留的上下左右四角元数据
- **hero 页用于章节封面/开场/收束/转场**，非 hero 页用于正文

### ⚠️ chrome 和 kicker 不要写同一句话

这是最常见的内容重复问题。两者在语义上完全不同的维度：

| 位置 | 角色 | 内容性质 | 例子 |
|------|------|---------|------|
| `.chrome` 左上 | **杂志页眉 / 导航元数据** | 稳定的"栏目名"或"章节分类"，跨多页可以相同 | "Act II · Workflow" / "Data · Result" / "2026.04" |
| `.chrome` 右上 | **页号 + 幕号** | 固定格式 | "Act II · 15 / 25" |
| `.kicker` | **这一页独一份的引导句** | 是大标题的"小前缀"，像杂志大标题上方的一行话，每页都应不同 | "BUT" / "一个人,做了什么。" / "Phase 01 · 设计阶段" |

**反例**（已踩坑）：chrome 写"设计先行 · Design First"，kicker 又写"Phase 01 · 设计阶段"——意思重复，读者一眼就觉得 AI 生成的。

**正确做法**：chrome 是**栏目标签**（稳定、跨页可复用），kicker 是**本页钩子**（短句、有戏剧性），两者互为补充，不互相翻译。

### ⚠️ 主题节奏规划（必读 · 生成前必做)

**核心机制**:每页 `<section>` 必须带 `light` / `dark` / `hero light` / `hero dark` 之一。JS 根据 class 推断主题,决定 body 加不加 `light-bg`,从而切换暗/亮两张 WebGL canvas 哪张在前。不带主题或写自定义名 = fallback 出错。

#### 按布局的主题默认值

| Layout | 默认主题 | 原因 |
|---|---|---|
| 1. 开场封面 | `hero dark` | 开场仪式感,暗底强冲击 |
| 2. 章节幕封 | `hero dark` 与 `hero light` **必须交替** | 呼吸节奏 |
| 3. 大字报(数据) | `light` | 数字需纸白底;多幕连发时可偶插 `dark` |
| 4. 左文右图 | **`light` / `dark` 交替** | 正文节奏主力 |
| 5. 图片网格 | `light` | 截图需亮底 |
| 6. Pipeline | `light` | 流程图需清晰 |
| 7. 问题页 | `hero dark` | 强视觉冲击默认 |
| 8. 大引用 | **`dark` 优先**,偶用 `light` | 金句仪式感靠暗底 |
| 9. 对比页 | `light` | 双列需清晰 |
| 10. 图文混排 | **`light` / `dark` 交替** | 节奏 |
| 11. 时间轴 | `light` / `dark` 交替 | 节奏 |
| 12. 单数字大字 | `hero dark` 优先 | 单数字靠暗底+WebGL 放大冲击 |
| 13. 引用墙 | `light` | 多条文字需清晰底 |
| 14. 三栏并列 | `light` | 三卡需清晰 |
| 15. 双页跨页 | `light` / `dark` 交替 | 节奏 |

#### 节奏硬规则(生成后 grep 自检)

- ❌ **禁止**连续 3 页以上相同主题(包括 light 堆叠和 dark 堆叠)
- ❌ **禁止**6 页以上的 deck 没有至少 1 个 `hero dark` + 1 个 `hero light`
- ❌ **禁止**整个 deck 只有 `light` 正文页没有任何 `dark` 正文页——会显得平淡、没呼吸
- ✅ **推荐**每 3-4 页插入 1 个 hero(封面/幕封/问题/大引用)

#### 不同页数的节奏模板

**6 页节奏模板（短分享）**：

| 页 | 主题 | 布局 | 备注 |
|---|---|---|---|
| 1 | `hero dark` | 封面 | 开场 |
| 2 | `light` | 大字报 / 左文右图 | 核心内容 |
| 3 | `dark` | 左文右图 / 大引用 | 呼吸 |
| 4 | `light` | Pipeline / 图片网格 | 补充 |
| 5 | `hero light` | 问题页 / 幕封 | 转折 |
| 6 | `dark` | 大引用 / 收束 | 收尾 |

**8 页节奏模板**：

| 页 | 主题 | 布局 | 备注 |
|---|---|---|---|
| 1 | `hero dark` | 封面 | 开场 |
| 2 | `light` | 大字报 | 数据抛出 |
| 3 | `dark` | 左文右图 | 对比/故事 |
| 4 | `light` | Pipeline | 流程 |
| 5 | `hero light` | 章节幕封 | 呼吸 |
| 6 | `dark` | 左文右图 or 大引用 | |
| 7 | `hero dark` | 问题页 | 悬念收束 |
| 8 | `light` | 大引用/结尾 | 收尾 |

**12 页节奏模板（标准分享）**：

| 页 | 主题 | 布局 | 备注 |
|---|---|---|---|
| 1 | `hero dark` | 封面 | 开场 |
| 2 | `light` | 大字报 | 数据冲击 |
| 3 | `dark` | 左文右图 | 故事/对比 |
| 4 | `light` | Pipeline / 图片网格 | 证据 |
| 5 | `hero light` | 幕封 | 第一幕结束 |
| 6 | `dark` | 左文右图 | 第二幕开始 |
| 7 | `light` | 图文混排 | 深入 |
| 8 | `dark` | 大引用 | 金句 |
| 9 | `light` | 对比页 | 范式转变 |
| 10 | `dark` | 左文右图 / 图文混排 | |
| 11 | `hero dark` | 问题页 | 悬念 |
| 12 | `light` | 大引用 / 收束 | 结尾 |

**先画这张表对齐,再动手写 slide**。跳过规划直接粘骨架 = 全是 light。

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

## Layout 3: 数据大字报（Big Numbers Grid）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 3×2 网格 (grid-6) | 默认，6 个指标 |
| **B** | 2×2 大格 (grid-4) | 只有 4 个核心指标、想让数字更大 |
| **C** | 横向数据条 (grid-3) | 3 个指标横排一行，配大段说明 |

### 变体 A · 3×2 网格（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>数据 · Data</div>
    <div>Act I / Data · 02 / 25</div>
  </div>
  <div class="frame" style="padding-top:6vh">
    <div class="kicker">标题引导语</div>
    <h2 class="h-xl">数据页标题</h2>
    <p class="lead" style="margin-bottom:5vh">补充说明。</p>

    <div class="grid-6" style="margin-top:6vh">
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">64 <span class="stat-unit">天</span></div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">110K+</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">5,166</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">41K+</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">19</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">608+</div>
        <div class="stat-note">注释说明</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>项目 · 名称</div>
    <div>Act I · Data</div>
  </div>
</section>
```

**要点**：3×2 `grid-6`；每个 `stat-card` 固定 label→nb→note；数字 2-3 位用 K/M 简写；留 5vh 上方缓冲。

### 变体 B · 2×2 大格

```html
<section class="slide light">
  <div class="chrome">
    <div>数据 · Data</div>
    <div>Act I / Data · 02 / 25</div>
  </div>
  <div class="frame" style="padding-top:6vh">
    <div class="kicker">标题引导语</div>
    <h2 class="h-xl">数据页标题</h2>
    <p class="lead" style="margin-bottom:6vh">补充说明。</p>

    <div class="grid-4" style="margin-top:4vh">
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">110K+</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">5,166</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">41K+</div>
        <div class="stat-note">注释说明</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">19</div>
        <div class="stat-note">注释说明</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>项目 · 名称</div>
    <div>Act I · Data</div>
  </div>
</section>
```

**要点**：`grid-4` 是 2×2，CSS 已让 `.grid-4 .stat-card .stat-nb` 字号更大（9rem）；只有 3-4 个硬指标时用这个，数字更震撼。**同一个 deck 里不要 A、B 连用**——两者都是网格大字报，会雷同；要换就换成 C 或别的布局。

### 变体 C · 横向数据条

```html
<section class="slide light">
  <div class="chrome">
    <div>数据 · Data</div>
    <div>Act I / Data · 02 / 25</div>
  </div>
  <div class="frame grid-2-8-4" style="padding-top:6vh">
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:4vh">
      <div>
        <div class="kicker">标题引导语</div>
        <h2 class="h-xl">数据页标题</h2>
        <p class="lead" style="margin-top:3vh">补充说明段落，可以比 A/B 变体写得更长，讲清这三个数字背后的故事。</p>
      </div>
      <div class="callout">
        "一句话点破这三个数字的关系。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
    <div class="grid-3" style="gap:2.4rem 2rem; align-content:center">
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">110K+</div>
        <div class="stat-note">注释</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">5,166</div>
        <div class="stat-note">注释</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Label</div>
        <div class="stat-nb">19</div>
        <div class="stat-note">注释</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>项目 · 名称</div>
    <div>Act I · Data</div>
  </div>
</section>
```

**要点**：左文右数据，3 个 stat 横排一行（`grid-3`）；适合"数字少但要讲故事"的页——左边可以放大段说明 + callout。和 A/B 的纯网格构图完全不同。

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

## Layout 5: 图片网格（多图对比）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 3×2 网格 (grid-3-3) | 默认，6 张图对比 |
| **B** | 2×2 大图 | 4 张关键截图，每张更大更清晰 |
| **C** | 1 大 + 多小（非对称） | 1 张主图 + 3-4 张细节辅图 |

### 变体 A · 3×2 网格（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>实证 · Proof</div>
    <div>Act I · 05 / 27</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Proof · 实证</div>
    <h2 class="h-xl">6 张截图</h2>

    <div class="grid-3-3" style="margin-top:4vh">
      <figure class="frame-img" style="height:26vh">
        <img src="images/01.png" alt="说明1">
        <figcaption class="img-cap">说明1</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/02.png" alt="说明2">
        <figcaption class="img-cap">说明2</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/03.png" alt="说明3">
        <figcaption class="img-cap">说明3</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/04.png" alt="说明4">
        <figcaption class="img-cap">说明4</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/05.png" alt="说明5">
        <figcaption class="img-cap">说明5</figcaption>
      </figure>
      <figure class="frame-img" style="height:26vh">
        <img src="images/06.png" alt="说明6">
        <figcaption class="img-cap">说明6</figcaption>
      </figure>
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>Page 05 · 实证</div>
  </div>
</section>
```

**要点**：每个 `frame-img` 写死 `height:26vh`（不用 aspect-ratio）；`grid-3-3`（3×2）承载。

### 变体 B · 2×2 大图

```html
<section class="slide light">
  <div class="chrome">
    <div>实证 · Proof</div>
    <div>Act I · 05 / 27</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Proof · 实证</div>
    <h2 class="h-xl">4 张关键截图</h2>

    <div class="grid-4" style="margin-top:4vh">
      <figure class="frame-img" style="height:34vh">
        <img src="images/01.png" alt="说明1">
        <figcaption class="img-cap">说明1</figcaption>
      </figure>
      <figure class="frame-img" style="height:34vh">
        <img src="images/02.png" alt="说明2">
        <figcaption class="img-cap">说明2</figcaption>
      </figure>
      <figure class="frame-img" style="height:34vh">
        <img src="images/03.png" alt="说明3">
        <figcaption class="img-cap">说明3</figcaption>
      </figure>
      <figure class="frame-img" style="height:34vh">
        <img src="images/04.png" alt="说明4">
        <figcaption class="img-cap">说明4</figcaption>
      </figure>
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>Page 05 · 实证</div>
  </div>
</section>
```

**要点**：`grid-4` 2×2，每张 `height:34vh` 比 A 更大；4 张图够用时优先这个，单图更清晰。和 A 都是"等分网格"，**同 deck 不要 A、B 连用**。

### 变体 C · 1 大 + 多小（非对称）

```html
<section class="slide light">
  <div class="chrome">
    <div>实证 · Proof</div>
    <div>Act I · 05 / 27</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Proof · 实证</div>
    <h2 class="h-xl">主图 + 细节</h2>

    <div style="display:grid; grid-template-columns:5fr 4fr; gap:2.4rem 2.7rem; margin-top:4vh">
      <figure class="frame-img" style="height:54vh">
        <img src="images/01-hero.png" alt="主图">
        <figcaption class="img-cap">主图说明</figcaption>
      </figure>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:2.4rem 2.7rem">
        <figure class="frame-img" style="height:26vh">
          <img src="images/02.png" alt="说明2">
          <figcaption class="img-cap">说明2</figcaption>
        </figure>
        <figure class="frame-img" style="height:26vh">
          <img src="images/03.png" alt="说明3">
          <figcaption class="img-cap">说明3</figcaption>
        </figure>
        <figure class="frame-img" style="height:26vh">
          <img src="images/04.png" alt="说明4">
          <figcaption class="img-cap">说明4</figcaption>
        </figure>
        <figure class="frame-img" style="height:26vh">
          <img src="images/05.png" alt="说明5">
          <figcaption class="img-cap">说明5</figcaption>
        </figure>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>Page 05 · 实证</div>
  </div>
</section>
```

**要点**：左大图（5fr、54vh）+ 右 2×2 小图（各 26vh），非对称构图；适合"一张总览 + 多张细节"的展示，比等分网格更有叙事。内联 grid 是允许的（Pre-flight A：自定义用 inline）。

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

## Layout 10: 图文混排（Lead Image + Side Text）

| 变体 | 构图 | 何时用 |
|---|---|---|
| **A** | 8:4 左文右辅图 | 默认，正文为主、图为辅 |
| **B** | 4:8 左图右文（镜像） | 图为主、文为辅 |
| **C** | 图作背景叠加 | 图当背景、文字叠在上面 |

### 变体 A · 8:4 左文右辅图（默认）

```html
<section class="slide light">
  <div class="chrome">
    <div>Design First · 设计先行</div>
    <div>08 / 16</div>
  </div>
  <div class="frame grid-2-8-4" style="padding-top:6vh">
    <div>
      <div class="kicker">Phase 01 · 阶段</div>
      <h2 class="h-xl" style="margin-top:1vh; margin-bottom:3vh">页面标题</h2>

      <p class="lead" style="margin-bottom:3vh">
        核心段落说明。
      </p>

      <p style="font-family:var(--sans-zh); font-size:max(14px,1.15vw); line-height:1.75; opacity:.78; margin-bottom:2.4vh">
        补充说明段落。
      </p>

      <div class="callout" style="margin-top:3vh">
        "引用文字。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
    <figure class="frame-img" style="aspect-ratio:3/4; max-height:60vh">
      <img src="images/example.png" alt="说明">
      <figcaption class="img-cap">图片说明</figcaption>
    </figure>
  </div>
  <div class="foot">
    <div>Page 08 · 说明</div>
    <div>阶段标签</div>
  </div>
</section>
```

**要点**：`grid-2-8-4`（8:4）正文为主、图为辅；左列 kicker→大标题→lead→正文→callout 多层级；右图竖版 3:4。

### 变体 B · 4:8 左图右文（镜像）

```html
<section class="slide dark">
  <div class="chrome">
    <div>Design First · 设计先行</div>
    <div>08 / 16</div>
  </div>
  <div class="frame grid-2-4-8" style="padding-top:6vh">
    <figure class="frame-img" style="aspect-ratio:3/4; max-height:64vh">
      <img src="images/example.png" alt="说明">
      <figcaption class="img-cap">图片说明</figcaption>
    </figure>
    <div>
      <div class="kicker">Phase 01 · 阶段</div>
      <h2 class="h-xl" style="margin-top:1vh; margin-bottom:3vh">页面标题</h2>
      <p class="lead" style="margin-bottom:3vh">核心段落说明。</p>
      <p style="font-family:var(--sans-zh); font-size:max(14px,1.15vw); line-height:1.75; opacity:.78; margin-bottom:2.4vh">补充说明段落。</p>
      <div class="callout" style="margin-top:3vh">
        "引用文字。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 08 · 说明</div>
    <div>阶段标签</div>
  </div>
</section>
```

**要点**：`grid-2-4-8`（4:8）图在左、文在右；**和 A 是镜像变体，同 deck 两页都用 Layout 10 时必须一页 A 一页 B**。配 `dark` 主题换节奏。

### 变体 C · 图作背景叠加

```html
<section class="slide hero light">
  <div class="chrome" style="position:relative; z-index:2">
    <div>Design First · 设计先行</div>
    <div>08 / 16</div>
  </div>
  <figure class="frame-img" style="position:absolute; inset:0; width:100%; height:100%; border-radius:0; z-index:0">
    <img src="images/example.png" alt="说明" style="object-position:center">
  </figure>
  <div class="bottom-right" style="z-index:2; max-width:44vw; text-align:right">
    <div class="kicker">Phase 01 · 阶段</div>
    <h2 class="h-xl" style="font-size:6vw; line-height:1.05; margin-top:1vh">页面标题</h2>
    <p class="lead" style="margin-top:2vh; max-width:38vw; margin-left:auto">核心段落说明，压在图右上角。</p>
  </div>
  <div class="foot" style="position:relative; z-index:2">
    <div>Page 08 · 说明</div>
    <div>阶段标签</div>
  </div>
</section>
```

**要点**：图 `position:absolute;inset:0` 当背景（Pre-flight B 例外），文字用 `.bottom-right` 压右下；和 Layout 4-C 的区别是 4-C 文字压**左下**且偏 hero 冲击、本变体压**右下**且偏图文叙事。同 deck 全幅叠加页（4-C + 10-C）合计不要超过 2 个。

---

## Layout 11: 时间轴（Timeline · 纵向节点）

适合发展历程、路线图、产品演进、个人/公司编年史。

```html
<section class="slide light">
  <div class="chrome">
    <div>历程 · Timeline</div>
    <div>Act I · 04 / 25</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Timeline · 编年</div>
    <h2 class="h-xl" style="margin-bottom:6vh">发展历程</h2>

    <div class="timeline">
      <div class="tl-node">
        <div class="tl-year">2019</div>
        <div>
          <div class="tl-title">起点</div>
          <div class="tl-desc">一个人、一台电脑，开始做这件事的描述。</div>
        </div>
      </div>
      <div class="tl-node">
        <div class="tl-year">2021</div>
        <div>
          <div class="tl-title">第一个转折</div>
          <div class="tl-desc">遇到了关键问题或机会的描述。</div>
        </div>
      </div>
      <div class="tl-node">
        <div class="tl-year">2023</div>
        <div>
          <div class="tl-title">规模化</div>
          <div class="tl-desc">从一个人变成一个体系的描述。</div>
        </div>
      </div>
      <div class="tl-node">
        <div class="tl-year">2026</div>
        <div>
          <div class="tl-title">现在</div>
          <div class="tl-desc">当下状态与下一步的描述。</div>
        </div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 04 · 历程</div>
    <div>Timeline</div>
  </div>
</section>
```

**要点**：
- 纵向时间轴，左列 `tl-year`（英文斜体年份）+ 右列 `tl-title`/`tl-desc`，节点间 `border-top` 分隔
- 节点数 4-6 个最稳，超过 6 个拆成两页或砍细节
- 想要横向时间轴？直接用 Layout 6 的 `.pipeline`，把 `step-nb` 换成年份即可——**不要**在同一 deck 里纵向横向都用，选一种

---

## Layout 12: 单数字大字（Single Hero Number）

一个巨型数字占满页面 + 一句注解。比 Layout 3 更聚焦——只讲一个数字。

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>核心数据 · The Number</div>
    <div>02 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:4vh; align-content:center; min-height:80vh">
    <div class="kicker">The Number · 一个数字</div>
    <div class="big-num" style="font-size:22vw; line-height:.85">1,284</div>
    <p class="lead" style="max-width:50vw">
      一句话讲清这个数字意味着什么。
    </p>
    <div class="meta-row">
      <span>来源 · 出处</span><span>·</span><span>截至 2026.04</span>
    </div>
  </div>
  <div class="foot">
    <div>Page 02 · 核心数据</div>
    <div>The Number</div>
  </div>
</section>
```

**要点**：
- 用 `.big-num`（Playfair 800）放一个数字，inline `font-size:22vw` 顶满；数字 ≤ 5 字符最稳（千分位逗号算 1 字符）
- 配 `hero dark`，WebGL 透出让数字漂浮感更强
- 适合"开场第二个硬数据"或"转折页抛一个惊人数字"
- 数字可加单位：`1,284<em style="font-size:.32em; opacity:.5; font-style:normal"> 次</em>`

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

## Layout 15: 双页跨页（Magazine Spread）

模拟杂志跨页：左右两页对照，中间竖线分隔，每侧独立的 kicker + 标题 + 内容。

```html
<section class="slide light">
  <div class="chrome">
    <div>跨页 · Spread</div>
    <div>Act II · 11 / 25</div>
  </div>
  <div class="frame" style="display:grid; grid-template-columns:1fr 1px 1fr; gap:0 3.6rem; align-items:stretch; padding-top:5vh">
    <!-- 左页 -->
    <div style="display:flex; flex-direction:column; gap:3vh">
      <div class="kicker">左页 · Left Page</div>
      <h2 class="h-xl" style="font-size:5vw">左侧标题</h2>
      <p class="lead" style="font-size:1.6rem">左侧正文段落，讲一个侧面。</p>
      <p style="font-family:var(--sans-zh); font-size:max(14px,1.1vw); line-height:1.75; opacity:.78; margin-top:auto">左侧补充说明，贴底。</p>
    </div>
    <!-- 中线 -->
    <div class="rule v" style="height:100%"></div>
    <!-- 右页 -->
    <div style="display:flex; flex-direction:column; gap:3vh">
      <div class="kicker">右页 · Right Page</div>
      <h2 class="h-xl" style="font-size:5vw">右侧标题</h2>
      <p class="lead" style="font-size:1.6rem">右侧正文段落，讲另一个侧面。</p>
      <div class="callout" style="margin-top:auto">
        "右侧引用压底。"
        <div class="callout-src">— 出处</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 11 · 跨页</div>
    <div>Spread</div>
  </div>
</section>
```

**要点**：
- 内联 3 列网格 `1fr 1px 1fr`，中间一列放 `.rule.v` 竖线；左右两页各自 `flex column`，内容可不同结构（一侧文一侧图也行）
- 适合"两个对等概念并置但都不是'旧vs新'"的页（那样用 Layout 9）；跨页感来自中线 + 左右独立 kicker
- 标题字号比单页小（5vw），因为要容下两列

---

## 附录：常用网格模板

| 类名 | 配比 | 用途 |
|---|---|---|
| `.grid-2-6-6` | 6:6（1:1） | 对半分 |
| `.grid-2-7-5` | 7:5 | 文字为主 + 辅助图 |
| `.grid-2-8-4` | 8:4（2:1） | 大段文字 + 小图/数据 |
| `.grid-2-5-7` | 5:7 | 图为主 + 辅助字（7:5 的镜像） |
| `.grid-2-4-8` | 4:8 | 图为主 + 大段字（8:4 的镜像） |
| `.grid-3` | 1:1:1 | 3 项并列（案例/截图/支柱） |
| `.grid-3-3` | 3×2 | 6 图矩阵 |
| `.grid-6` | 3×2 | 6 个数据卡片 |
| `.grid-4` | 2×2 | 4 个数据卡片 / 4 大图 |

所有网格都预留 `gap`，可以单独覆写。

---

## ⚠️ 变体变换规则（避免版式雷同 · 生成后必查）

这是本库存在的核心目的。**同一种布局的默认变体如果被反复使用，版式就会"固定"**。生成时必须遵守：

1. **同布局重复必须换变体**：一个 deck 里 Layout 4 出现两次，第二次必须用不同变体（A→B 或 A→C），不允许两页都是 A。
2. **相邻两页构图不得相同**：相邻 slide 的 grid 比例 / 方向（左字右图 vs 左图右字）/ 结构（网格 vs 堆叠 vs 全幅）至少有一项不同。
3. **grid 比例有意混用**：不要全 deck 都是 `grid-2-7-5`。7:5 / 5:7 / 8:4 / 6:6 / 3 栏要穿插。
4. **等分类布局不连用**：Layout 3-A（3×2）和 3-B（2×2）都是等分大字报网格，不要相邻；Layout 5-A 和 5-B 同理。要换就换成 C 或换布局。
5. **全幅叠加页克制**：Layout 4-C / 10-C 这类全幅图背景页，整个 deck 合计 ≤ 2 个。
6. **hero 页不堆叠**：连续两页都 hero（封面+幕封除外）会过重，hero 与正文页 2-3:1 交错。

**生成后自检**（grep + 目视）：

```bash
# 列出每页主题，确认节奏交错
grep 'class="slide' index.html
# 列出所有用到的 grid 比例，确认有混用（不应只有一个值）
grep -oE 'grid-2-[0-9]+-[0-9]+|grid-[0-9]+' index.html | sort | uniq -c
```

目视逐页扫一遍：有没有两页看起来"构图几乎一样"？有就回去换变体。

---

## 页面节奏建议

根据实际页数选择节奏：

**短 deck（5-8 页）**：
1. **Hero Cover** → 2-3 个正文页（light/dark 交替，布局换变体） → **Hero Question / Big Quote** 收束

**标准 deck（10-15 页）**：
1. **Hero Cover**（第 1 页）
2. **Act Divider**（第一幕开场，hero light 或 hero dark）
3. **Big Numbers / Single Hero Number**（抛硬数据制造冲击）
4. **Quote + Image**（讲故事）
5. **Image Grid / Timeline**（证据/历程）
6. **Hero Question**（幕收束，留悬念）
7. ... 第二幕同样节奏，布局换变体 ...
8. **Hero Close**（最后一页，问题或致谢）

**长 deck（20+ 页）**：
- 每 5-8 页一组幕，幕间用 Act Divider
- 幕内 3-4 正文页 + 1 hero 页交替
- 控制每个幕的页数大致均衡
- 跨幕重复使用同一布局时，**必须换变体**（见上「变体变换规则」）

hero 页与 non-hero 页应该 **2-3 : 1 比例交错**，不要连续超过 3 页 non-hero，也不要连续超过 2 页 hero。
