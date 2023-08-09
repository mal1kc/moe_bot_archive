from dataclasses import dataclass
import os
import sys

from moe_gatherer.temel_fonksiyonlar import sozlukeriBirlestir
from moe_gatherer.temel_siniflar import EkranBoyut, Kare, KaynakTipi, Koordinat2D

try:
    BASE_PATH = sys._MEIPASS  # type: ignore
except Exception:
    BASE_PATH = os.path.abspath(".")

UYUMA_SURESI = 2  # Saniye
GUNLUK_KLASORU = os.path.join(BASE_PATH, "loglar")
GUNLUK_SEVIYESI = "DEBUG"
ENGEL_KONTROL_SURESI = 3  # Saniye


@dataclass(frozen=True, order=True)
class TaramaSabitleri:
    """
    çalışma zamanı sabitleri
    """

    UYUMA_SURESI = 0.5

    DOSYA_YOLLARI = [
        "coordinates/regions.xlsx",
        os.path.join(BASE_PATH, "imgs/"),
    ]

    # *******************************************
    dil_tablos = {"en": {KaynakTipi.EKMEK.name: "food"}}
    # *******************************************

    kaynak_gorsel_yl_dsn = {
        KaynakTipi.EKMEK.name: "ek_*.png",
        KaynakTipi.ALTIN.name: "al_*.png",
        KaynakTipi.DEMIR.name: "de_*.png",
        KaynakTipi.GUMUS.name: "gu_*.png",
        KaynakTipi.TAS.name: "ta_*.png",
        KaynakTipi.ODUN.name: "od_*.png",
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

    GLOB_DSNLER = sozlukeriBirlestir(GLOB_DSNLER, kaynak_gorsel_yl_dsn, oyunui_gorsel_yl_dsn, svy_gorsel_yl_dsn, engel_gorsel_yl_dsn)

    del kaynak_gorsel_yl_dsn, oyunui_gorsel_yl_dsn, svy_gorsel_yl_dsn, engel_gorsel_yl_dsn

    # SVY_GORSEL_YL = [ 'svy_' + str(i) + '.png' for i in range(1, 12)]

    # SEFER_GORSEL_YL = [ 'sefer_' + str(i) + '.png' for i in range(0, 7)]

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
            "hizmet_basarisiz": Kare(1350, 960, 1200, 600),
            "oyundan_cik": Kare(1650, 410, 500, 200),
            "baglanti_kesildi": Kare(1500, 400, 800, 300),
            "dunya_ikonu": Kare(0, 2070, 240, 90),
            "maks_sefer": Kare(1650, 410, 500, 200),
            "tekrar_dene": Kare(1550, 1150, 1000, 600),
            "mavi_tamam": Kare(1550, 1150, 1000, 600),
            "geri_ok": Kare(0, 0, 200, 200),
            "tamam_buton": Kare(1550, 1150, 1000, 500),
        },
        "_1920": {
            "svy": Kare(925, 160, 235, 140),
            "isgal_durumu": Kare(820, 330, 270, 100),
            "sefer": Kare(170, 210, 120, 100),
            "sehir_ikonu": Kare(0, 920, 150, 260),
            "moe_logo": Kare(750, 0, 500, 200),
            "hizmet_basarisiz": Kare(670, 480, 600, 300),
            "oyundan_cik": Kare(820, 410, 250, 100),
            "baglanti_kesildi": Kare(750, 200, 400, 150),
            "dunya_ikonu": Kare(0, 1030, 120, 45),
            "maks_sefer": Kare(820, 200, 125, 50),
            "tekrar_dene": Kare(775, 570, 500, 300),
            "mavi_tamam": Kare(775, 570, 500, 300),
            "geri_ok": Kare(0, 0, 200, 200),
            "tamam_buton": Kare(775, 570, 500, 250),
        },
        "_1366": {
            "sehir_ikonu": Kare(0, 660, 100, 100),  # x,y ,genislik ,yukseklik
            "svy": Kare(640, 130, 180, 70),
            "isgal_durumu": Kare(575, 235, 200, 75),
            "sefer": Kare(110, 150, 100, 70),
        },
    }

    TIKLAMA_KISITLAMALARI = {
        "_3840": [
            {
                "x_taban": 0,
                "x_tavan": 1190,
                "y_taban": 0,
                "y_tavan": 1500,
            },
            {"y_taban": 1630},  # ölü bölge
            {"x_taban": 3580},  # ölü bölge
            {"y_tavan": 260},
        ],
        "_1920": [
            {
                "x_taban": 0,  # 290+
                "x_tavan": 600,  # 540-
                "y_taban": 0,  # 0+
                "y_tavan": 630,  # 550-
                # kombinleniyor x: 540-290 , y: 500-0
            },
            {"y_taban": 820},  # ölü bölge , 820+
            {"x_taban": 1750},  # ölü bölge  1750+
            {"y_tavan": 120},
        ],
        "_1366": [
            {
                "x_taban": 0,
                "x_tavan": 400,
                "y_taban": 0,
                "y_tavan": 440,
            },
            {"y_taban": 560},
            {"x_taban": 1270},
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
        },
        "_1920": {
            "bul_ikon": Koordinat2D(780, 50),
            "buyutec_ikon": Koordinat2D(1130, 180),
            "isgal_1": Koordinat2D(930, 770),
            "isgal_2": Koordinat2D(1330, 965),
            "isgal_duzeni": Koordinat2D(450, 140),
            "bul_y": Koordinat2D(1020, 175),
            "baglanti_yok": Koordinat2D(1050, 710),  # baglanti yok -tekrar dene- butonu # FIXME: koordinat ayarlanacak
            "sehir_ikonu": Koordinat2D(50, 1000),
        },
        "_1366": {
            "bul_ikon": Koordinat2D(560, 35),
            "buyutec_ikon": Koordinat2D(800, 120),
            "isgal_1": Koordinat2D(675, 550),
            "isgal_2": Koordinat2D(950, 690),
            "isgal_duzeni": Koordinat2D(370, 100),
            "bul_y": Koordinat2D(730, 125),
            "baglanti_yok": Koordinat2D(750, 490),
            "sehir_ikonu": Koordinat2D(30, 700),
        },
    }

    kaynak_eminlikler = {
        "_3840": {
            "FOOD": 0.8,
            "WOOD": 0.8,
            "STONE": 0.8,
            "IRON": 0.8,
            "SILVER": 0.8,
            "GOLD": 0.8,
        },
        "_1920": {
            # geçici değerler
            "WOOD": 0.7,
            "FOOD": 0.7,
            "STONE": 0.7,
            "IRON": 0.7,
            "SILVER": 0.7,
            "GOLD": 0.7,
        },
        "_1366": {
            # geçici değerler
            "WOOD": 0.7,
            "FOOD": 0.7,
            "STONE": 0.7,
            "IRON": 0.7,
            "SILVER": 0.7,
            "GOLD": 0.7,
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
        },
        "_1366": {
            "moe_logo": 0.8,
            "baglanti_yok": 0.8,
            "oyundan_cik": 0.8,
            "baglanti_kesildi": 0.8,
            "dunya_ikonu": 0.8,
            "devam_et_buton": 0.8,
            "tamam_buton": 0.8,
        },
    }

    EMINLIKLER = {
        # geçici değerler
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
