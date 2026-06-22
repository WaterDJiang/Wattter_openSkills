---
description: 通过逐幻灯片 / 逐对象的覆盖项，自定义默认的 PPTX 动画（顺序、效果、时机）
---

# 动画定制工作流

> 独立的生成后步骤。当用户要求调整动画顺序、效果、时机或对象级揭示时运行。默认 PPTX 导出已带全局动画；本工作流仅在用户希望做更细粒度控制时才创建 `animations.json` 覆盖。

## 何时运行

| 条件 | 操作 |
|---|---|
| 用户要求对象级动画、揭示顺序、时机或效果调整 | 运行本工作流 |
| 用户只要默认带动画的 deck | 不运行；正常 `svg_to_pptx.py` 导出即可 |
| `svg_output/*.svg` 缺失 | 先完成主流水线的执行器阶段 |
| 已存在 `animations.json` | 校验并编辑它；除非用户要求，否则不要覆盖 |

---

## 1. 获取真实 Group ID（不要 dump 完整脚手架）

**强制**：使用真实的 SVG group id。不要臆造 slide 或 group key。

**默认路径 —— `list-groups`**（轻量，即便在长 deck 上输出也仅约 1KB）：

```bash
python3 ${SKILL_DIR}/scripts/animation_config.py list-groups <project_path>
```

输出每页一行：`<slide_basename>: id1, id2, id3`——chrome 组（`bg` / `*-header` / `*-footer` / `*-decor` / `nav` / `watermark` / `logo` / `pagenumber`）已被排除，因为导出器会把它们固定为 `none`。在规划 §3 与编辑 §4 时以此为唯一来源——**除非需要把它当作编辑起点，否则不要读取完整脚手架文件**。

若 `animations.json` 不存在且希望拿到一个可编辑的起始文件：

```bash
python3 ${SKILL_DIR}/scripts/animation_config.py scaffold <project_path>
```

脚手架输出同样会排除 chrome、并附带一份 `defaults` 骨架。

若已存在：

```bash
python3 ${SKILL_DIR}/scripts/animation_config.py validate <project_path>
```

---

## 2. 阅读语义上下文

**强制**：编辑 `animations.json` 之前，先阅读 deck 的语义规划文件。

| 文件 | 用途 |
|---|---|
| `<project_path>/design_spec.md` | 理解每页的内容意图、叙事角色与视觉重点 |
| `<project_path>/spec_lock.md` | 确认页面节奏、版式角色、图表 / 模板约束与执行契约 |
| `<project_path>/notes/total.md` 或 `<project_path>/notes/*.md` | 用讲者语流调整揭示顺序、延迟与强调 |

**硬规则**：语义文件决定动画意图；`svg_output/*.svg` 决定合法的动画目标。绝不要引用脚手架 / SVG 扫描结果中不存在的 slide 或 group id。

**上下文缺失**：若某个语义文件缺失，说明缺什么，然后基于剩余文件与真实 SVG group id 继续。若 `design_spec.md` 与 `spec_lock.md` 都缺失，不要推断细粒度的对象编排；只使用保守默认值与用户明确指令。

---

## 3. 规划幻灯片与对象的运动

**强制**：编辑 `animations.json` 之前，先规划好页面级切换与页内对象入场两层。

| 层级 | 配置路径 | 用途 |
|---|---|---|
| 页面切换 | `defaults.transition` 或 `slides.<slide>.transition` | 控制一张幻灯片如何从上一张进入 |
| 页面动画默认值 | `defaults.animation` 或 `slides.<slide>.animation` | 控制该幻灯片上动画组的默认入场行为 |
| 对象覆盖项 | `slides.<slide>.groups.<group_id>` | 控制某个真实 SVG 组的顺序、效果、延迟或时长 |

**逐页运动简报**：对每张幻灯片，决定切换效果、切换时长、对象揭示序列、对象效果与时机。用 `design_spec.md` 把握幻灯片角色，`spec_lock.md` 把握节奏，讲者备注把握叙事顺序，SVG group id 保证目标合法。

**硬规则**：定制动画除了编辑 group 效果之外，还必须决定每张幻灯片应继承默认 transition 还是需要 slide 级的 `transition` 覆盖。

**时机指引**：当 deck 的幻灯片节奏或对象重要性差异较大时，优先按内容定制时长。当用户要求统一风格或 deck 节奏本身就匀速时，整齐一致的时长也可以接受。

**时长规划**：

| 场景 | 切换时长 | 对象时长 | 延迟 / 错位 |
|---|---:|---:|---:|
| `anchor` 幻灯片 / 章节开场 / 收束综合 | 0.35–0.60s | 0.45–0.75s | 0.20–0.40s |
| `breathing` 概念幻灯片 / 主视觉图 | 0.25–0.45s | 0.40–0.65s | 0.16–0.30s |
| `dense` 技术幻灯片 / 重复模式页 | 0.18–0.35s | 0.25–0.45s | 0.10–0.24s |
| 次要支撑对象 | 继承或 0.20–0.35s | 0.20–0.35s | 0.08–0.18s |
| 关键洞察 / 最终 take-away | 0.30–0.50s | 0.50–0.80s | 0.25–0.45s |

**时长指引**：扫读型重复内容用更短时长；概念性转折、章节切换、主视觉图、最终 take-away 用更长时长。

### 3.1 支持的页面切换

| 效果 | 行为 |
|---|---|
| `none` | 禁用页面切换 |
| `fade` | 技术类 deck 的中性默认值 |
| `push` | 定向滑入 |
| `wipe` | 定向揭示 |
| `split` | 对开式切换 |
| `strips` | 对角条纹切换 |
| `cover` | 侧向遮盖 |
| `random` | PowerPoint 随机切换 |

**切换字段**：

| 字段 | 行为 |
|---|---|
| `effect` | 支持的页面切换效果之一 |
| `duration` | 切换时长（秒） |
| `auto_advance` | 自动切到下一张前的可选秒数 |

### 3.2 支持的页内动画

| 效果 | 行为 |
|---|---|
| `none` | 把该对象或幻灯片排除在页内动画之外 |
| `appear` | 仅翻转可见性，无运动 |
| `fade` | 中性入场 |
| `fly` | 从底部飞入 |
| `cut` | 从左侧切入 |
| `zoom` | 缩放入场 |
| `wipe` | 擦除入场 |
| `split` | 对开 / 谷仓门入场 |
| `blinds` | 水平百叶 |
| `checkerboard` | 棋盘揭示 |
| `dissolve` | 溶解揭示 |
| `random_bars` | 随机条状揭示 |
| `peek` | 向下擦除 |
| `wheel` | 车轮入场 |
| `box` | 方框揭示 |
| `circle` | 圆形揭示 |
| `diamond` | 菱形揭示 |
| `plus` | 十字揭示 |
| `strips` | 对角条纹揭示 |
| `wedge` | 楔形揭示 |
| `stretch` | 拉伸入场 |
| `expand` | 展开入场 |
| `swivel` | 旋转入场 |
| `auto` | 按 group id 映射效果（chart→wipe，card-/step-/pillar-→fly，title/takeaway→fade）；类图片 id（hero / figure- / image / img- / kpi）在更大效果池（zoom / dissolve / circle / box / diamond / wheel）中循环，让 deck 中多张图片效果各异；未匹配 id 在 fade / wipe / fly / zoom 中循环 |
| `mixed` | 旧版 16 效果按 group 顺序循环（首组 fade，其余在大池里循环） |
| `random` | 从旧版池中为每个动画组随机抽样 |

**起始模式**：

| 触发 | 行为 |
|---|---|
| `after-previous` | 幻灯片入场后自动级联 |
| `with-previous` | 与幻灯片入场同时启动 |
| `on-click` | 每个动画组由演示者点击触发 |

---

## 4. 编辑 `animations.json`

**硬规则 —— 显式写出每张幻灯片；让 group 继承默认值**。`slides.<slide>` 下的每张幻灯片**必须**自带完整的 `transition` 与 `animation` 块（效果 + 时长 + 错位 + 触发，按需），即便值与 `defaults` 完全相同。这让逐页节奏一眼可读，不必再在脑中合并继承链。group 级覆盖仍为可选——只列出真正偏离幻灯片 `animation` 块的 group。Chrome 组保持缺席（导出器会把它们固定为 `none`）。

`defaults` 仍为必需：它为那些还没出现在 `slides` 中的页（少见，例如编辑中的草稿）提供回退值，并作为你逐页复制粘贴的 deck 级基线单一来源。

**禁止**：

- 遗漏 `svg_output/` 中实际存在的某张幻灯片 —— 每一张产出的页都必须出现在 `slides` 下
- 写出只含 `groups` 而缺 `transition`/`animation` 的幻灯片块
- 为了复述幻灯片级默认效果而把页内所有内容组逐一列举
- 列出 chrome 组（`bg`、`*-header`、`*-footer`、`*-decor`、`nav`、`watermark`、`logo`、`pagenumber`）

| 字段 | 行为 |
|---|---|
| `transition.effect` | 该幻灯片专属的页面切换效果 |
| `transition.duration` | 该幻灯片专属的页面切换时长 |
| `animation.effect` | 该幻灯片专属的默认对象入场效果 |
| `animation.duration` | 该幻灯片专属的默认对象入场时长 |
| `animation.stagger` | 该幻灯片专属的对象入场错位 |
| `animation.trigger` | 该幻灯片专属的起始模式 |
| `groups.<id>.effect` | 该对象专属的入场效果，可为 `auto`、`mixed`、`random` 或 `none` |
| `order` | 仅动画顺序；不改变 SVG 图层顺序 |
| `delay` | 在 `after-previous` 模式下该 group 启动前的额外秒数 |
| `duration` | 该 group 的入场时长（秒）；当语义权重或节奏需要时变化 |

**规范示例 —— 每张幻灯片都带显式 transition + animation；group 仅在偏离时出现**：

```json
{
  "version": 1,
  "defaults": {
    "transition": { "effect": "fade", "duration": 0.4 },
    "animation": { "effect": "fade", "duration": 0.4, "stagger": 0.5, "trigger": "after-previous" }
  },
  "slides": {
    "01_cover": {
      "transition": { "effect": "fade", "duration": 0.5 },
      "animation": { "effect": "fade", "duration": 0.5, "stagger": 0.4, "trigger": "after-previous" }
    },
    "02_agenda": {
      "transition": { "effect": "fade", "duration": 0.4 },
      "animation": { "effect": "fade", "duration": 0.4, "stagger": 0.5, "trigger": "after-previous" }
    },
    "03_market": {
      "transition": { "effect": "wipe", "duration": 0.35 },
      "animation": { "effect": "fade", "duration": 0.4, "stagger": 0.25, "trigger": "after-previous" },
      "groups": {
        "chart": { "effect": "wipe", "order": 2, "duration": 0.6 },
        "insight": { "effect": "fly", "order": 3, "delay": 0.2 }
      }
    },
    "07_hero_quote": {
      "transition": { "effect": "fade", "duration": 0.7 },
      "animation": { "effect": "fade", "duration": 0.7, "stagger": 0.3, "trigger": "after-previous" },
      "groups": {
        "quote": { "duration": 0.9, "delay": 0.3 }
      }
    }
  }
}
```

注释：
- `02_agenda` 原样重复 `defaults`——在新规则下这是有意的，让逐页节奏可一眼审计。
- `03_market` 与 `07_hero_quote` 只列出真正偏离的 group；`title`、`footer`、`bg`、`header` 等不逐一列举。
- Chrome 组永远不列出；导出器会把它们固定为 `none`。

**禁止 —— SVG 污染**：不要在 SVG 文件上加 `data-*` 动画属性。动画定制归 `animations.json`。

---

## 5. 校验与导出

按顺序执行：

```bash
python3 ${SKILL_DIR}/scripts/animation_config.py validate <project_path>
```

```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
```

**校验**：导出的原生 PPTX 应反映对象级覆盖项。`--animation none` 仍会禁用所有逐元素动画并覆盖 `animations.json`。

---

## ✅ 动画定制完成

- [x] 仅在确实请求了对象级定制时才存在 `animations.json`
- [x] 编辑动画覆盖前已查阅 `design_spec.md`、`spec_lock.md` 与可用讲者备注
- [x] `svg_output/` 中的每张幻灯片都出现在 `slides` 下，且带显式 `transition` + `animation` 块
- [x] 仅对那些真正偏离该幻灯片 `animation` 块的 group 加了 group 级条目
- [x] 页面切换与页内对象动画已一起规划
- [x] 切换时长与对象时长针对 deck 节奏刻意选取
- [x] `animation_config.py validate` 通过
- [x] 已用自定义动画覆盖项重新导出 PPTX