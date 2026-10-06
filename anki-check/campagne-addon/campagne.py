"""Campagne GZC III — rekenwerk en weergave. Gebruikt alleen `anki` en de standaardbibliotheek,
zodat het buiten Anki te testen is. De koppeling met de Anki-interface staat in __init__.py.
"""
from __future__ import annotations

import datetime as dt
import html
import math
import re
from collections import Counter, defaultdict

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
    'HC1': ('T1', 'HC 1 Hemato-erytropoëse (1)'), 'HC2': ('T1', 'HC 2 Hemato-erytropoëse (2)'),
    'HC3': ('T1', 'HC 3 Anemie'), 'HC4': ('T1', 'HC 4 Stollingsstoornissen'),
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
PLAN = [  # (datum, thema van de dag, colleges en extra's). T3 eerst: daar zit de groep nu; dan T1/T2 inhalen.
    ('2026-10-06', 'T3', ['HC11', 'AYA']), ('2026-10-07', 'T3', ['HC12', 'HC13', 'HCAI']),
    ('2026-10-08', 'T1', ['HC1', 'HC2']), ('2026-10-09', 'T1', ['HC3', 'HC4']),
    ('2026-10-10', 'T2', ['HC5']), ('2026-10-11', 'T2', ['HC6', 'HC7']), ('2026-10-12', 'T2', ['HC8', 'HC9']),
    ('2026-10-13', 'T2', ['HC10']),
    ('2026-10-14', 'T4', ['HC14', 'HC15']), ('2026-10-15', 'T4', ['HC16', 'HC17', 'RT']), ('2026-10-16', 'T4', ['HC18', 'HC19']),
    ('2026-10-17', 'B1', ['PH1', 'PH2', 'PH3', 'PH4']), ('2026-10-18', 'B1', ['PH5', 'PH6', 'PH7', 'PH8']),
    ('2026-10-19', 'B2', ['HC28', 'HC29', 'JP', 'HW']), ('2026-10-20', 'B3', ['HC30', 'HC31']),
    ('2026-10-21', None, []), ('2026-10-22', None, []),
    ('2026-10-23', None, ['OT1']), ('2026-10-24', None, ['OT2']), ('2026-10-25', None, ['OT3']),
    ('2026-10-26', None, ['OT4']), ('2026-10-27', None, ['OT5']), ('2026-10-28', None, ['OT6']),
]
CAMPAGNE_VOLGORDE = ['T3', 'T1', 'T2', 'T4', 'B1', 'B2', 'B3']  # volgorde van nieuwe kaarten
TITELS = ['Nieuweling', 'Pipetteur', 'Uitstrijkjesmaker', 'Bloedbeeldlezer', 'Stollingsdetective',
          'IJzerjager', 'Lymfoomspeurder', 'Myeloomtemmer', 'Blastenbestrijder', 'Kinderoncoloog i.o.',
          'Halsklierkenner', 'Schildklierfluisteraar', 'Poortwachter', 'Palliatief expert', 'Tentamenbeest']

XP_COLLEGE, XP_EXTRA = 50, 75
VERANKERD_IVL = 7  # dagen


def xp_drempel(n: int) -> int:
    """Totale XP nodig voor level n (level 1 = 0)."""
    return int(150 * (n - 1) ** 1.7)


def level_van(xp: int) -> tuple[int, str, int, int]:
    n = 1
    while xp >= xp_drempel(n + 1):
        n += 1
    titel = TITELS[min(n, len(TITELS)) - 1] + (f' ★{n - len(TITELS)}' if n > len(TITELS) else '')
    return n, titel, xp_drempel(n), xp_drempel(n + 1)


def thema_van(tags: list[str]) -> str | None:
    for t in tags:
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

    kaarten = col.db.all(f'select c.id, n.tags, c.queue, c.ivl, c.type from cards c join notes n on c.nid = n.id '
                         f'where (c.did in ({ids}) or c.odid in ({ids}))')
    per = {k: Counter() for k in THEMAS}
    totaal = Counter()
    for cid, tags, queue, ivl, ctype in kaarten:
        th = thema_van(tags.split())
        rij = [totaal] + ([per[th]] if th else [])
        for c in rij:
            c['n'] += 1
            if ctype != 0:
                c['gezien'] += 1
            if ctype == 2 and ivl >= VERANKERD_IVL:
                c['verankerd'] += 1
            if ctype == 0:
                c['nieuw'] += 1
            if queue == -1:
                c['opgeschort'] += 1

    log = col.db.all(f'select r.id, r.cid, r.ease, r.type from revlog r where r.cid in '
                     f'(select id from cards where did in ({ids}) or odid in ({ids})) and r.type < 4 and r.ease > 0 order by r.id')
    dag = lambda rid: (cutoff * 1000 - rid - 1) // 86400000  # 0 = vandaag
    xp_kaarten, eerste = 0, {}
    per_dag, goed_dag, nieuw_dag = Counter(), Counter(), Counter()
    uren = set()
    thema_van_cid = {cid: thema_van(tags.split()) for cid, tags, *_ in kaarten}
    ret = defaultdict(lambda: [0, 0])
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
        if rtype == 1 and d < 14 and thema_van_cid.get(cid):
            ret[thema_van_cid[cid]][1] += 1
            ret[thema_van_cid[cid]][0] += ease > 1

    afgevinkt = staat.get('afgevinkt', {})
    xp = xp_kaarten + sum(XP_COLLEGE if k in COLLEGES else XP_EXTRA for k in afgevinkt)
    lvl, titel, lo, hi = level_van(xp)

    drempel = cfg['reeks_drempel']
    actief = {d for d, n in per_dag.items() if n >= drempel}
    reeks, d = 0, (0 if 0 in actief else 1)
    while d in actief:
        reeks, d = reeks + 1, d + 1
    record, huidig = 0, 0
    for d in range(max(per_dag, default=0), -1, -1):
        huidig = huidig + 1 if d in actief else 0
        record = max(record, huidig)

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
            ('Zilver', f'{doel_nieuw} nieuwe kaarten', nieuw_vandaag >= doel_nieuw, f'{nieuw_vandaag}/{doel_nieuw}'),
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

    badges = [
        ('🩸', 'Eerste bloed', '25 nieuwe kaarten geleerd', len(eerste) >= 25),
        ('💯', 'Honderdklapper', '100 herhalingen op één dag', max(per_dag.values(), default=0) >= 100),
        ('🏃', 'Marathon', '300 herhalingen op één dag', max(per_dag.values(), default=0) >= 300),
        ('🔥', 'Week in vuur', '7 dagen op rij geleerd', record >= 7),
        ('🎯', 'Scherpschutter', 'Een dag met 50+ herhalingen en 90% goed',
         any(n >= 50 and goed_dag[d] / n >= 0.9 for d, n in per_dag.items())),
        ('🌅', 'Vroege vogel', 'Herhaald vóór 8:00', any(h < 8 and h >= 4 for h in uren)),
        ('🦉', 'Nachtuil', 'Herhaald na 23:00', any(h >= 23 or h < 4 for h in uren)),
        ('🗺️', 'Halverwege', 'De helft van alle kaarten gezien', totaal['n'] and totaal['gezien'] / totaal['n'] >= 0.5),
        ('👁️', 'Alles gezien', 'Elke kaart minstens één keer geleerd', totaal['n'] and totaal['nieuw'] == 0),
        ('🎓', 'Collegetijger', 'Alle 32 hoorcolleges afgevinkt', all(k in afgevinkt for k in COLLEGES)),
        ('📜', 'Oude rot', 'Alle 6 oude tentamens gemaakt', all(f'OT{i}' in afgevinkt for i in range(1, 7))),
        ('🏆', 'Drakendoder', 'Alle zeven eindbazen verslagen', bazen and all(b['status'] == 'verslagen' for b in bazen)),
    ]

    return dict(vandaag=vandaag, examen=examen, deadline=deadline, dagen_examen=(examen - vandaag).days, fase=fase,
                xp=xp, level=lvl, titel=titel, xp_lo=lo, xp_hi=hi, reeks=reeks, record=record, reeks_vandaag=per_dag[0] >= drempel,
                drempel=drempel, quests=quests, herhalingen_vandaag=per_dag[0], nieuw_vandaag=nieuw_vandaag, doel_nieuw=doel_nieuw,
                due=due, totaal=totaal, bazen=bazen, badges=badges, tempo=tempo, klaar_op=klaar_op,
                plan_vandaag=plan_vandaag, achterstand=achterstand, afgevinkt=afgevinkt,
                volgorde=staat.get('volgorde'), limiet_vandaag=staat.get('limiet') == vandaag.isoformat())


def snel(col, cfg: dict, staat: dict) -> dict:
    """Goedkope versie voor na elk antwoord: XP, level, quests van vandaag."""
    s = bereken(col, cfg, staat)
    return dict(level=s['level'], titel=s['titel'], quests=[q[2] for q in s['quests']], n=s['herhalingen_vandaag'],
                doel=s['doel_nieuw'], nieuw=s['nieuw_vandaag'], due=s['due']) if s else {}


# ------------------------------------------------------------------ acties
def campagnevolgorde(col, cfg: dict) -> int:
    """Geeft opgeschorte kaarten vrij en zet alle nieuwe kaarten in de volgorde van de campagne:
    per thema (CAMPAGNE_VOLGORDE), binnen een thema de gewone kaarten vóór casus/schema/tabel."""
    dids = deck_ids(col, cfg['deck'])
    ids = ','.join(map(str, dids))
    opgeschort = col.db.list(f'select id from cards where (did in ({ids}) or odid in ({ids})) and queue = -1')
    if opgeschort:
        col.sched.unsuspend_cards(opgeschort)
    rijen = col.db.all(f'select c.id, n.tags, c.due from cards c join notes n on c.nid = n.id '
                       f'where (c.did in ({ids}) or c.odid in ({ids})) and c.type = 0 and c.queue != -1')
    volgorde = CAMPAGNE_VOLGORDE

    def sleutel(r):
        tags = r[1].split()
        th = thema_van(tags)
        extra = any(t.startswith('vorm::') and t != 'vorm::ezelsbrug' for t in tags)
        return (volgorde.index(th) if th in volgorde else len(volgorde), extra, r[2])

    cids = [r[0] for r in sorted(rijen, key=sleutel)]
    if cids:
        col.sched.reposition_new_cards(cids, starting_from=0, step_size=1, randomize=False, shift_existing=False)
    return len(cids)


def zet_limiet(col, cfg: dict, n: int) -> None:
    deck = col.decks.by_name(cfg['deck'])
    deck['newLimitToday'] = {'limit': int(n), 'today': col.sched.today}
    col.decks.save(deck)


# ------------------------------------------------------------------ weergave
CSS = """
#gzc3{--bg:#fbf9fd;--kaart:#ffffff;--ink:#221a2e;--zacht:#6b6278;--lijn:#e4dcec;--hema:#5b3f8c;--hema-z:#ece5f6;
--eos:#d9577a;--eos-z:#fbe6ec;--goed:#1f8a4c;--goed-z:#e2f4e9;--brons:#a8642a;--zilver:#7d8794;--goud:#c49a1a;
max-width:760px;margin:18px auto 8px;padding:16px;border-radius:16px;background:var(--bg);color:var(--ink);
border:1px solid var(--lijn);text-align:left;font-family:-apple-system,"Segoe UI",Roboto,sans-serif;font-size:14px;line-height:1.45}
:root.night-mode #gzc3{--bg:#1b1622;--kaart:#241d2e;--ink:#efe9f6;--zacht:#a79cb6;--lijn:#3a3047;--hema:#b69ae6;--hema-z:#2f2642;
--eos:#f08aa6;--eos-z:#3a2230;--goed:#5fd08f;--goed-z:#193426;--brons:#d89a62;--zilver:#b6bfca;--goud:#e8c454}
#gzc3 *{box-sizing:border-box}
#gzc3 .kop{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
#gzc3 h2{margin:0;font-size:20px;letter-spacing:-.01em}
#gzc3 .sub{color:var(--zacht);font-size:13px}
#gzc3 .aftel{text-align:right}
#gzc3 .aftel b{font-size:28px;color:var(--eos);font-variant-numeric:tabular-nums;line-height:1}
#gzc3 .rij{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:14px}
#gzc3 .blok{background:var(--kaart);border:1px solid var(--lijn);border-radius:12px;padding:12px}
#gzc3 .label{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--zacht);font-weight:600;margin-bottom:6px}
#gzc3 .lvl{display:flex;align-items:baseline;gap:8px}
#gzc3 .lvl b{font-size:26px;color:var(--hema)}
#gzc3 .balk{height:8px;border-radius:99px;background:var(--lijn);overflow:hidden;margin-top:6px}
#gzc3 .balk span{display:block;height:100%;background:var(--hema)}
#gzc3 .quest{display:grid;grid-template-columns:62px 1fr auto;gap:8px;align-items:center;padding:5px 0;border-top:1px dashed var(--lijn)}
#gzc3 .quest:first-of-type{border-top:0}
#gzc3 .medaille{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;border-radius:99px;padding:2px 8px;text-align:center;border:1.5px solid}
#gzc3 .Brons{color:var(--brons)}#gzc3 .Zilver{color:var(--zilver)}#gzc3 .Goud{color:var(--goud)}
#gzc3 .quest.af .medaille{background:currentColor}#gzc3 .quest.af .medaille i{color:var(--kaart)}
#gzc3 .medaille i{font-style:normal}
#gzc3 .quest .st{font-variant-numeric:tabular-nums;color:var(--zacht);font-size:13px}
#gzc3 .quest.af .st{color:var(--goed);font-weight:600}
#gzc3 .bazen{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-top:8px}
#gzc3 .baas{background:var(--kaart);border:1px solid var(--lijn);border-radius:12px;padding:10px;position:relative}
#gzc3 .baas.vandaag{border-color:var(--eos);box-shadow:0 0 0 2px var(--eos-z)}
#gzc3 .baas.verslagen{background:var(--goed-z)}
#gzc3 .baas.slot{opacity:.7}
#gzc3 .baas .ic{font-size:22px}
#gzc3 .baas .nm{font-weight:600;font-size:13px}
#gzc3 .baas .th{font-size:12px;color:var(--zacht)}
#gzc3 .hp{height:7px;border-radius:99px;background:var(--lijn);overflow:hidden;margin:6px 0 3px}
#gzc3 .hp span{display:block;height:100%;background:var(--eos)}
#gzc3 .baas.verslagen .hp span{background:var(--goed)}
#gzc3 .klein{font-size:12px;color:var(--zacht);font-variant-numeric:tabular-nums}
#gzc3 .tag{position:absolute;top:8px;right:8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--eos)}
#gzc3 .vink{display:flex;gap:8px;align-items:flex-start;padding:4px 0;cursor:pointer}
#gzc3 .vink input{margin-top:3px;accent-color:var(--hema)}
#gzc3 .vink.gedaan span{color:var(--zacht);text-decoration:line-through}
#gzc3 .knoppen{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
#gzc3 button{font:inherit;font-size:13px;font-weight:600;border-radius:9px;padding:7px 12px;cursor:pointer;border:1.5px solid var(--hema);background:var(--hema);color:var(--kaart)}
#gzc3 button.licht{background:transparent;color:var(--hema)}
#gzc3 .badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
#gzc3 .badge{display:inline-flex;gap:5px;align-items:center;border-radius:99px;padding:3px 10px;border:1px solid var(--lijn);font-size:12px;background:var(--kaart)}
#gzc3 .badge.nee{opacity:.42;filter:grayscale(1)}
#gzc3 .chip{display:inline-block;border-radius:99px;padding:2px 9px;font-size:12px;font-weight:600}
#gzc3 .chip.ok{background:var(--goed-z);color:var(--goed)}#gzc3 .chip.nok{background:var(--eos-z);color:var(--eos)}
#gzc3 details{margin-top:12px}#gzc3 summary{cursor:pointer;color:var(--hema);font-weight:600}
#gzc3 .groep{margin-top:8px}#gzc3 .groep b{font-size:12px;color:var(--zacht)}
"""


def _e(s) -> str:
    return html.escape(str(s))


def _vink(key: str, tekst: str, af: bool, xp: int) -> str:
    return (f'<label class="vink{" gedaan" if af else ""}"><input type="checkbox" {"checked" if af else ""} '
            f'onclick="pycmd(\'gzc3:vink:{key}\');return false;"><span>{_e(tekst)} '
            f'<span class="klein">+{xp} XP</span></span></label>')


def weergave(s: dict) -> str:
    if not s:
        return ''
    dagen = s['dagen_examen']
    aftel = (f'<b>{dagen}</b><div class="sub">dagen tot het tentamen<br>{s["examen"].strftime("%d-%m")}</div>' if dagen > 0
             else '<b>🎯</b><div class="sub">tentamendag — succes!</div>')
    fase = ('Fase 1 · Veldtocht: nieuwe stof tot ' + s['deadline'].strftime('%d-%m')) if s['fase'] == 1 else 'Fase 2 · Eindbaas: herhalen en oude tentamens'
    pct = 0 if s['xp_hi'] == s['xp_lo'] else round(100 * (s['xp'] - s['xp_lo']) / (s['xp_hi'] - s['xp_lo']))
    reeks = f'🔥 {s["reeks"]} {"dag" if s["reeks"] == 1 else "dagen"} op rij' + ('' if s['reeks_vandaag'] else f' · vandaag nog {s["drempel"]} herhalingen voor je reeks')

    quests = ''.join(
        f'<div class="quest{" af" if af else ""}"><span class="medaille {m}"><i>{m}</i></span><span>{_e(t)}</span><span class="st">{"✓ " if af else ""}{_e(st)}</span></div>'
        for m, t, af, st in s['quests'])

    th_vandaag, items = s['plan_vandaag']
    vandaag_html = ''
    if th_vandaag:
        naam, baas, icoon = THEMAS[th_vandaag]
        vandaag_html = f'<div class="sub">Vandaag in de campagne: {icoon} <b>{_e(naam)}</b> — versla {_e(baas)}</div>'
    lijst = ''.join(_vink(k, (COLLEGES.get(k) or EXTRA[k])[1], k in s['afgevinkt'], XP_COLLEGE if k in COLLEGES else XP_EXTRA) for k in items)
    if s['achterstand']:
        lijst += '<div class="label" style="margin-top:8px">Inhalen</div>' + ''.join(
            _vink(k, (COLLEGES.get(k) or EXTRA[k])[1], False, XP_COLLEGE if k in COLLEGES else XP_EXTRA) for k in s['achterstand'][:6])
        if len(s['achterstand']) > 6:
            lijst += f'<div class="klein">en nog {len(s["achterstand"]) - 6} — zie alle colleges hieronder</div>'
    if not lijst:
        lijst = '<div class="klein">Geen colleges gepland: inhaal- of herhaaldag.</div>'

    knoppen = []
    if s['fase'] == 1 and s['doel_nieuw'] and not s['limiet_vandaag']:
        knoppen.append(f'<button onclick="pycmd(\'gzc3:limiet\')">Zet vandaag {s["doel_nieuw"]} nieuwe kaarten klaar</button>')
    if s['totaal']['opgeschort'] or (not s['volgorde'] and s['totaal']['nieuw']):
        tekst = (f'{s["totaal"]["opgeschort"]} opgeschorte kaarten vrijgeven en alles in campagnevolgorde zetten'
                 if s['totaal']['opgeschort'] else 'Nieuwe kaarten in campagnevolgorde zetten')
        knoppen.append(f'<button class="licht" onclick="pycmd(\'gzc3:volgorde\')">{tekst}</button>')

    t = s['totaal']
    if s['fase'] == 1 and t['nieuw'] and not s['tempo']:
        prognose = (f'<span class="chip nok">start</span> Nog {t["nieuw"]} kaarten te gaan in {(s["deadline"] - s["vandaag"]).days + 1} dagen: '
                    f'{s["doel_nieuw"]} nieuwe kaarten per dag houdt je op schema.')
    elif s['fase'] == 1 and t['nieuw']:
        op_tijd = s['klaar_op'] and s['klaar_op'] <= s['deadline']
        prognose = (f'<span class="chip {"ok" if op_tijd else "nok"}">{"op schema" if op_tijd else "achter op schema"}</span> '
                    f'Tempo laatste dagen: {s["tempo"]:.0f} nieuwe kaarten/dag'
                    + (f' → alles gezien op {s["klaar_op"].strftime("%d-%m")}' if s['klaar_op'] else ' → begin vandaag')
                    + f'. Nodig: {s["doel_nieuw"]}/dag.')
    elif t['nieuw'] == 0:
        prognose = '<span class="chip ok">alles gezien</span> Nu gaat het om verankeren: elke dag je herhalingen weg.'
    else:
        prognose = f'<span class="chip nok">{t["nieuw"]} kaarten nog nooit gezien</span> Doe die eerst, met voorrang voor <code>tag:prio::tentamen</code>.'

    bazen = ''.join(
        f'<div class="baas {b["status"]}{" vandaag" if b["vandaag"] else ""}" title="{_e(b["naam"])}">'
        + ('<span class="tag">vandaag</span>' if b['vandaag'] else '')
        + f'<div class="ic">{b["icoon"] if b["status"] != "verslagen" else "🏆"}</div><div class="nm">{_e(b["baas"])}</div>'
        f'<div class="th">{b["id"]} · {_e(b["naam"])}</div><div class="hp"><span style="width:{b["hp"]}%"></span></div>'
        f'<div class="klein">{"verslagen" if b["status"] == "verslagen" else str(b["hp"]) + " HP"} · gezien {b["gezien"]}/{b["n"]} · verankerd {b["verankerd"]}'
        + (f' · {b["retentie"]}% goed' if b['retentie'] is not None else '')
        + (f' · 🔒 {b["opgeschort"]} opgeschort' if b['opgeschort'] else '') + '</div></div>'
        for b in s['bazen'])

    badges = ''.join(f'<span class="badge{"" if ok else " nee"}" title="{_e(uitleg)}">{ic} {_e(nm)}</span>' for ic, nm, uitleg, ok in s['badges'])
    behaald = sum(1 for *_, ok in s['badges'] if ok)

    groepen = ''
    for k in CAMPAGNE_VOLGORDE:
        naam = THEMAS[k][0]
        rij = [(c, v[1]) for c, v in {**COLLEGES, **EXTRA}.items() if v[0] == k]
        groepen += f'<div class="groep"><b>{k} · {_e(naam)}</b>' + ''.join(
            _vink(c, tekst, c in s['afgevinkt'], XP_COLLEGE if c in COLLEGES else XP_EXTRA) for c, tekst in rij) + '</div>'
    groepen += '<div class="groep"><b>Oude tentamens</b>' + ''.join(
        _vink(c, v[1], c in s['afgevinkt'], XP_EXTRA) for c, v in EXTRA.items() if v[0] is None) + '</div>'
    n_col = sum(1 for k in COLLEGES if k in s['afgevinkt'])

    return f"""<style>{CSS}</style><div id="gzc3">
<div class="kop"><div><h2>Campagne GZC III</h2><div class="sub">{_e(fase)}</div>{vandaag_html}</div><div class="aftel">{aftel}</div></div>
<div class="rij">
 <div class="blok"><div class="label">Niveau</div><div class="lvl"><b>{s['level']}</b><span>{_e(s['titel'])}</span></div>
  <div class="balk"><span style="width:{pct}%"></span></div><div class="klein">{s['xp']} XP · nog {s['xp_hi'] - s['xp']} tot level {s['level'] + 1}</div>
  <div class="klein" style="margin-top:6px">{_e(reeks)} · record {s['record']}</div></div>
 <div class="blok"><div class="label">Dagquest</div>{quests}
  <div class="klein" style="margin-top:4px">Vandaag {s['herhalingen_vandaag']} herhalingen, {s['nieuw_vandaag']} nieuw</div></div>
</div>
<div class="blok" style="margin-top:12px"><div class="label">Vandaag op het programma</div>{lijst}
 <div class="knoppen">{''.join(knoppen)}</div></div>
<div style="margin-top:12px" class="sub">{prognose}</div>
<div class="label" style="margin-top:14px">Eindbazen · gezien {t['gezien']}/{t['n']} · verankerd {t['verankerd']} (interval ≥ {VERANKERD_IVL} dagen)</div>
<div class="bazen">{bazen}</div>
<div class="label" style="margin-top:14px">Badges · {behaald}/{len(s['badges'])}</div><div class="badges">{badges}</div>
<details><summary>Alle colleges en extra's ({n_col}/{len(COLLEGES)} colleges)</summary>{groepen}</details>
</div>"""
