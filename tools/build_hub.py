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
from locales import LOCALES, PUBLIC_ROOT, alternate_links, public_url  # noqa: E402
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
    markup = replace_once(
        markup,
        r'(?<=<b class="lmark" aria-hidden="true">文/A</b>)语言(?=</span>)',
        s["languageLabel"],
        "language label",
    )
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
    return markup


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

    Traditional converts the Chinese name. English promotes the name it already
    carries and demotes the Chinese one -- the same "other locale in the
    secondary slot" rule the character pages use, so the plate still says two
    things instead of printing one name twice.
    """

    def plate(match: re.Match[str]) -> str:
        chinese, english = match.group("zh"), match.group("en")
        if locale == "hant":
            return f'<span class="cnm"><b>{convert(chinese)}</b><i>{english}</i></span>'
        return f'<span class="cnm"><b>{english}</b><i>{chinese}</i></span>'

    return re.sub(
        r'<span class="cnm"><b>(?P<zh>[^<]*)</b><i>(?P<en>[^<]*)</i></span>',
        plate,
        markup,
    )


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
    # the alternates block goes in once, right after canonical
    return replace_once(
        markup,
        r'(?<=<link rel="canonical" href="' + re.escape(public_url(locale, "index.html")) + r'">)',
        "\n" + alternate_links("index.html"),
        "alternates",
    )


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
    markup = swap_paths(markup, locale)
    # the language control has to point back out of this tree
    return replace_once(
        markup,
        r'<div class="grp"><span class="lbl"><b class="lmark".*?</span></div>',
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
