#!/usr/bin/env bash
# One-command rebuild of the RusStudy "Le parcours" spot (37 s) after a retouch:
#   audio (music edit + SFX cues) -> lint -> render 60 fps + 30 fps -> remux the exact
#   master audio -> cover frames -> refresh OpenMontage artifacts.
#
# Usage:  bash scripts/render_all.sh            (full: audio + 60 fps + 30 fps)
#         bash scripts/render_all.sh --draft    (fast 30 fps draft only, renders/draft.mp4)
set -euo pipefail
cd "$(dirname "$0")/.."
HF="npx --yes hyperframes@0.8.133"   # pinned: the folder is named "hyperframes", a bare npx resolves the local package
DUR=37
NAME=russtudy_parcours_37s

python3 -c "import librosa, soundfile, scipy, jsonschema" 2>/dev/null || pip install -q -r scripts/requirements.txt

echo "==> soundtrack"
python3 scripts/build_audio.py
cp assets/audio/soundtrack.wav hyperframes/assets/audio/soundtrack.wav

cd hyperframes
$HF browser ensure >/dev/null
echo "==> lint"
$HF lint

remux() { # $1 = HyperFrames render, $2 = final file
  # HyperFrames' own audio pass lands ~1.4 dB under target: swap in the exact master
  ffmpeg -hide_banner -loglevel error -y -i "$1" -i assets/audio/soundtrack.wav \
    -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart -t "$DUR" "$2"
  rm -f "$1"
}

if [[ "${1:-}" == "--draft" ]]; then
  echo "==> draft render (30 fps)"
  $HF render --quality draft --fps 30 --output ../renders/_hf_draft.mp4
  remux ../renders/_hf_draft.mp4 ../renders/draft.mp4
  echo "draft: renders/draft.mp4"
  exit 0
fi

for fps in 60 30; do
  echo "==> render ${fps} fps"
  $HF render --quality high --fps "$fps" --output "../renders/_hf_${fps}.mp4"
  remux "../renders/_hf_${fps}.mp4" "../renders/${NAME}_${fps}fps.mp4"
done
cd ..

echo "==> covers"
ffmpeg -hide_banner -loglevel error -y -ss 0.4 -i "renders/${NAME}_60fps.mp4" -frames:v 1 renders/cover_hook.png
ffmpeg -hide_banner -loglevel error -y -ss 31.5 -i "renders/${NAME}_60fps.mp4" -frames:v 1 renders/cover_prix.png
ffmpeg -hide_banner -loglevel error -y -ss 36.9 -i "renders/${NAME}_60fps.mp4" -frames:v 1 renders/cover_fin_cta.png

echo "==> artifacts"
python3 scripts/write_artifacts.py

for f in "renders/${NAME}_60fps.mp4" "renders/${NAME}_30fps.mp4"; do
  d=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f")
  l=$(ffmpeg -hide_banner -i "$f" -af ebur128 -f null - 2>&1 | grep -A6 Summary | awk '/I:/{print $2}')
  echo "OK  $f  ${d}s  ${l} LUFS"
done
