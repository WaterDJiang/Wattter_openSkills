---
name: wtt-wechat-comment-miner
description: 微信公众号评论区/留言区数据挖掘。当用户要求打开公众号文章并整理、采集、分析留言区/评论区（含高赞留言、观点聚类、情绪分布、选题与商机提炼）时使用。核心链路：微信内置浏览器展开留言面板 → 界面逐屏滚动 → 窗口截图 → 本地 Vision OCR → 脚本清洗去重 → 逐条结构化与议题聚类 → 输出 HTML+MD 报告。适用于 mp.weixin.qq.com 文章的留言区，也适用于需要读取微信客户端 WebView 内文字的场景。注意：HTTP 直连与留言接口均拿不到留言数据，必须走微信客户端截图 OCR 路径；微信 4.1 主窗口不可截图，须走 Cmd+F 搜一搜独立窗口。
---

# 公众号评论区数据挖掘

## Overview

把一篇微信公众号文章的留言区，从「微信客户端里的一堆图片文字」变成「可统计、可引用、可提炼选题与商机的结构化报告」。

**铁律（任何步骤都生效）：**
1. **不要声称能 HTTP 直连抓留言**。文章正文能抓，留言区抓不到（`appmsg_token` 为空、接口返回「请在微信客户端打开链接」）。唯一可靠路径是微信客户端 + 截图 + OCR。
2. **绝不发送任何微信消息**。打开文章给「文件传输助手」发链接属于发送私聊，执行前必须获得用户明确授权。默认让用户自己在微信里打开文章。
3. **屏幕录制权限是硬前提**。宿主 App 的主进程（Bash/WorkBuddy 等）必须被授予 Screen Recording 权限，否则 `screencapture -l` 失败。权限没通时先让用户去「系统设置 → 隐私与安全性 → 屏幕录制」勾选，不要反复重试。
4. **只报可辨识的数据，不编造**。OCR 错字按上下文校正，不确定处标「疑似」；点赞数缺失就写缺失，不猜。报告里必须写清「识别 N 条 / 显示 M 条」的边界。
5. **合规红线**：不碰账号买卖、翻墙、中转站推荐。分析「账号焦虑」可以，提供规避方案不行。
6. **微信 4.1 主窗口不可截图，别跟它死磕**。主窗口 `kCGWindowSharingState = 0`（微信自己设的防截屏属性，一开始就如此，不是操作导致的）：按窗口 ID 截报 `could not create image from window`、整屏/区域截图合成时不渲染它、GUI advisor 拿到纯黑图、AX 树只有 3 个无标题按钮。**唯一可操作的是「搜一搜 / 公众号主页 / 文章」这类独立窗口**（约 817×1030，`sharing=1`，画面完全可读）。
7. **焦点决定点击是否生效**。每次工具调用都可能让宿主 app 抢走前台；微信一旦失前台，坐标点击就穿透到别的 app（实测点到错误文章、甚至把 Chrome 点到前台）。所以「激活微信 → 唤起搜索 → 输入 → 回车」必须在**同一个 Bash 脚本内**完成，不能跨工具调用拆开。

## When to use

- 用户给出 `mp.weixin.qq.com` 链接，要求整理/分析留言区、评论区、精选留言
- 用户只给公众号名（如「量子位」）要找最新过万文章并分析留言 → 走阶段 1 路径 B
- 用户想知道评论区在聊什么、高赞观点、情绪分布、可提炼的选题或商机
- 需要读取微信客户端 WebView 内的文字（AX Tree 读不到，只能截图 OCR）

## Workflow

### 阶段 0：环境自检（动手前先跑）

用 Bash 探测四件事，失败就先解决，不要硬上：

```bash
# 1) 屏幕录制权限：能截到图就通了
screencapture -x -l <WINDOW_ID> -t png /tmp/probe.png && ls -l /tmp/probe.png
# 2) 微信窗口清单（含 offscreen），记录 sharing 状态和尺寸
swift -e 'import CoreGraphics; let l=CGWindowListCopyWindowInfo([.excludeDesktopElements],kCGNullWindowID) as? [[String:Any]] ?? []; for w in l { let o=w["kCGWindowOwnerName"] as? String ?? ""; if o.contains("WeChat")||o.contains("微信") { let b=w["kCGWindowBounds"] as? [String:Any] ?? [:]; print("id=\(w["kCGWindowNumber"] ?? "-") sharing=\(w["kCGWindowSharingState"] ?? "-") \(b["Width"] ?? "?")x\(b["Height"] ?? "?") @ \(b["X"] ?? "?"),\(b["Y"] ?? "?")") } }'
# 3) OCR 二进制是否就绪
ls -l scripts/wx_ocr || swiftc scripts/wx_ocr.swift -o scripts/wx_ocr
# 4) 微信前台状态
swift -e 'import AppKit; print(NSWorkspace.shared.frontmostApplication?.localizedName ?? "-")'
```

窗口 ID 会变，以探测结果为准。外接屏时窗口坐标可能是负值，属正常——但这会让 advisor 定位失准，必要时用 AX `setPosition` 移回主屏。

**第 5 项：判断窗口能否被 GUI 接管（最关键的新增判据）**

对候选窗口逐个调 computer-use `get_app_state`，看返回里的 `image_base64_len`：

| `image_base64_len` | 含义 | 动作 |
|---|---|---|
| **> 100 KB**（实测约 245 KB） | 画面完整可读 | advisor 可用，放心精确点击 |
| **< 50 KB**（实测 24–49 KB） | 纯黑图，advisor 在猜坐标 | **禁止点击**，换窗口或走路径 B |

**不要试图根据猜测坐标去点黑图窗口。** 这是本 skill 最大的时间黑洞。

### 阶段 1：打开文章并展开留言面板

**先选路径**：用户愿意自己点 10 秒就走 A；用户只给公众号名 / 不想动手就走 B。

#### 路径 A：用户自行打开（最快）

让用户在微信里自行打开目标文章（避免发私聊），然后直接跳到下方「展开留言面板」。

#### 路径 B：Cmd+F 搜一搜自主定位（无需用户动手）

用户只给公众号名（例如「量子位」）时用这条。核心是**绕开不可截图的主窗口**，用键盘唤起搜索，回车进入「搜一搜」独立窗口（`sharing=1`，画面完全可读），后续全用 advisor 精确点击。

> **已证伪，别再试**：① 在 `sharing=0` 的主窗口上用坐标点击——advisor 看黑图给错坐标，实测点到「魔都攻略通」「番禺蒙记」的文章，甚至穿透到 Chrome；② `open -a WeChat <mp.weixin.qq.com/s/...>` 唤起文章窗口——返回 `-10820`；③ 后台 CGEvent 鼠标点击（无 Accessibility 权限，事件被丢弃）。**只有键盘事件（Cmd+F / 粘贴 / 回车）在单脚本内对前台微信有效。**

**B1 · 单脚本完成搜索（务必一个脚本内，别拆开）：**

```bash
swift -e '
import AppKit
import CoreGraphics
if let wx = NSWorkspace.shared.runningApplications.filter({ $0.bundleIdentifier == "com.tencent.xinWeChat" }).first {
    wx.activate(options: [])
    _ = wx.unhide()
}
usleep(600000)
func key(_ code: CGKeyCode, _ flags: CGEventFlags = []) {
    let d = CGEvent(keyboardEventSource: nil, virtualKey: code, keyDown: true)!
    let u = CGEvent(keyboardEventSource: nil, virtualKey: code, keyDown: false)!
    d.flags = flags; u.flags = flags
    d.post(tap: .cghidEventTap); usleep(30000); u.post(tap: .cghidEventTap)
}
key(3, [.maskCommand])            // Cmd+F 唤起搜索面板
usleep(700000)
let pb = NSPasteboard.general      // 中文必须用剪贴板粘贴，CGEvent 打不出中文
pb.clearContents()
pb.setString("量子位", forType: .string)   // ← 换成目标公众号名
key(9, [.maskCommand])            // Cmd+V
usleep(900000)
key(36)                            // Return 打开第一项（搜一搜结果页）
usleep(1000000)
print("frontmost=\(NSWorkspace.shared.frontmostApplication?.localizedName ?? "-")")
'
```

验证成功的标志：出现一个约 **817×1030** 的新微信窗口，`screencapture -l <新ID>` 能截出内容，`get_app_state` 的 `image_base64_len ≈ 245 KB`。搜索面板高度从 432 涨到 710 说明关键词命中了。

> 注：`swift -e` 里的中文字符串可直接写；若粘贴失效，检查 `NSPasteboard.general` 是否被其他 app 占用。不要按 Cmd+F 之后再去 `get_app_state`（会抢焦点）——直接在同一脚本里走完到回车。

**B2 · 在「搜一搜」窗口里导航（全程 advisor，画面可读）：**

1. `get_app_state(target_id=<新窗口ID>)` → 确认 `image_base64_len > 100KB`
2. `get_next_action` → 点顶部「账号」卡片里的目标公众号（实测量子位卡片约在窗口 `(303, 300)`）→ 进公众号主页
3. 主页按时间倒序列出推送，每条带标题、日期、阅读量、点赞数。**逐条核对阅读量**，用 `scroll` down 600 找**最新一篇 > 1 万**（显示 `1万+` / `10万+` / 大于 10000）。注意：**当天新推常常只有一两千阅读，别把「最新」等同于「过万」**——实测量子位当天头条 4485、次日 2494，最新过万的是昨天一条 4.2万。
4. `get_next_action` → 点目标文章卡片打开（文章可能在同一个 817×1030 窗口内打开，不一定新建窗口，截图确认即可）

#### 展开留言面板（路径 A / B 共用）

- 对文章窗口 `get_app_state` → `get_next_action` 定位并点击**右下角「留言 N」入口**（约 `[750, 1019]`，贴近窗口底边缘，可能被 clamp 但仍有效）
- 展开成功标志：右侧出现「留言 N」面板 + 底部「写留言」输入框
- 记下 `view_id`（形如 `v1-62565`）和 `target_id`（窗口 ID）

### 阶段 2：批量逐屏采集

**先判断要不要 OCR**：留言 ≤10 条且**一屏全部可见**时，直接用 `screencapture -l` 的高保真截图视觉直读（昵称/地区/时间/点赞/正文），跳过 OCR 和清洗，直接进阶段 4。实测 5 条留言视觉直读识别率 5/5，比 OCR 更准，且省掉整条采集链路。报告里如实写「一屏全显，视觉直读，未走 OCR」。

留言多于一屏才走下面的逐屏链路：

**开跑前先清掉上一轮的采集文件**：`rm -f /tmp/wx_full_*.txt`。`wx_grab.sh` 往 `/tmp/wx_full_all.txt` 追加写，`wx_clean.py` 默认 glob `/tmp/wx_full_*.txt`，旧文章的屏不清掉会混进本轮清洗（2026-11-23 实测复现）。

**关键提速技巧（血泪经验）：**
- `view_id` / 坐标系**只需建立一次**，之后可直接连续 `scroll`，不必每屏 `get_app_state`。只有报 `no_view: 尚未建立坐标系` 时才重新 `get_app_state`。
- **后台 CGEvent 滚动无效**（Bash 进程无 Accessibility 权限）；**AXUIElement 缩放微信窗口失败**（-25200，且全屏状态下连 setSize 都锁死返回 0 却不生效）。滚动只能用 computer-use 的 `scroll`。
- 每屏 scroll 后固定 `pixels: 600`（保证相邻屏有重叠，不漏留言），然后调用抓取脚本。

单屏采集（重复 until 到底）：

```bash
# computer-use scroll: {target_id, coordinate:[面板中心x, 面板中心y], direction:"down", pixels:600, view_id}
sleep 0.4 && bash <skill>/scripts/wx_grab.sh <屏号N> <WINDOW_ID>
```

脚本会截图、OCR、追加到 `/tmp/wx_full_all.txt`，并回显 `SCR N md5=... lines=...`。

**屏数多时交给子代理批量跑**，给它明确的 window_id / view_id / 坐标 / 脚本路径 / 停止条件，避免主对话被 80+ 轮工具调用淹没。

**到底判定**：连续 2–3 屏 md5 完全相同、尾部文字逐字一致，即已到底。不要信 `get_next_action` 说的 `done`（会误判），以 md5 为准。

### 阶段 3：清洗去重

```bash
python3 <skill>/scripts/wx_clean.py
```

脚本做两件事：
- 按「某行出现在 ≥12 屏」识别为**文章正文干扰行**并剔除（正文在左侧每屏重复，留言在右侧滚动）
- 相邻屏首尾滑窗匹配去重（scroll 有重叠）

输出 `/tmp/wx_clean_lines.txt`。

（阶段 2 若走视觉直读分支，跳过本阶段。）

### 阶段 4：逐条结构化与议题聚类

按 360 行一段切分（或视觉直读时直接逐条），识别昵称、地区、时间、点赞、正文，并按 6 类议题标注：

| 标签 | 议题 |
|---|---|
| A | 账号与可得性焦虑（封号/风控/地区限制/中转站/账号注册/充值） |
| B | 工具链与工程实现（skill/CLI/反代/computer use/自动派活/调度脚本） |
| C | 模型能力对比与体验（各模型文案/审美/可读性/沟通力评价） |
| D | 方法论二次创作与认同（框架演绎/类比/赞同） |
| E | 作者本人与情感连接（人格化/玩梗/关怀） |
| F | 求教程/催更/其他 |

**OCR 常见坑**：点赞数被识别成「色55」「凸 21」「直 30」「#7」「山5」「合 17」「72」等，取其中数字；「N条回复～/く/♥」是回复数不是点赞；claude→calude 等错字按上下文校正。

### 阶段 5：产出报告

生成两份文件到用户工作区，命名 `公众号留言分析_<主题>_<日期>.{md,html}`：

- **Markdown**：一句话结论 → 数据说明（采集路径/覆盖范围/精度边界）→ 议题分布表 → 高赞 Top N → 核心洞察（3–5 条）→ 金句原文 → 选题与商机 → 与前次结论修正（如有）
- **HTML**：暗色单文件、Chart.js 议题条形图、Top N 表格、洞察卡片、金句卡片、选题商机卡片；CDN 只用 `cdn.jsdelivr.net`

**报告必写边界**：识别条数 vs 显示总数、楼中回复是否展开、点赞数识别率、OCR 精度说明（视觉直读则写「未走 OCR，视觉直读 N/N」）。

## 从留言提炼选题与商机（分析框架）

采集分析完后，用户往往要「选题和商机」。套这个框架：

1. **找错位**：作者讲什么 vs 读者问什么，落差最大的地方就是最佳选题。
2. **看高赞结构**：如果 Top 5 多是情感/玩梗而非技术，说明人格化 IP 压倒内容本身，选题要带人情味。
3. **看争议**：留言里往返辩论、没有结论的点（如「平替之争」），是最明确的内容缺口。
4. **看赞数倒挂**：高质量二创却低赞 = 未被满足的深度内容需求。
5. **商机闭环**：公众号选题（流量）→ 免费模板（钩子）→ 付费工具包 / 陪跑（利润）→ 企业内训赠品（放大）。给出客单价区间和「最小验证路径」（先发选题+免费模板，看追问人数再决定是否封装）。

## Bundled resources

- `scripts/wx_ocr.swift` — Vision OCR 源码（`zh-Hans`/`en-US`，accurate 模式）。首次使用需 `swiftc scripts/wx_ocr.swift -o scripts/wx_ocr` 编译。
- `scripts/wx_grab.sh` — 单屏采集：`wx_grab.sh <屏号> <窗口ID>`（窗口 ID 每次会话都变，先用阶段 0 探测），截图 + OCR + 追加汇总。
- `scripts/wx_clean.py` — 清洗：`python3 scripts/wx_clean.py`，去正文干扰 + 相邻屏重叠去重，输出 `/tmp/wx_clean_lines.txt`。
- `references/field_notes.md` — 完整实战记录：HTTP 证伪证据、微信 4.1 主窗口黑图坑与 Cmd+F 破局全过程、窗口布局恢复、OCR 错字对照表。遇到环境问题先查这里，别在已证伪路径上浪费时间。
