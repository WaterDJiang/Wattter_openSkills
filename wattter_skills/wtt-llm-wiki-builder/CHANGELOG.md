# CHANGELOG — wtt-llm-wiki-builder

> 本文件只记版本演进，供回溯与迁移其他 wiki 时参考；SKILL.md 与 references 只保留当前规则。

## 2026-08-31 知识时效机制 + Karpathy llm-wiki 理念对齐

背景：03_Knowledge 实测验证了知识时效机制（97 张卡回填 knowledge_date、health_check 升 6 项、新旧碰撞判定），本次把该机制泛化进 skill；同时对照 Karpathy《LLM Wiki》范式查缺补漏。

### A. 知识时效（数据层 → 脚本层 → 规则层）

- **数据层**：知识卡片（kp/case/model/concept）必填 `knowledge_date`（知识发生时间，推断规则：source_files 文件名日期前缀最早 → raw mtime → 已有时间字段兜底）；近似回填标 `knowledge_date_basis: approximate`；被取代时标 `superseded_by`（用户确认后）。note 卡由 `date` 承担，不加重复字段。
- **脚本层**：
  - `scan_wiki.py`：轻量 7→8 项（+L17 时效字段）、深度 16→18 项（+L18 新旧体系健康：superseded 链死链/回链 + 同体系候选扫描）。候选扫描吸取 03 教训：先剔通用词再找公共子串、纯 ASCII 碎片不配对。
  - 新增 `backfill_knowledge_date.py`：存量回填，--dry-run → 抽查 diff → 执行（幂等），精确/近似/无法推断三类分开报告，未来日期拦截。
- **规则层**：
  - 编译流程新增第十一点五步「新旧碰撞判定」：互补合并 / 取代标链+演进史回链 / 并存边界对比 / 拿不准列候选问用户。铁律：不擅自标 superseded_by。
  - 检索输出加「知识时间」「状态」呈现契约：同体系归组、✅ 最新优先、⚠️ 已被 [[X]] 深化但保留展示。
  - lint-spec 新增 LLM 语义检查 S1-S5（矛盾对扫/过时结论/概念缺页/数据空洞/下一步提议）。
  - 新增 `references/knowledge-freshness.md`（机制总规范 + 迁移其他 wiki 的适配点 + 实战踩坑）。

### B. Karpathy《LLM Wiki》理念对齐

- **回答归档（Query→Archive）**：跨卡综合/对比/分析类回答，回答后提议归档回 wiki（note/model/concept 卡 + log `query:` 记录）——补上复利闭环；单卡转述不归档。
- **log 前缀标准化**：`## [时间] 操作: 主体`，操作 ∈ init/compile/query/lint-fix/maintain，`grep "^## \[" log.md | tail -5` 可直接解析；log 表新增「时效」字段。
- **Lint 语义项对齐**：S1-S5 覆盖 Karpathy 清单中的矛盾、过时结论、被反复提及却无页面的概念、数据空洞、"提议新问题/新资料"（深度 lint 收尾「下一步」节）。
- **波及面检查**：编译不只产新卡，既有相关卡片的关联/素材/appears_in 要回写。
- **Build 建议 git 化**；检索规模升级路径（qmd 等本地搜索引擎）写入 query-entries。
- **修复存量 bug**：architecture-contract.md 三份 CLAUDE.md 草案里编译器名仍是旧的 `wtt-course-knowledge-distillation` → 改为 wtt-llm-wiki-builder；草案补「知识时效」节。

### 实测验证（fixture 复刻 03 场景）

回填：日期前缀 exact / mtime approximate / 无法推断 / 未来日期拦截 / note 豁免 / 幂等重跑全过；L17 只剩需手工补的卡；L18 正确报出缺回链 + 1 对同体系候选；深度 lint 18 项跑通。
