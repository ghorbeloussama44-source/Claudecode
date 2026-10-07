# RusStudy — « Le parcours » (40 s et 60 s, vertical + YouTube 16:9, français + derja) — notes de reprise

Deuxième spot RusStudy (russieetudes.com), suite du 15 s (`../russtudy-motion-15s`).
Le film suit le prospect **du premier message WhatsApp jusqu'au premier jour à
l'université**, en passant par les 5 étapes du site — dont, depuis la v3, le **transfert de
Moscou vers la ville de l'université en train ou en voiture** — puis donne le prix de la
1ère année et renvoie vers WhatsApp. Deux formats, une seule composition à retoucher :
le vertical 9:16 (master) et la version **YouTube 16:9** qui en est générée. Depuis la v4,
chaque format existe aussi en **version 60 s au rythme moins accéléré** (le même film joué
1,5 fois plus lentement, sur une bande-son de 60 s). Depuis la v6, **le prix est en dinars
tunisiens** (« dès 12 000 DT ») et le film existe aussi **en arabe tunisien (derja)**, généré
depuis les compositions françaises. Le client garde les **versions 60 s** : ce sont elles qui
sont rendues en v6 (les rendus 40 s du dépôt sont ceux de la v5, prix en euros).

## Livrables (versionnés)

| Fichier | Usage |
|---|---|
| `renders/russtudy_parcours_40s_60fps.mp4` | **Master vertical** 1080×1920, 60 fps, H.264 + AAC 256k, −14 LUFS — TikTok, Shorts, Reels |
| `renders/russtudy_parcours_40s_30fps.mp4` | Même montage en 30 fps (Instagram / Facebook si besoin) |
| `renders/russtudy_parcours_40s_youtube_16x9_60fps.mp4` | **YouTube** 1920×1080, 60 fps, même bande-son |
| `renders/russtudy_parcours_60s_60fps.mp4` | **Rythme ralenti** (v4) vertical 1080×1920, 60 s, 60 fps |
| `renders/russtudy_parcours_60s_youtube_16x9_60fps.mp4` | **Rythme ralenti** (v4) YouTube 1920×1080, 60 s, 60 fps |
| `renders/russtudy_parcours_60s_derja_60fps.mp4` | **Arabe tunisien** (v6) vertical 1080×1920, 60 s, 60 fps |
| `renders/russtudy_parcours_60s_derja_youtube_16x9_60fps.mp4` | **Arabe tunisien** (v6) YouTube 1920×1080, 60 s, 60 fps |
| `renders/thumbnail_youtube.jpg`, `thumbnail_youtube_ar.jpg` | Miniatures YouTube 1280×720 (plan du prix), français et derja |
| `renders/cover_hook.png`, `cover_transfert.png`, `cover_prix.png`, `cover_fin_cta.png` | Couvertures verticales (accroche, transfert, prix + ticket, plan final), tirées de la version 60 s |
| `renders/cover_16x9_transfert.png`, `cover_16x9_prix.png`, `cover_16x9_fin_cta.png` | Les mêmes plans en 16:9 |
| `renders/cover_ar_*.png`, `cover_ar_16x9_*.png` | Les mêmes couvertures en derja |

Les rendus `russtudy_parcours_40s_*` datent de la v5 (prix en euros) : relancer
`bash scripts/render_all.sh` pour les mettre à jour si on en a de nouveau besoin.

## À valider par le client avant diffusion payante

- **Prix (v6, en dinars tunisiens)** : « 1ère année dès 12 000 DT » (montant donné par le
  client, équivalent de 3 500 €) + pastille « études + installation ». **Inclus** (7 lignes
  cochées du ticket, **sans montant par ligne** depuis la v7 : le client ne veut pas que l'on
  puisse calculer sa marge) : frais universitaires, consulting / orientation, accompagnement
  administratif, dossier visa, accueil aéroport, foyer 1 an, assurance médicale. « DT » est l'abréviation courante en
  Tunisie (« TND » si le client préfère : `#s11-cur`, `.rc-l .v`, `.rc-tot .b` et `#s11-deco`) ;
  en derja : « د.ت ». **Non inclus**, imprimés en bas du ticket sous « NON INCLUS · EN
  OPTION SUR DEMANDE » avec la mention « sur devis » : billet d'avion, train ou voiture
  jusqu'à la ville universitaire, hôtel & visites à Moscou. « Tout compris » a été retiré.
- **Prix des options** : aucun prix moyen n'est affiché (le billet d'avion varie selon la
  date ; un montant dans une pub se lit comme une promesse). Pour en afficher un, remplacer
  « sur devis » par « dès … € » ou « ≈ … € » dans les lignes `.rc-o` du ticket (montants
  fournis et tenus par le client).
- « Sans frais cachés » reprend l'engagement « Transparence sur les coûts » du site : les
  options non incluses sont désormais listées à l'écran.
- **Transfert** : « Train ou voiture, jusqu'à ta ville. » + « Organisé sur demande · en
  option » (`#tr-sub`), cohérent avec le ticket.
- Le cas montré (Médecine générale à **Lipetsk** — Kazan jusqu'à la v6 —, chambre 412,
  dossier RS-2026-0412, vol RS 2026) est **illustratif**, comme l'exemple de profil. Lipetsk
  fait partie des villes citées dans l'analyse de profil (« Moscou, Saint-Pétersbourg,
  Lipetsk… »).
- **Textes en derja** (v6) : à faire relire par un locuteur tunisien avant diffusion (liste
  complète dans `scripts/make_arabic.py`, `TEXTS`). Choix à confirmer : « tuteur bilingue » →
  « مرافق يحكي لغتين » (accompagnateur qui parle deux langues), « sur devis » → « حسب الديفي »,
  « études + installation » → « القراية + الاستقرار », tutoiement comme en français.

## Retrouver le projet

- Branche Git : `claude/install-openmontage-263px9`
  (`git fetch origin claude/install-openmontage-263px9 && git checkout claude/install-openmontage-263px9`).
- Versions livrées : **v2** (37 s, vertical) = commit `c6acc34` ; **v3** (40 s, transfert +
  YouTube 16:9) = commit `8fc0899` ; **v4** (+ versions 60 s au rythme ralenti) = commit
  `e819e3a` ; **v5** (arrivée à Moscou, transfert, prix « non inclus ») = commit `c091c3e` ;
  **v6** (prix en dinars, versions 60 s en derja) = commit `5038b78`.
  Revoir une version telle quelle : `git checkout <commit> -- openmontage/projects/russtudy-parcours` ;
  voir ce qui a changé depuis : `git diff <commit> -- openmontage/projects/russtudy-parcours`.
- Dossier : `openmontage/projects/russtudy-parcours/`. Kit de marque :
  `../russtudy-motion-15s/artifacts/brand-kit.md`. Direction artistique et storyboard :
  `artifacts/art-direction.md`.

## Retoucher

1. Modifier **`hyperframes/index.html`** (vertical) — c'est la seule source : texte,
   couleurs, timings. Si un timing visuel bouge, déplacer aussi le cue sonore dans
   `artifacts/sfx_cues.json` (`at`).
2. Régénérer le 16:9 : `python3 scripts/make_landscape.py` (quelques secondes). Le script
   s'arrête en citant l'extrait concerné si un élément qu'il adapte a changé dans la
   verticale : reporter la modification dans `scripts/make_landscape.py` (voir plus bas).
3. Contrôler vite : `bash scripts/render_all.sh --draft` (vertical → `renders/draft.mp4`) ou
   `--draft16` (YouTube → `renders/draft_16x9.mp4`), ou des images fixes :
   `cd hyperframes && npx --yes hyperframes@0.8.133 snapshot --at 1,5,8,10,13,16,19,22,25,28,30,35,39`
   (idem dans `hyperframes-16x9`).
4. Livrer : `bash scripts/render_all.sh` → bande-son, 16:9, lint des deux compositions,
   rendus 9:16 60 et 30 fps + 16:9 60 fps, remux du son master, couvertures, miniature
   YouTube, artefacts (≈ 15 min).
5. Versions 60 s : `bash scripts/render_all.sh --60s` → bande-son 60 s, 16:9,
   `make_arabic.py`, `make_slow.py`, rendus des **quatre** versions 60 s (français et derja,
   9:16 et 16:9, 60 fps), couvertures et miniatures. Rien à retoucher à part : elles
   reprennent la composition 40 s telle quelle.
6. Un texte français modifié ? `make_arabic.py` s'arrête en citant l'extrait : mettre à jour
   la paire français → derja correspondante dans `TEXTS` (voir plus bas).

Prérequis d'un conteneur neuf : Node 22 + ffmpeg ; le script installe les dépendances
Python (`scripts/requirements.txt`) et le Chrome de HyperFrames si besoin. Dans le dépôt,
`hyperframes-16x9/` ne contient que la composition générée, la photo 16:9 et la config :
polices, GSAP et bande-son y sont recopiées par `make_landscape.py`. Retouche à la souris en
local : `cd hyperframes && npx --yes hyperframes@0.8.133 preview` (Studio) — pour le 16:9,
lancer `make_landscape.py` puis la même commande dans `hyperframes-16x9` (toute retouche
faite dans le Studio 16:9 est écrasée à la régénération : la reporter dans la verticale ou
dans le script).

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
| 21–23 | `#s8` 05 Accueil | hall d'arrivée : baie vitrée sur Moscou de nuit (tour Spasskaïa, dômes de Saint-Basile, avion qui atterrit, neige, balisage), panneau à volets BIENVENUE EN RUSSIE, tuteur pixel derrière la barrière avec la pancarte (saut sur le temps, salut, « par ici ») | travelling vers la droite (23,0) : le hall sort à gauche avec parallaxe, le transfert entre à droite |
| 23–27 | `#tr` 05 Transfert | canvas pixel en parallaxe (fonction pure du temps) : train + voiture qui le double, neige, ville universitaire qui se lève à l'horizon, panneau ЛИПЕЦК / LIPETSK, jauge MOSCOU → LIPETSK, freinage | la porte du wagon s'ouvre sur le foyer (clip-path) |
| 27–29 | `#s9` 05 Foyer | carte-clé, porte 412 en 3D, chambre pixel, « 1 an inclus » | travelling dans la fenêtre + flash |
| 29–31 | `#s10` Université | photo d'amphi, typo lettre à lettre, carte d'étudiant | cut |
| 31–37 | `#s11` Prix | odomètre 12 000 DT, ticket imprimé ligne à ligne : inclus, total, puis « non inclus · en option », tampon | chute |
| 37–40 | `#s12` CTA | ville pixel, **logo sur l'accord final (37,0)**, WhatsApp, numéro, site | fin |

`#hud` (2,95–31 s) = barre de progression en 5 segments aux couleurs des étapes du site.
Les débuts de scène après l'aéroport sont des constantes en tête du script
(`T_TR`, `T9`, `T10`, `T11`, `T12`) : décaler une scène entière = changer un nombre
(+ les cues sonores correspondants).

## Version YouTube 16:9 (`scripts/make_landscape.py`)

Le script lit `hyperframes/index.html` et écrit `hyperframes-16x9/index.html` :

1. **remplacements vérifiés** des valeurs liées au format (tailles de canvas, trajectoires,
   clip-paths, caméra de la carte…) : chaque extrait doit exister tel quel dans la verticale ;
2. **zones portrait** (`Z_S1` … `Z_S9` : translation + échelle 0,78–0,95) : les objets
   verticaux (téléphone, fiches, dossier, enveloppe, passeport, porte du foyer) sont repris
   tels quels à droite de l'image, les titres passent à gauche ;
3. **bloc CSS paysage** en fin de script : positions des titres, de la barre de progression
   (bandeau haut), du prix, du CTA, etc.

Propres au 16:9 (dans le script) : carte du vol `scripts/map_rows_16x9.js` (grille 96 × 54,
Tunis (700, 880) → Moscou (1348, 236)) + `R0…R3` + caméra `#s7-cam` ; mise en page du
transfert `TRL` ; ville de nuit `CITY`, `DOMES`, `TENT` ; photo
`hyperframes-16x9/assets/img/amphitheatre_16x9.jpg`.

Message « expected 1 occurrence(s), found 0 » : l'extrait cité a été modifié dans la
verticale. Mettre à jour la ligne correspondante du script (la valeur de gauche = nouvelle
valeur verticale, celle de droite = son équivalent 16:9), puis relancer.

## Versions 60 s au rythme ralenti (`scripts/make_slow.py`, v4)

Le film n'est pas remonté à la main : la timeline de 40 s est **rejouée 1,5 fois plus
lentement**. Le script copie `hyperframes/` et `hyperframes-16x9/` vers `hyperframes-60s/`
et `hyperframes-60s-16x9/` en multipliant tous les `data-start` / `data-duration` par 1,5
et en confiant au rendu une timeline racine de 60 s qui parcourt celle de 40 s
(`slowTl`). Chaque image de la version 60 s à l'instant t × 1,5 est identique au pixel près
à celle de la version 40 s à l'instant t (vérifié) : toute retouche de la version 40 s
passe donc dans la version 60 s au prochain `render_all.sh --60s`.

Pour un autre facteur (par ex. 1,25 → 50 s) : changer `K` dans `make_slow.py` **et** dans
`build_audio.py` (`--slow`), puis refaire le montage musical `SEGMENTS` (`if SLOW:`) pour
que le drop A, le drop B et l'accord final tombent toujours sur 1,0 × K, 21,0 × K et
37,0 × K, et adapter l'automation `auto` (`if SLOW:`).

## Version en arabe tunisien (`scripts/make_arabic.py`, v6)

Le script lit les compositions françaises 40 s (`hyperframes/` et `hyperframes-16x9/`,
donc lancer `make_landscape.py` avant) et écrit `hyperframes-ar/` et `hyperframes-ar-16x9/`,
que `make_slow.py` passe ensuite en 60 s (`hyperframes-ar-60s*/`). Même animation, même
timing, même bande-son ; seuls changent :

1. **les textes** : liste `TEXTS` (paires français → derja, chacune doit exister telle quelle
   dans la version française, sinon le script s'arrête ; il vérifie aussi qu'aucun texte
   accentué français ne reste à l'écran) ;
2. **la typographie** : police **Cairo** (`hyperframes/assets/fonts/Cairo-arabic.woff2`,
   OFL) pour les glyphes arabes ; le latin, les chiffres et le logo restent en Space
   Grotesk. Pas d'espacement des lettres sur l'arabe (il casse les liaisons), interligne
   numérique 1,28 sur les libellés (Cairo a des métriques très hautes), masques de titres
   plus hauts (points et descendantes) et départ à `yPercent: 180` ;
3. **les animations lettre par lettre** (titre de l'université, slogan sous le logo) passent
   **mot par mot** ; le **panneau à volets** garde ses 18 cases et leur timing (le bruitage
   reste juste) mais chaque ligne est une phrase arabe révélée colonne par colonne (fenêtres
   `.fw`), de droite à gauche ;
4. **le sens de lecture** : titres, légendes et colonne du prix calés à droite (9:16) ou sur
   le bord droit de la colonne de texte (16:9, x = 840) ; téléphone, cartes, lettre, carte
   d'assurance, notification et ticket en miroir ; la barre de progression se remplit depuis
   la droite. Restent de gauche à droite : carte d'embarquement, carte du vol et jauge
   Moscou → Lipetsk (géographie), numéro de téléphone, site, codes et montants. Les milliers
   s'écrivent avec une espace insécable (`NB`) : une espace simple inverserait « 12 000 » au
   milieu d'un texte arabe.

## Où modifier quoi (`hyperframes/index.html` sauf mention)

Repères : bannières `/* === S1 — … */` (CSS), `<!-- === S1 — … -->` (HTML) et
`// === S1 — …` (animation) pour chaque scène.

| Élément | Où | Attention |
|---|---|---|
| Message tapé | JS `S1_TXT` + HTML `#m-out .l` (2 lignes de la bulle) | ≤ ~34 caractères pour tenir dans le champ ; la frappe dure 0,72 s (`renderS1`) et le cue `s1-typing` frappe 34 touches |
| Réponses du chat | HTML `#m-r1 .l`, `#m-r2` (`#r2-t1`, `#r2-t2`, `#r2-btn`), carte `#chat-biz` | bulles à hauteur fixe (2 lignes) |
| Titres des scènes | HTML `.title .tw` de chaque section | 104 px, ≤ ~900 px de large (112 px en 16:9) |
| Libellés des étapes (barre) | HTML `#hl1`…`#hl7` | texte du site (« Votre parcours en 5 étapes ») |
| Profil / plan | HTML `.prow` (`.pt1`, `.pt2`), `#s2-pm`, `#s2-ps` | cas illustratif |
| Documents du dossier | HTML `#sh0`…`#sh3 .band` | 2 lignes max par bandeau |
| Lettre d'admission | HTML `#lt-k`, `#lt-t`, `#lt-s` | |
| Visa / assurance / billet | HTML `#visa-*`, `#ins-*`, `#bp-*` | |
| Villes et trajet du vol | JS `MAP_ROWS` (régénérer avec `scripts/make_dotmap.py`), `R0…R3` + chemin `M220,1320 C420,1150 600,720 845,698` (3 occurrences) + épingles `#pin-*`, étiquettes `#lb-tun`, `#lb-mow` | la caméra (`#s7-cam`) vise Tunis puis Moscou : recalculer ses x/y si une ville bouge ; 16:9 : mêmes éléments dans `make_landscape.py` |
| Notification en vol | HTML `#nt-b` | |
| Panneau à volets | JS `FLAP` (2 mots de 9 cases) | le cue `s8-split-flap` est resynthétisé avec le même timing (`build_audio.py`) ; derja : `FLAP` dans `make_arabic.py` (2 phrases) |
| **Transfert** (textes) | HTML `#tr-t .tw`, `#tr-a` (MOSCOU), `#tr-b` (LIPETSK), `#tr-sub` | `#tr-sub` ≤ ~40 caractères |
| **Ville de l'université** | `#tr-b`, `#s2-pm`, carte d'étudiant `.sc-f .v2`, panneau du transfert : JS `word("ЛИПЕЦК", 8)` et `word("LIPETSK", 26)` dans `signSpr` | lettres pixel 5×7 dans `PXF` : ajouter celles qui manquent pour un autre nom (ex. « Т », « О », « M ») ; ≤ 13 lettres par ligne |
| Mise en page du transfert | JS `TRL` (horizon, rails, route, positions du train et de la voiture, entrée du panneau) | 16:9 : `TRL` dans `make_landscape.py` |
| Foyer | HTML `#d-plate`, `#kc-n`, puce `#s9-chip` | |
| Carte d'étudiant | HTML `#scard` (`.sc-f`) | |
| **Prix (gros chiffre)** | JS `ODO_TARGET` (chiffres) + `ODO_LAND` (arrivée), devise `#s11-cur` | 5 chiffres (12 000) ; pour un autre nombre de chiffres, ajouter/retirer une colonne `.odo` et mettre aussi à jour `odo_ticks` dans `build_audio.py` ; 16:9 : le chiffre est réduit à 92 % (`zoom`, `make_landscape.py`) pour laisser la place au ticket |
| **Ticket** (postes, montants, total) | HTML `#rc-paper .rc-l`, `.rc-tot` | 7 lignes de 66 px, toutes « inclus » (la 1re sort avec l'en-tête au 1er pas d'avance, pour garder le timing et le son de l'imprimante) ; une ligne de plus = +66 px à `#rc-paper`, `#rc-mask` et `top` de `#rc-slot`, un pas d'avance de plus (`paper feed`) et une rafale de plus dans `feeds` (`build_audio.py`) |
| **Options non incluses** | HTML `.rc-oh` (titre) et `#rc-paper .rc-o` (3 lignes de 56 px, valeur « sur devis ») | pour un prix : remplacer « sur devis » ; une ligne de plus = +56 px à `#rc-paper`/`#rc-mask`, un pas d'avance de plus, et une rafale de plus dans `feeds` (`build_audio.py`) |
| Pastille / tampon prix | HTML `#s11-pill`, `#st-tc` | pastille ≤ ~22 caractères à 44 px (le tampon est à sa droite) |
| Hall d'arrivée (vue de Moscou) | JS `S8L` (baie vitrée, sol, positions de la tour, des dômes et de l'atterrissage) ; tuteur `TUTOR_HEAD` / `HAND` ; barrière `#s8-rail` | 16:9 : `S8L` et CSS dans `make_landscape.py` |
| Travelling hall → transfert | JS bloc TR : `PAN_D` et les tweens `#s8-pan`, `#s8-cv`, `#sign-pos`, `#tr` à `T_TR` | cue `s8-pan` (whoosh) |
| CTA, numéro, site | HTML `#wa-t`, `#cta-chip` ; JS `TEL_TXT`, `URL_TXT`, `TAG_TXT` | CTA ≤ ~700 px à 50 px |
| Ville de nuit (fin) | JS `CITY`, `DOMES`, `TENT` | 16:9 : mêmes noms dans `make_landscape.py` |
| Timings | positions GSAP (secondes) sous chaque bannière JS ; `T_TR`…`T12` | rester sur la grille de 0,5 s ; reporter dans `sfx_cues.json` |
| Musique | `scripts/build_audio.py` → `SEGMENTS` + automation `auto` | coupes 10 ms avant une attaque |
| Volume / mix | `artifacts/sfx_cues.json` (`gain_db`), `build_audio.py` (ducking, limiteur) | cible −14 LUFS, normalisation linéaire |

## Grille musicale (ne pas casser)

Piste « Funky » (Pixabay, `assets/music/11_funky.mp3`), 120 BPM :

- vidéo 0–17 ← piste 15,026–32,026 (fin de build, **drop A à 1,0**, groove)
- vidéo 17–35 ← piste 76,025–94,025 (break de batterie 17, montée de basse 19, **drop B à
  21,0**, groove pendant l'accueil, le transfert, le foyer et le prix)
- vidéo 35–40 ← piste 62,025–67,025 (fill, **arrêt + accord de mi à 37,0**)

Version 60 s (`build_audio.py --slow`, même tempo, coupes recalées × 1,5) :

- vidéo 0–25,5 ← piste 14,526–40,026 (**drop A à 1,5**, groove)
- vidéo 25,5–53,5 ← piste 74,025–102,025 (2 mesures de break de batterie, montée de basse
  29,5, **drop B à 31,5**, groove)
- vidéo 53,5–60 ← piste 62,025–68,525 (fill, **arrêt + accord de mi à 55,5**)

Automation de gain : +6 dB sur le break (17–19), retour à 0 dB juste avant 21,0 ;
accord final +14 dB puis +18 dB à la fin. Les SFX tonals sont accordés (pops mi→fa♯→
sol♯→la, ping et notification en mi, carillon en la, ding-dong d'aéroport mi→do♯,
klaxon du train en la majeur) ; rails, moteur et souffle de porte accompagnent le transfert.

## Choix et garde-fous

- Interface de chat **façon** WhatsApp, sans logo WhatsApp (marque déposée) ; le nom
  « WhatsApp » n'apparaît que dans le texte du CTA et de l'appel (comme sur le site).
- Drapeaux tunisien et russe dessinés en SVG (seules couleurs hors charte, pour la lisibilité).
- Pas de visage : avatars et passagers en pixel art génériques.
- Panneau ЛИПЕЦК en lettres pixel dessinées (Space Grotesk n'a pas le cyrillique).
- Photo de l'amphithéâtre : celle du site (Unsplash) ; recadrage 16:9 de la même photo.
  Carte : masque terre/mer GLOBE (via `global-land-mask`, MIT) converti en grille
  embarquée — aucune donnée chargée au rendu.
- Licences : Space Grotesk et Cairo (OFL), musique et SFX Pixabay Content License (contester une
  éventuelle réclamation Content ID avec la licence Pixabay — utile surtout sur YouTube).

## Pièges rencontrés

- Mêmes que la v1 (CA du proxy pour Chromium, `npx --yes hyperframes@0.8.133`, remux du son).
- Éléments animés depuis l'extérieur de l'écran : leur position de départ doit être
  **entièrement** hors cadre (rotation comprise), sinon ils dépassent avant leur entrée.
- `loudnorm` repasse en mode dynamique si les crêtes inter-échantillons dépassent la
  cible : le limiteur tourne en 192 kHz (suréchantillonné) pour rester linéaire.
- `npx hyperframes validate` signale des contrastes sur les libellés de la barre qui
  sont hors du masque (invisibles) : faux positifs connus (les deux formats).
- Le transfert et la ville de nuit sont paramétrés (`TRL`, `CITY`) pour que le 16:9 ne
  remplace qu'une ligne ; la verticale a été vérifiée identique au pixel près après ce
  passage en paramètres.
