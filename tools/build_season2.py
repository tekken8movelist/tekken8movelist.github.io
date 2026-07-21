# -*- coding: utf-8 -*-
"""Build the generated Tekken 8 Chinese movelist pages.

The checked-in JSON snapshots are the reproducible source layer. This builder
does not access the network and writes byte-stable, self-contained HTML files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict, defaultdict
from html import escape
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SITE = ROOT / "docs"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from pipeline import first_step, parse_cmd  # noqa: E402
from season2_config import (  # noqa: E402
    CHARACTERS,
    COMBO_SECTION_NAMES,
    COMMON_COMMAND_ALIASES,
    COMMON_PREFIXES,
    COMMON_STATES,
    GLUED_COMBO_ANNOTATION,
    KNOWN_AGGREGATE_DAMAGE,
    KNOWN_BIG_DAMAGE,
    LATIN,
    PLACEHOLDER_COMBO,
    TARGET_TITLES,
)


PAGE_CSS = (TOOLS / "season2_page.css").read_text(encoding="utf-8")
PAGE_SCRIPT = "\n" + (TOOLS / "season2_page.js").read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def write_if_changed(path: Path, content: str) -> None:
    try:
        if path.read_text(encoding="utf-8") == content:
            return
    except (OSError, UnicodeError):
        pass
    path.write_text(content, encoding="utf-8", newline="\n")


def first_impact(value: str) -> str | None:
    tokens = [token for token in re.split(r"[ ,]+", value or "") if token]
    if not tokens:
        return None
    impact = tokens[0].lstrip(".")
    return f"i{impact}" if impact[:1].isdigit() else impact


class StartupResolver:
    def __init__(self, moves: list[dict]):
        self.exact = defaultdict(list)
        self.folded = defaultdict(list)
        for move in moves:
            command = move["command"]
            startup = move.get("startup", "").strip()
            self.exact[command].append(startup)
            self.folded[command.casefold()].append(startup)

    def resolve(self, command: str, own_startup: str = "") -> str:
        own_startup = own_startup.strip()
        if own_startup.startswith("i"):
            return first_impact(own_startup) or "—"
        candidates = [first_step(command), command]
        seen = set()
        for candidate in candidates:
            if candidate in seen:
                continue
            seen.add(candidate)
            values = self.exact.get(candidate)
            if values is None:
                values = self.folded.get(candidate.casefold(), [])
            for value in values:
                impact = first_impact(value)
                if impact:
                    return impact
        return "—"


def validate_translation(source: dict, translation: dict) -> None:
    move_ids = {move["id"] for move in source["moves"]}
    translated_ids = set(translation.get("move_names", {}))
    if move_ids != translated_ids:
        missing = sorted(move_ids - translated_ids)
        extra = sorted(translated_ids - move_ids)
        raise ValueError(f"translation ID mismatch: missing={missing}, extra={extra}")
    sections = {move["section"] for move in source["moves"]}
    translated_sections = set(translation.get("section_names", {}))
    if sections != translated_sections:
        missing = sorted(sections - translated_sections)
        extra = sorted(translated_sections - sections)
        raise ValueError(f"section mismatch: missing={missing}, extra={extra}")
    bad_names = {
        move_id: name
        for move_id, name in translation["move_names"].items()
        if not name.strip() or LATIN.search(name)
    }
    if bad_names:
        raise ValueError(f"non-Chinese move names: {bad_names}")


def validate_metadata(key: str, config: dict, documents: list[dict]) -> None:
    for document in documents:
        if document.get("character_key") != key:
            raise ValueError(
                f"character key mismatch: expected={key}, "
                f"actual={document.get('character_key')}"
            )
        if document.get("display_name_zh") != config["display"]:
            raise ValueError(
                f"display name mismatch for {key}: "
                f"expected={config['display']}, "
                f"actual={document.get('display_name_zh')}"
            )
        canonical = document.get("canonical_name")
        if canonical is not None and canonical != config["canonical"]:
            raise ValueError(
                f"canonical name mismatch for {key}: "
                f"expected={config['canonical']}, actual={canonical}"
            )


def validate_combo_annotations(combos: dict) -> None:
    for group in combos.get("sections", []):
        for entry in group.get("entries", []):
            for field in ("starter", "route"):
                value = entry.get(field, "")
                if GLUED_COMBO_ANNOTATION.search(value):
                    raise ValueError(
                        f"glued combo annotation in {field}: {value}"
                    )


def validate_damage_fields(key: str, source: dict) -> None:
    mismatches = set()
    big_allowed = KNOWN_BIG_DAMAGE.get(key, {})
    for record_id, move in record_ids(source["moves"]):
        damage_value = move.get("damage", "")
        if re.search(r"\d{3,}", damage_value):
            if big_allowed.get(move["id"]) != damage_value:
                raise ValueError(
                    f"joined damage token for {record_id}: {damage_value}"
                )
        targets = [
            part.strip()
            for part in move.get("target", "").split(",")
            if part.strip()
        ]
        damage = [
            part.strip()
            for part in damage_value.lstrip(",").split(",")
            if part.strip()
        ]
        if targets and damage and len(targets) != len(damage):
            mismatches.add(record_id)
    expected = KNOWN_AGGREGATE_DAMAGE[key]
    if mismatches != expected:
        raise ValueError(
            f"target/damage mismatch for {key}: "
            f"expected={sorted(expected)}, actual={sorted(mismatches)}"
        )


def state_label(value: str) -> str:
    if value.endswith(("中", "时", "后", "姿势")):
        return value
    return value + "中"


def strip_state_prefixes(
    command: str, stance_names: dict[str, str]
) -> tuple[str, list[str], list[tuple[str, str]]]:
    remaining = command.replace("\u200b", "")
    labels = []
    prefixes = OrderedDict(COMMON_PREFIXES)
    for code, name in stance_names.items():
        token = code if code.endswith(".") else code + "."
        prefixes[token] = state_label(name)
    ordered = sorted(prefixes.items(), key=lambda item: len(item[0]), reverse=True)
    while remaining:
        for token, label in ordered:
            if remaining.startswith(token):
                labels.append(label)
                remaining = remaining[len(token) :]
                break
        else:
            break

    return remaining, labels, ordered


def text_command(command: str, stance_names: dict[str, str]) -> str:
    remaining, labels, ordered = strip_state_prefixes(command, stance_names)
    for token, label in ordered:
        remaining = remaining.replace("," + token, "," + label + " ")
    return " ".join(labels + [remaining])


def expand_command(command: str, stance_names: dict[str, str]) -> tuple[str, list[str]]:
    # wavu case quirks: "(back_to_wall)b,b,ub" / lowercase stance codes
    command = re.sub(r"^\(back_to_wall\)\.?", "(Back_to_wall).", command, flags=re.I)
    for code in sorted(stance_names, key=len, reverse=True):
        if code.isupper() and len(code) >= 2 and "(" not in code:
            command = re.sub(
                rf"(?<![A-Za-z]){code}(?=[.~,:]|$)", code, command, flags=re.I
            )
    command = COMMON_COMMAND_ALIASES.get(command.casefold(), command)
    remaining, labels, ordered = strip_state_prefixes(command, stance_names)

    for token, label in ordered:
        remaining = remaining.replace("," + token, "," + label)
        remaining = remaining.replace(":" + token, ":" + label + " ")

    parry_label = state_label(stance_names.get("P", "防反成功后"))
    remaining = re.sub(r"(?:(?<=,)|^)P(?=,|$|_\()", parry_label, remaining)
    # parry follow-up prefixes: "P.2" / "P:b+2" / "b+1+3,P.4" / "ub+1.P.4"
    remaining = re.sub(
        r"(?:(?<=^)|(?<=,)|(?<=\.))P[.:]\s*", parry_label + " ", remaining
    )
    # hit-level variants: "_(High)" / "_(Low)" trailing the command
    remaining = re.sub(r"_\(High\)$", " （上段）", remaining, flags=re.I)
    remaining = re.sub(r"_\(Low\)$", " （下段）", remaining, flags=re.I)
    # wavu notation quirks: lowercase ss / BT+n / mid-string lowercase
    # neutral / charge-level "*(n)"
    remaining = re.sub(r"^ss(?=[1-4])", "SS+", remaining)
    remaining = re.sub(
        r"^BT\+?(?=[1-4])",
        state_label(stance_names.get("BT", "背身时")) + " ",
        remaining,
    )
    # lowercase cd at start: stance "CD+1" (jin) or crouch dash otherwise
    if "CD" in stance_names:
        remaining = re.sub(r"^cd(?=[.+])", "CD", remaining)
    remaining = re.sub(
        r"^CD\+(?=[1-4])",
        state_label(stance_names.get("CD", "蹲步中")) + " ",
        remaining,
    )
    remaining = re.sub(r"(?<=,)n(?=[+,]|$)", "N", remaining)
    remaining = re.sub(r"(?<=[~,])n$", "N", remaining)
    remaining = re.sub(r"\*\((\d+)\)", lambda m: f"* (蓄{m.group(1)}段)", remaining)

    remaining = re.sub(r"^ws\+?(?=[1-4+,]|$)", "WS+", remaining, flags=re.I)
    remaining = re.sub(
        r"^wr\+?(?![A-Za-z])",
        state_label(stance_names.get("wr", "奔跑中")),
        remaining,
        flags=re.I,
    )
    remaining = re.sub(r"(?<=,)n(?=,)", "N", remaining)
    remaining = re.sub(r"^n(?=,)", "N", remaining)
    for motion, sequence in (
        ("hcf", "b,d/b,d,d/f,f"),
        ("hcb", "f,d/f,d,d/b,b"),
        ("qcb", "d,d/b,b"),
    ):
        remaining = re.sub(rf"\b{motion}\b", sequence, remaining, flags=re.I)
    # mid-string stance transitions: "f+4~RFS.3" / "df+2~DCK~db" / ">LFS.4"
    mid = [
        (code if code.endswith(".") else code + ".", state_label(name))
        for code, name in stance_names.items()
    ]
    mid += list(COMMON_PREFIXES.items())
    for token, label in sorted(mid, key=lambda item: len(item[0]), reverse=True):
        remaining = re.sub(
            rf"(?<=[~,>]){re.escape(token)}", label + " ", remaining
        )
        code = token[:-1]
        if len(code) >= 3 and code.isalnum() and code.isupper():
            # bare stance code mid-string: "~DCK~db" / ",ORB1:2"
            remaining = re.sub(
                rf"(?<=[~,>]){re.escape(code)}(?=[~,>]|$)",
                label + " ",
                remaining,
            )
            remaining = re.sub(
                rf"(?:^|(?<=[~,>])){re.escape(code)}(?=[1-4])",
                label + " ",
                remaining,
            )
    # unmapped CD is crouch dash (kazuya / devil_jin combos): "CD.3" / "CD~WS3"
    if "CD" not in stance_names:
        remaining = re.sub(r"(?:^|(?<=[~,>\s]))CD[.:]?(?=\s*[1-4])", "qcf+", remaining)
        remaining = re.sub(r"(?:^|(?<=[~,>\s]))CD(?=~)", "qcf+", remaining)
        remaining = re.sub(r"(?:^|(?<=[~,>\s]))cd[.+]?(?=[1-4])", "qcf+", remaining)
    # "bf+2" / "bb" are b,f / b,b runs; SSR/SSL are sidestep capsules;
    # "u,f,n4" style lowercase neutral before a button
    remaining = re.sub(r"^bf(?=[+1-4])", "b,f", remaining)
    remaining = re.sub(r"^bb$", "b,b", remaining)
    remaining = re.sub(r"(?<![A-Za-z])SSR\.?(?=[1-4,~>\s]|$)", "横移右 ", remaining, flags=re.I)
    remaining = re.sub(r"(?<![A-Za-z])SSL\.?(?=[1-4,~>\s]|$)", "横移左 ", remaining, flags=re.I)
    remaining = re.sub(r"(?<=,)n(?=[1-4])", "N", remaining)
    # lone stance code with nothing else ("SNK" / "BOK.n" leftover "n")
    lone = {code: state_label(name) for code, name in stance_names.items()}
    if remaining in lone:
        remaining = lone[remaining]
    remaining = re.sub(r"(?<![A-Za-z])n$", "N", remaining)
    remaining = re.sub(
        r"(?<![A-Za-z])([dDuU])([fFbB])(?=[+,0-9#:]|$)",
        lambda match: match.group(1) + "/" + match.group(2),
        remaining,
    )
    return " ".join(labels + [remaining]), labels


def render_graphical_command(
    command: str,
    css_class: str,
    stance_names: dict[str, str],
    cap: int | None = 6,
    cram_at: int = 5,
    weight_at: float = 4.8,
    cram2_at: float = 5.8,
) -> str | None:
    if not command:
        return None
    if re.search(r"[<>&]", command):
        return None
    expanded, labels = expand_command(command, stance_names)
    states = list(dict.fromkeys(COMMON_STATES + [state_label(v) for v in stance_names.values()] + labels))
    graphical = parse_cmd(expanded, {"states": states}, cap=cap)
    if graphical is None:
        return None
    graphical = graphical.replace(
        'class="tk-in tk-sm"', f'class="tk-in tk-sm {css_class}"', 1
    )
    # long sequences get a compact tier so fixed-height table cells fit.
    # tier choice approximates rendered width (px @11px base ≈ 43 × weight):
    # a 2x2 button grid is ~2x as wide as an arrow, a state capsule ~2 grids
    grids = graphical.count('class="tk-b"')
    arrows = graphical.count('class="tk-dir') + graphical.count('class="tk-n"')
    capsules = graphical.count('class="tk-state"')
    weight = grids + 0.5 * arrows + 2.0 * capsules
    if grids >= 6 or weight >= cram2_at:
        tier = "tk-cram tk-cram2"
    elif grids >= cram_at or weight >= weight_at:
        tier = "tk-cram"
    else:
        tier = ""
    if tier:
        graphical = graphical.replace(
            'class="tk-in tk-sm', f'class="tk-in tk-sm {tier}', 1
        )
    return graphical


def render_command(
    command: str,
    css_class: str,
    stance_names: dict[str, str],
    cap: int | None = 6,
    cram_at: int = 5,
    weight_at: float = 4.8,
    cram2_at: float = 5.8,
) -> str:
    if not command:
        return "—"
    graphical = render_graphical_command(
        command, css_class, stance_names, cap, cram_at, weight_at, cram2_at
    )
    if graphical is None:
        return escape(command.replace("\u200b", ""))
    plain = escape(command.replace("\u200b", ""))
    return (
        f'<span class="cmd-gfx" aria-hidden="true">{graphical}</span>'
        f'<span class="cmd-txt">{plain}</span>'
        f'<span class="sr-only cmd-a11y">{plain}</span>'
    )


def target_descriptor(token: str) -> tuple[str, str, str]:
    lowered = token.lower()
    if lowered.startswith("sm"):
        css_class, label = "sp", "特中"
    elif lowered.startswith("sl"):
        css_class, label = "sp", "特下"
    elif lowered.startswith("h"):
        css_class, label = "hi", "上"
    elif lowered.startswith("m"):
        css_class, label = "md", "中"
    elif lowered.startswith("l"):
        css_class, label = "lo", "下"
    elif lowered.startswith("t"):
        css_class, label = "sp", "投"
    else:
        css_class, label = "sp", "特"
    title = TARGET_TITLES.get(token, TARGET_TITLES.get(lowered, token))
    if token.isupper() and token not in TARGET_TITLES and lowered in TARGET_TITLES:
        title += "（倒地）"
    return css_class, label, title


def translate_target(target: str) -> str:
    titles = [
        target_descriptor(part.strip())[2]
        for part in target.split(",")
        if part.strip()
    ]
    return "、".join(titles) or "—"


def render_target(target: str) -> str:
    if not target:
        return "—"
    rendered = []
    for part in target.split(","):
        token = part.strip()
        if not token:
            continue
        css_class, label, title = target_descriptor(token)
        title_attr = (
            f' title="{escape(title, quote=True)}"' if title != label else ""
        )
        rendered.append(
            f'<span class="{css_class}"{title_attr}>{escape(label)}</span>'
        )
    return "".join(rendered) or "—"


def throw_direction(move: dict) -> str:
    section = move.get("section", "").lower()
    command = move.get("command", "").lower()
    notes = move.get("notes", "").lower()
    targets = {
        token.strip().lower()
        for token in move.get("target", "").split(",")
        if token.strip()
    }
    if "t(w)" in targets or command.startswith("wall."):
        return "墙边"
    if "t(a)" in targets:
        return "空中"
    if "th(g)" in targets:
        return "地面"
    if "air" in section or "airborne" in command:
        return "空中"
    if "ground" in section or "grounded" in command:
        return "地面"
    if "crouch" in section:
        return "蹲姿"
    if "back" in command or "背后" in notes:
        return "背后"
    if "left" in command:
        return "左侧"
    if "right" in command:
        return "右侧"
    return "正面"


def throw_break(move: dict) -> str:
    notes = move.get("notes", "")
    if re.search(
        r"(?:cannot throw break|cannot be broken|unbreakable|"
        r"throw break:?\s*none)",
        notes,
        re.I,
    ):
        return "不可挣脱"
    match = re.search(
        r"Throw break:?\s+(1\+2|1\s+or\s+2|2\s+or\s+1|1|2)(?=\s|$)",
        notes,
        re.I,
    )
    if match:
        return match.group(1).replace(" or ", "或")
    match = re.search(
        r"(1\+2|1\s+or\s+2|2\s+or\s+1|1|2)\s+(?:throw\s+)?break\b",
        notes,
        re.I,
    )
    if match:
        return match.group(1).replace(" or ", "或")
    if re.search(r"Throw break .*opposite", notes, re.I):
        return "首/末异键"
    return "—（Wavu 未注明）"


def render_move_target(move: dict) -> str:
    rendered = render_target(move.get("target", ""))
    has_throw_target = any(
        token.strip().lower().startswith("t")
        for token in move.get("target", "").split(",")
    )
    if not has_throw_target:
        return rendered
    break_value = throw_break(move)
    if break_value == "—（Wavu 未注明）":
        return rendered
    break_label = (
        break_value
        if break_value == "不可挣脱"
        else f"挣脱 {break_value}"
    )
    return rendered + f'<span class="throw-break">{escape(break_label)}</span>'


def record_ids(moves: list[dict]) -> list[tuple[str, dict]]:
    occurrences = defaultdict(int)
    records = []
    for move in moves:
        move_id = move["id"]
        occurrences[move_id] += 1
        occurrence = occurrences[move_id]
        record_id = move_id if occurrence == 1 else f"{move_id}#{occurrence}"
        records.append((record_id, move))
    return records


def render_damage_cell(value: str) -> str:
    raw = (value or "").lstrip(",") or "—"
    compact = re.sub(r"\s+", "", raw)
    title = f' title="{escape(raw, quote=True)}"' if compact != raw else ""
    return f'<td class="dmg"{title}>{escape(compact)}</td>'


def render_startup_cell(startup: str) -> str:
    display = re.split(r"[(]", startup, maxsplit=1)[0].strip()
    if display != startup:
        return (
            f'<td class="fr" title="{escape(startup, quote=True)}">'
            f"{escape(display)}</td>"
        )
    return f'<td class="fr">{escape(startup)}</td>'


def render_move_row(
    record_id: str,
    move: dict,
    name: str,
    startup: str,
    kind: str,
    config: dict,
    stance_names: dict[str, str],
    command_cap: int | None = 6,
) -> str:
    attrs = (
        f'data-record-id="{escape(record_id, quote=True)}" '
        f'data-move-id="{escape(move["id"], quote=True)}" '
        f'data-command="{escape(move["command"], quote=True)}" '
        f'data-startup="{escape(startup, quote=True)}" data-kind="{kind}"'
    )
    cells = [
        f'<td class="name">{escape(name)}</td>',
        f'<td class="cmd">{render_command(move["command"], config["css_class"], stance_names, command_cap, 5, 4.0 if kind == "throw" else 4.8)}</td>',
        render_startup_cell(startup),
    ]
    damage_cell = render_damage_cell(move.get("damage", ""))
    if kind == "throw":
        break_value = throw_break(move)
        break_cell = (
            '<td class="break" title="Wavu 未注明挣脱键">—</td>'
            if break_value == "—（Wavu 未注明）"
            else f'<td class="break">{break_value}</td>'
        )
        cells.extend(
            [
                f'<td class="direction">{throw_direction(move)}</td>',
                damage_cell,
                break_cell,
            ]
        )
    else:
        cells.extend(
            [
                damage_cell,
                f'<td class="rng">{render_move_target(move)}</td>',
            ]
        )
    return f"<tr {attrs}>" + "".join(cells) + "</tr>"


def render_table(
    records: list[tuple[str, dict]],
    translation: dict,
    resolver: StartupResolver,
    config: dict,
    kind: str,
    command_cap: int | None = 6,
) -> str:
    table_class = "throw-table" if kind == "throw" else "move-table"
    if kind == "throw":
        header = "<tr><th>招式</th><th>指令</th><th>发生</th><th>方向</th><th>伤害</th><th>挣脱</th></tr>"
        columns = (17, 34, 9, 8, 16, 15)
    else:
        header = "<tr><th>招式</th><th>指令</th><th>发生</th><th>伤害</th><th>判定</th></tr>"
        columns = (24, 37, 9, 15, 15)
    rows = []
    for record_id, move in records:
        rows.append(
            render_move_row(
                record_id,
                move,
                translation["move_names"][move["id"]],
                resolver.resolve(move["command"], move.get("startup", "")),
                kind,
                config,
                translation.get("stance_names", {}),
                command_cap,
            )
        )
    colgroup = "<colgroup>" + "".join(
        f'<col style="width:{width}%">' for width in columns
    ) + "</colgroup>"
    return (
        f'<table class="{table_class}">{colgroup}<thead>{header}</thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def render_split_tables(
    records: list[tuple[str, dict]],
    translation: dict,
    resolver: StartupResolver,
    config: dict,
    kind: str,
    command_cap: int | None = 6,
) -> str:
    midpoint = (len(records) + 1) // 2
    halves = (records[:midpoint], records[midpoint:])
    return '<div class="cols2">' + "".join(
        render_table(half, translation, resolver, config, kind, command_cap)
        for half in halves
        if half
    ) + "</div>"


def section_code(section: str) -> str:
    return section.split(" (", 1)[0].upper()


def render_stance_matrix(
    stance_groups: OrderedDict,
    translation: dict,
    resolver: StartupResolver,
    config: dict,
) -> str:
    cells = []
    for index, (section, records) in enumerate(stance_groups.items(), start=1):
        cells.append(
            f'<td class="ltc stance-cell" id="stance-{index}">'
            f'<h2>{escape(translation["section_names"][section])}'
            f' <span class="en">{escape(section_code(section))}</span></h2>'
            f'{render_table(records, translation, resolver, config, "move", 6)}</td>'
        )
    rows = []
    for index in range(0, len(cells), 2):
        pair = cells[index : index + 2]
        if len(pair) == 1:
            pair[0] = pair[0].replace('<td class="ltc stance-cell"', '<td colspan="2" class="ltc stance-cell"', 1)
        rows.append("<tr>" + "".join(pair) + "</tr>")
    return '<table class="lt"><tbody>' + "".join(rows) + "</tbody></table>"


def partition_records(
    records: list[tuple[str, dict]],
    config: dict,
) -> tuple[
    list[tuple[str, dict]],
    list[tuple[str, dict]],
    OrderedDict,
    list[tuple[str, dict]],
    list[tuple[str, dict]],
]:
    throws = []
    attacks = []
    stances = OrderedDict()
    heat = []
    ten_strings = []
    known_sections = {move["section"] for _, move in records}
    configured_sections = set(config["stance_sections"]) | set(
        config["throw_sections"]
    )
    missing_sections = configured_sections - known_sections
    if missing_sections:
        raise ValueError(f"configured sections missing from source: {sorted(missing_sections)}")

    for record in records:
        move = record[1]
        section = move["section"]
        folded = section.casefold()
        if folded == "heat":
            heat.append(record)
        elif "10 string" in folded or "10 hit" in folded:
            ten_strings.append(record)
        elif section in config["stance_sections"]:
            stances.setdefault(section, []).append(record)
        elif section in config["throw_sections"]:
            throws.append(record)
        else:
            attacks.append(record)
    partitioned_count = (
        len(throws)
        + len(attacks)
        + sum(len(group) for group in stances.values())
        + len(heat)
        + len(ten_strings)
    )
    if partitioned_count != len(records):
        raise ValueError(
            f"record partition mismatch: expected={len(records)}, actual={partitioned_count}"
        )
    return throws, attacks, stances, heat, ten_strings


def valid_combo_groups(combos: dict) -> list[tuple[str, list[tuple[str, str]]]]:
    groups = []
    for group in combos.get("sections", []):
        section = group.get("section", "")
        rows = []
        for entry in group.get("entries", []):
            starter = entry.get("starter", "").strip()
            route = entry.get("route", "").strip()
            if not route or PLACEHOLDER_COMBO.search(route):
                continue
            rows.append((starter, route))
        if rows:
            groups.append((section, rows))
    return groups


def valid_combo_entries(combos: dict) -> list[tuple[str, str, str]]:
    return [
        (section, starter, route)
        for section, rows in valid_combo_groups(combos)
        for starter, route in rows
    ]


# Residual English in combo routes/starters -> Chinese. Applied in order;
# longer and more specific phrases must precede their substrings.
COMBO_LITERAL_PHRASES = [
    (r"the last hit can sometimes be avoided with B getup", "最后一击可能被 B 受身躲开"),
    (r"\(works on ([^)]+)\)", r"（仅对 \1 有效）"),
    (r"presumably works only on ([^)]+)\)", r"推测仅对 \1 有效）"),
    (r"super hard", "极难"),
    (r"\bcan use\b", "可用"),
    (r"\bto catch\b", "抓"),
    (r"(?:it )?will not hit grounded\b", "打不中倒地"),
    (r"\bbut\b", "但"),
    (r"does not work on small characters", "对小体型角色无效"),
    (r"may not work on small characters", "对小体型角色可能无效"),
    (r"does not work off-axis", "偏轴时无效"),
    (r"works on Alisa,?\s*bigs?", "仅对阿丽莎/大体型有效"),
    (r"only the second hit should connect", "只需第二击命中"),
    (r"Kuma/Panda/Raven only", "仅熊/熊猫/雷文"),
    (r"Bears and Jack only", "仅熊类/杰克"),
    (r"challenge combo", "挑战连招"),
    (r"\bKND\b", "击倒"),
    (r"\bCorner Carry\b", "板边墙运"),
    (r"\bworse\b", "较差"),
    (r"\bMore\b", "更多"),
    (r"\bPKB\b", "窥视架"),
    (r"\bTransition\b", "过渡"),
    (r"\bReliable\b", "稳定"),
    (r"\bDoes no\b", "不造成"),
    (r"\bbreaks floors\b", "破地板"),
    (r"\bless\b", "较少"),
    (r"(?i)\bmax\b", "最大"),
    (r"\bon bigs\b", "对大体型"),
    (r"\bdemo(?=[A-Z])", "演示："),
    (r"\bdemo\b", "演示"),
    (r"'s\b", "的"),
    (r"\bspreadsheet\b", "表"),
    (r"\bfrom\b", "来自"),
    (r"if you do hold B\.", "按住 B 时"),
    (r"if you dont hold B\.", "不按 B 时"),
    (r"(?i)\bstaple\b", "常用"),
    (r"(?i)\bleft\b", "左"),
    (r"(?i)\bright\b", "右"),
    (r"\bcannot\b", "无法"),
    (r"\binterrupt\b", "打断"),
    (r"\bBnB\b", "基础连"),
    (r"\bclean\b", "净命中"),
    (r"\bsoft\b", "软"),
    (r"\bcannot interrupt\b", "无法打断"),
    (r"\bas the\b", "当"),
    (r"\bnss\b", "无刀之极"),
    (r"\bHeatsmash\b", "热能猛击"),
    (r"(?i)\bwall break\b", "破墙"),
    (r"(?i)\bhard\b", "难"),
    (r"(?i)\beasy\b", "简单"),
    (r"(?i)\bclose range\b", "近身"),
    (r"(?i)\bclose\b", "近身"),
    (r"(?i)\bfar\b", "远身"),
    (r"(?i)\bsuccessful\b", "成功"),
    (r"(?i)\bfast\b", "快"),
    (r"(?i)\badvanced\b", "进阶"),
    (r"(?i)\bconfirm\b", "确认"),
    (r"\bGoes into\b", "进入"),
    (r"\bOK\b", "可"),
    (r"\bopp\.", "对手"),
    (r"\bMax\b", "最大"),
    (r"\bBurst\b", "爆发"),
    (r"\bOR\b", "或"),
    (r"\bFloorblast\b", "地板爆破"),
    (r"\bbleft\b", "左"),
    (r"\bright\b", "右"),
    (r"2nd hit", "第二击"),
    (r"1st hit", "第一击"),
    (r"first hit whiff", "第一击挥空"),
    (r"beats side", "克制侧"),
    (r"back to 墙", "贴墙"),
    (r"at the 墙", "在墙边"),
    (r"one prior 墙 hit", "墙前已命中一击"),
    (r"no prior 墙 hit", "墙前未命中"),
    (r"\bblossom\b", "花开"),
    (r"(\d+)\s*hits?\b", r"\1击"),
    (r"\braw\b", "直接"),
    (r"\bfiller\b", "填充"),
    (r"\bcombo\b", "连招"),
    (r"\bconcept\b", "概念"),
    (r"\bhazards\b", "场地机关"),
    (r"\brelated\b", "相关"),
    (r"\bon 防御\b", "被防时"),
    (r"\bon 蹲姿\b", "对蹲姿"),
    (r"\bHigh 防反", "上段防反"),
    (r"\bLow 防反", "下段防反"),
    (r"\bSabaki\b", "当身"),
    (r"pre-T!", "龙卷前"),
    (r"\bSNKc\b", "潜步取消"),
    (r"\bRA\b", "怒气技"),
    (r"\bHE\b", "热能启动"),
    (r"combo showcase by|credit to", "出处："),
    (r"without JFFEs?", "不带 JFFE"),
    (r"two JFFEs", "两次 JFFE"),
    (r"in season 2", "第2季中"),
    (r"Instant flicker cancel", "即时弹指取消"),
    (r"wake up backwards", "向后起身"),
    (r"wall carry/wall blast", "墙运/爆墙"),
    (r"wall carry/wall splat", "墙运/撞墙"),
    (r"[Ww]all [Cc]arry", "墙运"),
    (r"[Ww]all [Ss]plat", "撞墙"),
    (r"[Ww]all [Bb]last", "爆墙"),
    (r"[Ff]loor [Bb]lasts?", "地板爆破"),
    (r"[Ff]loor [Bb]reaks?", "破地板"),
    (r"[Bb]alcony [Bb]reak", "阳台破落"),
    (r"(?i)\bwall\b", "墙"),
    (r"(?i)\bfloor\b", "地板"),
    (r"\bbreak\b", "破坏"),
    (r"\bBefore\b", "之前"),
    (r"\bused\b", "使用"),
    (r"\bhit\b", "命中"),
    (r"[Tt]ech [Rr]oll", "受身"),
    (r"\btech\b", "受身"),
    (r"\broll\b", "翻滚"),
    (r"[Cc]hip [Dd]amage", "磨血"),
    (r"[Cc]ounter[- ][Hh]it", "迎击"),
    (r"[Bb]ackdash[_ ]?ss", "后撤横移"),
    (r"[Bb]ackturn(?:ed)?", "背身"),
    (r"[Hh]eat [Ee]ngager", "热能启动"),
    (r"(?i)\bheat\b", "热能"),
    (r"[Oo]kizeme|\b[Oo]ki\b", "压起身"),
    (r"[Gg]etup|\bukemi\b", "受身"),
    (r"[Mm]icrodash|m\.dash|\bmd\b", "微冲刺"),
    (r"[Bb]ackdash", "后撤步"),
    (r"\bLaunches opponent\b", "对手浮空"),
    (r"\b[Ll]aunche?s?\b", "浮空"),
    (r"\bInstant\b", "即时"),
    (r"\bflicker\b", "弹指"),
    (r"\bcancel\b", "取消"),
    (r"\bneutral\b", "回中"),
    (r"\brun\b", "奔跑"),
    (r"\bopponent\b", "对手"),
    (r"\bcrouching\b", "蹲姿"),
    (r"\bstanding\b", "站立"),
    (r"\bsuccessful\b", "成功"),
    (r"\bactivated\b", "激活"),
    (r"\bNatural\b", "自然连段"),
    (r"\bvery hard\b", "很难"),
    (r"\bhard\b", "难"),
    (r"\bdifficult\b", "难"),
    (r"\beasy\b", "简单"),
    (r"\badvanced\b", "进阶"),
    (r"\bfor damage\b", "求伤害"),
    (r"\bfor oki\b", "求压起身"),
    (r"(?i)\bdamage\b", "伤害"),
    (r"\bfor (?=\d)", "得"),
    (r"\bclose range\b", "近身"),
    (r"\bclose\b", "近身"),
    (r"\bfar\b", "远身"),
    (r"\boff-axis\b", "偏轴"),
    (r"\bResplat\b", "重新撞墙"),
    (r"\bReset\b", "重置"),
    (r"\bPickup\b", "捞起身"),
    (r"\bstep\b", "侧步"),
    (r"\bStaple\b", "常用"),
    (r"\bnotes?\b", "备注"),
    (r"\bspecific\b", "特定"),
    (r"\bdirection\b", "方向"),
    (r"\boddities\b", "特例"),
    (r"\buseful\b", "实用"),
    (r"\brarely\b", "较少使用"),
    (r"\bon block\b", "被防"),
    (r"\bblock\b", "防御"),
    (r"\band\b", "与"),
    (r"\bor\b", "或"),
    (r"\bNo\b", "无"),
    (r"\bwithout\b", "不带"),
    (r"\bwith\b", "带"),
    (r"\be\.g\.?\b", "例如"),
    (r"\bssl\b|\bssL\b|\bSSL\b", "横移左"),
    (r"\bssr\b|\bssR\b|\bSSR\b", "横移右"),
    (r"\bcc\b", "蹲消"),
    (r"\bGB\b", "破防"),
    (r"\bLow\b", "下段"),
    (r"\bFor\b", "用于"),
    (r"\bGain\b", "获得"),
    (r"\bEnder\b", "收尾"),
    # move nicknames (kept as readable Chinese names)
    (r"\bPEWGF\b", "最速电风拳"),
    (r"\bDEWGF\b", "恶魔电风拳"),
    (r"\bEWGF\b", "电风拳"),
    (r"\bEWHF\b", "电风勾拳"),
    (r"\bPEWGK\b", "最速电风踢"),
    (r"\bEWGK\b", "电风踢"),
    (r"\bOTGF\b", "奥义电风拳"),
    (r"\bWGF\b", "风神拳"),
    (r"\bOrbital\b", "轨道踢"),
    (r"\bMatterhorn\b", "马特洪峰"),
    (r"\bDemoman\b", "爆破手"),
    (r"\bSecluded Training\b", "幽闭训练场"),
    (r"\(x(\d)\)", r"×\1"),
    (r"\bdash\b", "冲刺"),
    (r"\bdamage\b", "伤害"),
    (r"\bdelay\b", "延迟"),
    (r"\bwake up\b", "起身"),
    (r"\bx(\d)\b", r"×\1"),
]

# Character names appearing in combo notes -> Chinese (word-bounded,
# longer names first so "Devil Jin" wins over "Jin")
COMBO_CHAR_NAMES = {
    "Devil Jin": "恶魔仁",
    "Armor King": "铠甲王",
    "Miary Zo": "米亚莉·佐",
    "Marshall Law": "马歇尔·洛",
    "Alisa": "阿丽莎",
    "Azucena": "阿苏塞娜",
    "Jun": "风间准",
    "Lili": "莉莉",
    "Nina": "妮娜",
    "Leroy": "勒罗伊",
    "Claudio": "克劳迪奥",
    "Steve": "史蒂夫",
    "DJ": "恶魔仁",
    "King": "金",
    "Paul": "保罗",
    "Victor": "维克多",
    "Feng": "冯威",
    "Kuma": "熊",
    "Panda": "熊猫",
    "Raven": "雷文",
    "Jack": "杰克",
    "Bear": "熊",
    "Lidia": "莉迪亚",
    "Lee": "李超狼",
    "Reina": "蕾娜",
    "Law": "洛",
    "Xiaoyu": "凌晓雨",
    "Jin": "风间仁",
    "Kazuya": "三岛一八",
    "Leo": "雷欧",
    "Hwoarang": "花郎",
    "Yoshimitsu": "吉光",
    "Anna": "安娜",
    "Eddy": "艾迪",
    "Heihachi": "三岛平八",
    "Clive": "克莱夫",
    "Bryan": "布莱恩",
}


def translate_combo_literal(text: str) -> str:
    result = text
    for pattern, replacement in COMBO_LITERAL_PHRASES:
        result = re.sub(pattern, replacement, result)
    for name in sorted(COMBO_CHAR_NAMES, key=len, reverse=True):
        result = re.sub(
            rf"(?<![A-Za-z]){re.escape(name)}(?![A-Za-z])",
            COMBO_CHAR_NAMES[name],
            result,
        )
    return result


def translate_combo_starter(value: str) -> str:
    replacements = [
        (r"Tornado Available", "可用龙卷"),
        (r"No Tornado", "不用龙卷"),
        (r"Tornado launch", "龙卷浮空"),
        (r"Regular launch", "常规浮空"),
        (r"Regular carry", "常规墙运"),
        (r"Grounded hits", "倒地追击"),
        (r"\s*\(on lower hit\)", "（下段命中时）"),
        (r"Low Parry", "下段化解"),
        (r"With\s*Heat", "（热能中）"),
        (r"Counter-hit", "迎击"),
        (r"Counter hit", "迎击"),
        (r"Backturned", "背身"),
        (r"Wall splat", "墙壁命中"),
        (r"Heat Dash", "热能冲刺"),
        (r"During Heat", "热能中"),
        (r"scaling", "缩放"),
        (r"e\.g\.", "例如"),
        (r"heat", "热能"),
        (r"Instant Tornado", "直接龙卷"),
        (r"Tornado", "龙卷"),
        (r"wall blast", "爆墙"),
        (r"wall carry", "墙运"),
        (r"long dash", "长冲刺"),
        (r"dash", "冲刺"),
        (r"(\d+)\s*hits?", r"\1击"),
        (r"unavailable", "不可用"),
        (r"available", "可用"),
        (r"after taunt", "嘲讽后"),
        (r"taunt", "嘲讽"),
        (r"without", "不带"),
        (r"with", "带"),
        (r"into", "接"),
        (r"combos?", "连招"),
        (r"wall", "墙"),
        (r"blocked", "被防"),
        (r"block", "防御"),
        (r"opponent", "对手"),
        (r"crouching", "蹲姿"),
        (r"standing", "站立"),
        (r"launchers?", "浮空技"),
        (r"launch", "浮空"),
        (r"post-T!?", "龙卷后"),
        (r"chip damage", "磨血"),
        (r"for damage", "求伤害"),
        (r"example", "例"),
        (r"damage", "伤害"),
        (r"Regular", "常规"),
        (r"long", "长"),
        (r"splat", "命中"),
        (r"hits", "击"),
        (r"parry", "防反"),
        (r"mini", "小"),
        (r"enders?", "收尾"),
        (r"finishers?", "终结"),
        (r"after", "后接"),
        (r"both", "双侧"),
    ]
    result = value
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result, flags=re.I)
    return translate_combo_literal(result)


def build_english_name_map(source: dict, translation: dict) -> dict[str, str]:
    """English move names appearing in combo starters -> Chinese names."""
    names = {}
    for move in source["moves"]:
        name = move.get("name", "")
        if name and LATIN.search(name):
            zh = translation["move_names"].get(move["id"])
            if zh:
                names.setdefault(name, zh)
    return names


def combo_starter_label(starter: str, english_names: dict[str, str]) -> str:
    result = translate_combo_starter(starter)
    for name in sorted(english_names, key=len, reverse=True):
        if name in result:
            result = result.replace(name, english_names[name])
    return result


def split_combo_tokens(value: str) -> list[str]:
    # "[...]" (damage notes) and "(...)" (annotations / command groups) both
    # protect inner whitespace so each stays one token
    tokens = []
    start = 0
    stack = []
    pairs = {"[": "]", "(": ")"}
    for index, character in enumerate(value):
        if character in pairs:
            stack.append(pairs[character])
        elif stack and character == stack[-1]:
            stack.pop()
        elif character.isspace() and not stack:
            if start < index:
                tokens.append(value[start:index])
            start = index + 1
    if start < len(value):
        tokens.append(value[start:])
    return tokens


def normalize_combo_token(value: str, stance_names: dict[str, str]) -> str:
    # combo-only punctuation: "<" delay / ">" then / grouping parens
    value = value.replace("<", ",").replace(">", ",")
    value = re.sub(r"[,~]{2,}", lambda m: "~" if "~" in m.group() else ",", value)
    value = value.strip(",").strip()
    value = value.replace("(", " ").replace(")", " ").strip()
    # repeat markers: "(uf+3+4~F)x2" / "(uf+3+4~Fx2)" tail or "x2" head
    value = re.sub(r"^x(\d)(?=[~,+]|$)", r"×\1", value)
    value = re.sub(r"x(\d)$", r"×\1", value)
    # microdash is just a quick f,f; "ff3," / "3,1,ff" glue the same run
    value = re.sub(r"m\.dash|microdash", "f,f", value, flags=re.I)
    value = re.sub(r"^ff(?=[+1-4])", "f,f", value)
    value = re.sub(r"(?<=,)ff$", "f,f", value)
    # source key-name aliases (PKB->PAB / OG->OTG), combo data only
    value = re.sub(r"^PKB(?=[.~]|$)", "PAB", value)
    value = re.sub(r"^OG(?=[.~]|$)", "OTG", value)
    if value.casefold() in {"dash", "ff"}:
        return "f,f"
    value = re.sub(r"^iws\.?(?=[1-4])", "ws", value, flags=re.I)
    value = re.sub(r"^ss(?=[1-4])", "SS.", value, flags=re.I)
    value = re.sub(r"^qcf[.:]?(?=[1-4])", "qcf+", value, flags=re.I)
    if "WALL" in stance_names:
        value = re.sub(r"^W\.", "WALL.", value)
    return re.sub(
        r"(?<![A-Za-z])([dDuU])([fFbB])(?=[^A-Za-z]|$)",
        lambda match: match.group(1) + "/" + match.group(2),
        value,
    )


def render_combo_piece(
    value: str, css_class: str, stance_names: dict[str, str]
) -> str:
    if re.fullmatch(r"CH|![A-Z][A-Za-z]{0,3}|[A-Z][A-Za-z]{0,3}!", value, re.I):
        return f'<span class="tk-tbang">{escape(value.upper())}</span>'

    def literal(text: str) -> str:
        translated = translate_combo_literal(text)
        # stance codes surviving inside notes get their Chinese label too
        for code, name in sorted(
            stance_names.items(), key=lambda item: len(item[0]), reverse=True
        ):
            if code.isalnum() and code.isupper() and len(code) >= 3:
                translated = re.sub(
                    rf"\b{re.escape(code)}\b", state_label(name), translated
                )
        return (
            '<span class="combo-literal">'
            f"{escape(translated)}</span>"
        )

    rendered = []
    for part in re.split(r"(\[[^\]]*\]|\([^()]*\))", value):
        if not part:
            continue
        if part.startswith("[") and part.endswith("]"):
            rendered.append(literal(part))
            continue
        if part.startswith("(") and part.endswith(")"):
            inner = part[1:-1]
            # command group ("(H.b+2)", "(LFS.1)"): convert, keep parens;
            # anything with whitespace is an annotation note -> translate
            if re.search(r"[1-4]", inner) and not re.search(r"\s", inner):
                graphical = render_graphical_command(
                    normalize_combo_token(inner, stance_names),
                    css_class,
                    stance_names,
                    None,
                )
                if graphical is not None:
                    rendered.append(
                        f"{literal('(')}{graphical}{literal(')')}"
                    )
                    continue
            rendered.append(literal(part))
            continue

        normalized = normalize_combo_token(part, stance_names)
        graphical = render_graphical_command(
            normalized, css_class, stance_names, None
        )
        if graphical is None:
            rendered.append(literal(part))
        else:
            rendered.append(graphical)

    return '<span class="combo-token">' + "".join(rendered) + "</span>"


def render_combo_command(
    value: str, css_class: str, stance_names: dict[str, str]
) -> str:
    plain = escape(value)
    graphical = "".join(
        render_combo_piece(token, css_class, stance_names)
        for token in split_combo_tokens(value)
    )
    return (
        f'<span class="cmd-gfx combo-gfx" aria-hidden="true">{graphical}</span>'
        f'<span class="cmd-txt">{plain}</span>'
        f'<span class="sr-only cmd-a11y">{plain}</span>'
    )


# Source key-name aliases seen only in combo data (PKB vs PAB etc.);
# merged into stance_names for combo rendering only.
COMBO_STANCE_ALIASES = {
    "steve": {"PKB": "窥视架"},
    "eddy": {"MD": "曼丁加"},
    "alisa": {"OG": "对手倒地时"},
}


# Stage/heat combo markers shown as tk-tbang badges; the combos intro legend
# explains the ones actually used on each page.
COMBO_MARKER_LEGEND = {
    "W!": "撞墙",
    "WT!": "墙壁回旋",
    "WB!": "破墙/弹墙",
    "WH!": "墙壁机关",
    "HWB!": "硬破墙",
    "BB!": "阳台破坏",
    "FB!": "破地板",
    "FBl!": "地板爆破",
    "WBl!": "爆墙",
    "HB!": "热能爆发",
    "WS!": "撞墙",
    "RA": "怒气技",
}


def combo_marker_note(combos: dict) -> str:
    """Legend line for stage/heat markers used in this character's combos."""
    text = " ".join(
        entry.get(field, "")
        for group in combos.get("sections", [])
        for entry in group.get("entries", [])
        for field in ("starter", "route")
    )
    used = []
    for marker, label in COMBO_MARKER_LEGEND.items():
        if marker == "RA":
            found = re.search(r"\bRA\b", text)
        else:
            found = re.search(rf"(?<![A-Za-z]){re.escape(marker)}", text)
        if found:
            used.append(f"{marker}={label}")
    if not used:
        return ""
    return "<br><b>标记</b>：" + " · ".join(used)


def render_combos(
    combos: dict,
    css_class: str,
    stance_names: dict[str, str],
    english_names: dict[str, str] | None = None,
) -> tuple[str, int]:
    english_names = english_names or {}
    groups = valid_combo_groups(combos)
    if not groups:
        body = (
            '<div class="tpFull"><h2>连招 <span class="en">COMBOS</span></h2>'
            '<p class="empty-note">Wavu 连招页当前没有可用路线；占位文本已剔除。'
            "为避免编造，本页暂不补写未经来源验证的连招。</p></div>"
        )
        return body, 0
    chunks = []
    combo_count = 0
    for section, rows in groups:
        combo_count += len(rows)
        title = COMBO_SECTION_NAMES.get(section, section)
        if LATIN.search(title):
            raise ValueError(f"untranslated combo section: {section}")
        rendered_rows = []
        for starter, route in rows:
            translated_starter = combo_starter_label(starter, english_names) or "通用"
            rendered_rows.append(
                "<tr>"
                '<td class="cmd combo-starter">'
                f"{render_combo_command(translated_starter, css_class, stance_names)}"
                "</td>"
                '<td class="cmd combo-route">'
                f"{render_combo_command(route, css_class, stance_names)}"
                "</td>"
                "</tr>"
            )
        chunks.append(
            f'<div class="tpFull"><h2>{escape(title)} <span class="en">COMBOS</span></h2>'
            '<table class="cb"><thead><tr><th>起手</th>'
            '<th>路线（[数字]=伤害 · T!=回旋 · ~F=按住前 · →=下一招）</th></tr></thead>'
            f'<tbody>{"".join(rendered_rows)}</tbody></table></div>'
        )
    return "".join(chunks), combo_count


def render_sheet_section(
    section_id: str,
    title: str,
    english_title: str,
    records: list[tuple[str, dict]],
    translation: dict,
    resolver: StartupResolver,
    config: dict,
    kind: str,
    *,
    split: bool = False,
    command_cap: int | None = 6,
) -> str:
    if not records:
        return ""
    if split:
        table_html = render_split_tables(
            records, translation, resolver, config, kind, command_cap
        )
    else:
        table_html = render_table(
            records,
            translation,
            resolver,
            config,
            kind,
            command_cap,
        )
    return (
        f'<section class="sheet-section" id="{escape(section_id, quote=True)}">'
        f'<h2>{escape(title)} <span class="en">{escape(english_title)}</span></h2>'
        f"{table_html}</section>"
    )


def ten_string_leaves(
    records: list[tuple[str, dict]],
) -> list[tuple[str, dict]]:
    named = [
        record
        for record in records
        if record[1].get("name", "").casefold() == "10 hit combo"
    ]
    if named:
        return named
    commands = [move["command"] for _, move in records]
    return [
        record
        for record in records
        if not any(
            other.startswith(record[1]["command"] + ",")
            for other in commands
            if other != record[1]["command"]
        )
    ]


def render_ten_string_table(
    records: list[tuple[str, dict]],
    resolver: StartupResolver,
    config: dict,
    stance_names: dict[str, str],
) -> str:
    leaves = ten_string_leaves(records)
    rows = []
    for record_id, move in leaves:
        command = move["command"]
        covered_ids = [
            candidate_id
            for candidate_id, candidate in records
            if command == candidate["command"]
            or command.startswith(candidate["command"] + ",")
        ]
        startup = resolver.resolve(command, move.get("startup", ""))
        attrs = (
            f'data-record-id="{escape(record_id, quote=True)}" '
            f'data-covered-record-ids="{escape("|".join(covered_ids), quote=True)}" '
            f'data-move-id="{escape(move["id"], quote=True)}" '
            f'data-command="{escape(command, quote=True)}" '
            f'data-startup="{escape(startup, quote=True)}" data-kind="move"'
        )
        rows.append(
            f"<tr {attrs}>"
            f'<td class="cmd">{render_command(command, config["css_class"], stance_names, None)}</td>'
            f"{render_startup_cell(startup)}"
            f'{render_damage_cell(move.get("damage", ""))}'
            f'<td class="rng">{render_target(move.get("target", ""))}</td>'
            "</tr>"
        )
    return (
        '<table class="ten-string-table"><colgroup><col style="width:55%">'
        '<col style="width:10%"><col style="width:22%"><col style="width:13%">'
        '</colgroup><thead><tr><th>指令</th><th>发生</th>'
        '<th>伤害</th><th>判定</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def render_system_sections(
    heat: list[tuple[str, dict]],
    ten_strings: list[tuple[str, dict]],
    translation: dict,
    resolver: StartupResolver,
    config: dict,
) -> str:
    ten_table = (
        render_ten_string_table(
            ten_strings,
            resolver,
            config,
            translation.get("stance_names", {}),
        )
        if ten_strings
        else ""
    )
    if heat and ten_strings:
        heat_table = render_table(heat, translation, resolver, config, "move")
        return (
            '<section class="sheet-section keep" id="systems"><div class="colsRow">'
            '<div><h2>热能系统 <span class="en">HEAT</span></h2>'
            f"{heat_table}</div>"
            '<div><h2>十连技 <span class="en">10 HIT COMBO</span></h2>'
            f"{ten_table}</div></div></section>"
        )
    heat_section = render_sheet_section(
            "heat",
            "热能系统",
            "HEAT",
            heat,
            translation,
            resolver,
            config,
            "move",
        )
    ten_section = (
        '<section class="sheet-section keep" id="ten-strings">'
        '<h2>十连技 <span class="en">10 HIT COMBO</span></h2>'
        f"{ten_table}</section>"
        if ten_strings
        else ""
    )
    return heat_section + ten_section


def build_page(key: str, config: dict, component_css: str) -> str:
    source = load_json(TOOLS / "source" / f"{key}.json")
    translation = load_json(TOOLS / "source" / f"{key}_zh.json")
    combos = load_json(TOOLS / "source" / f"{key}_combos.json")
    validate_metadata(key, config, [source, translation, combos])
    validate_translation(source, translation)
    validate_damage_fields(key, source)
    validate_combo_annotations(combos)
    resolver = StartupResolver(source["moves"])

    records = record_ids(source["moves"])
    throws, attacks, stances, heat, ten_strings = partition_records(records, config)
    sections = (
        render_sheet_section(
            "throws",
            "投技",
            "THROWS",
            throws,
            translation,
            resolver,
            config,
            "throw",
            split=True,
        )
        + render_sheet_section(
            "attacks",
            "打击技",
            "ATTACKS",
            attacks,
            translation,
            resolver,
            config,
            "move",
            split=True,
        )
        + (
            '<section class="sheet-section keep" id="stances">'
            + render_stance_matrix(stances, translation, resolver, config)
            + "</section>"
            if stances
            else ""
        )
        + render_system_sections(
            heat, ten_strings, translation, resolver, config
        )
    )
    combo_html, combo_count = render_combos(
        combos,
        config["css_class"],
        {
            **translation.get("stance_names", {}),
            **COMBO_STANCE_ALIASES.get(key, {}),
        },
        build_english_name_map(source, translation),
    )
    marker_note = combo_marker_note(combos)
    frame_count = sum(
        resolver.resolve(move["command"], move.get("startup", "")) != "—"
        for move in source["moves"]
    )
    move_count = len(source["moves"])
    visible_move_count = move_count - len(ten_strings) + len(
        ten_string_leaves(ten_strings)
    )
    collapsed_note = (
        f"；十连技的 {len(ten_strings)} 条递进源卡合并为完整招式"
        if len(ten_strings) > 1
        else ""
    )
    movelist_url = source["source_url"]
    combos_url = combos["source_url"]
    boot_script = """<script>(function(){try{var t=localStorage.getItem('tk-theme');if(t!=='light')document.documentElement.classList.add('dark')}catch(_){document.documentElement.classList.add('dark')}})();</script>"""
    page_title = (
        f"铁拳8 {config['display']}（{config['canonical']}）出招表"
        f" | TEKKEN 8 {config['canonical']} Movelist"
    )
    page_description = (
        f"{config['display']}（{config['canonical']}）《铁拳8》（TEKKEN 8）完整出招表："
        "招式指令、帧数表、确反数据与进阶连招。"
        f"Complete TEKKEN 8 {config['canonical']} movelist with frame data."
    )
    page_url = f"https://tekken8movelist.github.io/{config['filename']}"
    avatar_slug = config["filename"].removesuffix("_tk8_movelist.html")
    og_image = f"https://tekken8movelist.github.io/avatars/{avatar_slug}.png"
    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": page_title,
            "description": page_description,
            "url": page_url,
            "inLanguage": "zh-CN",
            "isPartOf": {
                "@type": "WebSite",
                "name": "铁拳8 全角色中文出招表",
                "url": "https://tekken8movelist.github.io/",
            },
            "breadcrumb": {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "首页",
                        "item": "https://tekken8movelist.github.io/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": f"{config['display']}出招表",
                        "item": page_url,
                    },
                ],
            },
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(page_title)}</title>
<meta name="description" content="{escape(page_description, quote=True)}">
<link rel="canonical" href="{page_url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_CN">
<meta property="og:site_name" content="铁拳8 全角色中文出招表">
<meta property="og:title" content="{escape(page_title, quote=True)}">
<meta property="og:description" content="{escape(page_description, quote=True)}">
<meta property="og:url" content="{page_url}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:alt" content="铁拳8 {escape(config['display'], quote=True)}（{escape(config['canonical'], quote=True)}）头像">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(page_title, quote=True)}">
<meta name="twitter:description" content="{escape(page_description, quote=True)}">
<meta name="twitter:image" content="{og_image}">
<script type="application/ld+json">{json_ld}</script>
{boot_script}
<style>{PAGE_CSS}</style>
<style id="tk-notation">{component_css}</style>
</head>
<body style="--accent:{config['accent']};--accent-ink:{config['accent_ink']}">
<header id="top">
  <h1>{escape(config['display'])}<small>{escape(config['canonical'].upper())} · 铁拳 8 出招表</small></h1>
  <div class="ntgl" id="thgl" aria-label="主题">主题<span class="seg"><button type="button" id="thd" class="on" aria-pressed="true">夜间</button><button type="button" id="thl" aria-pressed="false">浅色</button></span></div>
  <div class="ntgl" id="ntgl" aria-label="指令记法">记法<span class="seg"><button type="button" id="ng" class="on" aria-pressed="true">按键图</button><button type="button" id="nn" aria-pressed="false">无数字</button><button type="button" id="nt" aria-pressed="false">文字</button></span></div>
  <div class="sub">上段 <span style="color:#9fc9ff">■</span>　中段 <span style="color:#ffd18a">■</span>　下段 <span style="color:#ff9d9d">■</span></div>
</header>
<div class="legend"><b>指令说明</b>　1=左拳　2=右拳　3=左脚　4=右脚　|　f=前　b=后　u=上　d=下　d/f=前下　d/b=后下　u/f=前上　u/b=后上　|　f,f=前冲　WS=起身中　FC=蹲伏中　SS=横移中　+=同时按　~=紧接　|　<b>判定</b>：<span class="hi">上</span>=上段　<span class="md">中</span>=中段　<span class="lo">下</span>=下段　<span class="sp">特</span>=特殊　<span class="sp">投</span>=投掷　|　<b>发生</b>=首击冲击帧（i=impact，越小越快，依 Wavu）　|　{move_count} 条源记录 / {visible_move_count} 条表内招式 / {frame_count} 条有发生帧{collapsed_note}</div>
<div class="legend gfx-only"><b>图形记法</b>　<span class="tk-in tk-sm"><span class="tk-b"><i>1</i><i>2</i><i>3</i><i>4</i></span></span> 四键方阵（左上1 右上2 左下3 右下4，亮=按下）　<span class="tk-in tk-sm"><span class="tk-dir f"></span></span>=轻点方向　<span class="tk-in tk-sm"><span class="tk-dir f hold"></span></span>=按住　<span class="tk-in tk-sm"><span class="tk-n">N</span></span>=回中　<span class="tk-in tk-sm"><span class="tk-state">架势中</span></span>=状态前缀　|　<b>分隔</b>：› 接续　+ 方向＋键　~ 紧接　＊蓄力　→ 下一招　<span class="tk-tbang">T!</span> 回旋</div>
<main>
  <div id="movelist" data-source-record-count="{move_count}" data-visible-record-count="{visible_move_count}">{sections}</div>
  <section class="tipsPage" id="combos">
    <header><h1>进阶攻略<small>{escape(config['display'])} · Wavu Wiki 连招数据</small></h1></header>
    <div class="legend">仅收录 Wavu 连招页实际存在的 {combo_count} 条路线；原始记法与伤害标注保持不变（方括号数字为该段伤害，如 [25]），占位内容已剔除，不补写未经来源验证的打法。{marker_note}</div>
    {combo_html}
    <footer id="sources">数据来源：<a href="{escape(movelist_url, quote=True)}">Wavu Wiki movelist</a> · 打法参考：<a href="{escape(combos_url, quote=True)}">Wavu Wiki combos</a> · 招式名为中文意译，供参考；发生帧表示首击冲击帧。</footer>
  </section>
</main>
<script>{PAGE_SCRIPT}</script>
</body>
</html>
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=SITE, help="directory for generated HTML"
    )
    parser.add_argument(
        "--character", choices=list(CHARACTERS), help="build one character only"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    component_css = (
        ROOT / "design" / "notation-wireframe" / "tekken-input-notation.css"
    ).read_text(encoding="utf-8")
    selected = [args.character] if args.character else list(CHARACTERS)
    for key in selected:
        config = CHARACTERS[key]
        html = build_page(key, config, component_css)
        destination = args.output_dir / config["filename"]
        write_if_changed(destination, html)
        print(f"built {key}: {destination.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
