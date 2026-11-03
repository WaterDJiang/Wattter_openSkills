# 季节地图代码模板

同一微缩世界在一支片内连续换角度：俯视→左斜俯视→右斜俯视→回俯视。示例 `config.json` 采用孟菲斯色板、20秒、1080方形、60fps、1200帧和颗粒开合；`make(canvas,{})` 的兼容默认仍是 vivid / 30fps / 600帧 / 连续展示。真实地点先按[季节地图](../../references/seasonal-map.md)研究，不给示意小镇换个名字就称真实城市。

- `map.js`：统一 `make(canvas,config)/frame(i)`；从 `fps × durationSeconds` 得到整数总帧数。
- `world.js`：自写乡村/城市几何、高度投影、连续相机和两个有帧时码的微事件；Memphis 实际绘制深靛轮廓、硬投影及点/条/折线图案。
- `presentation.js`：同世界相机、面排序、vivid / soft / memphis 及四季功能色；色值见[美术与相机](../../references/map-art-direction.md)。
- `legacy-scroll.js`：显式 `scroll-top-down` 保留1440高世界和0.55云视差；同样从配置读取帧率与周期。
- `index.html`：浏览器播放/暂停/选帧和 `window.renderFrame(i)` 共用确定性画法，`__filmMeta` 提供真实帧率和总帧数。
- `export.cjs`：默认只出四张样帧、2×2拼图和检查。完整导出必须消费同目录已确认的冻结快照；拒绝覆盖。

## 按地点和内容配色

config中的七色只是示例，允许同色系、邻近色、对比色或低饱和。模型结合当地地貌/水色/建筑、季节与氛围，在brief记录依据，再写paletteOverrides；不需要新建palette:auto或增加配色选择。功能键与同色系示例见[地图美术](../../references/map-art-direction.md#先按地图与内容定色)。ground覆写主体地面，ink同步影响轮廓/硬影/图案；数组槽位可用相近色或重复色。配置固定后确定性绘制，四帧确认后冻结；改色需新预览。

## 先看四帧，再导出

在模板副本内安装固定依赖；已有安装可设 `CANVAS_MODULE`。复制模板到外部工程时，同时复制 Skill 的 `scripts/preview_review.py`，或通过 `PREVIEW_REVIEW_TOOL` 指向该共用门禁。完整 Skill 内运行无需额外设置。

```sh
npm init -y
npm install --save-exact canvas@3.2.0
node export.cjs --out ./preview-v001
```

查看 `preview-v001/.preview-review/versions/v0001/contact-sheet.png`。默认样帧来自3.0、7.6、12.8、17.2秒；可用 `--review-frames 180,456,768,1032` 明确指定四个代表帧。代理需展示实际拼图并等待用户对该版本明确确认；普通“继续”、风格选择、技术检查通过均不算批准。

只在取得明确确认后，由代理记录用户原话：

```sh
python3 ./preview-v001/preview_review.py approve ./preview-v001 --version v0001 --message '用户对当前拼图的明确确认原话'
node export.cjs --out ./preview-v001 --render-approved
```

后一句才逐帧输出 `frames/frame-0000.png` 至 `frame-1199.png`。批准绑定绘图源码、配置、样帧与拼图；修改后须生成新的候选预览。相同批准快照可复用；已有帧目录不可覆盖。

## 配乐与合成

`sound-events.json` 与画面同源：6.7秒车辆让行/脚步、12.8秒鸟掠过/鸟鸣。下例为原创五声音阶与合成风声，非当地实录；正式地点声音仍按[地点声音](../../references/location-sound.md)研究和审阅。

```sh
python3 /实际Skill路径/scripts/map_music.py ./preview-v001/music.wav --style pentatonic --seconds 20 --events ./preview-v001/sound-events.json
ffmpeg -n -framerate 60 -start_number 0 -i ./preview-v001/frames/frame-%04d.png -i ./preview-v001/music.wav -frames:v 1200 -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart ./preview-v001/final.mp4
python3 /实际Skill路径/scripts/check_loop.py ./preview-v001/final.mp4 --frames 1200 --fps 60 --out ./preview-v001/encoded-loop.json
```

修改配置时同步使用实际 `fps/frames/durationSeconds`，不要把600张帧标成60fps。Node逐帧已配套；需要无头Chrome时沿用通用逐帧渲染器、读取 `__filmMeta` 并遵守同一审片门。浏览器可从副本目录运行 `python3 -m http.server 8765 --bind 127.0.0.1` 后打开 `index.html`。

`--check-only` 同样只生成四帧和报告。`seam-check.json.passed` 只表示确定性/接缝/相机/非空检查通过；不能替代用户确认、最终MP4验收与声音试听。经纬度没有真实地理映射时保持固定或明确留空，不随相机编造数字。旧作品不自动升级，素材变更仍走候选/diff/确认机制。
