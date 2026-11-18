# OpenCLI 登录态草稿 Adapter

> 公众号官方 API 缺配置时，或用户明确要求微博长文，或知乎专栏、掘金、百家号、博客园创建草稿时加载。默认微博短帖不加载。

## 运行模型

这些 adapter 不需要 CSDN 同步助手，也不使用 `$pluginSyncer`。它们使用 OpenCLI 自身的 Chrome 桥接取得用户已有登录 Cookie，再在 adapter 内处理 CSRF/token 和草稿响应。

```text
platform_payload file
  -> OpenCLI adapter (--execute)
  -> browser cookie jar
  -> platform draft endpoint
  -> draft_id + draft_url
  -> target-platform readback
```

## 安装与预检

```bash
python3 scripts/install-opencli-adapters.py --check
python3 scripts/install-opencli-adapters.py --install
opencli doctor
python3 scripts/provider-preflight.py --platforms weibo,zhihu,juejin,baijiahao,cnblogs
```

`--install` 会写入 `~/.opencli/clis/`，必须先经用户授权。安装后 `opencli list -f json` 应包含：

```text
weixin/article-draft
weibo/article-draft
zhihu/article-draft
juejin/article-draft
baijiahao/article-draft
cnblogs/article-draft
weixin/draft-account
juejin/draft-account
baijiahao/draft-account
cnblogs/draft-account
```

预检会并行执行只读账号探针：微博、知乎复用 OpenCLI 内置 `whoami`，公众号、掘金、百家号、博客园使用随附的 `draft-account`。账号探针失败时不调用草稿接口，直接选择 UI 登录/发布路径。`--skip-account-check` 只允许离线规划，真实写入前禁止使用。

## 输入契约

- 正文必须是平台独立文件，不是 `payloads.md` 或执行日志。
- 公众号、知乎、微博长文、百家号使用 HTML；掘金、博客园使用 Markdown。微博的 `article-draft` 只服务显式 `longform`，默认短帖使用 `weibo/publish`。
- 标题与正文分离，正文剔除重复 H1。
- 当前版 adapter 不上传本地图片。检测到 `/Users/...`、`file://`、`/private/...` 或相对图片路径时，写入前直接失败。
- 本次必须自动处理图片时，用 `provider-preflight.py --require-images <platforms>` 跳过 adapter，改走可校验图片的 API/UI。

## 公众号 Cookie adapter（官方 API 替代路径）

`weixin/article-draft` 在公众号官方 API（`scripts/weixin_api_draft.py`，需要 appid/appsecret/IP 白名单）缺配置、但浏览器已登录 `mp.weixin.qq.com` 时启用。它解析后台首页 HTML 的 `token`，POST `/cgi-bin/operate_appmsg?t=ajax-response&sub=create&type=77&token=<token>` 一次性写入标题+正文 HTML 创建图文草稿，不依赖 appid/secret。

- 正文必须是已适配的公众号 HTML（`article.wechat.html`，由 `scripts/prepare-weixin-rich-html.py` 生成）。
- v1 不上传图片：`images:false`。需要正文图/封面时跳过本 adapter，走官方 API 路径或浏览器富文本粘贴。
- 公众号会拒绝含未授权外链的草稿（错误码 `412/62752/64507`）；正文 HTML 必须先剥站外链接（保留链接文字）。
- 其他登录态 adapter 契约（`--execute` 强制、返回 `created_unverified`、必须回读、`WRITE_UNKNOWN` 不重建）同样适用。

## 命令

```bash
opencli weixin article-draft --title '<title>' --file /abs/article.wechat.html --summary '<summary>' --execute -f json
opencli weibo article-draft --title '<title>' --file /abs/article.weibo.html --summary '<summary>' --execute -f json
opencli zhihu article-draft --title '<title>' --file /abs/article.zhihu.html --execute -f json
opencli juejin article-draft --title '<title>' --file /abs/article.juejin.md --category-id 0 --execute -f json
opencli baijiahao article-draft --title '<title>' --file /abs/article.baijiahao.html --execute -f json
opencli cnblogs article-draft --title '<title>' --file /abs/article.cnblogs.md --tags 'AI,skill' --execute -f json
```

执行微博长文命令前必须先用 `provider-preflight.py --weibo-variant longform`。没有显式长文意图时，不得因为该 adapter 已注册就创建长文草稿。

不带 `--execute` 时 adapter 必须在发起写请求前失败。

## 结果与对账

adapter 返回：

```yaml
status: success
write_state: created_unverified
provider: opencli_login_adapter
platform: juejin
account: 当前账号
draft_id: '123'
draft_url: https://juejin.cn/editor/drafts/123
detail: Draft created; target-platform readback still required
```

这个结果只能先记为 `created_unverified`。必须做目标平台回读：打开草稿编辑页，核对账号、标题、正文首尾、中段关键句和图片数，才能升级为 `created_verified`。

adapter 在“草稿创建成功，后续保存失败”时会报 `WRITE_UNKNOWN` 并带出草稿 ID。此时先对账，不得调用 UI 再建一份。

## 稳定性

```yaml
provider: opencli_login_adapter
stability: experimental
last_static_verified_at: 2026-07-21
supports: [draft, html, markdown]
does_not_support: [local_image_upload, public_publish]
verification_method: target_platform_draft_readback
```

端点漂移时使用 OpenCLI adapter-author/explorer 流程重新抓取并更新 adapter，不在真实发布任务里拼接临时 `fetch`。
