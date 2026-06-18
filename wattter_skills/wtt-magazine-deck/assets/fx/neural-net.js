/* 神经网络脉冲 — 多层节点+连线+信号传递，适合AI/深度学习页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['neural-net'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const ac = U.accent(el,'#7c5cff'), ac2 = U.accent2(el,'#22d3ee');
    const layers = [4,6,6,3];
    let nodes = [], edges = [], pulses = [];
    const layout = function() {
      nodes = [];
      const pad = 40;
      const cw = k.w - pad*2, ch = k.h - pad*2;
      for (let L = 0; L < layers.length; L++){
        const x = pad + (cw * L / (layers.length-1));
        const n = layers[L];
        for (let i = 0; i < n; i++){
          const y = pad + (ch * (i+0.5) / n);
          nodes.push({x:x, y:y, L:L, i:i});
        }
      }
      edges = [];
      for (let L = 0; L < layers.length-1; L++){
        const a = nodes.filter(function(n){return n.L===L;});
        const b = nodes.filter(function(n){return n.L===L+1;});
        for (let x = 0; x < a.length; x++){
          for (let y = 0; y < b.length; y++){
            edges.push([nodes.indexOf(a[x]), nodes.indexOf(b[y])]);
          }
        }
      }
    };
    layout();
    let lw = k.w, lh = k.h, last = 0;
    const stop = U.loop(function(t) {
      if (k.w !== lw || k.h !== lh){ layout(); lw = k.w; lh = k.h; }
      ctx.clearRect(0, 0, k.w, k.h);
      ctx.strokeStyle = 'rgba(160,160,200,0.22)'; ctx.lineWidth = 1;
      for (let i = 0; i < edges.length; i++){
        const a = nodes[edges[i][0]], b = nodes[edges[i][1]];
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
      if (t - last > 0.25){
        last = t;
        const starts = nodes.filter(function(n){return n.L===0;});
        const s = starts[(Math.random()*starts.length)|0];
        pulses.push({node:s, L:0, t:0, target:null});
      }
      for (let i = pulses.length - 1; i >= 0; i--){
        const p = pulses[i];
        if (!p.target){
          const next = nodes.filter(function(n){return n.L===p.L+1;});
          p.target = next[(Math.random()*next.length)|0];
        }
        p.t += 0.04;
        const a = p.node, b = p.target;
        const x = a.x + (b.x-a.x)*Math.min(1, p.t);
        const y = a.y + (b.y-a.y)*Math.min(1, p.t);
        ctx.fillStyle = ac2;
        ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI*2); ctx.fill();
        if (p.t >= 1){
          p.node = b; p.target = null; p.L++; p.t = 0;
          if (p.L >= layers.length-1) pulses.splice(i, 1);
        }
      }
      for (let i = 0; i < nodes.length; i++){
        const n = nodes[i];
        ctx.fillStyle = ac;
        ctx.beginPath(); ctx.arc(n.x, n.y, 6, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = ac2; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(n.x, n.y, 8, 0, Math.PI*2); ctx.stroke();
      }
    });
    return { stop: function(){ stop(); k.destroy(); } };
  };
})();
