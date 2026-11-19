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


def convert_moves(page: str, raw_moves: list[dict]) -> list[dict]:
    prefix = f"{page}-"
    moves = []
    for raw in raw_moves:
        move_id = raw["id"]
        if not move_id.startswith(prefix):
            continue  # Generic- cards and other layout furniture
        command = move_id[len(prefix):]
        if not command:
            continue
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
    unify_duplicate_names(moves)
    for move in moves:
        move.pop("_damage_tail")
        move.pop("_target_tail")
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


def unify_duplicate_names(moves: list[dict]) -> None:
    numbered = re.compile(r"^\(?\d+\)?$|^\d+(st|nd|rd|th) hit$", re.I)
    first: dict[str, str] = {}
    for move in moves:
        name = move["name"]
        if move["id"] not in first or (numbered.match(first[move["id"]]) and name and not numbered.match(name)):
            first[move["id"]] = name
    for move in moves:
        move["name"] = first[move["id"]]


def convert_combos(raw_sections: list[dict]) -> list[dict]:
    sections = []
    for raw in raw_sections:
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
                    starter = text
                else:
                    entries.append({"route": text, "starter": starter})
        if entries:
            sections.append(
                {"entries": entries, "raw": " ".join(parts), "section": clean(raw["section"])}
            )
    return sections


def snapshot_documents(page: str, key: str, raw: dict, canonical: str, display_zh: str):
    moves = convert_moves(page, raw["moves"])
    glued = [m["id"] for m in moves if GLUED.search(m["damage"].split("(")[0])]
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
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()
    raw = json.loads(args.raw.read_text(encoding="utf-8"))
    status = 0
    for pair in args.pairs:
        page, key, *rest = pair.split("=")
        canonical = rest[0] if rest else page.replace("_", " ")
        display_zh = rest[1] if len(rest) > 1 else ""
        movelist, combos, glued = snapshot_documents(page, key, raw[page], canonical, display_zh)
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
