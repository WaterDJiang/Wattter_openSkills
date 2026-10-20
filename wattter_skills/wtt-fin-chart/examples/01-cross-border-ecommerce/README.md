# 案例 01 · Horizon Outdoor Co.（跨境电商 DTC）

## 公司画像

- **公司**：Horizon Outdoor Co.
- **业务**：DTC 户外家居品牌，主营地垫/防水储物/户外照明，亚马逊美国站 + 品牌独立站
- **币种 / 单位**：USD / 千美元（'000）
- **财年**：与日历年同步（Jan–Dec）
- **数据状态**：FY2024/FY2025 经管理报表确认；FY2026 为 Jan–Sep 实际 + Oct–Dec 旺季预测 + Q4 季节性加权

## 这份案例想让 Skill 表达的财务故事

> Horizon 已从单平台增长过渡到多渠道结构化增长，毛利与现金同步改善。

核心 Signal：
1. 营收三年 CAGR 30.2%（$28.1M → $51.5M）
2. 毛利率从 55.6% 抬升至 57.2%（+1.5 pts，海运成本 + 越南议价是真实驱动）
3. FCF Margin 从 7.7% 升至 9.2%，CFO 转化率稳定在 60–70%
4. LTV : CAC 从 4.2x 升至 5.1x，复购率 24.1% → 27.8%

**下一阶段要回答**：TikTok Shop + Walmart 这两条新渠道能否维持利润率？而不是总盘子的扩张速度。

## 文件清单（标准办公格式）

```
01-cross-border-ecommerce/
├── README.md                    # 本文件
├── raw-data/                    # 4 份互相勾稽的模拟材料（Excel + PDF）
│   ├── README.md                          # 素材清单与 Skill 入口映射
│   ├── 01-P&L月度明细-FY2024-FY2026.xlsx       # 月度利润表 + 主要费用 + 年度关键比率
│   ├── 02-渠道与SKU-交叉维度-FY2025.xlsx       # 渠道/SKU/履约节点 + Channel×SKU 交叉矩阵 + CRM
│   ├── 03-资产负债表与现金流量-FY2024-FY2026.xlsx  # BS + CF + 财务比率 + DTC 运营 KPI
│   └── 04-FY2025年度董事会报告.pdf              # 8 页董事会报告（执行摘要 + 风险 + Action）
└── working-data/
    └── analysis.json                    # 已按 Skill 数据契约清洗好的结构化数据
```

## 如何让 Skill 跑这份案例

### 调用 1：直接给清洗好的 analysis.json（最快）

```text
请基于 working-data/analysis.json 给 Horizon Outdoor Co. 生成一份董事会财务报告。
受众：Founder、CFO、Lead Investors
目标：投研长页（不是单页 dashboard）
强调：① 多渠道结构化扩张；② 毛利率结构性提升的真实驱动（物流成本 + 议价）；
      ③ 自由现金流转化；④ TikTok Shop 与 Walmart 新渠道的可持续性。
输出：index.html + analysis.json + screenshot-full.png。
```

### 调用 2：把 3 份 xlsx + 1 份 PDF 当作原始材料交给 Skill

这是**最接近真实业务场景**的用法——用户常常就是把邮件附件 / 微信文件里的几份 Excel/PDF 直接丢给 AI：

```text
请阅读 raw-data/ 下的 4 份材料（3 份 xlsx + 1 份 PDF）：
- 01: 月度利润表
- 02: 渠道与 SKU 交叉维度
- 03: 资产负债表 + 现金流
- 04: FY2025 董事会报告（PDF）

按 Skill 的 Step 2 数据审计 → Step 3 写洞察 → Step 4 生成 HTML 完整流程跑一遍。
受众：董事会 / lead investors
目标：长页报告 + dashboard panel + PNG 全页截图备份
强调信号：营收 +41% / 毛利率 +1.5 pts / FCF margin +1pt / TikTok Shop +410%
```

### 调用 3：开发者本地复刻

```bash
# 复制 scaffold 与 assets
SKILL=~/.claude/skills/wtt-fin-chart
OUT=~/Desktop/horizon-fy25
mkdir -p "$OUT"/{css,js,data,images}
cp "$SKILL/assets/scaffold.html" "$OUT/index.html"
cp "$SKILL/assets/fin-chart.css" "$OUT/css/fin-chart.css"
cp "$SKILL/assets/fin-chart.js"  "$OUT/js/fin-chart.js"

# 用本目录的 analysis.json 数据替换 scaffold.html 中的 FIN_DATA 块
cp working-data/analysis.json "$OUT/data/analysis.json"

# 在浏览器打开
open "$OUT/index.html"
```

## 这份案例在 Skill 中的关键使用

| Skill 能力 | 体现位置（raw-data 文件 → 对应图表） |
|------------|---------------------------------------|
| 收入 × 利润率组合图 | 01 P&L → `metrics.revenue` + `metrics.grossMargin` |
| 渠道占比结构切换 | 02 SKU sheet → `segments` (100% stacked bar) |
| Channel × SKU 交叉 heatmap | 02 SKU sheet → `channelSkuCross2025` |
| 月度趋势 small multiple | 01 月度营收 → `monthlyRevenue` (24 个数据点) |
| 现金流量表 bars | 03 CF 部分 |
| 资产负债表结构 | 03 BS 部分 |
| Margin ladder | 从 03 比率部分派生 |

## 数据完整性自检结果（最近一次运行）

| 检查项 | FY2024 | FY2025 | FY2026E |
|--------|--------|--------|---------|
| `revenue = cogs + gp` | ✓ | ✓ | ✓ |
| `operatingIncome = gp - opex` | ✓ | ✓ | ✓ |
| `fcf = cfo - capex` | ✓ | ✓ | ✓ |
| `assets = liabilities + equity` | ✓ | ✓ | ✓ |
| 渠道合计 = revenue | ✓ | ✓ | ✓ |
| SKU 合计 = revenue | ✓ | ✓ | ✓ |
| Channel × SKU 2025 = FY2025 revenue | — | ✓ | — |

---

**案例免责声明**：本案例数据为 wtt-fin-chart Skill 调试而生成的模拟数据，所有公司名、产品名、客户名为虚构；不得作为投资依据。详见 `raw-data/README.md`。
