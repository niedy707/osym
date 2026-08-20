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
from slug import slug

BANDLAR = [(1, 1000), (1000, 5000), (5000, 10000), (10000, 25000), (25000, 50000),
           (50000, 100000), (100000, 200000), (200000, 300000), (300000, 10**7)]


def tr(n):
    return f"{n:,}".replace(',', '.')


def bandla(rows, baraj):
    sirs = [r['sira'] for r in rows if r['sira'] is not None]
    if not sirs:
        return []
    ust = baraj or max(sirs)
    out = []
    for a, b in BANDLAR:
        if a >= ust * 1.05:
            break
        acik = b >= 10**7                       # 300.000 – ∞ : ust sinir yok
        etiket = f"{tr(a)} – {'∞' if acik else tr(b)}"
        deger = sum(r['tk'] for r in rows if r['sira'] is not None and a <= r['sira'] < b)
        # [etiket, kontenjan, alt sinir, ust sinir]  — ust sinir None ise acik bant.
        # Oran modu bant genisligine bolecegi icin sinirlar istemciye lazim.
        out.append([etiket, deger, a, None if acik else b])
    return out


def varyant(rows):
    # Bolum TOPLAMLARI (kontenjan/yerlesen/acik) tum Lisans programlarini icermeli;
    # aksi halde hic dolmamis (sirasi olmayan) programlarin acik kadrolari ozetten
    # dusuyor ve Tip toplami 19.044 yerine 19.032 gorunuyordu. Sira/puan tabanli
    # alanlar yalnizca sirasi olan programlardan hesaplanir.
    g = {}
    for r in rows:
        if r['duzey'] != 'Lisans':
            continue
        g.setdefault(r['base'], []).append(r)

    out = []
    for ad, v in g.items():
        sirali = [x for x in v if x['sira'] is not None and x.get('yuzde') is not None]
        if not sirali:
            continue
        kont = sum(x['tk'] for x in v)          # TUM programlar
        yer = sum(x['ty'] for x in v)
        kont_s = sum(x['tk'] for x in sirali)   # yalnizca sirasi olanlar (agirlik icin)
        pts = {}
        for x in v:
            pts[x['pt']] = pts.get(x['pt'], 0) + x['tk']
        pt = max(pts, key=pts.get)
        mins = [x['min'] for x in sirali if x['min'] is not None]
        sirs = [x['sira'] for x in sirali]
        out.append({
            'ad': ad, 'slug': slug(ad), 'pt': pt, 'prog': len(v), 'kont': kont, 'yer': yer,
            'acik': sum(x['acik'] for x in v), 'fazla': sum(x['fazla'] for x in v),
            'dilim': round(sum(x['yuzde'] * x['tk'] for x in sirali) / max(1, kont_s), 4),
            'dol': round(100 * yer / kont, 4) if kont else None,
            'enIyiPuan': max(mins) if mins else None,
            'enDusukPuan': min(mins) if mins else None,
            'enIyiSira': min(sirs), 'enDipSira': max(sirs),
            'baraj': baraj_bul(ad),
            # kontenjanin yuzde kaci RESMI siraya dayaniyor (gerisi tahmin)
            'resmiPay': round(100 * sum(x['tk'] for x in sirali if x['sirakaynak'] == 'resmi')
                              / max(1, kont_s), 1),
            'bandlar': bandla(sirali, baraj_bul(ad)),
        })
    out.sort(key=lambda o: (o['dilim'], o['ad']))   # esit dilimde ad ile sabitle
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
        # arayuzun "kac program resmi, kac tahmini" cumlesini veriden kurmasi icin
        'sirakaynak': {
            'resmi': sum(1 for r in rows if r.get('sirakaynak') == 'resmi'),
            'tahmini': sum(1 for r in rows if r.get('sirakaynak') == 'tahmini'),
        },
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
