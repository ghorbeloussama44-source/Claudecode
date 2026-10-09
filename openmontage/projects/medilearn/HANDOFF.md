# MediLearn — HTA explainer video — handoff notes

Client: MediLearn podcast (hypertension/HTA episode, ~17 min real recording).
Two presenters: "l'animateur" (homme) and "l'animatrice" (femme).

Read this before touching the project again — it captures techniques that
took real back-and-forth to get right, not just file locations.

## Where things stand

- **Topic 1 (0:00–5:00.7 of the real audio)** is done and delivered in two
  cuts, both committed:
  - `projects/medilearn/renders/tv_topic1_v1_compressed.mp4` — pure
    TV/podium layout (see below), full 5 min.
  - `projects/medilearn/renders/topic1_v2_dialogue_intro_plus_tv.mp4` —
    same thing but the first 30.2s is swapped for the earlier
    `dialogue_hta_30s_v4_cleanaudio.mp4` (real avatar-generated
    back-and-forth), then cuts straight into the TV layout. **This is the
    most recent / most-approved-direction cut.**
- **Topic 2+ (grading, etiology, treatment)** not started. The slide deck
  already has the matching pages ready: see "PDF deck map" below.
- The client wants real lip-sync eventually; everything so far is
  intentionally **not** lip-synced ("pas la peine de synchroniser pour un
  concept") — these are concept/structure passes.

## The TV/podium layout (current visual direction)

Client sent a reference photo of a TV mounted on a wood-slat wall, with a
circular presenter insert on the left and a slide panel on the right. The
ask was to replicate that layout, not just describe it.

- Reference photo: `projects/medilearn/assets/originals/tv_podium_reference.png`
  (1672×941, i.e. already ~16:9 — resized directly to 1280×720 with no
  crop needed, saved as `remotion-composer/public/medilearn/tv/podium_bg.jpg`).
- **Circle position was extracted, not eyeballed**: OpenCV
  `cv2.HoughCircles` on the reference photo found center (403, 419),
  radius 313 in source-image pixels. Scaled to the 1280×720 canvas:
  `CIRCLE = { cx: 308, cy: 321, r: 240 }` in
  `remotion-composer/src/components/MediLearnTV.tsx`. If you ever get a
  *new* reference photo, redo this — don't guess coordinates by eye, the
  gradient background defeats simple pixel-brightness scanning (tried
  that first, it doesn't work reliably on this kind of stylized image;
  Hough circle detection on a median-blurred grayscale does).
- Diapo (slide) panel rect, same canvas: `DIAPO = { left: 548, top: 65,
  width: 683, height: 559 }` — the area to the right of the circle,
  bounded by the screen bezel. Panel background `#1b252f` is sampled
  directly from the slide deck's own navy background so letterboxing
  (object-fit: contain) is invisible.

### Shot grammar (don't regress to one static layout)

The client explicitly asked for variety and iterated on it twice. Current
component `MediLearnTV.tsx` implements a **frame-driven lookup over three
independent timelines** (not nested `<Sequence>` trees — that got
unwieldy once shots, slides and speakers needed to vary independently):

1. `SLIDES` — which deck page is showing, keyed by script time range.
2. `TURNS` — which presenter (F/H) is speaking, keyed by script time
   range (see "speaker detection" below).
3. `SHOTS` — which visual treatment is on screen, keyed by time range,
   one of six kinds: `tv_duo`, `tv_solo_big` (pulsing big circle),
   `tv_duo_both` (both presenters, two pulsing circles), `diapo_full`
   (slide fills the frame, no presenter — voice-only beat), `diapo_pip`
   (full-screen slide + small corner circle), `avatar_wide` (the raw
   paid AI-avatar clip, full-bleed, its own different background — this
   is the "podium différent" variety beat, and it's free since it reuses
   clips already generated for the circles).

Each frame computes `activeAt(list, t)` against all three independently,
so a shot cut never has to coincide with a slide change or a speaker
change. **Hard rules the client stated explicitly, keep enforcing them:**
- The circle must always have a visible **blue** glow ring (`RING`
  constant in the component) — a plain white ring was rejected.
- Whenever the TV background is shown, the diapo panel (or an equivalent
  full cover) must ALSO be shown — never leave the reference photo's own
  placeholder art ("Les grands axes" mock content) exposed in a gap.
- Shot kind must never repeat back-to-back (cut variety).
- Cuts should land on turn boundaries, not mid-sentence.

### Speaker detection (no reliable diarization available)

`faster-whisper`'s `diarize=True` does **not** work in this environment
(returns `NO_SPEAKER` for everything — looks like a missing/ungated
pyannote dependency). Don't retry it. Instead: pitch (F0) classification
per transcribed line via `librosa.pyin`, threshold at ~165Hz (female
≈175–240Hz, male ≈90–145Hz in this specific recording — re-measure if
you get a new recording, voices differ). Reusable script:
`projects/medilearn/scripts/classify_speakers.py` — takes a list of
(start,end) line timestamps (from a `faster-whisper` transcript) and
prints per-line labels plus merged continuous turns. Topic 1's 41 turns
are already baked into `TURNS` in `MediLearnTV.tsx`; for topic 2+ you'll
need to run this again against that span's transcript.

### PDF deck map

Client-supplied deck: `projects/medilearn/assets/originals/Mastering_Hypertension_2024.pdf`
(15 pages, no extractable text — it's rendered/vector, rasterize with
`pymupdf` at 2x zoom). Rasterized + topic-1-relevant pages are already in
`remotion-composer/public/medilearn/slides/slide_0{1..4}.jpg`. Full page
map (from visual inspection, not yet all rasterized):

| Page | Content | Topic |
|---|---|---|
| 1 | "200/110 mmHg" title card | 1 (slide_01) |
| 2 | Mythe salle d'attente / AVC branching diagram | 1 (slide_02) |
| 3 | 24h dynamic BP graph + effet blouse blanche | 1 (slide_03) |
| 4 | Seuils ESC 2024 (140/90, 135/85, 130/80) + "pression élevée" | 1 (slide_04) |
| 5 | HTA Grade 1/2/3 thermometer | 2 |
| 6 | HTA primaire/essentielle vs secondaire (10-35%) | 2 |
| 7 | Mesures hygiéno-diététiques (fondation thérapeutique) | 2 or 3 |
| 8 | Arsenal pharmacologique (IEC/ARA-II/inhib.calciques/diurétiques) | 3 |
| 9–15 | not yet reviewed | ? |

To rasterize more pages: see `projects/medilearn/scripts/render_pdf_slides.py`.

### Topic boundaries found so far

Found by progressively transcribing larger chunks with `faster-whisper`
(`small`, `language='fr'`) and watching for a topical shift:
- Topic 1 "Qu'est-ce que l'HTA ?": 0:00 → 5:00.7 (ends right as the
  conversation pivots to grading). Full word-for-word transcript:
  `projects/medilearn/assets/originals/medilearn_script_sujet1.md`.
- Topic 2+ boundaries: not yet determined. Keep transcribing forward from
  5:00.7.

## Assets inventory (all committed, not regenerable without cost)

- `projects/medilearn/assets/originals/client_audio_17min.m4a` — the real
  17-minute recording. **Always mux the final audio track as one
  continuous, unedited slice of this file** — never per-segment audio
  from individual generated clips. The client caught and complained about
  "tu as enlevé un sens" (lost meaning) the one time segment-level audio
  was used; the fix was always re-extracting one continuous slice.
- `projects/medilearn/assets/originals/tv_podium_reference.png` — the TV
  layout reference photo.
- `projects/medilearn/assets/originals/Mastering_Hypertension_2024.pdf` —
  the slide deck.
- `projects/medilearn/assets/originals/reference_style_notebooklm.mp4` —
  an earlier visual-style reference (sketch/whiteboard look) — **superseded**
  by the TV/podium layout; keep for history but don't revert to it unless
  asked.
- `remotion-composer/public/medilearn/avatar/` — paid AI-avatar
  generations (Replicate `prunaai/p-video-avatar`, image+audio→video).
  `loop_femme.mp4` (~9.04s) / `loop_homme.mp4` (~5.04s) are the clips used
  for the circle insert AND for `avatar_wide` full-bleed shots.
  `seg_wide_femme.mp4` / `seg_homme_close.mp4` are earlier wide/close
  generations, still referenced from the older `MediLearnConcept.tsx`
  composition (now superseded by `MediLearnTV.tsx`, but kept, don't
  delete).
- `remotion-composer/public/medilearn/broll/` — free stock footage
  (Pexels/Pixabay), used only by the superseded `MediLearnConcept.tsx`.
- `projects/medilearn/renders/dialogue_hta_30s_v4_cleanaudio.mp4` — the
  client's favorite early test: a proper back-and-forth dialogue using
  the AI avatar clips with varied camera angles, covering exactly
  0:00–30.2s of the real script (verified by transcript match). Reused as
  the opening of `topic1_v2_dialogue_intro_plus_tv.mp4`.

## Gotchas worth not re-discovering

- **gitignore parent-directory exclusion**: `projects/` is ignored
  wholesale, with `!projects/medilearn/` etc. negation exceptions to
  re-include specific deliverables (mirrors the same pattern already
  used for `mahdia-festival`). `git check-ignore` / `git status` can
  still report a *new* file under there as ignored even when the
  negation pattern looks right, because of how git resolves nested
  negations under an excluded parent. Don't fight it — just
  `git add -f` the specific file; it stages fine and behaves like any
  normal tracked file afterward. Always add a new `!projects/medilearn/renders/<file>.mp4`
  line to `.gitignore` for each new deliverable you want to keep (same
  for `assets/originals/<file>`), otherwise the NEXT container reset
  loses it — this has actually happened before on this project.
- **Replicate billing**: creation requests are rate-limited to 6/min
  (burst 1) while account credit is under $5, and a `402 Insufficient
  credit` can persist even after the client says they added a payment
  card — only resolves once there's an actual usable balance. Don't
  silently retry in a loop; report the exact error and wait.
- **Avatar output aspect ratio** follows the INPUT IMAGE's aspect ratio,
  not a requested "16:9" — always source genuinely 16:9 reference images,
  then pad near-miss output (e.g. 1280×704) to 1280×720 with
  `ffmpeg -vf "pad=1280:720:0:8:black"` if needed.
- **SendUserFile 30MB limit**: re-encode with `-b:v 600k -maxrate 750k
  -bufsize 1500k -c:a aac -b:a 96k` gets a 5-minute 1280×720 video to
  ~25MB. Scale the bitrate down further for longer cuts.
- **Concatenating a paid avatar clip with a Remotion render**: use the
  `concat` filter (`-filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[outv]"`)
  after re-encoding both inputs to matching codec/fps/pix_fmt — don't
  trust `-c copy` concat demuxer across clips from different pipelines.
  Pick the cut point to land exactly on a frame boundary of the real
  audio (e.g. clip duration × fps = whole number) so the continuation's
  continuous-audio mux lines up with zero seam.

## Compositions in `remotion-composer/src/Root.tsx`

- `MediLearnConcept` — **superseded**, first draft (hand-drawn whiteboard
  cards + broll + small circle PiP). Kept for history, not the current
  direction.
- `MediLearnTV` — **current / active**. The TV/podium layout described
  above. 1280×720, 24fps, `durationInFrames={7217}` (= 300.7s, topic 1's
  length). When topic 2 is ready, either extend this composition's
  duration and append to `SLIDES`/`TURNS`/`SHOTS`, or start a sibling
  composition — check with the client's framing at the time ("une
  première vidéo complet pour concept" suggested topic-at-a-time delivery
  is fine).

## Quick commands to pick back up

```bash
cd /home/user/Claudecode/openmontage/remotion-composer

# Preview a single frame to sanity-check layout/timing changes fast
npx remotion still src/index.tsx MediLearnTV /tmp/preview.png --frame=960

# Full render (no audio — Remotion videos are muted on purpose, audio is
# always muxed separately from the one continuous real-audio source)
npx remotion render src/index.tsx MediLearnTV out/tv_full_novoice.mp4 --concurrency=4

# Mux the real continuous audio + compress for delivery
ffmpeg -ss 0 -t <duration> -i ../projects/medilearn/assets/originals/client_audio_17min.m4a \
  -i out/tv_full_novoice.mp4 -map 1:v -map 0:a \
  -c:v libx264 -preset veryfast -b:v 600k -maxrate 750k -bufsize 1500k \
  -c:a aac -b:a 96k -shortest out/tv_full_final.mp4
```
