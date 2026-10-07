# Verwerking van slides en transcripten

Elk bestand `HCx.json` is het **gecontroleerde** resultaat van een workflow met twee stappen:

1. een agent las de slides, het transcript en de leerdoelen uit het blokboek, en legde ze naast de bestaande kaarten;
2. een tweede, sceptische agent las dezelfde bronnen en hield alleen over wat juist is, niet dubbel en niet triviaal.

`bouw_colleges.py` voegt deze bestanden samen met `colleges_inhoud.py`. Er zijn twee soorten bestanden.

**Aanvulling op een college dat al verwerkt was** (HC 1, 2, 3, 5), op basis van de transcripten:
- `nieuwe_kaarten`: krijgen de tag `bron::transcript` en een 🎙️ op de voorkant;
- `prio_guids`: bestaande kaarten waar de docent nadruk op legt; de add-on zet daar `prio::tentamen` en `nadruk::docent` op;
- `correcties`: bestaande kaarten die niet klopten met het college; de verbeterde versie gaat mee in `GZC3_colleges_import.txt`;
- `kapstok_aanvullingen`, `valkuilen`, `tentamentips` en `docentcitaten`: komen in de kapstok en in het collegevenster.

**Volledig nieuw verwerkt college** (HC 6, 7, 13): een kapstok, controlevragen, kaarten, casussen en tabellen, plus correcties, nadruk en `koppeling` (welke bestaande kaart bij welk college hoort).

In elk bestand staat onder `afgewezen` wat de controleur heeft geschrapt, en waarom.
