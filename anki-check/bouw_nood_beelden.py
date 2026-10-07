"""Bouwt het noodpakket en de afbeeldingen voor de campagne-add-on.

Invoer : verwerking/nood.json      gecontroleerde essentiekaarten en samenvattingen per thema (workflow)
         verwerking/beelden.json   gecontroleerde en geselecteerde afbeeldingen, met bron en licentie (workflow)
         beelden/                  de afbeeldingsbestanden zelf
         GZC3_*_import.txt         de huidige stand van het deck (voor thema- en collegetags)
Uitvoer: campagne-addon/data/GZC3_nood_import.txt     apart deck "GZC III - Noodpakket"
         campagne-addon/data/nood.json                samenvattingen en guids voor het noodpakketvenster
         campagne-addon/data/GZC3_beelden_import.txt  herkenkaarten (afbeelding op de voorkant)
         campagne-addon/data/beelden.json + beelden/  afbeeldingen per bestaande kaart
         noodpakket.md                                het hele noodpakket om te lezen of te printen
"""
import csv, hashlib, html, json, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from bouw_import import NOTETYPE, DECK  # noqa: E402
from bouw_colleges import WEG_AFBEELDINGEN  # noqa: E402

ADDON_DATA = ROOT / 'campagne-addon' / 'data'
VERWERKING = ROOT / 'verwerking'
NOOD_DECK = 'GZC III - Noodpakket'
THEMA_VOLGORDE = ['T1', 'T2', 'T3', 'T4', 'B1', 'B2', 'B3']
KOP = '#separator:tab\n#html:true\n#guid column:1\n#notetype column:2\n#deck column:3\n#tags column:6\n'
esc = html.escape


def deck_stand():
    """guid → (voorkant, achterkant, tags) over de drie imports, zonder dubbel/verwijderen; de laatste versie wint."""
    rij = {}
    for naam in ('GZC3_check_import.txt', 'GZC3_extra_import.txt', 'GZC3_colleges_import.txt'):
        with open(ROOT / naam, encoding='utf-8') as fh:
            for r in csv.reader((l for l in fh if not l.startswith('#')), delimiter='\t'):
                rij[r[0]] = (r[3], r[4], r[5].split())
    koppeling = json.loads((ADDON_DATA / 'koppeling.json').read_text(encoding='utf-8'))
    uit = {}
    for g, (v, a, t) in rij.items():
        if {'check::dubbel', 'check::verwijderen'} & set(t):
            continue
        college = koppeling.get(g) or next((x[9:] for x in t if x.startswith('college::')), None)
        uit[g] = dict(voor=v, achter=a, tags=t, college=college,
                      thema_tags=[x for x in t if re.match(r'GZC3::[AB]::', x)])
    return uit


def guid(prefix, *delen):
    return prefix + hashlib.sha1('|'.join(delen).encode()).hexdigest()[:10]


def schrijf(pad, rijen):
    with open(pad, 'w', newline='', encoding='utf-8') as fh:
        fh.write(KOP)
        csv.writer(fh, delimiter='\t', lineterminator='\n').writerows(rijen)


# ------------------------------------------------------------------ noodpakket
def noodpakket(deck):
    data = json.loads((VERWERKING / 'nood.json').read_text(encoding='utf-8'))
    samenvattingen, kaarten = {}, []
    for groep in data['groepen']:
        for s in groep['samenvattingen']:
            samenvattingen[s['thema'].upper()] = s['punten']
        kaarten += groep['kaarten']
    rijen, guids, gezien, onbekend = [], [], set(), []
    for k in kaarten:
        th = k['thema'].upper()
        sleutel = re.sub(r'\W+', ' ', k['voor'].lower()).strip()
        if sleutel in gezien:
            continue
        gezien.add(sleutel)
        bronnen = [b for b in k['bron_guids'] if b in deck]
        onbekend += [b for b in k['bron_guids'] if b not in deck]
        college = k.get('college') if k.get('college') not in (None, '', '?') else next(
            (deck[b]['college'] for b in bronnen if deck[b]['college']), None)
        g = guid('gzc3n-', k['voor'])
        tags = ['GZC3::noodpakket', f'nood::{th}'] + ([f'nood::{college}'] if college else [])
        achter = esc(k['achter']) + f'<div style="font-size:11px;opacity:.5;margin-top:8px">🚨 noodpakket · {th}{" · " + college if college else ""}</div>'
        rijen.append([g, NOTETYPE, NOOD_DECK, esc(k['voor']), achter, ' '.join(tags)])
        guids.append(g)
        k['_college'] = college
    rijen.sort(key=lambda r: (THEMA_VOLGORDE.index(r[5].split()[1][6:]) if r[5].split()[1][6:] in THEMA_VOLGORDE else 9))
    schrijf(ADDON_DATA / 'GZC3_nood_import.txt', rijen)
    (ADDON_DATA / 'nood.json').write_text(json.dumps({'samenvattingen': samenvattingen, 'guids': guids}, ensure_ascii=False, indent=1),
                                          encoding='utf-8')
    # leesversie
    regels = ['# Noodpakket GZC III', '',
              'Voor als je in tijdnood komt: per thema de samenvatting en de essentiekaarten. In Anki staat dit als apart deck *GZC III - Noodpakket*.', '']
    for th in THEMA_VOLGORDE:
        regels += [f'## {th}', '']
        regels += [f'- {p}' for p in samenvattingen.get(th, [])]
        ks = [k for k in kaarten if k['thema'].upper() == th]
        if ks:
            regels += ['', '| Vraag | Antwoord |', '|---|---|']
            regels += [f'| {k["voor"]} | {k["achter"]} |' for k in ks]
        regels.append('')
    (ROOT / 'noodpakket.md').write_text('\n'.join(regels), encoding='utf-8')
    per = {th: sum(1 for r in rijen if f'nood::{th}' in r[5].split()) for th in THEMA_VOLGORDE}
    print('noodpakket:', len(rijen), 'kaarten', per, '| onbekende bron-guids:', len(set(onbekend)))
    return len(rijen)


# ------------------------------------------------------------------ afbeeldingen
def bronnaam(url):
    host = re.sub(r'^https?://(www\.)?([^/]+).*', r'\2', url or '')
    return {'commons.wikimedia.org': 'Wikimedia Commons', 'upload.wikimedia.org': 'Wikimedia Commons', 'openstax.org': 'OpenStax',
            'smart.servier.com': 'Servier Medical Art', 'radiopaedia.org': 'Radiopaedia', 'openi.nlm.nih.gov': 'Open-i (NLM)',
            'phil.cdc.gov': 'CDC PHIL', 'webpath.med.utah.edu': 'WebPath (Utah)', 'imagebank.hematology.org': 'ASH Image Bank',
            'ncbi.nlm.nih.gov': 'NCBI'}.get(host, host)


def beelden(deck):
    data = json.loads((VERWERKING / 'beelden.json').read_text(encoding='utf-8'))
    doel = ADDON_DATA / 'beelden'
    if doel.exists():
        shutil.rmtree(doel)
    doel.mkdir(parents=True)
    lijst, herken, herken_guids = [], [], []
    for b in data['beelden']:
        bron = ROOT / 'beelden' / b['bestand']
        if not bron.exists():
            sys.exit(f'ontbreekt: {bron}')
        naam = 'gzc3_' + b['bestand']
        shutil.copy(bron, doel / naam)
        guids = [g for g in b['guids'] if g in deck]
        if len(guids) < len(b['guids']):
            print('  onbekende guid(s) weggelaten bij', b['bestand'], set(b['guids']) - set(guids))
        item = dict(bestand=naam, bijschrift=b['bijschrift'], auteur=b.get('auteur', ''), licentie=b.get('licentie', ''),
                    bron=bronnaam(b.get('bron_url')), bron_url=b.get('bron_url', ''), guids=guids)
        lijst.append(item)
        hk = b.get('herken_kaart')
        if hk and hk.get('voor') and hk.get('achter'):
            eerste = next((deck[g] for g in guids), None)
            tags = ['soort::beeld', 'bron::afbeelding', 'check::nieuw'] + (eerste['thema_tags'] if eerste else [])
            if eerste and eerste['college']:
                tags.append(f'college::{eerste["college"]}')
            if eerste and 'prio::tentamen' in eerste['tags']:
                tags.append('prio::tentamen')
            g = guid('gzc3b-', naam)
            img = f'<img src="{esc(naam)}" style="max-width:100%;max-height:440px;border-radius:6px">'
            bronregel = ' · '.join(x for x in (item['auteur'], item['licentie'], item['bron']) if x)
            herken.append([g, NOTETYPE, DECK, f'🔬 {esc(hk["voor"])}<br>{img}',
                           f'{esc(hk["achter"])}<div style="font-size:13px;opacity:.8;margin-top:8px">{esc(b["bijschrift"])}</div>'
                           f'<div style="font-size:10px;opacity:.55">{esc(bronregel)}</div>', ' '.join(dict.fromkeys(tags))])
            herken_guids.append(g)
    schrijf(ADDON_DATA / 'GZC3_beelden_import.txt', herken)
    # webafbeeldingen die niet kloppen of offline niet werken: weg (alleen als het om een bekende kaart gaat)
    weg = {}
    for g, n in deck.items():
        srcs = re.findall(r'<img[^>]*src=""?([^" >]+)', n['achter'])
        fout = [s for s in srcs if any(w in s for w in WEG_AFBEELDINGEN)]
        if fout:
            weg[g] = fout
    met_beeld = {g for b in lijst for g in b['guids']}
    for g, n in deck.items():  # webafbeelding vervangen door een lokale afbeelding op dezelfde kaart
        if g in met_beeld:
            weg.setdefault(g, []).extend(s for s in re.findall(r'<img[^>]*src=""?(https?://[^" >]+)', n['achter']) if s not in weg.get(g, []))
    versie = hashlib.sha1(json.dumps([lijst, herken_guids, weg], sort_keys=True).encode()).hexdigest()[:10]
    (ADDON_DATA / 'beelden.json').write_text(json.dumps({'versie': versie, 'beelden': lijst, 'herken_guids': herken_guids, 'weg': weg},
                                                        ensure_ascii=False, indent=1), encoding='utf-8')
    kb = sum(p.stat().st_size for p in doel.iterdir()) // 1024
    print(f'afbeeldingen: {len(lijst)} ({kb} kB) op {len(met_beeld)} kaarten · {len(herken)} herkenkaarten · '
          f'{sum(map(len, weg.values()))} webafbeeldingen weg · versie {versie}')
    return lijst


def main():
    deck = deck_stand()
    if (VERWERKING / 'nood.json').exists():
        noodpakket(deck)
    if (VERWERKING / 'beelden.json').exists():
        beelden(deck)


if __name__ == '__main__':
    main()
