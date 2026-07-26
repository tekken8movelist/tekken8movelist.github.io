# -*- coding: utf-8 -*-
"""One-way edits to the authored Simplified hub, made idempotent.

`docs/index.html` is hand-maintained, so this does not rewrite it -- it adds
the two things every locale build needs and that nobody should have to keep in
sync by hand:

  1. the language control, beside the notation one
  2. Traditional spellings in each card's `data-q`, so 風間仁 finds Jin on all
     three hubs (the search index is shared verbatim across locales)

Safe to re-run: both edits detect their own output and no-op.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from hub_i18n import HUB, locale_control  # noqa: E402
from zh_hant import convert  # noqa: E402

CARD = re.compile(
    r'(<a class="card"[^>]*?data-q=")(?P<q>[^"]*)("[^>]*>)(?P<body>.*?)</a>',
    re.S,
)
CARD_NAME = re.compile(r'<span class="cnm"><b>(?P<zh>[^<]*)</b>')
NOTATION_GROUP = re.compile(
    r'(<div class="grp">\s*<span class="lbl">记法</span>.*?</div>)', re.S
)


def add_traditional_search_terms(markup: str) -> tuple[str, int]:
    added = 0

    def rewrite(match: re.Match[str]) -> str:
        nonlocal added
        body = match.group("body")
        name = CARD_NAME.search(body)
        if not name:
            return match.group(0)
        traditional = convert(name.group("zh"))
        terms = match.group("q")
        if traditional == name.group("zh") or traditional in terms.split():
            return match.group(0)
        added += 1
        return (
            match.group(1)
            + f"{terms} {traditional}"
            + match.group(3)
            + body
            + "</a>"
        )

    return CARD.sub(rewrite, markup), added


def add_language_control(markup: str) -> tuple[str, bool]:
    if 'class="seg lseg"' in markup:
        return markup, False
    match = NOTATION_GROUP.search(markup)
    if not match:
        raise SystemExit("notation control group not found in the hub")
    # after 记法, per the design: a third labelled stack, not a new shape
    return (
        markup[: match.end()]
        + "\n      "
        + locale_control("hans")
        + markup[match.end() :],
        True,
    )


def main() -> int:
    markup = HUB.read_text(encoding="utf-8")
    markup, added = add_traditional_search_terms(markup)
    markup, control = add_language_control(markup)
    HUB.write_text(markup, encoding="utf-8", newline="\n")
    print(f"data-q: {added} card(s) gained a Traditional spelling")
    print(f"language control: {'added' if control else 'already present'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
