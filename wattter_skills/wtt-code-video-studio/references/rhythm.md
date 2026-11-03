## 节拍与动作事件（可选）

没有 rhythm / loop 的旧 film.json 保持原输出字段与时间语义。新增字段只编译节奏和审查信息，不选择画风、不改变旁白、不自动生成动作。修改这些代码/节奏配置需重锁时间轴和渲染；素材未变不重复确认。

```json
{
  "rhythm": {
    "bpm": 120,
    "offsetSeconds": 0,
    "beatsPerBar": 4,
    "basis": "用户提供的 120 BPM；已核对首重拍位于全片 0 秒",
    "audioFile": "audio/music.wav",
    "events": [
      {"id": "press", "beat": 2, "action": "光标按下按钮", "sceneId": "opening"},
      {"id": "expand", "beat": 4, "action": "同一容器展开为结果面板"}
    ]
  },
  "audioTracks": [
    {"file": "audio/music.wav", "startSeconds": 0, "gain": 0.15},
    {"file": "audio/click.wav", "startBeat": 2, "gain": 0.4}
  ],
  "loop": false
}
```

这是 film.json 的可选片段，仍须有完整的 schema、画幅和 scenes；示例事件必须落在实际片长及 opening 镜头内。文件先登记资产并 seal，按原 timeline --lock → mix → preview → render → finish 流程执行。

- 拍号从 0 开始。BPM 每个拍点从绝对时间单独量化到最近整数帧（半帧向上），不累计已舍入拍长。offsetSeconds 是**全片时间**，已包含音乐进入点；不额外加 audioTracks.startSeconds。
- 变速/人工核对网格用 `"beatTimesSeconds": [0.15, 0.66, 1.18, 1.71]` 替代 bpm 和 offsetSeconds，不允许两种来源同时填写。时间点严格递增且落在 [0,totalFrames) 内，不允许不同拍点落到同一帧。
- rhythm.basis 必填，说明用户提供/人工设计/分析后核对；不提供自动音频测拍或正确性认证。与实际音乐关联时填 audioFile，必须引用 audioTracks 内素材，受原哈希与审阅约束。无配乐的设计节奏可省略 audioFile。
- events 为关键动作提示，不是动作引擎。id 唯一，action 必填；可填 sceneId 检查事件是否仍在指定镜头。生成代码读取 `timeline.rhythm.events` 的 frame，不能另造一套舍入规则。
- 音轨 startBeat 与 startSeconds 互斥；编译器把 startBeat 转为同一拍点帧对应的 startSeconds，再按现有混音器定位。需要细分拍时提供更细的时间点网格；当前事件不接受小数拍号。
- 拍点越界、非法输入、音效超片尾均报错，不自动截断音乐或旁白。BPM 自动网格只生成片内拍点；引用片外 beat 会失败。更改镜头后复核事件与音乐关系。
- rhythm/loop 均写入 timeline 并由 filmSha256/时间轴过期检查约束。init 的工具副本需要同步升级 pipeline.py 和 render.cjs；原 asset_review.py、voice.py 保留在同目录。

预览继续包含每镜首中尾与字幕中点，额外抽取最多 64 个均匀覆盖全片的拍点，以及**每个**事件前/当/后帧。报告 `previewCoverage` 列出实际帧、总拍数/抽样拍数，长片不能冒称看完每拍；`preview/index.html` 汇总本次抽帧，旧 PNG 不列入本次索引。

`loop: true` 额外抽取片头/片尾连续三帧，并标 `sampled-needs-motion-and-audio-review`。不改变播放方式或导出长度，不调用区间外的第 N 帧，也不自动认定无缝；按制作类型说明人工检查接缝。

`previewPerformance` 保存实际截图调用数与耗时，以及全片截图成本粗估；其范围不含浏览器启动、完整编码与混音。它不是硬性时限或性能保证，shader、多重曝光等改动后必须重新测量。




四帧确认与最终编码验收沿[制作契约](production.md)和[四帧审阅](preview-review.md)，事件抽样不代替用户确认。
