# CE-16 癸水2027跨技能成片验证

- 用户要求八字技能＋思辨写作产出文章，再由本技能制作视频；先完成文章/旁白/四镜样图，用户明确回复“确认”后制作。
- [文章](../../../outputs/gui-water-2027/article.md)、[批准分镜](../../../outputs/gui-water-2027/storyboard.md)、[实际成片](../../../outputs/gui-water-2027/video/final.mp4)、[完整检查记录](../../../outputs/gui-water-2027/video/review.md)。
- 无出生资料，八字走术语问答；不伪造个人命盘。年历及藏干另作显式来源核验，发现安装知识卡错误并隔离，见[内容证据](../../../outputs/gui-water-2027/evidence/verification.md)。
- 本技能四个工具独立运行；背景用内置imagegen，模型/音色/运行时共用现有外部安装。[工具哈希与原文核对](../../../outputs/gui-water-2027/video/content-and-independence-check.json)。
- 171.733秒、5152帧、1920×1080/30fps、H.264/AAC；150预览样本、5个乱序一致性样本、空浏览器错误；完整解码通过，峰值-1.6dBFS。[技术报告](../../../outputs/gui-water-2027/video/delivery-check.json)与[画面复核](../../../outputs/gui-water-2027/video/final-review/visual-review.json)分开。

## 本次真实修复

长片首次finish拒绝“音画时长不闭合”：混音少3200采样，约67ms。仅在loudnorm后添加apad/atrim仍未修复。最终在归一化与重采样后重置PTS，以时间轴总帧数折算整数采样数补齐/限定，移除重复的输出-t限制；不放宽交付阈值，不改旁白或素材锁。

新增 [test_mix_duration.py](test_mix_duration.py) 使用真实FFmpeg，覆盖82、201、5152帧，断言音频采样误差不超过1采样且尾部测试音保留。全套87项通过，[真实日志](../../../outputs/gui-water-2027/video/logs/unit-final.log)。失败版本及第一轮失败测试保留在产物目录。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/wtt-concept-explainer/tests -p 'test_*.py' -v
git diff --check
```

状态：本机实际成片与技术/画面验证完成；未主观试听发音、未做词级强制对齐，用户成片观感及跨模型/跨系统未验证。未安装、提交、推送或发布。历史工程未自动更新。
