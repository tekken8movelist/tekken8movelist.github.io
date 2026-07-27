# -*- coding: utf-8 -*-
"""English names for the moves Wavu never named.

Wavu publishes no name for 1371 of the 6275 moves on this site. The Chinese
pages fill those with the project's own descriptive names -- 左高踢, 起身右拳,
下踢·爆膝 -- and the English pages used to show that Chinese verbatim with a
`ZH` badge, on the principle that inventing an English name and presenting it
as sourced would be worse than showing a name the reader cannot read.

Showing a name the reader cannot read turned out to be worse. So the English
pages now carry an English description instead, and the badge stays -- it now
says "this is the project's description, not an official name", which is the
same claim the Chinese pages have always made about the same 1371 moves.

The names are descriptive and built from a small vocabulary, so they are
composed from a segment table rather than listed one by one: that way a new
character's 左中踢 gets the same English as every other 左中踢, instead of
depending on who typed it. Anything the table cannot build -- proper names
like 无刀斩, and the handful of phrases whose English word order differs --
lives in `source/move_names_en.json`, and `--check` fails on anything that
resolves to neither.

    python tools/move_name_en.py --check      # every name resolves
    python tools/move_name_en.py --list       # dump the whole mapping
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
OVERRIDES_PATH = TOOLS / "source" / "move_names_en.json"

# ---------------------------------------------------------------------------
# Segment table. Longest match wins, so multi-character entries must be able to
# out-rank their own prefixes -- 中段 before 中, 刺拳 before 拳.
#
# Values are English words joined with spaces. An empty value drops the segment
# (the ordinal separator, for instance, is handled by the join rules below).
# ---------------------------------------------------------------------------

SEGMENTS: dict[str, str] = {
    # --- stance / approach ------------------------------------------------
    "起身": "Rising",
    "蹲身": "Crouching",
    "蹲姿": "Crouching",
    "全蹲": "Full Crouch",
    "俯身": "Ducking",
    "潜身": "Weaving",
    "背身": "Back-Turned",
    "横移": "Sidestep",
    "跃身": "Leaping",
    "跳身": "Jumping",
    "上跳": "Hopping",
    "后跃": "Backhop",
    "后闪": "Backsway",
    "后撤": "Retreating",
    "冲身": "Dashing",
    "前冲": "Rushing",
    "进身": "Advancing",
    "破势步": "Crouch Dash",
    "前进构": "Zenshin",
    "觉醒": "Awakened",
    "低位": "Low Stance",
    "中位": "Mid Stance",
    "前跳": "Forward Jump",
    "前跃": "Forward Leap",
    "跳步": "Hop",
    "跃步": "Hop Step",
    "跃起": "Leaping",
    "跳入": "Jump-In",
    "跳跃": "Jump",
    "半蹲": "Half Crouch",
    "蹲伏": "Crouching",
    "冲刺": "Sprint",
    "前进": "Advancing",
    "前踏": "Stepping",
    "助跑": "Running",
    "突进": "Charging",
    "突入": "Lunging",
    "推进": "Driving",
    "进步": "Stepping",
    "闪身": "Dodging",
    "雾步": "Mist Step",
    "对地": "Ground",
    "腾空": "Airborne",
    "腾身": "Vaulting",
    "逆侧翻": "Reverse Cartwheel",
    "旋避": "Evasive Spin",
    "后旋": "Spinning Back",
    "背转": "Turning",
    "转身": "Turning",
    "奔袭": "Charging",
    "热能": "Heat",
    # --- level / direction ------------------------------------------------
    "上段": "High",
    "中段": "Mid",
    "下段": "Low",
    "特殊中段": "Special Mid",
    "追踪": "Homing",
    "左": "Left",
    "右": "Right",
    "前": "Front",
    "后": "Back",
    "上": "Upper",
    "下": "Low",
    "中": "Mid",
    "高": "High",
    "低": "Low",
    "双": "Double",
    "内": "Inside",
    "外": "Outside",
    # --- strikes ----------------------------------------------------------
    "上勾拳": "Uppercut",
    "刺拳": "Jab",
    "直拳": "Straight Punch",
    "横拳": "Hook",
    "勾拳": "Hook",
    "重拳": "Heavy Punch",
    "落拳": "Falling Punch",
    "撞拳": "Ram Punch",
    "砸拳": "Hammer Punch",
    "背拳": "Backfist",
    "裏拳": "Backfist",
    "掌底": "Palm Heel",
    "熊掌": "Bear Palm",
    "掌": "Palm",
    "拳": "Punch",
    "爆膝": "Knee Blast",
    "顶膝": "Knee Thrust",
    "膝击": "Knee Strike",
    "膝": "Knee",
    "肘击": "Elbow Strike",
    "肘": "Elbow",
    "扫踢": "Sweep Kick",
    "侧踢": "Side Kick",
    "劈踢": "Axe Kick",
    "旋踢": "Spin Kick",
    "胫踢": "Shin Kick",
    "刈踢": "Reaping Kick",
    "回旋踢": "Roundhouse",
    "踏踢": "Stomp Kick",
    "踢": "Kick",
    "扫": "Sweep",
    "突刺": "Thrust",
    "突": "Thrust",
    "斩": "Slash",
    "撞": "Ram",
    "击腹": "Body Blow",
    "吸收击": "Absorbing Strike",
    "牵制": "Poke",
    "顶": "Thrust",
    "压": "Press",
    "擂": "Pound",
    "砸": "Smash",
    "刺": "Stab",
    "短拳": "Short Punch",
    "钩拳": "Hook",
    "轻拳": "Light Punch",
    "低拳": "Low Punch",
    "十字拳": "Cross",
    "震拳": "Shock Punch",
    "铲拳": "Shovel Punch",
    "冲拳": "Rush Punch",
    "拳锤": "Hammer Fist",
    "撑肘": "Elbow",
    "撞靠": "Shoulder Ram",
    "撞掌": "Palm Ram",
    "摆拳": "Swing Punch",
    "裂拳": "Splitting Punch",
    "脚尖踢": "Toe Kick",
    "连续踩踏": "Stomp Chain",
    "踩踏": "Stomp",
    "新月": "Crescent",
    "半月": "Half Moon",
    "横打": "Side Strike",
    "横斩": "Horizontal Slash",
    "狂旋": "Wild Spin",
    "直击": "Straight Strike",
    "追击": "Follow-up",
    "连段": "Chain",
    "双段": "Two-Hit",
    "双足": "Two-Leg",
    "双腿": "Two-Leg",
    "双重": "Double",
    "双击": "Double Strike",
    "双云": "Twin Cloud",
    "上勾": "Uppercut",
    "二连": "Two-Hit",
    "三连": "Three-Hit",
    "四连": "Four-Hit",
    "五连": "Five-Hit",
    "六连": "Six-Hit",
    "武器连击": "Weapon Combo",
    "武器击": "Weapon Strike",
    "中上段": "Mid-High",
    "中上": "Mid-High",
    "高位": "High",
    "不可防": "Unblockable",
    "重击": "Heavy Strike",
    "特下": "Special Low",
    "起手": "Opener",
    "取消": "Cancel",
    "派生": "Variant",
    "方向": "Directional",
    "反击": "Counter",
    "防反": "Parry",
    "擒抱": "Clinch",
    "擒摔": "Throw",
    "抓投": "Grab Throw",
    "背后": "Back",
    "架势": "Stance",
    "解除": "Exit",
    "蓄力": "Charge",
    "二段": "2nd Hit",
    "第二式": "2nd Form",
    "续": "Continued",
    "起": "Rise",
    "爆裂": "Burst",
    # --- chaining ---------------------------------------------------------
    "连环冲拳": "Rushing Punch Chain",
    "连拳": "Punch Combo",
    "连踢": "Kick Combo",
    "连打": "Combo",
    "连击": "Combo",
    "连斩": "Slash Combo",
    "追拳": "Follow-up Punch",
    "追踢": "Follow-up Kick",
    "追打": "Follow-up",
    "连": "Chain",
    "连环": "Chain",
    "三连打": "Three-Hit Combo",
    "接": "into",
    "蓄": "Charged",
    "强化": "Enhanced",
    # --- flavour names Wavu does not gloss anywhere -------------------------
    # Yoshimitsu's sword vocabulary; NSS is 无刀之极, so 无刀 alone is the
    # no-sword variant of a move rather than the stance
    "无刀": "No Sword",
    "薙": "Reaping Slash",
    "风车": "Windmill",
    "夺魂": "Soul Steal",
    "战轮": "War Wheel",
    "天守崩": "Tenshu Kuzushi",
    "奈落": "Naraku",
    "切腹": "Seppuku",
    "阎魔": "Enma",
    "押切": "Oshikiri",
    "祓魔": "Exorcism",
    "矢车": "Yaguruma",
    "印地安": "Indian",
    "毒风": "Poison Wind",
    "日晷": "Sundial",
    "应变卍": "Adaptive Manji",
    "致命怒": "Deadly Rage",
    # per-character flavour
    "弹指": "Flicker",
    "窥视": "Peekaboo",
    "螳螂": "Mantis",
    "稻草人": "Scarecrow",
    "隐士": "Hermit",
    "哀鸦": "Mourning Crow",
    "天怒": "Heaven's Wrath",
    "恶豹": "Bad Jaguar",
    "混沌": "Chaos",
    "锤击时机": "Hammer Chance",
    "金鸡": "Jin Ji",
    "朝露": "Dew",
    "狂兔": "Feisty Rabbit",
    "罗摩": "Rama",
    "莫伦吉": "Morengy",
    "猴面包树": "Baobab",
    "调香": "Perfumer",
    "居合": "Iai",
    "座禅": "Meditation",
    "蛇行": "Slither",
    "潜行蛇": "Stalking Snake",
    "电锯": "Chainsaw",
    "白鹭": "White Heron",
    "石拳": "Stone Fist",
    "掌击": "Palm Strike",
    "强化机枪": "Enhanced Machine Gun",
    "机枪": "Machine Gun",
    "活塞": "Piston",
    "散弹": "Scatter",
    "哥萨克": "Cossack",
    "千兆吨": "Gigaton",
    "双回旋": "Double Spin",
    "双旋发条": "Double Wind-Up",
    "可爱致命": "Lethal Cutie",
    "合字手": "Gassho",
    "后手": "Rear Hand",
    "吕布之矛": "Lu Bu's Spear",
    "咬踝": "Ankle Bite",
    "型号变更": "Model Change",
    "回击": "Counter Strike",
    "真红尖牙": "Crimson Fang",
    "绯红三角刃": "Scarlet Trident",
    "第六感": "Sixth Sense",
    "缠龙": "Coiling Dragon",
    "裁决": "Judgement",
    "速射": "Rapid Fire",
    "铁锤": "Sledgehammer",
    "风暴破": "Storm Breaker",
    "风神": "Wind God",
    "驱逐跟踪者": "Stalker Eviction",
    "怪客": "Prowler",
    "恍惚": "Trance",
    "快勾": "Quick Hook",
    "律动": "Rhythm",
    "引退": "Retirement",
    "换位": "Switch",
    "招架式": "Parry Stance",
    "拔塞突": "Corkscrew Thrust",
    "旋风魔": "Whirlwind Demon",
    "水仙": "Narcissus",
    "燕槌": "Swallow Hammer",
    "浪花突": "Naniwa Thrust",
    "恶魔光波": "Devil Beam",
    "直线": "Straight Line",
    "伏身": "Prone",
    "前移": "Forward Shift",
    "肩冲": "Shoulder Charge",
    "右直": "Right Straight",
    "左右": "Left Right",
    "左旋": "Left Spin",
    "双脚": "Two-Foot",
    "低段": "Low",
    "跃拳": "Leaping Punch",
    # the mined table has these only in their full stance form (狩猎构,
    # 狼袭构), and a move name uses the bare word
    "狩猎": "Hunting",
    "狼袭": "Stalking Wolf",
    "猫步": "Cat Step",
    "蛇眼": "Snake Eyes",
    "冲击": "Impact",
    "鞭击": "Whip Strike",
    "擒": "Grab",
    "热": "Heat",
    "跃": "Leaping",
    "跳": "Jump",
    "旋": "Spin",
    "击": "Strike",
    "二": "2nd",
    "三": "3rd",
    "四": "4th",
    "五": "5th",
    "六": "6th",
    "七": "7th",
    "八": "8th",
    "九": "9th",
    "十": "10th",
    "一": "1st",
}

# Segments whose English is a lowercase connector rather than a noun phrase.
CONNECTORS = {"into"}

@lru_cache(maxsize=1)
def lexicon() -> dict[str, str]:
    """The segment table, with the mined stance names layered underneath."""
    merged = dict(stance_segments())
    merged.update(SEGMENTS)  # a hand-written entry always wins
    return merged


@lru_cache(maxsize=1)
def _sorted_segments() -> list[str]:
    return sorted(lexicon(), key=len, reverse=True)
_ORDINALS = {
    "一": "1st", "二": "2nd", "三": "3rd", "四": "4th", "五": "5th",
    "六": "6th", "七": "7th", "八": "8th", "九": "9th", "十": "10th",
    # King's seventeen-hit string runs past ten
    "十一": "11th", "十二": "12th", "十三": "13th", "十四": "14th",
    "十五": "15th", "十六": "16th", "十七": "17th", "十八": "18th",
    "十九": "19th",
}
_VARIANT = {"甲": "A", "乙": "B", "丙": "C"}
CHAIN_HIT = re.compile(
    r"^(?P<ordinal>十[一二三四五六七八九]|[一二三四五六七八九十])连$"
)

# `十连技·甲五` -- the string tables, whose parts are an ordinal and sometimes
# a variant letter. Built from a pattern because every character has ten of
# them and listing 300 entries would bury the ones that matter.
TEN_STRING = re.compile(
    r"^(?P<name>.+?)·(?P<variant>[甲乙丙])?"
    r"(?P<ordinal>十[一二三四五六七八九]|[一二三四五六七八九十])$"
)
STRING_NAMES = {
    "十连技": "10-Hit Combo",
    "风间流六连": "Kazama Style 6-Hit Combo",
    "三岛流连打": "Mishima Style Combo",
}


@lru_cache(maxsize=1)
def stance_segments() -> dict[str, str]:
    """Chinese stance names -> Wavu's own English, mined from the snapshots.

    A third of these names lead with a stance -- 窥视左拳, 螳螂右拳, 隐士下踢 --
    and Wavu already names every stance in its section headings, which are
    written `PKB (Peekaboo)`. So the English for 窥视 is Peekaboo because Wavu
    says so, not because anybody here decided it. Only the strikes after the
    stance need a vocabulary of their own.
    """
    sys.path.insert(0, str(TOOLS))
    from season2_config import CHARACTERS  # noqa: E402

    found: dict[str, str] = {}
    for key in sorted(CHARACTERS):
        source = json.loads(
            (TOOLS / "source" / f"{key}.json").read_text(encoding="utf-8")
        )
        translation = json.loads(
            (TOOLS / "source" / f"{key}_zh.json").read_text(encoding="utf-8")
        )
        english = {}
        for section in {move.get("section", "") for move in source["moves"]}:
            code = section.split("(")[0].strip()
            label = re.search(r"\(([^)]+)\)", section)
            if code and label:
                english[code] = label.group(1).strip()
        for code, chinese in translation.get("stance_names", {}).items():
            name = english.get(code)
            # first character wins, deterministically: CHARACTERS is ordered and
            # a clash means two characters gloss the same word differently,
            # which the override table is the place to settle
            if name and chinese not in found:
                found[chinese] = name
    return found


@lru_cache(maxsize=1)
def overrides() -> dict[str, str]:
    if not OVERRIDES_PATH.is_file():
        return {}
    data = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    return {key: value for key, value in data.items() if not key.startswith("_")}


def compose(text: str) -> str | None:
    """Translate one `·`-free chunk by longest-match segmentation."""
    table = lexicon()
    words: list[str] = []
    rest = text
    while rest:
        for segment in _sorted_segments():
            if rest.startswith(segment):
                english = table[segment]
                if english:
                    words.append(english)
                rest = rest[len(segment):]
                break
        else:
            return None
    if not words:
        return None
    # 前下低踢 segments to Front + Low + Low Kick; the doubled word is an
    # artefact of the segmentation, not something the Chinese says twice
    flat: list[str] = []
    for word in " ".join(words).split(" "):
        if not flat or flat[-1] != word:
            flat.append(word)
    return " ".join(flat)


def english_name(chinese: str) -> str | None:
    """The English description for one project-authored Chinese move name."""
    chinese = chinese.strip()
    if not chinese:
        return None
    override = overrides().get(chinese)
    if override:
        return override

    match = TEN_STRING.match(chinese)
    if match and match.group("name") in STRING_NAMES:
        parts = [STRING_NAMES[match.group("name")]]
        if match.group("variant"):
            parts.append(_VARIANT[match.group("variant")])
        return f"{' '.join(parts)}, {_ORDINALS[match.group('ordinal')]} Hit"

    chunks = []
    for chunk in chinese.split("·"):
        # `连环冲拳·七连` is the seventh hit of the string, not a seventh chain
        hit = CHAIN_HIT.match(chunk)
        if hit:
            chunks.append(f"{_ORDINALS[hit.group('ordinal')]} Hit")
            continue
        composed = compose(chunk)
        if composed is None:
            return None
        chunks.append(composed)
    return " > ".join(chunks)


def unresolved(names: list[str]) -> list[str]:
    return [name for name in names if english_name(name) is None]


def project_names() -> dict[str, list[str]]:
    """Every Wavu-unnamed move's Chinese name -> the characters using it."""
    sys.path.insert(0, str(TOOLS))
    from season2_config import CHARACTERS  # noqa: E402

    found: dict[str, list[str]] = {}
    for key in CHARACTERS:
        source = json.loads(
            (TOOLS / "source" / f"{key}.json").read_text(encoding="utf-8")
        )
        translation = json.loads(
            (TOOLS / "source" / f"{key}_zh.json").read_text(encoding="utf-8")
        )
        for move in source["moves"]:
            if (move.get("name") or "").strip():
                continue
            name = translation["move_names"].get(move["id"], "").strip()
            if name:
                found.setdefault(name, []).append(key)
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args(argv)

    names = project_names()
    missing = unresolved(sorted(names))
    if args.list:
        for name in sorted(names):
            print(f"{name}\t{english_name(name) or '?'}")
    if missing:
        print(f"{len(missing)} of {len(names)} names have no English form:")
        for name in missing[:80]:
            print(f"  {name}  ({', '.join(names[name][:3])})")
        return 1
    print(f"ok    all {len(names)} project-authored names resolve to English")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
