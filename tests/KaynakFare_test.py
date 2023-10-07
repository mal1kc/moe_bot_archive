from moe_bot.moe_gatherer import KaynakFare, Varsayilanlar
from moe_bot.temel_siniflar import Koordinat2D


def test_kisitli_bolgeler():
    for tiklama_kistilamasi in Varsayilanlar.TIKLAMA_KISITLAMALARI:
        for k, v in tiklama_kistilamasi.items():
            assert isinstance(v, int)
            assert v >= 0


def test_bolge_kisitlimi_1366():
    kisitli_olan_bolgeler_1366 = {Koordinat2D(170, 300)}
    kisitli_olmayan_bolgeler_1366 = [
        Koordinat2D(1000, 300),
        Koordinat2D(900, 300),
        Koordinat2D(905, 354),
        Koordinat2D(1040, 480),
        Koordinat2D(550, 170),
        Koordinat2D(410, 510),
    ]
    kaynak_fare = KaynakFare()
    kaynak_fare.tiklama_kisitlamalari = [
        {"x_taban": 0, "x_tavan": 400, "y_taban": 0, "y_tavan": 440},
        {"y_taban": 560},
        {"x_taban": 1270},
    ]
    for i in kaynak_fare.tiklama_kisitlamalari:
        for k, v in i.items():
            if k.startswith("sefer"):
                kaynak_fare.tiklama_kisitlamalari.remove(i)
                break

    for bolge in kisitli_olan_bolgeler_1366:
        assert kaynak_fare._bolge_kisitlimi(bolge)

    for bolge in kisitli_olmayan_bolgeler_1366:
        assert not kaynak_fare._bolge_kisitlimi(bolge)
