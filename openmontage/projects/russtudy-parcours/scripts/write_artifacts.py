"""Write the canonical OpenMontage artifacts for RusStudy "Le parcours" (37 s) and validate them."""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ART = ROOT / "artifacts"
P = "russtudy-parcours"
NAME = "russtudy_parcours_37s"
DUR = 37.0

brief = {
    "version": "1.0",
    "title": "RusStudy — Le parcours : du premier message WhatsApp au premier jour à l'université (37 s)",
    "hook": "Tout commence par un message : le prospect écrit à RusStudy sur WhatsApp, envoie sur le drop, reçoit une réponse et réserve son appel d'orientation gratuit.",
    "key_points": [
        "Les 5 étapes du site : 01 consultation gratuite (appel de 15 min) · 02 dossier (traduction assermentée + légalisation) · 03 admission (lettre d'invitation d'État) · 04 visa & assurance · 05 accueil & installation (tuteur bilingue à l'aéroport, foyer)",
        "Prix fourni par le client : 1ère année dès 3 500 € tout compris = frais universitaires dès 2 200 € + consulting/orientation + dossier visa + accueil aéroport + foyer 1 an + assurance médicale",
        "Sans frais cachés (engagement « Transparence sur les coûts » du site)",
        "CTA : Écris-nous sur WhatsApp · +7 996 433 4489 · russieetudes.com · 1ère consultation gratuite",
    ],
    "tone": "Confiant, joueur, concret et rassurant",
    "style": "Atelier motion design aux tokens du site : un objet et une technique d'animation par étape, fil WhatsApp de bout en bout, PIXEL SYSTEM",
    "target_platform": "instagram",  # 9:16 — also TikTok / YouTube Shorts / Facebook Reels
    "target_duration_seconds": 37,
}

# (id, label, on-screen text, start, end)
SECTIONS = [
    ("s1", "Le message", "Tout commence par un message. — « Salam ! Je veux étudier en Russie. » — « Bienvenue ! On s'occupe de tout, de A à Z. » — Appel d'orientation · 15 min · gratuit · sans engagement — Réserver un appel gratuit", 0.0, 3.0),
    ("s2", "01 Consultation gratuite", "On analyse ton profil. — Appel d'orientation · 15 min · Zoom, téléphone ou WhatsApp · GRATUIT — Notes du Bac · Projet : Médecine · Ville & budget — Ton plan : Médecine générale · Moscou · Université d'État partenaire", 3.0, 7.0),
    ("s3", "02 Préparation du dossier", "On prépare ton dossier. Traduction assermentée + légalisation — Passeport · Diplôme du Bac · Relevés de notes · Acte de naissance — TRADUIT · LÉGALISÉ", 7.0, 9.0),
    ("s4", "03 Admission officielle", "Admission officielle. — Lettre d'invitation d'État · Admission confirmée · Médecine générale 2026–2027 — ADMIS", 9.0, 11.0),
    ("s5", "04 Visa & assurance", "Visa d'études + assurance. — Visa d'études Russie · Assurance médicale, couverture 1 an · Carte d'embarquement TUN → MOW", 11.0, 15.0),
    ("s6", "Départ", "Bon voyage !", 15.0, 17.0),
    ("s7", "En vol", "Cap sur Moscou. — Notification RusStudy : « Ton tuteur t'attend à l'arrivée. Bon vol ! »", 17.0, 21.0),
    ("s8", "05 Accueil", "BIENVENUE EN RUSSIE — Un tuteur bilingue t'attend à l'aéroport.", 21.0, 23.0),
    ("s9", "05 Foyer", "Foyer universitaire. — 1 an inclus — Chambre 412", 23.0, 25.0),
    ("s10", "Université", "Premier jour à l'université. — Carte d'étudiant · Médecine générale · Objectif atteint", 25.0, 27.0),
    ("s11", "Prix", "Budget 1ère année : dès 3 500 € tout compris — Frais universitaires dès 2 200 € · Consulting & orientation · Dossier visa · Accueil aéroport · Foyer universitaire 1 an · Assurance médicale : inclus — Total 1ère année dès 3 500 € — Sans frais cachés", 27.0, 33.0),
    ("s12", "CTA", "RusStudy. Études en Russie — Écris-nous sur WhatsApp — +7 996 433 4489 — russieetudes.com — 1ère consultation gratuite", 33.0, 37.0),
]
script = {
    "version": "1.0",
    "title": brief["title"],
    "total_duration_seconds": DUR,
    "sections": [{"id": i, "label": l, "text": t, "start_seconds": a, "end_seconds": b} for i, l, t, a, b in SECTIONS],
}

# (id, type, description, start, end, transition_in, transition_out, narrative role)
SCENES = [
    ("s1", "animation", "Téléphone en conversation façon WhatsApp (sans logo) : frappe caractère par caractère, envoi sur le drop (1,0 s), coches lues, « écrit… », réponse, carte d'appel ; la main pixel tape « Réserver un appel gratuit »", 0.0, 3.25, "cut (lisible dès la frame 0)", "ripple circulaire depuis le bouton tapé + poussée caméra", "introduce_subject"),
    ("s2", "animation", "Étape 01 : carte d'appel (anneaux, onde vocale, chrono accéléré 00:00 → 15:00), fiche profil scannée ligne par ligne avec coches tracées en SVG, bandeau vert « Ton plan »", 2.88, 7.1, "ripple circulaire", "push vertical de la scène violette", "establish_context"),
    ("s3", "animation", "Étape 02 : quatre documents en arcs (x et y à easings différents), classés dans la pochette, tampons TRADUIT et LÉGALISÉ en squash & stretch", 6.8, 9.1, "push vertical", "rideau or qui tombe", "deliver_payload"),
    ("s4", "animation", "Étape 03 : enveloppe qui tombe et s'écrase, rabat 3D (deux faces permutées), lettre d'invitation qui monte, signature tracée, tampon ADMIS + confettis pixel physiques", 8.84, 11.1, "rideau or", "whip-pan horizontal avec flou directionnel SVG", "deliver_payload"),
    ("s5", "animation", "Étape 04 : passeport dont la couverture s'ouvre en 3D, vignette visa claquée, carte d'assurance qui glisse, carte d'embarquement TUN → MOW avec code-barres", 10.86, 15.4, "whip-pan", "déchirure de la carte d'embarquement (bande dentelée)", "deliver_payload"),
    ("s6", "animation", "Départ : ciel révélé par la déchirure, « Bon voyage ! », avion pixel qui décolle sur MotionPath avec traînée pointillée, nuages pixel", 14.98, 17.06, "déchirure", "mur de nuages pixel (couverture totale à 17,0 s)", "emotional_beat"),
    ("s7", "animation", "En vol : carte en pixels générée depuis un masque terre/mer (Tunis → Moscou), caméra qui dézoome puis plonge sur Moscou, sillage doré, nuages en parallaxe, notification RusStudy", 17.0, 21.2, "mur de nuages", "iris vert depuis Moscou sur le drop B (21,0 s)", "build_tension"),
    ("s8", "animation", "Étape 05 : panneau d'arrivées à volets (split-flap) BIENVENUE EN RUSSIE, pancarte RusStudy du tuteur", 20.88, 23.05, "iris", "flip 3D plein écran", "emotional_beat"),
    ("s9", "animation", "Étape 05 : carte-clé sur le lecteur (LED verte), porte 412 qui s'ouvre en 3D sur une chambre pixel (lampe, neige à la fenêtre), puce « 1 an inclus »", 23.0, 25.1, "flip 3D", "travelling avant dans la fenêtre + flash blanc", "deliver_payload"),
    ("s10", "broll", "Premier jour : photo d'amphithéâtre (site) en Ken Burns, typo cinétique lettre par lettre, carte d'étudiant en 3D avec reflet, étoiles pixel ; la barre de progression se complète", 24.98, 27.0, "flash blanc", "cut sec", "resolution"),
    ("s11", "animation", "Prix : odomètre 3 500 € (flou directionnel), pastille « tout compris », ticket de caisse imprimé ligne par ligne, tampon SANS FRAIS CACHÉS", 27.0, 33.05, "cut sec", "chute avant l'arrêt de l'orchestre", "deliver_payload"),
    ("s12", "text_card", "Ville pixel de nuit (rappel du spot 15 s), logo RusStudy. sur l'accord final, CTA WhatsApp, numéro et site tapés, tap de la main pixel", 33.0, 37.0, "cut sur l'accord final (33,0 s)", "fin", "call_to_action"),
]
scene_plan = {
    "version": "1.0",
    "scenes": [
        {"id": i, "type": t, "description": d, "start_seconds": a, "end_seconds": b, "script_section_id": i,
         "transition_in": ti, "transition_out": to, "narrative_role": role}
        for i, t, d, a, b, ti, to, role in SCENES
    ],
}


def asset(i, typ, path, tool, scene, **kw):
    return {"id": i, "type": typ, "path": path, "source_tool": tool, "scene_id": scene, **kw}


asset_manifest = {
    "version": "1.0",
    "assets": [
        asset("img-amphitheatre", "image", "hyperframes/assets/img/amphitheatre.jpg", "russieetudes.com (Unsplash)", "s10", license="Unsplash License",
              original_url="https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0"),
        asset("font-space-grotesk", "font", "hyperframes/assets/fonts/SpaceGrotesk-latin.woff2", "Google Fonts", "all", license="SIL Open Font License 1.1"),
        asset("map-land-mask", "diagram", "scripts/make_dotmap.py", "global-land-mask 1.0.0 (NOAA GLOBE 1 km)", "s7", license="MIT (package) / public domain (GLOBE data)",
              generation_summary="Grille 54 x 96 terre/mer embarquée dans index.html (MAP_ROWS), régénérable avec scripts/make_dotmap.py"),
        asset("music-funky", "music", "assets/music/11_funky.mp3", "pixabay_music", "all", provider="pixabay", license="Pixabay Content License",
              original_url="https://cdn.pixabay.com/audio/2026/01/06/audio_437fcd7b2d.mp3", duration_seconds=139.8,
              generation_summary="120 BPM ; montage sur mesures : piste 15,026–32,026 s (drop A à 1,0 s) puis 76,025–90,025 s (break 17, montée 19, drop B à 21,0 s) puis 62,025–68,025 s (break de fin, arrêt + accord de mi à 33,0 s)"),
        asset("sfx-bundled", "sfx", "../../.agents/skills/hyperframes-media/assets/sfx", "hyperframes-media bundled library", "all", provider="pixabay", license="Pixabay Content License"),
        asset("sfx-synth", "sfx", "assets/audio/sfx", "scripts/build_audio.py", "all",
              generation_summary="Frappe clavier, papier, tampons, déchirure, décollage, carillon d'aéroport, vent, panneau à volets (timing identique à la composition), bip de badge, odomètre, imprimante — synthèse numpy déterministe"),
        asset("soundtrack", "audio", "hyperframes/assets/audio/soundtrack.wav", "scripts/build_audio.py", "all", duration_seconds=DUR, format="wav",
              generation_summary="Musique + 106 cues SFX, automation de gain (vol, accord final), ducking 3 dB, limiteur suréchantillonné, -14 LUFS / -2,4 dBTP"),
        asset("composition", "animation", "hyperframes/index.html", "hyperframes (atelier, GSAP 3.14)", "all",
              generation_summary="Composition écrite à la main, une seule timeline GSAP déterministe, 12 scènes + HUD de progression"),
    ],
}

edit_decisions = {
    "version": "1.0",
    "render_runtime": "hyperframes",
    "composition_mode": "atelier",
    "renderer_family": "animation-first",
    "cuts": [
        {"id": i, "source": f"hyperframes/index.html#{i}", "in_seconds": a, "out_seconds": b, "transition_in": ti, "transition_out": to}
        for i, t, d, a, b, ti, to, role in SCENES
    ],
}


def out(path, fmt, fps, platform):
    f = ROOT / path
    return {"path": path, "format": fmt, "codec": "h264" if fmt == "mp4" else None, "audio_codec": "aac" if fmt == "mp4" else None,
            "resolution": "1080x1920", "fps": fps, "duration_seconds": DUR if fmt == "mp4" else 0,
            "file_size_bytes": f.stat().st_size if f.exists() else 0, "platform_target": platform}


render_report = {"version": "1.0", "render_grammar": "animation-first", "outputs": []}
for o in [out(f"renders/{NAME}_60fps.mp4", "mp4", 60, "TikTok / YouTube Shorts / Reels (master)"),
          out(f"renders/{NAME}_30fps.mp4", "mp4", 30, "Instagram Reels / Facebook / Stories")]:
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
            [opt("animation", "animation (motion graphics / typo cinétique)", 0.95, "spot musical non narré où la motion porte le récit"),
             opt("animated-explainer", "animated-explainer", 0.45, "récit par étapes", "pensé pour une narration voix off ; pas de TTS demandé")],
            "animation", "Suite du spot 15 s ; l'utilisateur a demandé « travail à fond », 30–40 s, du premier message WhatsApp jusqu'à l'université.", True, 0.9),
        dec("d2", "proposal", "concept_selection", "Concept",
            [opt("parcours-objets", "Le parcours : un objet et une technique d'animation par étape, fil WhatsApp de bout en bout", 0.9, "montre le processus demandé ET la palette de techniques motion (3D, split-flap, carte, typo, physique)"),
             opt("telephone-continu", "Tout dans l'interface du téléphone", 0.55, "cohérent avec WhatsApp", "monotone visuellement sur 37 s, ne montre pas l'étendue du motion design"),
             opt("carte-seule", "Trajet sur carte animée", 0.4, "lisible", "ne montre pas les étapes administratives (dossier, admission, visa)")],
            "parcours-objets", "Voir artifacts/art-direction.md (storyboard en 12 scènes calé sur la grille musicale).", False, 0.85),
        dec("d3", "proposal", "render_runtime_selection", "Moteur de composition",
            [opt("hyperframes", "HyperFrames (HTML/CSS/GSAP)", 0.9, "même moteur que la v1 : réutilisation de la ville pixel, retouche identique"),
             opt("remotion", "Remotion (React)", 0.7, "disponible", "réécriture complète sans gain pour ce concept")],
            "hyperframes", "Continuité avec la v1 (scripts de rendu et de retouche identiques).", False, 0.85),
        dec("d4", "proposal", "composition_mode", "Mode d'écriture",
            [opt("atelier", "atelier (composition écrite à la main)", 0.95, "pièce vitrine de marque"),
             opt("templated", "scènes types", 0.2, "rapide", "rendu générique")],
            "atelier", "Une seule timeline GSAP déterministe, scènes en <section> horodatées.", False, 0.9),
        dec("d5", "assets", "music_source", "Musique",
            [opt("pixabay-funky", "Pixabay « Funky » réutilisée et remontée à 37 s", 0.85, "signature sonore commune aux deux spots ; la structure (build, drop A, break, drop B, arrêt sur accord) colle au récit"),
             opt("autre-piste", "Autre piste Pixabay", 0.5, "variété", "perd la continuité de marque entre les deux spots")],
            "pixabay-funky", "Drop A à 1,0 s (envoi du message), break pendant le vol, drop B à 21,0 s (arrivée), arrêt + accord à 33,0 s (logo).", False, 0.8),
        dec("d6", "assets", "provider_selection", "Sound design",
            [opt("bundled+synth", "SFX HyperFrames (Pixabay) + synthèse maison", 0.85, "gratuit, déterministe, accordé à la musique, timing exact des volets et de l'odomètre")],
            "bundled+synth", "106 cues calés sur les événements GSAP ; sons tonals accordés en la mixolydien / mi.", False, 0.8),
        dec("d7", "compose", "visual_accuracy_check", "Prix et promesses",
            [opt("client-price", "Prix donné par le client : dès 3 500 € la 1ère année, tout compris (frais universitaires dès 2 200 € inclus)", 0.8, "lecture la plus naturelle du message du client"),
             opt("price-plus-fees", "3 500 € d'accompagnement en plus des 2 200 € de frais", 0.2, "autre lecture possible", "le client écrit que les 3 500 € incluent consulting, accueil, foyer, assurance et visa, et que 2 200 € est le minimum universitaire")],
            "client-price", "À faire confirmer par le client avant diffusion payante ; « tout compris » = les postes listés sur le ticket (billet d'avion et vie courante non inclus). Interface façon WhatsApp sans logo ; promesses reprises du site (appel 15 min, traduction assermentée, lettre d'invitation d'État, tuteur bilingue, sans frais cachés).", False, 0.7),
        dec("d8", "compose", "motion_commitment", "Cadence de rendu",
            [opt("60fps", "Master 60 fps", 0.85, "mouvements rapides plus nets (whip-pan, volets, odomètre)"),
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
