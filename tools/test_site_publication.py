"""Publication contract for the static GitHub Pages site."""

from __future__ import annotations

import json
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from accent_contrast import AA_NORMAL_TEXT, WHITE, contrast_ratio  # noqa: E402
from locales import DEFAULT_LOCALE, LOCALES, public_url  # noqa: E402
from season2_config import CHARACTERS as GENERATOR_CHARACTERS  # noqa: E402
from zh_hant import simplified_only_codepoints  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
INDEX = SITE / "index.html"
SITEMAP = SITE / "sitemap.xml"
ROBOTS = SITE / "robots.txt"
PUBLIC_ROOT = "https://tekken8movelist.github.io/"
CLOUDFLARE_BEACON_SOURCE = "https://static.cloudflareinsights.com/beacon.min.js"
EXPECTED_CLOUDFLARE_WEB_ANALYTICS_TOKEN = "2b712855303a44c2ab09217bf6703fe1"

EXPECTED_CHARACTER_PAGES = 43
# the hub and the 404 page (tools/build_404.py)
EXPECTED_HTML_FILES = EXPECTED_CHARACTER_PAGES + 2
EXPECTED_AVATARS = 44

LEGACY_PIPELINE_PAGES = (
    "xiaoyu_tk8_movelist.html",
    "jun_tk8_movelist.html",
    "kunimitsu_tk8_movelist.html",
    "clive_tk8_movelist.html",
    "law_tk8_movelist.html",
)


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append((name, value))


class ElementIdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        for name, value in attrs:
            if name == "id" and value:
                self.ids.append(value)


class CloudflareBeaconParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.beacons: list[dict[str, str | None]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag != "script":
            return
        attributes = dict(attrs)
        if attributes.get("src") == CLOUDFLARE_BEACON_SOURCE:
            self.beacons.append(attributes)


def parse_references(path: Path) -> list[tuple[str, str]]:
    parser = ReferenceParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.references


def resolve_local_reference(source: Path, value: str) -> Path | None:
    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https", "mailto", "data"} or parsed.netloc:
        return None
    if parsed.scheme:
        raise AssertionError(f"Unsupported URL scheme in {source}: {value}")
    if not parsed.path:
        return None
    if parsed.path.startswith(("/", "\\")):
        raise AssertionError(f"Site-root absolute reference in {source}: {value}")

    target = (source.parent / unquote(parsed.path)).resolve()
    try:
        target.relative_to(SITE.resolve())
    except ValueError as error:
        raise AssertionError(f"Reference escapes docs/ in {source}: {value}") from error
    return target


def published_pages() -> list[Path]:
    """Every HTML file the site actually serves, in all three locale trees."""
    pages = list(SITE.glob("*.html"))
    for meta in LOCALES.values():
        if meta["dir"]:
            pages.extend((SITE / meta["dir"]).glob("*.html"))
    return sorted(pages)


CHINESE = re.compile(r"[一-鿿]")
_CODE_BLOCK = re.compile(r"<(script|style)\b[^>]*>(.*?)</\1>", re.S | re.I)
# a source comment is not page copy: the shared notation stylesheet documents
# its per-character accents in Simplified (`/* 阿丽莎 · 樱粉 */`) and the legend
# stylesheet quotes the Chinese key it is describing
_SOURCE_COMMENT = re.compile(r"/\*.*?\*/|^[ \t]*//.*$", re.S | re.M)
_STRING_LITERAL = re.compile(r"'([^'\n]*)'|\"([^\"\n]*)\"")
_COPY_ATTRIBUTE = re.compile(
    r'\b(?:content|alt|title|placeholder|aria-label)="([^"]*)"'
)
# The one thing a page may say in a language that is not its own: a control
# that labels its choices in the reader's language cannot be used to leave, so
# `简` is the only way an English page can offer Simplified to someone who
# reads Simplified. That is the entire exemption -- two glyphs of link text.
#
# It used to be written as three regexes that deleted the whole switcher
# element before scanning. An exemption shaped like a region is wider than a
# rule about two glyphs, and the difference shipped: `aria-label="Language /
# 语言"` sat on the opening tag of `.lcseg`, inside the deleted span, on all 42
# English pages. Same failure as the "bilingual by design" slots this test was
# written to replace -- the shape of the hole is what copy hides in, not its
# size.
_LANGUAGE_SELF_NAMES = frozenset({"简", "繁"})


def reader_text(markup: str) -> list[str]:
    """Every string a reader, a crawler or a screen reader can end up seeing.

    Not just the rendered body: `<meta>` and `<title>` reach link previews and
    search results, `alt`/`aria-label` reach assistive tech, and a string
    literal inside an inline script reaches the screen the moment the script
    runs. All three shipped untranslated because the first sweep looked only
    between the tags.
    """
    found: list[str] = []
    for block in _CODE_BLOCK.finditer(markup):
        for literal in _STRING_LITERAL.finditer(
            _SOURCE_COMMENT.sub(" ", block.group(2))
        ):
            found.append(literal.group(1) or literal.group(2) or "")
    body = _CODE_BLOCK.sub(" ", markup)
    found.extend(match.group(1) for match in _COPY_ATTRIBUTE.finditer(body))
    found.extend(re.sub(r"<[^>]+>", "\n", body).split("\n"))
    return [text.strip() for text in found if text.strip()]


def generator_pages() -> set[str]:
    """Filenames build_season2.py owns.

    Only a build-provenance split now, not a contract one. The five one-shot
    pipeline pages (jun, xiaoyu, kunimitsu, clive, law) are still published
    from hand-converted HTML rather than a structured snapshot, so their two
    other locales come from their own producers -- `build_legacy_hant.py` and
    `build_legacy_en.py` -- instead of from the generator. They reached all
    three trees anyway, with the same hreflang block as everyone else, so the
    locale contract below covers all 41 pages and both callers below take this
    set unioned with `LEGACY_PIPELINE_PAGES`.

    Migrating them into the generator is still an open project of its own --
    see design/plans/2026-07-26-pipeline-page-migration.md -- but nothing in
    this file waits on it any more.
    """
    return {config["filename"] for config in GENERATOR_CHARACTERS.values()}


class SitePublicationContractTest(unittest.TestCase):
    def test_publication_root_is_isolated(self) -> None:
        self.assertTrue(INDEX.is_file())
        self.assertTrue((SITE / ".nojekyll").is_file())
        self.assertEqual(list(ROOT.glob("*.html")), [])
        site_directories = {path.name for path in SITE.iterdir() if path.is_dir()}
        self.assertIn("avatars", site_directories)
        # the locale trees are the only directories the build may add, and they
        # come from the locale table rather than a hand-kept list, so adding a
        # fourth language does not need this assertion edited
        locale_directories = {
            meta["dir"] for meta in LOCALES.values() if meta["dir"]
        }
        self.assertLessEqual(
            site_directories, {"avatars", "assets"} | locale_directories
        )

    def test_every_locale_tree_holds_every_page(self) -> None:
        """No locale is short of a page any more.

        The five pipeline pages have no structured snapshot, so neither
        locale can come from `build_season2.py`. Traditional converts the
        published Simplified page (`build_legacy_hant.py`); English rebuilds
        it, taking move names from the Wavu scrape in `wavu_*_names.txt` and
        the rest of the copy from `legacy_en.py` (`build_legacy_en.py`).
        """
        owned = generator_pages() | set(LEGACY_PIPELINE_PAGES)
        expected = {"hant": owned, "en": owned}
        for code, meta in LOCALES.items():
            if not meta["dir"]:
                continue
            with self.subTest(locale=code):
                tree = SITE / meta["dir"]
                self.assertTrue(tree.is_dir(), f"{meta['dir']} not built")
                self.assertEqual(
                    {path.name for path in tree.glob("*_tk8_movelist.html")},
                    expected[code],
                )

    def test_locale_trees_declare_their_language_and_cross_link(self) -> None:
        # the hubs too: the Simplified one carried no hreflang at all until
        # 2026-11-19, because this test only looked at character pages
        owned = generator_pages() | set(LEGACY_PIPELINE_PAGES) | {"index.html"}
        for code, meta in LOCALES.items():
            tree = SITE / meta["dir"] if meta["dir"] else SITE
            for page in sorted(p for p in tree.glob("*.html")
                               if p.name in owned):
                with self.subTest(locale=code, page=page.name):
                    markup = page.read_text(encoding="utf-8")
                    self.assertIn(f'<html lang="{meta["lang"]}"', markup)
                    self.assertIn(
                        f'<link rel="canonical" href='
                        f'"{public_url(code, page.name)}">',
                        markup,
                    )
                    for other in LOCALES.values():
                        self.assertIn(
                            f'hreflang="{other["hreflang"]}"', markup
                        )
                    self.assertIn(
                        '<link rel="alternate" hreflang="x-default" '
                        f'href="{public_url(DEFAULT_LOCALE, page.name)}">',
                        markup,
                    )

    def test_the_traditional_tree_carries_no_simplified_only_glyph(self) -> None:
        """Nothing else would catch a string that skipped the converter.

        Same reach as the English check, and for the same reason: the hub's
        og:description and its search script's `' 名匹配'` both skipped the
        converter and neither was between a pair of tags.
        """
        alphabet = simplified_only_codepoints()
        tree = SITE / LOCALES["hant"]["dir"]
        for page in sorted(tree.glob("*.html")):
            stray = set("".join(
                fragment
                for fragment in reader_text(page.read_text(encoding="utf-8"))
                if fragment not in _LANGUAGE_SELF_NAMES
            ))
            stray &= alphabet
            with self.subTest(page=page.name):
                self.assertEqual(stray, set(), f"{page.name}: {sorted(stray)}")

    def test_the_english_tree_carries_no_chinese_at_all(self) -> None:
        """One exception, and it is the language switcher naming itself.

        The first version of this test allowed four "bilingual by design"
        slots and passed while the pages still showed `Throws 投技`, 风间仁
        under every h1, and a Chinese sentence in the footer. Allowing a slot
        is how copy hides. The only Chinese an English page may now contain is
        简 and 繁 as the switcher's own link text, because a language control
        that labels its choices in the reader's language cannot be used to
        leave -- and the exemption is those two glyphs, not the element they
        sit in. Deleting the element instead is what let `Language / 语言` ride
        along in its `aria-label`, which a screen reader reads out.

        `reader_text` deliberately reaches past the rendered body into script
        string literals and the head -- `n + ' 名匹配'` and the og:description
        are both copy, and both shipped in Chinese because the earlier sweep
        only looked at what was between the tags.
        """
        tree = SITE / LOCALES["en"]["dir"]
        for page in sorted(tree.glob("*.html")):
            stray = sorted({
                fragment for fragment in reader_text(page.read_text(encoding="utf-8"))
                if CHINESE.search(fragment) and fragment not in _LANGUAGE_SELF_NAMES
            })
            with self.subTest(page=page.name):
                self.assertEqual(stray, [], f"{page.name}: {stray[:3]}")

    def test_expected_page_and_avatar_inventory(self) -> None:
        html_files = sorted(SITE.glob("*.html"))
        character_pages = sorted(SITE.glob("*_tk8_movelist.html"))
        avatars = sorted((SITE / "avatars").glob("*.png"))
        self.assertEqual(len(html_files), EXPECTED_HTML_FILES)
        self.assertEqual(len(character_pages), EXPECTED_CHARACTER_PAGES)
        self.assertEqual(len(avatars), EXPECTED_AVATARS)

    def test_homepage_links_every_character_page(self) -> None:
        references = parse_references(INDEX)
        linked_pages = {
            value
            for name, value in references
            if name == "href" and value.endswith("_tk8_movelist.html")
        }
        checked_in_pages = {
            path.name for path in SITE.glob("*_tk8_movelist.html")
        }
        self.assertEqual(linked_pages, checked_in_pages)

        linked_avatars = {
            value
            for name, value in references
            if name == "src" and value.startswith("avatars/")
        }
        # cards load the WebP copy (tools/build_avatars_webp.py); the PNG
        # stays for og:image / twitter:image
        checked_in_avatars = {
            f"avatars/{path.name}" for path in (SITE / "avatars").glob("*.webp")
        }
        self.assertEqual(linked_avatars, checked_in_avatars)
        self.assertEqual(
            {p.stem for p in (SITE / "avatars").glob("*.webp")},
            {p.stem for p in (SITE / "avatars").glob("*.png")},
        )
        # homepage is dark-only (2026-07-22): the light-avatar swap must stay gone
        self.assertNotIn("avatars-light/", INDEX.read_text(encoding="utf-8"))

    def test_all_local_references_resolve_inside_docs(self) -> None:
        # every tree, not just the root: the derived hubs inherit the authored
        # page's relative links, so a page that exists only in Simplified has
        # to be re-pointed at ../ or the /en/ card is a 404
        failures: list[str] = []
        for page in sorted(published_pages()):
            for _, value in parse_references(page):
                try:
                    target = resolve_local_reference(page, value)
                except AssertionError as error:
                    failures.append(str(error))
                    continue
                if target is not None and not target.exists():
                    failures.append(f"Missing reference from {page.name}: {value}")
        self.assertEqual(failures, [])

    def test_html_files_are_parseable(self) -> None:
        for page in published_pages():
            with self.subTest(page=str(page.relative_to(SITE))):
                parse_references(page)

    def test_cloudflare_web_analytics_covers_every_published_page(self) -> None:
        tokens: set[str] = set()
        for page in sorted(SITE.glob("*.html")):
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                parser = CloudflareBeaconParser()
                parser.feed(html)
                parser.close()

                self.assertEqual(len(parser.beacons), 1)
                attributes = parser.beacons[0]
                self.assertEqual(attributes.get("type"), "module")
                beacon_data = attributes.get("data-cf-beacon")
                self.assertIsNotNone(beacon_data)
                config = json.loads(beacon_data)
                token = config.get("token")
                self.assertIsInstance(token, str)
                self.assertRegex(token, r"^[0-9a-f]{32}$")
                self.assertEqual(token, EXPECTED_CLOUDFLARE_WEB_ANALYTICS_TOKEN)
                self.assertLess(
                    html.index(CLOUDFLARE_BEACON_SOURCE), html.rindex("</body>")
                )
                tokens.add(token)

        self.assertEqual(len(tokens), 1)

    def test_search_discovery_files_cover_every_published_page(self) -> None:
        self.assertTrue(SITEMAP.is_file())
        self.assertTrue(ROBOTS.is_file())

        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        root = ElementTree.parse(SITEMAP).getroot()
        self.assertEqual(root.tag, "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")
        sitemap_urls = {
            location.text
            for location in root.findall("sm:url/sm:loc", namespace)
            if location.text
        }
        # every page in every tree it was actually built in -- the five pipeline
        # pages exist only in Simplified, and listing three URLs for them would
        # point a crawler at files that are not there
        expected_urls = set()
        for code, meta in LOCALES.items():
            tree = SITE / meta["dir"] if meta["dir"] else SITE
            expected_urls.add(public_url(code, "index.html"))
            expected_urls.update(
                public_url(code, page.name)
                for page in tree.glob("*_tk8_movelist.html")
            )
        self.assertEqual(sitemap_urls, expected_urls)

        # every URL dates its last content change (tools/build_sitemap.py
        # derives it from a content hash, so it never claims a change that
        # did not happen), and the manifest agrees with the pages on disk
        for url in root.findall("sm:url", namespace):
            lastmod = url.findtext("sm:lastmod", namespaces=namespace)
            with self.subTest(lastmod_for=url.findtext("sm:loc", namespaces=namespace)):
                self.assertRegex(lastmod or "", r"^\d{4}-\d{2}-\d{2}$")
        import build_sitemap  # noqa: E402  (local: only this test needs it)
        _, changed = build_sitemap.refresh_lastmod(build_sitemap.load_lastmod(), "9999-12-31")
        self.assertEqual(changed, 0, "a page changed without its sitemap lastmod moving")

        # and each URL declares the alternates that exist for it
        xhtml = {"xhtml": "http://www.w3.org/1999/xhtml"}
        for url in root.findall("sm:url", namespace):
            location = url.findtext("sm:loc", namespaces=namespace)
            alternates = url.findall("xhtml:link", xhtml)
            with self.subTest(url=location):
                self.assertTrue(alternates, "no alternates declared")
                self.assertIn(
                    "x-default",
                    {link.get("hreflang") for link in alternates},
                )
                for link in alternates:
                    self.assertIn(link.get("href"), expected_urls)

        robots = ROBOTS.read_text(encoding="utf-8")
        self.assertIn("User-agent: *", robots)
        self.assertIn("Allow: /", robots)
        self.assertIn(f"Sitemap: {PUBLIC_ROOT}sitemap.xml", robots)

    def test_phone_layout_media_query_covers_every_page(self) -> None:
        for name in LEGACY_PIPELINE_PAGES:
            with self.subTest(page=name):
                html = (SITE / name).read_text(encoding="utf-8")
                self.assertIn('<style id="mobile-phone">', html)
                self.assertIn("@media (max-width: 640px)", html)

        generated_pages = [
            path
            for path in SITE.glob("*_tk8_movelist.html")
            if path.name not in LEGACY_PIPELINE_PAGES
        ]
        self.assertEqual(
            len(generated_pages),
            EXPECTED_CHARACTER_PAGES - len(LEGACY_PIPELINE_PAGES),
        )
        for page in generated_pages:
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                self.assertIn("@media (max-width: 640px)", html)
                self.assertNotIn("width: 600px", html)

    def test_every_character_page_can_reach_the_hub(self) -> None:
        pages = sorted(SITE.glob("*_tk8_movelist.html"))
        self.assertEqual(len(pages), EXPECTED_CHARACTER_PAGES)
        for page in pages:
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                # the breadcrumb and the reveal bar, both pointing at the hub
                self.assertEqual(html.count('href="index.html" data-home'), 2)
                self.assertEqual(html.count('<div class="hdrtop">'), 1)
                self.assertEqual(html.count('<nav class="revealbar"'), 1)
                # the anchor the reveal bar observes to know it cleared the banner
                self.assertEqual(html.count('<header id="top">'), 1)
                # the breadcrumb must survive with scripting off
                self.assertIn(
                    '<a class="home" href="index.html" data-home '
                    'aria-label="返回全角色选择">',
                    html,
                )
                # a bar hidden by transform alone would still take focus
                self.assertIn("visibility: hidden;", html)

    def test_character_pages_show_portrait_and_official_profile(self) -> None:
        pages = sorted(SITE.glob("*_tk8_movelist.html"))
        self.assertEqual(len(pages), EXPECTED_CHARACTER_PAGES)
        for page in pages:
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                slug = page.name.removesuffix("_tk8_movelist.html")
                # the portrait is set into the header band, and the file it
                # points at has to exist inside the publication root
                self.assertEqual(html.count('<div class="hero">'), 1)
                self.assertIn(f'<img src="avatars/{slug}.webp"', html)
                self.assertTrue((SITE / "avatars" / f"{slug}.png").is_file())
                # country and fighting style, taken from the official site
                self.assertEqual(html.count('<dl class="hdrbio">'), 1)
                self.assertIn("<dt>国家</dt>", html)
                self.assertIn("<dt>拳法</dt>", html)
                # ... and nothing left in English inside that row
                bio = re.search(r'<dl class="hdrbio">(.*?)</dl>', html, re.DOTALL)
                self.assertIsNotNone(bio)
                values = re.findall(r"<dd>(.*?)</dd>", bio.group(1))
                self.assertTrue(values)
                for value in values:
                    self.assertNotRegex(
                        value,
                        r"[A-Za-z]{4,}",
                        f"untranslated profile text in {page.name}: {value}",
                    )

    def test_character_pages_split_the_legend_by_notation(self) -> None:
        # the legend explains the notation in force, so the half describing the
        # other one is noise. The legacy pages shipped a single always-visible
        # key for months because nothing asserted this.
        pages = sorted(SITE.glob("*_tk8_movelist.html"))
        self.assertEqual(len(pages), EXPECTED_CHARACTER_PAGES)
        for page in pages:
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                self.assertEqual(html.count('<div class="lgtop">'), 1)
                self.assertEqual(html.count('<div class="lgsub txt-only">'), 1)
                self.assertEqual(html.count('<div class="lgsub gfx-only">'), 1)
                # the spelled-out key belongs to text notation only
                self.assertNotIn("<b>指令说明</b>", html)
                for rule in (
                    ".legend .lgsub.txt-only {",
                    "body.txt-mode .legend .lgsub.txt-only {",
                    "body.txt-mode .legend .lgsub.gfx-only {",
                ):
                    self.assertIn(rule, html)
                # the divider needs a colour in both families
                self.assertIn("--lg-line", html)

    def test_white_text_surfaces_clear_wcag_aa_on_every_page(self) -> None:
        # The 41 accents were picked to read as accents on a dark page, so they
        # are pale: white on the raw accent ran from 3.2:1 down to Panda's
        # 1.2:1. Both the section headings and the title band paint white text
        # on the character colour, and both now use --accent-band instead.
        pages = sorted(SITE.glob("*_tk8_movelist.html"))
        self.assertEqual(len(pages), EXPECTED_CHARACTER_PAGES)
        for page in pages:
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                bands = set(re.findall(r"--accent-band:\s*(#[0-9a-fA-F]{6})", html))
                self.assertEqual(
                    len(bands), 1, f"{page.name}: expected one --accent-band, got {bands}"
                )
                band = bands.pop()
                ratio = contrast_ratio(WHITE, band)
                self.assertGreaterEqual(
                    ratio,
                    AA_NORMAL_TEXT,
                    f"{page.name}: white on {band} is {ratio:.2f}:1",
                )
                # ... and that the surfaces actually reference it
                self.assertRegex(html, r"h2\s*\{[^}]*background:\s*var\(--accent-band\)")
                self.assertRegex(html, r"--hc-accent:\s*var\(--accent-band\)")
                # Dimming the label would spend the whole contrast margin. The
                # legacy pages still carry their original `.75` rule, so what
                # matters is the last one to be declared, not the absence of it.
                opacities = re.findall(
                    r"h2 \.en\s*\{[^}]*?opacity:\s*([0-9.]+)", html, re.DOTALL
                )
                self.assertTrue(opacities, f"{page.name}: no h2 .en opacity rule")
                self.assertEqual(
                    opacities[-1],
                    "1",
                    f"{page.name}: heading label ends up at opacity {opacities[-1]}",
                )

    def test_every_page_declares_a_reciprocal_hreflang_cluster(self) -> None:
        """Each page names itself as canonical, and every alternate answers back.

        The Simplified hub shipped with no alternates at all for months while
        the other two hubs pointed at it -- the cross-link test looked only at
        character pages. This one walks every page that carries a cluster.
        """
        clusters: dict[str, dict[str, str]] = {}
        for page in published_pages():
            if page.name == "404.html":
                continue
            relative = page.relative_to(SITE).as_posix()
            markup = page.read_text(encoding="utf-8")
            own = PUBLIC_ROOT + (relative[: -len("index.html")] if relative.endswith("index.html") else relative)
            with self.subTest(page=relative):
                self.assertEqual(
                    re.findall(r'<link rel="canonical" href="([^"]*)">', markup), [own]
                )
                cluster = dict(re.findall(
                    r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', markup
                ))
                self.assertIn("x-default", cluster)
                self.assertIn(own, cluster.values(), "the cluster leaves this page out")
                clusters[own] = cluster
        for own, cluster in clusters.items():
            for language, target in cluster.items():
                with self.subTest(page=own, alternate=language):
                    self.assertIn(target, clusters, "alternate is not a published page")
                    self.assertEqual(clusters[target], cluster, "alternate answers differently")

    def test_no_placeholder_or_double_escaped_text_reaches_a_reader(self) -> None:
        """`undefined`, `NaN`, a replacement glyph or `&amp;amp;` on screen.

        Body text and copy attributes only: inline scripts legitimately say
        `typeof x === 'undefined'`, and that never reaches a reader.
        """
        import html as html_module

        suspects = ("undefined", "NaN", "[object", "�", "&amp;", "&lt;", "&gt;",
                    "​", "‌", "‍", "﻿")
        for page in published_pages():
            with self.subTest(page=page.relative_to(SITE).as_posix()):
                body = _CODE_BLOCK.sub(" ", page.read_text(encoding="utf-8"))
                texts = [m.group(1) for m in _COPY_ATTRIBUTE.finditer(body)]
                texts += re.sub(r"<[^>]+>", "\n", body).split("\n")
                # one unescape is what the browser does; anything entity-like
                # left after it was escaped twice
                shown = "\n".join(html_module.unescape(text) for text in texts)
                for suspect in suspects:
                    self.assertNotIn(suspect, shown)

    def test_titles_are_unique_across_the_site(self) -> None:
        seen: dict[str, str] = {}
        for page in published_pages():
            title = re.search(r"<title>(.*?)</title>", page.read_text(encoding="utf-8"), re.S)
            relative = page.relative_to(SITE).as_posix()
            with self.subTest(page=relative):
                self.assertIsNotNone(title)
                self.assertNotIn(title.group(1), seen, f"same title as {seen.get(title.group(1))}")
                seen[title.group(1)] = relative

    def test_share_images_exist(self) -> None:
        for page in published_pages():
            markup = page.read_text(encoding="utf-8")
            for url in re.findall(
                r'<meta (?:property="og:image"|name="twitter:image") content="([^"]+)">', markup
            ):
                with self.subTest(page=page.relative_to(SITE).as_posix(), image=url):
                    self.assertTrue(url.startswith(PUBLIC_ROOT))
                    self.assertTrue((SITE / url[len(PUBLIC_ROOT):]).is_file())

    def test_character_pages_have_unique_element_ids(self) -> None:
        # the browser gate only covers the 36 generator pages, so duplicate ids
        # injected into the 5 legacy ones would otherwise go unnoticed -- and
        # the hubs and both locale trees are published too
        for page in published_pages():
            with self.subTest(page=page.relative_to(SITE).as_posix()):
                parser = ElementIdParser()
                parser.feed(page.read_text(encoding="utf-8"))
                duplicates = sorted(
                    {value for value in parser.ids if parser.ids.count(value) > 1}
                )
                self.assertEqual(duplicates, [])

    def test_homepage_phone_layout_rules(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        marker = "@media (max-width:640px)"
        self.assertIn(marker, html)
        phone_block = html.split(marker, 1)[1]
        self.assertIn("aspect-ratio:4/5", phone_block)
        self.assertIn("body{zoom:1}", phone_block)

    def test_public_disclaimer_is_present(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        required_phrases = (
            "Wavu Wiki",
            "角色头像为非官方同人艺术演绎",
            "不作商业用途",
            "Bandai Namco Entertainment Inc.",
            "无隶属关系",
            "相关权利归 Bandai Namco Entertainment Inc. 及其他相应权利人所有",
        )
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, html)
        self.assertNotIn("生成式 AI", html)

    def test_hub_font_subset_covers_every_rendered_character(self) -> None:
        """Noto Sans SC is requested with text=<the hub's own characters>.

        A glyph missing from the subset would quietly render in the fallback
        face, so each hub's request must cover everything that hub shows
        (tools/hub_fonts.py), and both font links must load without blocking.
        """
        import html as html_module
        from urllib.parse import unquote

        from hub_fonts import rendered_characters

        for code, meta in LOCALES.items():
            tree = SITE / meta["dir"] if meta["dir"] else SITE
            with self.subTest(locale=code):
                markup = (tree / "index.html").read_text(encoding="utf-8")
                noto = re.findall(r'href="(https://fonts\.googleapis\.com/css2\?family=Noto[^"]*)"', markup)
                self.assertTrue(noto)
                subset = unquote(html_module.unescape(noto[0]).split("text=", 1)[1])
                missing = set(rendered_characters(markup)) - set(subset)
                self.assertEqual(missing, set())
                # the <noscript> twins are meant to be plain links
                scripted = re.sub(r"<noscript>.*?</noscript>", "", markup, flags=re.S)
                links = re.findall(r'<link rel="stylesheet" href="https://fonts[^>]*>', scripted)
                self.assertEqual(len(links), 2)
                for link in links:
                    self.assertIn('media="print"', link)

    def test_every_character_page_links_every_other_fighter(self) -> None:
        """The footer roster: each page reachable from every other one.

        Before 2026-11 a character page's only internal inbound link was the
        hub, and Search Console held eight of them at "crawled - currently
        not indexed".
        """
        for code, meta in LOCALES.items():
            tree = SITE / meta["dir"] if meta["dir"] else SITE
            pages = {p.name for p in tree.glob("*_tk8_movelist.html")}
            self.assertEqual(len(pages), EXPECTED_CHARACTER_PAGES)
            for name in sorted(pages):
                with self.subTest(locale=code, page=name):
                    html = (tree / name).read_text(encoding="utf-8")
                    roster = re.search(r'<nav class="roster".*?</nav>', html, re.S)
                    self.assertIsNotNone(roster)
                    linked = set(re.findall(r'href="([a-z0-9]+_tk8_movelist\.html)"', roster.group(0)))
                    self.assertEqual(linked, pages - {name})
                    self.assertIn('aria-current="page"', roster.group(0))

    def test_meta_descriptions_are_long_enough_and_distinct(self) -> None:
        """Bing Webmaster flagged 12 pages as "too short" in 2026-11.

        Every flagged one was under 100 characters (the hubs at 88, 金/熊/雷欧
        at 94-95); Bing asks for 150-160. Chinese reads far more per character
        than English, so the floor is Bing's threshold rather than its target,
        and the ceiling is where search results truncate. Within one tree no
        two pages may share a description -- the old template differed only by
        the name.
        """
        for code, meta in LOCALES.items():
            tree = SITE / meta["dir"] if meta["dir"] else SITE
            seen: dict[str, str] = {}
            for page in sorted(tree.glob("*.html")):
                with self.subTest(locale=code, page=page.name):
                    html = page.read_text(encoding="utf-8")
                    match = re.search(r'<meta name="description" content="([^"]*)"', html)
                    self.assertIsNotNone(match)
                    description = match.group(1).replace("&amp;", "&")
                    self.assertGreaterEqual(len(description), 100, description)
                    self.assertLessEqual(len(description), 160, description)
                    self.assertNotIn(description, seen, seen.get(description))
                    seen[description] = page.name

    def test_character_pages_have_seo_contract(self) -> None:
        for page in sorted(SITE.glob("*_tk8_movelist.html")):
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                self.assertEqual(html.count("<h1"), 1)
                self.assertRegex(
                    html,
                    r"<title>铁拳8 .+（.+）出招表 \| TEKKEN 8 .+ Move List</title>",
                )
                self.assertIn('<meta name="description" content="', html)
                self.assertIn(
                    f'<link rel="canonical" href="{PUBLIC_ROOT}{page.name}">',
                    html,
                )
                self.assertIn(
                    f'<meta property="og:url" content="{PUBLIC_ROOT}{page.name}">',
                    html,
                )
                title = re.search(r"<title>(.*?)</title>", html).group(1)
                self.assertIn(
                    f'<meta property="og:title" content="{title}">', html
                )
                slug = page.name.removesuffix("_tk8_movelist.html")
                self.assertIn(
                    '<meta property="og:image" content='
                    f'"{PUBLIC_ROOT}avatars/{slug}.png">',
                    html,
                )
                self.assertIn('<script type="application/ld+json">', html)
                self.assertIn('"@type":"WebPage"', html)
                self.assertIn('"@type":"BreadcrumbList"', html)
                self.assertEqual(html.count('class="page-intro"'), 1)


if __name__ == "__main__":
    unittest.main()
