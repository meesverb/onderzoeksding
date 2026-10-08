# Overdracht GZC III-studieproject (stand: 8 oktober 2026)

Plak dit in een nieuwe chat, of verwijs naar dit bestand op GitHub: repo `meesverb/onderzoeksding`, branch `claude/happy-goodall-mfwkk9`, map `anki-check/`.

## Wie en wat
- Geneeskundestudent, bachelor 3 (CRU+, UMC Utrecht), blok **Gezonde en Zieke Cellen III**.
- **Tentamen: donderdag 29 oktober 2026.** Leerdeadline voor nieuwe kaarten: 22 oktober.
- Leert met Anki 26.05 op Windows en op de telefoon. Versies 26.08 en 26.09 waren niet te installeren.
- **Werkwijze:** antwoord in het Nederlands, kort en to the point. Let op de tokenkosten: gebruik geen workflows of multi-agentrondes, tenzij de student daar zelf om vraagt.

## Bronnen
- **Google Drive-map "anki GZC III"** (id `1C_pR9kLuvoXzAtUjGUH2cm9hzvIFZrWA`) bevat:
  - het originele deck (652 kaarten);
  - het blokboek;
  - 6 oude tentamens;
  - slides (PDF) en transcripten (.txt), met het collegenummer in de bestandsnaam.
- **PDF's uit Drive:** lees ze met `read_file_content`. `download_file_content` is te groot.
- **Quiz "Uitstrijkje":** https://claude.ai/artifact/PhtbTb1u2XnUrMCQ8fTcYr. De bron staat in `quiz/` (`sjabloon.html` plus `vragen.json`, gebouwd tot `index.html`). De voortgang staat in de localStorage van de browser, per apparaat.

## Stand van zaken
- **Verwerkt** (slides en transcript): HC 1-7 en HC 13. Er ontbraken drie transcripten: het HC-deel van HC 1, HC 4/IC 4 en HC 6. Per college zijn er:
  - een kapstok met 5 controlevragen;
  - nieuwe kaarten, nadruk-tags en correcties;
  - een precieze koppeling `college::HCx`.
- **Nog niet verwerkt:** HC 8-12, HC AI, HC 14-19, PH 1-8 en HC 28-31. Hun kaarten zitten wel in het deck, maar zijn alleen op trefwoord aan een college gekoppeld.
- **Deck na installatie:** 1309 kaarten, twee keer zoveel als het origineel.

  | Bron | Kaarten |
  |---|---|
  | Eigen deck, opgeschoond | 592 |
  | Import 2: casussen, schema's en tabellen (dezelfde stof in een andere vorm) | 253 |
  | Import 3: kaarten uit de colleges | 464 |

  - 669 kaarten zijn **kern**: `prio::tentamen`, `nadruk::docent` of `GZC3::doelstelling`.
  - Realistisch haalbaar zijn er ~750 tot 22 oktober (~50 per dag). De kern past daarin, het hele deck niet.
- **Kaartgrootte:**
  - mediane achterkant: eigen deck 35 woorden, collegekaarten 27, import 2 12;
  - ongeveer 1 op de 4 kaarten heeft een achterkant van meer dan 40 woorden. Dat zijn opsommingen of meerdere mechanismen op één kaart.
- **Noodpakket** (`noodpakket.md`, deck *GZC III - Noodpakket*):
  - 193 essentiekaarten, met een antwoord van gemiddeld 6 à 9 woorden;
  - per thema een samenvatting;
  - apart van de campagne.
- **Afbeeldingen:** 38 stuks op 90 kaarten, plus 20 herkenkaarten. Bronnen staan in `beelden/BRONNEN.md`.
- **Lastige kaarten:** de W-toets zet de tag `opgezocht` en houdt een teller bij in de collectieconfig (`gzc3_opgezocht`). De campagne combineert dat met het aantal keer fout en de rode vlag.
- **Of de student alles heeft geïnstalleerd**, is niet bekend. De installatiecheck in de add-on laat het zien.

## Bestanden (`anki-check/`)
| Bestand | Inhoud |
|---|---|
| `GZC3_check_import.txt`, `bouw_import.py`, `rapport.md` | deckcheck tegen het blokboek (import 1) |
| `GZC3_extra_import.txt`, `bouw_extra.py`, `extra_inhoud.py` | casussen, schema's, tabellen, ezelsbruggen (import 2) |
| `colleges_inhoud.py` | HC 1-5 met de hand: kapstok, vragen, kaarten, casussen, tabellen, schema's |
| `verwerking/HCx.json` (+ `README.md`) | verwerkte colleges; `HC6.json` is het voorbeeld van een volledig nieuw college |
| `bouw_colleges.py` | voegt alles samen → `GZC3_colleges_import.txt` (import 3), `kapstokken/`, `koppeling.md`, `campagne-addon/data/`, de quiz |
| `campagne-addon/` | campagne-add-on (`campagne.py` = logica, `scherm.py` = HTML, `__init__.py` = Anki-koppeling); de voortgang staat in de collectieconfig en synchroniseert mee |
| `waarom-addon/` | W-toets: kopieert vraag + antwoord als prompt naar Claude (houdt niets bij) |
| `bouw_nood_beelden.py`, `verwerking/nood.json`, `verwerking/beelden.json`, `beelden/` | noodpakket en afbeeldingen → `campagne-addon/data/` (GZC3_nood_import, GZC3_beelden_import, nood.json, beelden.json, beelden/) |
| `test_campagne.py` | test in een lege collectie (vereist `pip install anki==26.5`); moet eindigen met `ALLES OK` |
| `STARTEN.md` | uitleg voor de student |

## Een nieuw college verwerken (afgesproken werkwijze)
1. Lees de slides, het transcript en de leerdoelen uit het blokboek. Leg ze naast de bestaande kaarten van dat college (`tag:college::HCx`, of zoek op trefwoord in de importbestanden).
2. Schrijf `verwerking/HCx.json` in hetzelfde formaat als `HC6.json`. **Beperk je:**
   - een kapstok met 5 controlevragen;
   - nadruk (`prio_guids`) en correcties op bestaande kaarten;
   - **maximaal ~15 nieuwe, kleine kaarten**, met één feit per kaart en een antwoord van ongeveer 15 woorden of minder.
   Doe het in één ronde, zonder tweede controleur.
3. Ontbreekt het college in `THEMA_NIEUW` (bovenaan `bouw_colleges.py`)? Voeg het dan toe:
   - HC 14-19 → T4;
   - PH → B1;
   - HC 28-29 → B2;
   - HC 30-31 → B3.
4. Bouwen, testen en inpakken:
   ```
   cd anki-check
   python3 bouw_colleges.py
   python3 test_campagne.py /tmp/uit
   cd campagne-addon && rm -f ../gzc3_campagne.ankiaddon && zip -r ../gzc3_campagne.ankiaddon . -x '*__pycache__*'
   ```
5. Commit, push en stuur `gzc3_campagne.ankiaddon` naar de student. De student installeert die over de oude heen. Daarna verschijnt **Import 3** weer in de installatiecheck.

## Lastige kaarten van de student verwerken
De student plakt een lijst met de kop "Ik leer voor het blok Gezonde en Zieke Cellen III … mijn lastigste Anki-kaarten". Lever het gevraagde importbestand:
- herschreven kaarten houden dezelfde GUID;
- nieuwe kaarten krijgen een GUID die begint met `gzc3l-`;
- notitietype `1706371006450`, deck *GZC III - Compleet*, tag `lastig::herschreven`.

## Open ideeën (nog niet gebouwd)
- **Lange kaarten opsplitsen:** de ~330 kaarten met een achterkant van meer dan 40 woorden, te beginnen bij de kern.
- **Quiz synchroniseren tussen telefoon en laptop:** via de opslag van het artifact, in plaats van localStorage.
