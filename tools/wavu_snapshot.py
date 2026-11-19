# -*- coding: utf-8 -*-
"""Turn a raw Wavu scrape (tools/wavu_extract.js) into the generator's snapshots.

The browser half lives in ``wavu_extract.js``: it runs inside a wavu.wiki tab
that has already passed Anubis and dumps ``{page: {moves, combos2}}`` to the
clipboard. This half is deterministic and offline:

    python tools/wavu_snapshot.py RAW.json Bob=bob "Roger_Jr.=roger_jr"

writes ``source/{key}.json``, ``source/{key}_combos.json`` and
``wavu_{key}.txt`` for every ``Page=key`` pair. ``--compare`` diffs against the
snapshots already on disk instead of writing, which is how the extractor was
checked against the 2026-07 scrape before it was trusted with new characters.

Since 2026-11 Wavu publishes most ten-strings as wikitables rather than move
cards. Pass ``--tables TENS.json`` (the browser half's ``TK8.grabTens``) or
those characters lose their ten-string tables; see ``synthesize_ten_strings``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SOURCE = TOOLS / "source"
ZERO_WIDTH = re.compile("[​‌‍﻿]")
GLUED = re.compile(r"(?<![\d.])\d{3,}(?![\d.])")

MOVE_FIELDS = (
    "alt",
    "block",
    "command",
    "counter_hit",
    "damage",
    "displayed_input",
    "hit",
    "id",
    "name",
    "notes",
    "number",
    "range",
    "recovery",
    "section",
    "startup",
    "states",
    "target",
)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", ZERO_WIDTH.sub("", value or "")).strip()


def join_chain(lead: str, tail: str) -> str:
    lead, tail = clean(lead), clean(tail)
    if not lead:
        return tail
    if not tail:
        return lead
    return lead + tail if tail.startswith(",") else f"{lead},{tail}"


def split_alts(values: list[str]) -> list[str]:
    """Wavu lists several alternative inputs in one cell, space separated.

    Split only when every part reads as notation (has a digit or a dot);
    a lone label such as `Single Boot` stays whole.
    """
    out = []
    for value in values:
        value = clean(value)
        if not value:
            continue
        parts = value.split(" ")
        if len(parts) > 1 and all(re.search(r"[\d.]", part) for part in parts):
            out.extend(parts)
        else:
            out.append(value)
    return out


def parent_command(command: str, displayed: str) -> str | None:
    """`df+1,2,1` shown as `,1` -> `df+1,2`; None when the tail does not fit."""
    bare = ZERO_WIDTH.sub("", command)
    tail = ZERO_WIDTH.sub("", displayed).replace(" ", "_")
    if not tail.startswith(",") or not bare.endswith(tail):
        return None
    return bare[: -len(tail)]


def convert_moves(page: str, raw_moves: list[dict], tables: list[dict] | None = None) -> list[dict]:
    prefix = f"{page}-"
    moves = []
    for raw in raw_moves:
        move_id = raw["id"]
        if move_id.startswith(prefix):
            command = move_id[len(prefix):]
        elif move_id.startswith("Generic-"):
            # shared cards (Heat Burst, Ki Charge) a page includes from the
            # Generic template; the July snapshots keep them under this id
            command = move_id[len("Generic-"):]
        elif "-" not in move_id.split(".")[0]:
            # a card whose id lost its character prefix on Wavu (Steve's
            # `EXD.1+2`): the id is the command
            command = move_id
        else:
            continue  # another character's card
        if not command:
            continue  # the empty `Paul-` legend card
        moves.append(
            {
                "alt": split_alts(raw.get("alt", [])),
                "block": clean(raw["block"]),
                "command": command,
                "counter_hit": clean(raw["counter_hit"]),
                "damage": join_chain(raw["damageLead"], raw["damageTail"]),
                "displayed_input": clean(raw["displayed_input"]),
                "hit": clean(raw["hit"]),
                "id": move_id,
                "name": clean(raw["name"]),
                "notes": clean(raw["notes"]),
                "number": clean(raw["number"]),
                "range": clean(raw["range"]),
                "recovery": clean(raw["recovery"]),
                "section": clean(raw["section"]),
                "startup": clean(raw["startup"]),
                "states": clean(raw["states"]),
                "target": join_chain(raw["targetLead"], raw["targetTail"]),
                "_damage_tail": clean(raw["damageTail"]),
                "_target_tail": clean(raw["targetTail"]),
            }
        )
    rebuild_glued_chains(moves)
    for move in moves:
        move.pop("_damage_tail")
        move.pop("_target_tail")
    moves.extend(synthesize_ten_strings(page, tables or []))
    unify_duplicate_names(moves)
    return moves


def rebuild_glued_chains(moves: list[dict]) -> None:
    """Wavu's lead node on 3+ hit derived cards can lose its separators
    (`1210` = 12,10). Rebuild any such chain from the parent card instead."""
    by_bare = {ZERO_WIDTH.sub("", m["command"]): m for m in moves}
    for move in moves:
        if not GLUED.search(move["damage"].split("(")[0]):
            continue
        parent = parent_command(move["command"], move["displayed_input"])
        if parent is None or parent not in by_bare:
            continue
        head = by_bare[parent]
        move["damage"] = join_chain(head["damage"], move["_damage_tail"])
        move["target"] = join_chain(head["target"], move["_target_tail"])


TEN_SECTION = re.compile(r"\b10[ -](?:strings?|hit)\b", re.I)


def ten_string_chains(tables: list[dict]) -> list[dict]:
    """Wavu's ten-string wikitables -> one chain per "10 Hit Combo N" block.

    A table is: an optional single-cell title row ("10 Hit Combo 2"), a row of
    <th> headers, then one row per hit. Two things the July synthesizer got
    wrong live here: the header row is not a hit (Paul's first column header is
    blank, so it read as an input with damage "Damage"), and one table can hold
    several strings (King's two combos came out as one 20-hit chain).
    """
    chains = []
    for table in tables:
        if not TEN_SECTION.search(table["section"]):
            continue
        current, header = None, None
        for row in table["rows"]:
            tags = [tag for tag, _ in row]
            cells = [clean(text) for _, text in row]
            if len(cells) == 1:
                current = {"section": table["section"], "title": cells[0], "steps": []}
                chains.append(current)
                header = None
                continue
            if all(tag == "th" for tag in tags):
                header = [cell.casefold() for cell in cells]
                continue
            if header is None or not cells or not cells[0]:
                continue
            if current is None:
                current = {"section": table["section"], "title": "", "steps": []}
                chains.append(current)
            column = dict(zip(header, cells))
            current["steps"].append(
                {
                    "input": cells[0],
                    "target": column.get("hit level") or column.get("level", ""),
                    "damage": column.get("damage", ""),
                    "startup": column.get("startup", ""),
                    "block": column.get("block", ""),
                    "hit": column.get("hit", ""),
                    "notes": column.get("notes", "") or column.get("combo", ""),
                }
            )
    return [chain for chain in chains if chain["steps"]]


def synthesize_ten_strings(page: str, tables: list[dict]) -> list[dict]:
    """Progressive records, one per prefix, in the card schema (anna shape)."""
    prefix = f"{page}-"
    records = []
    for chain in ten_string_chains(tables):
        steps = chain["steps"]
        for index in range(len(steps)):
            inputs = [step["input"] for step in steps[: index + 1]]
            step = steps[index]
            command = ",".join(inputs)
            records.append(
                {
                    "alt": [],
                    "block": step["block"],
                    "command": command,
                    "counter_hit": "",
                    "damage": ",".join(s["damage"] for s in steps[: index + 1]),
                    "displayed_input": step["input"] if index == 0 else f",{step['input']}",
                    "hit": step["hit"],
                    "id": prefix + command,
                    "name": "10 Hit Combo" if index == len(steps) - 1 else "",
                    "notes": step["notes"],
                    "number": "",
                    "range": "",
                    "recovery": "",
                    "section": chain["section"],
                    # only the opener's startup is a startup; later cells are
                    # the gap from the previous hit and read as ",i22" on cards
                    "startup": step["startup"] if index == 0 else (
                        f",{step['startup']}" if step["startup"] else ""
                    ),
                    "states": "",
                    "target": ",".join(s["target"] for s in steps[: index + 1]),
                }
            )
    return records


def unify_duplicate_names(moves: list[dict]) -> None:
    numbered = re.compile(r"^\(?\d+\)?$|^\d+(st|nd|rd|th) hit$", re.I)
    first: dict[str, str] = {}
    for move in moves:
        name = move["name"]
        if move["id"] not in first or (numbered.match(first[move["id"]]) and name and not numbered.match(name)):
            first[move["id"]] = name
    for move in moves:
        move["name"] = first[move["id"]]


def unglue_annotations(text: str) -> str:
    """Restore the word boundary Wavu's <sup> notes lose in textContent.

    `f,n,df+2<sup>HARD</sup>` reads back as `f,n,df+2HARD`, which the builder
    rejects (validate_combo_annotations). The July snapshots stored these as
    below; entries are normalized, `raw` stays verbatim.
    """
    text = re.sub(r"(?<=[\d\]])(HARD|Close range|Backturned)\b", r" (\1)", text)
    text = re.sub(r"(?<=[\d\]])(With heat)\b", r" \1", text)
    return re.sub(r"(?<=\S)\(on lower hit\)", " (on lower hit)", text)


def fold_minor_headings(raw_sections: list[dict]) -> list[dict]:
    """h2 and h3 are combo sections; an h4 belongs to the heading above it.

    Wavu's combo pages grew h4 sub-headings after July (Paul's "Resplat",
    Reina's "Heat available"). Splitting on them would turn one-line labels
    into page sections, so their routes join the nearest h2/h3 instead.
    """
    folded: list[dict] = []
    for raw in raw_sections:
        if raw.get("level") == "H4" and folded:
            folded[-1] = {**folded[-1], "dls": folded[-1]["dls"] + raw["dls"]}
        else:
            folded.append(raw)
    return folded


def convert_combos(raw_sections: list[dict]) -> list[dict]:
    sections = []
    for raw in fold_minor_headings(raw_sections):
        if not raw["dls"]:
            continue
        entries, parts = [], []
        for dl in raw["dls"]:
            starter = ""
            for tag, text in dl:
                text = clean(text)
                if not text:
                    continue
                parts.append(text)
                if tag == "dt":
                    starter = unglue_annotations(text)
                else:
                    entries.append({"route": unglue_annotations(text), "starter": starter})
        if entries:
            sections.append(
                {"entries": entries, "raw": " ".join(parts), "section": clean(raw["section"])}
            )
    return sections


def snapshot_documents(
    page: str,
    key: str,
    raw: dict,
    canonical: str,
    display_zh: str,
    tables: list[dict] | None = None,
):
    sys.path.insert(0, str(TOOLS))
    from season2_config import KNOWN_BIG_DAMAGE  # noqa: E402

    moves = convert_moves(page, raw["moves"], tables)
    allowed = KNOWN_BIG_DAMAGE.get(key, {})
    glued = [
        m["id"]
        for m in moves
        if GLUED.search(m["damage"].split("(")[0]) and allowed.get(m["id"]) != m["damage"]
    ]
    head = {
        "canonical_name": canonical,
        "character_key": key,
        "display_name_zh": display_zh,
        "schema_version": 1,
    }
    movelist = {**head, "moves": moves, "source_url": f"https://wavu.wiki/t/{page}_movelist"}
    combos = {
        **head,
        "sections": convert_combos(raw["combos2"]),
        "source_url": f"https://wavu.wiki/t/{page}_combos",
    }
    return movelist, combos, glued


def dump(document: dict) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def compare(key: str, movelist: dict, combos: dict) -> None:
    old = json.loads((SOURCE / f"{key}.json").read_text(encoding="utf-8"))
    old_moves = {m["id"]: m for m in old["moves"]}
    new_moves = {m["id"]: m for m in movelist["moves"]}
    print(f"{key}: old={len(old['moves'])} new={len(movelist['moves'])} "
          f"only_old={len(old_moves.keys() - new_moves.keys())} "
          f"only_new={len(new_moves.keys() - old_moves.keys())}")
    diffs = Counter()
    samples: dict[str, list] = {}
    for move_id in old_moves.keys() & new_moves.keys():
        for field in MOVE_FIELDS:
            if old_moves[move_id].get(field) != new_moves[move_id].get(field):
                diffs[field] += 1
                samples.setdefault(field, []).append(
                    (move_id, old_moves[move_id].get(field), new_moves[move_id].get(field))
                )
    for field, count in diffs.most_common():
        print(f"  {field}: {count}  e.g. {samples[field][:2]}")
    old_c = json.loads((SOURCE / f"{key}_combos.json").read_text(encoding="utf-8"))
    print("  combo sections old:", [(s["section"], len(s["entries"])) for s in old_c["sections"]])
    print("  combo sections new:", [(s["section"], len(s["entries"])) for s in combos["sections"]])


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("pairs", nargs="+", help="WavuPage=key[=Canonical Name=中文名]")
    parser.add_argument(
        "--tables",
        type=Path,
        help="ten-string wikitables ({page: [{section, rows}]}) from TK8.grabTens",
    )
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()
    raw = json.loads(args.raw.read_text(encoding="utf-8"))
    tables = json.loads(args.tables.read_text(encoding="utf-8")) if args.tables else {}
    status = 0
    for pair in args.pairs:
        page, key, *rest = pair.split("=")
        existing = SOURCE / f"{key}.json"
        if existing.is_file() and not rest:
            # a refresh keeps the names the snapshot already carries
            known = json.loads(existing.read_text(encoding="utf-8"))
            rest = [known["canonical_name"], known["display_name_zh"]]
        canonical = rest[0] if rest else page.replace("_", " ")
        display_zh = rest[1] if len(rest) > 1 else ""
        page_tables = tables.get(page)
        movelist, combos, glued = snapshot_documents(
            page, key, raw[page], canonical, display_zh,
            page_tables if isinstance(page_tables, list) else None,
        )
        if glued:
            print(f"{key}: unresolved glued damage tokens: {glued}")
            status = 1
        if args.compare:
            compare(key, movelist, combos)
            continue
        (SOURCE / f"{key}.json").write_text(dump(movelist), encoding="utf-8", newline="\n")
        (SOURCE / f"{key}_combos.json").write_text(dump(combos), encoding="utf-8", newline="\n")
        (TOOLS / f"wavu_{key}.txt").write_text(
            "".join(f'{m["command"]}|{m["startup"]}\n' for m in movelist["moves"]),
            encoding="utf-8",
            newline="\n",
        )
        print(f"{key}: {len(movelist['moves'])} moves, "
              f"{sum(len(s['entries']) for s in combos['sections'])} combo routes")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
