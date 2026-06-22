---
description: 在浏览器 SVG 编辑器未运行时启动它，并在 Step 7 导出后应用用户提交的批注
---

# 实时预览工作流

> **目的**：(1) 在当前没有预览服务运行时启动/重开浏览器 SVG 编辑器；(2) 在 Step 7 导出完成后应用用户提交的批注。
>
> **不在范围**：执行器强制要求的自动启动——那部分在 [`SKILL.md`](../SKILL.md) Step 6 中。已经运行的预览不要重启。

## 何时运行

- **启动（Step 1）** —— 预览服务当前未运行，且用户希望查看 deck 或点击元素。典型场景：在新聊天中导出后再次进入；或用户之前点击了 **Exit preview**，现在希望恢复。
- **应用批注（Step 2）** —— Step 7 已产出至少一份 PPTX，且用户给出"应用批注"的信号。触发条件包括：
  - 引用浏览器提示（`Changes saved to svg_output...` / `修改已保存到 svg_output...`）
  - 说 `apply my annotations` / `apply my edits` / `应用注解` / `开始应用` / 等价表达

## 何时不运行

- 预览服务已在运行 → 直接把 URL 给用户即可，不要重启。
- 用户给出了精确的聊天编辑指令（如"把第 3 页标题改成 X"）→ 直接编辑 SVG。
- 用户希望整体重新生成 → 使用主流水线。
- 本项目从未跑过 Step 7 → 此时无法应用批注，请先完成主流水线。

---

## Step 1：启动 / 重开编辑器

**前置条件**：本项目上没有预览服务运行。

```bash
python3 ${SKILL_DIR}/scripts/svg_editor/server.py <project_path>
```

（普通模式——没有 `--live`。`--live` 标志仅供 Step 6 的自动启动使用。）

服务监听 `127.0.0.1:5050`，在本地桌面打开浏览器，直接编辑 `<project_path>/svg_output/`。当它打印出 `SVG Editor running at http://localhost:5050` 后，用用户的语言发一条简短消息告知：

- 编辑器位于 `http://localhost:5050`
- **直接编辑**（确定性的微调——措辞、颜色、坐标、SVG 属性）：选中元素 → 在右侧面板修改控件 → 预览立即更新，但任何内容在点击 **Apply changes** 之前都不会写入 `svg_output/`。`Ctrl+Z` 或 **Undo** 按钮可一步步丢弃已分阶段的编辑；已应用的变更会记录到 `<project>/.live_edits.jsonl`。重新导出仍由聊天驱动：说 `"re-export"` / `"重新导出"` 即可刷新 PPTX。
- **批注**（需要 AI 判断 / 重新排版的变更）：选中元素 → 填写指令 → 点击 **Add annotation** 加入分阶段批注 → 点击 **Apply changes** 把批注标记写入磁盘 → 回到聊天说 `apply my annotations`（或引用浏览器提示）
- 跳过编辑器，直接在聊天里描述改动即可

不要等用户确认再启动——用户已经要求预览，启动本身就是响应。端口冲突 → 用 `--port <其他>` 并报告新 URL。远程访问 → 见附录。

---

## Step 2：应用已提交的批注

🚧 **GATE**：`<project_path>/exports/` 中至少有一份 `*.pptx`（Step 7 已完成）。否则不要应用批注——告诉用户先完成主流水线。

由"何时运行"列出的用户信号触发。

1. 探测批注：
   ```bash
   python3 ${SKILL_DIR}/scripts/check_annotations.py <project_path>
   ```
   输出已经按 `file → element_id → 批注文本 → 内容预览` 列出了每一项待办。可直接把它当作待办清单使用；不需要自己去重新解析 SVG 属性。
2. 若输出显示无批注：告诉用户，停止。
3. 对列出的每条批注：
   - 按批注文本在 `<project_path>/svg_output/<file>` 中编辑目标元素。
   - 从该元素移除 `data-edit-target` 与 `data-edit-annotation`。
4. 重新导出：
   ```bash
   python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
   python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
   ```
5. 用用户的语言告诉用户：批注已应用，新 PPTX 已导出，预览仍在运行。若浏览器还停留在旧页面，刷新或重新选择页面。
6. 循环：又提交了新批注 → 从 step 1 重来；用户表示完成或说"stop preview" → 结束。

---

## 备注（编辑器不变量——在 SKILL.md Step 6 中被引用）

- **UI**：中英双语；根据 `navigator.language` 自动检测，结果保存在 `localStorage`，通过右侧面板的 **中 / EN** 按钮切换。幻灯片导航：中间面板顶部有首页/上一张/下一张/末页按钮，外加 `←` / `→` / `Home` / `End`（在批注文本框内输入时会被屏蔽）。
- **按钮**：`Add annotation` 把批注文本分阶段存入内存；`Apply changes` 把分阶段的直接编辑与批注标记写入磁盘，并保持服务继续运行；**Exit preview** 是唯一会停止 Flask 的 UI 操作。
- **直接编辑（无 AI）**：选择模式决定右侧面板内容。单元素 = 完整对象检查器（几何、安全的文本内容、原始 SVG 属性，但 `id`、UI `class`、事件处理器、href 等受保护字段除外）。SVG `<g>` 分组 = 组级编辑面板；通过 `Alt/Option` + 点击或在子元素上点 **Select parent group** 进入。多选 = 仅在顶层被选对象之上的有限批量编辑器：共享 x/y，加上 `fill` / `stroke` / `opacity`；只有当选中对象全是 `text`/`tspan` 时才出现文本样式字段（`font-size` / `font-family` / `font-weight` / `text-anchor`）。预览立即更新；写入磁盘必须等 **Apply changes**。
- **拖拽移动**：按住并拖动已选中的元素即可在画布上重新定位（选中是单独的一次点击，因此背景永远不会被误拖）；多选时整个选区一起移动。指针位移通过每个元素自身的 CTM 映射，无论视口缩放或组变换如何，移动都跟随光标。每次释放为每个被移动的元素分阶段一次直接编辑（与几何输入产生的 `x`/`y` 或 `transform` 写入一致），预览实时更新，仅在 **Apply changes** 时落盘；在空白画布上拖动仍为橡皮筋框选。分阶段失败时画布回滚到拖动前位置。
- **方向键微调**：选中一个或多个元素时，`↑ ↓ ← →` 每次移动 1px，`Shift + 方向键` 移动 10px（在批注框中输入时会被屏蔽）。只有在未选中任何元素时，方向键才用于切换幻灯片。走的是和拖拽相同的分阶段/合并路径——一阵快速微调会合并为一个撤销步。
- **重叠拾取器**：在画布任意位置右键，可列出光标处全部可选元素（由上至下），让堆叠的形状能被命中而不必盲切。左键行为不变（选中最顶层）。鼠标悬停某行会高亮对应元素；点击即选中；`Esc` 或外部点击关闭列表。当光标下恰好只有一个元素时，右键会直接选中它。
- **撤销**：`Ctrl+Z` 或 **Undo** 按钮丢弃当前幻灯片最近一次分阶段的直接编辑（本次会话、每页独立 LIFO）。对**同一元素同一组字段**的连续编辑（如多次微调同一颜色或坐标）会合并为一步撤销，保留编辑前的原始值；切换元素或字段则开新步。已应用的新旧历史追加到 `<project>/.live_edits.jsonl`；未应用的分阶段编辑仅在内存中。
- **未保存工作的保护**：分阶段的直接编辑与批注变更（新增或删除）都保存在服务进程内存中，直到 **Apply changes**；只要还有未应用项，关闭标签页就会触发浏览器的"离开此站点？"提示，因为闲置超时或进程被杀都会把它们丢掉。
- **重新导出由聊天驱动**：应用变更只会更新 `svg_output/`。刷新 PPTX（finalize + svg_to_pptx）仍是聊天侧动作——编辑器绝不直接跑导出流水线。
- **停止条件**：服务在用户点击浏览器中的 **Exit preview**、在聊天中要求停止、闲置超时触发、或进程被外部终止时停止。
- **端口**：默认 `5050`；可用 `--port <其他>` 覆盖。
- **闲置超时**：普通模式 `900s`，`--live` 模式 `7200s`；可用 `--timeout <seconds>` 覆盖（`0` 表示禁用）。
- **每项目单实例**：`<project_path>/.live_preview.lock` 记录运行中的 pid + port。同一个项目第二次启动会被拒绝并打印现有 URL；进程已死的过期锁在下次启动时被覆盖。仅当进程已不存在但锁仍在时手动删除（极少见——`kill -9` 是常见原因）。
- **临时 id**：编辑器运行期间每个元素会获得一个临时 `_edit_N` id。保存时仅带批注的元素保留 id；未批注的 `_edit_N` id 在回写前会被剥掉。
- **浏览器预览**：服务端会把 `<use data-icon>` 占位符就地内联、并提供 `images/*` 服务，让 SVG 正确渲染；磁盘上的 SVG 不会被这次预览修改。

---

## 附录：远程访问

若项目位于远程 Linux 服务器，使用 `--no-browser`：

```bash
python3 ${SKILL_DIR}/scripts/svg_editor/server.py <project_path> --no-browser
# 或用于 Step 6 在远程主机上的自动启动：
python3 ${SKILL_DIR}/scripts/svg_editor/server.py <project_path> --live --no-browser
```

- **VS Code / Cursor Remote-SSH**：打开 **PORTS** 面板（`Ctrl+Shift+P` → `Ports: Focus on Ports View`），点击 **Forward a Port**，输入 `5050`。工作区会自动记住。
- **Termius**：在左侧栏（顶层、非嵌套）打开 **Port Forwarding** 模块。添加规则，**Type = Local**，Host 填你的远程主机，Binding `127.0.0.1:5050`，Destination `127.0.0.1:5050`。保存后启动该规则（▶ 按钮）。
- **普通 SSH**：`ssh -L 5050:127.0.0.1:5050 <user>@<host>`（或把 `LocalForward 5050 127.0.0.1:5050` 加进 `~/.ssh/config`）。

然后在本地浏览器打开 `http://localhost:5050`。