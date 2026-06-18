/* FX Autoloader — 动态加载所有 FX 模块，MutationObserver 自动管理生命周期 */
(function(){
  window.HPX = window.HPX || {};
  window.__hpxActive = new Map();

  var FX_LIST = [
    '_util','particle-burst','confetti-cannon','firework','starfield',
    'matrix-rain','knowledge-graph','neural-net','constellation','orbit-ring',
    'galaxy-swirl','word-cascade','letter-explode','chain-react','magnetic-field',
    'data-stream','gradient-blob','sparkle-trail','shockwave','typewriter-multi',
    'counter-explosion'
  ];

  var base = '';
  try {
    var cs = document.currentScript;
    if (cs && cs.src) base = cs.src.replace(/fx-runtime\.js$/, '');
  } catch(e){}
  if (!base) base = 'fx/';

  var loaded = 0, total = FX_LIST.length;
  var readyRes;
  var ready = new Promise(function(r){ readyRes = r; });

  for (var i = 0; i < FX_LIST.length; i++){
    (function(name){
      var s = document.createElement('script');
      s.src = base + name + '.js';
      s.async = false;
      s.onload = s.onerror = function(){
        loaded++;
        if (loaded >= total) readyRes();
      };
      document.head.appendChild(s);
    })(FX_LIST[i]);
  }

  function initFxIn(root){
    if (!window.HPX) return;
    var els = root.querySelectorAll('[data-fx]');
    for (var i = 0; i < els.length; i++){
      var el = els[i];
      if (window.__hpxActive.has(el)) continue;
      var name = el.getAttribute('data-fx');
      var fn = window.HPX[name];
      if (typeof fn === 'function'){
        try {
          var handle = fn(el);
          window.__hpxActive.set(el, handle);
        } catch(e){ console.warn('[fx-runtime] init error:', name, e); }
      }
    }
  }

  function stopFxIn(root){
    var els = root.querySelectorAll('[data-fx]');
    for (var i = 0; i < els.length; i++){
      var el = els[i];
      var handle = window.__hpxActive.get(el);
      if (handle){
        if (typeof handle.stop === 'function') handle.stop();
        window.__hpxActive.delete(el);
      }
    }
  }

  function reinitFxIn(root){
    stopFxIn(root);
    initFxIn(root);
  }

  window.__hpxReinit = reinitFxIn;

  ready.then(function(){
    var slides = document.querySelectorAll('.slide');
    for (var i = 0; i < slides.length; i++){
      (function(slide){
        var obs = new MutationObserver(function(mutations){
          for (var m = 0; m < mutations.length; m++){
            if (mutations[m].attributeName === 'class'){
              if (slide.classList.contains('is-active')){
                initFxIn(slide);
              } else {
                stopFxIn(slide);
              }
            }
          }
        });
        obs.observe(slide, { attributes: true, attributeFilter: ['class'] });
      })(slides[i]);
    }
  });
})();
