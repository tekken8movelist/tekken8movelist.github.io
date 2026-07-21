# -*- coding: utf-8 -*-
"""Static configuration for the Tekken 8 Season 2 page builder."""

from collections import OrderedDict
import re


CHARACTERS = OrderedDict(
    [
        (
            "jin",
            {
                "canonical": "Jin Kazama",
                "display": "风间仁",
                "filename": "jin_tk8_movelist.html",
                "css_class": "tk-char-jin",
                "accent": "#6fb3ff",
                "accent_ink": "#1e4067",
                "stance_sections": (
                    "CD (Breaking Step)",
                    "ZEN (Zenshin/Zanshin)",
                ),
                "throw_sections": ("Throws",),
            },
        ),
        (
            "anna",
            {
                "canonical": "Anna Williams",
                "display": "安娜·威廉斯",
                "filename": "anna_tk8_movelist.html",
                "css_class": "tk-char-anna",
                "accent": "#e07a8f",
                "accent_ink": "#6e2436",
                "stance_sections": (
                    "HAM (Hammer Chance)",
                    "CJM (Chaos Judgement)",
                    "TOM (Pleasure Time)",
                ),
                "throw_sections": ("Throws",),
            },
        ),
        (
            "fahkumram",
            {
                "canonical": "Fahkumram",
                "display": "法昆拉姆",
                "filename": "fahkumram_tk8_movelist.html",
                "css_class": "tk-char-fahkumram",
                "accent": "#6fe0c9",
                "accent_ink": "#175f55",
                "stance_sections": (
                    "GRF (Garuda Force)",
                    "RAM (Rama Stance)",
                ),
                "throw_sections": ("Throws",),
            },
        ),
        (
            "armor_king",
            {
                "canonical": "Armor King",
                "display": "铠甲王",
                "filename": "armorking_tk8_movelist.html",
                "css_class": "tk-char-armorking",
                "accent": "#7f8fb3",
                "accent_ink": "#31405f",
                "stance_sections": (
                    "BT (Back Turned)",
                    "CD (Beast Step / Crouch Dash)",
                    "BAD (Bad Jaguar)",
                ),
                "throw_sections": (
                    "Regular Throws",
                    "Command Throws",
                    "Ultimate Tackle",
                    "Crouch Throws",
                    "Ground Throws",
                    "Air throws",
                    "Dark Magma Drive (DMD)",
                ),
            },
        ),
        (
            "miary_zo",
            {
                "canonical": "Miary Zo",
                "display": "米亚莉·佐",
                "filename": "miaryzo_tk8_movelist.html",
                "css_class": "tk-char-miaryzo",
                "accent": "#c9e896",
                "accent_ink": "#49651f",
                "stance_sections": (
                    "MOR (Morengy Miroso)",
                    "BAO (Baobab Mihira)",
                    "WAL (Tromba)",
                ),
                "throw_sections": ("Throws",),
            },
        ),
        (
            "kazuya",
            {
                "canonical": "Kazuya Mishima",
                "display": "三岛一八",
                "filename": "kazuya_tk8_movelist.html",
                "css_class": "tk-char-kazuya",
                "accent": "#b18cff",
                "accent_ink": "#341b6a",
                "stance_sections": (
                    'Mist Step',
                    'Wind God Step',
                    'DVK (Devil Form)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "paul",
            {
                "canonical": "Paul Phoenix",
                "display": "保罗",
                "filename": "paul_tk8_movelist.html",
                "css_class": "tk-char-paul",
                "accent": "#ff8087",
                "accent_ink": "#6a1b1f",
                "stance_sections": (
                    'CS (Cormorant Step)',
                    'DPD (Deep Dive)',
                    'SWA (Sway)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "king",
            {
                "canonical": "King",
                "display": "金",
                "filename": "king_tk8_movelist.html",
                "css_class": "tk-char-king",
                "accent": "#e8a04c",
                "accent_ink": "#6a451b",
                "stance_sections": (
                    'CD (Beast Step/Crouch Dash)',
                    'BT (Back Turned)',
                    'JGS (Jaguar Step)',
                    'JGR (Jaguar Sprint/Jaguar Run)',
                ),
                "throw_sections": (
                    'Regular throws',
                    'Command throws',
                    'Ultimate Tackle',
                    'Crouch throws',
                    'Ground throws',
                    'Air throws',
                    'Chain throws',
                ),
            },
        ),
        (
            "lars",
            {
                "canonical": "Lars Alexandersson",
                "display": "拉斯",
                "filename": "lars_tk8_movelist.html",
                "css_class": "tk-char-lars",
                "accent": "#8fa8ff",
                "accent_ink": "#1b2c6a",
                "stance_sections": (
                    'DEN (Dynamic Entry)',
                    'SEN (Silent Entry)',
                    'LEN (Limited Entry)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "jack8",
            {
                "canonical": "Jack-8",
                "display": "杰克-8",
                "filename": "jack_tk8_movelist.html",
                "css_class": "tk-char-jack8",
                "accent": "#a9cf74",
                "accent_ink": "#475e27",
                "stance_sections": (
                    'GMH (Gamma Howl)',
                    'GMC (Gamma Charge)',
                    'SIT (Sit Down)',
                    'While Down (Face Up)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "nina",
            {
                "canonical": "Nina Williams",
                "display": "妮娜·威廉斯",
                "filename": "nina_tk8_movelist.html",
                "css_class": "tk-char-nina",
                "accent": "#d8a9ff",
                "accent_ink": "#461b6a",
                "stance_sections": (
                    'CD (Ducking Step)',
                    'SWA (Sway)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "leroy",
            {
                "canonical": "Leroy Smith",
                "display": "勒罗伊",
                "filename": "leroy_tk8_movelist.html",
                "css_class": "tk-char-leroy",
                "accent": "#9db4c9",
                "accent_ink": "#2e4356",
                "stance_sections": (
                    'HRM (Hermit)',
                    'SS or NMS (Nimble Shift)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "asuka",
            {
                "canonical": "Asuka Kazama",
                "display": "风间飞鸟",
                "filename": "asuka_tk8_movelist.html",
                "css_class": "tk-char-asuka",
                "accent": "#7fc4e8",
                "accent_ink": "#1b4f69",
                "stance_sections": (
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "lili",
            {
                "canonical": "Lili",
                "display": "莉莉",
                "filename": "lili_tk8_movelist.html",
                "css_class": "tk-char-lili",
                "accent": "#cdd6e0",
                "accent_ink": "#2e4156",
                "stance_sections": (
                    'DEW (Dew Glide)',
                    'RAB (Feisty Rabbit)',
                    'BT',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "bryan",
            {
                "canonical": "Bryan Fury",
                "display": "布莱恩",
                "filename": "bryan_tk8_movelist.html",
                "css_class": "tk-char-bryan",
                "accent": "#9ad0c2",
                "accent_ink": "#2e574c",
                "stance_sections": (
                    'SNE (Snake Eyes)',
                    'SLS (Slither Step)',
                    'SWA (Sway)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "hwoarang",
            {
                "canonical": "Hwoarang",
                "display": "花郎",
                "filename": "hwoarang_tk8_movelist.html",
                "css_class": "tk-char-hwoarang",
                "accent": "#ff8f4d",
                "accent_ink": "#6a381b",
                "stance_sections": (
                    'CD (Shark Step)',
                    'BT (Backturn Stance)',
                    'RFF (Right Stance)',
                    'LFS (Left Flamingo)',
                    'RFS (Right Flamingo)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "claudio",
            {
                "canonical": "Claudio Serafino",
                "display": "克劳迪奥",
                "filename": "claudio_tk8_movelist.html",
                "css_class": "tk-char-claudio",
                "accent": "#bcd4ff",
                "accent_ink": "#1b376a",
                "stance_sections": (
                    'STB (Starburst)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "azucena",
            {
                "canonical": "Azucena",
                "display": "阿苏塞娜",
                "filename": "azucena_tk8_movelist.html",
                "css_class": "tk-char-azucena",
                "accent": "#d9a878",
                "accent_ink": "#624223",
                "stance_sections": (
                    'LIB (Libertador)',
                    'BT',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "raven",
            {
                "canonical": "Raven",
                "display": "雷文",
                "filename": "raven_tk8_movelist.html",
                "css_class": "tk-char-raven",
                "accent": "#9f86d9",
                "accent_ink": "#372560",
                "stance_sections": (
                    'CD (Shadow Sprint)',
                    'SZN (Soulzone)',
                    'BT',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "leo",
            {
                "canonical": "Leo",
                "display": "雷欧",
                "filename": "leo_tk8_movelist.html",
                "css_class": "tk-char-leo",
                "accent": "#e0c187",
                "accent_ink": "#644c21",
                "stance_sections": (
                    'LTG (Lightning Glare)',
                    'KNK (Jin Ji Du Li)',
                    'BOK (Fo Bu)',
                    'CD (Jin Bu)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "steve",
            {
                "canonical": "Steve Fox",
                "display": "史蒂夫",
                "filename": "steve_tk8_movelist.html",
                "css_class": "tk-char-steve",
                "accent": "#84a9e0",
                "accent_ink": "#213c64",
                "stance_sections": (
                    'LWV (Ducking Left)',
                    'RWV (Ducking Right)',
                    'ALB (Quick Spin)',
                    'DCK (Ducking)',
                    'EXD (Ducking In)',
                    'PAB (Peekaboo)',
                    'SWY (Swaying)',
                    'FLK (Flicker Stance)',
                    'LNH (Lionheart)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "kuma",
            {
                "canonical": "Kuma",
                "display": "熊",
                "filename": "kuma_tk8_movelist.html",
                "css_class": "tk-char-kuma",
                "accent": "#c99b6e",
                "accent_ink": "#5c4229",
                "stance_sections": (
                    'HBS (Hunting)',
                    'SIT (Bear Sit)',
                    'ROL (Bear Roll)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "panda",
            {
                "canonical": "Panda",
                "display": "熊猫",
                "filename": "panda_tk8_movelist.html",
                "css_class": "tk-char-panda",
                "accent": "#e6e9ee",
                "accent_ink": "#2e3d56",
                "stance_sections": (
                    'HBS (Hunting)',
                    'SIT (Bear Sit)',
                    'ROL (Bear Roll)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "yoshimitsu",
            {
                "canonical": "Yoshimitsu",
                "display": "吉光",
                "filename": "yoshimitsu_tk8_movelist.html",
                "css_class": "tk-char-yoshi",
                "accent": "#7fd6a8",
                "accent_ink": "#255f41",
                "stance_sections": (
                    'KIN (Kincho)',
                    'MED (Meditation)',
                    'FLE (Flea)',
                    'IND (Indian Stance)',
                    'NSS (Mutou no Kiwami)',
                    'DGF (Manji Dragonfly)',
                    'BT',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "shaheen",
            {
                "canonical": "Shaheen",
                "display": "沙欣",
                "filename": "shaheen_tk8_movelist.html",
                "css_class": "tk-char-shaheen",
                "accent": "#e8cf9a",
                "accent_ink": "#664f1f",
                "stance_sections": (
                    'SNK (Stealth Step)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "dragunov",
            {
                "canonical": "Sergei Dragunov",
                "display": "德拉古诺夫",
                "filename": "dragunov_tk8_movelist.html",
                "css_class": "tk-char-dragunov",
                "accent": "#aab6c2",
                "accent_ink": "#2e4256",
                "stance_sections": (
                    'SNK (Sneak)',
                    'PGR (Pigeon Roll)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "feng",
            {
                "canonical": "Feng Wei",
                "display": "冯威",
                "filename": "feng_tk8_movelist.html",
                "css_class": "tk-char-feng",
                "accent": "#b5d98a",
                "accent_ink": "#455f26",
                "stance_sections": (
                    'CD (Lingering Shadow)',
                    'STC (Shifting Clouds)',
                    'KNP (Deceptive Step)',
                    'BT',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "lee",
            {
                "canonical": "Lee Chaolan",
                "display": "李超狼",
                "filename": "lee_tk8_movelist.html",
                "css_class": "tk-char-lee",
                "accent": "#c39bff",
                "accent_ink": "#3a1b6a",
                "stance_sections": (
                    'HMS (Hitman)',
                    'MS (Mist Step)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "alisa",
            {
                "canonical": "Alisa Bosconovitch",
                "display": "阿丽莎",
                "filename": "alisa_tk8_movelist.html",
                "css_class": "tk-char-alisa",
                "accent": "#ffb3c6",
                "accent_ink": "#6a1b2e",
                "stance_sections": (
                    'DES (Destructive Form)',
                    'SBT (Boot)',
                    'DBT (Dual Boot)',
                    'BKP (Backup)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "zafina",
            {
                "canonical": "Zafina",
                "display": "扎菲娜",
                "filename": "zafina_tk8_movelist.html",
                "css_class": "tk-char-zafina",
                "accent": "#c98fd0",
                "accent_ink": "#542b59",
                "stance_sections": (
                    'SCR (Scarecrow Stance)',
                    'TRT (Tarantula Stance)',
                    'MNT (Mantis Stance)',
                    'ORB (Anathema)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "devil_jin",
            {
                "canonical": "Devil Jin",
                "display": "恶魔仁",
                "filename": "deviljin_tk8_movelist.html",
                "css_class": "tk-char-deviljin",
                "accent": "#a17fe0",
                "accent_ink": "#382065",
                "stance_sections": (
                    'WGS (Wind God Step)',
                    'FLY (Fly)',
                    'MCR (Mourning Crow)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "victor",
            {
                "canonical": "Victor Chevalier",
                "display": "维克多",
                "filename": "victor_tk8_movelist.html",
                "css_class": "tk-char-victor",
                "accent": "#de9fe6",
                "accent_ink": "#5c2163",
                "stance_sections": (
                    'IAI (Iai Stance)',
                    'PRF (Perfumer)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "reina",
            {
                "canonical": "Reina",
                "display": "蕾娜",
                "filename": "reina_tk8_movelist.html",
                "css_class": "tk-char-reina",
                "accent": "#cf9ef0",
                "accent_ink": "#4a1b6a",
                "stance_sections": (
                    'WGS (Wind God Step)',
                    'SEN (Sentai)',
                    'SSH (Senshin)',
                    'UNS (Unsoku)',
                    "WRA (Heaven's Wrath)",
                    'WDS (Wind Step)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "eddy",
            {
                "canonical": "Eddy Gordo",
                "display": "艾迪",
                "filename": "eddy_tk8_movelist.html",
                "css_class": "tk-char-eddy",
                "accent": "#9fd97f",
                "accent_ink": "#396124",
                "stance_sections": (
                    'HSP (Bananeira)',
                    'RLX (Negativa)',
                    'MD (Mandinga)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "lidia",
            {
                "canonical": "Lidia Sobieska",
                "display": "莉迪亚",
                "filename": "lidia_tk8_movelist.html",
                "css_class": "tk-char-lidia",
                "accent": "#ffb0a6",
                "accent_ink": "#6a231b",
                "stance_sections": (
                    'HRS (Horse Stance)',
                    'CAT (Cat Stance)',
                    'WLF (Stalking Wolf Stance)',
                    'HAE (Heaven and Earth)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
        (
            "heihachi",
            {
                "canonical": "Heihachi Mishima",
                "display": "三岛平八",
                "filename": "heihachi_tk8_movelist.html",
                "css_class": "tk-char-heihachi",
                "accent": "#ffcf66",
                "accent_ink": "#6a511b",
                "stance_sections": (
                    'CD (Wind God Step)',
                    "RAI (Thunder God's Kamae)",
                    "FUJ (Wind God's Kamae)",
                    'WAR (Warrior Instinct)',
                ),
                "throw_sections": (
                    'Throws',
                ),
            },
        ),
    ]
)

COMMON_PREFIXES = OrderedDict(
    [
        ("(Back_to_wall).", "背墙时"),
        ("(Opponent_grounded).", "对手倒地时"),
        ("(Airborne).", "接近空中对手"),
        ("hFC.", "蹲伏中"),
        ("FC.", "蹲伏中"),
        ("BT.", "背身时"),
        ("SS.", "横移中"),
        ("WR.", "奔跑中"),
        ("CH.", "迎击时"),
        ("H.", "热能中"),
        ("R.", "愤怒中"),
    ]
)

COMMON_STATES = list(dict.fromkeys([*COMMON_PREFIXES.values(), "起身中", "横移左", "横移右"]))

COMMON_COMMAND_ALIASES = {
    "left_throw": "左侧 1+3 (或 2+4)",
    "right_throw": "右侧 1+3 (或 2+4)",
    "back_throw": "背后 1+3 (或 2+4)",
    # wavu id quirks, normalized for graphical rendering only (the raw
    # command text is always shown verbatim in text mode)
    "back_throw_1+3": "背后 1+3",
    "back_throw_2+4": "背后 2+4",
    "(during_enemy_wall_stun)_1+3": "对手撞墙硬直时 1+3",
    "d+3,1_(wall_stun)": "d+3,1 (对手撞墙时)",
    "fdft.3_(close)": "FDFT.3 (近身)",
    "after-2steps+1": "潜避两步后 1",
    "h.exdthrow.1": "H.TFA.1",
    "h.exdthrow.2": "H.TFA.2",
    "ut,2,1,2,1": "UT.2,1,2,1",
    "ut,1+2": "UT.1+2",
    "ut,1+2,1+2": "UT.1+2,1+2",
    "ut,3+4": "UT.3+4",
    "ut,3+4,1+2": "UT.3+4,1+2",
    "fufl/fufr.db+1+3": "FUFL.db+1+3",
    "fc.df,d,df${justframe}3": "FC.df,d,DF:3",
}

COMBO_SECTION_NAMES = {
    "Bread n' butter": "基础连招",
    "Bread n' Butter": "基础连招",
    "Mini-Combos": "小连段",
    "Back-turned Opponent": "背身对手",
    "Combo Theory": "连招理论",
    "Fake Combos": "伪连段",
    "Floor break": "破地连招",
    "Wall break": "破墙连招",
    "Heat": "热能连招",
    "Off Axis": "偏轴连招",
    "Off-Axis": "偏轴连招",
    "Slide": "滑铲连招",
    "Stage Hazard": "场景机关",
    "Wall Splat": "墙壁命中",
    "Mini-combos": "小连段",
    "Staples": "实战连招",
    "Wall": "墙边连招",
    "Float": "空中截击",
    "Back-turned opponent": "背身对手",
    "Backturned Opponent": "背身对手",
    "Stage hazard": "场景机关",
    "Floor Hazard": "地板机关",
    "Off-axis": "偏轴连招",
    "Wall Blast": "爆墙连招",
    "Wall Hazard": "墙壁机关",
    "Combo Enders": "连招收尾",
    "Followups": "后续追击",
    "Heat Combos": "热能连招",
    "Instant Tornado": "直接龙卷",
    "Regular Launch": "常规浮空",
    "Wall Combos": "墙边连招",
    "Extras": "补充连招",
}

PLACEHOLDER_COMBO = re.compile(
    r"^\s*combo\b|\b(?:goes here|combo here|placeholder|to be added|tbd)\b|\bcombo\b.*\bhere\b",
    re.I,
)
GLUED_COMBO_ANNOTATION = re.compile(
    r"(?:\d|\])(?:HARD|Close range|Backturned|With heat)\b|\S\(on lower hit\)",
    re.I,
)
KNOWN_AGGREGATE_DAMAGE = {
    "jin": {"Jin-H.2+3", "Jin-H.2+3,4", "Jin-R.df+1+2"},
    "anna": {"Anna-R.df+1+2", "Anna-uf+1+2"},
    "fahkumram": {
        "Fahkumram-H.2+3",
        "Fahkumram-b+1+3,P",
        "Fahkumram-GRF.1+2,P",
        "Fahkumram-R.df+1+2",
    },
    "armor_king": {
        "Armor_King-H.2+3",
        "Armor_King-f,hcf+1",
        "Armor_King-R.df+1+2",
        "Armor_King-(Back_to_wall).b,\u200bb,\u200bUB",
        "Armor_King-2+4,d+1+2",
        "Armor_King-f,hcf+1#2",
        "Armor_King-UT.2,1,2,1",
        "Armor_King-BM.2,1,2,1",
    },
    "miary_zo": {
        "Miary_Zo-H.2+3",
        "Miary_Zo-ub+1",
        "Miary_Zo-uf+1",
        "Miary_Zo-f,F+2,2",
        "Miary_Zo-R.df+1+2",
    },
    'kazuya': {'Kazuya-R.df+1+2'},
    'paul': {'Paul-R.df+1+2'},
    'king': {'King-AB1.1,1+2', 'King-Air.d+1+3,2,1,3,4', 'King-FUFT.db+1+3', 'King-MMD5.1+2,4,2,1+2', 'King-R.df+1+2', 'King-UT,2,1,2,1', 'King-b+2+4:3+4', 'King-f,hcf+1#2', 'King-f,hcf+1'},
    'lars': {'Lars-H.2+3', 'Lars-SEN.3+4', 'Lars-df+1+2', 'Lars-f,F+3+4', 'Lars-uf+3', 'Lars-uf+3+4,1+2', 'Lars-uf+3+4,4'},
    'jack8': {'Jack-8-H.2+3', 'Jack-8-R.df+1+2', 'Jack-8-db+3,d+1+2'},
    'nina': {'Nina-BHS.1+2', 'Nina-BHS.2', 'Nina-H.2+3', 'Nina-R.df+1+2', 'Nina-uf+1+2', 'Nina-ws3'},
    'leroy': {'Leroy-1+2', 'Leroy-1+2,1+2', 'Leroy-1+2,1+2,1#2', 'Leroy-1+2,1+2,1', 'Leroy-R.df+1+2', 'Leroy-df+3,1,4,1+2', 'Leroy-df+3,1,4,1+2,2', 'Leroy-df+3,1,4,1+2,2,1+2', 'Leroy-df+3,1,4,1+2,2,1+2,1+2'},
    'asuka': {'Asuka-FC.db+1+2', 'Asuka-H.2+3', 'Asuka-R.df+1+2#2', 'Asuka-R.df+1+2#3', 'Asuka-R.df+1+2'},
    'lili': {'Lili-3+4,H.3+4', 'Lili-H.2+3', 'Lili-R.df+1+2'},
    'bryan': {'Bryan-R.df+1+2'},
    'hwoarang': {'Hwoarang-H.2+3', 'Hwoarang-R.df+1+2'},
    'claudio': {'Claudio-H.2+3', 'Claudio-R.df+1+2', 'Claudio-f,F+2,1+2', 'Claudio-f,F+3,2', 'Claudio-f,F+3,2*'},
    'azucena': {'Azucena-R.df+1+2', 'Azucena-Tackle.2,1,2,1'},
    'raven': {'Raven-R.df+1+2'},
    'leo': {'Leo-R.df+1+2'},
    'steve': {'Steve-ALB.d,1', 'Steve-ALB.d,d+1', 'Steve-H.2+3', 'Steve-H.LNH.P#2', 'Steve-H.LNH.P', 'Steve-R.df+1+2'},
    'kuma': {'Kuma-H.2+3', 'Kuma-R.df+1+2'},
    'panda': {'Panda-R.df+1+2', 'Panda-db+1+2', 'Panda-db+1+2,1+2', 'Panda-db+1+2,1+2,2'},
    'yoshimitsu': {'Yoshimitsu-2,NSS.1', 'Yoshimitsu-H.2+3', 'Yoshimitsu-R.df+1+2'},
    'shaheen': {'Shaheen-H.2+3', 'Shaheen-H.f+1+2', 'Shaheen-R.df+1+2', 'Shaheen-b+2', 'Shaheen-f+3+4'},
    'dragunov': {'Dragunov-(During_enemy_wall_stun).f,f,F+4', 'Dragunov-R.df+1+2', 'Dragunov-SS.2,1+2,1+2'},
    'feng': {'Feng-R.df+1+2'},
    'lee': {'Lee-4,3,3', 'Lee-4,3,4', 'Lee-FC.UF+3+4', 'Lee-H.2+3', 'Lee-R.df+1+2'},
    'alisa': {'Alisa-BKP.1+2', 'Alisa-DBT.1', 'Alisa-DBT.2', 'Alisa-DBT.2,1', 'Alisa-DBT.4', 'Alisa-DBT.f+1', 'Alisa-DBT.f+1+2', 'Alisa-DES.1', 'Alisa-DES.d+1', 'Alisa-DES.f+1+2', 'Alisa-DES.f+1+2,1+2', 'Alisa-DES.f+2', 'Alisa-DES.f+2,1#2', 'Alisa-DES.f+2,1', 'Alisa-DES.f+2,1,2#2', 'Alisa-DES.f+2,1,2', 'Alisa-DES.uf+1+2', 'Alisa-R.df+1+2', 'Alisa-SBT.1,2,1,3+4', 'Alisa-SBT.4', 'Alisa-f,F+2,H.1+2'},
    'zafina': {'Zafina-H.2+3', 'Zafina-R.df+1+2', 'Zafina-b+1+2,ORB.1+2', 'Zafina-b+1:ORB.1+2', 'Zafina-b+3,ORB.1+2', 'Zafina-db+2,1+2', 'Zafina-df+1,2,1+2'},
    'devil_jin': {'Devil_Jin-R.df+1+2', 'Devil_Jin-b,f+1+2', 'Devil_Jin-b,f+1+2,2'},
    'victor': {'Victor-H.2+3', 'Victor-H.IAI.d+2', 'Victor-IAI.3', 'Victor-IAI.d+2', 'Victor-R.df+1+2', 'Victor-b+1,2'},
    'reina': {'Reina-R.df+1+2', 'Reina-SSH.CH.3', 'Reina-uf+3+4', 'Reina-uf+3+4,1+2'},
    'eddy': {'Eddy-R.df+1+2', 'Eddy-b+1,4,3+4', 'Eddy-b,B+2+3'},
    'lidia': {'Lidia-CH.db+3', 'Lidia-H.2+3', 'Lidia-R.df+1+2'},
    'heihachi': {'Heihachi-H.2+3', 'Heihachi-R.df+1+2'},
}
# verified against the wiki: genuinely huge single damage values (charged
# unblockables, lethal finishers), not glued join artifacts
KNOWN_BIG_DAMAGE = {
    "jack8": {"Jack-8-1+4*,1": "35/45/55/199"},
    "yoshimitsu": {
        "Yoshimitsu-d+1*(6),n": "200",
        "Yoshimitsu-f,F+1+4,F": "60,185",
    },
}

LATIN = re.compile(r"[A-Za-z]")

TARGET_TITLES = {
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
