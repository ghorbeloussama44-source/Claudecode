# RusStudy — série réseaux sociaux (TikTok · Instagram · Facebook)

9 vidéos verticales × 2 langues (français + derja), 1080×1920, 30 i/s, pensées pour être publiées avec une
voix off (témoignages réels ou conseiller RusStudy). Musique douce incluse à −20 LUFS.

| # | Vidéo | Série | Durée |
|---|---|---|---|
| 01 | Témoignage étudiant — 4 questions | témoignage | 40,5 s |
| 02 | Parole de parent — 3 questions | témoignage | 32,5 s |
| 03 | Ma première semaine en Russie | témoignage | 36 s |
| 04 | Le vrai prix de la 1ère année | conseil | 26 s |
| 05 | De Tunis à ta fac : 5 étapes | conseil | 30,5 s |
| 06 | Les 4 documents à préparer | conseil | 19,5 s |
| 07 | Parents : qui s'occupe de votre enfant ? | conseil | 26 s |
| 08 | Tu nous écris sur WhatsApp, et après ? | conseil | 26 s |
| 09 | Rentrée 2026–2027 : places limitées | conseil | 18,5 s |

- Vidéos : `renders/<slug>_fr.mp4`, `renders/<slug>_derja.mp4` ; couvertures `renders/covers/`
- Kit de publication : `kit/00_pages.md` (pages, bios, liens, calendrier, pub, WhatsApp),
  `kit/01_voix_off.md` (scripts minutés), `kit/02_legendes.md` (légendes + hashtags), `kit/images/`

## Fonctionnement

- `episodes/*.json` : le contenu de chaque vidéo (scènes typées, textes FR + derja, voix off, légendes).
- `engine/style.css` + `engine/lib.js` : le moteur commun (mise en page, thèmes nuit / crème / encre,
  animations GSAP déterministes, icônes pixel). Le derja se met en miroir via `direction: rtl` sur `#root`
  (jamais sur `<html>` : HyperFrames rend alors une vidéo vide).
- `scripts/build.py` : écrit un projet HyperFrames par vidéo dans `build/<slug>-<fr|ar>/` ; la taille de chaque
  titre est calculée d'après la largeur réelle du texte mesurée dans Chromium (`scripts/measure.cjs`).
- `scripts/beds.py` : musique de fond coupée à la durée, fondus, −20 LUFS (`assets/music`, licence Pixabay).
- `scripts/render_all.sh [numéros]` : musique → build → lint → rendu → remux du son exact → couvertures.
- `scripts/kit.py` : documents voix off + légendes ; `scripts/stills.py` : images des pages (`scripts/shoot.cjs`).

```bash
bash scripts/render_all.sh          # les 18 vidéos (~20 min)
bash scripts/render_all.sh 04 09    # seulement les épisodes 04 et 09
python3 scripts/kit.py && python3 scripts/stills.py
```

Musiques (Pixabay Content License) : « Hope Piano », « Lofi Chill », « 11_funky ».
