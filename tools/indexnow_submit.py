# -*- coding: utf-8 -*-
"""Tell IndexNow search engines (Bing, Yandex, Naver, Seznam, ...) what changed.

Google does not take part in IndexNow and retired its sitemap ping in 2023, so
for Google the sitemap in Search Console stays the channel; everything else
that honours IndexNow learns about new or changed pages from one POST here.

The key is not a secret: IndexNow proves ownership by fetching
`https://tekken8movelist.github.io/{KEY}.txt` and comparing. That file lives in
`docs/` and must already be published before a submission can succeed, so run
this *after* the push that carries the change has gone live on GitHub Pages.

    python tools/indexnow_submit.py                 # every URL in the sitemap
    python tools/indexnow_submit.py URL [URL ...]   # just these
    python tools/indexnow_submit.py --dry-run       # print the payload only
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from xml.etree import ElementTree

TOOLS = Path(__file__).resolve().parent
SITE = TOOLS.parent / "docs"
HOST = "tekken8movelist.github.io"
KEY = "35b2587af55415616ccdb53a4c9786cb"
KEY_FILE = SITE / f"{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def sitemap_urls() -> list[str]:
    root = ElementTree.parse(SITE / "sitemap.xml").getroot()
    return [loc.text for loc in root.findall("sm:url/sm:loc", SITEMAP_NS) if loc.text]


def payload(urls: list[str]) -> dict:
    foreign = [url for url in urls if not url.startswith(f"https://{HOST}/")]
    if foreign:
        raise SystemExit(f"not on {HOST}: {foreign}")
    return {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if KEY_FILE.read_text(encoding="utf-8").strip() != KEY:
        raise SystemExit(f"{KEY_FILE.name} does not hold the key")
    body = payload(args.urls or sitemap_urls())
    if args.dry_run:
        print(json.dumps(body, indent=2))
        return 0
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"IndexNow: HTTP {response.status} for {len(body['urlList'])} URLs")
            return 0
    except urllib.error.HTTPError as error:
        # 202 = accepted, key check pending; 403 = key file not reachable yet;
        # 422 = URLs do not belong to the host
        print(f"IndexNow: HTTP {error.code} {error.reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
