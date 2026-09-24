"""Bouwt de speelse uitbreiding: casus-, schema- en tabelkaarten, ezelsbruggen en de quizdata.

Invoer : anki-check/GZC3_check_import.txt (de check van eerder), werk/col.db, anki-check/extra_inhoud.py
Uitvoer: anki-check/GZC3_extra_import.txt, anki-check/quiz/vragen.json, anki-check/schemas/*.svg
"""
import csv, hashlib, html, json, pathlib, random, sqlite3, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'anki-check'))
import extra_inhoud as X  # noqa: E402
from bouw_import import DUBBEL, VERWIJDEREN, NOTETYPE, DECK  # noqa: E402

OUT = ROOT / 'anki-check'
THEMA_TAG = {
    'T1': 'GZC3::A::T1-benigne-hematologie', 'T2': 'GZC3::A::T2-maligne-hematologie',
    'T3': 'GZC3::A::T3-groepsspecifiek', 'T4': 'GZC3::A::T4-orgaanspecifiek',
    'B1': 'GZC3::B::B1-public-health', 'B2': 'GZC3::B::B2-revalidatie', 'B3': 'GZC3::B::B3-pijn-palliatief',
}
THEMA_NAAM = {
    'T1': 'Benigne hematologie', 'T2': 'Maligne hematologie', 'T3': 'Kind, AYA en geriatrie',
    'T4': 'Hoofd-hals, schildklier en oog', 'B1': 'Public health', 'B2': 'Revalidatie en psychosociaal',
    'B3': 'Pijn en palliatieve zorg',
}
esc = html.escape


def guid(*parts):
    return 'gzc3x-' + hashlib.sha1('|'.join(parts).encode()).hexdigest()[:12]


# ------------------------------------------------------------------ SVG
FILL, STROKE, INK = '#eef2f7', '#5b6b82', '#1b2430'
LABEL_FILL = '#f7f7f4'
Q_FILL, Q_STROKE = '#ffd57a', '#b87a00'


def box_text(x, y, w, h, text, fs=None):
    lines = text.split('\n')
    longest = max(len(l) for l in lines)
    fs = fs or max(10, min(15, int((w - 14) / (0.56 * max(longest, 1)))))
    lh = fs * 1.22
    top = y + h / 2 - lh * (len(lines) - 1) / 2 + fs * 0.35
    return ''.join(f'<text x="{x + w / 2:.0f}" y="{top + i * lh:.1f}" font-size="{fs}" text-anchor="middle" fill="{INK}">{esc(l)}</text>'
                   for i, l in enumerate(lines))


def anchors(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
    dx, dy = bcx - acx, bcy - acy
    if abs(dy) >= abs(dx) * 0.45:
        lo, hi = max(ax, bx), min(ax + aw, bx + bw)
        x1 = x2 = (lo + hi) / 2 if hi - lo > 20 else None
        if x1 is None:
            x1, x2 = acx, bcx
        return (x1, ay + ah if dy > 0 else ay), (x2, by if dy > 0 else by + bh)
    lo, hi = max(ay, by), min(ay + ah, by + bh)
    y1 = y2 = (lo + hi) / 2 if hi - lo > 14 else None
    if y1 is None:
        y1, y2 = acy, bcy
    return (ax + aw if dx > 0 else ax, y1), (bx if dx > 0 else bx + bw, y2)


def svg(schema, verborgen=None):
    sid = schema['id'] + (verborgen or '')
    boxes = {b[0]: b for b in schema['boxes']}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {schema["w"]} {schema["h"]}" '
             f'style="width:100%;max-width:{schema["w"]}px;height:auto;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif">',
             f'<defs><marker id="p{sid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{STROKE}"/></marker></defs>',
             f'<rect x="0" y="0" width="{schema["w"]}" height="{schema["h"]}" rx="12" fill="#ffffff"/>']
    for van, naar, soort in schema['arrows']:
        (x1, y1), (x2, y2) = anchors(boxes[van][1:5], boxes[naar][1:5])
        if soort == '-|':  # dwarsstreep net vóór het vak, anders valt hij eronder
            import math
            d = math.hypot(x2 - x1, y2 - y1) or 1
            x2, y2 = x2 - 7 * (x2 - x1) / d, y2 - 7 * (y2 - y1) / d
        extra = f' marker-end="url(#p{sid})"' if soort == '->' else ''
        parts.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{STROKE}" stroke-width="2"{extra}/>')
        if soort == '-|':  # remmende pijl: dwarsstreep
            import math
            ang = math.atan2(y2 - y1, x2 - x1) + math.pi / 2
            ox, oy = 9 * math.cos(ang), 9 * math.sin(ang)
            parts.append(f'<line x1="{x2 - ox:.0f}" y1="{y2 - oy:.0f}" x2="{x2 + ox:.0f}" y2="{y2 + oy:.0f}" stroke="{STROKE}" stroke-width="3"/>')
    for bid, x, y, w, h, text, uitleg in schema['boxes']:
        if bid == verborgen:
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{Q_FILL}" stroke="{Q_STROKE}" stroke-width="2.5"/>')
            parts.append(box_text(x, y, w, h, '?', fs=min(26, h - 8)))
        else:
            fill = FILL if uitleg else LABEL_FILL
            dash = '' if uitleg else ' stroke-dasharray="4 3"'
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{STROKE}" stroke-width="1.5"{dash}/>')
            parts.append(box_text(x, y, w, h, text))
    parts.append('</svg>')
    return ''.join(parts)


# ------------------------------------------------------------------ tabellen
TD = 'border:1px solid #9aa6b8;padding:6px 8px;vertical-align:top;'


def tabel(t, vr=None, vk=None):
    head = ''.join(f'<th style="{TD}background:#dfe6f0">{esc(k)}</th>' for k in t['kolommen'])
    body = []
    for ri, (rij, cellen) in enumerate(t['rijen']):
        tds = []
        for ki, c in enumerate(cellen):
            if (ri, ki) == (vr, vk):
                tds.append(f'<td style="{TD}background:{Q_FILL};font-weight:bold;text-align:center">?</td>')
            else:
                tds.append(f'<td style="{TD}">{esc(c)}</td>')
        body.append(f'<tr><th style="{TD}background:#eef2f7;text-align:left">{esc(rij)}</th>{"".join(tds)}</tr>')
    return (f'<table style="border-collapse:collapse;background:#fff;color:{INK};font-size:0.85em;margin:auto">'
            f'<tr><th style="{TD}background:#dfe6f0"></th>{head}</tr>{"".join(body)}</table>')


def main():
    random.seed(7)
    con = sqlite3.connect(ROOT / 'werk' / 'col.db')
    n2guid = {n: g for n, (g,) in enumerate(con.execute('select guid from notes order by id'), start=1)}
    basis = {r[0]: r for r in csv.reader((l for l in open(OUT / 'GZC3_check_import.txt', encoding='utf-8') if not l.startswith('#')), delimiter='\t')}

    rows, quiz, tel = [], [], {}

    def add(g, voor, achter, tags, soort):
        tel[soort] = tel.get(soort, 0) + 1
        rows.append([g, NOTETYPE, DECK, voor, achter, ' '.join(tags)])

    # 4. ezelsbruggen: volledige bestaande notitie met aangevulde achterkant
    for n, brug in X.EZELSBRUG.items():
        assert n not in DUBBEL and n not in VERWIJDEREN, n
        g = n2guid[n]
        r = basis[g]
        achter = r[4] + f'<br><br><span style="background:#fff3c4;color:#5a4300;padding:2px 6px;border-radius:6px">💡 {esc(brug)}</span>'
        add(g, r[3], achter, r[5].split() + ['vorm::ezelsbrug'], 'ezelsbrug')

    # 1. wie ben ik?
    groepen = {}
    for c in X.CASUS:
        groepen.setdefault(c[1], []).append(c)
    for i, (thema, groep, vignet, diagnose, waarom) in enumerate(X.CASUS):
        voor = f'<div style="font-size:0.8em;color:#6b7686">🕵️ Wie ben ik?</div>{esc(vignet)}'
        achter = f'<b>{esc(diagnose)}</b><br>{esc(waarom)}'
        add(guid('casus', diagnose, vignet[:30]), voor, achter, [THEMA_TAG[thema], 'check::nieuw', 'vorm::casus', 'prio::tentamen'], 'casus')
        pool = [c[3] for c in groepen[groep] if c[3] != diagnose]
        if len(pool) < 3:
            pool += [c[3] for c in X.CASUS if c[0] == thema and c[3] != diagnose and c[3] not in pool]
        quiz.append(dict(id=f'c{i}', thema=thema, soort='Wie ben ik?', vraag=vignet,
                         opties=[diagnose] + random.sample(pool, 3), uitleg=waarom))

    # 2. schema-occlusie
    (OUT / 'schemas').mkdir(exist_ok=True)
    for s in X.SCHEMAS:
        (OUT / 'schemas' / f'{s["id"]}.svg').write_text(svg(s))
        for bid, *_r, tekst, uitleg in s['boxes']:
            if not uitleg:
                continue
            voor = (f'<div style="font-size:0.8em;color:#6b7686">🧩 Schema</div><b>{esc(s["titel"])}</b><br>'
                    f'Wat hoort op de plek van het <span style="background:{Q_FILL};padding:0 6px;border-radius:4px">?</span><br><br>{svg(s, bid)}')
            achter = f'<b>{esc(tekst.replace(chr(10), " "))}</b><br>{esc(uitleg)}'
            add(guid('schema', s['id'], bid), voor, achter, [THEMA_TAG[s['thema']], 'check::nieuw', 'vorm::schema'], 'schema')

    # 3. vergelijkingstabellen
    for t in X.TABELLEN:
        k = len(t['kolommen'])
        for ri, (rij, cellen) in enumerate(t['rijen']):
            for ki, cel in enumerate(cellen):
                kol = t['kolommen'][ki]
                vraagtekst = f'{rij} bij {kol}' if k > 1 else f'{t["kolommen"][0]} bij {rij}'
                voor = (f'<div style="font-size:0.8em;color:#6b7686">📊 Vergelijk</div><b>{esc(t["titel"])}</b><br>'
                        f'Vul in: <i>{esc(vraagtekst)}</i><br><br>{tabel(t, ri, ki)}')
                add(guid('tabel', t['id'], str(ri), str(ki)), voor, f'<b>{esc(cel)}</b>',
                    [THEMA_TAG[t['thema']], 'check::nieuw', 'vorm::vergelijking'], 'vergelijking')
                if k >= 3:
                    opties = [cel] + [c for j, c in enumerate(cellen) if j != ki]
                    vraag = f'{t["titel"]} — {rij}: wat past bij {kol}?'
                elif k == 2:
                    opties = [kol] + [c for c in t['kolommen'] if c != kol]
                    vraag = f'{t["titel"]} — bij welke hoort „{cel}” ({rij.lower()})?'
                else:
                    anderen = [c[0] for j, (_, c) in enumerate(t['rijen']) if j != ri]
                    opties = [cel] + random.sample(anderen, 3)
                    vraag = f'Welke translocatie hoort bij: {rij}?'
                quiz.append(dict(id=f't{t["id"]}{ri}{ki}', thema=t['thema'], soort='Vergelijk', vraag=vraag,
                                 opties=opties[:4], uitleg=f'{kol if k > 1 else rij}: {cel}.'))

    # 6. losse tentamenvragen
    for i, (thema, vraag, opties, uitleg) in enumerate(X.QUIZ_EXTRA):
        quiz.append(dict(id=f'q{i}', thema=thema, soort='Tentamenvraag', vraag=vraag, opties=opties, uitleg=uitleg))

    with open(OUT / 'GZC3_extra_import.txt', 'w', newline='', encoding='utf-8') as fh:
        fh.write('#separator:tab\n#html:true\n#guid column:1\n#notetype column:2\n#deck column:3\n#tags column:6\n')
        csv.writer(fh, delimiter='\t', lineterminator='\n').writerows(rows)
    (OUT / 'quiz').mkdir(exist_ok=True)
    (OUT / 'quiz' / 'vragen.json').write_text(json.dumps(dict(themas=THEMA_NAAM, vragen=quiz), ensure_ascii=False, indent=1))
    sjabloon = (OUT / 'quiz' / 'sjabloon.html').read_text()
    data = json.dumps(dict(themas=THEMA_NAAM, vragen=quiz), ensure_ascii=False).replace('</', '<\\/')
    (OUT / 'quiz' / 'index.html').write_text(sjabloon.replace('/*DATA*/null', data))
    print(tel, 'quizvragen:', len(quiz), {t: sum(q['thema'] == t for q in quiz) for t in THEMA_NAAM})


if __name__ == '__main__':
    main()
