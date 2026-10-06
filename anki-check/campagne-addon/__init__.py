"""Campagne GZC III — je voortgang als spel, in het hoofdscherm van Anki.

Rekenwerk staat in campagne.py, de weergave in scherm.py; dit bestand koppelt ze aan Anki:
het hoofdscherm, het collegevenster, het HUD tijdens het leren en de installatiecheck.
"""
import html
import json

import aqt
from anki.collection import CsvMetadata, ImportCsvRequest
from aqt import gui_hooks, mw
from aqt.operations import CollectionOp
from aqt.operations.note import remove_notes
from aqt.qt import QDialog, QVBoxLayout
from aqt.utils import askUser, showInfo, tooltip
from aqt.webview import AnkiWebView

from . import campagne, scherm

CONFIG_KEY = 'gzc3_campagne'
DEFAULTS = {
    'deck': 'GZC III - Compleet',
    'examen': '2026-10-29',
    'leerdeadline': '2026-10-22',
    'reeks_drempel': 30,
    'eindfase_herhalingen': 150,
    'meldingen': True,
    'hud': True,
    'herkansing_dagen': 2,
}
IMPORTS = {'check': 'GZC3_check_import.txt', 'extra': 'GZC3_extra_import.txt', 'colleges': 'GZC3_colleges_import.txt'}
_vorige = {}   # stand na het vorige antwoord, voor de meldingen
_snel = {}     # laatste stand voor het HUD
_sessie = {}   # tellers van de huidige leersessie
_venster = None


def cfg():
    c = dict(DEFAULTS)
    c.update(mw.addonManager.getConfig(__name__) or {})
    return c


def staat():
    return dict(mw.col.get_config(CONFIG_KEY, {}) or {})


def bewaar(s):
    global _snel
    mw.col.set_config(CONFIG_KEY, s)
    _snel = {}


def ververs():
    if mw.state == 'deckBrowser':
        mw.deckBrowser.refresh()
    if _venster is not None:
        _venster.render()


# ------------------------------------------------------------------ hoofdscherm
def toon(deck_browser, content):
    try:
        c, st = cfg(), staat()
        s = campagne.bereken(mw.col, c, st)
        stappen = None
        if not st.get('installatie_klaar'):
            stappen = campagne.installatie(mw.col, c, st)
            if all(x['klaar'] for x in stappen):
                st['installatie_klaar'] = True
                bewaar(st)
        content.stats += scherm.weergave(s, stappen)
    except Exception as e:  # het hoofdscherm mag nooit stukgaan door deze add-on
        content.stats += f'<div style="color:#c2372f;margin:12px">Campagne GZC III: {html.escape(str(e))}</div>'


def bericht(handled, message, context):
    if not isinstance(message, str) or not message.startswith('gzc3:'):
        return handled
    try:
        verwerk(message.split(':')[1:])
    except Exception as e:
        showInfo(f'Campagne GZC III: {e}')
    return (True, None)


def verwerk(delen):
    actie, rest = delen[0], delen[1:]
    st = staat()
    if actie == 'vink':
        af = dict(st.get('afgevinkt', {}))
        key = rest[0]
        aan = key not in af
        if aan:
            af[key] = campagne.dt.date.today().isoformat()
        else:
            del af[key]
        st['afgevinkt'] = af
        bewaar(st)
        melding = f'+{campagne.XP_COLLEGE if key in campagne.COLLEGES else campagne.XP_EXTRA} XP' if aan else ''
        if st.get('slot'):
            n = campagne.vergrendel(mw.col, cfg(), af)
            if n:
                melding += f'<br>🔓 {n} kaarten vrijgespeeld!'
        if melding:
            tooltip(melding, period=3000)
    elif actie == 'limiet':
        s = campagne.bereken(mw.col, cfg(), st)
        campagne.zet_limiet(mw.col, cfg(), s['doel_nieuw'])
        st['limiet'] = s['vandaag'].isoformat()
        bewaar(st)
        tooltip(f'Vandaag staan er {s["doel_nieuw"]} nieuwe kaarten voor je klaar.')
    elif actie == 'start' or (actie == 'install' and rest[0] == 'campagne'):
        start(st)
    elif actie == 'vrij':
        st['slot'] = False
        bewaar(st)
        n = campagne.alles_vrijgeven(mw.col, cfg())
        tooltip(f'Slot uit: {n} kaarten vrijgegeven.')
    elif actie == 'college':
        open_college(rest[0])
        return
    elif actie == 'quiz':
        key, score = rest[0], int(rest[1])
        quiz = dict(st.get('quiz', {}))
        oud = quiz.get(key)
        if oud is None or score > oud:
            quiz[key] = score
            st['quiz'] = quiz
            bewaar(st)
            tooltip(f'🎯 Controlequiz {campagne.label(key)}: {score}/5 · +{campagne.XP_QUIZVRAAG * (score - (oud or 0))} XP', period=3500)
        if mw.state == 'deckBrowser':
            mw.deckBrowser.refresh()
        return  # het venster niet opnieuw laden: dan verdwijnen je antwoorden
    elif actie == 'browse':
        browser = aqt.dialogs.open('Browser', mw)
        browser.search_for(f'tag:college::{rest[0]}')
        return
    elif actie == 'herkansing':
        did, n = campagne.herkansing(mw.col, cfg(), rest[0] if rest else None)
        if not n:
            tooltip(f'Geen kaarten die je de laatste {cfg()["herkansing_dagen"]} dagen fout had. Goed bezig!')
            return
        mw.col.decks.select(did)
        tooltip(f'🔁 Herkansing: {n} kaarten klaargezet in „{campagne.HERKANSING}”.')
        mw.moveToState('overview')
        return
    elif actie == 'install':
        installeer(rest[0])
        return
    ververs()


def start(st):
    if askUser('Campagne starten?\n\n'
               'Alle nieuwe GZC III-kaarten komen op volgorde van de colleges in het plan. Kaarten van colleges die je '
               'nog niet hebt afgevinkt, gaan op slot (opgeschort). Vink je een college af, dan speel je die kaarten vrij.\n\n'
               'Kaarten die je al geleerd hebt, veranderen niet. Je kunt het slot altijd weer uitzetten onder "Uitleg en instellingen".'):
        st['slot'] = True
        n = campagne.campagne_starten(mw.col, cfg(), st.get('afgevinkt', {}))
        st['volgorde'] = campagne.dt.date.today().isoformat()
        bewaar(st)
        tooltip(f'Campagne gestart: {n} nieuwe kaarten op volgorde gezet.')


# ------------------------------------------------------------------ installatiecheck
def installeer(stap):
    if stap in IMPORTS:
        importeer(IMPORTS[stap])
    elif stap == 'opruimen':
        nids = list(mw.col.find_notes('tag:check::dubbel OR tag:check::verwijderen'))
        if nids and askUser(f'{len(nids)} notities verwijderen die in de check als dubbel of overbodig zijn gemarkeerd?\n\n'
                            'Ongedaan maken kan via Bewerken → Ongedaan maken.'):
            remove_notes(parent=mw, note_ids=nids).success(lambda _: ververs()).run_in_background()
    elif stap == 'fsrs':
        from aqt.deckoptions import display_options_for_deck_id
        did = mw.col.decks.id_for_name(cfg()['deck'])
        if did:
            display_options_for_deck_id(did)
            tooltip('Zet onderaan FSRS aan, stel de gewenste retentie in op 0,90 en klik op Opslaan.', period=8000)


def importeer(naam):
    pad = str(campagne.DATA / naam)

    def op(col):
        col.create_backup(backup_folder=mw.pm.backupFolder(), force=True, wait_for_completion=True)
        md = col.get_csv_metadata(path=pad, delimiter=None)
        md.dupe_resolution = CsvMetadata.DupeResolution.UPDATE
        return col.import_csv(ImportCsvRequest(path=pad, metadata=md))

    def klaar(out):
        log = out.log
        onderhoud(herorden=True)
        tooltip(f'{naam}: {len(log.new)} nieuw, {len(log.updated)} bijgewerkt. Er is eerst een back-up gemaakt.', period=6000)
        mis = len(log.missing_notetype) + len(log.missing_deck) + len(log.conflicting)
        if mis:
            showInfo(f'{mis} regels uit {naam} konden niet worden geïmporteerd (notitietype of deck niet gevonden). '
                     f'Importeer het bestand dan via Bestand → Importeren en kies het notitietype Basic en het deck {cfg()["deck"]}.')
        ververs()

    CollectionOp(parent=mw, op=op).success(klaar).run_in_background()


def onderhoud(herorden=False):
    """Zet de college-tags op de kaarten (ook na een import of synchronisatie) en houdt de campagnevolgorde bij."""
    n = campagne.koppel(mw.col)
    st = staat()
    if st.get('slot') and (n or herorden):
        campagne.campagne_starten(mw.col, cfg(), st.get('afgevinkt', {}))
    return n


# ------------------------------------------------------------------ collegevenster
class CollegeVenster(QDialog):
    def __init__(self, key):
        super().__init__(mw)
        self.key = key
        self.resize(800, 880)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.web = AnkiWebView(parent=self, title='gzc3_college')
        self.web.set_bridge_command(lambda cmd: bericht((False, None), cmd, self), self)
        lay.addWidget(self.web)
        self.render()

    def render(self):
        s = campagne.bereken(mw.col, cfg(), staat())
        self.setWindowTitle(f'{campagne.label(self.key)} — Campagne GZC III')
        self.web.stdHtml(scherm.dialoog(s, self.key), context=self)

    def done(self, r):
        global _venster
        _venster = None
        self.web.cleanup()
        super().done(r)


def open_college(key):
    global _venster
    if _venster is None:
        _venster = CollegeVenster(key)
    else:
        _venster.key = key
        _venster.render()
    _venster.show()
    _venster.raise_()
    _venster.activateWindow()


# ------------------------------------------------------------------ tijdens het leren
def _js(code):
    try:
        mw.reviewer.web.eval(scherm.HUD_JS + code)
    except Exception:
        pass


def bij_vraag(card):
    global _snel
    if not cfg().get('hud', True):
        return
    try:
        note = card.note()
        th = campagne.thema_van(note.tags)
        if not th:
            _js('gzc3hud(null);')
            return
        if not _snel:
            _snel = campagne.snel(mw.col, cfg(), staat())
        cl = campagne.college_van(note.tags, campagne.platte_tekst(note.joined_fields()))
        _js(f'gzc3hud({json.dumps(scherm.hud_data(_snel, th, cl))});')
    except Exception:
        pass


def na_antwoord(reviewer, card, ease):
    global _vorige, _snel
    c = cfg()
    try:
        if not campagne.thema_van(card.note().tags):
            return
        nu = campagne.snel(mw.col, c, staat())
        info = campagne.antwoord_xp(mw.col, card.id, ease, nu.get('combo', 0))
    except Exception:
        return
    _snel = nu
    s = _sessie
    s['n'] = s.get('n', 0) + 1
    s['goed'] = s.get('goed', 0) + (ease > 1)
    s['xp'] = s.get('xp', 0) + info['xp']
    s['nieuw'] = s.get('nieuw', 0) + info['nieuw']
    s['krit'] = s.get('krit', 0) + info['kritiek']
    s['combo'] = max(s.get('combo', 0), nu.get('combo', 0))

    if c.get('hud', True):
        pops = [(f'+{info["xp"]} XP', '')]
        if info['kritiek']:
            pops.append(('💥 Kritieke treffer! +10 XP', 'krit'))
        combo = nu.get('combo', 0)
        if ease > 1 and (combo in (10, 25) or (combo >= 50 and combo % 25 == 0)):
            pops.append((f'⚡ Combo {combo}!' + (' Nu ×2 XP' if combo == 10 else (' Nu ×3 XP' if combo == 25 else '')), 'combo'))
        _js(''.join(f'gzc3pop({json.dumps(t)}, {json.dumps(k)}, {i * 380});' for i, (t, k) in enumerate(pops)))

    if not c.get('meldingen', True):
        _vorige = nu
        return
    meldingen = []
    if _vorige and nu.get('level', 0) > _vorige.get('level', 0):
        meldingen.append(f'⬆️ Level {nu["level"]}: {nu["titel"]}!')
    for i, naam in enumerate(('Brons', 'Zilver', 'Goud')):
        if _vorige and nu['quests'][i] and not _vorige['quests'][i]:
            meldingen.append(f'🏅 Dagquest {naam} gehaald!')
    if not meldingen and nu.get('n') and nu['n'] % 50 == 0:
        rest = max(0, nu['doel'] - nu['nieuw'])
        meldingen.append(f'{nu["n"]} herhalingen vandaag' + (f' · nog {rest} nieuwe kaarten voor Zilver' if rest else ''))
    _vorige = nu
    if meldingen:
        tooltip('<br>'.join(meldingen), period=3500)


def bij_toestand(nieuw, oud):
    if nieuw == 'review' and oud != 'review':
        _sessie.clear()


def bij_einde_leren():
    s = dict(_sessie)
    _sessie.clear()
    if s.get('n', 0) < 5:
        return
    pct = round(100 * s['goed'] / s['n'])
    tooltip(f'<b>Sessie klaar</b><br>{s["n"]} kaarten ({s["nieuw"]} nieuw) · {pct}% goed · +{s["xp"]} XP'
            f'<br>⚡ beste combo {s["combo"]}' + (f' · 💥 {s["krit"]} kritieke treffer{"s" if s["krit"] != 1 else ""}' if s['krit'] else ''),
            period=7000)


def bij_start(*_):
    global _vorige, _snel
    _vorige, _snel = {}, {}
    try:
        n = onderhoud()
        if n:
            tooltip(f'Campagne GZC III: {n} kaarten aan hun college gekoppeld.', period=4000)
    except Exception as e:
        print('Campagne GZC III:', e)


def na_sync():
    try:
        onderhoud()
    except Exception as e:
        print('Campagne GZC III:', e)


gui_hooks.deck_browser_will_render_content.append(toon)
gui_hooks.webview_did_receive_js_message.append(bericht)
gui_hooks.reviewer_did_show_question.append(bij_vraag)
gui_hooks.reviewer_did_answer_card.append(na_antwoord)
gui_hooks.reviewer_will_end.append(bij_einde_leren)
gui_hooks.state_did_change.append(bij_toestand)
gui_hooks.profile_did_open.append(bij_start)
gui_hooks.sync_did_finish.append(na_sync)
