# 统一入口与兼容

## 名称与目录

| 原入口 | 现在从哪里进入 |
|---|---|
| wtt-code-animation-studio | wtt-code-video-studio：按内容选六类用途 |
| wtt-concept-explainer | wtt-code-video-studio：知识与原理；仍支持文字、图解、交互和视频 |

仓库只注册新入口，保留说明中的旧名帮助自然语言识别；不是同时安装三个Skill。当前源码变更不等于全局安装副本已更新。部署由用户另行授权，本轮没有运行更新脚本。

## 保留的接口

- `code-animation/v1`、素材/声音/视觉记录原schema保持不变。镜头、字幕、节奏及footage字段继续兼容。
- 自包含项目的 `tools/` 是创建时副本，不会自动升级。不批量改旧片，也不在旧项目重建素材锁。要迁移具体作品，先复制新版本工程，保留完整 .asset-review，再定向升级工具并核对。
- 公共素材审阅逻辑没有放宽：内容/来源/许可/导流变化必须diff，未经授权不得发布新版锁或验收。
- 两个旧声音配置位置只读兼容，私人模型和音色不移动、不打包。发现顺序与冲突处理见[声音指南](voice.md)。新项目明确需要某个旧默认时可用 `CODE_VIDEO_VOICE_CONFIG` 指向原文件。
- 概念图解的Klein蓝与产品发布式排布改为可选配方；不让所有故事套同一配色。概念方向确认与五方向选择合并；四帧审片是后续独立节点，已有风格选择不免除此门。

## 多人配音迁移

旧narration+voice和defaultVoice继续有效，voice仍是WAV文件路径。纯旧工程重编译时保持原timeline/字幕结构，不为新增角色能力强制改写旧片。旧timeline没有speech时，mix继续使用scene.voice。

新增同镜对白使用cast与scene.utterances；包含该字段的工程编译顶层speech及角色字幕。不要同时保留非空narration或scene.voice，也不要把scene.voice改填音色名。字段、互斥和句后停顿见[制作契约](production.md#角色与逐句话轮)。

自包含旧工程升级时，先复制新版本目录并保留完整.asset-review，再同步当前voice.py、pipeline.py及它们共同依赖的speech.py；使用新角色活动参数时同步runtime.js。导出/素材/四帧工具也按本次受影响范围成套核对，不能只拷voice.py却漏新依赖。也可直接调用完整新版Skill中的脚本并指向工程，不批量覆盖所有旧作品。

旁白继续用现有个人Base音色，角色需要固定声线及instruct时，在私人配置新增CustomVoice模型/voice条目；不更改defaultVoice，不移动或公开旧录音。两种权重不能以改ID互换。旧旁白已有文件可沿原记录使用；新TTS请求复用仍核对完整模型/参考/参数指纹。新话轮必须有其请求指纹或按外部音频规则明确核对，不能补写虚假情绪记录。

换角色、声音或表演时先生成候选，按素材diff审阅后重锁时/混音；视频按新实际版本四帧确认与完整验收，纯音频不套视频门。升级结构成功不等于人物听感或情绪效果通过，实际试音与技术记录分别报告。

## 合并来源

动画版提供公共项目、footage、节奏与素材门禁；概念版合入review-init/review、JPEG、舞台实际尺寸/MIME检查和混音尾部样本修正。asset_review.py原两份一致，保持同一实现。

原两个源码树在合并前完整冻结，清单记录逐文件SHA256；本机维护归档位于仓库 `archives/2026-11-03-code-video-unify-baseline/`，退役实际目录另存同次归档，SKILL入口改为 `.disabled`，不参与安装。公开版本历史由Git保留，归档不随安装包分发。

旧测试记录保留为历史，不能把原有成功记录说成本次生成结果。独立模型前后创作对照未运行，用户最终采用待确认。

## 四帧门迁移

新增纯音轨修订入口是`audio_revision.py`，依赖同版pipeline、voice、speech、asset_review、preview_review和footage；可直接从完整新版Skill调用，不必覆盖旧工程tools。新init自带工具和AUDIO-REVISION.md；其读原工程回执，不改旧工具/作品。规则见[纯音轨修订](audio-revision.md)。需要画面变化仍按下面四帧迁移，不能把后期入口当成通用免审开关。

旧项目tools是历史副本，不随Skill升级重写。继续使用旧工具不代表已通过新版流程；以新Skill维护旧片时，显式同步当前pipeline/render/preview_review及其素材工具，先保留旧回执与作品，再生成新四帧、展示确认，不能补写虚假旧批准。新init的QUALITY/PREVIEW是可独立阅读的短清单，不再复制含缺失相对链接的长方法。
