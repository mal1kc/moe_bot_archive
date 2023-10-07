from pprint import pprint

from moe_bot.moe_gatherer import KaynakTarayici, SvyTarayici, SeferTarayici, taramaBolgesiGetir
from moe_bot.temel_siniflar import KaynakTipi

if __name__ == "__main__":
    # sleep(2)
    kaynak_tarama_eminlik = 0.7
    kaynak_tarama = False
    svy_tarama = False
    svy_tarama_eminlik = 0.8
    sefer_tarama = True
    sefer_tarama_eminlik = 0.9
    max_sefer_sayisii = 3

    tip = KaynakTipi.DEMIR
    svy_tarama_bolgesi = taramaBolgesiGetir("svy")
    sefer_tarama_bolgesi = taramaBolgesiGetir("sefer")

    if kaynak_tarama:
        tarayici = KaynakTarayici(tip)
        # tarayici.ornek_dler = [
        #     'imgs/_3840/food_1_3840.png',
        #     'imgs/_3840/food_2_3840.png',
        #     'imgs/_3840/food_3_3840.png'
        # ]
        bulunan_kareler = tarayici.ekranTara(kaynak_tarama_eminlik, liste_don=True)
        print(bulunan_kareler)
    if svy_tarama:
        tarayici = SvyTarayici(eminlik=svy_tarama_eminlik, kaynak_tipi=tip, bolge=svy_tarama_bolgesi)
        bulunan_kareler = tarayici.ekranTara()
        pprint(bulunan_kareler)
    if sefer_tarama:
        tarayici = SeferTarayici(eminlik=sefer_tarama_eminlik, maks_sefer_sayisi=max_sefer_sayisii, bolge=sefer_tarama_bolgesi)
        bulunan_kareler = tarayici._ekranTara()
        pprint(bulunan_kareler)
