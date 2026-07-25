"""Fetch each character's official TEKKEN 8 profile card from tekken.com.

The fighter pages carry four authored fields -- epithet, country, fighting
style, birthday -- rendered as `innertext="..."` spans behind their labels.
Only the first three are kept; a birthday tells a movelist reader nothing.

Writes tools/source/official_profiles.json, which season2_config.py reads.
Re-run to refresh; the file is a snapshot so builds stay offline and stable.

    python tools/fetch_official_profiles.py [--character KEY]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SNAPSHOT = TOOLS / "source" / "official_profiles.json"
BASE = "https://tekken.com/fighters/"
USER_AGENT = "Mozilla/5.0 (compatible; tekken8movelist/1.0; +https://tekken8movelist.github.io/)"

# character key -> tekken.com slug
SLUGS = {
    "jin": "jin-kazama",
    "kazuya": "kazuya-mishima",
    "jun": "jun-kazama",
    "paul": "paul-phoenix",
    "law": "marshall-law",
    "king": "king",
    "lars": "lars-alexandersson",
    "jack8": "jack-8",
    "xiaoyu": "ling-xiaoyu",
    "nina": "nina-williams",
    "leroy": "leroy-smith",
    "asuka": "asuka-kazama",
    "lili": "lili",
    "bryan": "bryan-fury",
    "hwoarang": "hwoarang",
    "claudio": "claudio-serafino",
    "azucena": "azucena-milagros-ortiz-castillo",
    "raven": "raven",
    "leo": "leo",
    "steve": "steve-fox",
    "kuma": "kuma",
    "panda": "panda",
    "yoshimitsu": "yoshimitsu",
    "shaheen": "shaheen",
    "dragunov": "sergei-dragunov",
    "feng": "feng-wei",
    "lee": "lee-chaolan",
    "alisa": "alisa-bosconovitch",
    "zafina": "zafina",
    "devil_jin": "devil-jin",
    "victor": "victor-chevalier",
    "reina": "reina",
    "eddy": "eddy-gordo",
    "lidia": "lidia",
    "heihachi": "heihachi-mishima",
    "clive": "clive-rosfield",
    "anna": "anna-williams",
    "fahkumram": "fahkumram",
    "armor_king": "armor-king",
    "miary_zo": "miary-zo",
    "kunimitsu": "kunimitsu",
}

# The label sits as bare text inside its span, immediately before the value
# span. Anchoring on the '>' that opens it is what keeps `style:` from matching
# the thousands of `font-style:` declarations in the inlined CSS. Casing is
# inconsistent across pages -- some say `style:`, others `Style:`.
FIELD = re.compile(
    r">\s*(country|style|birthday)\s*:\s*(?:<!---->\s*)*<span[^>]*innertext=\"([^\"]*)\"",
    re.IGNORECASE,
)
# the epithet ("Anger of the Beast") is the h4 heading above the field list
EPITHET = re.compile(
    r"class=\"text--h4 text--uppercase\"[^>]*>\s*(?:<!---->\s*)*<span[^>]*innertext=\"([^\"]*)\"",
)


def fetch(slug: str) -> str:
    request = urllib.request.Request(
        BASE + slug, headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read().decode("utf-8", "replace")


def parse(page: str) -> dict:
    text = page.replace("&q;", '"')
    fields = {
        label.lower(): unescape(value).strip()
        for label, value in FIELD.findall(text)
    }
    epithet = EPITHET.search(text)
    return {
        "epithet": unescape(epithet.group(1)).strip() if epithet else "",
        # a handful of pages simply omit country; that is the site's own gap
        "country": fields.get("country", ""),
        "style": fields.get("style", ""),
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", choices=sorted(SLUGS))
    args = parser.parse_args(argv)

    profiles = {}
    if SNAPSHOT.exists():
        profiles = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    targets = [args.character] if args.character else list(SLUGS)
    incomplete = []
    for key in targets:
        slug = SLUGS[key]
        try:
            parsed = parse(fetch(slug))
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"FAIL   {key:<12} {slug}: {error}")
            incomplete.append(key)
            continue
        if not parsed["country"] or not parsed["style"]:
            print(f"THIN   {key:<12} {slug}: {parsed}")
            incomplete.append(key)
        else:
            print(f"ok     {key:<12} {parsed['country']} · {parsed['style']}")
        profiles[key] = parsed
        time.sleep(0.4)

    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(
        json.dumps(profiles, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"\nwrote {SNAPSHOT.relative_to(TOOLS.parent)} ({len(profiles)} characters)")
    if incomplete:
        print(f"needs attention: {', '.join(incomplete)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
