# 2026-YKS Yerleştirme Verisi — kontenjan, taban/tavan puan ve tahmini sıralama

[![lisans MIT](https://img.shields.io/badge/lisans-MIT-blue)](LICENSE)
[![veri ÖSYM 18.08.2026](https://img.shields.io/badge/veri-%C3%96SYM%2018.08.2026-c45a00)](kaynak/)
[![program 21.493](https://img.shields.io/badge/program-21.493-28c88a)](data/)
[![CI](https://github.com/niedy707/osym/actions/workflows/ci.yml/badge.svg)](https://github.com/niedy707/osym/actions/workflows/ci.yml)
[![canlı](https://img.shields.io/badge/canl%C4%B1-osym--yks.vercel.app-5b9cff)](https://osym-yks.vercel.app)

> **Doğrulama (19.08.2026):** YÖK Atlas 2026 verisi yayımlandı ve modelin tahminleri **18.251
> program** üzerinde resmî başarı sıralarıyla karşılaştırıldı — **medyan sapma %0,25**. Aynı
> karşılaştırmada 18.251 programın taban puanı ÖSYM verisiyle **birebir** tuttu (0 uyuşmazlık).
> Ayrıntı: [KALIBRASYON.md](KALIBRASYON.md).

> **In English** — Turkey's 2026 university placement data (YKS), rebuilt from ÖSYM's own official
> spreadsheets into one searchable dataset of **21,493 programmes**. ÖSYM publishes scores but **not**
> success ranks (*başarı sırası*) in these tables, so ranks come from two sources: for **18,251
> programmes** the official rank published by YÖK Atlas, fetched once by `resmi_sira.py`; for the rest
> an estimate interpolated from ÖSYM's own cumulative score-distribution table, marked `≈` in the UI.
> The estimator was measured against the official ranks on all 18,251 overlapping programmes:
> **median deviation 0.25%** ([KALIBRASYON.md](KALIBRASYON.md)). The placement pipeline itself reads
> only ÖSYM's primary files — it was unaffected when YÖK Atlas moved to a SPA in April 2026 — and
> degrades gracefully to estimated ranks if the YÖK Atlas file is absent.
> Live site: **https://osym-yks.vercel.app** · dataset: [`data/`](data/) (JSON + CSV,
> [field reference](data/README.md)) · MCP server: [`mcp_server.py`](mcp_server.py).
> Not affiliated with ÖSYM.

ÖSYM'nin 18 Ağustos 2026'da yayımladığı **resmî** yerleştirme dosyalarını (TABLO-3 + TABLO-4)
tek bir aranabilir veri setine ve yerelde çalışan bir arayüze dönüştürür. Ayrıca ÖSYM'nin
puan tablolarında **yayımlamadığı** başarı sırasını, yine ÖSYM'nin kendi resmî puan dağılımı
tablosundan tahmin eder.

**21.493 program · 779.870 kontenjan · 730.854 yerleşen**

> ✅ **Doğrulama:** Bu veri setinden hesaplanan toplam yerleşen sayısı **730.854**, ÖSYM'nin
> resmî *"Yerleştirme Sonuçlarına İlişkin Sayısal Bilgiler"* PDF'indeki rakamla birebir aynıdır.

---

## Hızlı başlangıç

```bash
python3 server.py            # yerel arayüz -> http://localhost:8787
python3 test_model.py        # 12 değişmez testi
```

Harici bağımlılık yok, `pip install` yok — sadece Python 3'ün standart kütüphanesi.
Veriyi sıfırdan üretmek için tek ek bağımlılık `openpyxl`:

```bash
pip install openpyxl
python3 build_data.py && python3 bolumler.py && python3 ozet.py && python3 test_model.py
```

### MCP sunucusu

Veri setini Claude Desktop gibi MCP istemcilerinden sorgulamak için:

```json
{"mcpServers": {"yks2026": {"command": "python3", "args": ["/MUTLAK/YOL/osym/mcp_server.py"]}}}
```

Araçlar: `bolum_ara` · `bolum_detay` · `program_ara` · `sira_puan`.

## Arayüzde neler var

| Sekme | İçerik |
|---|---|
| **Tüm Programlar** | 21.493 programda arama; düzey / puan türü / üniversite türü / şehir / burs / dil filtreleri; puan, sıralama ve kontenjan aralığı filtreleri; her sütuna göre sıralama; CSV dışa aktarma |
| **🩺 Tıp Paneli** | Kontenjan–kota doluluğu, açık kalan kadrolar (çoktan aza), puan ve sıralama bandı dağılımları, 242 Tıp programının tam listesi |
| **Üniversite Özeti** | 228 üniversite bazında kontenjan, doluluk, en yüksek taban, en iyi sıra |
| **Bölüm Özeti** | 517 bölüm bazında aynı metrikler |
| **Yöntem & Kaynak** | Sıralama tahmininin nasıl yapıldığı ve sınırları |

Sağ üstteki **KKTC dahil / KKTC hariç** anahtarı tüm sekmeleri aynı anda etkiler. "Hariç" modu
hem KKTC'deki üniversiteleri hem de Türkiye'deki üniversitelerin "KKTC Uyruklu" kontenjanlarını çıkarır.

---

## 🩺 Tıp fakültesi — 2026 özeti

| | **KKTC dahil** | **KKTC hariç** |
|---|---|---|
| Tıp programı | 242 | 220 |
| **Toplam kontenjan** | **19.044** | **18.731** |
| **Yerleşen** | **18.993** | **18.693** |
| **Açık kalan kadro** | **54** | **41** |
| Eşit puanla kontenjan üstü yerleşen | +3 | +3 |
| **Doluluk oranı** | **%99,73** | **%99,80** |
| Kota (ÖSYM başarı sırası barajı) | 50.000 | 50.000 |
| Kota kullanımı | %38,0 | %37,4 |
| **En son yerleşen aday** | **464,865 → 49.623. sıra** | **465,445 → 49.111. sıra** |
| En yüksek taban | 559,697 → 1. sıra | aynı |
| En yüksek puan (tavan) | 566,535 | aynı |
| Devlet / Vakıf kontenjanı | 15.219 / 3.530 | 15.201 / 3.530 |

> Sıralar YÖK Atlas'ın **resmî** başarı sırasıdır (Tıp'ta programların %100'ü).

**Açık kalan 54 kadronun dağılımı:** 38'i şehit-gazi yakını, 13'ü KKTC uyruklu, 3'ü okul birincisi
kontenjanından. Genel kontenjanda pratikte boşluk yok.

**Başarı sırası bandına göre Tıp kontenjanı** (KKTC dahil, resmî sıra):

| Başarı sırası bandı | Kontenjan |
|---|---|
| 1 – 1.000 | 328 |
| 1.000 – 5.000 | 2.129 |
| 5.000 – 10.000 | 3.126 |
| 10.000 – 20.000 | 8.154 |
| 20.000 – 30.000 | 3.082 |
| 30.000 – 40.000 | 1.765 |
| 40.000 – 50.000 | 448 |

**Kritik ayrım:** Devlet üniversitesindeki düz **"Tıp" (Türkçe, ücretsiz)** programları — 86 program,
**13.545 kontenjan, %100 dolu** — taban aralığı **1.132. – 21.048. sıra**. Yani klasik anlamda devlet
tıbbı ilk ~21 binde bitiyor. 21.000–49.000 bandını vakıf ücretli/indirimli programlar, MSB/İçişleri
kontenjanları ve UOLP programları dolduruyor.

---

## "İlk 25.000'in 20.000'i tıp yazdı" iddiası

Sosyal medyada dolaşan bu iddia resmî veriyle uyuşmuyor. `analiz_25k.py` bunu **dağılım varsayımı
yapmadan** test eder:

> Bir programa yerleşen **her** aday, o programın taban puanından yüksek puan almıştır.
> Dolayısıyla taban sırası R'den küçük olan programların **tüm** yerleşenleri kesin olarak
> ilk R sıra içindedir → **alt sınır**. Tavan sırası R'den küçük olan programlar da kısmen
> katkı verebilir → **üst sınır**. Gerçek değer bu bandın içindedir.

| İlk N sıra | ≈ Puan | Tıp'a yerleşen (alt–üst) | Oran |
|---|---|---|---|
| 10.000 | 514,13 | 5.803 – 10.000 | %58 – %100 |
| 20.000 | 498,62 | 14.511 – 17.116 | %73 – %86 |
| **25.000** | **492,55** | **15.808 – 18.436** | **%63 – %74** |
| 30.000 | 486,46 | 16.781 – 18.697 | %56 – %62 |
| 50.000 | 464,00 | 18.993 | %38 |

Üç bağımsız gerekçe:

1. **Türkiye'nin tüm Tıp kontenjanı 19.044.** İlk 25 binden 20 bin kişi Tıp kazansaydı, ülkedeki
   tüm Tıp kadrolarının %105'i tek başına ilk 25 binden dolardı. Oysa 20.000–50.000 sıralama bandında
   **4.483 Tıp kontenjanı** dolu durumda.
2. **Üst sınır bile 18.436** — iddia edilen 20.000'in altında.
3. Tıp'a yerleşenlerin **3.186'sı (%17)** zaten 25.000'in gerisinde.

Doğrusu: *ilk 25 binin yaklaşık üçte ikisi (%63–74) tıp kazandı.* Hâlâ çarpıcı, ama %80 değil.

---

## Sıralama nasıl tahmin edildi?

ÖSYM taban puan tablolarında **başarı sırası yayımlamıyor**. Bu proje sıralamayı, ÖSYM'nin kendi
resmî *"2026-YKS Yerleştirme Puanlarının Yığınsal Dağılımı"* tablosundan üretir. Bu tablo her puan
türü için "şu puan ve üstünde kaç aday var" bilgisini 20 puanlık basamaklarla verir
(örn. SAY'da 470+ → 44.919 aday, 490+ → 27.402 aday).

Basamaklar arası **probit interpolasyon** ile doldurulur: puan dağılımının kuyruğu yaklaşık normal
olduğundan, `z = Φ⁻¹(1 − N/N_toplam)` değeri puana karşı neredeyse doğrusaldır. z'yi doğrusal
interpole edip geri çevirmek, ham log-lineer interpolasyondan belirgin biçimde daha isabetlidir —
log-lineer yöntem normal kuyrukta sıraları sistematik olarak fazla iyimser tahmin eder
(ilk 1.000'de %100'ü aşan tutarsız sonuçlar üretiyordu).

**Doğrulama:** ÖSYM kılavuzu Tıp için **50.000 başarı sırası barajı** koyar. Modelin hesapladığı
en düşük Tıp taban sıralaması **49.623** — barajın hemen altında. Bu, modelin Tıp bandında iyi
kalibre olduğunu gösterir. `python3 rank_model.py` çalıştırıldığında model, tablodaki bilinen
basamakları birebir geri üretir.

### Bilinmesi gerekenler

- Bu dosyalardaki puanlar **yerleştirme puanı**dır (sınav puanı + OBP katkısı). ÖSYM'nin sonuç
  belgesindeki resmî **"başarı sırası"** ise OBP'siz **sınav puanına** göre hesaplanır. Bu yüzden
  buradaki sıralamalar YÖK Atlas'ta göreceğiniz resmî başarı sıralarıyla **birebir aynı olmayacaktır**.
  Tıp bandında fark küçüktür, alt bantlarda büyür.
- **550 puanın üstü ekstrapolasyondur.** ÖSYM tablosunun en üst basamağı "550 ve üstü" olduğundan
  ötesi en üst iki basamağın z-eğimiyle uzatılmıştır; arayüzde ⚠ ile işaretlidir.
- Taban/tavan puan ve sıralamalar **Genel Kontenjan** içindir. Okul birincisi, 34 yaş üstü kadın ve
  şehit/gazi yakını kontenjanları ayrı alanlarda tutulur.
- Kesin resmî başarı sıraları, YÖK Atlas 2026 verisi yayımlandığında oradan teyit edilmelidir.

---

## Dosyalar

| Dosya | İşlev |
|---|---|
| `server.py` | Bağımlılıksız yerel HTTP sunucusu (gzip destekli) |
| `index.html` | Tek dosyalık arayüz (vanilla JS, harici CDN yok) |
| `build_data.py` | `kaynak/*.xlsx` → `data/programlar.json` dönüşümü, şehir/burs/dil ayrıştırma, sıralama hesabı |
| `rank_model.py` | ÖSYM yığınsal dağılımı + probit interpolasyon. Tek başına çalıştırılabilir |
| `analiz_25k.py` | "İlk 25.000'in 20.000'i" iddiasının alt/üst sınır testi |
| `ozet.py` | `data/ozet.json` — açılışta yeterli olan 315 KB'lik önceden hesaplanmış özet |
| `bolumler.py` | Panel seçicisindeki bölüm listesi + ÖSYM barajları |
| `test_model.py` | Değişmez/regresyon testleri (`python3 test_model.py`) |
| `mcp_server.py` | Bağımlılıksız MCP sunucusu (stdio, JSON-RPC) |
| `kalibrasyon.py` | Tahminleri YÖK Atlas'ın resmî sıralarıyla karşılaştırır → [KALIBRASYON.md](KALIBRASYON.md) |
| `deploy.sh` | Vercel yayını + kalıcı alias'ın yeniden bağlanması |
| `.github/workflows/ci.yml` | Kaynak bütünlüğü, veri yeniden üretimi ve testler |
| `kaynak/` | ÖSYM'nin değiştirilmemiş orijinal dosyaları + indirme bağlantıları |
| `data/` | Üretilmiş veri seti: `programlar.json`, `programlar.csv`, `ozet.json`, `bolumler.json` — [alan sözlüğü](data/README.md) |

### Veri sözlüğü (`data/programlar.json`)

`kod` · `uni` · `unituru` (DEVLET/VAKIF/KKTC/YURTDISI VAKIF) · `fak` · `prog` · `base` (parantezsiz
bölüm adı) · `pt` (puan türü) · `duzey` · `sehir` · `burs` · `dil` · `kont`/`yer` (genel kontenjan) ·
`min`/`max` (taban/tavan puan) · `smin`/`smax` (tahmini taban/tavan sıra) · `acik` (kontenjan türü
bazında pozitif boşlukların toplamı) · `fazla` (eşit puan nedeniyle kontenjan üstü yerleşen) ·
`tk`/`ty` (tüm kontenjan türleri toplamı) · `ob_*`/`y34_*`/`sehit_*` (özel kontenjanlar) ·
`kktc`/`kktc_uni`/`uolp`/`uzaktan`/`io`/`aof` bayrakları

---

## Canlı sürüm

- **Uygulama:** https://osym-yks.vercel.app
- **Kısa yönlendirme:** https://niedy707.github.io/osym/ → yukarıdaki adrese yönlenir
- **Paylaşım görseli:** [`tip-25k.png`](tip-25k.png) — `paylas.html` dosyasından üretilir

## Lisans ve sorumluluk reddi

Kod MIT lisanslıdır. `kaynak/` altındaki belgeler ÖSYM'ye aittir ve değiştirilmemiştir.

Bu resmî bir ÖSYM ürünü **değildir**. Kontenjan, yerleşen ve puan değerleri resmî dosyalardan
birebir alınmıştır; **sıralamalar tahmindir**. Tercih kararlarında ÖSYM ve YÖK Atlas'ın resmî
yayınlarını esas alın.
