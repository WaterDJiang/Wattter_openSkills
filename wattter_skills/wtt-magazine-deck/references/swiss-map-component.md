# S08 + Swiss Map Component

> **S08 + Map 是版式 S08（Duo Compare）的右侧插槽扩展，不是新正文页。**
> 使用时仍写 `data-layout="S08"`，把右侧原本放对比内容的 `.col` 换成 `.history-map-grid` 即可。

## 使用场景

- 地理（城市、路线、位置）
- 历史（事件发生地、人物足迹）
- 关系（人物住所、机构位置）
- 城市关系（校区、门店、办公点）

不适用：纯时间线（用 S02/S11）、纯对比（用 S08 默认）、流程图（用 S14）。

## 必要 HTML 结构

```html
<section class="slide" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">章节 · 历程</div>
      <div class="r">08/NN</div>
    </div>
    <h2 class="h-xl-zh">标题：XX 事件 / XX 路线</h2>

    <div class="history-map-grid">
      <!-- 左侧：关系卡片（5 个 .relation-card） -->
      <aside class="history-side">
        <div class="history-side-head">
          <h3 style="font-weight:200">大说明文字</h3>
          <p>简述</p>
        </div>
        <div class="relation-card">
          <span class="pin-dot"></span>
          <div>
            <div class="nm">名称 01</div>
            <div class="mt">角色 / 描述</div>
          </div>
        </div>
        <!-- 4 个 .relation-card -->
      </aside>

      <!-- 右侧：MapLibre 地图（fallback 用静态 SVG） -->
      <div class="map-panel">
        <div class="map-title">
          <strong>RELATION MAP</strong><br>
          地点 / 人物 / 事件
        </div>
        <div class="map-controls">
          <button class="map-ctrl" data-map-ctrl="zoom-in">+</button>
          <button class="map-ctrl" data-map-ctrl="zoom-out">−</button>
          <button class="map-ctrl drag" data-map-ctrl="drag">DRAG</button>
        </div>
        <div id="swiss-map" class="swiss-map" data-points='[JSON]' data-relations='[JSON]'>
          <div class="map-static">
            <svg class="static-relations" viewBox="0 0 800 600">
              <!-- fallback 关系线 SVG（不写 <text>） -->
              <line x1="..." y1="..." x2="..." y2="..." stroke="#999" stroke-dasharray="2 2"/>
            </svg>
            <!-- 静态点位（CDN 失败时显示） -->
            <div class="static-marker" style="left:62%;top:68%">
              <span class="pin-dot"></span>
              <div class="pin-card">
                <div class="nm">顾维钧</div>
                <div class="mt">外交</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
```

## 数据契约

### `data-points`（点位）

```js
const MAP_POINTS = [
  { id: 'gu', name: '顾维钧', meta: '外交', coord: [117.2048, 39.1060], x: 62, y: 68, accent: true },
  // ...更多点位
];
```

- `coord`（可选）：经纬度 `[lng, lat]`，MapLibre 用
- `x` / `y`（可选）：百分比位置（0-100），static fallback 用
- `accent: true`：高亮此点位

### `data-relations`（关系）

```js
const MAP_RELATIONS = [
  ['gu', 'cao'],   // 顾维钧 → 曹
  ['cao', 'sun'],
];
```

- 每项 `[fromId, toId]`
- 渲染为虚线连接 + 端点高亮

## 外部依赖

```html
<!-- MapLibre -->
<link href="https://unpkg.com/maplibre-gl@5.14.0/dist/maplibre-gl.css" rel="stylesheet">
<script src="https://unpkg.com/maplibre-gl@5.14.0/dist/maplibre-gl.js"></script>
```

> **CDN 失败 fallback** 必须可读——所有点位 + 连线 + 卡片在 `.map-static` 里都有 SVG/CSS 实现。

## 硬规则

| # | 规则 |
|---|---|
| MM1 | 默认禁用 `scrollZoom` + `boxZoom` + `doubleClickZoom` + `dragPan`（避免触发 PPT 翻页） |
| MM2 | `DRAG` 按钮 toggle 后才允许拖动地图 |
| MM3 | 静态 fallback 必须可读（CDN / 瓦片失败时仍能看到点位 / 连线 / 卡片） |
| MM4 | SVG 只画 fallback 关系线，**禁止写可见 `<text>`**（所有文字标签用 HTML） |
| MM5 | `data-points` 至少 2 个，否则退回 S08 默认 duo-compare |
| MM6 | `<aside class="history-side">` 必须用 `display:grid;grid-template-rows:1.08fr repeat(4,1fr)` 排版 head + 4 个关系卡 |

## 配色（与 themes 配合）

- 历史连线 / 静态点位：`var(--ink)` / `var(--grey-3)` / `var(--accent)`
- 关系卡 `.relation-card`：背景 `var(--grey-1)`，数字/文字 `var(--ink)`
- 头部 `.history-side-head`：背景 `var(--accent)` + `var(--accent-on)`
- 控件 `.map-ctrl`：未激活时透明背景 + 1px `var(--ink)` 描边，激活时 `var(--accent)` 背景 + `var(--accent-on)` 文字

## 类名速查

| 类名 | 用途 |
|---|---|
| `.history-map-grid` | 整体布局（4.2fr 7.8fr） |
| `.history-side` | 左侧关系列表（head + 4 cards） |
| `.history-side-head` | 头部说明（accent 背景） |
| `.relation-card` | 单个关系卡（grid auto / 1fr） |
| `.map-panel` | 右侧地图容器 |
| `.map-title` | 地图左上标题（半透白底） |
| `.map-controls` | 地图右上控件组（+/−/DRAG） |
| `.map-ctrl` | 单个控件按钮（`min-width:32px`） |
| `.map-ctrl.drag` | DRAG 按钮（`min-width:58px`） |
| `.map-ctrl.active` | 激活态（accent 背景） |
| `.map-static` | 静态 fallback 容器 |
| `.static-marker` | 静态点位（百分比定位） |
| `.pin-dot` | 12px 圆点 |
| `.person-marker.accent` | accent 高亮点位 |
| `.pin-line` | 关系连线 |
| `.pin-card` | 卡片（72px+） |
