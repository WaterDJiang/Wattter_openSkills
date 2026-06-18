/* =============== 微动模式 ==============
   入场动画重播 + counter-up + 进度条
   每次切页：遍历 data-anim 元素，移除再添加动画类 + 强制 reflow */
(function(){
  /* 入场动画重播 */
  window.__onSlideEnter = function(idx, slide) {
    const els = slide.querySelectorAll('[data-anim]');
    els.forEach(el => {
      const name = el.dataset.anim;
      const cls = 'anim-' + name;
      el.classList.remove(cls);
      void el.offsetWidth; /* 强制 reflow */
      /* 自定义时长/延迟 */
      if (el.dataset.animDur) el.style.setProperty('--anim-dur', el.dataset.animDur);
      if (el.dataset.animDelay) el.style.animationDelay = el.dataset.animDelay;
      el.classList.add(cls);
    });

    /* stagger-list 子元素重播 */
    const staggerContainers = slide.querySelectorAll('[data-anim="stagger-list"]');
    staggerContainers.forEach(c => {
      const cls = 'anim-stagger-list';
      c.classList.remove(cls);
      void c.offsetWidth;
      c.classList.add(cls);
    });

    /* counter-up */
    const counters = slide.querySelectorAll('.counter[data-to]');
    counters.forEach(el => {
      const target = parseFloat(el.dataset.to);
      const dur = parseInt(el.dataset.dur) || 1200;
      const isFloat = el.dataset.to.includes('.');
      const suffix = el.dataset.suffix || '';
      const start = performance.now();
      function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / dur, 1);
        const ease = 1 - Math.pow(1 - progress, 3); /* cubic ease-out */
        const val = target * ease;
        el.textContent = (isFloat ? val.toFixed(el.dataset.decimals || 1) : Math.round(val)) + suffix;
        if (progress < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  };

  /* 初始页也触发 */
  const slides = window.__deckSlides;
  if (slides && slides.length) {
    const i = window.__deckIdx();
    window.__onSlideEnter(i, slides[i]);
  }
})();
