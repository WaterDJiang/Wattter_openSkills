# wtt-fin-chart 示例案例库

本目录提供两份完整的模拟财务材料案例，可用于直接调试、展示与回归测试 `wtt-fin-chart` Skill 输出。每份案例对应一个行业，每个行业都有不同的财务画像、维度分布和关键洞察。

## 案例清单

| 编号 | 行业 | 公司 | 币种 | 单位 | 期间 |
|------|------|------|------|------|------|
| [01](./01-cross-border-ecommerce/) | 跨境电商（DTC 户外家居） | Horizon Outdoor Co. | USD | 千 | FY2024–FY2026E |
| [02](./02-precision-manufacturing/) | 精密制造（金属结构件 B2B） | MingYuan Precision | CNY | 百万 | FY2023–FY2025E |

## 每个案例的标准结构

```
examples/{编号}/
├── README.md                  # 案例说明 + Skill 调用示例（必读）
├── raw-data/                  # 原始材料：3 份 .xlsx + 1 份 .pdf，模拟企业真实财务材料
│   ├── README.md              # 素材清单：每份文件用途 + 对应 Skill 入口
│   ├── 01-...xlsx             # 利润表 / 月度数据 / 成本结构
│   ├── 02-...xlsx             # 渠道或客户维度 + 交叉矩阵
│   ├── 03-...xlsx             # 三表 + 财务比率
│   └── 04-...pdf              # 对外披露文件（董事会报告 / IPO 报告）
└── working-data/
    └── analysis.json          # Skill 按 references/finance-metrics.md 数据契约清洗好的 JSON
```

**文件格式选择理由**：财务材料最常见的办公格式是 Excel（管理报表 + 经营分析数据）和 PDF（董事会报告 / IPO 招股书 / 年报）。这两份案例刻意采用这两种格式组合，更贴近用户的真实工作场景：用户常常就是把邮件附件 / 微信文件里的几份 Excel + PDF 直接丢给 AI，而不是 markdown 文本。

## 数据完整性承诺

每份 `analysis.json` 都经过自检脚本验证，确保：
- `revenue = cogs + grossProfit`（三个期间均满足）
- `operatingIncome = grossProfit - opex`（三个期间均满足）
- `fcf = cfo + capex`（FCF 勾稽）
- `totalAssets = totalLiabilities + shareholdersEquity`（资产负债表平衡）
- 所有 segments（渠道/行业/工艺）按期汇总 = revenue
- 交叉维度矩阵（如 channel × SKU）的合计与上层一致
- 季度 P&L 的年度合计与年度 NI 一致

`raw-data/*.xlsx` 中的数字与 `analysis.json` 中的数字完全勾稽：
- 关键指标（毛利率 / 净利率 / FCF / 客户集中度）在 Excel、PDF、JSON 三处口径一致
- 行业术语（OEE / Yield / CCC / LTV : CAC / FCC margin）与行业惯例一致
- 不指向任何真实存在的公司

## 如何用 Skill 跑通这两份案例

### 方式 A：把 working-data/analysis.json 作为输入（最快）

把 `analysis.json` 当作 Skill 的输入，由 Skill 走完整工作流（Step 2 数据审计 → Step 3 写洞察 → Step 4 复制 scaffold → Step 5 视觉生成 → Step 6 PNG 备份）：

```text
请基于 working-data/analysis.json 生成一份完整的财务图表报告，
受众是董事会，目标是把"增长质量、品类切换、营运资本压力"三件事讲清楚。
```

### 方式 B：把 raw-data 下 3 份 xlsx + 1 份 pdf 丢给 Skill（最真实）

```text
请阅读 raw-data/ 下的所有 Excel 和 PDF 财务材料，生成本案例的
- 受众：董事会 / 投资人
- 目标：投研长页（不是单页 dashboard）
- 输出：index.html + analysis.json + screenshot-full.png
```

### 方式 C：替换 scaffold 中的 FIN_DATA 示例数据（开发者）

如果你是开发者，可以直接把 `analysis.json` 翻译成 `FIN_DATA` 对象塞到 `assets/scaffold.html` 的 JS 块，然后 `python -m http.server` 即可在 1440×900 看效果。

详见每个案例目录下的 `README.md` 中的"如何让 Skill 跑这份案例"。

## 与 SKILL.md 工作流的对应关系

| SKILL.md 阶段 | 在本目录中的体现 |
|---------------|------------------|
| Step 1 分析口径 | 各案例 `README.md` 的 periodLabel / currency / unit / source 段 |
| Step 2 数据审计 | `working-data/analysis.json` 已通过内部对账检查 |
| Step 3 写洞察 | `analysis.json` 的 `insights / risks / actions / thesis` 字段 |
| Step 4 创建 HTML | 直接调用 assets/scaffold.html 即可消费 |
| Step 5 视觉设计 | 受 palette / font 配置控制 |
| Step 6 PNG 备份 | 通过 Playwright 截图自动生成 |

## 注意事项

1. **不能拿来做投资建议**。SKILL.md 的硬规则之一就是不做买入/卖出建议；案例里的"风险/机会"判断只是分析视角。
2. **数据是模拟的**，但内部的"驱动逻辑"是真实的——毛利率提升是否被运营杠杆验证、Capex 投入是否匹配订单储备、应收账款回款结构与客户类型是否一致——这种"商业合理性"是模拟时努力保留的。
3. **数字已四舍五入**到千美元 / 百万人民币；如做严谨对比，请以原始凭证为准。
4. **跨案例对比不直接可比**（币种、单位、行业不同）。Skill 内部不会做跨案例的归一化处理。
5. **xlsx 文件建议用 Excel / WPS / Google Sheets / Numbers 打开**，Skill 内部读取时不依赖 Excel 软件，会用 openpyxl 解析。
