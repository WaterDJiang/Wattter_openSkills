/* 渐变光球 — 4 个模糊光球叠加漂移，适合 light hero 页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['gradient-blob'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    function hexToRgb(hex){
      const m = hex.match(/^#?([\da-f]{2})([\da-f]{2})([\da-f]{2})$/i);
      return m ? [parseInt(m[1],16),parseInt(m[2],16),parseInt(m[3],16)] : [240,230,210];
    }
    const pal = U.palette(el);
    const c1 = hexToRgb(pal[0]);
    const c2 = hexToRgb(pal[1]);
    const c3 = hexToRgb(U.ink(el));
    const c4 = hexToRgb(U.paper(el));
    const blobs = [
      { cx:0.3, cy:0.3, r:0.35, phase:0, speed:0.15, color: c1 },
      { cx:0.7, cy:0.4, r:0.30, phase:2, speed:0.12, color: c2 },
      { cx:0.5, cy:0.7, r:0.28, phase:4, speed:0.18, color: c3 },
      { cx:0.2, cy:0.6, r:0.25, phase:1, speed:0.10, color: c4 }
    ];
    const stop = U.loop((t) => {
      const cw = k.w, ch = k.h;
      ctx.clearRect(0, 0, cw, ch);
      ctx.globalCompositeOperation = 'lighter';
      blobs.forEach(b => {
        const x = (b.cx + Math.sin(t * b.speed + b.phase) * 0.15) * cw;
        const y = (b.cy + Math.cos(t * b.speed * 0.8 + b.phase) * 0.12) * ch;
        const r = b.r * Math.min(cw, ch);
        const grad = ctx.createRadialGradient(x, y, 0, x, y, r);
        grad.addColorStop(0, 'rgba(' + b.color[0] + ',' + b.color[1] + ',' + b.color[2] + ',0.08)');
        grad.addColorStop(0.5, 'rgba(' + b.color[0] + ',' + b.color[1] + ',' + b.color[2] + ',0.03)');
        grad.addColorStop(1, 'rgba(' + b.color[0] + ',' + b.color[1] + ',' + b.color[2] + ',0)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, cw, ch);
      });
      ctx.globalCompositeOperation = 'source-over';
    });
    return { stop(){ stop(); k.destroy(); } };
  };
})();
