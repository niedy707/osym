# -*- coding: utf-8 -*-
"""2026-YKS yerlestirme puani -> tahmini basari sirasi.

Kaynak: OSYM "2026-YKS Sinav Sonuclarina Iliskin Sayisal Bilgiler" PDF'i,
"2026-YKS YERLESTIRME PUANLARININ YIGINSAL DAGILIMI" tablosu (resmi).

Yontem: PROBIT interpolasyon. Puan dagiliminin kuyrugu yaklasik normal
oldugu icin, z = Phi^-1(1 - N/Ntoplam) degeri puana karsi neredeyse
dogrusaldir. Iki basamak arasinda z'yi dogrusal interpole edip geri
cevirmek, ham log-lineer interpolasyondan belirgin sekilde daha isabetli
sonuc verir (log-lineer, normal kuyrukta siralari sistematik olarak fazla
iyimser tahmin eder).
"""
import math

CUM = {
 'TYT': [(550,112),(530,2045),(510,8638),(490,22600),(470,45313),(450,76021),(430,115071),
         (410,163211),(390,225038),(370,305570),(350,412011),(330,553526),(310,735519),
         (290,961261),(270,1219171),(250,1499060),(230,1782951),(210,2033331),(190,2166477),
         (170,2186977),(150,2187734),(130,2187742),(115,2187743)],
 'SAY': [(550,154),(530,3500),(510,12887),(490,27402),(470,44919),(450,63669),(430,83511),
         (410,105112),(390,129485),(370,157778),(350,191247),(330,232317),(310,282213),
         (290,344726),(270,425443),(250,533920),(230,681176),(210,858167),(190,1019046),
         (170,1117304),(150,1135198),(130,1135713),(115,1135718)],
 'SÖZ': [(550,4),(530,14),(510,69),(490,221),(470,606),(450,1566),(430,4058),(410,10184),
         (390,22750),(370,45237),(350,82479),(330,140496),(310,223004),(290,333238),
         (270,474443),(250,642816),(230,814264),(210,953036),(190,1040347),(170,1078859),
         (150,1085505),(130,1085697),(115,1085698)],
 'EA':  [(550,12),(530,98),(510,394),(490,1118),(470,2482),(450,5299),(430,12363),(410,29700),
         (390,58772),(370,97839),(350,148570),(330,215631),(310,307918),(290,429479),
         (270,585271),(250,775922),(230,990764),(210,1196809),(190,1347025),(170,1412649),
         (150,1421093),(130,1421289),(115,1421290)],
 'DİL': [(550,14),(530,231),(510,942),(490,2252),(470,4241),(450,7472),(430,12254),(410,18566),
         (390,26352),(370,34585),(350,43129),(330,51784),(310,60948),(290,70670),(270,81109),
         (250,92274),(230,104127),(210,116152),(190,125789),(170,131233),(150,132714),
         (130,132825),(115,132826)],
}
ALIAS = {'SÖZEL':'SÖZ','EŞİT AĞIRLIK':'EA','DIL':'DİL','SOZ':'SÖZ'}
NTOT = {k: v[-1][1] for k, v in CUM.items()}   # puan turu basina toplam aday


def _ndtr(z):
    "Standart normal birikimli dagilim."
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _ndtri(p):
    "Standart normal ters birikimli dagilim (Acklam yaklasimi + 1 Halley adimi)."
    if p <= 0.0: return -40.0
    if p >= 1.0: return 40.0
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00)
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p <= ph:
        q = p - 0.5; r = q * q
        x = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    e = _ndtr(x) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


def _z(n, ntot):
    "N kisilik ust kuyruga karsilik gelen z degeri."
    return _ndtri(1.0 - min(max(n / ntot, 1e-12), 1 - 1e-12))


def rank(puan, tur):
    """Yerlestirme puanindan tahmini sira. (sira, guven_etiketi) dondurur."""
    tur = ALIAS.get(tur, tur)
    pts = CUM.get(tur)
    if pts is None or puan is None:
        return None, None
    ntot = NTOT[tur]
    hi_p, hi_n = pts[0]
    lo_p, lo_n = pts[-1]
    if puan >= hi_p:
        # 550 ustu: en ust iki basamagin z-egimiyle uzatma (DUSUK GUVEN)
        p2, n2 = pts[0]; p1, n1 = pts[1]
        z2, z1 = _z(n2, ntot), _z(n1, ntot)
        z = z2 + (z2 - z1) / (p2 - p1) * (puan - p2)
        est = ntot * (1 - _ndtr(z))
        return max(1, int(round(est))), 'ekstrapolasyon'
    if puan <= lo_p:
        return int(lo_n), 'alt-sinir'
    for i in range(len(pts) - 1):
        p_hi, n_hi = pts[i]
        p_lo, n_lo = pts[i + 1]
        if p_lo <= puan < p_hi:
            f = (puan - p_lo) / (p_hi - p_lo)
            z = _z(n_lo, ntot) + f * (_z(n_hi, ntot) - _z(n_lo, ntot))
            est = ntot * (1 - _ndtr(z))
            return max(1, int(round(est))), 'interpolasyon'
    return None, None


def puan_at_rank(R, tur='SAY'):
    """Verilen siraya karsilik gelen yerlestirme puani (rank fonksiyonunun tersi)."""
    tur = ALIAS.get(tur, tur)
    pts = CUM[tur]; ntot = NTOT[tur]
    zR = _z(R, ntot)
    for i in range(len(pts) - 1):
        p_hi, n_hi = pts[i]; p_lo, n_lo = pts[i + 1]
        z_hi, z_lo = _z(n_hi, ntot), _z(n_lo, ntot)
        if z_lo <= zR <= z_hi:
            f = (zR - z_lo) / (z_hi - z_lo)
            return p_lo + f * (p_hi - p_lo)
    if R < pts[0][1]:                      # 550 ustu ekstrapolasyon
        p2, n2 = pts[0]; p1, n1 = pts[1]
        z2, z1 = _z(n2, ntot), _z(n1, ntot)
        return p2 + (zR - z2) * (p2 - p1) / (z2 - z1)
    return pts[-1][0]


if __name__ == '__main__':
    print("Kalibrasyon kontrolu — bilinen basamaklar birebir donmeli:")
    for p, n in CUM['SAY'][:8]:
        r, _ = rank(p - 1e-9, 'SAY')
        print(f"  {p}: resmi {n:>7,} | model {r:>7,}".replace(',', '.'))
    print("\nTip aralaginda ornek puanlar:")
    for p in (559.69717, 551.58605, 537.80956, 526.97542, 497.82994, 472.58645, 465.44458, 464.86489):
        r, c = rank(p, 'SAY')
        print(f"  SAY {p:10.5f} -> ~{r:>8,}. sira ({c})".replace(',', '.'))
    print("\nSira -> puan:")
    for R in (1000, 10000, 25000, 50000):
        print(f"  {R:>6,}. sira -> {puan_at_rank(R):.2f} puan".replace(',', '.'))
