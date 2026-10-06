"""Campagne GZC III — rekenwerk en acties. Gebruikt alleen `anki` en de standaardbibliotheek,
zodat het buiten Anki te testen is. De weergave staat in scherm.py, de koppeling met Anki in __init__.py.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import math
import pathlib
import re
from collections import Counter, defaultdict

DATA = pathlib.Path(__file__).resolve().parent / 'data'


def _laad(naam: str, standaard):
    try:
        return json.loads((DATA / naam).read_text(encoding='utf-8'))
    except Exception:
        return standaard


COLLEGEDATA = _laad('colleges.json', {})  # kapstok, controlevragen en verzamelcel per college
KOPPELING = _laad('koppeling.json', {})  # guid → college, met de hand ingedeeld op basis van de slides
BRON_TAG = 'bron::slides-HC1-5'
HERKANSING = 'GZC III - Herkansing'

# ------------------------------------------------------------------ inhoud van de campagne
THEMAS = {
    'T1': ('Benigne hematologie', 'De Hepcidinehydra', '🩸'),
    'T2': ('Maligne hematologie', 'Koning Blast', '👑'),
    'T3': ('Kind, AYA, geriatrie', 'De Kleine Kwaal', '🧸'),
    'T4': ('Hoofd-hals, schildklier, oog', 'De Halskliergolem', '🗿'),
    'B1': ('Public health', 'De Bureaucraat', '📋'),
    'B2': ('Revalidatie, psychosociaal', 'De Copingcolossus', '🧠'),
    'B3': ('Pijn en palliatieve zorg', 'De Pijnfeniks', '🔥'),
}
ZIEKTE_THEMA = {  # ziektebeeldenset heeft geen thematag
    'anemie': 'T1', 'neuroblastoom': 'T3', 'nefroblastoom': 'T3', 'osteosarcoom': 'T3',
    'ewing': 'T3', 'rhabdomyosarcoom': 'T3',
    'HH': 'T4', 'mondholte': 'T4', 'nasofarynx': 'T4', 'orofarynx': 'T4', 'hypofarynx': 'T4',
    'larynx': 'T4', 'sinonasale': 'T4', 'pleiomorf': 'T4', 'warthin': 'T4', 'speekselklier': 'T4',
    'paraganglioom': 'T4', 'schildkliernodus': 'T4', 'PTC': 'T4', 'MTC': 'T4', 'ATC': 'T4',
    'niet-toxisch': 'T4', 'toxisch': 'T4', 'retinoblastoom': 'T4', 'uveamelanoom': 'T4',
    'orbita': 'T4', 'traanklier': 'T4', 'ooglid': 'T4',
}
COLLEGES = {  # 32 hoorcolleges uit het blokboek
    'HC1': ('T1', 'HC 1 Hematopoëse'), 'HC2': ('T1', 'HC 2 Erytropoëse en zuurstofvoorziening'),
    'HC3': ('T1', 'HC 3 Anemie'), 'HC4': ('T1', 'HC 4 Stolling'),
    'HC5': ('T2', 'HC 5 Introductie hematologische maligniteiten'), 'HC6': ('T2', 'HC 6 MPN en CML'),
    'HC7': ('T2', 'HC 7 Maligne lymfoom en CLL'), 'HC8': ('T2', 'HC 8 Multipel myeloom'),
    'HC9': ('T2', 'HC 9 AML en MDS'), 'HC10': ('T2', 'HC 10 Pathologie maligne hematologie'),
    'HC11': ('T3', 'HC 11 Kinderoncologie'), 'HC12': ('T3', 'HC 12 AYA'),
    'HC13': ('T3', 'HC 13 Geriatrische oncologie'), 'HCAI': ('T3', 'HC Kunstmatige intelligentie'),
    'HC14': ('T4', 'HC 14 Hoofd-halstumoren: etiologie en diagnostiek'), 'HC15': ('T4', 'HC 15 Behandeling hoofd-halstumoren'),
    'HC16': ('T4', 'HC 16 Pathologie hoofd-halstumoren'), 'HC17': ('T4', 'HC 17 Schildkliertumoren'),
    'HC18': ('T4', 'HC 18 Oogheelkunde'), 'HC19': ('T4', 'HC 19 Farynx, larynx, nasofarynx, speekselklieren'),
    'PH1': ('B1', 'HC Introductie public health'), 'PH2': ('B1', 'HC Bevolkingsonderzoeken naar kanker'),
    'PH3': ('B1', 'HC Nationaal beleid gezondheidszorg'), 'PH4': ('B1', 'HC Verzekeraar en goede zorg'),
    'PH5': ('B1', 'HC Kanker in de huisartsenpraktijk'), 'PH6': ('B1', 'HC Diversiteit in de zorg'),
    'PH7': ('B1', 'HC Bedrijfsgeneeskunde'), 'PH8': ('B1', 'HC UWV en verzekeringsgeneeskunde'),
    'HC28': ('B2', 'HC 28 Introductie revalidatiegeneeskunde'), 'HC29': ('B2', 'HC 29 Psychosociale problematiek'),
    'HC30': ('B3', 'HC 30 Palliatieve zorg'), 'HC31': ('B3', 'HC 31 Pijn'),
}
EXTRA = {  # overige toetsstof en oude tentamens
    'AYA': ('T3', 'E-module AYA (wordt getoetst)'),
    'RT': ('T4', 'Bijlage Radiotherapie hoofd/hals'),
    'JP': ('B2', 'Bijlage Kanker: een existentiële opgave'),
    'HW': ('B2', 'Bijlage Signaleren van distress'),
    'OT1': (None, 'Oud tentamen: proeftentamen GZC III'),
    'OT2': (None, 'Oud tentamen: proeftentamen hemato-oncologie'),
    'OT3': (None, 'Oud tentamen: proeftentamen 2006'),
    'OT4': (None, 'Oud tentamen: tentamen 2010'),
    'OT5': (None, 'Oud tentamen: oefentoets 8 mei 2019'),
    'OT6': (None, 'Oud tentamen: tentamen 10 mei'),
}
PLAN = [  # (datum, hoofdspoor-thema, items). Hoofdspoor: T1 → T2 inhalen. Bijspoor: live colleges van de groep (T3).
    ('2026-10-06', 'T1', ['HC1', 'HC2', 'HC11']), ('2026-10-07', 'T1', ['HC3', 'HC5']), ('2026-10-08', 'T1', ['HC4', 'AYA']),
    ('2026-10-09', 'T2', ['HC6', 'HC12']), ('2026-10-10', 'T2', ['HC7']), ('2026-10-11', 'T2', ['HC8', 'HC13']),
    ('2026-10-12', 'T2', ['HC9', 'HCAI']), ('2026-10-13', 'T2', ['HC10']),
    ('2026-10-14', 'T4', ['HC14', 'HC15']), ('2026-10-15', 'T4', ['HC16', 'HC17', 'RT']), ('2026-10-16', 'T4', ['HC18', 'HC19']),
    ('2026-10-17', 'B1', ['PH1', 'PH2', 'PH3', 'PH4']), ('2026-10-18', 'B1', ['PH5', 'PH6', 'PH7', 'PH8']),
    ('2026-10-19', 'B2', ['HC28', 'HC29', 'JP', 'HW']), ('2026-10-20', 'B3', ['HC30', 'HC31']),
    ('2026-10-21', None, []), ('2026-10-22', None, []),
    ('2026-10-23', None, ['OT1']), ('2026-10-24', None, ['OT2']), ('2026-10-25', None, ['OT3']),
    ('2026-10-26', None, ['OT4']), ('2026-10-27', None, ['OT5']), ('2026-10-28', None, ['OT6']),
]
CAMPAGNE_VOLGORDE = ['T1', 'T2', 'T3', 'T4', 'B1', 'B2', 'B3']  # volgorde van de eindbazen
COLLEGE_VOLGORDE = [k for _, _, items in PLAN for k in items if k in COLLEGES]  # volgorde van nieuwe kaarten

# Welke kaart hoort bij welk college. Een tag college::HC3 op de notitie wint altijd (de add-on zet die tags voor alle
# T1/T2-kaarten op basis van de slides); anders deze trefwoorden (eerste treffer telt), anders het eerste college van het thema.
TREFWOORDEN = {
    'T1': [('HC4', r'stoll|hemofil|willebrand|trombocyt|trombo|plaatj|hemosta|aptt|\bpt\b|inr|fibrin|antistol|heparine|vka|doac|dis\b|itp|ttp|glanzmann|soulier|virchow|factor (v|x|ix|xi|xii|xiii|vii)'),
           ('HC3', r'anemie|anaemie|thalass|sikkel|hemoly|b12|folium|mcv|mchc|ferritin|sferocyt|g6pd|aplast|hemoglobinopath|retic|coombs|antiglobuline|hemochromat|brissot'),
           ('HC2', r'erytro|erythro|\bepo\b|ijzer|hepcidin|ferroport|transferr|\bhif\b|zuurstof|2,3-dpg|erythroferron|reticulocyt')],
    'T2': [('HC8', r'myeloom|mgus|waldenstr|amylo|m-prote|m-comp|plasmac|bence|crab|lichte keten|immunoglobul|hypercalc|smoulder'),
           ('HC9', r'\baml\b|\bmds\b|myelodysplas|acute (myelo|leuk)|\ball\b|leukostase|7\+3|auer|blast|promyelo|apl\b|tumorlysis|febriele|neutropen|flt3|npm1|azacitidine|venetoclax'),
           ('HC6', r'\bcml\b|polycyt|\bpv\b|\bet\b|trombocytose|myelofibrose|mpn|jak2|bcr-abl|philadelphia|imatinib|tki|calr|ruxolitinib'),
           ('HC10', r'reed-sternberg|lacunaire|popcorn|lymfo-epitheliale|starry|epidermotrop|histolog|morfolog'),
           ('HC7', r'lymfoom|hodgkin|\bcll\b|burkitt|malt|mantel|hairy|mycosis|s.zary|richter|folliculair|dlbcl|grootcellig|\bipi\b|flipi|ann arbor|lymfocytose|lymfadenopath|t-cel')],
    'T3': [('HC12', r'\baya|jongvolwassen|adolescent|fertiliteit'),
           ('HC13', r'geriatr|ouderen|oudere|cga|\bg8\b|kwetsba|karnofsky')],
    'T4': [('HC18', r'oog|retinoblast|uvea|choro|orbita|ooglid|traanklier|leukocorie|salmon|chalazion'),
           ('HC17', r'schildkl|thyre|struma|calciton|men2|\bret\b|bethesda|nodus|papillair|medullair|anaplast|h.rthle'),
           ('HC16', r'patholog|histolog|dysplas|p16|e6|e7|marge|perineura|infiltrat|groeipatroon|arrosie|keratin|desmosom|plaveiselcelcarcinoom zien'),
           ('HC19', r'speeksel|parotis|pleiomorf|warthin|frey|nasofar|larynx|laryng|farynx|stemband|heesheid|glottis|supraglott|hypofar|sinonasa|paraganglio'),
           ('HC14', r'risicofactor|symptom|diagnost|zwelling|\bdd\b|echo|punctie|scopie|otalgie|tnm|level|lymfeklierstation|draine|tweede (primaire )?tumor|field|incidentie|leukoplak|erytroplak|hpv|roken|alcohol|subsite|anatom'),
           ('HC15', r'behandel|radiother|bestral|halsklierdissectie|chemoradiat|cetuximab|fluor|laryngectomie|reconstruct')],
    'B1': [('PH8', r'uwv|verzekeringsarts|wia|iva|wga|ziektewet|risque|poortwachter'),
           ('PH7', r'bedrijfsarts|arbeid|werkgever|verzuim|beroepsziek|inzetbaar|belasting-belastbaar|biopsychosoc'),
           ('PH6', r'migra|etnic|cultu|diversit|healthy migrant|salmon effect|convergentie|niet-weten|tolk'),
           ('PH5', r'huisarts|poortwachter|voorafkans|chronische aard|vermijdbaar'),
           ('PH2', r'bevolkingsonderzoek|screening|sensitiv|specific|voorspellende|overdiagnost|lead time|wilson|wbo'),
           ('PH4', r'verzekeraar|naturapolis|restitutie|eigen risico|eigen bijdrage|dbc|dot\b'),
           ('PH3', r'zvw|wlz|wmo|wpg|jeugdwet|wgbo|wkkgz|wet big|financier|echelon|evidence|zorginstituut')],
    'B2': [('HC29', r'coping|psychosoc|existenti|trauma|distress|lastmeter|depress|angst|empathie|2legs|positieve gezondheid|naasten|mantelzorg|levensfase')],
    'B3': [('HC31', r'pijn|opio|morfine|ladder|neuropath|nocicept|chordotom|plexus|zadelblok|intrathec|allodyn|nmda|doorbraak|loeser|unmasking')],
}
EERSTE_COLLEGE = {'T1': 'HC1', 'T2': 'HC5', 'T3': 'HC11', 'T4': 'HC14', 'B1': 'PH1', 'B2': 'HC28', 'B3': 'HC30'}
ZIEKTE_COLLEGE = {'anemie': 'HC3', 'ALL': 'HC9', 'AML': 'HC9', 'MDS': 'HC9', 'CML': 'HC6', 'PV': 'HC6', 'ET': 'HC6',
                  'myelofibrose': 'HC6', 'multipel-myeloom': 'HC8', 'MGUS': 'HC8', 'AL-amyloidose': 'HC8', 'waldenstrom': 'HC8'}


def college_van(tags: list[str], tekst: str) -> str | None:
    for t in tags:
        if t.lower().startswith('college::'):
            k = t[9:].upper()
            if k in COLLEGES:
                return k
    th = thema_van(tags)
    if not th:
        return None
    for t in tags:
        if t.startswith('GZC3::ZIEKTE::'):
            z = t.split('::')[2]
            if z in ZIEKTE_COLLEGE:
                return ZIEKTE_COLLEGE[z]
    tekst = tekst.lower()
    for col_id, patroon in TREFWOORDEN.get(th, []):
        if re.search(patroon, tekst):
            return col_id
    return EERSTE_COLLEGE[th]


def platte_tekst(flds: str) -> str:
    flds = re.sub(r'<svg.*?</svg>', ' ', flds, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', ' ', flds.replace('\x1f', ' ')))


_COLLEGE_CACHE: dict[int, tuple[int, str | None]] = {}  # nid → (mod, college): de regexen hoeven maar één keer


def college_van_notitie(nid: int, mod: int, tags: str, flds: str) -> str | None:
    hit = _COLLEGE_CACHE.get(nid)
    if hit and hit[0] == mod:
        return hit[1]
    cl = college_van(tags.split(), platte_tekst(flds))
    _COLLEGE_CACHE[nid] = (mod, cl)
    return cl


TITELS = ['Nieuweling', 'Pipetteur', 'Uitstrijkjesmaker', 'Bloedbeeldlezer', 'Stollingsdetective',
          'IJzerjager', 'Lymfoomspeurder', 'Myeloomtemmer', 'Blastenbestrijder', 'Kinderoncoloog i.o.',
          'Halsklierkenner', 'Schildklierfluisteraar', 'Poortwachter', 'Palliatief expert', 'Tentamenbeest']

XP_COLLEGE, XP_EXTRA, XP_QUIZVRAAG, XP_KRITIEK = 50, 75, 10, 10
VERANKERD_IVL = 7  # dagen
COMBO_PAUZE_MS = 30 * 60 * 1000  # langer dan een half uur niets gedaan: nieuwe sessie, combo begint opnieuw


def xp_drempel(n: int) -> int:
    """Totale XP nodig voor level n (level 1 = 0)."""
    return int(150 * (n - 1) ** 1.7)


def level_van(xp: int) -> tuple[int, str, int, int]:
    n = 1
    while xp >= xp_drempel(n + 1):
        n += 1
    titel = TITELS[min(n, len(TITELS)) - 1] + (f' ★{n - len(TITELS)}' if n > len(TITELS) else '')
    return n, titel, xp_drempel(n), xp_drempel(n + 1)


def kritiek(rid: int) -> bool:
    """Ongeveer 1 op de 20 goede antwoorden is een kritieke treffer. Vast per revlog-id, dus altijd hetzelfde uitgerekend."""
    return (rid * 2654435761) % 4294967296 % 20 == 0


def combo_bonus(combo: int) -> int:
    return 2 if combo >= 25 else (1 if combo >= 10 else 0)


def thema_van(tags: list[str]) -> str | None:
    for t in sorted(tags, key=lambda t: not t.startswith('GZC3::B::')):  # B-tag wint als beide er zijn (bv. Lalonde)
        m = re.match(r'GZC3::[AB]::([TB]\d)', t)
        if m:
            return m.group(1)
    for t in tags:
        if t.startswith('GZC3::ZIEKTE::'):
            z = t.split('::')[2]
            for k, v in ZIEKTE_THEMA.items():
                if z.startswith(k):
                    return v
            return 'T2'
    return None


def label(k: str) -> str:
    return (COLLEGES.get(k) or EXTRA.get(k) or (None, k))[1]


def kort(k: str) -> str:
    """'HC3' → '3', 'PH2' → 'P2', 'HCAI' → 'AI'."""
    if k.startswith('HC'):
        return k[2:]
    if k.startswith('PH'):
        return 'P' + k[2:]
    return k


def sterren(pc: Counter, af: bool) -> int:
    """★ college afgevinkt · ★★ alle kaarten gezien · ★★★ 70% verankerd. Zonder kaarten: drie sterren bij afvinken."""
    if not pc or not pc['n']:
        return 3 if af else 0
    return int(af) + int(pc['nieuw'] == 0) + int(pc['verankerd'] / pc['n'] >= 0.7)


def cel_behaald(pc: Counter, af: bool) -> bool:
    return (pc['nieuw'] == 0) if pc and pc['n'] else af


# ------------------------------------------------------------------ status
def deck_ids(col, decknaam: str) -> list[int]:
    did = col.decks.id_for_name(decknaam)
    return list(col.decks.deck_and_child_ids(did)) if did else []


def bereken(col, cfg: dict, staat: dict) -> dict | None:
    dids = deck_ids(col, cfg['deck'])
    if not dids:
        return None
    ids = ','.join(map(str, dids))
    cutoff = col.sched.day_cutoff
    vandaag = dt.date.fromtimestamp(cutoff - 86400)
    examen = dt.date.fromisoformat(cfg['examen'])
    deadline = dt.date.fromisoformat(cfg['leerdeadline'])
    afgevinkt = staat.get('afgevinkt', {})

    kaarten = col.db.all(f'select c.id, c.nid, n.mod, n.tags, c.queue, c.ivl, c.type, n.flds from cards c join notes n on c.nid = n.id '
                         f'where (c.did in ({ids}) or c.odid in ({ids}))')
    per = {k: Counter() for k in THEMAS}
    totaal = Counter()
    per_college = defaultdict(Counter)
    thema_van_cid, college_van_cid = {}, {}
    for cid, nid, mod, tags, queue, ivl, ctype, flds in kaarten:
        th = thema_van(tags.split())
        cl = college_van_notitie(nid, mod, tags, flds) if th else None
        thema_van_cid[cid], college_van_cid[cid] = th, cl
        if ctype == 0 and queue != -1:
            totaal['beschikbaar'] += 1
        rij = [totaal] + ([per[th]] if th else []) + ([per_college[cl]] if cl else [])
        for c in rij:
            c['n'] += 1
            if ctype != 0:
                c['gezien'] += 1
            if ctype == 2 and ivl >= VERANKERD_IVL:
                c['verankerd'] += 1
            if ctype == 0:
                c['nieuw'] += 1
                c['open'] += queue != -1
            if queue == -1:
                c['opgeschort'] += 1

    log = col.db.all(f'select r.id, r.cid, r.ease, r.type from revlog r where r.cid in '
                     f'(select id from cards where did in ({ids}) or odid in ({ids})) and r.type < 4 and r.ease > 0 order by r.id')
    dag = lambda rid: (cutoff * 1000 - rid - 1) // 86400000  # 0 = vandaag
    xp_kaarten, eerste = 0, {}
    per_dag, goed_dag, nieuw_dag = Counter(), Counter(), Counter()
    uren = set()
    ret, ret_college = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    combo, record, vorige, xp_combo, kritieken = 0, 0, None, 0, 0
    for rid, cid, ease, rtype in log:
        d = dag(rid)
        xp_kaarten += 1 if ease == 1 else 2
        if cid not in eerste:
            eerste[cid] = d
            xp_kaarten += 3
            nieuw_dag[d] += 1
        per_dag[d] += 1
        if ease > 1:
            goed_dag[d] += 1
        uren.add(dt.datetime.fromtimestamp(rid / 1000).hour)
        if rtype == 1 and d < 14:
            for sleutel, bak in ((thema_van_cid.get(cid), ret), (college_van_cid.get(cid), ret_college)):
                if sleutel:
                    bak[sleutel][1] += 1
                    bak[sleutel][0] += ease > 1
        if vorige is not None and rid - vorige > COMBO_PAUZE_MS:
            combo = 0
        if ease == 1:
            combo = 0
        else:
            combo += 1
            xp_combo += combo_bonus(combo)
            if kritiek(rid):
                kritieken += 1
        record, vorige = max(record, combo), rid
    nu_ms = int(dt.datetime.now().timestamp() * 1000)
    combo_nu = combo if vorige is not None and nu_ms - vorige <= COMBO_PAUZE_MS else 0

    quiz = staat.get('quiz', {})
    xp_vinken = sum(XP_COLLEGE if k in COLLEGES else XP_EXTRA for k in afgevinkt)
    xp_quiz = XP_QUIZVRAAG * sum(quiz.values())
    xp = xp_kaarten + xp_combo + XP_KRITIEK * kritieken + xp_vinken + xp_quiz
    lvl, titel, lo, hi = level_van(xp)

    drempel = cfg['reeks_drempel']
    actief = {d for d, n in per_dag.items() if n >= drempel}
    reeks, d = 0, (0 if 0 in actief else 1)
    while d in actief:
        reeks, d = reeks + 1, d + 1
    record_reeks, huidig = 0, 0
    for d in range(max(per_dag, default=0), -1, -1):
        huidig = huidig + 1 if d in actief else 0
        record_reeks = max(record_reeks, huidig)

    due = len(col.find_cards(f'deck:"{cfg["deck"]}" is:due'))
    nieuw_vandaag = nieuw_dag[0]
    fase = 1 if vandaag <= deadline else 2
    dagen_over = (deadline - vandaag).days + 1
    doel_nieuw = math.ceil((totaal['nieuw'] + nieuw_vandaag) / dagen_over) if fase == 1 and dagen_over > 0 else 0

    plan = {dt.date.fromisoformat(d): (th, items) for d, th, items in PLAN}
    plan_vandaag = plan.get(vandaag, (None, []))
    achterstand = [k for d, (_, items) in plan.items() if d < vandaag for k in items if k not in afgevinkt]
    items_vandaag = plan_vandaag[1]
    if fase == 1:
        quests = [
            ('Brons', 'Alle herhalingen van vandaag weg', due == 0, f'nog {due}' if due else 'klaar'),
            ('Zilver', f'{doel_nieuw} nieuwe kaarten', nieuw_vandaag >= doel_nieuw,
             f'{nieuw_vandaag}/{doel_nieuw}' + (' · 🔒 kijk een college' if staat.get('slot') and totaal['beschikbaar'] < doel_nieuw - nieuw_vandaag else '')),
            ('Goud', 'Colleges van vandaag en achterstand afgevinkt',
             not achterstand and all(k in afgevinkt for k in items_vandaag),
             f'{sum(k in afgevinkt for k in items_vandaag)}/{len(items_vandaag)}' + (f' · {len(achterstand)} achter' if achterstand else '')),
        ]
    else:
        quests = [
            ('Brons', 'Alle herhalingen van vandaag weg', due == 0, f'nog {due}' if due else 'klaar'),
            ('Zilver', f'{cfg["eindfase_herhalingen"]} herhalingen', per_dag[0] >= cfg['eindfase_herhalingen'], f'{per_dag[0]}/{cfg["eindfase_herhalingen"]}'),
            ('Goud', 'Oud tentamen van vandaag gemaakt', bool(items_vandaag) and all(k in afgevinkt for k in items_vandaag),
             f'{sum(k in afgevinkt for k in items_vandaag)}/{len(items_vandaag)}' if items_vandaag else 'vrije dag'),
        ]

    tempo = sum(nieuw_dag[d] for d in (1, 2, 3)) / 3 or nieuw_vandaag
    klaar_op = vandaag + dt.timedelta(days=math.ceil(totaal['nieuw'] / tempo)) if tempo and totaal['nieuw'] else (vandaag if not totaal['nieuw'] else None)

    bazen = []
    for k in CAMPAGNE_VOLGORDE:
        naam, baas, icoon = THEMAS[k]
        c = per[k]
        if not c['n']:
            continue
        gez, ank = c['gezien'] / c['n'], c['verankerd'] / c['n']
        hp = round(100 * (1 - 0.5 * gez - 0.5 * ank))
        status = 'verslagen' if gez >= 0.95 and ank >= 0.7 else ('gevecht' if gez >= 0.05 else 'slot')
        r = ret.get(k)
        bazen.append(dict(id=k, naam=naam, baas=baas, icoon=icoon, n=c['n'], gezien=c['gezien'], verankerd=c['verankerd'], opgeschort=c['opgeschort'],
                          hp=max(0, hp), status=status, retentie=round(100 * r[0] / r[1]) if r and r[1] >= 20 else None,
                          vandaag=k == plan_vandaag[0]))

    colleges = {}
    for k in COLLEGES:
        pc, af = per_college.get(k, Counter()), k in afgevinkt
        r = ret_college.get(k)
        colleges[k] = dict(sterren=sterren(pc, af), cel=cel_behaald(pc, af), af=af, quiz=quiz.get(k),
                           retentie=round(100 * r[0] / r[1]) if r and r[1] >= 10 else None)
    album = []
    for k in COLLEGE_VOLGORDE + [k for k in COLLEGES if k not in COLLEGE_VOLGORDE]:
        cel = COLLEGEDATA.get(k, {}).get('cel')
        if cel:
            album.append(dict(id=k, emoji=cel[0], naam=cel[1], feit=cel[2], behaald=colleges[k]['cel']))
    n_cellen = sum(a['behaald'] for a in album)
    werkdruk = werkdruk_week(col, ids)

    badges = [
        ('🩸', 'Eerste bloed', '25 nieuwe kaarten geleerd', len(eerste) >= 25),
        ('💯', 'Honderdklapper', '100 herhalingen op één dag', max(per_dag.values(), default=0) >= 100),
        ('🏃', 'Marathon', '300 herhalingen op één dag', max(per_dag.values(), default=0) >= 300),
        ('🔥', 'Week in vuur', '7 dagen op rij geleerd', record_reeks >= 7),
        ('🎯', 'Scherpschutter', 'Een dag met 50+ herhalingen en 90% goed',
         any(n >= 50 and goed_dag[d] / n >= 0.9 for d, n in per_dag.items())),
        ('⚡', 'Combokoning', 'Een combo van 50 goede antwoorden op rij', record >= 50),
        ('💥', 'Kritiek!', '10 kritieke treffers', kritieken >= 10),
        ('🌅', 'Vroege vogel', 'Herhaald vóór 8:00', any(h < 8 and h >= 4 for h in uren)),
        ('🦉', 'Nachtuil', 'Herhaald na 23:00', any(h >= 23 or h < 4 for h in uren)),
        ('🚪', 'Poortwachter', 'Vijf controlequizzen foutloos (5/5)', sum(v >= 5 for v in quiz.values()) >= 5),
        ('🧫', 'Verzamelaar', '10 cellen in je album', n_cellen >= 10),
        ('👑', 'Meester', 'Een college met ★★★ (70% verankerd)', any(c['sterren'] == 3 and per_college.get(k, Counter())['n'] for k, c in colleges.items())),
        ('🗺️', 'Halverwege', 'De helft van alle kaarten gezien', totaal['n'] and totaal['gezien'] / totaal['n'] >= 0.5),
        ('👁️', 'Alles gezien', 'Elke kaart minstens één keer geleerd', totaal['n'] and totaal['nieuw'] == 0),
        ('🎓', 'Collegetijger', 'Alle 32 hoorcolleges afgevinkt', all(k in afgevinkt for k in COLLEGES)),
        ('📜', 'Oude rot', 'Alle 6 oude tentamens gemaakt', all(f'OT{i}' in afgevinkt for i in range(1, 7))),
        ('🏆', 'Drakendoder', 'Alle zeven eindbazen verslagen', bazen and all(b['status'] == 'verslagen' for b in bazen)),
    ]

    return dict(vandaag=vandaag, examen=examen, deadline=deadline, dagen_examen=(examen - vandaag).days, fase=fase,
                xp=xp, level=lvl, titel=titel, xp_lo=lo, xp_hi=hi, reeks=reeks, record=record_reeks, reeks_vandaag=per_dag[0] >= drempel,
                drempel=drempel, quests=quests, herhalingen_vandaag=per_dag[0], nieuw_vandaag=nieuw_vandaag, doel_nieuw=doel_nieuw,
                due=due, totaal=totaal, bazen=bazen, badges=badges, tempo=tempo, klaar_op=klaar_op,
                plan_vandaag=plan_vandaag, achterstand=achterstand, afgevinkt=afgevinkt,
                volgorde=staat.get('volgorde'), slot=staat.get('slot', False), per_college=per_college, colleges=colleges,
                album=album, n_cellen=n_cellen, werkdruk=werkdruk, combo=combo_nu, combo_record=record, kritieken=kritieken,
                xp_combo=xp_combo, quiz=quiz, limiet_vandaag=staat.get('limiet') == vandaag.isoformat(),
                fout_recent=len(col.find_cards(f'deck:"{cfg["deck"]}" rated:{cfg.get("herkansing_dagen", 2)}:1')))


def werkdruk_week(col, ids: str) -> list[int]:
    """Aantal herhalingen per dag voor vandaag (incl. achterstand en leerstappen) en de 6 dagen daarna."""
    vandaag = col.sched.today
    dues = col.db.list(f'select case when odid != 0 then odue else due end from cards '
                       f'where (did in ({ids}) or odid in ({ids})) and queue in (2, 3)')
    leren = col.db.scalar(f'select count() from cards where (did in ({ids}) or odid in ({ids})) and queue = 1') or 0
    week = [0] * 7
    for d in dues:
        i = max(0, d - vandaag)
        if i < 7:
            week[i] += 1
    week[0] += leren
    return week


def snel(col, cfg: dict, staat: dict) -> dict:
    """Voor na elk antwoord: wat de meldingen en het HUD nodig hebben."""
    s = bereken(col, cfg, staat)
    return dict(level=s['level'], titel=s['titel'], quests=[q[2] for q in s['quests']], n=s['herhalingen_vandaag'],
                doel=s['doel_nieuw'], nieuw=s['nieuw_vandaag'], due=s['due'], combo=s['combo'], xp=s['xp'],
                bazen={b['id']: b for b in s['bazen']}, colleges=s['colleges']) if s else {}


def antwoord_xp(col, card_id: int, ease: int, combo: int) -> dict:
    """Wat het antwoord dat net is gegeven opleverde, voor de zwevende +XP in het HUD."""
    rid, aantal = col.db.first('select max(id), count() from revlog where cid = ? and type < 4 and ease > 0', card_id) or (None, 0)
    if rid is None:
        return dict(xp=0, kritiek=False, nieuw=False)
    nieuw = aantal == 1
    krit = ease > 1 and kritiek(rid)
    xp = (1 if ease == 1 else 2) + (3 if nieuw else 0) + (XP_KRITIEK if krit else 0) + (combo_bonus(combo) if ease > 1 else 0)
    return dict(xp=xp, kritiek=krit, nieuw=nieuw)


# ------------------------------------------------------------------ acties
def _nieuwe_kaarten(col, cfg):
    ids = ','.join(map(str, deck_ids(col, cfg['deck'])))
    return col.db.all(f'select c.id, n.id, n.mod, n.tags, n.flds, c.due, c.queue from cards c join notes n on c.nid = n.id '
                      f'where (c.did in ({ids}) or c.odid in ({ids})) and c.type = 0')


def campagne_starten(col, cfg: dict, afgevinkt: dict) -> int:
    """Zet alle nieuwe kaarten op volgorde van de colleges in het plan (basiskaarten vóór casus/schema/tabel)
    en vergrendelt de kaarten van colleges die je nog niet hebt afgevinkt."""
    rijen = _nieuwe_kaarten(col, cfg)

    def sleutel(r):
        cid, nid, mod, tags, flds, due, _q = r
        cl = college_van_notitie(nid, mod, tags, flds)
        extra = any(t.startswith('vorm::') and t != 'vorm::ezelsbrug' for t in tags.split())
        prio = 'prio::tentamen' not in tags.split()
        return (COLLEGE_VOLGORDE.index(cl) if cl in COLLEGE_VOLGORDE else len(COLLEGE_VOLGORDE), extra, prio, due)

    cids = [r[0] for r in sorted(rijen, key=sleutel)]
    if cids:
        col.sched.reposition_new_cards(cids, starting_from=0, step_size=1, randomize=False, shift_existing=False)
    vergrendel(col, cfg, afgevinkt)
    return len(cids)


def vergrendel(col, cfg: dict, afgevinkt: dict) -> int:
    """Nieuwe kaarten van niet-afgevinkte colleges opschorten, die van afgevinkte vrijgeven.
    Kaarten die je al geleerd hebt, worden nooit aangeraakt. Geeft het aantal vrijgespeelde kaarten terug."""
    dicht, open_ = [], []
    for cid, nid, mod, tags, flds, _due, queue in _nieuwe_kaarten(col, cfg):
        cl = college_van_notitie(nid, mod, tags, flds)
        moet_dicht = cl is not None and cl not in afgevinkt
        if moet_dicht and queue != -1:
            dicht.append(cid)
        elif not moet_dicht and queue == -1:
            open_.append(cid)
    if dicht:
        col.sched.suspend_cards(dicht)
    if open_:
        col.sched.unsuspend_cards(open_)
    return len(open_)


def alles_vrijgeven(col, cfg: dict) -> int:
    ids = [r[0] for r in _nieuwe_kaarten(col, cfg) if r[6] == -1]
    if ids:
        col.sched.unsuspend_cards(ids)
    return len(ids)


def zet_limiet(col, cfg: dict, n: int) -> None:
    deck = col.decks.by_name(cfg['deck'])
    deck['newLimitToday'] = {'limit': int(n), 'today': col.sched.today}
    col.decks.save(deck)


def koppeling_versie() -> str:
    try:
        return hashlib.md5((DATA / 'koppeling.json').read_bytes()).hexdigest()[:10]
    except OSError:
        return ''


def koppel(col, koppeling: dict[str, str] | None = None) -> int:
    """Zet de tag college::HCx op de notities uit de koppeling (en haalt een afwijkende college-tag weg).
    Geeft het aantal notities terug dat een (andere) tag kreeg."""
    koppeling = KOPPELING if koppeling is None else koppeling
    erbij, eraf = defaultdict(list), defaultdict(list)
    for nid, guid, tags in col.db.all('select id, guid, tags from notes'):
        doel = koppeling.get(guid)
        if not doel:
            continue
        huidig = [t for t in tags.split() if t.lower().startswith('college::')]
        if [t.lower() for t in huidig] == [f'college::{doel}'.lower()]:
            continue
        for t in huidig:
            eraf[t].append(nid)
        erbij[f'college::{doel}'].append(nid)
    for t, nids in eraf.items():
        col.tags.bulk_remove(nids, t)
    for t, nids in erbij.items():
        col.tags.bulk_add(nids, t)
    _COLLEGE_CACHE.clear()
    return sum(len(v) for v in erbij.values())


def herkansing(col, cfg: dict, college: str | None = None) -> tuple[int, int]:
    """Gefilterd deck met de kaarten die je de laatste dagen fout had (optioneel van één college).
    Geeft (deck-id, aantal kaarten) terug; (0, 0) als er niets te herkansen valt."""
    zoek = f'deck:"{cfg["deck"]}" rated:{cfg.get("herkansing_dagen", 2)}:1' + (f' tag:college::{college}' if college else '')
    n = len(col.find_cards(zoek))
    if not n:
        return 0, 0
    fd = col.sched.get_or_create_filtered_deck(deck_id=col.decks.id_for_name(HERKANSING) or 0)
    fd.name = HERKANSING
    del fd.config.search_terms[1:]
    if not fd.config.search_terms:
        fd.config.search_terms.add()
    term = fd.config.search_terms[0]
    term.search, term.limit, term.order = zoek, 300, 1  # 1 = willekeurig
    fd.config.reschedule = True
    return col.sched.add_or_update_filtered_deck(fd).id, n


def installatie(col, cfg: dict, staat: dict) -> list[dict]:
    """De eenmalige stappen uit STARTEN.md, met wat er al gedaan is. Volgorde telt: elke stap bouwt op de vorige."""
    heeft = lambda zoek: bool(col.find_notes(zoek))
    check = heeft('tag:check::behouden')
    extra = heeft('tag:vorm::casus OR tag:vorm::schema')
    colleges = heeft(f'tag:{BRON_TAG}')
    n_weg = len(col.find_notes('tag:check::dubbel OR tag:check::verwijderen'))
    did = col.decks.id_for_name(cfg['deck'])
    try:
        fsrs = bool(did) and col.decks.get_deck_configs_for_update(did).fsrs
    except Exception:
        fsrs = False
    stappen = [
        dict(id='check', label='Import 1: de gecontroleerde kaarten', klaar=check, knop='Importeren',
             uitleg='GZC3_check_import.txt — verbeterde, gesplitste en nieuwe kaarten. Er wordt eerst een back-up gemaakt.'),
        dict(id='extra', label='Import 2: casussen, schema\'s, tabellen en ezelsbruggen', klaar=extra, knop='Importeren', na='check',
             uitleg='GZC3_extra_import.txt'),
        dict(id='colleges', label='Import 3: kaarten uit de slides van HC 1-5', klaar=colleges, knop='Importeren', na='extra',
             uitleg='GZC3_colleges_import.txt — 181 nieuwe kaarten en de MCV-grenzen uit het college (82-98 fl).'),
        dict(id='opruimen', label='Dubbele en overbodige kaarten verwijderen', klaar=check and n_weg == 0,
             knop=f'{n_weg} kaarten verwijderen' if n_weg else 'Verwijderen', na='check',
             uitleg='Notities met de tag check::dubbel of check::verwijderen. Te herstellen met Bewerken → Ongedaan maken.'),
        dict(id='fsrs', label='FSRS aanzetten', klaar=fsrs, knop='Deckopties openen',
             uitleg='Onderaan de deckopties: FSRS aan, gewenste retentie 0,90, Opslaan.'),
        dict(id='campagne', label='Campagne starten', klaar=bool(staat.get('slot')), knop='Starten', na='check',
             uitleg='Nieuwe kaarten op volgorde van de colleges, en kaarten van colleges die je nog niet hebt gedaan op slot.'),
    ]
    klaar = {s['id']: s['klaar'] for s in stappen}
    for s in stappen:
        s['kan'] = not s['klaar'] and klaar.get(s.get('na'), True)
    return stappen
