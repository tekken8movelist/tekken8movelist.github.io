# -*- coding: utf-8 -*-
"""Generate docs/sitemap.xml across every locale tree.

Driven by what is actually on disk rather than by a roster constant: the five
pipeline pages exist only in Simplified, so listing three URLs for them would
point Google at files that are not there. A page gets `xhtml:link` alternates
for exactly the locales it was built in.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from locales import DEFAULT_LOCALE, LOCALES, public_url  # noqa: E402

SITE = TOOLS.parent / "docs"
SITEMAP = SITE / "sitemap.xml"


def locale_dir(locale: str) -> Path:
    directory = LOCALES[locale]["dir"]
    return SITE / directory if directory else SITE


def built_pages() -> dict[str, list[str]]:
    """filename -> the locales it exists in, hub first, then characters."""
    pages: dict[str, list[str]] = {}
    for name in ["index.html"] + sorted(
        path.name for path in SITE.glob("*_tk8_movelist.html")
    ):
        present = [
            locale
            for locale in LOCALES
            if (locale_dir(locale) / name).is_file()
        ]
        if present:
            pages[name] = present
    return pages


def render() -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
        ' xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for name, present in built_pages().items():
        for locale in present:
            entry = [f"  <url><loc>{public_url(locale, name)}</loc>"]
            for other in present:
                entry.append(
                    f'<xhtml:link rel="alternate" '
                    f'hreflang="{LOCALES[other]["hreflang"]}" '
                    f'href="{public_url(other, name)}"/>'
                )
            if DEFAULT_LOCALE in present:
                entry.append(
                    '<xhtml:link rel="alternate" hreflang="x-default" '
                    f'href="{public_url(DEFAULT_LOCALE, name)}"/>'
                )
            entry.append("</url>")
            lines.append("".join(entry))
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if sitemap.xml is out of date")
    args = parser.parse_args(argv)

    content = render()
    total = content.count("<loc>")
    if args.check:
        current = SITEMAP.read_text(encoding="utf-8") if SITEMAP.is_file() else ""
        if current != content:
            print(f"STALE docs/sitemap.xml (expected {total} URLs)")
            return 1
        print(f"ok    docs/sitemap.xml ({total} URLs)")
        return 0

    SITEMAP.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote docs/sitemap.xml ({total} URLs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
