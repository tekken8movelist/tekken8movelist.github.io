# -*- coding: utf-8 -*-
"""List move names whose Traditional conversion is worth a human's eyes.

The s2twp table is right almost always, but Simplified merged several distinct
Traditional characters into one, and only context tells them apart: 发 is 發 or
髮, 里 is 裡 or 里, 干 is 乾/幹/干. Move names are short and idiomatic, which is
exactly where the phrase tables have the least to go on.

This prints every name containing one of those characters, next to what the
converter produced, so a reviewer can spot the wrong branch and register it in
tools/zh_hant_overrides.json (keyed by move id).

    python tools/scan_hant_suspects.py            # every character
    python tools/scan_hant_suspects.py jin lili   # just these
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from zh_hant import convert, simplified_only_codepoints  # noqa: E402

# Simplified characters that stand for more than one Traditional character.
# Not an exhaustive list of merges -- these are the ones that actually turn up
# in fighting-game move names.
AMBIGUOUS = "发里干后台松面历表钟制准范困游余系向志志板丑冲划"


def main(argv: list[str]) -> int:
    wanted = set(argv[1:])
    alphabet = simplified_only_codepoints()
    suspects = 0
    stray = 0
    for path in sorted((TOOLS / "source").glob("*_zh.json")):
        key = path.stem.removesuffix("_zh")
        if wanted and key not in wanted:
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        for move_id, name in (document.get("move_names") or {}).items():
            converted = convert(name)
            if set(converted) & alphabet:
                print(f"!! {key:12s} {move_id:30s} {name} -> {converted}  "
                      f"UNCONVERTED {sorted(set(converted) & alphabet)}")
                stray += 1
            elif set(name) & set(AMBIGUOUS):
                print(f"   {key:12s} {move_id:30s} {name} -> {converted}")
                suspects += 1
    print(f"\n{suspects} name(s) to review, {stray} with unconverted glyphs")
    return 1 if stray else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
