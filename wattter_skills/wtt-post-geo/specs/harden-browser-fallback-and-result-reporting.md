# 浏览器回退与结果回报加固

## 目标

- 吸收 `csdn-sync-extension_1.0.5` 的任务 ID、逐平台结果、进度状态、草稿链接和中断恢复思路。
- 解决真实测试中编辑器假失败、重复写入、旧封面误用、发布结果不可回读和未知状态重复提交问题。
- 每次任务结束强制输出「平台 / 完成情况 / 链接」三列表格。

## 范围

- 新增通用浏览器编辑器 payload 写入器，支持 CodeMirror 5、iframe HTML、textarea 和 contenteditable。
- 新增发布结果账本，记录平台状态、provider、write state、链接、证据和错误，并生成最终 Markdown 表格。
- 更新微博、知乎、CSDN、掘金、百家号、博客园、小红书的回退与回读规则。
- 更新入口 Skill、README 和文档回归测试。

不复制参考扩展的固定密钥、私有 Header 修改、遥测或内部接口请求；参考扩展只作为协议、状态机和平台 payload 的静态证据。

## 验收标准

- 浏览器写入器生成的脚本只写编辑器，不点击保存或发布；返回源内容与编辑器内容的长度、指纹和匹配状态。
- 掘金写入先读取 CodeMirror 内部值；`fill` 返回未验证时不得直接追加 `type`。保存后重载同一草稿并再次比对指纹。
- 百家号可向 UEditor iframe 写入清洗 HTML，使用语义化「存草稿」按钮，并从 `article_id` URL 回读草稿。
- CSDN 多段 Markdown 增加一次受控 contenteditable 注入探测；预览或指纹不匹配时才回到人工导入。
- 微博长文不得沿用旧封面；封面上传失败时保存草稿并报告待补封面。
- 小红书发布状态未知时只对账一次；创作中心无新作品但存在不可回读正文的草稿时，报告「已填写待确认」，不得重试。
- 博客园检测到「账号未开通博客」时直接报告阻塞，不继续创建草稿。
- 结果账本拒绝把未验证结果标为「已发布」，拒绝无证据覆盖已经验证的草稿/帖子。
- 最终输出始终包含且只要求三列：`平台`、`完成情况`、`链接`；无链接写 `—`。
- 所有单元测试和 Skill 基础校验通过。

## 影响面

- `SKILL.md`、`README.md`
- `references/content-format.md`
- `references/execution-routing.md`
- 新增 `references/browser-editor-fallback.md`、`references/result-reporting.md`
- 各平台 reference
- `scripts/prepare-csdn-markdown.py`
- 新增浏览器写入和结果账本脚本及测试
