# 发布结果账本与最终回报

> 任何真实写入、草稿创建或全平台任务都必须加载。

## 目标

为每个平台保留独立结果，并为每次 provider attempt 记录起止时间、耗时、写入状态、错误、证据和回退原因。不要把“任务 completed”误解为所有平台成功；部分失败必须是 `partial`。

## 初始化

真实写入前，在本次稳定输出目录创建账本：

```bash
python3 scripts/publish-result.py init \
  --file /abs/output/publish-results.json \
  --platforms weibo,zhihu,csdn,juejin
```

平台顺序就是最终表格顺序。只列用户请求的平台。

## 记录 Provider Attempt

写入前：

```bash
python3 scripts/publish-result.py attempt-start \
  --file /abs/output/publish-results.json \
  --platform juejin \
  --provider opencli_login_adapter \
  --attempt-id juejin-adapter-1
```

命令结束后立即记录：

```bash
python3 scripts/publish-result.py attempt-finish \
  --file /abs/output/publish-results.json \
  --platform juejin \
  --attempt-id juejin-adapter-1 \
  --status success \
  --write-state created_unverified \
  --evidence 'adapter 返回 draft_id=456'
```

主路径确认没有写入并回退时，加 `--fallback-reason <reason>`。超时或状态不明时用 `--status unknown --write-state unknown`，不记回退。

## 更新单个平台

公开文章已回读：

```bash
python3 scripts/publish-result.py update \
  --file /abs/output/publish-results.json \
  --platform zhihu \
  --status published \
  --write-state published_verified \
  --provider opencli_ui \
  --item-id 123 \
  --link https://zhuanlan.zhihu.com/p/123 \
  --evidence '公开页标题与正文首尾匹配'
```

草稿已回读：

```bash
python3 scripts/publish-result.py update \
  --file /abs/output/publish-results.json \
  --platform juejin \
  --status draft \
  --write-state created_verified \
  --provider opencli_ui \
  --item-id 456 \
  --link https://juejin.cn/editor/drafts/456
```

状态映射：

| CLI status | 用户看到的完成情况 | write_state |
|---|---|---|
| `published` | 已发布 | `published_verified` |
| `draft` | 已创建草稿 | `created_verified` |
| `filled` | 已填写待确认 | `created_unverified` / `published_unverified` / `unknown` |
| `failed` | 未完成 | `confirmed_not_created` / `unknown` |
| `skipped` | 已跳过 | `not_started` |

`published` 必须有公开链接；`draft` 必须有草稿 ID 或链接。账本拒绝把未经验证的结果标成成功，也拒绝无意覆盖已验证帖子或草稿。

## 最终输出

所有请求平台更新完成后执行：

最终门禁是 `summary --strict`：仍有 pending 平台时拒绝生成完成报告。

```bash
python3 scripts/publish-result.py summary \
  --file /abs/output/publish-results.json \
  --strict
```

把命令输出的表格原样放在最终回复中：

```markdown
| 平台 | 完成情况 | 链接 |
|---|---|---|
| 知乎 | 已发布 | [打开](https://example.com) |
| 小红书 | 已填写待确认：存在 6 图草稿，正文无法回读 | — |
```

硬性规则：

- 最终回复必须包含 `平台 / 完成情况 / 链接` 三列，不能只写散文总结。
- 没有链接写 `—`，不能编造 URL。
- `--strict` 报错时先补齐 pending 平台状态，不能省略失败平台。
- provider、错误、图片和人工动作可写进「完成情况」简述，详细证据保留在 JSON 账本。
