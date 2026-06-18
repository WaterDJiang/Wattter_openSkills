/* 烟花绽放 — 火箭升空 + 爆裂，适合高潮/节日页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['firework'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const pal = U.palette(el);
    let rockets = [], sparks = [];
    const launch = function() {
      rockets.push({
        x: U.rand(k.w*0.2, k.w*0.8), y: k.h+10,
        vx: U.rand(-30,30), vy: U.rand(-520,-380),
        tgtY: U.rand(k.h*0.15, k.h*0.45),
        c: pal[(Math.random()*pal.length)|0]
      });
    };
    const burst = function(x, y, c) {
      for (let i = 0; i < 70; i++){
        const a = Math.random()*Math.PI*2;
        const s = U.rand(60, 240);
        sparks.push({x:x, y:y, vx:Math.cos(a)*s, vy:Math.sin(a)*s, life:1, c:c});
      }
    };
    let last = -1;
    const stop = U.loop(function(t) {
      ctx.fillStyle = 'rgba(0,0,0,0.18)';
      ctx.fillRect(0, 0, k.w, k.h);
      if (t - last > 0.7) { launch(); last = t; }
      const dt = 1/60;
      rockets = rockets.filter(function(r) {
        r.x += r.vx*dt; r.y += r.vy*dt; r.vy += 260*dt;
        ctx.fillStyle = r.c;
        ctx.beginPath(); ctx.arc(r.x, r.y, 2.5, 0, Math.PI*2); ctx.fill();
        if (r.y <= r.tgtY || r.vy >= 0) { burst(r.x, r.y, r.c); return false; }
        return true;
      });
      sparks = sparks.filter(function(p){ return p.life > 0; });
      for (let i = 0; i < sparks.length; i++){
        const p = sparks[i];
        p.vy += 90*dt; p.vx *= 0.98; p.vy *= 0.98;
        p.x += p.vx*dt; p.y += p.vy*dt;
        p.life -= 0.012;
        ctx.globalAlpha = Math.max(0, p.life);
        ctx.fillStyle = p.c;
        ctx.beginPath(); ctx.arc(p.x, p.y, 2, 0, Math.PI*2); ctx.fill();
      }
      ctx.globalAlpha = 1;
    });
    return { stop: function(){ stop(); k.destroy(); } };
  };
})();
