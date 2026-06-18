/* 知识图谱 — 节点+连线力导向图，适合知识/概念页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['knowledge-graph'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const pal = U.palette(el);
    const tx = U.text(el, '#e7e7ef');
    const labels = ['AI','ML','LLM','Graph','Node','Edge','Claude','GPT','RAG','Vector',
      'Embed','Neural','Agent','Tool','Memory','Logic','Data','Train','Infer','Token',
      'Prompt','Chain','Plan','Skill','Cloud','Edge','GPU','Code','Task','Flow'];
    const N = 28;
    const nodes = [];
    for (let i = 0; i < N; i++){
      nodes.push({
        x: U.rand(40, 300), y: U.rand(40, 200),
        vx: 0, vy: 0, label: labels[i%labels.length],
        c: pal[i%pal.length]
      });
    }
    const edges = [];
    const made = {};
    while (edges.length < 50){
      const a = (Math.random()*N)|0, b = (Math.random()*N)|0;
      if (a === b) continue;
      const key = a < b ? a+'-'+b : b+'-'+a;
      if (made[key]) continue;
      made[key] = true; edges.push([a,b]);
    }
    const stop = U.loop(function() {
      for (let i = 0; i < N; i++){
        for (let j = i+1; j < N; j++){
          const a = nodes[i], b = nodes[j];
          const dx = b.x-a.x, dy = b.y-a.y;
          let d2 = dx*dx+dy*dy; if (d2 < 1) d2 = 1;
          const d = Math.sqrt(d2);
          const f = 1600/d2;
          const fx = (dx/d)*f, fy = (dy/d)*f;
          a.vx -= fx; a.vy -= fy; b.vx += fx; b.vy += fy;
        }
      }
      for (let e = 0; e < edges.length; e++){
        const a = nodes[edges[e][0]], b = nodes[edges[e][1]];
        const dx = b.x-a.x, dy = b.y-a.y, d = Math.hypot(dx,dy) || 1;
        const f = (d-90)*0.008;
        const fx = (dx/d)*f, fy = (dy/d)*f;
        a.vx += fx; a.vy += fy; b.vx -= fx; b.vy -= fy;
      }
      const cx = k.w/2, cy = k.h/2;
      for (let i = 0; i < nodes.length; i++){
        const n = nodes[i];
        n.vx += (cx-n.x)*0.002; n.vy += (cy-n.y)*0.002;
        n.vx *= 0.85; n.vy *= 0.85;
        n.x += n.vx; n.y += n.vy;
      }
      ctx.clearRect(0, 0, k.w, k.h);
      ctx.strokeStyle = 'rgba(180,180,220,0.25)'; ctx.lineWidth = 1;
      for (let e = 0; e < edges.length; e++){
        const a = nodes[edges[e][0]], b = nodes[edges[e][1]];
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
      ctx.font = '11px system-ui,sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      for (let i = 0; i < nodes.length; i++){
        const n = nodes[i];
        ctx.fillStyle = n.c;
        ctx.beginPath(); ctx.arc(n.x, n.y, 7, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = tx;
        ctx.fillText(n.label, n.x, n.y-14);
      }
    });
    return { stop: function(){ stop(); k.destroy(); } };
  };
})();
