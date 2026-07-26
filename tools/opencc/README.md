# Vendored OpenCC dictionaries

These four files are OpenCC's own conversion dictionaries, **copied verbatim**
from the `opencc-python-reimplemented` wheel. They are not edited, and nothing
in this repository is allowed to edit them — if a conversion is wrong for one
move, that goes in `tools/zh_hant_overrides.json`, not here.

| file | role in the chain |
|---|---|
| `STPhrases.txt` | Simplified → Traditional, phrases (49,051 entries) |
| `STCharacters.txt` | Simplified → Traditional, characters (3,980 entries) |
| `TWPhrases.txt` | Traditional → Taiwan vocabulary (509 entries) |
| `TWVariants.txt` | Traditional → Taiwan glyph variants (39 entries) |

## Why vendor them instead of depending on OpenCC

`tools/build_season2.py` is offline, stdlib-only and byte-reproducible, and the
Traditional locale must not cost that. Neither Python on this machine (the one
on `PATH`, nor the bundled runtime `validate_season2.ps1` actually resolves)
ships `opencc`, so depending on the package would mean the gate cannot run
until someone remembers to install it.

Vendoring the upstream text — rather than a JSON table derived from it — is
what makes the claim auditable: "is this really `s2twp`?" is answerable with a
`diff` against upstream, not with trust in a conversion script.

## Provenance

- Package: `opencc-python-reimplemented` 0.1.7
  (<https://github.com/yichen0831/opencc-python>)
- Upstream data: OpenCC (<https://github.com/BYVoid/OpenCC>)
- Licence: Apache License 2.0 — see `LICENSE.txt` in this directory
- Extracted: 2026-07-26

The pass order in `tools/zh_hant.py` is taken from the package's own
`opencc/config/s2twp.json`:

```
1. group(STPhrases, STCharacters)   Simplified  -> Traditional
2. TWPhrases                        Traditional -> Taiwan vocabulary
3. TWVariants                       Traditional -> Taiwan glyph variants
```

## Refreshing them

```powershell
python -m pip download opencc-python-reimplemented --no-deps -d $env:TEMP\occ
# extract opencc/dictionary/{STPhrases,STCharacters,TWPhrases,TWVariants}.txt
# and opencc_python_reimplemented-*.dist-info/LICENSE.txt into this directory,
# normalising line endings to LF
```

Then re-run the equivalence check, which is the only thing that proves the
walker in `zh_hant.py` still matches the real converter:

```powershell
python -m venv .venv-opencc
.venv-opencc\Scripts\python -m pip install opencc-python-reimplemented
.venv-opencc\Scripts\python tools\verify_zh_hant.py
```

Expected: `mismatches: 0` over every string in `tools/source/*_zh.json`.
Also re-run `python tools/scan_hant_suspects.py` and expect
`0 with unconverted glyphs`.
