#!/usr/bin/env node
/* =============== wtt-magazine-deck · theme contract validator ==============
   Cross-style checks for theme switching and color readability.

   registry.json is the source of truth. This script prevents one-off template
   fixes from drifting away from the shared theme behavior.
*/
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REGISTRY_PATH = resolve(__dirname, '../assets/styles/registry.json');
const SKILL_ROOT = dirname(dirname(dirname(REGISTRY_PATH)));

if (!existsSync(REGISTRY_PATH)) {
  console.error('Cannot find assets/styles/registry.json');
  process.exit(2);
}

const registry = JSON.parse(readFileSync(REGISTRY_PATH, 'utf8'));
const errors = [];
const warnings = [];

checkCoreThemeControls();
for (const style of registry.styles || []) checkStyleThemeContract(style);

console.log('\n  wtt-magazine-deck · validate-theme-contract.mjs\n');
if (errors.length) {
  console.log(`  x ${errors.length} error(s):`);
  errors.forEach(e => console.log(`    - ${e}`));
  console.log('');
}
if (warnings.length) {
  console.log(`  ! ${warnings.length} warning(s):`);
  warnings.forEach(w => console.log(`    - ${w}`));
  console.log('');
}
if (!errors.length && !warnings.length) {
  console.log('  OK theme contract checks passed.\n');
} else if (!errors.length) {
  console.log(`  OK no errors, ${warnings.length} warning(s) (non-blocking).\n`);
}
process.exit(errors.length ? 1 : 0);

function checkCoreThemeControls() {
  const navJs = readIfExists(join(SKILL_ROOT, 'assets/core/nav.js'));
  const navCss = readIfExists(join(SKILL_ROOT, 'assets/core/nav.css'));
  if (!/window\.__cycleTheme\s*=/.test(navJs)) {
    errors.push('Core: nav.js must expose window.__cycleTheme for keyboard and button theme switching.');
  }
  if (!/btn-theme/.test(navJs)) {
    errors.push('Core: nav.js must create or bind #btn-theme so old decks get the same visible T control.');
  }
  if (!/#nav-tools/.test(navCss) || !/\.nav-tool/.test(navCss)) {
    errors.push('Core: nav.css must style #nav-tools and .nav-tool for the shared T theme button.');
  }
}

function checkStyleThemeContract(style) {
  const styleId = style.id;
  const files = style.files || {};
  const templatePath = resolveFromRoot(files.template);
  const themesDir = resolveFromRoot(files.themesDir);
  const defaultTheme = style.defaultTheme;
  const availableThemes = style.availableThemes || [];

  if (!styleId) errors.push('Registry: style entry missing id.');
  if (!defaultTheme) errors.push(`${styleId}: missing defaultTheme in registry.`);
  if (!availableThemes.length) errors.push(`${styleId}: availableThemes must contain at least one theme.`);
  if (defaultTheme && availableThemes.length && !availableThemes.includes(defaultTheme)) {
    errors.push(`${styleId}: defaultTheme "${defaultTheme}" is not listed in availableThemes.`);
  }

  const template = readIfExists(templatePath);
  if (!template) {
    errors.push(`${styleId}: template not found at ${files.template}.`);
  } else {
    checkTemplate(style, template);
  }

  if (!existsSync(themesDir)) {
    errors.push(`${styleId}: themesDir not found at ${files.themesDir}.`);
    return;
  }

  const themeFiles = new Set(readdirSync(themesDir).filter(f => f.endsWith('.css')).map(f => f.replace(/\.css$/, '')));
  for (const theme of availableThemes) {
    if (!themeFiles.has(theme)) {
      errors.push(`${styleId}: registry theme "${theme}" has no ${join(files.themesDir, `${theme}.css`)} file.`);
      continue;
    }
    checkThemeCss(style, theme, join(themesDir, `${theme}.css`));
  }
  for (const theme of themeFiles) {
    if (!availableThemes.includes(theme)) {
      warnings.push(`${styleId}: theme file "${theme}.css" exists but is not listed in registry availableThemes.`);
    }
  }
}

function checkTemplate(style, template) {
  const styleId = style.id;
  const defaultTheme = style.defaultTheme;
  const availableThemes = style.availableThemes || [];
  const href = template.match(/<link\b[^>]*id="theme-link"[^>]*href="([^"]+)"/)?.[1] || '';
  const themeListRaw = template.match(/<body[^>]*\bdata-theme-list="([^"]*)"/)?.[1] || '';
  const themeList = themeListRaw.split(',').map(s => s.trim()).filter(Boolean);

  if (!href) errors.push(`${styleId}: template must include <link id="theme-link" href="css/<defaultTheme>.css">.`);
  if (defaultTheme && !href.endsWith(`/${defaultTheme}.css`) && href !== `css/${defaultTheme}.css`) {
    errors.push(`${styleId}: template theme-link href "${href}" does not point to defaultTheme "${defaultTheme}".`);
  }
  if (!themeList.length) {
    errors.push(`${styleId}: template <body> must include data-theme-list with registry availableThemes.`);
  } else if (themeList.join(',') !== availableThemes.join(',')) {
    errors.push(`${styleId}: template data-theme-list must exactly match registry availableThemes order. Template=[${themeList.join(',')}] Registry=[${availableThemes.join(',')}]`);
  }
  if (!/id="btn-theme"/.test(template)) {
    errors.push(`${styleId}: template must include visible #btn-theme. nav.js can backfill old decks, but templates must expose it.`);
  }
}

function checkThemeCss(style, theme, file) {
  const vars = parseCssVars(readIfExists(file));
  const required = [
    '--ink',
    '--ink-rgb',
    '--paper',
    '--paper-rgb',
    '--paper-tint',
    '--ink-tint',
    '--accent',
    '--accent-2',
    '--accent-on',
  ];
  if (style.id === 'swiss') required.push('--accent-rgb', '--accent-bright');
  if (style.id === 'linear') required.push('--accent-rgb', '--accent-bright', '--panel', '--panel-rgb');
  for (const name of required) {
    if (!vars[name]) errors.push(`${style.id}/${theme}: missing required CSS variable ${name}.`);
  }

  const accent = vars['--accent'];
  const accentOn = vars['--accent-on'];
  if (isHex(accent) && isHex(accentOn)) {
    const ratio = contrastRatio(hexToRgb(accent), hexToRgb(accentOn));
    if (ratio < 4.5) {
      errors.push(`${style.id}/${theme}: --accent ${accent} and --accent-on ${accentOn} contrast is ${ratio.toFixed(2)}; must be >= 4.5.`);
    }
  } else {
    errors.push(`${style.id}/${theme}: --accent and --accent-on must be literal #RRGGBB values so contrast can be checked.`);
  }
}

function resolveFromRoot(rel) {
  return rel ? join(SKILL_ROOT, rel) : '';
}

function readIfExists(file) {
  return file && existsSync(file) ? readFileSync(file, 'utf8') : '';
}

function parseCssVars(css) {
  const vars = {};
  for (const m of css.matchAll(/(--[a-z0-9-]+)\s*:\s*([^;]+);/gi)) {
    vars[m[1]] = m[2].trim();
  }
  return vars;
}

function isHex(v) {
  return /^#[0-9a-fA-F]{6}$/.test(String(v || '').trim());
}

function hexToRgb(hex) {
  const raw = hex.trim().replace('#', '');
  return [0, 2, 4].map(i => parseInt(raw.slice(i, i + 2), 16));
}

function luminance(rgb) {
  return rgb.map(v => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  }).reduce((acc, v, i) => acc + v * [0.2126, 0.7152, 0.0722][i], 0);
}

function contrastRatio(a, b) {
  const l1 = luminance(a);
  const l2 = luminance(b);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}
