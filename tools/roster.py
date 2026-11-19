# -*- coding: utf-8 -*-
"""The footer roster: every character page links to every other one.

Until 2026-11 a character page's only internal inbound link was the hub, and
Search Console held eight of them at "crawled - currently not indexed". Each
page now ends with one wrapping line naming every published fighter.

Shared by both page families -- build_season2.py renders it into the 38
generator pages, patch_legacy_pages.py into the five pipeline pages (whose
Traditional and English builds then convert / swap it) -- so the list, the
order and the markup come from one place. Styling lives in back_nav.css
for the same reason.
"""

from __future__ import annotations

import re
import sys
from functools import lru_cache
from html import escape
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SITE = TOOLS.parent / "docs"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from zh_hant import convert  # noqa: E402

HUB_CARD = re.compile(
    r'<a class="card"[^>]*\bhref="(?P<href>[a-z0-9]+_tk8_movelist\.html)"[^>]*>'
    r'.*?<span class="cnm"><b>(?P<zh>[^<]+)</b><i>(?P<en>[^<]+)</i></span>',
    re.S,
)
ROSTER_BLOCK = re.compile(r'<nav class="roster".*?</nav>', re.S)


@lru_cache(maxsize=1)
def site_roster() -> tuple[tuple[str, str, str], ...]:
    """Every published fighter as (filename, Chinese name, English name).

    Read from the hub, which is hand-maintained and already the one place
    that says who is on the site and in what order. Placeholder cards are
    `<div>`s, not links, so an unreleased fighter never shows up here.
    """
    hub = (SITE / "index.html").read_text(encoding="utf-8")
    roster = tuple(
        (m.group("href"), m.group("zh"), m.group("en")) for m in HUB_CARD.finditer(hub)
    )
    if not roster:
        raise ValueError("no fighter cards found in docs/index.html")
    return roster


def render_roster(current: str, locale: str, label: str) -> str:
    """One <nav>: same-directory links, since every tree holds every page."""
    items = []
    for href, chinese, english in site_roster():
        name = english if locale == "en" else (
            convert(chinese) if locale == "hant" else chinese
        )
        if href == current:
            items.append(f'<span aria-current="page">{escape(name)}</span>')
        else:
            items.append(f'<a href="{href}">{escape(name)}</a>')
    label = escape(label)
    return (
        f'<nav class="roster" aria-label="{label}"><b>{label}</b> '
        + " · ".join(items)
        + "</nav>"
    )
