# -*- coding: utf-8 -*-
"""«En basarili 25.000 kisinin 20.000'i tip yazdi» iddiasinin resmi veriyle testi.

Varsayimsiz yontem:
  Bir programa yerlesen HER aday, o programin TABAN puanindan yuksek puan almistir.
  Dolayisiyla taban sirasi R'den kucuk/esit olan programlarin TUM yerlesenleri,
  kesin olarak ilk R sira icindedir  ->  ALT SINIR.
  Tavan sirasi R'den kucuk olan programlar da en azindan bir kismiyla katkida
  bulunabilir  ->  bu programlarin yerlesenleri de eklenirse UST SINIR elde edilir.
Ikisi arasindaki bant, dagilim varsayimi yapmadan gercek degeri kapsar.
"""
import json
from rank_model import puan_at_rank

rows = json.load(open('data/programlar.json', encoding='utf-8'))
T = [r for r in rows if r['base'] == 'Tıp' and r['duzey'] == 'Lisans'
     and r['smin'] is not None and r['ty']]

def bant(R):
    alt = ust = 0
    for r in T:
        if r['smin'] <= R:          # taban sirasi ilk R icinde -> hepsi kesin ilk R'de
            alt += r['ty']; ust += r['ty']
        elif r['smax'] is not None and r['smax'] <= R:   # sadece bir kismi ilk R'de olabilir
            ust += r['ty']
    return alt, min(ust, R)

print("=" * 74)
print("  EKŞİ İDDİASI: «en başarılı 25.000 kişinin 20.000'i tıp yazmış»")
print("=" * 74)
print(f"\n  Türkiye'nin TOPLAM Tıp kontenjanı (KKTC dahil) : 19.044")
print(f"  Tıp'a yerleşen TOPLAM aday                     : 18.993")
print(f"  Bu 18.993 aday ~26. sıradan ~49.241. sıraya kadar yayılmış durumda.\n")
print(f"  {'İlk N sıra':>11} | {'≈ Puan':>7} | {'Tıp yerleşen (alt–üst sınır)':>30} | {'Oran':>13}")
print("  " + "-" * 70)
for R in (1000, 5000, 10000, 15000, 20000, 25000, 30000, 40000, 50000):
    a, u = bant(R)
    ba = f"{a:,} – {u:,}".replace(',', '.')
    o = f"%{100*a/R:.0f} – %{100*u/R:.0f}"
    print(f"  {R:>11,} | {puan_at_rank(R):>7.2f} | {ba:>30} | {o:>13}".replace(',', '.'))
a, u = bant(25000)
print(f"\n  SONUÇ — ilk 25.000 SAY adayı içinde Tıp'a yerleşen: {a:,}–{u:,} kişi".replace(',', '.'))
print(f"  (iddia: 20.000). Yani oran %{100*a/25000:.0f}–%{100*u/25000:.0f}, iddia edilen %80 değil.")
print(f"\n  Ayrıca: 20.000 rakamı ÜST SINIRIN da üstünde." if 20000 > u else
      f"\n  Not: 20.000 rakamı üst sınırın içinde kalıyor.")
print(f"  Tıp'a yerleşenlerin {18993-a:,}'i (%{100*(18993-a)/18993:.0f}) zaten 25.000'in GERİSİNDE.".replace(',', '.'))
