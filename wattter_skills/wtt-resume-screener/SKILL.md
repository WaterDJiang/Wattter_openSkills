---
name: wtt-resume-screener
description: 简历筛选与评估助手。输入 JD 与候选人简历文件（PDF/DOCX/Markdown），自动识别岗位级别（实习/校招/初级/中级/高级/专家/管理），从 HR 经理 + 业务负责人双视角进行评估，输出包含匹配度评分、维度拆解、双视角点评、推荐结论和面试重点的 Markdown 报告。当用户需要以下操作时使用：(1) 批量筛选一批简历，(2) 对单个候选人与 JD 做匹配度评估，(3) 招聘需求分析、生成评估维度，(4) 准备面试提问清单或招聘总结，(5) HR 复盘简历质量或为 ATS 准备候选人卡片。适合 HR、招聘经理、技术 Leader 使用。
---

# 简历筛选 (Resume Screener)

把一批简历扔进来，AI 扮演资深 HR 经理 + 业务负责人双重角色，按岗位级别动态调整评估标准，输出可直接拿去开会的筛选报告。

## 工作流程

```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│ 1. 输入 JD │ →  │ 2. 解析 JD │ →  │ 3. 解析简历 │ → │ 4. 结构化  │ → │ 5. AI 评估 │
│  (或提问)  │    │  + 推断级别 │    │ (PDF/DOCX)  │    │   输出     │    │ + 渲染报告 │
└────────────┘    └────────────┘    └────────────┘    └────────────┘    └────────────┘
```

## 步骤 1：获取 JD

按以下顺序处理：

1. **用户提供 JD 文本** → 直接进入步骤 2
2. **用户没提供** → 用 [JD 提问清单](references/jd_interview_questions.md) 引导：
   - 岗位名称 & 团队
   - 实习 / 校招 / 社招？什么级别？
   - 核心职责 3-5 条
   - 必备技能 vs 加分项
   - 学历/经验硬性要求
   - 业务背景、关键挑战
   - 团队规模、汇报关系
   - 薪资预算范围

每次只问 2-3 个问题，避免一次性轰炸。

## 步骤 2：解析 JD & 确定岗位级别

```bash
# 解析 JD 文本
python3 scripts/parse_jd.py --input ./jd.txt

# 或直接传文本
python3 scripts/parse_jd.py --text "$(cat ./jd.txt)"
```

输出包含：
- `level`：intern / fresh_grad / junior / mid / senior / staff / manager / director
- `education`、`years`、`salary`
- `skills`：从 JD 抽取的关键技能
- `responsibilities`：从 JD 抽取的职责短句

> 如需强制覆盖检测结果，使用 `screener.py --level senior`

## 步骤 3：解析简历

```bash
# 解析单个/多个简历
python3 scripts/parse_resume.py ./resumes/a.pdf ./resumes/b.docx
```

支持 PDF / DOCX / Markdown / TXT。输出每位候选人的：
- 基础信息（姓名、邮箱、电话）
- 教育背景
- 工作/项目经历
- 技能清单

## 步骤 4：生成结构化筛选上下文

```bash
python3 scripts/screener.py \
  --jd ./jd.txt \
  --resume ./resumes/*.pdf \
  --output ./context.json
```

这一步会：
1. 加载 `config/evaluation_standards.yaml` 中**当前岗位级别**对应的 `weights` / `hard_requirements` / `soft_focus`
2. 为每位候选人估算 0-100 的维度分 + 综合分
3. 计算技能命中 & 短板
4. 按综合分降序排列

## 步骤 5：AI 双视角评估 + 渲染报告

读取 `context.json` 与 [双视角评估模板](assets/prompts/dual_role_review.md)：

1. **扮演 HR 经理**：关注动机、稳定性、文化匹配、薪资、风险信号
2. **扮演业务负责人**：关注技术深度、项目复杂度、解决复杂问题的能力、团队 influence
3. **微调维度分**（如硬性条件缺失、过人之处、明显风险）
4. 把评估内容填充到骨架报告的 `<!-- AI_REVIEW_HERE -->` 位置

生成最终报告：

```bash
python3 scripts/render_report.py ./context.json --output ./screening_report.md
```

AI 在末尾追加 `## 📌 综合招聘建议`（Top 3 / 重点面试 / 渠道建议）。

## 评估标准（按岗位级别差异化）

不同级别关注点截然不同，详见 `config/evaluation_standards.yaml`。要点：

| 级别 | 关注重点 | 弱化项 |
| --- | --- | --- |
| **intern** | 潜力、学习曲线、基础功、课程项目 | 多年经验、大厂背景 |
| **fresh_grad** | 学校 + 基础 + 实习三件套 | 行业年限 |
| **junior** | 独立上手、完整项目周期 | 架构/管理 |
| **mid** | 业务骨干、跨团队协作 | 顶级学校 |
| **senior** | 技术决策、mentorship、复杂问题 | 频繁跳槽（要追因） |
| **staff** | 行业可见成果、技术战略、方向 | 教育背景 |
| **manager** | 业务 sense、团队建设、跨部门沟通 | 写代码细节 |
| **director** | 行业视野、组织设计、谈判 | 单一技术维度 |

权重总和 = 100。综合分按 `Σ(weight_i × score_i) / Σ(weight_i)` 计算。

## 推荐结论阈值

默认阈值（可在 `evaluation_standards.yaml` 调整）：
- 🟢🟢🟢 强烈推荐 ≥ 85
- 🟢🟢 推荐 ≥ 70
- 🟡 待定 ≥ 55
- 🔴 不推荐 < 55

## 输出报告结构

完整 Markdown 报告包含：

1. **报告抬头** — 时间、岗位级别、简历总数
2. **JD 摘要** — 解析后的关键信息
3. **评估标准** — 当前级别的维度权重表 + 硬性条件 + 可放宽项
4. **候选人总览表** — 排名、姓名、综合分、推荐结论、学历、经验数、技能命中
5. **候选人详情**（每位）
   - 联系方式、综合分、推荐结论
   - 各维度得分表
   - 技能命中 / 短板
   - 教育背景
   - 🧑‍💼 HR 视角点评（亮点 / 风险 / 动机匹配 / 沟通表达）
   - 👔 业务负责人视角点评（技能匹配 / 项目深度 / 解决问题 / influence）
   - 📊 调整后评分 + 关键优势/风险 + 面试重点
6. **📌 综合招聘建议** — Top 3、面试重点、渠道补充建议

## 关键设计原则

- **配置驱动**：`evaluation_standards.yaml` 改一行就能调权重，无需动代码
- **岗位级别自适应**：用同一份代码评估实习生和总监
- **双视角独立**：HR 看人，业务看事，避免一方噪声污染另一方判断
- **不替代面试**：报告只做初筛，最终决策必须由用人经理 + HRBP 共同完成

## 依赖

```bash
pip install -r requirements.txt
```

Python 3.8+，无外部 LLM 依赖（AI 评估由 Claude/Trae 自身完成）。

## 常见问题

**Q: 简历格式乱 / OCR 质量差？**
A: 优先让用户提供 Markdown 或纯文本版本；PDF 扫描件会被 pypdf 跳过。

**Q: JD 写得很模糊，没有级别关键词？**
A: 默认按 `mid` 处理，并显式询问用户确认。

**Q: 候选人简历里没有学校/公司名怎么办？**
A: `parse_resume.py` 会尝试从上下文推断；推断失败时评估分会更保守（55 分起步）。

**Q: 能不能输出 JSON 给 ATS？**
A: 报告中已含候选人卡片（`emit_candidate_cards: true`），可直接结构化提取。

## References

- **[references/jd_interview_questions.md](references/jd_interview_questions.md)** — 引导用户描述 JD 的提问清单（步骤 1 必读）
- **[assets/prompts/dual_role_review.md](assets/prompts/dual_role_review.md)** — AI 双视角评估的完整 Prompt 模板（步骤 5 必读）
- **[config/evaluation_standards.yaml](config/evaluation_standards.yaml)** — 8 种岗位级别的评估权重与硬性条件
- **[config/screener_config.yaml](config/screener_config.yaml)** — 全局行为开关
