from functools import lru_cache

from moe_bot.ayarlar import Ayarlar


@lru_cache(maxsize=1)
def ayarları_olustur() -> Ayarlar.ModAyarlari:
    return Ayarlar.ModAyarlari(
        bosta_bekleme_suresi=0.1,
        bekleme_suresi=0.5,
        tarama_bekleme_suresi=1,
        okunucak_dosyalar="coordinates/regions.xlsx",
        tarayicilar={
            # t_adi : ( "gorsel_adi", "eminlik" , (x, y, genislik, yukseklik))
        },
        coklu_tarayicilar={
            "svy_demir": ("svy_demir", (0.9, 0.9, 0.9), None),
        },
        ekstra_ayarlar=None,
    )
