# Kit de marque RusStudy (extrait de russieetudes.com, 5 oct. 2026)

Références brutes dans `reference/` : `site_brand_tokens.css` (bloc `:root` du CSS
du site), `site_text_fr.txt` (texte intégral de la page FR), captures
`site_hero_desktop.png`, `site_hero_mobile.png`, `site_full_page.jpg`.

## Logo (wordmark typographique, pas de fichier image)

```html
<!-- navigation (fond crème) -->
<span class="t-display font-bold tracking-[-0.05em]">Rus<span class="t-accent-text">Study</span>.</span>
<span class="text-[8px] font-medium tracking-[0.18em] opacity-50 uppercase">ÉTUDES EN RUSSIE</span>
<!-- footer (fond noir) : même balisage, tracking -0.04em -->
```

- « Rus » et le **point** = couleur du texte (encre `#0a0a0a` sur clair, blanc sur sombre).
- « Study » = violet accent `#a855f7`.
- Space Grotesk 700, interlettrage −0.05em ; signature « ÉTUDES EN RUSSIE » en
  capitales, interlettrage 0.18em, opacité 50 %.

## Couleurs (tokens CSS du site)

| Token | Valeur | Usage sur le site |
|---|---|---|
| `--bg` | `#f0ebe3` | fond crème |
| `--ink` | `#0a0a0a` | texte, cartes noires, barre d'urgence |
| `--accent` | `#a855f7` | « Study », bouton Postuler, carte Business (c5) |
| `--hl` / c1 | `#2460e8` | bleu : carte Médecine, ticker A (texte blanc) |
| c2 | `#f97316` | orange : carte Ingénierie |
| `--gold` / c3 | `#fbbb21` | or : carte Pharmacie, budget, ticker B, texte d'urgence |
| `--green` / c4 | `#22c55e` | vert : carte Dentaire, accueil, check |
| `--red` | `#ef4444` | mots d'alerte (« sans accompagnement ») |
| `theme-color` | `#2F66E8` | meta navigateur |
| hero nuit | ciel `#0f1c45 → #162f77`, immeubles `#0b0f1c`, fenêtres `#b09850`, neige `#6070a0` | canvas pixel du hero |

Formes : rayon des cartes 22 px, boutons/pastilles 999 px, kickers à bord fin
(`2.5px rgba(10,10,10,.3)`), style bento + « PIXEL SYSTEM V1 » (pixel-art en grille).

## Typographie

Space Grotesk (Google Fonts, OFL) 400–700 ; titres 700, tracking −0.04em,
interligne 1.05. Arabe : Tajawal 400/700 (version AR du site).

## Textes et chiffres du site (réutilisables)

- Accroche : « Étudie en Russie. Change ta vie. »
- « Universités de rang mondial · Frais dès 2 200€/an · Accompagnement total direct
  depuis la Tunisie. »
- Garanties : Visa garanti par contrat · 1ère consultation gratuite · Frais payés à
  l'université · Accueil à l'aéroport · Logement garanti à 100 % · Tuteur bilingue.
- Chiffres : +1 200 étudiants tunisiens placés · 40+ universités d'État
  partenaires · 7 ans d'expérience (depuis 2018).
- Filières (durée · prix/an) : Médecine générale 6 ans · 3 500 € ; Ingénierie & Tech
  4–5 ans · 2 800 € ; Pharmacie 5 ans · 3 200 € ; Médecine dentaire 5 ans · 3 200 € ;
  Économie & Business 4 ans · 2 200 €.
- Urgence : « Session 2026–2027 : dépôt des dossiers ouvert — les places d'État sont
  limitées. »
- CTA : « Commencer mon dossier gratuit ↗ », « Réserver un appel gratuit → »,
  « Postuler ».
- Contact : WhatsApp Business +7 996 433 4489 · contact@russieetudes.com.
- RusStudy est un projet de Master Services (accompagnement international depuis 2018).

## Photos du site (Unsplash, licence Unsplash)

| ID | Sujet (alt du site) |
|---|---|
| photo-1513326738677-b964603b136d | Cathédrale Saint-Basile, Moscou (utilisée) |
| photo-1547448415-e9f5b28e570d | Kremlin et Place Rouge sous la neige |
| photo-1556610961-2fecc5927173 | Pont ouvert sur la Néva, Saint-Pétersbourg |
| photo-1519452635265-7b1fbfd1e4e0 | Amphithéâtre aux sièges en bois (utilisée) |
| photo-1522202176988-66273c2fd55f | Étudiants internationaux en groupe |
| photo-1523240795612-9a054b0db644 | Étudiants en bibliothèque |
| photo-1520106212299-d99c443e4568 | Place Rouge de nuit sous la neige |
| photo-1541339907198-e08756dedf3f | Diplômés lançant leurs toques (utilisée — **prise à Singapour**) |

URL de téléchargement HD : `https://images.unsplash.com/<ID>?auto=format&fit=max&w=2000&q=88&fm=jpg`.
Ne pas utiliser les portraits des témoignages (photos stock présentées comme des
étudiants).
