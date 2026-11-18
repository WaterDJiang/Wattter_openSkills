# 微信公众号海报模板使用说明

## 功能介绍

提供3种4:3比例的海报模板，可用于微信公众号文章的封面、金句展示、核心内容可视化：

1. **封面模板** - 大标题+副标题，适合文章封面、核心观点展示
2. **对比模板** - 左右分栏，适合输入输出、前后对比、收益展示
3. **时间线模板** - 深色背景时间轴，适合发展历程、事件节点展示

## 模板文件

- `poster-templates.html` - 包含所有3种模板的完整HTML文件

## 使用方法

### 方法1：直接生成图片

1. 打开 `poster-templates.html` 在浏览器中
2. 修改需要自定义的文字内容
3. 使用截图工具（Mac: Command+Shift+4，Windows: Snipping Tool）截取4:3比例
4. 或者使用浏览器的"打印"功能，另存为PDF后转换为图片

### 方法2：集成到 wtt-post-multi-platform 的微信平台中

#### 步骤1：修改模板内容
根据需要自定义每个模板的文字内容：

```html
<!-- 封面模板自定义 -->
<div class="cover-title">
    你的大标题<span class="accent">，</span><br>
    第二行标题<span class="accent">。</span>
</div>

<div class="cover-subtitle">
    副标题第一行<br>
    <span class="highlight">副标题高亮文字</span>
</div>
```

```html
<!-- 对比模板自定义 -->
<li class="card-item">
    <span class="number">01</span>
    列表项文字<span class="highlight">高亮部分</span>
</li>
```

```html
<!-- 时间线模板自定义 -->
<div class="timeline-item">
    <div class="timeline-date">日期</div>
    <div class="timeline-event">事件标题</div>
    <div class="timeline-desc">事件描述</div>
</div>
```

#### 步骤2：提取单个模板CSS
将需要使用的模板对应的CSS提取出来，内嵌到HTML中：

```html
<style>
    /* 只保留需要的模板样式 */
    .poster { ... }
    .cover-poster { ... }
    /* 其他样式 */
</style>
```

#### 步骤3：转换为微信支持的格式
使用 `wtt-post-multi-platform` 的微信 HTML 转换功能，将自定义后的模板上传到微信公众号草稿箱。

## 样式定制

### 颜色变量
可以根据品牌需求调整颜色：

```css
:root {
    --color-bg: #f5f0e6;          /* 背景色 */
    --color-text: #0a1942;        /* 主文字色 */
    --color-accent: #1E40AF;      /* 强调色（克莱因蓝） */
    --color-dark-bg: #050f2c;     /* 深色背景 */
    --color-card-left: #f8f3e9;   /* 左侧卡片背景 */
    --color-card-right: #0a1942;  /* 右侧卡片背景 */
}
```

### 字体调整
默认使用 Google Fonts 的 Noto Sans SC，也可以替换为其他字体：

```css
@import url('字体URL');
body {
    font-family: '你的字体', sans-serif;
}
```

## 最佳实践

1. **封面模板**：大标题控制在8字以内，分两行显示效果最佳
2. **对比模板**：左侧列表不超过3项，右侧列表不超过10项
3. **时间线模板**：节点控制在4个，每个事件标题不超过20字
4. **导出图片**：建议导出为1200×900像素的PNG格式，清晰度最佳

## 示例

### 技能介绍封面
```html
<div class="cover-title">
    一键发布<span class="accent">，</span><br>
    无需排版<span class="accent">。</span>
</div>

<div class="cover-subtitle">
    Markdown 直接发布到微信公众号<br>
    <span class="highlight">再也不用手动复制粘贴。</span>
</div>
```

### 功能对比
```html
<li class="card-item">
    <span class="number">01</span>
    手动排版<span class="highlight">30分钟</span>
</li>
<li class="card-item">
    <span class="number">02</span>
    自动发布<span class="highlight">30秒</span>
</li>
```

### 功能更新时间线
```html
<div class="timeline-item">
    <div class="timeline-date">2026 · 04</div>
    <div class="timeline-event">支持代码块渲染</div>
    <div class="timeline-desc">Mac 风格代码块。</div>
</div>
```
