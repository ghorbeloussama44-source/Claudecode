#!/usr/bin/env bash
# Render the TSSR Instagram ad (derja, 1080x1920, 30 fps, 48 s):
#   soundtrack (music edit + SFX + loudness) -> lint -> render -> swap in the exact soundtrack
#   -> light version for WhatsApp -> cover PNG.
# Output: renders/tssr_pub_instagram_48s_derja_<version>.mp4, _leger.mp4, _couverture.png
#
# usage: bash scripts/render.sh [version]      (default: v1)
set -euo pipefail
cd "$(dirname "$0")/.."
HF="npx --yes hyperframes@0.8.133"
V="${1:-v1}"
OUT="renders/tssr_pub_instagram_48s_derja_${V}"
mkdir -p renders

echo "==> soundtrack"
python3 scripts/build_audio.py
echo "==> lint + render (about 4 min)"
(cd hyperframes && $HF lint >/dev/null)
(cd hyperframes && $HF render --quality high --fps 30 --output ../renders/_tmp.mp4 >/dev/null)
# Instagram-ready encode (~30 MB): x264 high profile, capped bitrate, exact soundtrack
ffmpeg -hide_banner -loglevel error -y -i renders/_tmp.mp4 -i hyperframes/assets/audio/soundtrack.wav \
  -map 0:v:0 -map 1:a:0 -c:v libx264 -preset slow -crf 19 -maxrate 6M -bufsize 12M -pix_fmt yuv420p \
  -profile:v high -level 4.1 -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t 48 "${OUT}.mp4"
rm -f renders/_tmp.mp4

echo "==> light version + cover"
ffmpeg -hide_banner -loglevel error -y -i "${OUT}.mp4" -vf scale=720:1280 -c:v libx264 -preset slow -crf 25 \
  -c:a aac -b:a 128k -movflags +faststart "${OUT}_leger.mp4"
ffmpeg -hide_banner -loglevel error -y -ss 3.0 -i "${OUT}.mp4" -frames:v 1 "${OUT}_couverture.png"
ls -la "${OUT}"*
