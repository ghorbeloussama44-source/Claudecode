"""Regenerate the dot-matrix land map of the flight scene (S7) in hyperframes/index.html.

The map is a 54 x 96 grid of 20 px cells (1080 x 1920) in an equirectangular projection
(longitude compressed by cos 46 deg), placed so that Tunis lands on (220, 1320) and
Moscow on (845, 698). Each cell is land when >= 5 of 9 samples are land.

The 16:9 version uses a 96 x 54 grid (1920 x 1080), 34 px per degree, Tunis on (700, 880):
    python3 scripts/make_dotmap.py MASK.npz 1920 1080 34 700 880

Land data: global-land-mask 1.0.0 (MIT, Todd Karin) = NOAA GLOBE 1 km mask (public domain).
    pip download global-land-mask --no-deps -d /tmp/glm && unzip -o /tmp/glm/*.whl -d /tmp/glm
    python3 scripts/make_dotmap.py /tmp/glm/global_land_mask/globe_combined_mask_compressed.npz
Paste the printed `const MAP_ROWS = [...]` over the one in index.html (S7 block). If a city
moves, also update R0..R3 / the route path `M220,1320 C420,1150 600,720 845,698` and the pins.
"""
import sys

import numpy as np

npz = np.load(sys.argv[1], allow_pickle=False)  # data only, no pickled code
ocean, lat, lon = npz["mask"], npz["lat"], npz["lon"]  # mask is True over the ocean

args = [float(a) for a in sys.argv[2:7]] if len(sys.argv) >= 7 else [1080, 1920, 32.8, 220, 1320]
CELL = 20
COLS, ROWS = int(args[0]) // CELL, int(args[1]) // CELL
S = args[2]  # px per degree of latitude
K = np.cos(np.radians(46.0))  # longitude compression at the route's mid-latitude
TUN, TUN_XY = (36.8065, 10.1815), (args[3], args[4])
lon0 = TUN[1] - TUN_XY[0] / (S * K)
lat_top = TUN[0] + TUN_XY[1] / S
dlat, dlon = lat[1] - lat[0], lon[1] - lon[0]

rows = []
for r in range(ROWS):
    line = []
    for c in range(COLS):
        hits = 0
        for sy in (0.25, 0.5, 0.75):
            for sx in (0.25, 0.5, 0.75):
                la = lat_top - (r + sy) * CELL / S
                lo = lon0 + (c + sx) * CELL / (S * K)
                i = int(round((la - lat[0]) / dlat))
                j = int(round((lo - lon[0]) / dlon))
                hits += not bool(ocean[i, j])
        line.append("1" if hits >= 5 else "0")
    rows.append("".join(line))

mow = ((37.6173 - lon0) * S * K, (lat_top - 55.7558) * S)
print(f"// Moscow projects to ({mow[0]:.1f}, {mow[1]:.1f})", file=sys.stderr)
print("const MAP_ROWS = [\n" + "".join(f'        "{row}",\n' for row in rows) + "      ];")
