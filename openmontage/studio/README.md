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

Fichiers joints actuels : projects `22fa62021cdc72b328864d2758bb6414`, videos
`0be8f5befcb801ad3c76e9d157d3b3f3`, backlog `7a16ad1df4fd9a663489e7dd9af43544`, outils
`d934f8140834210eb8b4657b631507aa`, usages `05c112ce0d7d678d259f92e03bc4d169`, recettes
`bb0ab43c42ec1d9db4a525d0e36e9d61`.

## Recettes : refaire une méthode pour un nouveau client ou une nouvelle chaîne

Chaque projet réussi devient une recette (`recettes.json`). Une recette « Automatique » se lance en
une commande ; une recette « Semi-automatique » a ses déclinaisons scriptées mais sa création à la
main ; une recette « Manuelle » n'a pas encore de script.

- **Clip paroles néon** : `python3 openmontage/studio/recettes/clip_paroles_neon.py init <dossier> --titre "…" --langue ar`,
  puis `… all <dossier>` (détails dans `openmontage/projects/clip-paroles-neon/README.md`).
- **Série réseaux sociaux à voix off** : écrire les fiches `episodes/*.json`, puis
  `bash openmontage/projects/russtudy-social/scripts/render_all.sh`.

Ranger un nouveau projet dans `openmontage/projects/<client>-<titre>/` pour qu'il entre dans
l'inventaire, puis l'ajouter au studio (étapes ci-dessus). Le dossier `openmontage/projects/` est
ignoré par Git : ajouter les livrables avec `git add -f`.

Clés d'API : les ranger dans les variables de l'environnement (paramètres de l'environnement cloud),
jamais dans le dépôt ni dans la conversation. Noms lus par OpenMontage : `PEXELS_API_KEY`,
`PIXABAY_API_KEY`, `SUNO_API_KEY`, `FAL_KEY`, `ELEVENLABS_API_KEY`, `GOOGLE_API_KEY`,
`REPLICATE_API_TOKEN`, `HF_TOKEN` (liste complète : `openmontage/.env.example`).
