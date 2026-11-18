// The shared world is sampled once per absolute frame, including the incoming blend.
const shotModules = new Map();
window.prepareScenes = async timeline => {
  let previous;
  const origin = timeline.scenes[0].worldStartFrame ?? 0;
  for (const scene of timeline.scenes) {
    const module = await import('./code/' + scene.id + '.js');
    if (typeof module.draw !== 'function') throw Error(scene.id + ' 缺少 draw(ctx, state)');
    if (scene.worldStartFrame !== undefined &&
        (!Number.isSafeInteger(scene.worldStartFrame) || scene.worldStartFrame < 0 ||
         scene.worldStartFrame !== origin + scene.startFrame)) {
      throw Error(scene.id + ' 共享时钟起点与实际时间轴不符，请按锁时结果校准');
    }
    const bridge = scene.transitionIn;
    if (bridge && (bridge.from !== previous?.id || !previous ||
        !Number.isSafeInteger(bridge.frames) || bridge.frames < 2 || bridge.frames > scene.durationFrames ||
        typeof module.drawTransition !== 'function' || typeof module.sampleWorld !== 'function' ||
        module.sampleWorld !== shotModules.get(previous.id).sampleWorld)) {
      throw Error(scene.id + ' 接镜需要相邻来源、片内过渡窗口、同一 sampleWorld 和 drawTransition');
    }
    if (module.prepare) await module.prepare(scene, timeline);
    shotModules.set(scene.id, module);
    previous = scene;
  }
};
window.drawScene = (ctx, state) => {
  const module = shotModules.get(state.scene.id);
  if (!module.sampleWorld) return module.draw(ctx, state);
  const frame = state.frame + (state.timeline.scenes[0].worldStartFrame ?? 0);
  const world = module.sampleWorld(frame, state.timeline.fps);
  const bridge = state.scene.transitionIn;
  if (bridge && state.localFrame < bridge.frames) {
    const t = state.localFrame / (bridge.frames - 1);
    const mix = t * t * (3 - 2 * t);
    return module.drawTransition(ctx, {...state, world, mix});
  }
  return module.draw(ctx, {...state, world});
};
