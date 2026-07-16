# 微博默认短帖发布

## 目标

- 将微博默认发布形态从长文草稿改为公开短帖。
- 同步调整微博内容生成，使长文章自动生成适合微博阅读的短帖摘要。
- 保留微博长文能力，但只在用户明确要求长文时启用。

## 范围

- 更新 `SKILL.md`、`README.md` 与微博相关 reference。
- 更新 `provider-preflight.py`，让微博默认选择 `weibo/publish`。
- 保留 `weibo/article-draft`，通过显式 `longform` 变体调用。
- 更新 manifest 与单元测试，防止默认路由重新漂移到长文编辑器。

## 内容生成规则

- `platform_payloads.weibo.variant` 默认设为 `short_post`。
- 从原文生成独立 `publish-output/<run-id>/weibo/body.txt`，不使用 `/tmp`，不直接截断源 Markdown。
- 默认结构为“一句钩子 + 2 到 4 个紧凑信息点 + 一个主要链接或收束句”。
- 使用纯文本，移除 Markdown 标题、加粗、分隔线、HTML 注释和代码围栏。
- 以 250–300 个可见字符作为保守内容预算；优先保留核心判断、关键证据和一个 GEO 主链接。
- 默认摘要转换视为微博平台适配，不再单独要求用户确认；必须保留原文并在 `adaptation_notes` 和最终结果中标记“微博摘要短帖”。
- 用户明确要求“微博长文、头条文章、全文发布、longform”时，才把 `variant` 设为 `longform`。

## 执行路由

- `short_post`：`opencli_adapter (weibo/publish) -> opencli_ui -> manual_confirm`。
- `longform`：`opencli_login_adapter (weibo/article-draft) -> opencli_ui_longform -> manual_confirm`。
- 长文失败不得自动降级成短帖；短帖失败也不得改建长文草稿。
- 图片上传失败时，短帖默认继续使用纯文本版本，不因封面阻塞发布；只有用户明确要求必须带图时才停在待确认。

## 验收标准

- 不传微博变体时，预检选择 `opencli_adapter` 和 `weibo/publish`。
- 传入 `--weibo-variant longform` 时，预检选择 `opencli_login_adapter` 和 `weibo/article-draft`。
- 长文 adapter 缺失时，显式长文任务进入长文 UI，不回退短帖。
- 文档明确记录短帖生成结构、独立正文文件、摘要标记与验证方法。
- 全量单元测试和 Skill 快速校验通过。

## 影响面

- 不删除现有微博长文 adapter，不改变知乎、CSDN、掘金、百家号、博客园等平台路由。
- 已显式设置 `variant: longform` 的调用保持原行为。
