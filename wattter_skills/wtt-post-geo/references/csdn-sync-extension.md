# CSDN 同步助手静态参考（不是 Provider）

> 只在维护本 skill、对照参考扩展架构或排查 adapter 漂移时加载。真实发布任务不加载、不安装、不调用该扩展。

## 结论

CSDN 同步助手的 `$pluginSyncer` 只是页面到扩展 service worker 的桥。真正创建草稿的能力是后台中 6 个平台 adapter：读取浏览器已有登录态、取得 CSRF/token、调用平台草稿接口、返回草稿 ID/编辑链接。

本 skill 已把这个结构重写为 OpenCLI 登录态 adapter：

- 微信公众号：官方 API 或 OpenCLI 内置 `weixin/create-draft`。
- 微博长文：`weibo/article-draft`。
- 知乎专栏：`zhihu/article-draft`。
- 掘金：`juejin/article-draft`。
- 百家号：`baijiahao/article-draft`。
- 博客园：`cnblogs/article-draft`。

运行时规则见 [login-state-adapters.md](login-state-adapters.md) 和 [execution-routing.md](execution-routing.md)。

## 可借鉴的任务协议

静态包中暴露了 `getPlatforms()`、`syncArticle()` 和 `openSyncPanel()`；可借鉴的是其内部任务协议，不是运行时 API：

- 每次任务有独立 `syncId`。
- 平台串行执行，单平台保存 `success/articleId/articleUrl/draftOnly/error/timestamp`。
- 同一源文章先生成各平台独立 `platformContents`。
- 中断任务不能简单重试；本 skill 使用更保守的 `unknown -> 目标平台对账`。
- 扩展“只要不是全部失败就 completed”的逻辑不采用；部分失败必须是 `partial`。

## 已放弃的扩展依赖

- 不检查 `window.$pluginSyncer.connected`。
- 不打开 CSDN 页面等待 MessageChannel。
- 不使用扩展 Manifest 的全域 host 权限或动态 Header 修改。
- 不复制固定密钥、签名、遥测、日志上报和 CSDN 账号标识。
- 不把参考扩展的 `success: true` 当成目标平台回读证据。

## 安全边界

参考扩展中的草稿端点属于平台网页后台接口，会漂移。只在有可追踪的 OpenCLI adapter、`--execute` 门禁、账号识别和写入后对账时使用。验证码、异常登录、频控或风险提示出现时立即停止。

