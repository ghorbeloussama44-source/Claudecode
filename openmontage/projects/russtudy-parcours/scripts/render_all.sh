#!/usr/bin/env bash
# One-command rebuild of the RusStudy "Le parcours" spot (40 s) after a retouch:
#   audio (music edit + SFX cues) -> 16:9 version regenerated from the vertical master ->
#   lint -> render 9:16 60 fps + 30 fps and YouTube 16:9 60 fps -> remux the exact master
#   audio -> cover frames + YouTube thumbnail -> refresh OpenMontage artifacts.
#
# Usage:  bash scripts/render_all.sh             (full: audio + all renders)
#         bash scripts/render_all.sh --draft     (fast 30 fps 9:16 draft, renders/draft.mp4)
#         bash scripts/render_all.sh --draft16   (fast 30 fps 16:9 draft, renders/draft_16x9.mp4)
set -euo pipefail
cd "$(dirname "$0")/.."
HF="npx --yes hyperframes@0.8.133"   # pinned: the folder is named "hyperframes", a bare npx resolves the local package
DUR=40
NAME=russtudy_parcours_40s
NAME16=russtudy_parcours_40s_youtube_16x9

python3 -c "import librosa, soundfile, scipy, jsonschema" 2>/dev/null || pip install -q -r scripts/requirements.txt

echo "==> soundtrack"
python3 scripts/build_audio.py
cp assets/audio/soundtrack.wav hyperframes/assets/audio/soundtrack.wav

echo "==> 16:9 version (generated from hyperframes/index.html)"
python3 scripts/make_landscape.py

(cd hyperframes && $HF browser ensure >/dev/null)
echo "==> lint"
(cd hyperframes && $HF lint)
(cd hyperframes-16x9 && $HF lint)

render() { # $1 = project dir, $2 = fps, $3 = quality, $4 = final file (relative to the project root)
  (cd "$1" && $HF render --quality "$3" --fps "$2" --output "../renders/_hf_tmp.mp4")
  # HyperFrames' own audio pass lands ~1.4 dB under target: swap in the exact master
  ffmpeg -hide_banner -loglevel error -y -i renders/_hf_tmp.mp4 -i hyperframes/assets/audio/soundtrack.wav \
    -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart -t "$DUR" "$4"
  rm -f renders/_hf_tmp.mp4
}

case "${1:-}" in
  --draft)
    render hyperframes 30 draft renders/draft.mp4
    echo "draft: renders/draft.mp4"
    exit 0 ;;
  --draft16)
    render hyperframes-16x9 30 draft renders/draft_16x9.mp4
    echo "draft: renders/draft_16x9.mp4"
    exit 0 ;;
esac

for fps in 60 30; do
  echo "==> render 9:16 ${fps} fps"
  render hyperframes "$fps" high "renders/${NAME}_${fps}fps.mp4"
done
echo "==> render 16:9 60 fps (YouTube)"
render hyperframes-16x9 60 high "renders/${NAME16}_60fps.mp4"

echo "==> covers"
frame() { ffmpeg -hide_banner -loglevel error -y -ss "$2" -i "$1" -frames:v 1 "$3"; }
frame "renders/${NAME}_60fps.mp4" 0.4 renders/cover_hook.png
frame "renders/${NAME}_60fps.mp4" 25.2 renders/cover_transfert.png
frame "renders/${NAME}_60fps.mp4" 35.5 renders/cover_prix.png
frame "renders/${NAME}_60fps.mp4" 39.9 renders/cover_fin_cta.png
frame "renders/${NAME16}_60fps.mp4" 25.2 renders/cover_16x9_transfert.png
frame "renders/${NAME16}_60fps.mp4" 35.5 renders/cover_16x9_prix.png
frame "renders/${NAME16}_60fps.mp4" 39.9 renders/cover_16x9_fin_cta.png
# YouTube custom thumbnail: 1280x720 JPEG (< 2 MB)
ffmpeg -hide_banner -loglevel error -y -i renders/cover_16x9_prix.png -vf scale=1280:720:flags=lanczos -q:v 2 renders/thumbnail_youtube.jpg

echo "==> artifacts"
python3 scripts/write_artifacts.py

for f in "renders/${NAME}_60fps.mp4" "renders/${NAME}_30fps.mp4" "renders/${NAME16}_60fps.mp4"; do
  d=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f")
  r=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$f")
  l=$(ffmpeg -hide_banner -i "$f" -af ebur128 -f null - 2>&1 | grep -A6 Summary | awk '/I:/{print $2}')
  echo "OK  $f  ${r}  ${d}s  ${l} LUFS"
done
