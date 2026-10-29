# 当前布局

新安装统一`WTT/Runtime/koreader`；旧收据路径仅供兼容识别。目录迁移依[迁移流程](runtime-migration.md)，验机前不删旧树。UI0.2.4仅补关于/内部路径入口，旧UI0.2.3的阅读交互保留。

# 安装、维护和传书

先读本机私有检查点/执行与安装收据/用户验收；[已知实测范围](verified-scope.md)只提供参考，不替代当前身份。所有工具用Skill真实绝对路径与电脑独立私有`--state-dir`。

## 首次或明确修复

1. verify-package，确认本次意图。型号/固件/USB身份不明不选包；已确认执行能力不重越狱，未具备时才读[bootstrap](bootstrap.md)。
2. 写设备前backup/verify-backup；仅排除卷根宿主元数据，源变化/摘要错误仍阻断。设备存储模式时不启动阅读器，文件导入前正常退出。
3. `wtt_koreader.py fetch`取固定KOReader v2026.07.1 kindle（PW1非pw2/hf/legacy）和微信v1.6.0资产，核验摘要。首次`install --device <盘> --backup <当前备份> --confirm-device`仅写新路径；已有未知koreader目录停，不自动覆盖。
4. 仅有同电脑冻结清理计划和成功收据时，`rebuild --device <盘> --backup <当前备份> --cleanup-plan <计划JSON> --confirm-device`补缺失程序并保留设置/历史/账号；无证明不能当可覆盖空目录。`inspect`先核实本次内容，rollback只处理本次所有权，未知变化停。
5. WTT界面维护见[wtt-ui](wtt-ui.md)；不会要求用户另装乔木Skill/SimpleUI或调用私有MCP。普通主页只保留WTT Reader，底座源码/许可在关于保留。
6. 安全弹出/拔USB后按本轮范围验入口、书架/开书、翻页、设置/返回/退出；收据只证明送达，标注、续读/休眠各自留证。先验证本地，必要时再联网。

## 日常导书（transfer）

USB：正常退出WTT，连电脑，将无DRM文件拖到`WTT/Books`；同名不同内容不覆盖，已有历史书仍在`documents`，不搬家。安全弹出/拔USB再看书架并开书，不重装/重置/整机备份。

Wi-Fi复用SSH/SFTP，不使用旧TLS。用户已跳过时不要求补测/IP或自动扫描。

- 首次电脑依赖`wtt_transfer.py setup`，隔离在私有运行目录，不改系统Python。后续connect/send失败不自动重装依赖。
- 首次本人正常退出/USB连接，`pair --device <盘> --confirm-device`保留现有authorized_keys/设置，只写公钥和本项目元数据。私钥仅系统钥匙串，禁无密码、服务不自启。
- 安全弹出后Kindle和电脑同Wi-Fi，WTT设置/兼容菜单中手动启动SSH，按屏幕IP/端口（常用2222）。电脑`connect --host <屏幕IP> --trust-new-device`仅首次明确信任；认证后核对USB序列摘要，再固定主机密钥。以后指纹改变停止，不自动替换；USB配对不等于已证明服务器密钥。
- `status`看本项目配对，`connect`握手；换网只核对当前地址和既有身份。`discover`仅已有固定身份时用于对应私有子网，不声称未验证自动发现可用。
- `send --file <本地文件>`：临时文件上传、完整回读大小/SHA-256后提交到WTT/Books。允许无DRM EPUB/PDF/TXT/MOBI/AZW3，上限512MiB，兼容仍看开书。同名同内容不重传，不同内容拒绝；断线先查同一个最终文件/任务，不能随意换名重发。
- 送达、刷新书架、实际阅读分别留证，用完可停SSH，接USB前先正常退出。网络失败留在transfer，绝不转复活或清空。

## 微信读书

WTT书架操作行点微信读书；首次按固定插件README由本人手机微信读书App开通官方Skill/API能力，再本人扫码确认/输入验证码。无需把API Key/Cookie/验证码交给Codex。先问实际页面/错误，不要求重新登录一个已经成功的账号。

入口、登录、本人书架与正文打开/翻页分开验；仅“OK”不明确时澄清一次，已明确正文可读就记录通过。书架列表/下载/进度同步没有单独测试则单列。开源版不冒充闭源WeReader全功能；当前固定配方从上游取包，个人验证与公开/商用分发许可分别核对。
