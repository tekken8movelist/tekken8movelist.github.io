# -*- coding: utf-8 -*-
"""English copy for the five one-shot pipeline pages.

`build_legacy_en.py` derives `docs/en/` for jun / xiaoyu / kunimitsu / clive /
law from their published Simplified HTML. Move names come from Wavu; the
notation columns are notation and do not translate. Everything else -- section
headings, table heads, the hand-written guide prose -- is copy this project
wrote, and this is where its English lives.

Two rules keep the tables honest:

  * Keys are the exact string as it appears on the page, whitespace and all.
    The converter matches whole text nodes, never substrings of prose, so a
    key that is *almost* right silently fails the build rather than producing
    half-translated output.
  * Nothing here is optional. A Chinese string with no entry stops the build
    and prints itself. That is the whole reason `docs/en/` can be trusted to
    hold no Chinese: it is not swept for afterwards, it cannot be built.

`CAPSULES` is different in kind from `PHRASES`. Capsules are the `.tk-state`
chips in the command column, and they take Wavu's own stance codes rather than
English words -- an English reader looking at `BT.1` in the command wants to
see `BT` on the chip, not "Back-turned". The ones that are conditions rather
than stances (a parry window, a wall) do get words, because Wavu has no code
for them.
"""

from __future__ import annotations

# --- state chips in the command column ------------------------------------
# Stances take Wavu's codes; conditions take words. Values are what the reader
# sees on the chip, not what the notation joiner uses (that is pipeline.CONFIG
# `prefix`, which carries the trailing dot).
CAPSULES = {
    # shared across characters
    "热能中": "HEAT",
    "热能": "HEAT",
    "愤怒中": "RAGE",
    "起身中": "WS",
    "蹲伏中": "FC",
    "横移中": "SS",
    "冲刺": "DASH",
    "奔跑": "RUN",
    "背身": "BT",
    "背身时": "BT",
    "背墙时": "WALL",
    "墙": "WALL",
    "架势中": "STANCE",
    "左侧": "LEFT",
    "右侧": "RIGHT",
    "背后": "BACK",
    "倒地仰面时": "DOWN, FACE UP",
    "接近空中对手": "VS AIRBORNE",
    "可发动热能时": "HEAT READY",
    "可发动时": "WHEN READY",
    "看准对手攻击": "ON PARRY",
    "看准攻击": "ON PARRY",
    "看准对手下段攻击": "VS LOW",
    "看准对手拳击": "VS PUNCH",
    "看准对手投技": "VS THROW",
    "自动格挡拳技": "AUTO-PARRIES PUNCHES",
    "收尾改": "ENDING",
    # jun
    "幻月中": "GEN",
    "出云中": "IZU",
    "御生中": "MIA",
    "刈足中": "KARIASHI",
    # xiaoyu
    "凤凰中": "AOP",
    "凤凰": "AOP",
    "催眠中": "HYP",
    "催眠": "HYP",
    # kunimitsu
    "火遁中": "KAT",
    "刹那驱中": "SET",
    "刹那驱中迎击时": "CH SET",
    "鼯鼠中": "MUS",
    "卍旋踢中": "MANJI SPIN",
    "热能中且火遁中": "HEAT KAT",
    "热能发动技按住": "HEAT ENGAGER, HOLD",
    "背身时看准对手攻击": "BT, ON PARRY",
    # clive
    "光翼中": "WOL",
    "气流中": "GAR",
    "精准闪避成功后": "AFTER PRECISION DODGE",
    "光翼中接近空中对手": "WOL, VS AIRBORNE",
    # law
    "龙构中": "DSS",
    "热能中龙构中": "HEAT DSS",
}

# Words that appear inside a command string but are not state chips.
COMMAND_WORDS = {
    "或": "or",
    "命中时": "on hit",
    "可蓄力": "chargeable",
    "蓄力": "charge",
}

# --- move names the command join cannot reach -----------------------------
# Keyed by (character, the Chinese name exactly as the page prints it).
#
# These are Wavu's own names. The join failed for a mechanical reason, noted
# per entry -- mostly because the page writes a follow-up as a Chinese
# condition (`d/f+3 命中时 1`) where Wavu writes it as another comma step
# (`df+3,1`), which `pipeline.candidates` cuts at the first Chinese character.
# Fixing that in `candidates` would change the shared joiner the Simplified
# pages' frame data already depends on, for five rows; listing them is cheaper
# and each one is checkable against the snapshot beside it.
MOVE_NAMES = {
    ("clive", "水流爆破"): "Hydro Blast",          # wavu df+3,1
    ("clive", "潮涌"): "Tidal Surge",              # wavu db+1,1
    ("clive", "瓦纳甘德"): "Vanagandr",            # wavu PHX.3,2
    ("clive", "暗涌"): "Dark Surge",               # wavu PHX.3,1+2
    ("law", "爆裂爪"): "Blast Claw",               # wavu df+1,H.2
    ("xiaoyu", "白杨燕底破"): "Bai Yang Yan Di Po",  # wavu f+2,1,H.2
    ("xiaoyu", "白莲燕底破"): "Bai Lian Yan Di Po",  # wavu f,F+1,H.2
    ("clive", "致命引燃热能中"): "Lethal Ignition",  # wavu f+2,2,H.1
    # ^ the Simplified page glued the state word 热能中 onto the name itself;
    #   left alone there rather than edited, since that page holds its ranking
    # Wavu writes the Heat step mid-command, the page writes it as a prefix
    ("law", "龙式格挡"): "Dragon Parry",           # wavu H.DSS,P (comma, not dot)
    ("xiaoyu", "清街扫"): "Street Sweeper",        # wavu writes `ss4`, page `SS+4`
    ("xiaoyu", "催眠师·绕背"): "Hypnotist",        # wavu db+1+2; 看准对手拳击 is
                                                   # a condition with no prefix
    ("jun", "刈足"): "Kariashi",                   # wavu db+4,4,4
    ("law", "十连技"): "10 Hit Combo",             # wavu 10_String
    ("clive", "昆古尼尔之舞"): "Gungnir Dance",     # wavu 2,2,1+2 -- the page
                                                   # writes one 2 too many
}

# Wavu publishes no name for these, so the page shows the project's own
# description, in italics like every other described name on the site.
# Where Wavu romanises the same kanji on a follow-up card, that romanisation
# is used rather than a fresh invention -- noted per entry.
MOVE_DESCRIPTIONS = {
    ("jun", "月云"): "Getsuun",            # wavu GEN.3,2 "Getsuun Renken"
    ("jun", "神柱"): "Kanbashira",         # wavu f+3,2 "Kanbashira > Izumo Strike"
    ("jun", "龙炎"): "Ryuen",              # wavu b+2,1,1 "Ryuen Saika Shikei"
    ("jun", "龙炎·肘击"): "Ryuen Elbow",
    ("kunimitsu", "隐天狼"): "Hidden Sirius",
    ("kunimitsu", "叩踢"): "Knock Kick",
    ("kunimitsu", "火遁转换"): "Katon Transition",
    ("kunimitsu", "跳踢 / 跳前踢"): "Jumping Kick / Jumping Front Kick",
    ("kunimitsu", "螺旋裂 / 螺旋断"): "Spiral Rend / Spiral Sunder",
    # ^ one cell, two moves: wavu names only SS.2,1+2 (Spiral Sunder), so the
    #   pair is italic -- claiming the sourcing of the half that has it would
    #   put it on the half that does not
    ("xiaoyu", "右回踢"): "Right Roundhouse Kick",
    ("xiaoyu", "小扫腿"): "Short Sweep",
    ("xiaoyu", "蹲拂"): "Crouching Swipe",
    ("clive", "追击核爆"): "Aerial Chase Blast",
    ("law", "龙构双飞踢"): "Dragon Flight Kicks",
    ("law", "龙构突拳"): "Dragon Thrust Punch",
    ("law", "双截棍连击"): "Nunchaku Combo",
}

# --- column heads ---------------------------------------------------------
# Consulted before PHRASES for `<th>` text, because a word can head a column
# and label a legend entry and want different English in each: 判定 heads a
# column called `Hit` and labels a legend entry that reads `Hit level`.
# Wording follows locales.py so a reader moving between the 36 generated pages
# and these five sees one vocabulary.
TABLE_HEADS = {
    "招式": "Move",
    "指令": "Input",
    "判定": "Hit",
    "伤害": "Dmg",
    "发生": "i",
    "挣脱": "Break",
    "架势": "Stance",
    "方向": "Direction",
    "说明": "Notes",
    "要点": "Key points",
    "起手": "Starter",
    "起点": "Start",
    "后续": "Follow-up",
    "追击": "Follow-up",
    "贴士": "Tips",
    "帧数": "Frames",
    "场景": "Situation",
    "用途": "Use",
    "选择": "Choice",
    "其他": "Other",
    "路线": "Route",
    "空中": "Air",
    "落地": "Landing",
    "命中": "On hit",
    "替代": "Alternative",
    "十连": "10-hit",
}

# --- everything else ------------------------------------------------------
# Headings, hit levels, copy attributes and the hand-written guide prose.
# Keys are exact page text, including `&amp;` where the page has it.
PHRASES = {
    # -- shared chrome ----------------------------------------------------
    "全角色": "All fighters",
    "全角色出招表": "All movelists",
    "返回全角色选择": "Back to the fighter list",
    "快速导航": "Quick navigation",
    "首页": "Home",
    "铁拳 8 出招表": "TEKKEN 8 movelist",
    "铁拳8 全角色中文出招表": "TEKKEN 8 Movelist · Frame Data & Command List",
    "主题": "Theme",
    "夜间": "Dark",
    "浅色": "Light",
    "记法": "Notation",
    "按键图": "Buttons",
    "无数字": "No digits",
    "文字": "Text",
    "国家": "COUNTRY",
    "拳法": "STYLE",
    "架势": "STANCES",

    # -- legend -----------------------------------------------------------
    # `判定` and `发生` also head columns, where they are shorter -- see
    # TABLE_HEADS. These are the legend labels.
    "判定": "Hit level",
    "发生": "i",
    "首击冲击帧（i=impact，越小越快，依 Wavu）":
        "startup frames to first impact — lower is faster, per Wavu",
    "按键 · 方向": "Buttons · directions",
    "状态 · 分隔": "States · separators",
    "分隔": "Separators",
    "图形记法": "Notation",
    "四键方阵（左上1 右上2 左下3 右下4，亮=按下）":
        "four-button grid (1 LP, 2 RP, 3 LK, 4 RK — lit = pressed)",
    "=轻点方向": "= tap direction",
    "=按住": "= hold",
    "=回中": "= neutral",
    "=状态前缀　|": "= state prefix　|",
    "› 接续　+ 方向＋键　~ 紧接　＊蓄力　→ 下一招":
        "› follow-up　+ direction & button　~ immediately after　＊ charge　→ next move",
    "回旋": "tornado",
    "1=左拳　2=右拳　3=左脚　4=右脚　|　f=前　b=后　u=上　d=下　"
    "d/f=前下　d/b=后下　u/f=前上　u/b=后上":
        "1=left punch　2=right punch　3=left kick　4=right kick　|　"
        "f=forward　b=back　u=up　d=down　d/f=down-forward　d/b=down-back　"
        "u/f=up-forward　u/b=up-back",
    "f,f=前冲　WS=起身中　FC=蹲伏中　SS=横移中　+=同时按　~=紧接　＊蓄力":
        "f,f=dash　WS=while standing　FC=full crouch　SS=sidestep　"
        "+=together　~=immediately after　＊=charge",
    "=上段": "=high",
    "=中段": "=mid",
    "=下段": "=low",
    "=特殊": "=special",
    "=投掷": "=throw",
    "=不可防御": "=unblockable",
    "专用记号": "Notation notes",
    "qcf=下前1/4圈　~F=按住前": "qcf=quarter-circle forward　~F=hold forward",
    "qcf=下前1/4圈(d,d/f,f)　~F=按住前":
        "qcf=quarter-circle forward (d,d/f,f)　~F=hold forward",
    "幻月中=GEN　出云中=IZU　御生中=MIA":
        "GEN=Genjitsu　IZU=Izumo　MIA=Miare",
    "凤凰=凤凰架势(AOP)　背身=雨舞背身(BT)　催眠=催眠师(HYP)":
        "AOP=Phoenix stance　BT=back-turned　HYP=Hypnotist",
    "光翼=光之翼　凤凰=不死鸟瞬移　气流=上升气流":
        "WOL=Wings of Light　PHX=Phoenix Shift　GAR=Updraft",
    "龙构=龙构架势(DSS)　背身=背身状态(BT)":
        "DSS=Dragon Charge stance　BT=back-turned",

    # -- hit levels -------------------------------------------------------
    "上": "High",
    "中": "Mid",
    "下": "Low",
    "特": "Sp.",
    "特下": "SL",
    "特中": "SM",
    "特中·投": "SM · Throw",
    "投": "Throw",
    "特殊": "Special",
    "无法防御": "Unblockable",
    "上上": "High, High",
    "上上上": "High, High, High",
    "中中": "Mid, Mid",
    "中中中": "Mid, Mid, Mid",
    "下下": "Low, Low",
    "中×4": "Mid ×4",
    "中×5": "Mid ×5",
    "上×6": "High ×6",
    "下×6": "Low ×6",
    "中(中中)": "Mid (Mid, Mid)",
    "下(下下)": "Low (Low, Low)",
    "中(地)": "Mid (grounded)",
    "中!": "Mid!",
    "不可防(中)": "Unblockable (Mid)",
    "不可防(上)": "Unblockable (High)",
    "正面": "Front",
    "左侧": "Left",
    "右侧": "Right",
    "背后": "Back",
    "立姿 10f": "Standing 10f",
    "蹲姿 10f": "Crouching 10f",
    "起身 11f": "While standing 11f",
    "起身 13f": "While standing 13f",
    "起身 15f": "While standing 15f",

    # -- section headings -------------------------------------------------
    "投技": "Throws",
    "投技 &amp; 当身": "Throws &amp; reversals",
    "打击技": "Attacks",
    "热能系统": "Heat",
    "十连技": "10-hit combo",
    "进阶攻略": "Advanced guide",
    "核心招式": "Key moves",
    "连招": "Combos",
    "连招 (Wavu 现版本)": "Combos (Wavu, current patch)",
    "确定反击": "Punishers",
    "确反": "Punishers",
    "确反 &amp; 惩罚要点": "Punishers &amp; what to punish with",
    "实用贴士": "Practical tips",
    "小连招": "Mini-combos",
    "小连招 &amp; 墙连": "Mini-combos &amp; wall",
    "热能运用": "Using Heat",
    "玩法定位": "Game plan",
    "术语": "Terms",
    "架势详解": "Stances in detail",
    "架势核心": "Stance core",
    "当身体系": "Reversal toolkit",
    "进入 &amp; 用法": "Entry &amp; use",
    "框架陷阱 &amp; 热能": "Frame traps &amp; Heat",
    "龙构与热能": "Dragon Charge &amp; Heat",
    "横移与特殊": "Sidestep &amp; specials",
    "实战攻略 · PRACTICAL GUIDE": "Practical guide",
    "连招 · 架势 · 实战技巧": "Combos · stances · practical notes",
    "连招 · 确反 · 实战技巧": "Combos · punishers · practical notes",
    "幻月": "Genjitsu",
    "出云": "Izumo",
    "御生": "Miare",
    "凤凰架势": "Phoenix stance",
    "催眠师": "Hypnotist",
    "催眠师(HYP)": "Hypnotist (HYP)",
    "凤凰(AOP)": "Phoenix (AOP)",
    "雨舞·背身": "Rain Dance · back-turned",
    "火遁": "Katon",
    "刹那驱": "Setsunagake",
    "背身": "Back-turned",
    "龙构": "Dragon Charge",
    "横移": "Sidestep",
    "光之翼": "Wings of Light",
    "不死鸟瞬移": "Phoenix Shift",
    "上升气流": "Updraft",
    "万用BnB": "Bread and butter",
    "精粹(Staples)": "Staples",
    "墙连 (带回旋)": "Wall (with tornado)",
    "墙连 (无回旋)": "Wall (no tornado)",
    "即时回旋 (如下段防反)": "Instant tornado (e.g. low parry)",
    "择/二择": "Mix-up",
    "择": "Mix-up",
    "当身": "Reversal",
    "防反": "Parry",
    "防守反击": "Parries &amp; reversals",
    "挥空罚": "Whiff punish",
    "追击": "Follow-up",
    "发动路线": "Engager routes",
    "发动技一览": "Engagers at a glance",
    "热能发动技": "Heat engager",
    "对空": "Anti-air",
    "空中": "Air",
    "落地": "Landing",
    "命中": "On hit",
    "命中时": "on hit",
    "替代": "Alternative",
    "十连": "10-hit",
    "路线": "Route",
    "起点": "Start",
    "后续": "Follow-up",
    "要点": "Key points",
    "说明": "Notes",
    "方向": "Direction",
    "挣脱": "Break",
    "场景": "Situation",
    "帧数": "Frames",
    "起手": "Starter",
    "贴士": "Tips",
    "其他": "Other",
    "用途": "Use",
    "选择": "Choice",
    "自动": "auto",
    "或": "or",
    "两大": "the two",
    "等": "and others",
    "兼": "and",
    "同": "same",
    "三条": "three of them",
    "派生": "follow-ups",
    "三派生": "three follow-ups",
    "后可续": "then continue with",
    "转热能": "into Heat",
    "转火遁": "into Katon",
    "转背身续压": "into back-turned to keep the pressure",
    "投后": "after the throw",
    "破墙用": "to break the wall, use",
    "收尾改": "change the ending to",
    "由快到伤害排序": "ordered fastest first, then by damage",
    "由近及远选择": "pick by range, nearest first",
    "按距离选择；4,3 可转龙构。":
        "Pick by range; 4,3 can go into Dragon Charge.",

    # -- per-character titles, portraits and meta -------------------------
    "风间准": "Jun Kazama",
    "风间准出招表": "Jun Kazama movelist",
    "风间准 · 飞白轮廓角色像": "Jun Kazama · flying-white outline portrait",
    "铁拳8 风间准（Jun Kazama）头像": "TEKKEN 8 Jun Kazama portrait",
    "铁拳8 风间准（Jun Kazama）出招表 | TEKKEN 8 Jun Kazama Movelist":
        "TEKKEN 8 Jun Kazama Movelist · Frame Data & Command List",
    "凌晓雨": "Ling Xiaoyu",
    "凌晓雨出招表": "Ling Xiaoyu movelist",
    "凌晓雨 · 飞白轮廓角色像": "Ling Xiaoyu · flying-white outline portrait",
    "铁拳8 凌晓雨（Ling Xiaoyu）头像": "TEKKEN 8 Ling Xiaoyu portrait",
    "铁拳8 凌晓雨（Ling Xiaoyu）出招表 | TEKKEN 8 Ling Xiaoyu Movelist":
        "TEKKEN 8 Ling Xiaoyu Movelist · Frame Data & Command List",
    "国光二世": "Kunimitsu II",
    "国光二世出招表": "Kunimitsu II movelist",
    "国光二世 · 飞白轮廓角色像": "Kunimitsu II · flying-white outline portrait",
    "铁拳8 国光二世（Kunimitsu II）头像": "TEKKEN 8 Kunimitsu II portrait",
    "铁拳8 国光二世（Kunimitsu II）出招表 | TEKKEN 8 Kunimitsu II Movelist":
        "TEKKEN 8 Kunimitsu II Movelist · Frame Data & Command List",
    "克莱夫·罗兹菲尔德": "Clive Rosfield",
    "克莱夫·罗兹菲尔德出招表": "Clive Rosfield movelist",
    "克莱夫·罗兹菲尔德 · 飞白轮廓角色像":
        "Clive Rosfield · flying-white outline portrait",
    "铁拳8 克莱夫·罗兹菲尔德（Clive Rosfield）头像":
        "TEKKEN 8 Clive Rosfield portrait",
    "铁拳8 克莱夫·罗兹菲尔德（Clive Rosfield）出招表 | TEKKEN 8 Clive Rosfield Movelist":
        "TEKKEN 8 Clive Rosfield Movelist · Frame Data & Command List",
    "马歇尔·洛": "Marshall Law",
    "马歇尔·洛出招表": "Marshall Law movelist",
    "马歇尔·洛 · 飞白轮廓角色像": "Marshall Law · flying-white outline portrait",
    "铁拳8 马歇尔·洛（Marshall Law）头像": "TEKKEN 8 Marshall Law portrait",
    "铁拳8 马歇尔·洛（Marshall Law）出招表 | TEKKEN 8 Marshall Law Movelist":
        "TEKKEN 8 Marshall Law Movelist · Frame Data & Command List",

    # -- official profile values ------------------------------------------
    "日本": "Japan",
    "中国": "China",
    "美国": "USA",
    "罗萨利亚大公国": "Grand Duchy of Rosaria",
    "风间流古武术": "Kazama Style Traditional Martial Arts",
    "以八卦掌、劈挂掌为基的中国武术":
        "Chinese martial arts based on Baguazhang and Piguazhang",
    "卍流忍术": "Manji Ninjutsu",
    "武术": "Martial arts",

    # -- meta descriptions and intros -------------------------------------
    "风间准（Jun Kazama）《铁拳8》（TEKKEN 8）完整出招表：招式指令、帧数表、"
    "确反数据与进阶连招。Complete TEKKEN 8 Jun Kazama movelist with frame data.":
        "The complete TEKKEN 8 Jun Kazama movelist: every command, startup "
        "frames, damage and hit level, plus punishers and combo routes.",
    "凌晓雨（Ling Xiaoyu）《铁拳8》（TEKKEN 8）完整出招表：招式指令、帧数表、"
    "确反数据与进阶连招。Complete TEKKEN 8 Ling Xiaoyu movelist with frame data.":
        "The complete TEKKEN 8 Ling Xiaoyu movelist: every command, startup "
        "frames, damage and hit level, plus punishers and combo routes.",
    "国光二世（Kunimitsu II）《铁拳8》（TEKKEN 8）完整出招表：招式指令、帧数表、"
    "确反数据与进阶连招。Complete TEKKEN 8 Kunimitsu II movelist with frame data.":
        "The complete TEKKEN 8 Kunimitsu II movelist: every command, startup "
        "frames, damage and hit level, plus punishers and combo routes.",
    "克莱夫·罗兹菲尔德（Clive Rosfield）《铁拳8》（TEKKEN 8）完整出招表：招式指令、"
    "帧数表、确反数据与进阶连招。Complete TEKKEN 8 Clive Rosfield movelist with "
    "frame data.":
        "The complete TEKKEN 8 Clive Rosfield movelist: every command, startup "
        "frames, damage and hit level, plus punishers and combo routes.",
    "马歇尔·洛（Marshall Law）《铁拳8》（TEKKEN 8）完整出招表：招式指令、帧数表、"
    "确反数据与进阶连招。Complete TEKKEN 8 Marshall Law movelist with frame data.":
        "The complete TEKKEN 8 Marshall Law movelist: every command, startup "
        "frames, damage and hit level, plus punishers and combo routes.",
    "本页收录《铁拳8》（TEKKEN 8）风间准（Jun Kazama）的完整出招表与帧数表"
    "（frame data），并整理进阶连招与实战技巧，供对局间隙快速查阅。":
        "The complete TEKKEN 8 Jun Kazama movelist and frame data, with combo "
        "routes and practical notes, laid out to be read between matches.",
    "本页收录《铁拳8》（TEKKEN 8）凌晓雨（Ling Xiaoyu）的完整出招表与帧数表"
    "（frame data），并整理进阶连招与实战技巧，供对局间隙快速查阅。":
        "The complete TEKKEN 8 Ling Xiaoyu movelist and frame data, with combo "
        "routes and practical notes, laid out to be read between matches.",
    "本页收录《铁拳8》（TEKKEN 8）国光二世（Kunimitsu II）的完整出招表与帧数表"
    "（frame data），并整理进阶连招与实战技巧，供对局间隙快速查阅。":
        "The complete TEKKEN 8 Kunimitsu II movelist and frame data, with combo "
        "routes and practical notes, laid out to be read between matches.",
    "本页收录《铁拳8》（TEKKEN 8）克莱夫·罗兹菲尔德（Clive Rosfield）的完整出招表"
    "与帧数表（frame data），并整理进阶连招与实战技巧，供对局间隙快速查阅。":
        "The complete TEKKEN 8 Clive Rosfield movelist and frame data, with "
        "combo routes and practical notes, laid out to be read between matches.",
    "本页收录《铁拳8》（TEKKEN 8）马歇尔·洛（Marshall Law）的完整出招表与帧数表"
    "（frame data），并整理进阶连招与实战技巧，供对局间隙快速查阅。":
        "The complete TEKKEN 8 Marshall Law movelist and frame data, with combo "
        "routes and practical notes, laid out to be read between matches.",

    # -- footers ----------------------------------------------------------
    "数据来源：Wavu Wiki (wavu.wiki/t/Jun_movelist · Jun_combos) · "
    "打法参考：TekkenDocs Jun Guide by Pagani · 招式名为中文意译，供参考":
        "Data: Wavu Wiki (wavu.wiki/t/Jun_movelist · Jun_combos) · "
        "Gameplay notes: TekkenDocs Jun Guide by Pagani · move names are "
        "Wavu's where Wavu publishes one",
    "数据来源：Wavu Wiki (wavu.wiki/t/Xiaoyu_movelist · Xiaoyu_combos) · "
    "打法参考：TekkenDocs Xiaoyu Guide by kanda · 招式名为中文意译，供参考":
        "Data: Wavu Wiki (wavu.wiki/t/Xiaoyu_movelist · Xiaoyu_combos) · "
        "Gameplay notes: TekkenDocs Xiaoyu Guide by kanda · move names are "
        "Wavu's where Wavu publishes one",
    "数据来源：Wavu Wiki (wavu.wiki/t/Kunimitsu_movelist · Kunimitsu_combos) · "
    "打法参考：esports.gg · 招式名为中文意译，供参考":
        "Data: Wavu Wiki (wavu.wiki/t/Kunimitsu_movelist · Kunimitsu_combos) · "
        "Gameplay notes: esports.gg · move names are Wavu's where Wavu "
        "publishes one",
    "数据来源：Wavu Wiki (wavu.wiki/t/Clive_movelist · Clive_combos) · "
    "打法参考：GameRant · 招式名参考 FF16 中文译名，供参考":
        "Data: Wavu Wiki (wavu.wiki/t/Clive_movelist · Clive_combos) · "
        "Gameplay notes: GameRant · move names are Wavu's where Wavu "
        "publishes one",
    "数据来源：Wavu Wiki (wavu.wiki/t/Law_movelist · Law_combos) · "
    "打法参考：TekkenDocs Law Guide by Landon D · 招式名为中文意译，供参考":
        "Data: Wavu Wiki (wavu.wiki/t/Law_movelist · Law_combos) · "
        "Gameplay notes: TekkenDocs Law Guide by Landon D · move names are "
        "Wavu's where Wavu publishes one",
    "连招依据 Wavu Wiki (现行版本) · 打法参考 TekkenDocs (Pagani)":
        "Combos from Wavu Wiki (current patch) · gameplay notes from "
        "TekkenDocs (Pagani)",
    "连招依据 Wavu Wiki (现行版本) · 打法参考 TekkenDocs (kanda)":
        "Combos from Wavu Wiki (current patch) · gameplay notes from "
        "TekkenDocs (kanda)",
    "连招依据 Wavu Wiki (现行版本) · 打法参考 esports.gg":
        "Combos from Wavu Wiki (current patch) · gameplay notes from esports.gg",
    "连招依据 Wavu Wiki (现行版本) · 打法参考 GameRant":
        "Combos from Wavu Wiki (current patch) · gameplay notes from GameRant",
    "连招依据 Wavu Wiki 当前页面 · 打法参考 TekkenDocs Season 2 Law Guide by Landon D":
        "Combos from Wavu Wiki (current page) · gameplay notes from TekkenDocs "
        "Season 2 Law Guide by Landon D",

    # -- combo legend rows ------------------------------------------------
    "路线 (T!=回旋 / ~=接 / SWL=左侧走)":
        "Route (T!=tornado / ~=into / SWL=sidewalk left)",
    "路线 (T!=回旋 · ~=紧接 · →=下一招)":
        "Route (T!=tornado · ~=immediately after · →=next move)",
    "路线 (T!=回旋 / ~F=按住前)": "Route (T!=tornado / ~F=hold forward)",
    "路线 (T!=回旋 / GAR=气流)": "Route (T!=tornado / GAR=Updraft)",
    "路线 (T!=回旋 · ~F=按住前 · →=下一招)":
        "Route (T!=tornado · ~F=hold forward · →=next move)",
    "=万用基础连招(Bread and Butter,优先练熟)　|":
        "=the everyday combo (bread and butter — learn this one first)　|",
    "=反击命中(Counter Hit):打中正在出招的对手,多数CH技有起浮/崩溃等强化效果　|":
        "=counter hit: catching an opponent mid-move; most moves gain a "
        "launch or crumple on CH　|",
    "=回旋(Tornado):命中空中对手使其横转、延长连招,每套连招限一次　|":
        "=tornado: spins an airborne opponent to extend the combo, once per "
        "combo　|",
    "=对手招式被防住后利用其硬直的必中惩罚　|":
        "=a guaranteed punish taken from the recovery of a blocked move　|",
    "=逼对手在站防(防中段)与蹲防(防下段)间二选一的猜拳局面,核心择=该角色主要的猜拳点":
        "=forcing a guess between standing (blocks mid) and crouching (blocks "
        "low); the core mix-up is the character's main guessing point",
    "=针对特定起手的更高伤害路线　|":
        "=a higher-damage route for one particular starter　|",

    # -- jun --------------------------------------------------------------
    # The game-plan paragraph is split by <b> tags, so these fragments are
    # translated to join back up in order. Values carry their own trailing
    # space where the page had none and English needs one.
    "风间准以": "Jun Kazama is built around ",
    "为核心：立回控距、后撤诱敌、用反击(CH)技惩罚对手抢招。"
    "风间流气功技(如 f+2 派生、d+1+2)被防时会":
        ": control the range in neutral, bait with backdashes, and punish "
        "impatience with counter hits. Her Kazama ki moves (the f+2 "
        "follow-ups, d+1+2) ",
    "消耗自身体力": "cost her own health",
    "(部分可回复)，热能中消耗减半且对敌削减增强；1,2,2 与 d/b+1,1,1+2 命中可":
        " when blocked (partly recoverable); in Heat the cost halves and the "
        "chip damage rises, and 1,2,2 and d/b+1,1,1+2 ",
    "回复体力": "restore health",
    "。中近距离用 b+2 / d+4 / d/b+3 戳刺压制，中距离用 d/f+4、b+3 拒止，"
    "f+2(鬼杀)惩罚挥空。":
        " on hit. Poke at close range with b+2 / d+4 / d/b+3, deny at mid "
        "range with d/f+4 and b+3, and punish whiffs with f+2 (Onikiri).",
    "鬼杀": "Onikiri",
    "天照": "Amaterasu",
    "岩户": "Iwato",
    "风切": "Kazakiri",
    "静心": "Inner Peace",
    "酢浆草": "Katabami",
    "返技": "Reversal",
    "自动": "auto",
    "幻月中自动防反下段": "GEN auto-parries lows",
    "(幻月自动)": "(GEN auto)",
    "看准对手下段攻击 f+3+4 (幻月自动)": "vs a low: f+3+4 (GEN auto)",
    "看准对手投技 f+3+4 (幻月自动)": "vs a throw: f+3+4 (GEN auto)",
    "静心变当身": "Inner Peace becomes a reversal",
    "双升踢(剪刀脚)": "Double Lift Kicks (scissors)",
    "额外扫堂": "A second sweep",
    "相当于第二把下段扫堂腿": "effectively a second low sweep",
    "热能+幻月中 1,2+3 (黄泉御柱) 相当于第二把下段扫堂腿":
        "In Heat, GEN 1,2+3 (Yomotsu Mihashira) works as a second low sweep",
    "气功增益": "Ki bonus",
    "热能中风间技对自身削减减半、对敌方增加,f,f+1+2 成为超强压制":
        "In Heat the ki moves cost Jun half as much and take more from the "
        "opponent, which turns f,f+1+2 into very strong pressure",
    "体力管理": "Health management",
    "血量吃紧时确反改用 1,2,2、d/b+1,1,1+2 回血;少按消耗大的气功技":
        "When low on health, punish with 1,2,2 and d/b+1,1,1+2 to heal, and "
        "lay off the expensive ki moves",
    "对付防守型": "Against turtles",
    "准难破铁龟:多用 幻月中1(+3)与 出云扫堂制造开口,耐心等CH":
        "Jun struggles to open up a blocker: use GEN 1 (+3) and the Izumo "
        "sweep to make a gap, and wait patiently for a counter hit",
    "出云二择": "The Izumo mix-up",
    "出云中 4,1 (下段) ⇄ 出云中 2 (中段,被防可罚) 是核心择":
        "IZU 4,1 (low) against IZU 2 (mid, punishable on block) is the core "
        "guess",
    "架势：出云中 4,1(下段扫堂) 与 2(中段起浮) 构成核心二择":
        "Stances: IZU 4,1 (low sweep) and IZU 2 (mid launcher) form the core "
        "mix-up",
    "御生2 慎用": "Use MIA 2 sparingly",
    "御生中 2 被防会被确反(含怒气技),尽量在热能中或确杀时使用":
        "MIA 2 is punishable on block, rage arts included — save it for Heat "
        "or for the kill",
    "主力下段戳刺：d+4 距离长追踪好；d/b+3 命中+2、CH+6 接续压制":
        "Main low pokes: d+4 has range and tracks well; d/b+3 is +2 on hit "
        "and +6 on counter hit, so pressure continues",
    "连招要点": "Combo notes",
    "核心过渡: f+3,2~出云 与 f,F+2~B 御生;收尾选 幻月中2(伤害) 或 f,F+2,3(运载)":
        "Core transitions: f+3,2~IZU and f,F+2~B into MIA; finish with GEN 2 "
        "for damage or f,F+2,3 to carry",
    "横移追踪(上段)，被防+3、命中+13，命中后接 1+2 必中(热能发动)":
        "Tracks a sidestep (high), +3 on block and +13 on hit, after which "
        "1+2 is guaranteed (Heat engager)",
    "横移追踪且转入": "tracks a sidestep and goes into",
    "压制技，是准少有的强帧数进攻起点":
        "a pressure move, and one of the few strong frame-advantage starts "
        "Jun has",
    "热能中 f+1+2 第5帧起当身，成功消耗热能接 御生2~F 起连招":
        "In Heat, f+1+2 reverses from frame 5; on success it spends Heat and "
        "goes into MIA 2~F for a full combo",
    "热能中 f+2,1+2 变安全、可命中确认的热能冲刺起浮技":
        "In Heat, f+2,1+2 becomes a safe, hit-confirmable Heat dash launcher",
    "变安全": "becomes safe",
    "可命中确认的热能冲刺起浮技": "a hit-confirmable Heat dash launcher",
    "最优起浮确反,连招路线最好": "the best launch punish, with the best routes",
    "最快起身浮空技": "fastest while-standing launcher",
    "最高伤害起身浮空": "highest-damage while-standing launcher",
    "长距离起浮": "long-range launcher",
    "确认起浮": "confirmable launcher",
    "可确认 45 伤害并回血": "confirms into 45 damage and heals",
    "可确认三段 28 伤害": "confirms three hits for 28 damage",
    "不可被下段防反": "cannot be low-parried",
    "击倒+贴墙,近墙首选": "knocks down and carries to the wall — first pick near one",
    "击倒,倒地压制好": "knocks down, with good oki",
    "36 伤害击倒,墙场极强(消耗自身)":
        "36 damage and a knockdown, very strong at the wall (costs health)",
    "被防+6": "+6 on block",
    "贴墙 (+27)": "At the wall (+27)",
    "贴墙 (稳定)": "At the wall (consistent)",
    "贴墙带回旋": "At the wall, with tornado",
    "(精粹 +55)": "(staple +55)",
    "(高伤 +73)": "(high damage +73)",
    "(黄泉御柱)": "(Yomotsu Mihashira)",
    "(命中/被防时)": "(on hit or block)",
    "(d/f+2等常规起浮)": "(d/f+2 and other standard launchers)",
    "d/f+2 (精粹 +55)": "d/f+2 (staple +55)",
    "d/f+2,1+2 (高伤 +73)": "d/f+2,1+2 (high damage +73)",
    "d/f+2 (命中/被防时) 1+2": "d/f+2 (on hit or block) 1+2",
    "f+2 (命中/被防时) 1+2": "f+2 (on hit or block) 1+2",
    "f+4 命中 (+20)": "f+4 on hit (+20)",
    "u+2 命中 (+18)": "u+2 on hit (+18)",
    "FC+d/b+1+2 投后 (+49)": "After the FC d/b+1+2 throw (+49)",
    "1,2,2 可确认转架势且回血；u/f+1 击倒(近墙优先)":
        "1,2,2 confirms into a stance and heals; u/f+1 knocks down (prefer it "
        "near the wall)",
    "→ b+4,2 (或 1+2 转热能)": "→ b+4,2 (or 1+2 into Heat)",
    "~f~幻月中4 → f+3 → b+2,1~F → 幻月中3&gt;2":
        "~f~GEN 4 → f+3 → b+2,1~F → GEN 3&gt;2",
    "，被防-25": ", -25 on block",
    "：i14 最强CH起浮技，带空中判定":
        ": i14, her best counter-hit launcher, with an airborne property",
    "：i15 长距离CH拒止中段，命中崩溃强制受身，被防-14 慎用":
        ": i15, a long-range counter-hit mid; on hit it crumples and forces a "
        "tech roll. -14 on block, so use it with care",
    "：i17 长距离浮空技，惩罚挥空的招牌；热能中 f+2,1+2 变为安全可确认起浮":
        ": i17, the long-range launcher and her signature whiff punish; in "
        "Heat, f+2,1+2 turns it into a safe, confirmable launch",
    "：i20 低姿态中段，被防仅-6，CH直接起浮，命中+5 可继续压制":
        ": i20, a low-profile mid, only -6 on block, launches on counter hit "
        "and is +5 on hit to keep pressuring",
    "：上段拂挡；热能中变为第5帧起当身，成功可接 御生2 转全套连招":
        ": a high parry; in Heat it becomes a frame-5 reversal that leads into "
        "MIA 2 and a full combo",
    "：立回王牌，中段横向覆盖极强，被防仅-8，命中击倒近墙可贴墙":
        ": her neutral trump card — a mid with excellent lateral coverage, "
        "only -8 on block, and a knockdown that carries to a nearby wall",

    # -- clive ------------------------------------------------------------
    "克莱夫是": "Clive is a summoner-style character built around ",
    "显现者": "the Dominant",
    "的召唤师型角色:上手容易(连招执行门槛低)、精通较难。他拥有全游戏独一份的":
        ": easy to pick up (the combo execution bar is low) and harder to "
        "master. He is the only character in the game with a ",
    "斩铁剑量表": "Zantetsuken gauge",
    "(1~5级,Lv5 清空对手恢复血)和专属\"跳跃\"架势。":
        " (levels 1-5; at level 5 it wipes the opponent's recoverable health) "
        "and his own \"jump\" stance.",
    "不用架势就等于没在玩克莱夫":
        "Not using the stances is not really playing Clive",
    "——不死鸟瞬移、光之翼、精准闪避必须刻进肌肉记忆。弱点:":
        " — Phoenix Shift, Wings of Light and Precision Dodge have to be "
        "muscle memory. Weaknesses: ",
    "下段贫弱": "weak lows",
    "(d+1 尚可),对懂招的对手择不动人;部分动作前摇怪异需适应。":
        " (d+1 is passable), so the mix-up does not move an opponent who knows "
        "the matchup, and some animations start oddly enough to need getting "
        "used to.",
    "架势核心": "Stance core",
    "架势详解": "Stances in detail",
    "凤凰接续": "Phoenix follow-ups",
    "很多招式可按住 F 转凤凰(如 4,4~F),被防后靠瞬移拉扯保持压力":
        "Many moves go into Phoenix by holding F (4,4~F for one), so a blocked "
        "string still keeps pressure through the shift",
    "进攻主发动机": "the main attack engine",
    "火焰突进拉近距离": "a fire dash that closes distance",
    "f+4 或 4,4~F 或众多招式按住 F。火焰突进拉近距离,派生 1(热浪)/2,1(升腾)/"
    "2,2(钢刃斩投)/4(下段纵火者)/1+2(绯红旋风HE)/3+4(雷电踏)/1+4(斩铁剑),进攻主发动机":
        "f+4, or 4,4~F, or hold F on any of a long list of moves. A fire dash "
        "that closes distance, with follow-ups 1 (Heatwave) / 2,1 (Rising "
        "Flame) / 2,2 (Steel Slash) / 4 (Firestarter) / 1+2 (Scarlet Cyclone, "
        "Heat engager) / 3+4 (Bolt Boot) / 1+4 (Zantetsuken) — the main attack "
        "engine",
    "专属跳跃架势": "his own jump stance",
    "u/f 专属跳跃架势:1(狮鹫猎手)/2,2(焰雨,连招核心)/3/4;延迟输入版伤害略高":
        "u/f, his own jump stance: 1 (Griffin Hunter) / 2,2 (Burning Rain, a "
        "combo staple) / 3 / 4; the delayed input does slightly more damage",
    "气流延迟版": "Updraft, delayed input",
    "气流派生有延迟输入版,伤害+1~2 但难度大,追求极限再练":
        "The Updraft follow-ups have a delayed-input version worth 1-2 more "
        "damage but much harder — one for when you are chasing the maximum",
    "延迟输入版伤害略高": "the delayed input does slightly more damage",
    "当身体系": "Reversal toolkit",
    "b+3 (中上) + 3+4 (下段) 双当身覆盖全高度;f,f+1+2 反击变审判之雷":
        "b+3 (mid and high) plus 3+4 (low) covers every height between them; "
        "on counter hit f,f+1+2 becomes Judgment Bolt",
    "b+3 中上段当身:成功后 2(精准反击35) 或 1+2(钢刃突进35);下段则用 3+4 光辉反击(20)":
        "b+3 reverses mids and highs: on success, 2 (Precision Counter, 35) or "
        "1+2 (Dash of Steel, 35); for lows use 3+4 (Radiant Counter, 20)",
    "3+4 光辉反击直接 20 伤害+起势":
        "3+4 (Radiant Counter) is a flat 20 damage and takes the initiative",
    "3+4 或 3,3。巴哈姆特之翼悬浮:1(迪亚)/2(脉冲弹幕);对空中对手 2 变":
        "3+4, or 3,3. The Bahamut's-wing hover: 1 (Dia) / 2 (Impulse); against "
        "an airborne opponent 2 becomes ",
    "追击核爆(70伤)": "an aerial chase blast (70 damage)",
    "光翼中 2 → 追击核爆 70 伤":
        "WOL 2 → aerial chase blast, 70 damage",
    "量表优先级": "Gauge priority",
    "没事就打 1,2 / 2,2,2,1+2 攒量表;连招收尾能接 1+4 就接,Lv5 是逆转发动机":
        "Throw out 1,2 and 2,2,2,1+2 whenever you can to build the gauge; end "
        "combos with 1+4 whenever it fits — level 5 is what turns a match "
        "around",
    "血条下方 1~5 级,特定招式充能(1,2 / 2,2,2,1+2 等);1+4 释放:Lv1 暗黑之腕10,"
    "Lv2-4 斩铁剑45,":
        "Levels 1-5, shown under the health bar and charged by specific moves "
        "(1,2 and 2,2,2,1+2 among them). 1+4 spends it: level 1 Arm of "
        "Darkness for 10, levels 2-4 Zantetsuken for 45, ",
    "Lv5 究极斩铁剑 80 并清空对手恢复血":
        "level 5 Ultimate Zantetsuken for 80, which also wipes the opponent's "
        "recoverable health",
    "。低于2格不要按!": ". Do not press it below level 2.",
    "快速确反": "Quick punish",
    "快速确反 + 斩铁剑充能,没事多按":
        "A quick punish that also charges Zantetsuken — press it often",
    "热能专属连段": "Heat-only strings",
    "热能中 f+2,2,1 可蓄力(25→30),中段确认":
        "In Heat, f+2,2,1 can be charged (25 → 30) and confirms as a mid",
    "直接转热能进攻": "goes straight into Heat offence",
    "f+1+2(,1) 日珥,直接转热能进攻":
        "f+1+2(,1), Prominence — straight into Heat offence",
    "2+3 新生狱火(55) / 凤凰中 2+3 钢之舞(42,更快更飘忽)":
        "2+3 Infernal Flames of Rebirth (55) / PHX 2+3 Dancing Steel (42, "
        "faster and harder to read)",
    "中段确认串;d/f+1,4,3 是连招回旋主力":
        "a confirmable mid string; d/f+1,4,3 is the workhorse combo tornado",
    "d/f+1,1,1 绯红突进 / u+1+2 烈焰系,全中段大压制":
        "d/f+1,1,1 Crimson Rush / u+1+2 Blazing Rush — all mid, heavy pressure",
    "全中段大压制": "all mid, heavy pressure",
    "1+2 / f+1+2 / 凤凰中1+2 三条,f+1+2 兼 -13 确反":
        "three of them — 1+2 / f+1+2 / PHX 1+2 — and f+1+2 doubles as a -13 "
        "punish",
    "主用 d+1 / d/f+3(,1) / 凤凰中4;别指望纯二择开人,靠架势压制骗出招":
        "Use d+1 / d/f+3(,1) / PHX 4; do not expect a pure mix-up to open "
        "anyone, bait the button out with stance pressure instead",
    "收尾改 凤凰中2,1 (半屏运载);破墙用 凤凰中1+2":
        "Change the ending to PHX 2,1 to carry half the screen; use PHX 1+2 to "
        "break the wall",
    "d/f+2:距离极远,大多数怒气技/大硬直都能罚":
        "d/f+2: enormous range, punishes most rage arts and anything with long "
        "recovery",
    "-15 起浮": "-15 launch",
    "距离极远": "enormous range",
    "大多数怒气技": "most rage arts",
    "大硬直都能罚": "and anything with long recovery",
    ":i15 双段起浮,主力确反,距离远能罚各种怒气技":
        ": i15, a two-hit launcher and the main punish; the range lets it hit "
        "rage arts",
    ":主力下段(20起),命中追加 1 共 58 伤害":
        ": the main low (20 on its own); follow with 1 on hit for 58 total",
    ":反击时变": ": on counter hit it becomes ",
    ":热能发动技,追加斩击爆发": ": a Heat engager with a follow-up burst",
    ":超长距离上段拒止,连招回旋(T!)工具":
        ": a very long-range high that denies approaches, and the combo "
        "tornado (T!) tool",
    ":远程魔弹骚扰(可蓄力)": ": a ranged magic bolt for chip pressure (chargeable)",
    ":连招起手核心过渡,接气流派生":
        ": the core combo-starter transition, into the Updraft follow-ups",
    ":霸体;迎击时变蓄力反击":
        ": armoured; on counter hit it becomes the windup counter",
    "(迎击变蓄力反击)": "(counter hit turns it into the windup counter)",
    "b+1+2 (迎击变蓄力反击)":
        "b+1+2 (counter hit turns it into the windup counter)",
    "b+2 (超长上段) / d/f+2 / f,f+2": "b+2 (very long high) / d/f+2 / f,f+2",
    "(超长上段)": "(very long high)",
    "(命中时强化)": "(stronger on hit)",
    "2, 2, 2 (命中时强化)": "2, 2, 2 (stronger on hit)",
    "(对倒地)": "(vs grounded)",
    "d/f+2, 2, 2 (对倒地)": "d/f+2, 2, 2 (vs grounded)",
    "(可蓄力)": "(chargeable)",
    "(附带充能)": "(charges the gauge)",
    "1,2 (附带充能) / 4,2": "1,2 (charges the gauge) / 4,2",
    "(热浪)": "(Heatwave)",
    "(升腾)": "(Rising Flame)",
    "(钢刃斩投)": "(Steel Slash)",
    "(下段纵火者)": "(Firestarter)",
    "(绯红旋风HE)": "(Scarlet Cyclone, Heat engager)",
    "(雷电踏)": "(Bolt Boot)",
    "(斩铁剑)": "(Zantetsuken)",
    "(狮鹫猎手)": "(Griffin Hunter)",
    "(焰雨,连招核心)": "(Burning Rain, a combo staple)",
    "(半屏运载)": "(carries half the screen)",
    "(量表≥2,满表最佳)": "(gauge 2 or more; best on a full gauge)",
    "(稳定 +60)": "(consistent +60)",
    "(简化 +58)": "(simplified +58)",
    "(斩铁剑 +57~85)": "(Zantetsuken +57-85)",
    "(斩铁剑简版 +52~81)": "(simplified Zantetsuken +52-81)",
    "f+3 (稳定 +60)": "f+3 (consistent +60)",
    "f+3 (简化 +58)": "f+3 (simplified +58)",
    "f+3 (斩铁剑 +57~85)": "f+3 (Zantetsuken +57-85)",
    "f+3 (斩铁剑简版 +52~81)": "f+3 (simplified Zantetsuken +52-81)",
    "f+4 (或 4,4~F 等)": "f+4 (or 4,4~F and others)",
    "f, f+1+2 (反击时)": "f, f+1+2 (on counter hit)",
    "(反击时)": "(on counter hit)",
    "d/b+1+2,1 → 气流中3 → 冲刺 4,4~F → 凤凰中2,1 T! → 冲刺 b+2~F → 凤凰中1+4 "
    "(量表≥2,满表最佳)":
        "d/b+1+2,1 → GAR 3 → dash 4,4~F → PHX 2,1 T! → dash b+2~F → PHX 1+4 "
        "(gauge 2 or more; best on a full gauge)",
    ",拒止神器": ", a superb denial tool",
    ",顶级连招收尾;自带下段防反(光辉反击)":
        ", a top-tier combo ender that comes with its own low parry (Radiant "
        "Counter)",
    "或众多招式按住": "or hold F on any of a long list of moves",
    "破墙用": "to break the wall, use",
    "墙运载": "Wall carry",
    "下段防反": "Low parry",
    "精准闪避": "Precision Dodge",
    "日珥": "Prominence",
    "热浪": "Heatwave",
    "绯红突进": "Crimson Rush",
    "烈焰系": "Blazing Rush",
    "剜击": "Gouge",
    "处刑者": "Executioner",
    "屠龙者": "Wyrm Killer",
    "审判之杖": "Staff of Judgment",
    "审判之雷(50伤)": "Judgment Bolt (50 damage)",
    "致命引燃": "Lethal Ignition",
    "致命拥抱": "Deadly Embrace",
    "蓄力重击": "Windup",
    "双热能斩": "Two Heat engagers",
    "水流爆破": "Hydro Blast",

    # -- kunimitsu --------------------------------------------------------
    # Move names quoted in the prose take Wavu's romanisation, so a reader can
    # find the row they refer to. The card each one comes from is in
    # wavu_kunimitsu_names.txt.
    "国光二世是": "Kunimitsu II is a ",
    "快攻忍者": "rushdown ninja",
    "：极快的移动与突进(刹那驱)、难以捉摸的高低二择和多架势混淆是她的招牌。弱点是":
        ": very fast movement and approach (Setsunagake), an elusive high-low "
        "mix-up and confusion across several stances are what she does. Her "
        "weakness is ",
    "招式偏直线": "how linear her moves are",
    "(尤其怕向右横移)、单发伤害低(靠长连招堆伤害)。远距离用苦无(qcf+1)骚扰,"
    "找机会用刹那驱贴身,近身后用架势派生打出压制;进入热能后贴墙压制最凶。背身(BT)期间":
        " (a sidestep to her right especially), plus low damage per hit, which "
        "she makes up for with long combos. At range, harass with the kunai "
        "(qcf+1); look for a chance to close with Setsunagake, then pressure "
        "with the stance follow-ups. In Heat, at the wall, she is at her most "
        "dangerous. While back-turned (BT) she ",
    "背身无法防御,靠快速派生(荒魂斩系)和秘花·里(3+4当身)自保":
        "cannot block from back-turned, and relies on fast follow-ups (the "
        "Aratama Slash family) and Secret Flower Ura (3+4 reversal) to protect "
        "herself",
    "背身风险": "Back-turned risk",
    "直线弱点": "Linear",
    "整套体系怕右横移,对横移多的对手多用追踪技(背身1,3 / d/b+2,4,2)":
        "The whole game plan struggles against a sidestep to her right, so "
        "against someone who moves a lot, lean on the tracking moves (BT 1,3 "
        "and d/b+2,4,2)",
    "伤害结构": "Damage profile",
    "单发伤害低,务必把每次浮空转化为满载连招+墙运载":
        "Low damage per hit, so every launch has to become a full combo with "
        "wall carry",
    "刹那驱进出": "Getting in and out of Setsunagake",
    "f+3 / f+4~F / 2,2,2~F / 背身4~F 均可进架势;B 后撤取消钓挥空":
        "f+3, f+4~F, 2,2,2~F and BT 4~F all enter the stance; B backs out of it "
        "to bait a whiff",
    "快速中段,按住 F 转刹那驱后变安全,是进攻发动机":
        "a fast mid that becomes safe by holding F into Setsunagake — the "
        "attack engine",
    "苦无控场": "Kunai zoning",
    "苦无远程压制(10,28 投);焰锁苍月带位移突进":
        "The kunai pressures from range (10, or 28 as a throw); Ensa Sogetsu "
        "closes in with it",
    "qcf+1 命中后按 F 变贯穿追加;远距离消耗+逼近利器":
        "After qcf+1 hits, press F for the piercing follow-up — chip damage at "
        "range and a way in",
    "下段poke:潜影斩与卍旋踢,用来逼对手蹲防":
        "Low pokes: the shadow slash and the Manji spin kicks, there to make "
        "the opponent crouch",
    "热能延伸": "Extending Heat",
    "热能发动技按住 F 冲刺后可续 qcf+2 → f+1+2 → qcf+1+2 大伤害":
        "Hold F after a Heat engager to dash, then continue qcf+2 → f+1+2 → "
        "qcf+1+2 for big damage",
    "热能随手可开": "Heat opens from almost anything",
    "发动路线多": "Many engager routes",
    "f+1+2 三派生 / WS+2,1 / 背身1,4 / 火遁1,2 / 刹那驱1+2,热能随手可开":
        "f+1+2 and its three follow-ups / WS 2,1 / BT 1,4 / KAT 1,2 / SET 1+2 "
        "— Heat opens from almost anything",
    "f+1+2派生 / WS+2,1 / 背身1,4 / 火遁1,2 / 刹那驱1+2":
        "f+1+2 follow-ups / WS 2,1 / BT 1,4 / KAT 1,2 / SET 1+2",
    "热能中 WS+2,1~F / 背身1,4~F / 火遁1,2~F":
        "In Heat: WS 2,1~F / BT 1,4~F / KAT 1,2~F",
    "热能中 2+3 (焰乱·月镜) 50伤中段投,距离好":
        "In Heat, 2+3 (Flame Riot: Lunar Mirror) is a 50-damage mid throw with "
        "good range",
    "热能中 d/b+1+2:安全的长距离中段(接地),主力开局":
        "In Heat, d/b+1+2 is a safe long-range mid that hits grounded — the "
        "main way to open",
    "热能+火遁中 d+1+2:带瞬身动画的超快下段":
        "In Heat and KAT, d+1+2 is a very fast low with a teleport animation",
    "安全的长距离中段": "a safe long-range mid",
    "带瞬身动画的超快下段": "a very fast low with a teleport animation",
    "主力开局": "the main way to open",
    "较安全的中段确认串(云雾斩·胧偃月)":
        "a fairly safe confirmable mid string (Unmuzan > Oboro Engetsu)",
    "标准浮空确反": "standard launch punish",
    "天翔回旋(升龙),起浮": "Tensho Kaisen (a rising uppercut), launches",
    "影抚斩,转背身": "Kagenade Slash, into back-turned",
    "霞斩(迎击变": "Kasumi Slash (on counter hit it becomes ",
    "飞龙焦花,大伤害": "Hiryu Scorching Blossoms, big damage",
    "大伤害": "big damage",
    ") / 霜滑(下段滑铲),核心二择":
        ") and Frost Slide (a low slide) — the core mix-up",
    ",注意风险管理。": ", so manage the risk.",
    "凤尾": "Phoenix Tail",
    "升月斩": "Rising Moon Slash",
    "夜幕": "Veil of Night",
    "影莲刃": "Shadow Lotus Blade",
    "烈火百合": "Blazing Fire Lilies",
    "牛头龙": "Gozuryu",
    "白光焰": "Yakouga",
    "双焰斩": "Twin Flame Slash",
    "热能斩": "Heat slash",
    "焰舞·上弦月": "Flame Dance: Waxing Moon",
    "焰舞·下弦月": "Flame Dance: Waning Moon",
    "火遁中 2 (瞬身)": "KAT 2 (teleport)",
    "(瞬身)": "(teleport)",
    "(接地)": "(hits grounded)",
    "(热能中)": "(in Heat)",
    "(鼯鼠扫)": "(Sasabi Barai)",
    "(迎击时强化)": "(stronger on counter hit)",
    "d+3+4 (迎击时强化)": "d+3+4 (stronger on counter hit)",
    "(d/f+2 等常规起浮)": "(d/f+2 and other standard launchers)",
    "3,4 / 1,1,4 命中": "3,4 / 1,1,4 on hit",
    "SS+2 命中": "SS 2 on hit",
    "u/f+2 命中": "u/f+2 on hit",
    "背身3 命中": "BT 3 on hit",
    "~F 转背身;1,1,1+2 转火遁续压":
        "~F goes into back-turned; 1,1,1+2 goes into KAT to keep pressuring",
    "→ u/f+3+4, 2 (鼯鼠扫)": "→ u/f+3+4, 2 (Sasabi Barai)",
    "→ 追击确定,继续压制": "→ the follow-up is guaranteed, pressure continues",
    ":三个派生全是热能发动技,主力确反兼开热能":
        ": all three follow-ups are Heat engagers — the main punish, and a way "
        "into Heat",
    ":瞬身移形闪避对手攻击并惩罚":
        ": teleports out of the way of an attack and punishes it",
    ":确反距离好,反击(CH)时起浮":
        ": good punish range, and launches on counter hit",
    "：快速多段,距离好;第二段后按 1+2 转火遁续压":
        ": fast, multi-hit and long; after the second hit, 1+2 goes into KAT "
        "to keep pressuring",
    "：距离优秀的主力浮空技": ": the main launcher, with excellent range",
    "：霸体,吸收中/上段攻击,迎击时伤害提升":
        ": armoured — it absorbs mids and highs, and does more damage on "
        "counter hit",

    # -- law --------------------------------------------------------------
    "定位：近身压制与节奏控制。用刺拳、d/f+1、龙锤和低踢逼对手出手，"
    "再以 d/f+2、反击命中与龙构分支兑现伤害。":
        "Game plan: close-range pressure and rhythm control. Use jabs, d/f+1, "
        "Dragon Hammer and low kicks to make the opponent press a button, then "
        "cash in with d/f+2, counter hits and the Dragon Charge branches.",
    "洛的强度集中在近距离；远距离只用 f,F+2、u/f+2、f+3,1 等安全手段接近。":
        "Law's strength is all at close range; from far out, only approach "
        "with safe tools like f,F+2, u/f+2 and f+3,1.",
    "近身框架": "Close-range frames",
    "最重要的短距离控制工具；观察对手按键、横移或蹲防后再分流。":
        "His most important short-range control tool; watch whether the "
        "opponent presses, steps or crouches, then branch accordingly.",
    "龙锤安全压制，反击命中可起连；与 d/b+3 组成核心中下择。":
        "Dragon Hammer is safe pressure and combos on counter hit; with d/b+3 "
        "it forms the core mid-low mix-up.",
    "中段压制": "Mid pressure",
    "低段消耗": "Low chip",
    "d/b+3 命中后保持攻势；横移中3伤害更高并进入龙构。":
        "Keep attacking after d/b+3 hits; SS 3 does more damage and goes into "
        "Dragon Charge.",
    "不要自动续完": "Do not finish strings on autopilot",
    "b+1,2,2 与拳串可延迟、停手或转龙构；固定续完会被蹲避或确反。":
        "b+1,2,2 and the punch strings can be delayed, stopped, or taken into "
        "Dragon Charge; finishing them the same way every time gets ducked or "
        "punished.",
    "龙构控制": "Dragon Charge control",
    "对手按键用龙吼，对手横移/防守时切蹲伏滑铲或延迟继续压制。":
        "Against a button, use Dragon Roar; against a step or a block, switch "
        "to the crouching slide or delay and keep pressuring.",
    "滑铲要铺垫": "Set the slide up",
    "先用起身中3、起身中4与龙构中段逼站防，再加入滑铲。":
        "Make them block standing with WS 3, WS 4 and the Dragon Charge mids "
        "first, then start mixing the slide in.",
    "滑铲": "Slide Kick",
    "洛的标志性全蹲下段；命中后通常可追 1+2。":
        "Law's signature full-crouch low; 1+2 usually follows on hit.",
    "滑铲续热": "The slide extends Heat",
    "滑铲命中 → 1+2；多数位置稳定追击，同时延长热能资源。":
        "Slide on hit → 1+2; it connects from most positions and stretches the "
        "Heat timer at the same time.",
    "热能专用与强化": "Heat-only and Heat-boosted",
    "热能双截棍": "Heat nunchaku",
    "：范围、追踪与安全性全面强化，命中可起浮并恢复热能。":
        ": more range, better tracking and safer across the board; on hit it "
        "launches and returns Heat.",
    "拳技自动格挡": "Auto-parries punches",
    "热能中进入龙构会自动格挡拳技；成功格挡与 b+2+4 可恢复热能。":
        "Entering Dragon Charge during Heat auto-parries punches; a successful "
        "parry and b+2+4 both return Heat.",
    "保留热能": "Save your Heat",
    "需要对拼特定角色时不要过早耗尽热能；龙构自动格挡与强化 1+2 是关键胜负点。":
        "Against some characters, do not burn Heat early: the Dragon Charge "
        "auto-parry and the boosted 1+2 are what decide those rounds.",
    "先抢近身": "Get in first",
    "简易通用起浮": "Simple all-purpose launcher",
    "安全起浮": "Safe launcher",
    "标准确反并转龙构。": "The standard punish, and it goes into Dragon Charge.",
    "站姿起浮确反。": "Standing launch punish.",
    "最快起身确反，可转龙构。":
        "Fastest while-standing punish, and it goes into Dragon Charge.",
    "起身11帧工具；转龙构后继续压制或进入滑铲二择。":
        "The 11-frame while-standing tool; go into Dragon Charge to keep "
        "pressuring or to set up the slide mix-up.",
    "15帧中段起浮，适合拦截抢招与横移后的对手。":
        "A 15-frame mid launcher, good for catching a button or someone who "
        "has just stepped.",
    "主力挥空惩罚，墙边优先虎牙。":
        "The main whiff punish; near the wall, prefer Tiger Fang.",
    "跳过下段的热能发动技，适合终结压制回合。":
        "A Heat engager that skips the low, good for ending a pressure turn.",
    "低段回避": "Low evasion",
    "低段格挡 T!": "Low parry T!",
    "闪光拳击倒。": "Flash Fist knocks down.",
    "龙上勾拳起浮。": "Dragon Uppercut launches.",
    "蹲姿启动": "Crouching start",
    "墙!": "Wall!",
    "热能中龙构中 自动格挡拳技":
        "In Heat, Dragon Charge auto-parries punches",

    # -- xiaoyu -----------------------------------------------------------
    "晓雨是": "Xiaoyu is an ",
    "回避特化": "evasion specialist",
    "角色：凤凰架势(AOP)蹲避上段与大量中段,背身横移增强,靠钻空子和惩罚对手失误抢回合。":
        ": the Phoenix stance (AOP) ducks highs and a good number of mids, "
        "back-turned sidesteps are stronger, and she takes her turn by "
        "slipping through gaps and punishing mistakes.",
    "是核心50/50架势——热能中跳过第一步,择更凶;热能+贴墙是她最强的场合。"
    "弱点:手短脚短、非热能时难开铁龟、立回缺快速CH技、下段poke伤害低。":
        " is the core 50/50 stance — in Heat it skips the first step, which "
        "makes the guess nastier, and Heat at the wall is her strongest "
        "situation. Weaknesses: short reach, trouble opening a blocker outside "
        "Heat, no fast counter-hit tool in neutral, and low damage on her low "
        "pokes.",
    "凤凰强化回避": "Phoenix evasion, upgraded",
    "凤凰中按 d (蝴蝶) 进一步下潜,可躲部分怒气技":
        "Pressing d in AOP (Butterfly) ducks lower still, under some rage arts",
    "注意:凤凰与背身期间无法防御":
        "Note: she cannot block during AOP or back-turned",
    "背身保命": "Staying alive back-turned",
    "背身被摸背时 BT.b+1+3 防反": "when caught back-turned, BT.b+1+3 parries",
    ",务必练成肌肉记忆": ", so drill it until it is muscle memory",
    "第1帧生效": "active from frame 1",
    "背身d/b后撤": "Backing off with BT d/b",
    "背身d/b 拉开距离钓挥空 → WS+1+2,1+2(安全) / WS+2(钓CH) / u/b+3(大罚)":
        "BT d/b backs out to bait a whiff → WS 1+2,1+2 (safe) / WS 2 (fishing "
        "for a counter hit) / u/b+3 (the big punish)",
    "对手怕什么": "What the opponent fears",
    "对手乱按=晓雨最开心;对手能忍耐后撤=最难打,要靠 f,f+3 / f,f+4 逼近":
        "A button-masher is what Xiaoyu wants; someone patient who backdashes "
        "is the hard matchup, and f,f+3 / f,f+4 are how she closes it",
    "热能强化": "Heat boost",
    "f+2,1,H.2 / f,f+1,H.2 确认连段;催眠跳步一;背身热能斩51伤":
        "f+2,1,H.2 and f,f+1,H.2 are the confirmable strings; HYP skips a step; "
        "the back-turned Heat smash does 51",
    "俯冲猎鹰:被防+7的安全起浮技,强制凤凰二择的主要方式":
        "Diving Falcon: a safe launcher that is +7 on block, and her main way "
        "to force the Phoenix mix-up",
    "i10 主力:扇舞转背身;,B 转催眠(命中后再转);尾段 1+2 惩罚乱动的对手":
        "The i10 workhorse: Fan Dance into back-turned; ,B goes into HYP (after "
        "it hits); the 1+2 ending punishes anyone still moving",
    "i14 长距中段poke转背身;CH大幅有利强制背身二择":
        "An i14 long-range mid poke into back-turned; on counter hit the "
        "advantage is big enough to force the back-turned mix-up",
    "i14 中段check,": "An i14 mid check, ",
    "i8 中段": "i8 mid",
    "基础蹲拳": "Basic crouch jab",
    "并转背身;尖端命中后 背身d/b 拉开钓挥空":
        "and goes into back-turned; at the tip, BT d/b backs out to bait a whiff",
    "横移后下段,CH起浮;尖端命中后后撤钓挥空":
        "A low out of a sidestep that launches on counter hit; at the tip, back "
        "off to bait a whiff",
    "横移追踪上段,被防+1、命中+13确保 b+4,1(热能发动)":
        "Tracks a sidestep (high), +1 on block and +13 on hit, which guarantees "
        "b+4,1 (Heat engager)",
    "长距离下段避上,被防可接背身防反(BT.b+1+3)自保;CH确保背身2,1":
        "A long low that ducks highs; on block, BT.b+1+3 covers her, and a "
        "counter hit guarantees BT 2,1",
    "自然连段且命中+5 强制对手蹲姿,蹲姿游戏主力下段":
        "A natural string that is +5 on hit and forces a crouch — the main low "
        "of her crouching game",
    "强制二择;CH直接大浮空":
        "forces the mix-up, and a counter hit launches high",
    "3=起浮;d/f+2系列近墙贴墙":
        "3 launches; the d/f+2 family carries to a nearby wall",
    ":蹲避上段+大量中段;横移右后进架势回避更强":
        ": ducks highs and a lot of mids; entering the stance after a sidestep "
        "right evades even more",
    ":长距离CH起浮,被防仅-1,可贴墙,近乎无解的骗招":
        ": a long-range counter-hit launcher, only -1 on block, carries to the "
        "wall — very nearly a free move",
    "确认小连段": "Confirmable mini-combo",
    "连段确反": "String punish",
    "避上段": "Ducks highs",
    "击倒": "Knockdown",
    "起浮,双向追踪": "launches, tracks both ways",
    "最高伤害起浮": "highest-damage launcher",
    "蹲姿最快起浮": "fastest crouching launcher",
    "命中/被防都进": "enters on hit or block",
    "拳挡成功": "punch parry lands",
    "云峰": "Clouded Peak",
    "凤凰炮": "Phoenix Cannon",
    "热能": "Heat",
    "!全游戏第二快,专治贴脸压制,命中转背身+1":
        "! The second-fastest in the game, the answer to point-blank pressure, "
        "and +1 into back-turned on hit",
    "1 / f+4 / d/b+3 命中": "1 / f+4 / d/b+3 on hit",
    "b+3 命中": "b+3 on hit",
    "f+4 命中 (+44)": "f+4 on hit (+44)",
    "背身3 命中 (+30)": "BT 3 on hit (+30)",
    "背身4 替代 (+54)": "BT 4 alternative (+54)",
    "背身f+1+2 拳挡成功 (+64)": "BT f+1+2, punch parry lands (+64)",
    "背身时 f+1+2 (拳当身)": "BT f+1+2 (punch reversal)",
    "BnB 替代 (+53)": "Bread-and-butter alternative (+53)",
    "催眠3(第二步) (+40)": "HYP 3 (second step) (+40)",
    "催眠3(第三步) (+58)": "HYP 3 (third step) (+58)",
    "催眠中 2+3 (b,b取消)": "HYP 2+3 (b,b cancels)",
    "凤凰中 d+1 (反击时)": "AOP d+1 (on counter hit)",
    "凤凰中 u/f 空中 3": "AOP u/f, airborne 3",
    "凤凰中 u/f 落地 3": "AOP u/f, landing 3",
    "凤凰中 u/f 落地 4": "AOP u/f, landing 4",
    "1, d+2 (,B转催眠)": "1, d+2 (,B into HYP)",
    "(,B转催眠)": "(,B into HYP)",
    "(b,b取消)": "(b,b cancels)",
    "(第二步)": "(second step)",
    "(第三步)": "(third step)",
    "(拳当身)": "(punch reversal)",
    "(投)": "(throw)",
    "(下段)": "(low)",
    "(中段HE)": "(mid, Heat engager)",
    "(起浮)": "(launches)",
    "(打抢招)": "(beats a button)",
    "(蓄力)": "(charged)",
    "(翔焰)": "(Soaring Blaze)",
    "(转背身)": "(into back-turned)",
    "(转催眠)": "(into HYP)",
    "(进催眠)": "(enters HYP)",
    "(被防+7)": "(+7 on block)",
    "(i11抢CH,倒地追击确定)":
        "(i11, beats a button; the grounded follow-up is guaranteed)",
    "(CH d/b+3 同)": "(same for CH d/b+3)",
    "d/f+1 (转背身)": "d/f+1 (into back-turned)",
    "f, f+3 (转背身)": "f, f+3 (into back-turned)",
    "f, f+4 (转催眠)": "f, f+4 (into HYP)",
    "f,f+4 (翔焰)": "f,f+4 (Soaring Blaze)",
    "f,f+4 (进催眠)": "f,f+4 (enters HYP)",
    "f,f,f+3 (被防+7)": "f,f,f+3 (+7 on block)",
    "→ 4 (i11 抢CH,倒地追击确定)":
        "→ 4 (i11, beats a button; the grounded follow-up is guaranteed)",
    "→ d/f+2,1+2 (CH d/b+3 同)": "→ d/f+2,1+2 (same for CH d/b+3)",
    "→ 催眠2 (中段HE) / 催眠3 (下段) / 催眠4 择":
        "→ HYP 2 (mid, Heat engager) / HYP 3 (low) / HYP 4 — the guess",
    "→ 凤凰2,1 (打抢招) / 凤凰u/f+3 (起浮)":
        "→ AOP 2,1 (beats a button) / AOP u/f+3 (launches)",
    "1或2": "1 or 2",
}
