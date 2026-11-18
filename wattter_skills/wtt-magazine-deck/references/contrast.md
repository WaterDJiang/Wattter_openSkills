# 文字与背景可读性

## 生成约束

- 先确定每个文字区域的实际底色，再选字色。局部卡片不沿用整页深浅推断。
- 新建纯色区域优先使用 `.surface-light` / `.surface-dark` / `.surface-accent`，同时绑定背景和文字变量；已有图片、组件底色使用 `.on-light` / `.on-dark` / `.on-accent` 声明语义。
- 正文使用继承色或 `var(--surface-text)`，辅助文字用 `var(--surface-muted)`。不能写整页后代选择器强制所有文字为 ink/paper；嵌套区域需保留自己的 surface。
- 品牌 accent 是背景/装饰色，不保证适合作为浅底小字。需要强调文字时先验证对比度，不通过则使用正文色，通过线条或色块保留品牌色。
- 图片/GIF/WebGL 上的文字使用 `.readable-zone.on-dark` / `.readable-zone.on-light`。默认不透明底板；若改为半透明，需对最亮/最暗画面复核，不能只检查 GIF 的第一帧。
- 普通文字对比度至少 4.5:1；24px 以上，或 18.667px 以上且字重至少 700 的大字至少 3:1。辅助文字、脚注同样检查，不用叠加 opacity 制造不可读的“高级灰”。

```html
<section class="slide light">
  <div class="surface-dark">
    <h2 class="h-md">深色卡片里的浅色标题</h2>
    <p class="text-primary">颜色由最近的 surface 决定。</p>
    <div class="surface-light"><p class="text-primary">嵌套浅底恢复深色字。</p></div>
  </div>
</section>
```

## 浏览器验收

静态 `validate-theme-contract.mjs` 检查主题颜色配对，不能代替真实页面检查。

生成后逐页打开，等待字体、主题 CSS、入场动画稳定，对所有可切换主题执行 `scripts/audit-contrast.js`。它是一个返回报告的浏览器表达式，不需要打包到 deck；可用浏览器工具执行文件内容，或通过已有 Playwright 环境：

```js
const source = readFileSync('<SKILL_ROOT>/scripts/audit-contrast.js', 'utf8');
const report = await page.evaluate(source);
console.log(report);
```

- `failures`：页号、文字片段、元素、实际对比度及阈值。修复后重新检查对应页/主题。
- `review`：图片、渐变、伪元素遮罩、祖先透明度或不支持的颜色语法等需要人工复核的区域；不能当成通过。
- `checked`：本次可量化的可见文字数量。为 0 时不算通过；不可见的其他页必须翻到该页后再测。
- 计算支持 RGB/RGBA、普通祖先背景合成及文字自身 opacity；不采样图片像素，也不推断兄弟元素遮挡、canvas、复杂堆叠。必须同时截图检查遮挡和溢出。
- 验收要求：所有页/主题 `failures` 为 0，`review` 每项有实际视觉复核或改成可计算的纯色底板。记录检查范围和未覆盖项。

旧 deck 的 CSS 已复制到独立目录；修改 skill 不会自动更新这些文件。重新生成或同步对应 base/style CSS 后再运行上述检查。
