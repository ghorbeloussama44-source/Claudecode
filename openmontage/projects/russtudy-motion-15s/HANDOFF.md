# RusStudy — spot motion design 15 s — notes de reprise

Client : **RusStudy** (russieetudes.com), agence d'orientation vers les universités
publiques russes pour étudiants tunisiens. Objectif : spot social vertical qui fait
cliquer vers le site pour la **1ère consultation gratuite**.

## Livrables (versionnés)

| Fichier | Usage |
|---|---|
| `renders/russtudy_motion_15s_60fps.mp4` | **Master** 1080×1920, 60 fps, H.264 High ~8,7 Mb/s, AAC 256k, −14 LUFS / −1,9 dBTP — TikTok, Shorts, Reels |
| `renders/russtudy_motion_15s_30fps.mp4` | Même montage en 30 fps (Instagram / Facebook si besoin) |
| `renders/cover_hook.png` | Couverture « Bac en poche ? BUSINESS en Russie. » |
| `renders/cover_fin_cta.png` | Couverture plan final (logo + CTA + URL) |

## Structure

- `artifacts/art-direction.md` — direction artistique, taste profile, storyboard.
- `artifacts/*.json` — artefacts canoniques OpenMontage validés contre `schemas/artifacts/`
  (brief, script, scene_plan, asset_manifest, edit_decisions, render_report,
  decision_log). Régénérés par `scripts/write_artifacts.py`.
- `artifacts/sfx_cues.json` — les 53 cues de sound design (temps = événements GSAP).
- `hyperframes/index.html` — **la composition** (HyperFrames, mode atelier, une seule
  timeline GSAP déterministe). Polices, GSAP et photos sont locaux dans
  `hyperframes/assets/` (aucun accès réseau au rendu).
- `scripts/build_audio.py` — montage musical sur mesures + synthèse des SFX +
  mixage (ducking, limiteur, loudnorm linéaire −14 LUFS / −1,5 dBTP max).

## Re-rendre

```bash
cd openmontage/projects/russtudy-motion-15s
python3 scripts/build_audio.py                      # -> assets/audio/soundtrack.wav
cp assets/audio/soundtrack.wav hyperframes/assets/audio/
cd hyperframes
npx --yes hyperframes@0.8.133 lint                  # 0 erreur attendue
npx --yes hyperframes@0.8.133 snapshot --at 1,3.5,6.3,8.2,9.8,11.6,14.9
npx --yes hyperframes@0.8.133 render --quality high --fps 60 --output ../renders/_hf.mp4
cd .. && ffmpeg -y -i renders/_hf.mp4 -i assets/audio/soundtrack.wav -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart -t 15 renders/russtudy_motion_15s_60fps.mp4
```

Le remux final est volontaire : le pipeline audio de HyperFrames ressort le son
~1,4 dB trop bas (−15,4 LUFS) ; on remplace donc la piste par le master exact
(synchro vérifiée par corrélation croisée : décalage 0 échantillon).

## Grille musicale (ne pas casser)

Piste « Funky » (Pixabay, `assets/music/candidates/11_funky.mp3`), **120,00 BPM
mesurés** (1 temps = 0,5 s). Attaques ~18 ms avant la grille librosa ; coupes 10 ms
avant chaque attaque :

- vidéo 0–9 s ← piste 15,026–24,026 s (fin de build, **drop à 1,0 s**)
- vidéo 9–15 s ← piste 60,025–66,025 s (raccord masqué par le volet à 9,0 s,
  **arrêt de l'orchestre + accord de mi tenu à 13,0 s**, remonté de +14 dB)

Temps forts : 1, 3, 5, 7, 9, 11, 13 s — chaque scène dure une mesure. Si on retouche
un timing visuel, déplacer le cue correspondant dans `sfx_cues.json` et relancer
`build_audio.py`. Les SFX tonals sont accordés (pops mi→fa♯→sol♯→la, ping en mi,
chime en la = résolution sur la tonique).

## Constantes mesurées (à refaire si le texte change)

Positions des points ronds de Space Grotesk, mesurées une fois dans Chromium avec la
police chargée (aucune mesure DOM au rendu, exigence de déterminisme) :

- point de « en Russie. » (196 px) : centre (958,2 ; 1132,4) — origine du portail
  circulaire qui révèle la scène prix ;
- point de « Change ta vie » (116 px) : (894,5 ; 822) ;
- point de « RusStudy » (176 px) : (920,9 ; 652,3).

## Choix et garde-fous

- Moteur : **HyperFrames** retenu (Remotion était aussi disponible) — typo cinétique,
  clip-path, MotionPath, synchro beat. Le choix est consigné dans `decision_log.json`
  comme non encore validé par le client.
- Logo fidèle au code du site : « Rus » couleur du texte, « Study » violet `#a855f7`,
  **point couleur du texte** (blanc sur fond sombre) — le point violet qui vole se
  recolore en blanc à l'atterrissage.
- La photo des diplômés a été prise à Singapour : elle est légendée « Objectif : ton
  diplôme » (comme sur le site), jamais présentée comme la Russie. Les visages des
  témoignages du site (photos stock) ne sont pas utilisés.
- Chiffres et promesses repris tels quels du site (dès 2 200 €/an, +1 200 étudiants,
  40+ universités, visa garanti par contrat, etc.) — à revalider avec le client avant
  diffusion payante.
- Licences : photos Unsplash (via le site), Space Grotesk (OFL), musique et SFX
  Pixabay Content License. Certaines pistes Pixabay sont enregistrées dans Content ID
  YouTube : en cas de réclamation, la contester avec la licence Pixabay.

## Pièges rencontrés

- Chromium (Playwright) ne faisait pas confiance à la CA du proxy : ajout de
  `/root/.ccr/agent-proxy-ca.crt` dans `~/.pki/nssdb` via `certutil` (paquet
  `libnss3-tools`). Ne jamais ignorer les erreurs de certificat.
- `npx hyperframes` dans un dossier nommé `hyperframes/` résout le package local :
  toujours appeler la version épinglée `npx --yes hyperframes@0.8.133 …`.
- Chrome du moteur : `npx hyperframes browser ensure` au premier usage.
- `alimiter` d'ffmpeg retarde le signal de 4 ms sans `latency=1` (activé).
- Éléments animés seulement en scale/opacity avec un état initial visible : les
  positionner en CSS et mettre `opacity: 0` par défaut (sinon un petit cercle reste
  visible avant l'animation).
- La scène nuit n'apparaît qu'une fois la mosaïque de pixels complète (11,02 s),
  sinon flash visible dans les zones non couvertes.

## Pistes v2

Version arabe (le site existe en AR, police Tajawal), déclinaison 4:5 / 1:1 pour le
fil, variantes de hook pour A/B test (« Médecine dès 3 500 €/an », « Visa garanti
par contrat »), voix off si un fournisseur TTS est configuré.
