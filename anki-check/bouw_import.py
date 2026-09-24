"""Bouwt het Anki-importbestand voor de GZC III-check.

Invoer : werk/col.db (uitgepakte collectie uit 'GZC III - Compleet.apkg')
Uitvoer: anki-check/GZC3_check_import.txt en anki-check/statistiek.txt

Kaartnummers (#n) verwijzen naar de volgorde van aanmaken (note-id), gelijk aan werk/deck.txt.
Bestaande notities houden hun GUID, zodat Anki ze bijwerkt en de leergeschiedenis behoudt.
"""
import csv, hashlib, re, sqlite3, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / 'werk' / 'col.db'
OUT = ROOT / 'anki-check'
DECK = 'GZC III - Compleet'
NOTETYPE = '1706371006450'  # id van het notitietype 'Basic' in jouw collectie (naam is niet uniek)

# ---------------------------------------------------------------- dubbelingen
# dubbele kaart -> kaart die blijft (unieke info is waar nodig in de blijver verwerkt)
DUBBEL = {
    9: 25, 26: 6, 27: 8, 36: 16, 56: 312, 536: 41, 537: 44, 538: 321, 540: 4,
    577: 67, 578: 70, 579: 68, 580: 79, 581: 83, 91: 583, 92: 587, 553: 95, 554: 95,
    555: 96, 556: 99, 593: 103, 605: 109, 604: 110, 602: 116, 438: 118, 596: 120,
    597: 119, 548: 122, 550: 124, 551: 125, 563: 129, 565: 424, 567: 425, 131: 568,
    134: 572, 135: 574, 136: 558, 595: 428, 594: 429, 591: 430, 592: 430, 437: 546,
    544: 152, 545: 149, 547: 155, 644: 159, 645: 160, 646: 161, 647: 164, 165: 648,
    166: 649, 167: 650, 168: 632, 352: 635, 474: 633, 607: 170, 609: 461, 606: 171,
    608: 187, 626: 208, 180: 629, 213: 629, 611: 201, 628: 212, 625: 468, 630: 205,
    631: 206, 636: 216, 217: 637, 477: 637, 215: 638, 619: 219, 621: 222, 622: 227,
    613: 345, 643: 354, 623: 464, 618: 465, 620: 466, 639: 478, 640: 479, 641: 480,
    642: 481, 491: 355, 261: 509, 364: 506, 274: 520, 278: 528,
}

# ---------------------------------------------------------------- verwijderen?
VERWIJDEREN = {
    139: 'geen leerstof: gaat over de voorbereiding van het practicum',
    383: 'basiskennis uit GZC I, geen leerdoel in GZC III',
    384: 'basiskennis immunologie, geen leerdoel in GZC III',
    385: 'basiskennis immunologie (MHC), geen leerdoel in GZC III',
    390: 'HbA1c/diabetes valt buiten de leerdoelen van GZC III',
}

# ---------------------------------------------------------------- inhoud nakijken
INHOUD = {
    2: 'afbeelding is van internet gelinkt (alt-tekst "VACTERL-associatie") — klopt het plaatje?',
    110: 'college zegt: MGUS hoeft door lage progressiekans niet standaard onder controle; oude kaart zei "levenslange controle"',
    144: 'leeftijdsgrens AYA: blokboek noemt 18-25 jaar, landelijk AYA-netwerk hanteert 18-39 jaar',
    417: '"behandelen bij minder dan 30%" is onduidelijk — check in de slides waar dit op slaat',
}

# ---------------------------------------------------------------- aanpassingen
# n -> (nieuwe voorkant of None, nieuwe achterkant of None)
EDIT = {
    67: (None, 'Pijnloze, vaste lymfadenopathie (cervicaal, supraclaviculair, mediastinaal), B-symptomen (koorts, nachtzweten, &gt;10% gewichtsverlies), jeuk, alcoholgeïnduceerde klierpijn, splenomegalie, verhoogde BSE'),
    83: (None, 'Zeer goed: stadium I-II circa 95%, stadium III-IV circa 70-80% vijfjaarsoverleving.<br>Beïnvloed door stadium, B-symptomen, bulk (mediastinum/thorax-ratio &gt;1/3), leeftijd en bij gevorderd stadium de IPS-score.<br>Sterkste voorspeller: de interim-PET na 2 kuren.'),
    103: (None, 'Het ontstaat in mucosa-geassocieerd lymfoïd weefsel door chronische antigene stimulatie. Verwijderen van die prikkel kan curatief zijn: H. pylori-eradicatie geneest een groot deel van de maaglokalisaties zonder chemotherapie.<br>Let op: bij t(11;18) reageert het maag-MALT niet op eradicatie en is chemo- of radiotherapie nodig.'),
    110: (None, 'Monoclonal gammopathy of undetermined significance:<br>- M-proteïne &lt;30 g/l<br>- &lt;10% klonale plasmacellen in het beenmerg<br>- géén CRAB-orgaanschade<br>Progressie naar myeloom circa 1% per jaar. Volgens het college is dat zo laag dat (laagrisico-)MGUS niet standaard onder controle hoeft.<br>Elk myeloom wordt voorafgegaan door MGUS, maar niet elke MGUS wordt een myeloom.'),
    155: (None, 'Kinderen: circa 90% vijfjaarsoverleving.<br>Volwassenen: circa 40-55%, door ongunstiger genetica (vaker BCR-ABL/Ph+ en KMT2A), slechtere tolerantie van intensieve protocollen en meer comorbiditeit.'),
    201: (None, 'Etiologie: EBV-geassocieerd, endemisch in Zuid-China en Noord-Afrika, met genetische aanleg en gezouten vis als cofactor.<br>Presentatie: halsklier (vaak eerste symptoom), unilaterale otitis media met effusie, neusobstructie of epistaxis, hersenzenuwuitval bij doorgroei in de schedelbasis (dubbelzien door n. abducens).<br>Behandeling: (chemo)radiotherapie — géén primaire chirurgie: slecht bereikbaar en zeer stralingsgevoelig. EBV-DNA in plasma is tumormarker.'),
    203: (None, 'Nodi zijn zeer frequent: palpabel bij circa 6% van de vrouwen en 1,5% van de mannen, echografisch bij tot de helft van de 50-plussers. Slechts circa 4-5% is maligne.<br>DD: colloïdnodus/multinodulair struma, folliculair adenoom, cyste, thyreoïditis, carcinoom (papillair, folliculair, medullair, anaplastisch), lymfoom, metastase.'),
    260: (None, 'Het is een plotselinge, oncontroleerbare confrontatie met levensbedreiging die de basale aannames over veiligheid, controle en toekomst doorbreekt. Er is verlies van perspectief, van rollen en van lichamelijke integriteit.<br>Specifiek voor kanker: de dreiging komt van binnenuit, de periode van onzekerheid is langdurig, en er zijn veel verliezen.'),
    310: (None, 'De drie factoren die trombose bevorderen: stase (immobilisatie, boezemfibrilleren), endotheelschade (trauma, chirurgie, katheter) en hypercoagulabiliteit (maligniteit, zwangerschap, oestrogenen, trombofilie). Kanker raakt alle drie de assen, vandaar het sterk verhoogde tromboserisico.'),
    319: (None, 'Inflammatoire cytokinen (vooral IL-6) verhogen hepcidine. Hepcidine blokkeert ferroportine: ijzer raakt opgesloten in macrofagen en de darmopname daalt — genoeg ijzer, maar niet beschikbaar. Daarnaast verminderde EPO-respons en kortere erytrocytenlevensduur.<br>Lab: ferritine normaal tot hoog, transferrine/TIBC laag, saturatie laag.<br>Let op: transferrine is een <b>negatief</b> acutefase-eiwit (daalt bij ontsteking), ferritine een positief.'),
    346: (None, 'Leukoplakie: witte, niet-afschraapbare slijmvliesplek die niet aan een andere aandoening is toe te schrijven. Een klinische (beschrijvende) diagnose, géén PA-diagnose. Premaligne, maar met een lage kans op dysplasie/ontaarding (enkele procenten).<br>Erytroplakie: rode fluweelachtige plek, zeldzamer maar veel gevaarlijker: hoog percentage dysplasie of carcinoom.<br>Beleid: biopteren en vervolgen, risicofactoren staken.'),
    355: (None, 'Jaarlijks ruim 120.000 nieuwe diagnoses; ongeveer 1 op de 2 Nederlanders krijgt ooit kanker, en kanker is doodsoorzaak nummer één.<br>Big five: huidkanker, borstkanker, darmkanker, longkanker en prostaatkanker.<br>De incidentie stijgt vooral door vergrijzing, terwijl de sterfte per patiënt daalt. Circa 70% van de patiënten heeft comorbiditeit.<br>Cijfers: Nederlandse Kankerregistratie (IKNL) en VZinfo/RIVM.'),
    359: (None, 'Tabaksontmoediging, alcoholbeperking, gezond gewicht en bewegen, uv-bescherming, beperking van beroepsblootstelling (asbest, houtstof, benzeen) en vaccinatie (HPV, hepatitis B).<br>Volgens het college is circa een kwart van de kankergevallen vermijdbaar met een gezonde leefstijl (roken verreweg het belangrijkst); ruimere schattingen komen uit op een derde.'),
    417: (None, '85% hemofilie A (factor VIII), 15% hemofilie B (factor IX; ook wel Christmas disease). X-gebonden recessief.<br>Bij circa 1 op de 3 patiënten gaat het om een spontane mutatie, dus een negatieve familieanamnese sluit niets uit.<br>Ongeveer de helft van de draagsters heeft zelf een verlaagd factorgehalte; behandelen bij minder dan 30%.'),
    433: (None, 'Dezelfde tumorcel (CD4-positieve T-cel), twee klinische beelden.<br>Mycosis fungoides: indolent, langzaam progressief; eczemateus beeld → plaques → tumoren, vaak in het zwembroekgebied; lijkt eerst op eczeem omdat het ook op steroïden reageert.<br>Sézary-syndroom: erythrodermie met circulerende tumorcellen in het bloed.<br>Histologie: epidermotropisme (lymfocyten in de epidermis), aan te tonen met CD3.'),
    451: (None, 'De combinatie werkt synergistisch: circa 14× verhoogd risico, meer dan de som van beide. Een tweede primaire tumor is bij deze patiënten doodsoorzaak nummer 2.'),
    465: (None, 'Tumoren van neusholte en neusbijholten (exclusief nasofarynx). Presentatie lijkt op sinusitis: eenzijdige aangezichtspijn, neusobstructie, pusafvloed al dan niet met bloed; soms pas ontdekt bij een dikke wang of hoogstand van het oog.<br>Vaak adenocarcinomen (minder stralingsgevoelig). Sterk werkgerelateerd: houtstof, lederstof, meel, nikkel, chroom.<br>Behandeling: chirurgie (endoscopisch of open), meestal gevolgd door radiotherapie. Metastasering zeldzaam; vijfjaarsoverleving circa 50%.'),
    498: (None, 'Vraag eerst wat de patiënt al weet en wíl weten, bouw op via het onderzoek voordat je de diagnose noemt, en wees duidelijk maar niet bruut direct. Erken de rol van de familie en bepaal wie de woordvoerder is, bied een professionele tolk aan en check actief of het begrepen is. De diagnose moet uiteindelijk wel expliciet worden benoemd.'),
    561: (None, 'Tyrosinekinaseremmers: imatinib (1e generatie; blokkeert de ATP-bindingsplaats van het BCR-ABL-kinase), daarnaast nilotinib en dasatinib, die ook bij resistentiemutaties werken.<br>In principe levenslang; bij zeer diepe remissie lukt staken soms. Allogene SCT alleen bij blastencrise of TKI-resistentie.'),
    562: (None, 'Circa 1-2 per 100.000, mediane leeftijd rond 50 jaar, vaker mannen.<br>Met TKI\'s is de levensverwachting vrijwel normaal, maar zonder curatie: de zieke stamcel blijft op laag niveau aanwezig.<br>Onbehandeld (of bij resistentie) overgang via acceleratiefase naar blastencrise (acute leukemie); onder TKI is dat zeldzaam geworden.'),
    582: ('Hoe wordt het nodulair lymfocyten-predominant Hodgkinlymfoom (NLPHL) behandeld, en waarom werkt rituximab daar wél?',
          'Vrijwel altijd stadium I-II: radiotherapie of excisie, plus rituximab.<br>Rituximab werkt omdat de popcorncellen CD20-positief zijn — klassiek Hodgkin is CD20-negatief (CD15+/CD30+).<br>ABVD of CHOP alleen bij uitgebreide ziekte of recidief.'),
    599: ('Multipel myeloom — met welke klachten presenteert het zich?',
          'Botpijn (vooral rug) en pathologische fracturen zijn de belangrijkste klacht.<br>Verder moeheid (anemie), dorst/polyurie/verwardheid (hypercalciëmie), nierfunctieverlies, infecties door immunoparese, en soms hyperviscositeit of amyloïdose.'),
    635: (None, 'Circa 1 op de 16.000 geboorten, ongeveer 11 nieuwe gevallen per jaar in Nederland; 85% onder de 3 jaar.<br>Vijfjaarsoverleving boven de 90%, maar met metastasen slechts circa 20%. Metastasering via de n. opticus naar het CZS en hematogeen (anders dan het uveamelanoom, dat naar de lever gaat).<br>Doodsoorzaken: metastasen, pineoblastoom (trilateraal retinoblastoom) en secundaire tumoren.'),
}

# ---------------------------------------------------------------- splitsingen
# n -> [(voor, achter), ...]; het eerste deel vervangt de bestaande kaart, de rest wordt nieuw
SPLIT = {
    93: [('Welke vijf factoren vormen de IPI (agressief non-Hodgkinlymfoom)?',
          '- Leeftijd &gt;60 jaar<br>- LDH verhoogd<br>- ECOG-performance status ≥2<br>- Ann Arbor-stadium III/IV<br>- &gt;1 extranodale lokalisatie'),
         ('Welke vijf factoren vormen de FLIPI (folliculair lymfoom)?',
          '- Leeftijd &gt;60 jaar<br>- Stadium III/IV<br>- Hb &lt;7,5 mmol/l (12 g/dl)<br>- &gt;4 aangedane klierstations<br>- LDH verhoogd<br><i>Ezelsbrug: NoLASH (Nodes, LDH, Age, Stage, Hb)</i>')],
    281: [('Wat kunnen de gevolgen van botmetastasen zijn?',
           'Pijn, pathologische fractuur, hypercalciëmie, myelumcompressie/dwarslaesie en beenmergverdringing.'),
          ('Hoe behandel je botmetastasen?',
           '- Analgesie<br>- Palliatieve radiotherapie (vaak eenmalig 8 Gy, effectief bij 60-80%)<br>- Bisfosfonaten of denosumab<br>- Chirurgische (profylactische) stabilisatie<br>- Systemische antitumortherapie<br>Dreigende dwarslaesie: direct dexamethason + spoedradiotherapie of -chirurgie.')],
    285: [('Wat is obstipatie en wat zijn de oorzaken bij patiënten met kanker?',
           'Minder dan 3× per week en/of harde, moeizaam te passeren ontlasting met klachten.<br>Oorzaken: opioïden (belangrijkste), andere medicatie (anticholinergica, ondansetron, ijzer), weinig vocht en vezels, immobiliteit, hypercalciëmie en hypokaliëmie, tumorobstructie, neurologische oorzaken.'),
          ('Hoe behandel je obstipatie bij een palliatieve patiënt?',
           '- Profylactisch laxans bij elk opioïd<br>- Osmotisch (macrogol, lactulose) en/of contactlaxans (bisacodyl, sennosiden)<br>- Rectaal bij fecale impactie<br>- Methylnaltrexon of naloxegol bij opioïd-geïnduceerde obstipatie')],
    288: [('Wat zijn de verschijnselen van pleuravocht?',
           'Dyspneu, droge hoest, ademhalingsgebonden pijn.<br>LO: gedempte percussie, verminderd ademgeruis, opgeheven stemfremitus.'),
          ('Wat zijn de verschijnselen van maligne ascites, en wat is de meest voorkomende oorzaak?',
           'Toenemende buikomvang, vol gevoel en vroege verzadiging, dyspneu, oedeem. LO: shifting dullness en undulatie.<br>Oorzaak meestal peritonitis carcinomatosa.'),
          ('Waarom kan bij pleuravocht wél pleurodese, maar bij ascites niet — en wat doe je bij ascites?',
           'Bij pleurodese (talk) plakken de twee pleurabladen aan elkaar; in de buikholte kan dat niet.<br>Ascites: herhaalde paracentese of een verblijfskatheter. Diuretica helpen bij ascites door portale hypertensie, maar nauwelijks bij maligne ascites door peritoneale metastasen.')],
    289: [('Hoe diagnosticeer je een depressie bij een patiënt met kanker?',
           'Somatische symptomen (moeheid, gewichtsverlies, slaapstoornis) zijn onbruikbaar: die horen ook bij de ziekte.<br>Let op de psychologische kernsymptomen: aanhoudende somberheid, anhedonie, hopeloosheid, waardeloosheid, schuld, suïcidale gedachten.<br>Sluit delier, hypothyreoïdie en medicatie (corticosteroïden) uit.'),
          ('Hoe behandel je een depressie bij een patiënt met kanker?',
           '- Psychosociale begeleiding / psychotherapie<br>- Antidepressivum: SSRI, of mirtazapine bij slaap- en eetlustproblemen<br>- Psychostimulantia bij korte levensverwachting<br>- Goede behandeling van pijn en andere symptomen<br>- Zo nodig een geestelijk verzorger')],
    291: [('Wat zijn de symptomen van een delier, en welke twee vormen onderscheid je?',
           'Acuut begin, wisselend beloop over de dag, gestoorde aandacht en bewustzijn, desoriëntatie, hallucinaties en wanen, verstoord dag-nachtritme.<br>Hyperactief (onrust, plukken) of hypoactief (stil, teruggetrokken — wordt vaak gemist en aangezien voor depressie).<br>In de terminale fase bij 80-90%.'),
          ('Hoe behandel je een delier?',
           '1. Uitlokkende factoren behandelen<br>2. Niet-medicamenteus: oriëntatiepunten, rustige omgeving, bril en gehoorapparaat, naasten erbij, dag-nachtritme, uitleg aan naasten<br>3. Medicamenteus: haloperidol eerste keus; benzodiazepine alleen bij ernstige onrust of alcoholonttrekking')],
    312: [('Wat is het aangrijpingspunt van de verschillende antistollingsmiddelen?',
           '- Acetylsalicylzuur: irreversibel COX-1 → geen tromboxaan A2 (primaire hemostase)<br>- Clopidogrel/ticagrelor: P2Y12 (ADP-receptor)<br>- Abciximab: GpIIb/IIIa<br>- Heparine/LMWH: via antitrombine op Xa (en IIa)<br>- VKA (acenocoumarol, fenprocoumon): vitamine K-epoxidereductase → II, VII, IX, X; gemonitord met INR<br>- DOAC: rivaroxaban/apixaban/edoxaban remmen Xa, dabigatran remt trombine<br>- SSRI: minder serotonine-opname in trombocyten'),
          ('Wat zijn de antidota van de antistollingsmiddelen?',
           '- VKA: vitamine K (plus 4-factorenconcentraat bij bloeding)<br>- Heparine: protaminesulfaat<br>- Dabigatran: idarucizumab<br>- Xa-remmers: andexanet alfa<br>- Trombocytenaggregatieremmers: geen antidotum (trombocytentransfusie)')],
    317: [('Wat is bèta-thalassemie en hoe presenteert de heterozygote vorm (minor)?',
           'Verminderde of afwezige bèta-globinesynthese → overtollige alfaketens slaan neer → ineffectieve erytropoëse. Vooral Middellandse Zeegebied, Midden-Oosten en Azië.<br>Minor: mild, sterk verlaagd MCV bij normaal of hoog erytrocytenaantal, HbA2 &gt;3% — vaak verward met ijzergebrek.'),
          ('Hoe presenteert bèta-thalassemie major (homozygoot)?',
           'Ernstige transfusieafhankelijke anemie vanaf de eerste levensmaanden (als HbF wegvalt), hemolyse, hepatosplenomegalie en extramedullaire hematopoëse, skeletafwijkingen door mergexpansie, en ijzerstapeling (door transfusies én lage hepcidine).')],
    318: [('Wat is de oorzaak en het mechanisme van sikkelcelziekte?',
           'Puntmutatie in het bèta-globinegen → HbS, dat bij deoxygenatie polymeriseert: sikkelvorming → hemolyse + vaso-occlusie.<br>Autosomaal recessief; vooral Afrikaanse en Caribische herkomst. MCV normaal (kwalitatieve hemoglobinopathie). Heterozygoot dragerschap: weinig tot geen klachten.'),
          ('Wat zijn de belangrijkste complicaties en de behandeling van sikkelcelziekte?',
           'Complicaties: vaso-occlusieve pijncrises, acute chest syndrome, herseninfarct, miltsequestratie en functionele asplenie (pneumokokkensepsis), aplastische crise door parvovirus B19, priapisme, nierschade.<br>Behandeling: hydroxycarbamide (↑HbF), foliumzuur, transfusie, vaccinaties + penicillineprofylaxe; allogene SCT is curatief.')],
    370: [('Wat zijn de alarmsymptomen van een dreigende dwarslaesie bij wervelmetastasen?',
           'Nieuwe of veranderde rugpijn (vaak dagen tot weken vooraf, erger bij liggen of persen), radiculaire uitstraling, krachtverlies, sensibele niveaugrens; pas laat mictie- of defecatiestoornissen.'),
          ('Wat is het beleid bij een dreigende dwarslaesie door wervelmetastasen?',
           'Spoed-MRI van de hele wervelkolom en direct dexamethason, gevolgd door radiotherapie of chirurgische decompressie.<br>De neurologische status bij de start bepaalt de uitkomst: wie nog loopt, blijft meestal lopen — dus niet afwachten.')],
}

# ---------------------------------------------------------------- nieuwe kaarten
T = {  # tagsets
    'T1': 'GZC3::A::T1-benigne-hematologie GZC3::doelstelling',
    'T2': 'GZC3::A::T2-maligne-hematologie GZC3::doelstelling',
    'T2c21': 'GZC3::A::T2-maligne-hematologie GZC3::casus::2.1 GZC3::zelfstudie::Z03',
    'T2c22': 'GZC3::A::T2-maligne-hematologie GZC3::casus::2.2 GZC3::zelfstudie::Z03',
    'T2c31': 'GZC3::A::T2-maligne-hematologie GZC3::casus::3.1 GZC3::zelfstudie::Z04',
    'T2c32': 'GZC3::A::T2-maligne-hematologie GZC3::casus::3.2 GZC3::zelfstudie::Z04',
    'T1c11': 'GZC3::A::T1-benigne-hematologie GZC3::casus::1.1 GZC3::zelfstudie::Z02',
    'T4': 'GZC3::A::T4-orgaanspecifiek GZC3::doelstelling',
    'B1': 'GZC3::B::B1-public-health GZC3::doelstelling',
    'B1z16': 'GZC3::B::B1-public-health GZC3::zelfstudie::Z16',
    'B3': 'GZC3::B::B3-pijn-palliatief GZC3::doelstelling',
}
NIEUW = [
    ('T1c11', 'Casus 1.1: hoe interpreteer je het lab van de 65-jarige man (Hb 4,6, MCV 68, MCHC laag, reticulocyten laag)?',
     'Microcytaire, hypochrome anemie met een inadequate beenmergrespons (lage reticulocyten) → aanmaakstoornis door ijzergebrek.<br>Bij een man van 65 is dat gastro-intestinaal bloedverlies tot het tegendeel bewezen is (hier een coecumcarcinoom).', False),
    ('T1', 'Wat is trombotische trombocytopenische purpura (TTP)?',
     'Tekort aan ADAMTS13 (meestal verworven door autoantistoffen), waardoor ultragrote VWF-multimeren niet worden geknipt → plaatjesrijke microtrombi.<br>Beeld: trombocytopenie + micro-angiopathische hemolytische anemie (fragmentocyten), eventueel neurologische klachten, nierfunctiestoornis en koorts.<br>Spoedsituatie: plasmaferese (plus immuunsuppressie).', True),
    ('T1', 'Wat is het defect bij de ziekte van Glanzmann en bij het Bernard-Soulier-syndroom?',
     'Glanzmann: defect GpIIb/IIIa → geen aggregatie (normaal plaatjesaantal).<br>Bernard-Soulier: defect GpIb → geen adhesie via VWF; reuzenplaatjes en trombocytopenie.<br>Beide: erfelijke trombopathie met een stoornis in de primaire hemostase.', True),
    ('T1', 'Welke stollingsstoornis geeft een ernstige bloeding (bv. navelstomp of intracranieel bij een neonaat) met een normale PT en aPTT?',
     'Factor XIII-deficiëntie. Factor XIII stabiliseert het fibrinenetwerk, maar PT en aPTT meten alleen het ontstaan van fibrine en blijven dus normaal. Aantonen met een specifieke factor XIII-bepaling.', True),
    ('T1', 'Wat is sideroblastaire anemie?',
     'Stoornis in de heemsynthese waardoor ijzer zich ophoopt in de mitochondriën rond de kern: ringsideroblasten in het beenmerg (ijzerkleuring).<br>Erfelijk (X-gebonden, microcytair) of verworven: MDS, alcohol, loodintoxicatie, vitamine B6-tekort/isoniazide.<br>Ferritine en ijzer normaal tot verhoogd; reticulocyten niet verhoogd.', True),
    ('T2c21', 'Wat is de DD van pijnloze vergrote lymfeklieren?',
     'Reactief: viraal (EBV, CMV, hiv), bacterieel, specifiek (tbc, toxoplasmose, kattenkrabziekte)<br>Maligne: lymfoom (Hodgkin, NHL), CLL, metastase van een solide tumor<br>Overig: sarcoïdose, auto-immuunziekte, medicatie', False),
    ('T2c21', 'Wanneer doe je een biopsie van een vergrote lymfeklier?',
     'Bij een klier &gt;1-2 cm die na 4-6 weken niet verdwenen is zonder verklaring, bij harde of gefixeerde klieren, supraclaviculaire lokalisatie, groei, of bijkomende B-symptomen of een afwijkend bloedbeeld.<br>Bij verdenking lymfoom: excisiebiopt (architectuur nodig). In de hals bij een oudere roker eerst een punctie om een metastase van een plaveiselcelcarcinoom uit te sluiten.', False),
    ('T2c21', 'Welke factoren zijn ongunstig bij een Hodgkinlymfoom in vroeg stadium?',
     'Grote mediastinale massa (mediastinum/thorax-ratio &gt;1/3), hogere leeftijd (≥50 jaar), verhoogde BSE, B-symptomen, meerdere (≥3-4) aangedane klierstations en extranodale lokalisatie.<br>Ze bepalen of iemand de gunstige of de ongunstige (intensievere) vroeg-stadiumbehandeling krijgt.', True),
    ('T2c22', 'Casus 2.2: wat is de FLIPI-score van de 56-jarige man met een folliculair lymfoom in alle klierstations en het beenmerg (lab normaal)?',
     'FLIPI 2 = intermediair risico: stadium IV (1 punt) en &gt;4 klierstations (1 punt). Leeftijd &lt;60, Hb en LDH normaal leveren geen punten op.', False),
    ('T2', 'Welke infecties zijn geassocieerd met lymfomen?',
     '- EBV: Burkitt (endemisch), Hodgkin (~40%), posttransplantatielymfoom, NK/T-cellymfoom<br>- HTLV-1: adulte T-celleukemie/-lymfoom<br>- H. pylori: MALT-lymfoom van de maag<br>- HHV-8: primary effusion lymphoma<br>- Hepatitis C: marginale-zonelymfoom<br>- Hiv: indirect via immuundeficiëntie', True),
    ('T2c31', 'Wat zijn de belangrijkste oorzaken van hypercalciëmie?',
     'Samen &gt;90%: primaire hyperparathyreoïdie (meest bij de poliklinische patiënt) en maligniteit (meest bij de opgenomen patiënt).<br>Overig: vitamine D-intoxicatie, granulomateuze ziekte (sarcoïdose), medicatie (thiazide, lithium, calcium), immobilisatie, hyperthyreoïdie.', False),
    ('T2c31', 'Via welke mechanismen veroorzaakt een maligniteit hypercalciëmie?',
     '1. PTHrP-productie door de tumor (humorale hypercalciëmie, o.a. plaveiselcelcarcinomen) — het meest voorkomend<br>2. Lokale osteolyse door botmetastasen of myeloom (osteoclastactivatie)<br>3. Calcitriolproductie (1,25-OH-vitamine D) door lymfomen', False),
    ('T2c31', 'Wat zijn oorzaken van een verhoogd totaal eiwit in het bloed?',
     'Monoklonaal (M-proteïne): multipel myeloom, M. Waldenström, MGUS<br>Polyklonaal: chronische infectie of ontsteking, leverziekte/cirrose, auto-immuunziekte<br>Relatief: dehydratie (hemoconcentratie)', False),
    ('T2c32', 'Wat is de DD van een pancytopenie?',
     'Centraal (beenmerg): infiltratie (acute leukemie, lymfoom, myeloom, metastasen), aplastische anemie, MDS, myelofibrose, B12-/foliumzuurtekort, chemotherapie of medicatie, virale infectie<br>Perifeer: hypersplenisme (sequestratie), auto-immuun, sepsis/DIS<br>Meestal is beenmergonderzoek nodig.', False),
    ('T2c32', 'Wat zijn risicofactoren voor het ontstaan van AML?',
     'Eerdere chemotherapie (alkylerende middelen, topo-II-remmers) of radiotherapie (therapiegerelateerde AML), ioniserende straling, benzeen, roken, voorafgaande MDS of MPN, en syndromen zoals Down en Fanconi. Meestal is er geen aanwijsbare oorzaak.', True),
    ('T4', 'Wat zijn de histologische kenmerken van een plaveiselcelcarcinoom?',
     'Invasief groeiende nesten en strengen atypische plaveiselcellen met verhoorning (keratinisatie, hoornparels), intercellulaire bruggen (desmosomen) en expressie van keratine (bv. CK5/6, p40/p63). De mate van verhoorning bepaalt de differentiatiegraad.', True),
    ('T4', 'Waarom wordt bij hoofd-halstumoren een versneld (geaccelereerd) bestralingsschema gebruikt?',
     'Plaveiselcelcarcinomen repopuleren snel tijdens een lange bestralingsperiode. Door de totale behandelduur te verkorten (bv. 6 in plaats van 5 fracties per week) neemt de kans op locoregionale controle toe. De prijs: heftigere acute reacties.', True),
    ('T4', 'Waarom zijn tandheelkundige sanering en fluorideprofylaxe belangrijk bij hoofd-halsradiotherapie?',
     'Door xerostomie ontstaat stralingscariës, en tandextracties in bestraald bot geven een risico op osteoradionecrose. Daarom vooraf tandheelkundige sanering en daarna langdurig (levenslang) dagelijks fluoride bij een hoge dosis op de speekselklieren.', True),
    ('T4', 'Wat zijn de gevolgen van doorroken tijdens en na radiotherapie voor een hoofd-halstumor?',
     'Meer complicaties, meer lokale recidieven (slechtere tumoroxygenatie → minder stralingsgevoelig) en meer tweede primaire tumoren. Níet meer afstandsmetastasen.', True),
    ('B1z16', 'Hoe is de Nederlandse gezondheidszorg in echelons georganiseerd?',
     '- Nulde lijn: collectieve preventie (GGD, jeugdgezondheidszorg, bevolkingsonderzoek)<br>- Eerste lijn: vrij toegankelijk (huisarts, wijkverpleging, fysiotherapeut, apotheek)<br>- Tweede lijn: specialistische zorg na verwijzing (ziekenhuis, GGZ)<br>- Derde lijn: hoogspecialistische zorg (UMC\'s, categorale centra)<br>De huisarts is de poortwachter tussen eerste en tweede lijn.', False),
    ('B1', 'Wat is het verschil tussen sterftecijfer (mortaliteit) en letaliteit?',
     'Sterftecijfer: aantal sterfgevallen door een ziekte per aantal personen in de bevolking per periode.<br>Letaliteit: het aandeel van de mensen mét de ziekte dat eraan overlijdt — een maat voor de ernst van de ziekte.', False),
    ('B3', 'Welke neurotransmitters/receptoren zijn betrokken bij misselijkheid en braken?',
     '- Dopamine (D2): haloperidol, metoclopramide<br>- Serotonine (5-HT3): ondansetron<br>- Histamine (H1): cyclizine, cinnarizine<br>- Acetylcholine (muscarine): scopolamine<br>- Substance P (NK1): aprepitant<br>Noradrenaline speelt géén rol.', True),
]

# ---------------------------------------------------------------- prioriteit: onderwerpen uit oude tentamens
PRIO = {4, 12, 44, 45, 48, 59, 67, 74, 76, 78, 86, 87, 89, 96, 97, 103, 104, 107, 110, 114, 115, 120, 121,
        127, 129, 138, 140, 141, 148, 151, 152, 156, 157, 159, 164, 169, 170, 193, 201, 209, 216, 218, 223,
        224, 260, 262, 264, 273, 275, 279, 287, 288, 291, 305, 306, 312, 317, 318, 319, 327, 343, 345, 346,
        348, 351, 354, 370, 389, 410, 411, 413, 414, 415, 417, 422, 424, 426, 428, 429, 430, 433, 436, 439,
        449, 462, 469, 482, 490, 495, 506, 509, 518, 520, 524, 528, 541, 542, 543, 546, 549, 559, 561, 562,
        570, 571, 573, 574, 575, 582, 583, 584, 586, 615, 624, 629, 632, 633, 637, 648, 649, 650, 651}

PREFIX = re.compile(r'^Zelfstudie \d+(?: \(casus ([\d.]+)\))?: ')


def strip_prefix(front):
    m = PREFIX.match(front)
    if not m:
        return front
    rest = front[m.end():]
    if m.group(1) and re.search(r'casus|\bpatiënte\b|\bhaar\b', rest, re.I):
        return f'Casus {m.group(1)}: {rest}'
    return rest[0].upper() + rest[1:]


def plain_len(s):
    return len(html.unescape(re.sub(r'<[^>]+>', '', s)))


def new_guid(front):
    return 'gzc3chk-' + hashlib.sha1(front.encode()).hexdigest()[:12]


def main():
    con = sqlite3.connect(DB)
    notes = con.execute('select guid, tags, flds from notes order by id').fetchall()
    rows, stats = [], {}

    def add(guid, front, back, tags, label):
        stats[label] = stats.get(label, 0) + 1
        rows.append([guid, NOTETYPE, DECK, front, back, ' '.join(tags)])

    for n, (guid, tags, flds) in enumerate(notes, start=1):
        front, back = flds.split('\x1f')
        tags = tags.split()
        extra = []
        if n in DUBBEL:
            extra.append('check::dubbel')
            label = 'dubbel'
        elif n in VERWIJDEREN:
            extra.append('check::verwijderen')
            label = 'verwijderen'
        elif n in SPLIT:
            parts = SPLIT[n]
            front, back = parts[0]
            extra.append('check::gesplitst')
            label = 'gesplitst'
        elif n in EDIT:
            f, b = EDIT[n]
            front, back = (f or front), (b or back)
            extra.append('check::aangepast')
            label = 'aangepast'
        else:
            extra.append('check::behouden')
            label = 'behouden'
        if n not in DUBBEL and n not in VERWIJDEREN:
            front = strip_prefix(front)
            if n in PRIO:
                extra.append('prio::tentamen')
            if label in ('behouden', 'aangepast') and plain_len(back) > 400:
                extra.append('check::lang')
        if n in INHOUD:
            extra.append('check::inhoud-controleren')
        add(guid, front, back, tags + extra, label)
        if n in SPLIT:
            for f, b in SPLIT[n][1:]:
                t = tags + ['check::gesplitst'] + (['prio::tentamen'] if n in PRIO else [])
                add(new_guid(f), f, b, t, 'gesplitst-nieuw')

    for key, f, b, prio in NIEUW:
        t = T[key].split() + ['check::nieuw'] + (['prio::tentamen'] if prio else [])
        add(new_guid(f), f, b, t, 'nieuw')

    out = OUT / 'GZC3_check_import.txt'
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        fh.write('#separator:tab\n#html:true\n#guid column:1\n#notetype column:2\n#deck column:3\n#tags column:6\n')
        csv.writer(fh, delimiter='\t', lineterminator='\n').writerows(rows)

    blijft = sum(v for k, v in stats.items() if k not in ('dubbel', 'verwijderen'))
    lang = sum(1 for r in rows if 'check::lang' in r[5])
    prio = sum(1 for r in rows if 'prio::tentamen' in r[5])
    lines = [f'{k}: {v}' for k, v in sorted(stats.items())]
    lines += [f'totaal regels: {len(rows)}', f'na opruimen (zonder dubbel/verwijderen): {blijft}',
              f'check::lang: {lang}', f'prio::tentamen: {prio}']
    (OUT / 'statistiek.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
