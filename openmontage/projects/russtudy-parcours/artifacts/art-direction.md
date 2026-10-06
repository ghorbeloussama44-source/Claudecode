# RusStudy — « Le parcours » (40 s) — Direction artistique

Suite du spot 15 s (`../russtudy-motion-15s`). Même marque, même système visuel, nouvelle
histoire : **du premier message WhatsApp jusqu'au premier jour à l'université**, en suivant
les 5 étapes du site (Consultation gratuite → Dossier → Admission → Visa & assurance →
Accueil & installation). Le film est lui-même un tunnel de conversion : il commence par un
message WhatsApp et finit par « Écris-nous sur WhatsApp ».

**v3** (demande du client) : après l'aéroport, le **transport interne de Moscou vers la ville
de l'université, en train ou en voiture** (scène TR, 4 s), puis une **version YouTube 16:9**
dérivée de la composition verticale (voir « Version YouTube 16:9 » plus bas).

## Prix (corrigé par le client)

**1ère année dès 3 500 €, tout compris** : frais universitaires (dès 2 200 €) + consulting /
orientation + dossier visa + accueil aéroport + foyer 1 an + assurance médicale.
(Lecture retenue du brief : 2 200 € = frais universitaires minimum, inclus dans les 3 500 €.)
v5 : « tout compris » retiré, les options non incluses sont listées sur le ticket.
**v6 : prix affiché en dinars tunisiens**, « dès 12 000 DT » (équivalent donné par le client),
frais universitaires « dès 7 500 DT » (même taux, arrondi, à confirmer) ; en derja « 12 000 د.ت ».

## Version en arabe tunisien (v6)

Même film, mêmes plans et même musique, textes en derja (écriture arabe, tutoiement comme en
français), police Cairo à côté de Space Grotesk, lecture de droite à gauche : titres et
légendes calés à droite, cartes et téléphone en miroir, barre de progression qui se remplit
depuis la droite ; la géographie (Tunis → Moscou → Kazan) reste de gauche à droite.
Généré par `scripts/make_arabic.py` depuis les compositions françaises (détails dans
HANDOFF.md).

## Design read

Un récit de voyage en motion design : chaque étape est un objet du parcours (téléphone,
dossier, lettre d'admission, passeport, carte d'embarquement, panneau d'arrivée, clé du
foyer, amphi) traité avec une technique d'animation différente, enchaînés en un seul
mouvement continu sur un groove funk. Confiant, joueur, concret, rassurant.

## Taste profile

| Cadran | Valeur | Conséquence |
|---|---|---|
| visual_variance | 8 | une technique et une couleur d'étape par scène (couleurs des 5 étapes du site) |
| motion_intensity | 8 | transitions motivées par les objets, respiration sur le vol et sur le prix |
| information_density | 4 | 1 titre + 1 objet par scène ; le reçu du prix est le seul moment dense (6 lignes, 6 s) |

- Palette : tokens du site uniquement. Couleurs d'étape = rangées « Votre parcours en 5
  étapes » du site : 01 blanc, 02 violet `#a855f7`, 03 or `#fbbb21`, 04 orange `#f97316`,
  05 vert `#22c55e` ; hook bleu `#2460e8` ; vol nuit `#0f1c45` ; prix encre `#0a0a0a`.
- Typo : Space Grotesk 700 (titres −0.04em), kickers en capitales 600.
- Chrome : barre de progression façon story (5 segments) + pastille « ÉTAPE n/5 ».
- Device signature : **le fil WhatsApp** — le parcours démarre dans une conversation, une
  notification RusStudy revient pendant le vol, et le CTA final renvoie vers WhatsApp.
  Pas de logo WhatsApp (marque déposée) : bulle de chat générique aux couleurs de la marque.
- Anti-patterns : même transition deux fois de suite, emoji (icônes pixel/SVG à la place),
  faux visages, promesses non fournies par le client.

## Grille musicale (Funky, 120 BPM, mesure = 2 s)

| Vidéo | Piste | Musique |
|---|---|---|
| 0–17 | 15,026–32,026 | fin de build, **drop A à 1,0**, groove |
| 17–21 | 76,025–80,025 | break de batterie (17) puis montée de basse (19) |
| 21–35 | 80,025–94,025 | **drop B à 21,0**, groove (2 mesures de plus pour le transfert) |
| 35–37 | 62,025–64,025 | fill avant l'arrêt |
| 37–40 | 64,025–67,025 | **arrêt + accord tenu** (+14 dB) |

## Storyboard final (1080×1920, 40 s)

| # | Temps | Étape | Objet / technique | Texte |
|---|---|---|---|---|
| 1 | 0–3 | Le message | téléphone, conversation façon WhatsApp (carte « compte professionnel · réponse sous 24 h ») : frappe, envoi **sur le drop**, coches lues, « écrit… », réponse, carte d'appel ; la main pixel réserve l'appel | « Tout commence par un message. » |
| 2 | 3–7 | 01 · Consultation gratuite | ripple depuis le bouton → appel 15 min (anneaux, onde, chrono 00:00 → 15:00), fiche profil scannée + coches tracées en SVG, bandeau « Ton plan » | « On analyse ton profil. » |
| 3 | 7–9 | 02 · Dossier | push vertical ; 4 documents en arcs (easings x/y différents) classés dans la pochette, tampons TRADUIT / LÉGALISÉ en squash & stretch | « On prépare ton dossier. » + « Traduction assermentée + légalisation » |
| 4 | 9–11 | 03 · Admission | rideau or ; enveloppe qui s'écrase, rabat 3D, lettre d'invitation d'État, signature tracée, tampon ADMIS + confettis pixel physiques | « Admission officielle. » |
| 5 | 11–15 | 04 · Visa & assurance | whip-pan flouté ; passeport 3D, vignette visa claquée, carte d'assurance, carte d'embarquement TUN → MOW | « Visa d'études + assurance. » |
| 6 | 15–17 | Départ | la carte d'embarquement se déchire et ouvre le ciel, avion pixel qui décolle, mur de nuages | « Bon voyage ! » |
| 7 | 17–21 | En vol | carte en pixels (masque terre/mer réel) Tunis → Moscou, sillage doré, nuages en parallaxe, notification RusStudy, plongée sur Moscou | « Cap sur Moscou. » + « Ton tuteur t'attend à l'arrivée. Bon vol ! » |
| 8 | 21–23 | 05 · Accueil | iris vert sur le **drop B** ; hall d'arrivée : par la baie vitrée, Moscou de nuit (tour Spasskaïa, dômes de Saint-Basile, fenêtres allumées, neige) et un avion qui atterrit ; panneau à volets BIENVENUE EN RUSSIE ; le tuteur (pixel art) se lève derrière la barrière avec la pancarte RusStudy, saute sur le temps, salue et la penche vers la sortie ; **travelling vers la droite** jusqu'au train | « Un tuteur bilingue t'attend à l'aéroport. » |
| 9 | 23–27 | 05 · Transfert | le travelling arrive sur un canvas pixel en parallaxe (étoiles, soleil couchant, collines, forêt, poteaux de caténaire, neige) : le **train** (passagers aux fenêtres) et une **voiture** orange qui le double phares allumés ; la ville universitaire (bâtiment à colonnes et coupole) se lève à l'horizon ; jauge MOSCOU → KAZAN, panneau КАЗАНЬ / KAZAN, freinage, la porte du wagon s'ouvre | « Train ou voiture, jusqu'à ta ville. » + « Organisé sur demande · en option » |
| 10 | 27–29 | 05 · Foyer | la scène s'ouvre **dans la porte du wagon** ; carte-clé, LED verte, porte 412 en 3D sur la chambre pixel, travelling dans la fenêtre | « Foyer universitaire. » + « 1 an inclus » |
| 11 | 29–31 | Université | flash blanc ; photo de l'amphi en Ken Burns, typo lettre à lettre, carte d'étudiant en 3D avec reflet, étoiles pixel ; barre « Objectif atteint » | « Premier jour à l'université. » |
| 12 | 31–37 | Prix | cut ; odomètre 12 000 DT, pastille « études + installation », ticket imprimé ligne à ligne : 6 postes inclus, total, puis « NON INCLUS · EN OPTION SUR DEMANDE » (billet d'avion, train ou voiture, hôtel & visites à Moscou : sur devis), tampon SANS FRAIS CACHÉS | « Budget 1ère année · dès 12 000 DT » |
| 13 | 37–40 | CTA | logo sur l'accord final, ville pixel de nuit (rappel du spot 15 s), bouton WhatsApp, numéro et site tapés, tap | « Écris-nous sur WhatsApp · +7 996 433 4489 · russieetudes.com · 1ère consultation gratuite » |

Ville universitaire d'exemple : **Kazan** (une des villes citées dans l'analyse de profil,
« Moscou, Saint-Pétersbourg, Kazan… »). Comme « Médecine générale », c'est un cas illustratif.

## Version YouTube 16:9 (1920×1080)

Même film, même bande-son, même timing ; mise en page repensée pour l'horizontal :

- titres à gauche (112 px, marge 120 px), illustration de la scène à droite ;
- barre de progression en **bandeau haut** (libellé de l'étape à gauche, 5 segments au
  centre, logo à droite) ;
- les objets verticaux (téléphone, fiches, dossier, enveloppe, passeport, porte du foyer)
  sont repris tels quels dans des « zones portrait » mises à l'échelle (0,78–0,95) ;
- scènes plein cadre recomposées : carte du vol (grille 96 × 54, Tunis → Moscou),
  transfert (horizon plus large, voiture qui dépasse le train), amphithéâtre recadré 16:9,
  ticket de prix à droite du chiffre, ville de nuit élargie (tour à gauche, cathédrale à droite).

La version 16:9 n'est jamais retouchée à la main : `scripts/make_landscape.py` la régénère
depuis la verticale.

## v5 : arrivée, transfert et prix précisés

- L'arrivée à Moscou devient un vrai hall d'arrivée (vue sur la ville de nuit, avion qui
  atterrit, tuteur derrière la barrière) et le retournement 3D vers le transfert, qui
  laissait voir un vide noir, est remplacé par un travelling latéral : le hall sort à
  gauche, le train entre à droite, dans le sens du voyage.
- Le transfert gagne de la neige et la ville universitaire qui se lève à l'horizon quand
  le train freine.
- Le prix dit clairement ce qui n'est pas inclus (billet d'avion, train ou voiture, hôtel
  et visites à Moscou : en option, sur devis) ; « tout compris » est retiré.

## Version 60 s au rythme moins accéléré (v4)

Demande du client : « une version où le rythme est moins accéléré ». Même film, mêmes
images, joué **1,5 fois plus lentement** : chaque étape reste 1,5 fois plus longtemps à
l'écran (3 s au lieu de 2 pour les étapes courtes, 9 s pour le prix, 4,5 s pour le CTA) et
chaque mouvement est plus doux. La musique garde son tempo (120 BPM) et est remontée sur
60 s : drop A sur l'envoi du message (1,5 s), break de batterie pendant le vol, drop B sur
l'arrivée (31,5 s), arrêt sur l'accord final avec le logo (55,5 s). Les sons du parcours
(frappe, volets, odomètre, imprimante, rails, moteur…) sont étirés au même rythme.
