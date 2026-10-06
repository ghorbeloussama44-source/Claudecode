#!/usr/bin/env python3
"""Build the YouTube 16:9 version (hyperframes-16x9/) from the vertical master.

The vertical composition `hyperframes/index.html` (1080x1920) stays the single source of
truth: texts, colours, timings and animations are edited there only. This script derives
`hyperframes-16x9/index.html` (1920x1080) by
  1. swapping the values that depend on the frame size. Every swap is asserted: if the
     vertical file no longer contains a snippet, the script stops and prints it, so a
     layout change in the vertical can never silently break the 16:9 version;
  2. wrapping groups of portrait illustrations in "portrait zones" (.pz: the vertical
     layout, scaled and moved into the right half of the 16:9 frame, titles on the left);
  3. appending a landscape CSS block (left-hand titles, HUD as a top bar, ...);
and copies the shared assets (fonts, GSAP, soundtrack) into the 16:9 project.

    python3 scripts/make_landscape.py        # after every edit of hyperframes/index.html

Only `assets/img/amphitheatre_16x9.jpg` (a 16:9 crop of the same Unsplash photo) belongs to
the 16:9 project itself; everything else in hyperframes-16x9/ is regenerated.
"""
import math
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "hyperframes"
DST = ROOT / "hyperframes-16x9"

s = (SRC / "index.html").read_text(encoding="utf-8")


def fail(msg, snippet):
    sys.exit(f"make_landscape: {msg}\n---\n{snippet}\n---\nUpdate scripts/make_landscape.py to match hyperframes/index.html.")


def sub(old, new, n=1):
    """Replace `old` by `new`; `old` must occur exactly n times."""
    global s
    c = s.count(old)
    if c != n:
        fail(f"expected {n} occurrence(s), found {c}:", old)
    s = s.replace(old, new)


def zone(start, end, z, after=False):
    """Wrap the markup from `start` to `end` (first occurrence after start) in a portrait zone.

    z = (x, y, k): the vertical 1080x1920 layout inside is scaled by k and moved by (x, y)."""
    global s
    if s.count(start) != 1:
        fail("zone start must be unique:", start)
    i = s.index(start)
    j = s.find(end, i)
    if j < 0:
        fail("zone end not found:", end)
    if after:
        j += len(end)
    x, y, k = z
    s = s[:i] + f'<div class="pz" style="transform: translate({x}px, {y}px) scale({k})">' + s[i:j] + "</div>" + s[j:]


def to_screen(z, px, py):
    """Vertical-layout point -> 16:9 screen point through zone z."""
    x, y, k = z
    return round(x + k * px, 1), round(y + k * py, 1)


def js_round(v):
    return math.floor(v + 0.5)


def num(pattern):
    m = re.search(pattern, s)
    if not m:
        fail("value not found:", pattern)
    return [float(g) for g in m.groups()]


# portrait zones (x, y, scale)
Z_S1 = (876, -310, 0.86)  # phone
Z_S2A = (937, -257, 0.82)  # call + profile analysis
Z_S2B = (73.2, -362, 0.78)  # "ton plan" card, under the title
Z_S3 = (895, -421, 0.9)  # documents + folder
Z_S4 = (863, -397, 0.92)  # envelope + letter
Z_S5 = (810, -400, 0.95)  # passport + insurance card
Z_S9 = (800, -364.8, 0.82)  # door, room, key card

# ---------------------------------------------------------------- frame
sub('<html lang="fr" data-resolution="portrait">', '<html lang="fr" data-resolution="landscape">')
sub('<meta name="viewport" content="width=1080, height=1920" />', '<meta name="viewport" content="width=1920, height=1080" />')
sub("<title>RusStudy — Le parcours 40s</title>", "<title>RusStudy — Le parcours 40s 16:9</title>")
sub('data-width="1080"\n      data-height="1920"', 'data-width="1920"\n      data-height="1080"')
for sel in ("      html,\n      body {\n", "      #root {\n        position: relative;\n", "      .clip {\n        position: absolute;\n        left: 0;\n        top: 0;\n", "      .fill {\n        position: absolute;\n        left: 0;\n        top: 0;\n"):
    sub(sel + "        width: 1080px;\n        height: 1920px;", sel + "        width: 1920px;\n        height: 1080px;")

# ---------------------------------------------------------------- S1
zone('<div id="s1-cam">', "\n      </section>", Z_S1)
sub(
    """          [44, 1560, 10, 0.2, false, 0],
          [800, 1640, 12, 0.15, true, 0.3],
          [-34, 760, 9, 0.13, false, 0.6],
          [940, 690, 8, 0.13, true, 0.9],
          [440, 1730, 7, 0.1, false, 1.2],""",
    """          [70, 800, 10, 0.2, false, 0],
          [1700, 820, 12, 0.15, true, 0.3],
          [860, 120, 9, 0.13, false, 0.6],
          [1730, 200, 8, 0.13, true, 0.9],
          [520, 900, 7, 0.1, false, 1.2],""",
)
# ripple into step 01 from the call button: its screen position goes through the phone zone
tap2 = num(r"const TAP2 = \{ x: ([\d.]+), y: ([\d.]+) \}")
t2 = to_screen(Z_S1, *tap2)
sub('clip-path: circle(0px at 492px 1294px)', f"clip-path: circle(0px at {t2[0]}px {t2[1]}px)")
x, y, k = Z_S1
sub(
    "{ clipPath: `circle(0px at ${TAP2.x}px ${TAP2.y}px)` },\n        { clipPath: `circle(1500px at ${TAP2.x}px ${TAP2.y}px)`",
    f"{{ clipPath: `circle(0px at ${{{x} + {k} * TAP2.x}}px ${{{y} + {k} * TAP2.y}}px)` }},\n"
    f"        {{ clipPath: `circle(1650px at ${{{x} + {k} * TAP2.x}}px ${{{y} + {k} * TAP2.y}}px)`",
)

# ---------------------------------------------------------------- HUD (top bar)
for i, (old, new) in enumerate([("28px", 680), ("211.2px", 850), ("394.4px", 1020), ("577.6px", 1190), ("760.8px", 1360)]):
    sub(f'<div class="seg" id="seg{i + 1}" style="left: {old}">', f'<div class="seg" id="seg{i + 1}" style="left: {new}px">')

# ---------------------------------------------------------------- S2 / S3
zone('<div id="s2-call">', '<div id="s2-plan">', Z_S2A)
zone('<div id="s2-plan">', '<div id="s2-shade"', Z_S2B)
sub('tl.fromTo("#s3", { y: 1920 }, { y: 0,', 'tl.fromTo("#s3", { y: 1080 }, { y: 0,')
sub('tl.to("#s2-wrap", { y: -560,', 'tl.to("#s2-wrap", { y: -340,')
zone('<div id="fold-tab">', "</div>\n      </section>", Z_S3)

# ---------------------------------------------------------------- S4
sub("inset(0px 0px 1920px 0px)", "inset(0px 0px 1080px 0px)", 2)
zone('<div id="env-a">', '<canvas id="s4-conf"', Z_S4)
# confetti: full-frame canvas, burst from the letter's screen position
sub('<canvas id="s4-conf" width="1080" height="1920"></canvas>', '<canvas id="s4-conf" width="1920" height="1080"></canvas>')
sub("cctx.clearRect(0, 0, 1080, 1920);", "cctx.clearRect(0, 0, 1920, 1080);")
cx, cy = num(r"x: ([\d.]+) \+ \(confRng\(\) - 0\.5\) \* 120,\s+y: ([\d.]+) \+ \(confRng\(\) - 0\.5\) \* 60,")
bx, by = to_screen(Z_S4, cx, cy)
sub(f"x: {cx:g} + (confRng() - 0.5) * 120,", f"x: {bx:g} + (confRng() - 0.5) * 120,")
sub(f"y: {cy:g} + (confRng() - 0.5) * 60,", f"y: {by:g} + (confRng() - 0.5) * 60,")
sub('tl.fromTo("#s4-pan", { x: 0 }, { x: -1080,', 'tl.fromTo("#s4-pan", { x: 0 }, { x: -1920,')
sub('tl.fromTo("#s5-pan", { x: 1080 }, { x: 0,', 'tl.fromTo("#s5-pan", { x: 1920 }, { x: 0,')

# ---------------------------------------------------------------- S5 + boarding pass
zone('<div id="pp">', "\n          </div>\n        </div>\n      </section>", Z_S5)
sub('tl.fromTo("#bp", { y: 640, rotation: 7 }', 'tl.fromTo("#bp", { y: 520, rotation: 7 }')
sub('tl.to("#bp", { y: -420, scale: 1.06,', 'tl.to("#bp", { x: 380, y: -250, scale: 1.06,')
sub('tl.to("#bp-main", { x: -780, y: 360, rotation: -14,', 'tl.to("#bp-main", { x: -1300, y: 360, rotation: -14,')
sub('tl.to("#bp-stub", { x: 600, y: -480, rotation: 26,', 'tl.to("#bp-stub", { x: 900, y: -480, rotation: 26,')
sub(
    "const TEAR_X = 752; // perforation x once the pass is centred (80 + 460 + 200 * 1.06)",
    "const TEAR_X = 1172; // perforation x once the pass is centred (120 + 380 + 460 + 200 * 1.06)",
)
sub("for (let k = 0; k <= 48; k++) zig.push({ y: k * 40,", "for (let k = 0; k <= 27; k++) zig.push({ y: k * 40,")

# ---------------------------------------------------------------- S6 + cloud wall
sub('<svg id="s6-route" width="1080" height="1920" viewBox="0 0 1080 1920">', '<svg id="s6-route" width="1920" height="1080" viewBox="0 0 1920 1080">')
sub('<mask id="s6-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="1080" height="1920">', '<mask id="s6-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080">')
sub("M-220,1520 C200,1400 660,1080 1420,560", "M-260,1000 C300,900 1000,640 2160,240", 3)
sub("const y = 200 + i * 270 + crng() * 80;", "const y = 120 + i * 150 + crng() * 50;")
sub("const x0 = -300 + crng() * 1100;", "const x0 = -300 + crng() * 2000;")
sub("for (let j = 0; j < 27; j++) {", "for (let j = 0; j < 48; j++) {")
sub("const y1 = 2600 + Math.round(b * 5) * C;", "const y1 = 1800 + Math.round(b * 5) * C;")
sub('<svg width="1080" height="2800" viewBox="0 0 1080 2800" shape-rendering="crispEdges">', '<svg width="1920" height="2000" viewBox="0 0 1920 2000" shape-rendering="crispEdges">')
sub('tl.fromTo("#cw-wall", { y: 1920 }, { y: -2800,', 'tl.fromTo("#cw-wall", { y: 1080 }, { y: -2000,')

# ---------------------------------------------------------------- S7 (96 x 54 map, Tunis (700, 880) -> Moscou (1348, 236))
sub('<canvas id="s7-map" width="1080" height="1920"></canvas>', '<canvas id="s7-map" width="1920" height="1080"></canvas>')
sub('<svg id="s7-svg" width="1080" height="1920" viewBox="0 0 1080 1920">', '<svg id="s7-svg" width="1920" height="1080" viewBox="0 0 1920 1080">')
sub('<mask id="s7-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="1080" height="1920">', '<mask id="s7-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080">')
sub("M220,1320 C420,1150 600,720 845,698", "M700,880 C906,705 1091,262 1348,236", 3)
sub('cx="220" cy="1320"', 'cx="700" cy="880"', 3)
sub('cx="845" cy="698"', 'cx="1348" cy="236"', 3)
i = s.find("      const MAP_ROWS = [\n")
j = s.find("      ];\n", i)
if i < 0 or j < 0 or s.count("const MAP_ROWS = [") != 1:
    fail("MAP_ROWS block not found", "const MAP_ROWS = [ ... ];")
rows16 = (ROOT / "scripts" / "map_rows_16x9.js").read_text(encoding="utf-8").strip()
s = s[:i] + "      " + rows16 + "\n" + s[j + len("      ];\n"):]
sub(
    """      const R0 = { x: 220, y: 1320 },
        R1 = { x: 420, y: 1150 },
        R2 = { x: 600, y: 720 },
        R3 = { x: 845, y: 698 };""",
    """      const R0 = { x: 700, y: 880 },
        R1 = { x: 906, y: 705 },
        R2 = { x: 1091, y: 262 },
        R3 = { x: 1348, y: 236 };""",
)
sub("mctx.clearRect(0, 0, 1080, 1920);", "mctx.clearRect(0, 0, 1920, 1080);")
sub('tl.fromTo("#s7-cam", { x: 0, y: -1004, scale: 1.7 }', 'tl.fromTo("#s7-cam", { x: -430, y: -736, scale: 1.7 }')
sub('tl.to("#s7-cam", { x: -1995, y: -1134, scale: 3.0,', 'tl.to("#s7-cam", { x: -3084, y: -168, scale: 3.0,')
sub('transformOrigin: "220px 1320px"', 'transformOrigin: "700px 880px"')
sub('transformOrigin: "845px 698px"', 'transformOrigin: "1348px 236px"')
sub("const x0 = 900 + prng() * 500,\n            y0 = -150 + prng() * 1500;", "const x0 = 1500 + prng() * 700,\n            y0 = -150 + prng() * 900;")
sub("{ x: x0 - 1500 * sp, y: y0 + 700 * sp,", "{ x: x0 - 2400 * sp, y: y0 + 500 * sp,")
sub('tl.fromTo("#s7-notif", { y: -260, opacity: 0 }', 'tl.fromTo("#s7-notif", { y: 260, opacity: 0 }')
sub('tl.to("#s7-notif", { y: -260, opacity: 0,', 'tl.to("#s7-notif", { y: 260, opacity: 0,')

# ---------------------------------------------------------------- S8
sub("circle(0px at 540px 960px)", "circle(0px at 960px 540px)", 2)
sub('{ clipPath: "circle(1300px at 540px 960px)",', '{ clipPath: "circle(1150px at 960px 540px)",')
sub('tl.fromTo("#sign-pos", { y: 1200, rotation: -10 }', 'tl.fromTo("#sign-pos", { y: 900, rotation: -10 }')

# ---------------------------------------------------------------- TR (transfer)
TRL = dict(W=1920, H=1080, horizon=640, railY=885, roadTop=955, roadH=86, trainX=470, sunX=1480, poleTop=640, starY0=30, starY1=480, fenceY=1052, tuftY=2000, carX0=240, carX1=1360, signX0=1960, signT=2.3)
sub('<canvas id="tr-cv" width="1080" height="1920"></canvas>', '<canvas id="tr-cv" width="1920" height="1080"></canvas>')
sub(
    "const TRL = { W: 1080, H: 1920, horizon: 1180, railY: 1462, roadTop: 1592, roadH: 108, trainX: 60, sunX: 770, poleTop: 1210, starY0: 40, starY1: 800, fenceY: 1730, tuftY: 1846, carX0: 20, carX1: 620, signX0: 1100, signT: 2.75 };",
    "const TRL = { " + ", ".join(f"{k}: {v}" for k, v in TRL.items()) + " };",
)
sub("for (let i = 0; i < 135; i++) {", "for (let i = 0; i < 240; i++) {")
sub("% 135]", "% 240]")
sub(
    "background: linear-gradient(180deg, #160d38 0%, #2e1065 22%, #6d28d9 41%, #a855f7 51%, #f97316 59%, #fbbb21 61.5%);",
    "background: linear-gradient(180deg, #160d38 0%, #2e1065 21.2%, #6d28d9 39.5%, #a855f7 49.2%, #f97316 56.9%, #fbbb21 59.3%);",
)
# the dorm opens through the coach door: its first frame, as in trDoorInset(T9 - 0.28 - T_TR)
t_tr, t9 = num(r"const T_TR = ([\d.]+),"), num(r"T9 = ([\d.]+),")
lt = t9[0] - 0.28 - t_tr[0]
dx = TRL["trainX"] + js_round(10 * lt) + 580
dy = TRL["railY"] - 188 + js_round(2 * math.sin(lt * 22)) + 44
sub("clip-path: inset(1318px 379px 502px 677px round 6px)", f"clip-path: inset({dy}px {1920 - (dx + 24)}px {1080 - (dy + 100)}px {dx}px round 6px)")

# ---------------------------------------------------------------- S9
zone('<div id="door-frame">', '\n        </div>\n        <div id="s9-flash"', Z_S9)
o9 = to_screen(Z_S9, *num(r"#s9-cam \{\n\s+transform-origin: ([\d.]+)px ([\d.]+)px;"))
sub('tl.fromTo("#s9-cam", { scale: 1 }, { scale: 7,', 'tl.fromTo("#s9-cam", { scale: 1 }, { scale: 9,')

# ---------------------------------------------------------------- S10
sub('src="assets/img/amphitheatre.jpg"', 'src="assets/img/amphitheatre_16x9.jpg"')
sub(
    'style="background: linear-gradient(180deg, rgba(10, 10, 10, 0.84) 0%, rgba(10, 10, 10, 0.6) 28%, rgba(10, 10, 10, 0.12) 44%, rgba(10, 10, 10, 0.16) 52%, rgba(10, 10, 10, 0.82) 100%)"',
    'style="background: linear-gradient(90deg, rgba(10, 10, 10, 0.86) 0%, rgba(10, 10, 10, 0.66) 36%, rgba(10, 10, 10, 0.22) 58%, rgba(10, 10, 10, 0.34) 100%)"',
)
sub('tl.fromTo("#sc-pos", { y: 1000, rotationX: 55, scale: 0.8 }', 'tl.fromTo("#sc-pos", { y: 800, rotationX: 55, scale: 0.8 }')
sub(
    """          [150, 975],
          [900, 990],
          [118, 1330],
          [948, 1400],
          [520, 952],
          [742, 1490],""",
    """          [1036, 300],
          [1792, 296],
          [1010, 640],
          [1836, 700],
          [1420, 280],
          [1600, 790],""",
)

# ---------------------------------------------------------------- S11
sub(
    'style="background: radial-gradient(55% 24% at 36% 26%, rgba(251, 187, 33, 0.17), rgba(251, 187, 33, 0) 70%)"',
    'style="background: radial-gradient(34% 44% at 24% 46%, rgba(251, 187, 33, 0.17), rgba(251, 187, 33, 0) 70%)"',
)

# ---------------------------------------------------------------- S12
sub('<canvas id="city" width="1080" height="1920"></canvas>', '<canvas id="city" width="1920" height="1080"></canvas>')
sub(
    "const CITY = { W: 1080, H: 1920, bh: [190, 220, 150], towerZone: [96, 300], towerH: [150, 70], towerX: 140, towerBase: 1540, cathZone: [676, 1100], cathH: [110, 90], wall: [700, 1500, 400] };",
    "const CITY = { W: 1920, H: 1080, bh: [120, 130, 120], towerZone: [110, 330], towerH: [90, 50], towerX: 170, towerBase: 860, cathZone: [1436, 1940], cathH: [40, 40], wall: [1460, 900, 480] };",
)
sub(
    """        { x: 748, top: 1296, A: "P", B: "G", drumH: 150, drum: "#b91c1c", d: 0.0 },
        { x: 846, top: 1250, A: "B", B: "W", drumH: 210, drum: "#c2410c", d: 0.07 },
        { x: 952, top: 1286, A: "N", B: "G", drumH: 170, drum: "#b91c1c", d: 0.12 },
        { x: 1048, top: 1336, A: "O", B: "W", drumH: 120, drum: "#c2410c", d: 0.18 },""",
    """        { x: 1508, top: 696, A: "P", B: "G", drumH: 150, drum: "#b91c1c", d: 0.0 },
        { x: 1606, top: 650, A: "B", B: "W", drumH: 210, drum: "#c2410c", d: 0.07 },
        { x: 1712, top: 686, A: "N", B: "G", drumH: 170, drum: "#b91c1c", d: 0.12 },
        { x: 1808, top: 736, A: "O", B: "W", drumH: 120, drum: "#c2410c", d: 0.18 },""",
)
sub("const TENT = { x: 900, top: 1226, h: 250 };", "const TENT = { x: 1660, top: 626, h: 250 };")
sub("const TAP3 = { x: 875, y: 835 };", "const TAP3 = { x: 1308, y: 450 };")

# ---------------------------------------------------------------- landscape CSS
CSS = f"""
      /* ================= 16:9 (YouTube) — generated by scripts/make_landscape.py ================= */
      .pz {{
        position: absolute;
        left: 0;
        top: 0;
        width: 1080px;
        height: 1920px;
        transform-origin: 0 0;
      }}
      .title {{
        left: 120px;
        top: 250px;
        font-size: 112px;
      }}
      .deco {{
        right: -30px;
        bottom: -130px;
        font-size: 640px;
      }}
      #s1-title {{
        left: 120px;
        top: 420px;
        font-size: 112px;
      }}
      #s1-title .ln {{
        height: 119px;
      }}
      #hud-box {{
        left: 96px;
        top: 40px;
        width: 1728px;
        height: 80px;
        border-radius: 26px;
      }}
      .seg {{
        top: 36px;
        width: 150px;
      }}
      #hud-lab {{
        top: 19px;
        width: 620px;
      }}
      #hud-wm {{
        top: 25px;
      }}
      #s3-sub {{
        left: 120px;
        top: 530px;
        font-size: 36px;
      }}
      #bp {{
        left: 120px;
        top: 680px;
      }}
      #s6-t {{
        left: 120px;
        top: 230px;
      }}
      #cw-wall {{
        width: 1920px;
        height: 2000px;
      }}
      #s7-cam {{
        width: 1920px;
        height: 1080px;
      }}
      #lb-tun {{
        left: 742px;
        top: 860px;
      }}
      #lb-mow {{
        left: 1394px;
        top: 206px;
      }}
      #s7-t {{
        left: 120px;
        top: 150px;
      }}
      #s7-notif {{
        left: 1000px;
        top: 880px;
        width: 820px;
      }}
      #flap {{
        left: 120px;
        top: 330px;
      }}
      #sign-pos {{
        left: 1180px;
        top: 310px;
      }}
      #s8-cap {{
        left: 120px;
        top: 790px;
        width: auto;
        text-align: left;
      }}
      #tr-t {{
        top: 150px;
      }}
      #tr-trip {{
        left: 120px;
        top: 398px;
      }}
      #tr-sub {{
        left: 120px;
        top: 506px;
      }}
      #s9-cam {{
        transform-origin: {o9[0]}px {o9[1]}px;
      }}
      #s9-wains {{
        top: 660px;
        width: 1920px;
        height: 254px;
      }}
      #s9-floor {{
        top: 914px;
        width: 1920px;
        height: 166px;
      }}
      #s9-chip {{
        left: 470px;
        top: 268px;
      }}
      #s10-img {{
        width: 1920px;
        height: 1080px;
      }}
      #sc-pos {{
        left: 1060px;
        top: 330px;
      }}
      #s11-deco {{
        left: 520px;
        top: 40px;
      }}
      #s11-k {{
        left: 120px;
        top: 200px;
      }}
      #s11-des {{
        left: 124px;
        top: 286px;
      }}
      #s11-num {{
        left: 112px;
        top: 368px;
      }}
      #s11-pill {{
        left: 120px;
        top: 628px;
      }}
      #st-tc {{
        left: 130px;
        top: 770px;
      }}
      #rc-mask {{
        left: 940px;
        top: 190px;
      }}
      #rc-slot {{
        left: 910px;
        top: 836px;
      }}
      #logo-lg {{
        top: 140px;
        width: 1920px;
        font-size: 150px;
      }}
      #lg-tag {{
        top: 312px;
        width: 1920px;
      }}
      #ring {{
        left: 860px;
        top: 115px;
      }}
      #wa {{
        left: 560px;
        top: 380px;
        width: 800px;
      }}
      #tel {{
        top: 556px;
        width: 1920px;
      }}
      #url {{
        top: 640px;
        width: 1920px;
      }}
      #cta-chip {{
        left: 680px;
        top: 720px;
      }}
      #click-ring {{
        left: 1248px;
        top: 390px;
      }}
    </style>"""
sub("\n    </style>", CSS)

# ---------------------------------------------------------------- write + sync shared assets
DST.mkdir(exist_ok=True)
(DST / "index.html").write_text(s, encoding="utf-8")
for sub_dir in ("fonts", "vendor", "audio"):
    shutil.copytree(SRC / "assets" / sub_dir, DST / "assets" / sub_dir, dirs_exist_ok=True)
for f in ("hyperframes.json", "package.json", "CLAUDE.md", "AGENTS.md"):
    shutil.copy2(SRC / f, DST / f)
img = DST / "assets" / "img" / "amphitheatre_16x9.jpg"
if not img.exists():
    sys.exit(f"make_landscape: missing {img.relative_to(ROOT)} (16:9 crop of the amphitheatre photo)")
print(f"hyperframes-16x9/index.html written ({len(s)} bytes); S2 ripple at {t2}, confetti at ({bx}, {by}), dorm push origin {o9}")
