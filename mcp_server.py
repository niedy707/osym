#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-YKS veri seti icin MCP sunucusu — stdio, JSON-RPC 2.0, bagimliliksiz.

Claude Desktop / diger MCP istemcileri icin yapilandirma:

    {"mcpServers": {"yks2026": {
        "command": "python3",
        "args": ["/MUTLAK/YOL/osym/mcp_server.py"]}}}

Sunulan araclar:
  bolum_ara        — bolum adina gore ozet (kontenjan, doluluk, basari sirasi araligi)
  program_ara      — universite/bolum/sehir filtreleriyle program listesi
  bolum_detay      — tek bolumun tam ozeti + siralama bandi dagilimi
  sira_puan        — bir tahmini siranin karsiligi olan yerlestirme puani (ve tersi)

NOT: siralar cogunlukla YOK Atlas'in RESMI basari sirasi; resmi sirasi olmayan
programlarda model tahmini kullanilir (sirakaynak alanina bakin).
"""
import json, os, sys

KOK = os.path.dirname(os.path.abspath(__file__))
_veri = {}


def yukle(ad):
    if ad not in _veri:
        with open(os.path.join(KOK, 'data', ad), encoding='utf-8') as f:
            _veri[ad] = json.load(f)
    return _veri[ad]


def norm(s):
    s = (s or '').casefold()
    for a, b in (('ı', 'i'), ('ğ', 'g'), ('ü', 'u'), ('ş', 's'), ('ö', 'o'), ('ç', 'c'), ('â', 'a')):
        s = s.replace(a, b)
    return s


def _ozet(kktc):
    return yukle('ozet.json')['bolumler']['in' if kktc else 'out']


# ---------------------------------------------------------------- araclar
def bolum_ara(sorgu='', kktc_dahil=False, limit=20, sirala='rekabetci'):
    q = norm(sorgu)
    v = [b for b in _ozet(kktc_dahil) if not q or q in norm(b['ad'])]
    v.sort(key={'rekabetci': lambda b: b['dilim'],
                'kontenjan': lambda b: -b['kont'],
                'puan': lambda b: -(b['enIyiPuan'] or 0)}.get(sirala, lambda b: b['dilim']))
    return [{k: b[k] for k in ('ad', 'pt', 'prog', 'kont', 'yer', 'acik', 'dol',
                               'dilim', 'enIyiPuan', 'enDusukPuan', 'enIyiSira', 'enDipSira', 'baraj')}
            for b in v[:max(1, min(int(limit), 200))]]


def bolum_detay(bolum, kktc_dahil=False):
    q = norm(bolum)
    for b in _ozet(kktc_dahil):
        if norm(b['ad']) == q:
            return b
    aday = [b for b in _ozet(kktc_dahil) if q in norm(b['ad'])]
    if not aday:
        return {'hata': f'"{bolum}" bulunamadı'}
    return aday[0] if len(aday) == 1 else {'birden_fazla_eslesme': [b['ad'] for b in aday[:20]]}


def program_ara(bolum='', universite='', sehir='', puan_turu='', duzey='Lisans',
                kktc_dahil=False, limit=50):
    rows = yukle('programlar.json')
    qb, qu, qs = norm(bolum), norm(universite), norm(sehir)
    out = []
    for r in rows:
        if duzey and r['duzey'] != duzey: continue
        if puan_turu and r['pt'] != puan_turu: continue
        if not kktc_dahil and (r.get('kktc') or r.get('kktc_uni')): continue
        if qb and qb not in norm(r['base']) and qb not in norm(r['prog']): continue
        if qu and qu not in norm(r['uni']): continue
        if qs and qs not in norm(r['sehir']): continue
        out.append({k: r[k] for k in ('kod', 'uni', 'sehir', 'prog', 'pt', 'unituru', 'burs',
                                      'tk', 'ty', 'acik', 'min', 'max', 'smin', 'smax', 'yuzde')})
        if len(out) >= max(1, min(int(limit), 500)): break
    out.sort(key=lambda r: -(r['min'] or 0))
    return out


def sira_puan(sira=None, puan=None, puan_turu='SAY'):
    sys.path.insert(0, KOK)
    import rank_model
    if sira is not None:
        p = rank_model.puan_at_rank(float(sira), puan_turu)
        return {'puan_turu': puan_turu, 'sira': sira, 'yerlestirme_puani': round(p, 3),
                'not': 'tahmindir'}
    if puan is not None:
        r, g = rank_model.rank(float(puan), puan_turu)
        return {'puan_turu': puan_turu, 'yerlestirme_puani': puan, 'tahmini_sira': r,
                'guven': g, 'not': 'tahmindir'}
    return {'hata': 'sira veya puan verilmeli'}


ARACLAR = [
    ('bolum_ara', 'Bölümleri ara ve özetlerini döndür (kontenjan, doluluk, başarı sırası aralığı).',
     {'sorgu': ('string', 'Bölüm adı parçası; boş bırakılırsa tümü'),
      'sirala': ('string', "rekabetci | kontenjan | puan"),
      'kktc_dahil': ('boolean', 'KKTC üniversiteleri ve KKTC uyruklu kontenjanları dahil et'),
      'limit': ('integer', 'En fazla kaç bölüm (varsayılan 20)')}, bolum_ara),
    ('bolum_detay', 'Tek bölümün tam özeti ve başarı sırası bandı dağılımı.',
     {'bolum': ('string', 'Bölüm adı'), 'kktc_dahil': ('boolean', '')}, bolum_detay),
    ('program_ara', 'Program listesi: bölüm/üniversite/şehir/puan türü filtreleriyle.',
     {'bolum': ('string', ''), 'universite': ('string', ''), 'sehir': ('string', ''),
      'puan_turu': ('string', 'SAY | EA | SÖZ | DİL | TYT'),
      'duzey': ('string', 'Lisans | Ön Lisans'), 'kktc_dahil': ('boolean', ''),
      'limit': ('integer', 'Varsayılan 50')}, program_ara),
    ('sira_puan', 'Sıra <-> yerleştirme puanı dönüşümü (model tahmini).',
     {'sira': ('integer', ''), 'puan': ('number', ''), 'puan_turu': ('string', 'SAY | EA | SÖZ | DİL | TYT')},
     sira_puan),
]


def sema(alanlar):
    return {'type': 'object',
            'properties': {a: {'type': t, **({'description': d} if d else {})}
                           for a, (t, d) in alanlar.items()}}


def islem(istek):
    m, pid = istek.get('method'), istek.get('id')
    if m == 'initialize':
        return {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}},
                'serverInfo': {'name': 'yks2026', 'version': '1.0.0'}}
    if m == 'tools/list':
        return {'tools': [{'name': n, 'description': d, 'inputSchema': sema(a)}
                          for n, d, a, _ in ARACLAR]}
    if m == 'tools/call':
        ad = istek['params']['name']
        arg = istek['params'].get('arguments') or {}
        for n, _, _, fn in ARACLAR:
            if n == ad:
                try:
                    sonuc = fn(**arg)
                except Exception as e:                       # istemciye hata olarak don
                    return {'content': [{'type': 'text', 'text': f'Hata: {e}'}], 'isError': True}
                return {'content': [{'type': 'text',
                                     'text': json.dumps(sonuc, ensure_ascii=False, indent=1)}]}
        raise ValueError(f'bilinmeyen araç: {ad}')
    raise ValueError(f'desteklenmeyen method: {m}')


def main():
    for satir in sys.stdin:
        satir = satir.strip()
        if not satir:
            continue
        try:
            istek = json.loads(satir)
        except json.JSONDecodeError:
            continue
        if 'id' not in istek:                                 # bildirim: yanit yok
            continue
        try:
            yanit = {'jsonrpc': '2.0', 'id': istek['id'], 'result': islem(istek)}
        except Exception as e:
            yanit = {'jsonrpc': '2.0', 'id': istek['id'],
                     'error': {'code': -32603, 'message': str(e)}}
        sys.stdout.write(json.dumps(yanit, ensure_ascii=False) + '\n')
        sys.stdout.flush()


if __name__ == '__main__':
    main()
