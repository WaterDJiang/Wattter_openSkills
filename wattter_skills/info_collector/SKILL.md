---
name: info-collector
description: 基于配置驱动的通用信息收集助手。支持多数据源模块化扩展，自动采集、分析并生成结构化报告。
---

# 信息收集助手 (Info Collector)

本技能是一个可扩展的信息采集框架，旨在自动化监控多个信息源，收集数据并生成统一的分析报告。

## 核心特性

1.  **配置驱动**：所有行为（目标源、筛选条件、运行参数）均由 `config.yaml` 定义，无需修改代码。
2.  **模块化架构**：每个数据源（如微博、小红书）均为独立模块，支持动态加载和按需执行。
3.  **智能持久化**：内置浏览器上下文持久化（Cookie/Session），一次登录，长期有效。
4.  **动态报告**：根据采集的数据类型自动匹配最合适的模板，生成 Markdown 格式的分析报告。

## 快速开始

### 1. 环境准备

```bash
cd skills/info-collector
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置说明

核心配置文件为 `config.yaml`。我们推荐使用 **YAML** 格式，因为它支持注释，结构清晰，非常适合作为人类可读写的配置文件。

**配置结构通用示例**：

```yaml
global:
  browser:
    headless: false  # 是否无头模式
    timeout: 180000  # 全局超时设置
  output_dir: "outputs"

modules:
  # 模块键名对应 scripts/modules/ 下的文件名 (如 weibo.py -> weibo)
  <module_name>:
    enabled: true    # 默认是否启用
    # 模块特定配置 (如 targets, filters, limit 等)
    ...
```

*注意：具体的参数选项（如筛选条件、目标列表）请直接参考 `config.yaml` 文件中的详细注释。*

### 3. 运行方式

脚本支持灵活的命令行参数，可覆盖配置文件中的默认行为。

**默认运行**（执行配置文件中所有 `enabled: true` 的模块）：

```bash
python scripts/collector.py
```

**指定模块运行**（动态覆盖配置）：

使用 `--modules` 参数可指定本次要运行的模块（忽略配置中的开关状态），支持多模块顺序执行。

```bash
# 语法：python scripts/collector.py --modules <模块名1> <模块名2> ... [其他参数]

# 示例：仅运行小红书调研（需配合关键词）
python scripts/collector.py --modules xiaohongshu --keyword "您的关键词"

# 示例：按顺序运行微博和小红书
python scripts/collector.py --modules weibo xiaohongshu --keyword "您的关键词"
```

**控制浏览器显示模式**（覆盖配置）：

默认情况下，浏览器显示模式（有头/无头）由 `config.yaml` 决定（默认为 `true` 即无头模式）。
**智能特性**：如果脚本在无头模式下检测到登录失效，会自动重启并切换到有头模式，提示用户手动登录。

您也可以通过命令行参数进行强制切换：

```bash
# 强制开启无头模式（后台运行，不显示浏览器窗口）
python scripts/collector.py --headless

# 强制开启有头模式（显示浏览器窗口，便于调试或人工介入）
python scripts/collector.py --headful
```

### 4. 报告输出

报告将自动生成在 `outputs/` 目录（或配置文件指定的目录）下。
文件名格式会自动包含参与的模块名，例如：`summary_weibo_xiaohongshu_<时间戳>.md`。

## 开发者指南

**添加新数据源**：

只需在 `scripts/modules/` 目录下创建一个新的 Python 文件（例如 `zhihu.py`），继承 `BaseModule` 类并实现 `run()` 方法即可。

系统会自动发现并加载该模块，您只需在 `config.yaml` 中添加对应的 `zhihu` 配置块即可生效。
