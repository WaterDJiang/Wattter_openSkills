# Wattter 技能集

个人开源 AI 技能集合，通过 Plugin 市场分发，增强 Claude/Trae 等 AI 代理的自动化能力。

## 可用技能

### 内容发布与自动化
- **wtt-auto-poster**：自动化内容发布助手。支持将 Markdown 文章自动发布到知乎和微信公众号，具备 Mac 风格代码块渲染、图片自动上传和自定义样式功能。
- **wtt-post-geo**：多平台 GEO 内容发布助手。通过“官方 API → 浏览器登录态 adapter → OpenCLI UI”分层路由，把同一份内容发布或创建草稿到微信公众号、微博、知乎专栏、CSDN、掘金、百家号、博客园、小红书、Twitter/X；统一处理平台格式、GEO 链接、媒体素材、防重复回退、状态校验与最终链接回报。微博默认生成并发布摘要短帖，只有用户明确要求时才走长文。

### 内容创作与 SEO
- **wtt-seo-geo-writer**：SEO / GEO 内容撰稿人。将输入内容转化为 SEO 或 GEO 优化的 Markdown 文章，主路径只有 SEO 与 GEO 两条；垂类品牌/行业语气作为可选 profile，仅在用户明确提及时加载。

### 信息采集与研究
- **wtt-info-collector**：基于配置驱动的通用信息收集助手。支持多数据源模块化扩展，自动采集、分析并生成结构化报告。
- **wtt-trend-radar**：多平台实时热点聚合与分析工具。支持从知乎、微博、抖音、B站等主流平台获取热搜数据，并根据关键词进行精准筛选。

### 产品与竞品分析
- **wtt-app-review-insights**：App Store 评论洞察分析工具。输入 App 名称、URL 或 App ID，自动抓取评论并通过 AI 深度挖掘产品痛点、机会、正面信号、用户分层、版本风险和行动建议，输出结构化洞察报告。

### 演示文稿与视觉表达
- **wtt-magazine-deck**：杂志风网页演示生成工具。支持生成自包含横向翻页 HTML deck，覆盖 editorial 与 swiss 两种风格，适用于分享、发布会、报告和作品展示。
- **wtt-course-pptx-builder**：课程 PPT 构建器。支持将 PDF、DOCX、URL、Markdown 等源文档转换为高质量 SVG 页面并导出为 PPTX，覆盖模板套用、AI 生图、图像搜索、实时预览、图表校准、动画定制和旁白生成等完整流程。

### 知识库与项目工程
- **wtt-llm-wiki-builder**：LLM 友好知识库构建工具。支持三种模式：从零搭建 wiki 范式（Build）、增量编译新资料（Compile）、扫描修复已有 wiki 健康问题（Lint）。
- **wtt-project-harness-generator**：项目 Harness 生成器。扫描项目代码，通过对话引导理解项目 DNA，自动生成 CLAUDE.md 和 AGENTS.md，包含组件化、规则、UI/UX 等规范。

### 招聘与人才评估
- **wtt-resume-screener**：简历筛选与评估助手。输入 JD 与候选人简历（PDF/DOCX/Markdown），自动识别岗位级别（实习/校招/初级/中级/高级/专家/管理），从 HR 经理 + 业务负责人双视角进行评估，输出包含匹配度评分、维度拆解、双视角点评、推荐结论和面试重点的 Markdown 报告。

## 安装与使用

本项目使用 `openskills` 管理和加载技能。

### 1. 同步技能
将本仓库中所有技能注册到当前环境：

```bash
openskills sync
```

该命令会更新根目录下的 `AGENTS.md` 文件，使 AI 代理能够发现可用技能。

### 2. 使用技能
同步完成后，可以直接向 AI 代理发出相关指令。代理会检查 `AGENTS.md` 并通过以下方式调用技能：

```bash
openskills read <技能名>
```

使用示例：
"帮我把这篇文章发布到微信公众号。"
"帮我收集关于这个话题的信息。"

## 项目结构
- `wattter_skills/`：所有技能的源码和定义。
- `AGENTS.md`：AI 代理可用的技能清单文件。
- `.claude-plugin/`：Plugin 市场打包配置。

## 许可证
各技能的具体许可信息请查看对应目录。
