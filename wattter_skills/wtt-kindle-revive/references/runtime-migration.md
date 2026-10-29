# 内部运行目录迁移

目标`WTT/Runtime/koreader`，内部辅助`WTT/Runtime/extensions/koreader`，真实执行证据`WTT/Runtime/Evidence`。书籍/外部侧车仍在documents与WTT/Books，旧WTT/State不改。第一次进入迁移先读本设备最新检查点与迁移收据，不重复越狱/备份/重新认证。

使用同一私有state运行`python3 <Skill>/scripts/wtt_migrate.py --state-dir <state> <command> --device <挂载盘> --confirm-device`：

- `plan --backup <当前完整校验备份>`：匹配USB/固件/执行及电脑设备收据，固定旧树/新树逐文件摘要，使用完整备份归档。未知目标/链接/待更新包或源变化停止。
- `deploy`：完整状态树与必要派生程序复制至内部，逐项读回；不改日常入口、不删旧根。中断按本次计划接续，未知/变化文件不覆盖。
- `activate`：新树读回后切换拥有的WTT Reader入口及维护收据，保持原微信/SSH身份。状态awaiting_hardware；安装送达不算验机。
- 安全弹出后，用户验证原书开书/翻页/字号/返回/退出/续读，原微信无需重新登录能开正文翻页，原标注/书签/进度仍在。登录状态迁移失败时先查原数据，不要求重新认证。
- 本次明确全部通过后，`record-validation --checks local_read_turn_font_return_exit_resume weread_existing_login_body_turn existing_notes_bookmarks_progress`（不用device）；不能由主机测试、历史成功或“能打开入口”替代。部分通过只记项目检查点，暂不运行finalize。
- 接USB后`finalize`：绑定本次真机记录，先归档并验证所有待删旧树字节，再按精确清单移除旧koreader、拥有extensions子目录、winterbreak2与WTT/bootstrap；未知/变化内容阻断，原始probe保留内部、维护门禁兼容。无顶层koreader链接。
- `rollback`：恢复本次旧布局与入口；迁后状态先完整私有归档并带回旧布局，原程序恢复原字节，不以旧账号/进度覆盖新状态。保留内部副本和恢复记录。中断清理/回滚先核对，不自动清空现场。

平台例外：libkh/bin/fbink为越狱平台安装的系统shell集成配套文件；USB模式不能安全改系统分区入口，因此本轮保留平台兼容路径，并为WTT保存内部副本。其它extensions未知兄弟不动。系统/临时/内核路径不移动。

编译SSH二进制含旧SFTP路径，WTT客户端使用显式exec-channel调用内部sftp-server；不改二进制、服务器密钥/authorized_keys/钥匙串及固定指纹。服务需保持WTT/KOReader运行，接USB前退出。通用第三方客户端的默认sftp子系统和旧SCP不声称适配；WTT无线真机未验继续单列。

原生OTA及旧扩展安装器会绕过WTT所有权，因此内部版停止这些入口，不升级底座版本；后续先按当前布局inspect/备份，固定组件工具部署只走内部路径。未知或变更文件先处理，不能复制一份顶层目录绕过门禁。
