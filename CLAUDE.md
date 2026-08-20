# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static, dependency-free site that turns ÖSYM's official 2026-YKS placement files into a searchable
dataset and attaches the **başarı sırası (success rank)** that ÖSYM does not publish in those files.
Ranks come from two sources — YÖK Atlas's official rank where it exists, the model's estimate
otherwise. Turkish is
the language of the UI, the data, the commit messages and the code comments — keep it that way.

## Commands

```bash
python3 server.py                 # yerel sunucu -> http://localhost:8787 (PORT env ile değiştirilir)
python3 test_model.py             # 12 değişmez/regresyon testi — her değişiklikten sonra koş
python3 rank_model.py             # modelin kendi kendini doğrulaması (basamakları birebir üretmeli)
./deploy.sh                       # Vercel'e yayın + alias'ı yeniden bağla
```

Veri hattı (bu **sırayla** koşar, her adım öncekinin çıktısını okur):

```bash
pip install openpyxl
python3 resmi_sira.py             # (nadiren) YÖK Atlas -> kaynak/yokatlas_basari_sirasi.json
python3 build_data.py             # kaynak/*.xlsx + resmî sıra -> data/programlar.{json,csv}
python3 bolumler.py               # -> data/bolumler.json      (panel seçicisi + barajlar)
python3 ozet.py                   # -> data/ozet.json          (açılışta inen küçük özet)
python3 dagilim.py                # -> data/dagilim.json       (çizgi grafik serileri)
python3 kalibrasyon.py <resmi.json>   # -> KALIBRASYON.md
python3 analiz_25k.py             # "ilk 25.000'in 20.000'i tıp" iddiasının alt/üst sınır testi
```

`rank_model.py`'ye dokunmak dört JSON'u da geçersiz kılar; hepsini yeniden üret.
CI (`.github/workflows/ci.yml`) bu üretimi sıfırdan koşup `git diff --exit-code -- data/` ile
depodakiyle karşılaştırır — çıktı **belirlenimci** olmalı (sıralamalarda tie-break şart).

Paylaşım görsellerini üretmek (headless Chrome, `paylas.html` / `paylas-tw.html` kaynak):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --force-device-scale-factor=2 --window-size=1200,1500 --hide-scrollbars --screenshot=out.png "file://$PWD/paylas.html"
```

## Architecture

```
kaynak/tablo3.xlsx ─┐                                    ┌─> bolumler.py ─> bolumler.json ─┐
kaynak/tablo4.xlsx ─┼─> build_data.py ─> programlar.json ─┼─> ozet.py     ─> ozet.json     ─┤
yokatlas_basari_    │        ▲              + .csv        └─> dagilim.py  ─> dagilim.json  ─┤
  sirasi.json ──────┘        │                                                             │
                       rank_model.py                          index.html <─────────────────┘
                    (probit interpolasyon)                 (tek dosya, framework yok)
```

- **`rank_model.py` is the analytical core.** `CUM` is the *"2026-YKS Yerleştirme Puanlarının Yığınsal
  Dağılımı"* table transcribed by hand from `kaynak/sinav_sb.pdf` — it is source data, not code; do not
  "clean it up". `rank(puan, tur)` interpolates between its 20-point steps in **probit space**
  (`z = Φ⁻¹(1 − N/N_toplam)`), because the score tail is roughly normal. A plain log-linear
  interpolation was tried first and was systematically too optimistic — it produced >100% of the top
  1.000 belonging to a single bölüm. Do not revert to it.
- **`build_data.py`** flattens ÖSYM's 22-column layout (4 quota types × kontenjan/yerleşen/min/max) into
  one record per program, derives `sehir` / `burs` / `dil` / `base` (parenthesis-free program name) and
  attaches `smin`/`smax`/`yuzde`.
- **`bolumler.py`** picks which bölümler appear in the panel's dropdown: union of "more than 1% of the
  kontenjan whose taban sıra is inside the top 2.000" and the same test for the top 50.000. It also
  holds `BARAJ_TAM` / `BARAJ_SONEK`, ÖSYM's official 2026 başarı sırası thresholds.
- **`index.html`** is one self-contained file: vanilla JS, no CDN, no bundler. On load it fetches
  only `ozet.json` + `bolumler.json` (~44 KB gzipped); the 15 MB `programlar.json` and the 806 KB
  `dagilim.json` are **lazy-loaded** when a tab needs them. Desktop renders tables, mobile renders
  cards or single-line rows (`mobil()` = width < 768). Editing it means editing the deployed artifact.
- **`ozet.py` / `dagilim.py`** precompute everything the default tabs need so the first paint does
  not require the full dataset. `dagilim.py` also enforces a physical constraint: a 1.000-rank bucket
  cannot hold more than 1.000 people, and the excess is *moved* to neighbouring buckets rather than
  clipped, so each bölüm's curve still integrates to its real yerleşen count.
- **`resmi_sira.py`** fetches YÖK Atlas's official ranks once into `kaynak/`. The pipeline is **not**
  dependent on it — if the file is missing, everything falls back to estimated ranks.
- **`server.py`** serves with gzip and falls back to `index.html` for extension-less paths, mirroring
  the Vercel rewrite that powers `/tip`, `/hemsirelik` etc.; stdlib only.

## Domain invariants — check these after touching the pipeline

Regressions here are silent and end up in public infographics, so verify explicitly:

| Kontrol | Beklenen |
|---|---|
| Toplam yerleşen (tüm veri) | **730.854** — ÖSYM'nin resmî PDF'iyle birebir |
| Tıp toplam kontenjan / yerleşen | 19.044 / 18.993 (KKTC dahil) |
| En dip **gösterilen** sıra (`sira`): Tıp / Diş / Mimarlık | 49.623 / 79.895 / 250.279 |
| ÖSYM barajı: Tıp / Diş / Eczacılık / Hukuk / Mimarlık | 50.000 / 80.000 / 100.000 / 100.000 / 250.000 |
| Modelin kalibrasyonu (18.251 programda) | medyan sapma **%0,25** — `KALIBRASYON.md` |
| Dağılım grafiği: her puan türünde kova toplamı | **≤ 1.000**, eğri toplamı = gerçek yerleşen |

`test_model.py` bunların hepsini koşuyor; elle kontrol yerine onu çalıştır. Baraj satırı artık
doğruluk testi değil **veri bütünlüğü** testidir: resmî sıra barajın üstüne çıkamaz. Modelin
doğruluğu ayrı olarak `KALIBRASYON.md`'de ölçülür.

## Concepts that are easy to get wrong

- **Three rank fields, do not confuse them.** `rsira` = YÖK Atlas's official başarı sırası (18.251
  programmes). `smin` = the model's estimate, always kept for calibration. `sira` = what the UI shows
  (`rsira` if present, else `smin`), and `sirakaynak` says which. Everything user-facing —
  `yuzde`, summaries, charts, baraj checks — must use `sira`, never `smin`.
- **Yerleştirme puanı ≠ başarı sırası.** The scores in TABLO-3/4 are *yerleştirme puanı* (sınav puanı +
  OBP katkısı); the official başarı sırası is computed on the OBP-free sınav puanı. That is why the
  *estimate* never matches YÖK Atlas exactly (median deviation 0,25%). Where `rsira` exists the
  displayed rank **is** the official one — do not label it "tahmini". Mark estimates with `≈`.
- **Ranks are not comparable across puan türü.** SAY has 1.135.718 candidates, DİL only 132.826 — rank
  15.000 means something completely different in each. Any cross-bölüm comparison must use the `yuzde`
  field (percentile within own puan türü), never `smin`. Ranking by raw `smin` made Japonca
  Öğretmenliği look more competitive than Tıp.
- **`acik` vs `fazla`.** ÖSYM places *above* quota when applicants tie on score, so a naive
  `kontenjan − yerleşen` nets out real vacancies. `acik` sums only positive gaps per quota type;
  `fazla` tracks the over-placements separately. Never report the net.
- **"KKTC" means two different things:** universities based in Northern Cyprus (`kktc_uni`) *and*
  "KKTC Uyruklu" quotas at mainland universities (`kktc`). The UI's KKTC toggle excludes both; default
  is **hariç**. Any KKTC-related figure must state which sense is used.
- **Scores above 550 are extrapolated** — ÖSYM's table stops at "550 ve üstü". These are flagged with ⚠
  in the UI; keep the flag.

## Shareable images

`paylas.html` and `paylas-tw.html` are standalone infographic sources rendered to PNG via headless
Chrome. Every chart card must name the bölüm it describes (`TIP FAKÜLTESİ — …`) so a cropped screenshot
cannot be mistaken for another bölüm's data. `paylas.html` carries an "ekşisözlük için oluşturulmuştur"
badge; the Twitter variant must not.

## Deployment

Live at <https://osym-yks.vercel.app> (primary). <https://niedy707.github.io/osym/> is a redirect
stub served from `docs/` — it must keep working, older ekşi sözlük entries and a tweet link to it.

Deploy with `./deploy.sh`, never bare `vercel --prod`: `osym-yks.vercel.app` is an alias, not a
project domain, so it must be re-pointed at each new production deployment.

**The repo name must stay lowercase.** GitHub Pages paths are case-sensitive, while ekşi sözlük and
several other platforms display link text lowercased — a repo named `OSYM` gave readers a 404 when they
retyped what they saw. Also avoid `≈`, `≥` and similar characters in text posted to ekşi sözlük; they
are mangled server-side into `?`.
