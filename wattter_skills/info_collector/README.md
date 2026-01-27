# Info Collector Workspace / 信息收集助手工作区

This directory contains the configuration and output files for the Info Collector skill.
本目录包含信息收集助手（Info Collector）技能的配置文件和输出文件。

## Configuration / 配置说明

Edit `config.yaml` to customize your data sources and collection parameters.
See the file comments for detailed instructions.

请编辑 `config.yaml` 文件以自定义数据源和采集参数。
详细说明请参阅文件中的注释。

## Login & Session Management / 登录与会话管理

The collector defaults to **Headless Mode** (background execution) for efficiency.
采集器默认为 **无头模式**（后台运行）以提高效率。

- **Automatic Mode Switching / 自动模式切换**:
  If a module detects that login is required (cookies expired or first-time use), the script will automatically restart in **Headful Mode** (visible browser).
  如果模块检测到需要登录（Cookie 过期或首次使用），脚本会自动重启并切换为 **有头模式**（显示浏览器）。

- **Manual Login / 手动登录**:
  When the browser window appears, please log in manually. The script will wait for successful login before proceeding.
  当浏览器窗口出现时，请手动完成登录。脚本会等待登录成功后继续执行。

- **Persistence / 持久化**:
  Login sessions are saved in `browser_data/`. Once logged in, subsequent runs will remain headless.
  登录会话保存在 `browser_data/` 目录中。一旦登录成功，后续运行将保持无头模式。

## Usage / 使用指南

Run the collector script (typically via the skill command) and it will use the configuration in this folder.
运行收集脚本（通常通过 skill 命令），它将自动使用本文件夹中的配置。

To run specific modules:
运行指定模块：

```bash
python <path_to_collector.py> --modules weibo xiaohongshu
```
