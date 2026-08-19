# -*- coding: utf-8 -*-
"""YOK Atlas 2026 tercih kilavuzu API'sinden RESMI basari siralarini indirir.

Cikti: kaynak/yokatlas_basari_sirasi.json  ->  {"<program kodu>": <basari sirasi>}

Neden ayri bir dosya: OSYM'nin TABLO-3/TABLO-4 dosyalarinda basari sirasi YOK.
YOK Atlas ayni programlar icin resmi basari sirasini yayimliyor. Bu script tek
seferlik/nadir calisir; projenin veri hattı YOK Atlas'a BAGIMLI DEGILDIR —
dosya yoksa build_data.py tahmini siralarla calismaya devam eder.

Kullanim:  python3 resmi_sira.py
"""
import json, os, time, urllib.request

API = 'https://yokatlas.yok.gov.tr/api/tercih-kilavuz/search'
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
CIKTI = 'kaynak/yokatlas_basari_sirasi.json'


def sayfa(no, boyut=1000):
    req = urllib.request.Request(
        API, data=json.dumps({'page': no, 'size': boyut}).encode(),
        headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                 'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def indir():
    ilk = sayfa(0)
    kayit = list(ilk['content'])
    print(f"{ilk['totalElements']} kayıt, {ilk['totalPages']} sayfa")
    for p in range(1, ilk['totalPages']):
        for deneme in range(3):
            try:
                kayit += sayfa(p)['content']
                break
            except Exception as e:
                if deneme == 2:
                    print(f'  sayfa {p} atlandı: {e}')
                time.sleep(2)
        time.sleep(0.35)

    out = {}
    for r in kayit:
        kod, sira = r.get('kilavuzKodu'), r.get('basariSirasi')
        if kod and sira:
            out[str(kod)] = int(sira)

    # Puan tutarliligi: ayni programin taban puani iki kaynakta da ayni mi?
    uyusmaz = 0
    if os.path.exists('data/programlar.json'):
        bizim = {x['kod']: x['min'] for x in json.load(open('data/programlar.json', encoding='utf-8'))}
        for r in kayit:
            k, p = str(r.get('kilavuzKodu')), r.get('minPuan')
            if k in bizim and bizim[k] and p and abs(float(p) - bizim[k]) > 0.001:
                uyusmaz += 1
        print(f'taban puan uyuşmazlığı: {uyusmaz}')

    os.makedirs('kaynak', exist_ok=True)
    json.dump(out, open(CIKTI, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    print(f'{CIKTI} — {len(out)} programda resmî başarı sırası '
          f'({os.path.getsize(CIKTI)/1024:.0f} KB)')


if __name__ == '__main__':
    indir()
