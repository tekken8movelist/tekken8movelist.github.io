# -*- coding: utf-8 -*-
"""Generate docs/sitemap.xml across every locale tree.

Driven by what is actually on disk rather than by a roster constant: the five
pipeline pages exist only in Simplified, so listing three URLs for them would
point Google at files that are not there. A page gets `xhtml:link` alternates
for exactly the locales it was built in.

Each URL also carries <lastmod>, the day its page last changed. Google and
Bing use lastmod to schedule recrawls only while it stays accurate, so it is
derived from content rather than from file times or the build date:
tools/source/sitemap_lastmod.json keeps a SHA-256 and a date per URL, and a
page's date moves to today only when its bytes change. Rebuilding an
unchanged site leaves every date where it was.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from locales import DEFAULT_LOCALE, LOCALES, public_url  # noqa: E402

SITE = TOOLS.parent / "docs"
SITEMAP = SITE / "sitemap.xml"
LASTMOD = TOOLS / "source" / "sitemap_lastmod.json"


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


def load_lastmod() -> dict[str, dict[str, str]]:
    if LASTMOD.is_file():
        return json.loads(LASTMOD.read_text(encoding="utf-8"))
    return {}


def refresh_lastmod(manifest: dict, today: str) -> tuple[dict, int]:
    """The manifest for what is on disk now; a page whose bytes changed gets today."""
    fresh: dict[str, dict[str, str]] = {}
    changed = 0
    for name, present in built_pages().items():
        for locale in present:
            url = public_url(locale, name)
            digest = hashlib.sha256((locale_dir(locale) / name).read_bytes()).hexdigest()
            known = manifest.get(url)
            if known and known["sha256"] == digest:
                fresh[url] = known
            else:
                fresh[url] = {"sha256": digest, "lastmod": today}
                changed += 1
    return fresh, changed


def render(manifest: dict[str, dict[str, str]]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
        ' xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for name, present in built_pages().items():
        for locale in present:
            url = public_url(locale, name)
            entry = [
                f"  <url><loc>{url}</loc>"
                f"<lastmod>{manifest[url]['lastmod']}</lastmod>"
            ]
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
                        help="fail if sitemap.xml or its lastmod dates are out of date")
    args = parser.parse_args(argv)

    manifest, changed = refresh_lastmod(load_lastmod(), date.today().isoformat())
    content = render(manifest)
    total = content.count("<loc>")
    if args.check:
        current = SITEMAP.read_text(encoding="utf-8") if SITEMAP.is_file() else ""
        if changed or current != content:
            print(f"STALE docs/sitemap.xml ({changed} pages changed since their lastmod)")
            return 1
        print(f"ok    docs/sitemap.xml ({total} URLs)")
        return 0

    LASTMOD.write_text(
        json.dumps(manifest, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    SITEMAP.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote docs/sitemap.xml ({total} URLs, {changed} new lastmod dates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
