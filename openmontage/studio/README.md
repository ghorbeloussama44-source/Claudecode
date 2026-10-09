# Studio OpenMontage — suivi des projets

Tableau de bord : https://claude.ai/artifact/7hSVzQ669qDXh7dj6ucj1H (artifact privé de type Dashboard).

Il lit trois fichiers JSON de ce dossier, joints à l'artifact :

| Fichier | Contenu | Mise à jour |
|---|---|---|
| `projects.json` | un projet par ligne : `id` (= nom du dossier dans `openmontage/projects/`), statut, version, dates, prochaine étape | à la main |
| `videos.json` | une ligne par vidéo des dossiers `renders/` : format, durée, langue, version, état | `python3 openmontage/studio/inventory.py` |
| `backlog.json` | une action à faire par ligne : `projet_id`, priorité (haute / moyenne / basse), état (`à faire` / `fait`) | à la main |

`dashboard.html` est la source de la page (document `files/index.html` de l'artifact).

## Ajouter un projet ou mettre à jour le studio

1. Ajouter ou modifier la ligne du projet dans `projects.json` (le plus récent en premier) et ses
   actions dans `backlog.json` ; une action terminée passe à `"etat": "fait"`.
2. Si le projet a de nouvelles vidéos : compléter `RULES` dans `inventory.py` (version et état des
   fichiers dont le nom ne le dit pas), puis lancer `python3 openmontage/studio/inventory.py`.
3. Envoyer chaque fichier modifié à l'artifact (outil Artifact, `asset: true`, même `url`), puis mettre
   à jour le document `datasets/<projects|videos|backlog>` : `source.url`, `source.name` et
   `updated: {at, by}`. Supprimer ensuite l'ancien fichier joint.
4. Committer ce dossier.

Fichiers joints actuels : projects `847c9d6fddfed7820b94c3463c13195f`, videos
`9fc0b222f39758e06d25561e7e866550`, backlog `6d9bfc67b440b34d8c9e3e3f500033d2`.
