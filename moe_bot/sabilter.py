from dataclasses import dataclass
import os
import sys
import logging

from moe_bot.temel_fonksiyonlar import sozlukeriBirlestir
from moe_bot.temel_siniflar import EkranBoyut, Kare, KaynakTipi, Koordinat2D

try:
    BASE_PATH = sys._MEIPASS  # type: ignore
except Exception:
    BASE_PATH = os.path.abspath(".")

UYUMA_SURESI = 0.5  # Saniye
GUNLUK_KLASORU = os.path.join(BASE_PATH, "loglar")
GUNLUK_SEVIYESI = logging.DEBUG
ENGEL_KONTROL_SURESI = 1  # Saniye
MESAJ_GECIKMESI = ENGEL_KONTROL_SURESI + 0.2  # Saniye

CRED_PATH = os.path.join(BASE_PATH, "credentials.txt")

GUI_LOGO_PATH = os.path.join(BASE_PATH, "arayuz\\moe_logo.png")
# GUI_ICON_PATH = os.path.join(BASE_PATH, "arayuz\\moe_icon.ico")
GUI_ICON_PATH = GUI_LOGO_PATH


GUI_ENTRY_WIDTH = 30


@dataclass(frozen=True, order=True)
class TaramaSabitleri:
    """
    çalışma zamanı sabitleri
    """

    DOSYA_YOLLARI = [
        "coordinates/regions.xlsx",
        os.path.join(BASE_PATH, "imgs/"),
    ]

    # *******************************************
    dil_tablos = {"en": {KaynakTipi.EKMEK.name: "food"}}
    # *******************************************

    kaynak_gorsel_yl_dsn = {
        KaynakTipi.EKMEK.name: "ek_*.png",
        KaynakTipi.ODUN.name: "od_*.png",
        KaynakTipi.TAS.name: "ta_*.png",
        KaynakTipi.DEMIR.name: "de_*.png",
        KaynakTipi.GUMUS.name: "gu_*.png",
        KaynakTipi.ALTIN.name: "al_*.png",
    }

    engel_gorsel_yl_dsn = {
        "sehir_ikonu": "sehir_ikonu*.png",
        "moe_logo": "moe_logo*.png",
        "hizmet_basarisiz": "hizmet_basarisiz*.png",
        "oyundan_cik": "oyundan_cik*.png",
        "baglanti_kesildi": "baglanti_kesildi*.png",
        "dunya_ikonu": "dunya_ikonu*.png",
        "maks_sefer": "maks_sefer*.png",
        "tekrar_dene": "tekrar_dene*.png",
        "mavi_tamam": "mavi_tamam*.png",
        "geri_ok": "geri_ok*.png",
        "tamam_buton": "tamam_buton*.png",
        "geri_buton": "geri_buton.png",
        "baglanti_yok": "baglanti_yok.png",
        # "kalkan": "kalkan.png",
        # "devre_disi": "devre_disi.png",
        # "devam_buton": "devam_buton.png",
    }

    oyunui_gorsel_yl_dsn = {
        "isgal_durumu": "isgal_durumu*.png",
        "sehir_ikonu": "sehir_ikonu*.png",
    }

    GLOB_DSNLER = {
        "engel": "engel_*.png",
        "svy": "svy_*.png",
        "sefer": "sefer_*.png",
    }

    svy_gorsel_yl_dsn = {ktip.name + "_svy": ktip.name.lower() + "_svy_*.png" for ktip in KaynakTipi}

    # örn { 'EKMEK_svy': 'e_svy_*.png', 'ALTIN_svy': 'a_svy_*.png', ...}

    GLOB_DSNLER = sozlukeriBirlestir(
        GLOB_DSNLER,
        kaynak_gorsel_yl_dsn,
        oyunui_gorsel_yl_dsn,
        svy_gorsel_yl_dsn,
        engel_gorsel_yl_dsn,
    )

    del (
        kaynak_gorsel_yl_dsn,
        oyunui_gorsel_yl_dsn,
        svy_gorsel_yl_dsn,
        engel_gorsel_yl_dsn,
    )

    # eğer oyun dili görsel diline etki ediyorsa True
    # etki etmiyorsa False

    # böylece çalışma sırasında etki etmeyenleri imgs/no_lang/{çöz}/{img_desen} yolundan alır
    # etki edenleri ise imgs/{dil}/{çöz}/{img_desen} yolundan alır
    # eğer dict içinde bulunmuyorsa False kabul edilir

    GORSEL_YL_DIL_BEYANLARI = {
        "ODUN": False,
        "TAS": False,
        "EKMEK": False,
        "ALTIN": False,
        "DEMIR": False,
        "GUMUS": False,
    }

    EKRAN_BOYUTLARI = {
        "_1366": EkranBoyut(1366, 768),
        "_1920": EkranBoyut(1920, 1080),
        "_3840": EkranBoyut(3840, 2160),
    }

    TARAMA_BOLGELERI = {
        "_3840": {
            "svy": Kare(1600, 400, 700, 200),
            "isgal_durumu": Kare(1580, 680, 1580 + 620, 190),
            "sefer": Kare(400, 500, 100, 90),
            "sehir_ikonu": Kare(0, 2070, 240, 90),
            "moe_logo": Kare(1500, 0, 1000, 400),
            "hizmet_basarisiz": Kare(1750, 500, 300, 300),
            "oyundan_cik": Kare(1650, 410, 500, 200),
            "baglanti_kesildi": Kare(1500, 400, 800, 300),
            "dunya_ikonu": Kare(0, 2070, 240, 90),
            "maks_sefer": Kare(1650, 410, 500, 200),
            "tekrar_dene": Kare(1550, 1150, 1000, 600),
            "mavi_tamam": Kare(1550, 1220, 1000, 600),
            "geri_ok": Kare(0, 0, 200, 200),
            "tamam_buton": Kare(1550, 1150, 1000, 500),
            "geri_buton": Kare(930, 1880, 500, 300),
            "baglanti_yok": Kare(1900, 500, 200, 200),
            # "kalkan": Kare(3650, 720, 160, 110),
            # "devre_disi": Kare(1780, 480, 250, 100),
            # "devam_buton": Kare(430, 1600, 700, 500),
        },
        "_1920": {
            "svy": Kare(925, 160, 235, 140),
            "isgal_durumu": Kare(820, 330, 270, 100),
            "sefer": Kare(170, 210, 120, 100),
            "sehir_ikonu": Kare(0, 950, 150, 130),
            "moe_logo": Kare(860, 0, 300, 200),
            "hizmet_basarisiz": Kare(740, 230, 470, 220),
            "oyundan_cik": Kare(820, 230, 250, 100),
            "baglanti_kesildi": Kare(740, 230, 470, 220),
            "dunya_ikonu": Kare(0, 950, 120, 130),
            "maks_sefer": Kare(820, 200, 125, 50),
            "tekrar_dene": Kare(960, 650, 200, 100),
            "mavi_tamam": Kare(730, 550, 500, 500),
            "geri_ok": Kare(0, 0, 200, 200),
            "tamam_buton": Kare(825, 450, 500, 250),
            "geri_buton": Kare(490, 950, 200, 200),
            "baglanti_yok": Kare(740, 230, 470, 220),
            # "kalkan": Kare(3650, 720, 160, 110), #değişecek
            # "devre_disi": Kare(1780, 480, 250, 100), #değişecek
            # "devam_buton": Kare(200, 850, 550, 1030),
        },
        "_1366": {
            "svy": Kare(640, 130, 180, 70),
            "isgal_durumu": Kare(575, 235, 200, 75),
            "sefer": Kare(110, 150, 100, 70),
            "sehir_ikonu": Kare(0, 730, 100, 38),  #
            "moe_logo": Kare(400, 0, 300, 200),  #
            "hizmet_basarisiz": Kare(480, 140, 410, 110),  #
            "oyundan_cik": Kare(480, 140, 410, 110),  #
            "baglanti_kesildi": Kare(480, 140, 410, 110),  #
            "dunya_ikonu": Kare(0, 730, 100, 38),  #
            "maks_sefer": Kare(480, 140, 400, 100),  #
            "tekrar_dene": Kare(680, 450, 140, 80),  #
            "mavi_tamam": Kare(530, 400, 300, 300),  #
            "geri_ok": Kare(0, 0, 50, 60),  #
            "tamam_buton": Kare(610, 450, 140, 100),  #
            "geri_buton": Kare(300, 650, 200, 100),  #
            "baglanti_yok": Kare(480, 140, 410, 110),  #
        },
    }

    TIKLAMA_KISITLAMALARI = {
        "_3840": [
            {
                "x_taban": 0,
                "x_tavan": 280,
                "y_taban": 0,
                "y_tavan": 1150,
            },
            {"y_taban": 1630},  # ölü bölge
            {"x_taban": 3580},  # ölü bölge
            {"y_tavan": 280},
        ],
        "_1920": [
            {
                "x_taban": 0,  # 290+
                "x_tavan": 135,  # 540-
                "y_taban": 0,  # 0+
                "y_tavan": 550,  # 550-
                # kombinleniyor x: 540-290 , y: 500-0
            },
            {"y_taban": 820},  # ölü bölge , 820+
            {"x_taban": 1750},  # ölü bölge  1750+
            {"y_tavan": 140},
        ],
        "_1366": [
            {
                "x_taban": 0,
                "x_tavan": 100,
                "y_taban": 0,
                "y_tavan": 400,
            },
            {"y_taban": 580},
            {"x_taban": 1270},
            {"y_tavan": 100},
        ],
    }

    TIKLAMA_NOKTALARI = {
        "_3840": {
            "bul_ikon": Koordinat2D(1580, 80),
            "buyutec_ikon": Koordinat2D(2260, 340),
            "isgal_1": Koordinat2D(1900, 1580),
            "isgal_2": Koordinat2D(2670, 1950),
            "isgal_duzeni": Koordinat2D(1100, 270),
            "bul_y": Koordinat2D(2030, 340),
            "cikis_hayir": Koordinat2D(2110, 1370),
            # "mavi_tamam": Koordinat2D(1900, 1540),
            # "kalkan": Koordinat2D(3700, 780),
            # "kalkan2": Koordinat2D(500, 540),
            # "kullan": Koordinat2D(2050, 1220),
            # "kalkan_al_Evet": Koordinat2D(1660, 1370),
        },
        "_1920": {
            "bul_ikon": Koordinat2D(780, 50),
            "buyutec_ikon": Koordinat2D(1130, 180),
            "isgal_1": Koordinat2D(930, 770),
            "isgal_2": Koordinat2D(1330, 965),
            "isgal_duzeni": Koordinat2D(450, 140),
            "bul_y": Koordinat2D(1020, 175),
            "cikis_hayir": Koordinat2D(1060, 690),
        },
        "_1366": {
            "bul_ikon": Koordinat2D(560, 35),
            "buyutec_ikon": Koordinat2D(800, 120),
            "isgal_1": Koordinat2D(675, 550),
            "isgal_2": Koordinat2D(950, 690),
            "isgal_duzeni": Koordinat2D(370, 100),
            "bul_y": Koordinat2D(730, 125),
            "cikis_hayir": Koordinat2D(750, 485),  #
        },
    }

    kaynak_eminlikler = {
        "_3840": {
            "EKMEK": 0.8,
            "ODUN": 0.8,
            "TAS": 0.8,
            "DEMIR": 0.8,
            "GUMUS": 0.8,
            "ALTIN": 0.8,
        },
        "_1920": {
            "EKMEK": 0.7,
            "ODUN": 0.7,
            "TAS": 0.7,
            "DEMIR": 0.7,
            "GUMUS": 0.7,
            "ALTIN": 0.7,
        },
        "_1366": {
            "EKMEK": 0.7,
            "ODUN": 0.7,
            "TAS": 0.7,
            "DEMIR": 0.7,
            "GUMUS": 0.7,
            "ALTIN": 0.7,
        },
    }

    oyunui_eminlikler = {
        "_3840": {
            "engel_1": 0.8,
            "engel_2": 0.8,
            "isgal_durumu": 0.8,
            "sehir_ikonu": 0.8,
        },
        "_1920": {
            # geçici değerler
            "engel_1": 0.8,
            "engel_2": 0.8,
            "isgal_durumu": 0.8,
            "sehir_ikonu": 0.8,
        },
        "_1366": {
            # geçici değerler
            "engel_1": 0.8,
            "engel_2": 0.8,
            "isgal_durumu": 0.8,
            "sehir_ikonu": 0.8,
        },
    }

    engel_eminlikler = {
        "_3840": {
            "sehir_ikonu": 0.8,
            "moe_logo": 0.8,
            "hizmet_basarisiz": 0.8,
            "oyundan_cik": 0.8,
            "baglanti_kesildi": 0.8,
            "dunya_ikonu": 0.8,
            "maks_sefer": 0.8,
            "tekrar_dene": 0.8,
            "mavi_tamam": 0.8,
            "geri_ok": 0.8,
            "tamam_buton": 0.8,
            "geri_buton": 0.8,
            "baglanti_yok": 0.8,
            # "kalkan": 0.8,
            # "devre_disi": 0.8,
            # "devam_buton": 0.8,
        },
        "_1920": {
            "sehir_ikonu": 0.8,
            "moe_logo": 0.8,
            "hizmet_basarisiz": 0.8,
            "oyundan_cik": 0.8,
            "baglanti_kesildi": 0.8,
            "dunya_ikonu": 0.8,
            "maks_sefer": 0.8,
            "tekrar_dene": 0.8,
            "mavi_tamam": 0.8,
            "geri_ok": 0.8,
            "tamam_buton": 0.8,
            "geri_buton": 0.8,
            "baglanti_yok": 0.8,
        },
        "_1366": {
            "sehir_ikonu": 0.8,
            "moe_logo": 0.8,
            "hizmet_basarisiz": 0.8,
            "oyundan_cik": 0.8,
            "baglanti_kesildi": 0.8,
            "dunya_ikonu": 0.8,
            "maks_sefer": 0.8,
            "tekrar_dene": 0.8,
            "mavi_tamam": 0.8,
            "geri_ok": 0.8,
            "tamam_buton": 0.8,
            "geri_buton": 0.8,
            "baglanti_yok": 0.8,
        },
    }

    EMINLIKLER = {
        "_3840": {
            "svy": 0.9,
            "sefer": 0.9,
        },
        "_1920": {
            "svy": 0.8,
            "sefer": 0.9,
        },
        "_1366": {
            "svy": 0.8,
            "sefer": 0.9,
        },
    }

    EMINLIKLER = sozlukeriBirlestir(EMINLIKLER, kaynak_eminlikler, oyunui_eminlikler, engel_eminlikler)

    del kaynak_eminlikler, oyunui_eminlikler
