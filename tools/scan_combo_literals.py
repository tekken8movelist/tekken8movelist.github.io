# -*- coding: utf-8 -*-
"""Scan Season 2 pages for combo-literal fallback fragments.

Renders every combo starter/route of the 36 generator-built characters with
the real builder functions (render_combo_command, same pipeline as
render_combos) and collects every <span class="combo-literal"> fragment that
falls back to plain text instead of the graphical button component.

Also scans the main movelist commands that render_graphical_command cannot
convert, and dumps the per-character stance prefix mappings.

Read-only: never touches source JSON, the builder, or generated pages.

Usage: python tools/scan_combo_literals.py [--character KEY]
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from collections import Counter, OrderedDict
from html import unescape
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_season2", TOOLS / "build_season2.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_builder()
CHARACTERS = builder.CHARACTERS
COMMON_PREFIXES = builder.COMMON_PREFIXES

LITERAL_RE = re.compile(r'<span class="combo-literal">(.*?)</span>')
# pure damage / hit-count annotations: [35], [+78; 57], [1], [2], [14 +] ...
DAMAGE_RE = re.compile(r"\[[\d\s;,+\-]*\]")
LATIN_RE = re.compile(r"[A-Za-z]")
CJK_RE = re.compile(r"[一-鿿]")
# stance-ish references inside a fragment
TILDE_STANCE_RE = re.compile(r"~[A-Z][A-Z0-9]{1,4}(?![a-z])")
DOTTED_STANCE_RE = re.compile(r"[A-Z][A-Z0-9]{1,4}\.")
STANDALONE_STANCE_RE = re.compile(r"[A-Z][A-Z0-9]{1,4}!?")
STANCE_TOKEN_RE = re.compile(r"[A-Z][A-Z0-9]{1,4}")
# move-name nicknames, not stances (kept out of the 2b stance summary)
NICKNAMES = {"EWGF", "EWHF", "PEWGF", "DEWGF", "OTGF", "CD"}


def is_damage(fragment: str) -> bool:
    return bool(DAMAGE_RE.fullmatch(fragment))


def is_stance_related(fragment: str) -> bool:
    """Fragments that reference a stance transition/prefix inside a command."""
    if not LATIN_RE.search(fragment) or is_damage(fragment):
        return False
    if TILDE_STANCE_RE.search(fragment):
        return True
    if DOTTED_STANCE_RE.search(fragment):
        return True
    match = STANDALONE_STANCE_RE.fullmatch(fragment)
    return bool(match) and fragment.rstrip("!") not in NICKNAMES


def clip(text: str, limit: int = 110) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def scan_character(key: str) -> dict:
    config = CHARACTERS[key]
    source = builder.load_json(TOOLS / "source" / f"{key}.json")
    translation = builder.load_json(TOOLS / "source" / f"{key}_zh.json")
    combos = builder.load_json(TOOLS / "source" / f"{key}_combos.json")
    stance_names = translation.get("stance_names", {})
    english_names = builder.build_english_name_map(source, translation)
    css_class = config["css_class"]

    fragments = OrderedDict()

    def record(fragment: str, field: str, raw: str, rendered: str) -> None:
        entry = fragments.setdefault(
            fragment,
            {"count": 0, "fields": set(), "example": "", "rendered": ""},
        )
        entry["count"] += 1
        entry["fields"].add(field)
        if not entry["example"]:
            entry["example"] = clip(raw)
            entry["rendered"] = clip(rendered)

    for _section, rows in builder.valid_combo_groups(combos):
        for starter, route in rows:
            label = builder.combo_starter_label(starter, english_names) or "通用"
            starter_html = builder.render_combo_command(
                label, css_class, stance_names
            )
            for raw_frag in LITERAL_RE.findall(starter_html):
                record(unescape(raw_frag), "starter", starter, label)
            route_html = builder.render_combo_command(route, css_class, stance_names)
            for raw_frag in LITERAL_RE.findall(route_html):
                record(unescape(raw_frag), "route", route, route)

    movelist_fails = OrderedDict()
    for move in source["moves"]:
        command = move["command"]
        if command in movelist_fails:
            continue
        if (
            builder.render_graphical_command(command, css_class, stance_names, 6)
            is not None
        ):
            continue
        uncapped_ok = (
            builder.render_graphical_command(command, css_class, stance_names, None)
            is not None
        )
        movelist_fails[command] = uncapped_ok

    return {
        "display": config["display"],
        "fragments": fragments,
        "movelist_fails": movelist_fails,
        "stance_names": stance_names,
        "stance_sections": config["stance_sections"],
    }


def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def report_per_character(results: OrderedDict) -> None:
    section("1. PER-CHARACTER combo-literal fragments (dedup, count, example)")
    for key, data in results.items():
        fragments = data["fragments"]
        interesting = {
            f: e for f, e in fragments.items() if not is_damage(f) and LATIN_RE.search(f)
        }
        other_text = {
            f: e for f, e in fragments.items() if not is_damage(f) and not LATIN_RE.search(f)
        }
        damage = {f: e for f, e in fragments.items() if is_damage(f)}
        total_occ = sum(e["count"] for e in fragments.values())
        print(
            f"\n--- {key} ({data['display']}) — {len(fragments)} distinct / "
            f"{total_occ} occurrences "
            f"[latin {len(interesting)}, zh-tag {len(other_text)}, "
            f"damage-note {len(damage)}]"
        )
        for frag, entry in sorted(
            interesting.items(), key=lambda kv: (-kv[1]["count"], kv[0])
        ):
            fields = "/".join(sorted(entry["fields"]))
            example = entry["example"]
            if entry["rendered"] != entry["example"]:
                example += f"  ⇒ {entry['rendered']}"
            print(f"  ×{entry['count']:<4d} [{fields:7s}] {frag!r}  e.g. {example}")
        if other_text:
            samples = sorted(other_text)[:4]
            occ = sum(e["count"] for e in other_text.values())
            print(
                f"  (zh starter labels: {len(other_text)} distinct / {occ} occ, "
                f"by design; e.g. {', '.join(repr(s) for s in samples)})"
            )


def report_latin(results: OrderedDict) -> None:
    section("2a. Fragments containing Latin letters — all distinct spellings")
    merged = Counter()
    owners = {}
    for key, data in results.items():
        for frag, entry in data["fragments"].items():
            if is_damage(frag) or not LATIN_RE.search(frag):
                continue
            merged[frag] += entry["count"]
            owners.setdefault(frag, set()).add(key)
    print(f"{len(merged)} distinct fragments:\n")
    for frag, count in sorted(merged.items(), key=lambda kv: (-kv[1], kv[0])):
        who = ",".join(sorted(owners[frag]))
        print(f"  ×{count:<4d} {frag!r}   [{who}]")
    words = Counter()
    for frag, count in merged.items():
        for word in re.findall(r"[A-Za-z]+", frag):
            words[word] += count
    print(f"\n  distinct latin words ({len(words)}):")
    print("  " + ", ".join(sorted(words, key=str.casefold)))


def report_stances(results: OrderedDict) -> None:
    section("2b. Fragments with stance abbreviations / transitions")
    merged = Counter()
    owners = {}
    for key, data in results.items():
        for frag, entry in data["fragments"].items():
            if not is_stance_related(frag):
                continue
            merged[frag] += entry["count"]
            owners.setdefault(frag, set()).add(key)
    print(f"{len(merged)} distinct stance-related fragments:\n")
    for frag, count in sorted(merged.items(), key=lambda kv: (-kv[1], kv[0])):
        who = ",".join(sorted(owners[frag]))
        print(f"  ×{count:<4d} {frag!r}   [{who}]")
    print("\n  stance abbreviation prefixes per character:")
    for key, data in results.items():
        found = OrderedDict()
        for frag in data["fragments"]:
            if not is_stance_related(frag):
                continue
            for token in STANCE_TOKEN_RE.findall(frag):
                if token in NICKNAMES:
                    continue
                mapped = data["stance_names"].get(token)
                found.setdefault(token, mapped)
        if not found:
            continue
        parts = [
            f"{token}→{mapped}" if mapped else f"{token}→(未配置)"
            for token, mapped in found.items()
        ]
        print(f"    {key:12s}: {' '.join(parts)}")


def report_damage(results: OrderedDict) -> None:
    section("2c. Pure damage / hit-count annotations [..] — totals only")
    merged = Counter()
    for data in results.values():
        for frag, entry in data["fragments"].items():
            if is_damage(frag):
                merged[frag] += entry["count"]
    print(
        f"  {len(merged)} distinct annotations, {sum(merged.values())} occurrences"
    )


def report_movelist(results: OrderedDict) -> None:
    section("3. Main movelist commands falling back to text (cap=6)")
    total = 0
    for key, data in results.items():
        fails = data["movelist_fails"]
        if not fails:
            continue
        total += len(fails)
        print(f"\n--- {key} ({data['display']}): {len(fails)}")
        for command, uncapped_ok in fails.items():
            note = (
                "overlong by design (renders with cap=None)"
                if uncapped_ok
                else "NOT parseable even with cap=None"
            )
            print(f"  {command!r}  — {note}")
    print(f"\n  total: {total} commands across all characters")


def report_stance_mappings(results: OrderedDict) -> None:
    section("4. Stance / prefix mappings (COMMON + per character)")
    print("\n  COMMON_PREFIXES (season2_config.py):")
    for token, label in COMMON_PREFIXES.items():
        print(f"    {token!r:28s} → {label}")
    print(
        "\n  Per character: <zh stance_names 键→中文名 (渲染实际使用, 来自 "
        "source/{key}_zh.json)> | stance_sections (season2_config.py)"
    )
    for key, data in results.items():
        names = ", ".join(
            f"{token}→{label}" for token, label in data["stance_names"].items()
        ) or "(无)"
        sections = ", ".join(data["stance_sections"]) or "(无)"
        print(f"\n  {key} ({data['display']})")
        print(f"    stance_names: {names}")
        print(f"    stance_sections: {sections}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", choices=list(CHARACTERS))
    args = parser.parse_args()

    keys = [args.character] if args.character else list(CHARACTERS)
    results = OrderedDict((key, scan_character(key)) for key in keys)

    report_per_character(results)
    report_latin(results)
    report_stances(results)
    report_damage(results)
    report_movelist(results)
    report_stance_mappings(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
