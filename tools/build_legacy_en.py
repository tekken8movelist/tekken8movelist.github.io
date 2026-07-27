# -*- coding: utf-8 -*-
"""English versions of the five one-shot pipeline pages.

jun / xiaoyu / kunimitsu / clive / law came out of `pipeline.py` and have no
structured snapshot, so `build_season2.py` cannot build them in any locale.
Traditional got here first, by running the published Simplified page through a
character converter -- these five pages are their own corpus.

English cannot be had that way, because a move's English name is not a
transformation of its Chinese one: it is Wavu's, or it does not exist. So this
takes the same published page and replaces, rather than converts:

  * `td.name` in the movelist tables takes Wavu's own English name, joined to
    the row by command through `pipeline.candidates` -- the same mapping that
    put startup frames on these pages in the first place. Where Wavu publishes
    no name, the cell takes the project's own description in italics, exactly
    as the other 36 pages do.
  * `.tk-state` chips and the plain-text command take Wavu's stance codes.
    The commands themselves are notation and are left alone.
  * Everything else is copy this project wrote, and comes from `legacy_en`.

Anything Chinese with no entry stops the build and prints itself, so a page
that builds is a page with no Chinese left in it.

Idempotent: re-running writes byte-identical output.

    python tools/build_legacy_en.py [--check] [--report]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pipeline  # noqa: E402
from build_season2 import render_target  # noqa: E402
from legacy_en import (  # noqa: E402
    CAPSULES, COMMAND_WORDS, MOVE_DESCRIPTIONS, MOVE_NAMES, PHRASES, TABLE_HEADS,
)
from locales import LOCALES, alternate_links, public_url, strings  # noqa: E402
from move_name_en import english_name  # noqa: E402
from patch_legacy_pages import LEGACY_PAGES  # noqa: E402

SITE = TOOLS.parent / "docs"
LOCALE = "en"

CHINESE = re.compile(r"[一-鿿]")
CODE_BLOCK = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
LD_JSON = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
COPY_ATTRIBUTE = re.compile(
    r'(\b(?:content|alt|title|placeholder|aria-label)=")([^"]*)(")'
)
TEXT_NODE = re.compile(r">([^<]+)<")
ROW = re.compile(r"<tr\b.*?</tr>", re.S)
NAME_CELL = re.compile(r'(<td class="name">)(.*?)(</td>)', re.S)
CMD_TXT = re.compile(r'(<span class="cmd-txt">)([^<]*)(</span>)')
STATE_CHIP = re.compile(r'(<span class="tk-state">)([^<]*)(</span>)')
EN_TWIN = re.compile(r'\s*<span class="en">[^<]*</span>')
TABLE_HEAD = re.compile(r"(<th\b[^>]*>)([^<]*)(</th>)")
TIPS_MARKER = '<section class="tipsPage">'
LOCALE_SLOT = "<!--locale-control-->"

# Longest first, so 背身时看准对手攻击 wins over 背身时.
_CHIP_KEYS = sorted(CAPSULES, key=len, reverse=True)
_WORD_KEYS = sorted({**CAPSULES, **COMMAND_WORDS}, key=len, reverse=True)
_NOTATION = {**CAPSULES, **COMMAND_WORDS}


class Missing:
    """Every Chinese string the tables could not account for."""

    def __init__(self) -> None:
        self.phrases: dict[str, set[str]] = {}
        self.names: dict[str, set[str]] = {}
        self.notation: dict[str, set[str]] = {}

    def add(self, bucket: str, text: str, where: str) -> None:
        getattr(self, bucket).setdefault(text, set()).add(where)

    def __bool__(self) -> bool:
        return bool(self.phrases or self.names or self.notation)

    def report(self) -> str:
        lines = []
        for label, bucket in (
            ("move names", self.names),
            ("notation words", self.notation),
            ("phrases", self.phrases),
        ):
            if not bucket:
                continue
            lines.append(f"\n--- {label}: {len(bucket)} ---")
            for text, pages in sorted(bucket.items()):
                lines.append(f"  {'/'.join(sorted(pages)):26s} {text}")
        return "\n".join(lines)


def load_wavu_names(key: str) -> dict[str, str]:
    """`command|name` as scraped from Wavu, keyed by command.

    A command can appear twice (once under Heat, once in its own section); the
    named one wins, because an empty name there means "listed again", not
    "unnamed".
    """
    names: dict[str, str] = {}
    path = TOOLS / f"wavu_{key}_names.txt"
    for line in path.read_text(encoding="utf-8").splitlines():
        if "|" not in line:
            continue
        command, name = line.split("|", 1)
        if command not in names or (not names[command] and name):
            names[command] = name.strip()
    return names


def wavu_name(command: str, cfg: dict, names: dict[str, str]) -> str | None:
    lowered = {k.lower(): v for k, v in names.items()}
    for candidate in pipeline.candidates(command, cfg):
        found = names.get(candidate)
        if found is None:
            found = lowered.get(candidate.lower())
        if found:
            return found
    return None


def translate_chip(text: str, missing: Missing, where: str) -> str:
    """A `.tk-state` chip is always a state word, so this stays strict."""
    out = text
    for word in _CHIP_KEYS:
        if word in out:
            out = out.replace(word, CAPSULES[word])
    for run in re.findall(r"[一-鿿]+", out):
        missing.add("notation", run, where)
    return out


def translate_command(text: str, missing: Missing, where: str) -> str:
    """The plain-text command, which in the guide tables is not always one.

    In the movelist a `cmd-txt` really is notation -- swapping the state words
    for Wavu's codes is the whole job. The guide reuses the same cell for combo
    routes and for sentences (`d/f+2:距离极远,大多数怒气技都能罚`), so anything
    still Chinese after the state words go falls back to the phrase table --
    keyed on the original line, so what a translator reads is what the page
    says.
    """
    out = text
    for word in _WORD_KEYS:
        if word in out:
            out = out.replace(word, _NOTATION[word])
    if not CHINESE.search(out):
        return out
    return translate_phrase(text, missing, where)


def rewrite_move_names(markup: str, key: str, cfg: dict, names: dict,
                       missing: Missing, title: str) -> str:
    """Movelist rows only -- the guide tables reuse `td.name` for labels."""

    def one_row(match: re.Match) -> str:
        row = match.group(0)
        command = CMD_TXT.search(row)
        if not command or '<td class="name">' not in row:
            return row
        raw = command.group(2).strip()

        def cell(name_match: re.Match) -> str:
            chinese = re.sub(r"<[^>]+>", "", name_match.group(2)).strip()
            if not chinese or not CHINESE.search(chinese):
                return name_match.group(0)
            official = wavu_name(raw, cfg, names) or MOVE_NAMES.get((key, chinese))
            if official:
                return name_match.group(1) + escape(official) + name_match.group(3)
            described = MOVE_DESCRIPTIONS.get((key, chinese)) or english_name(chinese)
            if described:
                return (
                    name_match.group(1)
                    + f'<span class="refname" title="{title}">'
                    + escape(described)
                    + "</span>"
                    + name_match.group(3)
                )
            missing.add("names", f"{chinese}\t[{raw}]", key)
            return name_match.group(0)

        return NAME_CELL.sub(cell, row, count=1)

    return ROW.sub(one_row, markup)


LEVEL_CELL = re.compile(
    r'(<td[^>]*>)((?:<span class="(?:hi|md|lo|sp)">[^<]*</span>)+)(</td>)'
)
LEVEL_SPAN = re.compile(r'<span class="(?:hi|md|lo|sp)">([^<]*)</span>')
# Longest first so 特中 is one token rather than 特 followed by 中.
LEVEL_GLYPHS = (("特中", "sm"), ("特下", "sl"), ("特殊", "sp"), ("上", "h"),
                ("中", "m"), ("下", "l"), ("投", "t"), ("特", "sp"))
LEVEL_NOISE = "·、,，"
LEVEL_REPEAT = re.compile(r"×(\d+)")


def level_tokens(text: str) -> list[str] | None:
    """Wavu-style tokens for a hit-level cell, or None if it is not one.

    Has to cope with the Simplified page's own shorthand, because that is what
    is on disk: `中×5` for five mids and `特中·投` with a separator between the
    two. Missing either means the cell falls through to the phrase table, and
    then a cell of several spans has each span translated on its own and they
    come out joined -- `HighHighSpecial`.
    """
    tokens: list[str] = []
    index = 0
    while index < len(text):
        character = text[index]
        if character in LEVEL_NOISE or character.isspace():
            index += 1
            continue
        if character == "×" and tokens:
            repeat = LEVEL_REPEAT.match(text, index)
            if not repeat:
                return None
            tokens.extend([tokens[-1]] * (int(repeat.group(1)) - 1))
            index = repeat.end()
            continue
        # Wavu already writes both of these: `m!` for an unblockable mid, and
        # an uppercase token for one that also hits a grounded opponent. Using
        # its spelling means `render_target` gives them the same title here as
        # it does on the other 36 pages.
        if character == "!" and tokens:
            tokens[-1] += "!"
            index += 1
            continue
        if text.startswith("(地)", index) and tokens:
            tokens[-1] = tokens[-1].upper()
            index += 3
            continue
        if text.startswith("(投)", index) and tokens:
            tokens[-1] += " (t)"  # wavu writes a throw-property mid as `m (t)`
            index += 3
            continue
        for glyph, token in LEVEL_GLYPHS:
            if text.startswith(glyph, index):
                tokens.append(token)
                index += len(glyph)
                break
        else:
            return None  # (地), 不可防(中) -- copy, not a run of levels
    return tokens or None


def render_hit_levels(markup: str) -> str:
    """Re-render the hit-level column through the generator's own renderer.

    The Simplified page prints one glyph per segment and no separator, which
    is right for Chinese -- 中投 reads as two things because each glyph is a
    word. Translate the glyphs where they sit and you get `MidThrow`, and a
    ten-hit string becomes an unreadable run. It is not even a stable split:
    the same 上上中 is sometimes three spans and sometimes two, so this reads
    the glyphs rather than the markup.

    `render_target` already decides all of this for the other 36 pages --
    spelled out to three segments, single letters with a title beyond that,
    `/` and a `<wbr>` between -- so it decides it here too.
    """
    s = strings(LOCALE)

    def cell(match: re.Match) -> str:
        glyphs = "".join(LEVEL_SPAN.findall(match.group(2)))
        tokens = level_tokens(glyphs)
        if tokens is None:
            return match.group(0)  # ×4, (地), 不可防(中) -- copy, not a run
        return match.group(1) + render_target(",".join(tokens), s) + match.group(3)

    return LEVEL_CELL.sub(cell, markup)


def translate_json(value, missing: Missing, where: str):
    if isinstance(value, str):
        return translate_phrase(value, missing, where)
    if isinstance(value, list):
        return [translate_json(item, missing, where) for item in value]
    if isinstance(value, dict):
        return {k: translate_json(v, missing, where) for k, v in value.items()}
    return value


def translate_phrase(text: str, missing: Missing, where: str) -> str:
    stripped = text.strip()
    if not stripped or not CHINESE.search(stripped):
        return text
    if stripped in PHRASES:
        lead = text[: len(text) - len(text.lstrip())]
        tail = text[len(text.rstrip()):]
        return lead + PHRASES[stripped] + tail
    missing.add("phrases", stripped, where)
    return text


def translate_markup(markup: str, missing: Missing, where: str) -> str:
    """Copy is translated; scripts, styles and class names are not touched."""
    pieces = []
    cursor = 0
    for block in CODE_BLOCK.finditer(markup):
        pieces.append(("copy", markup[cursor:block.start()]))
        pieces.append(("code", block.group(0)))
        cursor = block.end()
    pieces.append(("copy", markup[cursor:]))

    out = []
    for kind, piece in pieces:
        if kind == "code":
            ld = LD_JSON.fullmatch(piece)
            if ld:
                data = translate_json(json.loads(ld.group(2)), missing, where)
                piece = (
                    ld.group(1)
                    + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
                    + ld.group(3)
                )
            out.append(piece)
            continue
        # notation first: its Chinese must not reach the phrase table
        piece = STATE_CHIP.sub(
            lambda m: m.group(1)
            + translate_chip(m.group(2), missing, where)
            + m.group(3),
            piece,
        )
        piece = CMD_TXT.sub(
            lambda m: m.group(1)
            + translate_command(m.group(2), missing, where)
            + m.group(3),
            piece,
        )
        # A column head and a legend label can be the same Chinese word and
        # want different English: 判定 heads a column called `Hit` but labels a
        # legend entry that reads `Hit level`. Heads get first refusal.
        piece = TABLE_HEAD.sub(
            lambda m: m.group(1)
            + (
                TABLE_HEADS[m.group(2).strip()]
                if m.group(2).strip() in TABLE_HEADS
                else translate_phrase(m.group(2), missing, where)
            )
            + m.group(3),
            piece,
        )
        piece = COPY_ATTRIBUTE.sub(
            lambda m: m.group(1)
            + translate_phrase(m.group(2), missing, where)
            + m.group(3),
            piece,
        )
        piece = TEXT_NODE.sub(
            lambda m: ">" + translate_phrase(m.group(1), missing, where) + "<",
            piece,
        )
        out.append(piece)
    return "".join(out)


LEGEND_TOP = re.compile(r'(<div class="lgtop">)(.*?)(</div>)', re.S)


def add_legend_ref_note(markup: str, key: str) -> str:
    """The one line that says what the italic names are.

    The generator adds this from `legendRefNames`; these pages get their
    legend from `patch_legacy_pages`, which knows nothing about it. Skipped
    when the page has no described names -- a legend entry for something not
    on the page is just a puzzle.
    """
    if 'class="refname"' not in markup:
        return markup
    note = f'<span class="lgref">{escape(strings(LOCALE)["legendRefNames"])}</span>'
    updated, count = LEGEND_TOP.subn(
        lambda m: m.group(1) + m.group(2) + note + m.group(3), markup, count=1
    )
    if not count:
        raise SystemExit(f"{key}: no .lgtop to put the italics note in")
    return updated


def retarget(markup: str, filename: str) -> str:
    """One directory down, and pointing at the English canonical."""
    markup = markup.replace('src="avatars/', 'src="../avatars/')
    markup = markup.replace('href="avatars/', 'href="../avatars/')
    meta = LOCALES[LOCALE]
    markup = re.sub(r'(?<=<html lang=")[^"]*(?=")', meta["lang"], markup, count=1)
    body_class = meta["body_class"]
    if body_class:
        markup = markup.replace(
            f'<html lang="{meta["lang"]}">',
            f'<html lang="{meta["lang"]}" class="{body_class}">',
            1,
        )
    markup = re.sub(
        r'(?<=<meta property="og:locale" content=")[^"]*(?=")',
        meta["og"], markup, count=1,
    )
    markup = re.sub(
        r'(?<=<link rel="canonical" href=")[^"]*(?=")',
        public_url(LOCALE, filename), markup, count=1,
    )
    markup = re.sub(
        r'(?<=<meta property="og:url" content=")[^"]*(?=")',
        public_url(LOCALE, filename), markup, count=1,
    )
    canonical = f'<link rel="canonical" href="{public_url(LOCALE, filename)}">'
    if canonical not in markup:
        raise SystemExit(f"{filename}: canonical not rewritten")
    if 'rel="alternate"' not in markup:
        markup = markup.replace(
            canonical, canonical + "\n" + alternate_links(filename), 1
        )
    return markup


def build(key: str, filename: str, missing: Missing) -> str:
    cfg = pipeline.CONFIG[key]
    names = load_wavu_names(key)
    source = (SITE / filename).read_text(encoding="utf-8")
    title = escape(strings(LOCALE)["refNameTitle"], quote=True)

    head, marker, tips = source.partition(TIPS_MARKER)
    if not marker:
        raise SystemExit(f"{filename}: no tipsPage section to split on")
    head = rewrite_move_names(head, key, cfg, names, missing, title)
    markup = render_hit_levels(head + marker + tips)

    # The language control is rebuilt from `locales`, so lift it out before
    # translating: its 简 and 繁 are the one place Chinese belongs on an
    # English page, and letting them reach the phrase table would mean either
    # listing them as "translations" of themselves or carving an exception
    # into the missing report. Neither is as clear as not looking at it.
    markup = re.sub(
        r'<div class="lcgl">.*?</div>', LOCALE_SLOT, markup, count=1, flags=re.S
    )

    # The bilingual heading twins are a Chinese-page device: `Throws 投技`
    # helps a Chinese reader, `Throws Throws` helps nobody.
    markup = EN_TWIN.sub("", markup)

    markup = translate_markup(markup, missing, key)
    markup = add_legend_ref_note(markup, key)
    markup = retarget(markup, filename)
    from patch_legacy_pages import locale_control

    return markup.replace(LOCALE_SLOT, locale_control(filename, current=LOCALE), 1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if a page is out of date")
    parser.add_argument("--report", action="store_true",
                        help="list untranslated strings and write nothing")
    args = parser.parse_args(argv)

    missing = Missing()
    built_pages = {}
    for key, filename in LEGACY_PAGES.items():
        built_pages[filename] = build(key, filename, missing)

    if missing:
        print(missing.report())
        counts = (len(missing.names), len(missing.notation), len(missing.phrases))
        print(f"\n{sum(counts)} untranslated strings "
              f"({counts[0]} names, {counts[1]} notation, {counts[2]} phrases)")
        return 1
    if args.report:
        print("ok    every string on the five pages has English")
        return 0

    destination_dir = SITE / LOCALES[LOCALE]["dir"]
    destination_dir.mkdir(parents=True, exist_ok=True)
    status = 0
    for filename, built in built_pages.items():
        destination = destination_dir / filename
        current = (
            destination.read_text(encoding="utf-8")
            if destination.is_file() else ""
        )
        if args.check:
            state = "ok" if current == built else "STALE"
            if state == "STALE":
                status = 1
            print(f"{state:6s} en/{filename}")
        elif current == built:
            print(f"unchanged en/{filename}")
        else:
            destination.write_text(built, encoding="utf-8", newline="\n")
            print(f"built     en/{filename}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
