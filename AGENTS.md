# Repository Guidance

## Canonical layout

- `docs/` is the only publishable website root and the GitHub Pages source.
- `docs/index.html` is the hand-maintained character-select homepage.
- `docs/*_tk8_movelist.html` contains the 41 published character pages.
- `docs/avatars/` contains the final homepage portraits. Other local avatar directories are experiments or backups and are intentionally ignored.
- `tools/source/` is the structured source of truth for generated character pages.
- `tools/` contains generators, source snapshots, regression tests, and browser QA.
- `tools/jun_movelist_source_template.html` is the legacy pipeline input reference, not a published page.
- `design/notation-wireframe/` is the maintained reference for the shared input-notation component.
- `design/movelist-hub-prototype/` is a local, ignored design export. It is reference-only and must not be treated as production source or a publishable artifact.
- `workbench/` is local, ignored scratch space for avatar masters, backups, variants, and experimental tooling. Nothing under it is a release input unless deliberately promoted into a tracked canonical path.

Do not recreate generated HTML at the repository root. Do not treat ignored design exports, avatar masters, light-theme variants, or backup directories as publishable inputs.

## Editing rules

- Do not hand-edit generated pages covered by `tools/build_season2.py`. Update the structured source or generator and rebuild.
- The five legacy pipeline pages (`xiaoyu`, `jun`, `kunimitsu`, `clive`, and `law`) use `tools/pipeline.py`; read `CLAUDE.md` and `tools/KNOWLEDGE.md` before changing them.
- `docs/index.html` may be edited directly, but preserve relative links so the site works under `/tekken8movelist/` on GitHub Pages.
- Keep public attribution and the unofficial/non-commercial/non-affiliation disclaimer intact unless the underlying sources or rights context changes.
- Never commit local QA screenshots, avatar experiments, design exports, caches, or backup folders.

## Required validation

Run the complete gate before publishing:

```powershell
pwsh -File tools\validate_season2.ps1
```

The gate rebuilds all generator-owned pages, runs the Season 2, Law, and site-publication regression suites, and checks 360 browser states. Do not claim a release is validated when using `-SkipBrowser`.

Also verify `docs/index.html` at desktop and mobile widths, confirm all homepage links and avatar paths resolve, and check the deployed GitHub Pages URL after publishing.

## GitHub Pages

- Repository: `ludengz/tekken8movelist`
- Source: `main` branch, `/docs` folder
- Expected URL: `https://ludengz.github.io/tekken8movelist/`
