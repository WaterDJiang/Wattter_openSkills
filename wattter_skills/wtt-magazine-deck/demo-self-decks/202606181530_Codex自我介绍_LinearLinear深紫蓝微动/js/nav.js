/* =============== 导航核心 ==============
   键盘 / 滚轮 / 触屏 / 按钮翻页 + 圆点指示器
   + Hash 深链接 + 动画循环(A键) + 预览模式 + 演示者模式 + BroadcastChannel
   被 subtle.js 和 cinematic.js 扩展 */
(function(){
  const deck = document.getElementById('deck');
  const slides = deck.querySelectorAll('.slide');
  const nav = document.getElementById('nav');
  let idx = 0, total = slides.length, lock = false;

  deck.style.width = (total * 100) + 'vw';

  /* ---- 预览模式 ---- */
  const urlParams = new URLSearchParams(location.search);
  const previewMode = urlParams.has('preview');
  const previewIdx = previewMode ? parseInt(urlParams.get('preview'), 10) : -1;

  if (previewMode) {
    document.documentElement.dataset.preview = '1';
    document.body.dataset.preview = '1';
  }

  /* ---- BroadcastChannel ---- */
  let bc = null;
  try {
    bc = new BroadcastChannel('wtt-deck-' + location.pathname);
    window.__bc = bc;
    bc.onmessage = function(e) {
      var d = e.data;
      if (d.type === 'go') go(d.idx, true);
      if (d.type === 'theme' && window.__cycleTheme) {
        var link = document.getElementById('theme-link');
        if (link) {
          var basePath = link.getAttribute('href').replace(/[^/]+\.css$/, '');
          link.href = basePath + d.name + '.css';
        }
      }
    };
  } catch(e){}

  /* ---- 预览模式 iframe 消息 ---- */
  if (previewMode) {
    window.addEventListener('message', function(e){
      if (e.data === 'preview-goto') go(parseInt(e.data.idx, 10), true);
      if (e.data && e.data.type === 'preview-goto') go(e.data.idx, true);
      if (e.data && e.data.type === 'preview-theme' && window.__cycleTheme) {
        var link = document.getElementById('theme-link');
        if (link) {
          var basePath = link.getAttribute('href').replace(/[^/]+\.css$/, '');
          link.href = basePath + e.data.name + '.css';
        }
      }
    });
    window.parent.postMessage('preview-ready', '*');
  }

  /* 圆点 */
  slides.forEach(function(s, i){
    const b = document.createElement('span');
    b.className = 'dot';
    b.setAttribute('aria-label', 'Page ' + (i + 1));
    b.addEventListener('click', function(){ go(i); });
    nav.appendChild(b);
  });

  const progress = document.getElementById('progress');

  function ensureNavButtons() {
    var wrap = document.getElementById('nav-btns');
    if (!wrap) {
      wrap = document.createElement('div');
      wrap.id = 'nav-btns';
      document.body.appendChild(wrap);
    }
    if (!document.getElementById('btn-prev')) {
      var prev = document.createElement('button');
      prev.className = 'nav-btn';
      prev.id = 'btn-prev';
      prev.setAttribute('aria-label', '上一页');
      prev.innerHTML = '<svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>';
      wrap.appendChild(prev);
    }
    if (!document.getElementById('btn-next')) {
      var next = document.createElement('button');
      next.className = 'nav-btn';
      next.id = 'btn-next';
      next.setAttribute('aria-label', '下一页');
      next.innerHTML = '<svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>';
      wrap.appendChild(next);
    }
    var tools = document.getElementById('nav-tools');
    if (!tools) {
      tools = document.createElement('div');
      tools.id = 'nav-tools';
      document.body.appendChild(tools);
    }
    if (!document.getElementById('btn-theme')) {
      var theme = document.createElement('button');
      theme.className = 'nav-tool';
      theme.id = 'btn-theme';
      theme.type = 'button';
      theme.setAttribute('aria-label', '切换主题');
      theme.setAttribute('title', '切换主题 (T)');
      theme.textContent = 'T';
      tools.appendChild(theme);
    }
  }

  ensureNavButtons();
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnTheme = document.getElementById('btn-theme');
  if (btnPrev) btnPrev.onclick = function(){ go(idx - 1); };
  if (btnNext) btnNext.onclick = function(){ go(idx + 1); };

  /* ---- 主题热切换（所有动效模式共用） ---- */
  function readThemeList() {
    if (window.__DECK_THEMES && window.__DECK_THEMES.length) return window.__DECK_THEMES;
    var bodyAttr = document.body.getAttribute('data-theme-list');
    if (bodyAttr) {
      var list = bodyAttr.split(',').map(function(s){ return s.trim(); }).filter(Boolean);
      if (list.length) return list;
    }
    return [];
  }

  var THEMES = readThemeList();
  var themeIdx = 0;

  function detectCurrentTheme() {
    var link = document.getElementById('theme-link');
    if (!link) return 0;
    var href = link.getAttribute('href') || '';
    for (var i = 0; i < THEMES.length; i++) {
      if (href.indexOf(THEMES[i]) !== -1) return i;
    }
    return 0;
  }

  window.__cycleTheme = function() {
    var link = document.getElementById('theme-link');
    if (!link || !THEMES.length) return;
    themeIdx = (themeIdx + 1) % THEMES.length;
    var href = link.getAttribute('href') || '';
    if (/theme\.css(?:\?|#|$)/.test(href) && !THEMES.some(function(t){ return href.indexOf(t + '.css') !== -1; })) {
      console.warn('[wtt-magazine-deck] T theme switch skipped: current css/theme.css is a custom one-off theme. Copy preset theme files and set href to a preset name to enable cycling.');
      return;
    }
    var basePath = href.replace(/[^/]+\.css(?:\?.*)?$/, '');
    link.onload = function(){ if (window.__refreshThemeColors) window.__refreshThemeColors(); };
    link.href = basePath + THEMES[themeIdx] + '.css';
    setTimeout(function(){ if (window.__refreshThemeColors) window.__refreshThemeColors(); }, 120);
    if (window.__bc) window.__bc.postMessage({ type: 'theme', name: THEMES[themeIdx] });
  };
  themeIdx = detectCurrentTheme();
  if (btnTheme) {
    btnTheme.onclick = function(){
      if (window.__cycleTheme) window.__cycleTheme();
    };
    if (!THEMES.length) btnTheme.disabled = true;
  }

  /* 核心导航 */
  function go(n, fromRemote) {
    if (lock && !fromRemote) return;
    idx = Math.max(0, Math.min(total - 1, n));
    deck.style.transform = 'translateX(' + (-idx * 100) + 'vw)';

    nav.querySelectorAll('.dot').forEach(function(d, i){ d.classList.toggle('active', i === idx); });

    const el = slides[idx];
    const th = el.dataset.theme || (el.classList.contains('light') ? 'light' : (el.classList.contains('dark') ? 'dark' : 'dark'));
    document.body.classList.toggle('light-bg', th === 'light');

    if (btnPrev) btnPrev.disabled = idx === 0;
    if (btnNext) btnNext.disabled = idx === total - 1;

    if (progress) progress.style.width = ((idx + 1) / total * 100) + '%';

    if (typeof window.__fitSlide === 'function') window.__fitSlide(el);
    if (typeof window.__onSlideEnter === 'function') window.__onSlideEnter(idx, el);
    if (typeof window.__fitSlide === 'function') requestAnimationFrame(function(){ window.__fitSlide(el); });

    /* Hash 更新 */
    if (!previewMode) {
      try { history.replaceState(null, '', '#' + (idx + 1)); } catch(e){}
    }

    /* BroadcastChannel 同步 */
    if (!fromRemote && bc) bc.postMessage({ type: 'go', idx: idx });

    lock = true;
    setTimeout(function(){ lock = false; }, 700);
  }

  /* ---- Hash 深链接 ---- */
  function fromHash() {
    var h = location.hash;
    if (h && h.length > 1) {
      var n = parseInt(h.slice(1), 10);
      if (n >= 1 && n <= total) return n - 1;
    }
    return previewMode && previewIdx >= 0 ? Math.min(previewIdx, total-1) : 0;
  }

  window.addEventListener('hashchange', function(){
    var n = fromHash();
    if (n !== idx) go(n, true);
  });

  /* ---- 动画循环（A 键） ---- */
  const ANIMS = [
    'fade-up','fade-down','fade-left','fade-right','rise-in','drop-in','zoom-pop',
    'blur-in','glitch-in','typewriter','neon-glow','shimmer-sweep','gradient-flow',
    'stagger-list','counter-up','path-draw','parallax-tilt','card-flip-3d',
    'cube-rotate-3d','page-turn-3d','perspective-zoom','marquee-scroll','kenburns',
    'confetti-burst','spotlight','morph-shape','ripple-reveal'
  ];
  let animIdx = 0;

  function cycleAnim() {
    var slide = slides[idx];
    var target = slide.querySelector('[data-anim-target]') || slide;
    /* 移除旧的 anim 类 */
    ANIMS.forEach(function(a){
      target.classList.remove('anim-' + a);
    });
    void target.offsetWidth;
    var name = ANIMS[animIdx % ANIMS.length];
    target.classList.add('anim-' + name);
    target.dataset.anim = name;
    animIdx++;
  }

  /* ---- 演示者模式（S 键） ---- */
  function openPresenter() {
    var w = 1200, h = 800;
    var left = (screen.width - w) / 2, top = (screen.height - h) / 2;
    var popup = window.open(
      location.pathname + '?preview=' + idx,
      'wtt-presenter',
      'width=' + w + ',height=' + h + ',left=' + left + ',top=' + top
    );
  }

  /* 键盘 */
  addEventListener('keydown', function(e){
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ' || e.key === 'ArrowDown') { e.preventDefault(); go(idx + 1); }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp' || e.key === 'ArrowUp') { e.preventDefault(); go(idx - 1); }
    if (e.key === 'Enter') { e.preventDefault(); go(idx + 1); }
    if (e.key === 'Backspace') { e.preventDefault(); go(idx - 1); }
    if (e.key === 'Home') go(0);
    if (e.key === 'End') go(total - 1);
    if (e.key === 'F' || e.key === 'f') { e.preventDefault(); toggleFullscreen(); }
    if (e.key === 'n' || e.key === 'N') {
      var d = document.getElementById('notes-drawer');
      if (d) { d.classList.toggle('open'); updateNotes(idx); }
    }
    if (e.key === 'o' || e.key === 'O') {
      var ov = document.getElementById('overview');
      if (ov) ov.classList.toggle('open');
    }
    if (e.key === 't' || e.key === 'T') {
      if (window.__cycleTheme) window.__cycleTheme();
    }
    if (e.key === 'a' || e.key === 'A') {
      cycleAnim();
    }
    if (e.key === 's' || e.key === 'S') {
      openPresenter();
    }
    if (e.key === 'Escape') {
      var ov = document.getElementById('overview');
      if (ov) ov.classList.remove('open');
      var d = document.getElementById('notes-drawer');
      if (d) d.classList.remove('open');
    }
  });

  /* 滚轮 */
  var wheelTO = null, wheelAcc = 0;
  addEventListener('wheel', function(e){
    wheelAcc += e.deltaY + e.deltaX;
    if (Math.abs(wheelAcc) > 50) { go(idx + (wheelAcc > 0 ? 1 : -1)); wheelAcc = 0; }
    clearTimeout(wheelTO);
    wheelTO = setTimeout(function(){ wheelAcc = 0; }, 150);
  }, { passive: true });

  /* 触屏 */
  var touchX = 0, touchY = 0;
  addEventListener('touchstart', function(e){ touchX = e.touches[0].clientX; touchY = e.touches[0].clientY; }, { passive: true });
  addEventListener('touchend', function(e){
    var dx = (e.changedTouches[0].clientX - touchX);
    var dy = (e.changedTouches[0].clientY - touchY);
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) go(idx + (dx < 0 ? 1 : -1));
  }, { passive: true });

  /* Fullscreen */
  function toggleFullscreen() {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(function(){});
    else document.exitFullscreen().catch(function(){});
  }

  /* Notes 更新 */
  function updateNotes(i) {
    var drawer = document.getElementById('notes-drawer');
    if (!drawer) return;
    var note = slides[i].querySelector('.notes');
    var kicker = drawer.querySelector('.notes-kicker');
    var body = drawer.querySelector('.notes-body');
    if (kicker) kicker.textContent = 'NOTES · ' + (i + 1) + ' / ' + total;
    if (body) body.innerHTML = note ? note.innerHTML : '';
  }

  /* 导出 */
  window.__deckGo = go;
  window.__deckIdx = function(){ return idx; };
  window.__deckTotal = function(){ return total; };
  window.__deckSlides = slides;

  go(fromHash());
})();
