# 手绘电影V2原创源码示例

来自本库最后《晚风来信》V2的实际绘图源码：固定seed的形体笔触、暗前景/亮远林、衣料明暗、接地步态和手腕/道具共享状态。这里是**12秒完整工程示例**，正式内容仍按剧本、动作与真实配音定时，不固定12秒，不把每个主题都改成林间信使。

## 在新目录创建

从实际Skill目录执行：

```sh
python3 scripts/handpainted.py /path/to/new-handpainted-project
```

目录必须尚不存在。脚手架复用公共pipeline.init与声音doctor，然后复制完整绘图/示例配置/工具及源码指纹；不下载依赖、不生成音频、不锁素材、不自动审阅通过。旧工程不能用此命令覆盖。私人音色、模型、原参考视频、缓存或旧成片均不打包。

在新工程安装固定版本，保存你生成的package-lock.json：

```sh
npm install --save-exact canvas@3.2.0
python3 -m pip install numpy==1.26.2
node tools/keyframes.cjs art-v001
node tools/check_pose.cjs
```

也可以设置CANVAS_MODULE为已安装canvas模块的位置。示例不携带本机file:路径的npm锁或node_modules。Node/Canvas/字体版本不同不保证跨机器像素一致；本机乱序确定性必须一致。

## 先美术，再动作

keyframes在新art目录输出代表帧、像素SHA及全部绘图源码SHA；已有素材锁时先执行公共素材校验，拒绝覆盖预览目录。图片需要实际查看：原画幅和640宽对照主体/受光/笔触/景层/焦点。检查森林是否成为重复圆团、树根是否接地、角色是否过扁；代表帧不通过就先改画面。

可用下列命令输出本例4–8秒的640宽无声动作样片（帧窗口按新剧本调整）：

```sh
node tools/motion_preview.cjs 120 120 motion-v001
```

复杂动作另做短小样，检查脚的接地阶段、预备—动作—跟随—停留、道具附着与释放后的轨迹、前景是否遮掉动作。脚手架不会自动给美术或动作打分。示例check_pose只校验本信使的坐标/手腕/185帧离手规则，不是其他角色的通用验证器。

## 复现这个带声音的示例

仅当你确实要复现此无对白示例时，在新工程执行：

```sh
python3 tools/compose.py
python3 tools/asset_review.py seal .
python3 tools/pipeline.py timeline . --lock
python3 tools/pipeline.py mix .
node tools/render_handpainted.cjs . --preview
node tools/render_handpainted.cjs . --render
python3 tools/pipeline.py finish .
python3 tools/pipeline.py review-init .
```

compose只允许新工程首次生成原创配乐/动作音：有锁、已有素材记录或同名音频时拒绝，不覆盖当前素材。更换声音沿ASSETS.md候选/diff/确认，不能再次compose或seal绕过审阅。无对白仅是本例；正式剧本需要旁白且已有defaultVoice时，默认使用配置音色，按实际音频重新锁时，不能默认删去旁白。

render执行前/后校验素材锁和源码，验证时间轴与画面帧数一致，乱序取帧，再输出PNG/H264与实际报告；输出目录存在则拒绝覆盖。finish/review-init沿公共验收；实际查看最终缩小图/动作后再填写visual-review.json并运行pipeline.py review。技术、视觉、声音试听、用户采用分别记录。

## 文件与适配

- forest.js：V2原样绘画背景，局部受光团簇、纵向树干/横向水纹、低对比远林、前景树和蕨草；先画形体与明暗，纹理只在所属对象内生成。
- courier.js：V2原创信使、步态、脸/帽子/衣褶/皮包、手腕和纸鸟。新人物替换此模块并保持自身关节/道具契约。
- scene.js：画层组合、相机/焦点/次级动作与片名。本例12秒/1920×1080/30fps；改变故事、时长或画幅须一起改scene与动作/布局及film.json，不能只改总帧数或ffmpeg时长。
- film.example.json：示例六段动作，不是正式剧本默认答案。脚手架将其复制为film.json，不包含旧素材锁回执。
- tools：静帧、动作窗口、姿态检查、示例音乐及接入公共pipeline的渲染器。render-report.json验证全部绘图依赖，不能遗漏forest/courier。
- index.html：完成混音后通过本地HTTP打开，可播放/暂停/选帧；play.html播放最终MP4。文字/字段仍按本片重新排版。
- provenance.json：自有V2绘图源码哈希与来源范围，不包含参考媒体或私有音色。

当前可用基线为V2纯Canvas工艺，人物/树冠仍有几何感；不能宣称原参考同等级画质，也不能凭本例证明p5.js/Three.js路线。颜色、角色、道具、镜头与时长按新内容设计。完整配方见Skill的references/handpainted-cinema.md；该路径在安装包内，新工程另保留ASSETS/QUALITY/VOICE说明。
