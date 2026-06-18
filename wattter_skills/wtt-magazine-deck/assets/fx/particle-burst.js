/* 粒子爆裂 — 从中心爆开 + 重力 + 阻力，适合关键数据揭示 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['particle-burst'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const isLight = el.closest('.slide')?.classList.contains('light');
    function hexToRgb(hex){
      const m = hex.match(/^#?([\da-f]{2})([\da-f]{2})([\da-f]{2})$/i);
      return m ? [parseInt(m[1],16),parseInt(m[2],16),parseInt(m[3],16)] : [255,255,255];
    }
    const dotRgb = hexToRgb(isLight ? U.ink(el) : U.paper(el));

    let particles = [];
    let burstTimer = 0;
    const BURST_INTERVAL = 3;

    function burst() {
      const cx = k.w * 0.5, cy = k.h * 0.5;
      for (let i = 0; i < 60; i++){
        const angle = U.rand(0, Math.PI * 2);
        const speed = U.rand(2, 8);
        particles.push({
          x: cx, y: cy,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          life: 1, decay: U.rand(0.008, 0.02),
          size: U.rand(2, 5),
          hueShift: U.rand(-30, 30)
        });
      }
    }

    burst();

    const stop = U.loop((t) => {
      const cw = k.w, ch = k.h;
      ctx.clearRect(0, 0, cw, ch);

      burstTimer += 1/60;
      if (burstTimer > BURST_INTERVAL) {
        burst();
        burstTimer = 0;
      }

      for (let i = particles.length - 1; i >= 0; i--){
        const p = particles[i];
        p.vy += 0.08;
        p.vx *= 0.99;
        p.vy *= 0.99;
        p.x += p.vx; p.y += p.vy;
        p.life -= p.decay;
        if (p.life <= 0) { particles.splice(i, 1); continue; }
        const alpha = p.life * 0.8;
        const r = Math.min(255, Math.max(0, dotRgb[0] + p.hueShift));
        const g = Math.min(255, Math.max(0, dotRgb[1] + p.hueShift * 0.5));
        const b = Math.min(255, Math.max(0, dotRgb[2] - p.hueShift * 0.3));
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + Math.round(r) + ',' + Math.round(g) + ',' + Math.round(b) + ',' + alpha + ')';
        ctx.fill();
      }
    });
    return { stop(){ stop(); k.destroy(); } };
  };
})();
