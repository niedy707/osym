# -*- coding: utf-8 -*-
"""data/ozet.json — acilista yeterli olan kucuk ozet dosyasi.

index.html acilista 14,6 MB'lik programlar.json'u indirmek zorunda kalmasin diye,
varsayilan sekmelerin (Grafikler, Bolum Ozeti) ihtiyac duydugu her sey burada
onceden hesaplanir. Tam veri yalnizca program listesi gereken sekmelerde
(Tum Programlar, Bolum Paneli, Universiteler) tembel yuklenir.

KKTC anahtari iki ayri gorunum urettigi icin her iki varyant da hesaplanir.
"""
import json, os
from rank_model import NTOT
from bolumler import baraj as baraj_bul

BANDLAR = [(1, 1000), (1000, 5000), (5000, 10000), (10000, 25000), (25000, 50000),
           (50000, 100000), (100000, 200000), (200000, 300000), (300000, 10**7)]


def tr(n):
    return f"{n:,}".replace(',', '.')


def bandla(rows, baraj):
    sirs = [r['smin'] for r in rows if r['smin'] is not None]
    if not sirs:
        return []
    ust = baraj or max(sirs)
    out = []
    for a, b in BANDLAR:
        if a >= ust * 1.05:
            break
        etiket = f"{tr(a)} – {'∞' if b >= 10**7 else tr(b)}"
        out.append([etiket, sum(r['tk'] for r in rows if r['smin'] is not None and a <= r['smin'] < b)])
    return out


def varyant(rows):
    g = {}
    for r in rows:
        if r['duzey'] != 'Lisans' or r['smin'] is None or r.get('yuzde') is None:
            continue
        g.setdefault(r['base'], []).append(r)

    out = []
    for ad, v in g.items():
        kont = sum(x['tk'] for x in v)
        yer = sum(x['ty'] for x in v)
        pts = {}
        for x in v:
            pts[x['pt']] = pts.get(x['pt'], 0) + x['tk']
        pt = max(pts, key=pts.get)
        mins = [x['min'] for x in v if x['min'] is not None]
        sirs = [x['smin'] for x in v]
        out.append({
            'ad': ad, 'pt': pt, 'prog': len(v), 'kont': kont, 'yer': yer,
            'acik': sum(x['acik'] for x in v), 'fazla': sum(x['fazla'] for x in v),
            'dilim': round(sum(x['yuzde'] * x['tk'] for x in v) / max(1, kont), 4),
            'dol': round(100 * yer / kont, 4) if kont else None,
            'enIyiPuan': max(mins) if mins else None,
            'enDusukPuan': min(mins) if mins else None,
            'enIyiSira': min(sirs), 'enDipSira': max(sirs),
            'baraj': baraj_bul(ad),
            'bandlar': bandla(v, baraj_bul(ad)),
        })
    out.sort(key=lambda o: o['dilim'])
    return out


def uret():
    rows = json.load(open('data/programlar.json', encoding='utf-8'))
    kktc = lambda r: r.get('kktc_uni') or r.get('kktc')
    veri = {
        'kaynak': 'ÖSYM 2026-YKS TABLO-3 / TABLO-4 (18.08.2026)',
        'toplam_program': len(rows),
        'toplam_kontenjan': sum(r['tk'] for r in rows),
        'toplam_yerlesen': sum(r['ty'] for r in rows),
        'ntot': NTOT,
        'bolumler': {
            'in': varyant(rows),
            'out': varyant([r for r in rows if not kktc(r)]),
        },
    }
    os.makedirs('data', exist_ok=True)
    json.dump(veri, open('data/ozet.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    kb = os.path.getsize('data/ozet.json') / 1024
    print(f"data/ozet.json — {kb:.0f} KB · "
          f"{len(veri['bolumler']['in'])} bölüm (KKTC dahil) / "
          f"{len(veri['bolumler']['out'])} (hariç)")


if __name__ == '__main__':
    uret()
