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
- **wtt-nine-comic-imagegen**：多风格漫画与信息图提示词生成器。支持 9 号漫画恶搞科普、手绘信息图、四格漫画、线条人插画、生活感人像五种风格，默认输出中文提示词，可直接用于 ChatGPT / 即梦 / Midjourney 等图片生成平台。
- **wtt-code-animation-studio**：代码动画工坊。将想法、主题、文章或现成剧本制作为前端代码动画，按内容与实际旁白决定时长，先推荐风格由用户选择再制作，覆盖手绘纸纹、复古印刷网点、像素、水彩、沙画、粉笔、粒子、马赛克、黏土外观、MG 与混合画法，交付中文剧本、分镜、可改源码和带声音的 MP4。

### 知识库与项目工程
- **wtt-llm-wiki-builder**：LLM 友好知识库构建工具。支持三种模式：从零搭建 wiki 范式（Build）、增量编译新资料（Compile）、扫描修复已有 wiki 健康问题（Lint）。
- **wtt-project-harness-generator**：项目 Harness 生成器。扫描项目代码，通过对话引导理解项目 DNA，自动生成 CLAUDE.md 和 AGENTS.md，包含组件化、规则、UI/UX 等规范。

### 招聘与人才评估
- **wtt-resume-screener**：简历筛选与评估助手。输入 JD 与候选人简历（PDF/DOCX/Markdown），自动识别岗位级别（实习/校招/初级/中级/高级/专家/管理），从 HR 经理 + 业务负责人双视角进行评估，输出包含匹配度评分、维度拆解、双视角点评、推荐结论和面试重点的 Markdown 报告。

## 安装与使用

支持三种安装方式，按所用 Agent 选择。

### 方式一：Claude Code Plugin 市场（推荐）
本仓库已注册为 Claude Code Plugin 市场（`.claude-plugin/marketplace.json`），在 Claude Code 中直接安装：

```bash
# 1. 添加市场
/plugin marketplace add WaterDJiang/Wattter_openSkills

# 2. 按需安装单个技能，如 auto-poster
/plugin install wtt-auto-poster-skills@wattter-skills
```

插件名与 marketplace.json 的 `plugins[].name` 一致，格式为 `wtt-<技能名>-skills`。

### 方式二：Codex
Codex CLI 原生支持 Agent Skills 开放标准，把技能目录放入其技能目录即可被自动发现：

```bash
git clone https://github.com/WaterDJiang/Wattter_openSkills.git
mkdir -p ~/.codex/skills
cp -r Wattter_openSkills/wattter_skills/wtt-auto-poster ~/.codex/skills/
```

### 方式三：openskills（跨 Agent 通用）
适用于任何基于 AGENTS.md 发现技能的代理（Codex、Trae 等）：

```bash
openskills sync          # 将本仓库技能注册到 AGENTS.md
openskills read <技能名>  # 代理按需读取技能内容
```

### 调用技能
安装后直接向 AI 代理发出自然语言指令即可，例如：
"帮我把这篇文章发布到微信公众号。"
"帮我收集关于这个话题的信息。"

## 项目结构
- `wattter_skills/`：所有技能的源码和定义。
- `AGENTS.md`：AI 代理可用的技能清单文件。
- `.claude-plugin/`：Plugin 市场打包配置。

## 许可证
本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 许可，禁止商业用途。
