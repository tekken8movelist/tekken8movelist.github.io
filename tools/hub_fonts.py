# -*- coding: utf-8 -*-
"""The hubs' web-font links: Noto Sans SC subset to the text each hub shows.

Google Fonts serves Noto Sans SC in per-weight unicode-range slices, and a
page full of Chinese pulls in dozens of them: the Simplified hub downloaded
21 font files / 1.1 MB plus a 451 KB stylesheet, which on PageSpeed's slow
mobile link pushed its Largest Contentful Paint to 11 s (the English hub,
same markup, 1.0 s). The hub's text is fixed, so the request can name it:
`text=` returns one small file per weight holding exactly those glyphs --
13 KB of CSS and ~0.3 MB of fonts for the same four weights. Nothing looks
different: every character the page renders is in the subset.

Body text is set in Noto Sans SC first, Latin included, so the subset is
*every* rendered character, not only the CJK ones -- leaving the Latin out
would quietly swap the English names into the fallback face. Text typed into
the search box later is not known in advance and falls back per glyph,
which is what the system fonts behind Noto are for.

Saira and JetBrains Mono (display Latin, small) keep their full request.
Both links load at low priority (media="print", switched on load) with a
<noscript> twin; fonts.googleapis.com is unreachable from mainland China, so
nothing may wait on it.

augment_hub.py applies this to the authored Simplified hub, build_hub.py to
each derived hub after its copy is swapped, so every tree subsets its own
text. The block is regenerated from the page each time, which makes both
idempotent.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import quote

LATIN_FAMILIES = (
    "https://fonts.googleapis.com/css2?"
    "family=Saira:ital,wght@0,500;0,600;0,700;0,800;1,700;1,800"
    "&family=JetBrains+Mono:wght@500;700&display=swap"
)
NOTO = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap&text="
FONT_BLOCK = re.compile(
    r'<link rel="(?:stylesheet|preload)"[^>]*href="https://fonts\.googleapis\.com/css2\?[^"]*"[^>]*>'
    r'(?:<noscript><link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*"></noscript>)?'
    r'(?:\s*<link rel="(?:stylesheet|preload)"[^>]*href="https://fonts\.googleapis\.com/css2\?[^"]*"[^>]*>'
    r'(?:<noscript><link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*"></noscript>)?)*'
)
STRING_LITERAL = re.compile(r"'([^'\\\n]*)'|\"([^\"\\\n]*)\"")


class _RenderedText(HTMLParser):
    """Text nodes, the search placeholder, and inline-script string literals."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._in = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._in = tag
        for name, value in attrs:
            if name == "placeholder" and value:
                self.parts.append(value)

    def handle_endtag(self, tag):
        if tag == self._in:
            self._in = None

    def handle_data(self, data):
        if self._in == "style":
            return
        if self._in == "script":
            # strings a script may write into the page (' 名匹配', '未找到')
            self.parts.extend(a or b for a, b in STRING_LITERAL.findall(data))
            return
        self.parts.append(data)


def rendered_characters(markup: str) -> str:
    body = markup[markup.find("<body"):]
    parser = _RenderedText()
    parser.feed(body)
    chars = {c for c in "".join(parser.parts) if c.isprintable() and not c.isspace()}
    # all printable ASCII too: the search count is written at run time
    # ("7 名匹配"), so a digit the static page never shows can still appear
    chars |= {chr(code) for code in range(0x21, 0x7F)}
    return "".join(sorted(chars))


def font_block(markup: str) -> str:
    noto = NOTO + quote(rendered_characters(markup), safe="")
    links = []
    for href in (noto, LATIN_FAMILIES):
        href = href.replace("&", "&amp;")
        links.append(
            f'<link rel="stylesheet" href="{href}" media="print" onload="this.media=\'all\'">'
            f'<noscript><link rel="stylesheet" href="{href}"></noscript>'
        )
    return "\n".join(links)


def apply_hub_fonts(markup: str) -> str:
    match = FONT_BLOCK.search(markup)
    if not match:
        raise SystemExit("hub: Google Fonts links not found")
    return markup[: match.start()] + font_block(markup) + markup[match.end():]
