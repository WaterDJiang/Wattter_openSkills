/* 星座粒子 — 70 漂浮点 + 距离连线，适合 dark hero 页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['constellation'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const COUNT = 70, LINK_DIST = 150;
    const isLight = el.closest('.slide')?.classList.contains('light');
    function hexToRgb(hex){
      const m = hex.match(/^#?([\da-f]{2})([\da-f]{2})([\da-f]{2})$/i);
      return m ? [parseInt(m[1],16),parseInt(m[2],16),parseInt(m[3],16)] : [255,255,255];
    }
    const inkRgb = hexToRgb(U.ink(el));
    const paperRgb = hexToRgb(U.paper(el));
    const dotRgb = isLight ? inkRgb : paperRgb;
    const pts = [];
    for (let i = 0; i < COUNT; i++){
      pts.push({
        x: U.rand(0, k.w), y: U.rand(0, k.h),
        vx: U.rand(-0.3, 0.3), vy: U.rand(-0.3, 0.3),
        r: U.rand(1.2, 2.5)
      });
    }
    const stop = U.loop((t) => {
      const cw = k.w, ch = k.h;
      ctx.clearRect(0, 0, cw, ch);
      /* 更新位置 */
      pts.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = cw;
        if (p.x > cw) p.x = 0;
        if (p.y < 0) p.y = ch;
        if (p.y > ch) p.y = 0;
      });
      /* 连线 */
      for (let i = 0; i < COUNT; i++){
        for (let j = i + 1; j < COUNT; j++){
          const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y;
          const dist = Math.sqrt(dx*dx + dy*dy);
          if (dist < LINK_DIST){
            const alpha = (1 - dist / LINK_DIST) * 0.25;
            ctx.beginPath();
            ctx.moveTo(pts[i].x, pts[i].y);
            ctx.lineTo(pts[j].x, pts[j].y);
            ctx.strokeStyle = 'rgba(' + dotRgb[0] + ',' + dotRgb[1] + ',' + dotRgb[2] + ',' + alpha + ')';
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }
      /* 点 */
      pts.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + dotRgb[0] + ',' + dotRgb[1] + ',' + dotRgb[2] + ',0.6)';
        ctx.fill();
      });
    });
    return { stop(){ stop(); k.destroy(); } };
  };
})();
