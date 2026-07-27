# -*- coding: utf-8 -*-
"""Derive the Traditional and English hubs from the authored Simplified one.

`docs/index.html` carries the flux effect, the card grid, the whole design
system and 41 hand-placed cards. Templating it would mean owning all of that in
Python; instead the two other locales are derived from it here, swapping only
the copy and the paths. Run `augment_hub.py` first -- it puts the language
control and the Traditional search terms into the authored page.

Idempotent: re-running writes byte-identical output.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from hub_i18n import (  # noqa: E402
    COUNT_LINE,
    GROUP_HEADINGS,
    HUB,
    HUB_STRINGS,
    SITE,
    locale_control,
)
from locales import (  # noqa: E402
    DEFAULT_LOCALE,
    LOCALES,
    PUBLIC_ROOT,
    alternate_links,
    public_url,
)
from zh_hant import convert  # noqa: E402


def replace_once(markup: str, pattern: str, replacement: str, what: str) -> str:
    """Substitute exactly one occurrence, or fail loudly.

    A silent no-op here is the failure mode that matters: the derived hub would
    ship with a Simplified string in it and nothing would say so.
    """
    updated, count = re.subn(pattern, lambda _: replacement, markup, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"hub: {what} matched {count} times, expected 1")
    return updated


def swap_copy(markup: str, locale: str) -> str:
    s = {key: value[locale] for key, value in HUB_STRINGS.items()}
    markup = replace_once(markup, r"(?<=<h1>).*?(?=</h1>)", s["hubTitle"], "h1")
    markup = replace_once(
        markup, r'(?<=<p class="sub">).*?(?=</p>)', s["hubSub"], "sub"
    )
    markup = replace_once(
        markup, r'(?<=<span class="lbl">)记法(?=</span>)', s["notationLabel"], "记法"
    )
    markup = replace_once(
        markup, r'(?<=data-n="gfx">)按键图(?=</button>)', s["ntGfx"], "gfx button"
    )
    markup = replace_once(
        markup, r'(?<=data-n="txt">)文字(?=</button>)', s["ntTxt"], "txt button"
    )
    # the language label rides along with the whole control, replaced last
    markup = replace_once(
        markup,
        r'(?<=<input id="q" type="search" placeholder=")[^"]*(?=")',
        s["searchPlaceholder"],
        "search placeholder",
    )
    markup = replace_once(
        markup, r'(?<=<span class="cap">).*?(?=</span>)', s["demoCap"], "demo caption"
    )
    for key, chinese in (
        ("keyLP", "左拳 LP"),
        ("keyRP", "右拳 RP"),
        ("keyLK", "左脚 LK"),
        ("keyRK", "右脚 RK"),
    ):
        markup = replace_once(
            markup, rf"(?<=</span>){re.escape(chinese)}(?=</div>)", s[key], key
        )
    markup = replace_once(
        markup,
        r'(?<=<p class="footer-title">).*?(?=</p>)',
        s["footerTitle"],
        "footer title",
    )
    markup = replace_once(
        markup, r'(?<=<footer aria-label=")[^"]*(?=")', s["footerAria"], "footer aria"
    )
    # the disclaimer wraps two links; swap the text around them and leave the
    # anchors exactly as authored
    markup = replace_once(
        markup,
        r'(?<=<p class="footer-copy">).*?(?=<a href="https://wavu\.wiki/")',
        s["footerSource"],
        "source lead-in",
    )
    markup = replace_once(
        markup,
        r'(?<=>Wavu Wiki</a>).*?(?=</p>)',
        s["footerSourceTail"],
        "source tail",
    )
    markup = replace_once(
        markup,
        r'(?<=<p class="footer-copy">).*?(?=<a href="https://www\.bandainamcoent\.com)',
        s["footerFan"],
        "fan lead-in",
    )
    markup = replace_once(
        markup,
        r'(?<=Bandai Namco Entertainment Inc\.</a>).*?(?=</p>)',
        s["footerFanTail"],
        "fan tail",
    )
    markup = replace_once(
        markup,
        r'(?<=<b id="noneQ">).*?(?=</b>)',
        s["noneTitle"],
        "empty-state title",
    )
    markup = replace_once(
        markup,
        r'(?<=</b>\n  <span>).*?(?=</span>\n</div>)',
        s["noneHint"],
        "empty-state hint",
    )
    # the search script builds three strings at runtime; they are copy too
    markup = replace_once(
        markup,
        r"(?<=noneQ\.textContent = ')[^']*(?=' \+ q\.value\.trim\(\))",
        s["noneQueryOpen"],
        "empty-state query prefix",
    )
    markup = replace_once(
        markup,
        r"(?<=q\.value\.trim\(\) \+ ')[^']*(?=';)",
        s["noneQueryClose"],
        "empty-state query suffix",
    )
    markup = replace_once(
        markup,
        r"(?<=cnt\.textContent = raw \? n \+ ')[^']*(?=')",
        s["matchCount"],
        "match count",
    )
    return replace_once(
        markup,
        r'(?<=<span class="mono">TEKKEN™ 8</span>).*?(?=</p>)',
        s["footerLegal"],
        "legal line",
    )


def swap_counts(markup: str, locale: str) -> str:
    """The count line and every group heading."""
    numbers = re.search(
        r'<span class="cnt" id="cnt">(\d+)[^<]*?(\d+)[^<]*</span>', markup
    )
    if not numbers:
        raise SystemExit("hub: count line not found")
    markup = replace_once(
        markup,
        r'(?<=<span class="cnt" id="cnt">).*?(?=</span>)',
        COUNT_LINE[locale].format(
            pages=numbers.group(1), fighters=numbers.group(2)
        ),
        "count line",
    )

    # the script restores the same line when the search box is cleared
    markup = replace_once(
        markup,
        r"(?<=: ')(\d+)[^']*?(\d+)[^']*(?=';)",
        COUNT_LINE[locale].format(
            pages=numbers.group(1), fighters=numbers.group(2)
        ),
        "count line reset",
    )

    def heading(match: re.Match[str]) -> str:
        kicker, title, count = match.group("k"), match.group("t"), match.group("c")
        spec = GROUP_HEADINGS.get(kicker)
        if spec is None:
            raise SystemExit(f"hub: unregistered group heading {kicker!r}")
        new_kicker, new_title, count_template = spec[locale]
        number = re.search(r"\d+", count)
        if not number:
            raise SystemExit(f"hub: no count in {count!r}")
        return (
            f'<div class="ghead"><span class="gk">{new_kicker}</span>'
            f'<span class="gt">{new_title}</span><span class="sp"></span>'
            f'<span class="gc">{count_template.format(n=number.group(0))}</span></div>'
        )

    return re.sub(
        r'<div class="ghead"><span class="gk">(?P<k>[^<]*)</span>'
        r'<span class="gt">(?P<t>[^<]*)</span><span class="sp"></span>'
        r'<span class="gc">(?P<c>[^<]*)</span></div>',
        heading,
        markup,
    )


def swap_card_names(markup: str, locale: str) -> str:
    """The name plate on each card. `data-q` is never touched.

    Traditional converts the Chinese name and keeps the English one beneath
    it, which is what the player sees in-game. English shows the English name
    alone: the Chinese line is one an English reader cannot use, and search
    still finds the card either way because `data-q` carries every spelling.
    """

    def plate(match: re.Match[str]) -> str:
        chinese, english = match.group("zh"), match.group("en")
        if locale == "hant":
            return f'<span class="cnm"><b>{convert(chinese)}</b><i>{english}</i></span>'
        return f'<span class="cnm"><b>{english}</b></span>'

    return re.sub(
        r'<span class="cnm"><b>(?P<zh>[^<]*)</b><i>(?P<en>[^<]*)</i></span>',
        plate,
        markup,
    )


SOON_LABEL = re.compile(r'(<span class="(?:p|soonpill)">)即将上线(</span>)')


def swap_soon_labels(markup: str, locale: str) -> str:
    """"Coming soon" on the three unreleased S3 cards.

    Twice per card -- once over the portrait, once on the plate -- so this is
    the one copy slot that legitimately matches more than once.
    """
    label = HUB_STRINGS["soonLabel"][locale]
    markup, count = SOON_LABEL.subn(rf"\g<1>{label}\g<2>", markup)
    if count != 6:
        raise SystemExit(f"hub: soon label matched {count} times, expected 6")
    return markup


def swap_head(markup: str, locale: str) -> str:
    meta = LOCALES[locale]
    markup = replace_once(
        markup, r'(?<=<html lang=")[^"]*(?=")', meta["lang"], "html lang"
    )
    markup = replace_once(
        markup, r"(?<=<title>).*?(?=</title>)", HUB_STRINGS["pageTitle"][locale],
        "title",
    )
    markup = replace_once(
        markup,
        r'(?<=<link rel="canonical" href=")[^"]*(?=")',
        public_url(locale, "index.html"),
        "canonical",
    )
    markup = replace_once(
        markup,
        r'(?<=<meta property="og:locale" content=")[^"]*(?=")',
        meta["og"],
        "og:locale",
    )
    markup = replace_once(
        markup,
        r'(?<=<meta property="og:url" content=")[^"]*(?=")',
        public_url(locale, "index.html"),
        "og:url",
    )
    # everything else in the head that carries copy rather than a URL
    s = {key: value[locale] for key, value in HUB_STRINGS.items()}
    for pattern, value, what in (
        (r'(?<=<meta name="description" content=")[^"]*(?=")',
         s["metaDescription"], "meta description"),
        (r'(?<=<meta property="og:site_name" content=")[^"]*(?=")',
         s["siteName"], "og:site_name"),
        (r'(?<=<meta property="og:title" content=")[^"]*(?=")',
         s["pageTitle"], "og:title"),
        (r'(?<=<meta property="og:description" content=")[^"]*(?=")',
         s["shareDescription"], "og:description"),
        (r'(?<=<meta property="og:image:alt" content=")[^"]*(?=")',
         s["imageAlt"], "og:image:alt"),
        (r'(?<=<meta name="twitter:title" content=")[^"]*(?=")',
         s["pageTitle"], "twitter:title"),
        (r'(?<=<meta name="twitter:description" content=")[^"]*(?=")',
         s["shareDescription"], "twitter:description"),
    ):
        markup = replace_once(markup, pattern, value, what)
    # the structured-data block is rewritten whole rather than field by field:
    # a lookbehind cannot span the fields in front of the one being replaced
    structured = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": s["siteName"],
            "alternateName": "TEKKEN 8 Movelist",
            "url": public_url(locale, "index.html"),
            "inLanguage": meta["lang"],
            "description": s["shareDescription"],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    markup = replace_once(
        markup,
        r'(?<=<script type="application/ld\+json">).*?(?=</script>)',
        structured,
        "ld+json block",
    )
    # the alternates block goes in once, right after canonical
    return replace_once(
        markup,
        r'(?<=<link rel="canonical" href="' + re.escape(public_url(locale, "index.html")) + r'">)',
        "\n" + alternate_links("index.html"),
        "alternates",
    )


CARD_LINK = re.compile(r'href="(?P<name>[a-z0-9_]+_tk8_movelist\.html)"')


def retarget_missing_pages(markup: str, locale: str) -> str:
    """Cards for pages this locale does not have point back at Simplified.

    The five pipeline pages are Simplified-only until the migration in
    design/plans/2026-07-26-pipeline-page-migration.md lands. Card links are
    relative, so leaving them alone sends an /en/ visitor to
    /en/jun_tk8_movelist.html, which is a 404 -- the page is one directory up.

    `hreflang` is what says the destination is Simplified -- the card itself
    still reads the way its neighbours do, because the fighter's name is the
    same word whichever language the page under it happens to be in.
    """
    directory = LOCALES[locale]["dir"]
    if not directory:
        return markup
    home = LOCALES[DEFAULT_LOCALE]

    def link(match: re.Match[str]) -> str:
        name = match.group("name")
        if (SITE / directory / name).is_file():
            return match.group(0)
        return f'href="../{name}" hreflang="{home["hreflang"]}"'

    return CARD_LINK.sub(link, markup)


def swap_paths(markup: str, locale: str) -> str:
    """Assets live once at the publish root; character pages sit alongside."""
    depth = "../" if LOCALES[locale]["dir"] else ""
    markup = markup.replace('src="avatars/', f'src="{depth}avatars/')
    markup = markup.replace('href="avatars/', f'href="{depth}avatars/')
    markup = markup.replace('content="' + PUBLIC_ROOT + 'avatars/',
                            'content="' + PUBLIC_ROOT + 'avatars/')
    return markup


def derive(markup: str, locale: str) -> str:
    markup = swap_head(markup, locale)
    markup = swap_copy(markup, locale)
    markup = swap_counts(markup, locale)
    markup = swap_card_names(markup, locale)
    markup = swap_soon_labels(markup, locale)
    markup = swap_paths(markup, locale)
    markup = retarget_missing_pages(markup, locale)
    # the language control has to point back out of this tree
    return replace_once(
        markup,
        r'<div class="grp"><span class="lbl">语言</span>.*?</span></div>',
        locale_control(locale),
        "language control",
    )


def write_if_changed(path: Path, content: str) -> bool:
    try:
        if path.read_text(encoding="utf-8") == content:
            return False
    except (OSError, UnicodeError):
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if a derived hub is out of date")
    args = parser.parse_args(argv)

    source = HUB.read_text(encoding="utf-8")
    if 'class="seg lseg"' not in source:
        raise SystemExit("run tools/augment_hub.py first: no language control")

    status = 0
    for locale, meta in LOCALES.items():
        if not meta["dir"]:
            continue
        destination = SITE / meta["dir"] / "index.html"
        derived = derive(source, locale)
        if args.check:
            current = destination.read_text(encoding="utf-8") if destination.is_file() else ""
            state = "ok" if current == derived else "STALE"
            if state == "STALE":
                status = 1
            print(f"{state:6s} {destination.relative_to(SITE.parent)}")
        else:
            changed = write_if_changed(destination, derived)
            print(f"{'built' if changed else 'unchanged'} "
                  f"{destination.relative_to(SITE.parent)}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
