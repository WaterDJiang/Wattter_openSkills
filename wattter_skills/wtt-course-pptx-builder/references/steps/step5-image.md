---
description: Step 5 detail — HTML 背景渲染 + ai/web 图像获取（条件性，含场景门控）
---

# Step 5：图像获取阶段（条件性）—— 详细

> 本文件承接 SKILL.md Step 5 的执行细节。

## HTML 背景渲染（仅明确锁定 HTML 的 Free Route 页面）

先查已锁定的 route 与逐页背景。Deck Route 使用本包资产或锁定的原生重建，不生成 HTML manifest；Free Route 无 HTML 背景页也跳过本节。只有已锁定 HTML 背景时，Strategist 才在 §6.2 step 5 写 `images/html_background_manifest.json` 并运行 `html_render.py`。进入 Step 5 前，确认这些页面对应的 `images/bg_*.png` 已就位、manifest 全 `Rendered-HTML`（或 `Fallback-Solid`）。若未跑（如 resume 场景），补跑：

```bash
python3 ${SKILL_DIR}/scripts/html_render.py <project_path>
# Playwright/Chromium 不可用时用纯色兜底：
python3 ${SKILL_DIR}/scripts/html_render.py <project_path> --fallback-solid
```

**时序红线**：已锁定的 HTML-PNG 必须在 Step 6 Executor 前就位；此要求不用于没有 HTML 背景的页面。HTML 渲染与 ai/web 图像获取互不依赖，可并行。

## 触发条件（显式门控）

资源清单中至少有一行 `Acquire Via: ai` 和/或 `Acquire Via: web`。若所有行都是 `user`、`formula`、`html` 或 `placeholder`（方案 A / 无 ai·web 图），**跳过整个 Step 5**——**不读** `image-base.md` / `image-generator.md` / `image-searcher.md` / `image-layout-patterns.md` / `image-layout-spec.md` 这 5 个文件（共 ~95K 字符 / ~60K token 的节省）。`html` 背景行已在 Step 4 §6.2 step 5 由 `html_render.py` 渲染完毕，不进本步；`svg-image-embedding.md` 例外（小，且定义 html/placeholder 的状态枚举，随 executor-base 加载）。

## 进入 Step 5 后，加载路径专属参考

先加载通用框架：

```
Read references/image-base.md
```

然后**按需懒加载**路径专属参考：

| 获取方式 | 加载参考（仅当存在该类行时） | 运行 |
|---|---|---|
| `ai` | `references/image-generator.md` | `python3 ${SKILL_DIR}/scripts/image_gen.py --manifest <project_path>/images/image_prompts.json` |
| `web` | `references/image-searcher.md` | `python3 ${SKILL_DIR}/scripts/image_search.py ...` |
| `user` / `placeholder` | （跳过） | （跳过） |

只含 `ai` 行的 deck 永远不加载 `image-searcher.md`；只含 `web` 行的 deck 永远不加载 `image-generator.md`。混合 deck 两者都加载，各自行使自己的路径处理，输出 `image_prompts.json` 与 `image_sources.json`。

> 💡 **`ai` 行的回退链**：`image_gen.py --manifest` 按 `.env` 中 `IMAGE_BACKEND` 的**逗号分隔链路**顺序尝试每张图，首个成功即用，整链全失败才标记 `Failed`（如 `IMAGE_BACKEND=jimeng,minimax,zhipu,pexels`）。链路末端的 web 源（`pexels`/`pixabay`/`openverse`/`wikimedia`）在所有生成类后端失败时转调 `image_search.py` 搜图兜底，attribution 自动写入 `image_sources.json`。实际解析后端记入 manifest 的 `backend_used` 字段。单值配置（如 `IMAGE_BACKEND=zhipu`）是长度为 1 的链，行为与旧版单后端完全一致。

> ⚠️ **流水线内的 ai 路径必须用清单模式**——即便只有 1 行 ai 也一样。先写 `images/image_prompts.json`，再跑 `image_gen.py --manifest`，再跑 `image_gen.py --render-md` 生成 `image_prompts.md` 边车文件。位置参数形式（`image_gen.py "prompt" ...`）仅供**流水线外一次性测试 / 单图修补**——它跳过清单 + 边车，不留审计痕迹。

## 工作流

1. 从设计规范中提取所有 `Status: Pending` 且 `Acquire Via ∈ {ai, web}` 的行
2. 按 [`../image-base.md`](../image-base.md) §2 派发表为 ai 行生成提示词，为 web 行执行搜索
3. 确认每行达到终止状态：`Generated`（ai 成功）、`Sourced`（web 成功）或 `Needs-Manual`

> 获取失败时不要停下——遵循 [`../image-base.md`](../image-base.md) §5 中的失败处理规则：重试一次，然后把该行标记为 `Needs-Manual`，向用户报告，并继续到上面的检查点。
