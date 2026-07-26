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
from locales import LOCALES, public_url  # noqa: E402
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

EXPECTED_CHARACTER_PAGES = 41
EXPECTED_HTML_FILES = EXPECTED_CHARACTER_PAGES + 1
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


def generator_pages() -> set[str]:
    """Filenames build_season2.py owns.

    The five one-shot pipeline pages (jun, xiaoyu, kunimitsu, clive, law) are
    still published from hand-converted HTML, so they have no locale siblings
    and no hreflang block. Migrating them into the generator is a prerequisite
    project of its own -- see
    design/plans/2026-07-26-pipeline-page-migration.md -- and until it lands,
    the locale contract below applies to the pages the generator produces.
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

    def test_every_locale_tree_holds_a_full_set_of_character_pages(self) -> None:
        expected = generator_pages()
        for code, meta in LOCALES.items():
            if not meta["dir"]:
                continue
            with self.subTest(locale=code):
                tree = SITE / meta["dir"]
                self.assertTrue(tree.is_dir(), f"{meta['dir']} not built")
                self.assertEqual(
                    {path.name for path in tree.glob("*_tk8_movelist.html")},
                    expected,
                )

    def test_locale_trees_declare_their_language_and_cross_link(self) -> None:
        owned = generator_pages()
        for code, meta in LOCALES.items():
            tree = SITE / meta["dir"] if meta["dir"] else SITE
            for page in sorted(p for p in tree.glob("*_tk8_movelist.html")
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
                        f'href="{PUBLIC_ROOT}{page.name}">',
                        markup,
                    )

    def test_the_traditional_tree_carries_no_simplified_only_glyph(self) -> None:
        """Nothing else would catch a string that skipped the converter.

        Scoped to what a reader actually sees. `<style>` and `<script>` are cut
        first, not just their tags: the shared notation component documents its
        per-character accents in Simplified comments
        (`/* 阿丽莎 · 樱粉 */`), and those are one CSS file used verbatim by all
        three locales, not page copy that failed to convert.
        """
        alphabet = simplified_only_codepoints()
        tree = SITE / LOCALES["hant"]["dir"]
        code_blocks = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
        # the locale control names each language in its own script -- 简 on the
        # Traditional page is the Simplified locale's own label, the same way an
        # English page offers "Deutsch" rather than "German"
        locale_control = re.compile(r'<div class="lcgl".*?</div>', re.S)
        for page in sorted(tree.glob("*_tk8_movelist.html")):
            markup = locale_control.sub(" ", page.read_text(encoding="utf-8"))
            visible = re.sub(r"<[^>]+>", " ", code_blocks.sub(" ", markup))
            stray = set(visible) & alphabet
            with self.subTest(page=page.name):
                self.assertEqual(stray, set(), f"{page.name}: {sorted(stray)}")

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
        checked_in_avatars = {
            f"avatars/{path.name}" for path in (SITE / "avatars").glob("*.png")
        }
        self.assertEqual(linked_avatars, checked_in_avatars)
        # homepage is dark-only (2026-07-22): the light-avatar swap must stay gone
        self.assertNotIn("avatars-light/", INDEX.read_text(encoding="utf-8"))

    def test_all_local_references_resolve_inside_docs(self) -> None:
        failures: list[str] = []
        for page in sorted(SITE.glob("*.html")):
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
        for page in sorted(SITE.glob("*.html")):
            with self.subTest(page=page.name):
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
        expected_urls = {PUBLIC_ROOT}
        expected_urls.update(
            f"{PUBLIC_ROOT}{page.name}"
            for page in SITE.glob("*_tk8_movelist.html")
        )
        self.assertEqual(sitemap_urls, expected_urls)

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
                self.assertIn(f'<img src="avatars/{slug}.png"', html)
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

    def test_character_pages_have_unique_element_ids(self) -> None:
        # the browser gate only covers the 36 generator pages, so duplicate ids
        # injected into the 5 legacy ones would otherwise go unnoticed
        for page in sorted(SITE.glob("*_tk8_movelist.html")):
            with self.subTest(page=page.name):
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

    def test_character_pages_have_seo_contract(self) -> None:
        for page in sorted(SITE.glob("*_tk8_movelist.html")):
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                self.assertEqual(html.count("<h1"), 1)
                self.assertRegex(
                    html,
                    r"<title>铁拳8 .+（.+）出招表 \| TEKKEN 8 .+ Movelist</title>",
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
