# wtt-post-opencli

通过 OpenCLI 把内容发布或创建草稿到微信公众号、微博、知乎专栏、小红书、Twitter/X。这个 skill 会先做平台内容格式适配，再执行真实账号写入，并在平台侧校验结果。

## 需要准备的工具

### 1. Node.js 与 npm

用于安装 OpenCLI。先检查：

```bash
node --version
npm --version
```

### 2. OpenCLI

安装：

```bash
npm install -g opencli
```

检查：

```bash
command -v opencli
opencli --version
opencli doctor
```

### 3. OpenCLI 平台插件或适配器

不同机器上的 OpenCLI 插件安装方式可能随版本变化，先用当前 CLI 自检，不要硬猜：

```bash
opencli --help
opencli plugin --help
opencli list
opencli weixin --help -f yaml
opencli weibo --help -f yaml
opencli zhihu --help -f yaml
opencli xiaohongshu --help -f yaml
opencli twitter --help -f yaml
opencli x --help -f yaml
```

如果某个平台返回 `unknown command`、`unknown site`、`plugin not found` 或类似错误，说明对应平台插件或适配器缺失。此时应先确认当前 OpenCLI 推荐的安装命令，再征得用户确认后安装。

### 4. 浏览器与登录态

知乎专栏、部分微博回退路径、公众号账号切换依赖浏览器会话。检查：

```bash
opencli doctor
opencli browser weixin state
opencli browser weibo state
opencli browser zhihu state
opencli browser xiaohongshu state
opencli browser twitter state
opencli browser x state
```

需要用户在浏览器中登录目标账号。账号不明确时，不要发布，先让用户确认账号身份。

## 激活流程

每次真实发布或创建草稿前按顺序执行：

1. 检查 `opencli` 是否存在。
2. 运行 `opencli --version` 和 `opencli doctor`。
3. 按用户点名的平台检查对应命令或插件是否可用。
4. 加载 `references/content-format.md`，生成平台适配 payload。
5. 加载被点名平台的 reference，执行发布或草稿命令。
6. 用平台列表、草稿列表、URL、页面文本或最新帖子校验结果。

## 缺工具时的自动安装规则

如果缺少 OpenCLI、平台插件、浏览器桥接或 daemon：

1. 先停止真实发布流程。
2. 告诉用户缺少什么、会执行什么命令、影响范围是什么。
3. 等用户确认后再执行安装、重启或浏览器配置命令。
4. 安装后必须重新跑健康检查。
5. 仍然失败时，不要继续发布，按 `未完成` 回报并说明阻塞点。

示例确认话术：

```text
本机没有检测到 opencli。是否允许我执行 npm install -g opencli 安装后继续？
```

```text
检测到 xiaohongshu 平台命令不可用。是否允许我根据当前 opencli plugin 帮你安装对应插件？
```

## 平台格式适配

真实写入前必须先执行 `references/content-format.md`：

- `references/content-format.md` 只定义通用 payload 协议。
- 各平台的文字长度、图文、视频、封面、标签和发布/草稿规则放在对应平台 md。
- 内容长度或素材格式可能不匹配时，不静默截断或转换，先给摘要、拆条、补素材、草稿、跳过等选项。
- `format_only` 模式只输出适配稿，不调用 OpenCLI 写入。

## 目录结构

```text
wtt-post-opencli/
├── SKILL.md
├── README.md
└── references/
    ├── content-format.md
    ├── weixin.md
    ├── weibo.md
    ├── zhihu.md
    ├── xiaohongshu.md
    └── twitter.md
```
