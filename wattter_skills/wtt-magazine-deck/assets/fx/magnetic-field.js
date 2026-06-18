/* 磁力线 — 粒子沿正弦路径流动带尾迹，适合物理/场论页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['magnetic-field'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const pal = U.palette(el);
    const N = 60;
    const parts = [];
    for (let i = 0; i < N; i++){
      parts.push({
        phase: Math.random()*Math.PI*2,
        freq: U.rand(0.4, 1.2),
        amp: U.rand(30, 90),
        y0: U.rand(0.15, 0.85),
        c: pal[i%pal.length],
        trail: []
      });
    }
    const stop = U.loop(function(t) {
      ctx.fillStyle = 'rgba(0,0,0,0.08)';
      ctx.fillRect(0, 0, k.w, k.h);
      for (let i = 0; i < parts.length; i++){
        const p = parts[i];
        const x = ((t*80 + p.phase*50) % (k.w+100)) - 50;
        const y = k.h*p.y0 + Math.sin(x*0.02 + p.phase + t*p.freq)*p.amp;
        p.trail.push([x, y]);
        if (p.trail.length > 18) p.trail.shift();
        ctx.strokeStyle = p.c;
        ctx.lineWidth = 2;
        ctx.beginPath();
        for (let j = 0; j < p.trail.length; j++){
          if (j === 0) ctx.moveTo(p.trail[j][0], p.trail[j][1]);
          else ctx.lineTo(p.trail[j][0], p.trail[j][1]);
        }
        ctx.globalAlpha = 0.7;
        ctx.stroke();
        ctx.globalAlpha = 1;
        ctx.fillStyle = p.c;
        ctx.beginPath(); ctx.arc(x, y, 2.5, 0, Math.PI*2); ctx.fill();
      }
    });
    return { stop: function(){ stop(); k.destroy(); } };
  };
})();
