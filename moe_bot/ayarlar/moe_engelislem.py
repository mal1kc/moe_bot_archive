from functools import lru_cache

from moe_bot.ayarlar import Ayarlar
from moe_bot.enumlar import EkranBoyutEnum


@lru_cache(maxsize=1)
def ayarları_olustur(ekran_cozunurluk: EkranBoyutEnum | None = None) -> Ayarlar.ModAyarlari:
    # TODO tarayicilari ve ekranboyutdan bağımsız ayarları burda oluştur
    if ekran_cozunurluk == EkranBoyutEnum._3840:
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
    elif ekran_cozunurluk == EkranBoyutEnum._1920:
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
    elif ekran_cozunurluk == EkranBoyutEnum._1366:
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
    else:
        raise Exception("bu çözünürlük için ayar mevcut değil")


# tüm ayarlar

# Ayarlar.ModAyarlari(
#             bosta_bekleme_suresi=0.1,
#             bekleme_suresi=0.5,
#             tarama_bekleme_suresi=1,
#             tarayicilar={
#         TODO: buraya tarayicilari ekle
#                 # t_adi : ( "gorsel_adi", "eminlik" , (x, y, genislik, yukseklik))
#                 "sehir_ikonu": ("sehir_ikonu", 0.9, None),
#             },
#             okunucak_dosyalar=None,
#             coklu_tarayicilar=None,
#             ekstra_ayarlar=None,
#         )
