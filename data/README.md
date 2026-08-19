# Veri seti — 2026-YKS yerleştirme

ÖSYM'nin resmî TABLO-3 ve TABLO-4 dosyalarından üretilmiş, program bazlı tek veri seti.
**21.493 program · 779.870 kontenjan · 730.854 yerleşen.**

| Dosya | Biçim | Boyut | Kullanım |
|---|---|---|---|
| `programlar.json` | JSON (nesne dizisi) | ~14,6 MB | Web arayüzü, JS/Python |
| `programlar.csv` | CSV, `;` ayraçlı, UTF-8 BOM | ~6,7 MB | Excel, pandas, R |
| `bolumler.json` | JSON | ~4 KB | Panelin bölüm seçici listesi |

```python
import pandas as pd
df = pd.read_csv('programlar.csv', sep=';')
tip = df[(df.base == 'Tıp') & (df.duzey == 'Lisans')]
print(tip.tk.sum(), tip.ty.sum())      # 19044 18993
```

## Alanlar

### Kimlik
| Alan | Tip | Açıklama |
|---|---|---|
| `kod` | metin | ÖSYM program kodu (9 hane) |
| `uni` | metin | Üniversite adı (ÖSYM yazımıyla) |
| `unituru` | metin | `DEVLET` · `VAKIF` · `KKTC` · `YURTDISI VAKIF` |
| `sehir` | metin | Üniversite adından türetildi; yurt dışı için `YURT DIŞI` |
| `fak` | metin | Fakülte / yüksekokul adı |
| `prog` | metin | Program adı, ÖSYM'deki tam hâli |
| `base` | metin | Parantezsiz bölüm adı — `Tıp (İngilizce) (Burslu)` → `Tıp` |
| `duzey` | metin | `Lisans` (TABLO-4) · `Ön Lisans` (TABLO-3) |
| `pt` | metin | Puan türü: `SAY` `EA` `SÖZ` `DİL` `TYT` |
| `burs` | metin | `Burslu` · `%50 İndirimli` · `%25 İndirimli` · `Ücretli` · `—` |
| `dil` | metin | Öğretim dili; belirtilmemişse `Türkçe` |

### Genel kontenjan (taban/tavan puanlar bu kontenjan içindir)
| Alan | Tip | Açıklama |
|---|---|---|
| `kont` / `yer` | tam sayı | Genel kontenjan / yerleşen |
| `min` / `max` | ondalık | En küçük (taban) / en büyük (tavan) **yerleştirme puanı** |
| `smin` / `smax` | tam sayı | Taban / tavan puanın **tahmini** sırası |
| `yuzde` | ondalık | `smin`'in kendi puan türü içindeki yüzdelik dilimi |
| `guven` | metin | `interpolasyon` · `ekstrapolasyon` (550 üstü) · `alt-sinir` |

### Kontenjan muhasebesi
| Alan | Tip | Açıklama |
|---|---|---|
| `acik` | tam sayı | Kontenjan türü bazında **pozitif** boşlukların toplamı |
| `fazla` | tam sayı | Eşit puan nedeniyle kontenjan üstünde yerleştirilen aday |
| `tk` / `ty` | tam sayı | Tüm kontenjan türleri toplamı: kontenjan / yerleşen |

> `kont - yer` **kullanmayın**: ÖSYM eşit puanlı adaylarda kontenjanın üstünde yerleştirme
> yapar, bu da net farkta gerçek boşlukları maskeler. Boşluk için `acik` alanını kullanın.

### Özel kontenjanlar
`ob_*` okul birincisi · `y34_*` 34 yaş üstü kadın · `sehit_*` şehit/gazi yakını.
Her biri için `_k` kontenjan, `_y` yerleşen, `_min` / `_max` puan.

### Bayraklar (boolean)
`kktc` "KKTC Uyruklu" kontenjanı · `kktc_uni` üniversite KKTC/yurt dışı merkezli ·
`uolp` ortak program · `uzaktan` uzaktan öğretim · `io` ikinci öğretim · `aof` açıköğretim.

> "KKTC" iki ayrı şeydir: `kktc_uni` KKTC'deki üniversiteleri, `kktc` ise Türkiye'deki
> üniversitelerin KKTC uyruklulara ayırdığı kontenjanı gösterir. Arayüzdeki "KKTC hariç"
> anahtarı **ikisini birden** çıkarır.

## Sıralamalar hakkında

`smin` / `smax` / `yuzde` **tahmindir**. ÖSYM taban puan tablolarında başarı sırası
yayımlamaz; bu değerler ÖSYM'nin resmî *"2026-YKS Yerleştirme Puanlarının Yığınsal Dağılımı"*
tablosundan probit interpolasyonla hesaplanır (`rank_model.py`). Model, ÖSYM'nin
Tıp/Diş/Eczacılık/Hukuk/Mimarlık/Mühendislik/Öğretmenlik barajlarıyla yedi bağımsız noktada
%0,1–1,5 sapmayla doğrulanmıştır.

**Farklı puan türleri ham sırayla karşılaştırılamaz** — SAY'da 1.135.718, DİL'de 132.826 aday
var. Bölümler arası kıyas için `yuzde` alanını kullanın.

Puanlar **yerleştirme puanı**dır (sınav puanı + OBP katkısı). ÖSYM'nin sonuç belgesindeki
resmî "başarı sırası" OBP'siz sınav puanına göre hesaplanır; bu yüzden buradaki sıralar
YÖK Atlas'takilerle birebir aynı olmaz.

## Yeniden üretim

```bash
pip install openpyxl
python3 build_data.py && python3 bolumler.py && python3 test_model.py
```

Kaynak dosyalar `kaynak/` altında değiştirilmeden duruyor; `build_data.py` üretime
başlamadan önce SHA-256 özetlerini doğrular.

## Lisans

Üretilmiş veri MIT (bkz. `../LICENSE`). `kaynak/` altındaki ÖSYM belgeleri kapsam dışıdır
(bkz. `../NOTICE`). Bu resmî bir ÖSYM ürünü değildir.
