---
description: Step 3 detail — 显式 Deck 隔离路由 / Free Route / 用户 PPTX
---

# Step 3：模板获取（按流程分支）—— 详细

> 本文件承接 SKILL.md Step 3 的执行细节。SKILL.md 只保留 GATE + 三流程一句摘要 + 检查点。

> 三条入口共用 Step 4 之后的流水线；差异由 `spec_lock.route` 保留。Free Route 可以没有 `<project>/templates/design_spec.md`，不得为了统一路径伪造 Deck 或模板来源。

---

## 路由 A · 显式 Deck（隔离）

Deck 只在用户明确命名、选择或给出 `templates/decks/<id>/` 路径时启用。行业、品牌或内容相似度不能自动触发 Deck。

渐进加载顺序：

1. 已给精确路径：直接定位，不读 `decks_index.json`。
2. 已给精确名称：只读 `decks_index.json` 解析该 id；未命中时报告未找到，不猜路径。
3. 用户要求“查看 Deck”：读取索引并列出；列举不等于选中，选中一个后才继续。
4. 选中后只读该 Deck 的 `design_spec.md`、`page_catalog.json` 与被选中的 SVG/资源。先用紧凑查询筛选页面，不全量读取 SVG：

   ```bash
   python3 ${SKILL_DIR}/scripts/template_page_catalog.py <selected_deck> \
     search "<page intent>" --page-type <type> \
     --content-form <content_form_hint> --item-count <N> \
     --image-need <image_need> --precise-only \
     --topology <composition.topology> --emphasis <composition.emphasis> \
     --compact --limit 3
   ```

5. 将该包复制到 `<project_path>/templates/`，并在 `spec_lock.route` 写入：

   ```yaml
   kind: deck
   primary_source: decks/<selected_id>
   allowed_asset_scopes: [decks/<selected_id>, charts, icons]
   forbidden_asset_scopes: [other-decks, layouts, html-background-styles]
   ```

Step 3 只确定 Deck 来源；逐页取舍在 Step 4 完成。局部页面/底图/品牌资源优先；`--precise-only` 只返回具备明确用途门槛或独特构图、且匹配槽位与图片需求的包内页。若返回 `[]`，Step 4 按该页形态调用 `match_content_forms.py resolve <form> --count <N> --package <selected_id>` 查询全局 chart；该命令列出的包内形态变体仍只是候选。仅有相同 `content_form` 不足以拦截 chart。chart 只借几何结构，必须按选中 Deck 重着色。用户或设计意图明确要求某页用 chart 时，按 `binding_preference=chart` 处理。禁止 Deck + Layout、Deck + HTML Background、Deck + 其他 Deck 的融合。

## 路由 B · Free Route（默认）

用户未指定模板时，不读取 `decks_index.json`，也不从 Deck 借任何页面、底图、品牌色或资源。按内容和用户偏好选择：

| strategy | 读取范围 | 行为 |
|---|---|---|
| `layout-led` | `layouts_index.json` → 选中一个 Layout 的目录 | 用 Layout 提供结构骨架；主题色、HTML 背景、charts/icons 可自由组合 |
| `html-led` | `html-background-styles/_index.md` + theme palette | 背景系统主导；页面结构自由或按需查询 Layout |
| `full-free` | theme palette + charts/icons（按需） | 不选择 Layout，逐页自由设计 |

Free Route 的索引读取是按需的：先定 `content_form_hint / relationship / item_count / composition`，只有需要模板候选时才调用 `template_page_catalog.py ... search --content-form <form> --item-count <N> [--topology <topology>] [--emphasis <emphasis>] --compact --limit 3`；只有需要图表结构时才调用 `match_content_forms.py resolve <form>`。不得把全部 `page_catalog.json`、`charts_index.json` 或所有 SVG 放入上下文。

Brand 可作为 Free Route 的识别约束与一个 Layout 组合；融合仅允许 `brand + layout`。同 kind 多选默认不支持，用户必须收敛到一个来源。字段级修改进入 Step 4 八项确认，不在 Step 3 隐式合并。

选中 Layout/Brand 后，按索引中的 `path` 复制到 `<project_path>/templates/`；未选中任何包时直接进入 Step 4。写入：

```yaml
kind: free
strategy: layout-led | html-led | full-free
allowed_asset_scopes: [selected-layout-if-any, layouts, html-background-styles, charts, icons]
forbidden_asset_scopes: [decks]
```

> `register_template.py` 会把新增模板注册进对应索引。不要在 skill 文档或脚本中硬编码模板名单。

---

## 流程 2 · 用用户提供的模板

用户在 Step 1a 选了流程 2，或在开场附带 `.pptx` 模板 + 内容材料。本流程是独立工作流 [`use-user-template`](../../workflows/use-user-template.md) 的入口：

```
切换到 workflows/use-user-template.md
```

该工作流：
1. 运行 `pptx_template_import.py` 分析 `<project>/sources/` 中的用户 `.pptx`（主题色 / 字体 / 尺寸 / SVG 视图 / `manifest.json`）
2. ⛔ BLOCKING 子选择：**身份+结构复刻**（调 Template_Designer 项目模式，重建 SVG 版式清单 + 完整 `design_spec.md`）或**仅身份提取**（只写识别段 `design_spec.md`，结构留给 Strategist 自由设计）
3. 产物落 `<project>/templates/`（默认不入库）
4. 末尾可选入库（保存到 `templates/<kind>/<id>/` + `register_template.py` 注册，供未来流程 1 复用）

完成后回到主线，进入 Step 4。

> ❌ 流程 2 **不要**运行 `template_fill_pptx.py`（那是 [`template-fill-pptx.md`](../../workflows/template-fill-pptx.md) 的 OOXML 文本回填，不是设计身份分析）。

---

## 流程 3 · 自由构建

该入口等价于 Free Route。直接进入 Step 4，Strategist 选择 `layout-led` / `html-led` / `full-free`，绝不读取 Deck。

**结构页脚手架**：`layout-led` 时从选中的 Layout 查询 cover / chapter / ending；`html-led` 时优先使用 HTML 背景与文字槽；`full-free` 不写 `page_layouts`。

> 用户要**纯自由**（结构页也自由）→ 在确认时说"结构页也自由"/"全部自由设计"，Strategist 留空 `page_layouts` 整段，回退到全 free design。

---

> 若要新建版式或 deck 入库供未来流程 1 使用，请阅读 [`../../workflows/create-template.md`](../../workflows/create-template.md)。若要新建品牌入库，请阅读 [`../../workflows/create-brand.md`](../../workflows/create-brand.md)。这两个是**库资产创建**工作流，与流程 1/2 的**项目级使用**不同。
