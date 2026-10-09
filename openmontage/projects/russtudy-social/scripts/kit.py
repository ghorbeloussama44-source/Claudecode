#!/usr/bin/env python3
"""Publishing kit for the RusStudy social series, generated from episodes/*.json:

  kit/01_voix_off.md   timed voice-over scripts (French + derja) for the 9 videos
  kit/02_legendes.md   captions + hashtags to paste on TikTok / Instagram / Facebook

usage: python3 scripts/kit.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import ROOT, load_episodes, timings  # noqa: E402

KIT = ROOT / "kit"
TEL = "+7 996 433 4489"


def ts(t):
    m, s = divmod(t, 60)
    s = f"{s:04.1f}".replace(".", ",")
    return f"{int(m)}:{s}"


def screen(sc, lang):
    d = sc.get(lang, {})
    t = sc["type"]
    if t == "hook":
        return " ".join(d["title"])
    if t == "question":
        return f"{d['label']} {sc['n']}/{sc['of']} : " + " ".join(d["text"])
    if t == "day":
        return f"{d['label']} {sc['n']} — {d['text']}"
    if t == "price":
        return f"{d['kicker']} · {d['des']} 12 000 {d['cur']} · {d['pill']}"
    if t == "receipt":
        return f"{len(d['lines'])} lignes « {d['inc']} » · {d['total_v']} · options : " + ", ".join(d["opts"]) if lang == "fr" else f"{len(d['lines'])} « {d['inc']} » · {d['total_v']}"
    if t in ("steps",):
        return " → ".join(x[0] for x in d["items"])
    if t == "points":
        return " · ".join(x[1] for x in d["items"])
    if t in ("checklist", "recap", "chips"):
        return " · ".join(d["items"])
    if t == "chat":
        return f"WhatsApp : « {d['out']} » → « {d['in1']} » → {d['card_t']} ({d['card_s']}) → « {d['in2']} »"
    if t == "stats":
        return " · ".join(f"{v} {l}" for v, l in d["items"])
    if t == "cta":
        return f"RusStudy. · WhatsApp {TEL} · russieetudes.com · 1ère consultation gratuite · Lien en bio" if lang == "fr" else f"RusStudy. · WhatsApp {TEL} · russieetudes.com · أوّل استشارة بلاش · الرابط في البيو"
    return ""


INTRO_VO = """# Voix off — scripts minutés (FR + derja)

Les 18 vidéos sont prêtes à publier telles quelles (musique douce incluse, −20 LUFS) : on ajoute la voix
par-dessus dans CapCut, ou directement dans TikTok / Instagram (outil « Voix off »).

## Comment enregistrer (5 minutes par vidéo)

1. Téléphone à 15–20 cm de la bouche, pièce calme (une chambre avec rideaux et lit, pas une cuisine).
2. Ouvrir la vidéo dans CapCut → **Audio → Voix off** → enregistrer en regardant l'écran : chaque ligne du
   tableau commence au temps indiqué (le texte à l'écran sert de repère).
3. Volume : voix à 100 %, **son d'origine (musique) à 30–40 %**. Ou couper la musique et choisir un son
   tendance dans TikTok / Instagram (bonus de portée).
4. Sous-titres automatiques ON (TikTok « Sous-titres », CapCut « Légendes auto ») : beaucoup regardent sans le son.
5. Parler comme à un ami : phrases courtes, sourire dans la voix. Une prise ratée ? On refait seulement la ligne.

## Témoignages (vidéos 01, 02, 03) : règles d'or

- **Uniquement de vrais étudiants / parents RusStudy**, qui répondent avec leurs mots. On ne leur écrit pas le
  texte, on ne fait jamais parler une voix générée à leur place.
- Accord écrit avant publication (un message WhatsApp suffit) : « J'accepte que RusStudy publie ma voix et mon
  prénom dans ses vidéos. »
- Le plus simple : envoyer les questions en vocal WhatsApp à l'étudiant, il répond question par question
  (8 secondes max par réponse), puis on pose ses vocaux sur la vidéo dans CapCut.
- Pas de promesse absolue dans les réponses (« visa garanti à 100 % », « admission assurée »…) : on coupe au montage.
"""


def vo_doc(eps):
    out = [INTRO_VO]
    for k, ep in enumerate(eps, 1):
        starts, D = timings(ep)
        kind = "Témoignage (vraie voix d'étudiant / de parent)" if ep["series"] == "temoignage" else "Conseil (voix off d'un conseiller RusStudy)"
        out.append(f"\n## {ep['slug'][:2]} · {ep['title']['fr']} — {D:.1f} s".replace(".", ","))
        out.append(f"\n*{kind}* · vidéos : `renders/{ep['slug']}_fr.mp4` et `renders/{ep['slug']}_derja.mp4`\n")
        out.append("| Temps | À l'écran (FR) | Voix off FR | Voix off derja |")
        out.append("|---|---|---|---|")
        for sc, t0 in zip(ep["scenes"], starts):
            vo = sc.get("vo", {})
            out.append(f"| {ts(t0)} → {ts(t0 + sc['dur'])} | {screen(sc, 'fr')} | {vo.get('fr', '')} | {vo.get('ar', '')} |")
    return "\n".join(out) + "\n"


INTRO_CAP = """# Légendes et hashtags (copier-coller)

Règle simple : **derja sur TikTok et Facebook, français sur Instagram** la première semaine, puis on
inverse pour voir ce qui marche le mieux. Chaque légende renvoie vers WhatsApp (lien en bio).
Couverture : `renders/covers/<vidéo>.png` (Instagram et Facebook permettent de l'importer ; sur TikTok,
choisir l'image vers 2,5 s).
"""


def cap_doc(eps):
    out = [INTRO_CAP]
    for ep in eps:
        out.append(f"\n## {ep['slug'][:2]} · {ep['title']['fr']}\n")
        out.append(f"**Français** — `renders/{ep['slug']}_fr.mp4` · couverture `renders/covers/{ep['slug']}_fr.png`\n")
        out.append("```text\n" + ep["caption"]["fr"] + "\n\n" + ep["hashtags"] + "\n```\n")
        out.append(f"**Derja** — `renders/{ep['slug']}_derja.mp4` · couverture `renders/covers/{ep['slug']}_derja.png`\n")
        out.append("```text\n" + ep["caption"]["ar"] + "\n\n" + ep["hashtags"] + "\n```")
    return "\n".join(out) + "\n"


def main():
    KIT.mkdir(exist_ok=True)
    eps = load_episodes()
    (KIT / "01_voix_off.md").write_text(vo_doc(eps))
    (KIT / "02_legendes.md").write_text(cap_doc(eps))
    print("kit/01_voix_off.md, kit/02_legendes.md")


if __name__ == "__main__":
    main()
