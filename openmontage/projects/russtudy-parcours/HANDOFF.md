# RusStudy — « Le parcours » (37 s) — notes de reprise

Deuxième spot RusStudy (russieetudes.com), suite du 15 s (`../russtudy-motion-15s`).
Le film suit le prospect **du premier message WhatsApp jusqu'au premier jour à
l'université**, en passant par les 5 étapes du site, puis donne le prix de la 1ère année
et renvoie vers WhatsApp.

## Livrables (versionnés)

| Fichier | Usage |
|---|---|
| `renders/russtudy_parcours_37s_60fps.mp4` | **Master** 1080×1920, 60 fps, H.264 + AAC 256k, −14 LUFS — TikTok, Shorts, Reels |
| `renders/russtudy_parcours_37s_30fps.mp4` | Même montage en 30 fps (Instagram / Facebook si besoin) |
| `renders/cover_hook.png` | Couverture « Tout commence par un message. » |
| `renders/cover_prix.png` | Couverture prix + ticket (dès 3 500 €) |
| `renders/cover_fin_cta.png` | Couverture plan final (logo + WhatsApp + numéro + site) |

## À valider par le client avant diffusion payante

- **Prix** : affiché « 1ère année dès 3 500 € tout compris ». Lecture retenue du brief :
  les 3 500 € **incluent** les frais universitaires (dès 2 200 €), le consulting /
  orientation, le dossier visa, l'accueil aéroport, le foyer 1 an et l'assurance
  médicale (c'est exactement la liste du ticket). Si les 3 500 € s'ajoutent aux frais
  universitaires, modifier le ticket et le total (voir tableau ci-dessous).
- « Tout compris » = les postes du ticket ; billet d'avion et vie courante non inclus.
- « Sans frais cachés » reprend l'engagement « Transparence sur les coûts » du site.
- Le cas montré (Médecine générale, Moscou, chambre 412, dossier RS-2026-0412, vol
  RS 2026) est **illustratif**, comme l'exemple de profil.

## Retrouver le projet

- Branche Git : `claude/install-openmontage-263px9`
  (`git fetch origin claude/install-openmontage-263px9 && git checkout claude/install-openmontage-263px9`).
- Version livrée **v2 = commit `c6acc34`** (vidéo + outils de retouche). Revoir cette
  version telle quelle : `git checkout c6acc34 -- openmontage/projects/russtudy-parcours` ;
  voir ce qui a changé depuis : `git diff c6acc34 -- openmontage/projects/russtudy-parcours`.
- Dossier : `openmontage/projects/russtudy-parcours/`. Kit de marque :
  `../russtudy-motion-15s/artifacts/brand-kit.md`. Direction artistique et storyboard :
  `artifacts/art-direction.md`.

## Retoucher en 3 étapes

1. Modifier `hyperframes/index.html` (texte, couleurs, timings) et, si un timing visuel
   bouge, le cue sonore correspondant dans `artifacts/sfx_cues.json` (`at`).
2. Contrôler vite : `bash scripts/render_all.sh --draft` → `renders/draft.mp4` (≈ 2 min),
   ou des images fixes : `cd hyperframes && npx --yes hyperframes@0.8.133 snapshot --at 1,5,8,10,13,16,19,22,24,26,31,36`.
3. Livrer : `bash scripts/render_all.sh` → bande-son, lint, rendus 60 et 30 fps, remux du
   son master, couvertures, artefacts (≈ 6 min).

Prérequis d'un conteneur neuf : Node 22 + ffmpeg ; le script installe les dépendances
Python (`scripts/requirements.txt`) et le Chrome de HyperFrames si besoin. Retouche à la
souris en local : `cd hyperframes && npx --yes hyperframes@0.8.133 preview` (Studio).

## Structure du film (grille musicale : 1 temps = 0,5 s, 1 mesure = 2 s)

| Temps | Scène (`<section>`) | Technique | Transition de sortie |
|---|---|---|---|
| 0–3 | `#s1` Le message | conversation façon WhatsApp : frappe, **envoi sur le drop (1,0)**, coches lues, « écrit… », réponses | tap sur « Réserver un appel gratuit » → ripple |
| 3–7 | `#s2` 01 Consultation | appel 15 min (chrono accéléré, onde), scan du profil, coches tracées | push vertical |
| 7–9 | `#s3` 02 Dossier | documents en arcs, classement, tampons TRADUIT / LÉGALISÉ | rideau or |
| 9–11 | `#s4` 03 Admission | enveloppe 3D, lettre d'invitation, tampon ADMIS, confettis pixel | whip-pan flouté |
| 11–15 | `#s5` 04 Visa & assurance | passeport 3D, vignette visa, carte d'assurance ; carte d'embarquement (`#pl`) | déchirure du billet |
| 15–17 | `#s6` Départ | décollage sur MotionPath, nuages pixel | mur de nuages (`#cw`) |
| 17–21 | `#s7` En vol | carte en pixels Tunis → Moscou, notification RusStudy | plongée + iris vert sur le **drop B (21,0)** |
| 21–23 | `#s8` 05 Accueil | panneau à volets BIENVENUE EN RUSSIE, pancarte du tuteur | flip 3D plein écran |
| 23–25 | `#s9` 05 Foyer | carte-clé, porte 412 en 3D, chambre pixel, « 1 an inclus » | travelling dans la fenêtre + flash |
| 25–27 | `#s10` Université | photo d'amphi, typo lettre à lettre, carte d'étudiant | cut |
| 27–33 | `#s11` Prix | odomètre 3 500 €, ticket imprimé ligne à ligne, tampon | chute |
| 33–37 | `#s12` CTA | ville pixel, **logo sur l'accord final (33,0)**, WhatsApp, numéro, site | fin |

`#hud` (2,95–27 s) = barre de progression en 5 segments aux couleurs des étapes du site.

## Où modifier quoi (`hyperframes/index.html` sauf mention)

Repères : bannières `/* === S1 — … */` (CSS), `<!-- === S1 — … -->` (HTML) et
`// === S1 — …` (animation) pour chaque scène.

| Élément | Où | Attention |
|---|---|---|
| Message tapé | JS `S1_TXT` + HTML `#m-out .l` (2 lignes de la bulle) | ≤ ~34 caractères pour tenir dans le champ ; la frappe dure 0,72 s (`renderS1`) et le cue `s1-typing` frappe 34 touches |
| Réponses du chat | HTML `#m-r1 .l`, `#m-r2` (`#r2-t1`, `#r2-t2`, `#r2-btn`), carte `#chat-biz` | bulles à hauteur fixe (2 lignes) |
| Titres des scènes | HTML `.title .tw` de chaque section | 104 px, ≤ ~900 px de large |
| Libellés des étapes (barre) | HTML `#hl1`…`#hl7` | texte du site (« Votre parcours en 5 étapes ») |
| Profil / plan | HTML `.prow` (`.pt1`, `.pt2`), `#s2-pm`, `#s2-ps` | cas illustratif |
| Documents du dossier | HTML `#sh0`…`#sh3 .band` | 2 lignes max par bandeau |
| Lettre d'admission | HTML `#lt-k`, `#lt-t`, `#lt-s` | |
| Visa / assurance / billet | HTML `#visa-*`, `#ins-*`, `#bp-*` | |
| Villes et trajet | JS `MAP_ROWS` (régénérer avec `scripts/make_dotmap.py`), `R0…R3` + chemin `M220,1320 C420,1150 600,720 845,698` (3 occurrences) + épingles `#pin-*`, étiquettes `#lb-tun`, `#lb-mow` | la caméra (`#s7-cam`) vise Tunis puis Moscou : recalculer ses x/y si une ville bouge |
| Notification en vol | HTML `#nt-b` | |
| Panneau à volets | JS `FLAP` (2 mots de 9 cases) | le cue `s8-split-flap` est resynthétisé avec le même timing (`build_audio.py`) |
| Foyer | HTML `#d-plate`, `#kc-n`, puce `#s9-chip` | |
| Carte d'étudiant | HTML `#scard` (`.sc-f`) | |
| **Prix (gros chiffre)** | JS `ODO_TARGET` (chiffres) + `ODO_LAND` (arrivée) | 4 chiffres ; sinon ajouter une colonne `.odo` et recalculer ; mettre aussi à jour `odo_ticks` dans `build_audio.py` |
| **Ticket** (postes, montants, total) | HTML `#rc-paper .rc-l`, `.rc-tot` | 6 lignes de 66 px ; si on en ajoute, allonger `#rc-paper`/`#rc-mask` et les pas d'avance (`paper feed`) |
| Pastille / tampon prix | HTML `#s11-pill`, `#st-tc` | |
| CTA, numéro, site | HTML `#wa-t`, `#cta-chip` ; JS `TEL_TXT`, `URL_TXT`, `TAG_TXT` | CTA ≤ ~700 px à 50 px |
| Timings | positions GSAP (secondes) sous chaque bannière JS | rester sur la grille de 0,5 s ; reporter dans `sfx_cues.json` |
| Musique | `scripts/build_audio.py` → `SEGMENTS` + automation `auto` | coupes 10 ms avant une attaque |
| Volume / mix | `artifacts/sfx_cues.json` (`gain_db`), `build_audio.py` (ducking, limiteur) | cible −14 LUFS, normalisation linéaire |

## Grille musicale (ne pas casser)

Piste « Funky » (Pixabay, `assets/music/11_funky.mp3`), 120 BPM :

- vidéo 0–17 ← piste 15,026–32,026 (fin de build, **drop A à 1,0**, groove)
- vidéo 17–31 ← piste 76,025–90,025 (break de batterie 17, montée de basse 19, **drop B à 21,0**)
- vidéo 31–37 ← piste 62,025–68,025 (break, **arrêt + accord de mi à 33,0**)

Automation de gain : +6 dB sur le break (17–19), retour à 0 dB juste avant 21,0 ;
accord final +14 dB puis +19 dB à la fin. Les SFX tonals sont accordés (pops mi→fa♯→
sol♯→la, ping et notification en mi, carillon en la, ding-dong d'aéroport mi→do♯).

## Choix et garde-fous

- Interface de chat **façon** WhatsApp, sans logo WhatsApp (marque déposée) ; le nom
  « WhatsApp » n'apparaît que dans le texte du CTA et de l'appel (comme sur le site).
- Drapeaux tunisien et russe dessinés en SVG (seules couleurs hors charte, pour la lisibilité).
- Pas de visage : avatars en pixel art génériques.
- Photo de l'amphithéâtre : celle du site (Unsplash). Carte : masque terre/mer GLOBE
  (via `global-land-mask`, MIT) converti en grille embarquée — aucune donnée chargée au rendu.
- Licences : Space Grotesk (OFL), musique et SFX Pixabay Content License (contester une
  éventuelle réclamation Content ID avec la licence Pixabay).

## Pièges rencontrés

- Mêmes que la v1 (CA du proxy pour Chromium, `npx --yes hyperframes@0.8.133`, remux du son).
- Éléments animés depuis l'extérieur de l'écran : leur position de départ doit être
  **entièrement** hors cadre (rotation comprise), sinon ils dépassent avant leur entrée.
- `loudnorm` repasse en mode dynamique si les crêtes inter-échantillons dépassent la
  cible : le limiteur tourne en 192 kHz (suréchantillonné) pour rester linéaire.
- `npx hyperframes validate` signale des contrastes sur les libellés de la barre qui
  sont hors du masque (invisibles) : faux positifs connus.
