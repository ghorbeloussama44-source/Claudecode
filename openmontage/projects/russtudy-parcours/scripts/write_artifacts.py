"""Write the canonical OpenMontage artifacts for RusStudy "Le parcours" (40 s, 9:16 + YouTube 16:9) and validate them."""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ART = ROOT / "artifacts"
P = "russtudy-parcours"
NAME = "russtudy_parcours_40s"
NAME16 = "russtudy_parcours_40s_youtube_16x9"
NAME60 = "russtudy_parcours_60s"  # v4: same film 1.5x slower (scripts/make_slow.py)
NAME60_16 = "russtudy_parcours_60s_youtube_16x9"
DUR = 40.0

brief = {
    "version": "1.0",
    "title": "RusStudy — Le parcours : du premier message WhatsApp au premier jour à l'université (40 s)",
    "hook": "Tout commence par un message : le prospect écrit à RusStudy sur WhatsApp, envoie sur le drop, reçoit une réponse et réserve son appel d'orientation gratuit.",
    "key_points": [
        "Les 5 étapes du site : 01 consultation gratuite (appel de 15 min) · 02 dossier (traduction assermentée + légalisation) · 03 admission (lettre d'invitation d'État) · 04 visa & assurance · 05 accueil & installation (tuteur bilingue à l'aéroport, transfert, foyer)",
        "v3 (demande client) : transport interne de Moscou vers la ville de l'université, en train ou en voiture, avec le tuteur (exemple illustratif : Kazan)",
        "Prix fourni par le client : 1ère année dès 3 500 € = frais universitaires dès 2 200 € + consulting/orientation + dossier visa + accueil aéroport + foyer 1 an + assurance médicale",
        "Non inclus (précision du client, v5) : billet d'avion, transport Moscou → ville universitaire (train ou voiture, au choix), hôtel et visites à Moscou — en option, sur devis",
        "Sans frais cachés (engagement « Transparence sur les coûts » du site)",
        "CTA : Écris-nous sur WhatsApp · +7 996 433 4489 · russieetudes.com · 1ère consultation gratuite",
    ],
    "tone": "Confiant, joueur, concret et rassurant",
    "style": "Atelier motion design aux tokens du site : un objet et une technique d'animation par étape, fil WhatsApp de bout en bout, PIXEL SYSTEM",
    "target_platform": "instagram",  # 9:16 master — also TikTok / Shorts / Reels; YouTube 16:9 derived (render_report)
    "target_duration_seconds": 40,
}

# (id, label, on-screen text, start, end)
SECTIONS = [
    ("s1", "Le message", "Tout commence par un message. — « Salam ! Je veux étudier en Russie. » — « Bienvenue ! On s'occupe de tout, de A à Z. » — Appel d'orientation · 15 min · gratuit · sans engagement — Réserver un appel gratuit", 0.0, 3.0),
    ("s2", "01 Consultation gratuite", "On analyse ton profil. — Appel d'orientation · 15 min · Zoom, téléphone ou WhatsApp · GRATUIT — Notes du Bac · Projet : Médecine · Ville & budget — Ton plan : Médecine générale · Kazan · Université d'État partenaire", 3.0, 7.0),
    ("s3", "02 Préparation du dossier", "On prépare ton dossier. Traduction assermentée + légalisation — Passeport · Diplôme du Bac · Relevés de notes · Acte de naissance — TRADUIT · LÉGALISÉ", 7.0, 9.0),
    ("s4", "03 Admission officielle", "Admission officielle. — Lettre d'invitation d'État · Admission confirmée · Médecine générale 2026–2027 — ADMIS", 9.0, 11.0),
    ("s5", "04 Visa & assurance", "Visa d'études + assurance. — Visa d'études Russie · Assurance médicale, couverture 1 an · Carte d'embarquement TUN → MOW", 11.0, 15.0),
    ("s6", "Départ", "Bon voyage !", 15.0, 17.0),
    ("s7", "En vol", "Cap sur Moscou. — Notification RusStudy : « Ton tuteur t'attend à l'arrivée. Bon vol ! »", 17.0, 21.0),
    ("s8", "05 Accueil", "ARRIVÉES · BIENVENUE EN RUSSIE — pancarte RusStudy · ACCUEIL ÉTUDIANTS — Un tuteur bilingue t'attend à l'aéroport.", 21.0, 23.0),
    ("tr", "05 Transfert", "Train ou voiture, jusqu'à ta ville. — MOSCOU → KAZAN — Organisé sur demande · en option — panneau КАЗАНЬ / KAZAN", 23.0, 27.0),
    ("s9", "05 Foyer", "Foyer universitaire. — 1 an inclus — Chambre 412", 27.0, 29.0),
    ("s10", "Université", "Premier jour à l'université. — Carte d'étudiant · Médecine générale · Université d'État · Kazan · Objectif atteint", 29.0, 31.0),
    ("s11", "Prix", "Budget 1ère année : dès 3 500 € · études + installation — Frais universitaires dès 2 200 € · Consulting & orientation · Dossier visa · Accueil aéroport · Foyer universitaire 1 an · Assurance médicale : inclus — Total 1ère année dès 3 500 € — Non inclus · en option sur demande : billet d'avion, train ou voiture jusqu'à ta ville, hôtel & visites à Moscou (sur devis) — Sans frais cachés", 31.0, 37.0),
    ("s12", "CTA", "RusStudy. Études en Russie — Écris-nous sur WhatsApp — +7 996 433 4489 — russieetudes.com — 1ère consultation gratuite", 37.0, 40.0),
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
    ("s8", "animation", "Étape 05 : hall d'arrivée à Moscou — baie vitrée sur la ville de nuit (tour Spasskaïa, dômes de Saint-Basile, neige, balisage) et avion qui atterrit (canvas), panneau d'arrivées à volets BIENVENUE EN RUSSIE, tuteur en pixel art qui se lève derrière la barrière avec la pancarte RusStudy, saute sur le temps et la penche vers la sortie", 20.88, 23.5, "iris", "travelling latéral avec parallaxe vers le transfert", "emotional_beat"),
    ("tr", "animation", "Étape 05 (v3, enrichie en v5) : transfert Moscou → ville universitaire, en option. Canvas pixel en parallaxe (étoiles, soleil couchant, collines, forêt, caténaire, neige) : le train (passagers aux fenêtres) et une voiture orange qui le double, la ville universitaire qui se lève à l'horizon, panneau КАЗАНЬ / KAZAN, jauge MOSCOU → KAZAN ; freinage, la porte du wagon s'ouvre", 23.0, 27.05, "travelling latéral depuis le hall d'arrivée", "la scène suivante s'ouvre dans la porte du wagon (clip-path) + lumière chaude", "build_tension"),
    ("s9", "animation", "Étape 05 : carte-clé sur le lecteur (LED verte), porte 412 qui s'ouvre en 3D sur une chambre pixel (lampe, neige à la fenêtre), puce « 1 an inclus »", 26.72, 29.1, "porte du wagon (clip-path)", "travelling avant dans la fenêtre + flash blanc", "deliver_payload"),
    ("s10", "broll", "Premier jour : photo d'amphithéâtre (site) en Ken Burns, typo cinétique lettre par lettre, carte d'étudiant en 3D avec reflet, étoiles pixel ; la barre de progression se complète", 28.98, 31.0, "flash blanc", "cut sec", "resolution"),
    ("s11", "animation", "Prix : odomètre 3 500 € (flou directionnel), pastille « études + installation », ticket de caisse imprimé ligne par ligne (6 postes inclus, total, puis « non inclus · en option sur demande » : billet d'avion, train ou voiture, hôtel & visites à Moscou — sur devis), tampon SANS FRAIS CACHÉS", 31.0, 37.05, "cut sec", "chute avant l'arrêt de l'orchestre", "deliver_payload"),
    ("s12", "text_card", "Ville pixel de nuit (rappel du spot 15 s), logo RusStudy. sur l'accord final, CTA WhatsApp, numéro et site tapés, tap de la main pixel", 37.0, 40.0, "cut sur l'accord final (37,0 s)", "fin", "call_to_action"),
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
        asset("img-amphitheatre-16x9", "image", "hyperframes-16x9/assets/img/amphitheatre_16x9.jpg", "Unsplash (même photo, recadrage 16:9)", "s10", license="Unsplash License",
              original_url="https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0",
              generation_summary="Original 2400 x 3600, recadré 2400 x 1350 (y = 700) puis 1920 x 1080 (lanczos)"),
        asset("font-space-grotesk", "font", "hyperframes/assets/fonts/SpaceGrotesk-latin.woff2", "Google Fonts", "all", license="SIL Open Font License 1.1"),
        asset("map-land-mask", "diagram", "scripts/make_dotmap.py", "global-land-mask 1.0.0 (NOAA GLOBE 1 km)", "s7", license="MIT (package) / public domain (GLOBE data)",
              generation_summary="Grille 54 x 96 terre/mer embarquée dans index.html (MAP_ROWS) ; 96 x 54 pour le 16:9 (scripts/map_rows_16x9.js) ; régénérables avec scripts/make_dotmap.py"),
        asset("music-funky", "music", "assets/music/11_funky.mp3", "pixabay_music", "all", provider="pixabay", license="Pixabay Content License",
              original_url="https://cdn.pixabay.com/audio/2026/01/06/audio_437fcd7b2d.mp3", duration_seconds=139.8,
              generation_summary="120 BPM ; montage sur mesures : piste 15,026–32,026 s (drop A à 1,0 s) puis 76,025–94,025 s (break 17, montée 19, drop B à 21,0 s, groove pendant le transfert) puis 62,025–67,025 s (break de fin, arrêt + accord de mi à 37,0 s)"),
        asset("sfx-bundled", "sfx", "../../.agents/skills/hyperframes-media/assets/sfx", "hyperframes-media bundled library", "all", provider="pixabay", license="Pixabay Content License"),
        asset("sfx-synth", "sfx", "assets/audio/sfx", "scripts/build_audio.py", "all",
              generation_summary="Frappe clavier, papier, tampons, déchirure, décollage, carillon d'aéroport, vent, panneau à volets (timing identique à la composition), rails, moteur, klaxon de train, bip de badge, odomètre, imprimante — synthèse numpy déterministe"),
        asset("soundtrack", "audio", "hyperframes/assets/audio/soundtrack.wav", "scripts/build_audio.py", "all", duration_seconds=DUR, format="wav",
              generation_summary="Musique + 115 cues SFX, automation de gain (vol, accord final), ducking 3 dB, limiteur suréchantillonné, -14 LUFS / -2,5 dBTP ; même bande-son pour les deux formats"),
        asset("composition", "animation", "hyperframes/index.html", "hyperframes (atelier, GSAP 3.14)", "all",
              generation_summary="Composition écrite à la main (9:16, source unique), une seule timeline GSAP déterministe, 13 scènes + HUD de progression"),
        asset("composition-16x9", "animation", "hyperframes-16x9/index.html", "scripts/make_landscape.py", "all",
              generation_summary="Version YouTube 1920 x 1080 dérivée de la composition verticale : remplacements vérifiés, zones portrait mises à l'échelle à droite, titres à gauche, HUD en barre haute"),
        asset("composition-60s", "animation", "hyperframes-60s/index.html", "scripts/make_slow.py", "all",
              generation_summary="Version 60 s au rythme ralenti (v4) : la timeline de 40 s est rejouée 1,5 fois plus lentement par une timeline racine qui la parcourt ; data-start / data-duration x 1,5 ; idem pour hyperframes-60s-16x9/"),
        asset("soundtrack-60s", "audio", "assets/audio-60s/soundtrack.wav", "scripts/build_audio.py --slow", "all", duration_seconds=DUR * 1.5, format="wav",
              generation_summary="Même musique remontée sur 60 s (piste 14,526–40,026 puis 74,025–102,025 puis 62,025–68,525 : drop A à 1,5 s, drop B à 31,5 s, accord final à 55,5 s) ; cues SFX et sons synthétisés étirés x 1,5 ; -14 LUFS"),
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


def out(path, fmt, fps, platform, resolution="1080x1920", duration=DUR):
    f = ROOT / path
    return {"path": path, "format": fmt, "codec": "h264" if fmt == "mp4" else None, "audio_codec": "aac" if fmt == "mp4" else None,
            "resolution": resolution, "fps": fps, "duration_seconds": duration if fmt == "mp4" else 0,
            "file_size_bytes": f.stat().st_size if f.exists() else 0, "platform_target": platform}


render_report = {"version": "1.0", "render_grammar": "animation-first", "outputs": []}
for o in [out(f"renders/{NAME}_60fps.mp4", "mp4", 60, "TikTok / YouTube Shorts / Reels (master)"),
          out(f"renders/{NAME}_30fps.mp4", "mp4", 30, "Instagram Reels / Facebook / Stories"),
          out(f"renders/{NAME16}_60fps.mp4", "mp4", 60, "YouTube (16:9)", "1920x1080"),
          out(f"renders/{NAME60}_60fps.mp4", "mp4", 60, "Rythme ralenti 60 s — TikTok / Shorts / Reels", duration=DUR * 1.5),
          out(f"renders/{NAME60_16}_60fps.mp4", "mp4", 60, "Rythme ralenti 60 s — YouTube (16:9)", "1920x1080", DUR * 1.5)]:
    if o["file_size_bytes"]:  # list only the renders that exist
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
             opt("telephone-continu", "Tout dans l'interface du téléphone", 0.55, "cohérent avec WhatsApp", "monotone visuellement sur 40 s, ne montre pas l'étendue du motion design"),
             opt("carte-seule", "Trajet sur carte animée", 0.4, "lisible", "ne montre pas les étapes administratives (dossier, admission, visa)")],
            "parcours-objets", "Voir artifacts/art-direction.md (storyboard en 13 scènes calé sur la grille musicale).", False, 0.85),
        dec("d3", "proposal", "render_runtime_selection", "Moteur de composition",
            [opt("hyperframes", "HyperFrames (HTML/CSS/GSAP)", 0.9, "même moteur que la v1 : réutilisation de la ville pixel, retouche identique"),
             opt("remotion", "Remotion (React)", 0.7, "disponible", "réécriture complète sans gain pour ce concept")],
            "hyperframes", "Continuité avec la v1 (scripts de rendu et de retouche identiques).", False, 0.85),
        dec("d4", "proposal", "composition_mode", "Mode d'écriture",
            [opt("atelier", "atelier (composition écrite à la main)", 0.95, "pièce vitrine de marque"),
             opt("templated", "scènes types", 0.2, "rapide", "rendu générique")],
            "atelier", "Une seule timeline GSAP déterministe, scènes en <section> horodatées.", False, 0.9),
        dec("d5", "assets", "music_source", "Musique",
            [opt("pixabay-funky", "Pixabay « Funky » réutilisée et remontée à 40 s", 0.85, "signature sonore commune aux deux spots ; la structure (build, drop A, break, drop B, arrêt sur accord) colle au récit"),
             opt("autre-piste", "Autre piste Pixabay", 0.5, "variété", "perd la continuité de marque entre les deux spots")],
            "pixabay-funky", "Drop A à 1,0 s (envoi du message), break pendant le vol, drop B à 21,0 s (arrivée), groove prolongé de 2 mesures pour le transfert, arrêt + accord à 37,0 s (logo).", False, 0.8),
        dec("d6", "assets", "provider_selection", "Sound design",
            [opt("bundled+synth", "SFX HyperFrames (Pixabay) + synthèse maison", 0.85, "gratuit, déterministe, accordé à la musique, timing exact des volets et de l'odomètre")],
            "bundled+synth", "115 cues calés sur les événements GSAP ; sons tonals accordés en la mixolydien / mi.", False, 0.8),
        dec("d7", "compose", "visual_accuracy_check", "Prix et promesses",
            [opt("client-price", "Prix donné par le client : dès 3 500 € la 1ère année, tout compris (frais universitaires dès 2 200 € inclus)", 0.8, "lecture la plus naturelle du message du client"),
             opt("price-plus-fees", "3 500 € d'accompagnement en plus des 2 200 € de frais", 0.2, "autre lecture possible", "le client écrit que les 3 500 € incluent consulting, accueil, foyer, assurance et visa, et que 2 200 € est le minimum universitaire")],
            "client-price", "Confirmé et précisé par le client (v5) : billet d'avion, transport interne (train ou voiture), hôtel et visites à Moscou non inclus — listés sur le ticket en option, sur devis ; « tout compris » retiré. Interface façon WhatsApp sans logo ; promesses reprises du site (appel 15 min, traduction assermentée, lettre d'invitation d'État, tuteur bilingue, sans frais cachés).", False, 0.7),
        dec("d8", "compose", "motion_commitment", "Cadence de rendu",
            [opt("60fps", "Master 60 fps", 0.85, "mouvements rapides plus nets (whip-pan, volets, odomètre)"),
             opt("30fps", "Variante 30 fps", 0.75, "cadence la plus sûre pour Instagram/Facebook", "fournie en variante, pas en master")],
            "60fps", "Les deux versions sont livrées.", False, 0.85),
        dec("d9", "compose", "concept_selection", "Transport interne (v3)",
            [opt("train+voiture", "Un seul plan en parallaxe : le train (passagers aux fenêtres) et une voiture qui le double", 0.85, "le client a écrit « train ou voiture » : les deux modes sont montrés sans choisir"),
             opt("train", "Train seul", 0.6, "plus simple", "laisse croire que le transfert se fait toujours en train"),
             opt("carte", "Trajet sur la carte de vol", 0.4, "réutilise la scène S7", "redondant avec le vol, pas de sentiment de voyage terrestre")],
            "train+voiture", "Scène TR de 4 s (2 mesures) entre l'accueil et le foyer ; ville d'exemple Kazan (illustratif, comme Médecine générale) ; la musique gagne 2 mesures de groove et la fin passe de 4 à 3 s pour rester à 40 s.", False, 0.8),
        dec("d10", "compose", "capability_extension", "Version YouTube 16:9 (v3)",
            [opt("generateur", "Dériver le 16:9 de la composition verticale par script (remplacements vérifiés + zones portrait)", 0.85, "une seule source à retoucher : textes, couleurs et timings se propagent ; même bande-son"),
             opt("copie", "Copier et adapter la composition à la main", 0.5, "liberté totale de mise en page", "deux fichiers à maintenir, les retouches divergent"),
             opt("recadrage", "Recadrer / encadrer la vidéo verticale (bandes floues)", 0.2, "immédiat", "rendu amateur sur YouTube, texte trop petit")],
            "generateur", "scripts/make_landscape.py produit hyperframes-16x9/index.html ; le script s'arrête si un élément attendu a changé dans la version verticale.", False, 0.85),
        dec("d11", "compose", "motion_commitment", "Version au rythme moins accéléré (v4)",
            [opt("ralenti-x1.5", "Même film rejoué 1,5 fois plus lentement (60 s), musique remontée", 0.85, "scènes 1,5 fois plus longues et animations plus douces ; chaque image reste identique à celle de la version 40 s ; les retouches se propagent"),
             opt("pauses", "Allonger seulement les temps de pause entre les animations", 0.6, "animations aussi vives qu'avant", "réécriture complète de la timeline ; deux montages à maintenir"),
             opt("moins-de-scenes", "Retirer des scènes pour garder 40 s", 0.3, "plus court", "enlève des étapes du parcours demandé par le client")],
            "ralenti-x1.5", "Demande du client : « une version où le rythme est moins accéléré ». scripts/make_slow.py + build_audio.py --slow ; drop A à 1,5 s, drop B à 31,5 s, logo sur l'accord final à 55,5 s.", False, 0.8),
        dec("d12", "compose", "visual_accuracy_check", "Ce que le prix n'inclut pas (v5)",
            [opt("ticket-options", "Section « Non inclus · en option sur demande » en bas du ticket, valeurs « sur devis »", 0.85, "le spectateur voit au même endroit ce qui est inclus et ce qui ne l'est pas ; cohérent avec « sans frais cachés »"),
             opt("prix-moyen", "Afficher un prix moyen par option", 0.4, "plus concret", "le billet d'avion varie selon la date ; un montant dans une pub se lit comme une promesse — à ajouter seulement avec des montants fournis et tenus par le client"),
             opt("asterisque", "Astérisque et mention en petits caractères", 0.3, "discret", "illisible sur mobile")],
            "ticket-options", "Le client précise que les 3 500 € n'incluent ni le billet d'avion, ni le transport interne (train ou voiture), ni l'hôtel et les visites à Moscou ; pastille « études + installation » à la place de « tout compris » ; sous-titre du transfert « Organisé sur demande · en option ».", False, 0.85),
        dec("d13", "compose", "motion_commitment", "Arrivée à Moscou et transition vers le transfert (v5)",
            [opt("hall-travelling", "Hall d'arrivée avec vue sur Moscou + travelling latéral vers le train", 0.85, "situe l'arrivée à Moscou, humanise l'accueil (tuteur), transition continue dans le sens du voyage"),
             opt("flip-3d", "Garder le retournement 3D", 0.3, "déjà en place", "laissait voir un vide noir, surtout dans la version 60 s (remarque du client)")],
            "hall-travelling", "Retour du client : la transition vers 33–34 s (version 60 s) n'était pas bonne et l'arrivée / le transport devaient être plus travaillés.", False, 0.8),
    ],
}

SCHEMAS = REPO / "schemas/artifacts"
for name, data in [("brief", brief), ("script", script), ("scene_plan", scene_plan), ("asset_manifest", asset_manifest),
                   ("edit_decisions", edit_decisions), ("render_report", render_report), ("decision_log", decision_log)]:
    schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text())
    jsonschema.validate(data, schema)
    (ART / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"ok  {name}.json")
