#!/usr/bin/env python3
"""Studio OpenMontage: inventory of every delivered video.

Probes openmontage/projects/*/renders/*.mp4 and writes studio/videos.json (one row per video) for the
"Studio OpenMontage" dashboard. projects.json (one row per project) and backlog.json (one row per action)
are edited by hand. See studio/README.md for how the dashboard is updated.

usage: python3 openmontage/studio/inventory.py
"""
import json
import re
import subprocess
from pathlib import Path

STUDIO = Path(__file__).resolve().parent
PROJECTS = STUDIO.parent / "projects"

# version and state of a file when its name does not say it: (project, pattern, version, state)
# state: "actuelle" (the version to use), "livrée" (delivered, still valid), "ancienne" (superseded)
RULES = [
    ("mahdia-festival", r"_v8", "v8", "actuelle"),
    ("medilearn", r"^concept_", "concept", "ancienne"),
    ("medilearn", r"^tv_topic1_v1", "v1", "livrée"),
    ("medilearn", r"^topic1_v2", "v2", "actuelle"),
    ("russtudy-motion-15s", r"", "v1", "actuelle"),
    ("russtudy-parcours", r"_40s_", "v5", "ancienne"),
    ("russtudy-parcours", r"_60s_", "v7", "actuelle"),
    ("russtudy-social", r"", "v1", "actuelle"),
]
LANGUAGE = {"mahdia-festival": "arabe", "medilearn": "français"}


def probe(f):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate:format=duration",
         "-of", "json", str(f)], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return s["width"], s["height"], round(int(num) / int(den)), round(float(j["format"]["duration"]), 1)


def main():
    rows = []
    for f in sorted(PROJECTS.glob("*/renders/*.mp4")):
        project = f.parent.parent.name
        if f.name.startswith("_") or "draft" in f.name:
            continue
        w, h, fps, dur = probe(f)
        version, state = "—", "livrée"
        for p, pat, v, st in RULES:
            if p == project and re.search(pat, f.name):
                version, state = v, st
                break
        lang = LANGUAGE.get(project) or ("derja" if "derja" in f.name else "français")
        rows.append({
            "fichier": f.name,
            "projet": project,
            "format": "9:16" if h > w else "16:9",
            "resolution": f"{w}×{h}",
            "fps": fps,
            "duree_s": dur,
            "taille_mo": round(f.stat().st_size / 1e6, 1),
            "langue": lang,
            "version": version,
            "etat": state,
        })
    (STUDIO / "videos.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
    print(f"studio/videos.json: {len(rows)} videos, {sum(r['duree_s'] for r in rows) / 60:.1f} min")


if __name__ == "__main__":
    main()
