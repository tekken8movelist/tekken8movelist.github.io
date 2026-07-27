# Repository Guidance

## Canonical layout

- `docs/` is the only publishable website root and the GitHub Pages source.
- `docs/index.html` is the hand-maintained character-select homepage.
- `docs/*_tk8_movelist.html` contains the 41 published character pages (Simplified).
- `docs/zh-Hant/` and `docs/en/` are generated locale trees: 36 generator-owned
  pages plus a derived hub each. Never hand-edit anything under them; change the
  source or `tools/locales.py` and rebuild. The five pipeline pages exist only in
  Simplified until they are migrated into the generator; the derived hubs point
  their cards at `../` so those links resolve instead of 404ing.
- `docs/avatars/` contains the final homepage portraits. The homepage is dark-only (no theme toggle since flux v3); `docs/avatars-light/` was removed in that change. Other local avatar directories are experiments or backups and are intentionally ignored.
- `tools/source/` is the structured source of truth for generated character pages.
- `tools/` contains generators, source snapshots, regression tests, and browser QA.
- `tools/jun_movelist_source_template.html` is the legacy pipeline input reference, not a published page.
- `design/notation-wireframe/` is the maintained reference for the shared input-notation component.
- `design/movelist-hub-prototype/` is a local, ignored design export. It is reference-only and must not be treated as production source or a publishable artifact.
- `design/plans/` and `design/specs/` are local working documents. They are git-ignored for new files; files already committed stay on GitHub and remain tracked.
- `workbench/` is local, ignored scratch space for avatar masters, backups, variants, and experimental tooling. Nothing under it is a release input unless deliberately promoted into a tracked canonical path.

Do not recreate generated HTML at the repository root. Do not treat ignored design exports, avatar masters, or backup directories as publishable inputs.

## Editing rules

- Do not hand-edit generated pages covered by `tools/build_season2.py`. Update the structured source or generator and rebuild.
- The five legacy pipeline pages (`xiaoyu`, `jun`, `kunimitsu`, `clive`, and `law`) use `tools/pipeline.py`; read `CLAUDE.md` and `tools/KNOWLEDGE.md` before changing them.
- The header card and back navigation are shared by both page families through `tools/header_card.css`, `tools/back_nav.css`, and `tools/back_nav.js`. Edit those, then rebuild the generator pages and re-run `tools/patch_legacy_pages.py` for the five legacy ones; never patch either family by hand.
- Character country and fighting style come from `tools/source/official_profiles.json`, snapshotted from tekken.com. Refresh it with `tools/fetch_official_profiles.py`; add any new vocabulary to `tools/official_profile_zh.py` rather than letting English reach a page.
- `docs/index.html` may be edited directly, but preserve relative links so the site works from the GitHub Pages root and a local `docs/` server.
- After editing the hub, run `tools/augment_hub.py` (adds the language control and
  Traditional search terms) and `tools/build_hub.py` (derives the other two hubs).
  Both are idempotent and both are in the gate.
- Keep public attribution and the unofficial/non-commercial/non-affiliation disclaimer intact unless the underlying sources or rights context changes.
- Never commit local QA screenshots, avatar experiments, design exports, caches, or backup folders.

## Required validation

Run the complete gate before publishing:

```powershell
pwsh -File tools\validate_season2.ps1
```

The gate rebuilds all generator-owned pages in all three locales, rebuilds the
derived hubs and the sitemap, runs the locale, Traditional-conversion, Season 2,
Law, and site-publication regression suites, and checks 648 browser states
(Simplified 36x10, Traditional and English 36x4 each) plus 15 pipeline-page
legend states. Do not claim a release is validated when using `-SkipBrowser`.

Also verify `docs/index.html` at desktop and mobile widths, confirm all homepage links and avatar paths resolve, and check the deployed GitHub Pages URL after publishing.

## GitHub Pages

- Repository: `tekken8movelist/tekken8movelist.github.io`
- Source: `main` branch, `/docs` folder
- Expected URL: `https://tekken8movelist.github.io/`
