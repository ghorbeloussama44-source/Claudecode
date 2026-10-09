#!/usr/bin/env python3
"""Music beds for the RusStudy social series: build/_beds/<slug>.wav.

Each episode names a track from assets/music (Pixabay Content License) and an offset; the bed is cut
to the episode length, faded in / out and normalised (two-pass EBU R128) to -20 LUFS, -2 dBTP:
quiet enough to sit under a voice-over recorded in CapCut, TikTok or Instagram, where the original
sound can still be turned down or muted.

usage: python3 scripts/beds.py [slug-prefix ...]
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import BUILD, ROOT, load_episodes, timings  # noqa: E402

TARGET_I, TARGET_TP, TARGET_LRA = -20.0, -2.0, 11.0


def ffmpeg(*args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", *args], check=True, capture_output=True, text=True)


def main():
    out_dir = BUILD / "_beds"
    out_dir.mkdir(parents=True, exist_ok=True)
    for ep in load_episodes(sys.argv[1:]):
        _, D = timings(ep)
        src = ROOT / "assets" / "music" / f"{ep['bed']}.mp3"
        off = ep.get("bed_offset", 0.0)
        fades = f"afade=t=in:st=0:d=0.35,afade=t=out:st={D - 1.8:.3f}:d=1.8"
        ln = f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}"
        p1 = ffmpeg("-ss", f"{off}", "-t", f"{D}", "-i", str(src), "-af", f"{fades},{ln}:print_format=json", "-f", "null", "-")
        js = p1.stderr[p1.stderr.rindex("{") : p1.stderr.rindex("}") + 1]
        m = json.loads(js)
        ln2 = (
            f"{ln}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
        )
        out = out_dir / f"{ep['slug']}.wav"
        ffmpeg("-ss", f"{off}", "-t", f"{D}", "-i", str(src), "-af", f"{fades},{ln2},aresample=48000", "-ac", "2", "-c:a", "pcm_s16le", "-t", f"{D}", str(out))
        print(f"{out.relative_to(ROOT)}  {D:.2f} s  from {ep['bed']} @ {off:.1f} s  (input {m['input_i']} LUFS)")


if __name__ == "__main__":
    main()
