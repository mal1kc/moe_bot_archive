from moe_gatherer.kaynakislem import KaynakFare, Varsayilanlar
from moe_gatherer.sabitler import TaramaSabitleri
from moe_gatherer.temel_siniflar import Koordinat2D


def testKisitliBolgeler():
    for tiklama_kistilamasi in Varsayilanlar.TIKLAMA_KISITLAMALARI:
        for k, v in tiklama_kistilamasi.items():
            assert isinstance(v, int)
            assert v >= 0


def testBolgeKisitlimi_1920():
    kisitli_olan_bolgeler_1920 = {
        Koordinat2D(330, 440),
        Koordinat2D(423, 130),
        Koordinat2D(500, 170),
        Koordinat2D(330, 0),
        Koordinat2D(520, 1840),
        Koordinat2D(820, 950),
    }
    kisitli_olmayan_bolgeler_1920 = {
        Koordinat2D(960, 120),
        Koordinat2D(1420, 400),
        Koordinat2D(0, 440),
    }
    kaynak_fare = KaynakFare()
    kaynak_fare.tiklama_kisitlamalari: list[dict] = TaramaSabitleri.TIKLAMA_KISITLAMALARI["_1920"]  # type: ignore
    # kaynak_fare.tiklama_kisitlamalari = [
    #     {
    #         "x_taban": 290,  # 290+
    #         "x_tavan": 540,  # 540-
    #         "y_taban": 0,  # 0+
    #         "y_tavan": 550,  # 550-
    #         # kombinleniyor x: 540-290 , y: 500-0
    #     },
    #     {
    #         # "sefer_x_tavan": 580,  # 580-
    #         # "sefer_x_taban": 130,  # 130+
    #         # kombinleniyor x:500-130
    #         # eğer nokta x 500-130 arasında ise z ye basar ve tiklama yapar
    #     },
    #     {"y_taban": 820},  # ölü bölge , 820+
    #     {"x_taban": 1750},  # ölü bölge  1750+
    # ]

    # sefer tarayici ile ilgili kisitlamalari kaldiriyoruz
    for i in kaynak_fare.tiklama_kisitlamalari:
        for k, v in i.items():
            if k.startswith("sefer"):
                kaynak_fare.tiklama_kisitlamalari.remove(i)
                break

    for bolge in kisitli_olan_bolgeler_1920:
        assert kaynak_fare._bolge_kisitlimi(bolge)

    for bolge in kisitli_olmayan_bolgeler_1920:
        assert not kaynak_fare._bolge_kisitlimi(bolge)


def testBolgeKisitlimi_1366():
    kisitli_olan_bolgeler_1366 = {
        Koordinat2D(170, 300),
    }
    kisitli_olmayan_bolgeler_1366 = [
        Koordinat2D(1000, 300),
        Koordinat2D(900, 300),
        Koordinat2D(905, 354),
        Koordinat2D(1040, 480),
        Koordinat2D(550, 170),
        Koordinat2D(410, 510),
    ]
    kaynak_fare = KaynakFare()
    # kaynak_fare.tiklama_kisitlamalari: list[dict] = TaramaSabitleri.TIKLAMA_KISITLAMALARI["_1366"]  # type: ignore
    kaynak_fare.tiklama_kisitlamalari = [
        {
            "x_taban": 0,
            "x_tavan": 400,
            "y_taban": 0,
            "y_tavan": 440,
            # kombinleniyor x: 540-290 , y: 500-0
        },
        {"y_taban": 560},  # ölü bölge , 820+
        {"x_taban": 1270},
    ]

    # sefer tarayici ile ilgili kisitlamalari kaldiriyoruz
    for i in kaynak_fare.tiklama_kisitlamalari:
        for k, v in i.items():
            if k.startswith("sefer"):
                kaynak_fare.tiklama_kisitlamalari.remove(i)
                break

    for bolge in kisitli_olan_bolgeler_1366:
        assert kaynak_fare._bolge_kisitlimi(bolge)

    for bolge in kisitli_olmayan_bolgeler_1366:
        assert not kaynak_fare._bolge_kisitlimi(bolge)
