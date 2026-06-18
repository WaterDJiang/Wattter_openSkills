/* 字母爆散 — 文字从散乱飞回原位，适合标题/品牌页 */
(function(){
  window.HPX = window.HPX || {};
  window.HPX['letter-explode'] = function(el){
    const U = window.HPX._u;
    if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
    const src = el.querySelector('[data-fx-text]') || el;
    const text = (el.getAttribute('data-fx-text-value') || src.textContent || 'EXPLODE').trim();
    const wrap = document.createElement('div');
    wrap.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:1;';
    const inner = document.createElement('div');
    inner.style.cssText = 'font-size:64px;font-weight:900;letter-spacing:0.02em;color:var(--text-1,#fff);white-space:nowrap;';
    wrap.appendChild(inner);
    el.appendChild(wrap);
    const spans = [];
    for (let ci = 0; ci < text.length; ci++){
      const ch = text[ci];
      const s = document.createElement('span');
      s.textContent = ch === ' ' ? ' ' : ch;
      s.style.display = 'inline-block';
      s.style.transform = 'translate(0,0)';
      s.style.transition = 'transform 900ms cubic-bezier(.2,.9,.3,1), opacity 900ms';
      s.style.opacity = '0';
      inner.appendChild(s);
      spans.push(s);
    }
    let stopped = false;
    const run = function() {
      if (stopped) return;
      for (let i = 0; i < spans.length; i++){
        const s = spans[i];
        const dx = U.rand(-400, 400), dy = U.rand(-300, 300);
        s.style.transition = 'none';
        s.style.transform = 'translate(' + dx + 'px,' + dy + 'px) rotate(' + U.rand(-180,180) + 'deg)';
        s.style.opacity = '0';
      }
      void inner.offsetWidth;
      for (let i = 0; i < spans.length; i++){
        (function(s, idx){
          setTimeout(function(){
            if (stopped) return;
            s.style.transition = 'transform 900ms cubic-bezier(.2,.9,.3,1), opacity 900ms';
            s.style.transform = 'translate(0,0) rotate(0deg)';
            s.style.opacity = '1';
          }, idx*35);
        })(spans[i], i);
      }
    };
    run();
    const iv = setInterval(run, 4500);
    return { stop: function(){ stopped = true; clearInterval(iv); if (wrap.parentNode) wrap.parentNode.removeChild(wrap); } };
  };
})();
