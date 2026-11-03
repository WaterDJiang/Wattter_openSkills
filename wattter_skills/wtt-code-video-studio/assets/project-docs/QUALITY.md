# 本工程质量与验收

本说明可独立阅读。四帧用户决定见[PREVIEW.md](PREVIEW.md)，素材版本见[ASSETS.md](ASSETS.md)，音色配置见[VOICE.md](VOICE.md)，视频接入见[FOOTAGE.md](FOOTAGE.md)。完整风格制作方法留在来源Skill的对应reference；本工程不假装已经复制它们。

## 完整渲染前

- 先以当前代码查看代表帧、必要动作与转场，检查主体、标签、字幕避让及关键材质。需要运动来讲清的内容，不能只看静帧。
- 按剧本选四个不同的真实帧，生成带帧号/时码的2×2拼图，实际展示给用户并等待对该版本的明确确认。方向选择或自动检查不是批准。
- 横版默认查看640/960宽、竖版360/640宽。屏幕等效字号=输出字号×播放宽度/输出宽度；字幕约20px、核心标签约22px、必要次级标签约16px为设计起点。按播放位调整须说明依据，不能因为内容多直接缩字。
- 当前讲述信息对实际背景至少4.5:1，字幕最多两行并留安全区。辅助字可更小，关键条件不能藏在小字。
- 遵循本片已选风格和可见动作，不将产品/机械配方强加给所有故事。单片近似成功不证明整个风格或后端通用。

## 最终MP4

```sh
python3 tools/pipeline.py finish .
python3 tools/pipeline.py review-init .
# 实际查看quality-review内的图/片段，填写visual-review.json，再执行：
python3 tools/pipeline.py review .
```

finish检查素材、四帧批准、源码/时间轴/混音/渲染绑定、尺寸/fps/帧数、H.264/AAC和完整解码；技术通过不是画面或听感通过。最终编码后仍看每个视觉大镜的首中尾/字幕帧、关键动作和转场；不能拿浏览器预览替代真实成片。

visual-review.json记录实际审阅者/查看方式、readability/motion/focus/transitions/encoded具体观察及证据ID；待审/失败/缺证据不得写通过。连续大镜可用director.group合并，director.reviewAtSeconds指定动作起点；自动动作窗最多2秒，长过程另补真实证据。能正常播放并试听就优先使用，只看帧序列时如实注明。

review只核对记录完整性与当前文件绑定，不自动判断美感。audioReview单独记录主观试听，userAcceptance只有用户明确反馈才改变；技术检查、画面观察、听感和用户采用分别报告。

修改源码/声音/素材后重验受影响画面与转场。保留旧视觉记录后再review-init，不手写新哈希冒用旧通过。四帧批准和最终审阅都是针对版本的记录，互不替代。
