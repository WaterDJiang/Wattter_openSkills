# 季节地图代码模板

新项目默认采用本库兰州V2的鲜明粉彩与**单片内换视角**，连续循环：俯视→左斜俯视→右斜俯视→回俯视。20秒/1080方形/30fps。完整制作见[季节地图](../../references/seasonal-map.md)，色值/时间段见[地图美术与相机](../../references/map-art-direction.md)。

- map.js：统一make(canvas,config)/frame(i)入口，解析实际生效的viewProfile、palette、paletteOverrides与reveal。
- world.js：原创乡村/城市示意几何，按高度投影建筑、树、桥、交通和风车；通用示意不代表真实地点。
- presentation.js：同世界相机、真实高度投影、面排序、功能色与四季色板；默认multi-angle/vivid。
- legacy-scroll.js：显式scroll-top-down保留旧向下滚动、1440世界与0.55云视差。
- index.html：真实加载全部依赖，播放/暂停/选帧共用frame(i)，加载错误可见。通过本地HTTP服务打开。
- export.cjs：新目录导出600张PNG，快照全部绘图依赖/HTML/config与SHA256；--check-only仅作像素、相机、周期检查及8张关键帧＋未遮罩首帧。拒绝覆盖。
- config.json：默认示例小镇、multi-angle/vivid/reveal:false；真实地名/坐标须核对。固定top-down/isometric、柔和soft、开合reveal:true可显式配置，不新增开场选择题。

```sh
npm init -y
npm install --save-exact canvas@3.2.0
node export.cjs --out ./check-v001 --check-only
node export.cjs --out ./render-v001
python3 -m http.server 8765 --bind 127.0.0.1
```

已有安装可通过CANVAS_MODULE定位，不写本机硬编码。修改正式地点需先研究地图/地标、改原创构图/几何；不是改地名就有真实地图。模型与个人音色无需为无对白示范下载。

正式音乐/环境声按[地点声音](../../references/location-sound.md)研究并填写sound-plan.example.json，不把公开可听当作可用许可。map_music.py仅原创示范/兜底；素材锁变化沿原候选/diff/确认流程。编码与验收命令见季节地图指南；旧工程各自保留代码，不自动升级或替换音频。
