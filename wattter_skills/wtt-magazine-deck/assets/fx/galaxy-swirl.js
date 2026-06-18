/* 银河旋涡 — 三臂螺旋粒子，适合宇宙/宏观叙事页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['galaxy-swirl'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const pal = U.palette(el);
    const N = 800;
    const parts = [];
    for (let i = 0; i < N; i++){
      const arm = i % 3;
      const tt = Math.random();
      const r = tt*180 + 8;
      const base = (arm/3)*Math.PI*2;
      parts.push({
        r: r, a: base + Math.log(r+1)*1.6 + U.rand(-0.2,0.2),
        c: pal[arm%pal.length],
        s: U.rand(0.8, 2.2)
      });
    }
    const stop = U.loop(function(t) {
      ctx.fillStyle = 'rgba(0,0,0,0.15)';
      ctx.fillRect(0, 0, k.w, k.h);
      const cx = k.w/2, cy = k.h/2;
      for (let i = 0; i < parts.length; i++){
        const p = parts[i];
        const a = p.a + t*0.15;
        const x = cx + Math.cos(a)*p.r;
        const y = cy + Math.sin(a)*p.r*0.7;
        ctx.fillStyle = p.c;
        ctx.globalAlpha = 0.7;
        ctx.beginPath(); ctx.arc(x, y, p.s, 0, Math.PI*2); ctx.fill();
      }
      ctx.globalAlpha = 1;
    });
    return { stop: function(){ stop(); k.destroy(); } };
  };
})();
