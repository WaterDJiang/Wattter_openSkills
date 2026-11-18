# 渲染运行环境

课程在 Step 2 检查环境，字体方案锁定后、批量生成前再检查实际字体配置。恢复会话、切换解释器或配置变化时重验。预检失败先修复环境；不等整套 SVG 完成后才找可用 Python。

## 路径和解释器

- 从本次实际读取的 SKILL.md 定位 Skill 根目录，记录其绝对路径 `SKILL_DIR`；项目根使用课程工作区内的绝对路径 `PROJECT_DIR`，与安装树分开。安装更新会替换运行树，课程产物保存在该树之外。
- 选择候选 Python，运行 `python3 -c 'import sys; print(sys.executable)'` 取得绝对路径，记为 `PYTHON_BIN`。预检通过后全程沿用；安装到另一解释器不算修复。环境记录保存在项目 evidence 下的 runtime.json。
- 以下命令中的变量必须先替换为本次已确认的绝对路径。工具调用间不假定 shell 变量自动保留；新调用重新赋值或直接展开成带引号的绝对路径。
- 查文件先用 `rg --files "$SKILL_DIR/scripts/svg_to_pptx" -g '*text*.py'` 或 `rg -n 'convert_text' "$SKILL_DIR/scripts/svg_to_pptx"`。glob 必须作为带引号的 rg 参数；无匹配表示需改查找条件，不根据猜测拼出脚本名。禁止用未引用的 `text*.py` 让 zsh 提前展开。

## 预检

```bash
"$PYTHON_BIN" "$SKILL_DIR/scripts/render_course_pptx.py" --check --out "$PROJECT_DIR/evidence/runtime-attempt-01"
```

`--check` 不要求已有 PPT；如提供 PPT 则同时验证输入 ZIP 和页数。检查当前 Python 的真实 PyMuPDF 导入、soffice 可执行文件及版本、输出写入/读回。使用非 PATH 安装时显式传 `--soffice <绝对路径>`。`runtime.json` 记录 Python/依赖/Skill/工作目录/实际路径及错误；失败返回非零，并保留 failure.txt/json。输出目录已存在时拒绝覆盖；重试用新的 attempt。

缺 PyMuPDF 时错误中给出绑定当前解释器的安装命令；仅在允许安装依赖的环境执行，或选择已具备依赖的解释器重新预检。不要只运行不明确属于哪个 Python 的 `pip install`。预检不会安装依赖、切换解释器或修改系统字体。

字体方案确定后加 `--fontconfig <已核对的绝对路径>` 再预检。工具只检查配置 XML 可读、根节点和 hash；不证明字体覆盖、替代正确或字体文件可被 LibreOffice 使用。首批样章实际渲染后逐页核对字体。fontconfig 的自定义路径使用绝对路径；源配置在运行期间不可修改。实际渲染使用源配置路径以保留 include 语义，并保存原文快照；其引用的其他配置也应保留在项目内。

## 字体内容准备（仅需要隔离字体目录时）

直接读取系统字体可用时不复制。需要隔离时只给出已确认的字体文件：

```bash
"$PYTHON_BIN" "$SKILL_DIR/scripts/prepare_render_fonts.py" \
  "/已确认路径/中文字体.ttc" --out "$PROJECT_DIR/evidence/fonts-attempt-01"
```

工具用 `copyfile` 复制内容，前后检查 SHA-256；不调用 `copy2/copystat`，不继承系统文件标记。manifest.json 记录来源、实际文件名和 hash；失败尝试保留。fontconfig 的 dir 指向这个绝对目录。替代字体保留真实家族名，沿用已确认的项目级映射；不改字体内部名称、嵌入权限位或 LibreOffice 应用目录。需要改变 PPT 字体声明时先同步视觉锁及受影响页。

中文异常先渲染一页含中文正文、中文备注及大小字号混排的小样，检查 PDF 文字与像素。备注母版由原生导出器建立；若纯正文小样正常、带备注时异常，先检查备注部件与关系。包结构和实际字体可用性确认后再批量渲染，修复后复核受影响页及既有同 hash 证据。

## 实际渲染与错误分级

```bash
"$PYTHON_BIN" "$SKILL_DIR/scripts/render_course_pptx.py" \
  "$PROJECT_DIR/exports/实际文件.pptx" --out "$PROJECT_DIR/evidence/render-attempt-01" \
  --fontconfig "$PROJECT_DIR/实际字体配置.conf"
```

实际渲染会重跑预检。超时默认 120 秒，需要更长时显式传 `--timeout <正秒数>`；超时保留已捕获的 stdout/stderr，不静默换工具重试。

- **预检失败**：依赖/路径/配置问题，非零退出，查看 runtime.json 与 failure.txt。
- **渲染失败**：非零进程、超时、缺失/损坏 PDF、页数不符、文本越界或替换字符，非零退出，查看 renderer.log / diagnostics.json / manifest.json 中已产生的证据及 failure.txt。
- **渲染完成但有警告**：LibreOffice stderr、PyMuPDF 警告原文分别归档，不凭文字猜是哪个组件。即使遇到 `No common ancestor in structure tree`，也不自动过滤；先核对 PDF 页数、文本与像素，再记录影响。
- **视觉验收待完成**：manifest 的 `rendered_requires_review` 只表示实际转换与自动检查成功；仍须按[成品闸口](page-realization.md)逐页审查。未知警告逐项说明，不能以“PDF 已生成”代替视觉通过。

输出目录无法创建时没有可写位置留档，原始路径和异常打印到 stderr，由调用方保留命令输出。已有目录和失败证据不清理、不覆盖。
