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

Une page web (`public/`) avec un petit serveur Express (`server/`) qui prend
en entrée plusieurs fichiers vidéo bruts et renvoie une vidéo assemblée :
détection et suppression automatique des silences, normalisation (résolution/
fps/son communs) de chaque segment conservé, concaténation, puis équilibrage
du volume (loudnorm).

```bash
# 1. Installe les dépendances (Express, Multer, en plus de Puppeteer)
npm install

# 2. Lance le serveur (nécessite ffmpeg/ffprobe installés sur la machine)
npm run start:landing

# 3. Ouvre http://localhost:3000
```

Formats acceptés : mp4, mov, mkv, webm, avi, m4v — jusqu'à 20 fichiers de
500 Mo max chacun par requête. Les fichiers uploadés et le résultat sont
stockés dans `tmp/` (ignoré par git) et les fichiers sources sont supprimés
dès la fin du traitement.
