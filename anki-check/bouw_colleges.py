"""Verwerkt de colleges (slides HC 1-5 en IC 1-4) tot kaarten, kapstokken en campagnedata.

Invoer : GZC3_check_import.txt en GZC3_extra_import.txt (de huidige stand van het deck),
         colleges_inhoud.py (inhoud per college), extra_inhoud.py (voor het bijgewerkte MCV-schema)
Uitvoer: GZC3_colleges_import.txt          nieuwe kaarten HC 1-5 + bijgewerkte MCV-kaarten
         kapstokken/HCx.md                 kapstok van één pagina met 5 controlevragen
         koppeling.md                      welke kaart bij welk college hoort (ter controle)
         campagne-addon/data/*             koppeling, collegedata en importbestanden voor de add-on
         quiz/vragen.json + quiz/index.html  controlevragen ook in de quiz

Kaarten van T1 en T2 zijn met de hand ingedeeld op basis van de slides (zie KOPPELING_T1/T2 hieronder).
De nummers verwijzen naar de volgorde van de T1- en T2-notities in de twee importbestanden (zonder dubbel/verwijderen).
"""
import copy, csv, hashlib, html, json, pathlib, random, re, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import colleges_inhoud as CI  # noqa: E402
import extra_inhoud as X  # noqa: E402
from bouw_extra import THEMA_TAG, svg, tabel, Q_FILL  # noqa: E402
from bouw_import import NOTETYPE, DECK  # noqa: E402

esc = html.escape
ADDON_DATA = ROOT / 'campagne-addon' / 'data'
VERWERKING = ROOT / 'verwerking'  # gecontroleerde resultaten van de transcript- en collegeworkflows (zie verwerking/README.md)
THEMA_NIEUW = {'HC6': 'T2', 'HC7': 'T2', 'HC8': 'T2', 'HC9': 'T2', 'HC10': 'T2', 'HC11': 'T3', 'HC12': 'T3', 'HC13': 'T3', 'HCAI': 'T3'}
NADRUK_TAGS = ['prio::tentamen', 'nadruk::docent']


def bron_tag(hc, bron):
    if bron == 'transcript':
        return 'bron::transcript'
    return 'bron::slides-HC1-5' if hc in ('HC1', 'HC2', 'HC3', 'HC4', 'HC5') else 'bron::slides-HC6-13'


def samenvoegen():
    """Colleges uit colleges_inhoud.py plus de gecontroleerde workflowresultaten in verwerking/HCx.json.
    Geeft (colleges, prio, correcties, koppeling_extra) terug."""
    colleges = copy.deepcopy(CI.COLLEGES)
    prio, correcties, koppeling_extra = {}, {}, {}
    for p in sorted(VERWERKING.glob('HC*.json')):
        hc, v = p.stem, json.loads(p.read_text(encoding='utf-8'))
        if 'kapstok' in v:  # een volledig nieuw verwerkt college
            for q in v['vragen']:
                assert len(q['fout']) == 3, (hc, q['vraag'])
            assert len(v['vragen']) == 5, (hc, len(v['vragen']))
            tabellen = []
            for t in v['tabellen']:
                rijen = [(r['rij'], r['cellen']) for r in t['rijen']]
                assert all(len(c) == len(t['kolommen']) for _, c in rijen), (hc, t['id'])
                tabellen.append(dict(id=t['id'], titel=t['titel'], kolommen=t['kolommen'], rijen=rijen))
            colleges[hc] = dict(
                thema=THEMA_NIEUW[hc], titel=v['titel'], docent=v['docent'], bron=v['bron'], kern=v['kern'],
                kapstok=[(k['kop'], k['punten']) for k in v['kapstok']], valkuilen=v['valkuilen'],
                vragen=[(q['vraag'], q['juist'], q['fout'], q['uitleg']) for q in v['vragen']],
                cel=CI.CELLEN_OVERIG[hc], kaarten=[(k['voor'], k['achter'], k['prio'], 'slides') for k in v['kaarten']],
                casus=[(c['vignet'], c['diagnose'], c['waarom']) for c in v['casus']], tabellen=tabellen, schemas=[],
                tentamentips=v['tentamentips'], citaten=v.get('docentcitaten', []))
        else:  # aanvulling op een al verwerkt college uit de transcripten
            c = colleges[hc]
            c['kaarten'] = list(c['kaarten']) + [(k['voor'], k['achter'], k['prio'], 'transcript') for k in v['nieuwe_kaarten']]
            kapstok = [(kop_, list(punten)) for kop_, punten in c['kapstok']]
            for a in v['kapstok_aanvullingen']:
                doel = next((punten for kop_, punten in kapstok if kop_.lower() == a['kop'].lower()), None)
                if doel is None:
                    kapstok.append((a['kop'], [a['punt']]))
                else:
                    doel.append(a['punt'])
            c['kapstok'] = kapstok
            c['valkuilen'] = list(c['valkuilen']) + v['valkuilen']
            c['tentamentips'], c['citaten'] = v['tentamentips'], v['docentcitaten']
            c['bron'] = c['bron'] + ' + transcript'
        for x in v['prio_guids']:
            prio[x['guid']] = x['waarom']
        for x in v['correcties']:
            correcties[x['guid']] = x
        for x in v.get('koppeling', []):
            koppeling_extra[x['guid']] = x['college']
    colleges = dict(sorted(colleges.items(), key=lambda kv: (len(kv[0]), kv[0])))  # HC1 … HC9, HC13
    return colleges, prio, correcties, koppeling_extra


COLLEGES, PRIO, CORRECTIES, KOPPELING_EXTRA = samenvoegen()

# ------------------------------------------------------------------ koppeling bestaande kaarten
def reeks(*delen):
    uit = []
    for d in delen:
        if isinstance(d, tuple):
            uit += list(range(d[0], d[1] + 1))
        else:
            uit.append(d)
    return uit


KOPPELING_T1 = {
    'HC1': reeks(6, 7, 8, 18, 19, 40, 50, 51, 52, 53, 74, 76, 77, 78, 79, 80, 129),
    'HC2': reeks(15, 16, 17, 21, 22, 23, 25, 26, 27, 28, 29, 30, 71, 75, 81, (83, 96), 130, (150, 158)),
    'HC3': reeks(1, 2, 3, 4, 5, 20, 24, (31, 39), (67, 70), 72, 73, 82, (97, 101), (114, 118), 121, (122, 128), 131, 132, 136,
                 (159, 162), (175, 183)),
    'HC4': reeks((9, 14), (41, 49), (54, 66), (102, 113), 119, 120, 133, 134, 135, 137, (138, 149), (163, 174)),
}
KOPPELING_T2 = {
    'HC1': reeks(145),
    'HC5': reeks(1, 2, 5, 6, 74, 75, 76, 77, 78, 83, 84, 100, (169, 175)),
    'HC6': reeks(71, 72, 73, 99, (107, 111), (114, 122), (147, 150), (180, 195), 225),
    'HC7': reeks(3, 7, 8, 9, 10, 11, 13, (16, 44), 79, 89, 91, 92, 93, 95, 97, 98, 106, (123, 131), (137, 141), (153, 161),
                 (196, 204), 222, 223, 224),
    'HC8': reeks((45, 61), 101, (132, 136), (142, 144), (163, 166), (176, 179), (213, 221)),
    'HC9': reeks(4, (62, 70), 80, 81, 82, (85, 88), (102, 105), 112, 113, 146, 151, 152, 167, 168, (205, 212), 226, 228, 229),
    'HC10': reeks(12, 14, 15, 90, 94, 96, 162),
    'HC11': reeks(227),
}
COLLEGE_LABEL = {k: f'HC {k[2:]}' for k in COLLEGES}


def lees(p):
    return [r for r in csv.reader((l for l in open(p, encoding='utf-8') if not l.startswith('#')), delimiter='\t')]


def plat(s):
    s = re.sub(r'<svg.*?</svg>', ' [schema] ', s, flags=re.S)
    s = re.sub(r'<table.*?</table>', ' [tabel] ', s, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def thema_van(tags):
    for t in sorted(tags, key=lambda t: not t.startswith('GZC3::B::')):
        m = re.match(r'GZC3::[AB]::([TB]\d)', t)
        if m:
            return m.group(1)
    for t in tags:
        if t.startswith('GZC3::ZIEKTE::'):
            z = t.split('::')[2]
            return 'T1' if z.startswith('anemie') else ('T3' if z in ('neuroblastoom', 'nefroblastoom', 'osteosarcoom', 'ewing', 'rhabdomyosarcoom') else None)
    return None


def huidige_stand():
    """Alle notities zoals ze na beide imports in het deck staan (extra overschrijft check)."""
    notes, volgorde = {}, []
    for p in ('GZC3_check_import.txt', 'GZC3_extra_import.txt'):
        for r in lees(ROOT / p):
            if r[0] not in notes:
                volgorde.append(r[0])
            notes[r[0]] = r
    return notes, volgorde


def maak_koppeling(notes, volgorde):
    import importlib.util
    spec = importlib.util.spec_from_file_location('campagne', ROOT / 'campagne-addon' / 'campagne.py')
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    per_thema = {'T1': [], 'T2': []}
    for g in volgorde:
        tags = notes[g][5].split()
        if 'check::dubbel' in tags or 'check::verwijderen' in tags:
            continue
        th = C.thema_van(tags)
        if th in per_thema:
            per_thema[th].append(g)
    koppeling = {}
    for th, tabel_ in (('T1', KOPPELING_T1), ('T2', KOPPELING_T2)):
        lijst = per_thema[th]
        gezien = {}
        for col, nummers in tabel_.items():
            for n in nummers:
                assert n not in gezien, f'{th} #{n} staat bij {gezien[n]} én {col}'
                gezien[n] = col
                koppeling[lijst[n - 1]] = col
        missend = [i for i in range(1, len(lijst) + 1) if i not in gezien]
        assert not missend, f'{th}: niet ingedeeld: {missend}'
        assert max(gezien) == len(lijst), f'{th}: {len(lijst)} notities, maar nummer {max(gezien)} gebruikt'
    return koppeling


# ------------------------------------------------------------------ nieuwe kaarten
def guid(*delen):
    return 'gzc3c-' + hashlib.sha1('|'.join(delen).encode()).hexdigest()[:12]


def tekst(s):
    return esc(s).replace('\n', '<br>')


def kop(hc, soort=''):
    c = COLLEGES[hc]
    return f'<div style="font-size:0.8em;color:#6b7686">{soort}{COLLEGE_LABEL[hc]} · {esc(c["titel"])}</div>'


def nieuwe_rijen():
    rijen, tel = [], {}

    def add(g, voor, achter, tags, soort):
        tel[soort] = tel.get(soort, 0) + 1
        rijen.append([g, NOTETYPE, DECK, voor, achter, ' '.join(dict.fromkeys(tags))])

    for hc, c in COLLEGES.items():
        basis = [THEMA_TAG[c['thema']], f'college::{hc}', 'check::nieuw', bron_tag(hc, 'slides')]
        for voor, achter, prio, *bron in c['kaarten']:
            bron = bron[0] if bron else 'slides'
            tags = [THEMA_TAG[c['thema']], f'college::{hc}', 'check::nieuw', bron_tag(hc, bron)] + (['prio::tentamen'] if prio else [])
            add(guid('kaart', hc, voor), kop(hc, '🎙️ ' if bron == 'transcript' else '📚 ') + esc(voor), tekst(achter), tags,
                'transcript' if bron == 'transcript' else 'basis')
        for vignet, diagnose, waarom in c['casus']:
            add(guid('casus', hc, diagnose), f'<div style="font-size:0.8em;color:#6b7686">🕵️ Wie ben ik? · {COLLEGE_LABEL[hc]}</div>{esc(vignet)}',
                f'<b>{esc(diagnose)}</b><br>{esc(waarom)}', basis + ['vorm::casus', 'prio::tentamen'], 'casus')
        for t in c['tabellen']:
            prio = ['prio::tentamen'] if t['id'] in ('bloederstoller', 'almdsmpn', 'mcvmchc') else []
            k = len(t['kolommen'])
            for ri, (rij, cellen) in enumerate(t['rijen']):
                for ki, cel in enumerate(cellen):
                    kol = t['kolommen'][ki]
                    vraagtekst = f'{rij} — {kol}' if k > 1 else f'{kol}: {rij}'
                    voor = (f'<div style="font-size:0.8em;color:#6b7686">📊 Vergelijk · {COLLEGE_LABEL[hc]}</div><b>{esc(t["titel"])}</b><br>'
                            f'Vul in: <i>{esc(vraagtekst)}</i><br><br>{tabel(t, ri, ki)}')
                    add(guid('tabel', hc, t['id'], str(ri), str(ki)), voor, f'<b>{esc(cel)}</b>', basis + ['vorm::vergelijking'] + prio, 'vergelijking')
        for s in c['schemas']:
            (ROOT / 'schemas' / f'{s["id"]}.svg').write_text(svg(s))
            for bid, *_r, tekst_, uitleg in s['boxes']:
                if not uitleg:
                    continue
                voor = (f'<div style="font-size:0.8em;color:#6b7686">🧩 Schema · {COLLEGE_LABEL[hc]}</div><b>{esc(s["titel"])}</b><br>'
                        f'Wat hoort op de plek van het <span style="background:{Q_FILL};padding:0 6px;border-radius:4px">?</span><br><br>{svg(s, bid)}')
                achter = f'<b>{esc(tekst_.replace(chr(10), " "))}</b><br>{esc(uitleg)}'
                add(guid('schema', hc, s['id'], bid), voor, achter, basis + ['vorm::schema'], 'schema')
    return rijen, tel


def bijgewerkte_rijen(notes):
    """Bestaande kaarten die het college anders zegt: MCV-grenzen 82-98 fl (UMC Utrecht) in plaats van 80-100."""
    rijen = []
    mcv = notes['D]V)GGJ|2S']
    assert mcv[3].startswith('Hoe classificeer je anemie morfologisch'), mcv[3]
    achter = mcv[4].replace('Microcytair &lt;80 fl, normocytair 80-100 fl, macrocytair &gt;100 fl',
                            'Microcytair &lt;82 fl, normocytair 82-98 fl, macrocytair &gt;98 fl (grenzen uit het anemiecollege; elders zie je ook 80-100)')
    assert achter != mcv[4]
    rijen.append(mcv[:4] + [achter, mcv[5]])
    schema = next(s for s in X.SCHEMAS if s['id'] == 'anemie')
    (ROOT / 'schemas' / 'anemie.svg').write_text(svg(schema))
    for bid, *_r, tekst_, uitleg in schema['boxes']:
        if not uitleg:
            continue
        g = 'gzc3x-' + hashlib.sha1('|'.join(('schema', 'anemie', bid)).encode()).hexdigest()[:12]
        oud = notes[g]
        voor = (f'<div style="font-size:0.8em;color:#6b7686">🧩 Schema</div><b>{esc(schema["titel"])}</b><br>'
                f'Wat hoort op de plek van het <span style="background:{Q_FILL};padding:0 6px;border-radius:4px">?</span><br><br>{svg(schema, bid)}')
        achter = f'<b>{esc(tekst_.replace(chr(10), " "))}</b><br>{esc(uitleg)}'
        rijen.append([g, NOTETYPE, DECK, voor, achter, oud[5]])
    return rijen


# ------------------------------------------------------------------ kapstokken en campagnedata
def kapstok_md(hc, c):
    regels = [f'# {COLLEGE_LABEL[hc]} · {c["titel"]}', '', f'*{c["docent"]} · bron: {c["bron"]}*', '', f'> {c["kern"]}', '']
    for kop_, punten in c['kapstok']:
        regels.append(f'### {kop_}')
        regels += [f'- {p}' for p in punten]
        regels.append('')
    regels.append('### Valkuilen')
    regels += [f'- ⚠️ {v}' for v in c['valkuilen']]
    if c.get('tentamentips'):
        regels += ['', '### 🎯 Wat de docent zei over het tentamen']
        regels += [f'- „{t["citaat"]}” — {t["betekenis"]}' for t in c['tentamentips']]
    if c.get('citaten'):
        regels += ['', '### 🎙️ Uit het college']
        regels += [f'- „{t["citaat"]}” ({t["onderwerp"]})' for t in c['citaten']]
    regels += ['', '## 5 controlevragen', '']
    for i, (v, juist, fout, uitleg) in enumerate(c['vragen'], 1):
        opties = [juist] + fout
        random.Random(hc + str(i)).shuffle(opties)
        letter = 'ABCD'[opties.index(juist)]
        regels.append(f'**{i}. {v}**')
        regels += [f'- {"ABCD"[j]}. {o}' for j, o in enumerate(opties)]
        regels += ['', f'<details><summary>Antwoord</summary>', '', f'**{letter}.** {uitleg}', '', '</details>', '']
    n = len(c['kaarten']) + len(c['casus']) + sum(len(t['rijen']) * len(t['kolommen']) for t in c['tabellen']) \
        + sum(1 for s in c['schemas'] for b in s['boxes'] if b[-1])
    regels += [f'*In Anki: `tag:college::{hc}` — {n} nieuwe kaarten uit dit college, naast de bestaande.*', '']
    return '\n'.join(regels)


def campagnedata(marker):
    colleges = {'_meta': dict(marker=marker)}
    for hc, cel in CI.CELLEN_OVERIG.items():
        colleges[hc] = dict(cel=cel)
    for hc, c in COLLEGES.items():
        colleges[hc] = dict(titel=c['titel'], docent=c['docent'], bron=c['bron'], kern=c['kern'], kapstok=c['kapstok'],
                            valkuilen=c['valkuilen'], cel=c['cel'], tentamentips=c.get('tentamentips', []), citaten=c.get('citaten', []),
                            vragen=[dict(vraag=v, opties=[j] + f, uitleg=u) for v, j, f, u in c['vragen']])
    return colleges


def pas_correcties_toe(nieuw, bijgewerkt, notes):
    """Correcties uit de controle: nieuwe kaarten direct aanpassen, bestaande kaarten als bijgewerkte regel meesturen.
    Een ezelsbrug of afbeelding op de oude achterkant blijft staan."""
    per_guid = {r[0]: r for r in nieuw + bijgewerkt}
    extra, overgeslagen = [], []
    for g, c in CORRECTIES.items():
        if g in per_guid:
            per_guid[g][4] = tekst(c['voorstel'])
        elif g in notes:
            oud = notes[g]
            behoud = ''.join(re.findall(r'<img[^>]*>', oud[4])) + ''.join(re.findall(r'<br><br><span style="background:#fff3c4.*?</span>', oud[4], flags=re.S))
            extra.append(oud[:4] + [tekst(c['voorstel']) + behoud, oud[5]])
        else:
            overgeslagen.append(c)
    return extra, overgeslagen


def koppeling_md(notes, koppeling):
    per = {}
    for g, col in koppeling.items():
        per.setdefault(col, []).append(plat(notes[g][3]))
    regels = ['# Koppeling van bestaande kaarten aan colleges', '',
              'Met de hand ingedeeld op basis van de slides van HC 1-5 (T1) en de onderwerpen van HC 5-10 (T2).',
              'De add-on zet deze indeling als tag `college::HCx` op je kaarten. Klopt er een niet? Pas dan `KOPPELING_T1/T2` in `bouw_colleges.py` aan.', '']
    volgorde = ['HC1', 'HC2', 'HC3', 'HC4', 'HC5', 'HC6', 'HC7', 'HC8', 'HC9', 'HC10', 'HC11', 'HC12', 'HC13', 'HCAI']
    for col in volgorde:
        if col not in per:
            continue
        regels += [f'## {col} ({len(per[col])} kaarten)', '']
        regels += [f'- {v[:140]}' for v in per[col]]
        regels.append('')
    return '\n'.join(regels)


def quiz_bijwerken():
    data = json.loads((ROOT / 'quiz' / 'vragen.json').read_text())
    data['vragen'] = [q for q in data['vragen'] if not q['id'].startswith('k')]
    for hc, c in COLLEGES.items():
        for i, (v, j, f, u) in enumerate(c['vragen']):
            data['vragen'].append(dict(id=f'k{hc}{i}', thema=c['thema'], soort=f'Controlevraag {COLLEGE_LABEL[hc]}', vraag=v, opties=[j] + f, uitleg=u))
    (ROOT / 'quiz' / 'vragen.json').write_text(json.dumps(data, ensure_ascii=False, indent=1))
    sjabloon = (ROOT / 'quiz' / 'sjabloon.html').read_text()
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    (ROOT / 'quiz' / 'index.html').write_text(sjabloon.replace('/*DATA*/null', blob))
    return len(data['vragen'])


def main():
    notes, volgorde = huidige_stand()
    koppeling = maak_koppeling(notes, volgorde)
    weg = {g for g, r in notes.items() if {'check::dubbel', 'check::verwijderen'} & set(r[5].split())}
    for g, col in KOPPELING_EXTRA.items():  # verbeteringen uit de collegecontrole (o.a. de T3-kaarten)
        if g in notes and g not in weg:
            koppeling[g] = col
    nieuw, tel = nieuwe_rijen()
    bijgewerkt = bijgewerkte_rijen(notes)
    gids = [r[0] for r in nieuw]
    assert len(gids) == len(set(gids)), 'dubbele GUID'
    assert not set(gids) & set(notes), 'GUID botst met bestaande notitie'
    gecorrigeerd, overgeslagen = pas_correcties_toe(nieuw, bijgewerkt, notes)
    bijgewerkt += gecorrigeerd
    # nadruk van de docent: nieuwe kaarten krijgen de tags meteen, bestaande via de add-on
    for r in nieuw + bijgewerkt:
        if r[0] in PRIO:
            r[5] = ' '.join(dict.fromkeys(r[5].split() + NADRUK_TAGS))
    extra_tags = {g: NADRUK_TAGS for g in PRIO if g in notes and g not in weg}

    uit = ROOT / 'GZC3_colleges_import.txt'
    with open(uit, 'w', newline='', encoding='utf-8') as fh:
        fh.write('#separator:tab\n#html:true\n#guid column:1\n#notetype column:2\n#deck column:3\n#tags column:6\n')
        csv.writer(fh, delimiter='\t', lineterminator='\n').writerows(bijgewerkt + nieuw)

    (ROOT / 'kapstokken').mkdir(exist_ok=True)
    for hc, c in COLLEGES.items():
        (ROOT / 'kapstokken' / f'{hc}.md').write_text(kapstok_md(hc, c))
    (ROOT / 'koppeling.md').write_text(koppeling_md(notes, koppeling))

    ADDON_DATA.mkdir(exist_ok=True)
    (ADDON_DATA / 'koppeling.json').write_text(json.dumps(koppeling, ensure_ascii=False, sort_keys=True))
    (ADDON_DATA / 'extra_tags.json').write_text(json.dumps(extra_tags, ensure_ascii=False, sort_keys=True))
    marker = gids[-1]  # de add-on ziet aan deze notitie of de nieuwste versie van de collegeimport al binnen is
    (ADDON_DATA / 'colleges.json').write_text(json.dumps(campagnedata(marker), ensure_ascii=False))
    for naam in ('GZC3_check_import.txt', 'GZC3_extra_import.txt', 'GZC3_colleges_import.txt'):
        shutil.copy(ROOT / naam, ADDON_DATA / naam)
    nq = quiz_bijwerken()

    per = {}
    for col in koppeling.values():
        per[col] = per.get(col, 0) + 1
    print('nieuw:', tel, 'totaal', len(nieuw), '| bijgewerkt:', len(bijgewerkt), f'(waarvan {len(gecorrigeerd)} correcties)',
          '| nadruk op bestaande kaarten:', len(extra_tags), '| quizvragen:', nq, '| versie', marker)
    if overgeslagen:
        print('correcties zonder kaart (kapstok/vraag, met de hand verwerken):')
        for c in overgeslagen:
            print('  -', c['guid'], '|', c['huidig'][:90], '→', c['voorstel'][:120])
    print('koppeling:', dict(sorted(per.items(), key=lambda kv: (len(kv[0]), kv[0]))))
    print('per college nieuw:', {hc: sum(1 for r in nieuw if f'college::{hc}' in r[5]) for hc in COLLEGES})


if __name__ == '__main__':
    main()
