"""Campagne GZC III — je voortgang als spel, in het hoofdscherm van Anki.

Rekenwerk en weergave staan in campagne.py; dit bestand koppelt ze aan Anki.
"""
from aqt import gui_hooks, mw
from aqt.utils import askUser, tooltip

from . import campagne

CONFIG_KEY = 'gzc3_campagne'
DEFAULTS = {
    'deck': 'GZC III - Compleet',
    'examen': '2026-10-29',
    'leerdeadline': '2026-10-22',
    'reeks_drempel': 30,
    'eindfase_herhalingen': 150,
    'meldingen': True,
}
_vorige = {}


def cfg():
    c = dict(DEFAULTS)
    c.update(mw.addonManager.getConfig(__name__) or {})
    return c


def staat():
    return dict(mw.col.get_config(CONFIG_KEY, {}) or {})


def bewaar(s):
    mw.col.set_config(CONFIG_KEY, s)


def toon(deck_browser, content):
    try:
        s = campagne.bereken(mw.col, cfg(), staat())
        content.stats += campagne.weergave(s)
    except Exception as e:  # het hoofdscherm mag nooit stukgaan door deze add-on
        content.stats += f'<div style="color:#c2372f;margin:12px">Campagne GZC III: {e}</div>'


def bericht(handled, message, context):
    if not message.startswith('gzc3:'):
        return handled
    _, actie, *rest = message.split(':')
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
    elif actie == 'start':
        if askUser('Campagne starten?\n\n'
                   'Alle nieuwe GZC III-kaarten komen op volgorde van de colleges in het plan. Kaarten van colleges die je '
                   'nog niet hebt afgevinkt, gaan op slot (opgeschort). Vink je een college af, dan speel je die kaarten vrij.\n\n'
                   'Kaarten die je al geleerd hebt, veranderen niet. Je kunt het slot altijd weer uitzetten onder "Alle colleges".'):
            st['slot'] = True
            n = campagne.campagne_starten(mw.col, cfg(), st.get('afgevinkt', {}))
            st['volgorde'] = campagne.dt.date.today().isoformat()
            bewaar(st)
            tooltip(f'Campagne gestart: {n} nieuwe kaarten op volgorde gezet.')
    elif actie == 'vrij':
        st['slot'] = False
        bewaar(st)
        n = campagne.alles_vrijgeven(mw.col, cfg())
        tooltip(f'Slot uit: {n} kaarten vrijgegeven.')
    mw.deckBrowser.refresh()
    return (True, None)


def na_antwoord(reviewer, card, ease):
    c = cfg()
    if not c.get('meldingen', True):
        return
    try:
        nu = campagne.snel(mw.col, c, staat())
    except Exception:
        return
    global _vorige
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


def bij_start(*_):
    global _vorige
    _vorige = {}


gui_hooks.deck_browser_will_render_content.append(toon)
gui_hooks.webview_did_receive_js_message.append(bericht)
gui_hooks.reviewer_did_answer_card.append(na_antwoord)
gui_hooks.profile_did_open.append(bij_start)
