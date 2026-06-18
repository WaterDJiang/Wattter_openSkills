# Components · STYLE_NAME

本目录只放 `STYLE_ID` 的专属组件 CSS。

## 放入这里的组件

- 只有该风格使用的卡片、图表、时间轴、装饰、地图、图文结构。
- 带有明确风格指纹的 class。
- 需要在 `registry.json` 的 `styleIsolation.forbidClasses` 中禁止其他风格使用的 class。

## 不放入这里的组件

- 通用 slide 容器、导航、图片基础槽位、基础 grid。
- 已经在 `assets/core/` 里存在的低层结构。
- 其他风格的组件复制品。

## 命名建议

专属组件优先使用风格前缀或强语义名称，例如：

- `.STYLE_ID-panel`
- `.STYLE_ID-timeline`
- `.STYLE_ID-stat`

避免使用过泛的 `.card`、`.box`、`.item`。
