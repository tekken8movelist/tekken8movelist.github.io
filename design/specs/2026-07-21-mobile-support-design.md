# Mobile Support Design — Character Pages + Homepage

Date: 2026-07-21
Status: approved by user (brainstorming session, visual companion mockups in `.superpowers/brainstorm/490-1784607280/content/`)

## Problem

- **Character movelist pages** (`docs/*_tk8_movelist.html`, 41 pages): the current
  "mobile strategy" pins `body` to a fixed 600px width at `max-width:600px`, forcing
  horizontal overflow / pinch-zoom on phones. Not a real responsive layout.
- **Homepage** (`docs/index.html`): the desktop `@media screen{body{zoom:1.25}}` is
  never reset on small screens, and the 132px-wide mobile tile gives the image area
  only ~124px height (landscape band). Avatars are 512×512 squares cropped with
  `object-fit:cover;object-position:top`, so phones show only a top sliver of each head.

## Decisions (from brainstorming)

- Scope: all 41 movelist pages + homepage.
- Movelist mobile layout: **two-line list rows** (mockup option B) — line 1: move
  name (left) + stats (`i10 · 5 · 上`, right); line 2: the command on its own
  full-width line. Long commands (ten-hit strings, long combo routes) wrap onto
  additional lines instead of squeezing.
- The full `tk-in` button-map graphics (2×2 button grid, direction arrows, stance
  pills) render unchanged on mobile — no fallback to plain text. All three notation
  modes (`按键图 / 无数字 / 文字`) keep working.
- Homepage mobile layout: **portrait 4:5 image area, 2 columns** (mockup option A).

## Breakpoint strategy (site-wide)

- `≤640px`: phone layout (new).
- 641–1280px: existing single-column fallback (`.cols2`/`.colsRow` collapse) — unchanged.
- `>1280px`: desktop — completely unchanged.
- Every page resets `zoom:1` and clears fixed body widths inside the phone breakpoint.

## 1. Season 2 pages (36 generated pages)

Single edit point: `tools/season2_page.css`. Then rebuild via `tools/build_season2.py`
(the gate does this). Pure CSS reflow — no HTML-structure or JS changes.

- Replace the `@media (max-width:600px)` pinned-width block with a
  `@media (max-width:640px)` phone block:
  - `body { zoom:1; width:auto; min-width:0; padding:8px; }`
  - Move tables (`.move-table`, `.throw-table`, ten-hit table) reflow:
    - `thead` hidden; `table/tbody/tr/td` become block-level within the breakpoint.
    - Each `tr[data-record-id]` becomes a wrapping flex row:
      - Line 1: `td.name` (left) + stats (`td.fr`/`td.dmg`/`td.rng`, and the extra
        throw-table column) joined inline with ` · ` separators (right).
      - Line 2: `td.cmd` at `flex-basis:100%` — the command always gets its own
        full-width line below the name/stats line.
    - Long commands (ten-hit strings, long combo routes) wrap naturally onto
      additional lines inside that full-width command line — `tk-in` groups wrap
      at token boundaries, and the existing mega-token break rule
      (long unspaced route notation) keeps working. No squeezing, no cram tiers
      needed on phones.
    - Section/stance header rows inside tables stay full-width banners.
  - `tk-in` graphics render at normal size in the command line. The `tk-cram`
    shrink classes stay in the emitted markup (no generator change), but the
    phone breakpoint overrides them to normal size — wrapping replaces squeezing.
  - Header control bar (theme/notation segmented toggles) allowed to wrap.
  - `.legend` blocks wrap naturally; combos section is text-flow already — verify
    no overflow via QA.
- No changes to `tools/season2_page.js`.

## 2. Legacy pages (xiaoyu, jun, kunimitsu, clive, law)

- Maintained by in-place rewriting via `tools/pipeline.py`. Extend it with an
  idempotent "mobile CSS injection" step (same pattern as the existing
  `GFX_LEGEND` / notation-CSS injection) that inserts the equivalent phone block
  into each page's inline `<style>`; re-run the pipeline to apply.
- Per `AGENTS.md`: read `CLAUDE.md` and `tools/KNOWLEDGE.md` first. Verify legacy
  table classes match the Season 2 markup (`td.name/cmd/fr/dmg/rng`); if they
  differ, adapt the injected CSS to the legacy markup.
- Check whether legacy pages carry their own `zoom` or fixed-width rules and
  neutralize them inside the same breakpoint.

## 3. Homepage (`docs/index.html`, hand-maintained — edit directly)

Inside the existing `@media (max-width:640px)` block:

- `body { zoom:1 }` — cancel the desktop 1.25 zoom.
- Grid: fixed two columns (`grid-template-columns:repeat(2,1fr)`).
- `.cimg { aspect-ratio:4/5; flex:none; height:auto; }` — portrait image area;
  tile no longer bound by `--tile-h`; `object-position:top` unchanged so
  head+shoulders show fully.
- Nameplate, search box, theme toggle, footer (already single-column): verify fit
  only, no structural changes.

## 4. QA gate updates

- `tools/validate_season2.mjs`:
  - Rewrite the 390px assertions: from "must overflow horizontally with scroll
    width 595–605" to **zero horizontal overflow** (`scrollWidth ≈ clientWidth`).
  - Add stacked-layout assertions at 390px: e.g. within a `tr[data-record-id]`,
    the `td.cmd` box starts below the `td.name` box, and row height exceeds the
    desktop 38px row height.
  - Keep `responsiveWidths = [1280, 1024, 760, 390]`; 760/1024/1280 assertions
    unchanged.
- Check `tools/test_season2_pages.py` (and other regression suites) for assertions
  referencing the old 600px pinned-width rule; update to the new 640px block.
- Full gate before publishing: `pwsh -File tools\validate_season2.ps1`
  (rebuild + 3 unittest suites + 360 browser states). No `-SkipBrowser`.
- Manually verify `docs/index.html` at desktop and mobile widths; confirm all
  homepage links and avatar paths resolve; check the deployed GitHub Pages URL
  after publishing.

## Explicitly out of scope

- No new avatar assets (keeps the 512×512 squares; CSS-only fix).
- No desktop styling changes of any kind.
- No new JS interactions (no expand/collapse, no sticky headers).
- No changes to combo/move data sources.
