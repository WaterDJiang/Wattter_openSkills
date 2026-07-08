# 知乎发布流程

> 仅在用户明确点名「知乎」或要求「全平台」发布时加载此文件。

## 关键事实（实测）

- 知乎专栏文章主路径是浏览器自动化。知乎有 answer / comment 的 write 适配器，但通用专栏文章不一定有。
- 知乎专栏发布可能卡在 `/edit` 页面显示 `发布中...`；即便草稿内容已写入，也不算发布成功。
- 最多重试一次，反复点击会触发风控。
- OpenCLI `1.8+` 的 browser 命令需要显式 session 名，例如 `opencli browser zhihu state`。
- 执行前必须使用 `references/content-format.md` 生成的 `platform_payloads.zhihu`。标题进入标题字段，正文不要重复同一个 H1。

## 内容 payload 要求

```yaml
title: 知乎专栏标题
body: 完整正文
media:
  images: 正文图片绝对路径列表
  videos: 正文视频绝对路径列表
mode: publish|draft|fill_and_confirm
```

适配规则：

- 适合完整文章、解释型长文、观点论证。
- 保留完整结构和论证层次。
- 标题写入 title 字段，正文不要重复同一个 H1。
- 图片和视频都必须按当前知乎编辑器/适配器能力处理；不支持自动插入视频时，按 `已填写待确认` 或让用户人工补视频，不要把本地视频路径直接写进正文。
- 如果浏览器发布卡在 `/edit`，按校验规则回报为 `已填写待确认` 或 `已创建草稿`，不要算已发布。

## 主路径：专栏文章（浏览器自动化）

```bash
opencli zhihu whoami -f json
opencli browser zhihu open https://zhuanlan.zhihu.com/write --window foreground
opencli browser zhihu state
opencli browser zhihu find --css "textarea,[contenteditable=true],button" --limit 80 --text-max 120
opencli browser zhihu fill <title-ref> "<title>"
opencli browser zhihu fill <editor-ref> "<body>"
opencli browser zhihu click <publish-button-ref>
```

### 校验

```bash
opencli browser zhihu get url
opencli browser zhihu extract --chunk-size 4000
```

成功标准：

- 页面离开 `/edit`，或
- 显示已发布文章 URL，或
- 用户的文章列表里出现新文章。

如果页面仍停在 `/edit`、显示 `草稿` 或按钮一直是 `发布中...`，按 `草稿已填写/发布未确认` 上报，**不能算成功**。最多重试一次，不要反复点击。

## 副路径：回答 / 评论

对于问题回答或文章评论，使用对应适配器，并且只在用户明确要求真实写入时才加 `--execute`：

```bash
opencli zhihu answer "<target>" "<content>" --execute -f json
opencli zhihu comment "<target>" "<content>" --execute -f json
```
