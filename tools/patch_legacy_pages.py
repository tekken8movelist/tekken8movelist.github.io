"""Bring the five legacy pipeline pages up to the current page design.

jun / xiaoyu / clive / kunimitsu / law came out of the one-shot `pipeline.py`
and are never regenerated (see CLAUDE.md), so everything the generator emits
from a template has to be patched into their published HTML instead. This
script owns two of those things:

* back navigation -- the breadcrumb and the reveal bar (`back_nav.css` / `.js`)
* the header card  -- portrait, restructured title, official profile row
                      (`header_card.css`)
* the legend       -- split into a notation-independent row plus one half per
                      notation (`legend_card.css`)

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

from accent_contrast import band_color  # noqa: E402
from locales import (  # noqa: E402
    DEFAULT_LOCALE,
    LOCALES,
    PUBLIC_ROOT,
    alternate_links,
    page_href,
    strings,
)
from official_profile_zh import localized_profile  # noqa: E402
from pipeline import CONFIG as PIPELINE_CONFIG  # noqa: E402

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

def accent_binding(key: str) -> str:
    """Bind the shared chrome's colour hooks to what these pages call things.

    They name the accent `--jade` / `--jade-dark`, with `--acc` (the pale
    variant) only in dark mode. `--line` is a fixed light green -- dark mode
    overrides `.legend`'s border-color rather than the variable -- so the legend
    divider is bound per theme.

    `--accent-band` is the surface white text sits on: `--jade` is a mid tone
    (Law's #b88900 gives white 3.2:1), so it is recomputed here from the same
    accent/ink pair the pipeline used, exactly as the generator does.
    """
    config = PIPELINE_CONFIG[key]
    band = band_color(config["acc"], config["acc_ink"])
    return f"""
.revealbar {{ --bn-accent: var(--jade-dark); }}
html.dark .revealbar {{ --bn-accent: var(--acc); }}
body {{ --accent-band: {band}; }}
header {{ --hc-accent: var(--accent-band); --hc-ink: var(--jade-dark); }}
h2 {{ background: var(--accent-band); }}
h2 .en {{ opacity: 1; }}
/* these pages hard-code the active toggle's colour to `--jade`, which on Law
   is a mid gold (#b88900, 3.2:1 on the white pill) */
.ntgl button.on {{ color: var(--jade-dark); }}
.legend {{ --lg-line: var(--line); }}
html.dark .legend {{ --lg-line: #2a323d; }}
"""

# The per-character tail of each page's original hand-written legend, kept
# verbatim: it explains this character's stances and any notation only they use,
# and it was written against the page rather than derived, so nothing here can
# be regenerated. Jun is the exception -- that page never explained its three
# stances, so the codes come from `pipeline.CONFIG["jun"]["prefix"]`, the same
# map that turned those Chinese prefixes into Wavu notation.
LEGEND_EXTRA = {
    "jun": "<span><b>架势</b>　幻月中=GEN　出云中=IZU　御生中=MIA</span>",
    "xiaoyu": "<span><b>架势</b>　凤凰=凤凰架势(AOP)　背身=雨舞背身(BT)　催眠=催眠师(HYP)</span>",
    "clive": (
        "<span><b>专用记号</b>　qcf=下前1/4圈　~F=按住前</span>"
        "<span><b>架势</b>　光翼=光之翼　凤凰=不死鸟瞬移　气流=上升气流</span>"
    ),
    "kunimitsu": "<span><b>专用记号</b>　qcf=下前1/4圈(d,d/f,f)　~F=按住前</span>",
    "law": "<span><b>架势</b>　龙构=龙构架势(DSS)　背身=背身状态(BT)</span>",
}

LEGEND_JUDGEMENT = (
    '<b>判定</b><span><span class="hi">上</span>=上段　<span class="md">中</span>=中段　'
    '<span class="lo">下</span>=下段　<span class="sp">特</span>=特殊　'
    '<span class="sp">投</span>=投掷　<span class="sp">!</span>=不可防御</span>'
    "<b>发生</b><span>首击冲击帧（i=impact，越小越快，依 Wavu）</span>"
)
LEGEND_KEYS = (
    "<span><b>按键 · 方向</b>　1=左拳　2=右拳　3=左脚　4=右脚　|　"
    "f=前　b=后　u=上　d=下　d/f=前下　d/b=后下　u/f=前上　u/b=后上</span>"
    "<span><b>状态 · 分隔</b>　f,f=前冲　WS=起身中　FC=蹲伏中　SS=横移中　"
    "+=同时按　~=紧接　＊蓄力</span>"
)
LEGEND_GFX = (
    '<b>图形记法</b>　<span class="tk-in tk-sm"><span class="tk-b">'
    "<i>1</i><i>2</i><i>3</i><i>4</i></span></span> 四键方阵（左上1 右上2 左下3 右下4，亮=按下）　"
    '<span class="tk-in tk-sm"><span class="tk-dir f"></span></span>=轻点方向　'
    '<span class="tk-in tk-sm"><span class="tk-dir f hold"></span></span>=按住　'
    '<span class="tk-in tk-sm"><span class="tk-n">N</span></span>=回中　'
    '<span class="tk-in tk-sm"><span class="tk-state">架势中</span></span>=状态前缀　|　'
    "<b>分隔</b>　› 接续　+ 方向＋键　~ 紧接　＊蓄力　→ 下一招　"
    '<span class="tk-tbang">T!</span> 回旋'
)

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
# Two shapes again: pristine is one always-visible legend followed by a separate
# `.legend.gfx-only` block; this script's own output is a single id'd block whose
# only line starting with `</div>` is its own closing tag.
LEGEND = re.compile(
    r"<div class=\"legend\" id=\"notation-legend\">\n.*?\n</div>"
    r"|<div class=\"legend\">\s*<b>指令说明</b>"
    r".*?<div class=\"legend gfx-only\">.*?\n</div>",
    re.DOTALL,
)


def built_locales(filename: str) -> set[str]:
    """Which locales this page has actually been produced in.

    Read from disk rather than declared, so the control follows the build:
    Traditional appeared the day `build_legacy_hant.py` started converting
    these pages, and English will appear the day the migration gives them a
    structured snapshot.
    """
    found = {DEFAULT_LOCALE}
    for code, meta in LOCALES.items():
        if meta["dir"] and (SITE / meta["dir"] / filename).is_file():
            found.add(code)
    return found


def locale_control(filename: str, current: str = DEFAULT_LOCALE) -> str:
    """The same language group the generator pages carry.

    A locale this page has not been built in is shown dimmed rather than
    dropped: the control is on the other 36 pages, and a switcher that
    silently vanishes on 5 of 41 reads as a bug, where a disabled choice reads
    as "not translated yet" -- which is what it is, until the migration in
    design/plans/2026-07-26-pipeline-page-migration.md lands.
    """
    s = strings(current)
    available = built_locales(filename)
    items = []
    for code, meta in LOCALES.items():
        label = escape(meta["short"])
        if code == current:
            items.append(f'<span aria-current="true">{label}</span>')
        elif code in available:
            href = escape(page_href(current, code, filename), quote=True)
            items.append(
                f'<a href="{href}" lang="{meta["lang"]}" '
                f'hreflang="{meta["hreflang"]}">{label}</a>'
            )
        else:
            title = escape(
                s["localeMissing"].format(language=meta["endonym"]), quote=True
            )
            items.append(f'<span class="off" title="{title}">{label}</span>')
    return (
        '<div class="lcgl">'
        f'<span class="lcl" aria-hidden="true">{escape(s["languageLabel"])}</span>'
        f'<span class="lcseg" role="group" '
        f'aria-label="{escape(s["localeAria"], quote=True)}">'
        + "".join(items)
        + "</span></div>"
    )


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
        f"      {locale_control(LEGACY_PAGES[key])}\n"
        "    </div>\n"
        '    <div class="hdrtop hdrtop2">\n'
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


def build_legend(key: str) -> str:
    """The judgement/startup row, plus one half per notation."""
    return (
        '<div class="legend" id="notation-legend">\n'
        f'  <div class="lgtop">{LEGEND_JUDGEMENT}</div>\n'
        f'  <div class="lgsub txt-only">{LEGEND_KEYS}{LEGEND_EXTRA[key]}</div>\n'
        f'  <div class="lgsub gfx-only">{LEGEND_GFX}</div>\n'
        "</div>"
    )


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

    # now that these pages have a Traditional twin, tell crawlers about it
    if 'rel="alternate"' not in text:
        canonical_link = (
            f'<link rel="canonical" href="{PUBLIC_ROOT}{LEGACY_PAGES[key]}">'
        )
        if canonical_link not in text:
            raise ValueError(f"{key}: canonical link not found")
        text = text.replace(
            canonical_link,
            canonical_link + "\n" + alternate_links(LEGACY_PAGES[key]),
            1,
        )

    legend = LEGEND.search(text)
    if not legend:
        raise ValueError(f"{key}: notation legend not found")
    text = text[: legend.start()] + build_legend(key) + text[legend.end() :]

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
        f'<style id="legacy-chrome">{css}{accent_binding(key)}</style>\n</head>',
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
        for name in (
            "table_text.css",
            "header_card.css",
            "legend_card.css",
            "back_nav.css",
        )
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
