# wtt-post-geo 重命名规格

## 目标

- 将 skill 从 `wtt-post-opencli` 重命名为 `wtt-post-geo`。
- 名称突出“多平台发布与 GEO 分发”，不再把 OpenCLI 绑定在 skill 名称中。

## 范围

- 将目录改为 `skills/wtt-post-geo/`。
- 同步更新 `SKILL.md` frontmatter、skill README、脚本说明、历史规格和发布产物中的旧绝对路径。
- 同步更新仓库 `CLAUDE.md`、`AGENTS.md` 与 `.claude-plugin/marketplace.json` 的技能登记。
- 不修改平台发布逻辑、OpenCLI adapter 命令名、发布结果或账号配置。

## 验收标准

- `skills/wtt-post-geo/SKILL.md` 的 `name` 为 `wtt-post-geo`。
- 除本迁移规格的历史说明外，仓库运行时文件中不存在 `wtt-post-opencli` 或 `skills/wtt-post-opencli` 引用。
- 根部三份技能登记只包含新名称，skill 总数不变。
- 全部单元测试、JavaScript 语法检查和 `quick_validate.py` 通过。
- Git 能识别为目录重命名，不丢失原有文件和发布产物。

## 影响面

- 已安装环境中的 `wtt-post-opencli` 旧软链需要在下次运行仓库同步脚本时清理并创建 `wtt-post-geo` 软链。
- OpenCLI 用户级 adapter 安装目录和命令保持不变，无需重装。
