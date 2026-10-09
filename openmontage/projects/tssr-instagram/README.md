# TSSR — pub Instagram en derja (48 s, 9:16)

Client : **TSSR · Study in Russia**. Point de départ : le storyboard du client
(`reference/storyboard_tssr.png`, 7 scènes, ≈ 47 s). Diffusion : Instagram (Reels, Stories).

## Livrables (`renders/`)

| Fichier | Contenu |
|---|---|
| `tssr_pub_instagram_48s_derja_v1.mp4` | la pub complète, 1080×1920, 30 images/s, son AAC 192 k à −14 LUFS |
| `tssr_pub_instagram_48s_derja_v1_leger.mp4` | la même en 720×1280, pour l'envoyer au client sur WhatsApp |
| `tssr_pub_instagram_48s_derja_v1_couverture.png` | couverture (drapeau + « القراية في روسيا ») |
| `tssr_apercu_0-8s_derja.mp4` | ancien aperçu de direction (scènes 1–2, ancienne musique) |

## Les 7 scènes

| # | Temps | Musique | Texte à l'écran (derja) | Sens | Visuel |
|---|---|---|---|---|---|
| 1 | 0 – 4 s | montée | القراية في روسيا | Étudier en Russie | Saint-Basile, drapeau russe qui flotte (dessiné en code), titre + encadré rouge |
| 2 | 4 – 7,4 s | drop | حلمك ممكن! | Ton rêve est possible ! | carte photo des diplômés, rayons, trait rouge, étincelles |
| 3 | 7,4 – 14,3 s | drop | جامعات معروفة في العالم الكل | Des universités connues dans le monde entier | globe filaire qui tourne, université dessinée au trait (silhouette de l'université d'État de Moscou), fenêtres qui s'allument, étoile, toque en orbite |
| 4 | 14,3 – 21,1 s | drop | طب · هندسة · إعلامية · وبرشا اختصاصات أخرى | Médecine, ingénierie, informatique… et beaucoup d'autres spécialités | trois cartes façon « story » avec barre de progression, puis trois vignettes |
| 5 | 21,1 – 31,4 s | drop | نرافقوك من الأول للآخر — الطلب أونلاين · الاستقبال في المطار · التسجيل في الجامعة · المبيت والمرافقة | On t'accompagne du début à la fin : demande en ligne, accueil à l'aéroport, inscription à l'université, foyer et suivi | infographie en 4 étapes, une par mesure, puis coches vertes |
| 6 | 31,4 – 38,3 s | pause puis montée | مستقبلك في روسيا! | Ton avenir en Russie ! | photo d'étudiants, écriture calligraphique, trait rouge, flash blanc |
| 7 | 38,3 – 48 s | 2e drop, accord final à 45,1 s | TSSR · Study in Russia — سجّل توّا — مرافقة على قياسك · نصايح خبراء · تسجيل آمن — tssr.study.ru · ابعثلنا ميساج | Inscris-toi maintenant — accompagnement sur mesure, conseils d'experts, inscription sécurisée — écris-nous | fond clair, logo, bouton rouge « tapé », 3 avantages cochés, compte Instagram |

Promesses : pas de « garanti » ; « تسجيل آمن » (inscription sécurisée) reprend le storyboard.

## Provisoire, à remplacer quand le client les envoie

- **Logo** : la scène 7 et la pastille en haut affichent un logo texte (« TSSR · Study in Russia » +
  toque). Remplacer `#s7-cap` / `#s7-tssr` et `#chip` dans `hyperframes/index.html` par le logo HD.
- **Compte Instagram** : `tssr.study.ru` vient du storyboard ; à confirmer (`#s7-handle`).
- **Photos** : photos de banque Unsplash (pas de vrais étudiants TSSR). De vraies photos, avec
  l'accord des personnes, se mettent dans `hyperframes/assets/img/` sous le même nom.
- **Textes en derja** : à faire relire par le client.

## Méthode (refaire une pub du même type pour un autre client)

1. Lire le storyboard du client : scènes, textes, points clés, charte (couleurs, logo).
2. Choisir une musique jamais utilisée pour un autre client du même secteur, puis mesurer sa
   grille avec librosa : ici 140 BPM, un temps = 0,428571 s, attaques 14 ms avant la grille.
3. Caler les scènes sur la musique : le drop tombe sur la scène 2, chaque scène commence sur une
   mesure, l'appel à l'action sur le 2e drop. Dans `index.html`, `B(n)` = temps n après le drop.
4. Écrire la composition HyperFrames scène par scène (GSAP, SVG tracés, canvas), vérifier les images
   clés avec `hyperframes snapshot`.
5. Bande-son : `scripts/build_audio.py` monte la musique en 3 morceaux coupés sur les mesures, pose
   37 bruitages sur les animations et normalise à −14 LUFS. Le fichier produit,
   `hyperframes/assets/audio/soundtrack.wav`, n'est pas dans Git : le script le recrée.
6. Rendu en une commande : `bash scripts/render.sh v2` (bande-son, rendu ≈ 5 min, version légère,
   couverture).

Montage musical (piste `assets/music/future_bass_upbeat.mp3`, Pixabay, 140 BPM) :

| Vidéo | Piste | Rôle |
|---|---|---|
| 0 – 34,847 s | 11,459 – 46,306 s | montée, drop à 4 s, pause à 31,4 s |
| 34,847 – 41,704 s | 66,878 – 73,735 s | fin de la 2e montée, 2e drop à 38,286 s |
| 41,704 – 48 s | 94,306 – 100,602 s | dernières mesures, accord final à 45,143 s |

## Outils

HyperFrames 0.8.133 (rendu), GSAP 3.14 (animation calée sur les temps), SVG (université, icônes et
traits dessinés à l'écran), Canvas 2D (drapeau qui flotte, globe qui tourne), polices Cairo, Aref
Ruqaa et Montserrat, librosa (tempo, drops, points de coupe), numpy + soundfile (montage et
bruitages), ffmpeg (normalisation −14 LUFS, encodage), photos Unsplash, musique et bruitages Pixabay.

## Sources et licences

- Musique : Pixabay, « future bass upbeat » (licence Pixabay, usage commercial sans attribution).
  Certaines pistes Pixabay sont dans Content ID : en cas de réclamation, la contester avec la licence.
- Bruitages : fournis avec HyperFrames (Pixabay).
- Photos Unsplash (licence Unsplash) : `medecin.jpg` (photo-1612349317150-e413f6a5b16d),
  `ingenierie.jpg` (photo-1581091226825-a6a2a5aee158), `informatique.jpg`
  (photo-1531482615713-2afd69097998), `etudiants_groupe.jpg` (photo-1517486808906-6ca8b3f04846) ;
  `saint_basile.jpg` et `diplomes_toques.jpg` viennent de l'aperçu.
- Polices : Google Fonts (OFL).
