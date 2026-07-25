"""Give the five legacy pipeline pages the same back navigation as the rest.

jun / xiaoyu / clive / kunimitsu / law came out of the one-shot `pipeline.py`
and are never regenerated (see CLAUDE.md), so the breadcrumb and reveal bar have
to be patched into the published HTML directly. The markup, CSS and JS are the
same ones the generator emits -- `back_nav.css` and `back_nav.js` are the single
source of truth for both page families; only the accent binding differs, because
these pages name their theme colours `--jade-dark` / `--acc` rather than
`--accent-ink` / `--accent`.

Idempotent: re-running refreshes the injected blocks from the shared assets
instead of stacking another copy.

    python tools/patch_legacy_back_nav.py [--check]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SITE = ROOT / "docs"

LEGACY_PAGES = (
    "jun_tk8_movelist.html",
    "xiaoyu_tk8_movelist.html",
    "clive_tk8_movelist.html",
    "kunimitsu_tk8_movelist.html",
    "law_tk8_movelist.html",
)

# these pages call the accent `--jade-dark` (light) and `--acc` (dark)
ACCENT_BINDING = """
.revealbar { --bn-accent: var(--jade-dark); }
html.dark .revealbar { --bn-accent: var(--acc); }
"""

BREADCRUMB = (
    '  <div class="homerow"><a class="home" href="index.html" data-home '
    'aria-label="返回全角色选择"><span aria-hidden="true">←</span>全角色出招表</a></div>\n'
)

# the banner header is the only <header> whose first heading is an <h1>; the
# tips section further down has its own bare <header> that must stay untouched.
# Matches both the pristine and the already-patched shape, so re-running is safe.
BANNER = re.compile(
    r"<header(?: id=\"top\")?>\n"
    r"(?:  <div class=\"homerow\">.*?</div>\n)?"
    r"  <h1>(.*?)<small>(.*?)</small></h1>"
)
STYLE_BLOCK = re.compile(r"\n?<style id=\"back-nav(?:-style)?\">.*?</style>", re.DOTALL)
SCRIPT_BLOCK = re.compile(r"\n?<script id=\"back-nav(?:-script)?\">.*?</script>", re.DOTALL)


def reveal_bar(display: str, canonical: str) -> str:
    return (
        '<nav class="revealbar" aria-label="快速导航">'
        '<a href="index.html" data-home aria-label="返回全角色选择">'
        '<span aria-hidden="true">←</span> 全角色</a>'
        f"<b>{display}<small>{canonical}</small></b></nav>\n"
    )


def patch(text: str, css: str, script: str) -> str:
    match = BANNER.search(text)
    if not match:
        raise ValueError("banner <header> followed by <h1> not found")
    display = match.group(1)
    canonical = match.group(2).split(" · ")[0]

    # 1. the anchor the reveal bar's IntersectionObserver needs
    text = (
        text[: match.start()]
        + match.group(0).replace("<header>", '<header id="top">', 1)
        + text[match.end() :]
    )

    # 2. breadcrumb as the header's first child
    if 'class="homerow"' not in text:
        opening = '<header id="top">\n'
        index = text.index(opening) + len(opening)
        text = text[:index] + BREADCRUMB + text[index:]

    # 3. reveal bar as the body's first child, so it precedes the breadcrumb in
    #    tab order exactly as it does visually once revealed
    if 'class="revealbar"' not in text:
        opening = "<body>\n"
        index = text.index(opening) + len(opening)
        text = text[:index] + reveal_bar(display, canonical) + text[index:]

    # 4/5. refresh the shared CSS and JS
    text = STYLE_BLOCK.sub("", text)
    text = SCRIPT_BLOCK.sub("", text)
    text = text.replace(
        "</head>", f'<style id="back-nav-style">{css}{ACCENT_BINDING}</style>\n</head>', 1
    )
    text = text.replace(
        "</body>", f'<script id="back-nav-script">{script}</script>\n</body>', 1
    )
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when a page is out of date",
    )
    args = parser.parse_args(argv)

    css = (TOOLS / "back_nav.css").read_text(encoding="utf-8")
    script = (TOOLS / "back_nav.js").read_text(encoding="utf-8")

    stale: list[str] = []
    for name in LEGACY_PAGES:
        path = SITE / name
        current = path.read_text(encoding="utf-8")
        patched = patch(current, css, script)
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
