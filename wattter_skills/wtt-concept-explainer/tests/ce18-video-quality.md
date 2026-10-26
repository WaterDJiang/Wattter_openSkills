# CE-18 视频质量约束与工具验证

## 改动及依据

- 用户对CE-17癸水V2明确反馈“效果好很多”，要求把约束内置Skill。复用其字号、主体动作、逐项聚焦、缩小画面和最终编码检查方法；不固定庭院风格、镜头数或特效类型。
- 主入口、视频叙事/工艺/制作参考统一指向[质量约束](../references/video-quality.md)。starter默认横版64px字幕，其他尺寸按实际播放位换算；最多两行，超限报错不缩字。
- 独立pipeline新增review-init/review；新工程带QUALITY.md。自动抽最终MP4原尺寸/缩小图及正常速度2秒动作窗口，生成pending记录；检查各大镜覆盖、首中尾/字幕帧、动作窗口、最终文件与证据指纹。视觉内容仍由真实审阅判断。
- 不改变既有协议或finish技术校验，不覆写旧工程；无需新依赖或其他Skill。

## 真实运行

[验证目录](../../../outputs/concept-quality-check/)保留命令日志、浏览器证据、最终文件与回执。

- 新工程init→锁素材→锁时→mix→render→finish→review-init→实际图像检查→review运行成功。
- [技术短片](../../../outputs/concept-quality-check/project/final.mp4)：5秒、150帧、1080p/30fps、H.264/AAC，旁白复用已批准g03-01，不新生成TTS。仅验证管线、字幕和三项包含关系，不能替代复杂创作质量评测。
- 自动生成12张图片（4个帧×原尺寸/640/960宽）及1个正常速度2秒片段；待审记录实测被review拒绝。
- 查看640首中尾/字幕图、960字幕图，以及片段4fps抽样8帧。填写真实观察后review成功；[视觉回执](../../../outputs/concept-quality-check/project/visual-review-check.json)保持audioReview=not_checked、userAcceptance=pending。未冒称主观试听或全片主观播放。

## 自动回归

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/wtt-concept-explainer/tests -p 'test_*.py' -v
PLAYWRIGHT_MODULE=/path/to/playwright node skills/wtt-concept-explainer/tests/check-video-quality.cjs outputs/concept-quality-check/project outputs/concept-quality-check/caption-tests
```

- 101项Python测试通过，[日志](../../../outputs/concept-quality-check/logs/unit-final.log)。新增14项覆盖分句合并、动作起点越界、待审/失败、过期成片、证据变动/缺失、遗漏大镜、静态图冒充动作、大图冒充缩小检查、遗漏首尾/字幕帧、已有记录保护和旧成功回执清除。
- 1920×1080、1280×720、1080×1920实际浏览器字幕换行/安全区通过；相同3种画幅的超长字幕均被拒绝，[结果](../../../outputs/concept-quality-check/caption-tests/caption-check.json)。这些是字幕测试，不是整套竖版构图已验收。
- 首轮浏览器测试给竖版也用32字正例，实际需要三行，触发`Error: 字幕溢出`；保留[原始失败](../../../outputs/concept-quality-check/logs/caption-tests-first-failure.log)。修改为竖版24字正例后通过；未放宽字号或两行阈值。
- 标题与标签也取消Canvas maxWidth隐式挤压，三种画幅均验证正常文案及超长拒绝。首轮暴露竖版模板辅助提示过长，改成短提示后通过；[失败日志](../../../outputs/concept-quality-check/logs/template-first-failure.log)保留，没有动态缩小字号。
- quick_validate、JS语法、Markdown本地链接与git diff --check通过。未验证跨模型和其他操作系统。

## 状态

工作区实现与本机真实工具链验证完成；未执行安装同步、提交或发布。技术记录完整不等于算法能自动判断美感；每次仍须查看真实成片证据。
