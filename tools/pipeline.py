# -*- coding: utf-8 -*-
"""Unified per-character pipeline: graphical input notation + startup
frames + theme/notation toggles, replicating everything applied to the
Xiaoyu sheet in one pass.

Usage: python pipeline.py <jun|kunimitsu|clive|law>
"""
import io
import os
import re
import sys

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SCRATCH = os.path.dirname(os.path.abspath(__file__))  # wavu_*.txt live here
BASE = os.path.dirname(SCRATCH)
SITE = os.path.join(BASE, "docs")
CSS_PATH = os.path.join(
    BASE, "design", "notation-wireframe", "tekken-input-notation.css"
)

COMMON_STATES = ["可发动热能时", "看准对手下段攻击", "接近空中对手", "愤怒中",
                 "热能中", "起身中", "蹲伏中", "横移中", "背墙时",
                 "左侧", "右侧", "背后", "冲刺", "奔跑", "背身"]
COMMON_PREFIX = {"热能中": "H.", "愤怒中": "R.", "背墙时": "(Back_to_wall).",
                 "可发动热能时": "", "左侧": "Left_Throw",
                 "右侧": "Right_Throw", "背后": "Back_Throw",
                 "看准对手攻击": "", "看准攻击": "",
                 "看准对手下段攻击": "", "看准对手投技": ""}

CONFIG = {
    # xiaoyu was converted by the original incremental scripts; config kept
    # here for reference (states/prefix mapping) and idempotent reruns
    "xiaoyu": {
        "file": "xiaoyu_tk8_movelist.html",
        "acc": "#ff9fce", "acc_ink": "#8c2f5c",
        "wavu": "wavu_xiaoyu.txt",
        "states": ["凤凰中", "催眠中", "背身时", "看准对手拳击",
                   "可发动时"] + COMMON_STATES,
        "prefix": dict(COMMON_PREFIX, **{
            "凤凰中": "AOP.", "催眠中": "HYP.", "背身时": "BT.",
            "可发动时": ""}),
    },
    "jun": {
        "file": "jun_tk8_movelist.html",
        "acc": "#7ed6b8", "acc_ink": "#1f6f5b",
        "wavu": "wavu_jun.txt",
        "states": ["幻月中自动防反下段", "看准对手投技", "看准对手攻击",
                   "幻月中", "出云中", "御生中", "刈足中"] + COMMON_STATES,
        "prefix": dict(COMMON_PREFIX, **{
            "幻月中": "GEN.", "出云中": "IZU.", "御生中": "MIA.",
            "刈足中": "db+4,"}),  # 刈足=db+4 sweep; wavu "Kariashi Hakuro"
    },
    "kunimitsu": {
        "file": "kunimitsu_tk8_movelist.html",
        "acc": "#ff93a6", "acc_ink": "#8c2338",
        "wavu": "wavu_kunimitsu.txt",
        "states": ["刹那驱中迎击时", "背身时看准对手攻击", "热能中且火遁中",
                   "卍旋踢中", "刹那驱中", "看准攻击", "火遁中", "背身时",
                   "鼯鼠中"] + COMMON_STATES,
        "prefix": dict(COMMON_PREFIX, **{
            "火遁中": "KAT.", "刹那驱中": "SET.", "刹那驱中迎击时": "CH.SET.",
            "鼯鼠中": "MUS.", "背身时": "BT.", "热能中且火遁中": "H.KAT.",
            "背身时看准对手攻击": "BT.",
            "卍旋踢中": "db+3,3,3,3,3,",
            "接近空中对手": "(Airborne)."}),
    },
    "clive": {
        "file": "clive_tk8_movelist.html",
        "acc": "#9db9ff", "acc_ink": "#2f4272",
        "wavu": "wavu_clive.txt",
        "states": ["光翼中接近空中对手", "精准闪避成功后", "看准对手攻击",
                   "光翼中", "凤凰中", "气流中", "热能"] + COMMON_STATES,
        "prefix": dict(COMMON_PREFIX, **{
            "光翼中": "WOL.", "凤凰中": "PHX.", "气流中": "GAR.",
            "精准闪避成功后": "b+3,P,", "热能": "H."}),
    },
    "law": {
        "file": "law_tk8_movelist.html",
        "acc": "#ffe07a", "acc_ink": "#6e5200",
        "wavu": "wavu_law.txt",
        "states": ["热能中龙构中", "倒地仰面时", "自动格挡拳技",
                   "龙构中", "背身时"] + COMMON_STATES,
        "prefix": dict(COMMON_PREFIX, **{
            "热能中龙构中": "H.DSS.", "龙构中": "DSS.",
            "背身时": "BT.", "蹲伏中": "hFC.", "起身中": "ws",
            "横移中": "ss",
            "倒地仰面时": "(While_down,_facing_up)."}),
    },
}

DIR_CLASS = {"f": "f", "b": "b", "u": "u", "d": "d",
             "d/f": "df", "d/b": "db", "u/f": "uf", "u/b": "ub"}
STANCE_ABBR = {"WS": "起身中", "FC": "蹲伏中", "SS": "横移中"}

TOKEN_RE = re.compile(r"""
    (?P<dir2>[dDuU]/[fFbB])
  | (?P<badge>SWL|GAR|T!|W!|CH)
  | (?P<qcf>qcf)
  | (?P<arrow>→)
  | (?P<btn>[1-4])
  | (?P<stance>WS|FC|SS)
  | (?P<neutral>N)
  | (?P<dir1>[fbudFBUD])(?![A-Za-z])
  | (?P<cjk>[一-鿿]+)
  | (?P<comma>,)
  | (?P<plus>\+)
  | (?P<tilde>~)
  | (?P<star>\*)
  | (?P<slash>/)
  | (?P<lparen>\()
  | (?P<rparen>\))
  | (?P<space>\s+)
  | (?P<other>.)
""", re.X)


def tokenize(text):
    return [(m.lastgroup, m.group()) for m in TOKEN_RE.finditer(text)]


def el_grid(btns):
    on = set(btns)
    return '<span class="tk-b">%s</span>' % "".join(
        '<i class="on">%s</i>' % n if n in on else "<i>%s</i>" % n
        for n in "1234")


def el_dir(v):
    return '<span class="tk-dir %s%s"></span>' % (
        DIR_CLASS[v.lower()], " hold" if v != v.lower() else "")


def el_sep(ch, extra=""):
    return '<span class="tk-sep%s">%s</span>' % (extra, ch)


def el_txt(s):
    return '<span class="tk-txt">%s</span>' % s


def el_state(s):
    return '<span class="tk-state">%s</span>' % s


DMG_PAREN = re.compile(r"^\+\d+$")


class Renderer:
    def __init__(self, states):
        self.states = states
        self.out = []
        self.pending = []
        self.pending_sep = None
        self.last = None
        self.grids = 0
        self.core = 0
        self.invalid = False

    def cjk_parts(self, run):
        parts, rest = [], run
        by_len = sorted(self.states, key=len, reverse=True)
        while rest:
            for w in by_len:
                if rest.startswith(w):
                    parts.append(("state", w))
                    rest = rest[len(w):]
                    break
            else:
                parts.append(("text", rest))
                rest = ""
        return parts

    def emit(self, html, last):
        if self.pending_sep:
            self.out.append(el_sep(self.pending_sep))
            self.pending_sep = None
        self.out.append(html)
        self.last = last

    def flush(self):
        if self.pending:
            self.emit(el_grid(self.pending), "grid")
            self.pending = []
            self.grids += 1
            self.core += 1

    def walk(self, tokens):
        i, n = 0, len(tokens)
        while i < n:
            kind, val = tokens[i]
            if kind == "space":
                pass
            elif kind == "btn":
                self.pending.append(val)
            elif kind == "plus":
                nxt = next((k for k, _ in tokens[i + 1:]
                            if k != "space"), None)
                if self.pending and nxt == "btn":
                    pass
                elif self.last == "state" or self.last is None:
                    pass
                else:
                    self.flush()
                    self.emit(el_sep("+"), "sep")
            elif kind == "comma":
                self.flush()
                if self.last == "grid":
                    self.pending_sep = "›"
            elif kind in ("dir1", "dir2"):
                self.flush()
                self.emit(el_dir(val), "dir")
                self.core += 1
            elif kind == "qcf":
                self.flush()
                self.emit(el_dir("d") + el_dir("d/f") + el_dir("f"), "dir")
                self.core += 1
            elif kind == "stance":
                self.flush()
                self.emit(el_state(STANCE_ABBR[val]), "state")
            elif kind == "neutral":
                self.flush()
                self.emit('<span class="tk-n">N</span>', "n")
                self.core += 1
            elif kind == "star":
                self.flush()
                self.emit(el_sep("＊"), "sep")
            elif kind == "tilde":
                self.flush()
                self.emit(el_sep("~"), "sep")
            elif kind == "arrow":
                self.flush()
                self.pending_sep = None
                self.emit(el_sep("→", " tk-arw"), "sep")
            elif kind == "badge":
                self.flush()
                self.emit('<span class="tk-tbang">%s</span>' % val, "text")
            elif kind == "slash":
                self.flush()
                self.pending_sep = None
                self.emit(el_txt("/"), "text")
            elif kind == "cjk":
                self.flush()
                for pk, pv in self.cjk_parts(val):
                    if pk == "state":
                        self.emit(el_state(pv), "state")
                    else:
                        self.emit(el_txt(pv), "text")
            elif kind == "lparen":
                j, depth = i + 1, 1
                while j < n and depth:
                    if tokens[j][0] == "lparen":
                        depth += 1
                    elif tokens[j][0] == "rparen":
                        depth -= 1
                    if depth:
                        j += 1
                inner = tokens[i + 1:j]
                raw = "".join(t[1] for t in inner)
                nonsp = [t for t in inner if t[0] != "space"]
                has_cjk = any(k == "cjk" for k, _ in nonsp)
                starts_or = nonsp and nonsp[0] == ("cjk", "或")
                if DMG_PAREN.match(raw.replace(" ", "")) or (
                        has_cjk and not starts_or):
                    self.flush()
                    self.emit(el_txt("(" + raw + ")"), "text")
                else:
                    self.flush()
                    self.emit(el_txt("("), "text")
                    if starts_or:
                        self.emit(el_txt("或"), "text")
                        k0 = inner.index(("cjk", "或"))
                        inner = inner[k0 + 1:]
                    self.walk(inner)
                    self.flush()
                    self.emit(el_txt(")"), "text")
                i = j
            elif kind == "rparen":
                self.flush()
                self.emit(el_txt(")"), "text")
            else:
                if re.match(r"[A-Za-z0-9]", val):
                    self.invalid = True
                self.flush()
                self.emit(el_txt(val), "text")
            i += 1
        return self


def parse_cmd(text, cfg, cap=6):
    stripped = text.strip()
    if not stripped:
        return None
    tokens = [t for t in tokenize(stripped)]
    # leading CJK run(s): every part becomes a state capsule
    lead = []
    while tokens and tokens[0][0] in ("cjk", "space"):
        if tokens[0][0] == "space":
            tokens = tokens[1:]
            continue
        r = Renderer(cfg["states"])
        for pk, pv in r.cjk_parts(tokens[0][1]):
            lead.append(el_state(pv))
        tokens = tokens[1:]
    if not tokens:
        # capsule-only command (e.g. a lone stance name): render if any
        if lead:
            return '<span class="tk-in tk-sm">%s</span>' % "".join(lead)
        return None
    r = Renderer(cfg["states"])
    r.walk(tokens)
    r.flush()
    # stance/parry-only commands (no buttons/directions) still render as long
    # as at least one state capsule was produced; pure text stays fallback
    has_state = any("tk-state" in frag for frag in lead + r.out)
    if r.invalid or (r.core == 0 and not has_state):
        return None
    if cap is not None and r.grids > cap:
        return None
    return '<span class="tk-in tk-sm">%s</span>' % "".join(lead + r.out)


CMD_CELL = re.compile(r'(<td class="cmd">)((?:<b>[^<]*</b>)?\s*)([^<]+)(</td>)')


def convert_cells(chunk, cfg, cap=6, stats=None):
    def repl(m):
        gfx = parse_cmd(m.group(3), cfg, cap)
        if gfx is None:
            if stats is not None:
                stats["kept"] += 1
            return m.group(0)
        if stats is not None:
            stats["done"] += 1
        return ('%s%s<span class="cmd-gfx">%s</span>'
                '<span class="cmd-txt">%s</span>%s'
                % (m.group(1), m.group(2), gfx, m.group(3), m.group(4)))
    return CMD_CELL.sub(repl, chunk)


# ---------------------------------------------------------------- layout
def find_balanced_table(html, pos):
    """Return (start, end) of the <table class="lt"> containing pos."""
    s = html.rindex('<table class="lt">', 0, pos)
    i, depth = s + 1, 1
    while depth:
        nt = html.find("<table", i)
        ct = html.find("</table>", i)
        if ct == -1:
            raise ValueError("unbalanced")
        if nt != -1 and nt < ct:
            depth += 1
            i = nt + 6
        else:
            depth -= 1
            i = ct + 8
    return s, i


def split_ltc(block):
    parts = block.split('<td class="ltc">')
    cells = []
    for chunk in parts[1:]:
        cells.append(chunk[:chunk.rindex("</td>")])
    return cells


def lt_row(cells):
    tds = "\n".join('    <td class="ltc" style="width:%d%%">%s</td>'
                    % (100 // len(cells), c) for c in cells)
    return '<table class="lt"><tbody><tr>\n%s\n  </tr></tbody></table>' % tds


# ---------------------------------------------------------------- frames
def load_wavu(path):
    frames = {}
    with open(path, encoding="utf-8") as source:
        for line in source:
            line = line.strip()
            if not line:
                continue
            k, v = line.split("|", 1)
            frames[k] = v.strip()
    lower = {k.lower(): v for k, v in frames.items()}
    return frames, lower


def first_step(t):
    seen = False
    for i, ch in enumerate(t):
        if ch in "1234":
            seen = True
        elif ch == "," and seen:
            return t[:i]
    return t


def candidates(cmd, cfg):
    # a "+" joining two CJK condition words (热能+凤凰中) is a compound prefix
    cmd = re.sub(r"(?<=[一-鿿])\+(?=[一-鿿])", "", cmd)
    # alternation parens like (或 u) just drop; other parentheticals such
    # as (命中时) act as string continuations -> comma
    t = re.sub(r"\(或[^)]*\)", " ", cmd)
    t = re.sub(r"\([^)]*\)", ",", t).split(" / ")[0].strip(" ,")
    pre = ""
    m = re.match(r"^([一-鿿·]+)\s*", t)
    if m:
        run = m.group(1).strip("·")
        t = t[m.end():]
        while run:
            run = run.lstrip("·")
            for w in sorted(cfg["prefix"], key=len, reverse=True):
                if run.startswith(w):
                    pre += cfg["prefix"][w]
                    run = run[len(w):]
                    break
            else:
                return []  # unmapped condition (parry, unique stance)
        if pre.endswith(("Throw", "throw")):
            return [pre]
    if not t:
        return [pre] if pre else []
    # a mid-command CJK condition word ends the notation proper
    t = re.split(r"[一-鿿·]", t)[0]
    t = t.replace(" ", "").strip(",")
    for a, b in (("d/f", "df"), ("d/b", "db"), ("u/f", "uf"), ("u/b", "ub"),
                 ("U/B", "UB"), ("D/F", "DF"), ("D/B", "DB"), ("U/F", "UF"),
                 ("N", "n")):
        t = t.replace(a, b)
    t = re.sub(r"^f,f,f\+", "f,f,F+", t)
    t = re.sub(r"^f,f\+", "f,F+", t)
    t = re.sub(r"^WS\+", "ws", t)
    t = re.sub(r"^SS\+", "SS.", t)
    t = re.sub(r"^FC\+", "FC.", t)
    cut = first_step(t)
    cands = [pre + cut, pre + t]
    cands += [c.replace("ws1+2", "ws+1+2").replace("ws3+4", "ws+3+4")
              for c in list(cands)]
    cands += [re.sub(r"\bws\+(\d\+\d)", r"ws\1", c) for c in list(cands)]
    cands += [c.replace("f,F+", "f+") for c in list(cands)]
    cands += [c.replace("hFC.uf", "FC.UF").replace("hFC.ub", "FC.UB")
              .replace("hFC.df", "FC.df").replace("hFC.db", "FC.db")
              for c in list(cands)]
    cands += [c.replace("FC.", "hFC.").replace("hFC.df", "FC.df")
              .replace("hFC.db", "FC.db") for c in list(cands)]
    cands += [re.sub(r"^([FBUD])(?=\+)", lambda m: m.group(1).lower(), c)
              for c in list(cands)]
    cands += [c.replace(",n,", ",") for c in list(cands)]
    if pre.startswith("H."):
        cands += [c[2:] for c in list(cands) if c.startswith("H.")]
    seen, out = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def lookup(cmd, cfg, frames, lower):
    found_empty = False
    for c in candidates(cmd, cfg):
        v = frames.get(c)
        if v is None:
            v = lower.get(c.lower())
        if v is not None:
            if not v:
                found_empty = True
                continue
            tok = [x for x in re.split(r"[ ,]+", v) if x]
            if tok:
                return tok[0]
            found_empty = True
    return "—" if found_empty else None


ORIG_RE = re.compile(
    r'<td class="cmd">(?:(?:<b>[^<]*</b>)?\s*<span class="cmd-gfx">.*'
    r'<span class="cmd-txt">([^<]*)</span>|([^<]*))</td>', re.S)


def add_frames(head, cfg, frames, lower, stats):
    def process_row(row):
        if "<th>指令</th>" in row:
            return row.replace("<th>指令</th>", "<th>指令</th><th>发生</th>", 1)
        if '<td class="cmd">' not in row:
            return row
        m = ORIG_RE.search(row)
        if not m:
            return row
        cmd = (m.group(1) or m.group(2) or "").strip()
        if ">防反<" in row:
            fr = "—"
        else:
            fr = lookup(cmd, cfg, frames, lower)
            if fr is None:
                stats["miss"].append(cmd)
                fr = "—"
            else:
                stats["hit"] += 1
        return row[:m.end()] + '<td class="fr">%s</td>' % fr + row[m.end():]

    parts = re.split(r"(<tr>.*?</tr>)", head, flags=re.S)
    return "".join(process_row(p) if p.startswith("<tr>") else p
                   for p in parts)


# ---------------------------------------------------------------- assets
def adapt_css(cfg):
    return """
/* ---- adaptation: graphical notation on this sheet ---- */
.tk-in{--tk-acc:%(acc)s}
td.cmd .tk-b i:not(.on){color:transparent}
body.nn-mode td.cmd .tk-b i.on{color:transparent}
.tk-txt{font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;font-size:.85em;opacity:.72;white-space:nowrap}
.tk-tbang{color:var(--mid,#ffb45e);font-weight:700;font-size:.8em;letter-spacing:.5px}
.tk-sep.tk-arw{opacity:.7;font-size:.95em}
td.fr{font-family:Consolas,'Courier New',monospace;font-size:9px;white-space:nowrap;color:#8a6f7d}
html.dark td.fr{color:#8fa3b8}
section:not(.tipsPage) table:not(.lt) td{vertical-align:middle}
.tipsPage .tpFull td{vertical-align:middle}
td.cmd .tk-in{flex-wrap:wrap;row-gap:.25em;vertical-align:middle}
table.cb td{padding:8px 8px}
table.cb td:first-child{border-right:1px solid rgba(139,152,165,.22);padding-right:10px}
table.cb .tk-sep.tk-arw{margin:0 .3em}
body.txt-mode .cmd-gfx{display:none}
body.txt-mode .gfx-only{display:none}
body:not(.txt-mode) .cmd-txt{display:none}
.ntgl{display:inline-flex;align-items:center;gap:8px;font-size:10px;opacity:.95}
.ntgl .seg{display:inline-flex;border:1px solid rgba(255,255,255,.45);border-radius:999px;overflow:hidden}
.ntgl button{font:inherit;border:0;background:transparent;color:#fff;padding:2px 10px;cursor:pointer;letter-spacing:1px}
.ntgl button.on{background:rgba(255,255,255,.92);color:%(ink)s;font-weight:600}
""" % {"acc": cfg["acc"], "ink": cfg["acc_ink"]}


TOGGLES = (
    '<div class="ntgl" id="thgl">主题<span class="seg">'
    '<button type="button" id="thd" class="on">夜间</button>'
    '<button type="button" id="thl">浅色</button></span></div>\n  '
    '<div class="ntgl" id="ntgl">记法<span class="seg">'
    '<button type="button" id="ng" class="on">按键图</button>'
    '<button type="button" id="nn">无数字</button>'
    '<button type="button" id="nt">文字</button></span></div>')

GFX_LEGEND = """
<div class="legend gfx-only">
  <b>图形记法</b>
  <span class="tk-in tk-sm"><span class="tk-b"><i>1</i><i>2</i><i>3</i><i>4</i></span></span> 四键方阵（左上1 右上2 左下3 右下4，亮=按下）
  <span class="tk-in tk-sm"><span class="tk-dir f"></span></span>=轻点方向
  <span class="tk-in tk-sm"><span class="tk-dir f hold"></span></span>=按住
  <span class="tk-in tk-sm"><span class="tk-n">N</span></span>=回中
  <span class="tk-in tk-sm"><span class="tk-state">架势中</span></span>=状态前缀　|
  <b>分隔</b>：› 接续　+ 方向＋键　~ 紧接　＊蓄力　→ 下一招　<span class="tk-tbang">T!</span> 回旋(连招)
</div>"""

BOOT_JS = ("<script>/* tk-theme boot */\n"
           "try{if((localStorage.getItem('tk-theme')||'dark')==='dark')"
           "document.documentElement.classList.add('dark')}"
           "catch(e){document.documentElement.classList.add('dark')}</script>\n")

TOGGLE_JS = """
<script>
(function(){
  var KEY='tk-notation', BTN={gfx:'ng', nn:'nn', txt:'nt'};
  function set(m){
    if(!BTN[m]) m='gfx';
    document.body.classList.toggle('txt-mode', m==='txt');
    document.body.classList.toggle('nn-mode', m==='nn');
    for(var k in BTN){
      document.getElementById(BTN[k]).classList.toggle('on', k===m);
    }
    try{localStorage.setItem(KEY,m)}catch(e){}
  }
  var m='gfx';
  try{m=localStorage.getItem(KEY)||'gfx'}catch(e){}
  set(m);
  for(var k in BTN){(function(mode){
    document.getElementById(BTN[mode]).onclick=function(){set(mode)};
  })(k);}
})();
(function(){
  var KEY='tk-theme', BTN={dark:'thd', light:'thl'};
  function set(m){
    if(!BTN[m]) m='dark';
    document.documentElement.classList.toggle('dark', m==='dark');
    for(var k in BTN){
      document.getElementById(BTN[k]).classList.toggle('on', k===m);
    }
    try{localStorage.setItem(KEY,m)}catch(e){}
  }
  var m='dark';
  try{m=localStorage.getItem(KEY)||'dark'}catch(e){}
  set(m);
  for(var k in BTN){(function(mode){
    document.getElementById(BTN[mode]).onclick=function(){set(mode)};
  })(k);}
})();
</script>"""


def scope_dark(html):
    start = html.index("<style>\n:root { --hi:#6fb3ff")
    end = html.index("</style>", start)
    block = html[start + len("<style>\n"):end]
    out = []
    for sel, decl in re.findall(r"([^{}]+)\{([^}]*)\}", block):
        parts = []
        for s in (x.strip() for x in sel.split(",")):
            if s in (":root", "html"):
                parts.append("html.dark")
            elif s == "body":
                parts.append("html.dark body")
            else:
                parts.append("html.dark " + s)
        out.append("%s { %s }" % (", ".join(parts), decl.strip()))
    dark_css = ("/* ---- dark theme (html.dark) ---- */\n" + "\n".join(out)
                + "\n/* ---- light theme extras ---- */\n"
                "html:not(.dark) .tk-in{--tk-ink:#1d1d1f;--tk-bg:#ffffff}\n"
                "html:not(.dark) .tk-b i.on{box-shadow:none}\n"
                "html:not(.dark) .tk-dir::before{filter:none}\n"
                "html:not(.dark) section.tipsPage{border-top:2px solid "
                "var(--line);padding-top:14px;margin-top:16px}\n")
    return html[:start + len("<style>\n")] + dark_css + html[end:]


# ---------------------------------------------------------------- main
def run(key):
    cfg = CONFIG[key]
    path = os.path.join(SITE, cfg["file"])
    with open(path, encoding="utf-8") as f:
        html = f.read()
    if "tk-notation" in html:
        print(key, ": already processed, aborting")
        return
    component_css = open(CSS_PATH, encoding="utf-8").read()

    # --- 1. inject CSS + toggles + legends -----------------------------
    html = html.replace(
        "</head>",
        '<style id="tk-notation">\n%s\n%s</style>\n%s</head>'
        % (component_css, adapt_css(cfg), BOOT_JS))
    html = html.replace('<div class="sub">', TOGGLES + '\n  <div class="sub">', 1)
    first_leg = html.index('<div class="legend">')
    leg_end = html.index("</div>", first_leg)
    html = (html[:leg_end]
            + "　|　<b>发生</b>=首击冲击帧(i=impact,越小越快,依 Wavu)"
            + html[leg_end:] )
    leg_close = html.index("</div>", html.index('<div class="legend">')) + 6
    html = html[:leg_close] + GFX_LEGEND + html[leg_close:]
    html = html.replace("</body>", TOGGLE_JS + "\n</body>")

    tips_at = html.index('<section class="tipsPage">')
    head, tail = html[:tips_at], html[tips_at:]

    # --- 2. movelist conversion (10-hit section uncapped) --------------
    stats = {"done": 0, "kept": 0}
    ten_h2 = head.find("十连技")
    if ten_h2 != -1:
        sec_s = head.rindex("<section", 0, ten_h2)
        sec_e = head.index("</section>", ten_h2)
        head = (convert_cells(head[:sec_s], cfg, 6, stats)
                + convert_cells(head[sec_s:sec_e], cfg, None, stats)
                + convert_cells(head[sec_e:], cfg, 6, stats))
    else:
        head = convert_cells(head, cfg, 6, stats)

    # --- 3. movelist stance lt with 3+ columns -> rows of 2 ------------
    for marker_pos in [m.start() for m in
                       re.finditer(r'<table class="lt">', head)][::-1]:
        s, e = find_balanced_table(head, marker_pos + len('<table class="lt">'))
        cells = split_ltc(head[s:e])
        if len(cells) < 3:
            continue
        rows = [lt_row(cells[i:i + 2]) for i in range(0, len(cells), 2)]
        head = head[:s] + "\n".join(rows) + head[e:]

    # --- 4. tips: restack the lt containing 连招; convert cells --------
    combo_h2 = tail.index("连招 (Wavu")
    s, e = find_balanced_table(tail, combo_h2)
    cells = split_ltc(tail[s:e])
    stacked = "\n  ".join('<div class="tpFull">%s</div>' % c for c in cells)
    tail = tail[:s] + stacked + tail[e:]

    # combos table: class + wider starter column
    m = re.search(r"<table>(\s*<tr><th[^>]*>起手</th><th[^>]*>[^<]*路线)", tail)
    if m:
        tail = (tail[:m.start()] + '<table class="cb">'
                + tail[m.start() + len("<table>"):])
        tail = tail.replace("<th>起手</th><th>路线",
                            '<th style="width:225px">起手</th><th>路线', 1)

    tstats = {"done": 0, "kept": 0}
    tip_h2 = tail.find("实用贴士")
    if tip_h2 != -1:
        tip_end = tail.index("</table>", tip_h2) + len("</table>")
        tail = (convert_cells(tail[:tip_h2], cfg, None, tstats)
                + tail[tip_h2:tip_end]
                + convert_cells(tail[tip_end:], cfg, None, tstats))
    else:
        tail = convert_cells(tail, cfg, None, tstats)

    # --- 5. startup frames on movelist tables --------------------------
    frames, lower = load_wavu(SCRATCH + "\\" + cfg["wavu"])
    fstats = {"hit": 0, "miss": []}
    head = add_frames(head, cfg, frames, lower, fstats)

    html = head + tail

    # --- 6. theme consolidation + title --------------------------------
    html = scope_dark(html)
    html = html.replace(" · 夜间版</title>", "</title>")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("%s: movelist %d gfx/%d text, tips %d gfx/%d text, "
          "frames %d hit/%d miss"
          % (key, stats["done"], stats["kept"], tstats["done"],
             tstats["kept"], fstats["hit"], len(fstats["miss"])))
    for miss in fstats["miss"]:
        print("  MISS:", miss)


if __name__ == "__main__":
    run(sys.argv[1])
