import { existsSync, mkdirSync, readdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, isAbsolute, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..');
const siteRoot = resolve(repoRoot, 'docs');
const allPages = {
  jin: 'jin_tk8_movelist.html',
  anna: 'anna_tk8_movelist.html',
  fahkumram: 'fahkumram_tk8_movelist.html',
  armor_king: 'armorking_tk8_movelist.html',
  miary_zo: 'miaryzo_tk8_movelist.html',
  kazuya: 'kazuya_tk8_movelist.html',
  paul: 'paul_tk8_movelist.html',
  king: 'king_tk8_movelist.html',
  lars: 'lars_tk8_movelist.html',
  jack8: 'jack_tk8_movelist.html',
  nina: 'nina_tk8_movelist.html',
  leroy: 'leroy_tk8_movelist.html',
  asuka: 'asuka_tk8_movelist.html',
  lili: 'lili_tk8_movelist.html',
  bryan: 'bryan_tk8_movelist.html',
  hwoarang: 'hwoarang_tk8_movelist.html',
  claudio: 'claudio_tk8_movelist.html',
  azucena: 'azucena_tk8_movelist.html',
  raven: 'raven_tk8_movelist.html',
  leo: 'leo_tk8_movelist.html',
  steve: 'steve_tk8_movelist.html',
  kuma: 'kuma_tk8_movelist.html',
  panda: 'panda_tk8_movelist.html',
  yoshimitsu: 'yoshimitsu_tk8_movelist.html',
  shaheen: 'shaheen_tk8_movelist.html',
  dragunov: 'dragunov_tk8_movelist.html',
  feng: 'feng_tk8_movelist.html',
  lee: 'lee_tk8_movelist.html',
  alisa: 'alisa_tk8_movelist.html',
  zafina: 'zafina_tk8_movelist.html',
  devil_jin: 'deviljin_tk8_movelist.html',
  victor: 'victor_tk8_movelist.html',
  reina: 'reina_tk8_movelist.html',
  eddy: 'eddy_tk8_movelist.html',
  lidia: 'lidia_tk8_movelist.html',
  heihachi: 'heihachi_tk8_movelist.html',
};
// Locale trees. Simplified keeps the full state matrix -- it is the indexed
// tree and the one every layout rule was tuned against. The other two run a
// reduced matrix: their layout differs from it in exactly two ways (row height
// and the English column shares), and running 10 states each would triple a
// gate that already takes four minutes for no coverage the reduced set misses.
//
// Row heights are measured post-`zoom: 1.25`, so 38px of CSS lands near 47.5
// and English's 46px lands near 57.5.
const locales = [
  {
    id: 'hans',
    dir: '',
    rowHeight: [46, 49],
    states: [
      { width: 1480, theme: 'dark', mode: 'gfx', stackedLayout: false },
      { width: 1480, theme: 'dark', mode: 'nn', stackedLayout: false },
      { width: 1480, theme: 'dark', mode: 'txt', stackedLayout: false },
      { width: 1480, theme: 'light', mode: 'gfx', stackedLayout: false },
      { width: 1480, theme: 'light', mode: 'nn', stackedLayout: false },
      { width: 1480, theme: 'light', mode: 'txt', stackedLayout: false },
    ],
    responsive: [1280, 1024, 760, 390],
    full: true,
  },
  {
    id: 'hant',
    dir: 'zh-Hant',
    rowHeight: [46, 49],
    states: [
      { width: 1480, theme: 'dark', mode: 'gfx', stackedLayout: false },
      { width: 1480, theme: 'light', mode: 'txt', stackedLayout: false },
      { width: 1480, theme: 'dark', mode: 'nn', stackedLayout: false },
    ],
    responsive: [390],
    full: false,
  },
  {
    id: 'en',
    dir: 'en',
    rowHeight: [56, 60],
    states: [
      { width: 1480, theme: 'dark', mode: 'gfx', stackedLayout: false },
      { width: 1480, theme: 'light', mode: 'txt', stackedLayout: false },
      { width: 1480, theme: 'dark', mode: 'nn', stackedLayout: false },
    ],
    responsive: [390],
    full: false,
  },
];

const onlyCharacters = process.env.CHARACTERS
  ? new Set(process.env.CHARACTERS.split(',').map((value) => value.trim()))
  : null;
const pages = Object.fromEntries(
  Object.entries(allPages).filter(([key]) => !onlyCharacters || onlyCharacters.has(key)),
);
if (!Object.keys(pages).length) {
  throw new Error(`CHARACTERS filter matched no pages: ${process.env.CHARACTERS}`);
}
// whatever is published but not generated: the one-shot pipeline pages. They
// now exist in all three locales -- Traditional converted from the published
// Simplified page (build_legacy_hant.py) and English rebuilt from it against
// Wavu's own move names (build_legacy_en.py) -- so the legend check runs over
// every tree that has them.
const legacyNames = readdirSync(siteRoot)
  .filter((name) => name.endsWith('_tk8_movelist.html'))
  .filter((name) => !Object.values(allPages).includes(name))
  .filter((name) => !onlyCharacters || onlyCharacters.has(name.replace('_tk8_movelist.html', '')))
  .sort();
const legacyPages = [];
for (const locale of locales) {
  const dir = locale.dir ? join(siteRoot, locale.dir) : siteRoot;
  for (const name of legacyNames) {
    if (existsSync(join(dir, name))) legacyPages.push({ name, dir, locale: locale.id });
  }
}
const notationButtons = { gfx: '#ng', nn: '#nn', txt: '#nt' };
const themeButtons = { dark: '#thd', light: '#thl' };
const screenshotDir = process.env.SCREENSHOT_DIR
  ? resolve(process.cwd(), process.env.SCREENSHOT_DIR)
  : null;

function findChrome() {
  if (process.env.CHROME_PATH) {
    const configured = isAbsolute(process.env.CHROME_PATH)
      ? process.env.CHROME_PATH
      : resolve(process.cwd(), process.env.CHROME_PATH);
    if (!existsSync(configured)) {
      throw new Error(`CHROME_PATH does not exist: ${configured}`);
    }
    return configured;
  }

  const candidates = [
    process.env.ProgramFiles && join(process.env.ProgramFiles, 'Google', 'Chrome', 'Application', 'chrome.exe'),
    process.env['ProgramFiles(x86)'] && join(process.env['ProgramFiles(x86)'], 'Google', 'Chrome', 'Application', 'chrome.exe'),
    process.env.LOCALAPPDATA && join(process.env.LOCALAPPDATA, 'Google', 'Chrome', 'Application', 'chrome.exe'),
  ].filter(Boolean);
  const detected = candidates.find((candidate) => existsSync(candidate));
  if (!detected) {
    throw new Error(
      `Chrome was not found. Set CHROME_PATH explicitly. Checked: ${candidates.join(', ')}`,
    );
  }
  return detected;
}

function assertPageFiles() {
  const missing = Object.values(pages)
    .map((filename) => join(siteRoot, filename))
    .filter((file) => !existsSync(file));
  if (missing.length) {
    throw new Error(`Generated Season 2 pages are missing: ${missing.join(', ')}`);
  }
}

function attachRuntimeErrorCapture(page) {
  const errors = [];
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`);
  });
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  return errors;
}

async function stubCloudflareWebAnalytics(context) {
  await context.route(
    'https://static.cloudflareinsights.com/beacon.min.js',
    (route) => route.fulfill({ contentType: 'application/javascript', body: '' }),
  );
}

async function collectMetrics(page, expected) {
  return page.evaluate(({ theme: expectedTheme, mode: expectedMode, stackedLayout, width, rowHeight }) => {
    const label = (element) =>
      element.closest('[data-record-id]')?.getAttribute('data-record-id') ||
      element.id ||
      String(element.className) ||
      element.tagName;
    const overflowDetails = (element) => ({
      label: label(element),
      tag: element.tagName,
      className: String(element.className),
      delta: element.scrollWidth - element.clientWidth,
      scrollWidth: element.scrollWidth,
      clientWidth: element.clientWidth,
    });
    const internalSelector = [
      '.cols2',
      '.colsRow',
      'table.lt',
      'table.move-table',
      'table.throw-table',
      'table.ten-string-table',
      'table.cb',
      'td',
    ].join(',');
    const horizontalOverflow = [...document.querySelectorAll(internalSelector)]
      .filter((element) => element.scrollWidth > element.clientWidth + 1)
      .map(overflowDetails)
      .sort((left, right) => right.delta - left.delta);
    const verticalOverflow = [...document.querySelectorAll('tr[data-record-id] td')]
      .filter((element) => element.scrollHeight > element.clientHeight + 1)
      .map((element) => ({
        ...overflowDetails(element),
        verticalDelta: element.scrollHeight - element.clientHeight,
      }));
    const unevenTables = [...document.querySelectorAll('table:not(.ten-string-table)')]
      .map((table, index) => {
        const heights = [...new Set(
          [...table.querySelectorAll('tr[data-record-id]')]
            .map((row) => Math.round(row.getBoundingClientRect().height * 10) / 10),
        )];
        return { index, heights };
      })
      .filter((entry) => entry.heights.length > 1);
    const rowHeightIssues = [...document.querySelectorAll(
      'section:not(.tipsPage) table:not(.ten-string-table) tr[data-record-id]',
    )]
      .map((row) => ({ label: label(row), height: row.getBoundingClientRect().height }))
      .filter(({ height }) => height < rowHeight[0] || height > rowHeight[1]);

    const isVisibleContent = (element) => {
      if (element.matches('.sr-only,[aria-hidden="true"]')) return false;
      const style = getComputedStyle(element);
      return style.display !== 'none' && style.visibility !== 'hidden';
    };
    const visibleContentRight = (cell) => {
      const rights = [];
      for (const child of cell.children) {
        if (isVisibleContent(child)) rights.push(child.getBoundingClientRect().right);
      }
      for (const node of cell.childNodes) {
        if (node.nodeType !== Node.TEXT_NODE || !node.textContent.trim()) continue;
        const range = document.createRange();
        range.selectNodeContents(node);
        for (const rect of range.getClientRects()) rights.push(rect.right);
      }
      return rights.length ? Math.max(...rights) : cell.getBoundingClientRect().left;
    };
    const contentOverlaps = width > 640 ? [...document.querySelectorAll(
      'section:not(.tipsPage) tr[data-record-id]',
    )].flatMap((row) => {
      const cells = [...row.cells];
      return cells.slice(0, -1).flatMap((cell, index) => {
        const next = cells[index + 1].getBoundingClientRect();
        const contentRight = visibleContentRight(cell);
        return contentRight > next.left + 1
          ? [{ label: label(row), className: cell.className, delta: contentRight - next.left }]
          : [];
      });
    }) : [];

    const layoutIssues = [...document.querySelectorAll('.cols2,.colsRow')].flatMap((container) => {
      const children = [...container.children]
        .filter((child) => getComputedStyle(child).display !== 'none');
      if (children.length < 2) return [];
      const first = children[0].getBoundingClientRect();
      const second = children[1].getBoundingClientRect();
      if (stackedLayout) {
        const stacked = second.top >= first.bottom - 1;
        const aligned = Math.abs(second.left - first.left) <= 1;
        return stacked && aligned
          ? []
          : [{ label: label(container), expected: 'stacked', first, second }];
      }
      const sideBySide = Math.abs(second.top - first.top) <= 1 && second.left > first.right;
      return sideBySide
        ? []
        : [{ label: label(container), expected: 'side-by-side', first, second }];
    });

    const phoneRowIssues = width <= 640 ? [...document.querySelectorAll('tr[data-record-id]')].flatMap((row) => {
      const cmd = row.querySelector('td.cmd');
      if (!cmd) return [{ label: label(row), problems: ['missing cmd cell'] }];
      const anchor = row.querySelector('td.name') || row.querySelector('td.fr');
      const rowRect = row.getBoundingClientRect();
      const cmdRect = cmd.getBoundingClientRect();
      const anchorRect = anchor.getBoundingClientRect();
      const issues = [];
      if (cmdRect.top < anchorRect.bottom - 1) issues.push('command not stacked below name/stats line');
      if (Math.abs(cmdRect.left - rowRect.left) > 3) issues.push('command not full-width');
      if (rowRect.height <= 49) issues.push('row still desktop-height');
      return issues.length ? [{ label: label(row), problems: issues }] : [];
    }) : [];
    const bodyZoom = getComputedStyle(document.body).zoom;

    const commandPairs = [...document.querySelectorAll('.cmd-gfx')].map((gfx) => ({
      gfx,
      txt: gfx.nextElementSibling?.matches('.cmd-txt') ? gfx.nextElementSibling : null,
    }));
    const commandPairIssues = commandPairs
      .filter(({ txt }) => !txt)
      .map(({ gfx }) => label(gfx));
    const commandVisibilityIssues = commandPairs.flatMap(({ gfx, txt }) => {
      if (!txt) return [];
      const gfxDisplay = getComputedStyle(gfx).display;
      const txtDisplay = getComputedStyle(txt).display;
      const valid = expectedMode === 'txt'
        ? gfxDisplay === 'none' && txtDisplay !== 'none'
        : gfxDisplay !== 'none' && txtDisplay === 'none';
      return valid ? [] : [{ label: label(gfx), gfxDisplay, txtDisplay }];
    });
    const activeNotation = [...document.querySelectorAll('#ng,#nn,#nt')]
      .filter((button) => button.classList.contains('on') && button.getAttribute('aria-pressed') === 'true')
      .map((button) => button.id);
    const activeTheme = [...document.querySelectorAll('#thd,#thl')]
      .filter((button) => button.classList.contains('on') && button.getAttribute('aria-pressed') === 'true')
      .map((button) => button.id);
    const activeButtonColors = [...new Set(
      [...document.querySelectorAll('.tk-b i.on')].map((button) => getComputedStyle(button).color),
    )];
    const transparent = (color) => color === 'transparent' || color === 'rgba(0, 0, 0, 0)';
    let storedTheme = null;
    let storedNotation = null;
    try {
      storedTheme = localStorage.getItem('tk-theme');
      storedNotation = localStorage.getItem('tk-notation');
    } catch (_) {}

    const homeLinks = [...document.querySelectorAll('[data-home]')];
    const breadcrumb = document.querySelector('header#top .home');
    const revealbar = document.querySelector('.revealbar');
    const banner = document.querySelector('header#top');
    const portrait = document.querySelector('header#top .hero img');
    const bio = document.querySelector('header#top .hdrbio');
    // WCAG contrast of the section headings as the browser actually resolves
    // them. Both colours are flat here, so computed styles are the whole truth.
    const contrastOf = (node) => {
      if (!node) return null;
      const parse = (value) => (value.match(/[\d.]+/g) || []).slice(0, 3).map(Number);
      const channel = (v) => (v / 255 <= 0.03928 ? v / 255 / 12.92 : ((v / 255 + 0.055) / 1.055) ** 2.4);
      const luminance = ([r, g, b]) => 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
      const style = getComputedStyle(node);
      const ink = parse(style.color);
      // a transparent background means the ground belongs to an ancestor
      let ground = null;
      for (let el = node; el; el = el.parentElement) {
        const bg = getComputedStyle(el).backgroundColor;
        if (!/^rgba\(.*,\s*0\)$/.test(bg) && bg !== 'transparent') { ground = parse(bg); break; }
      }
      if (ink.length !== 3 || !ground || ground.length !== 3) return null;
      // an opacity below 1 composites the ink back towards its ground, in sRGB
      const alpha = Number(style.opacity);
      const painted = ink.map((v, i) => v * alpha + ground[i] * (1 - alpha));
      const [lit, dim] = [luminance(painted), luminance(ground)].sort((a, b) => b - a);
      return Math.round(((lit + 0.05) / (dim + 0.05)) * 100) / 100;
    };
    const heading = document.querySelector('section > h2');
    const headingEn = document.querySelector('section > h2 .en');

    const legendTop = document.querySelector('.legend .lgtop');
    const legendTxt = document.querySelector('.legend .lgsub.txt-only');
    const legendGfx = document.querySelector('.legend .lgsub.gfx-only');

    return {
      contrast: {
        heading: contrastOf(heading),
        headingEn: contrastOf(headingEn),
      },
      legend: {
        // the column key is about the table, not the notation, so it always shows
        topVisible: Boolean(legendTop) && isVisibleContent(legendTop),
        // exactly one notation half at a time -- see legend_card.css
        txtVisible: Boolean(legendTxt) && isVisibleContent(legendTxt),
        gfxVisible: Boolean(legendGfx) && isVisibleContent(legendGfx),
      },
      headerCard: {
        // a portrait that 404s would leave the band looking merely empty
        portraitLoaded: Boolean(portrait) && portrait.complete && portrait.naturalWidth > 0,
        portraitSrc: portrait ? portrait.getAttribute('src') : null,
        portraitVisible: Boolean(portrait) && isVisibleContent(portrait)
          && portrait.getBoundingClientRect().width > 8,
        bioValues: bio ? [...bio.querySelectorAll('dd')].map((dd) => dd.textContent.trim()) : [],
        // the whole point of treatment A: the band absorbs the portrait and the
        // content column keeps its width, so the band must not scroll sideways
        bannerOverflow: Boolean(banner) && banner.scrollWidth > banner.clientWidth + 1,
      },
      backNav: {
        homeHrefs: homeLinks.map((link) => link.getAttribute('href')),
        breadcrumbVisible: Boolean(breadcrumb) && isVisibleContent(breadcrumb),
        revealbarVisibility: revealbar ? getComputedStyle(revealbar).visibility : null,
        // fixed positioning under `zoom: 1.25` must still resolve to the
        // viewport, not to 1.25x of it
        revealbarWidth: revealbar ? Math.round(revealbar.getBoundingClientRect().width) : 0,
      },
      documentOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      bodyOverflow: document.body.scrollWidth > document.body.clientWidth + 1,
      widths: {
        documentScroll: document.documentElement.scrollWidth,
        documentClient: document.documentElement.clientWidth,
        bodyScroll: document.body.scrollWidth,
        bodyClient: document.body.clientWidth,
      },
      horizontalOverflow,
      verticalOverflow,
      unevenTables,
      rowHeightIssues,
      contentOverlaps,
      layoutIssues,
      phoneRowIssues,
      bodyZoom,
      rowCount: document.querySelectorAll('tr[data-record-id]').length,
      duplicateIds: [...document.querySelectorAll('[id]')]
        .map((element) => element.id)
        .filter((id, index, ids) => ids.indexOf(id) !== index),
      controlCount: document.querySelectorAll('#ng,#nn,#nt,#thd,#thl').length,
      commandPairCount: commandPairs.length,
      commandPairIssues,
      commandVisibilityIssues,
      activeNotation,
      activeTheme,
      dark: document.documentElement.classList.contains('dark'),
      noNumberColorsValid: activeButtonColors.length > 0 && activeButtonColors.every(transparent),
      graphicalColorsValid: activeButtonColors.length > 0 && activeButtonColors.every((color) => !transparent(color)),
      storedTheme,
      storedNotation,
    };
  }, expected);
}

function analyzeMetrics(metrics, expected, runtimeErrors) {
  const problems = [];
  if (metrics.documentOverflow || metrics.bodyOverflow) {
    problems.push(`page overflow: ${JSON.stringify(metrics.widths)}`);
  }
  if (expected.width <= 640) {
    if (metrics.bodyZoom !== '1') {
      problems.push(`body zoom at 390px: ${metrics.bodyZoom}`);
    }
    if (metrics.phoneRowIssues.length) {
      problems.push(`phone stacking: ${JSON.stringify(metrics.phoneRowIssues.slice(0, 8))}`);
    }
  }
  if (metrics.horizontalOverflow.length) {
    problems.push(`internal horizontal overflow: ${JSON.stringify(metrics.horizontalOverflow.slice(0, 12))}`);
  }
  if (metrics.verticalOverflow.length) {
    problems.push(`internal vertical overflow: ${JSON.stringify(metrics.verticalOverflow.slice(0, 12))}`);
  }
  if (expected.width === 1480 && metrics.unevenTables.length) {
    problems.push(`uneven rows: ${JSON.stringify(metrics.unevenTables.slice(0, 6))}`);
  }
  if (expected.width === 1480 && metrics.rowHeightIssues.length) {
    problems.push(`row height: ${JSON.stringify(metrics.rowHeightIssues.slice(0, 12))}`);
  }
  if (metrics.contentOverlaps.length) {
    problems.push(`visible content overlap: ${JSON.stringify(metrics.contentOverlaps.slice(0, 12))}`);
  }
  if (metrics.layoutIssues.length) {
    problems.push(`layout: ${JSON.stringify(metrics.layoutIssues.slice(0, 8))}`);
  }
  if (metrics.rowCount === 0) problems.push('no generated move rows');
  if (metrics.duplicateIds.length) problems.push(`duplicate ids: ${metrics.duplicateIds.join(', ')}`);
  if (metrics.controlCount !== 5) problems.push(`expected 5 controls, found ${metrics.controlCount}`);
  if (metrics.commandPairCount === 0) problems.push('no graphical/text command pairs');
  if (metrics.commandPairIssues.length) {
    problems.push(`command pair structure: ${metrics.commandPairIssues.slice(0, 12).join(', ')}`);
  }
  if (metrics.commandVisibilityIssues.length) {
    problems.push(`command visibility: ${JSON.stringify(metrics.commandVisibilityIssues.slice(0, 12))}`);
  }
  if (metrics.activeNotation.join() !== ({ gfx: 'ng', nn: 'nn', txt: 'nt' })[expected.mode]) {
    problems.push('notation toggle state');
  }
  if (metrics.activeTheme.join() !== (expected.theme === 'dark' ? 'thd' : 'thl')) {
    problems.push('theme toggle state');
  }
  if (metrics.dark !== (expected.theme === 'dark')) problems.push('theme class state');
  if (expected.mode === 'nn' && !metrics.noNumberColorsValid) problems.push('no-number color');
  if (expected.mode === 'gfx' && !metrics.graphicalColorsValid) problems.push('graphical number color');
  const headerCard = metrics.headerCard;
  if (!headerCard.portraitLoaded) {
    problems.push(`portrait not loaded: ${headerCard.portraitSrc}`);
  }
  if (!headerCard.portraitVisible) problems.push('portrait not visible in the band');
  if (headerCard.bannerOverflow) problems.push('header band overflows horizontally');
  if (headerCard.bioValues.length < 2) {
    problems.push(`profile row: ${JSON.stringify(headerCard.bioValues)}`);
  }
  // The Chinese builds must not leak English into the profile row -- that is
  // official_profile_zh.py's whole contract. The English build shows
  // tekken.com's own wording there, so the same check would flag it for being
  // correct.
  if (expected.locale !== 'en'
    && headerCard.bioValues.some((value) => /[A-Za-z]{4,}/.test(value))) {
    problems.push(`untranslated profile text: ${JSON.stringify(headerCard.bioValues)}`);
  }

  const backNav = metrics.backNav;
  if (backNav.homeHrefs.length !== 2 || backNav.homeHrefs.some((href) => href !== 'index.html')) {
    problems.push(`back nav home links: ${JSON.stringify(backNav.homeHrefs)}`);
  }
  if (!backNav.breadcrumbVisible) problems.push('back nav breadcrumb not visible');
  if (backNav.revealbarVisibility !== 'hidden') {
    problems.push(`reveal bar not parked at rest: ${backNav.revealbarVisibility}`);
  }
  if (Math.abs(backNav.revealbarWidth - metrics.widths.documentClient) > 1) {
    problems.push(
      `reveal bar width ${backNav.revealbarWidth} != viewport ${metrics.widths.documentClient}`,
    );
  }
  if (metrics.storedTheme !== expected.theme) problems.push(`stored theme: ${metrics.storedTheme}`);
  // 13px bold is below the size WCAG lets off at 3:1, so the full 4.5 applies.
  // `h2 .en` is the other locale's name for the section, and the English pages
  // have none -- `Throws 投技` is a line its reader cannot read -- so there it
  // is absent rather than unmeasurable.
  const absentByDesign = expected.locale === 'en' ? new Set(['headingEn']) : new Set();
  for (const [what, ratio] of Object.entries(metrics.contrast)) {
    if (ratio === null) {
      if (!absentByDesign.has(what)) problems.push(`contrast: ${what} not measurable`);
    } else if (ratio < 4.5) {
      problems.push(`contrast: ${what} is ${ratio}:1, below AA`);
    }
  }
  if (expected.locale === 'en' && metrics.contrast.headingEn !== null) {
    problems.push('English page still carries an h2 .en twin');
  }

  const legend = metrics.legend;
  if (!legend.topVisible) problems.push('legend judgement/startup row not visible');
  const wantsText = expected.mode === 'txt';
  if (legend.txtVisible !== wantsText) {
    problems.push(`legend text half visible=${legend.txtVisible} in ${expected.mode} mode`);
  }
  if (legend.gfxVisible === wantsText) {
    problems.push(`legend button-map half visible=${legend.gfxVisible} in ${expected.mode} mode`);
  }

  if (metrics.storedNotation !== expected.mode) problems.push(`stored notation: ${metrics.storedNotation}`);
  if (runtimeErrors.length) problems.push(runtimeErrors.join('; '));
  return problems;
}

async function captureScreenshot(page, character, expected) {
  if (!screenshotDir) return;
  const filename = `${character}-${expected.width}-${expected.theme}-${expected.mode}.png`;
  await page.screenshot({ path: join(screenshotDir, filename), fullPage: true });
}

async function runState(page, character, expected, runtimeErrors, results) {
  await page.locator(themeButtons[expected.theme]).click();
  await page.locator(notationButtons[expected.mode]).click();
  const metrics = await collectMetrics(page, expected);
  const stateErrors = runtimeErrors.splice(0, runtimeErrors.length);
  const problems = analyzeMetrics(metrics, expected, stateErrors);
  results.push({ character, ...expected, problems });
  await captureScreenshot(page, character, expected);
}

// The bar only earns its keep if an upward scroll actually summons it, so drive
// a real scroll round-trip rather than trusting the CSS to be wired up.
async function verifyRevealBar(page, result) {
  const readBar = () => page.evaluate(() => {
    const bar = document.querySelector('.revealbar');
    return {
      visibility: getComputedStyle(bar).visibility,
      top: Math.round(bar.getBoundingClientRect().top),
      overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
    };
  });

  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  await page.waitForTimeout(300);
  const atBottom = await readBar();
  if (atBottom.visibility !== 'hidden') {
    result.problems.push(`reveal bar: shown while scrolling down (${atBottom.visibility})`);
  }

  await page.evaluate(() => window.scrollBy(0, -500));
  await page.waitForTimeout(300);
  const afterScrollUp = await readBar();
  if (afterScrollUp.visibility !== 'visible' || afterScrollUp.top !== 0) {
    result.problems.push(`reveal bar: not revealed on scroll up (${JSON.stringify(afterScrollUp)})`);
  }
  if (afterScrollUp.overflow) {
    result.problems.push('reveal bar: causes horizontal overflow while shown');
  }

  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(300);
  const backAtTop = await readBar();
  if (backAtTop.visibility !== 'hidden') {
    result.problems.push(`reveal bar: still shown back at the banner (${backAtTop.visibility})`);
  }
}

// The 5 one-shot pipeline pages sit outside the 360-state gate -- their markup
// predates the generator and most of its assertions do not apply. They do share
// the notation legend, and they shipped an always-visible key for months
// precisely because nothing ever rendered them. So check that one half hides.
async function runLegacyLegendStates(browser, results) {
  for (const { name: filename, dir, locale } of legacyPages) {
    const character = `${filename.replace('_tk8_movelist.html', '')}:${locale}`;
    const context = await browser.newContext({ viewport: { width: 1480, height: 1000 } });
    try {
      await stubCloudflareWebAnalytics(context);
      const page = await context.newPage();
      const runtimeErrors = attachRuntimeErrorCapture(page);
      await page.goto(pathToFileURL(join(dir, filename)).href, { waitUntil: 'load' });
      for (const mode of ['gfx', 'nn', 'txt']) {
        await page.locator(notationButtons[mode]).click();
        const legend = await page.evaluate(() => {
          const shown = (selector) => {
            const node = document.querySelector(selector);
            if (!node) return null;
            return getComputedStyle(node).display !== 'none'
              && node.getBoundingClientRect().height > 0;
          };
          const parse = (v) => (v.match(/[\d.]+/g) || []).slice(0, 3).map(Number);
          const ch = (v) => (v / 255 <= 0.03928 ? v / 255 / 12.92 : ((v / 255 + 0.055) / 1.055) ** 2.4);
          const lum = ([r, g, b]) => 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b);
          const heading = document.querySelector('section > h2');
          let headingContrast = null;
          if (heading) {
            const s = getComputedStyle(heading);
            const [hi, lo] = [lum(parse(s.color)), lum(parse(s.backgroundColor))].sort((a, b) => b - a);
            headingContrast = Math.round(((hi + 0.05) / (lo + 0.05)) * 100) / 100;
          }
          return {
            top: shown('.legend .lgtop'),
            txt: shown('.legend .lgsub.txt-only'),
            gfx: shown('.legend .lgsub.gfx-only'),
            headingContrast,
          };
        });
        const problems = [];
        const wantsText = mode === 'txt';
        if (legend.top !== true) problems.push(`judgement row: ${legend.top}`);
        if (legend.txt !== wantsText) problems.push(`text half visible=${legend.txt}`);
        if (legend.gfx !== !wantsText) problems.push(`button-map half visible=${legend.gfx}`);
        if (!(legend.headingContrast >= 4.5)) {
          problems.push(`heading contrast ${legend.headingContrast}:1, below AA`);
        }
        problems.push(...runtimeErrors.splice(0, runtimeErrors.length));
        results.push({ character, mode, legacy: true, problems });
      }
    } finally {
      await context.close();
    }
  }
}

async function verifyReloadPersistence(page, expected, runtimeErrors, result) {
  await page.reload({ waitUntil: 'load' });
  const metrics = await collectMetrics(page, expected);
  const stateErrors = runtimeErrors.splice(0, runtimeErrors.length);
  const problems = analyzeMetrics(metrics, expected, stateErrors);
  result.problems.push(...problems.map((problem) => `reload persistence: ${problem}`));
}

assertPageFiles();
if (screenshotDir) mkdirSync(screenshotDir, { recursive: true });

const results = [];
const legacyResults = [];
let browser;
try {
  browser = await chromium.launch({ executablePath: findChrome(), headless: true });

  for (const locale of locales) {
    const tree = locale.dir ? join(siteRoot, locale.dir) : siteRoot;
    const label = (character) => (locale.id === 'hans' ? character : `${character}@${locale.id}`);

    for (const [character, filename] of Object.entries(pages)) {
      if (!existsSync(join(tree, filename))) continue;
      const context = await browser.newContext({ viewport: { width: 1480, height: 1000 } });
      try {
        await stubCloudflareWebAnalytics(context);
        const page = await context.newPage();
        const runtimeErrors = attachRuntimeErrorCapture(page);
        await page.goto(pathToFileURL(join(tree, filename)).href, { waitUntil: 'load' });
        for (const state of locale.states) {
          await runState(
            page,
            label(character),
            { ...state, rowHeight: locale.rowHeight, locale: locale.id },
            runtimeErrors,
            results,
          );
        }
        // the reveal bar and the reload round-trip are behaviour, not layout,
        // and the script driving them is shared verbatim -- checking them once
        // per character in the indexed tree is the coverage that pays
        if (locale.full) {
          await verifyRevealBar(page, results.at(-1));
          await verifyReloadPersistence(
            page,
            {
              width: 1480,
              theme: 'light',
              mode: 'txt',
              stackedLayout: false,
              rowHeight: locale.rowHeight,
              locale: locale.id,
            },
            runtimeErrors,
            results.at(-1),
          );
        }
      } finally {
        await context.close();
      }
    }

    for (const [character, filename] of Object.entries(pages)) {
      if (!existsSync(join(tree, filename))) continue;
      for (const width of locale.responsive) {
        const context = await browser.newContext({ viewport: { width, height: 1000 } });
        try {
          await stubCloudflareWebAnalytics(context);
          const page = await context.newPage();
          const runtimeErrors = attachRuntimeErrorCapture(page);
          await page.goto(pathToFileURL(join(tree, filename)).href, { waitUntil: 'load' });
          await runState(
            page,
            label(character),
            {
              width,
              theme: 'dark',
              mode: 'gfx',
              stackedLayout: true,
              rowHeight: locale.rowHeight,
              locale: locale.id,
            },
            runtimeErrors,
            results,
          );
        } finally {
          await context.close();
        }
      }
    }
  }

  await runLegacyLegendStates(browser, legacyResults);
} finally {
  if (browser) await browser.close();
}

const failures = [...results, ...legacyResults].filter((result) => result.problems.length);
const expectedStateCount = locales.reduce(
  (total, locale) => total
    + Object.keys(pages).filter((character) => existsSync(
      join(locale.dir ? join(siteRoot, locale.dir) : siteRoot, pages[character]),
    )).length * (locale.states.length + locale.responsive.length),
  0,
);
const perLocaleStateCount = Object.fromEntries(locales.map((locale) => [
  locale.id,
  results.filter((result) => result.locale === locale.id).length,
]));
const expectedLegacyStateCount = legacyPages.length * 3;
console.log(JSON.stringify({
  stateCount: results.length,
  expectedStateCount,
  perLocaleStateCount,
  legacyStateCount: legacyResults.length,
  expectedLegacyStateCount,
  failureCount: failures.length,
  screenshotDir,
  failures,
}, null, 2));
process.exitCode = results.length === expectedStateCount
  && legacyResults.length === expectedLegacyStateCount
  && failures.length === 0 ? 0 : 1;
