#!/usr/bin/env python3
"""RusStudy social series: episodes/*.json -> build/<slug>-<lang>/ (one HyperFrames project per video).

An episode is a list of typed scenes (hook, question, day, price, receipt, steps, checklist, points,
chat, recap, stats, chips, cta) written in French and in Tunisian Arabic (derja). This script lays
them out on the shared engine (engine/style.css + engine/lib.js), sizes every headline to the safe
column with widths measured in headless Chromium with the real fonts (scripts/measure.cjs), and
writes one project per video: index.html, fonts, GSAP, music bed (build/_beds, scripts/beds.py),
HyperFrames config.

usage: python3 scripts/build.py [slug-prefix ...]      (default: every episode, both languages)
"""
import glob
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine"
ASSETS = ROOT / "assets"
EPISODES = ROOT / "episodes"
BUILD = ROOT / "build"
MDIR = BUILD / "_measure"
CACHE = MDIR / "widths.json"
LANGS = ("fr", "ar")
NBSP = " "
W = 876  # safe column width (x 72..948)
TEL = "+7" + NBSP + "996" + NBSP + "433" + NBSP + "4489"
WEB = "russieetudes.com"
HOOK_TAIL = 0.48  # the hook page lifts off over the start of the next scene

UI = {
    "fr": {
        "answer": "Réponse",
        "tag": "Études en Russie",
        "wa": {"student": "Écris-nous sur WhatsApp", "parent": "Vos questions sur WhatsApp"},
        "free": "1ère consultation gratuite",
        "bio": "Lien en bio",
        "ck_head": "À préparer",
        "book": "Réserver l'appel",
        "msg": "Message",
        "stamp": ["SANS FRAIS", "CACHÉS"],
        "day": "JOUR",
    },
    "ar": {
        "answer": "الجواب",
        "tag": "الدراسة في روسيا",
        "wa": {"student": "ابعثلنا على WhatsApp", "parent": "أسئلتك على WhatsApp"},
        "free": "أوّل استشارة بلاش",
        "bio": "الرابط في البيو",
        "ck_head": "حضّر",
        "book": "احجز المكالمة",
        "msg": "ميساج",
        "stamp": ["بلا مصاريف", "مخفية"],
        "day": "نهار",
    },
}
THEME_FG = {"night": "#ffffff", "cream": "#0a0a0a", "ink": "#ffffff"}
THEME_SEED = {"night": 11, "cream": 23, "ink": 37}
TICKS = (
    '<svg width="30" height="18" viewBox="0 0 30 18"><path d="M2 9.5l4.5 4.5L16 3.5" fill="none" stroke="#8a8a8a" '
    'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M11 13l1 1L22 3.5" fill="none" '
    'stroke="#8a8a8a" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)
ICON_SIZE = {  # rows, cols of the pixel maps in engine/lib.js
    "plane": (12, 22), "cap": (11, 18), "doc": (11, 9), "pin": (10, 9), "shield": (12, 13), "star": (7, 7),
    "coin": (12, 12), "key": (7, 15), "card": (11, 16), "city": (14, 16), "mic": (13, 10), "chat": (11, 14),
}


def icon_px(name, h, w):
    r, c = ICON_SIZE[name]
    return max(2, min(h // r, w // c))


# ---------------------------------------------------------------- text helpers
NUM = re.compile(r"[+]?\d(?:[\d .,/:–-]*\d)?[+]?")


def norm(t):
    t = re.sub(r"(\d) (\d{3})(?!\d)", "\\1" + NBSP + "\\2", t)
    t = re.sub(r" ([?!:;»])", NBSP + r"\1", t)
    t = re.sub(r"(«) ", r"\1" + NBSP, t)
    return t


def esc(t):
    return html.escape(t, quote=False)


def rich(t, lang):
    """Escaped text; in derja, digit groups (12 000, 2026–2027, +40) are isolated left-to-right."""
    t = norm(t)
    if lang != "ar":
        return esc(t)
    out, pos = [], 0
    for m in NUM.finditer(t):
        out.append(esc(t[pos : m.start()]))
        out.append(f'<span class="ltr">{esc(m.group())}</span>')
        pos = m.end()
    out.append(esc(t[pos:]))
    return "".join(out)


def words(line, lang):
    toks = [w for w in norm(line).split(" ") if w]
    return " ".join(f'<span class="mk"><span class="w">{rich(w, lang)}</span></span>' for w in toks)


def lines_html(lines):
    return "".join(f'<span class="ln">{l}</span>' for l in lines)


def balance(text):
    """Split a sentence in two lines of similar length (by characters)."""
    ws = norm(text).split(" ")
    best, cut = None, 1
    for k in range(1, len(ws)):
        a, b = " ".join(ws[:k]), " ".join(ws[k:])
        d = abs(len(a) - len(b))
        if best is None or d < best:
            best, cut = d, k
    return [" ".join(ws[:cut]), " ".join(ws[cut:])]


WM = '<span class="wm">Rus<span class="s">Study</span>.</span>'


# ---------------------------------------------------------------- measurement (Chromium, real fonts)
class Measurer:
    def __init__(self):
        self.cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
        self.need = {}

    @staticmethod
    def key(lang, cls, h):
        return hashlib.sha1(f"{lang}|{cls}|{h}".encode()).hexdigest()[:16]

    def width(self, lang, cls, h):
        """Width in px of html `h` with class `cls` at font-size 100px."""
        k = self.key(lang, cls, h)
        if k in self.cache:
            return self.cache[k]
        self.need[k] = (lang, cls, h)
        return 100.0

    def run(self):
        if not self.need:
            return False
        (MDIR / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
        for f in (ASSETS / "fonts").glob("*.woff2"):
            shutil.copy(f, MDIR / "assets" / "fonts" / f.name)
        css = (ENGINE / "style.css").read_text()
        items = {"fr": [], "ar": []}
        for k, (lang, cls, h) in self.need.items():
            items[lang].append(f'<div><span data-m="{k}" class="{cls}" style="font-size: 100px; white-space: nowrap; display: inline-block">{h}</span></div>')
        page = f"""<!doctype html><html><head><meta charset="UTF-8"><style>{css}
      html, body {{ width: auto; height: auto; overflow: visible; background: #fff; }}
      .mroot {{ position: relative; width: 6000px; color: #000; }}</style></head><body>
<div class="mroot fr" dir="ltr" style="font-family: 'Space Grotesk', sans-serif">{''.join(items['fr'])}</div>
<div class="mroot ar" dir="rtl" style="font-family: 'Space Grotesk', 'Cairo', sans-serif">{''.join(items['ar'])}</div>
</body></html>"""
        (MDIR / "index.html").write_text(page)
        mods = sorted(glob.glob(os.path.expanduser("~/.npm/_npx/*/node_modules/puppeteer-core")))
        if not mods:
            sys.exit("puppeteer-core not found: run `npx --yes hyperframes@0.8.133 --version` once to populate the npx cache")
        env = dict(os.environ, NODE_PATH=str(Path(mods[-1]).parent))
        out = MDIR / "out.json"
        subprocess.run(["node", str(ROOT / "scripts" / "measure.cjs"), str(MDIR), str(out)], check=True, env=env)
        res = json.loads(out.read_text())
        bad = [f for f in res["fonts"] if not f.endswith("loaded") and not f.endswith("unloaded")]
        if bad:
            print("font status:", bad)
        self.cache.update(res["w"])
        CACHE.write_text(json.dumps(self.cache, indent=0, sort_keys=True))
        self.need = {}
        return True


def fit(M, lang, cls, hs, maxw, maxsize):
    w = max(M.width(lang, cls, h) for h in hs)
    return round(min(maxsize, maxw / w * 100 * 0.985), 1)


# ---------------------------------------------------------------- scenes
def sec_open(sid, kind, t0, dur, ti, z, extra_style=""):
    return (
        f'      <section id="{sid}" class="clip sc {kind}" data-start="{t0:.2f}" data-duration="{dur:.2f}" '
        f'data-track-index="{ti}" style="z-index: {z}{extra_style}">\n'
    )


def hook(M, ep, sc, lang, ctx):
    d = sc[lang]
    fr = lang == "fr"
    bg = sc["bg"].lower()
    ink = sc.get("ink", False)
    fg = "#0a0a0a" if ink else "#ffffff"
    ul = "#0a0a0a" if ink else ("#ffffff" if bg == "#f97316" else "#fbbb21")
    ls = [words(l, lang) for l in d["title"]]
    fs = fit(M, lang, "t-hook", ls, W, 132 if fr else 124)
    lh = 1.02 if fr else 1.3
    wl = round(M.width(lang, "t-hook", ls[-1]) * fs / 100)
    ul_top = round(640 + len(ls) * lh * fs + (6 if fr else -0.08 * fs))
    ul_left = 72 if fr else 948 - wl
    name = sc["icon"]
    px = icon_px(name, 156, 300)
    deco_pal = json.dumps({c: fg for c in "KWGBPONRCY"})
    h = sec_open(ctx["sid"], "hook", ctx["t0"], sc["dur"] + HOOK_TAIL, ctx["ti"], 60, f"; --hk: {bg}; --hkfg: {fg}; --hkul: {ul}")
    h += f"""        <div class="fill hk-bg"></div>
        <div class="fill hk-shade"></div>
        <div class="hk-deco" data-layout-ignore><span class="pix" data-icon="{name}" data-px="{icon_px(name, 560, 900)}" data-pal='{deco_pal}'></span></div>
        <div class="box hk-k"><span class="pill kick t-label"><span>{rich(d["kicker"], lang)}</span></span></div>
        <div class="box hk-ic"><span class="pix" data-icon="{name}" data-px="{px}"></span></div>
        <div class="box hk-t t-hook" style="font-size: {fs}px">{lines_html(ls)}</div>
        <div class="hk-ul" style="left: {ul_left}px; top: {ul_top}px; width: {wl}px"></div>
      </section>
"""
    return h, {}


def question(M, ep, sc, lang, ctx):
    d = sc[lang]
    fr = lang == "fr"
    ls = [words(l, lang) for l in d["text"]]
    fs = fit(M, lang, "t-q", ls, W, 108 if fr else 102)
    lh = 1.06 if fr else 1.32
    top = round(470 + len(ls) * lh * fs + 90)
    dots = "".join(f'<i class="{"on" if k < sc["n"] else ""}"></i>' for k in range(sc["of"]))
    h = sec_open(ctx["sid"], "q", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="box q-lab"><span class="pill t-label"><span>{rich(d["label"], lang)} <b class="ltr">{sc["n"]}/{sc["of"]}</b></span></span><span class="q-dots">{dots}</span></div>
        <div class="box q-t t-q" style="font-size: {fs}px">{lines_html(ls)}</div>
        <div class="box q-ans" style="top: {top}px">
          <div class="q-mic"><div class="q-ring"></div><span class="pix" data-icon="mic" data-px="6"></span></div>
          <div class="q-al t-label">{rich(UI[lang]["answer"], lang)}</div>
          <div class="q-wave">{"<i></i>" * 26}</div>
        </div>
      </section>
"""
    return h, {}


def day(M, ep, sc, lang, ctx):
    d = sc[lang]
    fr = lang == "fr"
    ls = [words(d["text"], lang)]
    fs = fit(M, lang, "t-hook", ls, W, 140 if fr else 132)
    name = sc["icon"]
    h = sec_open(ctx["sid"], "dy", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="box dy-l t-label">{rich(d["label"], lang)}</div>
        <div class="box dy-n"><span class="num t-big"><span class="mk"><span class="w">{sc["n"]}</span></span></span><span class="pix" data-icon="{name}" data-px="{icon_px(name, 230, 430)}"></span></div>
        <div class="box dy-t t-hook" style="font-size: {fs}px">{lines_html(ls)}</div>
      </section>
"""
    return h, {}


def week(ep, lang, days, ti):
    t0 = days[0]["t0"]
    end = days[-1]["t0"] + days[-1]["dur"]
    cells = "".join(
        f'<div class="wk-d"><div class="wk-hl"></div><div class="wk-tx"><span class="a">{esc(UI[lang]["day"])}</span>'
        f'<span class="b">{k}</span></div><div class="wk-ok" data-check="#ffffff" data-s="26" data-w="5"></div></div>'
        for k in range(1, 8)
    )
    h = sec_open("wk", "wk-sc", t0, end - t0, ti, 45)
    h += f"""        <div class="box wk">{cells}</div>
      </section>
"""
    return h, {"t0": round(t0, 3), "dur": round(end - t0, 3), "days": [{"n": d["n"], "t0": round(d["t0"], 3)} for d in days]}


def price(M, ep, sc, lang, ctx):
    d = sc[lang]
    fr = lang == "fr"
    value = sc.get("value", "12000")
    cols = ""
    for i, _ in enumerate(value):
        if i == len(value) - 3:
            cols += '<div class="odo-sp"></div>'
        cols += '<div class="odo"><div class="odo-col"></div></div>'
    cur = rich(d["cur"], lang)
    cur_w = M.width(lang, "t-big", cur) * (112 if fr else 104) / 100
    ns = round(min(216, (W - 18 - cur_w) / (0.6 * len(value) + 0.22) * 0.98), 1)
    h = sec_open(ctx["sid"], "pr", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="fill pr-glow"></div>
        <div class="pr-deco" data-layout-ignore>{cur}</div>
        <div class="box pr-k"><span class="pill kick t-label"><span>{rich(d["kicker"], lang)}</span></span></div>
        <div class="box pr-des t-title">{rich(d["des"], lang)}</div>
        <div class="box pr-row"><div class="pr-num t-big" style="font-size: {ns}px">{cols}</div><div class="pr-cur t-big">{cur}</div></div>
        <div class="box pr-pill"><span class="pill t-title"><span>{rich(d["pill"], lang)}</span></span></div>
      </section>
"""
    return h, {"digits": [int(c) for c in value], "num_size": ns}


def zigzag(cls):
    pts = ["0,14"] + [f"{x},{0 if (x // 12) % 2 else 14}" for x in range(0, 877, 12)] + ["876,14"]
    return f'<svg class="rc-zz {cls}" viewBox="0 0 876 14" preserveAspectRatio="none"><polygon points="{" ".join(pts)}" fill="#ffffff"/></svg>'


def receipt(M, ep, sc, lang, ctx):
    d = sc[lang]
    inc = "".join(
        f'<div class="rc-l inc"><span class="lab">{rich(l, lang)}</span><span class="dt"></span><span class="v">'
        f'<span>{rich(d["inc"], lang)}</span><span class="ok" data-check="#0a0a0a" data-s="23" data-w="4.5"></span></span></div>'
        for l in d["lines"]
    )
    opts = "".join(
        f'<div class="rc-l rc-o"><span class="lab">{rich(o, lang)}</span><span class="dt"></span><span class="v">{rich(d["opt_v"], lang)}</span></div>'
        for o in d["opts"]
    )
    stamp = "".join(f"<span>{esc(s)}</span>" for s in UI[lang]["stamp"])
    h = sec_open(ctx["sid"], "rc", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="box rc-paper">
          {zigzag("t")}
          <div class="rc-h">{WM}<span class="t-label">{rich(d["head"], lang)}</span></div>
          {inc}
          <div class="rc-div"></div>
          <div class="rc-tot"><span class="a">{rich(d["total"], lang)}</span><span class="b">{rich(d["total_v"], lang)}</span></div>
          <div class="rc-oh">{rich(d["opt_head"], lang)}</div>
          {opts}
          {zigzag("b")}
        </div>
        <div class="stamp" style="top: 1262px; inset-inline-end: 104px">{stamp}</div>
      </section>
"""
    return h, {}


def list_gap(sc, n):
    return round((sc["dur"] - 0.3 - 3.6) / max(1, n - 1), 3)


def steps(M, ep, sc, lang, ctx):
    d = sc[lang]
    fr = lang == "fr"
    items = d["items"]
    avail = W - 94 - 30
    tf = min(fit(M, lang, "t-title", [rich(t, lang)], avail, 56 if fr else 52) for t, _ in items)
    df = min(fit(M, lang, "t-body", [rich(x, lang)], avail, 36) for _, x in items)
    ih = 212
    rows = "".join(
        f'<div class="ls-i" style="height: {ih}px"><div class="ls-n"><div class="f"></div><span>{k + 1}</span></div>'
        f'<div class="ls-tx"><div class="ls-ti t-title" style="font-size: {tf}px">{rich(t, lang)}</div>'
        f'<div class="ls-de t-body" style="font-size: {df}px">{rich(x, lang)}</div></div></div>'
        for k, (t, x) in enumerate(items)
    )
    h = sec_open(ctx["sid"], "steps", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="box ls">
          <div class="ls-line" style="height: {(len(items) - 1) * ih}px"><div class="ls-fill"></div></div>
          {rows}
        </div>
      </section>
"""
    return h, {"gap": list_gap(sc, len(items))}


def points(M, ep, sc, lang, ctx):
    d = sc[lang]
    fr = lang == "fr"
    items = d["items"]
    avail = W - 112 - 30
    maxs = 52 if fr else 50
    blocks = []
    for name, text in items:
        one = [words(text, lang)]
        if fit(M, lang, "t-title", one, avail, maxs) >= 46:
            blocks.append((name, one))
        else:
            blocks.append((name, [words(l, lang) for l in balance(text)]))
    fs = min(fit(M, lang, "t-title", ls, avail, maxs) for _, ls in blocks)
    ih = 212
    rows = "".join(
        f'<div class="ls-i" style="height: {ih}px"><div class="ls-ic"><span class="pix" data-icon="{name}" data-px="{icon_px(name, 76, 92)}"></span></div>'
        f'<div class="ls-tx"><div class="ls-ti t-title" style="font-size: {fs}px">{lines_html(ls)}</div></div></div>'
        for name, ls in blocks
    )
    h = sec_open(ctx["sid"], "pt", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="box ls">
          {rows}
        </div>
      </section>
"""
    return h, {"gap": list_gap(sc, len(items))}


def checklist(M, ep, sc, lang, ctx):
    d = sc[lang]
    fr = lang == "fr"
    fs = min(fit(M, lang, "t-title", [rich(t, lang)], W - 96 - 76 - 34, 62 if fr else 58) for t in d["items"])
    rows = "".join(
        f'<div class="ck-i"><span class="ck-b"><span class="f"></span><span data-check="#ffffff" data-s="54" data-w="4.6"></span></span>'
        f'<span class="ck-t t-title" style="font-size: {fs}px">{rich(t, lang)}</span></div>'
        for t in d["items"]
    )
    note = lines_html([words(l, lang) for l in balance(d["note"])])
    nfs = fit(M, lang, "t-title", [words(l, lang) for l in balance(d["note"])], W - 68 - 78 - 26, 42)
    h = sec_open(ctx["sid"], "ck", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="box ck-card">
          <div class="ck-h"><span class="t-label">{rich(UI[lang]["ck_head"], lang)}</span><span class="pix" data-icon="doc" data-px="6"></span></div>
          {rows}
        </div>
        <div class="box ck-note"><span class="pix" data-icon="shield" data-px="6"></span><span class="t-title" style="font-size: {nfs}px">{note}</span></div>
      </section>
"""
    return h, {}


def chat(M, ep, sc, lang, ctx):
    d = sc[lang]
    h = sec_open(ctx["sid"], "chat", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="ph"><div class="ph-scr">
          <div class="ph-hd"><div class="ph-av"><span class="ltr">R.</span></div><div><div class="ph-nm">{WM}</div><div class="ph-st"><i></i>{rich(d["status"], lang)}</div></div></div>
          <div class="ph-msgs">
            <div class="bub out">{rich(d["out"], lang)}<span class="meta">10:02 <span class="tk">{TICKS}</span></span></div>
            <div class="slot"><div class="typ"><i></i><i></i><i></i></div><div class="bub in in1">{rich(d["in1"], lang)}<span class="meta">10:02</span></div></div>
            <div class="wcard"><div class="top"><div class="ic" data-chat="#a855f7" data-s="46" data-dots="#ffffff"></div><div><div class="tt t-title">{rich(d["card_t"], lang)}</div><div class="ss">{rich(d["card_s"], lang)}</div></div></div><div class="bt">{rich(UI[lang]["book"], lang)}</div></div>
            <div class="bub in in2">{rich(d["in2"], lang)}<span class="meta">10:03</span></div>
          </div>
          <div class="ph-in"><div class="f">{rich(UI[lang]["msg"], lang)}</div><div class="s" data-send="#ffffff" data-s="40"></div></div>
        </div></div>
      </section>
"""
    return h, {}


def recap(M, ep, sc, lang, ctx):
    d = sc[lang]
    fg = THEME_FG[ep["theme"]]
    fs = min(fit(M, lang, "t-title", [rich(t, lang)], W - 26 - 98 - 28 - 40, 48) for t in d["items"])
    parts = []
    for k, t in enumerate(d["items"]):
        if k:
            parts.append(f'<div class="rp-ar"><span data-down="{fg}" data-s="56"></span></div>')
        parts.append(f'<div class="rp-i"><span class="rp-n">{k + 1}</span><span class="t-title" style="font-size: {fs}px">{rich(t, lang)}</span></div>')
    h = sec_open(ctx["sid"], "rp-sc", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="box rp">{"".join(parts)}</div>
      </section>
"""
    return h, {}


def stats(M, ep, sc, lang, ctx):
    d = sc[lang]
    vals = []
    for v, label in d["items"]:
        m = re.match(r"^(\+?)(\d[\d ]*)(\+?)\s*(.*)$", norm(v))
        pre, num, post, suf = m.groups()
        target = int(num.replace(NBSP, ""))
        inner = f'<span class="ltr">{pre}<span class="num" data-v="{target}" data-sep="{NBSP if target >= 1000 else ""}">{esc(num)}</span>{post}</span>'
        if suf:
            inner += f'<span class="suf">{rich(suf, lang)}</span>'
        vals.append((inner, label))
    vs = min(fit(M, lang, "t-big", [i], W, 196) for i, _ in vals)
    lsz = min(fit(M, lang, "t-body", [rich(l, lang)], W, 48) for _, l in vals)
    rows = "".join(
        f'<div class="st"><div class="st-v t-big" style="font-size: {vs}px">{i}</div>'
        f'<div class="st-l t-body" style="font-size: {lsz}px">{rich(l, lang)}</div><div class="st-bar"></div></div>'
        for i, l in vals
    )
    h = sec_open(ctx["sid"], "sts-sc", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="box sts">{rows}</div>
      </section>
"""
    return h, {"gap": round((sc["dur"] - 0.15 - 2.6) / max(1, len(vals) - 1), 3)}


def chips(M, ep, sc, lang, ctx):
    d = sc[lang]
    fs = min(fit(M, lang, "t-title", [rich(t, lang)], W - 24 - 84 - 26 - 44, 52) for t in d["items"])
    pills = "".join(
        f'<span class="pill t-title" style="font-size: {fs}px"><span class="ok" data-check="#ffffff" data-s="48" data-w="4.5"></span><span>{rich(t, lang)}</span></span>'
        for t in d["items"]
    )
    h = sec_open(ctx["sid"], "ch-sc", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="box chs">{pills}</div>
      </section>
"""
    return h, {}


def cta(M, ep, sc, lang, ctx):
    u = UI[lang]
    h = sec_open(ctx["sid"], "cta", ctx["t0"], sc["dur"], ctx["ti"], ctx["z"])
    h += f"""        <div class="fill cta-bg"></div>
        <div class="box cta-wm">{WM}</div>
        <div class="box cta-tag t-label">{rich(u["tag"], lang)}</div>
        <div class="box cta-wa"><span class="ic" data-chat="#ffffff" data-s="66" data-dots="#16a34a"></span><span><div class="a t-title">{rich(u["wa"][ep.get("cta", "student")], lang)}</div><div class="b t-big"><span class="ltr">{TEL}</span></div></span></div>
        <div class="box cta-web t-title">{WEB}</div>
        <div class="box cta-chip"><span class="pill t-title"><span>{rich(u["free"], lang)}</span></span></div>
        <div class="box cta-bio"><span class="pill t-title"><span>{rich(u["bio"], lang)} <span class="arr">↑</span></span></span></div>
      </section>
"""
    return h, {}


SCENES = {
    "hook": hook, "question": question, "day": day, "price": price, "receipt": receipt, "steps": steps,
    "points": points, "checklist": checklist, "chat": chat, "recap": recap, "stats": stats, "chips": chips, "cta": cta,
}


# ---------------------------------------------------------------- episode
def timings(ep):
    """Scene start times (s): back to back; the hook page lifts off over the next scene."""
    t, out = 0.0, []
    for sc in ep["scenes"]:
        out.append(round(t, 3))
        t += sc["dur"]
    return out, round(t, 3)


def load_episodes(prefixes=()):
    eps = []
    for p in sorted(EPISODES.glob("*.json")):
        ep = json.loads(p.read_text())
        if prefixes and not any(ep["slug"].startswith(x) for x in prefixes):
            continue
        eps.append(ep)
    return eps


def render_episode(M, ep, lang):
    starts, D = timings(ep)
    body, scenes, days = [], [], []
    for i, (sc, t0) in enumerate(zip(ep["scenes"], starts)):
        ctx = {"sid": f"s{i}", "t0": t0, "ti": 10 + i, "z": 20 + i}
        h, extra = SCENES[sc["type"]](M, ep, sc, lang, ctx)
        body.append(h)
        scenes.append(dict({"id": ctx["sid"], "type": sc["type"], "t0": t0, "dur": sc["dur"], "i": i}, **extra))
        if sc["type"] == "day":
            days.append({"n": sc["n"], "t0": t0, "dur": sc["dur"]})
    wk = None
    if days:
        h, wk = week(ep, lang, days, 9)
        body.append(h)
    fr = lang == "fr"
    epj = {"D": D, "lang": lang, "rtl": not fr, "theme": ep["theme"], "seed": THEME_SEED[ep["theme"]] + len(ep["slug"]), "scenes": scenes, "week": wk}
    css = (ENGINE / "style.css").read_text()
    lib = (ENGINE / "lib.js").read_text()
    title = ep["title"][lang]
    doc = f"""<!doctype html>
<html lang="{lang}" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>RusStudy — {esc(title)}</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <script src="assets/vendor/CustomEase.min.js"></script>
    <style>
{css}    </style>
  </head>
  <body>
    <div id="root" class="{lang} th-{ep["theme"]}" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920" data-fps="30">
      <audio id="bed" src="assets/bed.wav" data-start="0" data-duration="{D}" data-track-index="0" data-volume="1"></audio>
      <section id="amb" class="clip" data-start="0" data-duration="{D}" data-track-index="1" style="z-index: 1"><canvas id="amb-c" width="1080" height="1920"></canvas></section>
{"".join(body)}      <section id="chrome" class="clip" data-start="0" data-duration="{D}" data-track-index="2" style="z-index: 100">
        <div id="topbar" class="box"><span id="brand" class="pill">{WM}</span><span id="series" class="pill t-label"><span>{rich(ep["top"][lang], lang)}</span></span></div>
        <div id="prog" class="box"><div id="progf"></div></div>
      </section>
    </div>
    <script>
      window.__EP = {json.dumps(epj, ensure_ascii=False)};
    </script>
    <script>
{lib}    </script>
  </body>
</html>
"""
    return doc, D


def write_project(ep, lang, doc):
    out = BUILD / f"{ep['slug']}-{lang}"
    (out / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    (out / "assets" / "vendor").mkdir(parents=True, exist_ok=True)
    for f in (ASSETS / "fonts").glob("*.woff2"):
        shutil.copy(f, out / "assets" / "fonts" / f.name)
    for f in ("gsap.min.js", "CustomEase.min.js"):
        shutil.copy(ASSETS / "vendor" / f, out / "assets" / "vendor" / f)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(ENGINE / f, out / f)
    (out / "meta.json").write_text(json.dumps({"id": f"russtudy-{ep['slug']}-{lang}", "name": f"RusStudy — {ep['title'][lang]}"}, ensure_ascii=False, indent=2))
    bed = BUILD / "_beds" / f"{ep['slug']}.wav"
    if bed.exists():
        shutil.copy(bed, out / "assets" / "bed.wav")
    else:
        print(f"  ! no music bed yet for {ep['slug']} (run scripts/beds.py)")
    (out / "index.html").write_text(doc)
    return out


def main():
    eps = load_episodes(sys.argv[1:])
    M = Measurer()
    for _ in range(3):  # pass 1 collects the strings to measure, the next passes use the widths
        docs = [(ep, lang, *render_episode(M, ep, lang)) for ep in eps for lang in LANGS]
        if not M.run():
            break
    for ep, lang, doc, D in docs:
        out = write_project(ep, lang, doc)
        print(f"{out.relative_to(ROOT)}  {D:.2f} s")


if __name__ == "__main__":
    main()
