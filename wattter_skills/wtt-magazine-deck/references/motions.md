# 动效模式参考（Motions）

三档动效模式，在 Step 1 需求澄清时由用户选择（或根据场景推荐）。

---

## 模式总览

| | 静态 | 微动 | 沉浸 |
|---|---|---|---|
| **入场动画** | 无 | 27 种 CSS keyframes | 27 种 CSS keyframes |
| **counter-up** | 无 | 有 | 有 |
| **动画重播** | 无 | 每次切页重放 `data-anim` | 每次切页重放 |
| **Canvas FX** | 无 | 无 | 20 种（含 4 种经典 + 16 种新增） |
| **WebGL 背景** | 无（纯色） | hero 页可见 | hero 页可见 |
| **Overview 网格** | 无 | 无 | O 键触发 |
| **Notes 抽屉** | 无 | 无 | N 键触发 |
| **演示者模式** | 无 | 无 | S 键弹出 |
| **动画循环** | 无 | 无 | A 键循环当前 slide 动画 |
| **Hash 深链接** | 无 | 有 | 有 |
| **进度条** | 无 | 有 | 有 |
| **主题热切换** | T 键切换当前风格预设主题 | T 键切换当前风格预设主题 | T 键切换当前风格预设主题 |
| **输出文件** | base.css + theme.css + nav.js | + animations.css + subtle.js | + fx/fx-runtime.js + cinematic.js |

---

## CSS 入场动画（微动 + 沉浸共享）

在 HTML 元素上加 `data-anim="动画名"` 声明，切页时自动触发。

### 方向渐入

| 动画名 | 效果 | 推荐使用 |
|---|---|---|
| `fade-up` | 从下方 32px 浮入 + opacity | 通用，标题、正文、卡片 |
| `fade-down` | 从上方 32px 浮入 + opacity | 少用，特殊布局 |
| `fade-left` | 从左侧 40px 滑入 + opacity | 右列元素 |
| `fade-right` | 从右侧 40px 滑入 + opacity | 左列元素 |

### 质感进入

| 动画名 | 效果 | 推荐使用 |
|---|---|---|
| `rise-in` | translateY(60px) + scale(0.97) + blur(6px) | Hero 大标题，最有质感 |
| `drop-in` | 从上方 60px 掉落 + scale(0.97) | 重大消息、标题从天而降 |
| `zoom-pop` | scale(0.6) → 1.04 → 1 弹性 | 数据数字、强调元素 |
| `blur-in` | filter blur(18px) 渐清 | 特殊视觉页 |
| `glitch-in` | 水平抖动 + clip-path 切片 | 科技感、故障风格 |

### 文字特效

| 动画名 | 效果 | 推荐使用 |
|---|---|---|
| `typewriter` | 逐字显现 + 闪烁光标 | 英文 display 标题 |
| `neon-glow` | text-shadow 呼吸发光 | 霓虹风格标题 |
| `shimmer-sweep` | 光泽横扫伪元素 | 金色/银色主题点缀 |
| `gradient-flow` | 渐变色流动文字 | 强调标题、品牌名 |

### 页面级揭示

| 动画名 | 效果 | 推荐使用 |
|---|---|---|
| `spotlight` | clip-path circle 从中心展开 | Hero 页全页揭示 |
| `ripple-reveal` | clip-path circle 从左下角展开 | 幕封页、数据页 |
| `confetti-burst` | 彩纸伪元素爆散（纯 CSS） | 庆祝/发布页点缀 |

### 3D 变换

| 动画名 | 效果 | 推荐使用 |
|---|---|---|
| `card-flip-3d` | rotateY(-90deg) → 0 卡片翻转 | 卡片式内容揭示 |
| `cube-rotate-3d` | 3D 立方旋转入场 | 科技/产品页 |
| `page-turn-3d` | rotateY(-85deg) 翻页效果 | 书本/叙事页 |
| `perspective-zoom` | 景深缩放从远处推近 | 沉浸式内容揭示 |

### 其他特效

| 动画名 | 效果 | 推荐使用 |
|---|---|---|
| `stagger-list` | 子元素依次延迟进入 | 列表、卡片组、pipeline |
| `path-draw` | SVG stroke-dashoffset 递减 | 图标绘制、流程图 |
| `parallax-tilt` | hover 时 3D 微倾 | 卡片交互 |
| `marquee-scroll` | translateX 无限滚动 | 品牌墙、合作伙伴 logo |
| `kenburns` | 内部 img 慢速 zoom+pan | 图片容器 |
| `morph-shape` | SVG path d 属性变形 | 装饰性图形 |
| `counter-up` | JS 驱动数字递增 | 数据数字 |

### 自定义参数

```html
<!-- 自定义时长 -->
<h2 data-anim="fade-up" data-anim-dur="1.2s">标题</h2>

<!-- 自定义延迟 -->
<div data-anim="fade-up" data-anim-delay="0.3s">延迟 0.3s 出现</div>

<!-- stagger-list 自动为子元素设置递增延迟 -->
<div class="grid-3" data-anim="stagger-list">
  <div>第一个</div>   <!-- 0.05s -->
  <div>第二个</div>   <!-- 0.15s -->
  <div>第三个</div>   <!-- 0.25s -->
</div>
```

### 推荐搭配

| 页面类型 | 推荐动画 | 加在哪个元素 |
|---|---|---|
| Hero 封面 | `spotlight` 或 `ripple-reveal` | `<section>` 上 |
| 幕封 | `ripple-reveal` | `<section>` 上 |
| 数据大字报 | `stagger-list` | grid 容器上 |
| 双列内容 | `fade-up` | 左列文字容器 |
| 图片网格 | `stagger-list` | grid 容器上 |
| 大引用 | `rise-in` | callout 容器上 |
| 收束页 | `fade-up` | `<section>` 上 |
| 图片容器 | `kenburns` | `.frame-img` 父级 |
| 科技标题 | `glitch-in` 或 `neon-glow` | 标题元素 |
| 品牌文字 | `gradient-flow` | 标题元素 |
| 3D 卡片 | `card-flip-3d` | 卡片容器 |

---

## Counter-up 数字递增

在含数字的元素上加 `.counter` 类和 `data-to` 属性：

```html
<!-- 从 0 数到 128 -->
<span class="counter" data-to="128">0</span>

<!-- 浮点数，保留 1 位小数 -->
<span class="counter" data-to="3.7" data-decimals="1">0</span>

<!-- 自定义时长（毫秒） -->
<span class="counter" data-to="500" data-dur="2000">0</span>

<!-- 带后缀 -->
<span class="counter" data-to="99" data-suffix="%">0</span>
```

推荐放在 `.stat-nb` 内，与 stat-card 搭配效果最佳。

---

## Canvas FX（仅沉浸模式）

在元素上加 `data-fx="FX名"` 声明。FX 通过 fx-runtime.js 自动加载和生命周期管理。FX 会自动读取当前主题色适配明暗。

### 经典 FX（4 种）

| FX 名 | 效果 | 推荐使用 |
|---|---|---|
| `constellation` | 70 个漂浮点 + 距离连线 | Dark hero 页背景容器 |
| `gradient-blob` | 4 个模糊光球叠加漂移 | Light hero 页背景容器 |
| `sparkle-trail` | 跟随鼠标的星光粒子 + 空闲自游走 | 互动展示页、demo 页 |
| `particle-burst` | 从中心爆开 + 重力 + 阻力，每 3 秒循环 | 关键数据揭示页 |

### 新增 FX（16 种）

| FX 名 | 效果 | 推荐使用 |
|---|---|---|
| `confetti-cannon` | 从两侧底部喷射彩纸，3 秒循环 | 庆祝/发布/里程碑页 |
| `firework` | 火箭升空 + 爆裂，0.7 秒一次 | 节日/高潮/产品发布 |
| `starfield` | 从中心向外扩散的星点 | 宇宙/科技/宏观叙事 |
| `matrix-rain` | 片假名/十六进制字符下落 | 黑客/数据/技术展示 |
| `knowledge-graph` | 节点+连线力导向图（28 节点） | 知识/概念/AI 生态 |
| `neural-net` | 多层节点+连线+信号传递 | AI/深度学习/神经网络 |
| `orbit-ring` | 多层同心圆轨道+粒子环绕 | 系统/架构/层级展示 |
| `galaxy-swirl` | 三臂螺旋粒子（800 个） | 宇宙/宏观/哲学叙事 |
| `word-cascade` | 词语从上方下落堆叠 | 知识/概念/文字展示 |
| `letter-explode` | 文字从散乱飞回原位 | 标题/品牌/名字揭示 |
| `chain-react` | 脉冲沿节点链传播 | 流程/系统/因果链 |
| `magnetic-field` | 粒子沿正弦路径流动带尾迹 | 物理/场论/流动系统 |
| `data-stream` | 十六进制/二进制横向流动 | 数据/传输/底层系统 |
| `shockwave` | 从中心扩散的同心圆波 | 震撼/发布/冲击力 |
| `typewriter-multi` | 终端风格逐行打字 | 技术/黑客/终端页 |
| `counter-explosion` | 数字递增后爆裂粒子 | 里程碑/大数字/数据 |

### FX 特殊 data 属性

部分 FX 支持自定义 data 属性：

| FX | 属性 | 说明 | 默认值 |
|---|---|---|---|
| `letter-explode` | `data-fx-text-value` | 要爆炸的文字 | 元素文本内容 |
| `letter-explode` | `data-fx-text` | 子元素选择器 | 元素自身 |
| `typewriter-multi` | `data-fx-line1` | 第一行文字 | `> initializing knowledge graph...` |
| `typewriter-multi` | `data-fx-line2` | 第二行文字 | `> loading 28 concept nodes` |
| `typewriter-multi` | `data-fx-line3` | 第三行文字 | `> agent ready. awaiting prompt_` |
| `counter-explosion` | `data-fx-to` | 目标数字 | `2400` |

### FX 容器要求

`data-fx` 元素必须有明确的宽高（通常是 `position:relative` 的容器），因为 canvas 会被插入为第一个子元素：

```html
<!-- 正确：frame 容器有 flex:1 自动撑满 -->
<div class="frame" data-fx="constellation">
  <span class="kicker" style="z-index:1">...</span>
  <h2 style="z-index:1">...</h2>
</div>
```

**注意**：FX 容器内的内容需要 `z-index:1` 或更高的 `position:relative` 才能在 canvas 之上显示。

### FX Autoloader 机制

沉浸模式下，`fx-runtime.js` 作为 autoloader 自动管理 FX 生命周期：
1. 动态加载所有 21 个 FX 脚本（`_util` 最先）
2. 加载完成后为每个 `.slide` 挂载 MutationObserver
3. 当 slide 获得 `is-active` 类时自动启动其 `[data-fx]` FX
4. 当 slide 失去 `is-active` 类时自动停止 FX
5. 支持通过 `window.__hpxReinit(el)` 手动重启

---

## 交互类

| 类名 | 效果 | 用法 |
|---|---|---|
| `.card-hover` | hover 时 translateY(-4px) + 阴影 | 加在卡片元素上 |
| `.anim-parallax-tilt` | hover 时 3D 微倾 | 加在需要 3D 倾斜效果的容器上 |

---

## 快捷键

| 按键 | 静态 | 微动 | 沉浸 |
|---|---|---|---|
| `← →` / `Space` | 翻页 | 翻页 | 翻页 |
| `Home` / `End` | 首页/末页 | 首页/末页 | 首页/末页 |
| `F` | 全屏 | 全屏 | 全屏 |
| `T` | — | 切换主题 | 切换主题 |
| `N` | — | — | Notes 抽屉 |
| `O` | — | — | Overview 网格 |
| `A` | — | — | 动画循环 |
| `S` | — | — | 演示者模式 |
| `Esc` | — | — | 关闭 overlay |

### 新增快捷键说明

- **A 键 — 动画循环**：在当前 slide 上依次切换 27 种入场动画效果，便于快速预览哪种动画最适合当前页面
- **S 键 — 演示者模式**：弹出独立窗口，包含当前页/下页预览 + 演讲稿 + 计时器，通过 BroadcastChannel 与主窗口同步翻页和主题

### Hash 深链接

URL 格式 `#/N`（N 为 1 起始的页号）支持直接跳转到指定页面：
- 打开 `index.html#/3` 直接跳到第 3 页
- 翻页时 URL 自动更新
- 浏览器前进/后退支持

---

## 无障碍

所有模式均支持 `prefers-reduced-motion: reduce`——在该系统设置开启时，所有 CSS 动画和过渡自动禁用，内容瞬间出现。
