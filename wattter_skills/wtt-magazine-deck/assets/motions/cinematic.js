/* =============== 沉浸模式 ==============
   含微动模式全部能力 + Canvas FX 管理（通过 fx-runtime.js） + Overview 网格 + Notes 抽屉 + 主题热切换 */
(function(){

  /* ============ 动画重播 + counter-up（同 subtle.js） ============ */
  function replayAnims(slide) {
    const els = slide.querySelectorAll('[data-anim]');
    els.forEach(function(el){
      const name = el.dataset.anim;
      const cls = 'anim-' + name;
      el.classList.remove(cls);
      void el.offsetWidth;
      if (el.dataset.animDur) el.style.setProperty('--anim-dur', el.dataset.animDur);
      if (el.dataset.animDelay) el.style.animationDelay = el.dataset.animDelay;
      el.classList.add(cls);
    });
    const staggerContainers = slide.querySelectorAll('[data-anim="stagger-list"]');
    staggerContainers.forEach(function(c){
      const cls = 'anim-stagger-list';
      c.classList.remove(cls);
      void c.offsetWidth;
      c.classList.add(cls);
    });
    const counters = slide.querySelectorAll('.counter[data-to]');
    counters.forEach(function(el){
      const target = parseFloat(el.dataset.to);
      const dur = parseInt(el.dataset.dur) || 1200;
      const isFloat = el.dataset.to.includes('.');
      const suffix = el.dataset.suffix || '';
      const start = performance.now();
      function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / dur, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        const val = target * ease;
        el.textContent = (isFloat ? val.toFixed(el.dataset.decimals || 1) : Math.round(val)) + suffix;
        if (progress < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }

  /* ============ FX 管理（委托给 fx-runtime.js） ============ */
  function activateSlideFx(slide) {
    slide.classList.add('is-active');
    if (window.__hpxReinit) window.__hpxReinit(slide);
  }

  function deactivateSlideFx(slide) {
    slide.classList.remove('is-active');
  }

  /* ============ Overview 网格 ============ */
  function buildOverview() {
    const slides = window.__deckSlides;
    if (!slides) return;
    let ov = document.getElementById('overview');
    if (ov) { ov.innerHTML = ''; }
    else {
      ov = document.createElement('div');
      ov.id = 'overview';
      document.body.appendChild(ov);
    }
    const grid = document.createElement('div');
    grid.className = 'ov-grid';
    Array.from(slides).forEach(function(slide, i){
      const card = document.createElement('div');
      card.className = 'ov-card';
      const inner = document.createElement('div');
      inner.className = 'ov-inner';
      const clone = slide.cloneNode(true);
      clone.style.cssText = 'width:1920px;height:1080px;transform:scale(var(--ov-scale));transform-origin:top left;position:absolute;inset:0;pointer-events:none;';
      inner.appendChild(clone);
      const num = document.createElement('span');
      num.className = 'ov-num';
      num.textContent = (i + 1);
      card.appendChild(num);
      card.appendChild(inner);
      card.addEventListener('click', function(){
        ov.classList.remove('open');
        if (window.__deckGo) window.__deckGo(i);
      });
      grid.appendChild(card);
    });
    ov.appendChild(grid);

    requestAnimationFrame(function(){
      const cards = ov.querySelectorAll('.ov-card');
      cards.forEach(function(card){
        const inner = card.querySelector('.ov-inner');
        if (inner) {
          const w = card.offsetWidth;
          const scale = w / 1920;
          inner.style.setProperty('--ov-scale', scale);
        }
      });
    });
  }

  /* ============ Notes 抽屉 ============ */
  function buildNotesDrawer() {
    if (document.getElementById('notes-drawer')) return;
    const drawer = document.createElement('div');
    drawer.id = 'notes-drawer';
    drawer.innerHTML = '<div class="notes-kicker">NOTES</div><div class="notes-body"></div>';
    document.body.appendChild(drawer);
  }

  /* ============ 滑动进入回调 ============ */
  window.__onSlideEnter = function(idx, slide) {
    replayAnims(slide);
    const slides = window.__deckSlides;
    Array.from(slides).forEach(function(s){ deactivateSlideFx(s); });
    activateSlideFx(slide);
    const drawer = document.getElementById('notes-drawer');
    if (drawer && drawer.classList.contains('open')) {
      const note = slide.querySelector('.notes');
      const kicker = drawer.querySelector('.notes-kicker');
      const body = drawer.querySelector('.notes-body');
      if (kicker) kicker.textContent = 'NOTES · ' + (idx + 1) + ' / ' + window.__deckTotal();
      if (body) body.innerHTML = note ? note.innerHTML : '';
    }
    if (window.__bc) window.__bc.postMessage({ type: 'go', idx: idx });
  };

  /* ============ 初始化 ============ */
  buildNotesDrawer();
  buildOverview();
  const slides = window.__deckSlides;
  if (slides && slides.length) {
    const i = window.__deckIdx();
    window.__onSlideEnter(i, slides[i]);
  }
})();
