---
description: Step 1 detail — 三流程闸口 + 源内容转 Markdown
---

# Step 1：流程确认与源内容处理（详细）

> 本文件承接 SKILL.md Step 1 的执行细节。SKILL.md 只保留 GATE / BLOCKING / 检查点；进入 Step 1 时读本文件。

## 1-0. 标准交接检测

若输入目录存在 `course_contract.json`：

1. 读取 `../course-handoff-protocol.md`。
2. 运行 `python3 ${SKILL_DIR}/scripts/validate_course_handoff.py <bundle>`。
3. 验证通过后，把 `course_contract.json + pages.jsonl` 视为内容真源；若含 design profile，再用 `--require-design` 校验。检查并读取同包随附的 `render_request.md`，保留其中用户原话、模板名称/路径及来源；不能只读 design profile 后把明确模板请求丢失。
4. 未经 contract policy 和用户明确授权，不重排、不改页数、不扩知识范围。
5. 未知协议版本或验证失败时列出原始错误；若另有普通源材料，可回退 1b，但不得猜字段。

标准交接只是可选快速路径，不改变下面的路由选择，也不要求安装 generator 或 scriptwriter。

`render_request.md` 是可选的渲染请求附件，不是内容契约的新必填字段；旧包缺少它时读取当前对话的用户请求。路由同时核对当前请求与附件中的原话：用户本次明确选择 Deck 时，按该选择进入 Deck Route，旧包的 `free/full-free` 路由、自由风格或其他冲突视觉推荐不能覆盖它。把被替代的视觉字段及依据记入新项目 `design_spec.md`，据此重建 `spec_lock.md` 和缓存，不沿用旧锁；未被本次请求改变的内容、页序和教学约束仍继承。附件与当前请求冲突时以当前用户请求为准，不把上游自行推荐写成用户指定。

详尽讲师大纲但无页表：先读 [教学分镜扩展](../teaching-contract.md)，形成页表和简短讲师提示；以教学任务决定分页，不按总时长机械造页。已有页表不重新编课。检测位置包括输入目录、`sources/course-handoff/` 和旧项目平铺 `sources/`；发现不完整契约须报错，不能当无契约跳过。

## 1a. 流程确认（三选一闸口）

⛔ **BLOCKING（仅当歧义时）**：只有用户明确说“用某个模板”但无法判断是库内 Deck、Layout 还是用户 PPTX 时才追问。用户未指定模板不构成歧义，默认进入 Free Route，不读取 Deck 索引。

| 流程 | 含义 | 触发信号 |
|---|---|---|
| **流程 1 · 用 skill 库资产** | 显式 Deck 名称/路径进入隔离的 Deck Route；否则只在 Layout / Brand / HTML Background 中按需匹配 | 用户明确指定库内模板，或要求查看某类库资产 |
| **流程 2 · 用用户提供的模板** | 用户以 `.pptx` 文件形式提供模板，skill 分析其设计身份后构建 | 用户附带 `.pptx` 模板 + 内容材料 / 说"套这份 pptx 模板" |
| **流程 3 · Free Route**（默认） | 不进入 Deck；按内容选择 `layout-led` / `html-led` / `full-free`，图表与图标按需渐进检索 | 用户未指定模板，或明确说"自由发挥" |

**路由判定**：

- 用户逐字指定 `decks_index.json` 中的 Deck id，或给出 `templates/decks/<id>/` → `route.kind=deck`；只读取该 Deck。
- 用户附 `.pptx` 模板 → 流程 2。
- 用户指定 Layout / Brand → Free Route 中的 `layout-led` / brand 识别约束；不读取 Deck。
- 无模板信号、"都行"、"按需设定" → `route.kind=free`；默认推荐 `layout-led` 或 `html-led`，允许用户切为 `full-free`。

> **Deck 是显式 opt-in**：品牌/行业语义相似不能自动选择 Deck。只有用户明确命名、选择或给出 Deck 路径才进入 Deck Route。用户问“有哪些 Deck”时可读取 `decks_index.json` 列表，但列举本身不等于选中。

确认后，所选流程决定 Step 3 的获取方式；Step 2 及之后的生成流水线三条流程完全一致。

## 1b. 源内容处理

> **没有源内容怎么办？** 当用户只提供主题名或需求，没有任何文件或实质性描述时，请先运行 [`topic-research`](../../workflows/topic-research.md) 工作流，再回到此处以其产物作为输入。

若用户提供的是非 Markdown 内容，请立即转换：

| 用户提供 | 命令 |
|---------------|---------|
| PDF 文件 | `python3 ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` |
| DOCX / Word / Office 文档 | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| XLSX / XLSM / Excel 工作簿 | `python3 ${SKILL_DIR}/scripts/source_to_md/excel_to_md.py <file>` |
| CSV / TSV | 直接以纯文本表格源读取 |
| PPTX / PowerPoint 演示文稿 | `python3 ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py <file>` |
| EPUB / HTML / LaTeX / RST / 其他 | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| 网页链接 | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` |
| 微信 / 高安全站点 | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>`（需要 `curl_cffi`，已包含在 `requirements.txt` 中） |
| Markdown | 直接读取 |

> **流程 2 的 `.pptx` 模板文件不是内容源**——它是设计参考。在 Step 2 `import-sources` 时随内容源一起进入 `sources/`，但 Step 1b 不对它做内容转换；它的设计分析发生在 Step 3 流程 2。

> **来自 DOCX/PPTX 源中的 Office 矢量资源（EMF/WMF）**：
> `doc_to_md.py` / `ppt_to_md.py` 会提取内嵌的 Office 矢量图像（.emf/.wmf）与位图一起被导出。`import-sources` 后，这些资源会落到 `images/` 目录中，与 `image_manifest.json` 一起作为 §VIII 图像资源清单中的一等资源。
>
> **不要把 EMF/WMF 转成 PNG。** 课程 PPT 构建器流水线将它们作为外部引用保留（`finalize_svg.py` 会跳过它们），`svg_to_pptx.py` 通过 `image/x-emf` / `image/x-wmf` MIME 嵌入为 PPTX 原生媒体——PowerPoint 以全矢量保真度渲染。通过 LibreOffice/Inkscape 转换会引入 CJK 字体替换漂移以及栅格化损失；原始 EMF/WMF 始终比转换后的 PNG 保真度更高。
>
> 基于浏览器的实时预览无法渲染 EMF（会显示空白）——这是预期行为；PPTX 输出才是最终标准。
