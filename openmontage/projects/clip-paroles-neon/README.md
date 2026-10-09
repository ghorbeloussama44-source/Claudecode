# Clip paroles néon — méthode et outils

Clip de votre chanson en arabe : chaque mot chanté s'allume seul, en néon doré, au centre de
l'image, sur des plans d'archives étalonnés en tons chauds. Réalisé en août 2026 (avant le 19),
archivé ici le 9 octobre 2026.

- Vidéo finale : `renders/clip_paroles_neon_v3.mp4` — 4 min, 1280×720, 30 images/s, H.264 + AAC,
  volume −16 LUFS, environ 29 changements de plan.
- Aperçus : `apercus/planche_v3.png` (18 images de la vidéo), `apercus/image_090s.png`.

## La méthode, étape par étape

1. **Musique** : chanson générée avec **Suno**, fournie par vous.
2. **Paroles calées mot par mot** : transcription automatique avec l'heure de chaque mot, puis
   correction avec vos paroles exactes. L'IA entend mal le chant en arabe : vos paroles donnent
   les bons mots, la transcription donne le moment où chacun est chanté.
3. **Plans** : vidéos gratuites de banques d'images (Pexels d'après vos souvenirs ; la liste exacte
   des plans n'a pas été gardée), choisies pour l'ambiance des paroles : bougie, lune, nuages,
   montagne, feu, mer et voilier, salle de théâtre vide, danseuse.
4. **Montage** : environ un plan par phrase, avec des fondus.
5. **Étalonnage** : tons chauds et dorés, contraste doux, vignettage.
6. **Mots en néon** : composant Remotion `NeonWordOverlay`
   (`openmontage/remotion-composer/src/components/NeonWordOverlay.tsx`) :
   - police Noto Kufi Arabic, graisse 900, texte crème `#fff8ec` ;
   - contour de 1 px et halo doré `#FFC94A` (quatre lueurs de 10 à 80 px) qui respire doucement
     (1,4 fois par seconde) ;
   - entrée en « coup de poing » avec un léger rebond, sortie en fondu sur 6 images, le mot reste
     120 ms après la fin du chant ;
   - 140 px pour une image de 1 080 px de haut ; rendu sur fond transparent, puis posé sur le montage.
7. **Export** : 1280×720, 30 images/s, version légère (environ 800 kb/s) pour l'envoi.

## Refaire un clip de ce type : la recette automatique

La méthode est rejouable en une commande avec `openmontage/studio/recettes/clip_paroles_neon.py`
(testée le 9 octobre 2026 sur 30 s de cette chanson : 53 mots calés, 9 plans, néon, export à
−14 LUFS, environ 6 minutes).

```bash
python3 openmontage/studio/recettes/clip_paroles_neon.py init openmontage/projects/<client>-<titre> --titre "Mon titre" --langue ar
# copier la chanson dans input/chanson.mp3 et les paroles corrigées dans input/paroles.txt (une phrase par ligne)
python3 openmontage/studio/recettes/clip_paroles_neon.py all openmontage/projects/<client>-<titre>
```

Livrables dans `renders/` : la vidéo 1080p pour YouTube, une version légère, les sous-titres `.srt`
(à importer sur YouTube) et une miniature. Pour corriger le moment d'un mot, l'ajouter dans
`input/corrections.json` et relancer les étapes `overlay` puis `final`.

Réglages dans `config.json` : client et chaîne de diffusion, format 16:9 ou 9:16 (Shorts, TikTok,
Reels), couleur et taille du néon, mots-clés des plans, étalonnage chaud / froid / neutre, volume,
modèle de transcription (`medium` par défaut, `large-v3` plus précis mais plus lent).

Les plans automatiques demandent la clé `PEXELS_API_KEY` dans les variables de l'environnement.
Sans elle, on dépose ses propres plans dans `footage/`.
