# -*- coding: utf-8 -*-
"""Shared knowledge about the hub's localisable slots.

`docs/index.html` stays hand-maintained -- AGENTS.md allows editing it directly
and it carries the flux effect, the card grid and the whole design system. So
rather than templating it, the two other locales are *derived* from it, and
this module is the single description of what "derived" means: which slots
carry copy, and what each locale puts in them.

Kept apart from build_hub.py so the augment step (which edits the authored
Simplified page in place) and the derive step (which writes the other two) read
the same table.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from locales import LOCALES, page_href, strings  # noqa: E402

SITE = TOOLS.parent / "docs"
HUB = SITE / "index.html"

# Group headings. The Chinese builds read as an English kicker over a Chinese
# title; English cannot repeat itself there, so the kicker takes the roster tag
# and the title takes the plain name -- the pair still says two things.
GROUP_HEADINGS = {
    "Core Roster": {
        "hans": ("Core Roster", "核心阵容", "{n} 名"),
        "hant": ("Core Roster", "核心陣容", "{n} 名"),
        "en": ("Base Game", "Core Roster", "{n} fighters"),
    },
    "Season 1": {
        "hans": ("Season 1", "第1季 DLC", "{n} 名"),
        "hant": ("Season 1", "第1季 DLC", "{n} 名"),
        "en": ("DLC", "Season 1", "{n} fighters"),
    },
    "Season 2": {
        "hans": ("Season 2", "第2季 DLC", "{n} 名"),
        "hant": ("Season 2", "第2季 DLC", "{n} 名"),
        "en": ("DLC", "Season 2", "{n} fighters"),
    },
    "Season 3": {
        "hans": ("Season 3", "第3季 DLC", "{n} 名"),
        "hant": ("Season 3", "第3季 DLC", "{n} 名"),
        "en": ("DLC", "Season 3", "{n} fighters"),
    },
}

# Copy slots keyed by a regex that captures exactly the text to replace.
# Each value is the per-locale replacement.
HUB_STRINGS = {
    "hubTitle": {
        "hans": "全角色出招表",
        "hant": "全角色出招表",
        "en": "Every Fighter",
    },
    "hubSub": {
        "hans": "选择角色查看完整出招表 · 图形化按键记法 · 逐招发生帧 · 数据源自 Wavu Wiki",
        "hant": "選擇角色查看完整出招表 · 圖形化按鍵記法 · 逐招發生幀 · 資料源自 Wavu Wiki",
        "en": (
            "Pick a fighter for the full movelist — graphical input notation, "
            "per-move startup frames, data from Wavu Wiki"
        ),
    },
    "notationLabel": {"hans": "记法", "hant": "記法", "en": "Notation"},
    "ntGfx": {"hans": "按键图", "hant": "按鍵圖", "en": "Buttons"},
    "ntTxt": {"hans": "文字", "hant": "文字", "en": "Text"},
    "languageLabel": {"hans": "语言", "hant": "語言", "en": "Language"},
    "soonLabel": {"hans": "即将上线", "hant": "即將上線", "en": "Coming soon"},
    # the empty-search state, half of it built by the inline search script
    "noneTitle": {"hans": "未找到", "hant": "未找到", "en": "No matches"},
    "noneHint": {
        "hans": "试试角色的中文名或英文名",
        "hant": "試試角色的中文名或英文名",
        "en": "Try the fighter's name or an alias",
    },
    "noneQueryOpen": {"hans": "未找到「", "hant": "未找到「", "en": "No match for “"},
    "noneQueryClose": {"hans": "」", "hant": "」", "en": "”"},
    "matchCount": {"hans": " 名匹配", "hant": " 名符合", "en": " matches"},
    "searchPlaceholder": {
        "hans": "搜索角色 · 中文名 / English",
        "hant": "搜尋角色 · 中文名 / English",
        "en": "Search fighters · name or alias",
    },
    "demoCap": {
        "hans": "示例 · 月燕（凌晓雨）",
        "hant": "範例 · 月燕（凌曉雨）",
        "en": "Example · Rainbow Kick (Xiaoyu)",
    },
    "keyLP": {"hans": "左拳 LP", "hant": "左拳 LP", "en": "Left punch LP"},
    "keyRP": {"hans": "右拳 RP", "hant": "右拳 RP", "en": "Right punch RP"},
    "keyLK": {"hans": "左脚 LK", "hant": "左腳 LK", "en": "Left kick LK"},
    "keyRK": {"hans": "右脚 RK", "hant": "右腳 RK", "en": "Right kick RK"},
    "footerTitle": {
        "hans": "非官方《铁拳 8》中文出招参考",
        "hant": "非官方《鐵拳 8》中文出招參考",
        "en": "An unofficial TEKKEN 8 movelist reference",
    },
    # The disclaimer is a rights statement, so the English wording is taken
    # verbatim from README.md rather than translated here. The links inside it
    # are preserved by matching only the text around them.
    "footerSource": {
        "hans": "招式数据整理自 ",
        "hant": "招式資料整理自 ",
        "en": "Movelist data is compiled from ",
    },
    "footerSourceTail": {
        "hans": "；中文招式名为非官方意译，仅供参考。",
        "hant": "；中文招式名為非官方意譯，僅供參考。",
        "en": (
            ". Chinese move names are unofficial reference interpretations. "
            "Character portraits are unofficial generative-AI outline-style "
            "interpretations created for this project."
        ),
    },
    "footerFan": {
        "hans": "角色头像为非官方同人艺术演绎。本项目仅供个人学习、研究与交流，不作商业用途；与 ",
        "hant": "角色頭像為非官方同人藝術演繹。本專案僅供個人學習、研究與交流，不作商業用途；與 ",
        "en": (
            "This is a non-commercial, unofficial fan project for personal "
            "study, research, and discussion. It is not affiliated with, "
            "sponsored by, or endorsed by "
        ),
    },
    "footerFanTail": {
        "hans": " 无隶属关系，亦未获其赞助或认可。",
        "hant": " 無隸屬關係，亦未獲其贊助或認可。",
        "en": ".",
    },
    "footerLegal": {
        "hans": " 及其角色、名称、商标与原始设计的相关权利归 Bandai Namco Entertainment Inc. 及其他相应权利人所有。",
        "hant": " 及其角色、名稱、商標與原始設計的相關權利歸 Bandai Namco Entertainment Inc. 及其他相應權利人所有。",
        "en": (
            " and its characters, names, trademarks, and original designs "
            "belong to Bandai Namco Entertainment Inc. and their respective "
            "rights holders."
        ),
    },
    "footerAria": {
        "hans": "项目来源与法律声明",
        "hant": "專案來源與法律聲明",
        "en": "Sources and legal notice",
    },
    "pageTitle": {
        "hans": "铁拳8 全角色中文出招表｜TEKKEN 8 Movelist",
        "hant": "鐵拳8 全角色中文出招表｜TEKKEN 8 Movelist",
        "en": "TEKKEN 8 Movelist · Frame Data & Command List",
    },
    # The head block: everything a crawler, a link preview or a screen reader
    # reads before the page renders. Missed in the first pass because it is
    # invisible on screen -- which is exactly why it needed the audit.
    "metaDescription": {
        "hans": (
            "铁拳8（TEKKEN 8）全角色中文出招表，提供高质量中文招式名、图形化四键映射、"
            "带数字、无数字与纯英文三种记法，以及发生帧、判定、伤害、投技、架势、"
            "Heat 招式与示例连招。"
        ),
        "hant": (
            "鐵拳8（TEKKEN 8）全角色中文出招表，提供高品質中文招式名、圖形化四鍵對應、"
            "帶數字、無數字與純英文三種記法，以及發生幀、判定、傷害、投技、架勢、"
            "Heat 招式與範例連招。"
        ),
        "en": (
            "The complete TEKKEN 8 movelist for every fighter: graphical "
            "button notation, startup frames, hit levels, damage, throws, "
            "stances, Heat moves and sample combos."
        ),
    },
    "siteName": {
        "hans": "铁拳8 全角色中文出招表",
        "hant": "鐵拳8 全角色中文出招表",
        "en": "TEKKEN 8 Movelist",
    },
    "shareDescription": {
        "hans": "高质量中文招式名、图形化四键映射与三种输入记法，一页查看完整招式与帧数资料。",
        "hant": "高品質中文招式名、圖形化四鍵對應與三種輸入記法，一頁查看完整招式與幀數資料。",
        "en": (
            "Graphical button notation, startup frames and full frame data "
            "for all 41 fighters, one page each."
        ),
    },
    "imageAlt": {
        "hans": "铁拳8 全角色中文出招表角色选择页",
        "hant": "鐵拳8 全角色中文出招表角色選擇頁",
        "en": "TEKKEN 8 Movelist fighter select",
    },
}

# The count line carries two numbers the build knows; keep them substituted
# rather than hard-coded so a new character does not need this file edited.
COUNT_LINE = {
    "hans": "{pages} 页出招表 · 共 {fighters} 名角色",
    "hant": "{pages} 頁出招表 · 共 {fighters} 名角色",
    "en": "{pages} movelists · {fighters} fighters",
}


def locale_control(locale: str) -> str:
    """The hub's language group, shaped like the notation control beside it."""
    items = []
    for code, meta in LOCALES.items():
        label = meta["short"]
        href = page_href(locale, code, "index.html")
        if code == locale:
            items.append(f'<button type="button" class="on" aria-current="true" disabled>{label}</button>')
        else:
            items.append(f'<a href="{href}" lang="{meta["lang"]}" hreflang="{meta["hreflang"]}">{label}</a>')
    label = HUB_STRINGS["languageLabel"][locale]
    return (
        '<div class="grp">'
        f'<span class="lbl">{label}</span>'
        f'<span class="seg lseg" role="group" aria-label="{strings(locale)["localeAria"]}">'
        + "".join(items)
        + "</span></div>"
    )


def strip_tags(fragment: str) -> str:
    return re.sub(r"<[^>]+>", "", fragment).strip()
