# Build 模式 — 三种起点的完整决策树

Build 模式处理"从无到有"的场景。SKILL.md B1-B5 是骨架，本文档给三种起点的细节。

## 起点 A：完全空目录

**症状**：`ls -la` 只显示 `.` 和 `..`，或只有一个 README。

**决策树**：

1. 直接询问用户主语境（课程/案例库/模型库/综合）
2. 创建完整骨架：`raw/{articles,transcripts,assets}` + `wiki/{kps,cases,models,concepts,materials,indexes}`（即使本次只用部分子目录，全部建好以备将来）
3. 落 CLAUDE.md（按 `architecture-contract.md` 第 3.3 节抽对应草案）
4. 落空 log.md / index.md
5. 写第一条 log：`init: 空目录初始化`
6. 询问是否有现成资料要导入 raw/

**注意**：空目录不需要"迁移"步骤。直接进入"等待用户喂资料"状态。

---

## 起点 B：散落文件（无 raw/wiki 子目录）

**症状**：目录里有一堆 markdown / pdf / txt，但没有 raw/ 也没有 wiki/。

**决策树**：

### B-1. 散落文件分类

先 `find . -type f` 列出所有文件，按扩展名 + 文件名 + 内容前 200 字推断：

| 类别 | 特征 | 归到 |
|:---|:---|:---|
| 长文章 | .md/.txt 单文件 > 1000 字 | `raw/articles/` |
| 录音转写 | 文件名含"录音/transcript/会议/课程"，正文含时间戳 | `raw/transcripts/` |
| 图片/音频 | .png/.jpg/.mp3/.mp4 等 | `raw/assets/` |
| 已蒸馏的 wiki 卡片 | 有 frontmatter 且字段名是 kp_name/case_name 等 | `wiki/{对应语境}/` |
| 索引文件 | 文件名含 index/log/mapping，或正文是大量链接表 | `wiki/indexes/` |
| 不确定 | 其他 | 列出问用户 |

### B-2. 给用户一份「迁移计划」预览

格式：

```
📦 迁移计划：将散落文件归类到范式目录

现状：12 个 .md，3 个 .pdf，1 个 .txt

→ raw/articles/ (8 个)
   - 选题方法论-完整版.md
   - 4P 营销框架介绍.md
   - ...

→ raw/transcripts/ (2 个)
   - 2026-05-20 高效会议录音稿.txt
   - ...

→ raw/assets/ (3 个)
   - 课程封面.pdf
   - ...

→ wiki/kps/（疑似已蒸馏）(2 个)
   - MECE原则.md
   - 金字塔结构.md

→ ⚠️ 不确定 (1 个)
   - 草稿.md（请确认归到哪里）

是否按此迁移？所有迁移用 git mv（如果是 git 仓库）或 cp -p（保留时间戳）。
```

### B-3. 用户确认后执行

```bash
mkdir -p raw/{articles,transcripts,assets}
mkdir -p wiki/{kps,cases,models,concepts,materials,indexes}

# 用 git mv 优先（保留 git 历史）
git mv 选题方法论-完整版.md raw/articles/  # 若是 git
# 否则
mv 选题方法论-完整版.md raw/articles/      # 退化方案
```

如果疑似已蒸馏的卡片要进 wiki/，**不要直接放**——先校验 frontmatter（用 `scripts/scan_wiki.py --check L1` 跑一遍），合规才放。

### B-4. 落 schema + 索引

同起点 A 步骤 3-5。

### B-5. 衔接 Compile

询问："raw/ 已就绪，是否立刻编译首批资料？"

---

## 起点 C：已有 raw/ 或 wiki/ 但不完整

**症状**：之前有人搭过一半，比如有 `wiki/kps/` 但没有 `wiki/indexes/`，或有 `raw/` 但没 `CLAUDE.md`。

**决策树**：

### C-1. 体检报告（不动文件）

先报告现状，不直接补：

```
📋 当前状态：
✅ raw/articles/ (8 个文件)
✅ wiki/kps/ (15 个 kp 文件)
❌ wiki/indexes/ 不存在
❌ wiki/concepts/ 不存在
⚠️ CLAUDE.md 不存在
⚠️ wiki/kps/ 里的卡片有 5 个缺 frontmatter（L1 检查）
```

### C-2. 优先级排序的修复方案

按"先补无副作用的，再问需要决策的"顺序：

1. **直接做**（无副作用）：
   - 创建 `wiki/indexes/` 和空 log.md / index.md
   - 创建 `wiki/concepts/`、`wiki/materials/` 空目录
2. **问用户**（需要决策）：
   - CLAUDE.md 用什么 schema 草案？
   - 现有卡片缺 frontmatter，是手工补还是按某规则推断？
   - index.md 是 reverse engineering 现有 kps 一次重建，还是只填空？
3. **报告但不动**：
   - 现有卡片中疑似的同义概念（让用户决定是否归并）
   - 文件命名违规（让用户确认是否批量重命名）

### C-3. reverse engineering index

如果要从现有 kps 重建 index，调用：

```bash
python3 scripts/scan_wiki.py {target} --check L3
```

得到所有 kp 文件清单，按 frontmatter 的 `module` / `knowledge_domain` / `knowledge_type` 聚合，生成 index.md 各段。

### C-4. 完成后写 log

第一条 log 写 `migrate: 补全 wiki 范式`，列出本次补的内容。

---

## Build 模式的边界

### 不要做的事

- ❌ 不要在 Build 模式下做内容萃取——Build 只搭骨架和迁移，萃取交给 Compile
- ❌ 不要批量重命名用户的散落文件——保持原文件名（迁移时只移动位置）
- ❌ 不要在没有用户确认的情况下创建 CLAUDE.md——schema 影响所有未来 compile，必须用户审阅
- ❌ 不要假设主语境——多样性目录有可能是综合库，问清楚

### 衔接规则

Build 完成后的衔接：

| 用户回答 | 下一步 |
|:---|:---|
| "立刻编译" | 进入 Compile 模式第零步（注意：第零步会再跑一次轻量 lint，符合预期） |
| "暂时不要" | 结束。给用户一句话指引："以后跑 `compile` 把 raw/ 资料编译进 wiki/，跑 `lint` 检查健康度" |
| "我还要再补点 raw/" | 等用户补完，再衔接 Compile |
