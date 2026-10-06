"""Write the canonical OpenMontage artifacts for the RusStudy 15 s spot and validate them."""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ART = ROOT / "artifacts"
P = "russtudy-motion-15s"

brief = {
    "version": "1.0",
    "title": "RusStudy — Étudie en Russie. Change ta vie. (spot motion design 15 s)",
    "hook": "Bac en poche ? Une machine à sous de filières (Médecine, Ingénierie, Pharmacie, Business) se verrouille sur le drop, puis « en Russie. »",
    "key_points": [
        "Filières : Médecine, Ingénierie, Pharmacie, Business",
        "Frais de scolarité dès 2 200 €/an, jusqu'à 4× moins cher qu'en Europe",
        "Accompagnement total : visa garanti par contrat, logement garanti, accueil à l'aéroport, diplômes d'État reconnus (OMS & Tunisie)",
        "+1 200 étudiants placés, 40+ universités d'État partenaires",
        "CTA : 1ère consultation gratuite sur russieetudes.com — places limitées session 2026–2027",
    ],
    "tone": "Jeune, confiant, joueur et précis — sérieux sur les preuves",
    "style": "Atelier motion design aux tokens du site (bento saturé, Space Grotesk, PIXEL SYSTEM V1)",
    "target_platform": "instagram",  # 9:16 — also TikTok / YouTube Shorts / Facebook Reels
    "target_duration_seconds": 15,
}

script = {
    "version": "1.0",
    "title": brief["title"],
    "total_duration_seconds": 15,
    "sections": [
        {"id": "s0", "label": "Hook", "text": "Bac en poche ? MÉDECINE · INGÉNIERIE · PHARMACIE · BUSINESS — en Russie.", "start_seconds": 0.0, "end_seconds": 3.2},
        {"id": "s1", "label": "Prix", "text": "Frais de scolarité — dès 2 200 € /an — jusqu'à 4× moins cher qu'en Europe", "start_seconds": 3.2, "end_seconds": 5.0},
        {"id": "s2", "label": "Accompagnement", "text": "Accompagnement total — On gère tout. Visa garanti · Logement garanti à 100 % · Accueil à l'aéroport · Diplômes d'État reconnus", "start_seconds": 5.0, "end_seconds": 7.2},
        {"id": "s3", "label": "Trajet", "text": "On t'accueille à l'arrivée. TUNIS → MOSCOU. Un tuteur bilingue t'attend sur place.", "start_seconds": 7.2, "end_seconds": 8.9},
        {"id": "s4", "label": "Preuve", "text": "La Russie en vrai — +1 200 étudiants placés en Russie · 40+ universités d'État partenaires", "start_seconds": 8.9, "end_seconds": 11.0},
        {"id": "s5", "label": "Promesse", "text": "Étudie en Russie. Change ta vie.", "start_seconds": 11.0, "end_seconds": 13.0},
        {"id": "s6", "label": "Logo + CTA", "text": "RusStudy. ÉTUDES EN RUSSIE — 1ère consultation gratuite — russieetudes.com — Places limitées · Session 2026–2027", "start_seconds": 13.0, "end_seconds": 15.0},
    ],
}

scenes = [
    ("s0", "animation", "Machine à filières : carte-rouleau colorée (couleurs des filières du site) en rotation floutée dès la frame 0, verrouillage avec rebond sur le drop (1,0 s), un mot par temps ; « en Russie. » claque sur le temps fort de 3,0 s", 0.0, 3.6, "cut", "iris circulaire depuis le point doré de « Russie. »"),
    ("s1", "animation", "Odomètre du prix sur fond or : chiffres qui roulent (flou directionnel SVG) et se posent sur le temps à 4,0 s, pastille « /an »", 3.15, 5.4, "iris circulaire (portail clip-path)", "rétractation clip-path en carte or du bento"),
    ("s2", "animation", "Bento « Accompagnement total » : 4 cartes aux couleurs du site qui éclosent à la croche, icônes pixel-art animées", 4.9, 7.5, "FLIP clip-path depuis la scène prix", "zoom-through dans la carte verte"),
    ("s3", "animation", "Trajet Tunis → Moscou : avion pixel sur arc (MotionPath), traînée pointillée qui se dessine, check d'arrivée", 7.2, 9.3, "zoom-through", "volet diagonal tricolore dans l'axe du vol"),
    ("s4", "broll", "La Russie en vrai : photos du site (Saint-Basile, amphithéâtre, diplômés) révélées par masques, cartes stats noires avec compteurs", 8.8, 11.4, "volet diagonal (masque le raccord musical)", "dissolution en pixels"),
    ("s5", "animation", "Ville pixel de nuit (hero du site) + tour Spasskaïa et coupoles de Saint-Basile aux couleurs RusStudy, fenêtres qui s'allument, neige ; « Étudie en Russie. Change ta vie. »", 11.02, 13.0, "dissolution en pixels", "le point de « vie. » s'envole vers le logo"),
    ("s6", "text_card", "Logo RusStudy. assemblé sur l'accord final, signature, CTA « 1ère consultation gratuite », URL tapée, puce d'urgence, tap du curseur pixel", 13.0, 15.0, "match-cut sur le point", "fin (boucle vers le hook)"),
]
ROLES = {"s0": "introduce_subject", "s1": "deliver_payload", "s2": "deliver_payload", "s3": "emotional_beat",
         "s4": "evidence", "s5": "resolution", "s6": "call_to_action"}
scene_plan = {
    "version": "1.0",
    "scenes": [
        {"id": i, "type": t, "description": d, "start_seconds": a, "end_seconds": b, "script_section_id": i,
         "transition_in": ti, "transition_out": to, "narrative_role": ROLES[i]}
        for i, t, d, a, b, ti, to in scenes
    ],
}

def asset(i, typ, path, tool, scene, **kw):
    return {"id": i, "type": typ, "path": path, "source_tool": tool, "scene_id": scene, **kw}

asset_manifest = {
    "version": "1.0",
    "assets": [
        asset("img-saint-basile", "image", "hyperframes/assets/img/saint_basile.jpg", "russieetudes.com (Unsplash)", "s4", license="Unsplash License", original_url="https://images.unsplash.com/photo-1513326738677-b964603b136d"),
        asset("img-amphitheatre", "image", "hyperframes/assets/img/amphitheatre.jpg", "russieetudes.com (Unsplash)", "s4", license="Unsplash License", original_url="https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0"),
        asset("img-diplomes", "image", "hyperframes/assets/img/diplomes_toques.jpg", "russieetudes.com (Unsplash)", "s4", license="Unsplash License", original_url="https://images.unsplash.com/photo-1541339907198-e08756dedf3f",
              generation_summary="Photo prise à Singapour : légendée « Objectif : ton diplôme » (comme sur le site), jamais présentée comme la Russie"),
        asset("font-space-grotesk", "font", "hyperframes/assets/fonts/SpaceGrotesk-latin.woff2", "Google Fonts", "all", license="SIL Open Font License 1.1"),
        asset("music-funky", "music", "assets/music/candidates/11_funky.mp3", "pixabay_music", "all", provider="pixabay", license="Pixabay Content License",
              original_url="https://cdn.pixabay.com/audio/2026/01/06/audio_437fcd7b2d.mp3", duration_seconds=139.8,
              generation_summary="120 BPM mesuré ; montage sur mesures : piste 15,026–24,026 s puis 60,025–66,025 s (drop à 1,0 s, accord final à 13,0 s)"),
        asset("sfx-bundled", "sfx", "../../.agents/skills/hyperframes-media/assets/sfx", "hyperframes-media bundled library", "all", provider="pixabay", license="Pixabay Content License"),
        asset("sfx-synth", "sfx", "assets/audio/sfx", "scripts/build_audio.py", "all", generation_summary="Cliquetis de rouleau, odomètre, compteurs, arpège 8-bit, bloop/fwip du point — synthèse déterministe numpy"),
        asset("soundtrack", "audio", "hyperframes/assets/audio/soundtrack.wav", "scripts/build_audio.py", "all", duration_seconds=15.0, format="wav",
              generation_summary="Musique + 53 cues SFX, ducking 3 dB, limiteur, -14 LUFS / -1,9 dBTP"),
        asset("composition", "animation", "hyperframes/index.html", "hyperframes (atelier, GSAP 3.14)", "all", generation_summary="Composition écrite à la main, une seule timeline GSAP déterministe"),
    ],
}

edit_decisions = {
    "version": "1.0",
    "render_runtime": "hyperframes",
    "composition_mode": "atelier",
    "renderer_family": "animation-first",
    "cuts": [
        {"id": i, "source": f"hyperframes/index.html#{i if i != 's6' else 's5'}", "in_seconds": a, "out_seconds": b, "transition_in": ti, "transition_out": to}
        for i, t, d, a, b, ti, to in scenes
    ],
}

def out(path, fmt, fps, platform):
    f = ROOT / path
    return {"path": path, "format": fmt, "codec": "h264" if fmt == "mp4" else None, "audio_codec": "aac" if fmt == "mp4" else None,
            "resolution": "1080x1920", "fps": fps, "duration_seconds": 15.0 if fmt == "mp4" else 0,
            "file_size_bytes": f.stat().st_size if f.exists() else 0, "platform_target": platform}

render_report = {"version": "1.0", "render_grammar": "animation-first", "outputs": []}
for o in [out("renders/russtudy_motion_15s_60fps.mp4", "mp4", 60, "TikTok / YouTube Shorts / Reels (master)"),
          out("renders/russtudy_motion_15s_30fps.mp4", "mp4", 30, "Instagram Reels / Facebook / Stories")]:
    render_report["outputs"].append({k: v for k, v in o.items() if v is not None})

def dec(i, stage, cat, subject, options, selected, reason, approved=False, conf=0.85):
    return {"decision_id": i, "stage": stage, "category": cat, "subject": subject, "options_considered": options,
            "selected": selected, "reason": reason, "user_visible": True, "user_approved": approved, "confidence": conf}

def opt(oid, label, score, reason, rejected=None):
    o = {"option_id": oid, "label": label, "score": score, "reason": reason}
    if rejected:
        o["rejected_because"] = rejected
    return o


decision_log = {
    "version": "1.0",
    "project_id": P,
    "decisions": [
        dec("d1", "proposal", "pipeline_selection", "Pipeline OpenMontage",
            [opt("animation", "animation (motion graphics / typo cinétique)", 0.95, "spot non narré où la motion est le message"),
             opt("animated-explainer", "animated-explainer", 0.4, "pensé pour un récit narré", "pas de narration dans un spot musical de 15 s"),
             opt("cinematic", "cinematic", 0.2, "montage de plans tournés/générés", "aucun fournisseur vidéo IA configuré ; le brief demande du motion design")],
            "animation", "Demande « vas-y à fond » = exécution de bout en bout autorisée par l'utilisateur (pas d'arrêt aux portes d'approbation intermédiaires).", True, 0.9),
        dec("d2", "proposal", "render_runtime_selection", "Moteur de composition",
            [opt("hyperframes", "HyperFrames (HTML/CSS/GSAP)", 0.9, "typo cinétique, masques clip-path, MotionPath, synchro beat ; moteur recommandé pour les promos de marque"),
             opt("remotion", "Remotion (React)", 0.75, "déjà utilisé dans ce dépôt (MediLearn), rendu image par image fiable", "les animations GSAP de ce concept s'écrivent plus naturellement en HTML/GSAP"),
             opt("ffmpeg", "FFmpeg seul", 0.05, "assemblage simple", "pas de motion design possible")],
            "hyperframes", "Les deux moteurs étaient disponibles (preflight) ; choix fait par l'agent, à confirmer par l'utilisateur.", False, 0.8),
        dec("d3", "proposal", "composition_mode", "Mode d'écriture",
            [opt("atelier", "atelier (composition écrite à la main)", 0.95, "pièce vitrine de marque, direction artistique propre"),
             opt("templated", "scènes types", 0.2, "rapide", "rendu générique, ne démontre pas l'expertise motion")],
            "atelier", "Voir artifacts/art-direction.md.", False, 0.9),
        dec("d4", "assets", "music_source", "Musique",
            [opt("pixabay-funky", "Pixabay « Funky » (120 BPM, la mixolydien)", 0.85, "très percussive (0,83), build→drop net et accord final tenu"),
             opt("pixabay-other", "11 autres pistes Pixabay analysées", 0.55, "tempo/énergie mesurés", "moins percussives ou sans fin naturelle"),
             opt("magnific-music", "Génération Magnific (Lyria / ElevenLabs)", 0.0, "musique sur mesure", "compte gratuit, 0 crédit"),
             opt("higgsfield-audio", "Génération Higgsfield", 0.0, "musique sur mesure", "service indisponible pendant la session")],
            "pixabay-funky", "Montage sur mesures : drop à 1,0 s, raccord masqué à 9,0 s, accord final à 13,0 s.", False, 0.75),
        dec("d5", "assets", "provider_selection", "Sound design",
            [opt("bundled+synth", "SFX HyperFrames (Pixabay) + synthèse maison", 0.85, "gratuit, déterministe, accordé à la musique"),
             opt("magnific-sfx", "SFX Magnific", 0.0, "SFX génératifs", "non disponible sur le plan du compte")],
            "bundled+synth", "53 cues calés sur les événements GSAP ; sons tonals accordés (mi tenu, résolution sur la).", False, 0.8),
        dec("d6", "compose", "visual_accuracy_check", "Fidélité marque et honnêteté",
            [opt("faithful", "Logo officiel, légendes honnêtes, pas de faux témoignages", 1.0, "conforme au site et non trompeur")],
            "faithful", "Point du logo blanc sur fond sombre comme dans le code du site ; photo des diplômés (Singapour) légendée « Objectif : ton diplôme » ; visages stock des témoignages non utilisés ; chiffres repris du site.", False, 0.95),
        dec("d7", "compose", "motion_commitment", "Cadence de rendu",
            [opt("60fps", "Master 60 fps", 0.85, "mouvements rapides plus nets (rouleau, zoom-through)"),
             opt("30fps", "Variante 30 fps", 0.75, "cadence la plus sûre pour Instagram/Facebook", "fournie en variante, pas en master")],
            "60fps", "Les deux versions sont livrées.", False, 0.85),
    ],
}

SCHEMAS = REPO / "schemas/artifacts"
for name, data in [("brief", brief), ("script", script), ("scene_plan", scene_plan), ("asset_manifest", asset_manifest),
                   ("edit_decisions", edit_decisions), ("render_report", render_report), ("decision_log", decision_log)]:
    schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text())
    jsonschema.validate(data, schema)
    (ART / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"ok  {name}.json")
