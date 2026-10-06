#!/usr/bin/env bash
# One-command rebuild of the RusStudy "Le parcours" spot after a retouch.
#   40 s (default): audio (music edit + SFX cues) -> 16:9 version regenerated from the
#     vertical master -> lint -> render 9:16 60 fps + 30 fps and YouTube 16:9 60 fps ->
#     remux the exact master audio -> cover frames + YouTube thumbnail -> OpenMontage artifacts.
#   60 s (--60s): the same film played 1.5x slower (scripts/make_slow.py) on its own 60 s
#     soundtrack (build_audio.py --slow), in French and in Tunisian Arabic (derja, generated from
#     the French compositions by scripts/make_arabic.py) -> render the four 60 s versions
#     (9:16 + 16:9, 60 fps) -> covers + YouTube thumbnails.
#
# Usage:  bash scripts/render_all.sh             (40 s: audio + all renders)
#         bash scripts/render_all.sh --60s       (60 s versions, French + derja, 9:16 + 16:9)
#         bash scripts/render_all.sh --draft     (fast 30 fps 9:16 draft, renders/draft.mp4)
#         bash scripts/render_all.sh --draft16   (fast 30 fps 16:9 draft, renders/draft_16x9.mp4)
set -euo pipefail
cd "$(dirname "$0")/.."
HF="npx --yes hyperframes@0.8.133"   # pinned: the folder is named "hyperframes", a bare npx resolves the local package
MODE="${1:-}"
NAME=russtudy_parcours_40s
NAME16=russtudy_parcours_40s_youtube_16x9
NAME60=russtudy_parcours_60s
NAME60_16=russtudy_parcours_60s_youtube_16x9
NAME60_AR=russtudy_parcours_60s_derja
NAME60_AR16=russtudy_parcours_60s_derja_youtube_16x9

python3 -c "import librosa, soundfile, scipy, jsonschema" 2>/dev/null || pip install -q -r scripts/requirements.txt

render() { # $1 = project dir, $2 = fps, $3 = quality, $4 = final file, $5 = duration (s)
  (cd "$1" && $HF render --quality "$3" --fps "$2" --output "../renders/_hf_tmp.mp4")
  # HyperFrames' own audio pass lands ~1.4 dB under target: swap in the exact master
  ffmpeg -hide_banner -loglevel error -y -i renders/_hf_tmp.mp4 -i "$1/assets/audio/soundtrack.wav" \
    -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart -t "$5" "$4"
  rm -f renders/_hf_tmp.mp4
}

frame() { ffmpeg -hide_banner -loglevel error -y -ss "$2" -i "$1" -frames:v 1 "$3"; }
covers() { # $1 = 9:16 render, $2 = 16:9 render, $3 = file prefix ("" or "ar_"), $4 = time scale (1 = 40 s, 1.5 = 60 s)
  local k="$4"
  ts() { awk -v t="$1" -v k="$k" 'BEGIN { printf "%.3f", t * k }'; }
  frame "$1" "$(ts 0.4)" "renders/cover_${3}hook.png"
  frame "$1" "$(ts 25.2)" "renders/cover_${3}transfert.png"
  frame "$1" "$(ts 35.5)" "renders/cover_${3}prix.png"
  frame "$1" "$(ts 39.9)" "renders/cover_${3}fin_cta.png"
  frame "$2" "$(ts 25.2)" "renders/cover_${3}16x9_transfert.png"
  frame "$2" "$(ts 35.5)" "renders/cover_${3}16x9_prix.png"
  frame "$2" "$(ts 39.9)" "renders/cover_${3}16x9_fin_cta.png"
  # YouTube custom thumbnail: 1280x720 JPEG (< 2 MB)
  ffmpeg -hide_banner -loglevel error -y -i "renders/cover_${3}16x9_prix.png" -vf scale=1280:720:flags=lanczos -q:v 2 "renders/thumbnail_youtube${3:+_${3%_}}.jpg"
}

report() {
  for f in "$@"; do
    d=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f")
    r=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$f")
    l=$(ffmpeg -hide_banner -i "$f" -af ebur128 -f null - 2>&1 | grep -A6 Summary | awk '/I:/{print $2}')
    echo "OK  $f  ${r}  ${d}s  ${l} LUFS"
  done
}

if [[ "$MODE" == "--60s" ]]; then
  echo "==> soundtrack 60 s"
  python3 scripts/build_audio.py --slow
  echo "==> 60 s versions (generated from the 40 s compositions): French + derja, 9:16 + 16:9"
  python3 scripts/make_landscape.py
  python3 scripts/make_arabic.py
  python3 scripts/make_slow.py
  (cd hyperframes-60s && $HF browser ensure >/dev/null)
  echo "==> lint"
  for d in hyperframes-60s hyperframes-60s-16x9 hyperframes-ar-60s hyperframes-ar-60s-16x9; do (cd "$d" && $HF lint); done
  echo "==> render 60 fps (60 s): French 9:16, French 16:9, derja 9:16, derja 16:9"
  render hyperframes-60s 60 high "renders/${NAME60}_60fps.mp4" 60
  render hyperframes-60s-16x9 60 high "renders/${NAME60_16}_60fps.mp4" 60
  render hyperframes-ar-60s 60 high "renders/${NAME60_AR}_60fps.mp4" 60
  render hyperframes-ar-60s-16x9 60 high "renders/${NAME60_AR16}_60fps.mp4" 60
  echo "==> covers"
  covers "renders/${NAME60}_60fps.mp4" "renders/${NAME60_16}_60fps.mp4" "" 1.5
  covers "renders/${NAME60_AR}_60fps.mp4" "renders/${NAME60_AR16}_60fps.mp4" "ar_" 1.5
  echo "==> artifacts"
  python3 scripts/write_artifacts.py
  report "renders/${NAME60}_60fps.mp4" "renders/${NAME60_16}_60fps.mp4" "renders/${NAME60_AR}_60fps.mp4" "renders/${NAME60_AR16}_60fps.mp4"
  exit 0
fi

echo "==> soundtrack"
python3 scripts/build_audio.py
cp assets/audio/soundtrack.wav hyperframes/assets/audio/soundtrack.wav

echo "==> 16:9 version (generated from hyperframes/index.html)"
python3 scripts/make_landscape.py

(cd hyperframes && $HF browser ensure >/dev/null)
echo "==> lint"
(cd hyperframes && $HF lint)
(cd hyperframes-16x9 && $HF lint)

case "$MODE" in
  --draft)
    render hyperframes 30 draft renders/draft.mp4 40
    echo "draft: renders/draft.mp4"
    exit 0 ;;
  --draft16)
    render hyperframes-16x9 30 draft renders/draft_16x9.mp4 40
    echo "draft: renders/draft_16x9.mp4"
    exit 0 ;;
esac

for fps in 60 30; do
  echo "==> render 9:16 ${fps} fps"
  render hyperframes "$fps" high "renders/${NAME}_${fps}fps.mp4" 40
done
echo "==> render 16:9 60 fps (YouTube)"
render hyperframes-16x9 60 high "renders/${NAME16}_60fps.mp4" 40

echo "==> covers"
covers "renders/${NAME}_60fps.mp4" "renders/${NAME16}_60fps.mp4" "" 1

echo "==> artifacts"
python3 scripts/write_artifacts.py

report "renders/${NAME}_60fps.mp4" "renders/${NAME}_30fps.mp4" "renders/${NAME16}_60fps.mp4"
