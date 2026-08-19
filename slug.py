# -*- coding: utf-8 -*-
"""Bolum adindan paylasilabilir URL parcasi uretir.

Turkce'ye ozgu harfler once ASCII karsiliklarina cevrilir; aksi halde
unicodedata.normalize 'i'yi noktasiz 'i'ye tasiyip 'İ' ile 'I'yi ayni
sonuca goturmez ve slug'lar tutarsiz olur.
"""
import re, unicodedata

TR = {'ı': 'i', 'İ': 'i', 'I': 'i', 'ğ': 'g', 'Ğ': 'g', 'ü': 'u', 'Ü': 'u',
      'ş': 's', 'Ş': 's', 'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c',
      'â': 'a', 'Â': 'a', 'î': 'i', 'Î': 'i', 'û': 'u', 'Û': 'u'}


def slug(ad):
    s = ''.join(TR.get(c, c) for c in ad).lower()
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return re.sub(r'-{2,}', '-', s)
