"""Test van de campagne-add-on buiten Anki: lege collectie → drie imports → koppeling → slot → herhalen → weergave.

Gebruik: python3 test_campagne.py <uitvoermap>
Vereist het pakket `anki` (pip install anki==26.5). Schrijft hoofdscherm.html, college.html en hud.html naar de uitvoermap.
"""
import json
import os
import pathlib
import sys
import tempfile
import types

import anki.collection  # noqa: F401  (laadt het pakket in de juiste volgorde)
from anki.collection import Collection, CsvMetadata, ImportCsvRequest
from anki.scheduler.v3 import CardAnswer

HIER = pathlib.Path(__file__).resolve().parent
ADDON = HIER / 'campagne-addon'
UIT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp())
UIT.mkdir(parents=True, exist_ok=True)

# de add-on als pakket laden zonder __init__.py (die heeft aqt nodig)
pkg = types.ModuleType('gzc3')
pkg.__path__ = [str(ADDON)]
sys.modules['gzc3'] = pkg
from gzc3 import campagne, scherm  # noqa: E402

CFG = dict(deck='GZC III - Compleet', examen='2026-10-29', leerdeadline='2026-10-22', reeks_drempel=30,
           eindfase_herhalingen=150, meldingen=True, hud=True, herkansing_dagen=2)
NOTETYPE_ID = 1706371006450


def maak_collectie():
    pad = os.path.join(tempfile.mkdtemp(), 'test.anki2')
    col = Collection(pad)
    nt = col.models.new('Basic')
    for veld in ('Front', 'Back'):
        col.models.add_field(nt, col.models.new_field(veld))
    t = col.models.new_template('Card 1')
    t['qfmt'], t['afmt'] = '{{Front}}', '{{FrontSide}}<hr id=answer>{{Back}}'
    col.models.add_template(nt, t)
    oud = col.models.add_dict(nt).id
    for tabel, kolom in (('notetypes', 'id'), ('fields', 'ntid'), ('templates', 'ntid')):
        col.db.execute(f'update {tabel} set {kolom} = ? where {kolom} = ?', NOTETYPE_ID, oud)
    col.close()
    col = Collection(pad)
    did = col.decks.id(CFG['deck'])
    conf = col.decks.config_dict_for_deck_id(did)
    conf['new']['perDay'] = 9999
    col.decks.update_config(conf)
    col.decks.select(did)
    return col


def importeer(col, naam):
    p = str(ADDON / 'data' / naam)
    md = col.get_csv_metadata(path=p, delimiter=None)
    md.dupe_resolution = CsvMetadata.DupeResolution.UPDATE
    log = col.import_csv(ImportCsvRequest(path=p, metadata=md)).log
    fout = len(log.missing_notetype) + len(log.missing_deck) + len(log.conflicting)
    print(f'  {naam}: {len(log.new)} nieuw, {len(log.updated)} bijgewerkt, {fout} fout')
    assert fout == 0
    return log


def beantwoord(col, n, patroon):
    """Beantwoord n kaarten uit de wachtrij; patroon(i) geeft de rating."""
    for i in range(n):
        qc = col.sched.get_queued_cards(fetch_limit=1)
        if not qc.cards:
            return i
        q = qc.cards[0]
        card = col.get_card(q.card.id)
        card.start_timer()
        col.sched.answer_card(col.sched.build_answer(card=card, states=q.states, rating=patroon(i)))
    return n


def main():
    col = maak_collectie()
    st = {}
    stappen = campagne.installatie(col, CFG, st)
    assert [s['klaar'] for s in stappen] == [False] * 6 and stappen[0]['kan'] and not stappen[1]['kan'], stappen
    print('imports:')
    importeer(col, 'GZC3_check_import.txt')
    importeer(col, 'GZC3_extra_import.txt')
    log = importeer(col, 'GZC3_colleges_import.txt')
    assert len(log.new) == 181 and len(log.updated) == 5, (len(log.new), len(log.updated))
    mcv = col.get_note(col.find_notes('"Hoe classificeer je anemie morfologisch*"')[0])
    assert '82-98 fl' in mcv['Back'], mcv['Back']

    stappen = {s['id']: s for s in campagne.installatie(col, CFG, st)}
    assert stappen['check']['klaar'] and stappen['extra']['klaar'] and stappen['colleges']['klaar']
    assert not stappen['opruimen']['klaar'] and stappen['opruimen']['kan'] and '93' in stappen['opruimen']['knop'], stappen['opruimen']
    col.remove_notes(col.find_notes('tag:check::dubbel OR tag:check::verwijderen'))
    assert campagne.installatie(col, CFG, st)[3]['klaar']

    n = campagne.koppel(col)
    print('koppeling:', n, 'notities getagd')
    assert n == 412, n
    assert campagne.koppel(col) == 0, 'tweede keer koppelen moet niets meer doen'
    for k, verwacht in (('HC1', 18 + 33), ('HC3', 57 + 47), ('HC4', 70 + 35), ('HC5', 19 + 30)):
        gevonden = len(col.find_notes(f'tag:college::{k}'))
        assert gevonden == verwacht, (k, gevonden, verwacht)
    # een afwijkende college-tag wordt rechtgezet
    nid = col.find_notes('tag:college::HC1')[0]
    col.tags.bulk_remove([nid], 'college::HC1')
    col.tags.bulk_add([nid], 'college::HC9')
    assert campagne.koppel(col) == 1 and 'college::HC9' not in col.get_note(nid).tags

    s = campagne.bereken(col, CFG, st)
    print('per college (nieuw):', {k: s['per_college'][k]['n'] for k in ('HC1', 'HC2', 'HC3', 'HC4', 'HC5', 'HC6', 'HC7', 'HC11')})
    totaal = s['totaal']['n']

    st['slot'] = True
    campagne.campagne_starten(col, CFG, {})
    opgeschort = len(col.find_cards('is:suspended'))
    zonder_thema = sum(1 for (tags,) in col.db.all('select tags from notes') if not campagne.thema_van(tags.split()))
    print('slot aan:', opgeschort, 'van', totaal, 'kaarten op slot ·', zonder_thema, 'notities zonder thema')
    assert opgeschort == totaal - zonder_thema, 'zonder afgevinkte colleges moet alles met een thema op slot'
    st['afgevinkt'] = {'HC1': '2026-10-06', 'HC2': '2026-10-06'}
    vrij = campagne.vergrendel(col, CFG, st['afgevinkt'])
    print('HC1 + HC2 afgevinkt:', vrij, 'kaarten vrijgespeeld')
    assert vrij == len(col.find_cards('tag:college::HC1 OR tag:college::HC2'))
    eerste = col.get_card(col.sched.get_queued_cards(fetch_limit=1).cards[0].card.id)
    assert 'college::HC1' in eerste.note().tags, 'HC1-kaarten horen vooraan te staan'

    # herhalen: 60 goed op rij, dan een paar fout
    goed = beantwoord(col, 60, lambda i: CardAnswer.GOOD)
    fout = beantwoord(col, 6, lambda i: CardAnswer.AGAIN)
    print(f'beantwoord: {goed} goed, {fout} fout')
    snel = campagne.snel(col, CFG, st)
    s = campagne.bereken(col, CFG, st)
    print(f'xp {s["xp"]} (combo-bonus {s["xp_combo"]}, kritiek {s["kritieken"]}) · level {s["level"]} {s["titel"]} · '
          f'beste combo {s["combo_record"]} · combo nu {s["combo"]} · fout recent {s["fout_recent"]}')
    assert s['combo_record'] == 60 and s['combo'] == 0
    assert s['xp_combo'] == sum(campagne.combo_bonus(i) for i in range(1, 61))
    rid = col.db.scalar('select max(id) from revlog')
    info = campagne.antwoord_xp(col, col.db.scalar('select cid from revlog where id = ?', rid), 1, 0)
    assert info['xp'] in (1, 4), info
    assert s['colleges']['HC1']['sterren'] >= 1 and snel['bazen']['T1']['hp'] < 100

    did, n = campagne.herkansing(col, CFG)
    assert n == fout and did, (did, n)
    assert col.decks.name(did) == campagne.HERKANSING
    assert campagne.herkansing(col, CFG, 'HC1') == (0, 0), 'alle HC1-kaarten waren goed'
    did2, n2 = campagne.herkansing(col, CFG, 'HC2')  # tweede keer: zelfde deck, opnieuw gevuld
    assert did2 == did and n2 == fout, (did, did2, n2)
    print('herkansing:', n, 'kaarten in', campagne.HERKANSING)

    # weergave
    s = campagne.bereken(col, CFG, st)
    stappen = campagne.installatie(col, CFG, st)
    st['quiz'] = {'HC1': 4}
    s = campagne.bereken(col, CFG, st)
    assert s['quiz'] == {'HC1': 4}
    pagina = scherm.weergave(s, stappen)
    for licht in (True, False):
        (UIT / f'hoofdscherm{"" if licht else "-donker"}.html').write_text(
            f'<!doctype html><html class="{"" if licht else "night-mode"}"><head><meta charset="utf-8"></head>'
            f'<body style="background:{"#f5f3f7" if licht else "#2c2c2c"};margin:0;padding:1px">'
            f'<script>function pycmd(c){{document.title=c}}</script>{pagina}</body></html>', encoding='utf-8')
    for k in ('HC3', 'HC9'):
        body = scherm.dialoog(s, k)
        (UIT / f'college-{k}.html').write_text(
            f'<!doctype html><html><head><meta charset="utf-8"></head><body><script>function pycmd(c){{document.title=c}}</script>{body}</body></html>',
            encoding='utf-8')
    hud = scherm.hud_data(campagne.snel(col, CFG, st), 'T1', 'HC3')
    (UIT / 'hud.html').write_text(
        f'<!doctype html><html><head><meta charset="utf-8"></head><body style="font:20px serif;padding:60px">'
        f'<div id="qa">Wat is de beenmergniche?</div><script>{scherm.HUD_JS}gzc3hud({json.dumps(dict(hud, combo=12))});'
        f'gzc3pop("+2 XP","",0);gzc3pop("⚡ Combo 10! Nu ×2 XP","combo",300);gzc3pop("💥 Kritieke treffer! +10 XP","krit",600);</script></body></html>',
        encoding='utf-8')
    print('weergave geschreven naar', UIT)
    col.close()
    print('ALLES OK')


if __name__ == '__main__':
    main()
