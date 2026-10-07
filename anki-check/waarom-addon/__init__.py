"""Vraag Claude waarom — druk tijdens het herhalen op W (instelbaar).

Zet de vraag en het antwoord van de huidige kaart in een kant-en-klare prompt, kopieert die naar
het klembord en opent Claude: in Claude Desktop met de prompt al ingevuld, anders in de browser
(dan alleen nog Ctrl+V en Enter).

Elke keer opzoeken wordt bijgehouden: de kaart krijgt de tag `opgezocht` en een teller in de collectie
(sleutel gzc3_opgezocht, synchroniseert mee). De campagne-add-on gebruikt dat voor "Lastige kaarten".
"""
import html
import re
import sys
from urllib.parse import quote

from aqt import gui_hooks, mw
from aqt.qt import QAction, QApplication, QDesktopServices, QUrl
from aqt.utils import tooltip

DEFAULTS = {
    "sneltoets": "w",
    "openen_in": "auto",  # auto | desktop | web
    "bijhouden": True,
    "prompt": (
        "Ik leer voor het blok Gezonde en Zieke Cellen III (geneeskunde, bachelor jaar 3). "
        "Hieronder staat een flashcard. Leg uit WAAROM het antwoord klopt: het onderliggende mechanisme "
        "of de redenering, zodat ik het begrijp in plaats van stamp. Maximaal ongeveer 150 woorden, "
        "in het Nederlands. Geef een ezelsbrug als er een goede bestaat, en zeg het als de kaart "
        "iets onjuists of verouderds bevat.\n\nVRAAG:\n{vraag}\n\nANTWOORD:\n{antwoord}\n\nTAGS: {tags}"
    ),
}


def cfg():
    c = dict(DEFAULTS)
    c.update(mw.addonManager.getConfig(__name__) or {})
    return c


def naar_tekst(veld):
    # schema's (SVG): alleen de tekst uit de vakken bewaren
    veld = re.sub(r"<svg.*?</svg>", lambda m: "\n[schema met vakken: " + " | ".join(
        html.unescape(t) for t in re.findall(r"<text[^>]*>(.*?)</text>", m.group(0), re.S)) + "]\n", veld, flags=re.S)
    veld = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", veld, flags=re.S)
    veld = re.sub(r"</t[dh]>", " | ", veld)
    veld = re.sub(r"<br\s*/?>|</(div|p|li|tr)>", "\n", veld)
    veld = re.sub(r"<img[^>]*>", "[afbeelding]", veld)
    veld = html.unescape(re.sub(r"<[^>]+>", "", veld))
    return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t]+", " ", veld)).strip()


def heeft_desktop():
    if sys.platform != "win32":
        return None  # onbekend: gewoon proberen
    import winreg
    for root, pad in ((winreg.HKEY_CURRENT_USER, r"Software\Classes\claude"), (winreg.HKEY_CLASSES_ROOT, "claude")):
        try:
            winreg.CloseKey(winreg.OpenKey(root, pad))
            return True
        except OSError:
            pass
    return False


OPGEZOCHT_KEY = "gzc3_opgezocht"


def registreer(note):
    """Onthoud dat je deze kaart opzocht: teller per GUID in de collectieconfig, plus de tag `opgezocht`."""
    try:
        teller = dict(mw.col.get_config(OPGEZOCHT_KEY, {}) or {})
        teller[note.guid] = teller.get(note.guid, 0) + 1
        mw.col.set_config(OPGEZOCHT_KEY, teller)
        if "opgezocht" not in (t.lower() for t in note.tags):
            mw.col.tags.bulk_add([note.id], "opgezocht")
        return teller[note.guid]
    except Exception:
        return 0


def vraag_waarom():
    card = mw.reviewer.card if mw.reviewer else None
    if not card:
        tooltip("Geen kaart open.")
        return
    note = card.note()
    keer = registreer(note) if cfg().get("bijhouden", True) else 0
    velden = list(note.values())
    vraag = naar_tekst(velden[0]) if velden else ""
    antwoord = naar_tekst("\n".join(velden[1:])) if len(velden) > 1 else naar_tekst(card.answer())
    c = cfg()
    prompt = c["prompt"].format(vraag=vraag, antwoord=antwoord, tags=" ".join(note.tags) or "-")[:12000]
    QApplication.clipboard().setText(prompt)

    wijze = c["openen_in"]
    if wijze == "auto":
        wijze = "web" if heeft_desktop() is False else "desktop"
    if wijze == "desktop" and QDesktopServices.openUrl(QUrl("claude://claude.ai/new?q=" + quote(prompt))):
        tooltip("Geopend in Claude — druk op Enter." + (f" (🔍 {keer}× opgezocht)" if keer else ""), period=2500)
        return
    QDesktopServices.openUrl(QUrl("https://claude.ai/new"))
    tooltip("Prompt gekopieerd — plak met Ctrl+V (Cmd+V) en druk op Enter." + (f" (🔍 {keer}× opgezocht)" if keer else ""), period=3500)


def sneltoetsen(state, shortcuts):
    if state == "review":
        shortcuts.append((cfg()["sneltoets"], vraag_waarom))


def contextmenu(reviewer, menu):
    actie = QAction(f"Vraag Claude waarom ({cfg()['sneltoets'].upper()})", menu)
    actie.triggered.connect(vraag_waarom)
    menu.addAction(actie)


gui_hooks.state_shortcuts_will_change.append(sneltoetsen)
gui_hooks.reviewer_will_show_context_menu.append(contextmenu)
