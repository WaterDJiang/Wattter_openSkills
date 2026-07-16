# API 优先、OpenCLI 回退发布路由规格

## 目标

- 升级 `wtt-post-geo` 为分层发布路由：优先使用成本更低、格式保真更好的 API/登录态适配器，明确失败后回退 OpenCLI adapter 或浏览器 UI。
- 可选复用 CSDN 同步助手暴露的 `$pluginSyncer`，覆盖微信公众号、微博长文、知乎专栏、掘金、百家号和博客园草稿。
- 防止主路径状态不明时继续回退，造成重复草稿或重复公开发布。

## 范围

- 新增 `references/execution-routing.md`，定义 provider 顺序、写入状态、回退门槛、熔断、校验与回报协议。
- 新增 `references/csdn-sync-extension.md`，定义 `$pluginSyncer` 探测、请求、结果对账和安全边界。
- 新增 `references/juejin.md`、`references/baijiahao.md`、`references/cnblogs.md`。
- 更新 `SKILL.md`、`README.md`、`references/content-format.md`。
- 更新公众号、微博、知乎 reference，使其显式采用分层路由；不改变已经验证的现有命令和浏览器路径。
- 不复制 `csdn-sync-extension_1.0.5` 的打包代码，不硬编码其中的密钥、内部接口或遥测逻辑。
- 不自动安装浏览器扩展、OpenCLI adapter 或全局依赖；缺失时先确认。
- 本次不执行真实平台写入。

## 路由决策

默认顺序：

1. 平台官方 API（已有配置且当前可验证）。
2. 已安装 OpenCLI 的 `COOKIE` / `HEADER` / `INTERCEPT` 写 adapter。
3. 已安装并可探测的 CSDN 同步助手 `$pluginSyncer` 草稿路径。
4. OpenCLI `UI` adapter 或 `opencli browser` 原生编辑器路径。
5. `fill_and_confirm` / `manual_asset_ready`。

平台 reference 可以调整前 3 项顺序，但必须记录原因和验证证据。

## 回退门槛

- 只有上一 provider 的 `write_state` 为 `not_started` 或 `confirmed_not_created`，才允许进入下一 provider。
- 超时、连接断开、响应解析失败、只拿到“已受理”但未拿到平台结果时，统一标记 `unknown`，先查草稿/帖子，不得自动回退。
- 已创建草稿但内容校验失败时，不创建第二份草稿；保留原草稿并进入修复或 `已填写待确认`。
- 公开发布路径只有在平台明确返回失败且回读确认没有新内容时，才允许换 provider 重试。
- 同一 provider 在同一任务连续出现 2 次确定性失败后，本轮熔断，不再重复调用。

## 验收标准

- 通用 payload 包含 `execution`、`attempts`、`write_state`、`verification` 和 `fallback_reason`。
- `SKILL.md` 明确真实写入前加载 `execution-routing.md`。
- `$pluginSyncer.syncArticle()` 的立即返回只能视为 `accepted`，不能视为草稿成功。
- 新增三个平台 reference 均包含内容格式、provider 路由、图片处理、草稿校验和 OpenCLI 回退。
- 微博长文不得静默降级成短微博；任何摘要或改写仍需用户确认。
- 所有平台最终状态继续使用 `已发布`、`已创建草稿`、`已填写待确认`、`未完成`、`已跳过`。
- 静态测试能检查路由 reference、平台表、关键写入状态和新平台文件是否一致。

## 影响面

- 这是 skill 协议与平台 reference 升级，不修改用户已有平台账号、浏览器配置或 OpenCLI 私有 adapter。
- API/登录态路径减少浏览器交互成本；OpenCLI UI 仍作为兼容回退。
- 新增掘金、百家号和博客园草稿能力说明；未完成真实账号验证前，相关 API provider 保持 `experimental`。
