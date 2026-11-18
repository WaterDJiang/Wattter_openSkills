# 源 PowerPoint 版式参考

这里保存从 `../source_template.pptx` 提取的 1 个 master、4 个 layout、4 个页级图层，以及 `inheritance.json`。这些 SVG 展示源文件的版式图层和占位元数据；真正可选的 4 张镜像页在上级目录，由 `page_catalog.json` 索引。

| 文件 | 源版式名 | 源页使用情况 | 元素 |
|---|---|---|---|
| `layout_01_slideLayout1.svg` | `3_自定义版式` | 1、4 | 整页蓝青波纹、右上 Logo、正文占位 |
| `layout_02_slideLayout2.svg` | `4_自定义版式` | 未使用 | 白底、右上 Logo、正文占位、页码 |
| `layout_03_slideLayout3.svg` | `2_自定义版式` | 未使用 | 白底、右上 Logo、左上标题、正文占位、页码 |
| `layout_04_slideLayout4.svg` | `统一模板` | 2、3 | 白底、右上 Logo、标题占位 |

源占位导引不是输出页面中的可见对象。页 3 的可见内容仅有 Logo；`chapter_candidate` 是导入器的候选猜测，主目录按源页用途将它登记为 `content`。

`slide_01.svg` 至 `slide_04.svg` 是各页自身图层；结合 `inheritance.json` 指向的 layout/master 才是完整源页。上级目录的 `001_*.svg` 至 `004_*.svg` 已包含这些继承层。
