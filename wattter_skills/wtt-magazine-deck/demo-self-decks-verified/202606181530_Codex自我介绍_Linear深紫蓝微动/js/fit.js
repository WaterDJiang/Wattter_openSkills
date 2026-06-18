/* =============== 内容适配 ==============
   自动缩放当前 slide 的主内容，避免长标题/KPI 矩阵把内容挤出视口。
   优先使用 .fit-shell；editorial 兼容 .frame；Swiss 不缩放 .canvas-card 本体。 */
(function(){
  const MIN_SCALE = 0.72;
  const PAD = 12;

  function targetFor(slide) {
    return slide.querySelector('.fit-shell') ||
      (slide.closest('body[data-style="swiss"]') ? null : slide.querySelector('.frame'));
  }

  function reset(el) {
    el.style.setProperty('--fit-scale', '1');
    el.classList.remove('is-fit-scaled');
  }

  function fitSlide(slide) {
    const el = targetFor(slide);
    if (!el) {
      const card = slide.querySelector('.canvas-card');
      if (card) {
        const over = card.scrollHeight > card.clientHeight + PAD || card.scrollWidth > card.clientWidth + PAD;
        slide.classList.toggle('fit-overflow-risk', over);
      }
      return;
    }
    reset(el);
    const availW = Math.max(1, el.clientWidth - PAD);
    const availH = Math.max(1, el.clientHeight - PAD);
    const needW = Math.max(el.scrollWidth, el.getBoundingClientRect().width);
    const needH = Math.max(el.scrollHeight, el.getBoundingClientRect().height);
    const scale = Math.min(1, availW / needW, availH / needH);
    if (scale < 0.995) {
      const clamped = Math.max(MIN_SCALE, scale);
      el.style.setProperty('--fit-scale', String(clamped));
      el.classList.add('is-fit-scaled');
      slide.classList.toggle('fit-overflow-risk', scale < MIN_SCALE);
    } else {
      slide.classList.remove('fit-overflow-risk');
    }
  }

  function fitAll() {
    const slides = window.__deckSlides || document.querySelectorAll('.slide');
    Array.from(slides).forEach(fitSlide);
  }

  window.__fitSlide = fitSlide;
  window.__fitDeck = fitAll;
  addEventListener('resize', function(){ requestAnimationFrame(fitAll); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll).catch(function(){});
  requestAnimationFrame(fitAll);
})();
