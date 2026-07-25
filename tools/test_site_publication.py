"""Publication contract for the static GitHub Pages site."""

from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree


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


class SitePublicationContractTest(unittest.TestCase):
    def test_publication_root_is_isolated(self) -> None:
        self.assertTrue(INDEX.is_file())
        self.assertTrue((SITE / ".nojekyll").is_file())
        self.assertEqual(list(ROOT.glob("*.html")), [])
        site_directories = {path.name for path in SITE.iterdir() if path.is_dir()}
        self.assertIn("avatars", site_directories)
        self.assertLessEqual(site_directories, {"avatars", "assets"})

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
