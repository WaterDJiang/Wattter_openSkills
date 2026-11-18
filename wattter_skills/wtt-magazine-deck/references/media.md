# 图片与 GIF 媒体接入

用户提供的图片和 GIF 都是 deck 的内容素材，不要默认重画或丢弃。图片最终落在 `images/`，页面通过现有 `figure-frame` / `frame-img` / 风格专属图片版式引用。

## 生成前登记

在 Brief Gate 中把素材和页面做一张映射表，至少写清：

| 页面 | 素材文件 | 角色 | 显示方式 | 备注 |
|---|---|---|---|---|
| 封面 | `cover.png` | 主视觉 | `hero` / 全幅 | 不裁主体 |
| 工作流页 | `demo.gif` | 动态证据 | `figure-frame` | 保留动画 |

- 能从大纲和素材名称明确判断页面时直接映射；页面归属不明确时，在 Brief Gate 一次问清，不等到 HTML 写完再返工。
- 多张素材不要只按上传顺序盲排；按叙事角色命名，如 `01-cover.webp`、`03-workflow.gif`、`05-result.png`。
- 图片、截图、GIF 都归入 `figure-frame`，不要新增 `gif-card`、`screenshot-callout` 等顶层组件。

## 复制与命名

```bash
mkdir -p "$DIR/images"
cp "/素材路径/demo.gif" "$DIR/images/03-workflow.gif"
cp "/素材路径/cover.png" "$DIR/images/01-cover.png"
```

- 保留用户素材的原始扩展名；GIF 必须仍是 `.gif`，不要为了统一尺寸转成 PNG/WebP，也不要先截成静态帧。
- 只改成稳定、无空格的 deck 内文件名；同一素材在多个页面复用同一个文件，不复制出带随机后缀的副本。
- HTML 只使用相对路径 `images/...`，不要写用户电脑的绝对路径、`file://` 或临时上传 URL。
- 需要统一截图比例或背景时，先读 `references/screenshot-framing.md`；GIF 默认只做尺寸适配，不做截图再设计。

## 嵌入规则

静态图片和 GIF 都使用 `<img>`，放在当前风格已有图片槽位中：

```html
<figure class="figure-frame">
  <div class="figure-media" style="height:42vh">
    <img src="images/03-workflow.gif" alt="产品工作流演示 GIF" loading="eager">
  </div>
  <figcaption class="figure-caption">
    <strong>工作流演示</strong>
    <span>动态素材</span>
  </figcaption>
</figure>
```

- GIF 需要保留完整画面时使用当前风格已登记的 `contain` / `.fit-contain` 变体；照片或允许只裁底部的图片才使用 `cover`。
- 不要把 GIF 写成 CSS `background-image` 或 canvas 纹理；`<img>` 才能保留可访问的 `alt`、相对路径和原生动画。
- 不要给 GIF 额外叠加 deck 动效去模拟第二套动画；GIF 是内容媒体，`data-anim` 只控制页面入场。
- Swiss 页面仍遵守对应 `data-image-slot`、比例和 `Sxx` 版式约束；素材类型不会绕过风格校验。
- 每张素材都补 `alt`；有必要时用 `figcaption` 写一句上下文，不把素材说明写成长正文。

## 交付前检查

- 检查 `index.html` 的每个 `src="images/..."` 都能在同一 deck 的 `images/` 找到。
- 浏览器打开实际页面，确认 GIF 在对应页仍播放、没有被错误裁切，翻页离开再回来后仍能显示。
- 截图类素材检查顶部和左右关键信息没有被裁掉；网格使用固定 `height`，不要用会撑破布局的自定义 `aspect-ratio`。
