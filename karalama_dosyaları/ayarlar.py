from __future__ import annotations
from collections import namedtuple
from enum import Enum, auto
from typing import NamedTuple
import cv2
import numpy
import pyautogui

Koordinat2D = namedtuple("Koordinat2D", ["x", "y"], defaults=[0, 0])


class OnSvyEnum(Enum):
    BIR = 1
    IKI = 2
    UC = 3
    BES = 5
    ALTI = 6
    YEDI = 7
    SEKIZ = 8
    DOKUZ = 9
    ON = 10
    ONBIR = 11
    ONIKI = 12


# class SeferSayisiEnum(Enum):
#     SIFIR = 0
#     BIR = 1
#     IKI = 2
#     UC = 3
#     DORT = 4
#     BES = 5
#     ALTI = 6
#     YEDI = 7


class MevsimTipiEnum(Enum):
    YAZ = auto()
    SONBAHAR = auto()
    KIS = auto()
    BAHAR = auto()


class KampTipiEnum(Enum):
    KABAK = auto()
    KUPA = auto()
    ...


class Kare(NamedTuple):
    x: int = 0
    y: int = 0
    genislik: int = 0
    yukseklik: int = 0

    def gecersizMi(self) -> bool:
        if not any([isinstance(i, int) for i in self]):
            return True
        return self.genislik == 0 or self.yukseklik == 0


def ekran_goruntusu_al(grayscale: bool = True) -> cv2.typing.MatLike:
    screenshot = pyautogui.screenshot()
    screenshot = numpy.array(screenshot)
    if grayscale:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        return screenshot
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot


KampTaramaAyarlar = {
    "onsvy_ad": "kamp_onsvy{onsvy_val}_*",
    # "svy": "svy_*.png",
    "sefer_sayisi_resim": "sefer_{sefer_sayisi}_*.png",
    # sefer_0_*.png , sefer_0_1.png , sefer_0_6.png  -> 0
    # sefer_4_*.png , sefer_4_9.png , sefer_4_3.png  -> 4
    "sefer_boncuk_sayisi_resim": "sefer_boncuk_{sefer_boncuk_sayisi}.png",
    # "onsvy_cascade": "kamp_onsvy{onsvy_val}.xml", # -> kamp_onsvy5.xml
    "kamp_tip_cascade": "kamp_tip.xml",
    "mevsim": "mvsm_{mvsm_nm}*.png",  # -> mvsm_yaz*.png
}


KampSaldiriAyarlar = {
    "musama_aktif_resim": "musama_aktif.png",
    "musama_liste_resim": "musama_liste.png",
    "cikiskamp_resim": "cikis_kamp.png",
    "enerji_resim": "enerji_kontrol.png",
    "hizli_saldir_resim": "hizli_saldiri.png",
    "satin_al_resim": "satin_al.png",
    "kullan_buton_resim": "kullan.png",
    "saldir_buton_resim": "saldir_buton.png",
    "enerji_kontrol_resim": True,
    "yardimci_resim": "yardimci.png",
    "sekme_resim": "sekme.png",
    "rastgele_resim": "rastgele.png",
    "tamam_buton_resim": "tamam_buton.png",
    "isinlanma_resim": "isinlanma.png",
    "kalemi_goster_resim": "kalemi_goster.png",
    "cikis_bina_resim": "cikis_bina.png",
}


SabitTiklama = {
    "sol_nokta": Koordinat2D(1000, 1500),
    "sol_nokta2": Koordinat2D(1010, 1500),
    "sag_nokta": Koordinat2D(3500, 1500),
    "sag_nokta2": Koordinat2D(3490, 1500),
    "ust_nokta": Koordinat2D(1900, 400),
    "ust_nokta2": Koordinat2D(1900, 390),
    "alt_nokta": Koordinat2D(1900, 1500),
    "alt_nokta2": Koordinat2D(1900, 1490),
    "alt_bitis": Koordinat2D(1900, 300),
    "alt_bitis2": Koordinat2D(1900, 310),
    "ust_bitis": Koordinat2D(1900, 1800),
    "ust_bitis2": Koordinat2D(1900, 1790),
    "hizli_saldiri": Koordinat2D(2430, 1850),
    "saldir_sayac": Koordinat2D(2100, 1800),
    "inaktif_bolge1": Koordinat2D(650, 120),
    "inaktif_bolge2": Koordinat2D(2750, 120),
}


TumEminlikler = {
    "onsvy_eminlik": 0.8,
    "kamp_tip_eminlik": 0.9,
    "svy_eminlik": 0.9,
    "mevsim_eminlik": 0.9,
    "enerji_eminlik": 0.9,
    "musama_aktif_eminlik": 0.9,
    "musama_liste_eminlik": 0.9,
    "hizli_saldiri_eminlik": 0.9,
    "saldir_buton_eminlik": 0.9,
    "kullan_buton_eminlik": 0.9,
    "satin_al_eminlik": 0.9,
    "cikiskamp_eminlik": 0.9,
    "sefer_eminlik": 0.9,
    "yardimci_eminlik": 0.9,
    "sekme_eminlik": 0.9,
    "rastgele_eminlik": 0.9,
    "soguma_eminlik": 0.9,
    "tamam_buton_eminlik": 0.9,
    "isinlanma_eminlik": 0.9,
    "kalemi_goster_eminlik": 0.9,
    "pop_up_eminlik": 0.9,
    "cikis_bina_eminlik": 0.9,
}

TumTaramaBolgeleri: dict[str, Kare | tuple[int, int, int, int]] = {
    #  "kamp_tip": (-75, -100, 200, 300),  # önseviye+tarama olarak yazılacak
    # örn kullanımı
    #
    # onseviye_kare = locateonScreen ...
    # kamp_tip_kare = locateOnScree(.... , region =( onseviye_kare[0] + TumTaramaBolgeleri \
    #  ['kamp_tip'][0] , onseviye_kare[0] + TumTaramaBolgeleri['kamp_tip'][1])  ,...)
    #
    "mevsim_bolge": Kare(270, 300, 3300, 1300),
    "seviye_bolge": Kare(1650, 130, 500, 150),
    "musama_aktif_bolge": Kare(1360, 350, 300, 200),
    "musama_liste_bolge": Kare(1240, 450, 200, 700),
    "saldir_buton_bolge": Kare(1900, 1700, 500, 300),
    "enerji_bolge": Kare(1430, 750, 100, 110),
    "musama_kullan_bolge": Kare(1800, 700, 500, 700),
    # "satin_al_bolge": Kare(111, 111, 111, 111),
    "cikiskamp_bolge": Kare(2450, 100, 130, 110),
    "sefer_bolge": Kare(400, 500, 100, 90),
    "sefer_boncuk_bolge": Kare(130, 715, 100, 110),
    "yardimci_bolge": Kare(2750, 400, 500, 150),
    "sekme_bolge": Kare(1850, 570, 200, 150),
    "rastgele_bolge": Kare(1200, 650, 800, 1400),
    "rastgele_isin_kullan_bolge": Kare(),
    "tamam_buton_bolge": Kare(1750, 1300, 400, 150),
    "isinlanma_bolge": Kare(1650, 1200, 500, 250),
    "kalemi_goster_bolge": Kare(1600, 1650, 150, 120),
    "pop_up_cikis_bolge": Kare(2400, 400, 200, 150),
    "kamp_tip_tarama_bolge": Kare(250, 250, 3330, 1450),
    "hizli_saldir_bolge": Kare(2300, 1750, 250, 200),
    "cikis_bina_bolge": Kare(2380, 340, 200, 400),
}


EngelKontrolu = {
    "sehir_ikonu_resim": "sehir_ikonu.png",
    "moe_logo_resim": "moe_logo.png",
    "hizmet_basarisiz_resim": "hizmet_basarisiz.png",
    "baglanti_kesildi_resim": "baglanti_kesildi.png",
    "dunya_ikonu_resim": "dunya_ikonu.png",
    "maks_sefer_resim": "maks_sefer.png",
    "tekrar_dene_resim": "tekrar_dene.png",
    "mavi_tamam_resim": "mavi_tamam.png",
    "geri_ok_resim": "geri_ok.png",
    "oyundan_cik_resim": "oyundan_cik.png",
    "geri_buton_resim": "geri_buton.png",
    "baglanti_yok_resim": "baglanti_yok.png",
    "devam_buton_resim": "devam_buton.png",
    "soguma_resim": "soguma.png",
    "kalkan_al_resim": "kalkan.png",
    "yarali_var_resim": "yarali_var.png",
    "iyilestir_buton_resim": "iyilestir_buton.png",
    "tumunu_sec_buton_resim": "tumunu_sec_buton.png",
    "secimi_kaldir_buton_resim": "secimi_kaldir_buton.png",
    "simdi_iyilestir_resim": "simdi_iyilestir.png",
    "aninda_iyilestir_resim": "aninda_iyilestir.png",
    "evet_buton_resim": "evet_buton.png",
}

EngelEminlik = {
    "sehir_ikonu_eminlik": 0.9,
    "moe_logo_eminlik": 0.9,
    "hizmet_basarisiz_eminlik": 0.9,
    "baglanti_kesildi_eminlik": 0.9,
    "dunya_ikonu_eminlik": 0.9,
    "maks_sefer_eminlik": 0.9,
    "tekrar_dene_eminlik": 0.9,
    "mavi_tamam_eminlik": 0.9,
    "geri_ok_eminlik": 0.9,
    "tamam_buton_eminlik": 0.9,
    "oyundan_cik_eminlik": 0.9,
    "geri_buton_eminlik": 0.9,
    "baglanti_yok_eminlik": 0.9,
    "devam_buton_eminlik": 0.9,
    "pop_up_eminlik": TumEminlikler["pop_up_eminlik"],
    "kalkan_al_eminlik": 0.9,
    "yarali_var_eminlik": 0.9,
    "iyilestir_buton_eminlik": 0.9,
    "tumunu_sec_buton_eminlik": 0.9,
    "secimi_kaldir_buton_eminlik": 0.9,
    "simdi_iyilestir_eminlik": 0.9,
    "aninda_iyilestir_eminlik": 0.9,
    "evet_buton_eminlik": 0.9,
}


EngelTaramaBolgeleri = {
    "sehir_ikonu_bolge": Kare(0, 2070, 240, 90),
    "moe_logo_bolge": Kare(1500, 0, 1000, 400),
    "hizmet_basarisiz_bolge": Kare(1750, 500, 300, 300),
    "oyundan_cik_bolge": Kare(1650, 410, 500, 200),
    "baglanti_kesildi_bolge": Kare(1500, 400, 800, 300),
    "dunya_ikonu_bolge": Kare(0, 2070, 240, 90),
    "maks_sefer_bolge": Kare(1650, 410, 500, 200),
    "tekrar_dene_bolge": Kare(1550, 1150, 1000, 600),
    "mavi_tamam_bolge": Kare(1550, 1220, 1000, 600),
    "geri_ok_bolge": Kare(0, 0, 200, 200),
    "tamam_buton_bolge": Kare(1550, 1150, 1000, 500),
    "geri_buton_bolge": Kare(930, 1880, 500, 300),
    "baglanti_yok_bolge": Kare(1900, 500, 200, 200),
    "devam_buton_bolge": Kare(430, 1600, 700, 500),
    "pop_up_bolge": Kare(1700, 450, 500, 200),
    "kalkan_al_bolge": Kare(3400, 700, 200, 170),
    "yarali_var_bolge": Kare(0, 550, 200, 150),
    "iyilestir_buton_bolge": Kare(650, 580, 300, 140),
    "tumunu_sec_buton_bolge": Kare(1250, 1500, 400, 200),
    "secimi_kaldir_buton_bolge": Kare(1250, 1500, 400, 200),
    "simdi_iyilestir_bolge": Kare(1700, 1480, 400, 200),
    "aninda_iyilestir_bolge": Kare(1600, 460, 300, 140),
    "evet_buton_bolge": Kare(1500, 1250, 350, 200),
}

TIKLAMA_KISITLAMALARI = (
    {
        "x_taban": 0,
        "x_tavan": 280,
        "y_taban": 0,
        "y_tavan": 1150,
    },
    {"y_taban": 1630},  # ölü bölge
    {"x_taban": 3580},  # ölü bölge
    {"y_tavan": 280},
)
