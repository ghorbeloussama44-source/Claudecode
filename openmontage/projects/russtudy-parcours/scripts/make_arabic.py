#!/usr/bin/env python3
"""Build the Tunisian Arabic (derja) versions from the French compositions.

The French files stay the single source of truth: this script reads the vertical master
(`hyperframes/index.html`) and the 16:9 version generated from it (`hyperframes-16x9/`, run
`python3 scripts/make_landscape.py` first) and writes `hyperframes-ar/` and `hyperframes-ar-16x9/`
(40 s; `scripts/make_slow.py` then derives the 60 s versions). It
  - swaps every on-screen French text for its derja translation (asserted substitutions: a text
    edited in the French master makes this script stop instead of silently keeping French);
  - keeps the animation, the timing and the soundtrack untouched;
  - adapts the typography to Arabic script: Cairo for the Arabic glyphs (Space Grotesk keeps the
    Latin text, the digits and the wordmark), no letter-spacing (it would break the joins), taller
    reveal masks for the dots and descenders, words instead of letters wherever the French
    animates letter by letter (titles, tagline, split-flap board);
  - aligns the Arabic text right-to-left: titles, captions and price column hug the right margin
    in 9:16 (the right edge of the text column in 16:9), the phone, the cards and the receipt are
    mirrored inside, the HUD fills from the right. Travel diagrams (boarding pass, flight map,
    Moscow -> Kazan bar) keep the geography left to right; phone number and site stay LTR.

    python3 scripts/make_landscape.py && python3 scripts/make_arabic.py && python3 scripts/make_slow.py
"""
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAIRS = [("hyperframes", "hyperframes-ar"), ("hyperframes-16x9", "hyperframes-ar-16x9")]
NB = " "  # no-break space: a "common separator", keeps "12 000" in one LTR number inside Arabic text

# ---------------------------------------------------------------- on-screen texts (French -> derja)
TEXTS = [
    ("</title>", " · derja</title>", 1),
    ('<html lang="fr"', '<html lang="ar"', 1),
    # S1 — the WhatsApp message
    ('<div class="ln"><span class="w">Tout</span> <span class="w">commence</span></div>',
     '<div class="ln"><span class="w">كلّ</span> <span class="w">شي</span> <span class="w">يبدا</span></div>', 1),
    ('<div class="ln"><span class="w">par</span> <span class="w">un</span> <span class="w" id="s1-msg">message.<i id="s1-ul"></i></span></div>',
     '<div class="ln"><span class="w" id="s1-msg">بميساج.<i id="s1-ul"></i></span></div>', 1),
    ('<span id="st-on">en ligne</span><span id="st-typ">écrit…</span>', '<span id="st-on">متّصل</span><span id="st-typ">يكتب…</span>', 1),
    ('<div id="chat-date">AUJOURD’HUI</div>', '<div id="chat-date">اليوم</div>', 1),
    ("</span> · compte professionnel</div>", "</span> · حساب تجاري</div>", 1),
    ("<div>Réponse d’un conseiller sous 24 h, 7j/7</div>", "<div>مستشار يجاوبك في أقل من 24 ساعة، 7/7</div>", 1),
    ('<div class="l">Salam ! Je veux</div>', '<div class="l">سلام! نحب نقرا</div>', 1),
    ('<div class="l">étudier en Russie.</div>', '<div class="l">في روسيا.</div>', 1),
    ('<div class="l">Bienvenue ! On s’occupe</div>', '<div class="l">مرحبا بيك! نتلهاو</div>', 1),
    ('<div class="l">de tout, de A à Z.</div>', '<div class="l">بكلّ شي، من الألف للياء.</div>', 1),
    ('<div id="r2-t1">Appel d’orientation</div>', '<div id="r2-t1">مكالمة توجيه</div>', 1),
    ('<div id="r2-t2">15 min · gratuit · sans engagement</div>', '<div id="r2-t2">15 دقيقة · بلاش · بلا التزام</div>', 1),
    ('<div id="r2-btn">Réserver un appel gratuit</div>', '<div id="r2-btn">احجز مكالمة بلاش</div>', 1),
    ('<div id="inp-ph">Message</div>', '<div id="inp-ph">رسالة</div>', 1),
    ('const S1_TXT = "Salam ! Je veux étudier en Russie.";', 'const S1_TXT = "سلام! نحب نقرا في روسيا.";', 1),
    # HUD — the five steps
    ("</span>Consultation gratuite</div>", "</span>استشارة بلاش</div>", 1),
    ("</span>Préparation du dossier</div>", "</span>تحضير الدوسي</div>", 1),
    ("</span>Admission officielle</div>", "</span>قبول رسمي</div>", 1),
    ("</span>Visa &amp; assurance</div>", "</span>الفيزا والتأمين</div>", 1),
    ("</span>En route · Tunis – Moscou</div>", "</span>في الطريق · تونس – موسكو</div>", 1),
    ("</span>Accueil &amp; installation</div>", "</span>الاستقبال والسكنى</div>", 1),
    ("</span>Objectif atteint</div>", "</span>الهدف تحقّق</div>", 1),
    # S2 — 01 free consultation
    ('<span class="tw">On analyse</span>', '<span class="tw">نحلّلو</span>', 1),
    ('<span class="tw">ton <span class="hlb">profil.</span></span>', '<span class="tw"><span class="hlb">بروفيلك.</span></span>', 1),
    ('<div id="s2-c1">Appel d’orientation</div>', '<div id="s2-c1">مكالمة توجيه</div>', 1),
    ('<div id="s2-c2">15 min · Zoom, téléphone ou WhatsApp</div>', '<div id="s2-c2">15 دقيقة · Zoom، تليفون ولا WhatsApp</div>', 1),
    ('<div id="s2-free">GRATUIT</div>', '<div id="s2-free">بلاش</div>', 1),
    ('<div id="s2-ph">ANALYSE DE TON PROFIL</div>', '<div id="s2-ph">تحليل البروفيل متاعك</div>', 1),
    ('<div class="pt1">Notes du Bac</div>', '<div class="pt1">أعداد الباك</div>', 1),
    ('<div class="pt2">Résultats &amp; moyenne</div>', '<div class="pt2">النتايج والمعدّل</div>', 1),
    ('<div class="pt1">Projet : Médecine</div>', '<div class="pt1">المشروع: الطب</div>', 1),
    ('<div class="pt2">Ta filière idéale</div>', '<div class="pt2">الشعبة اللي تناسبك</div>', 1),
    ('<div class="pt1">Ville &amp; budget</div>', '<div class="pt1">المدينة والميزانية</div>', 1),
    ('<div class="pt2">Moscou, Saint-Pétersbourg, Kazan…</div>', '<div class="pt2">موسكو، سان بطرسبرغ، قازان…</div>', 1),
    ('<div id="s2-pk">TON PLAN</div>', '<div id="s2-pk">البرنامج متاعك</div>', 1),
    ('<div id="s2-pm">Médecine générale · Kazan</div>', '<div id="s2-pm">طب عام · قازان</div>', 1),
    ('<div id="s2-ps">Université d’État partenaire</div>', '<div id="s2-ps">جامعة حكومية شريكة</div>', 1),
    # S3 — 02 the file
    ('<span class="tw">On prépare</span>', '<span class="tw">نحضّرو</span>', 1),
    ('<span class="tw">ton dossier.</span>', '<span class="tw">الدوسي متاعك.</span>', 1),
    ('<div id="s3-sub">Traduction assermentée + légalisation</div>', '<div id="s3-sub">ترجمة محلّفة + مصادقة</div>', 1),
    ("<div>PASSEPORT</div>", "<div>جواز السفر</div>", 1),
    ("<div>DIPLÔME</div><div>DU BAC</div>", "<div>شهادة</div><div>الباك</div>", 1),
    ("<div>RELEVÉS</div><div>DE NOTES</div>", "<div>كشف</div><div>الأعداد</div>", 1),
    ("<div>ACTE DE</div><div>NAISSANCE</div>", "<div>مضمون</div><div>الولادة</div>", 1),
    ('<div id="fold-lab">DOSSIER</div>', '<div id="fold-lab">الدوسي</div>', 1),
    ('<div id="st-trad" class="stamp">TRADUIT</div>', '<div id="st-trad" class="stamp">مترجم</div>', 1),
    ('<div id="st-leg" class="stamp">LÉGALISÉ</div>', '<div id="st-leg" class="stamp">مصادق عليه</div>', 1),
    # S4 — 03 admission
    ('<span class="tw">Admission</span>', '<span class="tw">قبول</span>', 1),
    ('<span class="tw">officielle.</span>', '<span class="tw">رسمي.</span>', 1),
    ('<div id="lt-k">LETTRE D’INVITATION D’ÉTAT</div>', '<div id="lt-k">دعوة رسمية من الدولة</div>', 1),
    ('<div id="lt-t">Admission confirmée</div>', '<div id="lt-t">قبولك تأكّد</div>', 1),
    ('<div id="lt-s">Médecine générale · 2026–2027</div>', '<div id="lt-s">طب عام · 2026–2027</div>', 1),
    ('<div id="st-admis" class="stamp">ADMIS<span id="admis-ck"></span></div>', '<div id="st-admis" class="stamp">مقبول<span id="admis-ck"></span></div>', 1),
    # S5 — 04 visa & insurance
    ('<span class="tw">Visa d’études</span>', '<span class="tw">فيزا الدراسة</span>', 1),
    ('<span class="tw">+ assurance.</span>', '<span class="tw">+ التأمين.</span>', 1),
    ('<div class="pg-h">VISAS</div>', '<div class="pg-h">تأشيرات</div>', 1),
    ('<div id="visa-t">VISA D’ÉTUDES</div>', '<div id="visa-t">تأشيرة دراسة</div>', 1),
    ('<div id="visa-c">RUSSIE</div>', '<div id="visa-c">روسيا</div>', 1),
    ('<div class="c1">PASSEPORT</div>', '<div class="c1">جواز سفر</div>', 1),
    ('<div id="ins-t">ASSURANCE MÉDICALE</div>', '<div id="ins-t">تأمين صحّي</div>', 1),
    ('<div id="ins-s">Couverture 1 an</div>', '<div id="ins-s">تغطية عام كامل</div>', 1),
    # boarding pass
    ('<div class="k">CARTE D’EMBARQUEMENT</div>', '<div class="k">بطاقة الركوب</div>', 1),
    ('<div class="bp-city" style="left: 38px">Tunis</div>', '<div class="bp-city" style="left: 38px">تونس</div>', 1),
    ('<div class="bp-city" style="left: 424px">Moscou</div>', '<div class="bp-city" style="left: 424px">موسكو</div>', 1),
    ("<div>VOL<b>RS 2026</b></div>", "<div>الرحلة<b>RS 2026</b></div>", 1),
    ("<div>PORTE<b>7</b></div>", "<div>البوابة<b>7</b></div>", 1),
    ("<div>EMBARQ.<b>08:40</b></div>", "<div>الركوب<b>08:40</b></div>", 1),
    ('<div id="bp-seat">SIÈGE<b>12A</b></div>', '<div id="bp-seat">المقعد<b>12A</b></div>', 1),
    # S6 — departure
    ('<span class="tw">Bon</span>', '<span class="tw">تمشي</span>', 1),
    ('<span class="tw">voyage&#8239;!</span>', '<span class="tw">بالسلامة!</span>', 1),
    # S7 — flight
    ('<span id="flag-tn"></span>TUNIS</div>', '<span id="flag-tn"></span>تونس</div>', 1),
    ('<span id="flag-ru"></span>MOSCOU<span id="mow-chk"></span>', '<span id="flag-ru"></span>موسكو<span id="mow-chk"></span>', 1),
    ('<span class="tw">Cap sur Moscou.</span>', '<span class="tw">يلّا على موسكو!</span>', 1),
    ('<div id="nt-time">maintenant</div>', '<div id="nt-time">توّا</div>', 1),
    ('<div id="nt-b">Ton tuteur t’attend à l’arrivée. Bon vol&#8239;!</div>', '<div id="nt-b">المرافق متاعك يستنّى فيك كي توصل. رحلة سعيدة!</div>', 1),
    # S8 — arrivals hall
    ('<div id="flap-h1">ARRIVÉES</div>', '<div id="flap-h1">الوصول</div>', 1),
    ('<div id="flap-h2">RS 2026 · À L’HEURE</div>', '<div id="flap-h2">RS 2026 · في الوقت</div>', 1),
    ('<div id="sign-sub">ACCUEIL ÉTUDIANTS</div>', '<div id="sign-sub">استقبال الطلبة</div>', 1),
    ('<div id="s8-cap">Un tuteur bilingue t’attend à l’aéroport.</div>', '<div id="s8-cap">مرافق يحكي لغتين يستنّى فيك في المطار.</div>', 1),
    # TR — train or car to the university city
    ('<span class="tw">Train ou voiture,</span>', '<span class="tw">تران ولا كرهبة،</span>', 1),
    ('<span class="tw">jusqu’à ta ville.</span>', '<span class="tw">حتى لمدينتك.</span>', 1),
    ('<div id="tr-a">MOSCOU</div>', '<div id="tr-a">موسكو</div>', 1),
    ('<div id="tr-b">KAZAN<span id="tr-ok"></span></div>', '<div id="tr-b">قازان<span id="tr-ok"></span></div>', 1),
    ('<div id="tr-sub">Organisé sur demande · en option</div>', '<div id="tr-sub">حسب الطلب · اختياري</div>', 1),
    # S9 — dorm
    ('<span class="tw">Foyer</span>', '<span class="tw">المبيت</span>', 1),
    ('<span class="tw">universitaire.</span>', '<span class="tw">الجامعي.</span>', 1),
    ('<span id="s9-chk"></span>1 an inclus</div>', '<span id="s9-chk"></span>عام كامل مشمول</div>', 1),
    ('<div id="kc-k">FOYER UNIVERSITAIRE</div>', '<div id="kc-k">المبيت الجامعي</div>', 1),
    ('<div id="kc-n">CHAMBRE 412</div>', '<div id="kc-n">غرفة 412</div>', 1),
    # S10 — first day at university
    ('alt="Amphithéâtre universitaire"', 'alt="مدرّج جامعي"', 1),
    ('<span class="tw">Premier jour</span>', '<span class="tw">أوّل نهار</span>', 1),
    ('<span class="tw">à l’université.</span>', '<span class="tw">في الجامعة.</span>', 1),
    ("<span>CARTE D’ÉTUDIANT</span>", "<span>بطاقة طالب</span>", 1),
    ('<div class="k">FACULTÉ</div><div class="v">Médecine générale</div>', '<div class="k">الكلية</div><div class="v">طب عام</div>', 1),
    ('<div class="k">UNIVERSITÉ</div><div class="v2">Université d’État · Kazan</div>', '<div class="k">الجامعة</div><div class="v2">جامعة حكومية · قازان</div>', 1),
    ('<div class="k">N° ÉTUDIANT</div>', '<div class="k">رقم الطالب</div>', 1),
    # S11 — price (12 000 DT = « 12 000 د.ت »)
    ('<div id="s11-deco" data-layout-ignore>DT</div>', '<div id="s11-deco" data-layout-ignore>د.ت</div>', 1),
    ('<div id="s11-k" class="kicker">Budget 1ère année</div>', '<div id="s11-k" class="kicker">ميزانية العام الأوّل</div>', 1),
    ('<div id="s11-des" class="h">dès</div>', '<div id="s11-des" class="h">ابتداءً من</div>', 1),
    ('<div id="s11-cur">DT</div>', '<div id="s11-cur">د.ت</div>', 1),
    ('<div id="s11-pill">études + installation</div>', '<div id="s11-pill">القراية + الاستقرار</div>', 1),
    ("<span>1ÈRE ANNÉE</span></div>", "<span>العام الأوّل</span></div>", 1),
    ('<span>Frais universitaires</span><i class="dt"></i><span class="v">dès 7 500 DT</span>',
     f'<span>معاليم الجامعة</span><i class="dt"></i><span class="v">من 7{NB}500 د.ت</span>', 1),
    ("<span>Consulting &amp; orientation</span>", "<span>الاستشارة والتوجيه</span>", 1),
    ("<span>Dossier visa</span>", "<span>ملف الفيزا</span>", 1),
    ("<span>Accueil aéroport</span>", "<span>الاستقبال في المطار</span>", 1),
    ("<span>Foyer universitaire · 1 an</span>", "<span>المبيت الجامعي · عام كامل</span>", 1),
    ("<span>Assurance médicale</span>", "<span>التأمين الصحّي</span>", 1),
    ('<span class="v">inclus<i class="ok"></i></span>', '<span class="v">مشمول<i class="ok"></i></span>', 5),
    ('<span class="a">TOTAL 1ÈRE ANNÉE</span><span class="b">dès 12 000 DT</span>',
     f'<span class="a">المجموع للعام الأوّل</span><span class="b">من 12{NB}000 د.ت</span>', 1),
    ('<div class="rc-oh">NON INCLUS · EN OPTION SUR DEMANDE</div>', '<div class="rc-oh">موش مشمول · اختياري حسب الطلب</div>', 1),
    ("<span>Billet d’avion</span>", "<span>تذكرة الطيارة</span>", 1),
    ("<span>Train ou voiture jusqu’à ta ville</span>", "<span>تران ولا كرهبة حتى لمدينتك</span>", 1),
    ("<span>Hôtel &amp; visites à Moscou</span>", "<span>أوتيل وزيارات في موسكو</span>", 1),
    ('<span class="v">sur devis</span>', '<span class="v">حسب الديفي</span>', 3),
    ('<div id="st-tc" class="stamp"><span>SANS FRAIS</span><span>CACHÉS</span></div>', '<div id="st-tc" class="stamp"><span>بلا مصاريف</span><span>مخفية</span></div>', 1),
    # S12 — logo + WhatsApp CTA (number and site unchanged)
    ('<div id="wa-t">Écris-nous sur WhatsApp</div>', '<div id="wa-t">ابعثلنا على WhatsApp</div>', 1),
    ('<div id="cta-chip" class="chip">1ère consultation gratuite</div>', '<div id="cta-chip" class="chip">أوّل استشارة بلاش</div>', 1),
]

# ---------------------------------------------------------------- animation changes for Arabic script
ANIM = [
    # reveal masks are taller in derja (see .mask below): start further down so nothing peeks out
    ("yPercent: 115", "yPercent: 180", 4),
    # S10 title: word by word (letters must stay joined)
    (
        """      $$("#s10-t .tw").forEach((tw) => {
        tw.innerHTML = tw.textContent
          .split("")
          .map((c) => `<span class="ch">${c === " " ? "&nbsp;" : c}</span>`)
          .join("");
      });""",
        """      $$("#s10-t .tw").forEach((tw) => {
        // derja: word by word (splitting Arabic into letters would break the joins)
        tw.innerHTML = tw.textContent
          .split(" ")
          .map((w) => `<span class="ch">${w}</span>`)
          .join(" ");
      });""",
        1,
    ),
    ('ease: "expo.out", stagger: 0.018 }, T10 + 0.05);', 'ease: "expo.out", stagger: 0.07 }, T10 + 0.05);', 1),
    # tagline under the logo: the words gather from both sides (right-to-left order)
    (
        """      const TAG_TXT = "ÉTUDES EN RUSSIE";
      $("#lg-tag").innerHTML = TAG_TXT.split("")
        .map((c) => `<span class="tg" style="display:inline-block">${c === " " ? "&nbsp;" : c}</span>`)
        .join("");
      $$("#lg-tag .tg").forEach((g, i, all) => {
        const k = i - (all.length - 1) / 2;
        tl.fromTo(g, { x: k * 34, opacity: 0 }""",
        """      const TAG_TXT = "الدراسة في روسيا";
      $("#lg-tag").innerHTML = TAG_TXT.split(" ")
        .map((w) => `<span class="tg" style="display:inline-block">${w}</span>`)
        .join(" ");
      $$("#lg-tag .tg").forEach((g, i, all) => {
        const k = (all.length - 1) / 2 - i;
        tl.fromTo(g, { x: k * 90, opacity: 0 }""",
        1,
    ),
    # split-flap board: Arabic letters cannot be shown one per cell, so each row is one shaped
    # phrase revealed column by column (.fw windows, as wide as a cell plus the gaps, so the letters
    # stay joined across the cells; the split line is drawn over them). The cells keep the French
    # timings (the flap clatter of build_audio.py still matches), mirrored to fill from the right
    (
        """      const FLAP = ["BIENVENUE", "EN RUSSIE"];
      const FL_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
      const flapRng = mulberry32(2108);
      const flapCells = [];
      FLAP.forEach((word, r) =>
        word.split("").forEach((ch, c) => {
          const d = document.createElement("div");
          d.className = "fc";
          d.style.left = 32 + c * 96 + "px";
          d.style.top = 86 + r * 140 + "px";
          d.innerHTML = `<span class="fch"></span><i class="ffl"></i><b class="fsp"></b>`;
          $("#flap").appendChild(d);
          flapCells.push({ ch: d.querySelector(".fch"), fl: d.querySelector(".ffl"), target: ch === " " ? "" : ch, r, c, start: 20.96 + c * 0.012 + r * 0.02, settle: 21.02 + c * 0.07 + r * 0.16 + flapRng() * 0.04 });
        }),
      );""",
        """      const FLAP = ["مرحبا بيك", "في روسيا"];
      const FL_SET = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي";
      const flapRng = mulberry32(2108);
      const flapCells = [];
      FLAP.forEach((phrase, r) => {
        for (let c = 0; c < 9; c++) {
          const x = 32 + (8 - c) * 96;
          const d = document.createElement("div");
          d.className = "fc";
          d.style.left = x + "px";
          d.style.top = 86 + r * 140 + "px";
          d.innerHTML = `<span class="fch"></span><i class="ffl"></i><b class="fsp"></b>`;
          $("#flap").appendChild(d);
          const w = document.createElement("div");
          w.className = "fw";
          w.style.left = x - 4 + "px";
          w.style.top = 86 + r * 140 + "px";
          w.innerHTML = `<span class="fsl" style="left: ${4 - x}px">${phrase}</span><b class="fsp"></b>`;
          $("#flap").appendChild(w);
          flapCells.push({ ch: d.querySelector(".fch"), sl: w, fl: d.querySelector(".ffl"), target: "", r, c, start: 20.96 + c * 0.012 + r * 0.02, settle: 21.02 + c * 0.07 + r * 0.16 + flapRng() * 0.04 });
        }
      });""",
        1,
    ),
    (
        "          if (f.ch.textContent !== ch) f.ch.textContent = ch;\n",
        "          if (f.ch.textContent !== ch) f.ch.textContent = ch;\n          f.sl.style.opacity = T >= f.settle ? 1 : 0;\n",
        1,
    ),
]

FONT_FACE = """      @font-face {
        font-family: "Cairo";
        src: url("assets/fonts/Cairo-arabic.woff2") format("woff2");
        font-weight: 400 900;
        font-display: block;
        unicode-range: U+0600-06FF, U+0750-077F, U+0870-088E, U+0890-0891, U+0898-08E1, U+08E3-08FF, U+200C-200E,
          U+2010-2011, U+204F, U+2E41, U+FB50-FDFF, U+FE70-FE74, U+FE76-FEFC;
      }
"""

# ---------------------------------------------------------------- CSS (both formats)
CSS_COMMON = """
      /* ================= derja (arabe tunisien) — generated by scripts/make_arabic.py ================= */
      /* Arabic glyphs come from Cairo; Latin text, digits and the wordmark stay in Space Grotesk.
         No letter-spacing on Arabic (it breaks the joins); taller reveal masks for dots and
         descenders; right-to-left text, mirrored cards; documents and route diagrams keep their layout. */
      #root {
        font-family: "Space Grotesk", "Cairo", sans-serif;
      }
      .wm {
        direction: ltr;
        unicode-bidi: isolate;
      }
      .mask {
        padding: 0.32em 0.08em 0.4em;
        margin: -0.32em -0.08em -0.4em;
      }
      .title .ln {
        height: 1.16em;
      }
      #s6-t .ln {
        height: 1.2em;
      }
      .h,
      .kicker,
      .chip,
      .stamp,
      .hl-i,
      #chat-date,
      #chat-biz,
      .bub,
      #r2-t1,
      #r2-t2,
      #r2-btn,
      #s2-c1,
      #s2-free,
      #s2-ph,
      .prow .pt1,
      #s2-pk,
      #s2-pm,
      #s3-sub,
      .sh .band,
      #fold-lab,
      #lt-k,
      #lt-t,
      #pp-page .pg-h,
      #visa-t,
      #visa-c,
      #pp-cover .c1,
      #ins-t,
      #bp-band .k,
      #bp-info,
      #bp-seat,
      .pinlabel,
      #nt-b,
      #flap-h1,
      #flap-h2,
      #sign-sub,
      #s8-cap,
      #tr-a,
      #tr-b,
      #tr-sub,
      #kc-k,
      #kc-n,
      #sc-band,
      .sc-f .k,
      .sc-f .v,
      .sc-f .v2,
      #s11-pill,
      .rc-h,
      .rc-l,
      .rc-tot .a,
      .rc-tot .b,
      .rc-oh,
      #lg-tag,
      #wa-t {
        letter-spacing: 0;
      }
      #ch-st span,
      #s2-c1,
      #s2-c2,
      #s2-ph,
      .prow .pt1,
      .prow .pt2,
      #s2-pk,
      #s2-pm,
      #s2-ps,
      #s3-sub,
      #fold-lab,
      #lt-k,
      #lt-t,
      #lt-s,
      #pp-page .pg-h,
      #visa-t,
      #visa-c,
      #pp-cover .c1,
      #ins-t,
      #ins-s,
      #bp-band .k,
      .bp-city,
      #bp-info,
      #bp-seat,
      #nt-time,
      #nt-b,
      #flap-h1,
      #flap-h2,
      #sign-sub,
      #s8-cap,
      #tr-sub,
      #kc-k,
      #kc-n,
      .sc-f .k,
      .sc-f .v,
      .sc-f .v2,
      #lg-tag {
        line-height: 1.28;
      }
      .sh .band {
        line-height: 1.3;
      }
      #s1-title,
      .title,
      #s6-t,
      #s7-t,
      .hl-i,
      #chat-biz,
      .bub,
      #r2-t1,
      #r2-t2,
      #inp-txt,
      #s2-c1,
      #s2-c2,
      #s2-ph,
      .prow .pt1,
      .prow .pt2,
      #s2-pk,
      #s2-pm,
      #s2-ps,
      #s3-sub,
      .sh .band,
      .stamp,
      #lt-k,
      #lt-t,
      #lt-s,
      #ins-t,
      #ins-s,
      #nt-b,
      #flap-h2,
      #s8-cap,
      #tr-sub,
      .chip,
      #sc-band,
      .sc-f,
      #s11-des,
      .rc-h,
      .rc-l,
      .rc-tot,
      .rc-oh,
      #lg-tag,
      #wa {
        direction: rtl;
      }
      /* S1: phone UI in Arabic (bubbles, input field, booking card) */
      #s1-title {
        transform-origin: 100% 100%;
      }
      #s1-ul {
        left: 8px;
        right: 2px;
        bottom: -0.26em;
        transform-origin: 100% 50%;
      }
      .bub .meta {
        right: auto;
        left: 16px;
      }
      #r2-ic {
        left: auto;
        right: 20px;
      }
      #r2-t1,
      #r2-t2 {
        left: auto;
        right: 100px;
      }
      #inp-ph,
      #inp-txt {
        left: auto;
        right: 28px;
      }
      #inp-caret {
        margin-left: 0;
        margin-right: 2px;
      }
      /* HUD: steps fill from the right, labels on the right, wordmark on the left */
      #hud-lab {
        left: auto;
        right: 28px;
      }
      #hud-wm {
        right: auto;
        left: 28px;
      }
      .hl-i {
        left: auto;
        right: 0;
      }
      .seg i,
      .seg b {
        transform-origin: 100% 50%;
      }
      /* S2: call card, profile analysis, plan (mirrored) */
      #s2-av,
      .s2-ring {
        left: auto;
        right: 32px;
      }
      #s2-c1,
      #s2-c2,
      #s2-wave {
        left: auto;
        right: 180px;
      }
      #s2-timer,
      #s2-free {
        right: auto;
        left: 36px;
      }
      #s2-ph {
        left: auto;
        right: 40px;
      }
      #s2-pct {
        right: auto;
        left: 40px;
      }
      .prow .scan {
        transform-origin: 100% 50%;
      }
      .prow .pic {
        left: auto;
        right: 20px;
      }
      .prow .pt1,
      .prow .pt2 {
        left: auto;
        right: 106px;
      }
      .prow .pck {
        right: auto;
        left: 24px;
      }
      #s2-pk,
      #s2-pm,
      #s2-ps {
        left: auto;
        right: 40px;
      }
      #s2-pa {
        right: auto;
        left: 34px;
      }
      #s2-pa svg {
        transform: scaleX(-1);
      }
      /* S3: sheets and folder */
      .sh .ico,
      .sh .sl {
        left: auto;
        right: 16px;
      }
      #fold-lab {
        left: auto;
        right: 40px;
      }
      #fold-num {
        right: auto;
        left: 40px;
      }
      /* S4: invitation letter */
      #lt-k,
      #lt-t,
      #lt-s,
      .lt-l,
      #lt-sig {
        left: auto;
        right: 36px;
      }
      #lt-seal {
        right: auto;
        left: 36px;
      }
      /* S5: insurance card */
      #ins-ic,
      #ins-t,
      #ins-s,
      #ins-n {
        left: auto;
        right: 30px;
      }
      #ins-chip {
        right: auto;
        left: 30px;
      }
      /* S7: notification */
      #nt-ic {
        left: auto;
        right: 26px;
      }
      #nt-a,
      #nt-b {
        left: auto;
        right: 132px;
      }
      #nt-time {
        right: auto;
        left: 32px;
      }
      /* S8: arrivals board — each row is one Arabic phrase, revealed column by column */
      #flap-h1 {
        left: auto;
        right: 34px;
      }
      #flap-h2 {
        right: auto;
        left: 34px;
      }
      .fch {
        margin-top: -14px;
        font-size: 76px;
      }
      .fw {
        position: absolute;
        width: 96px;
        height: 124px;
        overflow: hidden;
        opacity: 0;
      }
      .fw .fsp {
        width: 96px;
      }
      .fsl {
        position: absolute;
        top: 0;
        width: 920px;
        height: 124px;
        line-height: 124px;
        margin-top: -16px;
        text-align: center;
        direction: rtl;
        font-size: 84px;
        font-weight: 800;
        color: #fff;
        white-space: nowrap;
      }
      /* S10: student card fields right-aligned (photo stays on the left, like a Tunisian ID card) */
      .sc-f {
        right: 36px;
        text-align: right;
      }
      /* S11: the currency reads after the number, i.e. on its left */
      #s11-cur {
        order: -1;
        margin-left: 0;
        margin-right: 18px;
      }
      #tel,
      #url {
        direction: ltr;
      }
"""

# 9:16: the text column hugs the right margin (72 px)
CSS_PORTRAIT = """      /* 9:16: titles, captions and the price column hug the right margin */
      #s1-title,
      .title,
      #s6-t,
      #s7-t,
      #s3-sub,
      #tr-sub,
      #s11-k,
      #s11-pill {
        left: auto;
        right: 72px;
      }
      .title {
        font-size: 96px;
      }
      #s1-title .ln {
        height: 120px;
      }
      #s9-chip {
        left: auto;
        right: 390px;
      }
      #s11-des {
        left: auto;
        right: 76px;
      }
      #s11-num {
        left: auto;
        right: 64px;
      }
      #st-tc {
        left: 52px;
      }
"""

# 16:9: the text column stays on the left of the illustrations, aligned on its right edge
CSS_LANDSCAPE = """      /* 16:9: the text column stays left of the illustrations, aligned on its right edge (x = 840) */
      #s1-title,
      .title,
      #s6-t,
      #s7-t,
      #s3-sub {
        left: auto;
        right: 1080px;
      }
      .title {
        font-size: 104px;
      }
      #s1-title .ln {
        height: 136px;
      }
      #s9-chip {
        left: auto;
        right: 1420px;
      }
      #tr-t,
      #tr-sub {
        left: auto;
        right: 864px;
      }
      #s8-cap {
        left: auto;
        right: 880px;
        text-align: right;
      }
      #s11-k,
      #s11-pill {
        left: auto;
        right: 970px;
      }
      #s11-des {
        left: auto;
        right: 966px;
      }
      #s11-num {
        left: auto;
        right: 1054.3px;
      }
"""


def fail(*a):
    sys.exit("make_arabic: " + " ".join(str(x) for x in a))


for src_name, dst_name in PAIRS:
    src, dst = ROOT / src_name, ROOT / dst_name
    if not (src / "index.html").exists():
        fail(f"{src_name}/index.html missing (run scripts/make_landscape.py first)")
    s = (src / "index.html").read_text(encoding="utf-8")
    landscape = 'data-width="1920"' in s

    def sub(old, new, n=1):
        global s
        c = s.count(old)
        if c != n:
            fail(f"{src_name}: expected {n}x, found {c}x:", repr(old[:90]))
        s = s.replace(old, new)

    for old, new, n in TEXTS + ANIM:
        sub(old, new, n)
    # HUD: the five step segments fill from the right
    box_w, seg_w = (1728, 150) if landscape else (960, 171.2)
    segs = re.findall(r'<div class="seg" id="seg(\d)" style="left: ([\d.]+)px">', s)
    if len(segs) != 5:
        fail(f"{src_name}: 5 HUD segments expected, found {len(segs)}")
    for i, left in segs:
        mirrored = round(box_w - seg_w - float(left), 1)
        sub(f'<div class="seg" id="seg{i}" style="left: {left}px">', f'<div class="seg" id="seg{i}" style="left: {mirrored:g}px">')
    # fonts + CSS
    anchor = "      :root {\n"
    sub(anchor, FONT_FACE + anchor)
    sub("\n    </style>", CSS_COMMON + (CSS_LANDSCAPE if landscape else CSS_PORTRAIT) + "    </style>")
    # anything French left on screen? (accented letters outside comments/identifiers)
    body = s[s.index("<body>"):s.index("<script>", s.index("<body>"))]
    leftovers = sorted({w for w in re.findall(r">([^<>{}]*[éèêàùçôîÉÈÀ][^<>{}]*)<", body) if w.strip()})
    if leftovers:
        fail(f"{src_name}: French text left in the markup:", leftovers[:8])

    dst.mkdir(exist_ok=True)
    (dst / "index.html").write_text(s, encoding="utf-8")
    for sub_dir in ("fonts", "vendor", "img", "audio"):
        if (src / "assets" / sub_dir).exists():
            shutil.copytree(src / "assets" / sub_dir, dst / "assets" / sub_dir, dirs_exist_ok=True)
    for f in ("hyperframes.json", "package.json", "CLAUDE.md", "AGENTS.md"):
        shutil.copy2(src / f, dst / f)
    meta = json.loads((src / "meta.json").read_text())
    meta.update(id=dst_name, name=dst_name)
    (dst / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"{dst_name}/index.html written ({len(s.encode())} bytes, {'16:9' if landscape else '9:16'})")
