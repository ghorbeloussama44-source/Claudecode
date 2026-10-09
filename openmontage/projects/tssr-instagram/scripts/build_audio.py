"""Build the 48 s soundtrack of the TSSR Instagram ad: bar-aligned music edit + timed SFX + loudness.

Music: Pixabay future bass track (assets/music/future_bass_upbeat.mp3, Pixabay Content License),
measured at 140.00 BPM (beat = 0.428571 s). Attacks sit ~14 ms before the librosa beat grid; every
cut is placed 10 ms before an attack so transients stay intact.

  video  0.000 - 34.847 <- track 11.459 - 46.306  build, drop 1 at video 4.000, breakdown from 31.429
  video 34.847 - 41.704 <- track 66.878 - 73.735  end of build 2, drop 2 at video 38.286 (call to action)
  video 41.704 - 48.000 <- track 94.306 - 100.602 last bars, final hit at video 45.143, tail

Video beat grid: B(n) = 4.0 + n * 0.428571 (n < 0 in the opening build).

Usage: python3 scripts/build_audio.py   (writes hyperframes/assets/audio/soundtrack.wav)
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
MUSIC_SRC = ROOT / "assets/music/future_bass_upbeat.mp3"
SFX_DIR = ROOT.parents[1] / ".agents/skills/hyperframes-media/assets/sfx"
OUT = ROOT / "hyperframes/assets/audio/soundtrack.wav"
SR = 48000
DURATION = 48.0
BEAT = 0.428571

SEGMENTS = [  # (video_start, track_start, length)
    (0.0, 11.459, 34.847),
    (34.847, 66.878, 6.857),
    (41.704, 94.306, 6.296),
]
XFADE = 0.008


def B(n: float) -> float:
    return 4.0 + n * BEAT


# (time in video, sfx file, gain dB, pan) -- time is when the sound's attack must land
CUES = [
    (0.10, "whoosh.mp3", -8, -0.3),          # photo push-in
    (B(-7), "pop.mp3", -6, 0.2),             # القراية
    (B(-6), "click.mp3", -2, 0.3),           # red box
    (3.62, "whoosh-short.mp3", -4, 0.6),     # flag stripes sweep
    (B(0), "impact-bass-1.mp3", -7, 0.0),    # drop 1 / card lands
    (B(1), "pop.mp3", -7, 0.2),              # حلمك
    (B(3), "sparkle.mp3", -9, -0.2),         # ممكن! swash + sparkles
    (B(7) - 0.05, "whoosh.mp3", -6, 0.0),    # iris to S3
    (B(12), "sparkle.mp3", -10, 0.1),        # star on the spire
    (B(16), "whoosh-short.mp3", -10, -0.4),  # orbit
    (B(24) - 0.2, "whoosh.mp3", -6, -0.5),   # card 1
    (B(25), "pop.mp3", -8, 0.0),             # طب
    (B(28) - 0.2, "whoosh.mp3", -7, -0.5),   # card 2
    (B(29), "pop.mp3", -8, 0.0),             # هندسة
    (B(32) - 0.2, "whoosh.mp3", -7, -0.5),   # card 3
    (B(33), "pop.mp3", -8, 0.0),             # إعلامية
    (B(36), "whoosh-short.mp3", -8, 0.0),    # deck collapses
    (B(37), "pop.mp3", -9, 0.3),             # وبرشا
    (B(40) - 0.15, "whoosh.mp3", -6, 0.4),   # to S5
    (B(44), "click.mp3", 0, 0.3),            # step 1
    (B(48), "click.mp3", 0, 0.3),            # step 2
    (B(48) + 0.3, "whoosh-short.mp3", -12, 0.5),  # plane
    (B(52), "click.mp3", 0, 0.3),            # step 3
    (B(56), "click.mp3", 0, 0.3),            # step 4
    (B(60), "chime.mp3", 4, 0.0),            # all ticked
    (B(64) - 0.3, "whoosh-cinematic.mp3", -12, 0.0),  # into the breakdown (peak ~2.4 s after attack)
    (B(67), "sparkle.mp3", -10, 0.2),        # red swash
    (B(80) - 3.45, "riser.mp3", -10, 0.0),   # build 2 -> CTA (peak ~3.3 s after start)
    (B(80), "impact-bass-2.mp3", -9, 0.0),   # drop 2 / logo slam
    (B(82), "pop.mp3", -6, 0.0),             # button
    (B(84), "click.mp3", 2, 0.2),            # tap
    (B(85), "click.mp3", -4, -0.1),          # tick 1
    (B(86), "click.mp3", -4, -0.1),          # tick 2
    (B(87), "click.mp3", -4, -0.1),          # tick 3
    (B(88), "pop.mp3", -8, 0.0),             # handle chip
    (B(96), "sparkle.mp3", -6, 0.0),         # final hit
    (B(96), "chime.mp3", 2, 0.0),
]
# measured attack position inside each file (s)
ATTACK = {"whoosh.mp3": 0.075, "whoosh-short.mp3": 0.075, "pop.mp3": 0.128, "click.mp3": 0.053,
          "impact-bass-1.mp3": 0.053, "impact-bass-2.mp3": 0.032, "sparkle.mp3": 0.032,
          "chime.mp3": 0.032, "whoosh-cinematic.mp3": 0.224, "riser.mp3": 0.0}


def load_stereo(path: Path) -> np.ndarray:
    y, _ = librosa.load(path, sr=SR, mono=False)
    if y.ndim == 1:
        y = np.vstack([y, y])
    return y.astype(np.float32)


def music_edit() -> np.ndarray:
    src = load_stereo(MUSIC_SRC)
    n_total = int(round(DURATION * SR))
    out = np.zeros((2, n_total), dtype=np.float32)
    nx = int(round(XFADE * SR))
    for i, (v0, t0, length) in enumerate(SEGMENTS):
        a = int(round((t0 - XFADE / 2) * SR))
        b = int(round((t0 + length + XFADE / 2) * SR))
        seg = src[:, max(0, a):b].copy()
        ramp = np.sqrt(np.linspace(0.0, 1.0, nx, dtype=np.float32))  # equal-power
        if i > 0:
            seg[:, :nx] *= ramp
        if i < len(SEGMENTS) - 1:
            seg[:, -nx:] *= ramp[::-1]
        d0 = int(round((v0 - XFADE / 2) * SR))
        lo = max(0, d0)
        seg = seg[:, lo - d0:]
        hi = min(n_total, lo + seg.shape[1])
        out[:, lo:hi] += seg[:, : hi - lo]
    fi = int(0.01 * SR)
    out[:, :fi] *= np.linspace(0, 1, fi, dtype=np.float32)
    fo = int(1.2 * SR)  # the track's own tail is already decaying; smooth the last 1.2 s
    out[:, -fo:] *= np.linspace(1, 0, fo, dtype=np.float32) ** 2
    return out


def place(bus: np.ndarray, clip: np.ndarray, at: float, gain_db: float, pan: float = 0.0) -> None:
    g = 10 ** (gain_db / 20)
    lg = g * np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
    rg = g * np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    s = int(round(at * SR))
    c = clip
    if s < 0:
        c, s = c[:, -s:], 0
    e = min(bus.shape[1], s + c.shape[1])
    bus[0, s:e] += c[0, : e - s] * lg
    bus[1, s:e] += c[1, : e - s] * rg


def loudnorm(src: Path, dst: Path, target: float = -14.0, tp: float = -1.5) -> None:
    first = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af",
         f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, check=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", first, re.S).group(0))
    af = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-af", af,
                    "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", str(dst)], check=True)


def main() -> None:
    music = music_edit()
    sfx = np.zeros_like(music)
    cache: dict[str, np.ndarray] = {}
    for at, name, gain, pan in CUES:
        if name not in cache:
            cache[name] = load_stereo(SFX_DIR / name)
        place(sfx, cache[name], at - ATTACK.get(name, 0.0), gain, pan)
    mix = 0.82 * music + 0.55 * sfx
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = OUT.with_name("_mix_raw.wav")
    sf.write(raw, mix.T, SR, subtype="PCM_24")
    loudnorm(raw, OUT)
    raw.unlink()
    print(f"{OUT.relative_to(ROOT)}: {DURATION:.1f} s, {len(CUES)} cues")


if __name__ == "__main__":
    main()
