# -*- coding: utf-8 -*-
"""Panelde secenek olarak sunulacak "revacta" bolumlerin listesini uretir.

Kural (kullanici karari): iki listenin BIRLESIMI
  A) ilk 2.000 sirada taban'i olan programlarin kontenjaninin %1'inden fazlasi
  B) ilk 50.000 sirada taban'i olan programlarin kontenjaninin %1'inden fazlasi
A "zirvede revacta", B "kitlesel revacta" bolumleri yakalar.
"""
import json, collections

# OSYM 2026-YKS Tercih Kilavuzu, basari sirasi barajlari (resmi)
BARAJ_TAM = {'Tıp': 50000, 'Diş Hekimliği': 80000, 'Eczacılık': 100000, 'Hukuk': 100000,
             'Mimarlık': 250000}
BARAJ_SONEK = {'Mühendisliği': 300000, 'Öğretmenliği': 300000}

# dropdown'da gorunecek adlar (fakulte olarak anilanlar)
GORUNEN = {'Tıp': 'Tıp Fakültesi', 'Diş Hekimliği': 'Diş Hekimliği Fakültesi',
           'Hukuk': 'Hukuk Fakültesi', 'Eczacılık': 'Eczacılık Fakültesi',
           'İlahiyat': 'İlahiyat Fakültesi'}

def baraj(base):
    if base in BARAJ_TAM:
        return BARAJ_TAM[base]
    for sonek, v in BARAJ_SONEK.items():
        if base.endswith(sonek):
            return v
    return None

def uret(rows, esik=0.01):
    L = [r for r in rows if r['duzey'] == 'Lisans' and r['smin']]

    def pay(limit):
        c = collections.Counter()
        for r in L:
            if r['smin'] <= limit:
                c[r['base']] += r['tk']
        return c, sum(c.values())

    c2, t2 = pay(2000)
    c50, t50 = pay(50000)
    secilen = {k for k, v in c2.items() if v / t2 > esik} | {k for k, v in c50.items() if v / t50 > esik}

    ptc = collections.defaultdict(collections.Counter)
    top = collections.Counter()
    for r in L:
        ptc[r['base']][r['pt']] += r['tk']
        top[r['base']] += r['tk']

    out = []
    for k in sorted(secilen):          # set uzerinde dolasmak sirayi belirsiz birakiyordu
        out.append({
            'base': k,
            'ad': GORUNEN.get(k, k),
            'pt': max(ptc[k], key=ptc[k].get),
            'baraj': baraj(k),
            'kont': top[k],
            'pay2000': round(100 * c2.get(k, 0) / t2, 2),
            'pay50000': round(100 * c50.get(k, 0) / t50, 2),
        })
    # ilk 50.000 payina gore sirala, Tip her zaman basta (varsayilan secim).
    # Son anahtar ad: esit paylarda siranin calistirmadan calistirmaya degismemesi icin.
    out.sort(key=lambda x: (x['base'] != 'Tıp', -x['pay50000'], -x['pay2000'], x['base']))
    return out

if __name__ == '__main__':
    rows = json.load(open('data/programlar.json', encoding='utf-8'))
    b = uret(rows)
    json.dump(b, open('data/bolumler.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{len(b)} bölüm seçildi -> data/bolumler.json\n")
    print(f"{'Bölüm':<42} {'tür':<4} {'baraj':>9} {'ilk2000':>8} {'ilk50k':>7}")
    for x in b:
        print(f"{x['ad'][:42]:<42} {x['pt']:<4} {(f'{x[chr(98)+chr(97)+chr(114)+chr(97)+chr(106)]:,}'.replace(',','.') if x['baraj'] else '—'):>9} "
              f"{x['pay2000']:>7.1f}% {x['pay50000']:>6.1f}%")
