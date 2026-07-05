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
