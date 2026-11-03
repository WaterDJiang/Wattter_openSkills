/* Optional frame sequences: bounded decoded-image cache, no autonomous video playback. */
window.openFootage = async (timeline, limit = 24) => {
  if (!timeline.footageManifest) return null;
  if (!Number.isInteger(limit) || limit < 1) throw Error('视频缓存上限须为正整数');
  const response = await fetch(timeline.footageManifest);
  if (!response.ok) throw Error(`视频清单读取失败: ${response.status}`);
  const data = await response.json();
  if (data.schema !== 'code-animation-footage/v1' || data.fps !== timeline.fps) throw Error('视频清单协议/帧率不符');
  const clips = new Map(data.clips.map(clip => [clip.id, clip]));
  if (clips.size !== data.clips.length) throw Error('视频片段 ID 重复');
  const cache = new Map();
  return {
    async image(id, frame) {
      const clip = clips.get(id);
      if (!clip) throw Error(`未知视频片段: ${id}`);
      const index = frame - clip.startFrame;
      if (!Number.isInteger(frame) || index < 0 || index >= clip.durationFrames) throw Error(`视频帧越界: ${id}/${frame}`);
      const path = clip.frames[index]?.path;
      if (!path || path.startsWith('/') || path.includes('..') || path.includes(':') || path.startsWith('.')) throw Error('无效视频帧路径');
      if (cache.has(path)) {
        const item = cache.get(path); cache.delete(path); cache.set(path,item);
        return item;
      }
      const promise = new Promise((resolve,reject) => {
        const img = new Image();
        img.onload = () => img.decode().then(() => resolve(img),reject);
        img.onerror = () => reject(Error(`视频帧缺失或解码失败: ${path}`));
        img.src = path;
      });
      cache.set(path,promise);
      while(cache.size > limit) cache.delete(cache.keys().next().value);
      try { return await promise; }
      catch(error) { cache.delete(path); throw error; }
    },
    clear() { cache.clear(); }
  };
};
