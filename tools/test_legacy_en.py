# -*- coding: utf-8 -*-
"""Regression tests for the English pipeline pages.

`build_legacy_en.py` already fails loudly on any Chinese it has no English
for, and the gate runs it, so an untranslated string cannot ship. These cover
what that does not: that the pages on disk are the ones the builder produces,
that names really are coming from Wavu rather than quietly falling through to
a description, and that the two halves of the described-name treatment (the
italics and the line explaining them) never ship apart.
"""

from __future__ import annotations

import html
import re
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_legacy_en as builder  # noqa: E402
from legacy_en import CAPSULES, MOVE_DESCRIPTIONS, MOVE_NAMES, PHRASES  # noqa: E402
from patch_legacy_pages import LEGACY_PAGES  # noqa: E402

SITE = TOOLS.parent / "docs"
CHINESE = re.compile(r"[一-鿿]")
NAME_CELL = re.compile(r'<td class="name">(.*?)</td>', re.S)


class LegacyEnglishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.missing = builder.Missing()
        cls.built = {
            key: builder.build(key, filename, cls.missing)
            for key, filename in LEGACY_PAGES.items()
        }

    def test_every_string_on_the_five_pages_has_english(self) -> None:
        self.assertFalse(bool(self.missing), self.missing.report())

    def test_the_published_pages_match_the_builder(self) -> None:
        for key, filename in LEGACY_PAGES.items():
            with self.subTest(character=key):
                published = SITE / "en" / filename
                self.assertTrue(published.is_file(), f"en/{filename} not built")
                self.assertEqual(
                    published.read_text(encoding="utf-8"),
                    self.built[key],
                    f"en/{filename} is stale -- run tools/build_legacy_en.py",
                )

    def test_most_names_come_from_wavu_rather_than_from_here(self) -> None:
        """A collapse in the command join would show up as a flood of italics.

        The join is the load-bearing part: it is what makes these Wavu's
        English names and not this project's guesses. Roughly nine names in
        ten are Wavu's, so a threshold well under that still catches a break
        without pinning an exact count that a snapshot refresh would move.
        """
        for key, markup in self.built.items():
            with self.subTest(character=key):
                named = len(NAME_CELL.findall(markup))
                described = markup.count('class="refname"')
                self.assertGreater(named, 100)
                # 0.15 until 2026-11-19, when strings Wavu lists without a
                # name stopped borrowing their first hit's (law's 1,1 had read
                # "Jab"): law went to 28/185 honestly described. A collapse of
                # the join would still put this past one half.
                self.assertLess(
                    described / named, 0.20,
                    f"{key}: {described}/{named} names are the project's own",
                )

    def test_described_names_never_ship_without_their_disclosure(self) -> None:
        """They look like every other name, so the legend has to say so.

        Nothing marks these rows individually any more -- a `ref` chip and
        then italics both made a fifth of the table look broken. That puts the
        whole weight of the disclosure on the legend line and the tooltip, so
        neither may go missing.
        """
        for key, markup in self.built.items():
            with self.subTest(character=key):
                if 'class="refname"' in markup:
                    self.assertIn('class="lgref"', markup)
                    self.assertIn('<span class="refname" title="', markup)

    def test_hit_levels_are_separated(self) -> None:
        """`中投` reads as two words in Chinese; `MidThrow` does not."""
        for key, markup in self.built.items():
            with self.subTest(character=key):
                for cell in re.findall(
                    r'<td[^>]*>((?:<span class="(?:hi|md|lo|sp)"[^>]*>[^<]*</span>'
                    r'|<i class="lvsep"[^>]*>[^<]*</i>|<wbr>)+)</td>',
                    markup,
                ):
                    spans = re.findall(r"<span[^>]*>([^<]*)</span>", cell)
                    if len(spans) > 1:
                        self.assertIn("lvsep", cell, f"{spans} run together")

    def test_a_string_never_borrows_another_moves_name(self) -> None:
        """One English name standing for several Chinese moves is a wrong join.

        Until 2026-11-19, 46 names did: strings took their first hit's name
        (law's 1,2,2,2 read "Jab"), and variants behind a condition word took
        their base move's (Jun's Amaterasu read "Genjitsu"). What remains is
        Wavu's own sharing, listed with the reason.
        """
        allowed = {
            ("xiaoyu", "Hypnotist"),           # wavu: db+1+2 and HYP.1+2 alike
            ("xiaoyu", "Spinning Push Hands"),  # 鞋底拍击 is its punch-parry use
            ("xiaoyu", "X Marks the Spot"),    # wavu: f,F+1+2,1+2 and ws+1+2,1+2
            ("clive", "Fangs of Ruin"),        # wavu Left_throw = 1+3
            ("clive", "Punisher"),             # wavu Right_throw = 2+4
            ("clive", "Judgment Bolt"),        # wavu: CH.f,F+1+2 and Back_throw
            ("law", "Dragon's Rising Kick"),   # the page lists u/f+4 twice
        }
        row = re.compile(r"<tr>(?:(?!</tr>).)*?</tr>", re.S)
        badge = re.compile(r'<span class="tag[^"]*">[^<]*</span>')

        def rows(markup: str) -> list[tuple[str, bool]]:
            found = []
            for tr in row.findall(markup.partition('<section class="tipsPage">')[0]):
                name = re.search(r'<td class="name">(.*?)</td>', tr, re.S)
                if name and '<span class="cmd-txt">' in tr:
                    text = re.sub(r"<[^>]+>", "", badge.sub("", name.group(1))).strip()
                    found.append((html.unescape(text), "refname" in name.group(1)))
            return found

        for key, markup in self.built.items():
            with self.subTest(character=key):
                chinese = rows((SITE / LEGACY_PAGES[key]).read_text(encoding="utf-8"))
                english = rows(markup)
                self.assertEqual(len(chinese), len(english))
                sources: dict[str, set[str]] = {}
                for (zh, _), (en, described) in zip(chinese, english):
                    if not described:
                        sources.setdefault(en, set()).add(zh)
                shared = {en for en, zh in sources.items() if len(zh) > 1}
                self.assertEqual(
                    shared, {en for k, en in allowed if k == key},
                    f"{key}: one English name for several moves",
                )

    def test_name_badges_survive_the_rename(self) -> None:
        """Heat Engager / Rage Art / Stance badges reach the English page.

        The name cell is replaced wholesale with the Wavu name, and until
        2026-11-19 its badges went with it: 78 of 79 were missing.
        """
        badge = re.compile(r'<span class="(tag[^"]*)">')
        for key, markup in self.built.items():
            with self.subTest(character=key):
                source = (SITE / LEGACY_PAGES[key]).read_text(encoding="utf-8")
                self.assertEqual(badge.findall(markup), badge.findall(source))

    def test_no_table_is_left_holding_chinese(self) -> None:
        for key, markup in self.built.items():
            with self.subTest(character=key):
                for cell in NAME_CELL.findall(markup):
                    self.assertFalse(
                        CHINESE.search(cell), f"{key}: Chinese move name {cell}"
                    )

    def test_the_tables_carry_no_stale_keys(self) -> None:
        """A key nothing matches is a translation of something no longer said.

        Left alone they accumulate, and the next person cannot tell which
        entries are load-bearing. Capsules are exempt: they are keyed on state
        words shared across characters, so a few are legitimately unused.
        """
        pages = "".join(
            (SITE / filename).read_text(encoding="utf-8")
            for filename in LEGACY_PAGES.values()
        )
        for label, table in (("PHRASES", PHRASES),):
            unused = sorted(key for key in table if key not in pages)
            with self.subTest(table=label):
                self.assertEqual(unused, [], f"{label} keys match nothing")

    def test_move_tables_are_keyed_to_real_characters(self) -> None:
        for table in (MOVE_NAMES, MOVE_DESCRIPTIONS):
            for key, _chinese in table:
                self.assertIn(key, LEGACY_PAGES)

    def test_capsules_never_answer_with_chinese(self) -> None:
        for chinese, english in CAPSULES.items():
            with self.subTest(state=chinese):
                self.assertFalse(CHINESE.search(english))


if __name__ == "__main__":
    unittest.main()
