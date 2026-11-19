# -*- coding: utf-8 -*-
"""Carry Chinese names across a Wavu refresh; list what still needs a translator.

Run after `wavu_snapshot.py` has rewritten tools/source/{key}.json. The
committed (HEAD) snapshot is the "before", the working tree the "after":

    python tools/carry_translations.py jin king      # or --all
    python tools/carry_translations.py --all --write

For every move id in the new snapshot that {key}_zh.json does not name:

- ten-string steps (sections "10 String(s)" / "10 Hit Combo") are named by
  position, 十连技·三 ... 十连技·十 for the leaf -- the July names could not
  be trusted here (Claudio's were shifted by one by the header-row bug);
- an id whose command matches a translated one from before, once case, the
  FC./hFC. prefix and stray commas are normalised (FC.1 -> hFC.1,
  D+4 -> d+4, `1+4,,1` -> `1+4,1`), keeps that name;
- anything else is listed as MISSING, and the run fails until a person has
  written it into {key}_zh.json. Wavu's English name is printed beside it.

Ids that left the snapshot are dropped from the translation, and section
names the snapshot no longer uses are pruned. Without --write nothing is
written. 2026-11-19: this is the procedure the 36-character refresh used.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SOURCE = TOOLS / "source"
sys.path.insert(0, str(TOOLS))

from season2_config import CHARACTERS  # noqa: E402

TEN = re.compile(r"\b10[ -](?:strings?|hit)\b", re.I)
NUMERALS = "一二三四五六七八九十"


def normalise(command: str) -> str:
    text = command.replace("​", "").casefold()
    text = re.sub(r"^hfc\.", "fc.", text)
    return re.sub(r",+", ",", text).strip(",")


def head_snapshot(key: str) -> dict | None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"HEAD:tools/source/{key}.json"],
        capture_output=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout) if result.returncode == 0 else None


def ten_string_step(move: dict, moves: list[dict]) -> int:
    """Position of a ten-string record in its chain (1-based)."""
    commands = {m["command"] for m in moves if TEN.search(m["section"])}
    command = move["command"]
    return sum(1 for other in commands if command == other or command.startswith(other + ","))


def carry(key: str) -> tuple[dict, list[tuple[str, str, str]], int]:
    source = json.loads((SOURCE / f"{key}.json").read_text(encoding="utf-8"))
    translation = json.loads((SOURCE / f"{key}_zh.json").read_text(encoding="utf-8"))
    names = translation["move_names"]
    before = head_snapshot(key) or {"moves": []}
    by_command = {}
    for move in before["moves"]:
        if move["id"] in names:
            by_command.setdefault(normalise(move["command"]), names[move["id"]])

    carried: dict[str, str] = {}
    missing: list[tuple[str, str, str]] = []
    for move in source["moves"]:
        move_id = move["id"]
        if move_id in carried:
            continue
        if move_id in names:
            carried[move_id] = names[move_id]
        elif TEN.search(move["section"]):
            if move.get("name", "").casefold() == "10 hit combo":
                carried[move_id] = "十连技·十"
            else:
                step = min(ten_string_step(move, source["moves"]), 10)
                carried[move_id] = f"十连技·{NUMERALS[step - 1]}"
        elif normalise(move["command"]) in by_command:
            carried[move_id] = by_command[normalise(move["command"])]
        else:
            missing.append((move_id, move.get("name", ""), move["section"]))
    dropped = len(set(names) - set(carried))
    sections = list(dict.fromkeys(m["section"] for m in source["moves"]))
    translation["move_names"] = carried
    translation["section_names"] = {
        s: translation["section_names"][s] for s in sections if s in translation["section_names"]
    }
    unnamed_sections = [s for s in sections if s not in translation["section_names"]]
    missing += [(f"section:{s}", s, "") for s in unnamed_sections]
    return translation, missing, dropped


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keys", nargs="*")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    keys = list(CHARACTERS) if args.all else args.keys
    if not keys:
        parser.error("name characters or pass --all")

    status = 0
    for key in keys:
        translation, missing, dropped = carry(key)
        if args.write:
            (SOURCE / f"{key}_zh.json").write_text(
                json.dumps(translation, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        if missing or dropped:
            print(f"{key}: {len(missing)} need a name, {dropped} dropped")
        for move_id, english, section in missing:
            print(f"    MISSING {move_id}  ({english or 'unnamed on Wavu'}; {section})")
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
