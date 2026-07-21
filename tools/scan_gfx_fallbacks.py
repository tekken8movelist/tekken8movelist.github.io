# -*- coding: utf-8 -*-
"""Scan all character pages for command cells that were NOT converted to
button-map (tk-in) markup. A converted cell contains <span class="cmd-gfx">.
Usage: python tools/scan_gfx_fallbacks.py [substr-filter]"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs"

# command-bearing cells: main tables use td.cmd; combos/ten-string may differ
CMD_CELL = re.compile(
    r'<td class="cmd[^"]*">((?:(?!</td>).)*?)</td>', re.S)

def scan(path):
    html = path.read_text(encoding="utf-8")
    misses = []
    for m in CMD_CELL.finditer(html):
        cell = m.group(1)
        if 'cmd-gfx' in cell:
            continue
        # strip tags to get the raw text
        text = re.sub(r"<[^>]+>", "", cell).strip()
        if text:
            misses.append(text)
    return misses

def main():
    filt = sys.argv[1] if len(sys.argv) > 1 else ""
    total = 0
    for path in sorted(SITE.glob("*_tk8_movelist.html")):
        if filt and filt not in path.name:
            continue
        misses = scan(path)
        total += len(misses)
        print(f"\n=== {path.name}  ({len(misses)} misses) ===")
        for t in misses:
            print("   ", t[:120])
    print(f"\nTOTAL misses: {total}")

if __name__ == "__main__":
    main()
