/* 文字瀑布 — 词语从上方下落堆叠，适合知识/概念页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['word-cascade'] = function(el){
    const U = window.HPX._u;
    const k = U.canvas(el), ctx = k.ctx;
    const pal = U.palette(el);
    const WORDS = ['AI','知识','Graph','Claude','LLM','Agent','Vector','RAG','Token','神经',
      'Prompt','Chain','Skill','Code','Cloud','GPU','Flow','推理','Data','Model'];
    let items = [];
    let last = -1;
    let piles = {};
    const stop = U.loop(function(t) {
      ctx.clearRect(0, 0, k.w, k.h);
      if (t - last > 0.18){
        last = t;
        const w = WORDS[(Math.random()*WORDS.length)|0];
        items.push({
          text: w, x: U.rand(40, k.w-40), y: -20,
          vy: 0, c: pal[(Math.random()*pal.length)|0],
          size: U.rand(16,26), landed: false
        });
      }
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      for (let i = 0; i < items.length; i++){
        const it = items[i];
        if (!it.landed){
          it.vy += 0.4;
          it.y += it.vy;
          const col = Math.round(it.x/60);
          const floor = k.h - (piles[col]||0) - it.size*0.6;
          if (it.y >= floor){
            it.y = floor; it.landed = true;
            piles[col] = (piles[col]||0) + it.size*1.1;
            if ((piles[col]||0) > k.h*0.8) piles[col] = 0;
          }
        }
        ctx.fillStyle = it.c;
        ctx.font = '700 ' + it.size + 'px system-ui,sans-serif';
        ctx.fillText(it.text, it.x, it.y);
      }
      if (items.length > 120){
        items = items.filter(function(i){return !i.landed;}).concat(
          items.filter(function(i){return i.landed;}).slice(-60)
        );
      }
    });
    return { stop: function(){ stop(); k.destroy(); } };
  };
})();
