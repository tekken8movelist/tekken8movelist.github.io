# -*- coding: utf-8 -*-
"""Chinese rendering of the official TEKKEN 8 profile fields.

`fetch_official_profiles.py` snapshots country / fighting style / epithet
verbatim from tekken.com. This module is the vocabulary that turns those
English strings into the page's Chinese. Every entry is a proper noun or an
established martial-art name, so the mapping is a lookup rather than a
judgement call -- and an unmapped value raises instead of silently shipping
English into a page that promises to be all-Chinese.

Japanese-derived style names take their kanji directly (三島流喧嘩空手,
風間流古武術, 卍流忍術); the rest follow the project's usual rule of
translating descriptive English by meaning.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SNAPSHOT = TOOLS / "source" / "official_profiles.json"

# the official pages carry stray zero-width characters (Xiaoyu's style, at least)
ZERO_WIDTH = re.compile(r"[​-‏﻿]")

COUNTRY_ZH = {
    "Brazil": "巴西",
    "China": "中国",
    "France": "法国",
    "Germany": "德国",
    "Grand Duchy of Rosaria": "罗萨利亚大公国",
    "Ireland": "爱尔兰",
    "Italy": "意大利",
    "Japan": "日本",
    "Likely Japan (Refuted by Japanese government)": "推定日本（日本政府否认）",
    "Madagascar": "马达加斯加",
    "Mexico": "墨西哥",
    "Monaco": "摩纳哥",
    "None": "无",
    "None (Formely Japan)": "无（原日本）",
    "None (Relinquished his Japanese nationality)": "无（已放弃日本国籍）",
    "Peru": "秘鲁",
    "Poland": "波兰",
    "Russia": "俄罗斯",
    "Saudi Arabia": "沙特阿拉伯",
    "South Korea": "韩国",
    "Sweden": "瑞典",
    "Thailand": "泰国",
    "U.S.A.": "美国",
    "United Kingdom": "英国",
    "Unknown": "不明",
}

STYLE_ZH = {
    "Advanced Manji Ninjutsu": "进阶卍流忍术",
    "Ancient Assassination Arts": "古代暗杀术",
    "Assassination Arts": "暗杀术",
    "Baguazhang, Piguazhang-based Chinese Martial Arts": "以八卦掌、劈挂掌为基的中国武术",
    "Bajiquan": "八极拳",
    "Boxing": "拳击",
    "Brute Force": "蛮力",
    "Capoeira": "卡波耶拉",
    "Close Quarters Combat": "近身格斗",
    "Commando Sambo": "突击桑搏",
    # Final Fantasy XVI's official Chinese term for a Dominant is 显现者
    "Dominant": "显现者",
    "Heihachi-Style Advanced Kuma Shin Ken": "平八流进阶熊真拳",
    "Integrated Martial Arts Based on Judo": "以柔道为根基的综合格斗",
    "Karate": "空手道",
    "Kazama-Style Traditional Martial Arts": "风间流古武术",
    "Kickboxing": "踢拳",
    "Manji Ninjutsu": "卍流忍术",
    "Martial Arts": "武术",
    "Mishima-Style Fighting Karate": "三岛流喧哗空手",
    "Mixed Martial Arts (Striker)": "综合格斗（打击系）",
    "Morengy and other African Martial Arts": "莫伦基等非洲武术",
    "Muay Thai": "泰拳",
    # the official page spells it "Ninjitsu"
    "Ninjitsu": "忍术",
    "Pro Wrestling": "职业摔角",
    "Self-Taught Style": "自创流派",
    "Sirius Exorcist Arts": "天狼星驱魔术",
    "Super Spy CQB": "超级间谍近身格斗",
    "Taekwondo": "跆拳道",
    "Taijiquan": "太极拳",
    "Tekken Force Martial Arts": "铁拳众武术",
    "Thruster-Based High-Mobility Fighting Style": "推进器高机动战斗风格",
    "Traditional Karate": "传统空手道",
    "Unknown": "不明",
    "Wing Chun": "咏春拳",
}


def _clean(value: str) -> str:
    return ZERO_WIDTH.sub("", value or "").strip()


def load_profiles() -> dict:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def localized_profile(key: str, profiles: dict | None = None) -> dict:
    """Country and fighting style in Chinese, plus the English style for the title.

    Returns empty strings for fields the official page itself leaves out, so a
    page renders whatever is actually known and omits the rest.
    """
    profiles = load_profiles() if profiles is None else profiles
    profile = profiles.get(key)
    if profile is None:
        raise KeyError(f"no official profile snapshot for {key!r}")

    country = _clean(profile.get("country", ""))
    style = _clean(profile.get("style", ""))
    for value, table, label in (
        (country, COUNTRY_ZH, "country"),
        (style, STYLE_ZH, "style"),
    ):
        if value and value not in table:
            raise KeyError(
                f"{key}: unmapped {label} {value!r} -- add it to official_profile_zh.py"
            )
    return {
        "country_zh": COUNTRY_ZH.get(country, ""),
        "style_zh": STYLE_ZH.get(style, ""),
        "style_en": style,
        "epithet_en": _clean(profile.get("epithet", "")),
    }
