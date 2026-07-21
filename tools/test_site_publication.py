"""Publication contract for the static GitHub Pages site."""

from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
INDEX = SITE / "index.html"

EXPECTED_CHARACTER_PAGES = 41
EXPECTED_HTML_FILES = EXPECTED_CHARACTER_PAGES + 1
EXPECTED_AVATARS = 44


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

    def test_public_disclaimer_is_present(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        required_phrases = (
            "Wavu Wiki",
            "生成式 AI 制作的非官方轮廓风格演绎",
            "不作商业用途",
            "Bandai Namco Entertainment Inc.",
            "无隶属关系",
        )
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, html)


if __name__ == "__main__":
    unittest.main()
