# -*- coding: utf-8 -*-
"""Simplified -> Taiwan Traditional conversion, at build time, with no deps.

`build_season2.py` has always been offline, stdlib-only and byte-reproducible,
and the Traditional locale must not cost that. So instead of importing OpenCC,
this module carries OpenCC's own dictionary files verbatim under `tools/opencc/`
and walks them itself. The vendored files are upstream text, unedited, so the
question "is this really s2twp?" is answerable with a diff rather than trust --
see `tools/opencc/README.md` for provenance and the refresh procedure.

The `s2twp` conversion chain, per OpenCC's own `s2twp.json`, is three passes:

    1. group(STPhrases, STCharacters)   Simplified -> Traditional
    2. TWPhrases                        Traditional -> Taiwan vocabulary
    3. TWVariants                       Traditional -> Taiwan glyph variants

They stay three passes here for the same reason OpenCC keeps them separate: a
Taiwan phrase must not fire on text that has not been converted yet. Within a
pass, matching is greedy longest-first, which is what makes a phrase entry beat
the character-by-character mapping sitting beside it in the same group.

This converts the *corpus* -- move, section and stance names. UI chrome is NOT
converted here: 记法 -> 記法 is mechanical, but 数据 -> 資料 and 视频 -> 影片
are Taiwan vocabulary rather than character mapping, so chrome strings are
authored per locale in `tools/locales.py`.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
DICTIONARIES = TOOLS / "opencc"
OVERRIDES_PATH = TOOLS / "zh_hant_overrides.json"

# one pass per entry, in s2twp's chain order; a pass may merge several files
# the way OpenCC's `group` dict does
PASSES = (
    ("STPhrases", "STCharacters"),
    ("TWPhrases",),
    ("TWVariants",),
)

LOCALISABLE_FIELDS = ("move_names", "section_names", "stance_names")


def _load_candidates(name: str) -> dict[str, list[str]]:
    """Parse one OpenCC `.txt` dictionary: `source<TAB>target [target...]`."""
    mapping: dict[str, list[str]] = {}
    text = (DICTIONARIES / f"{name}.txt").read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        source, _, targets = line.partition("\t")
        candidates = [token for token in targets.split(" ") if token.strip()]
        if source and candidates:
            mapping[source] = candidates
    return mapping


def _load_dictionary(name: str) -> dict[str, str]:
    """The same dictionary reduced to one target per source.

    Entries may list several candidates; OpenCC takes the first, and so do we.
    """
    return {
        source: candidates[0]
        for source, candidates in _load_candidates(name).items()
    }


@lru_cache(maxsize=1)
def _passes() -> tuple[tuple[dict[str, str], int], ...]:
    """(mapping, longest key length) per pass, parsed once per process."""
    compiled = []
    for names in PASSES:
        mapping: dict[str, str] = {}
        for name in names:
            # earlier files in a group win, matching OpenCC's group semantics
            for source, target in _load_dictionary(name).items():
                mapping.setdefault(source, target)
        compiled.append((mapping, max(map(len, mapping))))
    return tuple(compiled)


@lru_cache(maxsize=1)
def simplified_only_codepoints() -> frozenset[str]:
    """Characters that exist in Simplified but not in Traditional.

    The gate's alphabet: none of these may survive into a Hant page, because
    their presence means a string reached it without being converted.

    The test is *not* "would the converter change this character" -- that
    over-reaches. Simplified merged several distinct Traditional characters
    into one, and for many of those merges the Simplified form is itself a
    perfectly good Traditional character used in another sense: 里 is 裏 in
    「里面」 but stays 里 in 「香格里拉」, 后 is 後 in 「背后」 but stays 后 in
    「皇后」, likewise 征/徵, 台/臺, 干/幹, 面/麪. Flagging those would fail the
    gate on correct Traditional output.

    OpenCC already encodes the distinction: STCharacters lists every valid
    Traditional reading of a Simplified character, and lists the character
    itself among them exactly when it is also a Traditional character. So a
    source that is absent from its own candidate list -- 发 -> 發/髮, 读 -> 讀,
    帧 -> 幀 -- is Simplified-only, and one that is present is not.

    That alone still over-reaches, because the chain's last pass can hand a
    character back: 峰 becomes 峯 in the Traditional pass and 峰 again under
    TWVariants, 秘 likewise via 祕. Those round-trip, so they appear in correct
    Hant output and must not be flagged. Hence the second condition -- the full
    chain has to actually change the character.
    """
    return frozenset(
        source
        for source, candidates in _load_candidates("STCharacters").items()
        if len(source) == 1 and source not in candidates and convert(source) != source
    )


def _apply(text: str, mapping: dict[str, str], longest: int) -> str:
    out: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        width = min(longest, length - index)
        while width > 0:
            replacement = mapping.get(text[index : index + width])
            if replacement is not None:
                out.append(replacement)
                index += width
                break
            width -= 1
        else:
            out.append(text[index])
            index += 1
    return "".join(out)


@lru_cache(maxsize=None)
def convert(text: str) -> str:
    for mapping, longest in _passes():
        text = _apply(text, mapping, longest)
    return text


@lru_cache(maxsize=1)
def _default_overrides() -> dict[str, dict[str, str]]:
    """Load the override table, dropping `_`-prefixed keys at both levels.

    The file carries its rationale inline -- an override that cannot say why it
    exists is one nobody can safely remove later -- so `_comment` / `_review`
    keys appear beside characters and beside move ids, and neither is data.
    """
    if not OVERRIDES_PATH.is_file():
        return {}
    document = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    return {
        key: {
            move_id: name
            for move_id, name in value.items()
            if not move_id.startswith("_")
        }
        for key, value in document.items()
        if not key.startswith("_") and isinstance(value, dict)
    }


def override_keys(key: str, overrides: dict | None = None) -> set[str]:
    """Override ids registered for one character, for the staleness gate."""
    table = _default_overrides() if overrides is None else overrides
    return set(table.get(key, {}))


def convert_translation(
    translation: dict,
    key: str,
    overrides: dict | None = None,
) -> dict:
    """Convert a `{key}_zh.json` document; per-move-id overrides win.

    Returns a new document -- the caller's Simplified snapshot is the source of
    truth for the other two locales and must not be mutated underneath them.
    """
    table = _default_overrides() if overrides is None else overrides
    move_overrides = table.get(key, {})
    converted = dict(translation)
    for field in LOCALISABLE_FIELDS:
        values = translation.get(field)
        if values is None:
            continue
        if field == "move_names":
            converted[field] = {
                move_id: move_overrides.get(move_id, convert(name))
                for move_id, name in values.items()
            }
        else:
            converted[field] = {
                code: convert(name) for code, name in values.items()
            }
    return converted
