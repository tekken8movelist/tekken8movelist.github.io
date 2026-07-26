# -*- coding: utf-8 -*-
"""One-time cross-check: does the vendored-dictionary walker equal real OpenCC?

Not a build dependency and not part of the gate -- `tools/zh_hant.py` carries
OpenCC's dictionaries but not OpenCC, so this script is how that claim gets
tested for real. Run it in a throwaway environment that has
`opencc-python-reimplemented` installed, against the whole corpus:

    python -m venv .venv-opencc
    .venv-opencc/Scripts/python -m pip install opencc-python-reimplemented
    .venv-opencc/Scripts/python tools/verify_zh_hant.py

Re-run it whenever tools/opencc/*.txt is refreshed. Exit code 0 = equivalent.
Last run: 2026-07-26, 6,924 strings across 36 snapshots, 0 mismatches.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from zh_hant import convert  # noqa: E402

try:
    from opencc import OpenCC
except ImportError:  # pragma: no cover - the whole point of this script
    raise SystemExit(
        "opencc-python-reimplemented is not installed; see this file's docstring"
    )


def corpus() -> list[tuple[str, str, str]]:
    """(character, field/id, Simplified string) over every checked-in snapshot."""
    entries: list[tuple[str, str, str]] = []
    for path in sorted((TOOLS / "source").glob("*_zh.json")):
        key = path.stem.removesuffix("_zh")
        document = json.loads(path.read_text(encoding="utf-8"))
        for field in ("move_names", "section_names", "stance_names"):
            for name, value in (document.get(field) or {}).items():
                entries.append((key, f"{field}/{name}", value))
    return entries


def main() -> int:
    reference = OpenCC("s2twp")
    entries = corpus()
    mismatches = []
    for key, where, value in entries:
        expected = reference.convert(value)
        actual = convert(value)
        if expected != actual:
            mismatches.append((key, where, value, expected, actual))

    print(f"checked {len(entries)} strings from {len(list((TOOLS / 'source').glob('*_zh.json')))} snapshots")
    print(f"mismatches: {len(mismatches)}")
    for key, where, value, expected, actual in mismatches[:40]:
        print(f"  {key:12s} {where:34s} {value!r}")
        print(f"      opencc={expected!r}  ours={actual!r}")
    if len(mismatches) > 40:
        print(f"  ... and {len(mismatches) - 40} more")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
