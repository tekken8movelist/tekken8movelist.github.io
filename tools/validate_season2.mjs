import { existsSync, mkdirSync } from 'node:fs';
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
const onlyCharacters = process.env.CHARACTERS
  ? new Set(process.env.CHARACTERS.split(',').map((value) => value.trim()))
  : null;
const pages = Object.fromEntries(
  Object.entries(allPages).filter(([key]) => !onlyCharacters || onlyCharacters.has(key)),
);
if (!Object.keys(pages).length) {
  throw new Error(`CHARACTERS filter matched no pages: ${process.env.CHARACTERS}`);
}
const notationButtons = { gfx: '#ng', nn: '#nn', txt: '#nt' };
const themeButtons = { dark: '#thd', light: '#thl' };
const responsiveWidths = [1280, 1024, 760, 390];
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

async function collectMetrics(page, expected) {
  return page.evaluate(({ theme: expectedTheme, mode: expectedMode, stackedLayout, width }) => {
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
      .filter(({ height }) => height < 46 || height > 49);

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

    return {
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
  if (metrics.storedTheme !== expected.theme) problems.push(`stored theme: ${metrics.storedTheme}`);
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
let browser;
try {
  browser = await chromium.launch({ executablePath: findChrome(), headless: true });

  for (const [character, filename] of Object.entries(pages)) {
    const context = await browser.newContext({ viewport: { width: 1480, height: 1000 } });
    try {
      const page = await context.newPage();
      const runtimeErrors = attachRuntimeErrorCapture(page);
      await page.goto(pathToFileURL(join(siteRoot, filename)).href, { waitUntil: 'load' });
      for (const theme of ['dark', 'light']) {
        for (const mode of ['gfx', 'nn', 'txt']) {
          await runState(
            page,
            character,
            { width: 1480, theme, mode, stackedLayout: false },
            runtimeErrors,
            results,
          );
        }
      }
      await verifyReloadPersistence(
        page,
        { width: 1480, theme: 'light', mode: 'txt', stackedLayout: false },
        runtimeErrors,
        results.at(-1),
      );
    } finally {
      await context.close();
    }
  }

  for (const [character, filename] of Object.entries(pages)) {
    for (const width of responsiveWidths) {
      const context = await browser.newContext({ viewport: { width, height: 1000 } });
      try {
        const page = await context.newPage();
        const runtimeErrors = attachRuntimeErrorCapture(page);
        await page.goto(pathToFileURL(join(siteRoot, filename)).href, { waitUntil: 'load' });
        await runState(
          page,
          character,
          { width, theme: 'dark', mode: 'gfx', stackedLayout: true },
          runtimeErrors,
          results,
        );
      } finally {
        await context.close();
      }
    }
  }
} finally {
  if (browser) await browser.close();
}

const failures = results.filter((result) => result.problems.length);
const expectedStateCount = Object.keys(pages).length * 10;
console.log(JSON.stringify({
  stateCount: results.length,
  expectedStateCount,
  failureCount: failures.length,
  screenshotDir,
  failures,
}, null, 2));
process.exitCode = results.length === expectedStateCount && failures.length === 0 ? 0 : 1;
