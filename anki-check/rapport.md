# Anki-check GZC III — kaarten naast het blokboek

**Bronnen:** alle 652 kaarten uit `GZC III - Compleet.apkg`, het volledige blokboek 2026-2027 (59 pagina's: alle doelstellingen, casussen en leeropdrachten) en 6 oude tentamens en oefententamens.

## Oordeel in het kort

Inhoudelijk is het deck sterk: vrijwel elke doelstelling en leeropdracht uit het blokboek heeft een kaart, en ik vond maar een paar echte fouten. Er waren drie problemen die het leren inefficiënt maakten:

1. **Veel dubbele kaarten.** Het deck bestaat uit drie lagen die elkaar overlappen: doelstellingen, zelfstudie-/casusvragen en een ziektebeeldenset (per ziekte presentatie, oorzaak, diagnostiek, behandeling en prognose). **88 kaarten** vroegen hetzelfde als een andere kaart.
2. **Lange antwoorden.** De mediane antwoordlengte is ~290 tekens en 108 kaarten hadden meer dan 400 tekens. Zulke kaarten kun je bij het toetsen niet eerlijk goed of fout rekenen.
3. **Een paar gaten en tegenstrijdigheden** ten opzichte van het blokboek en de oude tentamens (bijvoorbeeld TTP, oorzaken van hypercalciëmie, de DD van pancytopenie, en MGUS-controle waarin twee kaarten elkaar tegenspraken).

Je had pas 16 van de 652 kaarten ooit geleerd, dus omgooien kost je nu vrijwel niets aan voortgang.

## Resultaat

| | Aantal |
|---|---|
| Behouden (ongewijzigd, of alleen het voorvoegsel "Zelfstudie X:" verwijderd) | 526 |
| Aangepast (fout hersteld, tegenstrijdigheid opgelost of aangevuld) | 23 |
| Gesplitst (10 overvolle kaarten → 21 kaarten) | 10 + 11 nieuw |
| Nieuw (gaten t.o.v. blokboek en tentamens) | 22 |
| **Dubbel** → mag weg | 88 |
| **Verwijderen?** (geen leerdoel in GZC III) | 5 |
| **Deck na opruimen** | **592 kaarten** (was 652) |

Er zijn ook drie hulptags:

- `prio::tentamen`: 141 kaarten over onderwerpen die in de oude tentamens terugkomen.
- `check::lang`: 74 kaarten die nog steeds lang zijn. Splits die als je ze tegenkomt, of beoordeel ze op de kern.
- `check::inhoud-controleren`: 4 kaarten waarbij je de slides moet naslaan (zie onder).

### Verdeling per thema (vóór → na opruimen, inclusief nieuwe kaarten)

| Thema | Vóór | Na |
|---|---|---|
| T1 Benigne hematologie | 120 | 119 |
| T2 Maligne hematologie | 109 | 111 |
| T3 Groepsspecifieke oncologie (kind, AYA, geriatrie) | 46 | 42 |
| T4 Orgaanspecifieke oncologie (hoofd-hals, schildklier, oog) | 105 | 102 |
| B1 Public health | 62 | 63 |
| B2 Revalidatie / psychosociaal | 32 | 30 |
| B3 Pijn en palliatieve zorg | 61 | 67 |
| Ziektebeeldenset (zonder thematag) | 117 | 58 |

## Importeren (±5 minuten)

1. **Maak eerst een back-up:** *Bestand → Back-up maken*.
2. Download `GZC3_check_import.txt` en kies in Anki *Bestand → Importeren*.
3. Het bestand zet notitietype, deck, GUID en tags zelf goed. Controleer alleen dat bij **Bestaande notities** de optie **Bijwerken** staat (Engels: *Existing notes: Update*). Klik op *Importeren*.
4. Verwachte uitkomst: **652 bijgewerkt, 33 nieuw**. Je leergeschiedenis blijft behouden, omdat de kaarten via hun GUID worden bijgewerkt en niet opnieuw worden aangemaakt.
   *Getest op een kopie van jouw collectie: 652 bijgewerkt, 33 nieuw, 0 conflicten, planning ongewijzigd.*

## Opruimen na de import

In de Anki-browser (*Bladeren*):

| Zoekopdracht | Wat je doet |
|---|---|
| `tag:check::dubbel` | Alles selecteren → verwijderen (of opschorten als je het eerst wilt zien). De unieke informatie staat al in de kaart die blijft. |
| `tag:check::verwijderen` | 5 kaarten nalopen en weghalen als je het met me eens bent. |
| `tag:check::inhoud-controleren` | De 4 kaarten hieronder naast de slides leggen. |
| `tag:check::nieuw or tag:check::gesplitst` | Even doorlezen, zodat je weet wat erbij is gekomen. |
| `tag:prio::tentamen` | Handig als gefilterd deck vlak voor het tentamen. |

Daarna kun je alle `check::`-tags weghalen met *Notities → Tags opruimen*, of ze laten staan.

## Wat is er inhoudelijk veranderd

**Tegenstrijdigheden opgelost**

- **MGUS:** de ene kaart zei "levenslange controle", maar het college (en de uitleg bij het oefententamen) zegt dat de kans op progressie van ~1%/jaar zo klein is dat laagrisico-MGUS niet standaard onder controle hoeft. De kaart volgt nu het college. *Controleer dit in de slides.*
- **CML:** "circa 20% gaat over in acute leukemie" aangepast. Blastencrise treedt op bij onbehandelde of resistente ziekte en is onder TKI zeldzaam geworden. Het mechanisme van imatinib (ATP-bindingsplaats van BCR-ABL) staat er nu ook in; dat werd op het tentamen gevraagd.
- **Prognose Hodgkin, ALL bij volwassenen, schildkliernodi en vermijdbare kanker:** getallen tussen kaarten gelijkgetrokken.

**Aangevuld**

- **Hematologie:** transferrine is een *negatief* acutefase-eiwit (anemie bij chronische ziekte). Hemofilie B heet ook Christmas disease. Mycosis fungoides is CD4+ en indolent. MALT met t(11;18) reageert niet op eradicatie. Rituximab werkt bij NLPHL (CD20+) en niet bij klassiek Hodgkin.
- **Hoofd-hals en psychosociaal:** dubbelzien bij nasofarynxcarcinoom betekent doorgroei in de schedelbasis. Leukoplakie is een klinische diagnose, geen PA-diagnose. Maligne ascites komt meestal door peritonitis carcinomatosa. Kanker als trauma: de dreiging komt van binnenuit, de onzekerheid duurt lang en er zijn veel verliezen.

**Typfouten:** kliierpijn, boeienfibrilleren, woordvaerder.

**Gesplitst** (lijstkaarten opgeknipt in toetsbare delen): IPI/FLIPI, botmetastasen, obstipatie, pleuravocht/ascites (3 kaarten), depressie, delier, antistolling (aangrijpingspunten en antidota), bèta-thalassemie minor/major, sikkelcelziekte, dreigende dwarslaesie.

**Nieuw: gaten ten opzichte van blokboek en tentamens**

| Waarom | Kaart |
|---|---|
| Blokboek casus 1.1 | Interpretatie van het lab van de 65-jarige man |
| Oud tentamen | TTP (ADAMTS13) · Glanzmann vs. Bernard-Soulier · Factor XIII-deficiëntie · Sideroblastaire anemie |
| Blokboek werkgroep 1 | DD van pijnloze lymfeklieren · Wanneer een klierbiopsie · Ongunstige factoren bij Hodgkin in vroeg stadium |
| Blokboek casus 2.2 | FLIPI-score van de casus (= 2, intermediair) |
| Oud tentamen | Infecties geassocieerd met lymfomen (EBV, HTLV-1, H. pylori, HHV-8, HCV) |
| Blokboek casus 3.1 (leerdoel) | Oorzaken van hypercalciëmie · Mechanismen bij maligniteit · Oorzaken van verhoogd totaal eiwit |
| Blokboek casus 3.2 (leerdoel) | DD van pancytopenie · Risicofactoren AML (o.a. benzeen) |
| Oud tentamen / practicum | Histologie van het plaveiselcelcarcinoom · Versneld bestralingsschema · Fluorideprofylaxe · Doorroken tijdens radiotherapie |
| Blokboek B1 | Echelons in de NL-zorg · Sterftecijfer vs. letaliteit |
| Oud tentamen | Neurotransmitters bij misselijkheid |

## Nog open

**4 kaarten met `check::inhoud-controleren`**

- *MCV-classificatie:* het plaatje wordt van internet geladen en heeft als alt-tekst "VACTERL-associatie". Kijk of het klopt. Let op: plaatjes van internet werken niet offline, en dat geldt ook voor de MCHC- en hemostasekaart.
- *MGUS:* controle wel of niet (zie boven).
- *AYA:* het blokboek noemt 18-25 jaar, het landelijke AYA-netwerk 18-39 jaar. Kies wat de docent gebruikt.
- *Hemofilie:* "behandelen bij minder dan 30%" is onduidelijk. Waar slaat dit op?

**Niet te controleren zonder de slides:**

- practica (microscopie, preparaten)
- het hoorcollege AI
- de e-module AYA (volgens het blokboek wordt daaruit getoetst)
- de verplichte bijlagen: *Radiotherapie hoofd/hals*, *Kanker: een existentiële opgave*, *Signaleren van distress*

Dat is de volgende stap met de colleges.

**5 voorstellen om te verwijderen:**

- de practicumvoorbereiding
- granulocytfuncties
- aangeboren vs. adaptief immuunsysteem
- MHC-klassen
- HbA1c

Die stof komt uit eerdere blokken of valt buiten de leerdoelen.

## Bijlage: welke dubbele kaart valt weg, en welke blijft

| Dubbele kaart (weg) | Blijft staan |
|---|---|
| Normocytaire anemie — hoe stuur je de diagnostiek? | Wat zegt het reticulocytengetal bij anemie? |
| Wat zijn mogelijke oorzaken van trombocytopenie? | Wat zijn oorzaken van trombocytopenie, geordend naar mechanisme? |
| Wanneer ontstaat leukocytose? | Wat zijn oorzaken van leukocytose? |
| Wat kunnen oorzaken zijn van toegenomen erytropoëse (te hoog Hb)? | Wat zijn de belangrijkste oorzaken van polycythemie? |
| Wat zijn oorzaken van leukocytopenie/neutropenie? | Wat zijn oorzaken van leukocytopenie? |
| Microcytaire anemie — oorzaken? | Welk mechanisme ligt ten grondslag aan een microcytaire hypochrome anemie? |
| Microcytaire anemie — hoe onderscheid je de hoofdoorzaken? | Hoe onderscheid je ijzergebreksanemie, anemie bij chronische ziekte en heterozygote bèta-thalassemie? |
| Klassiek Hodgkinlymfoom — presentatie? | Wat zijn de belangrijkste klinische kenmerken bij presentatie van een Hodgkinlymfoom? |
| Klassiek Hodgkinlymfoom — aanvullend onderzoek? | Hoe verloopt de diagnostiek van het Hodgkinlymfoom? |
| Klassiek Hodgkinlymfoom — oorzaak en pathogenese? | Wat is de mogelijke rol van EBV in de pathogenese van het Hodgkinlymfoom? |
| Klassiek Hodgkinlymfoom — behandeling? | Hoe wordt een gelokaliseerd Hodgkinlymfoom behandeld? |
| Klassiek Hodgkinlymfoom — incidentie en prognose? | Hoe is de prognose van het Hodgkinlymfoom en waardoor wordt deze beïnvloed? |
| CLL — presentatie? | Wat is de herkomst en het klinisch beeld van chronische lymfatische leukemie? |
| CLL — oorzaak en pathogenese? | Wat is de herkomst en het klinisch beeld van chronische lymfatische leukemie? |
| CLL — aanvullend onderzoek? | Hoe wordt de diagnose CLL gesteld? |
| CLL — behandeling? | Wat zijn indicaties om te starten met behandeling van CLL? |
| MALT-lymfoom — kenmerken en behandeling? | Waarom wordt het MALT-lymfoom als aparte entiteit gezien? |
| AL-amyloïdose — oorzaak, presentatie en behandeling? | Wat is amyloïdose? |
| MGUS — kenmerken en beleid? | Geef een beschrijving van MGUS |
| Multipel myeloom — behandeling? | Bespreek de verschillende stappen van de behandeling van multipel myeloom |
| Wat is het International Staging System (ISS) bij multipel myeloom? | Welke prognostische factoren kent u voor multipel myeloom? |
| Morbus Waldenström — oorzaak en diagnostiek? | Wat is de definitie van de ziekte van Waldenström? |
| Morbus Waldenström — presentatie? | Wat zijn de 3 belangrijkste klinische verschijnselen van M. Waldenström? |
| AML — presentatie? | Beschrijf het klinisch beeld van AML en waardoor het wordt bepaald |
| AML — aanvullend onderzoek? | Hoe wordt de diagnose AML gesteld? |
| AML — behandeling? | Bespreek de principes van de behandeling van acute leukemie |
| MDS — presentatie? | Beschrijf het klinisch beeld en de prognose van het myelodysplastisch syndroom |
| ALL — aanvullend onderzoek? | Beschrijf het diagnostisch proces bij verdenking op leukemie bij kinderen |
| ALL — oorzaak en pathogenese? | Geef prognostisch gunstige en ongunstige cytogenetische afwijkingen bij ALL en AML bij kinderen |
| ALL — incidentie en prognose? | Wat is de prognose van ALL bij kinderen, en hoe verschilt die van ALL op volwassen leeftijd? |
| Neuroblastoom — presentatie? | Met welke klachten kan een neuroblastoom zich presenteren? |
| Neuroblastoom — aanvullend onderzoek? | Hoe verloopt de diagnostiek van het neuroblastoom? |
| Neuroblastoom — behandeling? | Hoe wordt een neuroblastoom behandeld? |
| Neuroblastoom — prognose en prognostische factoren? | Wat is de prognose van een neuroblastoom en welke prognostische factoren zijn er? |
| Hoofd-halskanker algemeen — oorzaak? | Wat zijn de risicofactoren voor het ontstaan van hoofd-halstumoren? |
| Hoofd-halskanker algemeen — presentatie? | Welke symptomen kunnen duiden op een hoofd-halstumor? |
| Hoofd-halskanker algemeen — aanvullend onderzoek? | Welke diagnostiek is nodig bij het vinden van een lymfeklier in de hals? |
| Nasofarynxcarcinoom — presentatie, oorzaak en behandeling? | Wat zijn de etiologie, behandeling en prognose van het nasofarynxcarcinoom? |
| Niet-toxisch struma — oorzaak en behandeling? | Beschrijf de etiologie van het niet-toxisch struma |
| Toxisch folliculair adenoom — oorzaak en behandeling? | Hoe ontstaat een toxisch folliculair adenoom? |
| Papillair en folliculair schildkliercarcinoom — behandeling? | Wat is de operatieve therapie voor papillair en folliculair schildkliercarcinoom? |
| Medullair schildkliercarcinoom — kenmerken en behandeling? | Hoe wordt medullair schildkliercarcinoom gediagnosticeerd en behandeld? |
| Uveamelanoom — presentatie en diagnostiek? | Noem de initiële symptomen van een choroïdeamelanoom en hoe de diagnose wordt gesteld |
| Pleiomorf adenoom — kenmerken en behandeling? | Wat is de meest voorkomende speekselkliertumor en waar zit die meestal? |
| Maligne speekselkliertumoren — presentatie en diagnostiek? | Stel een DD op van een zwelling in de parotis en bespreek de klinische verschijnselen |
| Maligne speekselkliertumoren — behandeling en prognose? | Bespreek de chirurgische therapie bij speekselkliertumoren en de indicaties voor postoperatieve radiotherapie |
| Welke medicamenten kunnen een bloedingsneiging verklaren, en via welk mechanisme? | Geef een overzicht van de antistollingsmedicatie en hun aangrijpingspunt |
| Microcytaire anemie — behandeling? | Geef een overzicht van de behandeling per hoofdoorzaak van anemie |
| Orofarynxcarcinoom — prognose? | Wat is bijzonder aan het HPV-positieve orofarynxcarcinoom? |
| Ooglidtumoren — kenmerken en behandeling? | Wat kenmerkt de tumoren van de oogleden en hoe worden ze behandeld? |
| Wat zijn de 'Big Five' van kanker in Nederland? | Hoe ziet de epidemiologie van kanker in Nederland eruit? |
| MDS — aanvullend onderzoek? | Wat zijn de morfologische kenmerken van dysplasie bij MDS? |
| MDS — incidentie en prognose? | Waardoor wordt de prognose van MDS bepaald? |
| Hairy cell leukemie — kenmerken en behandeling? | Wat kenmerkt hairy cell leukemie? |
| Mantelcellymfoom — kenmerken? | Wat kenmerkt het mantelcellymfoom? |
| Burkitt-lymfoom — presentatie en oorzaak? | Welke drie vormen van het Burkitt-lymfoom zijn er? |
| Burkitt-lymfoom — behandeling en prognose? | Welke drie vormen van het Burkitt-lymfoom zijn er? |
| Hoofd-halskanker algemeen — incidentie en prognose? | Wat is de incidentie en algemene prognose van hoofd-halskanker in Nederland? |
| Paraganglioom hoofd-hals — kenmerken? | Wat is een paraganglioom in het hoofd-halsgebied? |
| Sinonasale tumoren — presentatie, behandeling en prognose? | Wat kenmerkt sinonasale tumoren? |
| Warthin-tumor — kenmerken? | Wat kenmerkt de Warthin-tumor? |
| Schildkliernodus — incidentie en kans op maligniteit? | Hoe vaak komt een schildkliernodus voor en hoe groot is de kans op maligniteit? |
| Orbitaal rhabdomyosarcoom — kenmerken en behandeling? | Hoe presenteert het orbitale rhabdomyosarcoom zich, en wat is de DD? |
| Orbitaal non-Hodgkinlymfoom — kenmerken en behandeling? | Wat is de salmon patch? |
| Maligne traankliertumoren — kenmerken en behandeling? | Welke traankliertumoren zijn er en wat is het beleid? |
| Metastasen in de orbita — kenmerken en behandeling? | Hoe presenteren metastasen in de orbita zich? |
| Wat kenmerkt een existentiële crisis bij de diagnose kanker? | Wat zijn de zeven kenmerken van een existentiële crisis? |
| Welke copingstijlen kun je onderscheiden? | Welke vijf copingstijlen worden onderscheiden? |
| Wat zijn de farmacologische stappen om nociceptieve pijn te behandelen? | Hoe ziet de WHO-pijnladder er volledig uit? |
| Hoe worden epidurale/intrathecale pijnbestrijding, zadelblok, plexus coeliacusblokkade en chordotomie toegepast? | Hoe kies je tussen de verschillende invasieve pijntechnieken? |
| Welke immunotherapie wordt gebruikt bij hoogrisico-ALL? | ALL — behandeling? |
| Beschrijf symptomen, prognose en behandeling van chronische myeloïde leukemie | CML — presentatie? |
| Beschrijf symptomen, prognose en behandeling van polycythaemia vera | Polycythaemia vera — presentatie? |
| Beschrijf symptomen, prognose en behandeling van essentiële trombocytose | Essentiële trombocytose — presentatie en diagnostiek? |
| Beschrijf symptomen, prognose en behandeling van myelofibrose | Myelofibrose — presentatie? |
| Bespreek herkomst, groeigedrag, immunofenotypering, behandeling en prognose van het folliculair lymfoom | Folliculair lymfoom — presentatie en oorzaak? |
| Bespreek herkomst, groeigedrag, immunofenotypering, behandeling en prognose van het diffuus grootcellig B-cellymfoom | Diffuus grootcellig B-cellymfoom — presentatie? |
| Wat kenmerkt het anaplastisch schildkliercarcinoom? | Anaplastisch schildkliercarcinoom — presentatie, behandeling en prognose? |
| Bespreek klachten, prognose en therapeutische opties van het anaplastisch schildkliercarcinoom | Anaplastisch schildkliercarcinoom — presentatie, behandeling en prognose? |
| Wat zijn de klinische verschijnselen en behandeling van het retinoblastoom? | Retinoblastoom — presentatie? |
| Welke bevinding is vrijwel pathognomonisch voor het retinoblastoom? | Retinoblastoom — oorzaak en diagnostiek? |
| Wat zijn de karakteristieke bijzonderheden van het retinoblastoom als intraoculaire tumor? | Retinoblastoom — incidentie en prognose? |
| Welke behandelingsvormen bestaan er voor het choroïdeamelanoom? | Uveamelanoom — behandeling? |
| Wat zijn de complicaties van plaque-brachytherapie bij een oogmelanoom? | Uveamelanoom — behandeling? |
| In welke leeftijdsgroep wordt het choroïdeamelanoom vooral aangetroffen? | Uveamelanoom — incidentie en prognose? |
| Welk onderzoek is nodig voor diagnose en stadiëring van het nefroblastoom? | Nefroblastoom (Wilms-tumor) — presentatie en diagnostiek? |
| Wat zijn behandeling, prognose en prognostische factoren van het nefroblastoom? | Nefroblastoom (Wilms-tumor) — behandeling en prognose? |
| Bespreek de presentatie en behandeling van osteosarcoom, Ewing-sarcoom en rhabdomyosarcoom | Osteosarcoom — presentatie en behandeling? |

---
Gegenereerd met `anki-check/bouw_import.py` (alle beslissingen per kaart staan daar in).
