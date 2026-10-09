#!/usr/bin/env python3
"""Page images for the RusStudy social accounts (same brand system as the videos):

  kit/images/photo_profil.png           1080x1080  profile picture (reads as a circle)
  kit/images/a_la_une_<name>.png        1080x1920  Instagram highlight covers (Prix, Étapes, Avis, Parents, Contact)
  kit/images/facebook_couverture.png    1640x624   Facebook page cover (content in the mobile-safe centre)
  kit/images/apercu_profil_instagram.png 1080x2450 how the profile looks with the 9 covers (needs renders/covers)

usage: python3 scripts/stills.py
"""
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import ASSETS, BUILD, ENGINE, ROOT  # noqa: E402

OUT = ROOT / "kit" / "images"
SRC = BUILD / "_stills"
TEL = "+7 996 433 4489"
WM = '<span class="wm">Rus<span class="s">Study</span>.</span>'


def icons_js():
    lib = (ENGINE / "lib.js").read_text().splitlines()
    a = next(i for i, l in enumerate(lib) if "---- pixel icons" in l)
    b = next(i for i, l in enumerate(lib) if "---- shared moves" in l)
    return "const RTL = false;\nconst $$ = (s, r) => Array.from((r || document).querySelectorAll(s));\n" + "\n".join(lib[a:b])


def page(w, h, css, body, script=""):
    base = (ENGINE / "style.css").read_text()
    return f"""<!doctype html><html lang="fr"><head><meta charset="UTF-8"><style>{base}
      html, body {{ width: {w}px; height: {h}px; overflow: hidden; }}
      .pg {{ position: absolute; left: 0; top: 0; width: {w}px; height: {h}px; overflow: hidden; font-family: "Space Grotesk", "Cairo", sans-serif; }}
{css}</style></head><body><div class="pg">{body}</div><script>{icons_js()}
{script}</script></body></html>"""


NIGHT_JS = """
function night(cv, seed, sky) {
  const ctx = cv.getContext("2d"), W = cv.width, H = cv.height;
  let a = seed;
  const rng = () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, "#0a1433"); g.addColorStop(0.6, "#12276b"); g.addColorStop(1, "#1d3f9e");
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = "#fff";
  for (let i = 0; i < W / 14; i++) { ctx.globalAlpha = 0.3 + rng() * 0.7; const r = 1 + rng() * 2.4; ctx.fillRect(rng() * W, rng() * H * 0.8, r, r); }
  ctx.globalAlpha = 1;
  let x = -10;
  while (x < W) {
    const w = 50 + Math.floor(rng() * 5) * 16, h = sky * (0.45 + Math.floor(rng() * 9) * 0.07);
    ctx.fillStyle = "#081030"; ctx.fillRect(x, H - h, w, h);
    ctx.fillStyle = "#fbbb21";
    for (let wy = H - h + 18; wy < H - 20; wy += 26) for (let wx = x + 10; wx < x + w - 14; wx += 20) if (rng() < 0.3) ctx.fillRect(wx, wy, 8, 11);
    x += w + 5;
  }
}
"""


def avatar():
    css = """
      .av { position: absolute; inset: 0; background: radial-gradient(circle at 34% 28%, #c58cff 0%, #a855f7 42%, #7e22ce 100%); }
      .mono { position: absolute; left: 0; right: 0; top: 168px; text-align: center; font-weight: 700; font-size: 660px;
        letter-spacing: -0.07em; line-height: 1; color: #fff; padding-right: 30px; }
      .mono .d { color: #0a0a0a; }
      .pl { position: absolute; left: 618px; top: 214px; }
      .st { position: absolute; }
    """
    body = """<div class="av"></div>
      <span class="pix pl" data-icon="plane" data-px="8"></span>
      <span class="pix st" style="left: 250px; top: 236px" data-icon="star" data-px="7" data-pal='{"W":"#ffffff","G":"#fbbb21"}'></span>
      <span class="pix st" style="left: 790px; top: 700px" data-icon="star" data-px="5" data-pal='{"W":"#fbbb21","G":"#ffffff"}'></span>
      <div class="mono">R<span class="d">.</span></div>"""
    return page(1080, 1080, css, body)


HIGHLIGHTS = [
    ("prix", "coin", "#0a0a0a", 30),
    ("etapes", "plane", "#2460e8", 22),
    ("avis", "star", "#a855f7", 52),
    ("parents", "shield", "#22c55e", 30),
    ("contact", "chat", "#f97316", 30),
]


def highlight(icon, color, px):
    css = f"""
      .bg {{ position: absolute; inset: 0; background: #f0ebe3;
        background-image: linear-gradient(rgba(10,10,10,.05) 2px, transparent 2px), linear-gradient(90deg, rgba(10,10,10,.05) 2px, transparent 2px);
        background-size: 72px 72px; }}
      .c {{ position: absolute; left: 140px; top: 560px; width: 800px; height: 800px; border-radius: 50%; background: {color};
        box-shadow: 0 0 0 14px #0a0a0a; display: flex; align-items: center; justify-content: center; }}
    """
    body = f"""<div class="bg"></div><div class="c"><span class="pix" data-icon="{icon}" data-px="{px}"></span></div>"""
    return page(1080, 1920, css, body)


def fb_cover():
    css = """
      #sky { position: absolute; left: 0; top: 0; }
      .mid { position: absolute; left: 0; right: 0; top: 92px; display: flex; flex-direction: column; align-items: center; color: #fff; }
      .mid .wm { font-size: 150px; }
      .mid .wm .s { color: #c084fc; }
      .tg { margin-top: 18px; font-size: 38px; font-weight: 600; letter-spacing: 0.06em; color: rgba(255,255,255,.85); display: flex; gap: 22px; align-items: center; }
      .tg .ar { font-family: "Cairo", sans-serif; font-weight: 700; letter-spacing: 0; direction: rtl; }
      .tg i { width: 10px; height: 10px; border-radius: 50%; background: #fbbb21; }
      .row { margin-top: 30px; display: flex; gap: 18px; }
      .row .pill { height: 66px; padding: 0 28px; font-size: 30px; font-weight: 700; background: rgba(255,255,255,.12); color: #fff; box-shadow: inset 0 0 0 3px rgba(255,255,255,.25); }
      .row .pill.g { background: #fbbb21; color: #0a0a0a; box-shadow: none; }
      .pl { position: absolute; left: 1290px; top: 70px; transform: rotate(-8deg); }
      .pl2 { position: absolute; left: 150px; top: 96px; transform: rotate(-10deg); }
    """
    body = f"""<canvas id="sky" width="1640" height="624"></canvas>
      <span class="pix pl" data-icon="plane" data-px="7"></span>
      <span class="pix pl2" data-icon="cap" data-px="6"></span>
      <div class="mid">{WM}
        <div class="tg"><span>ÉTUDES EN RUSSIE</span><i></i><span class="ar">الدراسة في روسيا</span></div>
        <div class="row"><span class="pill">Universités d'État</span><span class="pill">+1 200 étudiants tunisiens</span><span class="pill g">1ère consultation gratuite</span></div>
      </div>"""
    return page(1640, 624, css, body, NIGHT_JS + 'night(document.getElementById("sky"), 2026, 170);')


GRID = ["09-rentree-2026", "04-le-vrai-prix", "01-temoignage-etudiant", "05-les-5-etapes", "07-parents", "08-whatsapp", "06-documents", "02-temoignage-parent", "03-premiere-semaine"]
GRID_LANG = ["derja", "fr", "derja", "fr", "derja", "fr", "derja", "fr", "derja"]


def profile_mock():
    cells = []
    for slug, lang in zip(GRID, GRID_LANG):
        p = ROOT / "renders" / "covers" / f"{slug}_{lang}.png"
        if not p.exists():
            return None
        shutil.copy(p, SRC / f"c_{slug}_{lang}.png")
        cells.append(f'<div class="cell" style="background-image: url(c_{slug}_{lang}.png)"></div>')
    shutil.copy(OUT / "photo_profil.png", SRC / "avatar.png")
    hl = "".join(
        f'<div class="hl"><div class="hc"><img src="hl_{n}.png"></div><span>{lab}</span></div>'
        for (n, *_), lab in zip(HIGHLIGHTS, ["Prix", "Étapes", "Avis", "Parents", "Contact"])
    )
    for n, *_ in HIGHLIGHTS:
        shutil.copy(OUT / f"a_la_une_{n}.png", SRC / f"hl_{n}.png")
    css = """
      .pg { background: #ffffff; color: #0a0a0a; }
      .top { height: 120px; display: flex; align-items: center; padding: 0 40px; font-size: 40px; font-weight: 700; letter-spacing: -0.02em; gap: 16px; }
      .hd { display: flex; align-items: center; gap: 40px; padding: 10px 40px 0; }
      .avt { width: 220px; height: 220px; border-radius: 50%; background: url(avatar.png) center / cover; box-shadow: 0 0 0 6px #fff, 0 0 0 10px #a855f7; flex: none; }
      .nm { font-size: 38px; font-weight: 700; }
      .ct { font-size: 28px; color: #737373; margin-top: 6px; }
      .bio { padding: 26px 40px 0; font-size: 31px; line-height: 1.42; }
      .bio .ar { font-family: "Cairo", sans-serif; font-weight: 600; direction: rtl; text-align: left; }
      .bio a { color: #2460e8; font-weight: 600; text-decoration: none; }
      .bt { display: flex; gap: 16px; padding: 28px 40px 0; }
      .bt span { flex: 1; height: 72px; border-radius: 16px; background: #efefef; display: flex; align-items: center; justify-content: center; font-size: 29px; font-weight: 700; }
      .bt span.wa { background: #16a34a; color: #fff; }
      .hls { display: flex; gap: 30px; padding: 34px 40px 0; }
      .hl { display: flex; flex-direction: column; align-items: center; gap: 12px; font-size: 25px; font-weight: 500; }
      .hc { width: 150px; height: 150px; border-radius: 50%; overflow: hidden; box-shadow: 0 0 0 4px #fff, 0 0 0 7px #d4d4d4; }
      .hc img { width: 150px; height: 267px; margin-top: -58px; object-fit: cover; }
      .grid { position: absolute; left: 0; top: 1010px; width: 1080px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; }
      .cell { height: 477px; background-size: 100% auto; background-position: center 42%; }
    """
    body = f"""<div class="top">russtudy</div>
      <div class="hd"><div class="avt"></div><div><div class="nm">RusStudy · Études en Russie</div><div class="ct">Service éducatif</div></div></div>
      <div class="bio">Études en Russie 🇷🇺 · universités d'État<br><div class="ar">القراية في روسيا · جامعات حكومية</div>+1 200 étudiants tunisiens depuis 2018<br>💬 1ère consultation gratuite ⬇️<br><a>wa.me/79964334489</a></div>
      <div class="bt"><span>Suivre</span><span class="wa">WhatsApp</span><span>Contacter</span></div>
      <div class="hls">{hl}</div>
      <div class="grid">{"".join(cells)}</div>"""
    return page(1080, 2450, css, body)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (SRC / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (ASSETS / "fonts").glob("*.woff2"):
        shutil.copy(f, SRC / "assets" / "fonts" / f.name)
    jobs = []

    def add(name, html, w, h, out):
        (SRC / name).write_text(html)
        jobs.append({"page": str(SRC / name), "out": str(out), "w": w, "h": h})

    add("avatar.html", avatar(), 1080, 1080, OUT / "photo_profil.png")
    for n, icon, color, px in HIGHLIGHTS:
        add(f"hl_{n}.html", highlight(icon, color, px), 1080, 1920, OUT / f"a_la_une_{n}.png")
    add("fb.html", fb_cover(), 1640, 624, OUT / "facebook_couverture.png")
    mods = sorted(glob.glob(os.path.expanduser("~/.npm/_npx/*/node_modules/puppeteer-core")))
    env = dict(os.environ, NODE_PATH=str(Path(mods[-1]).parent))
    jf = SRC / "jobs.json"
    jf.write_text(json.dumps(jobs))
    subprocess.run(["node", str(ROOT / "scripts" / "shoot.cjs"), str(jf)], check=True, env=env)
    mock = profile_mock()
    if mock:
        jobs = []
        add("profile.html", mock, 1080, 2450, OUT / "apercu_profil_instagram.png")
        jf.write_text(json.dumps(jobs))
        subprocess.run(["node", str(ROOT / "scripts" / "shoot.cjs"), str(jf)], check=True, env=env)
    else:
        print("covers missing: run scripts/render_all.sh first for the profile preview")


if __name__ == "__main__":
    main()
