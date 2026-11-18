/* 在浏览器执行此文件，返回当前可见文字的渲染对比度报告。
   Playwright: const report = await page.evaluate(source);
   只读，不修改页面；逐页、逐主题、入场动画结束后运行。
   复杂绘制返回 review，不冒充自动通过。 */
(() => {
  const failures = [], review = [];
  let checked = 0;
  const rgb = value => {
    const m = value.match(/^rgba?\(([^)]+)\)$/);
    if (!m) return null;
    const n = m[1].split(/[\s,/]+/).filter(Boolean).map(Number);
    return n.length >= 3 && n.every(Number.isFinite) ? [...n.slice(0, 3), n[3] ?? 1] : null;
  };
  const over = (fg, bg) => fg.slice(0, 3).map((v, i) => v * fg[3] + bg[i] * (1 - fg[3]));
  const lum = c => c.slice(0, 3).map(v => {
    v /= 255;
    return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4;
  }).reduce((s, v, i) => s + v * [.2126, .7152, .0722][i], 0);
  const ratio = (a, b) => (Math.max(lum(a), lum(b)) + .05) / (Math.min(lum(a), lum(b)) + .05);
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    if (!node.textContent.trim()) continue;
    const el = node.parentElement;
    if (!el || el.closest('script,style,noscript,[aria-hidden="true"]')) continue;
    const range = document.createRange();
    range.selectNodeContents(node);
    if (![...range.getClientRects()].some(r => r.width && r.height && r.right > 0 && r.bottom > 0 && r.left < innerWidth && r.top < innerHeight)) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility !== 'visible') continue;
    const item = { slide: [...document.querySelectorAll('.slide')].indexOf(el.closest('.slide')) + 1,
      element: el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}.${[...el.classList].join('.')}`,
      text: node.textContent.trim().slice(0, 90) };
    const layers = [];
    let reason = '', hidden = false, opaque = false;
    for (let p = el; p; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (s.display === 'none' || Number(s.opacity) === 0) { hidden = true; break; }
      if (p !== el && Number(s.opacity) !== 1) reason ||= '祖先 opacity 需要复核';
      if (s.filter !== 'none' || s.mixBlendMode !== 'normal') reason ||= '滤镜/混合模式需要复核';
      if (opaque) continue;
      if (s.backgroundImage !== 'none') reason ||= '图片/渐变背景需要复核';
      for (const pseudo of ['::before', '::after']) {
        const ps = getComputedStyle(p, pseudo);
        if (ps.content !== 'none' && ps.content !== 'normal' &&
            (ps.backgroundImage !== 'none' || (rgb(ps.backgroundColor)?.[3] ?? 0) > 0)) {
          reason ||= '伪元素底板/遮罩需要复核';
        }
      }
      const bg = rgb(s.backgroundColor);
      if (!bg) { reason ||= '暂不支持的背景色语法'; continue; }
      if (p === el && Number(s.opacity) !== 1 && bg[3] > 0) reason ||= '文字与背景整体透明需要复核';
      layers.push(bg);
      if (bg[3] === 1) opaque = true;
    }
    if (hidden) continue;
    const fg = rgb(cs.color);
    if (!fg) reason ||= '暂不支持的文字色语法';
    if (!opaque) reason ||= '透明背景，底层画面需要复核';
    if (reason) { review.push({ ...item, reason }); continue; }
    let bg = [255, 255, 255];
    for (const layer of layers.reverse()) bg = over(layer, bg);
    fg[3] *= Number(cs.opacity);
    const value = ratio(over(fg, bg), bg);
    const threshold = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.667 && Number(cs.fontWeight) >= 700) ? 3 : 4.5;
    checked++;
    if (value < threshold) failures.push({ ...item, ratio: +value.toFixed(2), threshold, foreground: cs.color, background: bg });
  }
  return { checked, failures, review, passed: checked > 0 && failures.length === 0 && review.length === 0 };
})();
