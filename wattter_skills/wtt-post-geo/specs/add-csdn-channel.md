# CSDN 渠道发布能力规格

## 目标

- 为 `wtt-post-geo` 增加 CSDN 博客长文发布能力。
- 保持渐进式披露：CSDN 的标题、Markdown、标签、分类、版权声明、可见性、草稿和发布校验全部收敛到独立 reference。
- 只在平台侧公开文章可回读时报告 `已发布`。

## 范围

- 新增 `references/csdn.md`。
- 新增 `scripts/prepare-csdn-markdown.py` 与单元测试，稳定生成独立正文、标题和本地图片阻塞清单。
- 更新 `SKILL.md` 的触发词、适用场景、全平台顺序和 payload 协议。
- 更新 `README.md` 的能力说明、健康检查和目录结构。
- 更新 `references/content-format.md` 的平台列表与通用 `platform_options` 扩展位。
- 不创建全局 OpenCLI 私有 adapter，不调用 CSDN 私有写入 API。
- 用户明确要求后，使用 `[TEST]` 标题和正文执行一次真实发布前向测试。

## 当前能力基线

- OpenCLI `1.8.6` 的 `opencli list -f json` 中没有 `csdn` 站点 adapter。
- `https://editor.csdn.net/md/` 当前可访问，页面标题为 `写文章-CSDN博客`。
- 当前编辑器 bundle 提供 Markdown 导入、保存草稿、发布文章、文章标签、最多 3 个分类专栏、原创/转载/翻译、可见性和创作声明等 UI。
- 2026-07-15 已在真实账号完成单段纯文本发布闭环：编辑器写入、发布字段、成功页、公开文章和管理页 `已发布` 状态均已回读。
- 当前浏览器桥对 Markdown 文件 input 返回 `Not allowed`；直接 `fill/type` 多段 Markdown 会压缩换行。因此多段/富 Markdown 必须停在 `fill_and_confirm`，由用户手动导入后再继续校验发布。
- 当前测试账号博客等级低于 3 级，不能创建自定义标签；已验证可以从平台标签库选择现有标签。

## 验收标准

- 用户点名 CSDN 时只加载 `content-format.md`、`csdn.md`，涉及图片时再加载 `media-assets.md`。
- CSDN payload 明确包含标题、Markdown 正文、标签、分类、文章类型、来源授权、可见性、创作声明和模式。
- 准备脚本能剥离 frontmatter 与重复 H1，并在正文仍含本地图片时把发布状态标记为阻塞。
- 准备脚本只把无本地图片的单段正文标记为 `direct_fill_ready`；多段 Markdown 标记为 `manual_import_required`。
- 主路径使用 `opencli browser csdn ...` 与 CSDN 原生 Markdown 编辑器，不出现不存在的 `opencli csdn publish` 命令。
- 草稿成功必须由草稿提示、`articleId` 与文章管理列表共同校验。
- 发布成功必须拿到并回读 `blog.csdn.net/<user>/article/details/<id>`；只有成功页或点击结果时不得报告 `已发布`。
- README、SKILL、content-format 与 reference 中的 CSDN 名称、链接和顺序一致。

## 影响面

- 文档型能力升级，不修改现有平台脚本。
- 全平台默认顺序新增 CSDN，现有平台相对顺序保持不变。
- 通用 payload 新增可选 `platform_options`，现有平台无需迁移。
