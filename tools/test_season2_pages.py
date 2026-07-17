import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from html import escape
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

CHARACTERS = {
    "jin": {
        "display": "风间仁",
        "filename": "风间仁_铁拳8_出招表.html",
        "css_class": "tk-char-jin",
        "moves": 144,
        "visible": 135,
        "startup_coverage": 133,
        "combos_count": 44,
        "movelist": "https://wavu.wiki/t/Jin_movelist",
        "combos": "https://wavu.wiki/t/Jin_combos",
    },
    "anna": {
        "display": "安娜·威廉斯",
        "filename": "安娜·威廉斯_铁拳8_出招表.html",
        "css_class": "tk-char-anna",
        "moves": 183,
        "visible": 174,
        "startup_coverage": 169,
        "combos_count": 0,
        "movelist": "https://wavu.wiki/t/Anna_movelist",
        "combos": "https://wavu.wiki/t/Anna_combos",
    },
    "fahkumram": {
        "display": "法昆拉姆",
        "filename": "法昆拉姆_铁拳8_出招表.html",
        "css_class": "tk-char-fahkumram",
        "moves": 147,
        "visible": 147,
        "startup_coverage": 142,
        "combos_count": 15,
        "movelist": "https://wavu.wiki/t/Fahkumram_movelist",
        "combos": "https://wavu.wiki/t/Fahkumram_combos",
    },
    "armor_king": {
        "display": "铠甲王",
        "filename": "铠甲王_铁拳8_出招表.html",
        "css_class": "tk-char-armorking",
        "moves": 182,
        "visible": 182,
        "startup_coverage": 169,
        "combos_count": 63,
        "movelist": "https://wavu.wiki/t/Armor_King_movelist",
        "combos": "https://wavu.wiki/t/Armor_King_combos",
    },
    "miary_zo": {
        "display": "米亚莉·佐",
        "filename": "米亚莉·佐_铁拳8_出招表.html",
        "css_class": "tk-char-miaryzo",
        "moves": 130,
        "visible": 130,
        "startup_coverage": 115,
        "combos_count": 52,
        "movelist": "https://wavu.wiki/t/Miary_Zo_movelist",
        "combos": "https://wavu.wiki/t/Miary_Zo_combos",
    },
    "kazuya": {
        "display": "三岛一八",
        "filename": "三岛一八_铁拳8_出招表.html",
        "css_class": "tk-char-kazuya",
        "moves": 160,
        "visible": 143,
        "startup_coverage": 136,
        "combos_count": 27,
        "movelist": "https://wavu.wiki/t/Kazuya_movelist",
        "combos": "https://wavu.wiki/t/Kazuya_combos",
    },
    "paul": {
        "display": "保罗",
        "filename": "保罗_铁拳8_出招表.html",
        "css_class": "tk-char-paul",
        "moves": 177,
        "visible": 155,
        "startup_coverage": 141,
        "combos_count": 370,
        "movelist": "https://wavu.wiki/t/Paul_movelist",
        "combos": "https://wavu.wiki/t/Paul_combos",
    },
    "king": {
        "display": "金",
        "filename": "金_铁拳8_出招表.html",
        "css_class": "tk-char-king",
        "moves": 255,
        "visible": 236,
        "startup_coverage": 213,
        "combos_count": 66,
        "movelist": "https://wavu.wiki/t/King_movelist",
        "combos": "https://wavu.wiki/t/King_combos",
    },
    "lars": {
        "display": "拉斯",
        "filename": "拉斯_铁拳8_出招表.html",
        "css_class": "tk-char-lars",
        "moves": 140,
        "visible": 131,
        "startup_coverage": 130,
        "combos_count": 39,
        "movelist": "https://wavu.wiki/t/Lars_movelist",
        "combos": "https://wavu.wiki/t/Lars_combos",
    },
    "jack8": {
        "display": "杰克-8",
        "filename": "杰克-8_铁拳8_出招表.html",
        "css_class": "tk-char-jack8",
        "moves": 229,
        "visible": 220,
        "startup_coverage": 220,
        "combos_count": 48,
        "movelist": "https://wavu.wiki/t/Jack-8_movelist",
        "combos": "https://wavu.wiki/t/Jack-8_combos",
    },
    "nina": {
        "display": "妮娜·威廉斯",
        "filename": "妮娜·威廉斯_铁拳8_出招表.html",
        "css_class": "tk-char-nina",
        "moves": 211,
        "visible": 202,
        "startup_coverage": 186,
        "combos_count": 102,
        "movelist": "https://wavu.wiki/t/Nina_movelist",
        "combos": "https://wavu.wiki/t/Nina_combos",
    },
    "leroy": {
        "display": "勒罗伊",
        "filename": "勒罗伊_铁拳8_出招表.html",
        "css_class": "tk-char-leroy",
        "moves": 147,
        "visible": 141,
        "startup_coverage": 138,
        "combos_count": 42,
        "movelist": "https://wavu.wiki/t/Leroy_movelist",
        "combos": "https://wavu.wiki/t/Leroy_combos",
    },
    "asuka": {
        "display": "风间飞鸟",
        "filename": "风间飞鸟_铁拳8_出招表.html",
        "css_class": "tk-char-asuka",
        "moves": 163,
        "visible": 145,
        "startup_coverage": 156,
        "combos_count": 3,
        "movelist": "https://wavu.wiki/t/Asuka_movelist",
        "combos": "https://wavu.wiki/t/Asuka_combos",
    },
    "lili": {
        "display": "莉莉",
        "filename": "莉莉_铁拳8_出招表.html",
        "css_class": "tk-char-lili",
        "moves": 156,
        "visible": 156,
        "startup_coverage": 142,
        "combos_count": 22,
        "movelist": "https://wavu.wiki/t/Lili_movelist",
        "combos": "https://wavu.wiki/t/Lili_combos",
    },
    "bryan": {
        "display": "布莱恩",
        "filename": "布莱恩_铁拳8_出招表.html",
        "css_class": "tk-char-bryan",
        "moves": 175,
        "visible": 166,
        "startup_coverage": 168,
        "combos_count": 53,
        "movelist": "https://wavu.wiki/t/Bryan_movelist",
        "combos": "https://wavu.wiki/t/Bryan_combos",
    },
    "hwoarang": {
        "display": "花郎",
        "filename": "花郎_铁拳8_出招表.html",
        "css_class": "tk-char-hwoarang",
        "moves": 225,
        "visible": 216,
        "startup_coverage": 210,
        "combos_count": 64,
        "movelist": "https://wavu.wiki/t/Hwoarang_movelist",
        "combos": "https://wavu.wiki/t/Hwoarang_combos",
    },
    "claudio": {
        "display": "克劳迪奥",
        "filename": "克劳迪奥_铁拳8_出招表.html",
        "css_class": "tk-char-claudio",
        "moves": 117,
        "visible": 108,
        "startup_coverage": 103,
        "combos_count": 9,
        "movelist": "https://wavu.wiki/t/Claudio_movelist",
        "combos": "https://wavu.wiki/t/Claudio_combos",
    },
    "azucena": {
        "display": "阿苏塞娜",
        "filename": "阿苏塞娜_铁拳8_出招表.html",
        "css_class": "tk-char-azucena",
        "moves": 165,
        "visible": 156,
        "startup_coverage": 138,
        "combos_count": 103,
        "movelist": "https://wavu.wiki/t/Azucena_movelist",
        "combos": "https://wavu.wiki/t/Azucena_combos",
    },
    "raven": {
        "display": "雷文",
        "filename": "雷文_铁拳8_出招表.html",
        "css_class": "tk-char-raven",
        "moves": 195,
        "visible": 186,
        "startup_coverage": 172,
        "combos_count": 83,
        "movelist": "https://wavu.wiki/t/Raven_movelist",
        "combos": "https://wavu.wiki/t/Raven_combos",
    },
    "leo": {
        "display": "雷欧",
        "filename": "雷欧_铁拳8_出招表.html",
        "css_class": "tk-char-leo",
        "moves": 148,
        "visible": 148,
        "startup_coverage": 139,
        "combos_count": 67,
        "movelist": "https://wavu.wiki/t/Leo_movelist",
        "combos": "https://wavu.wiki/t/Leo_combos",
    },
    "steve": {
        "display": "史蒂夫",
        "filename": "史蒂夫_铁拳8_出招表.html",
        "css_class": "tk-char-steve",
        "moves": 189,
        "visible": 185,
        "startup_coverage": 165,
        "combos_count": 41,
        "movelist": "https://wavu.wiki/t/Steve_movelist",
        "combos": "https://wavu.wiki/t/Steve_combos",
    },
    "kuma": {
        "display": "熊",
        "filename": "熊_铁拳8_出招表.html",
        "css_class": "tk-char-kuma",
        "moves": 150,
        "visible": 141,
        "startup_coverage": 141,
        "combos_count": 8,
        "movelist": "https://wavu.wiki/t/Kuma_movelist",
        "combos": "https://wavu.wiki/t/Kuma_combos",
    },
    "panda": {
        "display": "熊猫",
        "filename": "熊猫_铁拳8_出招表.html",
        "css_class": "tk-char-panda",
        "moves": 144,
        "visible": 144,
        "startup_coverage": 134,
        "combos_count": 1,
        "movelist": "https://wavu.wiki/t/Panda_movelist",
        "combos": "https://wavu.wiki/t/Panda_combos",
    },
    "yoshimitsu": {
        "display": "吉光",
        "filename": "吉光_铁拳8_出招表.html",
        "css_class": "tk-char-yoshi",
        "moves": 376,
        "visible": 340,
        "startup_coverage": 330,
        "combos_count": 71,
        "movelist": "https://wavu.wiki/t/Yoshimitsu_movelist",
        "combos": "https://wavu.wiki/t/Yoshimitsu_combos",
    },
    "shaheen": {
        "display": "沙欣",
        "filename": "沙欣_铁拳8_出招表.html",
        "css_class": "tk-char-shaheen",
        "moves": 106,
        "visible": 97,
        "startup_coverage": 101,
        "combos_count": 30,
        "movelist": "https://wavu.wiki/t/Shaheen_movelist",
        "combos": "https://wavu.wiki/t/Shaheen_combos",
    },
    "dragunov": {
        "display": "德拉古诺夫",
        "filename": "德拉古诺夫_铁拳8_出招表.html",
        "css_class": "tk-char-dragunov",
        "moves": 165,
        "visible": 151,
        "startup_coverage": 153,
        "combos_count": 58,
        "movelist": "https://wavu.wiki/t/Dragunov_movelist",
        "combos": "https://wavu.wiki/t/Dragunov_combos",
    },
    "feng": {
        "display": "冯威",
        "filename": "冯威_铁拳8_出招表.html",
        "css_class": "tk-char-feng",
        "moves": 168,
        "visible": 159,
        "startup_coverage": 155,
        "combos_count": 42,
        "movelist": "https://wavu.wiki/t/Feng_movelist",
        "combos": "https://wavu.wiki/t/Feng_combos",
    },
    "lee": {
        "display": "李超狼",
        "filename": "李超狼_铁拳8_出招表.html",
        "css_class": "tk-char-lee",
        "moves": 174,
        "visible": 169,
        "startup_coverage": 162,
        "combos_count": 135,
        "movelist": "https://wavu.wiki/t/Lee_movelist",
        "combos": "https://wavu.wiki/t/Lee_combos",
    },
    "alisa": {
        "display": "阿丽莎",
        "filename": "阿丽莎_铁拳8_出招表.html",
        "css_class": "tk-char-alisa",
        "moves": 197,
        "visible": 188,
        "startup_coverage": 172,
        "combos_count": 49,
        "movelist": "https://wavu.wiki/t/Alisa_movelist",
        "combos": "https://wavu.wiki/t/Alisa_combos",
    },
    "zafina": {
        "display": "扎菲娜",
        "filename": "扎菲娜_铁拳8_出招表.html",
        "css_class": "tk-char-zafina",
        "moves": 164,
        "visible": 155,
        "startup_coverage": 150,
        "combos_count": 64,
        "movelist": "https://wavu.wiki/t/Zafina_movelist",
        "combos": "https://wavu.wiki/t/Zafina_combos",
    },
    "devil_jin": {
        "display": "恶魔仁",
        "filename": "恶魔仁_铁拳8_出招表.html",
        "css_class": "tk-char-deviljin",
        "moves": 160,
        "visible": 151,
        "startup_coverage": 149,
        "combos_count": 74,
        "movelist": "https://wavu.wiki/t/Devil_Jin_movelist",
        "combos": "https://wavu.wiki/t/Devil_Jin_combos",
    },
    "victor": {
        "display": "维克多",
        "filename": "维克多_铁拳8_出招表.html",
        "css_class": "tk-char-victor",
        "moves": 139,
        "visible": 130,
        "startup_coverage": 131,
        "combos_count": 36,
        "movelist": "https://wavu.wiki/t/Victor_movelist",
        "combos": "https://wavu.wiki/t/Victor_combos",
    },
    "reina": {
        "display": "蕾娜",
        "filename": "蕾娜_铁拳8_出招表.html",
        "css_class": "tk-char-reina",
        "moves": 192,
        "visible": 174,
        "startup_coverage": 168,
        "combos_count": 215,
        "movelist": "https://wavu.wiki/t/Reina_movelist",
        "combos": "https://wavu.wiki/t/Reina_combos",
    },
    "eddy": {
        "display": "艾迪",
        "filename": "艾迪_铁拳8_出招表.html",
        "css_class": "tk-char-eddy",
        "moves": 176,
        "visible": 167,
        "startup_coverage": 163,
        "combos_count": 66,
        "movelist": "https://wavu.wiki/t/Eddy_movelist",
        "combos": "https://wavu.wiki/t/Eddy_combos",
    },
    "lidia": {
        "display": "莉迪亚",
        "filename": "莉迪亚_铁拳8_出招表.html",
        "css_class": "tk-char-lidia",
        "moves": 174,
        "visible": 166,
        "startup_coverage": 151,
        "combos_count": 35,
        "movelist": "https://wavu.wiki/t/Lidia_movelist",
        "combos": "https://wavu.wiki/t/Lidia_combos",
    },
    "heihachi": {
        "display": "三岛平八",
        "filename": "三岛平八_铁拳8_出招表.html",
        "css_class": "tk-char-heihachi",
        "moves": 152,
        "visible": 152,
        "startup_coverage": 139,
        "combos_count": 97,
        "movelist": "https://wavu.wiki/t/Heihachi_movelist",
        "combos": "https://wavu.wiki/t/Heihachi_combos",
    },
}

EXPECTED_PARTITIONS = {
    "jin": (8, 90, {"CD (Breaking Step)": 8, "ZEN (Zenshin/Zanshin)": 11}, 17, 10),
    "anna": (10, 108, {"HAM (Hammer Chance)": 13, "CJM (Chaos Judgement)": 19, "TOM (Pleasure Time)": 5}, 18, 10),
    "fahkumram": (7, 118, {"GRF (Garuda Force)": 8, "RAM (Rama Stance)": 7}, 7, 0),
    "armor_king": (38, 105, {"BT (Back Turned)": 5, "CD (Beast Step / Crouch Dash)": 7, "BAD (Bad Jaguar)": 15}, 12, 0),
    "miary_zo": (6, 87, {"MOR (Morengy Miroso)": 11, "BAO (Baobab Mihira)": 8, "WAL (Tromba)": 5}, 13, 0),
    'kazuya': (7, 100, {'Mist Step': 3, 'Wind God Step': 9, 'DVK (Devil Form)': 15}, 7, 19),
    'paul': (17, 90, {'CS (Cormorant Step)': 11, 'DPD (Deep Dive)': 7, 'SWA (Sway)': 9}, 18, 25),
    'king': (82, 112, {'CD (Beast Step/Crouch Dash)': 4, 'BT (Back Turned)': 6, 'JGS (Jaguar Step)': 8, 'JGR (Jaguar Sprint/Jaguar Run)': 11}, 12, 20),
    'lars': (8, 84, {'DEN (Dynamic Entry)': 12, 'SEN (Silent Entry)': 9, 'LEN (Limited Entry)': 5}, 12, 10),
    'jack8': (21, 154, {'GMH (Gamma Howl)': 15, 'GMC (Gamma Charge)': 3, 'SIT (Sit Down)': 9, 'While Down (Face Up)': 1}, 16, 10),
    'nina': (33, 141, {'CD (Ducking Step)': 8, 'SWA (Sway)': 2}, 17, 10),
    'leroy': (6, 103, {'SS or NMS (Nimble Shift)': 4, 'HRM (Hermit)': 19}, 8, 7),
    'asuka': (13, 122, {}, 7, 21),
    'lili': (7, 101, {'DEW (Dew Glide)': 9, 'RAB (Feisty Rabbit)': 6, 'BT': 17}, 16, 0),
    'bryan': (7, 122, {'SNE (Snake Eyes)': 13, 'SLS (Slither Step)': 10, 'SWA (Sway)': 6}, 7, 10),
    'hwoarang': (11, 91, {'CD (Shark Step)': 4, 'BT (Backturn Stance)': 4, 'RFF (Right Stance)': 34, 'LFS (Left Flamingo)': 31, 'RFS (Right Flamingo)': 27}, 13, 10),
    'claudio': (6, 85, {'STB (Starburst)': 9}, 7, 10),
    'azucena': (11, 90, {'LIB (Libertador)': 23, 'BT': 16}, 15, 10),
    'raven': (7, 98, {'CD (Shadow Sprint)': 9, 'SZN (Soulzone)': 13, 'BT': 41}, 17, 10),
    'leo': (6, 102, {'LTG (Lightning Glare)': 5, 'KNK (Jin Ji Du Li)': 13, 'BOK (Fo Bu)': 9, 'CD (Jin Bu)': 6}, 7, 0),
    'steve': (7, 74, {'LWV (Ducking Left)': 10, 'RWV (Ducking Right)': 5, 'ALB (Quick Spin)': 6, 'DCK (Ducking)': 10, 'EXD (Ducking In)': 9, 'PAB (Peekaboo)': 25, 'SWY (Swaying)': 5, 'FLK (Flicker Stance)': 15, 'LNH (Lionheart)': 5}, 13, 5),
    'kuma': (8, 92, {'HBS (Hunting)': 19, 'SIT (Bear Sit)': 5, 'ROL (Bear Roll)': 6}, 10, 10),
    'panda': (8, 92, {'HBS (Hunting)': 18, 'SIT (Bear Sit)': 5, 'ROL (Bear Roll)': 6}, 15, 0),
    'yoshimitsu': (8, 165, {'KIN (Kincho)': 21, 'MED (Meditation)': 9, 'FLE (Flea)': 19, 'IND (Indian Stance)': 13, 'NSS (Mutou no Kiwami)': 57, 'DGF (Manji Dragonfly)': 12, 'BT': 6}, 26, 40),
    'shaheen': (6, 72, {'SNK (Stealth Step)': 9}, 9, 10),
    'dragunov': (17, 109, {'SNK (Sneak)': 7, 'PGR (Pigeon Roll)': 4}, 12, 16),
    'feng': (8, 109, {'BT': 8, 'CD (Lingering Shadow)': 7, 'STC (Shifting Clouds)': 7, 'KNP (Deceptive Step)': 8}, 11, 10),
    'lee': (6, 126, {'HMS (Hitman)': 11, 'MS (Mist Step)': 6}, 19, 6),
    'alisa': (7, 117, {'DES (Destructive Form)': 25, 'SBT (Boot)': 10, 'DBT (Dual Boot)': 11, 'BKP (Backup)': 6}, 11, 10),
    'zafina': (6, 88, {'SCR (Scarecrow Stance)': 20, 'TRT (Tarantula Stance)': 9, 'MNT (Mantis Stance)': 20, 'ORB (Anathema)': 4}, 7, 10),
    'devil_jin': (9, 91, {'WGS (Wind God Step)': 13, 'FLY (Fly)': 12, 'MCR (Mourning Crow)': 12}, 13, 10),
    'victor': (6, 82, {'IAI (Iai Stance)': 19, 'PRF (Perfumer)': 12}, 10, 10),
    'reina': (9, 93, {'WGS (Wind God Step)': 11, 'SEN (Sentai)': 9, 'SSH (Senshin)': 6, 'UNS (Unsoku)': 12, "WRA (Heaven's Wrath)": 15, 'WDS (Wind Step)': 3}, 14, 20),
    'eddy': (10, 107, {'HSP (Bananeira)': 15, 'RLX (Negativa)': 16, 'MD (Mandinga)': 10}, 8, 10),
    'lidia': (6, 106, {'HRS (Horse Stance)': 11, 'CAT (Cat Stance)': 14, 'WLF (Stalking Wolf Stance)': 9, 'HAE (Heaven and Earth)': 5}, 14, 9),
    'heihachi': (7, 86, {'CD (Wind God Step)': 16, "RAI (Thunder God's Kamae)": 6, "FUJ (Wind God's Kamae)": 11, 'WAR (Warrior Instinct)': 11}, 15, 0),
}

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

# verified against the wiki: genuinely huge damage values, not join artifacts
KNOWN_BIG_DAMAGE = {
    "jack8": {"Jack-8-1+4*,1": "35/45/55/199"},
    "yoshimitsu": {
        "Yoshimitsu-d+1*(6),n": "200",
        "Yoshimitsu-f,F+1+4,F": "60,185",
    },
}

# Rows allowed to fall back to text notation by design: sequences beyond six
# button grids do not fit fixed-height narrow tables (KNOWLEDGE §1), and these
# strings live outside the full-width ten-string table on Wavu itself.
EXPECTED_GFX_FALLBACKS = {
    "bryan": {
        "Bryan-ub+1+2,1,2,1,2,1,2",
        "Bryan-ub+1+2,1,2,1,2,1,2,1",
        "Bryan-ub+1+2,1,2,1,2,1,2,1,2",
        "Bryan-ub+1+2,1,2,1,2,1,2,1,2,1",
        "Bryan-ub+1+2,1,2,1,2,1,2,1,2,1,4",
    },
    "king": {"King-MMD6.2,4,3,1,1+3_2,4,3,1,2+4"},
}

PLACEHOLDER_COMBO = re.compile(
    r"^\s*combo\b|\b(?:goes here|combo here|placeholder|to be added|tbd)\b|\bcombo\b.*\bhere\b",
    re.I,
)


class MovelistParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.ids = []
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "tr" and "data-record-id" in attrs:
            self._row = {
                "record_id": attrs["data-record-id"],
                "id": attrs["data-move-id"],
                "command": attrs.get("data-command", ""),
                "startup": attrs.get("data-startup", ""),
                "kind": attrs.get("data-kind", "move"),
                "covered_record_ids": attrs.get(
                    "data-covered-record-ids", attrs["data-record-id"]
                ).split("|"),
                "cells": [],
            }
        elif tag == "td" and self._row is not None:
            self._cell = {"class": attrs.get("class", ""), "text": []}

    def handle_data(self, data):
        if self._cell is not None:
            self._cell["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self._cell is not None:
            self._cell["text"] = re.sub(
                r"\s+", " ", "".join(self._cell["text"])
            ).strip()
            self._row["cells"].append(self._cell)
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None


class ComboParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self._in_table = False
        self._in_body = False
        self._row = None
        self._cell = None
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self._skip_depth:
            self._skip_depth += 1
            return
        if self._cell is not None and (
            attrs.get("aria-hidden") == "true"
            or "sr-only" in attrs.get("class", "").split()
        ):
            self._skip_depth = 1
            return
        if tag == "table" and "cb" in attrs.get("class", "").split():
            self._in_table = True
        elif self._in_table and tag == "tbody":
            self._in_body = True
        elif self._in_body and tag == "tr":
            self._row = []
        elif self._row is not None and tag == "td":
            self._cell = []

    def handle_data(self, data):
        if self._cell is not None and not self._skip_depth:
            self._cell.append(data)

    def handle_endtag(self, tag):
        if self._skip_depth:
            self._skip_depth -= 1
            return
        if tag == "td" and self._cell is not None:
            text = re.sub(r"\s+", " ", "".join(self._cell)).strip()
            self._row.append(text)
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(tuple(self._row))
            self._row = None
        elif tag == "tbody" and self._in_body:
            self._in_body = False
        elif tag == "table" and self._in_table:
            self._in_table = False


def snapshot_first_impact(value):
    tokens = [token for token in re.split(r"[ ,]+", value or "") if token]
    if not tokens:
        return None
    impact = tokens[0].lstrip(".")
    return f"i{impact}" if impact[:1].isdigit() else impact


def snapshot_first_step(command):
    saw_button = False
    for index, character in enumerate(command):
        if character in "1234":
            saw_button = True
        elif character == "," and saw_button:
            return command[:index]
    return command


def snapshot_expected_startup(move, moves):
    own = move.get("startup", "").strip()
    if own.startswith("i"):
        return snapshot_first_impact(own) or "—"
    exact = {}
    folded = {}
    for candidate in moves:
        command = candidate["command"]
        startup = candidate.get("startup", "").strip()
        exact.setdefault(command, []).append(startup)
        folded.setdefault(command.casefold(), []).append(startup)
    for command in dict.fromkeys(
        (snapshot_first_step(move["command"]), move["command"])
    ):
        values = exact.get(command)
        if values is None:
            values = folded.get(command.casefold(), [])
        for value in values:
            impact = snapshot_first_impact(value)
            if impact:
                return impact
    return "—"


def snapshot_combo_entries(combos):
    entries = []
    for group in combos.get("sections", []):
        for entry in group.get("entries", []):
            starter = entry.get("starter", "").strip()
            route = entry.get("route", "").strip()
            if route and not PLACEHOLDER_COMBO.search(route):
                entries.append((starter, route))
    return entries


def row_markup(html, record_id):
    match = re.search(
        rf'<tr [^>]*data-record-id="{re.escape(record_id)}".*?</tr>',
        html,
        flags=re.S,
    )
    if not match:
        raise AssertionError(f"missing rendered row: {record_id}")
    return match.group(0)


def combo_cell_markup(html, value):
    encoded = escape(value)
    match = re.search(
        rf'<td class="cmd combo-[^"]+">(?:(?!</td>).)*?'
        rf'<span class="cmd-txt">{re.escape(encoded)}</span>'
        rf'(?:(?!</td>).)*?</td>',
        html,
        flags=re.S,
    )
    if not match:
        raise AssertionError(f"combo cell not found: {value}")
    return match.group(0)


def load_json(path):
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def load_builder_module():
    spec = importlib.util.spec_from_file_location(
        "build_season2", TOOLS / "build_season2.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Season2SourceContractTests(unittest.TestCase):
    def test_snapshots_have_complete_expected_cardinality(self):
        for key, cfg in CHARACTERS.items():
            with self.subTest(character=key):
                source = load_json(TOOLS / "source" / f"{key}.json")
                self.assertEqual(source["source_url"], cfg["movelist"])
                self.assertEqual(len(source["moves"]), cfg["moves"])
                self.assertTrue(all(move["command"] for move in source["moves"]))

    def test_snapshot_metadata_is_consistent(self):
        for key, cfg in CHARACTERS.items():
            with self.subTest(character=key):
                documents = [
                    load_json(TOOLS / "source" / f"{key}.json"),
                    load_json(TOOLS / "source" / f"{key}_zh.json"),
                    load_json(TOOLS / "source" / f"{key}_combos.json"),
                ]
                for document in documents:
                    self.assertEqual(document["character_key"], key)
                    self.assertEqual(document["display_name_zh"], cfg["display"])

    def test_damage_segments_have_no_join_artifacts(self):
        for key in CHARACTERS:
            with self.subTest(character=key):
                source = load_json(TOOLS / "source" / f"{key}.json")
                occurrences = {}
                mismatches = set()
                big_allowed = KNOWN_BIG_DAMAGE.get(key, {})
                for move in source["moves"]:
                    if big_allowed.get(move["id"]) != move.get("damage", ""):
                        self.assertIsNone(
                            re.search(r"\d{3,}", move.get("damage", "")),
                            move["id"],
                        )
                    occurrences[move["id"]] = occurrences.get(move["id"], 0) + 1
                    suffix = occurrences[move["id"]]
                    record_id = (
                        move["id"] if suffix == 1 else f'{move["id"]}#{suffix}'
                    )
                    targets = [
                        part
                        for part in move.get("target", "").split(",")
                        if part.strip()
                    ]
                    damage = [
                        part
                        for part in move.get("damage", "").lstrip(",").split(",")
                        if part.strip()
                    ]
                    if targets and damage and len(targets) != len(damage):
                        mismatches.add(record_id)
                self.assertEqual(mismatches, KNOWN_AGGREGATE_DAMAGE[key])

    def test_builder_rejects_joined_damage_and_new_shape_mismatches(self):
        module = load_builder_module()
        source = load_json(TOOLS / "source" / "anna.json")

        joined = copy.deepcopy(source)
        joined["moves"][0]["damage"] = "1523"
        with self.assertRaisesRegex(ValueError, "joined damage token"):
            module.validate_damage_fields("anna", joined)

        mismatched = copy.deepcopy(source)
        existing = KNOWN_AGGREGATE_DAMAGE["anna"]
        occurrences = {}
        for move in mismatched["moves"]:
            occurrences[move["id"]] = occurrences.get(move["id"], 0) + 1
            suffix = occurrences[move["id"]]
            record_id = move["id"] if suffix == 1 else f'{move["id"]}#{suffix}'
            targets = [part for part in move.get("target", "").split(",") if part]
            damage = [
                part for part in move.get("damage", "").lstrip(",").split(",") if part
            ]
            if targets and len(targets) == len(damage) and record_id not in existing:
                move["damage"] += ",1"
                break
        else:
            self.fail("no exact target/damage record available for mutation")
        with self.assertRaisesRegex(ValueError, "target/damage mismatch"):
            module.validate_damage_fields("anna", mismatched)

    def test_combo_annotation_boundaries_are_validated(self):
        module = load_builder_module()
        combos = load_json(TOOLS / "source" / "armor_king_combos.json")
        module.validate_combo_annotations(combos)

        broken = copy.deepcopy(combos)
        broken["sections"][0]["entries"][0]["starter"] = "[14 +] f,n,df+2HARD"
        with self.assertRaisesRegex(ValueError, "glued combo annotation"):
            module.validate_combo_annotations(broken)

        broken = copy.deepcopy(combos)
        broken["sections"][0]["entries"][0]["starter"] = (
            "[14; 9] f,n,d,df+2(on lower hit)"
        )
        with self.assertRaisesRegex(ValueError, "glued combo annotation"):
            module.validate_combo_annotations(broken)

    def test_duplicate_wavu_ids_are_semantically_consistent(self):
        for key in CHARACTERS:
            with self.subTest(character=key):
                source = load_json(TOOLS / "source" / f"{key}.json")
                grouped = {}
                for move in source["moves"]:
                    grouped.setdefault(move["id"], []).append(move)
                for move_id, moves in grouped.items():
                    commands = {move["command"] for move in moves}
                    names = {move["name"] for move in moves}
                    self.assertEqual(len(commands), 1, move_id)
                    self.assertEqual(len(names), 1, move_id)

    def test_translation_maps_cover_every_move_id(self):
        for key in CHARACTERS:
            with self.subTest(character=key):
                source = load_json(TOOLS / "source" / f"{key}.json")
                translation = load_json(TOOLS / "source" / f"{key}_zh.json")
                source_ids = [move["id"] for move in source["moves"]]
                translated_ids = list(translation["move_names"])
                self.assertEqual(set(source_ids), set(translated_ids))
                self.assertEqual(len(set(source_ids)), len(translated_ids))

    def test_move_names_are_simplified_chinese_without_latin_text(self):
        for key in CHARACTERS:
            with self.subTest(character=key):
                translation = load_json(TOOLS / "source" / f"{key}_zh.json")
                translated_labels = {
                    **translation["move_names"],
                    **{
                        f"section:{name}": value
                        for name, value in translation["section_names"].items()
                    },
                    **{
                        f"stance:{name}": value
                        for name, value in translation.get("stance_names", {}).items()
                    },
                }
                for label_id, label in translated_labels.items():
                    self.assertTrue(label.strip(), label_id)
                    self.assertIsNone(re.search(r"[A-Za-z]", label), label_id)

    def test_wavu_snapshots_match_structured_sources(self):
        for key in CHARACTERS:
            with self.subTest(character=key):
                source = load_json(TOOLS / "source" / f"{key}.json")
                expected = [
                    f'{move["command"]}|{move["startup"]}' for move in source["moves"]
                ]
                actual = (TOOLS / f"wavu_{key}.txt").read_text(
                    encoding="utf-8"
                ).splitlines()
                self.assertEqual(expected, actual)
                self.assertTrue(all(line.count("|") == 1 for line in actual))


class Season2BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.output_dir = Path(cls.tempdir.name)
        cls.build_command = [
            sys.executable,
            str(TOOLS / "build_season2.py"),
            "--output-dir",
            str(cls.output_dir),
        ]
        cls.first_run = subprocess.run(
            cls.build_command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def test_build_succeeds(self):
        self.assertEqual(
            self.first_run.returncode,
            0,
            self.first_run.stdout + self.first_run.stderr,
        )

    def test_output_is_byte_stable_on_second_build(self):
        self.assertEqual(self.first_run.returncode, 0)
        before = {
            key: hashlib.sha256(
                (self.output_dir / cfg["filename"]).read_bytes()
            ).hexdigest()
            for key, cfg in CHARACTERS.items()
        }
        second = subprocess.run(
            self.build_command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        after = {
            key: hashlib.sha256(
                (self.output_dir / cfg["filename"]).read_bytes()
            ).hexdigest()
            for key, cfg in CHARACTERS.items()
        }
        self.assertEqual(before, after)

    def test_checked_in_pages_match_generator_output(self):
        self.assertEqual(self.first_run.returncode, 0)
        for key, cfg in CHARACTERS.items():
            with self.subTest(character=key):
                generated = (self.output_dir / cfg["filename"]).read_bytes()
                checked_in = (ROOT / cfg["filename"]).read_bytes()
                self.assertEqual(checked_in, generated)

    def test_source_sections_drive_move_partitioning(self):
        module = load_builder_module()
        for key, expected in EXPECTED_PARTITIONS.items():
            with self.subTest(character=key):
                source = load_json(TOOLS / "source" / f"{key}.json")
                throws, attacks, stances, heat, ten_strings = (
                    module.partition_records(
                        module.record_ids(source["moves"]),
                        module.CHARACTERS[key],
                    )
                )
                actual = (
                    len(throws),
                    len(attacks),
                    {section: len(records) for section, records in stances.items()},
                    len(heat),
                    len(ten_strings),
                )
                self.assertEqual(actual, expected)

    def test_pages_cover_sources_and_shared_ui_contract(self):
        self.assertEqual(self.first_run.returncode, 0)
        module = load_builder_module()
        for key, cfg in CHARACTERS.items():
            with self.subTest(character=key):
                source = load_json(TOOLS / "source" / f"{key}.json")
                combos = load_json(TOOLS / "source" / f"{key}_combos.json")
                page = self.output_dir / cfg["filename"]
                html = page.read_text(encoding="utf-8")
                parser = MovelistParser()
                parser.feed(html)
                combo_parser = ComboParser()
                combo_parser.feed(html)

                self.assertIn("<!doctype html>", html.lower())
                self.assertIn(f"<title>{cfg['display']} · 铁拳8 出招表</title>", html)
                for control_id in (
                    "thgl",
                    "ntgl",
                    "thd",
                    "thl",
                    "ng",
                    "nn",
                    "nt",
                ):
                    self.assertIn(f'id="{control_id}"', html)
                self.assertIn("localStorage", html)
                self.assertIn(cfg["css_class"], html)
                self.assertIn(cfg["movelist"], html)
                self.assertIn(cfg["combos"], html)
                self.assertIn(
                    f'<footer id="sources">数据来源：<a href="{cfg["movelist"]}">'
                    f'Wavu Wiki movelist</a> · 打法参考：<a href="{cfg["combos"]}">'
                    "Wavu Wiki combos</a>",
                    html,
                )
                self.assertIn('<section class="sheet-section" id="throws">', html)
                self.assertIn('<section class="sheet-section" id="attacks">', html)
                self.assertIn('class="cols2"', html)
                if EXPECTED_PARTITIONS[key][2]:
                    self.assertIn('class="lt"', html)
                self.assertIn('<section class="tipsPage" id="combos">', html)
                self.assertIn('class="tpFull"', html)
                if cfg["combos_count"]:
                    self.assertIn('class="cb"', html)
                for obsolete_class in (
                    "hero",
                    "quick-nav",
                    "move-section",
                    "combo-list",
                    "combo-group",
                    "combo-table",
                    "cmd-raw",
                ):
                    self.assertNotIn(f'class="{obsolete_class}', html)
                _, _, _, heat_count, ten_count = EXPECTED_PARTITIONS[key]
                if heat_count and ten_count:
                    self.assertIn('class="colsRow"', html)
                if ten_count:
                    self.assertIn('class="ten-string-table"', html)
                self.assertNotIn("goes here", html.lower())
                self.assertNotIn("combo here", html.lower())
                self.assertNotIn("combo when", html.lower())
                self.assertNotIn("combo off-axis", html.lower())
                self.assertNotRegex(html.lower(), r"\bcombo\b.*\bhere\b")
                self.assertNotIn("—（Wavu 未注明）", html)
                self.assertNotRegex(html, r'<td class="dmg">,')
                self.assertEqual(len(parser.ids), len(set(parser.ids)))
                self.assertIn(
                    f'data-source-record-count="{cfg["moves"]}"',
                    html,
                )
                self.assertIn(
                    f'data-visible-record-count="{cfg["visible"]}"',
                    html,
                )
                self.assertIn(
                    f'实际存在的 {cfg["combos_count"]} 条路线', html
                )
                translation = load_json(TOOLS / "source" / f"{key}_zh.json")
                english_names = module.build_english_name_map(
                    source, translation
                )
                expected_combo_rows = [
                    (
                        module.combo_starter_label(starter, english_names)
                        or "通用",
                        route,
                    )
                    for starter, route in snapshot_combo_entries(combos)
                ]
                self.assertEqual(combo_parser.rows, expected_combo_rows)
                self.assertEqual(len(combo_parser.rows), cfg["combos_count"])
                if not cfg["combos_count"]:
                    self.assertIn("Wavu 连招页当前没有可用路线", html)
                if key == "armor_king":
                    self.assertIn("[14 +] f,n,df+2 (HARD)", html)
                    self.assertIn("[11 +] uf+2,1 (Close range)", html)
                    self.assertIn("f,n,d,df+2（下段命中时）", html)
                    self.assertIn("b+3 （热能中）", html)
                    self.assertIn("[70; 34] (Backturned)", html)
                    self.assertNotIn("f,n,df+2HARD", html)
                    self.assertNotIn("uf+2,1Close range", html)
                    self.assertNotIn("df+2(on lower hit)", html)
                    self.assertNotIn("]Backturned", html)
                    self.assertNotIn("b+3With heat", html)

                occurrences = {}
                source_by_record_id = {}
                for move in source["moves"]:
                    occurrences[move["id"]] = occurrences.get(move["id"], 0) + 1
                    suffix = occurrences[move["id"]]
                    record_id = move["id"] if suffix == 1 else f'{move["id"]}#{suffix}'
                    source_by_record_id[record_id] = move
                rendered_by_record_id = {
                    row["record_id"]: row for row in parser.rows
                }
                covered_record_ids = {
                    covered_id
                    for row in parser.rows
                    for covered_id in row["covered_record_ids"]
                }
                self.assertEqual(
                    set(source_by_record_id), covered_record_ids
                )
                self.assertEqual(cfg["visible"], len(parser.rows))
                self.assertEqual(len(rendered_by_record_id), len(parser.rows))
                startup_coverage = sum(
                    snapshot_expected_startup(move, source["moves"]) != "—"
                    for move in source["moves"]
                )
                self.assertEqual(startup_coverage, cfg["startup_coverage"])
                for record_id, row in rendered_by_record_id.items():
                    move = source_by_record_id[record_id]
                    move_id = move["id"]
                    self.assertEqual(move_id, row["id"])
                    self.assertEqual(move["command"], row["command"])
                    self.assertEqual(
                        row["startup"],
                        snapshot_expected_startup(move, source["moves"]),
                        record_id,
                    )
                    name_cells = [
                        cell for cell in row["cells"] if "name" in cell["class"].split()
                    ]
                    if len(row["covered_record_ids"]) > 1:
                        self.assertGreater(EXPECTED_PARTITIONS[key][4], 1)
                        self.assertEqual(len(name_cells), 0)
                        self.assertEqual(len(row["cells"]), 4)
                    else:
                        self.assertEqual(len(name_cells), 1, move_id)
                        self.assertIsNone(
                            re.search(r"[A-Za-z]", name_cells[0]["text"]),
                            move_id,
                        )
                    target_cells = [
                        cell for cell in row["cells"] if "rng" in cell["class"].split()
                    ]
                    for target_cell in target_cells:
                        self.assertIsNone(
                            re.search(r"[A-Za-z]", target_cell["text"]), move_id
                        )
                    if row["kind"] == "throw":
                        self.assertEqual(len(row["cells"]), 6, move_id)
                        self.assertTrue(row["cells"][-1]["text"], move_id)
                    elif len(row["covered_record_ids"]) == 1:
                        self.assertEqual(len(row["cells"]), 5, move_id)

    def test_contextual_duplicate_keeps_its_own_startup(self):
        module = load_builder_module()
        source = load_json(TOOLS / "source" / "armor_king.json")
        duplicates = [
            move for move in source["moves"] if move["id"] == "Armor_King-f,hcf+1"
        ]
        resolver = module.StartupResolver(source["moves"])
        resolved = {
            move["section"]: resolver.resolve(move["command"], move["startup"])
            for move in duplicates
        }
        self.assertEqual(resolved["BAD (Bad Jaguar)"], "i14")
        self.assertEqual(resolved["Command Throws"], "i10")

    def test_resolve_startup_uses_first_attack_impact(self):
        module = load_builder_module()
        for key in CHARACTERS:
            with self.subTest(character=key):
                source = load_json(TOOLS / "source" / f"{key}.json")
                resolver = module.StartupResolver(source["moves"])
                for move in source["moves"]:
                    actual = resolver.resolve(
                        move["command"], move.get("startup", "")
                    )
                    self.assertEqual(
                        actual,
                        snapshot_expected_startup(move, source["moves"]),
                        move["id"],
                    )

    def test_startup_resolver_exact_branches(self):
        module = load_builder_module()
        resolver = module.StartupResolver(
            [
                {"command": "HAM.1+3", "startup": "i11~12"},
                {"command": "WS+1", "startup": "i13"},
                {"command": "f,n,d,df+2", "startup": "i14"},
            ]
        )
        self.assertEqual(resolver.resolve("HAM.1+3,1"), "i11~12")
        self.assertEqual(resolver.resolve("ws+1"), "i13")
        self.assertEqual(resolver.resolve("f,n,d,df+2"), "i14")
        self.assertEqual(resolver.resolve("1", "i8~9"), "i8~9")
        self.assertEqual(resolver.resolve("unknown"), "—")

    def test_target_descriptors_cover_all_snapshot_tokens(self):
        module = load_builder_module()
        tokens = set()
        for key in CHARACTERS:
            source = load_json(TOOLS / "source" / f"{key}.json")
            for move in source["moves"]:
                tokens.update(
                    part.strip()
                    for part in move.get("target", "").split(",")
                    if part.strip()
                )
        for token in sorted(tokens):
            with self.subTest(token=token):
                css_class, label, title = module.target_descriptor(token)
                self.assertTrue(css_class)
                self.assertTrue(label)
                self.assertTrue(title)
        self.assertEqual(module.target_descriptor("h!"), ("hi", "上", "上（不可防）"))
        self.assertEqual(module.target_descriptor("th(g)"), ("sp", "投", "地面投"))
        self.assertEqual(
            module.target_descriptor("SM"),
            ("sp", "特中", "特中（可击中倒地）"),
        )
        self.assertEqual(module.target_descriptor("t(w)"), ("sp", "投", "墙边投"))

    def test_ham_throw_chains_use_graphical_buttons_and_raw_text(self):
        self.assertEqual(self.first_run.returncode, 0)
        html = (self.output_dir / CHARACTERS["anna"]["filename"]).read_text(
            encoding="utf-8"
        )
        first_matrix = (
            '<span class="tk-b"><i class="on">1</i><i>2</i>'
            '<i class="on">3</i><i>4</i></span>'
        )
        second_matrices = {
            "1": '<span class="tk-b"><i class="on">1</i><i>2</i><i>3</i><i>4</i></span>',
            "2": '<span class="tk-b"><i>1</i><i class="on">2</i><i>3</i><i>4</i></span>',
        }
        for suffix in ("1", "2"):
            command = f"HAM.1+3,{suffix}"
            for record_id in (f"Anna-{command}", f"Anna-{command}#2"):
                with self.subTest(command=command, record_id=record_id):
                    markup = row_markup(html, record_id)
                    self.assertIn('class="cmd-gfx"', markup)
                    self.assertIn('<span class="tk-state">锤击时机中</span>', markup)
                    self.assertEqual(markup.count('class="tk-b"'), 2)
                    self.assertIn(first_matrix, markup)
                    self.assertIn(second_matrices[suffix], markup)
                    self.assertIn(f'<span class="cmd-txt">{command}</span>', markup)

    def test_combo_starters_and_routes_use_graphical_notation(self):
        self.assertEqual(self.first_run.returncode, 0)
        module = load_builder_module()
        for key, config in CHARACTERS.items():
            combos = load_json(TOOLS / "source" / f"{key}_combos.json")
            source = load_json(TOOLS / "source" / f"{key}.json")
            translation = load_json(TOOLS / "source" / f"{key}_zh.json")
            english_names = module.build_english_name_map(source, translation)
            entries = snapshot_combo_entries(combos)
            html = (self.output_dir / config["filename"]).read_text(
                encoding="utf-8"
            )
            with self.subTest(character=key):
                self.assertEqual(
                    html.count('class="cmd-gfx combo-gfx"'), len(entries) * 2
                )
                for starter, route in entries:
                    translated_starter = (
                        module.combo_starter_label(starter, english_names)
                        or "通用"
                    )
                    combo_cell_markup(html, translated_starter)
                    combo_cell_markup(html, route)

        html = (self.output_dir / CHARACTERS["miary_zo"]["filename"]).read_text(
            encoding="utf-8"
        )
        starter = combo_cell_markup(html, "[12] H.df+2")
        self.assertIn('<span class="tk-state">热能中</span>', starter)
        self.assertEqual(starter.count('class="tk-b"'), 1)

        followup = combo_cell_markup(html, "[+22] ws1,4")
        self.assertIn('<span class="tk-state">起身中</span>', followup)
        self.assertEqual(followup.count('class="tk-b"'), 2)

        heat_route = combo_cell_markup(
            html,
            "[+33] dl u+3 u+3 u+3 df+4,F MOR.1,4 BAO.2 T! wr4,4,4",
        )
        self.assertIn('<span class="tk-state">莫伦吉进击中</span>', heat_route)
        self.assertIn('<span class="tk-state">猴面包树之歌中</span>', heat_route)
        self.assertIn('<span class="tk-tbang">T!</span>', heat_route)
        self.assertEqual(heat_route.count('class="tk-b"'), 10)

    def test_button_commands_and_side_throws_use_graphical_notation(self):
        self.assertEqual(self.first_run.returncode, 0)
        module = load_builder_module()
        side_throw_states = {
            "left_throw": "左侧",
            "right_throw": "右侧",
            "back_throw": "背后",
        }
        for key, config in CHARACTERS.items():
            html = (self.output_dir / config["filename"]).read_text(
                encoding="utf-8"
            )
            source = load_json(TOOLS / "source" / f"{key}.json")
            source_by_command = {}
            for move in source["moves"]:
                source_by_command.setdefault(move["command"].casefold(), move)
            parser = MovelistParser()
            parser.feed(html)
            rows = {row["command"].casefold(): row for row in parser.rows}
            allowed_fallbacks = EXPECTED_GFX_FALLBACKS.get(key, set())
            for row in parser.rows:
                if re.search(r"[1-4]", row["command"]):
                    with self.subTest(
                        character=key, record_id=row["record_id"]
                    ):
                        markup = row_markup(html, row["record_id"])
                        if row["record_id"] in allowed_fallbacks:
                            self.assertNotIn('class="cmd-gfx"', markup)
                        else:
                            self.assertIn('class="cmd-gfx"', markup)
            for suffix, state in side_throw_states.items():
                row = rows.get(suffix)
                if row is None:
                    # character records this throw differently on Wavu
                    # (e.g. Paul's Back_Throw.1+3 / .2+4 variants)
                    continue
                with self.subTest(character=key, command=suffix):
                    markup = row_markup(html, row["record_id"])
                    self.assertIn('class="cmd-gfx"', markup)
                    self.assertIn(f'<span class="tk-state">{state}</span>', markup)
                    self.assertEqual(markup.count('class="tk-b"'), 2)
                    expected = module.throw_break(source_by_command[suffix])
                    if expected == "—（Wavu 未注明）":
                        expected = "—"
                    self.assertEqual(row["cells"][-1]["text"], expected)

        html = (self.output_dir / CHARACTERS["armor_king"]["filename"]).read_text(
            encoding="utf-8"
        )
        for move_id, state in {
            "Armor_King-UT.2,1,2,1": "终极扑倒中",
            "Armor_King-BM.2,1,2,1": "骑背压制中",
        }.items():
            with self.subTest(move_id=move_id):
                markup = row_markup(html, move_id)
                self.assertIn('class="cmd-gfx"', markup)
                self.assertIn(f'<span class="tk-state">{state}</span>', markup)
                self.assertEqual(markup.count('class="tk-b"'), 4)
                self.assertIn(f'<span class="cmd-txt">{move_id.split("-", 1)[1]}</span>', markup)

    def test_throw_breaks_and_wall_direction_survive_section_layout(self):
        self.assertEqual(self.first_run.returncode, 0)
        html = (self.output_dir / CHARACTERS["armor_king"]["filename"]).read_text(
            encoding="utf-8"
        )
        parser = MovelistParser()
        parser.feed(html)
        rows = {row["record_id"]: row for row in parser.rows}
        for record_id, target_text in {
            "Armor_King-3+4*": "中上投不可挣脱",
            "Armor_King-df+3+4": "特中投不可挣脱",
            "Armor_King-BAD.2+4": "投挣脱 2",
        }.items():
            with self.subTest(record_id=record_id):
                self.assertEqual(rows[record_id]["kind"], "move")
                self.assertEqual(rows[record_id]["cells"][-1]["text"], target_text)
                self.assertIn('class="throw-break"', row_markup(html, record_id))
        wall_throw = rows["Armor_King-WALL.1+3"]
        self.assertEqual(wall_throw["kind"], "throw")
        self.assertEqual(wall_throw["cells"][3]["text"], "墙边")
        self.assertEqual(wall_throw["cells"][5]["text"], "不可挣脱")

    def test_common_direction_commands_use_graphical_notation(self):
        module = load_builder_module()
        expected_graphical = {
            "anna": {"Anna-CJM.df"},
            "armor_king": {
                "Armor_King-wr4",
                "Armor_King-f,n,d,df",
                "Armor_King-(Back_to_wall).b,\u200bb,\u200bUB",
            },
            "miary_zo": {"Miary_Zo-BAO.uf", "Miary_Zo-WAL.uf"},
        }
        for key, move_ids in expected_graphical.items():
            source = load_json(TOOLS / "source" / f"{key}.json")
            translation = load_json(TOOLS / "source" / f"{key}_zh.json")
            moves = {move["id"]: move for move in source["moves"]}
            for move_id in move_ids:
                with self.subTest(character=key, move_id=move_id):
                    rendered = module.render_command(
                        moves[move_id]["command"],
                        CHARACTERS[key]["css_class"],
                        translation.get("stance_names", {}),
                    )
                    self.assertIn('class="cmd-gfx"', rendered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
