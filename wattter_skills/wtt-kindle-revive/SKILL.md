---
name: wtt-kindle-revive
description: Kindle首次复活、定向修复与日常USB/Wi-Fi传书。WTT Reader复用KOReader和微信插件；先核对当前记录，传书不重置或重装。
metadata:
  version: "0.15.0"
---

# WTT Kindle

用户只安装这一个Skill。电脑侧负责检查/备份/固定组件部署/恢复/传书；设备使用WTT Reader UI0.2.4＋KOReader v2026.07.1＋微信插件v1.6.0，SSH/SFTP负责无线传输。保留上游来源/许可，不把Kindle Wi-Fi等同Android APK能力，不回到旧C阅读器或TLS路线。

## 先判断意图，再读对应流程

- **revive**：首次配置，或用户明确修复。先读取当前私有检查点、执行/安装收据和用户已验项目；已有成功能力从断点接续，不重复越狱、清理、整机备份或微信认证。只修坏的层：引导、底座、WTT界面、格式样本、账号、传输彼此分开。
- **transfer**：日常USB拖书或Wi-Fi传书。只核对文件、连接/配对/目标身份和送达；不运行revive、整机备份、重装或重置。连接失败仍留在transfer。
- 意图不明只问本次要修复还是传书。组件清单/历史备份/文件复制不是设备成功证据，也不能据此自动清空。用户已跳过某项就记录跳过，不反复索要IP或补测。

| 情况 | 按需读取 |
|---|---|
| 首次安装或成熟底座维护 | [安装与传书工作流](references/koreader-workflow.md) |
| 旧根目录迁入WTT、引导归档/清理、布局回滚 | 先读[内部目录迁移](references/runtime-migration.md)，按计划部署/切换，用户本次真机通过后才清理旧根 |
| UI更新、入口清理、旧UI回滚 | [WTT界面工作流](references/wtt-ui.md) |
| 未取得对应机型的真实执行能力 | [引导流程](references/bootstrap.md)；已有执行收据不加载此分支 |
| 报错、卡住、网页无效果、格式失败 | 先只读diagnose，再查[故障表](references/troubleshooting.md) |
| 核对已跑通范围/避免重复验收 | [实测范围](references/verified-scope.md)及本次设备私有记录；后者优先 |

## 真实命令与边界

用当前Skill的真实绝对路径；`--state-dir`是电脑上的独立私有目录，不放在Skill或Kindle里。

- `scripts/wtt_kindle.py`：scan、backup、verify-backup、status/plan、verify-package、diagnose及bootstrap-*。先verify-package；status的全局未验证清单不表示已配置设备需要重装。
- `scripts/wtt_kindle.py --state-dir <目录> diagnose [--device <已挂载盘>] [--log <私有日志>] --mode <auto|revive|transfer>`：只读，无目录创建、网络或自动修复；只输出固定原因码，不回显原日志。未连接时可用已有记录分析，不强迫为每条问题接USB。
- `scripts/wtt_koreader.py`：fetch/install/rebuild/inspect/hide-legacy-entry/rollback；只采用固定下载配方。未知既有目录先停；清理后rebuild须同电脑清理成功证明及当前备份，保留设置/历史/账号。
- `scripts/wtt_ui.py`：inspect/install/rollback；仅拥有的八文件UI，不顺带重装底座。正常只见WTT Reader；额外原生脚本保留于非主页恢复目录，未知入口不删。
- `scripts/wtt_transfer.py`：setup/pair/connect/status/send/discover，使用成熟SSH/SFTP。setup只首次装电脑依赖；公钥USB配置，私钥在系统钥匙串，服务手动开启/仅密钥/不自启。首次由用户给出地址并明确首次信任，核对USB序列摘要；以后指纹变化停止，不能忽略主机身份。

所有新安装底座位于`WTT/Runtime/koreader`，插件/字体/缓存/原配置同树保存。旧根只识别、迁移或恢复；不能创建顶层软链接伪装迁移。`wtt_migrate.py`负责plan/deploy/activate/inspect/record-validation/finalize/rollback，普通传书不调用迁移。原生OTA/扩展更新停止，由固定WTT工具维护；关于保留KOReader/微信作者和许可证。

## 写入与故障接续

设备身份/固件不明不挑包或升级。写入前匹配目标、载荷摘要和当前已验证备份；备份仅用户分区，卷根macOS索引元数据排除，不是系统镜像。源变化/摘要不符仍阻断。正常运行的设备不因本Skill更新而重装。

失败先记录当前屏幕/最近会话/阶段及退出码，不反复点Start或用重装替代定位。一次小变更完成主机验证后再安全弹出、按变化范围验机；按钮测试须包含真实上游构造参数、原生触控/菜单排序，直接调用回调不算触屏证明。

回滚只处理本机收据拥有且哈希匹配的剩余文件；AppleDouble先核对再删，已消失的拥有文件可续跑，未知/变化内容先停，不递归清空状态目录。清空/恢复出厂须另说明删除范围、备份局限和恢复条件，由用户明确选择；已有修复授权不反复问同一操作。

## 阅读与交付验收

书库用`WTT/Books`，历史书籍在`documents`原位置；同名不同内容不覆盖，同内容不重发，断线先核对同一最终文件。SSH送达、书架可见和实际开书分别记录。共享KOReader进度/书签/标注，旧WTT/State保留但不承诺自动迁移。

微信本人手机开通官方Skill能力、扫码/验证码本人操作；不索取或打印API Key/Cookie/验证码。入口、登录、书架、正文打开/翻页是不同验收层；用户明确已能正文翻页就记录通过，不要求重复认证。未明确“OK”到哪一步时只澄清一次。

代码/包、Water源目录同步、个人Skill注册、设备文件安装、用户实机验收和公开发布分别报告。个人副本/软链接保持用户原有状态。公开记录不带私人书名/账号/完整序列号，原日志只留私有目录。单机通过不等于全型号、所有格式/同步或无线都通过。
