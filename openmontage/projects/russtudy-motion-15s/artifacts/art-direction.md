# RusStudy — Motion design 15 s — Direction artistique

Client : **RusStudy** (russieetudes.com) — agence d'orientation vers les universités
publiques russes pour étudiants tunisiens.
Objectif : spot social vertical (Reels / TikTok / Shorts / Facebook) qui fait cliquer
vers le site pour une **1ère consultation gratuite**.

## Design read

Une campagne jeune et sûre d'elle pour une décision sérieuse : les blocs bento saturés
et l'humour pixel-art du site (« PIXEL SYSTEM V1 ») mis en mouvement sur un groove funk —
confiant, joueur et précis. Les chiffres tombent sur le temps, et le plan final reproduit
le hero du site : quand on tape sur la pub, on atterrit sur exactement la même image
(continuité pub → landing page).

## Taste profile

| Cadran | Valeur | Conséquence |
|---|---|---|
| visual_variance | 7 | chaque mesure a son propre sujet visuel (rouleau, odomètre, bento, trajet, photos, ville pixel, logo), reliés par la palette, la typo et le « point » |
| motion_intensity | 9 | cinétique rapide calée au BPM, mais une respiration nette sur le plan final |
| information_density | 4 | une idée par mesure, typo géante, ≤ 6 mots lisibles à la fois |

- **Palette (tokens CSS du site uniquement)** : crème `#f0ebe3`, encre `#0a0a0a`,
  violet accent `#a855f7`, bleu `#2460e8`, or `#fbbb21`, orange `#f97316`, vert `#22c55e`.
  Nuit du hero : ciel `#0f1c45 → #162f77`, immeubles `#0b0f1c`, fenêtres or `#b09850`,
  neige `#6070a0`.
- **Typo** : Space Grotesk 700, interlettrage −0.04em (titres), −0.05em (logo) ;
  kickers en capitales 600, interlettrage +0.05em à +0.18em, pastilles à bord fin (style `.t-kicker`).
- **Formes** : cartes à rayon 22–40 px, pastilles 999 px, pixel-art en grille (icônes maison).
- **Device signature : le point.** Le point rond de Space Grotesk (celui de « RusStudy. »).
  Il n'apparaît que sur deux temps : (1) le point de « en Russie. » s'ouvre en iris doré
  sur la scène prix ; (2) le point de « Change ta vie. » s'envole pour devenir le point du logo.
- **Anti-patterns** : dégradés IA violets génériques, emoji (remplacés par des icônes pixel),
  même transition à chaque coupe, même easing partout, photos plates sans traitement,
  visages de témoignages stock présentés comme de vrais étudiants (non utilisés).

## Grille musicale

Piste : « Funky » (Pixabay, licence Pixabay Content License), **120 BPM** mesuré
(1 temps = 0,5 s, résidu ±4 ms). Montage sur les mesures :

- vidéo 0,0–9,0 s ← piste 15,054–24,054 s (fin de build + **drop à 1,0 s**)
- vidéo 9,0–15,0 s ← piste 60,054–66,054 s (fin de phrase + **accord final à 13,0 s**, résonance)

Temps forts (mesures) : 1, 3, 5, 7, 9, 11, 13 s. Chaque scène = 1 mesure (2 s).

## Storyboard (1080×1920, 15,0 s)

| # | Temps | Sujet principal | Mouvement / transition | Texte |
|---|---|---|---|---|
| 0 | 0,0–3,4 | **Machine à filières** : rouleau de carte colorée (une couleur de filière du site par mot) | rotation floutée (flou directionnel SVG) dès la frame 0, verrouillage avec rebond **sur le drop (1,0 s)**, un mot par temps | « Bac en poche ? » · MÉDECINE / INGÉNIERIE / PHARMACIE / BUSINESS · « en Russie. » |
| 1 | 3,2–5,4 | **Odomètre** du prix sur fond or | iris circulaire depuis le point de « Russie. », chiffres qui roulent et se posent sur le temps (4,0 s) | « Frais de scolarité » · « dès 2 200 € /an » · « jusqu'à 4× moins cher qu'en Europe » |
| 2 | 5,0–7,3 | **Bento** « Accompagnement total » sur crème | la scène or se rétracte (clip-path) pour devenir la carte or de la grille ; 4 cartes en cascade à la croche | Visa garanti · Logement garanti · Accueil aéroport · Diplômes d'État reconnus |
| 3 | 7,0–9,3 | **Trajet Tunis → Moscou** (avion pixel sur arc pointillé) | zoom-through dans la carte verte ; l'avion suit une trajectoire (MotionPath) et trace sa traînée | TUNIS · MOSCOU · « On t'accueille à l'arrivée » |
| 4 | 9,0–11,3 | **La Russie en vrai** : photos du site (Saint-Basile, amphi, diplômés) + cartes stats noires | volet diagonal dans l'axe de l'avion (masque le raccord musical), révélations par masque, compteurs | +1 200 étudiants placés · 40+ universités d'État |
| 5 | 11,0–13,0 | **Ville pixel de nuit** (hero du site + dômes russes en pixel-art) | dissolution en pixels, immeubles qui montent, fenêtres qui s'allument en cascade, neige pixel | « Étudie en Russie. » « Change ta vie. » |
| 6 | 13,0–15,0 | **Logo + CTA** sur la ville illuminée | **accord final** : le point de « vie. » devient le point de « RusStudy. » (squash & stretch) ; CTA en pastille | RusStudy. · ÉTUDES EN RUSSIE · « Réserve ta consultation gratuite » · russieetudes.com · Places limitées 2026–2027 |

## Sound design (sous la musique, ~−10 dB)

Clics de rouleau (pré-drop), impact sur le drop, petits « flicks » à chaque mot, whoosh
d'iris, cliquetis d'odomètre + « ding » à l'arrêt, pops des cartes, whoosh de zoom,
passage d'avion, whoosh de volet (masque le raccord), tics des compteurs, scintillement
des fenêtres, impact grave sur le logo, pop du CTA.
