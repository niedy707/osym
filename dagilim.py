# -*- coding: utf-8 -*-
"""data/dagilim.json — cizgi grafik icin bolum bazli sira dagilimi.

Elimizde ogrenci basina sira YOK; her programin taban sirasi (ve tahmini tavan
sirasi) var. Bu yuzden her programin YERLESEN sayisi, kendi
[tavan sira .. taban sira] araligina DUZGUN dagitilir ve 1.000'lik kovalarda
toplanir. Sonuc olculmus degil MODELLENMIS bir dagilimdir; grafikte boyle yazar.

Amac bolumleri birbiriyle kiyaslamak degil, her bolumun dagilim desenini
gormek — bu yuzden farkli puan turleri ayni eksende cizilebiliyor.
"""
import json, os

KOVA = 1000
ELEME_KONT = 50      # bu kontenjanin altindakiler eleme adayi
ELEME_SIRA = 10000   # ...ama ilk bu siranin icinde yerleseni varsa kalir
KAC = None        # None = tum bolumler (secim istemcide yapiliyor)


def seri(programlar):
    """Bir bolumun programlarindan kova -> kisi sayisi sozlugu uretir."""
    kova = {}
    for r in programlar:
        n = r.get('ty') or 0
        if not n or r.get('sira') is None:
            continue
        alt = r.get('smax') or r['sira']          # tavan puan -> daha iyi sira
        ust = r['sira']                            # taban puan -> daha kotu sira
        if alt > ust:
            alt, ust = ust, alt
        k0, k1 = alt // KOVA, ust // KOVA
        pay = n / (k1 - k0 + 1)
        for k in range(k0, k1 + 1):
            kova[k] = kova.get(k, 0) + pay
    return kova


def kapasite_uygula(bolum_kova, pt_of, tur=60):
    """Bir kovaya, o aralikta bulunan aday sayisindan fazla kisi yerlestirilemez.

    Duzgun yayma varsayimi programlarin yogun ustuste bindigi ust siralarda
    fiziksel siniri asiyordu (SAY 0-1.000 kovasinda 1.662 kisi cikiyordu; oysa
    orada 1.000 aday var). Sebep, tavan siranin TEK bir ucdegerden turetilmesi:
    araliklar gercekte oldugundan genis cikiyor.

    Cozum kirpmak DEGIL tasimak: kapasiteyi asan kovada fazlalik alinir ve ayni
    BOLUMUN kendi komsu kovalarina, bos kapasite oraninda dagitilir. Boylece
    her bolumun egrisi altindaki toplam gercek yerlesen sayisina esit kalir
    ve hicbir kova kapasitesini asmaz.
    """
    for _ in range(tur):
        toplam = {}
        for ad, kova in bolum_kova.items():
            pt = pt_of[ad]
            for k, v in kova.items():
                toplam[(pt, k)] = toplam.get((pt, k), 0) + v
        asan = {kk: t for kk, t in toplam.items() if t > KOVA + 1e-9}
        if not asan:
            return True
        for ad, kova in bolum_kova.items():
            pt = pt_of[ad]
            fazla = 0.0
            for k in list(kova):
                t = toplam.get((pt, k))
                if t and t > KOVA:
                    yeni = kova[k] * KOVA / t
                    fazla += kova[k] - yeni
                    kova[k] = yeni
            if fazla <= 0:
                continue
            # bos kapasitesi olan kendi kovalarina, bosluk oraninda tasi
            bosluk = {}
            for k in kova:
                b = KOVA - toplam.get((pt, k), 0)
                if b > 0:
                    bosluk[k] = b
            if not bosluk:                       # komsu kovalara genislet
                k0, k1 = min(kova), max(kova)
                for k in (k0 - 1, k1 + 1):
                    if k >= 0:
                        bosluk[k] = max(1.0, KOVA - toplam.get((pt, k), 0))
            tb = sum(bosluk.values())
            for k, b in bosluk.items():
                kova[k] = kova.get(k, 0) + fazla * b / tb
    return False


def varyant(rows):
    g = {}
    for r in rows:
        if r['duzey'] != 'Lisans' or not r.get('ty'):
            continue
        g.setdefault(r['base'], []).append(r)

    # Kucuk ve ust siralarda hic gorunmeyen bolumler grafigi kalabaliklastirmaktan
    # baska ise yaramiyor. Kural: kontenjani 50'den azsa VE ilk 10.000 icinde tek
    # bir yerlesenı bile yoksa disarida birak. Ilk 10.000'de bir kisisi olan
    # kucuk bolum grafige GIRER.
    def kalsin(prg):
        if sum(r['tk'] for r in prg) >= ELEME_KONT:
            return True
        return any((r.get('smax') or r['sira']) <= ELEME_SIRA for r in prg if r.get('ty'))

    elenen = [ad for ad, prg in g.items() if not kalsin(prg)]
    for ad in elenen:
        g.pop(ad)

    sirali = sorted(g.items(), key=lambda kv: -sum(r['tk'] for r in kv[1]))
    if KAC: sirali = sirali[:KAC]

    ham = {ad: seri(prg) for ad, prg in sirali}
    pt_of = {}
    for ad, prg in sirali:
        p = {}
        for r in prg:
            p[r['pt']] = p.get(r['pt'], 0) + r['tk']
        pt_of[ad] = max(p, key=p.get)
    tamam = kapasite_uygula(ham, pt_of)
    print('  kapasite kısıtı: ' + ('sağlandı' if tamam else 'UYARI: yakınsamadı'))

    out = []
    for ad, prg in sirali:
        kova = ham[ad]
        if not kova:
            continue
        k0, k1 = min(kova), max(kova)
        # bas taraftaki bos kovalari saklamamak icin baslangic indisi + dizi
        deger = [round(kova.get(k, 0)) for k in range(k0, k1 + 1)]
        out.append({
            'ad': ad,
            'pt': pt_of[ad],
            'kont': sum(r['tk'] for r in prg),
            'yer': sum(r['ty'] for r in prg),
            'bas': k0,          # ilk kovanin indisi (sira = bas*1000)
            'v': deger,         # her kovadaki kisi sayisi
        })
    print(f'  elenen bölüm: {len(elenen)}')
    return out


def uret():
    rows = json.load(open('data/programlar.json', encoding='utf-8'))
    kktc = lambda r: r.get('kktc_uni') or r.get('kktc')
    veri = {
        'kova': KOVA,
        'aciklama': ('Her programın yerleşeni, kendi tavan–taban sıra aralığına düzgün '
                     'dağıtılarak 1.000\'lik kovalarda toplandı; bir kovadaki toplam, o '
                     'aralıktaki aday sayısını aşamayacağı için üst sıralarda oransal '
                     'düzeltme uygulandı. Modellenmiş dağılımdır.'),
        'eleme': {'kontenjan': ELEME_KONT, 'sira': ELEME_SIRA},
        'bolumler': {
            'in': varyant(rows),
            'out': varyant([r for r in rows if not kktc(r)]),
        },
    }
    os.makedirs('data', exist_ok=True)
    json.dump(veri, open('data/dagilim.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    kb = os.path.getsize('data/dagilim.json') / 1024
    n = len(veri['bolumler']['out'])
    nokta = sum(len(b['v']) for b in veri['bolumler']['out'])
    print(f"data/dagilim.json — {kb:.0f} KB · {n} bölüm · {nokta:,} nokta".replace(',', '.'))


if __name__ == '__main__':
    uret()
