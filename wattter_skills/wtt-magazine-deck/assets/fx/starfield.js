/* 星空穿梭 — 从中心向外扩散的星点，适合宇宙/科技页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['starfield'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const tx = U.text(el, '#ffffff');
    const N = 260;
    const stars = [];
    for (let i = 0; i < N; i++){
      stars.push({ x: U.rand(-1,1), y: U.rand(-1,1), z: Math.random() });
    }
    const stop = U.loop(function() {
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.fillRect(0, 0, k.w, k.h);
      const cx = k.w/2, cy = k.h/2;
      for (let i = 0; i < stars.length; i++){
        const s = stars[i];
        s.z -= 0.006;
        if (s.z <= 0.02) { s.x = U.rand(-1,1); s.y = U.rand(-1,1); s.z = 1; }
        const px = cx + (s.x/s.z)*cx;
        const py = cy + (s.y/s.z)*cy;
        if (px < 0 || py < 0 || px > k.w || py > k.h) continue;
        const r = (1-s.z)*2.4;
        ctx.globalAlpha = 1-s.z;
        ctx.fillStyle = tx;
        ctx.beginPath(); ctx.arc(px, py, r, 0, Math.PI*2); ctx.fill();
      }
      ctx.globalAlpha = 1;
    });
    return { stop: function(){ stop(); k.destroy(); } };
  };
})();
