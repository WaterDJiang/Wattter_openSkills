# 当前布局

新安装统一`WTT/Runtime/koreader`；旧收据路径仅供兼容识别。目录迁移依[迁移流程](runtime-migration.md)，验机前不删旧树。UI0.2.4仅补关于/内部路径入口，旧UI0.2.3的阅读交互保留。

# WTT界面维护

当前UI0.2.3；Skill0.14.0不改变设备界面。首台用户已确认字体/返回/两处设置与退出、微信正文可用，详见[实测范围](verified-scope.md)。本机私有记录优先，不能因更新Skill而再装UI。

## 只更新需要变化的层

- 先`wtt_ui.py --state-dir <私有目录> inspect --device <盘>`。同版匹配则不装；未知变化停，不能强行覆盖。底座问题用wtt_koreader检查，UI问题不顺带重装底座。
- 新装UI须已核验固定KOReader/条件启动文案和当前备份：`install --device <盘> --backup <当前备份> --confirm-device`只写插件源码/许可/来源/图标及`documents/WTT-Reader-03.sh`共八文件，主页显示WTT Reader。
- 不同UI版本先依据同电脑/设备收据回滚旧UI，重新取当前backup/verify-backup再install；不能把已删文件后的设备拿旧备份冒充当前。回滚`rollback --device <盘> --confirm-device`只删匹配收据的剩余拥有文件，支持已删除一部分的中断续跑。
- macOS AppleDouble在删主文件后可能自动消失；先识别/校验元数据再精确删拥有文件，仅删空目录。未知/变化内容全部在删除前阻断，不rmtree清空程序/账号目录。
- 多余的自有原生主页入口只用`wtt_koreader.py hide-legacy-entry --device <盘> --backup <当前备份> --confirm-device`核验后迁入`WTT/Integration/recovery/`并同步所有权。若同轮回滚UI，先迁入口再回滚，再新备份；必要KOReader内核/署名保留，不以名字删除未知组件。

## 已知接口不变量

- 原生ReaderUI构造传入的`dialog`是父阅读窗口。WTT自有工具条用`control_dialog`，不能复用/关闭父窗口；真实构造参数与CloseWidget事件须入回归。
- `返回书架`只叠加WTT列表并保留当前书；继续同书不重开，换书由原生showReader管理，显式退出才调用原生生命周期。不要把返回书架实现成退出进程。
- WTT菜单注册到reader/filemanager共同的`main`；不能用阅读菜单没有的`filemanager_settings`。原生排序会消耗输入表，出错后不能直接重复排序同一残表。
- 原生菜单回退成功才提示已切换；失败则独立继续/退出控件接管，不再将点按送入损坏菜单。

## 验收

主机回归使用固定原生MenuSorter/TouchMenu/Button及UIManager派发，按绘制后的范围点击，不只调用callback。叶子文字栅格/EPDC/OS仍需设备观察；文件送达不证明可用。安全弹出后按此次变化只验相关入口、子菜单、返回/退出，已有成功项目保留。用户仍卡住先恢复/读日志，不反复安装或重越狱。

条件启动文案只改原koreader.sh的一处成功提示分支，仍在原路径运行并保持原自校验；源码/原始与产物摘要/许可在插件ORIGIN。不改内核、设备驱动或删上游署名。
