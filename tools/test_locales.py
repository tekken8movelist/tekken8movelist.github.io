# -*- coding: utf-8 -*-
"""Contract for the locale table and the three-column chrome vocabulary."""

import re
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from locales import (  # noqa: E402
    DEFAULT_LOCALE,
    LOCALES,
    PUBLIC_ROOT,
    alternate_links,
    asset_href,
    page_href,
    public_url,
    strings,
)
from zh_hant import simplified_only_codepoints  # noqa: E402

PAGE = "jin_tk8_movelist.html"


class LocaleTableTests(unittest.TestCase):
    def test_simplified_is_the_default_and_lives_at_the_publish_root(self) -> None:
        self.assertEqual(list(LOCALES)[0], "hans")
        self.assertEqual(DEFAULT_LOCALE, "hans")
        self.assertEqual(LOCALES["hans"]["dir"], "")
        self.assertEqual(LOCALES["hans"]["lang"], "zh-CN")
        self.assertEqual(LOCALES["hans"]["body_class"], "")

    def test_new_locales_are_additive_subdirectories(self) -> None:
        self.assertEqual(LOCALES["hant"]["dir"], "zh-Hant")
        self.assertEqual(LOCALES["en"]["dir"], "en")
        self.assertEqual(LOCALES["hant"]["lang"], "zh-Hant")
        self.assertEqual(LOCALES["en"]["lang"], "en")

    def test_every_locale_declares_a_full_row(self) -> None:
        fields = {"lang", "dir", "og", "hreflang", "short", "body_class"}
        # the default locale is the publish root and carries no marker class,
        # so both of those are empty for it by design
        blank_for_default = {"dir", "body_class"}
        for code, meta in LOCALES.items():
            with self.subTest(locale=code):
                self.assertEqual(set(meta), fields)
                for field, value in meta.items():
                    if field in blank_for_default:
                        continue
                    self.assertTrue(value, f"{code}.{field} is empty")
        for field in blank_for_default:
            self.assertEqual(LOCALES[DEFAULT_LOCALE][field], "")
            for code in LOCALES:
                if code != DEFAULT_LOCALE:
                    self.assertTrue(LOCALES[code][field], f"{code}.{field}")

    def test_open_graph_locales_are_the_expected_ones(self) -> None:
        self.assertEqual(LOCALES["hans"]["og"], "zh_CN")
        self.assertEqual(LOCALES["hant"]["og"], "zh_TW")
        self.assertEqual(LOCALES["en"]["og"], "en_US")


class PathTests(unittest.TestCase):
    def test_cross_locale_links_are_relative_both_ways(self) -> None:
        self.assertEqual(page_href("hans", "hans", PAGE), PAGE)
        self.assertEqual(page_href("hans", "hant", PAGE), f"zh-Hant/{PAGE}")
        self.assertEqual(page_href("hans", "en", PAGE), f"en/{PAGE}")
        self.assertEqual(page_href("en", "en", PAGE), PAGE)
        self.assertEqual(page_href("en", "hans", PAGE), f"../{PAGE}")
        self.assertEqual(page_href("en", "hant", PAGE), f"../zh-Hant/{PAGE}")
        self.assertEqual(page_href("hant", "en", PAGE), f"../en/{PAGE}")

    def test_no_cross_locale_link_is_absolute(self) -> None:
        for source in LOCALES:
            for target in LOCALES:
                href = page_href(source, target, PAGE)
                with self.subTest(source=source, target=target):
                    self.assertFalse(href.startswith("/"))
                    self.assertFalse(href.startswith("http"))

    def test_assets_resolve_from_every_locale_directory(self) -> None:
        self.assertEqual(asset_href("hans", "avatars/jin.png"), "avatars/jin.png")
        self.assertEqual(asset_href("hant", "avatars/jin.png"), "../avatars/jin.png")
        self.assertEqual(asset_href("en", "avatars/jin.png"), "../avatars/jin.png")

    def test_public_urls_keep_the_simplified_paths_unchanged(self) -> None:
        self.assertEqual(public_url("hans", PAGE), f"{PUBLIC_ROOT}{PAGE}")
        self.assertEqual(public_url("hant", PAGE), f"{PUBLIC_ROOT}zh-Hant/{PAGE}")
        self.assertEqual(public_url("en", PAGE), f"{PUBLIC_ROOT}en/{PAGE}")
        self.assertEqual(public_url("hans", "index.html"), PUBLIC_ROOT)
        self.assertEqual(public_url("en", "index.html"), f"{PUBLIC_ROOT}en/")

    def test_alternate_block_covers_three_locales_plus_x_default(self) -> None:
        block = alternate_links(PAGE)
        self.assertEqual(block.count("<link rel=\"alternate\""), len(LOCALES) + 1)
        for meta in LOCALES.values():
            self.assertIn(f'hreflang="{meta["hreflang"]}"', block)
        self.assertIn(
            '<link rel="alternate" hreflang="x-default" '
            f'href="{PUBLIC_ROOT}{PAGE}">',
            block,
        )


class VocabularyTests(unittest.TestCase):
    def test_every_locale_defines_every_chrome_string(self) -> None:
        reference = set(strings(DEFAULT_LOCALE))
        self.assertGreater(len(reference), 60)
        for code in LOCALES:
            with self.subTest(locale=code):
                self.assertEqual(set(strings(code)), reference)

    def test_no_chrome_string_is_accidentally_empty(self) -> None:
        # both of these are empty on purpose: the ZH tooltip only exists on the
        # English build, and Chinese hit levels are single glyphs that read fine
        # run together, so they want no separator
        optional = {"zhTagTitle", "targetSeparator"}
        for code in LOCALES:
            for key, value in strings(code).items():
                if key in optional or not isinstance(value, str):
                    continue
                with self.subTest(locale=code, key=key):
                    self.assertTrue(value.strip(), f"{code}.{key} is empty")

    def test_the_hit_level_tables_line_up_across_locales(self) -> None:
        for field in ("targetLabels", "targetTitles"):
            reference = set(strings(DEFAULT_LOCALE)[field])
            for code in LOCALES:
                with self.subTest(locale=code, field=field):
                    self.assertEqual(set(strings(code)[field]), reference)

    def test_simplified_column_matches_what_ships_today(self) -> None:
        """The refactor's acceptance test in miniature.

        These are the exact literals the generator carried before the locale
        table existed. If one drifts, the Simplified pages stop being
        byte-identical and the URLs that hold the rankings change under us.
        """
        s = strings("hans")
        self.assertEqual(s["crumb"], "全角色出招表")
        self.assertEqual(s["crumbShort"], "全角色")
        self.assertEqual(s["crumbAria"], "返回全角色选择")
        self.assertEqual(s["quickNav"], "快速导航")
        self.assertEqual(s["themeLabel"], "主题")
        self.assertEqual(s["themeDark"], "夜间")
        self.assertEqual(s["themeLight"], "浅色")
        self.assertEqual(s["notationLabel"], "记法")
        self.assertEqual(s["notationAria"], "指令记法")
        self.assertEqual(s["ntGfx"], "按键图")
        self.assertEqual(s["ntNn"], "无数字")
        self.assertEqual(s["ntTxt"], "文字")
        self.assertEqual(s["pageKind"], "铁拳 8 出招表")
        self.assertEqual(s["secThrows"], "投技")
        self.assertEqual(s["secThrowsAlt"], "THROWS")
        self.assertEqual(s["secAttacks"], "打击技")
        self.assertEqual(s["secAttacksAlt"], "ATTACKS")
        self.assertEqual(s["secHeat"], "热能系统")
        self.assertEqual(s["secTen"], "十连技")
        self.assertEqual(s["secTenAlt"], "10 HIT COMBO")
        self.assertEqual(s["thMove"], "招式")
        self.assertEqual(s["thInput"], "指令")
        self.assertEqual(s["thStartup"], "发生")
        self.assertEqual(s["thDmg"], "伤害")
        self.assertEqual(s["thLevel"], "判定")
        self.assertEqual(s["thSide"], "方向")
        self.assertEqual(s["thBreak"], "挣脱")
        self.assertEqual(s["comboStarter"], "起手")
        self.assertEqual(
            s["comboRoute"], "路线（[数字]=伤害 · T!=回旋 · ~F=按住前 · →=下一招）"
        )
        self.assertEqual(s["breakNone"], "不可挣脱")
        self.assertEqual(s["breakOpposite"], "首/末异键")
        self.assertEqual(s["breakUnknownTitle"], "Wavu 未注明挣脱键")
        self.assertEqual(s["throwFront"], "正面")
        self.assertEqual(s["throwWall"], "墙边")
        self.assertEqual(s["siteName"], "铁拳8 全角色中文出招表")
        self.assertEqual(s["footSource"], "数据来源：")
        self.assertEqual(s["footOfficial"], "TEKKEN 8 官方网站")
        self.assertEqual(
            s["footNote"], "招式名为中文意译，供参考；发生帧表示首击冲击帧。"
        )
        self.assertEqual(
            s["legendStartup"], "首击冲击帧（i=impact，越小越快，依 Wavu）"
        )

    def test_the_traditional_column_carries_no_simplified_glyph(self) -> None:
        """Chrome is authored, not converted, so nothing checks it but this."""
        alphabet = simplified_only_codepoints()
        for key, value in strings("hant").items():
            values = value.values() if isinstance(value, dict) else [value]
            for text in values:
                stray = set(text) & alphabet
                with self.subTest(key=key):
                    self.assertEqual(stray, set(), f"hant.{key}: {sorted(stray)}")

    def test_the_alt_heading_slot_is_the_other_locale_not_english(self) -> None:
        """投技 / THROWS in Chinese, Throws / 投技 in English (spec 7.1)."""
        self.assertEqual(strings("en")["secThrows"], "Throws")
        self.assertEqual(strings("en")["secThrowsAlt"], "投技")
        self.assertEqual(strings("hans")["secThrowsAlt"], "THROWS")
        for code in LOCALES:
            with self.subTest(locale=code):
                self.assertNotEqual(
                    strings(code)["secThrows"], strings(code)["secThrowsAlt"]
                )

    def test_the_english_site_name_drops_chinese_and_keeps_the_search_term(self) -> None:
        name = strings("en")["siteName"]
        self.assertNotIn("中文", name)
        self.assertEqual(name, "TEKKEN 8 Movelist · Frame Data & Command List")
        self.assertNotIn("中文", strings("en")["titleTemplate"])
        self.assertNotIn("中文", strings("en")["descriptionTemplate"])

    def test_english_hit_levels_are_spelled_out(self) -> None:
        labels = strings("en")["targetLabels"]
        self.assertEqual(labels["h"], "High")
        self.assertEqual(labels["m"], "Mid")
        self.assertEqual(labels["l"], "Low")
        self.assertEqual(labels["t"], "Throw")
        self.assertEqual(labels["sp"], "Sp.")
        self.assertEqual(strings("en")["targetTitles"]["SM"],
                         "Special mid (hits grounded)")

    def test_only_the_english_build_needs_the_zh_fallback_tooltip(self) -> None:
        self.assertTrue(strings("en")["zhTagTitle"])
        self.assertEqual(strings("hans")["zhTagTitle"], "")
        self.assertEqual(strings("hant")["zhTagTitle"], "")

    def test_templates_use_the_placeholders_the_generator_supplies(self) -> None:
        allowed = {"display", "canonical", "count", "moves", "visible",
                   "frames", "collapsed", "value"}
        placeholder = re.compile(r"\{(\w+)\}")
        for code in LOCALES:
            for key, value in strings(code).items():
                if not isinstance(value, str):
                    continue
                for name in placeholder.findall(value):
                    with self.subTest(locale=code, key=key, placeholder=name):
                        self.assertIn(name, allowed)


if __name__ == "__main__":
    unittest.main()
