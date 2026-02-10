---
name: trend-radar
description: 多平台实时热点聚合与分析工具。支持从知乎、微博、抖音、B站等主流平台获取热搜数据，并根据关键词进行精准筛选。
---

# 热点雷达 (Trend Radar)

本技能通过聚合多平台实时榜单，帮助用户快速洞察特定领域或话题的全网热点。它采用沙盒运行模式，通过 Python 脚本和浏览器自动化技术直接从数据源获取最新信息。

## 核心特性

1.  **多平台聚合**：实时获取知乎、微博、抖音、B站、百度等 11+ 主流平台的热点榜单。
2.  **动态渲染**：集成 Playwright 绕过常规 API 限制，确保数据采集的稳定性。
3.  **精准筛选**：支持根据用户输入的关键词对海量热点进行实时过滤。
4.  **结构化输出**：返回包含标题、热度、来源平台及原始链接的 JSON 格式数据。

## 使用指南

### 1. 环境初始化
在使用前，请确保已安装必要的依赖：
```bash
pip install -r skills/trend-radar/requirements.txt
playwright install chromium
```

### 2. 动态关键词识别
本技能**不需要**预先在配置文件中定义关键词。AI 助手会根据你的输入，自动识别核心话题并转换为搜索指令。
- **高级过滤语法**：
    - `+词语`：结果必须包含。
    - `!词语`：结果必须排除。
    - `普通词`：包含其中之一即可。

### 3. 脚本运行
AI 会根据需求动态生成调用指令。
- **基本用法**：`python3 skills/trend-radar/scripts/collector.py --keywords "关键词1, 关键词2"`
- **指定输出路径**：`python3 skills/trend-radar/scripts/collector.py --keywords "AI" --output "./my_reports/ai_trends.md"`
- **全网热搜**：`python3 skills/trend-radar/scripts/collector.py --keywords ""`

### 4. 目录结构
- `scripts/`: 核心采集逻辑。
- `config/`: 平台配置 (API 列表)。
- `assets/`: 分析模板与提示词。
- `reports/`: 默认报告存储目录（如果未指定 `--output`）。

## 技术原理
- **引擎**：Playwright (Chromium)
- **数据源**：newsnow API 聚合分发
- **处理**：异步并发请求 (asyncio) + 跨平台结果排序
