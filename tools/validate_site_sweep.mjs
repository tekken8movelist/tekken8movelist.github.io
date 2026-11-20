// Site-wide browser sweep: every published page, four widths, both themes.
//
// validate_season2.mjs checks the generator pages in depth at 1480px and one
// phone width. Everything found in the 2026-11-19 audit sat outside that:
// the hubs, the five pipeline pages, tablet widths (law clipped 19 names at
// 700-820px), and the light theme (pipeline footers at 2.7:1). This sweep is
// shallow but wide, so a defect of that shape fails the gate instead of
// waiting for someone to go looking:
//
//   every page x 360/768/1024/1480   no horizontal page overflow, no script
//                                    error, no broken local image
//   character pages, same widths     no table text cut off by an ellipsis or
//                                    hidden overflow (both axes)
//   character pages, both themes     footer text and tag badges at WCAG AA
//
// The network is cut off: everything a page needs is local, and an external
// request (fonts, analytics) failing must not count as a page error.

import { createRequire } from 'node:module';
import { existsSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

// SITE_ROOT points the sweep at another build (e.g. an older one, to prove it fails)
const siteRoot = process.env.SITE_ROOT
  ? resolve(process.env.SITE_ROOT)
  : resolve(dirname(fileURLToPath(import.meta.url)), '..', 'docs');
const trees = ['', 'zh-Hant', 'en'];
const widths = [
  { width: 360, height: 780, isMobile: true },
  { width: 768, height: 1024, isMobile: false },
  { width: 1024, height: 900, isMobile: false },
  { width: 1480, height: 1000, isMobile: false },
];
const CONTRAST_WIDTH = 1480;

function findChrome() {
  if (process.env.CHROME_PATH) return resolve(process.env.CHROME_PATH);
  const candidates = [
    process.env.ProgramFiles && join(process.env.ProgramFiles, 'Google', 'Chrome', 'Application', 'chrome.exe'),
    process.env['ProgramFiles(x86)'] && join(process.env['ProgramFiles(x86)'], 'Google', 'Chrome', 'Application', 'chrome.exe'),
    process.env.LOCALAPPDATA && join(process.env.LOCALAPPDATA, 'Google', 'Chrome', 'Application', 'chrome.exe'),
  ].filter(Boolean);
  const found = candidates.find((candidate) => existsSync(candidate));
  if (!found) throw new Error(`Chrome was not found; set CHROME_PATH. Checked: ${candidates.join(', ')}`);
  return found;
}

const pages = trees.flatMap((tree) => readdirSync(join(siteRoot, tree))
  .filter((name) => name.endsWith('.html'))
  .map((name) => ({ rel: tree ? `${tree}/${name}` : name, file: join(siteRoot, tree, name), character: name.endsWith('_tk8_movelist.html') })));
if (pages.length < 100) throw new Error(`only ${pages.length} pages found under ${siteRoot}`);

// runs in the page
function inspect({ character, checkContrast }) {
  const problems = [];
  const de = document.documentElement;
  const overflow = de.scrollWidth - de.clientWidth;
  if (overflow > 0) {
    const culprits = [];
    for (const el of document.querySelectorAll('body *')) {
      const box = el.getBoundingClientRect();
      if (box.width > 0 && box.right > de.clientWidth + 1 && getComputedStyle(el).position !== 'fixed') {
        culprits.push(`${el.tagName.toLowerCase()}.${String(el.className).split(' ')[0]}`);
        if (culprits.length >= 3) break;
      }
    }
    problems.push(`page overflows horizontally by ${overflow}px (${culprits.join(', ')})`);
  }
  for (const img of document.images) {
    if (img.isConnected && img.complete && img.naturalWidth === 0) problems.push(`broken image ${img.getAttribute('src')}`);
  }
  if (character) {
    const clipped = [];
    for (const el of document.querySelectorAll('td, th, h2')) {
      if (el.offsetParent === null || el.clientWidth === 0) continue;
      const cs = getComputedStyle(el);
      const hidesX = cs.overflowX !== 'visible' || cs.textOverflow === 'ellipsis';
      const hidesY = cs.overflowY !== 'visible';
      if ((hidesX && el.scrollWidth > el.clientWidth + 1) || (hidesY && el.scrollHeight > el.clientHeight + 1)) {
        clipped.push(`"${el.textContent.trim().slice(0, 20)}"`);
      }
    }
    if (clipped.length) problems.push(`${clipped.length} cell(s) cut off: ${clipped.slice(0, 4).join(', ')}`);
  }
  if (checkContrast) {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const rgba = (value) => {
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillStyle = '#000';
      ctx.fillStyle = value;
      ctx.fillRect(0, 0, 1, 1);
      const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data;
      return a === 0 ? { r: 0, g: 0, b: 0, a: 0 } : { r: (r * 255) / a, g: (g * 255) / a, b: (b * 255) / a, a: a / 255 };
    };
    const over = (top, under) => ({
      r: top.r * top.a + under.r * (1 - top.a),
      g: top.g * top.a + under.g * (1 - top.a),
      b: top.b * top.a + under.b * (1 - top.a),
    });
    const background = (el) => {
      const layers = [];
      for (let node = el; node; node = node.parentElement) {
        const layer = rgba(getComputedStyle(node).backgroundColor);
        if (layer.a > 0.01) { layers.push(layer); if (layer.a >= 1) break; }
      }
      return layers.reverse().reduce((under, top) => over(top, under), { r: 255, g: 255, b: 255 });
    };
    const luminance = (c) => {
      const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
      return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
    };
    for (const theme of ['dark', 'light']) {
      de.classList.toggle('dark', theme === 'dark');
      const weak = new Set();
      for (const el of document.querySelectorAll('footer, footer *, span.tag')) {
        if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        let opacity = 1;
        for (let node = el; node; node = node.parentElement) opacity *= Number(getComputedStyle(node).opacity);
        const bg = background(el);
        const ink = rgba(cs.color);
        const fg = over({ ...ink, a: ink.a * opacity }, bg);
        const [hi, lo] = [luminance(fg), luminance(bg)].sort((x, y) => y - x);
        const ratio = (hi + 0.05) / (lo + 0.05);
        const size = parseFloat(cs.fontSize);
        const large = size >= 24 || (size >= 18.66 && Number(cs.fontWeight) >= 700);
        if (ratio < (large ? 3 : 4.5)) weak.add(`${el.tagName.toLowerCase()}${el.className ? '.' + el.className : ''} ${ratio.toFixed(2)}:1`);
      }
      if (weak.size) problems.push(`${theme} theme below AA: ${[...weak].slice(0, 4).join(', ')}`);
    }
  }
  return problems;
}

const browser = await chromium.launch({ executablePath: findChrome(), headless: true });
const failures = [];
let checks = 0;
try {
  for (const viewport of widths) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      isMobile: viewport.isMobile,
      hasTouch: viewport.isMobile,
    });
    await context.route(/^https?:/, (route) => route.abort());
    const page = await context.newPage();
    let errors = [];
    page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
    page.on('console', (message) => {
      // an aborted external request is this sweep's own doing
      if (message.type() === 'error' && !/net::|Failed to load resource/.test(message.text())) {
        errors.push(`console: ${message.text()}`);
      }
    });
    page.on('requestfailed', (request) => {
      if (request.url().startsWith('file:')) errors.push(`missing local file ${request.url().split('/docs/')[1]}`);
    });
    for (const target of pages) {
      errors = [];
      await page.goto(pathToFileURL(target.file).href, { waitUntil: 'load' });
      const problems = await page.evaluate(inspect, {
        character: target.character,
        checkContrast: target.character && viewport.width === CONTRAST_WIDTH,
      });
      problems.push(...errors);
      checks += 1;
      if (problems.length) failures.push({ page: target.rel, width: viewport.width, problems });
    }
    await context.close();
  }
} finally {
  await browser.close();
}

console.log(JSON.stringify({ pages: pages.length, checks, failureCount: failures.length, failures }, null, 2));
process.exitCode = failures.length ? 1 : 0;
