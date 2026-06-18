/* FX 公共工具 */
(function(){
  window.HPX = window.HPX || {};
  const U = {};

  U.css = function(el, name, fb) {
    return getComputedStyle(el).getPropertyValue(name).trim() || fb;
  };
  U.accent = function(el, fb) {
    return U.css(el, '--accent', fb || '#7c5cff');
  };
  U.accent2 = function(el, fb) {
    return U.css(el, '--accent-2', fb || '#22d3ee');
  };
  U.text = function(el, fb) {
    return U.css(el, '--text-1', fb || '#eaeaf2');
  };
  U.paper = function(el) {
    return U.css(el, '--paper', '#f1efea');
  };
  U.ink = function(el) {
    return U.css(el, '--ink', '#0a0a0b');
  };
  U.palette = function(el) {
    return [
      U.accent(el, '#7c5cff'),
      U.accent2(el, '#22d3ee'),
      U.css(el, '--ok', '#22c55e'),
      U.css(el, '--warn', '#f59e0b'),
      U.css(el, '--danger', '#ef4444')
    ];
  };

  U.canvas = function(el) {
    if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
    const c = document.createElement('canvas');
    c.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;display:block;z-index:0';
    el.appendChild(c);
    const ctx = c.getContext('2d');
    let w = 0, h = 0, dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    const fit = function() {
      var r = el.getBoundingClientRect();
      w = Math.max(1, r.width | 0);
      h = Math.max(1, r.height | 0);
      c.width = (w * dpr) | 0;
      c.height = (h * dpr) | 0;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    fit();
    var ro = new ResizeObserver(fit);
    ro.observe(el);
    return {
      c: c, ctx: ctx,
      get w() { return w; },
      get h() { return h; },
      get dpr() { return dpr; },
      destroy: function() {
        try { ro.disconnect(); } catch(e) {}
        if (c.parentNode) c.parentNode.removeChild(c);
      }
    };
  };

  U.loop = function(fn) {
    var raf = 0, stopped = false, t0 = performance.now();
    var tick = function(t) {
      if (stopped) return;
      fn((t - t0) / 1000);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return function stop() {
      stopped = true;
      cancelAnimationFrame(raf);
    };
  };

  U.rand = function(a, b) { return a + Math.random() * (b - a); };

  window.HPX._u = U;
})();
