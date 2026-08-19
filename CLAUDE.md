# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static, dependency-free site that turns ÖSYM's official 2026-YKS placement files into a searchable
dataset, and adds an **estimated başarı sırası (success rank)** that ÖSYM does not publish. Turkish is
the language of the UI, the data, the commit messages and the code comments — keep it that way.

## Commands

```bash
python3 server.py                 # yerel sunucu -> http://localhost:8787 (PORT env ile değiştirilir)
python3 build_data.py             # kaynak/*.xlsx -> data/programlar.json   (openpyxl gerekir)
python3 bolumler.py               # data/programlar.json -> data/bolumler.json
python3 rank_model.py             # modelin kendi kendini doğrulaması (basamakları birebir üretmeli)
python3 analiz_25k.py             # "ilk 25.000'in 20.000'i tıp" iddiasının alt/üst sınır testi
vercel --prod --yes               # Vercel'e yayın
```

**Regeneration order matters:** `build_data.py` must run before `bolumler.py` — the latter reads
`data/programlar.json`. Any edit to `rank_model.py` invalidates both JSON files; rebuild both.

There is no test suite, no linter and no build step. Verification is done against the invariants below.

Paylaşım görsellerini üretmek (headless Chrome, `paylas.html` / `paylas-tw.html` kaynak):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --force-device-scale-factor=2 --window-size=1200,1500 --hide-scrollbars --screenshot=out.png "file://$PWD/paylas.html"
```

## Architecture

```
kaynak/tablo3.xlsx  ─┐
kaynak/tablo4.xlsx  ─┴─> build_data.py ─> data/programlar.json ─> bolumler.py ─> data/bolumler.json
                              │                    │                                    │
                        rank_model.py              └────────> index.html <──────────────┘
                     (probit interpolasyon)                (tek dosya, framework yok)
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
- **`index.html`** is one self-contained file: vanilla JS, no CDN, no bundler. It fetches both JSON
  files and renders tables on desktop, cards on mobile (`mobil()` = width < 768). Editing it means
  editing the deployed artifact directly.
- **`server.py`** exists mainly to gzip the 14 MB JSON down to ~1.3 MB; stdlib only.

## Domain invariants — check these after touching the pipeline

Regressions here are silent and end up in public infographics, so verify explicitly:

| Kontrol | Beklenen |
|---|---|
| Toplam yerleşen (tüm veri) | **730.854** — ÖSYM'nin resmî PDF'iyle birebir |
| Tıp toplam kontenjan / yerleşen | 19.044 / 18.993 (KKTC dahil) |
| En dip taban sırası: Tıp / Diş / Eczacılık / Hukuk | 49.241 / 79.783 / 99.643 / 99.923 |
| ÖSYM barajı: Tıp / Diş / Eczacılık / Hukuk | 50.000 / 80.000 / 100.000 / 100.000 |
| Mimarlık / Mühendislik / Öğretmenlik | 250.397, 300.841, 300.488 vs. baraj 250.000 / 300.000 / 300.000 |

The last three rows are the model's only real accuracy test: a bölüm's bottom program must land just
under ÖSYM's threshold. Deviation is currently %0,1–1,5. If a change pushes it outside ~2%, the change
is wrong, not the data.

## Concepts that are easy to get wrong

- **Yerleştirme puanı ≠ başarı sırası.** The scores in TABLO-3/4 are *yerleştirme puanı* (sınav puanı +
  OBP katkısı). ÖSYM's official *başarı sırası* is computed on the OBP-free sınav puanı. Ranks here are
  therefore close to, but never identical to, YÖK Atlas. Say so wherever a rank is shown.
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

Live at <https://niedy707.github.io/osym/> (primary) and <https://osym-tau.vercel.app> (mirror).

**The repo name must stay lowercase.** GitHub Pages paths are case-sensitive, while ekşi sözlük and
several other platforms display link text lowercased — a repo named `OSYM` gave readers a 404 when they
retyped what they saw. Also avoid `≈`, `≥` and similar characters in text posted to ekşi sözlük; they
are mangled server-side into `?`.
