---
description: Step 2 detail — project_manager init + import-sources
---

# Step 2：项目初始化（详细）

> 本文件承接 SKILL.md Step 2 的执行细节。

先按[运行环境](../render-runtime.md)确认 Skill/项目/Python 的绝对路径；项目建立后，课程立即执行渲染 `--check` 并保存 runtime.json。后续命令使用同一已验证解释器。字体配置在 Step 4 锁定后，批量生成前加 `--fontconfig` 重验；检查失败先处理环境。

```bash
python3 ${SKILL_DIR}/scripts/project_manager.py init <project_name> --format <format> --dir <课程工作区绝对路径>/projects
```

格式选项：`ppt169`（默认）、`ppt43`、`xhs`、`story` 等。完整格式列表请见 [`../canvas-formats.md`](../canvas-formats.md)。

项目建在课程工作区，后续使用命令返回的绝对路径作为 `PROJECT_DIR`。Skill 安装目录随部署替换，初始化入口会拒绝在其内部创建项目，软链路径同样检查。

课程 handoff 是带相对引用的文件包：整包复制到 `sources/course-handoff/`，连同 source_outline、materials、notes、source_coverage 和 readiness 保持相对位置；引用包外文件时复制并更新引用。复制后运行 `validate_course_handoff.py` 和 `validate_teaching_contract.py`。不移动用户原始课程或拆散整包。旧项目平铺 `sources/` 兼容读取。

其他源内容（按情况选择）：

| 情况 | 操作 |
|-----------|--------|
| 有源文件（PDF/MD 等） | `python3 ${SKILL_DIR}/scripts/project_manager.py import-sources <project_path> <source_files...> --move` |
| 用户直接在对话中提供文字 | 无需导入——内容已在对话上下文中；后续步骤可直接引用 |

> `--move` 只用于本轮生成、允许移动的转换中间文件；用户原始文件用默认复制导入。课程 handoff 按上方整包导入规则处理，避免移动后备注和材料失联。
