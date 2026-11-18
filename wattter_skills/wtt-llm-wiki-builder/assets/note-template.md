# {note_name}

```yaml
---
note_name: {note_name}             # 唯一短名（与文件名一致更稳）
type: note                        # 固定值
note_type: {反思/摘录/会议/观察/问题清单/日记/引用/思考/事件/临时}
topic: {topic}                    # 主题或项目名（必填）
date: {YYYY-MM-DD}                # 笔记发生日期（必填）
source_marking: [{已提取}/{AI补全}]  # 必填
tags: [{tag1}, {tag2}]            # 可选（细粒度标签）
related:                          # 可选（关联卡片，宽松即可）
  - "[[{related_note_or_card}]]"
source_files:                     # 可选（来自哪份原始资料）
  - {raw/path/file.md}
last_compiled: {YYYY-MM-DD}        # 可选（增量编译用）
confidence: {high/medium/low}      # 可选（仅 [AI补全] 时填）
---
```

---

> **一句话**：（用一句话说清这条笔记的核心）

## 背景

（什么时候、为什么想到这个 —— 没有就留空）

## 关键内容

（核心想法，分段或列表均可）

## 待跟进

（还没想清楚的问题，可链接到对应的"问题清单"笔记）

- [ ]
- [ ]

## 关联

- [[{关联卡片 1}]] — （关系说明）
- [[{关联卡片 2}]] — （关系说明）
