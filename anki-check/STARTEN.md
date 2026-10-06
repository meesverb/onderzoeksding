# Vandaag starten (di 6 oktober) — 23 dagen tot het tentamen

## Eenmalig instellen (±10 minuten)

1. **Add-ons installeren** (*Extra → Add-ons → Installeren uit bestand*): `gzc3_campagne.ankiaddon` (de nieuwe versie gaat over de oude heen) en `vraag_claude_waarom.ankiaddon`. Herstart Anki.
2. In het hoofdscherm staat onder je decks nu **Campagne GZC III**, met bovenaan een **installatiecheck**. Die ziet zelf wat je al gedaan hebt; klik bij elke open stap op de knop, van boven naar beneden:
   1. **Import 1**: de gecontroleerde kaarten (er wordt eerst automatisch een back-up gemaakt).
   2. **Import 2**: casussen, schema's, tabellen en ezelsbruggen.
   3. **Import 3**: de 181 kaarten uit de slides van HC 1-5.
   4. **Dubbele kaarten verwijderen**: de 93 notities met `check::dubbel` of `check::verwijderen`.
   5. **FSRS**: opent de deckopties. Zet FSRS aan, kies een retentie van 0,90 en klik op Opslaan.
   6. **Campagne starten**: zet de nieuwe kaarten op volgorde van de colleges, en kaarten van colleges die je nog niet hebt gedaan, op slot. Je eerdere opschorting per thema vervalt daarmee.

   Het blok verdwijnt zodra alles klaar is. Heb je iets al met de hand gedaan, dan staat het al op ✅.
3. Elke dag: **„Zet vandaag N nieuwe kaarten klaar”**.
4. Na elk college: klik op het college op de **wereldkaart** (of op 📖 Open). Daar vind je de kapstok en de controlequiz, en met **„✓ College gedaan”** speel je de kaarten vrij (🔓, +50 XP).

De add-on koppelt alle T1- en T2-kaarten zelf aan hun college (tag `college::HC3` enz.). Dat gebeurt bij het openen van je profiel, na elke import en na het synchroniseren. Zoek in de browser op `tag:college::HC3` om alle kaarten van één college te zien.

## Nieuw: de colleges HC 1-5 verwerkt

- **Kapstokken** van één pagina met 5 controlevragen: `kapstokken/HC1.md` t/m `HC5.md`, ook in het collegevenster in Anki en in de quiz (soort *Controlevraag*).
- **181 nieuwe kaarten** (`bron::slides-HC1-5`): 100 basiskaarten, 14 casussen uit de IC's, 34 tabelkaarten en 33 schemakaarten. De schema's zijn zelfgetekende versies van de belangrijkste figuren: hiërarchie van de hematopoëse, ijzerkringloop, reperfusieschade, bilirubineafbraak en aangrijpingspunten van de antistolling.
- **MCV-grenzen** aangepast aan het college: 82-98 fl (het deck zei 80-100).
- **Koppeling** van alle 412 T1/T2-kaarten aan HC 1-10, met de hand op basis van de slides. Ter controle: `koppeling.md`.

## Het plan

Twee sporen. **Hoofdspoor:** van het begin inhalen (T1 → T2), want T2 en de leukemie-casus van T3 bouwen op T1 voort. **Bijspoor:** de live colleges van de groep (nu T3), zodat je bij het werkcollege voorbereid bent.

| Dag | Hoofdspoor | Bijspoor (live) |
|---|---|---|
| di 6 okt | HC 1-2 Hemato-erytropoëse | HC 11 Kinderoncologie |
| wo 7 | HC 3 Anemie, HC 5 Intro hematologische maligniteiten (kapstok) | |
| do 8 | HC 4 Stolling | E-module AYA |
| vr 9 | HC 6 MPN en CML | HC 12 AYA |
| za 10 | HC 7 Lymfoom en CLL | |
| zo 11 | HC 8 Myeloom | HC 13 Geriatrie |
| ma 12 | HC 9 AML en MDS | HC AI |
| di 13 | HC 10 Pathologie maligne hematologie | |
| wo 14 – vr 16 | T4: HC 14 t/m 19, bijlage radiotherapie | |
| za 17 – zo 18 | B1 Public health (8 colleges) | |
| ma 19 | B2: HC 28, HC 29, 2 bijlagen | |
| di 20 | B3: HC 30, HC 31 | |
| wo 21 – do 22 | Inhalen | |
| vr 23 – wo 28 | Eindbaas: elke dag 1 oud tentamen + herhalen + quiz | |
| **do 29 okt** | **Tentamen** | |

Volgt de groep een andere volgorde? Stuur het rooster, dan schuif ik het bijspoor mee.

Elke dag: ±50 nieuwe kaarten (de campagne rekent het precies uit) plus je herhalingen. Reken op 1 à 1,5 uur Anki en 1,5 à 2 uur colleges per dag.
Volgt de groep een andere volgorde dan dit plan? Stuur het rooster, dan pas ik de data aan.

## Hoe de campagne werkt

- **Wereldkaart:** elk thema is een wereld met een eindbaas en een pad van colleges. Een college krijgt sterren:
  - ★ afgevinkt;
  - ★★ alle kaarten gezien;
  - ★★★ 70% van de kaarten verankerd (interval van 7 dagen of meer).

  🔒 betekent dat de kaarten nog op slot zitten.
- **Collegevenster:** klik op een college voor de kapstok, de valkuilen, de controlequiz (+10 XP per goed antwoord; je beste poging telt), je kaarten van dat college, en een herkansing met alleen de foute kaarten van dat college.
- **Slot per college:** T1 en T2 zijn precies gekoppeld op basis van de slides. De rest gaat nog op trefwoord, tot de slides er zijn. Loop je vast, dan zet je het slot uit onder „Uitleg en instellingen”.
- **Celalbum:** elk college heeft een verzamelcel, met een feitje (de Reed-Sternbergcel, de Auerstaaf, het Philadelphiachromosoom …). Je krijgt hem zodra je alle kaarten van dat college hebt gezien.
- **Tijdens het leren:** rechtsboven een klein paneel met de eindbaas van de kaart (HP), het college, je level en je combo. Na elk antwoord zweeft er „+2 XP” omhoog.
  - **Combo:** vanaf 10 goede antwoorden op rij +1 XP per kaart, vanaf 25 +2.
  - **💥 Kritieke treffer:** ongeveer 1 op de 20 goede antwoorden, +10 XP.
  - Als je stopt, krijg je een **sessierapport**.
  - Het paneel zet je uit met `"hud": false` in de config.
- **🔁 Herkansing:** één klik maakt een gefilterd deck *GZC III - Herkansing* met de kaarten die je de laatste 2 dagen fout had.
- **Herhalingen komende week:** een staafje per dag, zodat je een lawine van herhalingen ziet aankomen.
- **Dagquest:** Brons = alle herhalingen weg; Zilver = je nieuwe kaarten van vandaag; Goud = de colleges van vandaag én je achterstand afgevinkt. In de laatste week: Zilver = 150 herhalingen, Goud = het oude tentamen van die dag.
- **XP en levels:** 1 XP per fout antwoord, 2 per goed antwoord, +3 voor elke nieuwe kaart, +50 per college, +75 per e-module, bijlage of oud tentamen, plus combo's, kritieke treffers en controlequizzen. Vijftien levels, van Nieuweling tot Tentamenbeest.
- **Reeks:** elke dag met minstens 30 herhalingen houdt je reeks in leven.
- **Eindbazen:** zijn HP daalt als je kaarten ziet en verankert. Verslagen bij 95% gezien en 70% verankerd.
- **17 badges**, onder andere Combokoning (combo van 50), Kritiek! (10 kritieke treffers), Poortwachter (5 controlequizzen foutloos), Verzamelaar (10 cellen), Meester (een college met ★★★) en Drakendoder.
- **Prognose:** op schema of achter op schema, op basis van je tempo van de laatste drie dagen.

Leer je op je telefoon? Dat telt gewoon mee: na het synchroniseren ziet de campagne op je computer alles.
