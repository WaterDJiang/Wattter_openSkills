# Layouts · STYLE_NAME

本文件登记 `STYLE_ID` 的版式。新增风格必须定义自己的 layout ID，不要复用 `editorial` 的 `Lxx` 或 `swiss` 的 `Sxx`，除非该风格就是对应风格的兼容扩展。

## 通用约束

- 每页 `<section class="slide ...">` 必须写 `data-layout="STYLE_ID-01"` 这类稳定 ID。
- 首页必须体现所选主题：大面积使用 `--accent`、主题背景、或该风格的核心视觉元素。
- 主体内容必须在 16:9 视口内完整显示；长标题用 `.fit-safe-text`，高密度主体包 `.fit-shell` 或拆页。
- 不要使用其他风格的专属 class。

## STYLE_ID-01 · Cover

**用途**：封面 / 章节首页  
**关键 class**：`.slide.accent` `.fit-shell` `.fit-safe-text`  
**动效**：`hero`

```html
<section class="slide accent" data-layout="STYLE_ID-01" data-animate="hero">
  <div class="frame fit-shell" style="display:grid;grid-template-rows:auto 1fr auto;gap:3vh">
    <div class="kicker">SECTION</div>
    <h1 class="h-hero fit-safe-text">[必填] 标题</h1>
    <p class="lead">副标题或一句话说明</p>
  </div>
</section>
```

## STYLE_ID-02 · Statement

**用途**：核心观点页  
**关键 class**：`.frame` `.h-xl` `.lead`  
**动效**：`fade-up`

```html
<section class="slide light" data-layout="STYLE_ID-02" data-animate="fade-up">
  <div class="frame">
    <div class="kicker">POINT</div>
    <h2 class="h-xl fit-safe-text">一句核心判断</h2>
    <p class="lead">解释这句话为什么重要。</p>
  </div>
</section>
```

## 新增版式记录格式

每个新增版式都要补：

- 用途
- 必需 class / data 属性
- 图片槽位和比例
- 中文长标题、长数字、长标签的替代写法
- 推荐动效
- 禁止使用场景
