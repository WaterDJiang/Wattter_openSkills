/* 鼠标星光 — 跟随指针 + 空闲自游走，适合互动展示页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['sparkle-trail'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const isLight = el.closest('.slide')?.classList.contains('light');
    function hexToRgb(hex){
      const m = hex.match(/^#?([\da-f]{2})([\da-f]{2})([\da-f]{2})$/i);
      return m ? [parseInt(m[1],16),parseInt(m[2],16),parseInt(m[3],16)] : [255,255,255];
    }
    const dotRgb = hexToRgb(isLight ? U.ink(el) : U.paper(el));
    const particles = [];
    let mx = k.w / 2, my = k.h / 2, idle = true, idleAngle = 0;

    el.addEventListener('mousemove', e => {
      const rect = el.getBoundingClientRect();
      mx = e.clientX - rect.left;
      my = e.clientY - rect.top;
      idle = false;
      for (let i = 0; i < 3; i++){
        particles.push({
          x: mx + U.rand(-4, 4), y: my + U.rand(-4, 4),
          vx: U.rand(-1.5, 1.5), vy: U.rand(-2, 0.5),
          life: 1, decay: U.rand(0.01, 0.025),
          size: U.rand(1.5, 3.5),
          hue: U.rand(-20, 20)
        });
      }
    });
    el.addEventListener('mouseleave', () => { idle = true; });

    const stop = U.loop((t) => {
      const cw = k.w, ch = k.h;
      ctx.clearRect(0, 0, cw, ch);
      if (idle) {
        idleAngle += 0.02;
        mx = cw * 0.5 + Math.sin(idleAngle) * cw * 0.2;
        my = ch * 0.5 + Math.cos(idleAngle * 0.7) * ch * 0.15;
        if (Math.random() < 0.3) {
          particles.push({
            x: mx + U.rand(-4,4), y: my + U.rand(-4,4),
            vx: U.rand(-1, 1), vy: U.rand(-1.5, 0.3),
            life: 1, decay: U.rand(0.015, 0.03),
            size: U.rand(1.2, 2.8), hue: U.rand(-15, 15)
          });
        }
      }
      for (let i = particles.length - 1; i >= 0; i--){
        const p = particles[i];
        p.x += p.vx; p.y += p.vy;
        p.vy += 0.02;
        p.life -= p.decay;
        if (p.life <= 0) { particles.splice(i, 1); continue; }
        const alpha = p.life * 0.7;
        const r = Math.min(255, dotRgb[0] + p.hue);
        const g = Math.min(255, dotRgb[1] + p.hue * 0.5);
        const b = Math.min(255, dotRgb[2] - p.hue * 0.3);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + Math.round(r) + ',' + Math.round(g) + ',' + Math.round(b) + ',' + alpha + ')';
        ctx.fill();
      }
    });
    return { stop(){ stop(); k.destroy(); } };
  };
})();
