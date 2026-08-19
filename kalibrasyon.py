# -*- coding: utf-8 -*-
"""Tahmini siralari, YOK Atlas'in RESMI basari siralariyla karsilastirir.

Bu projenin tek iddiali ciktisi siralama tahmini. YOK Atlas 2026 verisi
yayimlandiginda bu script tahminleri resmi rakamlarla karsilastirip
KALIBRASYON.md uretir — sonuc iyi de ciksa kotu de ciksa yayimlanir.

Kullanim:
    python3 kalibrasyon.py resmi_siralar.json

Beklenen girdi bicimi (program kodu -> resmi basari sirasi):
    {"105610634": 3251, "104810617": 1104, ...}

Bu dosya, YOK Atlas 2026 erisime acildiginda ondan uretilebilir
(orn. yokatlas-py paketiyle; bu tek seferlik bir DOGRULAMA kullanimidir,
projenin veri hattinin YOK Atlas'a bagimli hale gelmesi DEGILDIR).

NOT: Iki sayi ayni sey degildir ve birebir tutmasi beklenmez.
  - Buradaki sira: YERLESTIRME puanina (OBP dahil) gore
  - OSYM'nin resmi basari sirasi: OBP'siz SINAV puanina gore
Bu yuzden amac sifir sapma degil, sapmanin BUYUKLUGUNU ve puan araligina
gore nasil degistigini olcup acikca yayimlamaktir.
"""
import json, os, statistics, sys


def yukle_resmi(yol):
    if not os.path.exists(yol):
        raise SystemExit(
            f"'{yol}' bulunamadi.\n\n"
            "YOK Atlas 2026 verisi henuz yayimlanmadiysa bu script calistirilamaz.\n"
            "Durum: 19.08.2026 itibariyle YOK Atlas 2026 yerlestirme verisi erisime acilmamisti."
        )
    return {str(k): int(v) for k, v in json.load(open(yol, encoding='utf-8')).items()}


def rapor(resmi):
    rows = json.load(open('data/programlar.json', encoding='utf-8'))
    esles = [(r, resmi[r['kod']]) for r in rows if r['kod'] in resmi and r.get('smin')]
    if not esles:
        raise SystemExit('Eslesen program yok — program kodlari uyusmuyor olabilir.')

    sapmalar = [(abs(r['smin'] - g) / max(1, g), r, g) for r, g in esles]
    yuzdeler = [s * 100 for s, _, _ in sapmalar]
    sapmalar.sort(key=lambda x: -x[0])   # sadece sapmaya gore; esitlikte dict karsilastirilmasin

    bantlar = [(1, 5000), (5000, 20000), (20000, 50000), (50000, 150000),
               (150000, 400000), (400000, 10**9)]
    sat = []
    for a, b in bantlar:
        alt = [s * 100 for s, _, g in sapmalar if a <= g < b]
        if alt:
            sat.append((f'{a:,}–{b:,}'.replace(',', '.') if b < 10**9 else f'{a:,}+'.replace(',', '.'),
                        len(alt), statistics.median(alt), max(alt)))

    L = []
    L.append('# Sıralama tahmininin kalibrasyonu\n')
    L.append(f'Karşılaştırılan program: **{len(esles):,}**'.replace(',', '.') + '\n')
    L.append(f'- Medyan mutlak sapma: **%{statistics.median(yuzdeler):.2f}**')
    L.append(f'- Ortalama mutlak sapma: %{statistics.mean(yuzdeler):.2f}')
    L.append(f'- 90. yüzdelik sapma: %{statistics.quantiles(yuzdeler, n=10)[8]:.2f}')
    L.append(f'- En kötü sapma: %{max(yuzdeler):.2f}\n')
    L.append('## Sıralama bandına göre sapma\n')
    L.append('| Resmî sıra bandı | Program | Medyan sapma | En kötü |')
    L.append('|---|---|---|---|')
    for ad, n, med, mx in sat:
        L.append(f'| {ad} | {n} | %{med:.2f} | %{mx:.2f} |')
    L.append('\n## En kötü 20 program\n')
    L.append('| Program | Tahmini | Resmî | Sapma |')
    L.append('|---|---|---|---|')
    for s, r, g in sapmalar[:20]:
        L.append(f"| {r['uni']} — {r['prog']} | {r['smin']:,} | {g:,} | %{s*100:.1f} |".replace(',', '.'))
    L.append(
        '\n---\n\n**Yöntem notu.** Buradaki tahmin *yerleştirme puanına* (OBP dahil), ÖSYM\'nin resmî '
        'başarı sırası ise *OBP\'siz sınav puanına* göre hesaplanır. İki sayının birebir tutması '
        'beklenmez; bu tablo sapmanın büyüklüğünü ve sıralama bandına göre nasıl değiştiğini gösterir.\n')
    open('KALIBRASYON.md', 'w', encoding='utf-8').write('\n'.join(L))
    print('KALIBRASYON.md yazıldı — medyan sapma %{:.2f}'.format(statistics.median(yuzdeler)))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    rapor(yukle_resmi(sys.argv[1]))
