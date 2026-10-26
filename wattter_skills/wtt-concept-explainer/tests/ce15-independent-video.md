# CE-15 独立视频能力验证

## 实现与依赖边界

- 本技能拥有 pipeline.py / voice.py / asset_review.py / render.cjs，约88KB；模板约24KB。入口与参考均不要求读取另一 Skill。
- 一次性移植自有工具与对应行为测试，来源哈希见 [溯源](ce15-source-provenance.json)。未复制种子角色/画风库、历史评测系统或第三方包。
- 保留数据协议名称与含义，避免打断已有音色/素材格式。新增本技能配置优先级，原用户级音色路径仅作可选只读数据兼容。
- 外部共用 Python、Node、FFmpeg/FFprobe、Playwright/Chrome、MLX Audio、Qwen3-TTS 权重及默认个人音色资料。未复制模型、参考录音、用户配置或环境目录。
- 原 code animation 的四脚本、runtime、公开配置及声音依赖声明哈希仍与迁移前一致；原八字41.1秒成片保留，本次技术短片不替代它。

## 自动回归

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/wtt-concept-explainer/tests -p 'test_*.py' -v
node --check skills/wtt-concept-explainer/scripts/render.cjs
node --check skills/wtt-concept-explainer/assets/starter/runtime.js
node --check skills/wtt-concept-explainer/assets/starter/scenes.js
```

86项通过，见 [原始输出](ce15-unit-results.txt)。覆盖真实音频时长、不裁切、旧旁白/时间轴拒绝、素材变更/授权边界、模型校验、声音发现优先级、独立目录初始化等。测试中的合成假数据只用于负例/单元边界，不当成真实配音证据。

新测试首次两条失败：`AssertionError: PosixPath('/private/var/...') != PosixPath('/var/...')`。命令同上；原因是macOS临时目录别名，测试fixture改为resolve后86项通过。原始失败留在 [失败日志](../../../outputs/concept-independent-video/logs/unit-first-failure.txt)。未复制针对原 Skill 专属snapshot维护器的1项测试，未声称迁移了该维护器。

## 独立目录真实运行

[验证根目录](../../../outputs/concept-independent-video/) 中的 installed/ **只有** wtt-concept-explainer，无相邻 code animation。只从这个安装副本初始化，项目 tools 与本技能 scripts 的四份文件哈希一致，见 [独立性证据](../../../outputs/concept-independent-video/independence-check.json)。这证明本机独立工具调用链成立，不是操作系统级文件访问沙箱证明。

实际执行顺序：

```sh
python3 installed/wtt-concept-explainer/scripts/pipeline.py init project
python3 project/tools/pipeline.py tts project
# 填写实际声音素材及旁车清单
python3 project/tools/asset_review.py seal project
python3 project/tools/pipeline.py timeline project --lock
python3 project/tools/pipeline.py mix project
node project/tools/render.cjs project --preview
node project/tools/render.cjs project --render --frame-format jpeg
python3 project/tools/pipeline.py finish project
```

运行浏览器时 PLAYWRIGHT_MODULE 指向本机已有第三方包，未指向其他 Skill。TTS 使用本技能 voice.py 与用户已有外部模型/音色。该完整运行未使用外部音频豁免标记。

- [真实配音短片](../../../outputs/concept-independent-video/project/final.mp4)：6.700秒、201帧、1920×1080、30fps、H.264/AAC；2句已批准台词新合成。9个抽帧、5个乱序一致性样本通过，浏览器错误为空，完整解码无错误，峰值-1.5 dBFS。
- [默认模板技术片](../../../outputs/concept-independent-video/template-check/final.mp4)：0.500秒、12帧、640×360、24fps；原生模板与默认PNG路径成功。无旁白，仅作模板/编码验证，不能当配音成果。
- CSS以正确MIME实际加载；主动将舞台缩到100px时拒绝：`#stage 实际尺寸与时间轴不符；检查样式加载与缩放`；恢复后预览/编码通过。[预期拒绝日志](../../../outputs/concept-independent-video/logs/expected-stage-size-rejection.txt)保留。
- 已查看模板帧、旁白片关键帧及最终MP4第3秒截图，字组/日干焦点与字幕可读。自动delivery-check的visualReview仍为pending；本条是独立图像检查记录，不改写自动结果。未主观试听，不声称词级对齐、跨机器一致或用户采用。
- 辅助读取日志时发生一次 `cat: .../finish-jpeg.txt: No such file or directory`：后台浏览器尚未退出，finish未启动；等待原命令结束后自然产生成功日志，未重跑或伪造结果。

## 状态

本机独立配音、初始化、锁时、混音、两种编码输入、完整解码实际通过；结构检查、JS语法、Markdown相对链接与diff检查通过。未执行安装更新、提交、推送或公开发布。跨模型、Windows/Linux声音后端和主观音色质量未在本轮验收。
