# 无 CSDN 插件的登录态适配器与图片回退

## 目标

- 复制 CSDN 同步助手的有用能力，不依赖、不安装、不运行 CSDN 同步助手。
- 使用 OpenCLI 浏览器桥接读取用户已有登录态，将知乎、微博长文、掘金、百家号、博客园的草稿写入封装为 OpenCLI adapter。
- 默认路由改为“官方 API -> OpenCLI 登录态 adapter -> OpenCLI UI/browser -> 人工确认”。
- 早失败、逐次记录耗时，避免在不存在的 provider 上等待超时。
- 配图按“文章专属生成图 -> 内置默认图 -> 平台原生默认封面/人工补图”回退。

## 范围

- 更新 `SKILL.md`、`README.md`、执行路由和各平台 reference。
- 新增可随 skill 分发的 OpenCLI 适配器源码，安装时复制到 `~/.opencli/clis/<site>/`。
- 适配器写入默认要求 `--execute`，返回 `status/draft_id/draft_url/provider/account`。
- 新增 provider 预检脚本，根据 `opencli list -f json` 和 `opencli doctor` 结果生成平台路由表。
- 扩展 `publish-results.json` 的 attempt 记录，包含开始、结束、耗时、写入状态、错误、证据和回退原因。
- 新增 900x383、1200x900、1200x1200、1080x1440 四张通用 PNG 回退图及选图脚本。
- 媒体规则仅处理本次目标平台，不为已排除平台生成素材。

## 非目标

- 不复制 CSDN 扩展的 Manifest、`$pluginSyncer` 桥、全域 host 权限、遥测或日志上报。
- 不复制、固化或传播扩展内部的密钥、签名、用户 Cookie 或 token。
- 不在本次升级中创建真实草稿或公开发布测试文章。
- 不绕过验证码、风控、异常登录或平台审核。
- OpenCLI 自身的 Chrome 桥接仍是 COOKIE/HEADER/UI adapter 的运行前置；“无插件”特指无 CSDN 同步助手依赖。

## 影响面

- skill 路由与发布状态机。
- OpenCLI 私有 adapter 注册表（仅在用户执行安装脚本后）。
- 知乎、微博长文、掘金、百家号、博客园的草稿端点会随平台改版漂移，因此 adapter 初始稳定性标为 `experimental`。
- 图片回退资产与发布输出目录。

## 验收标准

- 默认路由不再出现 `csdn_sync_extension`，`$pluginSyncer` 只出现在参考取证说明中。
- 不安装 CSDN 同步助手时，provider 预检仍能选中已注册的 OpenCLI 登录态 adapter。
- 适配器未安装或 OpenCLI 桥接不健康时，预检在数秒内返回 `unavailable` 和回退 provider，不先进入写入超时。
- 五个草稿 adapter 都需要 `--execute`，且返回可用于对账的草稿 ID/编辑链接。
- 任何写入超时或响应未知不会自动切换 provider；先标记 `unknown` 并对账。
- 账本每次 attempt 包含 `started_at/finished_at/duration_ms/status/write_state/error/evidence/fallback_reason`。
- 最终回报继续固定输出“平台 / 完成情况 / 链接”三列表。
- 文章专属图不可用时，选图脚本能根据用途选中尺寸正确的内置 PNG，并在媒体计划中标明 `source: bundled_default`。
- `python3 -m unittest discover -s tests -v` 和 skill validator 通过。
