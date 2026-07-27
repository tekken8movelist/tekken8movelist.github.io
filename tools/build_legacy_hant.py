# -*- coding: utf-8 -*-
"""Traditional versions of the five one-shot pipeline pages.

jun / xiaoyu / clive / kunimitsu / law came out of `pipeline.py` and have no
structured snapshot, so `build_season2.py` cannot build them in any locale.
English therefore has to wait for the migration -- Wavu's English move names
only exist in a snapshot nobody has taken yet.

Traditional does not have to wait. It was never a translation in the first
place: the other 36 pages get it by running their Simplified corpus through
`zh_hant.convert` at build time, and these five pages *are* their own corpus,
sitting on disk as Simplified HTML. So this converts the published page
directly and writes `docs/zh-Hant/`.

What gets converted is the narrow part that matters and nothing else:

  * text between tags, outside `<script>` and `<style>`
  * the attributes that carry copy (`content`, `alt`, `title`, ...)
  * the string values inside the `application/ld+json` block, parsed as JSON
    rather than pattern-matched, so a comma inside a description cannot break
    the document

Everything else -- CSS, the notation and theme scripts, every command string --
is left byte-for-byte alone. Commands are notation, not language.

Idempotent: re-running writes byte-identical output.

    python tools/build_legacy_hant.py [--check]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from locales import LOCALES, alternate_links, public_url  # noqa: E402
from patch_legacy_pages import LEGACY_PAGES  # noqa: E402
from zh_hant import convert  # noqa: E402

SITE = TOOLS.parent / "docs"
LOCALE = "hant"

CODE_BLOCK = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
LD_JSON = re.compile(
    r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S
)
COPY_ATTRIBUTE = re.compile(
    r'(\b(?:content|alt|title|placeholder|aria-label)=")([^"]*)(")'
)
TEXT_NODE = re.compile(r">([^<]+)<")
CHINESE = re.compile(r"[一-鿿]")


def convert_json_strings(value):
    if isinstance(value, str):
        return convert(value)
    if isinstance(value, list):
        return [convert_json_strings(item) for item in value]
    if isinstance(value, dict):
        return {key: convert_json_strings(item) for key, item in value.items()}
    return value


def convert_markup(markup: str) -> str:
    """Convert copy, leave code alone.

    Splitting on the code blocks first is the whole safety argument: the
    converter never sees a selector, a class name or a command string, so the
    only way it can change the page is through words a reader reads.
    """
    pieces = []
    cursor = 0
    for block in CODE_BLOCK.finditer(markup):
        pieces.append(("copy", markup[cursor:block.start()]))
        pieces.append(("code", block.group(0)))
        cursor = block.end()
    pieces.append(("copy", markup[cursor:]))

    converted = []
    for kind, piece in pieces:
        if kind == "code":
            ld = LD_JSON.fullmatch(piece)
            if ld:
                data = convert_json_strings(json.loads(ld.group(2)))
                piece = ld.group(1) + json.dumps(
                    data, ensure_ascii=False, separators=(",", ":")
                ) + ld.group(3)
            converted.append(piece)
            continue
        piece = COPY_ATTRIBUTE.sub(
            lambda m: m.group(1) + convert(m.group(2)) + m.group(3), piece
        )
        piece = TEXT_NODE.sub(lambda m: ">" + convert(m.group(1)) + "<", piece)
        converted.append(piece)
    return "".join(converted)


def locale_control(filename: str) -> str:
    """简 becomes a link now that this page has a Traditional twin.

    English stays disabled: there is no English page to point at, and a
    control that lies about where it goes is worse than one that says no.
    """
    from patch_legacy_pages import locale_control as simplified_control

    return simplified_control(filename, current=LOCALE)


def retarget(markup: str, filename: str) -> str:
    """One directory down: assets move up, the hub link stays put."""
    markup = markup.replace('src="avatars/', 'src="../avatars/')
    markup = markup.replace('href="avatars/', 'href="../avatars/')
    meta = LOCALES[LOCALE]
    markup = re.sub(r'(?<=<html lang=")[^"]*(?=")', meta["lang"], markup, count=1)
    markup = re.sub(
        r'(?<=<meta property="og:locale" content=")[^"]*(?=")',
        meta["og"], markup, count=1,
    )
    for attribute in ("canonical", "og:url"):
        pattern = (
            r'(?<=<link rel="canonical" href=")[^"]*(?=")'
            if attribute == "canonical"
            else r'(?<=<meta property="og:url" content=")[^"]*(?=")'
        )
        markup = re.sub(pattern, public_url(LOCALE, filename), markup, count=1)
    # alternates go in once, right after canonical
    canonical = (
        f'<link rel="canonical" href="{public_url(LOCALE, filename)}">'
    )
    if canonical not in markup:
        raise SystemExit(f"{filename}: canonical not rewritten")
    # `hreflang=` alone is the wrong guard: the locale control carries one on
    # every link, so it is always present and the block was never inserted
    if 'rel="alternate"' not in markup:
        markup = markup.replace(
            canonical, canonical + "\n" + alternate_links(filename), 1
        )
    return markup


def build(filename: str) -> str:
    source = (SITE / filename).read_text(encoding="utf-8")
    markup = convert_markup(source)
    markup = retarget(markup, filename)
    # the Simplified page's control was written for a page with no twin
    markup = re.sub(
        r'<div class="lcgl">.*?</div>', locale_control(filename), markup,
        count=1, flags=re.S,
    )
    return markup


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if a page is out of date")
    args = parser.parse_args(argv)

    destination_dir = SITE / LOCALES[LOCALE]["dir"]
    destination_dir.mkdir(parents=True, exist_ok=True)
    status = 0
    for filename in LEGACY_PAGES.values():
        built = build(filename)
        destination = destination_dir / filename
        current = (
            destination.read_text(encoding="utf-8")
            if destination.is_file()
            else ""
        )
        if args.check:
            state = "ok" if current == built else "STALE"
            if state == "STALE":
                status = 1
            print(f"{state:6s} zh-Hant/{filename}")
        elif current == built:
            print(f"unchanged zh-Hant/{filename}")
        else:
            destination.write_text(built, encoding="utf-8", newline="\n")
            print(f"built     zh-Hant/{filename}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
