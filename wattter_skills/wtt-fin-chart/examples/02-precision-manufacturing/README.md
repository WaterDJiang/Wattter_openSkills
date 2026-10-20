# 案例 02 · MingYuan Precision（精密制造）

## 公司画像

- **公司**：东莞市铭远精密结构件有限公司（MingYuan Precision）
- **业务**：精密金属结构件（铝合金/不锈钢冲压、CNC 后处理、表面阳极氧化），主要服务消费电子 + 新能源汽车 + 工业自动化客户
- **币种 / 单位**：CNY / 百万元
- **财年**：与日历年同步（Jan–Dec）
- **数据状态**：FY2023 / FY2024 经四大事务所审计；FY2025 Q3 末在审，Q4 为管理层预测
- **特殊身份**：高新技术企业 + 专精特新（享 15% 优惠所得税率），已启动 IPO 辅导备案

## 这份案例想让 Skill 表达的财务故事

> MingYuan 用 Capex 换了一个新增长曲线，但接下来半年是验证期。

核心 Signal：
1. 营收两年 CAGR 24.0%（¥492.1M → ¥757.3M）
2. 新能源汽车占比从 7.8% 升至 28.4%，结构性切换完成中段
3. 毛利率 30.2%（2024）→ 29.3%（2025Q3），0.9 pt 预警已出现
4. FCF 三年负值：-10.8 / -40.1 / -6.5；CFO 仍正向（41.6 / 45.5 / 75.5）
5. 有息负债从 ¥81M 增至 ¥230M，资产负债率 46.3% → 56.9%
6. 应收账款周转天数 65.8 → 78.5，CCC 由 88 升至 106

**下一阶段要回答**：增长是否带着利润和回款？这是 IPO 估值能否守住的关键半年。

## 文件清单（标准办公格式）

```
02-precision-manufacturing/
├── README.md                    # 本文件
├── raw-data/                    # 4 份互相勾稽的模拟材料（Excel + PDF）
│   ├── README.md                                  # 素材清单与 Skill 入口映射
│   ├── 01-季度利润表-FY2023-FY2025.xlsx           # 11 季度 P&L + 月度营收 + 成本结构 + 原材料价格
│   ├── 02-客户与交叉维度-FY2024.xlsx              # TOP10 客户 + 客户×行业 + 客户×工艺 + DSO + 订单储备
│   ├── 03-三表与财务比率-FY2023-FY2025.xlsx       # 资产负债表 + 现金流量表 + 财务比率 + 应收账款账龄 + ESG
│   └── 04-FY2025IPO前投资分析报告.pdf              # 8 页 IPO 前投资分析报告
└── working-data/
    └── analysis.json                    # 已按 Skill 数据契约清洗好的结构化数据
```

## 如何让 Skill 跑这份案例

### 调用 1：直接给清洗好的 analysis.json（最快）

```text
请基于 working-data/analysis.json 给 MingYuan Precision 生成一份 IPO 前财务回顾报告。

受众：Founder、CFO、IPO Sponsor、Lead Investors
目标：投研长页（董事会讨论 Pre-IPO 估值用）
强调：① 新能源汽车品类作为第二增长曲线；② 客户集中度动态重塑（富鸿→蔚蓝）；
      ③ Capex 投入回收期的现金压力；④ 2025Q3 毛利率预警的解释；
      ⑤ 营运资本结构性拉长（新能源汽车 DSO）。
输出：index.html + analysis.json + screenshot-full.png。
```

### 调用 2：把 3 份 xlsx + 1 份 PDF 当作原始材料交给 Skill（最真实）

```text
请阅读 raw-data/ 下的 4 份材料（3 份 xlsx + 1 份 PDF）：
- 01: 季度利润表 + 月度营收 + 成本结构
- 02: TOP10 客户 + 客户×行业 + 客户×工艺交叉矩阵
- 03: 三表 + 财务比率 + 应收账款账龄
- 04: IPO 前投资分析报告（PDF）

按 Skill 的 Step 2 数据审计 → Step 3 写洞察 → Step 4 生成 HTML 完整流程跑一遍。
受众：董事会 + IPO 评估
目标：长页报告（突出 Capex 与营运资本视角）
强调：FCF 三年负值的合理性 vs 融资压力，以及 TOP1 客户切换的合规披露
```

### 调用 3：开发者本地复刻

```bash
SKILL=~/.claude/skills/wtt-fin-chart
OUT=~/Desktop/mingyuan-fy25
mkdir -p "$OUT"/{css,js,data,images}
cp "$SKILL/assets/scaffold.html" "$OUT/index.html"
cp "$SKILL/assets/fin-chart.css" "$OUT/css/fin-chart.css"
cp "$SKILL/assets/fin-chart.js"  "$OUT/js/fin-chart.js"
cp working-data/analysis.json "$OUT/data/analysis.json"
open "$OUT/index.html"
```

## 这份案例在 Skill 中的关键使用

| Skill 能力 | 体现位置（raw-data 文件 → 对应图表） |
|------------|---------------------------------------|
| 收入 × 利润率组合图（含负 FCF margin 警示） | 01 P&L → `metrics.revenue / grossMargin / operatingMargin / fcfMargin` |
| 行业结构切换（100% 堆叠柱） | 02 行业 sheet → `segments_by_industry` |
| 工艺结构 + 毛利率差异 | 02 工艺 sheet → `segments_by_process` |
| 客户 × 行业 cross heatmap | 02 客户×行业 sheet → `topCustomers2024` |
| 客户 × 工艺 cross heatmap | 02 客户×工艺 sheet → `customerProcessCross2024` |
| 季度 P&L small multiple | 01 P&L sheet → `quarterlyPnL` (12 个季度) |
| 成本结构拆分（制造业特有） | 01 成本结构 → `costStructure` (6 项) |
| 三表 + 现金流 | 03 BS + CF 部分 |
| 应收账款账龄堆叠图 | 03 账龄 sheet（4 个时间段 × 3 个年度） |
| 比率趋势（ROE / 资产负债率 / CCC） | 03 比率 sheet → 派生 |
| 估值锚 + 同业对照 | 04 PDF 估值锚章节（外部对照） |

## 数据完整性自检结果（最近一次运行）

| 检查项 | FY2023 | FY2024 | FY2025E |
|--------|--------|--------|---------|
| `revenue = cogs + gp` | ✓ | ✓ | ✓ |
| `operatingIncome = gp - opex` | ✓ | ✓ | ✓ |
| `fcf = cfo - capex` | ✓ | ✓ | ✓ |
| `assets = liabilities + equity` | ✓ | ✓ | ✓ |
| 行业 segments 合计 = revenue | ✓ | ✓ | ✓ |
| 工艺 segments 合计 = revenue | ✓ | ✓ | ✓ |
| 客户 × 行业 cross (2024) | — | ✓ | — |
| 季度合计 = 年度 | ✓ | ✓ | ✓ |

## 这份案例与案例 01 的对照价值

| 维度 | 跨境电商案例 01 | 制造业案例 02 |
|------|--------------|--------------|
| 增长来源 | 渠道扩张 + 复购 | 客户结构 + 产能扩张 |
| 毛利率驱动 | 物流 + 议价 | 工艺 + 良率 + 原料锁价 |
| 现金特征 | CFO 强、FCF 正 | CFO 正、FCF 负（capex 期）|
| 客户集中度 | TOP1 占比下降 | TOP1 集中度动态切换 |
| 派生指标 | LTV : CAC, Ads/Sales | ROE, ROIC, CCC, OEE |
| 适合演示的图表类型 | 收入 + 渠道 mix + 堆叠 | 行业 mix + 客户 heatmap + 季度 small multiple |

两个案例一起用，可以完整覆盖 Skill 文档里 `chart-patterns.md` 中的 5–8 种主要图表类型，并演示制造业特有的"成本结构拆分 + 营运资本压力"那一类分析。

---

**案例免责声明**：本案例数据为 wtt-fin-chart Skill 调试而生成的模拟数据，客户名已脱敏；不得作为投资依据。详见 `raw-data/README.md`。
