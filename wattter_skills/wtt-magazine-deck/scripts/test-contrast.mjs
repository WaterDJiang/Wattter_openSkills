// node scripts/test-contrast.mjs [绝对路径/playwright/index.mjs]
import { readFileSync, mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import assert from 'node:assert/strict';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = p => readFileSync(resolve(root, p), 'utf8');
// 验证静态检查能识别最近 surface，不把 background-color 当成 color。
const temp = mkdtempSync(resolve(tmpdir(), 'deck-contrast-'));
try {
  for (const [body, expected] of [
    ['<div class="surface-dark"><p style="color:var(--paper)">可读</p></div>', false],
    ['<div class="surface-dark"><p style="color:var(--ink)">不可读</p></div>', true],
    ['<div style="background-color:var(--paper)">浅底</div>', false],
    ['<div class="surface-accent"><p style="color:var(--ink)">亮主题待浏览器检查</p></div>', false],
  ]) {
    const file = resolve(temp, 'index.html');
    writeFileSync(file, `<body data-style="editorial"><section class="slide light">${body}</section></body>`);
    const result = spawnSync(process.execPath, [resolve(root, 'scripts/validate-deck.mjs'), file, 'editorial', '--allow-legacy-dir'], { encoding: 'utf8' });
    assert.ok(result.stdout.includes('error'), 'fixture must execute validator');
    assert.equal(result.stdout.includes('surface contrast conflict'), expected, body);
  }
} finally { rmSync(temp, { recursive: true }); }
const { chromium } = await import(process.argv[2] ? pathToFileURL(resolve(process.argv[2])).href : 'playwright');
const browser = await chromium.launch({ headless: true, channel: 'chrome' });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const base = ['tokens', 'slide', 'typography', 'layout', 'components', 'image', 'chrome', 'nav', 'responsive'].map(n => read(`assets/core/${n}.css`)).join('\n');
  let themes = 0, pairs = 0;
  for (const style of JSON.parse(read('assets/styles/registry.json')).styles) {
    for (const theme of style.availableThemes) {
      const themeCss = read(`${style.files.themesDir}/${theme}.css`);
      const styleCss = read(`assets/styles/${style.id}/style.css`);
      for (const outer of ['light', 'dark', 'accent']) {
        await page.setContent(`<style>${base}\n${styleCss}\n${themeCss}</style>
          <section class="slide ${outer}">
            ${['light', 'dark', 'accent'].map(surface => `<div class="surface-${surface}">
              <h2 class="h-md" id="${surface}">标题</h2>
              <p class="text-primary" id="${surface}-body">正文</p>
              <div class="surface-light"><h2 class="h-md" id="${surface}-nested">嵌套标题</h2></div>
            </div>`).join('')}
          </section>`);
        const result = await page.evaluate(() => {
          const cs = el => getComputedStyle(el);
          const resolveColor = name => {
            const el = document.createElement('span');
            el.style.color = `var(${name})`; document.body.append(el);
            const value = cs(el).color; el.remove(); return value;
          };
          return ['light', 'dark', 'accent'].flatMap(surface => {
            const expected = resolveColor(surface === 'light' ? '--ink' : surface === 'dark' ? '--paper' : '--accent-on');
            return [surface, `${surface}-body`, `${surface}-nested`].map(id => ({
              id, actual: cs(document.getElementById(id)).color,
              expected: id.endsWith('-nested') ? resolveColor('--ink') : expected,
            }));
          });
        });
        for (const r of result) { assert.equal(r.actual, r.expected, `${style.id}/${theme}/${outer}/${r.id}`); pairs++; }
      }
      if (style.id === 'linear') {
        await page.setContent(`<style>${base}\n${styleCss}\n${themeCss}</style><section class="slide grey"><p class="text-primary" id="grey">灰底正文</p></section>`);
        assert.equal(await page.locator('#grey').evaluate(el => getComputedStyle(el).color), await page.locator('.slide').evaluate(el => getComputedStyle(el).color));
      }
      themes++;
    }
  }
  const source = read('scripts/audit-contrast.js');
  await page.setContent('<body style="background:#fff;color:#000;font:16px Arial"><p id="good">正常</p><p id="bad" style="color:#eee">浅字浅底</p><p id="bad-dark" style="background:#111;color:#222">深字深底</p><p id="complex" style="background:linear-gradient(white,black)">渐变</p></body>');
  const report = await page.evaluate(source);
  assert.deepEqual(report.failures.map(r => r.element).sort(), ['#bad', '#bad-dark']);
  assert.ok(report.review.some(r => r.element === '#complex'));
  assert.equal(report.passed, false);
  await page.setContent('<body style="background:#fff;color:#000;font:16px Arial"><p>可读正文</p></body>');
  assert.equal((await page.evaluate(source)).passed, true);
  console.log(`PASS ${themes} themes, ${pairs} nested text assertions; light/dark failures detected; gradient review; clean fixture passed.`);
} finally { await browser.close(); }
