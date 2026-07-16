# 无 CSDN 插件的分层发布路由

> 任何真实发布、草稿创建或编辑器写入都必须加载。`format_only` 不需要。

## 目标

优先使用格式保真、交互成本低的官方 API 或 OpenCLI 登录态 adapter。只有上一路径明确没有产生写入时，才回退 OpenCLI UI/浏览器编辑器。

这套路由不安装、不探测、不调用 CSDN 同步助手。OpenCLI 自身的 Chrome 桥接仍用于读取用户已有 Cookie/CSRF 和执行 UI 回退。

## Provider 类型

| Provider | 含义 | 前置 |
|---|---|---|
| `official_api` | 平台公开 API 或已有官方 API 脚本 | 配置、token、白名单 |
| `opencli_login_adapter` | 本 skill 随附的 COOKIE/HEADER 草稿 adapter | adapter 已注册、OpenCLI 桥接健康、平台已登录 |
| `opencli_adapter` | OpenCLI 已内置的平台写 adapter | 命令已注册、OpenCLI 桥接健康 |
| `opencli_ui` | OpenCLI UI adapter 或 `opencli browser` 原生编辑器 | `opencli doctor` 通过 |
| `manual_confirm` | 内容/素材已准备，等待用户完成平台操作 | 明确的人工动作 |

不得把发布任务中临时手写的私有 `fetch` 当作 provider。网页后台接口必须封装成带 `--execute`、结构化结果和校验方法的 OpenCLI adapter。

## 默认优先级

```text
official_api
  -> opencli_login_adapter
  -> opencli_adapter
  -> opencli_ui
  -> manual_confirm
```

微博必须先按 payload 变体裁剪候选 provider：`short_post` 默认只使用 `weibo/publish -> opencli_ui -> manual_confirm`；只有显式 `longform` 才使用 `weibo/article-draft -> opencli_ui_longform -> manual_confirm`。预检通过 `--weibo-variant short_post|longform` 接收这个决策，禁止仅因长文 adapter 已安装就优先选择它。

平台 reference 可以删掉不适用的 provider，但每个自动 provider 必须写明：

- `stability: stable|experimental`
- `last_verified_at`
- `supports: draft|publish|images|cover|html|markdown`
- `verification_method`

没有账号识别、没有写入后回读方法，或本次必需能力不支持时，不得选为主路径。

## 执行前预检

先只对本次目标平台执行：

```bash
python3 scripts/provider-preflight.py \
  --platforms weibo,zhihu,juejin,baijiahao,cnblogs \
  --require-images weibo,zhihu
```

预检会读取 `opencli list -f json`、`opencli doctor` 和 `adapters/manifest.json`，并行执行只读账号探针，输出每个平台的 `account_check/selected_provider/selected_command/fallback_reason/candidates`。

- adapter 未注册：`adapter_not_registered`，立即选 UI，不发起写请求。
- OpenCLI 桥接不健康：`opencli_bridge_unhealthy`，立即停在人工确认或修复桥接。
- 账号探针失败：`account_not_authenticated`，直接选 UI 登录/发布路径，不尝试 adapter 写入。
- 本次必须自动处理图片，但 adapter 只支持文本：`missing_capability:images`，直接选图片可校验的 UI/API 路径。

只有在 adapter 源码新增或更新后，才运行：

```bash
python3 scripts/install-opencli-adapters.py --check
python3 scripts/install-opencli-adapters.py --install
opencli list -f json
```

安装会写入 `~/.opencli/clis/`，必须先获得用户授权。

## 执行结构

```yaml
execution:
  selected_provider: null
  fallback_chain: [official_api, opencli_login_adapter, opencli_adapter, opencli_ui, manual_confirm]
  write_state: not_started
  circuit_breaker:
    max_confirmed_failures: 2
    confirmed_failures: 0
    open: false
  attempts: []
  verification:
    status: pending
    draft_id: null
    post_id: null
    url: null
    title_matched: false
    body_start_matched: false
    body_end_matched: false
    key_sections_matched: []
    expected_images: 0
    verified_images: 0
    evidence: []
  fallback_reason: null
```

每次 attempt 必须写入账本：

```yaml
- attempt_id: attempt_xxx
  provider: opencli_login_adapter
  started_at: 2026-07-16T10:00:00+08:00
  finished_at: null
  duration_ms: null
  status: pending|accepted|success|failed|unknown|skipped
  write_state: not_started|confirmed_not_created|created_unverified|created_verified|published_unverified|published_verified|unknown
  error: null
  evidence: []
  fallback_reason: null
```

## 写入状态机

| `write_state` | 含义 | 允许自动回退 |
|---|---|---|
| `not_started` | 尚未发起写请求 | 是 |
| `confirmed_not_created` | 平台明确失败，且回读确认没有草稿/帖子 | 是 |
| `created_unverified` | 拿到草稿 ID/编辑链接，内容未核对 | 否 |
| `created_verified` | 草稿存在且内容已核对 | 不需要 |
| `published_unverified` | 收到发布响应，公开内容未回读 | 否 |
| `published_verified` | 公开内容存在且已回读 | 不需要 |
| `unknown` | 超时、断连、响应解析失败或只收到受理结果 | 否，先对账 |

除 `not_started`、`confirmed_not_created` 外，其他状态不得自动回退。禁止把 HTTP 200、命令退出码0、按钮点击成功单独当成平台写入成功。

## Provider 执行与对账

1. 初始化 `publish-results.json`。
2. 运行预检，选择第一个满足命令、账号、内容格式和媒体能力的 provider。
3. 用 `attempt-start` 记录开始时间，再发起写入。
4. 命令结束立即用 `attempt-finish` 记录状态、耗时、错误与回退原因。
5. adapter 返回草稿 ID/链接后先记 `created_unverified`，再在目标平台草稿列表/编辑页回读。
6. 核对标题、正文开头/结尾、1 个中段关键句和图片数。
7. 只有确认没有新写入，才能设为 `confirmed_not_created` 并回退。
8. 同一 provider 本轮 2 次确定性失败后熔断。

超时、桥接断开、adapter 报 `WRITE_UNKNOWN`、UI 点击后页面不跳转，都必须先用账号、标题指纹和执行时间窗口查最近草稿/帖子。

## 内容与媒体继承

- 所有 provider 必须消费同一份已适配 `platform_payload`，不得在回退时重新使用原文。
- 适配器当前只在无本地图片引用时进入写入路径。本次必须自动处理图片时，预检直接选 API/UI。
- 微博默认先生成并发布摘要短帖；显式微博长文失败不得自动改成短微博，短帖失败也不得改建长文草稿。知乎/公众号富文本失败不得静默退成未排版纯文本。
- 图片生成与平台插入是两个独立状态；未插入时标记 `manual_asset_ready` 或 `blocked`。

## 最终回报

先运行 `scripts/publish-result.py summary --strict`。最终回复必须包含：

```markdown
| 平台 | 完成情况 | 链接 |
|---|---|---|
```

每个平台报告最终 provider、主路径错误/回退原因、草稿或帖子链接、标题/正文/图片校验结果。没有链接写 `—`，不得省略失败、跳过或待确认平台。
