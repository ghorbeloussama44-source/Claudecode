# Studio OpenMontage — suivi des projets

Tableau de bord : https://claude.ai/artifact/7hSVzQ669qDXh7dj6ucj1H (artifact privé de type Dashboard).

Il lit six fichiers JSON de ce dossier, joints à l'artifact :

| Fichier | Contenu | Mise à jour |
|---|---|---|
| `projects.json` | un projet par ligne : `id` (= nom du dossier dans `openmontage/projects/`), client, diffusion (chaîne, réseaux), statut, version, dates, `recette`, prochaine étape | à la main |
| `videos.json` | une ligne par vidéo des dossiers `renders/` : format, durée, langue, version, état | `python3 openmontage/studio/inventory.py` |
| `backlog.json` | une action à faire par ligne : `projet_id`, priorité (haute / moyenne / basse), état (`à faire` / `fait`) | à la main |
| `outils.json` | le catalogue : un outil ou une bibliothèque par ligne (famille, ce que ça fait, accès, site) | à la main |
| `usages.json` | un outil utilisé dans un projet par ligne, avec ce qu'il y a fait | à la main (relevé dans les HANDOFF, scripts et `asset_manifest.json`) |
| `recettes.json` | une méthode réutilisable par ligne : pour qui, ce qu'il faut fournir, étapes, niveau d'automatisation, commande, projet d'origine | à la main |

`dashboard.html` est la source de la page (document `files/index.html` de l'artifact).

## Ajouter un projet ou mettre à jour le studio

1. Ajouter ou modifier la ligne du projet dans `projects.json` (le plus récent en premier) et ses
   actions dans `backlog.json` ; une action terminée passe à `"etat": "fait"`.
2. Noter les outils du projet : les nouveaux dans `outils.json`, puis une ligne par outil utilisé dans
   `usages.json` (avec ce qu'il a fait dans ce projet).
3. Si le projet a de nouvelles vidéos : compléter `RULES` dans `inventory.py` (version et état des
   fichiers dont le nom ne le dit pas), puis lancer `python3 openmontage/studio/inventory.py`.
4. Envoyer chaque fichier modifié à l'artifact (outil Artifact, `asset: true`, même `url`), puis mettre
   à jour le document `datasets/<projects|videos|backlog|outils|usages|recettes>` : `source.url`, `source.name` et
   `updated: {at, by}`. Supprimer ensuite l'ancien fichier joint.
5. Committer ce dossier.

Fichiers joints actuels : projects `ed468868e7b1bf4a738d6cec2c108c1c`, videos
`4d36b6ef27c41da08026624bcd84e61a`, backlog `cd458287277bf7cc9bcf008bf7f9d720`, outils
`7a719676f3137deef69870224e4e7d0b`, usages `59ff035fa4fe42e0499ad0a8907898a1`, recettes
`653ea8902c020d91a29a1c159538b84a`.

## Recettes : refaire une méthode pour un nouveau client ou une nouvelle chaîne

Chaque projet réussi devient une recette (`recettes.json`). Une recette « Automatique » se lance en
une commande ; une recette « Semi-automatique » a ses déclinaisons scriptées mais sa création à la
main ; une recette « Manuelle » n'a pas encore de script.

- **Clip paroles néon** : `python3 openmontage/studio/recettes/clip_paroles_neon.py init <dossier> --titre "…" --langue ar`,
  puis `… all <dossier>` (détails dans `openmontage/projects/clip-paroles-neon/README.md`).
- **Série réseaux sociaux à voix off** : écrire les fiches `episodes/*.json`, puis
  `bash openmontage/projects/russtudy-social/scripts/render_all.sh`.
- **Pub d'après un storyboard** : composer les scènes dans `hyperframes/index.html` (temps `B(n)` calés
  sur la musique), puis `bash openmontage/projects/tssr-instagram/scripts/render.sh v2` (bande-son,
  rendu, version légère, couverture ; méthode dans `openmontage/projects/tssr-instagram/README.md`).

Ranger un nouveau projet dans `openmontage/projects/<client>-<titre>/` pour qu'il entre dans
l'inventaire, puis l'ajouter au studio (étapes ci-dessus). Le dossier `openmontage/projects/` est
ignoré par Git : ajouter les livrables avec `git add -f`.

Clés d'API : les ranger dans les variables de l'environnement (paramètres de l'environnement cloud),
jamais dans le dépôt ni dans la conversation. Noms lus par OpenMontage : `PEXELS_API_KEY`,
`PIXABAY_API_KEY`, `SUNO_API_KEY`, `FAL_KEY`, `ELEVENLABS_API_KEY`, `GOOGLE_API_KEY`,
`REPLICATE_API_TOKEN`, `HF_TOKEN` (liste complète : `openmontage/.env.example`).
