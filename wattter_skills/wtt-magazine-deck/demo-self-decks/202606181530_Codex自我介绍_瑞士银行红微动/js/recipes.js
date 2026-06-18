/* =============== 风格 B · swiss 专属动效 recipe ==============
   从 assets/styles/swiss/template.html 的内联脚本抽出。
   22 个 data-animate recipe 名（hero/progression/statement/.../image-hero），
   实际由 onEnter() 按选择器执行 6 类通用动画：
   1. [data-anim] → 加 .in 类（60ms 错峰）
   2. .kpi-* / .num-mega / .name-mega → scale(.96)→1
   3. .h-bar-chart .row-fill → width 0→target
   4. .v-bar-chart .col-bar / .spec-bars .vbar / .bar-tower .body-block → scaleY 0→1
   5. .loop-diagram svg circle / .system-diagram svg circle → stroke-dashoffset
   6. .spec-kpi → 加 .in（顶线展开）

   通过 window.__onSlideEnter 接入 core/nav.js 的翻页回调。
   低功耗模式（B 键）下所有动画跳过。 */
(function(){
  var EASE = {
    prod: function(){ return 'cubic-bezier(.2,0,.38,.9)'; },
    exp:  function(){ return 'cubic-bezier(.4,.14,.3,1)'; }
  };

  function onEnter(slide){
    /* 1. 通用 reveal：所有 [data-anim] 容器加 .in（60ms 错峰） */
    var animEls = slide.querySelectorAll('[data-anim]');
    for (var i = 0; i < animEls.length; i++){
      (function(el, idx){
        el.style.transitionDelay = (idx * 60) + 'ms';
        el.classList.add('in');
      })(animEls[i], i);
    }

    /* 2. 数字 scale-in：kpi-hero / kpi-big / kpi-mid / kpi-thin / num-mega / name-mega */
    var numEls = slide.querySelectorAll('.kpi-hero,.kpi-big,.kpi-mid,.kpi-thin,.kpi-thin-sm,.num-mega,.name-mega');
    for (var j = 0; j < numEls.length; j++){
      (function(el){
        el.style.transform = 'scale(.96)';
        el.style.opacity = '0';
        el.style.transition = 'transform .9s ' + EASE.exp() + ', opacity .9s ' + EASE.exp();
        requestAnimationFrame(function(){
          el.style.transform = 'scale(1)';
          el.style.opacity = '1';
        });
      })(numEls[j]);
    }

    /* 3. 横条：width 0 → target */
    var hBars = slide.querySelectorAll('.h-bar-chart .row-fill');
    for (var k = 0; k < hBars.length; k++){
      (function(el){
        var w = el.style.width;
        el.style.width = '0%';
        requestAnimationFrame(function(){
          el.style.transition = 'width 1.2s ' + EASE.prod();
          el.style.width = w;
        });
      })(hBars[k]);
    }

    /* 4. 竖条：scaleY 0→1 */
    var vBars = slide.querySelectorAll('.v-bar-chart .col-bar, .spec-bars .vbar, .bar-tower .body-block');
    for (var m = 0; m < vBars.length; m++){
      (function(el){
        el.style.transform = 'scaleY(0)';
        el.style.transformOrigin = 'bottom';
        el.style.transition = 'transform 1.2s ' + EASE.prod();
        requestAnimationFrame(function(){ el.style.transform = 'scaleY(1)'; });
      })(vBars[m]);
    }

    /* 5. 圆环 stroke-dashoffset（loop-diagram / system-diagram svg circle） */
    var circles = slide.querySelectorAll('.loop-diagram svg circle, .system-diagram svg circle');
    for (var n = 0; n < circles.length; n++){
      (function(el){
        var r = parseFloat(el.getAttribute('r')) || 100;
        var c = 2 * Math.PI * r;
        el.style.strokeDasharray = c;
        el.style.strokeDashoffset = c;
        el.style.transition = 'stroke-dashoffset 1.4s ' + EASE.exp();
        requestAnimationFrame(function(){ el.style.strokeDashoffset = '0'; });
      })(circles[n]);
    }

    /* 6. spec-kpi 顶线展开 */
    var specKpis = slide.querySelectorAll('.spec-kpi');
    for (var p = 0; p < specKpis.length; p++){
      specKpis[p].classList.add('in');
    }
  }

  function onLeave(slide){
    var animEls = slide.querySelectorAll('[data-anim]');
    for (var i = 0; i < animEls.length; i++){
      animEls[i].classList.remove('in');
    }
  }

  /* ============ 接入 core/nav.js 回调 ============ */
  window.__onSlideEnter = function(idx, slide){
    onEnter(slide);
  };
  /* nav.js 没有显式 onLeave 回调，但切页时会重新触发 onEnter；
     这里保留 onLeave 供未来扩展（如 overview 模式重置） */
  window.__swissOnLeave = onLeave;

  /* ============ ASCII 呼吸场（封面/收尾用） ============ */
  function initAsciiCanvas(){
    var canvases = document.querySelectorAll('canvas.ascii-bg');
    for (var i = 0; i < canvases.length; i++){
      (function(c){
        var ctx = c.getContext('2d');
        var text = c.dataset.ascii || 'SWISS';
        var w = c.parentElement.clientWidth, h = c.parentElement.clientHeight;
        c.width = w; c.height = h;
        var cols = Math.floor(w / 9), rows = Math.floor(h / 14);
        function frame(t){
          ctx.fillStyle = 'rgba(255,255,255,0)';
          ctx.clearRect(0, 0, w, h);
          ctx.fillStyle = 'rgba(255,255,255,0.18)';
          ctx.font = '12px "JetBrains Mono", monospace';
          for (var y = 0; y < rows; y++){
            for (var x = 0; x < cols; x++){
              var n = Math.sin((x * 0.15) + (y * 0.18) + t * 0.6) * 0.5 + 0.5;
              if (n > 0.85) ctx.fillText(text[(x + y) % text.length], x * 9, y * 14);
            }
          }
        }
        var t0 = Date.now();
        (function loop(){
          if (document.body.classList.contains('low-power')){ requestAnimationFrame(loop); return; }
          frame((Date.now() - t0) / 1000);
          requestAnimationFrame(loop);
        })();
      })(canvases[i]);
    }
  }

  /* ============ 初始化 ============ */
  /* 低功耗模式持久化（B 键） */
  if (localStorage.getItem('wtt-low') === '1') document.body.classList.add('low-power');
  document.body.classList.add('motion-ready');

  /* 首屏触发 */
  var slides = window.__deckSlides;
  if (slides && slides.length){
    var i = window.__deckIdx ? window.__deckIdx() : 0;
    onEnter(slides[i]);
  }

  /* ASCII 画布在 DOM 就绪后初始化 */
  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', initAsciiCanvas);
  } else {
    initAsciiCanvas();
  }

  /* Lucide 图标渲染 */
  if (window.lucide) lucide.createIcons();
  window.addEventListener('load', function(){ if (window.lucide) lucide.createIcons(); });
})();
