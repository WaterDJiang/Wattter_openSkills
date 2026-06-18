#!/usr/bin/env node
/* =============== wtt-magazine-deck 跨风格校验脚本 ==============
   读 assets/styles/registry.json 知道有哪些风格 + 风格专属规则，
   然后对 index.html 做 10+ 项硬规则检查。

   Usage: node scripts/validate-deck.mjs <index.html> [style-id]
   示例:  node scripts/validate-deck.mjs 202606181530_AI课程合作介绍_瑞士克莱因蓝电影/index.html swiss
         node scripts/validate-deck.mjs 202606181530_AI课程合作介绍_瑞士克莱因蓝电影/index.html # 自动从 <body data-style> 检测
         node scripts/validate-deck.mjs old-deck/index.html swiss --allow-legacy-dir
*/
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { basename, dirname, join, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
// 兼容两种调用：scripts/ 在仓库根目录 或 在 skill 内
function findRegistry() {
  const candidates = [
    resolve(__dirname, '../assets/styles/registry.json'),
    resolve(__dirname, '../../assets/styles/registry.json'),
    resolve(__dirname, 'assets/styles/registry.json'),
    resolve(__dirname, 'skills/wtt-magazine-deck/assets/styles/registry.json'),
    resolve(__dirname, '../skills/wtt-magazine-deck/assets/styles/registry.json'),
  ];
  for (const c of candidates) if (existsSync(c)) return c;
  throw new Error('Cannot find assets/styles/registry.json. Pass --skill-root=<path> or place script under skill root or repo root.');
}

const args = process.argv.slice(2);
const skillRootArg = args.find(a => a.startsWith('--skill-root='));
const positional = args.filter(a => !a.startsWith('--'));

const REGISTRY_PATH = skillRootArg
  ? resolve(process.cwd(), skillRootArg.split('=')[1], 'assets/styles/registry.json')
  : findRegistry();
const SKILL_ROOT = dirname(dirname(dirname(REGISTRY_PATH)));  // .../skills/wtt-magazine-deck
const REGISTRY = JSON.parse(readFileSync(REGISTRY_PATH, 'utf8'));

const file = positional[0];
const styleArg = positional[1];
const allowExperimental = process.argv.includes('--allow-experimental');
const allowLegacyDir = process.argv.includes('--allow-legacy-dir');

if (!file) {
  console.error('Usage: node scripts/validate-deck.mjs <index.html> [style-id] [--allow-experimental] [--allow-legacy-dir]');
  process.exit(2);
}
if (!existsSync(file)) {
  console.error(`File not found: ${file}`);
  process.exit(2);
}

const html = readFileSync(file, 'utf8');
const htmlStripped = html.replace(/<!--[\s\S]*?-->/g, '');
const errors = [];
const warnings = [];

// === 自动检测风格（从 <body data-style="...">） ===
const styleMatch = html.match(/<body[^>]*\bdata-style="([^"]+)"/);
const detectedStyle = styleMatch?.[1];
const styleId = styleArg || detectedStyle;
if (!styleId) {
  errors.push('Cannot detect style: pass style-id as 2nd arg or set <body data-style="..."> in HTML.');
} else if (!REGISTRY.styles.find(s => s.id === styleId)) {
  errors.push(`Unknown style: ${styleId}. Available: ${REGISTRY.styles.map(s => s.id).join(', ')}`);
}
if (detectedStyle && styleArg && detectedStyle !== styleArg) {
  warnings.push(`<body data-style="${detectedStyle}"> but passed style="${styleArg}". Using passed.`);
}

const STYLE_GUARDS = {
  editorial: {
    foreignLayouts: /\bdata-layout="(?:S\d{2}|SWISS-[^"]+)"/i,
    foreignClasses: [
      'canvas-card','chrome-min','ascii-bg','split-half','sub-grid-3-2','timeline-v','timeline-h',
      'th-node','kpi-row-4','kpi-cell','kpi-hero','kpi-big','kpi-mid','kpi-thin','kpi-thin-sm',
      'num-mega','name-mega','t-cat','t-body','t-body-sm','t-body-emp','t-h-prod',
      'duo-compare','bar-towers','h-bar-chart','stack-row','stack-block','force-card',
      'loop-diagram','system-diagram','why-now-grid','four-cards','stacked-ledger',
      'ledger-row','ledger-num','spec-kpi','spec-bars','hero-ink-col','image-hero-stats',
      'history-map-grid','relation-card','map-panel','accent-block','ink-block','grey-block',
      'card-fill','card-ink','card-accent','card-outlined','dot-mat','ring-mat','cross-mat','hatch',
      'swiss-img-split','swiss-img-copy','swiss-img-grid','swiss-img-caption'
    ],
    msg: 'Editorial deck contains Swiss-only layout/class. Regenerate this page with editorial layouts instead of mixing style systems.'
  },
  swiss: {
    foreignLayouts: /\bdata-layout="L\d{2}"/i,
    foreignClasses: [
      'chrome','foot','display','display-zh','h1-zh','h2-zh','h3-zh','body-zh','body-serif',
      'big-num','mid-num','ghost','en','stat','plat','rowline','quote-wall','qw-item','qw-text','qw-cite'
    ],
    msg: 'Swiss deck contains editorial-only layout/class. Use registered Sxx Swiss layouts and components only.'
  }
};

// === 提取所有 <section class="slide"> ===
const slideRe = /<section\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>[\s\S]*?<\/section>/g;
const slides = [...htmlStripped.matchAll(slideRe)].map((m, idx) => ({
  idx: idx + 1,
  html: m[0],
  tag: m[0].match(/<section\b[^>]*>/)?.[0] ?? '',
}));
if (!slides.length) {
  errors.push('No <section class="slide"> pages found.');
}

// ============= 通用规则（跨风格） =============
function addError(slide, msg){ errors.push(`Slide ${slide}: ${msg}`); }
function addWarning(slide, msg){ warnings.push(`Slide ${slide}: ${msg}`); }
function hasClass(tag, name){ return new RegExp(`\\b${name}\\b`).test(tag); }
function getStyleAttr(tag){ return tag.match(/\bstyle="([^"]*)"/i)?.[1] || ''; }
function isSwiss(){ return styleId === 'swiss'; }
function inferTheme(slide) {
  const tag = slide.tag;
  if (hasClass(tag, 'dark')) return 'dark';
  if (hasClass(tag, 'accent') || hasClass(tag, 'split') || /\bhalf\s+b-accent\b/.test(slide.html)) return 'accent';
  if (hasClass(tag, 'grey')) return 'grey';
  if (hasClass(tag, 'light')) return 'light';
  if (hasClass(tag, 'hero')) return 'hero';
  return isSwiss() ? 'paper' : null;
}

const STYLE_NAME_ALIASES = {
  editorial: ['杂志', '叙事', 'editorial'],
  swiss: ['瑞士', 'swiss'],
  linear: ['Linear', 'linear', '科技']
};

const THEME_NAME_ALIASES = {
  'ink-classic': ['墨水经典', '墨水', 'ink-classic'],
  'indigo-porcelain': ['靛蓝瓷', '靛蓝', 'indigo-porcelain'],
  'forest-ink': ['森林墨', '森林', 'forest-ink'],
  'kraft-paper': ['牛皮纸', 'kraft-paper'],
  dune: ['沙丘', 'dune'],
  'ikb-blue': ['克莱因蓝', 'IKB', 'ikb-blue'],
  'hermes-orange': ['爱马仕橙', '爱马仕', 'hermes-orange'],
  'bank-red': ['银行红', 'bank-red'],
  'tiffany-blue': ['蒂芙尼蓝', '蒂芙尼', 'tiffany-blue'],
  'valentino-pink': ['华伦天奴粉', '华伦天奴', 'valentino-pink'],
  'bottega-green': ['宝缇嘉绿', '宝缇嘉', 'bottega-green'],
  'lemon-yellow': ['柠檬黄', 'lemon-yellow'],
  'lemon-green': ['柠檬绿', 'lemon-green'],
  'safety-orange': ['安全橙', 'safety-orange'],
  'linear-dark': ['Linear深紫蓝', '深紫蓝', 'linear-dark'],
  'linear-aurora': ['极光紫', 'linear-aurora'],
  'linear-graphite': ['石墨银灰', '石墨', 'linear-graphite'],
  'linear-solar': ['暗底暖金', '暖金', 'linear-solar']
};

const MOTION_NAME_ALIASES = {
  static: ['静态', 'static'],
  subtle: ['微动', 'subtle'],
  cinematic: ['电影', '沉浸', 'cinematic']
};

function detectThemeIdFromHtml(html) {
  const href = html.match(/<link\b[^>]*id="theme-link"[^>]*href="([^"]+)"/)?.[1] || '';
  const file = basename(href).replace(/\.css(?:\?.*)?$/, '');
  if (!file || file === 'theme') return '';
  return file;
}

function detectMotionIdFromHtml(html) {
  if (/fx-runtime\.js|js\/fx\//i.test(html)) return 'cinematic';
  if (/animations\.css|motion\.js/i.test(html)) return 'subtle';
  return 'static';
}

function includesAny(text, aliases) {
  return aliases.some(alias => text.includes(alias));
}

function checkOutputDirectoryName(file, errors, warnings, allowLegacy, styleId, html) {
  const dirName = basename(dirname(resolve(file)));
  const pattern = /^(\d{12})_([^_\s][^_]*)_([^_\s][^_]*)$/u;
  const match = dirName.match(pattern);
  const example = '202606181530_AI课程合作介绍_瑞士克莱因蓝电影';
  const msg = `Global: output directory "${dirName}" must be named YYYYMMDDHHmm_内容主题_模板主题色动效, e.g. ${example}. Do not use the old *_Mdeck suffix.`;
  if (allowLegacy) {
    warnings.push(`${msg} Skipped because --allow-legacy-dir is set.`);
    return;
  }
  if (!match) {
    errors.push(`${msg} Use --allow-legacy-dir only when validating old decks.`);
    return;
  }
  const [, , topicPart, configPart] = match;
  if (/^(Mdeck|deck|slides|output|dist)$/i.test(configPart) || /Mdeck$/i.test(dirName)) {
    errors.push(`${msg} Config segment must describe the actual template/theme/motion, not a generic output type.`);
  }
  if (topicPart.length < 2) {
    errors.push(`${msg} Content topic segment is too short to describe the deck.`);
  }

  const styleAliases = STYLE_NAME_ALIASES[styleId] || [styleId].filter(Boolean);
  if (styleAliases.length && !includesAny(configPart, styleAliases)) {
    errors.push(`Global: output directory config segment "${configPart}" must include the selected template/style name, e.g. ${styleAliases[0]}.`);
  }

  const themeId = detectThemeIdFromHtml(html);
  const themeAliases = THEME_NAME_ALIASES[themeId] || [themeId].filter(Boolean);
  if (themeAliases.length && !includesAny(configPart, themeAliases)) {
    errors.push(`Global: output directory config segment "${configPart}" must include the selected theme/color, e.g. ${themeAliases[0]}.`);
  } else if (!themeAliases.length) {
    warnings.push('Global: cannot infer preset theme from theme-link; custom theme directories should include a human theme/color label in the config segment.');
  }

  const motionId = detectMotionIdFromHtml(html);
  const motionAliases = MOTION_NAME_ALIASES[motionId] || [];
  if (motionAliases.length && !includesAny(configPart, motionAliases)) {
    errors.push(`Global: output directory config segment "${configPart}" must include the selected motion label, e.g. ${motionAliases[0]}.`);
  }
}

function checkStyleIsolation(slides, html, styleId, errors) {
  const styleConf = REGISTRY.styles.find(s => s.id === styleId);
  const registered = styleConf?.styleIsolation;
  const fallback = STYLE_GUARDS[styleId];
  const guard = registered ? {
    foreignLayoutValue: registered.forbidLayoutPattern ? new RegExp(registered.forbidLayoutPattern, 'i') : null,
    foreignLayouts: fallback?.foreignLayouts,
    foreignClasses: registered.forbidClasses || fallback?.foreignClasses || [],
    msg: fallback?.msg || `${styleId} deck contains foreign style layout/class.`
  } : fallback;
  if (!guard) return;
  const hasForeignLayout = guard.foreignLayoutValue
    ? [...html.matchAll(/\bdata-layout="([^"]+)"/gi)].some(m => guard.foreignLayoutValue.test(m[1]))
    : guard.foreignLayouts?.test(html);
  if (hasForeignLayout) {
    errors.push(`Global: ${guard.msg}`);
  }
  const forbidden = new Set(guard.foreignClasses);
  slides.forEach(s => {
    for (const m of s.html.matchAll(/\bclass="([^"]+)"/gi)) {
      const hit = m[1].split(/\s+/).find(c => forbidden.has(c));
      if (hit) addError(s.idx, `${guard.msg} Offending class: .${hit}`);
    }
  });
}

checkStyleIsolation(slides, htmlStripped, styleId, errors);
checkOutputDirectoryName(file, errors, warnings, allowLegacyDir, styleId, htmlStripped);

// 1. <title> 不含 [必填]
if (/<title>[^<]*\[必填\]/.test(html)) {
  errors.push('Global: <title> still contains [必填] placeholder.');
}

// 2. 不含 {{ 残留占位符
if (/\{\{/.test(html)) {
  errors.push('Global: index.html contains {{ ... }} placeholder (not replaced).');
}

// 3. 每个 slide 主题类。Editorial 必写 light/dark；Swiss 允许默认 paper、grey、accent、split。
slides.forEach(s => {
  if (!isSwiss() && !/\b(light|dark)\b/.test(s.tag)) {
    addError(s.idx, 'missing theme class (light or dark).');
  }
});

// 4. 连续 3 个 slide 同主题
let prev1 = null, prev2 = null;
slides.forEach(s => {
  const theme = inferTheme(s);
  if (theme && theme === prev1 && theme === prev2) {
    addError(s.idx, `3 consecutive slides share theme "${theme}" — breaks rhythm.`);
  }
  prev2 = prev1; prev1 = theme;
});

// 5. Editorial ≥6 页时必须有 ≥1 hero dark + ≥1 hero light。
// Swiss 的 accent/split/S01/S10 已承担封面/收束职责，不套用 editorial hero 节奏。
if (!isSwiss() && slides.length >= 6) {
  const hasHeroDark = slides.some(s => /\bhero\b.*\bdark\b|\bdark\b.*\bhero\b/.test(s.tag));
  const hasHeroLight = slides.some(s => /\bhero\b.*\b light\b|\b light\b.*\bhero\b/.test(s.tag));
  if (!hasHeroDark) errors.push('Global: ≥6 slides but no "hero dark" page found.');
  if (!hasHeroLight) errors.push('Global: ≥6 slides but no "hero light" page found.');
}

// 6. grid-2-*-* 种类数 ≥ 2（grid 比例不能单一）
const gridVariants = new Set();
slides.forEach(s => {
  const m = s.html.match(/grid-2-(\d+-\d+)/g);
  if (m) m.forEach(v => gridVariants.add(v.replace('grid-2-', '')));
});
if (slides.length >= 4 && gridVariants.size === 1) {
  warnings.push(`Global: only ${gridVariants.size} grid ratio(s) used — consider mixing proportions.`);
}

// 7. hero 页数 / 总页数 ≤ 1/3
const heroCount = slides.filter(s => /\bhero\b/.test(s.tag)).length;
if (slides.length >= 6 && heroCount / slides.length > 0.4) {
  warnings.push(`Global: ${heroCount}/${slides.length} hero pages (>40%) — too many, may exhaust audience.`);
}

// 8. 微动/沉浸模式：每页至少一个 data-anim
//    （静态模式允许不写 data-anim；校验脚本不强加，因为无法判断 deck 用的哪种模式）
//    默认行为：不报错（仅当明确指定了 motion 时才校验）
//    留作：未来加 --motion=subtle|cinematic 参数时启用

// 9. kbd nav 必备：nav.js 引入了
if (!/nav\.js/.test(html)) {
  errors.push('Global: nav.js not loaded.');
}
if (!/fit\.js/.test(html)) {
  errors.push('Global: fit.js not loaded. Deck must include content fitting to avoid viewport overflow.');
}

// 10. theme-link 必须存在
if (!/id="theme-link"/.test(html)) {
  errors.push('Global: <link id="theme-link"> not found.');
}
const themeHref = html.match(/<link\b[^>]*id="theme-link"[^>]*href="([^"]+)"/)?.[1] || '';
const bodyThemeList = html.match(/<body[^>]*\bdata-theme-list="([^"]+)"/)?.[1] || '';
if (bodyThemeList && /theme\.css(?:\?|#|$)/.test(themeHref)) {
  warnings.push('Global: data-theme-list is present but theme-link points to css/theme.css. T key stays locked for custom theme; use a concrete preset file like css/ikb-blue.css to enable cycling.');
}

// 11. 通用左右翻页按钮必须存在
if (!/id="nav-btns"/.test(html)) {
  errors.push('Global: #nav-btns container not found. All deck styles must expose prev/next page buttons.');
}
if (!/id="btn-prev"/.test(html) || !/id="btn-next"/.test(html)) {
  errors.push('Global: #btn-prev and #btn-next buttons are required for visible page navigation.');
}
if (!/id="btn-theme"/.test(html)) {
  warnings.push('Global: #btn-theme not found in template. nav.js will create it at runtime, but new decks should include the visible T theme button.');
}

// 12. 跨风格 surface 可读性：拦截深字深底、浅字浅底，并要求局部底色声明 surface。
checkSurfaceContrastRules(slides, errors, warnings);

// 13. Swiss 颜色/字体可读性：拦截过粗大标题和圆角；颜色冲突由通用 surface 规则处理。
if (isSwiss()) {
  checkSwissCoverTheme(slides, errors);
  checkSwissStaticStyleRules(slides, errors, warnings);
}
checkOverflowRisk(slides, warnings);

// ============= 风格专属规则（从 validate-rules.json 读） =============
if (styleId) {
  const styleConf = REGISTRY.styles.find(s => s.id === styleId);
  const rulesRelPath = styleConf?.validateRules || styleConf?.files?.validateRules;
  const rulesPath = rulesRelPath
    ? join(SKILL_ROOT, rulesRelPath)
    : null;
  if (rulesPath && existsSync(rulesPath)) {
    const rulesDoc = JSON.parse(readFileSync(rulesPath, 'utf8'));
    for (const rule of rulesDoc.rules || []) {
      try {
        applyRule(rule, slides, htmlStripped, errors, warnings, allowExperimental);
      } catch (e) {
        warnings.push(`Rule ${rule.id}: execution error — ${e.message}`);
      }
    }
  }
}

function applyRule(rule, slides, html, errors, warnings, allowExp) {
  if (rule.id === 'S-001' || rule.check === 'require-attr') {
    slides.forEach(s => {
      const re = new RegExp(`<section\\b[^>]*class="[^"]*\\b${rule.selector.replace('.', '')}\\b[^"]*"[^>]*>`, 'g');
      const tag = [...s.html.matchAll(re)][0]?.[0] || '';
      const m = tag.match(new RegExp(`\\b${rule.attr}="([^"]*)"`, 'i'));
      if (!m) { addError(s.idx, `Rule ${rule.id}: missing attribute ${rule.attr} (${rule.description})`); return; }
      const experimentalLayouts = ['P23','P24','SWISS-IMAGE-SPLIT','EVIDENCE-GRID','THREE-CIRCLES'];
      if (allowExp && rule.attr === 'data-layout' && experimentalLayouts.includes(m[1])) return;
      if (rule.pattern && !new RegExp(rule.pattern).test(m[1])) {
        addError(s.idx, `Rule ${rule.id}: ${rule.attr}="${m[1]}" doesn't match ${rule.pattern}`);
      }
    });
    return;
  }
  if (rule.id === 'S-002' || rule.check === 'allowlist-attr') {
    slides.forEach(s => {
      const m = s.html.match(new RegExp(`\\b${rule.attr}="([^"]*)"`));
      if (!m && rule.required) {
        addError(s.idx, `Rule ${rule.id}: missing required attribute ${rule.attr} (${rule.description})`);
        return;
      }
      const experimentalLayouts = ['P23','P24','SWISS-IMAGE-SPLIT','EVIDENCE-GRID','THREE-CIRCLES'];
      if (m && allowExp && rule.attr === 'data-layout' && experimentalLayouts.includes(m[1])) return;
      if (m && !rule.allowlist.includes(m[1])) {
        addError(s.idx, `Rule ${rule.id}: ${rule.attr}="${m[1]}" not in allowlist [${rule.allowlist.join(',')}]`);
      }
    });
    return;
  }
  if (rule.check === 'swiss-no-center-title') {
    const statementLayouts = ['S03','S09','S10','SWISS-COVER-ASCII','SWISS-CLOSING-ASCII'];
    slides.forEach(s => {
      const layout = s.tag.match(/\bdata-layout="([^"]+)"/)?.[1];
      if (!statementLayouts.includes(layout) && /text-align\s*:\s*center/i.test(s.html.slice(0, 1800))) {
        addError(s.idx, `Rule ${rule.id}: top title area contains text-align:center (${rule.description})`);
      }
    });
    return;
  }
  if (rule.check === 'swiss-no-centered-heading') {
    const statementLayouts = ['S03','S09','S10','SWISS-COVER-ASCII','SWISS-CLOSING-ASCII'];
    slides.forEach(s => {
      const layout = s.tag.match(/\bdata-layout="([^"]+)"/)?.[1];
      const topChunk = s.html.slice(0, 1800);
      if (!statementLayouts.includes(layout) && /align-self\s*:\s*center/i.test(topChunk) && /<h[12]\b/i.test(topChunk)) {
        addError(s.idx, `Rule ${rule.id}: top heading appears centered (${rule.description})`);
      }
    });
    return;
  }
  if (rule.check === 'swiss-no-svg-text') {
    slides.forEach(s => {
      const layout = s.tag.match(/\bdata-layout="([^"]+)"/)?.[1] || 'unknown';
      if (/<svg\b[\s\S]*?<text\b/i.test(s.html)) {
        addError(s.idx, `Rule ${rule.id}: SVG contains visible <text> in ${layout} (${rule.description})`);
      }
    });
    return;
  }
  if (rule.check === 'swiss-img-requires-slot') {
    slides.forEach(s => {
      for (const m of s.html.matchAll(/<img\s+[^>]*src="(images\/[^"]+)"/g)) {
        if (!/data-image-slot=/.test(m[0])) {
          addError(s.idx, `Rule ${rule.id}: <img src="${m[1]}"> missing data-image-slot (${rule.description})`);
        }
      }
    });
    return;
  }
  if (rule.check === 'swiss-s15-s16-ratio') {
    slides.forEach(s => {
      const layout = s.tag.match(/\bdata-layout="([^"]+)"/)?.[1];
      if (layout !== 'S15' && layout !== 'S16') return;
      for (const m of s.html.matchAll(/class="([^"]*\bframe-img\b[^"]*)"/gi)) {
        const cls = m[1];
        if (!/\br-(?:21x9|16x10)\b/.test(cls)) {
          addError(s.idx, `Rule ${rule.id}: S15/S16 image group must use .frame-img.r-21x9 or .frame-img.r-16x10`);
        }
        if (/\bfit-contain\b/.test(cls)) {
          addError(s.idx, `Rule ${rule.id}: .fit-contain is forbidden for S15/S16 regenerated images`);
        }
      }
    });
    return;
  }
  if (rule.check === 'swiss-s22-hero') {
    slides.forEach(s => {
      const layout = s.tag.match(/\bdata-layout="([^"]+)"/)?.[1];
      if (layout !== 'S22') return;
      if (!/<img\s+[^>]*data-image-slot="[^"]*s22-hero-21x9[^"]*"/i.test(s.html)) {
        addError(s.idx, `Rule ${rule.id}: S22 must include data-image-slot="s22-hero-21x9"`);
      }
      if (/object-position\s*:\s*top\s*center/i.test(s.html)) {
        addError(s.idx, `Rule ${rule.id}: S22 cannot use object-position:top center`);
      }
    });
    return;
  }
  if (rule.check === 'style-cover-accent') {
    const cover = slides[0];
    if (!cover) return;
    const hasThemeSignal = hasClass(cover.tag, 'accent') ||
      /\bhero\b/i.test(cover.tag) ||
      /background(?:-color)?\s*:\s*var\(--accent\)/i.test(cover.html) ||
      /color\s*:\s*var\(--accent\)/i.test(cover.html) ||
      /\b(data-theme-signal|theme-signal|accent-block|card-accent)\b/.test(cover.html);
    if (!hasThemeSignal) {
      addError(1, `Rule ${rule.id}: cover does not visibly use the selected theme accent or hero surface (${rule.description})`);
    }
    return;
  }
  if (rule.check === 'max-font-weight') {
    checkMaxFontWeightRule(rule, slides, errors);
    return;
  }
  // 其他规则（E-001/S-003/E-002/S-004）由 cheerio-style 解析更稳，本脚本保守跳过
  // 实际检查靠人工对照 checklist.md + grep
  if (rule.check === 'require-style' && rule.style === 'border-radius' && rule.value === '0') {
    checkNoBorderRadius(slides, errors, rule.id);
    return;
  }
  if (rule.id === 'E-001' || rule.id === 'E-003' || rule.id === 'S-003' || rule.id === 'S-004' || rule.check === 'require-style' || rule.check === 'forbid-style') {
    // 静态样式类规则需要解析 style=""，本脚本不实现（标注为待办）
    warnings.push(`Rule ${rule.id}: static-style rule not auto-checked. See ${rule.description}`);
    return;
  }
  if (rule.id === 'E-002' || rule.check === 'max-font-size') {
    // 同上
    warnings.push(`Rule ${rule.id}: static-style rule not auto-checked. See ${rule.description}`);
    return;
  }
  warnings.push(`Rule ${rule.id}: unknown check type "${rule.check}" — skipped.`);
}

function checkSwissStaticStyleRules(slides, errors, warnings) {
  checkNoBorderRadius(slides, errors, 'SW-E2');
  checkMaxFontWeightRule({ id: 'SW-E1', selector: '.h-hero,.h-xl,.h-hero-zh,.h-xl-zh', max: 300 }, slides, errors);
}

function checkSurfaceContrastRules(slides, errors, warnings) {
  slides.forEach(s => {
    const slideSurface = inferSurfaceFromSlide(s);
    const sectionStyle = getStyleAttr(s.tag);
    checkTextAgainstSurface(s.idx, slideSurface, sectionStyle, 'slide section', errors);

    for (const m of s.html.matchAll(/<([a-z0-9-]+)\b([^>]*)>/gi)) {
      const tagName = m[1].toLowerCase();
      if (tagName === 'section' || tagName === 'script' || tagName === 'style') continue;
      const attrs = m[2] || '';
      const style = attrs.match(/\bstyle="([^"]*)"/i)?.[1] || '';
      const cls = attrs.match(/\bclass="([^"]*)"/i)?.[1] || '';
      const explicitSurface = inferSurfaceFromAttrs(attrs, style, cls);
      const surface = explicitSurface || slideSurface;

      if (style) checkTextAgainstSurface(s.idx, surface, style, `<${tagName}>`, errors);

      const hasLocalBackground = /background(?:-color)?\s*:/i.test(style) ||
        /\b(?:b-ink|b-accent|hero-ink-col|ink-banner-full|card-ink|card-accent|accent-block|ink-block|grey-block|card-fill)\b/i.test(cls);
      const hasSurfaceMarker = /\b(?:surface-light|surface-dark|surface-accent|on-light|on-dark|on-accent)\b/i.test(cls) ||
        /\bdata-surface="(?:light|dark|accent)"/i.test(attrs);
      if (hasLocalBackground && !hasSurfaceMarker && !/color\s*:/i.test(style)) {
        addWarning(s.idx, `local background on <${tagName}> has no surface marker. Add .on-dark/.on-light/.on-accent or data-surface so text tokens follow the local background.`);
      }
    }
  });
}

function inferSurfaceFromSlide(slide) {
  const theme = inferTheme(slide);
  if (theme === 'dark' || theme === 'hero') return 'dark';
  if (theme === 'accent') return 'accent';
  return 'light';
}

function inferSurfaceFromAttrs(attrs, style, cls) {
  if (/\bdata-surface="dark"/i.test(attrs) || /\b(?:surface-dark|on-dark)\b/i.test(cls)) return 'dark';
  if (/\bdata-surface="light"/i.test(attrs) || /\b(?:surface-light|on-light)\b/i.test(cls)) return 'light';
  if (/\bdata-surface="accent"/i.test(attrs) || /\b(?:surface-accent|on-accent)\b/i.test(cls)) return 'accent';
  if (/\b(?:b-ink|hero-ink-col|ink-banner-full|card-ink|ink-block)\b/i.test(cls)) return 'dark';
  if (/\b(?:b-accent|card-accent|accent-block)\b/i.test(cls)) return 'accent';
  if (/\b(?:grey-block|card-fill)\b/i.test(cls)) return 'light';
  if (/background(?:-color)?\s*:\s*var\(--(?:ink|ink-tint|panel)\)/i.test(style)) return 'dark';
  if (/background(?:-color)?\s*:\s*var\(--accent\)/i.test(style)) return 'accent';
  if (/background(?:-color)?\s*:\s*var\(--(?:paper|paper-tint|grey-1|grey-2)\)/i.test(style)) return 'light';
  if (/background(?:-color)?\s*:\s*#(?:0[0-9a-f]{2,4}|1[0-9a-f]{2,4}|2[0-9a-f]{2,4})\b/i.test(style)) return 'dark';
  if (/background(?:-color)?\s*:\s*#(?:e[0-9a-f]{2,4}|f[0-9a-f]{2,4})\b/i.test(style)) return 'light';
  return '';
}

function checkTextAgainstSurface(slideIdx, surface, style, context, errors) {
  if (!surface || !/color\s*:/i.test(style)) return;
  if ((surface === 'dark' || surface === 'accent') && isDarkTextColor(style)) {
    addError(slideIdx, `surface contrast conflict: ${context} uses dark text on ${surface} surface. Use .on-dark/.on-accent with var(--surface-text), or change text to var(--paper)/var(--accent-on).`);
  }
  if (surface === 'light' && isLightTextColor(style)) {
    addError(slideIdx, `surface contrast conflict: ${context} uses light text on light surface. Use .on-light with var(--surface-text), or change text to var(--ink).`);
  }
}

function isDarkTextColor(style) {
  return /color\s*:\s*var\(--(?:ink|text-on-light)\)/i.test(style) ||
    /color\s*:\s*#(?:0[0-9a-f]{2,5}|1[0-9a-f]{2,5}|2[0-9a-f]{2,5}|333(?:333)?|000(?:000)?)\b/i.test(style);
}

function isLightTextColor(style) {
  return /color\s*:\s*var\(--(?:paper|text-on-dark)\)/i.test(style) ||
    /color\s*:\s*#(?:e[0-9a-f]{2,5}|f[0-9a-f]{2,5}|fff(?:fff)?|eee(?:eee)?)\b/i.test(style);
}

function checkOverflowRisk(slides, warnings) {
  slides.forEach(s => {
    for (const m of s.html.matchAll(/<h[1-2]\b[^>]*>([\s\S]*?)<\/h[1-2]>/gi)) {
      const text = m[1].replace(/<[^>]*>/g, '').replace(/\s+/g, '').trim();
      if (text.length > 32 && !/\bfit-safe-text\b/.test(m[0])) {
        addWarning(s.idx, `heading has ${text.length} chars without .fit-safe-text; long titles can drift or overflow.`);
      }
    }
    const statLike = [...s.html.matchAll(/\b(class="[^"]*(?:stat-card|kpi-|ledger-row|sub-card|force-card)[^"]*")/g)].length;
    if (statLike >= 8 && !/\bfit-shell\b/.test(s.html)) {
      addWarning(s.idx, `contains ${statLike} dense stat/card elements without .fit-shell; wrap the dense body, split the page, or use a lower-density layout.`);
    }
  });
}

function checkSwissCoverTheme(slides, errors) {
  const cover = slides[0];
  if (!cover) return;
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

function checkNoBorderRadius(slides, errors, ruleId) {
  slides.forEach(s => {
    for (const m of s.html.matchAll(/<([a-z0-9-]+)\b[^>]*style="([^"]*\bborder-radius\s*:\s*([^;"']+)[^"]*)"[^>]*>/gi)) {
      const raw = m[3].trim().toLowerCase();
      if (!/^(0|0px|0rem|0em|0%)\s*!important?$/.test(raw)) {
        addError(s.idx, `Rule ${ruleId}: Swiss forbids border-radius="${raw}" in generated slide HTML.`);
      }
    }
  });
}

function checkMaxFontWeightRule(rule, slides, errors) {
  const max = Number(rule.max ?? 300);
  const classes = String(rule.selector || '')
    .split(',')
    .map(s => s.trim().replace(/^\./, ''))
    .filter(Boolean);
  slides.forEach(s => {
    for (const m of s.html.matchAll(/<(h[1-6]|[a-z0-9-]+)\b([^>]*)>/gi)) {
      const tagName = m[1].toLowerCase();
      const attrs = m[2];
      const cls = attrs.match(/\bclass="([^"]*)"/i)?.[1] || '';
      const isTarget = /^h[12]$/.test(tagName) || classes.some(c => new RegExp(`\\b${c}\\b`).test(cls));
      if (!isTarget) continue;
      const style = attrs.match(/\bstyle="([^"]*)"/i)?.[1] || '';
      const weight = style.match(/\bfont-weight\s*:\s*(\d+)/i)?.[1];
      if (weight && Number(weight) > max) {
        addError(s.idx, `Rule ${rule.id}: heading font-weight ${weight} exceeds Swiss max ${max}.`);
      }
    }
  });
}

function dedupeInPlace(list) {
  const seen = new Set();
  let write = 0;
  for (const item of list) {
    if (seen.has(item)) continue;
    seen.add(item);
    list[write++] = item;
  }
  list.length = write;
}

// ============= 输出 =============
dedupeInPlace(errors);
dedupeInPlace(warnings);

const styleName = REGISTRY.styles.find(s => s.id === styleId)?.name || styleId;
console.log(`\n  wtt-magazine-deck · validate-deck.mjs`);
console.log(`  File:   ${file}`);
console.log(`  Style:  ${styleName} (${styleId || 'unknown'})`);
console.log(`  Slides: ${slides.length}\n`);

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
