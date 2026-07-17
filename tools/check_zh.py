# -*- coding: utf-8 -*-
"""Standalone translation-contract checker for one character.

Validates {key}_zh.json against {key}.json BEFORE the character is registered
in season2_config: metadata, full move-id coverage, pure-Chinese labels,
command-prefix coverage in stance_names, and the button-map guarantee (every
command containing buttons 1-4 must render graphical notation).

Usage: python tools/check_zh.py <key>
Exit code 0 = contract satisfied.
"""
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from build_season2 import render_graphical_command, load_json  # noqa: E402
from season2_config import (  # noqa: E402
    COMMON_COMMAND_ALIASES,
    COMMON_PREFIXES,
    LATIN,
)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    key = sys.argv[1]
    source = load_json(TOOLS / "source" / f"{key}.json")
    translation = load_json(TOOLS / "source" / f"{key}_zh.json")
    problems = []

    if translation.get("character_key") != key:
        problems.append(f"character_key: {translation.get('character_key')}")
    if translation.get("display_name_zh") != source["display_name_zh"]:
        problems.append(
            f"display_name_zh mismatch: {translation.get('display_name_zh')}"
            f" != {source['display_name_zh']}"
        )

    source_ids = {m["id"] for m in source["moves"]}
    translated = translation.get("move_names", {})
    missing = sorted(source_ids - set(translated))
    extra = sorted(set(translated) - source_ids)
    if missing:
        problems.append(f"missing move ids ({len(missing)}): {missing[:10]}")
    if extra:
        problems.append(f"extra move ids ({len(extra)}): {extra[:10]}")

    sections = {m["section"] for m in source["moves"]}
    section_names = translation.get("section_names", {})
    missing_sections = sorted(sections - set(section_names))
    extra_sections = sorted(set(section_names) - sections)
    if missing_sections:
        problems.append(f"missing sections: {missing_sections}")
    if extra_sections:
        problems.append(f"extra sections: {extra_sections}")

    labels = {
        **{f"move:{k}": v for k, v in translated.items()},
        **{f"section:{k}": v for k, v in section_names.items()},
        **{f"stance:{k}": v for k, v in translation.get("stance_names", {}).items()},
    }
    for label_id, label in labels.items():
        if not str(label).strip():
            problems.append(f"empty label: {label_id}")
        elif LATIN.search(str(label)):
            problems.append(f"latin in label: {label_id} = {label}")

    # every dotted command prefix must resolve to a state capsule
    stance_names = translation.get("stance_names", {})
    known = set(COMMON_PREFIXES) | {
        (code if code.endswith(".") else code + ".") for code in stance_names
    }
    unknown_prefixes = set()
    for move in source["moves"]:
        command = move["command"].replace("​", "")
        command = COMMON_COMMAND_ALIASES.get(command.casefold(), command)
        for match in re.finditer(r"(?:^|[,.:])([A-Za-z_()0-9]{2,24}\.)", command):
            token = match.group(1)
            if token not in known and token.lower() not in {
                k.lower() for k in known
            }:
                unknown_prefixes.add(token)
    if unknown_prefixes:
        problems.append(
            f"command prefixes missing from stance_names: {sorted(unknown_prefixes)}"
        )

    # button-map guarantee; sequences beyond the 6-grid cap that DO render
    # without the cap are intentional design fallbacks, not translation gaps
    fallbacks, design = [], []
    for move in source["moves"]:
        command = move["command"]
        if not re.search(r"[1-4]", command):
            continue
        folded = move["section"].casefold()
        cap = None if ("10 string" in folded or "10 hit" in folded) else 6
        if render_graphical_command(command, "tk-x", stance_names, cap) is None:
            if cap is not None and render_graphical_command(
                command, "tk-x", stance_names, None
            ) is not None:
                design.append(f"{move['id']}: {command}")
            else:
                fallbacks.append(f"{move['id']}: {command}")
    if design:
        print(f"[{key}] note: {len(design)} design fallbacks (>6 grids): "
              f"{design[:6]}")
    if fallbacks:
        problems.append(
            f"button-map fallbacks ({len(fallbacks)}): {fallbacks[:12]}"
        )

    if problems:
        print(f"[{key}] FAILED:")
        for problem in problems:
            print("  -", problem)
        return 1
    print(f"[{key}] OK: {len(translated)} names, {len(section_names)} sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
