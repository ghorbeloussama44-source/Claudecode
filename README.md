# RuStudy Scraper

Script Puppeteer qui compare plusieurs déploiements Vercel du projet RuStudy
selon des critères objectifs (SEO, accessibilité, performance, contenu).

## Sites comparés

- https://rustudy.vercel.app/
- https://rustudyclaudev-2.vercel.app/
- https://landing-page-rustudy.vercel.app/
- https://rustudystudiov1.vercel.app/
- https://rustudystudiov2.vercel.app/
- https://rustudystudiov3.vercel.app/
- https://rustudystudiov4.vercel.app/
- https://rustudystudiov5.vercel.app/

## Utilisation

```bash
# 1. Installe Puppeteer (si pas installé)
npm install puppeteer

# 2. Lance le script
node scrape-rustudy.js
```

## Résultat

Le script génère un dossier `rustudy-report/` (ignoré par git) contenant :

- `comparison.json` — données brutes par site (statut HTTP, temps de
  chargement, titre, meta description, nombre de mots, images sans `alt`,
  liens internes/externes, structure de titres, erreurs console, poids de
  la page, usage mémoire JS)
- `comparison.md` — tableau récapitulatif lisible en Markdown
- `screenshots/` — capture d'écran pleine page de chaque site

Un échec sur un site (timeout, DNS, etc.) n'interrompt pas l'analyse des
autres : l'erreur est simplement consignée dans le rapport.

## Landing page : rushes → vidéo finale

Une page web (`public/`) déployée en fonctions serverless Vercel (`api/`) qui
prend en entrée plusieurs fichiers vidéo bruts et renvoie une vidéo
assemblée : détection et suppression automatique des silences, normalisation
(résolution/fps/son communs) de chaque segment conservé, concaténation, puis
équilibrage du volume (loudnorm).

Architecture pensée pour Vercel (serverless, sans serveur persistant) :

- Chaque clip est envoyé **directement du navigateur vers Vercel Blob**
  (`@vercel/blob/client`), pas via nos fonctions — une fonction Vercel est
  limitée à 4.5 Mo de corps de requête, largement en dessous de la taille
  d'une vidéo.
- `api/blob-upload.js` génère le jeton d'upload (types vidéo uniquement, 500
  Mo max par fichier).
- `api/finalize.js` télécharge les clips depuis Blob storage, lance le
  pipeline ffmpeg (`lib/pipeline.js`, avec les binaires statiques
  `ffmpeg-static`/`ffprobe-static` embarqués car ffmpeg n'est pas installé
  nativement sur Vercel), puis réuploade le résultat sur Blob storage et
  renvoie son URL.

### Configuration requise (à faire une fois, dans le dashboard Vercel)

1. **Storage → Create Database → Blob**, associer le store à ce projet
   (accès *Public*).
2. Vercel ajoute automatiquement `BLOB_READ_WRITE_TOKEN` aux variables
   d'environnement du projet.
3. Redéployer (ou `vercel env pull` puis `vercel dev` en local).

### Développement local

```bash
npm install       # installe @vercel/blob, ffmpeg-static, ffprobe-static, puppeteer
vercel env pull    # récupère BLOB_READ_WRITE_TOKEN dans .env.local
vercel dev         # sert public/ + api/ comme en production
```

Formats acceptés : mp4, mov, mkv, webm, avi, m4v — jusqu'à 20 fichiers de
500 Mo max chacun. Les clips sources sont supprimés du Blob store juste après
l'assemblage ; la vidéo finale reste sur le store à l'URL retournée.

**Points d'attention connus :**
- Traitement limité à `maxDuration: 300s` (voir `vercel.json`) — un très
  grand nombre de clips volumineux peut dépasser cette limite (erreur
  `FUNCTION_INVOCATION_TIMEOUT`) selon le plan Vercel utilisé.
- `/api/blob-upload` n'a pas d'authentification (outil public, pas de
  comptes) : seuls le type de fichier et la taille max sont vérifiés côté
  serveur. À surveiller si le trafic devient significatif (coût de
  stockage).
