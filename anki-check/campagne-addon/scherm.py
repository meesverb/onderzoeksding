"""Campagne GZC III — weergave: hoofdscherm, collegevenster en het HUD tijdens het leren.
Alleen HTML, CSS en JavaScript; geen Anki-imports, zodat het buiten Anki te testen is.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import random

from .campagne import (COLLEGEDATA, COLLEGES, CAMPAGNE_VOLGORDE, EXTRA, THEMAS, VERANKERD_IVL, XP_COLLEGE, XP_EXTRA,
                       XP_QUIZVRAAG, kort, label)

CSS = """
.gz{--bg:#fbf9fd;--kaart:#ffffff;--ink:#221a2e;--zacht:#6b6278;--lijn:#e4dcec;--hema:#5b3f8c;--hema-z:#ece5f6;
--eos:#d9577a;--eos-z:#fbe6ec;--goed:#1f8a4c;--goed-z:#e2f4e9;--brons:#a8642a;--zilver:#7d8794;--goud:#c49a1a;--goud-z:#fbf1cf;
color:var(--ink);text-align:left;font-family:-apple-system,"Segoe UI",Roboto,sans-serif;font-size:14px;line-height:1.45}
:root.night-mode .gz,.nightMode .gz{--bg:#1b1622;--kaart:#241d2e;--ink:#efe9f6;--zacht:#a79cb6;--lijn:#3a3047;--hema:#b69ae6;--hema-z:#2f2642;
--eos:#f08aa6;--eos-z:#3a2230;--goed:#5fd08f;--goed-z:#193426;--brons:#d89a62;--zilver:#b6bfca;--goud:#e8c454;--goud-z:#3a3118}
#gzc3{max-width:820px;margin:18px auto 8px;padding:16px;border-radius:16px;background:var(--bg);border:1px solid var(--lijn)}
.gz *{box-sizing:border-box}
.gz .kop{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
.gz h2{margin:0;font-size:20px;letter-spacing:-.01em}
.gz h3{margin:14px 0 4px;font-size:14px}
.gz .sub{color:var(--zacht);font-size:13px}
.gz .aftel{text-align:right}
.gz .aftel b{font-size:28px;color:var(--eos);font-variant-numeric:tabular-nums;line-height:1}
.gz .rij{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-top:14px}
.gz .blok{background:var(--kaart);border:1px solid var(--lijn);border-radius:12px;padding:12px}
.gz .label{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--zacht);font-weight:600;margin-bottom:6px}
.gz .lvl{display:flex;align-items:baseline;gap:8px}
.gz .lvl b{font-size:26px;color:var(--hema)}
.gz .balk{height:8px;border-radius:99px;background:var(--lijn);overflow:hidden;margin-top:6px}
.gz .balk span{display:block;height:100%;background:var(--hema)}
.gz .quest{display:grid;grid-template-columns:62px 1fr auto;gap:8px;align-items:center;padding:5px 0;border-top:1px dashed var(--lijn)}
.gz .quest:first-of-type{border-top:0}
.gz .medaille{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;border-radius:99px;padding:2px 8px;text-align:center;border:1.5px solid}
.gz .Brons{color:var(--brons)}.gz .Zilver{color:var(--zilver)}.gz .Goud{color:var(--goud)}
.gz .quest.af .medaille{background:currentColor}.gz .quest.af .medaille i{color:var(--kaart)}
.gz .medaille i{font-style:normal}
.gz .quest .st{font-variant-numeric:tabular-nums;color:var(--zacht);font-size:13px}
.gz .quest.af .st{color:var(--goed);font-weight:600}
.gz .klein{font-size:12px;color:var(--zacht);font-variant-numeric:tabular-nums}
.gz .missie{display:flex;align-items:center;gap:10px;padding:7px 0;border-top:1px dashed var(--lijn)}
.gz .missie:first-of-type{border-top:0}
.gz .missie .wat{flex:1;min-width:0}
.gz .missie.gedaan .wat b{color:var(--zacht);text-decoration:line-through}
.gz .ster{color:var(--goud);letter-spacing:1px;font-size:13px}
.gz .ster .leeg{color:var(--lijn)}
.gz .knoppen{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.gz button{font:inherit;font-size:13px;font-weight:600;border-radius:9px;padding:7px 12px;cursor:pointer;border:1.5px solid var(--hema);background:var(--hema);color:var(--kaart)}
.gz button.licht{background:transparent;color:var(--hema)}
.gz button.klein{padding:3px 9px;font-size:12px}
.gz button:disabled{opacity:.4;cursor:default}
.gz .vink{display:inline-flex;gap:6px;align-items:center;cursor:pointer;font-size:12px;color:var(--zacht);white-space:nowrap}
.gz .vink input{accent-color:var(--hema);margin:0}
.gz .badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
.gz .badge{display:inline-flex;gap:5px;align-items:center;border-radius:99px;padding:3px 10px;border:1px solid var(--lijn);font-size:12px;background:var(--kaart)}
.gz .badge.nee{opacity:.42;filter:grayscale(1)}
.gz .chip{display:inline-block;border-radius:99px;padding:2px 9px;font-size:12px;font-weight:600}
.gz .chip.ok{background:var(--goed-z);color:var(--goed)}.gz .chip.nok{background:var(--eos-z);color:var(--eos)}
.gz .chip.paars{background:var(--hema-z);color:var(--hema)}
.gz details{margin-top:12px}.gz summary{cursor:pointer;color:var(--hema);font-weight:600}
/* installatie */
.gz .install{border-color:var(--eos);background:linear-gradient(0deg,var(--kaart),var(--eos-z))}
.gz .stap{display:grid;grid-template-columns:22px 1fr auto;gap:8px;align-items:center;padding:5px 0;border-top:1px dashed var(--lijn)}
.gz .stap:first-of-type{border-top:0}
.gz .stap.klaar .wat b{color:var(--zacht)}
.gz .stap .vk{font-size:15px;text-align:center}
/* werkdruk */
.gz .week{display:flex;gap:6px;align-items:flex-end;height:58px;margin-top:6px}
.gz .week div{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;font-size:11px;color:var(--zacht)}
.gz .week span{display:block;width:100%;border-radius:5px 5px 2px 2px;background:var(--hema);opacity:.75;min-height:2px}
.gz .week div:first-child span{opacity:1;background:var(--eos)}
/* wereldkaart */
.gz .wereld{background:var(--kaart);border:1px solid var(--lijn);border-radius:12px;padding:10px 12px;margin-top:10px}
.gz .wereld.vandaag{border-color:var(--eos);box-shadow:0 0 0 2px var(--eos-z)}
.gz .wereld.verslagen{background:var(--goed-z)}
.gz .baaskop{display:grid;grid-template-columns:34px 1fr minmax(150px,220px);gap:10px;align-items:center}
.gz .baaskop .ic{font-size:26px;text-align:center}
.gz .hp{height:7px;border-radius:99px;background:var(--lijn);overflow:hidden;margin:3px 0}
.gz .hp span{display:block;height:100%;background:var(--eos)}
.gz .wereld.verslagen .hp span{background:var(--goed)}
.gz .pad{position:relative;display:flex;flex-wrap:wrap;gap:10px 14px;margin-top:10px;padding-left:4px}
.gz .node{position:relative;display:flex;flex-direction:column;align-items:center;gap:1px;background:none;border:0;padding:0;color:var(--ink);cursor:pointer;width:46px}
.gz .node .bol{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;
 border:2px solid var(--hema);background:var(--kaart);color:var(--hema);transition:transform .12s}
.gz .node:hover .bol{transform:scale(1.08)}
.gz .node.slot .bol{border-color:var(--lijn);color:var(--zacht);background:var(--bg)}
.gz .node.slot .bol::after{content:"🔒";position:absolute;top:-4px;right:-2px;font-size:11px}
.gz .node.s2 .bol{background:var(--hema);color:var(--kaart)}
.gz .node.s3 .bol{background:var(--goud);border-color:var(--goud);color:#3a2a00}
.gz .node.extra .bol{border-radius:10px;width:36px;height:36px;font-size:11px}
.gz .node.vandaag .bol{box-shadow:0 0 0 3px var(--eos-z),0 0 0 5px var(--eos)}
.gz .node .ster{font-size:10px;line-height:1}
/* album */
.gz .album{display:grid;grid-template-columns:repeat(auto-fill,minmax(64px,1fr));gap:8px;margin-top:6px}
.gz .tegel{background:var(--kaart);border:1px solid var(--lijn);border-radius:10px;padding:6px 4px;text-align:center;cursor:pointer;font:inherit;color:var(--ink)}
.gz .tegel .em{font-size:24px;line-height:1.2}
.gz .tegel .nm{font-size:10px;line-height:1.2;color:var(--zacht);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.gz .tegel.nee .em{filter:grayscale(1) brightness(.2);opacity:.35}
.gz .tegel.ja{border-color:var(--goud);background:var(--goud-z)}
/* collegevenster */
body.gz{margin:0;background:var(--bg)}
.gz .venster{max-width:760px;margin:0 auto;padding:18px 20px 30px}
.gz .kern{border-left:4px solid var(--hema);background:var(--hema-z);border-radius:0 10px 10px 0;padding:10px 12px;margin:12px 0}
.gz .venster ul{margin:4px 0 8px;padding-left:20px}
.gz .venster li{margin:2px 0}
.gz .valkuil{background:var(--eos-z);border-radius:10px;padding:8px 12px;margin-top:8px}
.gz .tip{background:var(--goud-z);border-radius:10px;padding:8px 12px;margin-top:8px}
.gz .citaten{margin-top:10px}
.gz .citaten blockquote{margin:6px 0;padding:6px 12px;border-left:3px solid var(--lijn);font-style:italic}
.gz .vraag{background:var(--kaart);border:1px solid var(--lijn);border-radius:12px;padding:12px;margin-top:10px}
.gz .opties{display:grid;gap:6px;margin-top:8px}
.gz .optie{text-align:left;font-weight:500;background:var(--bg);color:var(--ink);border:1.5px solid var(--lijn)}
.gz .optie.goed{border-color:var(--goed);background:var(--goed-z)}
.gz .optie.fout{border-color:var(--eos);background:var(--eos-z)}
.gz .uitleg{display:none;margin-top:8px;font-size:13px;color:var(--zacht)}
.gz .vraag.klaar .uitleg{display:block}
.gz .grootcel{display:flex;gap:14px;align-items:center;background:var(--kaart);border:1px solid var(--lijn);border-radius:14px;padding:12px;margin-top:10px}
.gz .grootcel .em{font-size:44px}
.gz .grootcel.nee .em{filter:grayscale(1) brightness(.2);opacity:.35}
.gz .grootcel.ja{border-color:var(--goud);background:var(--goud-z)}
.gz .score{font-size:18px;font-weight:700;color:var(--hema);margin-top:10px}
"""


DAGEN = ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo']


def _e(s) -> str:
    return html.escape(str(s))


def sterren_html(n: int) -> str:
    return f'<span class="ster">{"★" * n}<span class="leeg">{"★" * (3 - n)}</span></span>'


def _cmd(cmd: str) -> str:
    return f'onclick="pycmd(\'{cmd}\');return false;"'


# ------------------------------------------------------------------ hoofdscherm
def _missie(s: dict, k: str) -> str:
    af = k in s['afgevinkt']
    xp = XP_COLLEGE if k in COLLEGES else XP_EXTRA
    pc = s['per_college'].get(k)
    extra = ''
    if pc and pc['nieuw']:
        extra = f' · {"🔓" if af or not s["slot"] else "🔒"} {pc["nieuw"]} nieuwe kaarten'
    elif pc and pc['n']:
        extra = f' · alle {pc["n"]} kaarten gezien'
    st = sterren_html(s['colleges'][k]['sterren']) + ' ' if k in COLLEGES else ''
    open_knop = f'<button class="licht klein" {_cmd("gzc3:college:" + k)}>📖 Open</button>' if k in COLLEGES else ''
    return (f'<div class="missie{" gedaan" if af else ""}"><div class="wat"><b>{_e(label(k))}</b><div class="klein">{st}+{xp} XP{extra}</div></div>'
            f'{open_knop}<label class="vink"><input type="checkbox" {"checked" if af else ""} {_cmd("gzc3:vink:" + k)}> gedaan</label></div>')


def _installatie(stappen: list[dict]) -> str:
    if not stappen or all(st['klaar'] for st in stappen):
        return ''
    rijen = ''.join(
        f'<div class="stap{" klaar" if st["klaar"] else ""}"><span class="vk">{"✅" if st["klaar"] else "⬜"}</span>'
        f'<div class="wat"><b>{_e(st["label"])}</b><div class="klein">{_e(st["uitleg"])}</div></div>'
        + ('' if st['klaar'] else f'<button class="klein" {"" if st["kan"] else "disabled"} {_cmd("gzc3:install:" + st["id"])}>{_e(st["knop"])}</button>')
        + '</div>' for st in stappen)
    n = sum(st['klaar'] for st in stappen)
    return (f'<div class="blok install" style="margin-top:12px"><div class="label">Installatiecheck · {n}/{len(stappen)} klaar · '
            f'dit blok verdwijnt als alles klaar is</div>{rijen}</div>')


def _wereld(s: dict, th: str) -> str:
    naam, baas, icoon = THEMAS[th]
    b = next((b for b in s['bazen'] if b['id'] == th), None)
    items = [k for k, v in COLLEGES.items() if v[0] == th] + [k for k, v in EXTRA.items() if v[0] == th]
    vandaag = set(s['plan_vandaag'][1])
    nodes = []
    for k in items:
        af = k in s['afgevinkt']
        if k in COLLEGES:
            c = s['colleges'][k]
            pc = s['per_college'].get(k)
            klasse = 'slot' if s['slot'] and not af else ('s3' if c['sterren'] == 3 else ('s2' if c['sterren'] == 2 else ''))
            tip = f'{label(k)} — {sterren_tekst(c["sterren"])}' + (f' · {pc["gezien"]}/{pc["n"]} kaarten gezien' if pc and pc['n'] else '')
            nodes.append(f'<button class="node {klasse}{" vandaag" if k in vandaag else ""}" title="{_e(tip)}" {_cmd("gzc3:college:" + k)}>'
                         f'<span class="bol">{_e(kort(k))}</span>{sterren_html(c["sterren"])}</button>')
        else:
            nodes.append(f'<button class="node extra{" s2" if af else ""}{" vandaag" if k in vandaag else ""}" title="{_e(label(k))}{" ✓" if af else ""}" '
                         f'{_cmd("gzc3:vink:" + k)}><span class="bol">{_e(k)}</span><span class="ster">{"✓" if af else ""}</span></button>')
    if b:
        status = 'verslagen' if b['status'] == 'verslagen' else f'{b["hp"]} HP'
        info = (f'<div class="hp"><span style="width:{b["hp"]}%"></span></div><div class="klein">{status} · gezien {b["gezien"]}/{b["n"]} · '
                f'verankerd {b["verankerd"]}' + (f' · {b["retentie"]}% goed' if b['retentie'] is not None else '') + '</div>')
        klasse = (' verslagen' if b['status'] == 'verslagen' else '') + (' vandaag' if b['vandaag'] else '')
    else:
        info, klasse = '<div class="klein">nog geen kaarten</div>', ''
    ic = '🏆' if b and b['status'] == 'verslagen' else icoon
    return (f'<div class="wereld{klasse}"><div class="baaskop"><div class="ic">{ic}</div><div><b>{_e(baas)}</b>'
            f'<div class="klein">{th} · {_e(naam)}</div></div><div>{info}</div></div><div class="pad">{"".join(nodes)}</div></div>')


def sterren_tekst(n: int) -> str:
    return ['nog niet gedaan', '★ afgevinkt', '★★ alle kaarten gezien', '★★★ verankerd'][n] if n < 4 else ''


def weergave(s: dict, stappen: list[dict] | None = None) -> str:
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
    lijst = ''.join(_missie(s, k) for k in items)
    if s['achterstand']:
        lijst += '<div class="label" style="margin-top:10px">Inhalen</div>' + ''.join(_missie(s, k) for k in s['achterstand'][:6])
        if len(s['achterstand']) > 6:
            lijst += f'<div class="klein">en nog {len(s["achterstand"]) - 6} — zie de wereldkaart hieronder</div>'
    if not lijst:
        lijst = '<div class="klein">Geen colleges gepland: inhaal- of herhaaldag.</div>'

    knoppen = []
    if s['fase'] == 1 and s['doel_nieuw'] and not s['limiet_vandaag']:
        knoppen.append(f'<button {_cmd("gzc3:limiet")}>Zet vandaag {s["doel_nieuw"]} nieuwe kaarten klaar</button>')
    if s['fout_recent']:
        knoppen.append(f'<button class="licht" {_cmd("gzc3:herkansing")}>🔁 Herkansing: {s["fout_recent"]} kaarten die je net fout had</button>')
    if not s['slot']:
        knoppen.append(f'<button class="licht" {_cmd("gzc3:start")}>▶ Campagne starten: kaarten vrijspelen per college</button>')

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

    week = s['werkdruk']
    hoogste = max(week) or 1
    labels = ['vand.', 'morgen'] + [DAGEN[(s['vandaag'] + dt.timedelta(days=i)).weekday()] for i in range(2, 7)]
    werkdruk = ''.join(f'<div title="{n} herhalingen"><b style="font-size:11px;color:var(--ink)">{n}</b>'
                       f'<span style="height:{max(3, round(40 * n / hoogste))}px"></span>{lab}</div>' for n, lab in zip(week, labels))

    werelden = ''.join(_wereld(s, th) for th in CAMPAGNE_VOLGORDE)
    ots = ''.join(f'<button class="node extra{" s2" if k in s["afgevinkt"] else ""}{" vandaag" if k in items else ""}" title="{_e(v[1])}" '
                  f'{_cmd("gzc3:vink:" + k)}><span class="bol">{_e(k)}</span><span class="ster">{"✓" if k in s["afgevinkt"] else ""}</span></button>'
                  for k, v in EXTRA.items() if v[0] is None)
    album = ''.join(f'<button class="tegel {"ja" if a["behaald"] else "nee"}" title="{_e(a["naam"] + " — " + a["feit"]) if a["behaald"] else "Zie alle kaarten van " + _e(label(a["id"])) + " om deze cel te verzamelen"}" '
                    f'{_cmd("gzc3:college:" + a["id"])}><div class="em">{a["emoji"]}</div><div class="nm">{_e(a["naam"]) if a["behaald"] else _e(kort(a["id"]))}</div></button>'
                    for a in s['album'])
    badges = ''.join(f'<span class="badge{"" if ok else " nee"}" title="{_e(uitleg)}">{ic} {_e(nm)}</span>' for ic, nm, uitleg, ok in s['badges'])
    behaald = sum(1 for *_, ok in s['badges'] if ok)
    n_col = sum(1 for k in COLLEGES if k in s['afgevinkt'])
    vrij_knop = (f'<div class="knoppen"><button class="licht" {_cmd("gzc3:vrij")}>Slot uitzetten: alle kaarten vrijgeven</button></div>' if s['slot'] else '')
    combo = f' · ⚡ combo {s["combo"]}' if s['combo'] >= 5 else ''

    return f"""<style>{CSS}</style><div id="gzc3" class="gz">
<div class="kop"><div><h2>Campagne GZC III</h2><div class="sub">{_e(fase)}</div>{vandaag_html}</div><div class="aftel">{aftel}</div></div>
{_installatie(stappen or [])}
<div class="rij">
 <div class="blok"><div class="label">Niveau</div><div class="lvl"><b>{s['level']}</b><span>{_e(s['titel'])}</span></div>
  <div class="balk"><span style="width:{pct}%"></span></div><div class="klein">{s['xp']} XP · nog {s['xp_hi'] - s['xp']} tot level {s['level'] + 1}</div>
  <div class="klein" style="margin-top:6px">{_e(reeks)} · record {s['record']}</div>
  <div class="klein">⚡ beste combo {s['combo_record']} · 💥 {s['kritieken']} kritieke treffers{combo}</div></div>
 <div class="blok"><div class="label">Dagquest</div>{quests}
  <div class="klein" style="margin-top:4px">Vandaag {s['herhalingen_vandaag']} herhalingen, {s['nieuw_vandaag']} nieuw</div></div>
</div>
<div class="blok" style="margin-top:12px"><div class="label">Vandaag op het programma{' · vink een college af om de kaarten vrij te spelen' if s['slot'] else ''}</div>{lijst}
 <div class="knoppen">{''.join(knoppen)}</div></div>
<div class="rij">
 <div class="blok"><div class="label">Prognose</div><div class="sub">{prognose}</div></div>
 <div class="blok"><div class="label">Herhalingen komende week</div><div class="week">{werkdruk}</div></div>
</div>
<div class="label" style="margin-top:16px">Wereldkaart · klik op een college voor de kapstok, de controlequiz en je kaarten · {n_col}/{len(COLLEGES)} colleges</div>
{werelden}
<div class="wereld"><div class="baaskop"><div class="ic">📜</div><div><b>Arena van de oude tentamens</b><div class="klein">Fase 2 · 23 t/m 28 oktober</div></div><div></div></div>
 <div class="pad">{ots}</div></div>
<div class="label" style="margin-top:16px">Celalbum · {s['n_cellen']}/{len(s['album'])} verzameld · zie alle kaarten van een college om de cel te krijgen</div>
<div class="album">{album}</div>
<div class="label" style="margin-top:14px">Badges · {behaald}/{len(s['badges'])}</div><div class="badges">{badges}</div>
<details><summary>Uitleg en instellingen</summary>
<div class="klein" style="margin-top:6px">★ college afgevinkt · ★★ alle kaarten van het college gezien (cel voor je album) · ★★★ 70% verankerd (interval ≥ {VERANKERD_IVL} dagen).<br>
XP: 2 per goed, 1 per fout antwoord, +3 per nieuwe kaart, +{XP_COLLEGE} per college, +{XP_EXTRA} per e-module/bijlage/oud tentamen, +{XP_QUIZVRAAG} per goede controlevraag (beste poging).<br>
Combo: vanaf 10 goede antwoorden op rij +1 XP per kaart, vanaf 25 +2. Ongeveer 1 op de 20 goede antwoorden is een 💥 kritieke treffer (+10 XP).</div>
{vrij_knop}</details>
</div>"""


# ------------------------------------------------------------------ collegevenster
DIALOOG_JS = """
function gzKies(knop){
  var v = knop.closest('.vraag'); if (v.classList.contains('klaar')) return;
  v.classList.add('klaar');
  var goed = knop.dataset.goed === '1';
  knop.classList.add(goed ? 'goed' : 'fout');
  v.querySelectorAll('.optie').forEach(function(o){ if (o.dataset.goed === '1') o.classList.add('goed'); });
  v.dataset.score = goed ? 1 : 0;
  var alle = document.querySelectorAll('.vraag'), klaar = document.querySelectorAll('.vraag.klaar');
  if (klaar.length === alle.length) {
    var s = 0; klaar.forEach(function(q){ s += +q.dataset.score; });
    var el = document.getElementById('gzscore');
    el.textContent = 'Score: ' + s + '/' + alle.length + (s === alle.length ? ' — foutloos! 🎉' : (s >= alle.length - 1 ? ' — bijna! 💪' : ' — lees de kapstok nog eens 📖'));
    pycmd('gzc3:quiz:' + document.body.dataset.college + ':' + s);
  }
}
function gzOpnieuw(){
  document.querySelectorAll('.vraag').forEach(function(v){
    v.classList.remove('klaar'); delete v.dataset.score;
    v.querySelectorAll('.optie').forEach(function(o){ o.classList.remove('goed', 'fout'); });
    var opties = v.querySelector('.opties');
    for (var i = opties.children.length; i > 1; i--) opties.appendChild(opties.children[Math.random() * i | 0]);
  });
  document.getElementById('gzscore').textContent = '';
  window.scrollTo(0, document.getElementById('quiz').offsetTop - 10);
}
"""


def dialoog(s: dict, k: str) -> str:
    """Body-HTML voor het venster van één college: kapstok, controlequiz, kaarten en verzamelcel."""
    data = COLLEGEDATA.get(k, {})
    c = s['colleges'].get(k, {})
    pc = s['per_college'].get(k)
    af = k in s['afgevinkt']
    n = pc['n'] if pc else 0
    stats = (f'{n} kaarten · {pc["gezien"]} gezien · {pc["verankerd"]} verankerd · {pc["nieuw"]} nieuw'
             + (f' ({pc["opgeschort"]} op slot)' if pc['opgeschort'] else '') if n else 'Nog geen kaarten aan dit college gekoppeld.')
    if c.get('retentie') is not None:
        stats += f' · {c["retentie"]}% goed (14 dagen)'
    slot = ('<span class="chip ok">🔓 vrijgespeeld</span>' if af or not s['slot'] else '<span class="chip nok">🔒 op slot</span>')
    knoppen = [f'<button {_cmd("gzc3:vink:" + k)}>{"↩︎ Afvinken ongedaan maken" if af else "✓ College gedaan: kaarten vrijspelen (+" + str(XP_COLLEGE) + " XP)"}</button>']
    if n:
        knoppen.append(f'<button class="licht" {_cmd("gzc3:browse:" + k)}>🔎 Kaarten bekijken</button>')
        knoppen.append(f'<button class="licht" {_cmd("gzc3:herkansing:" + k)}>🔁 Herkansing van dit college</button>')

    delen = [f'<h2>{_e(label(k))}</h2>']
    if data.get('docent'):
        delen.append(f'<div class="sub">{_e(data["docent"])} · bron: {_e(data.get("bron", ""))}</div>')
    delen.append(f'<div style="margin-top:8px">{sterren_html(c.get("sterren", 0))} <span class="sub">{_e(sterren_tekst(c.get("sterren", 0)))}</span> {slot}</div>')
    delen.append(f'<div class="klein" style="margin-top:4px">{stats}</div><div class="knoppen">{"".join(knoppen)}</div>')

    if data.get('kapstok'):
        delen.append(f'<div class="kern">{_e(data["kern"])}</div><div class="label" style="margin-top:14px">Kapstok</div>')
        for kop, punten in data['kapstok']:
            delen.append(f'<h3>{_e(kop)}</h3><ul>' + ''.join(f'<li>{_e(p)}</li>' for p in punten) + '</ul>')
        delen.append('<div class="valkuil"><b>⚠️ Valkuilen</b><ul>' + ''.join(f'<li>{_e(v)}</li>' for v in data['valkuilen']) + '</ul></div>')
        if data.get('tentamentips'):
            delen.append('<div class="tip"><b>🎯 Wat de docent zei over het tentamen</b><ul>'
                         + ''.join(f'<li>„{_e(t["citaat"])}” <span class="sub">— {_e(t["betekenis"])}</span></li>' for t in data['tentamentips']) + '</ul></div>')
        if data.get('citaten'):
            delen.append('<div class="citaten"><b>🎙️ Uit het college</b>'
                         + ''.join(f'<blockquote>„{_e(t["citaat"])}”<span class="sub"> · {_e(t["onderwerp"])}</span></blockquote>' for t in data['citaten']) + '</div>')
    else:
        delen.append('<div class="kern">Voor dit college zijn de slides nog niet verwerkt. Zet ze in de Drive-map, dan komt hier de kapstok met controlevragen.</div>')

    if data.get('vragen'):
        beste = c.get('quiz')
        rnd = random.Random()
        vragen = []
        for i, q in enumerate(data['vragen']):
            opties = [(o, j == 0) for j, o in enumerate(q['opties'])]
            rnd.shuffle(opties)
            knoppen_q = ''.join(f'<button class="optie" data-goed="{1 if goed else 0}" onclick="gzKies(this)">{_e(o)}</button>' for o, goed in opties)
            vragen.append(f'<div class="vraag"><b>{i + 1}. {_e(q["vraag"])}</b><div class="opties">{knoppen_q}</div>'
                          f'<div class="uitleg">💡 {_e(q["uitleg"])}</div></div>')
        delen.append(f'<div class="label" id="quiz" style="margin-top:18px">Controlequiz · {len(vragen)} vragen · +{XP_QUIZVRAAG} XP per goed antwoord (beste poging telt)'
                     + (f' · jouw beste score: {beste}/{len(vragen)}' if beste is not None else '') + '</div>'
                     + ''.join(vragen) + '<div class="score" id="gzscore"></div>'
                     + '<div class="knoppen"><button class="licht" onclick="gzOpnieuw()">↻ Opnieuw (andere volgorde)</button></div>')

    cel = data.get('cel')
    if cel:
        if c.get('cel'):
            delen.append(f'<div class="grootcel ja"><div class="em">{cel[0]}</div><div><div class="label">Cel verzameld</div><b>{_e(cel[1])}</b>'
                         f'<div class="sub">{_e(cel[2])}</div></div></div>')
        else:
            hint = 'Vink dit college af om de cel te krijgen.' if not n else f'Zie alle {n} kaarten van dit college minstens één keer om deze cel te verzamelen (nog {pc["nieuw"]}).'
            delen.append(f'<div class="grootcel nee"><div class="em">{cel[0]}</div><div><div class="label">Verzamelcel</div><b>???</b>'
                         f'<div class="sub">{_e(hint)}</div></div></div>')
    return (f'<style>{CSS}</style><script>{DIALOOG_JS}</script>'
            f'<div class="venster gz">{"".join(delen)}</div>'
            f'<script>document.body.classList.add("gz");document.body.dataset.college={json.dumps(k)};</script>')


# ------------------------------------------------------------------ HUD tijdens het leren
HUD_JS = """
(function(){
if (window.gzc3hud) return;
var css = document.createElement('style');
css.textContent = `
#gzc3hud{position:fixed;top:8px;right:10px;z-index:9999;pointer-events:none;font:12px/1.35 -apple-system,"Segoe UI",Roboto,sans-serif;
 background:rgba(255,255,255,.88);color:#221a2e;border:1px solid #e4dcec;border-radius:12px;padding:6px 10px;box-shadow:0 2px 10px rgba(40,20,60,.12);min-width:150px;opacity:.92}
.night-mode #gzc3hud,.nightMode #gzc3hud{background:rgba(36,29,46,.9);color:#efe9f6;border-color:#3a3047}
#gzc3hud .r{display:flex;justify-content:space-between;gap:10px;align-items:center}
#gzc3hud .hp{height:5px;border-radius:9px;background:#e4dcec;overflow:hidden;margin:3px 0 2px}
.night-mode #gzc3hud .hp,.nightMode #gzc3hud .hp{background:#3a3047}
#gzc3hud .hp i{display:block;height:100%;background:#d9577a;transition:width .6s}
#gzc3hud .z{color:#8a8098;font-size:11px}
#gzc3hud .combo{font-weight:700;color:#c49a1a}
.gzc3pop{position:fixed;right:24px;top:100px;z-index:10000;pointer-events:none;font:700 15px -apple-system,"Segoe UI",Roboto,sans-serif;color:#5b3f8c;
 animation:gzc3op 1.6s ease-out forwards;text-shadow:0 1px 0 rgba(255,255,255,.7)}
.night-mode .gzc3pop,.nightMode .gzc3pop{color:#b69ae6;text-shadow:none}
.gzc3pop.krit{font-size:20px;color:#c49a1a}
.gzc3pop.combo{font-size:17px;color:#d9577a}
@keyframes gzc3op{0%{opacity:0;transform:translateY(6px) scale(.9)}15%{opacity:1;transform:translateY(0) scale(1.05)}100%{opacity:0;transform:translateY(-34px) scale(1)}}`;
document.head.appendChild(css);
window.gzc3hud = function(d){
  var el = document.getElementById('gzc3hud');
  if (!el) { el = document.createElement('div'); el.id = 'gzc3hud'; document.body.appendChild(el); }
  if (!d) { el.style.display = 'none'; return; }
  el.style.display = '';
  var esc = function(s){ var t = document.createElement('span'); t.textContent = s; return t.innerHTML; };
  el.innerHTML = (d.baas ? '<div class="r"><span>' + d.icoon + ' <b>' + esc(d.baas) + '</b></span><span class="z">' + d.hp + ' HP</span></div>'
      + '<div class="hp"><i style="width:' + d.hp + '%"></i></div>' : '')
    + '<div class="r"><span class="z">' + esc(d.college || '') + ' ' + (d.sterren || '') + '</span><span class="z">Lv ' + d.level + '</span></div>'
    + (d.combo >= 3 ? '<div class="r"><span class="combo">⚡ combo ' + d.combo + (d.combo >= 25 ? ' ×3' : (d.combo >= 10 ? ' ×2' : '')) + '</span></div>' : '');
};
window.gzc3pop = function(tekst, soort, vertraging){
  setTimeout(function(){
    var p = document.createElement('div'); p.className = 'gzc3pop ' + (soort || ''); p.textContent = tekst;
    p.style.top = (100 + 30 * document.querySelectorAll('.gzc3pop').length) + 'px';
    document.body.appendChild(p); setTimeout(function(){ p.remove(); }, 1700);
  }, vertraging || 0);
};
})();
"""


def hud_data(snel: dict, thema: str | None, college: str | None) -> dict | None:
    if not snel:
        return None
    b = snel.get('bazen', {}).get(thema) if thema else None
    c = snel.get('colleges', {}).get(college) if college else None
    return dict(baas=b['baas'] if b else '', icoon=b['icoon'] if b else '', hp=b['hp'] if b else 0,
                college=label(college) if college else '', sterren='★' * c['sterren'] if c else '',
                level=snel.get('level', 1), combo=snel.get('combo', 0))
