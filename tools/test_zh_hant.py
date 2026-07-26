# -*- coding: utf-8 -*-
"""Contract for the build-time Simplified -> Taiwan Traditional conversion.

These are property assertions rather than a table of hand-picked translations:
the authority on what s2twp produces is OpenCC itself, and the vendored
dictionaries are checked against it wholesale by tools/_verify_zh_hant.py
(a one-time cross-check, not a build dependency). What has to hold on every
build is that the output carries no Simplified-only glyph, that phrase entries
beat character-by-character mapping, and that overrides win.
"""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from zh_hant import (  # noqa: E402
    convert,
    convert_translation,
    override_keys,
    simplified_only_codepoints,
)


class ConvertTests(unittest.TestCase):
    def test_the_simplified_only_alphabet_is_populated(self) -> None:
        alphabet = simplified_only_codepoints()
        self.assertGreater(len(alphabet), 2000)
        for char in "发伤达帧读历冲":
            self.assertTrue(char in alphabet, f"{char} should be Simplified-only")
        # characters shared by both scripts must not be in it, or the gate would
        # reject perfectly good Traditional output
        for char in "月白拍子天雨花":
            self.assertFalse(char in alphabet, f"{char} is shared, not Simplified")

    def test_merged_characters_that_are_valid_traditional_are_not_flagged(self) -> None:
        """里 in 香格里拉 and 征 in 征服者 are correct Traditional, not misses.

        Simplified merged pairs like 裏/里 and 徵/征 onto one glyph, and the
        surviving glyph is still a Traditional character in its own right. A
        gate that flagged them would fail on output OpenCC itself produces.
        """
        alphabet = simplified_only_codepoints()
        for char in "里征后台干松表准范游余向志丑划面":
            self.assertFalse(
                char in alphabet,
                f"{char} is a valid Traditional character in some sense",
            )
        for name in ("香格里拉", "征服者连打", "背后擒摔"):
            with self.subTest(name=name):
                self.assertFalse(set(convert(name)) & alphabet)

    def test_characters_the_chain_hands_back_are_not_flagged(self) -> None:
        """峰 -> 峯 -> 峰 and 秘 -> 祕 -> 秘 survive the round trip.

        TWVariants, the last pass, restores them, so they legitimately appear
        in Hant output even though STCharacters does not list them as their own
        Traditional reading.
        """
        alphabet = simplified_only_codepoints()
        for char in "峰秘":
            self.assertEqual(convert(char), char)
            self.assertFalse(char in alphabet, f"{char} round-trips, do not flag it")

    def test_the_alphabet_never_flags_the_converter_s_own_output(self) -> None:
        """The gate must not fail on anything this converter can produce."""
        alphabet = simplified_only_codepoints()
        for source in "发读伤帧历冲里征后台干秘峰":
            with self.subTest(source=source):
                self.assertFalse(set(convert(source)) & alphabet)

    def test_output_never_contains_simplified_only_codepoints(self) -> None:
        sample = (
            "背身时　破势步　热能爆发　起身中　横移中　数据来源　"
            "发生帧　伤害　判定　挣脱　十连技　进阶攻略"
        )
        stray = set(convert(sample)) & simplified_only_codepoints()
        self.assertEqual(stray, set(), f"unconverted glyphs: {sorted(stray)}")

    def test_japanese_kanji_move_names_survive_the_crossing(self) -> None:
        # the corpus is largely kanji taken straight across from Japanese
        for name in ("月读", "白拍子", "天丛云", "彼岸花", "时雨"):
            with self.subTest(name=name):
                converted = convert(name)
                self.assertEqual(len(converted), len(name))
                self.assertFalse(set(converted) & simplified_only_codepoints())

    def test_phrase_entries_beat_character_by_character_mapping(self) -> None:
        """`s2twp` is a chain, and the phrase passes have to run.

        发 alone is 發; inside 头发 it is 髮. Only the phrase pass knows that,
        so this is the assertion that fails if the chain collapses to one
        character table.
        """
        phrase = "头发"
        char_by_char = "".join(convert(char) for char in phrase)
        self.assertEqual(char_by_char, "頭發")
        self.assertEqual(convert(phrase), "頭髮")

    def test_conversion_is_idempotent_on_its_own_output(self) -> None:
        sample = "热能爆发　背身时　发生帧　数据来源"
        once = convert(sample)
        self.assertEqual(convert(once), once)

    def test_ascii_and_command_notation_pass_through_untouched(self) -> None:
        # the command column never translates -- d/f+2, WS, FC, SS, CD, qcf
        for command in ("d/f+2", "WS", "FC", "SS", "CD", "qcf", "b,f+2,1,df+2"):
            with self.subTest(command=command):
                self.assertEqual(convert(command), command)


class TranslationDocumentTests(unittest.TestCase):
    def document(self) -> dict:
        return {
            "schema_version": 1,
            "character_key": "jin",
            "move_names": {"Jin-2+3": "热能爆发", "Jin-1": "左直拳"},
            "section_names": {"Heat": "热能", "WS": "起身技"},
            "stance_names": {"BT": "背身时", "CD": "破势步"},
        }

    def test_every_localisable_field_is_converted(self) -> None:
        converted = convert_translation(self.document(), "jin")
        alphabet = simplified_only_codepoints()
        for field in ("move_names", "section_names", "stance_names"):
            for value in converted[field].values():
                self.assertFalse(set(value) & alphabet, f"{field}: {value}")

    def test_untouched_fields_survive(self) -> None:
        converted = convert_translation(self.document(), "jin")
        self.assertEqual(converted["schema_version"], 1)
        self.assertEqual(converted["character_key"], "jin")

    def test_the_source_document_is_not_mutated(self) -> None:
        document = self.document()
        convert_translation(document, "jin")
        self.assertEqual(document["move_names"]["Jin-2+3"], "热能爆发")

    def test_overrides_win_over_the_converter(self) -> None:
        document = self.document()
        converted = convert_translation(
            document, "jin", overrides={"jin": {"Jin-1": "左直拳（覆蓋）"}}
        )
        self.assertEqual(converted["move_names"]["Jin-1"], "左直拳（覆蓋）")
        # a move without an override still goes through the table
        self.assertNotEqual(converted["move_names"]["Jin-2+3"], "热能爆发")

    def test_override_keys_are_reported_for_the_staleness_gate(self) -> None:
        keys = override_keys("jin", overrides={"jin": {"Jin-1": "x", "Jin-9": "y"}})
        self.assertEqual(keys, {"Jin-1", "Jin-9"})
        self.assertEqual(override_keys("nobody", overrides={}), set())


if __name__ == "__main__":
    unittest.main()
