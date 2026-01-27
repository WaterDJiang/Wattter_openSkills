# Wattter Skills Collection

This repository contains a collection of AI skills designed to enhance the capabilities of Claude/Trae agents.

## Available Skills

### Content Publishing & Automation
- **auto-poster**: 自动化内容发布助手。支持将 Markdown 文章自动发布到知乎和微信公众号，具备 Mac 风格代码块渲染、图片自动上传和自定义样式功能。

### Information Collection & Research
- **info-collector**: 基于配置驱动的通用信息收集助手。支持多数据源模块化扩展，自动采集、分析并生成结构化报告。

## Installation & Usage

This project uses `openskills` to manage and load skills.

### 1. Sync Skills
To register all skills in this repository with your current environment, run:

```bash
openskills sync
```

This will update the `AGENTS.md` file in the root directory, making the skills discoverable by the AI agent.

### 2. Use a Skill
Once synced, you can ask the AI agent to perform tasks related to these skills. The agent will check `AGENTS.md` and invoke the appropriate skill using:

```bash
openskills read <skill-name>
```

For example:
"Help me publish this article to WeChat."
"Collect information about this topic."

## Structure
- `wattter_skills/`: Contains the source code and definitions for all skills.
- `AGENTS.md`: The manifest file listing all available skills for the AI agent.
- `.claude-plugin/`: Configuration for plugin packaging.

## License
See individual skill directories for specific license information.
