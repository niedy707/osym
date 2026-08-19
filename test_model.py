# -*- coding: utf-8 -*-
"""Sessiz regresyonlara karsi altin-deger testleri.

Buradaki sayilar dogrudan halka acik infografiklere gidiyor. Modelde yapilan bir
degisiklik sonucu makul GORUNEN ama yanlis bir sayi uretebilir; bu testler o
sessiz bozulmayi yakalar. Calistir:  python3 test_model.py
"""
import json, os, unittest
import rank_model

VERI = 'data/programlar.json'


def yukle():
    if not os.path.exists(VERI):
        raise unittest.SkipTest(f'{VERI} yok — once: python3 build_data.py')
    return json.load(open(VERI, encoding='utf-8'))


class ModelKalibrasyonu(unittest.TestCase):
    """rank_model, OSYM'nin yayimladigi basamaklari birebir geri uretmeli."""

    def test_basamaklar_birebir(self):
        for tur, tablo in rank_model.CUM.items():
            for puan, n in tablo[:-1]:            # son satir alt sinir, ayri ele alinir
                r, _ = rank_model.rank(puan - 1e-9, tur)
                self.assertEqual(r, n, f'{tur} {puan} basamagi: beklenen {n}, bulunan {r}')

    def test_sira_puan_tersi_tutarli(self):
        for R in (100, 1000, 10_000, 50_000, 300_000):
            p = rank_model.puan_at_rank(R, 'SAY')
            geri, _ = rank_model.rank(p, 'SAY')
            self.assertLess(abs(geri - R) / R, 0.02, f'{R}. sira -> {p:.2f} -> {geri}')

    def test_sira_puanla_monoton(self):
        onceki = None
        for puan in range(150, 560, 10):
            r, _ = rank_model.rank(puan, 'SAY')
            if onceki is not None:
                self.assertLessEqual(r, onceki, f'{puan} puanda sira kotulesti')
            onceki = r


class VeriDegismezleri(unittest.TestCase):
    """OSYM'nin resmi toplamlariyla ve barajlariyla uyum."""

    @classmethod
    def setUpClass(cls):
        cls.rows = yukle()

    def test_toplam_yerlesen_osym_ile_ayni(self):
        # OSYM "Yerlestirme Sonuclarina Iliskin Sayisal Bilgiler" PDF'i: 730.854
        self.assertEqual(sum(r['ty'] for r in self.rows), 730_854)

    def test_program_sayisi(self):
        self.assertEqual(len(self.rows), 21_493)

    def test_tip_kontenjani(self):
        T = [r for r in self.rows if r['base'] == 'Tıp' and r['duzey'] == 'Lisans']
        self.assertEqual(sum(r['tk'] for r in T), 19_044)
        self.assertEqual(sum(r['ty'] for r in T), 18_993)

    def test_acik_ve_fazla_ayri_sayiliyor(self):
        # Esit puan nedeniyle kontenjan ustu yerlestirme, gercek bosluklari maskelememeli
        T = [r for r in self.rows if r['base'] == 'Tıp' and r['duzey'] == 'Lisans']
        self.assertEqual(sum(r['acik'] for r in T), 54)
        self.assertEqual(sum(r['fazla'] for r in T), 3)

    def test_barajlar(self):
        """Bir bolumun en dipteki programi, OSYM barajinin hemen ALTINDA olmali.

        Modelin tek gercek dogruluk testi bu. Sapma su an %0,1-1,5; %3'u asarsa
        degisiklik yanlistir, veri degil.
        """
        BARAJ = {'Tıp': 50_000, 'Diş Hekimliği': 80_000, 'Eczacılık': 100_000,
                 'Hukuk': 100_000, 'Mimarlık': 250_000, 'Bilgisayar Mühendisliği': 300_000,
                 'Makine Mühendisliği': 300_000, 'Elektrik-Elektronik Mühendisliği': 300_000,
                 'Okul Öncesi Öğretmenliği': 300_000, 'Türkçe Öğretmenliği': 300_000}
        for bolum, baraj in BARAJ.items():
            sirs = [r['smin'] for r in self.rows
                    if r['base'] == bolum and r['duzey'] == 'Lisans' and r['smin']]
            self.assertTrue(sirs, f'{bolum}: program bulunamadi')
            dip = max(sirs)
            sapma = abs(dip - baraj) / baraj
            self.assertLess(sapma, 0.03,
                            f'{bolum}: baraj {baraj:,}, en dip sira {dip:,}, sapma %{sapma*100:.1f}')

    def test_yuzde_alani_puan_turune_gore(self):
        for r in self.rows:
            if r.get('yuzde') is None:
                continue
            self.assertLessEqual(r['yuzde'], 100.0001)
            beklenen = 100 * r['smin'] / rank_model.NTOT[r['pt']]
            self.assertAlmostEqual(r['yuzde'], beklenen, places=3)

    def test_550_ustu_ekstrapolasyon_isaretli(self):
        ust = [r for r in self.rows if r['min'] and r['min'] > 550]
        self.assertTrue(ust, '550 üstü program yok — veri seti şüpheli')
        for r in ust:
            self.assertEqual(r['guven'], 'ekstrapolasyon', f"{r['kod']}: guven etiketi yanlis")


if __name__ == '__main__':
    unittest.main(verbosity=2)
