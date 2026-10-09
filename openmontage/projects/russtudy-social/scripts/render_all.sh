#!/usr/bin/env bash
# Render the RusStudy social series: 9 episodes x (French, derja), 1080x1920, 30 fps.
#   music beds -> build the 18 HyperFrames projects -> lint -> render -> swap in the exact
#   music bed -> cover PNG (frame at the episode's cover_at) -> report.
# Output: renders/<slug>_fr.mp4, renders/<slug>_derja.mp4, renders/covers/<slug>_<fr|derja>.png
#
# usage: bash scripts/render_all.sh                 (everything)
#        bash scripts/render_all.sh 04 09           (episodes whose slug starts with 04 or 09)
set -euo pipefail
cd "$(dirname "$0")/.."
HF="npx --yes hyperframes@0.8.133"

python3 scripts/beds.py "$@"
python3 scripts/build.py "$@"
mkdir -p renders/covers

ep_field() { # $1 = build dir, $2 = python expression on the episode dict `e` / timeline `ep`
  python3 - "$1" "$2" <<'PY'
import json, re, sys
d, expr = sys.argv[1], sys.argv[2]
ep = json.loads(re.search(r"window.__EP = (\{.*?\});\n", open(d + "/index.html").read()).group(1))
slug = d.rstrip("/").split("/")[-1].rsplit("-", 1)[0]
e = json.load(open(f"episodes/{slug}.json"))
print(eval(expr))
PY
}

done_list=()
for slug in $(python3 -c "
import sys; sys.path.insert(0, 'scripts')
from build import load_episodes
print(' '.join(e['slug'] for e in load_episodes(sys.argv[1:])))" "$@"); do
  for lang in fr ar; do
    d="build/${slug}-${lang}"
    tag=$([[ $lang == ar ]] && echo derja || echo fr)
    out="renders/${slug}_${tag}.mp4"
    D=$(ep_field "$d" "ep['D']")
    echo "==> ${slug} (${tag}) ${D} s"
    (cd "$d" && $HF lint >/dev/null)
    (cd "$d" && $HF render --quality high --fps 30 --output "../../renders/_tmp.mp4" >/dev/null)
    ffmpeg -hide_banner -loglevel error -y -i renders/_tmp.mp4 -i "$d/assets/bed.wav" \
      -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t "$D" "$out"
    rm -f renders/_tmp.mp4
    ffmpeg -hide_banner -loglevel error -y -ss "$(ep_field "$d" "e['cover_at']")" -i "$out" -frames:v 1 "renders/covers/${slug}_${tag}.png"
    done_list+=("$out")
  done
done

for f in "${done_list[@]}"; do
  d=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f")
  r=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$f")
  s=$(du -h "$f" | cut -f1)
  echo "OK  $f  ${r}  ${d}s  ${s}"
done
