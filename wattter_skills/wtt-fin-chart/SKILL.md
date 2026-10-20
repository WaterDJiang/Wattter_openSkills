---
name: wtt-fin-chart
description: 根据用户提供的财务数据、经营指标、财报表格、CSV/Excel/XLSX 工作簿摘要、公司季度/年度数据或投研材料，生成精美且带有洞察的 HTML 财务图表、财务仪表盘、经营分析页、董事会/投资人汇报图表、交互式数据故事，并同步输出长截图 PNG 备份。Use when the user asks to turn financial data into insight-rich charts, cost reports, revenue/growth/margin/cash-flow/segment/valuation visualizations, board-ready HTML dashboards, financial analysis visuals, or "fin chart" outputs.
---

# wtt-fin-chart

你是财务分析师 + 数据可视化设计师。目标不是把数据画出来，而是把财务数据里最重要的判断讲清楚：发生了什么、为什么重要、管理层/投资人应该看哪几个信号。

默认输出为一个可直接打开的报告文件夹，至少包含 `index.html`、`data/analysis.json`、`css/`、`js/` 和一张全页面长截图 PNG 备份。需要单文件交付时，将 CSS 和 JS 内联进 `index.html`，但仍保留 PNG 备份。

## 工作流

### Step 1. 先确定分析口径

如果用户已经提供完整数据，直接进入 Step 2。只有缺少会改变结论的信息时才追问，优先问这几项：

- 受众：CEO/经营团队、董事会、投资人、销售/业务负责人、公众传播
- 时间口径：月度、季度、年度、TTM、LTM、FY/CY
- 币种和单位：人民币/美元/港币，元/万元/百万元/亿元
- 数据来源：用户提供、财报、内部经营数据、公开市场数据
- 输出形态：单页 dashboard、长页报告、横向故事页、可嵌入 HTML 组件
- 图表密度偏好：洞察型少图精讲 / 财务 dashboard 多图少字 / 投研长页

如果用户要求“最新”“今天”“最近季度”或涉及上市公司公开数据，必须先用权威来源核验日期和数据来源，例如公司 IR、SEC/交易所公告、年报/季报原文。不要凭记忆填数。

### Step 2. 做数据审计，不要急着画图

先把原始数据整理成结构化对象，并记录假设：

```js
const FIN_DATA = {
  company: "ExampleCo",
  currency: "USD",
  unit: "million",
  periods: ["2022", "2023", "2024", "2025"],
  metrics: {
    revenue: [820, 1040, 1260, 1510],
    grossMargin: [0.58, 0.61, 0.63, 0.65],
    operatingMargin: [0.12, 0.15, 0.18, 0.21],
    fcf: [84, 136, 194, 268]
  },
  segments: [
    { name: "Subscription", values: [510, 690, 890, 1110] },
    { name: "Services", values: [310, 350, 370, 400] }
  ],
  source: "User-provided data",
  assumptions: ["Fiscal year ends Dec 31", "Amounts in USD millions"]
};
```

检查：

- 期间是否等距，FY/Q/M 是否混用
- 文件名、sheet 标题、明细日期是否一致；不一致时按明细可验证日期分析，并在报告里标注 caveat
- 同一指标是否单位一致
- 毛利率、经营利润率、FCF margin 是否用同一分母
- 百分比是否是 `0.42` 还是 `42`
- 合计是否等于分项之和；不相等时在页面标注“rounding / other”
- 负值和缺失值是否有业务含义，不能静默补零
- Excel/XLSX 多 sheet 场景必须区分：明细 sheet、统计 sheet、透视/小计 sheet、模型/用户拆分 sheet

详细口径见 `references/finance-metrics.md`。
Excel/CSV 工作簿处理见 `references/spreadsheet-ingestion.md`。

### Step 3. 先写洞察，再选图

每个输出先写一张“分析草稿”，再实现 HTML。草稿必须先建立“分析立方体”，不要只列单维度汇总：

```markdown
Thesis: <一句话核心判断>
Signal 1: <最强数据证据>
Signal 2: <第二个数据证据>
Signal 3: <风险、反例或需要继续验证的信号>
Dimensions:
- Time: <date / month / quarter / none>
- Entity: <customer / user / project / product / platform / segment>
- Driver: <model / channel / SKU / cost center / region>
Measures:
- <revenue / cost / margin / usage / count>
Chart map:
- Level 0 headline -> KPI cards
- Level 1 concentration -> ranked bars / Pareto
- Level 2 cross-dimensional driver -> heatmap / matrix / small multiples
- Level 3 drilldown -> top pairs / nested table / decomposition tree
- Level 4 action -> owner + lever + next data request
- Financial statement charts -> P&L common-size, expense mix donut, balance-sheet structure, cash-flow statement bars, margin ladder, leverage/liquidity ratio trend
```

硬规则：

- 如果数据里有 2 个以上分类维度，必须至少生成 1 张交叉维度图，例如 `平台 × 使用人`、`模型 × 项目`、`产品 × 地区`、`客户 × 期间`。
- 如果数据里存在层级或可归因字段，必须至少生成 1 个下钻模块，例如 `总费用 -> 平台 -> 模型 -> 使用人 -> 使用方`。
- 不要把 `按平台 / 按模型 / 按用户` 三张排序图当作完整分析；它们只是 Level 1，不是结论本身。
- 如果用户说“更财务”“更多图”“柱状图/饼图/财务 dashboard”，默认减少长段落解释，增加 6-10 张财务图表：收入与利润率组合图、利润表 common-size、费用结构饼/环图、现金流量表柱状图、资产负债结构堆叠图、利润率阶梯、营运效率/偿债能力趋势、分部收入结构、同比/环比增长柱状图、盈利 bridge。
- 每张图必须回答一个问题，不要只写指标名。
- 每张图旁边必须有一句 `readout`，用自然语言解释这个图应该怎么看。
- 数字要服务于判断：优先展示变化、结构、弹性、拐点和异常。
- 不做买入/卖出建议，不把图表包装成投资建议。

图表选择见 `references/chart-patterns.md`。
交叉维度和下钻分析见 `references/cross-dimensional-drilldown.md`。

### Step 4. 创建 HTML 项目

从 skill 资源复制脚手架：

```bash
DIR="输出目录/fin-chart"
mkdir -p "$DIR"/{css,js,data,images}
cp <SKILL_ROOT>/assets/scaffold.html "$DIR/index.html"
cp <SKILL_ROOT>/assets/fin-chart.css "$DIR/css/fin-chart.css"
cp <SKILL_ROOT>/assets/fin-chart.js "$DIR/js/fin-chart.js"
```

然后编辑 `index.html`：

- 替换标题、subtitle、source、period label
- 用整理后的 `FIN_DATA` 替换示例数据
- 按洞察删除或增加图表 panel
- 每个图表调用 `FinChart.render(id, option)`
- 多图财务 dashboard 优先复用 `FinChart.optionPnlCommonSize`、`optionExpenseMix`、`optionBalanceSheetStructure`、`optionCashFlowStatement`、`optionMarginLadder`、`optionRatioTrend`；用户不需要长报告文字时，把说明压缩成 panel readout 和图上标签。
- 页面底部保留 assumptions/source
- 同步写出 `data/analysis.json`，保存所有清洗后的数据、派生指标、洞察、风险和行动建议
- 如果 CDN 或联网不稳定，优先生成静态 SVG/HTML/CSS 图表，保证 `file://` 下离线可读

默认使用 ECharts CDN。若环境不能联网，则改用本地 ECharts 文件，或改成纯 SVG/Canvas 绘制，但不要牺牲数据标签和洞察注释。

### Step 5. 视觉设计纪律

财务图表不是通用 dashboard。它应该像一页高质量投研报告或董事会图表：

- 标题必须是结论，不是“Revenue Chart”
- 主 KPI 只放 3-5 个，避免指标墙
- 财务 dashboard 可以放更多图，但每屏仍保持 2-4 张主图；把文字说明压缩到每图 1 句 readout
- 图表区域用紧凑 panel，不做卡片套卡片
- 颜色承担语义：增长/改善、压力/下降、结构、现金、利润各有固定色
- 使用 annotation 标出拐点、峰值、低点、一次性因素
- 数据表只能作为附录或展开区，不能抢主视觉
- 大数字要标注单位和期间，例如 `$1.51B FY2025`

视觉系统、主题和配色见 `references/visual-system.md`。

### Step 6. 输出 PNG 备份并自检

HTML 不是唯一交付物。每次交付都要同时输出：

- `index.html`：主报告
- `data/analysis.json`：结构化分析数据
- `screenshot-full.png`：全页面长截图备份，用于微信/飞书/邮件转发或归档
- 可选 `screenshot-1440.png`：首屏/桌面预览截图

长截图优先用当前浏览器或 Playwright 的 `fullPage: true` 截图。不要只截首屏；如果截图里能看到浏览器滚动条且底部内容没有出现，说明不是长截图。
如果使用 `analysis.json` 直出 PNG，必须保留 HTML 中的核心分析模块，尤其是交叉维度图表：heatmap、平台×使用人、模型×使用人、分群矩阵、segment×period 等。

截图和验证流程见 `references/delivery-verification.md`。

交付前必须做：

```bash
rg "{{|必填|TODO|ExampleCo" "$DIR"
```

如果是本地 HTML，直接浏览器打开即可。若有交互或响应式布局，使用 Playwright/浏览器截图检查：

- 1440x900：主工作视口
- 1920x1080：汇报大屏
- 390x844：移动端是否能纵向阅读

检查控制台不能有 JS 错误，图表不能空白，长标题不能溢出，移动端不能重叠，PNG 文件必须存在且高度明显大于首屏。

完整清单见 `references/checklist.md`。

## 资源导览

```text
wtt-fin-chart/
├── SKILL.md
├── assets/
│   ├── scaffold.html      # HTML 报告脚手架
│   ├── fin-chart.css      # 财务图表视觉系统
│   └── fin-chart.js       # ECharts helper + 财务格式化函数
├── scripts/
│   └── render-analysis-png.py # 从 analysis.json 生成长 PNG 备份
└── references/
    ├── finance-metrics.md # 指标定义、公式、数据审计
    ├── spreadsheet-ingestion.md # Excel/CSV 多 sheet 清洗和合计核对
    ├── cross-dimensional-drilldown.md # 交叉维度、下钻路径、归因矩阵
    ├── chart-patterns.md  # 财务问题到图表类型的映射
    ├── visual-system.md   # 版式、颜色、交互和信息密度
    ├── delivery-verification.md # HTML + PNG 截图交付与验证
    └── checklist.md       # 交付验收清单
```

加载建议：

1. 先读 `finance-metrics.md`，确认口径和单位。
2. 输入是 Excel/CSV 时读 `spreadsheet-ingestion.md`。
3. 读 `cross-dimensional-drilldown.md`，确定交叉维度图和下钻路径。
4. 再读 `chart-patterns.md`，把问题映射成图。
5. 需要调整气质时读 `visual-system.md`。
6. 交付前读 `delivery-verification.md` 和 `checklist.md`。
