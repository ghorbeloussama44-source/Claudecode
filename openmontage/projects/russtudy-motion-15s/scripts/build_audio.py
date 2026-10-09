"""Build the 15 s soundtrack: bar-aligned music edit + timed SFX layer + loudness.

Music: Pixabay "Funky" (11_funky.mp3), measured at 120.00 BPM (beat = 0.5 s,
fit residual ~4 ms). Attack transients sit ~18 ms before the librosa beat grid;
every cut is placed 10 ms before an attack so transients stay intact.

  video 0.0 - 9.0  <- track 15.026 - 24.026  (end of intro build, drop at video 1.0)
  video 9.0 - 15.0 <- track 60.025 - 66.025  (phrase end, final chord at video ~13.0)

Usage: python build_audio.py [--no-sfx]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
MUSIC_SRC = ROOT / "assets/music/candidates/11_funky.mp3"
SFX_DIR = ROOT.parents[1] / ".agents/skills/hyperframes-media/assets/sfx"
OUT_DIR = ROOT / "assets/audio"
SR = 48000
DURATION = 15.0

SEGMENTS = [  # (video_start, track_start, length)
    (0.0, 15.026, 9.0),
    (9.0, 60.025, 6.0),
]
XFADE = 0.008


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
        # take XFADE extra on both sides so neighbours can overlap
        a = int(round((t0 - XFADE / 2) * SR))
        b = int(round((t0 + length + XFADE / 2) * SR))
        seg = src[:, a:b].copy()
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
    # click-free head/tail
    fi = int(0.005 * SR)
    out[:, :fi] *= np.linspace(0, 1, fi, dtype=np.float32)
    fo = int(0.06 * SR)
    out[:, -fo:] *= np.linspace(1, 0, fo, dtype=np.float32) ** 2
    return out


def place(bus: np.ndarray, clip: np.ndarray, at: float, gain_db: float,
          fade_out: float | None = None, max_len: float | None = None,
          pan: float = 0.0, pan_to: float | None = None) -> None:
    """Mix `clip` into `bus` starting at `at` seconds (equal-power pan, optional auto-pan)."""
    c = clip.copy()
    if max_len is not None:
        c = c[:, : int(max_len * SR)]
    if fade_out:
        nf = min(c.shape[1], int(fade_out * SR))
        c[:, -nf:] *= np.linspace(1, 0, nf, dtype=np.float32) ** 2
    g = 10 ** (gain_db / 20)
    p = np.full(c.shape[1], pan, dtype=np.float32)
    if pan_to is not None:
        p = np.linspace(pan, pan_to, c.shape[1], dtype=np.float32)
    lg = g * np.cos((p + 1) * np.pi / 4) * np.sqrt(2)
    rg = g * np.sin((p + 1) * np.pi / 4) * np.sqrt(2)
    s = int(round(at * SR))
    if s < 0:
        c, lg, rg = c[:, -s:], lg[-s:], rg[-s:]
        s = 0
    e = min(bus.shape[1], s + c.shape[1])
    n = e - s
    bus[0, s:e] += c[0, :n] * lg[:n]
    bus[1, s:e] += c[1, :n] * rg[:n]


# ---------------------------------------------------------------- synthesized SFX
def _env(n: int, tau: float) -> np.ndarray:
    return np.exp(-np.arange(n) / (tau * SR)).astype(np.float32)


def tick(freq: float = 2200.0, tau: float = 0.004, noise: float = 0.7, rng=None) -> np.ndarray:
    """Short plastic click: high-passed noise burst + damped sine."""
    rng = rng or np.random.default_rng(0)
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    nz = rng.standard_normal(n).astype(np.float32)
    nz = np.diff(nz, prepend=0.0)  # crude high-pass
    sig = noise * nz * _env(n, tau * 0.6) + np.sin(2 * np.pi * freq * t) * _env(n, tau)
    return (sig / (np.abs(sig).max() + 1e-9)).astype(np.float32)


def sweep(f0: float, f1: float, dur: float, shape: str = "exp") -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, 1, n, dtype=np.float32)
    f = f0 * (f1 / f0) ** t if shape == "exp" else f0 + (f1 - f0) * t
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph).astype(np.float32)


def pulse(freq: float, dur: float, duty: float = 0.25) -> np.ndarray:
    n = int(dur * SR)
    ph = (np.arange(n) * freq / SR) % 1.0
    return np.where(ph < duty, 1.0, -1.0).astype(np.float32)


def bezier_ease(segs, x: np.ndarray) -> np.ndarray:
    """Evaluate a GSAP CustomEase made of cubic segments at progress x."""
    s = np.linspace(0, 1, 2000)
    xs, ys = [], []
    for p0, p1, p2, p3 in segs:
        b = lambda a, k: ((1 - s) ** 3 * a[k] + 3 * (1 - s) ** 2 * s * p1[k] + 3 * (1 - s) * s ** 2 * p2[k] + s ** 3 * p3[k])
        xs.append(b(p0, 0)); ys.append(b(p0, 1))
    return np.interp(x, np.concatenate(xs), np.concatenate(ys))


ODO_ROLL = [((0, 0), (0.08, 0.42), (0.24, 0.86), (0.5, 0.97)),
            ((0.5, 0.97), (0.7, 1.01), (0.86, 1.003), (1, 1))]


def ticks_at(times, freqs, gains, length: float, rng_seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(rng_seed)
    out = np.zeros(int(length * SR) + SR // 10, dtype=np.float32)
    for t, f, g in zip(times, freqs, gains):
        c = tick(f, rng=rng) * g
        i = int(t * SR)
        out[i:i + len(c)] += c[: max(0, len(out) - i)]
    return out


def synth_all(sfx_dir: Path) -> None:
    sfx_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)

    def save(name, mono, peak_db=-1.0):
        mono = mono / (np.abs(mono).max() + 1e-9) * 10 ** (peak_db / 20)
        sf.write(sfx_dir / f"{name}.wav", np.vstack([mono, mono]).T, SR, subtype="FLOAT")

    # reel ratchet: one click per block crossing the window (20 blocks/s), plus a soft whirr
    times = np.arange(20) * 0.05
    spin = ticks_at(times, 1900 + rng.uniform(-120, 120, 20), rng.uniform(0.7, 1.0, 20), 1.0, 11)
    n = len(spin)
    whirr = np.convolve(rng.standard_normal(n), np.ones(24) / 24, mode="same").astype(np.float32)
    whirr = np.diff(whirr, prepend=0) * (0.5 + 0.5 * np.sin(2 * np.pi * 20 * np.arange(n) / SR))
    fade = np.clip(1 - np.arange(n) / (0.98 * SR), 0, 1)
    save("reel_spin", spin + 0.35 * whirr / (np.abs(whirr).max() + 1e-9) * fade)
    save("tick", tick(2000, rng=rng))

    # odometer: a click every time any digit column crosses a digit (decelerating roll)
    t0, land = 3.4, [3.86, 3.91, 3.96, 4.0]
    target = [2, 2, 0, 0]
    tt, ff = [], []
    for i in range(4):
        a, b = 3 + i * 2, 20 + target[i] + (i % 2) * 10
        x = np.linspace(0, 1, 4000)
        pos = a + (b - a) * bezier_ease(ODO_ROLL, x)
        crossings = np.where(np.diff(np.floor(pos)) > 0)[0]
        tt += list(x[crossings] * (land[i] - t0))
        ff += [2600 + i * 180] * len(crossings)
    order = np.argsort(tt)
    save("odo_ticks", ticks_at(np.array(tt)[order], np.array(ff)[order], np.full(len(tt), 0.8), 0.7, 21))

    # counters (+1 200 then 40+): power2.out, a click every 60 / every 2 units
    def counter(total, step, dur, f_lo, f_hi, seed):
        v = np.arange(step, total + 1, step)
        p = 1 - np.sqrt(1 - v / total)
        return ticks_at(p * dur, np.linspace(f_lo, f_hi, len(v)), np.linspace(0.6, 1.0, len(v)), dur, seed)

    save("count_a", counter(1200, 60, 0.6, 1700, 2500, 31))
    save("count_b", counter(40, 2, 0.5, 1800, 2700, 41))

    # 8-bit arpeggio for the pixel dissolve (A major, matches the track)
    notes = [880.0, 1108.73, 1318.51, 1760.0, 2217.46, 2637.02, 2217.46, 1760.0]
    arp = []
    for k, f in enumerate(notes):
        d = 0.042 if k < 6 else 0.05
        nn = pulse(f, d) * (np.exp(-np.arange(int(d * SR)) / (0.03 * SR)))
        arp.append(nn * (1.0 if k < 6 else 0.55))
    save("pixel_arp", np.concatenate(arp).astype(np.float32), -3.0)

    # dot: squash "bloop", flight "fwip", URL typing ticks
    save("bloop", sweep(560, 240, 0.11) * _env(int(0.11 * SR), 0.05))
    fw = sweep(240, 1500, 0.27)
    fw *= np.linspace(0.2, 1.0, len(fw)) ** 1.5
    fw += 0.25 * np.diff(rng.standard_normal(len(fw)), prepend=0).astype(np.float32) * np.linspace(0, 1, len(fw))
    save("fwip", fw.astype(np.float32), -2.0)
    save("url_ticks", ticks_at(np.arange(16) * 0.022, 1300 + rng.uniform(-150, 150, 16), rng.uniform(0.5, 0.9, 16), 0.4, 51))


def sfx_layer(cues: list[dict]) -> np.ndarray:
    n_total = int(round(DURATION * SR))
    bus = np.zeros((2, n_total), dtype=np.float32)
    cache: dict[str, np.ndarray] = {}
    for cue in cues:
        name = cue["sfx"]
        if name not in cache:
            p = OUT_DIR / "sfx" / f"{name}.wav"
            if not p.exists():
                p = SFX_DIR / f"{name}.mp3"
            cache[name] = load_stereo(p)
        clip = cache[name]
        if cue.get("offset"):
            clip = clip[:, int(cue["offset"] * SR):]
        if cue.get("rate", 1.0) != 1.0:
            # varispeed (pitch + time) by resampling, used to tune tonal SFX to the track key
            clip = librosa.resample(clip, orig_sr=SR, target_sr=int(round(SR / cue["rate"])))
        # `lead` is the peak/attack offset in source-file seconds (after `offset`); it scales with varispeed
        lead = cue.get("lead", 0.0) / cue.get("rate", 1.0)
        place(bus, clip, cue["at"] - lead, cue.get("gain_db", -12.0),
              cue.get("fade_out"), cue.get("max_len"), cue.get("pan", 0.0), cue.get("pan_to"))
    return bus


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    music = music_edit()
    sf.write(OUT_DIR / "music_edit.wav", music.T, SR, subtype="PCM_24")
    # the band stops at 13.0 and only a quiet E chord rings: lift it +14 dB so the ending stays full
    g = np.ones(music.shape[1], dtype=np.float32)
    i0, i1 = int(13.02 * SR), int(13.12 * SR)
    g[i0:i1] = np.linspace(1.0, 10 ** (14 / 20), i1 - i0)
    g[i1:] = 10 ** (14 / 20)
    music = music * g[None, :]
    mix = music.copy()
    cues_path = ROOT / "artifacts/sfx_cues.json"
    if "--no-sfx" not in sys.argv and cues_path.exists():
        synth_all(OUT_DIR / "sfx")
        cues = json.loads(cues_path.read_text())["cues"]
        sfx = sfx_layer(cues)
        sf.write(OUT_DIR / "sfx_layer.wav", sfx.T, SR, subtype="PCM_24")
        # duck the music bed (max 3 dB) under the SFX envelope so accents read without being loud
        env = np.abs(sfx).max(axis=0)
        win = int(0.03 * SR)
        env = np.convolve(env, np.ones(win) / win, mode="same")
        rel = np.exp(-1.0 / (0.12 * SR))
        sm = np.empty_like(env)
        acc = 0.0
        for i, v in enumerate(env):  # fast attack, 120 ms release
            acc = v if v > acc else acc * rel + v * (1 - rel)
            sm[i] = acc
        duck_db = -3.0 * np.clip(sm / 0.25, 0, 1)
        mix = music * (10 ** (duck_db / 20))[None, :] + sfx
    raw = OUT_DIR / "mix_raw.wav"
    sf.write(raw, mix.T, SR, subtype="FLOAT")
    # gain-stage then brick-wall limit (lookahead) so loudnorm can stay linear (no pumping)
    pre = OUT_DIR / "mix_premaster.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw), "-af",
         "volume=-2dB,alimiter=limit=0.82:attack=4:release=60:level=disabled:latency=1", "-c:a", "pcm_f32le", str(pre)],
        check=True,
    )
    # social loudness target: -14 LUFS integrated, -1 dBTP (two-pass loudnorm)
    probe = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(pre), "-af",
         "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    stats = json.loads(probe[probe.rfind("{"):])
    final = OUT_DIR / "soundtrack.wav"
    norm = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(pre), "-af",
         "loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:"
         f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
         f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
         f"offset={stats['target_offset']}:print_format=json,aresample=48000",
         "-c:a", "pcm_s16le", "-t", f"{DURATION}", str(final)],
        check=True, capture_output=True, text=True,
    ).stderr
    norm_type = json.loads(norm[norm.rfind("{"):]).get("normalization_type") if "{" in norm else "n/a"
    check = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(final), "-af",
         "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    out = json.loads(check[check.rfind("{"):])
    print(json.dumps({"premaster_lufs": stats["input_i"], "premaster_tp": stats["input_tp"],
                      "final_lufs": out["input_i"], "final_tp": out["input_tp"], "normalization": norm_type,
                      "output": str(final)}, indent=1))


if __name__ == "__main__":
    main()
