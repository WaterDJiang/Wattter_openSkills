#!/usr/bin/env node
/* =============== wtt-magazine-deck · 风格 B 瑞士国际主义 · 校验脚本 ==============
   跨 deck 校验：检查 V1-V8 硬约束
   读 assets/styles/registry.json 知道哪些是 swiss 的登记版式
   ============================================================================ */
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));

// 找 registry.json（支持多种调用路径）
function findRegistry() {
  const candidates = [
    resolve(__dirname, '../assets/styles/registry.json'),
    resolve(__dirname, '../../assets/styles/registry.json'),
  ];
  for (const c of candidates) if (existsSync(c)) return c;
  throw new Error('Cannot find assets/styles/registry.json');
}
const REGISTRY_PATH = findRegistry();
const REGISTRY = JSON.parse(readFileSync(REGISTRY_PATH, 'utf8'));
const SWISS = REGISTRY.styles.find(s => s.id === 'swiss');
if (!SWISS) {
  console.error('swiss style not found in registry.json');
  process.exit(2);
}

const file = process.argv[2];
const allowExperimental = process.argv.includes('--allow-experimental');

if (!file) {
  console.error('Usage: node scripts/validate-swiss-deck.mjs <index.html> [--allow-experimental]');
  process.exit(2);
}
if (!existsSync(file)) {
  console.error(`File not found: ${file}`);
  process.exit(2);
}

const html = readFileSync(file, 'utf8');
const htmlForSlides = html.replace(/<!--[\s\S]*?-->/g, '');
const errors = [];
const warnings = [];

// ===== 版式白名单 =====
const allowedLayouts = new Set([
  ...Array.from({ length: 22 }, (_, i) => `S${String(i + 1).padStart(2, '0')}`),
  'SWISS-COVER-ASCII',
  'SWISS-CLOSING-ASCII',
]);
const experimentalLayouts = new Set(['P23', 'P24', 'SWISS-IMAGE-SPLIT', 'EVIDENCE-GRID', 'THREE-CIRCLES']);
const allowedRecipes = new Set([
  'hero','progression','statement','grid-reveal','stack-build','measure-up','bar-grow','duo-mirror',
  'matrix-statement','split-statement','timeline-walk','manifesto','three-forces','loop-form',
  'matrix-fill','field-notes','system-diagram','why-now','four-cards','stacked-ledger','tech-spec','image-hero',
]);

// ===== 提取 slide =====
const slideRe = /<section\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>[\s\S]*?<\/section>/g;
const slides = [...htmlForSlides.matchAll(slideRe)].map((m, idx) => ({
  idx: idx + 1,
  html: m[0],
  tag: m[0].match(/<section\b[^>]*>/)?.[0] ?? '',
}));

if (!slides.length) {
  errors.push('No <section class="slide"> pages found.');
}

const isolation = SWISS.styleIsolation || {};
const editorialOnlyClasses = isolation.forbidClasses || [
  'chrome','foot','display','display-zh','h1-zh','h2-zh','h3-zh','body-zh','body-serif',
  'big-num','mid-num','ghost','en','stat','plat','rowline','quote-wall','qw-item','qw-text','qw-cite'
];
const editorialClassSet = new Set(editorialOnlyClasses);
const forbiddenLayoutRe = isolation.forbidLayoutPattern ? new RegExp(isolation.forbidLayoutPattern, 'i') : /^L\d{2}$/i;
slides.forEach(slide => {
  const layout = slide.tag.match(/\bdata-layout="([^"]+)"/)?.[1] || '';
  if (layout && forbiddenLayoutRe.test(layout)) {
    errors.push(`Slide ${slide.idx}: Swiss deck contains editorial layout id. Use registered Sxx layouts only.`);
  }
  for (const m of slide.html.matchAll(/\bclass="([^"]+)"/gi)) {
    const hit = m[1].split(/\s+/).find(c => editorialClassSet.has(c));
    if (hit) {
      errors.push(`Slide ${slide.idx}: Swiss deck contains editorial-only class ".${hit}". Use registered Sxx Swiss components only.`);
    }
  }
});

// ===== 全局检查 =====
if (/<title>[^<]*\[必填\]/.test(html)) {
  errors.push('Global: <title> still contains [必填] placeholder.');
}
if (/\{\{/.test(html)) {
  errors.push('Global: index.html contains {{ ... }} placeholder (not replaced).');
}
if (!/fit\.js/.test(html)) {
  errors.push('Global: fit.js not loaded. Swiss deck must include content fitting to avoid viewport overflow.');
}

function hasClass(tag, name){ return new RegExp(`\\b${name}\\b`).test(tag); }
function getStyleAttr(tag){ return tag.match(/\bstyle="([^"]*)"/i)?.[1] || ''; }
function inferTheme(slide) {
  const tag = slide.tag;
  if (hasClass(tag, 'dark')) return 'dark';
  if (hasClass(tag, 'accent') || hasClass(tag, 'split') || /\bhalf\s+b-accent\b/.test(slide.html)) return 'accent';
  if (hasClass(tag, 'grey')) return 'grey';
  if (hasClass(tag, 'light')) return 'light';
  return 'paper';
}

// ===== 首页必须体现主题色 =====
if (slides[0]) {
  const cover = slides[0];
  const layout = cover.tag.match(/\bdata-layout="([^"]+)"/)?.[1];
  const isCoverLayout = layout === 'S01' || layout === 'SWISS-COVER-ASCII';
  const hasAccentSurface = hasClass(cover.tag, 'accent') ||
    /background(?:-color)?\s*:\s*var\(--accent\)/i.test(cover.html) ||
    /\b(ascii-bg|b-accent|card-accent|accent-block)\b/.test(cover.html);
  if (!isCoverLayout) {
    errors.push('Slide 1: Swiss cover must use S01 or SWISS-COVER-ASCII so the first impression is a controlled theme page.');
  }
  if (!hasAccentSurface) {
    errors.push('Slide 1: Swiss cover must visibly use the selected theme accent (class="slide accent" preferred; the chosen preset or custom color should dominate the cover).');
  }
}

// ===== 每个 slide 检查 =====
slides.forEach(slide => {
  const tag = slide.tag;
  const layout = tag.match(/\bdata-layout="([^"]+)"/)?.[1];
  const recipe = tag.match(/\bdata-animate="([^"]+)"/)?.[1];

  // V1: 必须写 data-layout
  if (!layout) {
    errors.push(`Slide ${slide.idx}: missing data-layout. Swiss requires S01-S22 or SWISS-COVER-ASCII/SWISS-CLOSING-ASCII.`);
    return;
  }

  // V1b: 必须写 data-animate recipe
  if (!recipe) {
    errors.push(`Slide ${slide.idx} (${layout}): missing data-animate recipe.`);
  } else if (!allowedRecipes.has(recipe)) {
    errors.push(`Slide ${slide.idx} (${layout}): data-animate="${recipe}" is not a registered Swiss recipe.`);
  }

  // V2: 未登记版式
  if (!allowedLayouts.has(layout)) {
    if (experimentalLayouts.has(layout) && !allowExperimental) {
      errors.push(`Slide ${slide.idx}: data-layout="${layout}" is experimental. Add --allow-experimental to enable.`);
    } else if (!experimentalLayouts.has(layout) || allowExperimental) {
      errors.push(`Slide ${slide.idx}: data-layout="${layout}" is not registered in swiss-layout-lock.md.`);
    }
  }

  // V3: 非 statement 页顶部 text-align:center 报错
  const isStatement = ['S03', 'S09', 'S10', 'SWISS-COVER-ASCII', 'SWISS-CLOSING-ASCII'].includes(layout);
  const topChunk = slide.html.slice(0, 1800);
  if (!isStatement && /text-align\s*:\s*center/i.test(topChunk)) {
    errors.push(`Slide ${slide.idx} (${layout}): top title area contains text-align:center. Swiss body titles should stay left aligned.`);
  }

  // V4: 非 statement 页 h1/h2 不在垂直/水平居中
  if (!isStatement && /align-self\s*:\s*center/i.test(topChunk) && /<h[12]\b/i.test(topChunk)) {
    errors.push(`Slide ${slide.idx} (${layout}): top heading appears vertically/centrally aligned. Use the original left-top title skeleton.`);
  }

  // V5: SVG 不含 <text>
  if (/<svg\b[\s\S]*?<text\b/i.test(slide.html)) {
    errors.push(`Slide ${slide.idx} (${layout}): SVG contains visible <text>. Put labels in HTML grid/captions, keep SVG for geometry only.`);
  }

  // V6: 本地图片必带 data-image-slot
  const imgRe = /<img\s+[^>]*src="(images\/[^"]+)"/g;
  for (const m of slide.html.matchAll(imgRe)) {
    const imgTag = m[0];
    if (!/data-image-slot=/.test(imgTag)) {
      errors.push(`Slide ${slide.idx} (${layout}): <img src="${m[1]}"> missing data-image-slot="..." attribute.`);
    }
  }

  // V7: S15/S16 重生成图片必须用 .frame-img.r-21x9，无 .fit-contain，无 height:Xvh 短槽
  if (layout === 'S15' || layout === 'S16') {
    if (/\.frame-img\.r-(?!21x9|16x10)\w+/i.test(slide.html)) {
      errors.push(`Slide ${slide.idx} (${layout}): S15/S16 image group must use uniform 21:9 or 16:10 ratio.`);
    }
    if (/\.frame-img[^"]*\bfit-contain\b/i.test(slide.html)) {
      errors.push(`Slide ${slide.idx} (${layout}): .fit-contain is forbidden for S15/S16 re-generated images.`);
    }
  }

  // V8: S22 必须 data-image-slot=s22-hero-21x9，不含 object-position:top center
  if (layout === 'S22') {
    const s22Imgs = [...slide.html.matchAll(/<img\s+[^>]*data-image-slot="([^"]+)"/g)];
    if (!s22Imgs.length || !s22Imgs.some(m => m[1].includes('s22-hero-21x9'))) {
      errors.push(`Slide ${slide.idx} (${layout}): S22 must have <img data-image-slot="s22-hero-21x9">.`);
    }
    if (/object-position\s*:\s*top\s*center/i.test(slide.html)) {
      errors.push(`Slide ${slide.idx} (${layout}): S22 images cannot use object-position:top center. Use center 35%.`);
    }
  }
});

// ===== 密度风险提示 =====
slides.forEach(slide => {
  for (const m of slide.html.matchAll(/<h[1-2]\b[^>]*>([\s\S]*?)<\/h[1-2]>/gi)) {
    const text = m[1].replace(/<[^>]*>/g, '').replace(/\s+/g, '').trim();
    if (text.length > 28 && !/\bfit-safe-text\b/.test(m[0])) {
      warnings.push(`Slide ${slide.idx}: heading has ${text.length} chars without .fit-safe-text; long titles can drift or overflow.`);
    }
  }
  const dense = [...slide.html.matchAll(/\b(class="[^"]*(?:kpi-|ledger-row|sub-card|force-card|stat-card)[^"]*")/g)].length;
  if (dense >= 8 && !/\bfit-shell\b/.test(slide.html)) {
    warnings.push(`Slide ${slide.idx}: contains ${dense} dense stat/card elements without .fit-shell; wrap the dense body, split the page, or use a lower-density layout.`);
  }
});

// ===== Swiss 静态样式检查：颜色冲突 / 圆角 / 大标题字重 =====
slides.forEach(slide => {
  const theme = inferTheme(slide);
  const sectionStyle = getStyleAttr(slide.tag);
  if ((theme === 'paper' || theme === 'light' || theme === 'grey') && /color\s*:\s*var\(--paper\)/i.test(sectionStyle)) {
    errors.push(`Slide ${slide.idx}: color conflict: light/grey/default slide sets color:var(--paper), causing pale text on pale background.`);
  }
  if ((theme === 'dark' || theme === 'accent') && /color\s*:\s*var\(--ink\)/i.test(sectionStyle)) {
    errors.push(`Slide ${slide.idx}: color conflict: dark/accent slide sets color:var(--ink), causing dark text on dark background.`);
  }

  for (const m of slide.html.matchAll(/<([a-z0-9-]+)\b[^>]*style="([^"]*)"[^>]*>/gi)) {
    const tag = m[0];
    const style = m[2];
    const hasDarkBg = /background(?:-color)?\s*:\s*var\(--(?:ink|accent)\)/i.test(style) || /\b(b-ink|b-accent|hero-ink-col|ink-banner-full)\b/.test(tag);
    const hasLightBg = /background(?:-color)?\s*:\s*var\(--(?:paper|grey-1|grey-2)\)/i.test(style);
    if (hasLightBg && /color\s*:\s*var\(--paper\)/i.test(style)) {
      errors.push(`Slide ${slide.idx}: color conflict: same element uses light background with color:var(--paper).`);
    }
    if (hasDarkBg && /color\s*:\s*var\(--ink\)/i.test(style)) {
      errors.push(`Slide ${slide.idx}: color conflict: same element uses dark/accent background with color:var(--ink).`);
    }
    const radius = style.match(/\bborder-radius\s*:\s*([^;"']+)/i)?.[1]?.trim().toLowerCase();
    if (radius && !/^(0|0px|0rem|0em|0%)\s*!important?$/.test(radius)) {
      errors.push(`Slide ${slide.idx}: Swiss forbids border-radius="${radius}" in generated slide HTML.`);
    }
  }

  for (const m of slide.html.matchAll(/<(h[1-6]|[a-z0-9-]+)\b([^>]*)>/gi)) {
    const tagName = m[1].toLowerCase();
    const attrs = m[2];
    const cls = attrs.match(/\bclass="([^"]*)"/i)?.[1] || '';
    const isTarget = /^h[12]$/.test(tagName) || /\b(h-hero|h-xl|h-hero-zh|h-xl-zh)\b/.test(cls);
    if (!isTarget) continue;
    const weight = attrs.match(/\bstyle="[^"]*\bfont-weight\s*:\s*(\d+)/i)?.[1];
    if (weight && Number(weight) > 300) {
      errors.push(`Slide ${slide.idx}: heading font-weight ${weight} exceeds Swiss max 300.`);
    }
  }
});

// ===== 全局模式检查 =====
let prev1 = null, prev2 = null;
slides.forEach(s => {
  const theme = inferTheme(s);
  if (theme && theme === prev1 && theme === prev2) {
    warnings.push(`Slide ${s.idx}: 3 consecutive slides share theme "${theme}".`);
  }
  prev2 = prev1; prev1 = theme;
});

// Sxx 覆盖度
const usedLayouts = new Set(slides.map(s => s.tag.match(/data-layout="([^"]+)"/)?.[1]).filter(Boolean));
if (slides.length >= 7) {
  const validCount = [...usedLayouts].filter(l => allowedLayouts.has(l)).length;
  if (validCount < 6) {
    warnings.push(`Global: ${slides.length} slides use only ${validCount} unique Sxx layouts (recommend ≥6 for variety).`);
  }
}

// ===== 输出 =====
console.log(`\n  wtt-magazine-deck · validate-swiss-deck.mjs`);
console.log(`  File:   ${file}`);
console.log(`  Style:  ${SWISS.name} (swiss)`);
console.log(`  Slides: ${slides.length}`);
console.log(`  Layouts: ${[...usedLayouts].join(', ')}\n`);

if (errors.length) {
  console.log(`  ✗ ${errors.length} error(s):`);
  errors.forEach(e => console.log(`    - ${e}`));
  console.log('');
}
if (warnings.length) {
  console.log(`  ⚠ ${warnings.length} warning(s):`);
  warnings.forEach(w => console.log(`    - ${w}`));
  console.log('');
}
if (!errors.length && !warnings.length) {
  console.log(`  ✓ All checks passed.\n`);
} else if (!errors.length) {
  console.log(`  ✓ No errors, ${warnings.length} warning(s) (non-blocking).\n`);
}

process.exit(errors.length ? 1 : 0);
