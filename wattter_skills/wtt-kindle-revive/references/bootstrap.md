# 首次执行能力（仅匹配设备时）

本路线实测仅PW1 Wi-Fi/B024/5.6.1.1。已有当前设备真实执行收据且WTT可读时，跳过此文件的引导操作。其它型号/固件先独立确认，不套用本台包、不升级固件。

USB只部署用户分区文件，不授予root。首次触发仍需已审阅的WinterBreak2/jb.sh路径；不能承诺“只插USB就全自动重构系统”。正常任务保留系统/账号/书籍，不默认恢复出厂。

## 准备与触发

1. 用户能回Kindle主页，先飞行模式、USB连接。核对USB身份与固件、固定资产摘要；当前用户分区backup/verify-backup通过才写入。
2. 用当前`wtt_kindle.py --state-dir <私有目录> bootstrap-fetch`获取固定资产，`bootstrap-plan --device <挂载点>`核对路线/空间。`bootstrap-prepare --device <盘> --backup <当前备份> --jb <fetch的jb.sh> --wb <fetch的WinterBreak2包> --confirm-device --airplane-confirmed`只用于尚未执行的首轮。保留本会话暂存/占位/收据，重跑先检查。
3. 正常安全弹出后拔USB，Kindle与电脑同Wi-Fi。`bootstrap-serve --bind <电脑当前局域网IPv4> --port 8080 --timeout 900`保持前台服务，使用返回的短根URL。地址是当前网络的，不复用历史日志里的IP。
4. 页面/HTTP成功后，仍需JS ON和Connection OK。只点一次Start并确认下载。下载响应不等于root/安装成功；最多等约两分钟观察自动重启/安装文字，仍无变化则飞行模式接USB只读最近entry.log/platform.log和diagnose，不连点或再prepare。
5. 自动重启稳定后关闭Wi-Fi，点击本会话WTT Probe等完成，再USB。`bootstrap-check --device <盘>`校验真实身份/challenge、root、固件、OTA阻断与探测摘要。标记/手改布尔值、文件复制或网页请求不能代替探测。0.14.0新会话采用shell_execution_v2，只证明执行/身份/OTA/machine，显示/输入由成熟底座后续真机验证；旧会话按原探测收据校验，不自动改写成新格式。新首装脚本仅主机验证，不冒称已在设备重跑。

## 定向恢复

- 页面打不开先查服务是否到期/电脑地址变化/JS开关。80端口权限不足不等于Kindle不兼容，保持实际可用端口，不重做设备安装。
- entry.log的`stage=entered/uid/hash_check/prerequisites/platform_start/exit`决定下一步。命令查找器不可用时不据此报告所有命令缺失；先诊断lookup。摘要必须通过；随包SHA/Base64工具按入口复制到私有tmp后执行，兼容noexec用户分区。
- 只有已有暂存/摘要/备份一致，且明确失败在入口的已知依赖阶段，才用`bootstrap-repair --device <盘> --confirm-device --airplane-confirmed`。平台已有进展/收据冲突先停，不泛化为“失败就修入口再试”。
- 执行收据通过后`bootstrap-cleanup --device <盘> --confirm-device`仅删除本会话逐项登记且仍为零的占位。平台文件变化后做当前部署前备份，原始备份保留；随后按[koreader-workflow](koreader-workflow.md)部署成熟底座/UI，**不调用旧install/launcher-install**。

## 边界

备份仅可读用户分区，不是系统镜像；应用回滚不等于通用救砖或还原越狱/固件。SHA/Base64工具ARM产物保持不变，完整对应源码小包及MuPDF来源/摘要在`assets/hash-source.json`，主机重建：`python3 device/hash_build.py --deps-dir <电脑缓存> --output <输出路径>`，可选`--zig <编译器>`构建ARM。
