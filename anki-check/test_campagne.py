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
    assert [s['id'] for s in stappen] == ['check', 'extra', 'colleges'] + ['beelden'] * bool(campagne.BEELDEN.get('beelden')) + ['opruimen', 'fsrs', 'campagne']
    assert not any(s['klaar'] for s in stappen) and stappen[0]['kan'] and not stappen[1]['kan'], stappen
    print('imports:')
    importeer(col, 'GZC3_check_import.txt')
    importeer(col, 'GZC3_extra_import.txt')
    bestaand = {r.split('\t', 1)[0] for naam in ('GZC3_check_import.txt', 'GZC3_extra_import.txt')
                for r in (ADDON / 'data' / naam).read_text(encoding='utf-8').splitlines() if not r.startswith('#')}
    rijen = [r.split('\t') for r in (ADDON / 'data' / 'GZC3_colleges_import.txt').read_text(encoding='utf-8').splitlines() if not r.startswith('#')]
    log = importeer(col, 'GZC3_colleges_import.txt')
    pad_b = ADDON / 'data' / 'GZC3_beelden_import.txt'
    beeldrijen = [r.split('\t') for r in pad_b.read_text(encoding='utf-8').splitlines() if not r.startswith('#')] if pad_b.exists() else []
    verwacht_nieuw = sum(r[0] not in bestaand for r in rijen)
    assert len(log.new) == verwacht_nieuw and len(log.updated) == len(rijen) - verwacht_nieuw, (len(log.new), len(log.updated))
    mcv = col.get_note(col.find_notes('"Hoe classificeer je anemie morfologisch*"')[0])
    assert '82-98 fl' in mcv['Back'], mcv['Back']
    assert campagne.IMPORT_GUIDS and campagne.installatie(col, CFG, {})[2]['klaar'], 'collegeimport moet als binnen gelden'

    stappen = {s['id']: s for s in campagne.installatie(col, CFG, st)}
    assert stappen['check']['klaar'] and stappen['extra']['klaar'] and stappen['colleges']['klaar']
    assert not stappen['opruimen']['klaar'] and stappen['opruimen']['kan'] and '93' in stappen['opruimen']['knop'], stappen['opruimen']
    col.remove_notes(col.find_notes('tag:check::dubbel OR tag:check::verwijderen'))
    assert {s['id']: s for s in campagne.installatie(col, CFG, st)}['opruimen']['klaar']

    # afbeeldingen: mediabestanden, achterkant van bestaande kaarten, herkenkaarten, verkeerde webafbeelding weg
    B = campagne.BEELDEN
    if B.get('beelden'):
        assert campagne.beelden_stand(col) == (False, True) and stappen['beelden']['kan']
        n = campagne.beelden_toepassen(col)
        importeer(col, 'GZC3_beelden_import.txt')
        assert campagne.beelden_stand(col) == (True, True), 'na toepassen moet de stap klaar zijn'
        assert campagne.beelden_toepassen(col) == 0, 'tweede keer toepassen moet niets doen'
        assert all(col.media.have(b['bestand']) for b in B['beelden'])
        for b in B['beelden']:
            for g in b['guids']:
                nid = col.db.scalar('select id from notes where guid = ?', g)
                assert nid and f'src="{b["bestand"]}"' in col.get_note(nid).fields[1], (g, b['bestand'])
        for g, srcs in B['weg'].items():
            nid = col.db.scalar('select id from notes where guid = ?', g)
            assert not nid or not any(x in col.get_note(nid).fields[1] for x in srcs), g
        print(f'afbeeldingen: {len(B["beelden"])} bestanden, {n} kaarten aangepast, {len(B["herken_guids"])} herkenkaarten')
    assert 'kinderneurologie' not in col.get_note(col.find_notes('"Hoe classificeer je anemie morfologisch*"')[0]).fields[1]

    # noodpakket: apart deck, telt niet mee in de campagne
    totaal_voor = campagne.bereken(col, CFG, st)['totaal']['n']
    assert campagne.nood_stand(col) is None
    if campagne.NOOD.get('guids'):
        did = campagne.nood_instellen(col)
        importeer(col, 'GZC3_nood_import.txt')
        nd = campagne.nood_stand(col)
        assert nd['did'] == did and nd['per']['totaal']['n'] == len(campagne.NOOD['guids']), nd
        assert col.decks.config_dict_for_deck_id(did)['new']['perDay'] == 60
        assert campagne.bereken(col, CFG, st)['totaal']['n'] == totaal_voor, 'noodpakket mag niet meetellen in de campagne'
        assert not col.find_notes(f'deck:"{campagne.NOOD_DECK}" tag:GZC3::A::*'), 'noodkaarten horen geen themataak van de campagne te hebben'
        print('noodpakket:', {k: v['n'] for k, v in nd['per'].items()})

    n = campagne.koppel(col)
    print('koppeling:', n, 'notities getagd ·', len(campagne.KOPPELING), 'in de koppeling ·', len(campagne.EXTRA_TAGS), 'met nadruk van de docent')
    assert n >= len(campagne.KOPPELING) - 1, n
    assert campagne.koppel(col) == 0, 'tweede keer koppelen moet niets meer doen'
    guid_tags = {g: set(t.lower().split()) for g, t in col.db.all('select guid, tags from notes')}
    for g, k in campagne.KOPPELING.items():
        assert f'college::{k}'.lower() in guid_tags[g], (g, k)
    for g, tags in campagne.EXTRA_TAGS.items():
        assert all(t.lower() in guid_tags[g] for t in tags), g
    for k in ('HC1', 'HC3', 'HC4', 'HC5', 'HC7', 'HC13'):
        verwacht = ({g for g, c in campagne.KOPPELING.items() if c == k} | {r[0] for r in rijen if f'college::{k}' in r[5].split()}
                    | {r[0] for r in beeldrijen if f'college::{k}' in r[5].split()})
        gevonden = len(col.find_notes(f'tag:college::{k}'))
        assert gevonden == len(verwacht), (k, gevonden, len(verwacht))
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
    zonder_thema = sum(1 for (tags,) in col.db.all('select n.tags from notes n where n.id in (select nid from cards where did in ({}))'.format(
        ','.join(map(str, campagne.deck_ids(col, CFG['deck']))))) if not campagne.thema_van(tags.split()))
    assert not col.find_cards(f'deck:"{campagne.NOOD_DECK}" is:suspended'), 'het slot van de campagne mag het noodpakket niet raken'
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
    assert campagne.herkansing(col, CFG, 'HC31') == (0, 0), 'HC31 is nog niet geleerd'
    fout_college = next(t[9:] for t in col.get_note(col.get_card(col.find_cards('rated:2:1')[0]).nid).tags if t.startswith('college::'))
    did2, n2 = campagne.herkansing(col, CFG, fout_college)  # tweede keer: zelfde deck, opnieuw gevuld
    assert did2 == did and 0 < n2 <= fout, (did, did2, n2)
    print('herkansing:', n, 'kaarten in', campagne.HERKANSING)

    # lastige kaarten: fout, opgezocht met W, rode vlag
    g_zoek = col.db.scalar('select guid from notes where id = ?', eerste.nid)
    col.set_config(campagne.OPGEZOCHT_KEY, {g_zoek: 2})
    cid_vlag = col.find_cards(f'deck:"{CFG["deck"]}" -is:new')[1]
    col.set_user_flag_for_cards(1, [cid_vlag])
    lastig = campagne.lastige_kaarten(col, CFG)
    gl = {r['guid']: r for r in lastig}
    assert g_zoek in gl and gl[g_zoek]['opgezocht'] == 2, lastig[:3]
    g_vlag = col.db.scalar('select n.guid from cards c join notes n on n.id = c.nid where c.id = ?', cid_vlag)
    assert g_vlag in gl and gl[g_vlag]['rood'], 'rode vlag hoort lastig te maken'
    prompt = campagne.lastig_prompt(lastig)
    assert '#guid column:1' in prompt and g_zoek in prompt and '1706371006450' in prompt
    print('lastige kaarten:', len(lastig))

    # weergave
    s = campagne.bereken(col, CFG, st)
    assert s['n_lastig'] == len(lastig) and len(s['lastig']) <= 5
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
    assert 'Lastige kaarten' in pagina and (not campagne.NOOD.get('guids') or 'Noodpakket' in pagina)
    (UIT / 'nood.html').write_text(f'<!doctype html><html><head><meta charset="utf-8"></head><body>{scherm.nood_dialoog(s)}</body></html>', encoding='utf-8')
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
