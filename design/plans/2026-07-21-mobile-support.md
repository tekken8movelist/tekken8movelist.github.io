# Mobile Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the fake "pinned 600px canvas" mobile behavior with a real responsive phone layout (≤640px) on all 41 movelist pages, and fix homepage avatar cropping + zoom on phones.

**Architecture:** Pure-CSS reflow driven by a new `@media (max-width:640px)` block. Season 2 pages (36) get it via the single shared stylesheet `tools/season2_page.css` + rebuild; the 5 legacy pages get an equivalent injected `<style id="mobile-phone">` block; the homepage's existing 640px block is extended. The browser QA's 390px assertions are flipped from "must overflow" to "zero overflow + stacked rows" first (TDD red), then the CSS makes them pass (green).

**Tech Stack:** Static HTML/CSS, Python 3 generators (`tools/build_season2.py`), Node + Playwright QA (`tools/validate_season2.mjs`), PowerShell gate (`tools/validate_season2.ps1`).

**Spec:** `design/specs/2026-07-21-mobile-support-design.md`

## Global Constraints

- **Never hand-edit generated Season 2 pages** (`docs/*_tk8_movelist.html` except xiaoyu/jun/kunimitsu/clive/law). Only edit `tools/season2_page.css` and rebuild with `python tools/build_season2.py`.
- Phone breakpoint is **exactly `@media (max-width: 640px)`** everywhere. Desktop (>1280px) and the 641–1280px fallback must remain pixel-identical — all phone rules live inside the 640px media block.
- The phone layout contract the QA depends on: move rows are `tr[data-record-id]`; cell classes are `td.name`, `td.cmd`, `td.fr`, `td.dmg`, `td.rng` (+ `td.direction`, `td.break` in throw tables); ten-string rows have no `td.name`. Do not change this markup.
- `tk-in` button-map graphics must render unchanged on phones (no text fallback); `按键图/无数字/文字` notation modes and theme toggle keep working.
- Keep public attribution and the unofficial/non-commercial disclaimer intact.
- Playwright resolves via `NODE_PATH="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"` (Git Bash syntax). Chrome is the system Chrome (found by `findChrome()`).
- `docs/` is the public web root — no new files there except edited pages.
- If `python` is not on PATH, use the bundled runtime `"$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"`.

---

### Task 1: Flip the browser-QA 390px assertions to expect the phone layout (red)

**Files:**
- Modify: `tools/validate_season2.mjs:109-110` (destructure), `:177-188` (`contentOverlaps`), `:207-208` (insert phone metrics after `layoutIssues`), `:242-272` (return object), `:278-289` (`analyzeMetrics` 390px branch)

**Interfaces:**
- Consumes: existing `collectMetrics(page, expected)` / `analyzeMetrics(metrics, expected, runtimeErrors)` flow; `expected` objects already carry `{ width, theme, mode, stackedLayout }`.
- Produces: new metrics fields `phoneRowIssues` (array) and `bodyZoom` (string) consumed by `analyzeMetrics`; new failure strings `page overflow:`, `body zoom at 390px:`, `phone stacking:` at width 390. Task 2's CSS must make these pass.

- [ ] **Step 1: Widen the `collectMetrics` destructure to include `width`**

In `tools/validate_season2.mjs:110`, change:

```js
  return page.evaluate(({ theme: expectedTheme, mode: expectedMode, stackedLayout }) => {
```

to:

```js
  return page.evaluate(({ theme: expectedTheme, mode: expectedMode, stackedLayout, width }) => {
```

- [ ] **Step 2: Gate `contentOverlaps` to widths above the phone breakpoint**

The check compares horizontally adjacent cells; at ≤640px cells stack vertically, so it false-positives. In `tools/validate_season2.mjs:177-188`, change:

```js
    const contentOverlaps = [...document.querySelectorAll(
      'section:not(.tipsPage) tr[data-record-id]',
    )].flatMap((row) => {
```

to:

```js
    const contentOverlaps = width > 640 ? [...document.querySelectorAll(
      'section:not(.tipsPage) tr[data-record-id]',
    )].flatMap((row) => {
```

and close the ternary: change the end of that expression from

```js
          : [];
      });
    });
```

to:

```js
          : [];
      });
    }) : [];
```

- [ ] **Step 3: Add phone-layout metrics**

Immediately after the `layoutIssues` block (after `tools/validate_season2.mjs:207`), insert:

```js

    const phoneRowIssues = width === 390 ? [...document.querySelectorAll('tr[data-record-id]')].flatMap((row) => {
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
```

- [ ] **Step 4: Return the new metrics**

In the `return { ... }` of `collectMetrics` (`tools/validate_season2.mjs:242-272`), add two lines (e.g. after `layoutIssues,`):

```js
      phoneRowIssues,
      bodyZoom,
```

- [ ] **Step 5: Rewrite the 390px branch of `analyzeMetrics`**

Replace `tools/validate_season2.mjs:278-289`:

```js
  if (expected.width === 390) {
    const expectedCanvas = (value) => value >= 595 && value <= 605;
    if (
      !metrics.documentOverflow ||
      !expectedCanvas(metrics.widths.documentScroll) ||
      !expectedCanvas(metrics.widths.bodyScroll)
    ) {
      problems.push(`unexpected 390px canvas: ${JSON.stringify(metrics.widths)}`);
    }
  } else if (metrics.documentOverflow || metrics.bodyOverflow) {
    problems.push(`page overflow: ${JSON.stringify(metrics.widths)}`);
  }
```

with:

```js
  if (metrics.documentOverflow || metrics.bodyOverflow) {
    problems.push(`page overflow: ${JSON.stringify(metrics.widths)}`);
  }
  if (expected.width === 390) {
    if (metrics.bodyZoom !== '1') {
      problems.push(`body zoom at 390px: ${metrics.bodyZoom}`);
    }
    if (metrics.phoneRowIssues.length) {
      problems.push(`phone stacking: ${JSON.stringify(metrics.phoneRowIssues.slice(0, 8))}`);
    }
  }
```

- [ ] **Step 6: Run the QA on two characters — verify RED at 390px only**

```bash
cd "C:/Users/luden/workspace/tekken8movelist"
NODE_PATH="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules" \
  CHARACTERS=alisa,yoshimitsu node tools/validate_season2.mjs
```

Expected: exit code 1; every failure entry has `width: 390` and `page overflow:` problems (old CSS pins body to 600px). The 1280/1024/760-width and 1480 desktop states still pass (their entries have empty `problems`). `stateCount: 20`, `expectedStateCount: 20`.

- [ ] **Step 7: Commit**

```bash
git add tools/validate_season2.mjs
git commit -m "QA: expect zero overflow and stacked phone rows at 390px"
```

---

### Task 2: Season 2 phone CSS block + rebuild (green)

**Files:**
- Modify: `tools/season2_page.css:545-552` (replace the pinned-600px block)
- Regenerated (by build, never by hand): `docs/*_tk8_movelist.html` (36 pages)

**Interfaces:**
- Consumes: Task 1's QA expectations (`page overflow`, `phone stacking`, `bodyZoom`).
- Produces: the phone layout contract used verbatim by Task 3's legacy injection: line 1 = `td.name` + stats, line 2 = full-width `td.cmd`, cram tiers neutralized, zebra on the row box.

- [ ] **Step 1: Replace the phone media block**

In `tools/season2_page.css`, replace lines 545-552:

```css
@media (max-width: 600px) {
  body {
    zoom: 1;
    padding: 8px;
    width: 600px;
    min-width: 600px;
  }
}
```

with:

```css
/* ---- phone layout: 1 move per row ----------------------------------
   Line 1: move name (left) + stats (right, "·"-separated).
   Line 2: the command on its own full-width line; long commands
   (ten-hit strings, long routes) wrap instead of squeezing.
   The tk-in button-map graphics render unchanged; cram shrink tiers
   are neutralized because wrapping replaces cramming. */
@media (max-width: 640px) {
  body {
    zoom: 1;
    width: auto;
    min-width: 0;
    padding: 8px;
    font-size: 12px;
  }

  .legend {
    font-size: 11px;
  }

  section:not(.tipsPage) table.move-table,
  section:not(.tipsPage) table.throw-table,
  section:not(.tipsPage) table.ten-string-table {
    display: block;
  }

  section:not(.tipsPage) table.move-table > thead,
  section:not(.tipsPage) table.throw-table > thead,
  section:not(.tipsPage) table.ten-string-table > thead {
    display: none;
  }

  section:not(.tipsPage) table.move-table > tbody,
  section:not(.tipsPage) table.throw-table > tbody,
  section:not(.tipsPage) table.ten-string-table > tbody {
    display: block;
  }

  section:not(.tipsPage) tr[data-record-id] {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 6px 8px;
    height: auto;
    padding: 6px 2px;
    border-bottom: 1px solid var(--line);
  }

  section:not(.tipsPage) tr[data-record-id] td {
    display: block;
    padding: 0;
    border-bottom: 0;
    overflow: visible;
    white-space: normal;
  }

  /* zebra striping moves from the cells to the row box */
  section:not(.tipsPage) tbody tr:nth-child(even) td {
    background: none;
  }

  section:not(.tipsPage) tbody tr:nth-child(even) {
    background: color-mix(in srgb, var(--paper-alt) 52%, transparent);
  }

  section:not(.tipsPage) tr[data-record-id] td.name {
    flex: 1 1 auto;
    min-width: 0;
    font-size: 13px;
  }

  section:not(.tipsPage) tr[data-record-id] td.fr,
  section:not(.tipsPage) tr[data-record-id] td.dmg,
  section:not(.tipsPage) tr[data-record-id] td.rng,
  section:not(.tipsPage) tr[data-record-id] td.break,
  section:not(.tipsPage) tr[data-record-id] td.direction {
    flex: 0 0 auto;
    font-size: 11px;
  }

  /* ten-string rows have no name cell: push the stats line right */
  section:not(.tipsPage) tr[data-record-id] td.cmd + td.fr {
    margin-left: auto;
  }

  /* stat separators (td.cmd precedes td.fr in the DOM, so it is never matched) */
  section:not(.tipsPage) tr[data-record-id] td.fr ~ td:not(.cmd)::before {
    content: "·";
    margin-right: 8px;
    opacity: .45;
  }

  section:not(.tipsPage) tr[data-record-id] td.cmd {
    order: 2;
    flex: 0 0 100%;
    font-size: 11px;
  }

  section:not(.tipsPage) tr[data-record-id] td.cmd .cmd-gfx {
    white-space: normal;
  }

  section:not(.tipsPage) tr[data-record-id] td.cmd .tk-in,
  section:not(.tipsPage) tr[data-record-id] td.cmd .tk-in.tk-cram,
  section:not(.tipsPage) tr[data-record-id] td.cmd .tk-in.tk-cram.tk-cram2 {
    flex-wrap: wrap;
    row-gap: .35em;
    font-size: 11px;
  }
}
```

- [ ] **Step 2: Rebuild all 36 Season 2 pages**

```bash
cd "C:/Users/luden/workspace/tekken8movelist"
python tools/build_season2.py
```

Expected: 36 lines of `built <key>: <file>.html`; `git status` shows the 36 `docs/*_tk8_movelist.html` modified (not xiaoyu/jun/kunimitsu/clive/law).

- [ ] **Step 3: Run the Python regression suites**

```bash
python -B -m unittest tools.test_season2_pages tools.test_law_page tools.test_site_publication -v
```

Expected: all pass (no suite references the old 600px rule — verified during planning).

- [ ] **Step 4: Run the QA subset — verify GREEN at 390px**

```bash
NODE_PATH="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules" \
  CHARACTERS=alisa,yoshimitsu node tools/validate_season2.mjs
```

Expected: exit code 0, `failureCount: 0`, `stateCount: 20`.

- [ ] **Step 5: Run the full 360-state browser QA**

```bash
NODE_PATH="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules" \
  node tools/validate_season2.mjs
```

Expected: exit code 0, `stateCount: 360`, `failureCount: 0`. If a `table.cb` (combos) horizontal-overflow failure appears at 390px, add inside the 640px block and re-run from Step 2:

```css
  table.cb td:first-child {
    width: auto;
    border-right: 0;
  }
```

- [ ] **Step 6: Commit**

```bash
git add tools/season2_page.css docs/
git commit -m "Add responsive phone layout to Season 2 movelist pages"
```

---

### Task 3: Inject the phone block into the 5 legacy pages

**Files:**
- Modify: `docs/xiaoyu_tk8_movelist.html`, `docs/jun_tk8_movelist.html`, `docs/kunimitsu_tk8_movelist.html`, `docs/clive_tk8_movelist.html`, `docs/law_tk8_movelist.html` — insert one `<style id="mobile-phone">` block immediately before `</head>` in each
- Create: `workbench/qa/check_legacy_mobile.mjs` (verification script; `workbench/` is git-ignored scratch space)

**Interfaces:**
- Consumes: Task 2's layout contract, adapted to legacy markup: movelist tables are plain `<table>` (no `.move-table` class), rows are plain `<tr>` (no `data-record-id`), no `<thead>` (header rows are `<tr><th>…` inside the implicit `<tbody>`), throw rows carry two unclassed cells (`<td>正面</td>` direction, `<td>1+2</td>` break), stance matrices are `<table class="lt">`, combos are `<table class="cb">`. `pipeline.py` refuses to reprocess these pages, so hand-editing them is correct here.
- Produces: `workbench/qa/check_legacy_mobile.mjs` used by Task 5's full verification.

- [ ] **Step 1: Verify the structural assumptions hold on all 5 pages**

```bash
cd "C:/Users/luden/workspace/tekken8movelist"
for c in xiaoyu jun kunimitsu clive law; do
  echo "== $c"
  grep -c '<td class="name">' docs/${c}_tk8_movelist.html
  grep -c '<thead>' docs/${c}_tk8_movelist.html
  grep -c 'data-record-id' docs/${c}_tk8_movelist.html
  grep -c 'table class="cb"' docs/${c}_tk8_movelist.html
done
```

Expected for every page: `td.name` count > 50, `<thead>` count 0, `data-record-id` count 0. If a page deviates (e.g. has `<thead>` or table classes), adapt that page's injected selectors accordingly instead of applying the block blindly.

- [ ] **Step 2: Insert the phone style block before `</head>` in all 5 pages**

Insert exactly this (identical for all 5 pages) on its own line immediately before `</head>`:

```html
<style id="mobile-phone">
/* phone layout (<=640px): 1 move per row — line 1 name + stats, line 2 full-width command.
   Legacy pages use plain <table>/<tr> (no .move-table / data-record-id), so rows are
   matched via :has(> td.name); header rows (<tr><th>…) are hidden. */
@media (max-width: 640px) {
  body {
    zoom: 1;
    padding: 8px;
    font-size: 12px;
  }

  .legend {
    font-size: 11px;
  }

  table.lt,
  table.lt > tbody,
  table.lt > tbody > tr,
  table.lt > tbody > tr > td.ltc {
    display: block;
    width: 100%;
  }

  table.lt > tbody > tr > td.ltc + td.ltc {
    padding: 10px 0 0 !important;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) {
    display: block;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) > tbody {
    display: block;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) > tbody > tr:has(> th) {
    display: none;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) > tbody > tr:has(> td.name) {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 6px 8px;
    padding: 6px 2px;
    border-bottom: 1px solid #f5ecf1;
  }

  html.dark section:not(.tipsPage) table:not(.lt):not(.cb) > tbody > tr:has(> td.name) {
    border-bottom-color: #232a33;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) > tbody > tr:has(> td.name) > td {
    display: block;
    padding: 0;
    border-bottom: 0;
    white-space: normal;
    overflow: visible;
    background: none;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) > tbody > tr:nth-child(even):has(> td.name) {
    background: #fcf7fa;
  }

  html.dark section:not(.tipsPage) table:not(.lt):not(.cb) > tbody > tr:nth-child(even):has(> td.name) {
    background: #161b22;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) td.name {
    flex: 1 1 auto;
    min-width: 0;
    font-size: 13px;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) td.fr,
  section:not(.tipsPage) table:not(.lt):not(.cb) td.dmg,
  section:not(.tipsPage) table:not(.lt):not(.cb) td.rng,
  section:not(.tipsPage) table:not(.lt):not(.cb) td:not([class]) {
    flex: 0 0 auto;
    font-size: 11px;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) td.cmd + td.fr {
    margin-left: auto;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) td.fr ~ td:not(.cmd)::before {
    content: "·";
    margin-right: 8px;
    opacity: .45;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) td.cmd {
    order: 2;
    flex: 0 0 100%;
    font-size: 11px;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) td.cmd .cmd-gfx {
    white-space: normal;
  }

  section:not(.tipsPage) table:not(.lt):not(.cb) td.cmd .tk-in {
    flex-wrap: wrap;
    row-gap: .35em;
    font-size: 11px;
  }
}
</style>
```

Note: the two legacy-only colors (`#f5ecf1`/`#fcf7fa` light, `#232a33`/`#161b22` dark) mirror each page's existing td-border and zebra colors; the pages' own `@media screen { body { zoom: 1.25; } }` and `@media (max-width: 760px)` rules stay untouched (the Law regression test asserts their presence).

- [ ] **Step 3: Run the legacy-affecting regression suites**

```bash
python -B -m unittest tools.test_law_page tools.test_site_publication -v
```

Expected: all pass (the Law contract test only asserts presence of existing rules; the injection adds, never removes).

- [ ] **Step 4: Write the legacy phone verification script**

Create `workbench/qa/check_legacy_mobile.mjs`:

```js
import { existsSync } from 'node:fs';
import { createRequire } from 'node:module';
import { isAbsolute, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const pages = ['xiaoyu', 'jun', 'kunimitsu', 'clive', 'law'];
const repoRoot = resolve(process.cwd());

function findChrome() {
  if (process.env.CHROME_PATH) {
    const configured = isAbsolute(process.env.CHROME_PATH)
      ? process.env.CHROME_PATH
      : resolve(process.cwd(), process.env.CHROME_PATH);
    if (existsSync(configured)) return configured;
  }
  const candidates = [
    process.env.ProgramFiles && join(process.env.ProgramFiles, 'Google', 'Chrome', 'Application', 'chrome.exe'),
    process.env['ProgramFiles(x86)'] && join(process.env['ProgramFiles(x86)'], 'Google', 'Chrome', 'Application', 'chrome.exe'),
    process.env.LOCALAPPDATA && join(process.env.LOCALAPPDATA, 'Google', 'Chrome', 'Application', 'chrome.exe'),
  ].filter(Boolean);
  const detected = candidates.find((candidate) => existsSync(candidate));
  if (!detected) throw new Error(`Chrome not found; set CHROME_PATH. Checked: ${candidates.join(', ')}`);
  return detected;
}

const results = [];
const browser = await chromium.launch({ executablePath: findChrome(), headless: true });
try {
  for (const name of pages) {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    try {
      const page = await context.newPage();
      await page.goto(pathToFileURL(join(repoRoot, 'docs', `${name}_tk8_movelist.html`)).href, { waitUntil: 'load' });
      const m = await page.evaluate(() => {
        const rowSel = 'section:not(.tipsPage) table:not(.lt):not(.cb) > tbody > tr';
        const dataRows = [...document.querySelectorAll(`${rowSel}:has(> td.name)`)];
        const stackingIssues = dataRows.flatMap((row) => {
          const cmd = row.querySelector('td.cmd');
          const nameCell = row.querySelector('td.name');
          const r = row.getBoundingClientRect();
          const c = cmd.getBoundingClientRect();
          const n = nameCell.getBoundingClientRect();
          const bad = [];
          if (c.top < n.bottom - 1) bad.push('cmd not stacked');
          if (Math.abs(c.left - r.left) > 3) bad.push('cmd not full-width');
          return bad.length ? [`${nameCell.textContent}: ${bad.join(', ')}`] : [];
        });
        return {
          zoom: getComputedStyle(document.body).zoom,
          overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
          dataRowCount: dataRows.length,
          headerRowsHidden: [...document.querySelectorAll(`${rowSel}:has(> th)`)]
            .every((tr) => getComputedStyle(tr).display === 'none'),
          stackingIssues: stackingIssues.slice(0, 5),
        };
      });
      const problems = [];
      if (m.zoom !== '1') problems.push(`zoom=${m.zoom}`);
      if (m.overflow > 1) problems.push(`horizontal overflow ${m.overflow}px`);
      if (m.dataRowCount < 50) problems.push(`only ${m.dataRowCount} data rows`);
      if (!m.headerRowsHidden) problems.push('header rows still visible');
      problems.push(...m.stackingIssues);
      results.push({ name, ok: problems.length === 0, problems });
    } finally {
      await context.close();
    }
  }
} finally {
  await browser.close();
}
console.log(JSON.stringify(results, null, 2));
process.exitCode = results.every((r) => r.ok) ? 0 : 1;
```

- [ ] **Step 5: Run the legacy verification**

```bash
NODE_PATH="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules" \
  node workbench/qa/check_legacy_mobile.mjs
```

Expected: exit code 0; all 5 entries `"ok": true` with empty `problems`.

- [ ] **Step 6: Manual spot-check of `docs/law_tk8_movelist.html` in Chrome**

Open the file in Chrome, DevTools device toolbar at 390px width, and verify: no horizontal scrollbar; each move is one stacked row (name+stats, then full-width button-map command); a 十连技/十连 string wraps onto multiple lines; `按键图/无数字/文字` switch re-renders commands; `夜间/浅色` switch still works; desktop width renders exactly as before.

- [ ] **Step 7: Commit**

```bash
git add docs/xiaoyu_tk8_movelist.html docs/jun_tk8_movelist.html docs/kunimitsu_tk8_movelist.html docs/clive_tk8_movelist.html docs/law_tk8_movelist.html
git commit -m "Add phone layout to the five legacy movelist pages"
```

---

### Task 4: Homepage mobile fix (avatars + zoom)

**Files:**
- Modify: `docs/index.html:295-299` (the existing `@media (max-width:640px)` block)

**Interfaces:**
- Consumes: existing card markup `.card > .cimg > img` (spans, blockified as flex items), `--tile-w/--tile-h` tokens, `@media screen{body{zoom:1.25}}` at `docs/index.html:47`.
- Produces: 2-column portrait cards on phones; desktop rendering unchanged.

- [ ] **Step 1: Rewrite the 640px block**

In `docs/index.html`, replace lines 295-299:

```css
@media (max-width:640px){
  :root{--tile-w:132px;--tile-h:172px}
  h1{font-size:26px}
  footer{grid-template-columns:1fr;gap:16px}
}
```

with:

```css
@media (max-width:640px){
  body{zoom:1}
  .wrap{padding:16px 14px 48px}
  .grid{grid-template-columns:repeat(2,1fr);gap:10px}
  .card{height:auto}
  .cimg{flex:none;aspect-ratio:4/5}
  h1{font-size:26px}
  footer{grid-template-columns:1fr;gap:16px}
}
```

(`--tile-w`/`--tile-h` overrides are dropped: the fixed 2-column grid no longer uses `--tile-w`, and `.card{height:auto}` frees the tile from `--tile-h`. `object-fit:cover;object-position:top` is unchanged, so the 4:5 portrait area shows head and shoulders. The 640px block sits later than the `zoom:1.25` rule at line 47, so `zoom:1` wins at equal specificity.)

- [ ] **Step 2: Run the site publication suite**

```bash
python -B -m unittest tools.test_site_publication -v
```

Expected: all pass (homepage link/avatar inventory unchanged).

- [ ] **Step 3: Manual check of `docs/index.html` in Chrome**

At 390px (device toolbar): exactly 2 columns; avatars show head+shoulders (not a top sliver); page is not zoomed; search filter still narrows the grid; theme toggle swaps dark/light avatar sets; tap target of a card opens the character page. At desktop width: rendering pixel-identical to before.

- [ ] **Step 4: Commit**

```bash
git add docs/index.html
git commit -m "Fix homepage avatars and zoom on phones"
```

---

### Task 5: Full gate + documentation

**Files:**
- Modify: `tools/KNOWLEDGE.md` (append one section)

**Interfaces:**
- Consumes: everything above; `workbench/qa/check_legacy_mobile.mjs` from Task 3.
- Produces: a documented phone-layout contract for future maintainers.

- [ ] **Step 1: Document the phone layout contract**

Append to the end of `tools/KNOWLEDGE.md`:

```markdown
## Phone layout (added 2026-07)

- All 41 movelist pages reflow at `@media (max-width: 640px)`: line 1 = move name +
  stats, line 2 = full-width command; long commands wrap (`tk-in` groups +
  mega-token break rule). Body `zoom` resets to 1 on phones.
- Season 2 pages: the block lives in `tools/season2_page.css` (end of file) —
  edit there and rebuild; never hand-edit generated pages.
- Legacy 5 pages: an equivalent `<style id="mobile-phone">` block sits before
  `</head>` (plain-table markup, rows matched via `:has(> td.name)`).
- `tools/validate_season2.mjs` asserts zero horizontal overflow + stacked rows at
  390px; `contentOverlaps` is skipped at ≤640px because cells stack vertically.
  Legacy pages are covered by `workbench/qa/check_legacy_mobile.mjs` (ignored
  scratch, re-create from the plan in `design/plans/2026-07-21-mobile-support.md`
  if deleted).
```

- [ ] **Step 2: Run the complete gate (no skips)**

```powershell
pwsh -File tools\validate_season2.ps1
```

Expected: every step passes — Python compile, Season 2 rebuild (no diff produced, since Task 2 already rebuilt with the same sources), 3 unittest suites, 360-state browser QA.

- [ ] **Step 3: Re-run the legacy phone check**

```bash
NODE_PATH="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules" \
  node workbench/qa/check_legacy_mobile.mjs
```

Expected: exit code 0, all 5 pages `"ok": true`.

- [ ] **Step 4: Final manual homepage check**

Repeat Task 4 Step 3 (390px + desktop) against the final state.

- [ ] **Step 5: Commit**

```bash
git add tools/KNOWLEDGE.md
git commit -m "Document phone layout contract"
```

---

## Self-Review Notes (already applied)

- **Spec coverage:** Season 2 CSS (Task 2), legacy 5 pages (Task 3), homepage (Task 4), QA updates (Task 1, gate in Task 5), button-map preservation (CSS keeps `tk-in` intact; QA checks gfx mode at 390px), long-command wrapping (`flex-wrap` + mega-token rule; manual check Task 3 Step 6). All spec items mapped.
- **`docs/superpowers/` deviation:** plan lives in `design/plans/` because `docs/` is the public GitHub Pages root.
- **Legacy pages are hand-edited intentionally:** `pipeline.py` aborts on already-processed pages (`"already processed, aborting"`), so a pipeline injection step could never touch them.
- **Type/selector consistency:** QA phone metrics use the same `tr[data-record-id]` / `td.name` / `td.cmd` / `td.fr` contract the CSS implements; legacy script uses the `:has(> td.name)` contract from the injected block.
