# 公开配音回归

本次公开测试覆盖多人声音、逐句表演请求、稳定seed与缓存、实际音长编排、角色字幕、活动角色状态和四帧审阅源绑定。

在Skill目录运行：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/catalog.py check
node --check scripts/render.cjs
node --check assets/starter/runtime.js
node --check assets/handpainted-cinema/tools/render_handpainted.cjs
```

需要Python3、FFmpeg/FFprobe和Node。声音模型调用在单元测试中使用替身，不下载权重、不读取用户私人声音配置；临时WAV在测试目录中生成。Node负责角色状态行为检查，FFmpeg负责合成轨与实际混音检查。

[固定四话轮输入](fixtures/voice-cast-01/film.json)可供另做本地试音；[模型与配音说明](../references/voice.md)解释实际依赖。公开包不附发布者的私人录音、配置、模型、音频样本或原始制作日志。真实克隆相似度、台词完整度和情绪自然度由实际试音判断；通过测试不代表主观听感通过。
