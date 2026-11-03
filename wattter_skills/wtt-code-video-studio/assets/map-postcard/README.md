# 季节地图代码模板

配方与完整命令见[地图指南](../../references/seasonal-map.md)。

- map.js：浏览器和node-canvas共用frame(i)；季节、地点、乡村/城市从config读取。
- index.html：滑杆精确选帧，控制台play()播放；通过本地HTTP服务器打开。
- export.cjs：新目录导出600张PNG、接缝报告和预览；--check-only只校验与抽帧。
- config.json：示例参数，正式地名/坐标需核对；reveal:false保留字幕但取消开合遮罩。
- presentation.js：可供新场景显式调用的鲜明/柔和配色、俯视/等距/多角度周期相机、真实高度投影与面排序小组件。原map.js/index.html/export.cjs仍是2D俯视示例，不会自动读取或应用它；新地标按片重画。调用和验收见[地图美术与相机](../../references/map-art-direction.md)。
- 正式地点的声音先按[地点声音选材](../../references/location-sound.md)研究，可复制sound-plan.example.json填写；它不是已选曲目或另一套素材锁。大城市/小众地区均按地方线索匹配，外地录音明确标作氛围素材。
- scripts/map_music.py仅提供八音盒/8bit原创示范和兜底，不能替代地方选材；编码后接缝使用scripts/check_loop.py，音乐接缝另需实际试听。禁止覆盖旧素材或验收报告，已有项目素材变更进入候选审阅。

代码原创，不包含用户附件媒体。node-canvas为外部依赖，固定版本安装；模型/音色不用下载，配乐不克隆声音。
