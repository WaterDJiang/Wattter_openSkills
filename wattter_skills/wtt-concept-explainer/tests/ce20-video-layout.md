# CE-20：苹果风格15秒视频验证

- 用户本轮要求将新版排布用于附件特斯拉视频，随后限定15秒。沿用附件原三维模型和3句音频，在本仓库独立输出，不改原项目。
- 新增 video-layout 参考并接入主入口、叙事、视觉工艺与质量参考；不改变时间轴协议、素材校验、工具和starter帧接口。starter仍是功能示例，正式画面按新排布重做，不机械将示例节点图当成成品。
- 复用原模型时去掉网格地台、页眉、侧栏、常驻标签与横条；白底总览/储气、深底开阀特写；绝对帧驱动离地、外壳透明、开阀与气路。改用平滑容器法线，整车保留原简化几何。

## 实际结果

- [最终样片](../../../outputs/tesla-apple-15s/final.mp4)：1920×1080、30fps、450帧、15.000秒、H.264/AAC。
- `python3 tools/pipeline.py timeline . --lock`：450帧/15.000秒；混音沿用3句音轨，无变速无截句。
- `node tools/render.cjs . --preview` 与 `--render --frame-format jpeg`：实际渲染通过；5个乱序重绘一致，浏览器错误为空。使用现有Playwright模块和本机Chromium。
- `python3 tools/pipeline.py finish .`：音轨、峰值、时长/帧数、完整解码通过。
- 实际查看最终MP4的12张最小640宽首中尾/最长字幕画面，以及3个动作窗口每窗3张解码序列帧；无叠字、截字、主体字幕遮挡；深底容器左端为有目的裁切，阀门、路径和喷口完整；储气镜头有意静止供阅读。
- `python3 tools/pipeline.py review .`：实际填写的视觉记录完整并绑定当前文件；不代表自动美学判断。证据见[最终记录](../../../outputs/tesla-apple-15s/visual-review.json)及工程内quality-review/。
- 相关Markdown相对链接和`git diff --check`通过。未改工具行为，不重复运行与本次文档/排布无关的101项工具回归。

## 保留的失败与限制

- `apply_patch` 首次拒绝在同一补丁删除/新建index.html：`invalid patch: multiple operations target .../index.html`，改成原位更新后成功；未更改原作品。
- 沙箱执行预览返回`Error: listen EPERM: operation not permitted 127.0.0.1`；同一本地命令经权限审核后成功，没有修改浏览器或系统安全设置。
- 保存审阅记录脚本在工程目录重复使用`outputs/tesla-apple-15s`相对路径，触发`FileNotFoundError`；后续review拒绝`填写实际审阅者及查看方式，不能自动记为已审阅`。修正路径为当前目录、填写真实观察后重新校验通过。
- 渲染前实际查看首中尾/字幕/转场抽帧，未做渲染前正常速度连续片段播放；最终动作检查也仅为解码序列帧，不声称正常速度全片播放或主观试听。音频试听状态明确为not_checked，最终用户采用pending。
- 本片验证排布与基本三维动作，不声称达到生成方向图的写实车辆材质。未部署全局技能、未提交、未公开发布。
