# 定向排障

先`wtt_kindle.py --state-dir <私有目录> diagnose --log <日志> --mode <模式>`，设备已安全退出且USB挂载时才加`--device`。诊断不会创建目录/联网/备份/改设备，也不会替你修复。保留原始日志在私有目录，分享固定原因码即可；未知/无日志时不编造根因。

| 现象/原因码 | 下一步 | 停止条件 |
|---|---|---|
| 电池/充电画面，或型号固件不明 | 先充电、实际USB身份/版本和能否进主页 | 未识别前不挑刷写包/重置 |
| 页面打不开、network_address | 核对当前网段、电脑新地址、服务是否到期、浏览器根页及JS | 不重做备份、占位或安装；换网不等于重头来 |
| 下载成功但无变化 | 等一次约两分钟，飞行模式接USB看entry/platform最近阶段 | 下载/HTTP/JS均不等于设备执行；不连点Start |
| lookup_unavailable | 先验证命令查找器对已执行工具是否可靠 | 不把所有工具一起报缺失 |
| sha256_tool_missing / sha256_mismatch | 固定源与随包校验工具；noexec区的工具按引导复制到私有tmp | 不能跳过摘要，不执行未核验载荷 |
| base64_missing | 核对旧系统解码与随包SHA/Base64工具 | 只有对应失败阶段才定向修入口，不重复引导 |
| busybox_dirname | 旧BusyBox不接受`dirname --`，使用已验证POSIX启动流程 | 不据此改阅读引擎/升级固件 |
| usb_state_query | 只用本机实际可用接口与安全弹出后的屏幕观察 | 不绕过USB存储保护，不借用其它型号接口 |
| 工具条全按钮无效，老UI0.2.1 | 核对原生传入dialog是否被当自有弹层关闭；UI0.2.2起用control_dialog | 先查真实构造/关闭事件，不能只测callback或反复安装 |
| menusorter_failure | 核对reader/filemanager中注册位置及自定义菜单；WTT现用共同main | 失败排序会消耗原表，不继续点击损坏菜单 |
| native_fallback_failed | 当前UI保留独立继续/退出控件 | 未开成功不能称“已切换原生菜单” |
| document_open_failed | 检查文件完整性/DRM/EPUB容器元数据，另一本合法样例对照 | 坏EPUB不等于KOReader没有EPUB，不重装底座 |
| macOS备份噪声 | 排除卷根索引元数据，保留书/配置及嵌套同名文件 | 不是任意忽略读错/源变化/摘要失败 |
| appledouble_rollback | 先核对剩余拥有文件与元数据，再精确续跑旧UI回滚 | 未知/变化文件停止；不泛用rmtree或忽略所有错误 |
| 清理后剩koreader状态目录 | 有同电脑清理收据＋当前备份才rebuild缺失程序 | 保留账号/进度/笔记，不强删目录当首次安装 |
| 传书/配对失败、legacy_tls_pairing | 保持transfer，检查SSH公钥/手动服务/当前地址与固定身份 | 不转旧TLS、重置、重越狱或整机备份 |

原始错误包含URL查询、令牌、书名或账号时不转贴。`crash.log`以前的失败可能已经解决；diagnose优先最近`launching...`会话，entry优先最近`stage=entered`。正常exit0只证明这次退出，不能替代开书/正文/标注验收。
