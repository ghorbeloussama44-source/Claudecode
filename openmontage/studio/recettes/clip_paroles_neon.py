#!/usr/bin/env python3
"""Recette « Clip paroles néon » : une chanson + ses paroles corrigées -> un clip où chaque mot chanté
s'allume en néon doré au centre de l'image, sur des plans d'archives étalonnés.

C'est la méthode du clip « paroles néon » (août 2026), rendue automatique :
  musique Suno -> paroles calées mot par mot (transcription + vos corrections) -> plans Pexels
  -> montage changé à chaque phrase, étalonnage chaud -> mots en néon (Remotion, NeonWordOverlay)
  -> assemblage, volume, export YouTube + version légère + sous-titres .srt + miniature.

Un projet = un dossier :
  config.json            réglages (titre, client / chaîne, langue, format, mots-clés des plans, couleur…)
  input/chanson.mp3      la chanson (Suno ou autre)
  input/paroles.txt      les paroles corrigées, une phrase par ligne
  input/corrections.json (facultatif) corrections manuelles de timing : [{"i": 12, "startMs": 15320, "endMs": 15800}]
  footage/               les plans (téléchargés par l'étape footage, ou déposés à la main)
  build/                 fichiers intermédiaires ;  renders/  les livrables

Étapes (chacune relançable seule, dans cet ordre) :
  init      crée le dossier et un config.json à remplir
  align     transcrit la chanson (faster-whisper, horodatage par mot) et cale chaque mot de paroles.txt
            -> build/words.json (mots + temps), build/lines.json (phrases), renders/<slug>.srt
  footage   télécharge des plans Pexels pour chaque mot-clé du config (variable PEXELS_API_KEY) -> footage/
  montage   un plan par phrase (coupé s'il dépasse duree_plan_max), recadrage au format, fondus enchaînés,
            étalonnage -> build/montage.mp4
  overlay   rend les mots en néon sur fond transparent (Remotion, NeonWordOverlayOnly) -> build/overlay.webm
  final     néon + montage + chanson, volume normalisé -> renders/<slug>.mp4, <slug>_leger.mp4, miniature
  all       enchaîne align, footage (si des plans manquent), montage, overlay, final

usage :
  python3 openmontage/studio/recettes/clip_paroles_neon.py init  <dossier> --titre "Mon titre" --langue ar
  python3 openmontage/studio/recettes/clip_paroles_neon.py all   <dossier>
  python3 openmontage/studio/recettes/clip_paroles_neon.py align <dossier>      (une seule étape)
"""
import argparse
import difflib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

OPENMONTAGE = Path(__file__).resolve().parents[2]
COMPOSER = OPENMONTAGE / "remotion-composer"

DEFAULTS = {
    "titre": "Clip paroles néon",
    "client": "",
    "diffusion": "YouTube",
    "langue": "ar",
    "rtl": True,
    "format": "16:9",
    "fps": 30,
    "neon_color": "#FFC94A",
    "font_size": 140,
    "whisper_model": "medium",
    "mots_cles": ["candle flame dark", "mountain clouds sunrise", "stormy sea sailboat", "fire night", "desert golden hour",
                  "empty theater seats", "woman dancing beach wind", "full moon silhouette"],
    "plans_par_mot_cle": 2,
    "duree_plan_max": 8.0,
    "fondu": 0.5,
    "etalonnage": "chaud",
    "loudness": -14,
}
GRADES = {
    # warm golden look of the August clip: lower saturation, warm mids, vignette, light film grain
    "chaud": "eq=contrast=1.07:brightness=-0.015:saturation=0.9,colorbalance=rs=0.06:gs=0.015:bs=-0.07:rm=0.05:gm=0.01:bm=-0.05,"
             "vignette=angle=PI/4.6,noise=alls=5:allf=t+u",
    "froid": "eq=contrast=1.06:saturation=0.85,colorbalance=rs=-0.04:bs=0.06:rm=-0.02:bm=0.05,vignette=angle=PI/4.6,noise=alls=5:allf=t+u",
    "neutre": "eq=contrast=1.04:saturation=0.95,vignette=angle=PI/5",
}


def log(msg):
    print(f"[clip-néon] {msg}", flush=True)


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def ffprobe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def slugify(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "clip"


class Project:
    def __init__(self, folder):
        self.dir = Path(folder).resolve()
        cfg = self.dir / "config.json"
        self.cfg = dict(DEFAULTS, **(json.loads(cfg.read_text()) if cfg.exists() else {}))
        self.song = self.dir / "input" / "chanson.mp3"
        self.lyrics = self.dir / "input" / "paroles.txt"
        self.footage = self.dir / "footage"
        self.build = self.dir / "build"
        self.renders = self.dir / "renders"
        self.slug = slugify(self.cfg["titre"])
        portrait = self.cfg["format"] == "9:16"
        self.W, self.H = (1080, 1920) if portrait else (1920, 1080)
        for d in (self.footage, self.build, self.renders):
            d.mkdir(parents=True, exist_ok=True)

    def duration(self):
        return ffprobe_duration(self.song)


# ---------------------------------------------------------------- init
def step_init(folder, titre, langue):
    p = Path(folder).resolve()
    for d in ("input", "footage", "build", "renders"):
        (p / d).mkdir(parents=True, exist_ok=True)
    cfg = dict(DEFAULTS, titre=titre, langue=langue, rtl=langue in ("ar", "fa", "he", "ur"))
    (p / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
    if not (p / "input" / "paroles.txt").exists():
        (p / "input" / "paroles.txt").write_text("")
    log(f"projet créé : {p}")
    log("à faire : copier la chanson dans input/chanson.mp3, les paroles corrigées dans input/paroles.txt (une phrase par ligne),")
    log("          ajuster config.json (client, diffusion, format, mots_cles), puis lancer l'étape all")


# ---------------------------------------------------------------- align
AR_DIACRITICS = re.compile("[ؐ-ًؚ-ٰٟۖ-ۭـ]")
PUNCT = re.compile(r"[\s\.,;:!?\"'«»()\[\]\-–—…،؛؟]+")


def norm(word):
    w = AR_DIACRITICS.sub("", unicodedata.normalize("NFC", word))
    w = w.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"}))
    return PUNCT.sub("", w).lower()


def similarity(a, b):
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def align_words(hyp, ref):
    """Needleman-Wunsch on word similarity: returns, for each reference word, the index of its
    matched recognised word or None."""
    n, m = len(hyp), len(ref)
    gap = -0.45
    hn = [norm(h["w"]) for h in hyp]
    rn = [norm(r) for r in ref]
    score = [[0.0] * (m + 1) for _ in range(n + 1)]
    back = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        score[i][0], back[i][0] = i * gap, 1
    for j in range(1, m + 1):
        score[0][j], back[0][j] = j * gap, 2
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = similarity(hn[i - 1], rn[j - 1])
            diag = score[i - 1][j - 1] + (s * 2 - 0.6)
            up = score[i - 1][j] + gap
            left = score[i][j - 1] + gap
            best = max(diag, up, left)
            score[i][j] = best
            back[i][j] = 0 if best == diag else (1 if best == up else 2)
    match = [None] * m
    i, j = n, m
    while i > 0 and j > 0:
        b = back[i][j]
        if b == 0:
            if similarity(hn[i - 1], rn[j - 1]) >= 0.34:
                match[j - 1] = i - 1
            i, j = i - 1, j - 1
        elif b == 1:
            i -= 1
        else:
            j -= 1
    return match


def step_align(p):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper manquant : pip install faster-whisper (le modèle se télécharge au premier lancement)")

    lines = [l.strip() for l in p.lyrics.read_text().splitlines() if l.strip()]
    if not lines:
        sys.exit("input/paroles.txt est vide : coller les paroles corrigées, une phrase par ligne")
    ref, ref_line = [], []
    for li, line in enumerate(lines):
        for w in line.split():
            ref.append(w)
            ref_line.append(li)
    log(f"transcription ({p.cfg['whisper_model']}, langue {p.cfg['langue']}) : quelques minutes pour une chanson entière")
    model = WhisperModel(p.cfg["whisper_model"], device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(p.song), language=p.cfg["langue"], word_timestamps=True)
    hyp = [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segments for w in (s.words or []) if w.word.strip()]
    (p.build / "transcript.json").write_text(json.dumps(hyp, ensure_ascii=False, indent=0))
    match = align_words(hyp, ref)
    found = sum(1 for x in match if x is not None)
    log(f"{len(hyp)} mots entendus, {found}/{len(ref)} mots des paroles calés directement, le reste interpolé")

    # timings: matched words take the recognised word's time; the others share the gap between
    # their matched neighbours in proportion to their length
    starts = [hyp[k]["s"] if k is not None else None for k in match]
    ends = [hyp[k]["e"] if k is not None else None for k in match]
    total = p.duration()
    j = 0
    while j < len(ref):
        if starts[j] is not None:
            j += 1
            continue
        k = j
        while k < len(ref) and starts[k] is None:
            k += 1
        t0 = ends[j - 1] if j > 0 else max(0.0, (starts[k] if k < len(ref) else total) - 0.6 * (k - j))
        t1 = starts[k] if k < len(ref) else min(total, t0 + 0.6 * (k - j))
        weights = [max(1, len(norm(ref[x]))) for x in range(j, k)]
        span = max(0.12 * (k - j), t1 - t0)
        acc = t0
        for x, wgt in zip(range(j, k), weights):
            d = span * wgt / sum(weights)
            starts[x], ends[x] = acc, acc + d
            acc += d
        j = k
    words = []
    prev_end = 0.0
    for x, w in enumerate(ref):
        s = max(starts[x], prev_end)
        e = max(ends[x], s + 0.12)
        e = min(e, s + 1.8)
        words.append({"word": w, "startMs": round(s * 1000), "endMs": round(e * 1000), "line": ref_line[x]})
        prev_end = s + 0.05
    corr = p.dir / "input" / "corrections.json"
    if corr.exists():
        for c in json.loads(corr.read_text()):
            i = int(c["i"])
            if 0 <= i < len(words):
                words[i].update({k: int(c[k]) for k in ("startMs", "endMs") if k in c})
        log(f"corrections appliquées : {corr.name}")
    (p.build / "words.json").write_text(json.dumps(words, ensure_ascii=False, indent=0))
    out_lines = []
    for li, text in enumerate(lines):
        ws = [w for w in words if w["line"] == li]
        out_lines.append({"line": li, "text": text, "startMs": ws[0]["startMs"], "endMs": ws[-1]["endMs"]})
    (p.build / "lines.json").write_text(json.dumps(out_lines, ensure_ascii=False, indent=1))

    def srt_t(ms):
        h, r = divmod(int(ms), 3600000)
        m_, r = divmod(r, 60000)
        s_, ms_ = divmod(r, 1000)
        return f"{h:02d}:{m_:02d}:{s_:02d},{ms_:03d}"

    srt = []
    for k, l in enumerate(out_lines, 1):
        end = min(l["endMs"] + 400, out_lines[k]["startMs"] if k < len(out_lines) else l["endMs"] + 400)
        srt.append(f"{k}\n{srt_t(l['startMs'])} --> {srt_t(end)}\n{l['text']}\n")
    (p.renders / f"{p.slug}.srt").write_text("\n".join(srt))
    log(f"build/words.json ({len(words)} mots), build/lines.json ({len(out_lines)} phrases), renders/{p.slug}.srt")


# ---------------------------------------------------------------- footage
def clips_in(folder):
    return sorted(f for f in Path(folder).iterdir() if f.suffix.lower() in (".mp4", ".mov", ".webm", ".mkv"))


def step_footage(p):
    if not os.environ.get("PEXELS_API_KEY"):
        log("PEXELS_API_KEY absente : déposer des plans dans footage/ à la main, ou ajouter la clé dans les variables de l'environnement")
        return False
    sys.path.insert(0, str(OPENMONTAGE))
    from tools.video.pexels_video import PexelsVideo

    tool = PexelsVideo()
    orientation = "portrait" if p.cfg["format"] == "9:16" else "landscape"
    got = 0
    for kw in p.cfg["mots_cles"]:
        for page in range(1, int(p.cfg["plans_par_mot_cle"]) + 1):
            out = p.footage / f"{slugify(kw)}_{page}.mp4"
            if out.exists():
                continue
            res = tool.execute({"query": kw, "orientation": orientation, "size": "medium", "min_duration": 5,
                                "per_page": 1, "page": page, "output_path": str(out)})
            if res.success:
                got += 1
                log(f"plan : {out.name}")
            else:
                log(f"pas de plan pour « {kw} » (page {page}) : {res.error}")
    log(f"{got} plans téléchargés dans footage/ (Pexels, licence gratuite)")
    return True


# ---------------------------------------------------------------- montage
def shot_plan(p, total):
    lines = json.loads((p.build / "lines.json").read_text()) if (p.build / "lines.json").exists() else []
    cuts = [0.0] + [l["startMs"] / 1000 for l in lines if 0.5 < l["startMs"] / 1000 < total - 0.5] + [total]
    cuts = sorted(set(round(c, 3) for c in cuts))
    shots = []
    maxd = float(p.cfg["duree_plan_max"])
    for a, b in zip(cuts, cuts[1:]):
        n = max(1, math.ceil((b - a) / maxd))
        for k in range(n):
            shots.append((a + (b - a) * k / n, a + (b - a) * (k + 1) / n))
    merged = []
    for a, b in shots:  # no shot shorter than 1.2 s: glue it to the previous one
        if merged and b - a < 1.2:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged


def step_montage(p):
    clips = clips_in(p.footage)
    if not clips:
        sys.exit("footage/ est vide : lancer l'étape footage (clé Pexels) ou déposer des plans")
    total = p.duration()
    shots = shot_plan(p, total)
    fade = float(p.cfg["fondu"])
    W, H, fps = p.W, p.H, int(p.cfg["fps"])
    sd = p.build / "shots"
    sd.mkdir(exist_ok=True)
    durations = {c: ffprobe_duration(c) for c in clips}
    used = {c: 0.0 for c in clips}
    files = []
    log(f"{len(shots)} plans de montage à partir de {len(clips)} rushs")
    for k, (a, b) in enumerate(shots):
        clip = clips[k % len(clips)]
        length = (b - a) + (fade if k < len(shots) - 1 else 0)
        start = used[clip] if used[clip] + length <= durations[clip] else 0.0
        used[clip] = start + length
        out = sd / f"shot_{k:03d}.mp4"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-stream_loop", "-1", "-ss", f"{start:.3f}", "-i", str(clip),
             "-t", f"{length:.3f}", "-an", "-vf",
             f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={fps},setsar=1,format=yuv420p",
             "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", str(out)])
        files.append((out, b - a))
    grade = GRADES.get(p.cfg["etalonnage"], GRADES["chaud"])
    out = p.build / "montage.mp4"
    if fade > 0 and len(files) > 1:
        inputs, chain, offset = [], "", 0.0
        for f, _ in files:
            inputs += ["-i", str(f)]
        prev = "[0:v]"
        for k in range(1, len(files)):
            offset += files[k - 1][1]
            label = f"[x{k}]"
            chain += f"{prev}[{k}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}{label};"
            prev = label
        chain += f"{prev}{grade},format=yuv420p[v]"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", chain, "-map", "[v]",
             "-t", f"{total:.3f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out)])
    else:
        lst = sd / "list.txt"
        lst.write_text("".join(f"file '{f}'\n" for f, _ in files))
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf",
             f"{grade},format=yuv420p", "-t", f"{total:.3f}", "-c:v", "libx264", "-crf", "18", str(out)])
    log(f"build/montage.mp4 ({W}x{H}, {total:.1f} s, étalonnage {p.cfg['etalonnage']})")


# ---------------------------------------------------------------- overlay
def step_overlay(p):
    words = json.loads((p.build / "words.json").read_text())
    fps = int(p.cfg["fps"])
    frames = math.ceil(p.duration() * fps)
    font = round(float(p.cfg["font_size"]) * min(p.W, p.H) / 1080)
    props = {"words": [{"word": w["word"], "startMs": w["startMs"], "endMs": w["endMs"]} for w in words],
             "fontSize": font, "neonColor": p.cfg["neon_color"], "rtl": bool(p.cfg["rtl"])}
    pf = p.build / "overlay_props.json"
    pf.write_text(json.dumps(props, ensure_ascii=False))
    out = p.build / "overlay.webm"
    log(f"néon : {len(words)} mots, police {font} px, {frames} images (Remotion, fond transparent)")
    run(["./node_modules/.bin/remotion", "render", "src/index.tsx", "NeonWordOverlayOnly", str(out), f"--props={pf}",
         "--codec=vp9", "--pixel-format=yuva420p", "--image-format=png", f"--width={p.W}", f"--height={p.H}",
         f"--fps={fps}", f"--duration={frames}", "--log=error"], cwd=COMPOSER)
    log("build/overlay.webm")


# ---------------------------------------------------------------- final
def step_final(p):
    total = p.duration()
    out = p.renders / f"{p.slug}.mp4"
    lufs = float(p.cfg["loudness"])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(p.build / "montage.mp4"),
         "-c:v", "libvpx-vp9", "-i", str(p.build / "overlay.webm"), "-i", str(p.song),
         "-filter_complex", f"[0:v][1:v]overlay=format=auto,format=yuv420p[v];[2:a]loudnorm=I={lufs}:TP=-1:LRA=11,aresample=48000[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    light = p.renders / f"{p.slug}_leger.mp4"
    scale = "scale=1280:-2" if p.W >= p.H else "scale=-2:1280"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(out), "-vf", scale, "-c:v", "libx264",
         "-b:v", "800k", "-maxrate", "1000k", "-bufsize", "2000k", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(light)])
    # thumbnail: the middle of the first long word after a quarter of the song
    words = json.loads((p.build / "words.json").read_text())
    pick = next((w for w in words if w["startMs"] > total * 250 and w["endMs"] - w["startMs"] > 400), words[len(words) // 2])
    t = (pick["startMs"] + pick["endMs"]) / 2000
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", str(out), "-frames:v", "1", "-q:v", "2",
         str(p.renders / f"{p.slug}_miniature.jpg")])
    log(f"renders/{out.name}, {light.name}, {p.slug}_miniature.jpg")


STEPS = {"align": step_align, "footage": step_footage, "montage": step_montage, "overlay": step_overlay, "final": step_final}


def main():
    ap = argparse.ArgumentParser(description="Recette « Clip paroles néon »")
    ap.add_argument("step", choices=["init", "all", *STEPS])
    ap.add_argument("folder")
    ap.add_argument("--titre", default="Clip paroles néon")
    ap.add_argument("--langue", default="ar")
    a = ap.parse_args()
    if a.step == "init":
        step_init(a.folder, a.titre, a.langue)
        return
    p = Project(a.folder)
    if not p.song.exists():
        sys.exit("input/chanson.mp3 manquant")
    if a.step == "all":
        step_align(p)
        if not clips_in(p.footage):
            step_footage(p)
        step_montage(p)
        step_overlay(p)
        step_final(p)
    else:
        STEPS[a.step](p)


if __name__ == "__main__":
    main()
