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
        if key in af:
            del af[key]
        else:
            af[key] = campagne.dt.date.today().isoformat()
            tooltip(f'+{campagne.XP_COLLEGE if key in campagne.COLLEGES else campagne.XP_EXTRA} XP')
        st['afgevinkt'] = af
        bewaar(st)
    elif actie == 'limiet':
        s = campagne.bereken(mw.col, cfg(), st)
        campagne.zet_limiet(mw.col, cfg(), s['doel_nieuw'])
        st['limiet'] = s['vandaag'].isoformat()
        bewaar(st)
        tooltip(f'Vandaag staan er {s["doel_nieuw"]} nieuwe kaarten voor je klaar.')
    elif actie == 'volgorde':
        if askUser('Alle opgeschorte GZC III-kaarten vrijgeven en alle nieuwe kaarten op volgorde van de campagne zetten?\n\n'
                   'Opschorten per thema is dan niet meer nodig: de volgorde zorgt dat je elk thema op het juiste moment krijgt.\n\n'
                   'Per thema in de volgorde van het plan (T3 → T1 → T2 → T4 → B1 → B2 → B3), en binnen een thema eerst de gewone kaarten, '
                   'daarna de casus-, schema- en tabelkaarten. Kaarten die je al geleerd hebt, veranderen niet.'):
            n = campagne.campagnevolgorde(mw.col, cfg())
            st['volgorde'] = campagne.dt.date.today().isoformat()
            bewaar(st)
            tooltip(f'{n} nieuwe kaarten op campagnevolgorde gezet.')
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
