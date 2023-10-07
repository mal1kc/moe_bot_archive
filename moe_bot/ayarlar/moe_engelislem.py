from functools import lru_cache
from moe_bot.ayarlar import Ayarlar


@lru_cache(maxsize=1)
def ayarları_olustur() -> Ayarlar.ModAyarlari:
    return Ayarlar.ModAyarlari(
        bosta_bekleme_suresi=0.1,
        bekleme_suresi=0.5,
        tarama_bekleme_suresi=1,
        tarayicilar={
            # t_adi : ( "gorsel_adi", "eminlik" , (x, y, genislik, yukseklik))
            "sehir_ikonu": ("sehir_ikonu", 0.9, None),
        },
        okunucak_dosyalar=None,
        coklu_tarayicilar=None,
        ekstra_ayarlar=None,
    )
