# -*- coding: utf-8 -*-
"""Locale table and hand-written chrome vocabulary for the trilingual site.

Three columns, one place.

**The Simplified column is byte-identical to the literals the generator carried
before this file existed.** That is not a nicety -- it is the acceptance test
for the whole locale refactor: a Simplified page rebuilt through this table
must not change by a single byte, because those URLs hold the site's current
rankings and the spec forbids moving them.

Chrome is authored in all three columns rather than machine-converted between
the Chinese variants. 记法 -> 記法 is mechanical, but 数据 -> 資料 and
视频 -> 影片 are Taiwan vocabulary, not character mapping, and no converter
knows which of those a given string wants. The *corpus* -- move, section and
stance names -- is a different matter and does go through `zh_hant.convert`.

Adding a fourth locale is meant to be config-only: append to `LOCALES`, add a
column to every table below, and the generator picks it up.
"""

from __future__ import annotations

from collections import OrderedDict

PUBLIC_ROOT = "https://tekken8movelist.github.io/"
DEFAULT_LOCALE = "hans"


LOCALES = OrderedDict(
    [
        (
            "hans",
            {
                "lang": "zh-CN",
                # the publish root: these URLs must never move
                "dir": "",
                "og": "zh_CN",
                "hreflang": "zh-Hans",
                "short": "简",
                "body_class": "",
            },
        ),
        (
            "hant",
            {
                "lang": "zh-Hant",
                "dir": "zh-Hant",
                "og": "zh_TW",
                "hreflang": "zh-Hant",
                "short": "繁",
                "body_class": "loc-hant",
            },
        ),
        (
            "en",
            {
                "lang": "en",
                "dir": "en",
                "og": "en_US",
                "hreflang": "en",
                "short": "EN",
                "body_class": "loc-en",
            },
        ),
    ]
)


# ---------------------------------------------------------------------------
# Hit-level vocabulary.
#
# The Chinese pages show one glyph per level and put the full reading in a
# title. English spells the level out instead -- 上/中/下 are as short as a
# glyph gets, H/M/L would read as an abbreviation of something the reader has
# not been told. Uppercase Wavu targets (M, L) mean "hits grounded", which is
# why several titles carry a parenthetical the label does not.
# ---------------------------------------------------------------------------

_TARGET_LABELS_ZH = {
    "sm": "特中",
    "sl": "特下",
    "h": "上",
    "m": "中",
    "l": "下",
    "t": "投",
    "sp": "特",
}

_TARGET_LABELS_HANT = {
    "sm": "特中",
    "sl": "特下",
    "h": "上",
    "m": "中",
    "l": "下",
    "t": "投",
    "sp": "特",
}

_TARGET_LABELS_EN = {
    "sm": "Sp. mid",
    "sl": "Sp. low",
    "h": "High",
    "m": "Mid",
    "l": "Low",
    "t": "Throw",
    "sp": "Sp.",
}

_TARGET_TITLES_ZH = {
    "!": "不可防",
    "h": "上",
    "h!": "上（不可防）",
    "m": "中",
    "m!": "中（不可防）",
    "l": "下",
    "l (t)": "下（龙卷）",
    "m (t)": "中（龙卷）",
    "t": "投",
    "t!": "投（不可防）",
    "t(a)": "空中投",
    "t(s)": "站立投",
    "t(w)": "墙边投",
    "th": "上段投",
    "th(g)": "地面投",
    "th(h)": "上段投",
    "th(m)": "中段投",
    "sm": "特中",
    "sl": "特下",
    "SM": "特中（可击中倒地）",
    "SL": "特下（可击中倒地）",
    "sp": "特殊动作",
}

_TARGET_TITLES_HANT = {
    "!": "不可防",
    "h": "上",
    "h!": "上（不可防）",
    "m": "中",
    "m!": "中（不可防）",
    "l": "下",
    "l (t)": "下（龍捲）",
    "m (t)": "中（龍捲）",
    "t": "投",
    "t!": "投（不可防）",
    "t(a)": "空中投",
    "t(s)": "站立投",
    "t(w)": "牆邊投",
    "th": "上段投",
    "th(g)": "地面投",
    "th(h)": "上段投",
    "th(m)": "中段投",
    "sm": "特中",
    "sl": "特下",
    "SM": "特中（可擊中倒地）",
    "SL": "特下（可擊中倒地）",
    "sp": "特殊動作",
}

_TARGET_TITLES_EN = {
    "!": "Unblockable",
    "h": "High",
    "h!": "High (unblockable)",
    "m": "Mid",
    "m!": "Mid (unblockable)",
    "l": "Low",
    "l (t)": "Low (tornado)",
    "m (t)": "Mid (tornado)",
    "t": "Throw",
    "t!": "Throw (unblockable)",
    "t(a)": "Air throw",
    "t(s)": "Standing throw",
    "t(w)": "Wall throw",
    "th": "High throw",
    "th(g)": "Ground throw",
    "th(h)": "High throw",
    "th(m)": "Mid throw",
    "sm": "Special mid",
    "sl": "Special low",
    "SM": "Special mid (hits grounded)",
    "SL": "Special low (hits grounded)",
    "sp": "Special move",
}


STRINGS: dict[str, dict[str, object]] = {
    # -------------------------------------------------------------------
    "hans": {
        # --- navigation and the title band ---
        "crumb": "全角色出招表",
        "crumbShort": "全角色",
        "crumbAria": "返回全角色选择",
        "quickNav": "快速导航",
        "localeAria": "语言 / Language",
        "themeLabel": "主题",
        "themeAria": "主题",
        "themeDark": "夜间",
        "themeLight": "浅色",
        "notationLabel": "记法",
        "notationAria": "指令记法",
        "ntGfx": "按键图",
        "ntNn": "无数字",
        "ntTxt": "文字",
        "pageKind": "铁拳 8 出招表",
        "bioCountry": "国家",
        "bioStyle": "拳法",
        "bioStances": "架势",
        "heroAltSuffix": " · 飞白轮廓角色像",
        # --- section headings; `Alt` is the other-locale line, not "English" ---
        "secThrows": "投技",
        "secThrowsAlt": "THROWS",
        "secAttacks": "打击技",
        "secAttacksAlt": "ATTACKS",
        "secHeat": "热能系统",
        "secHeatAlt": "HEAT",
        "secTen": "十连技",
        "secTenAlt": "10 HIT COMBO",
        "secCombos": "连招",
        "secCombosAlt": "COMBOS",
        "secTips": "进阶攻略",
        "secTipsSub": " · Wavu Wiki 连招数据",
        # --- table headers ---
        "thMove": "招式",
        "thInput": "指令",
        "thStartup": "发生",
        "thDmg": "伤害",
        "thLevel": "判定",
        "thSide": "方向",
        "thBreak": "挣脱",
        # --- hit levels ---
        "targetLabels": _TARGET_LABELS_ZH,
        "targetTitles": _TARGET_TITLES_ZH,
        "targetGrounded": "（倒地）",
        "targetJoin": "、",
        "dash": "—",
        # --- throws ---
        "throwFront": "正面",
        "throwLeft": "左侧",
        "throwRight": "右侧",
        "throwBack": "背后",
        "throwAir": "空中",
        "throwGround": "地面",
        "throwCrouch": "蹲姿",
        "throwWall": "墙边",
        "breakNone": "不可挣脱",
        "breakOr": "或",
        "breakOpposite": "首/末异键",
        "breakLabel": "挣脱 {value}",
        "breakUnknownTitle": "Wavu 未注明挣脱键",
        # --- combos ---
        "comboStarter": "起手",
        "comboRoute": "路线（[数字]=伤害 · T!=回旋 · ~F=按住前 · →=下一招）",
        "comboGeneric": "通用",
        "comboMarkerPrefix": "<br><b>标记</b>：",
        "comboEmpty": (
            "Wavu 连招页当前没有可用路线；占位文本已剔除。"
            "为避免编造，本页暂不补写未经来源验证的连招。"
        ),
        "comboNote": (
            "仅收录 Wavu 连招页实际存在的 {count} 条路线；"
            "原始记法与伤害标注保持不变（方括号数字为该段伤害，如 [25]），"
            "占位内容已剔除，不补写未经来源验证的打法。"
        ),
        # --- legend ---
        "legendJudgementLabel": "判定",
        "legendJudgement": (
            '<span class="hi">上</span>=上段　<span class="md">中</span>=中段　'
            '<span class="lo">下</span>=下段　<span class="sp">特</span>=特殊　'
            '<span class="sp">投</span>=投掷　<span class="sp">!</span>=不可防御'
        ),
        "legendStartupLabel": "发生",
        "legendStartup": "首击冲击帧（i=impact，越小越快，依 Wavu）",
        "legendCount": "{moves} 条源记录 / {visible} 条表内招式 / {frames} 条有发生帧{collapsed}",
        "legendCollapsed": "；十连技的 {count} 条递进源卡合并为完整招式",
        "legendKeys": (
            "<span><b>按键 · 方向</b>　1=左拳　2=右拳　3=左脚　4=右脚　|　"
            "f=前　b=后　u=上　d=下　d/f=前下　d/b=后下　u/f=前上　u/b=后上</span>"
            "<span><b>状态 · 分隔</b>　f,f=前冲　WS=起身中　FC=蹲伏中　SS=横移中　"
            "+=同时按　~=紧接　＊蓄力</span>"
        ),
        "legendGfxLabel": "图形记法",
        "legendGrid": "四键方阵（左上1 右上2 左下3 右下4，亮=按下）",
        "legendTap": "=轻点方向",
        "legendHold": "=按住",
        "legendNeutral": "=回中",
        "legendStanceChip": "架势中",
        "legendStance": "=状态前缀",
        "legendSepLabel": "分隔",
        "legendSeps": "› 接续　+ 方向＋键　~ 紧接　＊蓄力　→ 下一招",
        "legendTornado": "回旋",
        # --- SEO, footer, intro ---
        "siteName": "铁拳8 全角色中文出招表",
        "titleTemplate": "铁拳8 {display}（{canonical}）出招表 | TEKKEN 8 {canonical} Movelist",
        "descriptionTemplate": (
            "{display}（{canonical}）《铁拳8》（TEKKEN 8）完整出招表："
            "招式指令、帧数表、确反数据与进阶连招。"
            "Complete TEKKEN 8 {canonical} movelist with frame data."
        ),
        "ogImageAltTemplate": "铁拳8 {display}（{canonical}）头像",
        "breadcrumbHome": "首页",
        "breadcrumbPageTemplate": "{display}出招表",
        "introPrimaryTemplate": (
            "本页收录《铁拳8》（TEKKEN 8）{display}（{canonical}）"
            "的完整出招表与帧数表（frame data），并整理进阶连招与实战技巧，"
            "供对局间隙快速查阅。"
        ),
        "introSecondaryTemplate": (
            "The complete TEKKEN 8 {canonical} movelist — "
            "full command list, frame data, and combos, written in Chinese."
        ),
        "footSource": "数据来源：",
        "footSourceLink": "Wavu Wiki movelist",
        "footCombos": "打法参考：",
        "footCombosLink": "Wavu Wiki combos",
        "footProfile": "角色资料（国家 · 拳法）来自 ",
        "footOfficial": "TEKKEN 8 官方网站",
        "footNote": "招式名为中文意译，供参考；发生帧表示首击冲击帧。",
        "zhTagTitle": "",
    },
    # -------------------------------------------------------------------
    "hant": {
        "crumb": "全角色出招表",
        "crumbShort": "全角色",
        "crumbAria": "返回全角色選擇",
        "quickNav": "快速導航",
        "localeAria": "語言 / Language",
        "themeLabel": "主題",
        "themeAria": "主題",
        "themeDark": "夜間",
        "themeLight": "淺色",
        "notationLabel": "記法",
        "notationAria": "指令記法",
        "ntGfx": "按鍵圖",
        "ntNn": "無數字",
        "ntTxt": "文字",
        "pageKind": "鐵拳 8 出招表",
        "bioCountry": "國家",
        "bioStyle": "拳法",
        "bioStances": "架勢",
        "heroAltSuffix": " · 飛白輪廓角色像",
        "secThrows": "投技",
        "secThrowsAlt": "THROWS",
        "secAttacks": "打擊技",
        "secAttacksAlt": "ATTACKS",
        "secHeat": "熱能系統",
        "secHeatAlt": "HEAT",
        "secTen": "十連技",
        "secTenAlt": "10 HIT COMBO",
        "secCombos": "連招",
        "secCombosAlt": "COMBOS",
        "secTips": "進階攻略",
        "secTipsSub": " · Wavu Wiki 連招資料",
        "thMove": "招式",
        "thInput": "指令",
        "thStartup": "發生",
        "thDmg": "傷害",
        "thLevel": "判定",
        "thSide": "方向",
        "thBreak": "掙脫",
        "targetLabels": _TARGET_LABELS_HANT,
        "targetTitles": _TARGET_TITLES_HANT,
        "targetGrounded": "（倒地）",
        "targetJoin": "、",
        "dash": "—",
        "throwFront": "正面",
        "throwLeft": "左側",
        "throwRight": "右側",
        "throwBack": "背後",
        "throwAir": "空中",
        "throwGround": "地面",
        "throwCrouch": "蹲姿",
        "throwWall": "牆邊",
        "breakNone": "不可掙脫",
        "breakOr": "或",
        "breakOpposite": "首/末異鍵",
        "breakLabel": "掙脫 {value}",
        "breakUnknownTitle": "Wavu 未註明掙脫鍵",
        "comboStarter": "起手",
        "comboRoute": "路線（[數字]=傷害 · T!=迴旋 · ~F=按住前 · →=下一招）",
        "comboGeneric": "通用",
        "comboMarkerPrefix": "<br><b>標記</b>：",
        "comboEmpty": (
            "Wavu 連招頁目前沒有可用路線；佔位文字已剔除。"
            "為避免編造，本頁暫不補寫未經來源驗證的連招。"
        ),
        "comboNote": (
            "僅收錄 Wavu 連招頁實際存在的 {count} 條路線；"
            "原始記法與傷害標註保持不變（方括號數字為該段傷害，如 [25]），"
            "佔位內容已剔除，不補寫未經來源驗證的打法。"
        ),
        "legendJudgementLabel": "判定",
        "legendJudgement": (
            '<span class="hi">上</span>=上段　<span class="md">中</span>=中段　'
            '<span class="lo">下</span>=下段　<span class="sp">特</span>=特殊　'
            '<span class="sp">投</span>=投擲　<span class="sp">!</span>=不可防禦'
        ),
        "legendStartupLabel": "發生",
        "legendStartup": "首擊衝擊幀（i=impact，越小越快，依 Wavu）",
        "legendCount": "{moves} 條源紀錄 / {visible} 條表內招式 / {frames} 條有發生幀{collapsed}",
        "legendCollapsed": "；十連技的 {count} 條遞進來源卡合併為完整招式",
        "legendKeys": (
            "<span><b>按鍵 · 方向</b>　1=左拳　2=右拳　3=左腳　4=右腳　|　"
            "f=前　b=後　u=上　d=下　d/f=前下　d/b=後下　u/f=前上　u/b=後上</span>"
            "<span><b>狀態 · 分隔</b>　f,f=前衝　WS=起身中　FC=蹲伏中　SS=橫移中　"
            "+=同時按　~=緊接　＊蓄力</span>"
        ),
        "legendGfxLabel": "圖形記法",
        "legendGrid": "四鍵方陣（左上1 右上2 左下3 右下4，亮=按下）",
        "legendTap": "=輕點方向",
        "legendHold": "=按住",
        "legendNeutral": "=回中",
        "legendStanceChip": "架勢中",
        "legendStance": "=狀態前綴",
        "legendSepLabel": "分隔",
        "legendSeps": "› 接續　+ 方向＋鍵　~ 緊接　＊蓄力　→ 下一招",
        "legendTornado": "迴旋",
        "siteName": "鐵拳8 全角色中文出招表",
        "titleTemplate": "鐵拳8 {display}（{canonical}）出招表 | TEKKEN 8 {canonical} Movelist",
        "descriptionTemplate": (
            "{display}（{canonical}）《鐵拳8》（TEKKEN 8）完整出招表："
            "招式指令、幀數表、確反資料與進階連招。"
            "Complete TEKKEN 8 {canonical} movelist with frame data."
        ),
        "ogImageAltTemplate": "鐵拳8 {display}（{canonical}）頭像",
        "breadcrumbHome": "首頁",
        "breadcrumbPageTemplate": "{display}出招表",
        "introPrimaryTemplate": (
            "本頁收錄《鐵拳8》（TEKKEN 8）{display}（{canonical}）"
            "的完整出招表與幀數表（frame data），並整理進階連招與實戰技巧，"
            "供對局間隙快速查閱。"
        ),
        "introSecondaryTemplate": (
            "The complete TEKKEN 8 {canonical} movelist — "
            "full command list, frame data, and combos, written in Chinese."
        ),
        "footSource": "資料來源：",
        "footSourceLink": "Wavu Wiki movelist",
        "footCombos": "打法參考：",
        "footCombosLink": "Wavu Wiki combos",
        "footProfile": "角色資料（國家 · 拳法）來自 ",
        "footOfficial": "TEKKEN 8 官方網站",
        "footNote": "招式名為中文意譯，供參考；發生幀表示首擊衝擊幀。",
        "zhTagTitle": "",
    },
    # -------------------------------------------------------------------
    "en": {
        "crumb": "All fighters",
        "crumbShort": "All fighters",
        "crumbAria": "Back to the fighter list",
        "quickNav": "Quick navigation",
        "localeAria": "Language / 语言",
        "themeLabel": "Theme",
        "themeAria": "Theme",
        "themeDark": "Dark",
        "themeLight": "Light",
        "notationLabel": "Notation",
        "notationAria": "Command notation",
        "ntGfx": "Buttons",
        "ntNn": "No digits",
        "ntTxt": "Text",
        "pageKind": "TEKKEN 8 movelist",
        "bioCountry": "COUNTRY",
        "bioStyle": "STYLE",
        "bioStances": "STANCES",
        "heroAltSuffix": " · flying-white outline portrait",
        # the `Alt` line is the other locale, so on the English pages it is
        # Chinese -- the two-tier heading still says two things
        "secThrows": "Throws",
        "secThrowsAlt": "投技",
        "secAttacks": "Attacks",
        "secAttacksAlt": "打击技",
        "secHeat": "Heat",
        "secHeatAlt": "热能系统",
        "secTen": "10-hit combo",
        "secTenAlt": "十连技",
        "secCombos": "Combos",
        "secCombosAlt": "连招",
        "secTips": "Combos & notes",
        "secTipsSub": " · Wavu Wiki combo data",
        "thMove": "Move",
        "thInput": "Input",
        "thStartup": "i",
        "thDmg": "Dmg",
        "thLevel": "Hit",
        "thSide": "Side",
        "thBreak": "Break",
        "targetLabels": _TARGET_LABELS_EN,
        "targetTitles": _TARGET_TITLES_EN,
        "targetGrounded": " (hits grounded)",
        "targetJoin": ", ",
        "dash": "—",
        "throwFront": "Front",
        "throwLeft": "Left",
        "throwRight": "Right",
        "throwBack": "Back",
        "throwAir": "Air",
        "throwGround": "Ground",
        "throwCrouch": "Crouching",
        "throwWall": "Wall",
        "breakNone": "No break",
        "breakOr": " or ",
        "breakOpposite": "Opposite of first/last",
        "breakLabel": "Break {value}",
        "breakUnknownTitle": "Wavu does not state the break",
        "comboStarter": "Starter",
        "comboRoute": "Route ([n]=damage · T!=tornado · ~F=hold forward · →=next move)",
        "comboGeneric": "Any",
        "comboMarkerPrefix": "<br><b>Markers</b>: ",
        "comboEmpty": (
            "Wavu's combo page currently lists no usable routes, and its "
            "placeholder text has been stripped. Nothing unsourced is written "
            "in to fill the gap."
        ),
        "comboNote": (
            "Only the {count} routes Wavu's combo page actually lists. Wavu's "
            "own notation and damage annotations are unchanged (a bracketed "
            "number is that hit's damage, e.g. [25]); placeholder content is "
            "stripped and nothing unsourced is added."
        ),
        "legendJudgementLabel": "Hit level",
        "legendJudgement": (
            '<span class="hi">High</span>　<span class="md">Mid</span>　'
            '<span class="lo">Low</span>　<span class="sp">Sp.</span>=special　'
            '<span class="sp">Throw</span>　<span class="sp">!</span>=unblockable'
        ),
        "legendStartupLabel": "i",
        "legendStartup": "startup frames to first impact — lower is faster, per Wavu",
        "legendCount": "{moves} source records / {visible} listed moves / {frames} with startup{collapsed}",
        "legendCollapsed": "; the 10-hit string's {count} progressive source cards are merged into whole moves",
        "legendKeys": (
            "<span><b>Buttons · directions</b>　1=left punch　2=right punch　"
            "3=left kick　4=right kick　|　f=forward　b=back　u=up　d=down　"
            "d/f=down-forward　d/b=down-back　u/f=up-forward　u/b=up-back</span>"
            "<span><b>States · separators</b>　f,f=dash　WS=while standing　"
            "FC=full crouch　SS=sidestep　+=together　~=immediately after　"
            "＊=charge</span>"
        ),
        "legendGfxLabel": "Notation",
        "legendGrid": "four-button grid (1 LP, 2 RP, 3 LK, 4 RK — lit = pressed)",
        "legendTap": "= tap direction",
        "legendHold": "= hold",
        "legendNeutral": "= neutral",
        "legendStanceChip": "STANCE",
        "legendStance": "= state prefix",
        "legendSepLabel": "Separators",
        "legendSeps": "› follow-up　+ direction & button　~ immediately after　＊ charge　→ next move",
        "legendTornado": "tornado",
        # the site name in English is also the search term; "中文" would be a
        # lie here and costs the phrase people actually type
        "siteName": "TEKKEN 8 Movelist · Frame Data & Command List",
        "titleTemplate": "TEKKEN 8 {canonical} Movelist · Frame Data & Command List",
        "descriptionTemplate": (
            "The complete TEKKEN 8 {canonical} movelist: every command, "
            "startup frames, damage and hit level, plus throws, stances, "
            "Heat moves and sample combos on one page."
        ),
        "ogImageAltTemplate": "TEKKEN 8 {canonical} portrait",
        "breadcrumbHome": "Home",
        "breadcrumbPageTemplate": "{canonical} movelist",
        "introPrimaryTemplate": (
            "The complete TEKKEN 8 {canonical} movelist: every command, "
            "startup frames, damage and hit level, plus throws, stances, "
            "Heat moves and sample combos on one page."
        ),
        "introSecondaryTemplate": (
            "本页为《铁拳8》{display}出招表的英文版，"
            "招式名与判定取自 Wavu Wiki 原文。"
        ),
        "footSource": "Data: ",
        "footSourceLink": "Wavu Wiki movelist",
        "footCombos": "Combos: ",
        "footCombosLink": "Wavu Wiki combos",
        "footProfile": "Fighter profile (country · style) from the ",
        "footOfficial": "TEKKEN 8 official site",
        "footNote": (
            "English move names are Wavu Wiki's; startup is frames to first "
            "impact."
        ),
        # only the English build can show this tag, so only it needs the text
        "zhTagTitle": (
            "Wavu publishes no English name for this move; the project's "
            "Chinese reference name is shown"
        ),
    },
}


def strings(locale: str) -> dict[str, object]:
    return STRINGS[locale]


def _depth(locale: str) -> int:
    return 1 if LOCALES[locale]["dir"] else 0


def page_href(from_locale: str, to_locale: str, filename: str) -> str:
    """Relative link between two locale trees.

    Relative, not absolute, so the tree works the same from a local `docs/`
    server, a `file://` copy and the published root -- the same reason
    AGENTS.md requires relative links on the hub.
    """
    if from_locale == to_locale:
        return filename
    directory = LOCALES[to_locale]["dir"]
    return "../" * _depth(from_locale) + (
        f"{directory}/{filename}" if directory else filename
    )


def asset_href(locale: str, path: str) -> str:
    """Assets live once, at the publish root; locale trees reach up to them."""
    return "../" * _depth(locale) + path


def public_url(locale: str, filename: str) -> str:
    directory = LOCALES[locale]["dir"]
    prefix = f"{directory}/" if directory else ""
    if filename == "index.html":
        return f"{PUBLIC_ROOT}{prefix}"
    return f"{PUBLIC_ROOT}{prefix}{filename}"


def alternate_links(filename: str) -> str:
    """The hreflang block every page in every locale carries.

    Identical across locales by design: a search engine that lands on any one
    of the three has to be able to see the other two, and x-default points at
    Simplified because that is where the existing rankings live.
    """
    links = [
        f'<link rel="alternate" hreflang="{meta["hreflang"]}" '
        f'href="{public_url(code, filename)}">'
        for code, meta in LOCALES.items()
    ]
    links.append(
        '<link rel="alternate" hreflang="x-default" '
        f'href="{public_url(DEFAULT_LOCALE, filename)}">'
    )
    return "\n".join(links)
