# WTT Kindle 复活 Skill

把闲置 Kindle 重新配置成日常阅读器。一个 `wtt-kindle-revive` Skill 负责电脑侧检查、备份、固定组件获取、部署维护与传书；设备上使用 WTT Reader 文字书架与大按钮阅读控制。

## 已验证到哪里

- 当前运行版本：Skill 0.15.0 / WTT Reader UI0.2.4。此公开副本补充 README 和 requirements，运行代码与同版原包保持一致。
- 首台实测：Kindle Paperwhite 第一代 Wi-Fi，B024 型号前缀，固件 5.6.1.1；电脑侧为 macOS / Python 3.12。工具最低 Python 3.10。
- 已有用户实机反馈：本地 TXT/PDF/EPUB 样例打开和翻页；字体与排版、返回书架、设置和退出；迁移前后原书续读与已有书签笔记；微信本人登录、正文打开与翻页。
- SSH/SFTP 代码及公钥配置已有主机检查，实际无线送达与开书未完成真机验收。微信独立下载、跨设备同步及全部文件格式未逐项验证。
- 这是首台设备的经验与工具包；其它机型、固件和电脑系统需另行验证。近期全新清空重装的文件阶段已完成，该次重新登录与阅读验收不能直接继承历史通过结果。

## 用 WorkBuddy 调用

- 下载本仓库并解压，取出完整的 `wattter_skills/wtt-kindle-revive` 文件夹；只复制 `SKILL.md` 会缺脚本和载荷配方。
- 将这个文件夹交给 WorkBuddy，或作为工作目录打开，让它先读取本文件与 `SKILL.md`。本说明采用读取本地目录的方式，不限定某一版本的界面按钮。
- Kindle 先充电到可正常启动，用可传数据的 USB 线连接电脑。先确认它能作为存储设备识别。
- 发出指令：

> 请使用这个目录中的 wtt-kindle-revive Skill 帮我检查并复活 Kindle。先读取 README.md 和 SKILL.md，核对机型、固件和现有安装，再确定适配路线。写设备前备份并校验，保留原有书籍、标注和进度；涉及清空时先说明范围，等我明确选择。已越狱或已有可用安装就从当前状态继续。

先执行只验证包、不写设备的命令：

```bash
python3 scripts/wtt_kindle.py verify-package
```

首次获取上游组件需要网络。USB 扫描、备份和包验证使用标准库；Wi-Fi 工具的固定依赖由 `scripts/wtt_transfer.py --state-dir <电脑私有目录> setup` 创建隔离环境安装，`requirements.txt` 提供同一版本锁入口。常规使用交给 Skill 按当前阶段执行，不把安装、清空或重新越狱当作每次调用的默认操作。

## 进入 WTT 和阅读

- 安装完成、安全弹出并拔掉 USB 后，在 Kindle 主页的「本机」找到封面写着 WTT 的「WTT Reader」入口，点开进入 WTT 书架。
- 点书名打开书。书架提供继续阅读、最近书籍、`WTT/Books` 导入书库，以及原位置的 `documents` 历史书籍。
- 点书架顶部「微信读书 · 设置 · 刷新 · 退出」这一行，打开大按钮菜单。
- 阅读时点正文中央或上方菜单区域，呼出阅读控制：返回书架、字体与排版、目录、书签与标注、搜索、阅读设置、添加或取消书签。
- 「返回书架」保留当前阅读会话；「退出阅读」关闭阅读器并返回 Kindle 原界面。
- 微信读书入口调用 finlater/weread.koplugin。手机端所需能力开通、扫码、验证码和授权由本人操作，不向他人提交 Cookie、Key 或验证码。

## 日常导书

USB：退出阅读器 → 连接电脑 → 将有权使用的无 DRM 电子书复制到 `WTT/Books` → 安全弹出并拔线 → 进入 WTT、刷新并打开书。同名不同内容不覆盖。EPUB/PDF/TXT/MOBI/AZW3 由 KOReader 提供格式能力，不表示每个文件都能打开。

Wi-Fi：在设置中手动开启 SSH，电脑与 Kindle 网络互通，再让同一个 Skill 按 transfer 流程配对、核对身份、发送及校验；用完可关闭 SSH。当前真机无线传书尚未验收，按钮不是自动启动的云传书服务。

> 请用 wtt-kindle-revive 把我指定的电子书传到已经配置好的 Kindle。只走传书流程，不重新初始化、重装或清空。连接失败先检查目标身份、网络与接收服务。

## 来源与许可

- WTT 界面、启动文本派生与对应源码：见本目录 `LICENSE`、`device/wttui.koplugin/ORIGIN.json`，AGPL-3.0-only。
- 阅读与设备底座：[KOReader](https://github.com/koreader/koreader)，版本和获取摘要在 `assets/reuse-lock.json`；保留作者、源码和 AGPL 许可。
- 微信读书：[finlater/weread.koplugin](https://github.com/finlater/weread.koplugin)。本仓库只包含入口与固定版本获取配方，未复制插件包；上游许可/非商业声明仍需按其条款核对，不作商用再分发承诺。
- SSH/SFTP 模块来自 [joeseesun/qiaomu-send2kindle](https://github.com/joeseesun/qiaomu-send2kindle)，保留固定提交、修改说明与 GPL-3.0 许可证；不依赖其私有 MCP。
- 校验工具源码、构建说明与依赖来源随包保留。各组件按各自许可使用，本目录不套用仓库其它内容的非商业限制。

公开目录只含工具、源码、固定获取配方与说明；运行数据和用户分区备份需留在电脑的独立私有目录。用户分区备份不是系统镜像，本项目不承诺通用救砖或恢复出厂后的通用恢复。
