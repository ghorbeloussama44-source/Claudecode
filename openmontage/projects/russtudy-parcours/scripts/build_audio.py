"""Build the 40 s "parcours" soundtrack: bar-aligned music edit + timed SFX + loudness.

Music: Pixabay "Funky" (11_funky.mp3), measured at 120.00 BPM (beat = 0.5 s).
Attack transients sit ~18 ms before the librosa beat grid; every cut is placed
~10 ms before an attack so transients stay intact.

  video  0 - 17 <- track 15.026 - 32.026  (end of build, drop A at video 1.0, groove)
  video 17 - 35 <- track 76.025 - 94.025  (drum break 17, bass build 19, drop B at 21, groove)
  video 35 - 40 <- track 62.025 - 67.025  (fill, band stops on an E chord at video 37.0)

--slow builds the 60 s version (scripts/make_slow.py: the same film played 1.5x slower).
Every SFX cue time and every synthesized timing is multiplied by K = 1.5; the music keeps
its tempo and is re-edited so the big moments still land on downbeats (x 1.5):
  video  0   - 25.5 <- track 14.526 - 40.026  (drop A at video 1.5, groove)
  video 25.5 - 53.5 <- track 74.025 - 102.025 (2 bars of drum break, bass build 29.5, drop B 31.5)
  video 53.5 - 60   <- track 62.025 - 68.525  (fill, band stops on the E chord at video 55.5)

Usage: python build_audio.py [--no-sfx] [--slow]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parents[1]
MUSIC_SRC = ROOT / "assets/music/11_funky.mp3"
SFX_DIR = ROOT.parents[1] / ".agents/skills/hyperframes-media/assets/sfx"
SLOW = "--slow" in sys.argv
K = 1.5 if SLOW else 1.0  # time scale of the slow (60 s) version
OUT_DIR = ROOT / ("assets/audio-60s" if SLOW else "assets/audio")
SR = 48000
DURATION = 40.0 * K

SEGMENTS = [  # (video_start, track_start, length)
    (0.0, 15.026, 17.0),
    (17.0, 76.025, 18.0),
    (35.0, 62.025, 5.0),
]
if SLOW:
    SEGMENTS = [(0.0, 14.526, 25.5), (25.5, 74.025, 28.0), (53.5, 62.025, 6.5)]
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


def mulberry32(a: int):
    """Same PRNG as the composition (JS), so synthesized events match the visuals."""
    state = [a & 0xFFFFFFFF]

    def rnd() -> float:
        state[0] = (state[0] + 0x6D2B79F5) & 0xFFFFFFFF
        t = state[0]
        t = ((t ^ (t >> 15)) * (1 | t)) & 0xFFFFFFFF
        t = ((t + (((t ^ (t >> 7)) * (61 | t)) & 0xFFFFFFFF)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return rnd


def bandnoise(n: int, lo: float, hi: float, rng, order: int = 2) -> np.ndarray:
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, rng.standard_normal(n)).astype(np.float32)


def lownoise(n: int, fc: float, rng, order: int = 2) -> np.ndarray:
    sos = signal.butter(order, fc, btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, rng.standard_normal(n)).astype(np.float32)


def env_ad(n: int, a: float, d: float) -> np.ndarray:
    t = np.arange(n) / SR
    return np.where(t < a, t / max(a, 1e-4), np.exp(-(t - a) / d)).astype(np.float32)


def norm(x: np.ndarray) -> np.ndarray:
    return (x / (np.abs(x).max() + 1e-9)).astype(np.float32)


def add_at(out: np.ndarray, clip: np.ndarray, t: float, g: float = 1.0) -> None:
    i = int(round(t * SR))
    n = min(len(clip), len(out) - i)
    if n > 0:
        out[i:i + n] += clip[:n] * g


def tone(freq: float, dur: float, partials=((1, 1.0),), a: float = 0.003, d: float = 0.08) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(g * np.sin(2 * np.pi * freq * k * t) for k, g in partials)
    return (x * env_ad(n, a, d)).astype(np.float32)


def thud(f0: float = 110, f1: float = 55, dur: float = 0.22, rng=None) -> np.ndarray:
    rng = rng or np.random.default_rng(3)
    n = int(dur * SR)
    body = sweep(f0, f1, dur) * env_ad(n, 0.002, 0.06)
    click = lownoise(n, 900, rng) * env_ad(n, 0.0005, 0.006)
    return norm(body + 0.6 * norm(click))


def paper(rng) -> np.ndarray:
    n = int(0.16 * SR)
    a = bandnoise(n, 900, 6500, rng) * env_ad(n, 0.003, 0.03)
    b = np.zeros(n, dtype=np.float32)
    add_at(b, bandnoise(int(0.08 * SR), 1200, 5000, rng) * env_ad(int(0.08 * SR), 0.002, 0.02), 0.028, 0.5)
    return norm(norm(a) + b + 0.25 * tone(140, 0.16, d=0.04))


def shuffle(rng, dur: float = 0.34) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    hi = bandnoise(n, 2000, 6000, rng)
    lo = bandnoise(n, 600, 2200, rng)
    x = norm(hi) * (1 - t / dur) + norm(lo) * (t / dur)
    flutter = 0.55 + 0.45 * norm(lownoise(n, 40, rng)) ** 2
    shape = np.minimum(1, t / 0.06) * np.minimum(1, (dur - t) / 0.12)
    return norm(x * flutter * shape)


def rip(rng) -> np.ndarray:
    """Paper tear: a crackle of micro-bursts over a hissing bed."""
    dur = 0.46
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    for _ in range(90):
        u = rng.beta(1.6, 2.4) * 0.38
        m = int(0.012 * SR)
        add_at(out, bandnoise(m, 1500, 7500, rng) * env_ad(m, 0.0004, 0.003 + 0.004 * rng.random()), u, 0.4 + 0.6 * rng.random())
    t = np.arange(n) / SR
    bed = bandnoise(n, 2500, 7000, rng) * np.minimum(1, t / 0.05) * np.exp(-np.maximum(0, t - 0.3) / 0.05)
    return norm(norm(out) + 0.35 * norm(bed))


def stamp(rng) -> np.ndarray:
    n = int(0.26 * SR)
    x = thud(160, 70, 0.26, rng)
    x += 0.7 * norm(bandnoise(n, 300, 2600, rng)) * env_ad(n, 0.0005, 0.012)
    tk = tick(3000, rng=rng)
    x[: len(tk)] += 0.25 * tk
    return norm(x)


def slap(rng) -> np.ndarray:
    n = int(0.22 * SR)
    hiss = signal.sosfilt(signal.butter(2, 900, btype="high", fs=SR, output="sos"), rng.standard_normal(n))
    return norm(norm(hiss * env_ad(n, 0.0005, 0.014)) + 0.6 * thud(130, 60, 0.22, rng))


def jet(rng, dur: float = 1.9) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    low = norm(lownoise(n, 350, rng, 3))
    high = norm(bandnoise(n, 900, 3200, rng))
    mix = np.clip((t - 0.2) / 1.3, 0, 1)
    whine = sweep(1700, 2700, dur) * 0.1
    shape = np.minimum(1, t / 0.55) ** 2 * np.minimum(1, (dur - t) / 0.45)
    return norm((low * (1 - 0.6 * mix) + high * mix * 0.8 + whine) * shape)


def bell(freq: float, dur: float = 1.4) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k, g, d in ((1, 1.0, 0.9), (2.0, 0.45, 0.5), (3.0, 0.22, 0.3), (4.2, 0.12, 0.18)):
        x += g * np.sin(2 * np.pi * freq * k * t) * np.exp(-t / d)
    return (x * np.minimum(1, t / 0.003)).astype(np.float32)


def wind(rng, dur: float = 4.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = norm(lownoise(n, 600, rng, 3)) + 0.3 * norm(bandnoise(n, 800, 1700, rng))
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * t + 1.2)
    shape = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.6)
    return norm(x * lfo * shape)


def riser(rng, dur: float = 2.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    lo, hi = norm(bandnoise(n, 400, 1100, rng)), norm(bandnoise(n, 2000, 6500, rng))
    p = t / dur
    x = lo * (1 - p) + hi * p + 0.5 * sweep(220, 880, dur)
    shape = p ** 2.5 * np.minimum(1, (dur - t) / 0.02)
    return norm(x * shape)


def horn(dur: float = 0.95) -> np.ndarray:
    """Two-blast train horn on an A major chord (in key with the track)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
    x = np.zeros(n)
    for f in (220.0, 277.18, 329.63):
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        x += np.sign(np.sin(ph)) * 0.5 + np.sin(ph)  # reedy square + fundamental
    x = signal.sosfilt(signal.butter(2, 2400, btype="low", fs=SR, output="sos"), x)
    blast = lambda a, b: np.clip((t - a) / 0.04, 0, 1) * np.clip((b - t) / 0.08, 0, 1)
    return norm(x * (blast(0.0, 0.36) + blast(0.46, dur)))


def synth_all(sfx_dir: Path) -> None:
    sfx_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)

    def save(name, mono, peak_db=-1.0):
        mono = mono / (np.abs(mono).max() + 1e-9) * 10 ** (peak_db / 20)
        sf.write(sfx_dir / f"{name}.wav", np.vstack([mono, mono]).T, SR, subtype="FLOAT")

    save("tick", tick(2000, rng=rng))
    # phone keyboard: one tap per character of "Salam ! Je veux étudier en Russie." (34 chars in 0.72 s)
    taps = np.zeros(int(0.9 * K * SR), dtype=np.float32)
    for k in range(1, 35):
        tap = tick(1600 + rng.uniform(0, 800), tau=0.003, noise=0.5, rng=rng) + 0.5 * tone(230, 0.03, d=0.008)
        add_at(taps, tap, 0.72 * K * k / 34, rng.uniform(0.5, 0.9))
    save("kb_typing", taps)
    # UI: call connected (A5 -> E6), profile scan sweep, card-reader beep (E6 -> A6)
    con = np.zeros(int(0.3 * SR), dtype=np.float32)
    add_at(con, tone(880, 0.07, d=0.03), 0.0)
    add_at(con, tone(1318.51, 0.11, d=0.05), 0.085)
    save("connect", con, -3.0)
    sc = sweep(600, 1300, 0.42 * K) * (0.5 + 0.5 * np.sin(2 * np.pi * 28 * np.arange(int(0.42 * K * SR)) / SR))
    sc *= np.minimum(1, np.arange(len(sc)) / (0.08 * SR)) * np.minimum(1, (len(sc) - np.arange(len(sc))) / (0.05 * SR))
    save("scan", sc.astype(np.float32), -6.0)
    bp = np.zeros(int(0.3 * SR), dtype=np.float32)
    add_at(bp, tone(1318.51, 0.075, ((1, 1.0), (3, 0.3)), d=0.2) * np.minimum(1, (0.075 * SR - np.arange(int(0.075 * SR))) / 400), 0.0)
    add_at(bp, tone(1760.0, 0.12, ((1, 1.0), (3, 0.3)), d=0.2) * np.minimum(1, (0.12 * SR - np.arange(int(0.12 * SR))) / 600), 0.11)
    save("beep2", bp, -3.0)
    # paper / folder / stamps
    save("paper", paper(rng))
    save("shuffle", shuffle(rng))
    save("thud", thud(110, 55, 0.22, rng))
    save("stamp", stamp(rng))
    save("slap", slap(rng))
    save("rip", rip(rng))
    # confetti: tiny pops thinning out
    cp = np.zeros(int(0.7 * K * SR), dtype=np.float32)
    for u in np.sort(rng.random(16) ** 1.8 * 0.55 * K):
        add_at(cp, tone(rng.uniform(1200, 3200), 0.02, d=0.005), u, rng.uniform(0.3, 0.8))
    save("confetti_pops", cp, -2.0)
    # travel: take-off, airport "ding-dong" (E5 -> C#5, in key), wind bed, riser into drop B
    save("jet", jet(rng, 1.9 * K))
    dd = np.zeros(int(1.9 * SR), dtype=np.float32)
    add_at(dd, bell(659.26), 0.0)
    add_at(dd, bell(554.37), 0.42, 0.9)
    save("dingdong", dd, -2.0)
    save("wind", wind(rng, 4.0 * K))
    save("riser2", riser(rng, 2.0 * K))
    # split-flap board: every flip of every cell, timed exactly like renderFlap() in index.html
    fr = mulberry32(2108)
    t0 = 20.96
    clat = np.zeros(int(1.2 * K * SR), dtype=np.float32)
    for r, word in enumerate(["BIENVENUE", "EN RUSSIE"]):
        for c in range(len(word)):
            start = 20.96 + c * 0.012 + r * 0.02
            settle = 21.02 + c * 0.07 + r * 0.16 + fr() * 0.04
            k = 0
            while start + k * 0.05 < settle:
                add_at(clat, tick(rng.uniform(2200, 3600), tau=0.0025, noise=0.8, rng=rng), (start + k * 0.05 - t0) * K, rng.uniform(0.18, 0.32))
                k += 1
            add_at(clat, tick(1300, tau=0.006, noise=0.9, rng=rng), (settle - t0) * K, 0.85)
    save("flap_clatter", clat)
    # odometer 12 000 (DT): a click each time a digit column crosses a digit
    t_start, land, target = 27.15, [27.76, 27.82, 27.88, 27.94, 28.0], [1, 2, 0, 0, 0]
    tt, ff = [], []
    for i in range(len(target)):
        a_, b_ = 3 + i * 2, 20 + target[i] + (i % 2) * 10
        x = np.linspace(0, 1, 4000)
        pos = a_ + (b_ - a_) * bezier_ease(ODO_ROLL, x)
        crossings = np.where(np.diff(np.floor(pos)) > 0)[0]
        tt += list(x[crossings] * (land[i] - t_start) * K)
        ff += [2600 + i * 180] * len(crossings)
    order = np.argsort(tt)
    save("odo_ticks", ticks_at(np.array(tt)[order], np.array(ff)[order], np.full(len(tt), 0.8), 0.95 * K, 21))
    # thermal printer: one feed burst per receipt line, from T11 + 1.5: header, 6 lines, total,
    # "non inclus" header, 3 option lines, end of paper (same steps as the #rc-paper tweens)
    pr = np.zeros(int(3.2 * K * SR), dtype=np.float32)
    feeds = [(0, 0.14)] + [(0.25 * k, 0.12) for k in range(1, 12)] + [(2.87, 0.1)]
    for u, d in feeds:
        u, d = u * K, d * K
        n = int(d * SR)
        tt_ = np.arange(n) / SR
        buzz = norm(bandnoise(n, 1200, 5200, rng)) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 120 * tt_)))
        buzz += 0.12 * np.sin(2 * np.pi * 3200 * tt_)
        buzz *= np.minimum(1, tt_ / 0.005) * np.minimum(1, (d - tt_) / 0.01)
        add_at(pr, buzz.astype(np.float32), u, 0.8)
        add_at(pr, tick(1800, rng=rng), u + d, 0.4)
    save("printer", pr)
    # sparkles arpeggio (A major, one note per pixel star)
    arp = np.zeros(int(0.9 * K * SR), dtype=np.float32)
    for k, f in enumerate([880.0, 1108.73, 1318.51, 1760.0, 2217.46, 2637.02]):
        d = 0.07
        add_at(arp, pulse(f, d) * np.exp(-np.arange(int(d * SR)) / (0.035 * SR)), k * 0.12 * K)
    save("pixel_arp", arp, -3.0)
    # end card typing: phone number (15 chars, 22 ms) and URL (16 chars, 18 ms)
    save("tel_ticks", ticks_at(np.arange(15) * 0.022 * K, 1250 + rng.uniform(-150, 150, 15), rng.uniform(0.5, 0.9, 15), 0.45 * K, 61))
    save("url_ticks", ticks_at(np.arange(16) * 0.018 * K, 1450 + rng.uniform(-150, 150, 16), rng.uniform(0.5, 0.9, 16), 0.4 * K, 51))
    # transfer: horn, rail joints "ta-dum" on every beat (fading as the train brakes),
    # car engine revving as it overtakes, pneumatic coach door
    save("horn", horn(), -2.0)
    rails = np.zeros(int(4.2 * K * SR), dtype=np.float32)
    for k in range(8):
        g = 1.0 if k < 6 else 0.75 - 0.2 * (k - 6)
        for dt, gg in ((0.0, 1.0), (0.09, 0.8)):
            n = int(0.06 * SR)
            thump = tone(95, 0.06, d=0.02) * 0.9 + 0.5 * norm(bandnoise(n, 2000, 6500, rng)) * env_ad(n, 0.0005, 0.006)
            add_at(rails, thump.astype(np.float32), (k * 0.5 + dt) * K, g * gg)
    save("rails", rails)
    n = int(3.6 * K * SR)
    tt = np.arange(n) / SR
    f0 = 68 + 26 * np.clip(tt / (3.0 * K), 0, 1) ** 1.5
    ph = 2 * np.pi * np.cumsum(f0) / SR
    eng = sum(np.sin(k * ph) / k for k in range(1, 7)) * (0.75 + 0.25 * np.sin(2 * np.pi * 24 * tt))
    eng = signal.sosfilt(signal.butter(2, 900, btype="low", fs=SR, output="sos"), eng)
    save("engine", norm(eng * np.minimum(1, tt / 0.4) * np.minimum(1, (3.6 * K - tt) / 0.5)))
    n = int(0.32 * SR)
    hiss = signal.sosfilt(signal.butter(2, 1500, btype="high", fs=SR, output="sos"), rng.standard_normal(n))
    save("pshh", norm(hiss * env_ad(n, 0.01, 0.09)), -3.0)


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
        kl = K if name.startswith("whoosh") else 1.0
        fade_out = cue.get("fade_out") and cue["fade_out"] * kl
        max_len = cue.get("max_len") and cue["max_len"] * kl
        place(bus, clip, cue["at"] * K - lead, cue.get("gain_db", -12.0),
              fade_out, max_len, cue.get("pan", 0.0), cue.get("pan_to"))
    return bus


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    music = music_edit()
    sf.write(OUT_DIR / "music_edit.wav", music.T, SR, subtype="PCM_24")
    # music gain automation (piecewise-linear in dB):
    # - the flight (17-21) sits on a sparse drum break then a bass build: lift it so the
    #   scene breathes without sagging, and land back at 0 dB just before drop B (21.0);
    # - the band stops at 37.0 and only an E chord rings: lift it +14 dB, then keep
    #   opening the gain to +18 dB by the end so the decay does not fade under the CTA.
    auto = [(0.0, 0.0), (16.995, 0.0), (17.03, 6.0), (19.0, 6.0), (20.8, 3.0), (20.985, 0.0),
            (37.02, 0.0), (37.12, 14.0), (DURATION, 18.0)]
    if SLOW:  # same moves at the slow version's times (two drum-break bars, longer chord)
        auto = [(0.0, 0.0), (25.495, 0.0), (25.53, 6.0), (29.5, 6.0), (31.3, 3.0), (31.485, 0.0),
                (55.52, 0.0), (55.62, 14.0), (DURATION, 20.0)]
    tt = np.arange(music.shape[1]) / SR
    g_db = np.interp(tt, [a for a, _ in auto], [b for _, b in auto])
    music = music * (10 ** (g_db / 20)).astype(np.float32)[None, :]
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
    # gain-stage then brick-wall limit (lookahead, 4x oversampled to catch inter-sample peaks)
    # so the loudnorm pass can stay linear (no pumping)
    pre = OUT_DIR / "mix_premaster.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw), "-af",
         "volume=-2dB,aresample=192000,alimiter=limit=0.8:attack=4:release=60:level=disabled:latency=1,aresample=48000", "-c:a", "pcm_f32le", str(pre)],
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
        ["ffmpeg", "-y", "-hide_banner", "-i", str(pre), "-af",
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
