"""Bring the five legacy pipeline pages up to the current page design.

jun / xiaoyu / clive / kunimitsu / law came out of the one-shot `pipeline.py`
and are never regenerated (see CLAUDE.md), so everything the generator emits
from a template has to be patched into their published HTML instead. This
script owns two of those things:

* back navigation -- the breadcrumb and the reveal bar (`back_nav.css` / `.js`)
* the header card  -- portrait, restructured title, official profile row
                      (`header_card.css`)

Both stylesheets are the single source of truth for all 41 pages; this script
only injects them and rewrites the markup around them. Anything visual belongs
in those files, never inlined here, or the two families drift apart.

Idempotent: re-running refreshes the injected blocks and re-derives the header
from its own output instead of stacking another copy.

    python tools/patch_legacy_pages.py [--check]
"""

from __future__ import annotations

import argparse
import re
import sys
from html import escape
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from official_profile_zh import localized_profile  # noqa: E402

ROOT = TOOLS.parent
SITE = ROOT / "docs"

# page key -> published filename. The key also indexes official_profiles.json.
LEGACY_PAGES = {
    "jun": "jun_tk8_movelist.html",
    "xiaoyu": "xiaoyu_tk8_movelist.html",
    "clive": "clive_tk8_movelist.html",
    "kunimitsu": "kunimitsu_tk8_movelist.html",
    "law": "law_tk8_movelist.html",
}

# these pages call the accent `--jade` / `--jade-dark`, and `--acc` in dark mode
ACCENT_BINDING = """
.revealbar { --bn-accent: var(--jade-dark); }
html.dark .revealbar { --bn-accent: var(--acc); }
header { --hc-accent: var(--jade); --hc-ink: var(--jade-dark); }
"""

STYLE_BLOCK = re.compile(
    r"\n?<style id=\"(?:back-nav|back-nav-style|legacy-chrome)\">.*?</style>", re.DOTALL
)
SCRIPT_BLOCK = re.compile(
    r"\n?<script id=\"(?:back-nav|back-nav-script)\">.*?</script>", re.DOTALL
)
HEADER_BLOCK = re.compile(r"<header(?: id=\"top\")?>\n(.*?)\n</header>", re.DOTALL)
# The banner is the only header carrying an <h1>. Both patterns must match the
# pristine markup AND this script's own output, or a second run explodes.
TITLE = re.compile(
    r"<h1>(.*?)<small>(.*?)</small>(?:<span class=\"hsub\">.*?</span>)?</h1>",
    re.DOTALL,
)
TOGGLE = re.compile(r"<div class=\"ntgl\"[^>]*>.*?</span></div>", re.DOTALL)
PAGE_INTRO = re.compile(r"\s*<p class=\"page-intro\">.*?</p>", re.DOTALL)
FOOTER = re.compile(r"(<footer[^>]*>)")


def build_header(key: str, block: str, slug: str) -> tuple[str, str]:
    """Return (new header inner HTML, the page-intro lifted out of it)."""
    title = TITLE.search(block)
    if not title:
        raise ValueError(f"{key}: no <h1> in the banner header")
    display = title.group(1).strip()
    # legacy small text is "CANONICAL · 铁拳 8 出招表"; keep the canonical only
    canonical = title.group(2).split("·")[0].strip()

    toggles = TOGGLE.findall(block)
    if len(toggles) != 2:
        raise ValueError(f"{key}: expected 2 .ntgl toggles, found {len(toggles)}")

    intro = PAGE_INTRO.search(block)
    intro_html = intro.group(0).strip() if intro else ""

    profile = localized_profile(key)
    rows = "".join(
        f"<div><dt>{label}</dt><dd>{escape(value)}</dd></div>"
        for label, value in (("国家", profile["country_zh"]), ("拳法", profile["style_zh"]))
        if value
    )
    bio = f'<dl class="hdrbio">{rows}</dl>' if rows else ""

    header = (
        f'<div class="hero"><img src="avatars/{slug}.png" '
        f'alt="{escape(display, quote=True)} · 飞白轮廓角色像" decoding="async"></div>\n'
        '  <div class="hdrmain">\n'
        '    <div class="hdrtop">\n'
        '      <a class="home" href="index.html" data-home aria-label="返回全角色选择">'
        '<span aria-hidden="true">←</span>全角色出招表</a>\n'
        '      <div class="hdrctl">\n'
        f"        {toggles[0]}\n"
        f"        {toggles[1]}\n"
        "      </div>\n"
        "    </div>\n"
        f'    <h1>{display}<small>{canonical}</small>'
        '<span class="hsub">铁拳 8 出招表</span></h1>\n'
        f"    {bio}\n"
        "  </div>"
    )
    return header, intro_html


def reveal_bar(display: str, canonical: str) -> str:
    return (
        '<nav class="revealbar" aria-label="快速导航">'
        '<a href="index.html" data-home aria-label="返回全角色选择">'
        '<span aria-hidden="true">←</span> 全角色</a>'
        f"<b>{display}<small>{canonical}</small></b></nav>\n"
    )


def patch(key: str, text: str, css: str, script: str) -> str:
    slug = LEGACY_PAGES[key].removesuffix("_tk8_movelist.html")

    match = HEADER_BLOCK.search(text)
    if not match or "<h1>" not in match.group(1):
        raise ValueError(f"{key}: banner header not found")
    header_inner, intro_html = build_header(key, match.group(1), slug)
    title = TITLE.search(match.group(1))
    display, canonical = title.group(1).strip(), title.group(2).split("·")[0].strip()

    text = (
        text[: match.start()]
        + f'<header id="top">\n{header_inner}\n</header>'
        + text[match.end() :]
    )

    # the reveal bar sits before the header, matching the tab order it has once
    # revealed
    if 'class="revealbar"' not in text:
        opening = "<body>\n"
        index = text.index(opening) + len(opening)
        text = text[:index] + reveal_bar(display, canonical) + text[index:]

    # the intro paragraph now belongs to the footer, as on the generator pages
    if intro_html and 'class="page-intro"' not in text:
        text = FOOTER.sub(lambda m: m.group(1) + intro_html, text, count=1)

    text = STYLE_BLOCK.sub("", text)
    text = SCRIPT_BLOCK.sub("", text)
    text = text.replace(
        "</head>",
        f'<style id="legacy-chrome">{css}{ACCENT_BINDING}</style>\n</head>',
        1,
    )
    text = text.replace(
        "</body>", f'<script id="back-nav-script">{script}</script>\n</body>', 1
    )
    return text


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when a page is out of date",
    )
    args = parser.parse_args(argv)

    css = "".join(
        (TOOLS / name).read_text(encoding="utf-8")
        for name in ("header_card.css", "back_nav.css")
    )
    script = (TOOLS / "back_nav.js").read_text(encoding="utf-8")

    stale: list[str] = []
    for key, name in LEGACY_PAGES.items():
        path = SITE / name
        current = path.read_text(encoding="utf-8")
        patched = patch(key, current, css, script)
        if patched == current:
            print(f"unchanged {name}")
            continue
        stale.append(name)
        if args.check:
            continue
        path.write_text(patched, encoding="utf-8")
        print(f"patched   {name}")

    if args.check and stale:
        print(f"out of date: {', '.join(stale)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
