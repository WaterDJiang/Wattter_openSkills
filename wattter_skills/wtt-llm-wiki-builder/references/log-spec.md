# log.md 规范

`wiki/indexes/log.md` 是「目标目录」的时间轴日志。每次 compile 必须追加一条记录。

## 设计原则

1. **追加不修改**：log 是 append-only，旧条目永远不改
2. **可被 LLM 一眼读懂**：不用 JSON，用 markdown 表格 + 短句
3. **有摘要也有指针**：每条 log 给规模摘要，详细产物列在该次产出文件本身的 frontmatter 里
4. **冲突显式记录**：合并模式下产生的冲突要在 log 中点名，不能只静默写进卡片
5. **统一前缀，grep 可解析**：每条记录以 `## [时间] 操作: 主体` 开头，unix 工具直接可用——`grep "^## \[" log.md | tail -5` 即最近 5 条。**操作**是动词（init/compile/query/lint-fix/maintain），主体是名词

## 文件结构

```markdown
# {目录名} — Compile Log

> 每次由编译器追加。append-only。
> 前缀格式：## [YYYY-MM-DD HH:MM] {操作}: {主体名}
> 操作 ∈ init / compile / query / lint-fix / maintain

## [YYYY-MM-DD HH:MM] compile: {本次主体名}

| 维度 | 内容 |
|:---|:---|
| **源** | `raw/articles/xxx.md` + `raw/transcripts/yyy.md` |
| **产出** | N 个 kp / M 个 module-summary / K 个 case |
| **路径** | `wiki/kps/{课程名}-knowledge-points/` |
| **新增** | {kp 列表，最多 10 个；超出写"等 N 个"} |
| **合并** | {同名追加的 kp 列表} |
| **冲突** | {冲突点；无则写"无"} |
| **时效** | {新旧碰撞判定结果：取代 N 对（旧→新）/ 互补并入 N 张 / 并存 N 对 / 候选待确认 N 对；无则写"无"} |
| **跨课程归并** | {抽到 concepts/ 的概念；无则写"无"} |
| **未完成** | {本次未处理的 raw 文件 / 未补全的字段} |
| **下一步建议** | {1-2 条} |

---

## [YYYY-MM-DD HH:MM] ...

```

> 旧格式 `## [时间] {语境}: {主体}`（语境=course/case 等）仍然可读，不必回改历史；新条目一律用操作前缀。

## 操作类型与精简条目

compile 用上面的全表；其他操作允许精简为一两行：

```markdown
## [2026-08-31 14:20] query: 对比 X 与 Y（已归档 → wiki/notes/对比XY.md）

## [2026-08-31 15:00] lint-fix: 修复 3 处死链 + 回填 12 张卡 knowledge_date

## [2026-09-02 09:10] maintain: 手工补 商业讲师成功四要素模型 的 superseded_by（用户确认）
```

- **query**：仅当回答归档回 wiki 时才记（临时问答不留痕）
- **lint-fix**：用户确认修复后才写；lint 报告本身落 `lint-{date}.md`，不进 log 主流
- **maintain**：手工修正、批量脚本执行（如回填）的记录

## 增量场景的写法

### 同一课程二次编译（增量补充）

```markdown
## [2026-06-15 10:20] compile: 选题方法论

| **源** | `raw/transcripts/20260615_补录.md` |
| **产出** | 3 个新 kp，5 个 kp 追加素材 |
| **路径** | `wiki/kps/选题方法论-knowledge-points/` |
| **新增** | 选题三维度--工具篇.md, ... |
| **合并** | MECE原则.md（追加 3 条素材，1 条边界）, ... |
| **冲突** | MECE原则.md：上次说"必须穷尽"，本次说"业务场景下不必"——已用 ⚠️ 块并存 |
| **时效** | 候选待确认 1 对：选题三维度（20260510） vs 选题三维度--工具篇（20260615），疑似互补 |
| **未完成** | raw/transcripts/20260615_补录.md 第 8 节"案例分析"未提取，下次处理 |
```

### 跨课程归并

```markdown
## [2026-06-20 16:00] compile: 高效会议

| **跨课程归并** | "MECE 原则" 已在选题方法论、咨询基础中各自存在；本次抽出到 wiki/concepts/MECE原则.md，三处 kp 改为引用 |
```

## 与 mapping.json 的关系

`mapping.json`（可选）是 raw → wiki 的精确映射，结构：

```json
{
  "raw/articles/xxx.md": [
    "wiki/kps/课程A-knowledge-points/01-选题/选题三维度.md",
    "wiki/kps/课程A-knowledge-points/01-选题/_module-summary.md"
  ]
}
```

log.md 是人读的摘要，mapping.json 是机器读的索引。**编译器优先维护 log.md**；mapping.json 只在目录 CLAUDE.md 明确要求时才维护。

## 何时不写 log

不存在"不写"的情况。即使本次只是修一个错别字、只 compile 了一张卡片，也要写一条 log——log 是全量历史，不是有意义事件流。
