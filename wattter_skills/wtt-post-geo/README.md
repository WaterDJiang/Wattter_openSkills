# wtt-post-geo

多平台 GEO 内容发布 skill。把一份 Markdown 按平台规则适配后，发布或创建草稿到微信公众号、微博、知乎专栏、CSDN、掘金、百家号、博客园、小红书、Twitter/X，并保留官网、来源引用、llms.txt、sitemap 等 GEO 信息的分平台露出策略。

名称不再绑定 OpenCLI：执行时采用“官方 API -> 浏览器登录态 adapter -> OpenCLI 内置 adapter/UI -> 人工确认”的分层路由。OpenCLI 是执行工具之一，不是 skill 的能力边界。

微博默认发布摘要短帖：先从原文生成独立 `weibo/body.txt`，再走 `weibo/publish`。只有用户明确要求微博长文、头条文章或全文发布时，才启用 `weibo/article-draft` 和长文编辑器。

该 skill 不安装、不探测、不调用 CSDN 同步助手。它只借鉴参考扩展“每平台独立 adapter + 登录态 + 草稿 ID/链接 + 任务账本”的结构，重写为可审查的 OpenCLI adapter。

## 执行路由

```text
平台官方 API
  -> OpenCLI 登录态 article-draft adapter（需要长文/草稿的平台）
  -> OpenCLI 内置 adapter
  -> OpenCLI UI/browser
  -> 已填写待确认
```

只有上一 provider 为 `not_started` 或已回读确认 `confirmed_not_created` 时才能回退。超时、桥接断开、响应解析失败、`WRITE_UNKNOWN` 或只有受理态时，先查目标平台草稿/帖子，不重复创建。

## 环境检查

```bash
node --version
npm --version
command -v opencli
opencli --version
opencli doctor
opencli list -f json
```

OpenCLI 自身的 Chrome 桥接是 COOKIE/HEADER/UI adapter 的运行前置。这不等于安装 CSDN 同步助手。

## 登录态 Adapter

本 skill 随附：

- `weibo/article-draft`（仅显式微博长文）
- `zhihu/article-draft`
- `juejin/article-draft`
- `baijiahao/article-draft`
- `cnblogs/article-draft`
- `juejin/draft-account`
- `baijiahao/draft-account`
- `cnblogs/draft-account`

先检查：

```bash
python3 scripts/install-opencli-adapters.py --check
```

需要安装时，在用户授权写入 `~/.opencli/clis/` 后执行：

```bash
python3 scripts/install-opencli-adapters.py --install
opencli list -f json
```

命令默认只创建草稿，并且必须显式加 `--execute`。不带 `--execute` 时不会发起写请求。

预检会并行运行只读账号探针；未登录或无法识别账号时直接转 UI，不先试写、也不等待写入超时。

当前 adapter 支持 HTML/Markdown 正文和平台主要草稿字段，不上传本地图片。任务必须自动处理图片时，预检会直接跳过 adapter 选 API/UI：

```bash
python3 scripts/provider-preflight.py \
  --platforms weibo,zhihu,juejin,baijiahao,cnblogs \
  --require-images weibo,zhihu
```

微博默认短帖与显式长文分别预检：

```bash
python3 scripts/provider-preflight.py --platforms weibo --weibo-variant short_post
python3 scripts/provider-preflight.py --platforms weibo --weibo-variant longform
```

前者应选择 `weibo/publish`；后者才选择 `weibo/article-draft`。短帖稿使用纯文本 `weibo/body.txt`，默认结构为一句钩子、2–4 个信息点和一个主链接或收束句。

## 媒体回退

缺图时默认生成文章专属 HTML PNG。渲染能力不可用、生成失败或尺寸不对时，使用 `assets/default-images/` 中的 4 张内置图：

- 900x383 公众号封面
- 1200x900 微博配图
- 1200x1200 通用方图
- 1080x1440 小红书竖图

```bash
python3 scripts/select-publish-image.py \
  --use-case weixin_cover \
  --preferred /abs/article-cover.png
```

只为本次实际目标平台生成素材。用户排除的平台不做图。

## 结果账本

第一次写入前：

```bash
python3 scripts/publish-result.py init \
  --file /abs/output/publish-results.json \
  --platforms weibo,zhihu,juejin
```

每次 provider 写入前后：

```bash
python3 scripts/publish-result.py attempt-start \
  --file /abs/output/publish-results.json \
  --platform juejin \
  --provider opencli_login_adapter \
  --attempt-id juejin-1

python3 scripts/publish-result.py attempt-finish \
  --file /abs/output/publish-results.json \
  --platform juejin \
  --attempt-id juejin-1 \
  --status success \
  --write-state created_unverified
```

任务完成后：

```bash
python3 scripts/publish-result.py summary \
  --file /abs/output/publish-results.json \
  --strict
```

最终回复必须由账本生成：

```markdown
| 平台 | 完成情况 | 链接 |
|---|---|---|
```

## 安全边界

- 验证码、异常登录、频控、风险提示或审核拦截出现时立即停止。
- 不绕过风控，不伪装“真人操作”，不复制参考扩展的固定密钥、签名、遥测或全域权限。
- 草稿 ID/链接只是 `created_unverified`；目标平台回读通过才是 `created_verified`。
- 不得因为某平台失败而重复创建同标题内容。

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 /Users/water/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```
