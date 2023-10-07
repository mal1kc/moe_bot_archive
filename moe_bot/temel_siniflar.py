import logging
import time
from pyautogui import size as screen_size
from collections import namedtuple
from enum import Enum, auto

# -- typing
import pathlib
from typing import Optional, Self, Protocol, NamedTuple
from multiprocessing.synchronize import Event

# -- end typing

import multiprocessing
import functools

import pyautogui

from moe_bot.ayarlar import genel_ayarlar

from .enumlar import EkranBoyutEnum, DilEnum, ModSinyal  # noqa
from .hatalar import Hata, KullaniciHatasi


Koordinat2D = namedtuple("Koordinat2D", ["x", "y"], defaults=[0, 0])

_GUNLUKCU = logging.getLogger("moe_bot.genel")


# TODO: move this to moe_gatherer.py
class KaynakTipi(Enum):
    EKMEK = auto()
    ODUN = auto()
    TAS = auto()
    DEMIR = auto()
    GUMUS = auto()
    ALTIN = auto()


class KullaniciGirisVerisi(NamedTuple):
    name: str
    password_hash: str

    def toTuple(self):
        return (self.name, self.password_hash)


class Kare(NamedTuple):
    x: int = 0
    y: int = 0
    genislik: int = 0
    yukseklik: int = 0

    def gecersizMi(self) -> bool:
        if not any([isinstance(i, int) for i in self]):
            return True
        return self.genislik == 0 or self.yukseklik == 0


class EkranBoyut(NamedTuple):
    genislik: int
    yukseklik: int

    def __eq__(self, __value: object) -> bool:
        _GUNLUKCU.debug(f"EkranBoyut.__eq__({self}, {__value})")
        if not isinstance(__value, EkranBoyut):
            raise Hata(f"hatalı karşılaştırma EkranBoyut.__eq__({self}, {__value})")
        return f"{self.genislik}x{self.yukseklik}" == f"{__value.genislik}x{__value.yukseklik}"

    def __str__(self) -> str:
        return f"{self.genislik}x{self.yukseklik}"


class KaynakKare(Kare):
    def __new__(
        cls,
        x: int | Kare,
        y: Optional[int] = None,
        genislik: Optional[int] = None,
        yukseklik: Optional[int] = None,
    ):
        _GUNLUKCU.debug("kaynak kare oluşturuluyor.")
        if isinstance(x, Kare):
            return super().__new__(cls, x.x, x.y, x.genislik, x.yukseklik)
        return super().__new__(cls, x, y, genislik, yukseklik)

    def __init__(
        self,
        x: int | Kare,
        y: Optional[int] = None,
        genislik: Optional[int] = None,
        yukseklik: Optional[int] = None,
    ) -> None:
        self.gecici_auto_kareler = None
        if all([y is None, genislik is None, yukseklik is None]):
            Hata("Kare oluşturulamadı.")

        if isinstance(x, Kare):
            self.koordinat = x
        else:
            self.koordinat = Kare(x, y, genislik, yukseklik)  # type: ignore

        if Kare.gecersizMi(self.koordinat):  # type: ignore
            raise Hata(f"Geçersiz kare: {self.koordinat}")

        _GUNLUKCU.debug(f"KaynakKare oluşturuldu: {self},{id(self)}")

    def __str__(self) -> str:
        return f"KaynakKare({self.koordinat.x},{self.koordinat.y},{self.koordinat.genislik},{self.koordinat.yukseklik})"

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return hash(str(self.koordinat))

    def disindaMi(self, dkare: Kare, buyutme_miktari: int = 30) -> bool:
        buyutulmus_kare = self.buyutulmusKare(buyutme_miktari)
        _GUNLUKCU.debug(f"buyutulmus_kare: {buyutulmus_kare} , dkare: {dkare}")

        _GUNLUKCU.debug(
            str(
                (
                    buyutulmus_kare.x > dkare.x + dkare.genislik,
                    buyutulmus_kare.y > dkare.y + dkare.yukseklik,
                    buyutulmus_kare.x + buyutulmus_kare.genislik < dkare.x,
                    buyutulmus_kare.y + buyutulmus_kare.yukseklik < dkare.y,
                )
            )
        )
        return (
            buyutulmus_kare.x > dkare.x + dkare.genislik
            or buyutulmus_kare.y > dkare.y + dkare.yukseklik
            or buyutulmus_kare.x + buyutulmus_kare.genislik < dkare.x
            or (buyutulmus_kare.y + buyutulmus_kare.yukseklik < dkare.y)
        )

    def buyutulmusKare(self, buyutme_miktari: int = 100) -> Kare:
        return Kare(
            self.koordinat.x - buyutme_miktari,
            self.koordinat.y - buyutme_miktari,
            self.koordinat.genislik + buyutme_miktari,
            self.koordinat.yukseklik + buyutme_miktari,
        )

    def merkez(self):
        return Koordinat2D(
            self.koordinat.x + self.koordinat.genislik / 2,
            self.koordinat.y + self.koordinat.yukseklik / 2,
        )


class GenelAyarlar:
    __slots__ = ()
    UYUMA_SURESI: float = genel_ayarlar.UYUMA_SURESI
    DOSYA_YOLLARI: tuple[str, str] = genel_ayarlar.DOSYA_YOLLARI  # type: ignore
    EKRAN_BOYUTU: EkranBoyut | None = None
    FARE_UYUMA_SURESI: float = genel_ayarlar.UYUMA_SURESI / 2
    KLAVYE_UYUMA_SURESI: float = genel_ayarlar.UYUMA_SURESI / 1.5

    def __init__(self) -> None:
        "this class works without instance"
        raise NotImplementedError

    @staticmethod
    def ayarla(
        uyuma_suresileri=(genel_ayarlar.UYUMA_SURESI, genel_ayarlar.UYUMA_SURESI / 2, genel_ayarlar.UYUMA_SURESI / 1.5),
        dosya_yollari=genel_ayarlar.DOSYA_YOLLARI,
        ekran_boyutu=None,
    ):
        uyuma_suresi, fare_uyuma_suresi, klavye_uyuma_suresi = uyuma_suresileri

        GenelAyarlar.UYUMA_SURESI = uyuma_suresi if uyuma_suresi is not None else genel_ayarlar.UYUMA_SURESI

        GenelAyarlar.FARE_UYUMA_SURESI = fare_uyuma_suresi if fare_uyuma_suresi is not None else uyuma_suresi / 2

        GenelAyarlar.KLAVYE_UYUMA_SURESI = klavye_uyuma_suresi if klavye_uyuma_suresi is not None else uyuma_suresi / 1.5

        GenelAyarlar.DOSYA_YOLLARI = dosya_yollari

        GenelAyarlar.EKRAN_BOYUTU = ekran_boyutu if ekran_boyutu is not None else aktif_ekran_boyutu_getir()

    @staticmethod
    def gorsel_dosya_yolu(gorsel_yolu_oneki: str) -> str:
        '-> ex: "imgs/{lang}/{resolution}/{file_name}.png"'
        d_yolu_format = "{base_img_dir}/{lang}/{resolution}/{file_name}.png"
        gorsel_klasor_yolu = GenelAyarlar.DOSYA_YOLLARI[1]
        return d_yolu_format.format(
            base_img_dir=gorsel_klasor_yolu,
            lang=Diller.aktif_dil.name.lower(),
            resolution=aktif_ekran_boyutu_getir(),
            file_name=gorsel_yolu_oneki,
        )


def aktif_ekran_boyutu_getir() -> EkranBoyut:
    aktif_ekran_boyutu = screen_size()
    aktif_ekran_boyutu = EkranBoyut(aktif_ekran_boyutu.width, aktif_ekran_boyutu.height)
    if aktif_ekran_boyutu not in EkranBoyutEnum.__members__.values():
        raise KullaniciHatasi(f"aktif ekran çözünürlüğü {str(aktif_ekran_boyutu)}, bu çözünürlük desteklenmiyor.")
    return aktif_ekran_boyutu


def aktif_dil_getir() -> DilEnum:
    return Diller.aktif_dil


class BotModu(Protocol):
    __slots__ = ("_sinyal_alma_knl", "_sinyal_gonderme_knl" + "_process", "_ayarlar") + (
        # mod specific slots
    )
    _mod_ad: str
    _aktif: Event = multiprocessing.Event()

    def __new__(cls, *args, **kwargs) -> Self:
        # if not hasattr(cls, "instance"):
        #     cls.instance = super().__new__(cls)
        # cls.__init__(*args, **kwargs)
        # return cls.instance
        ...

    @functools.cached_property
    def _gunlukcu(self) -> logging.Logger:
        ...

    @functools.cached_property
    def ayarlar(self) -> dict[str, str]:
        ...

    def __init__(self) -> None:
        ...

    def _aktifmi(self) -> bool:
        ...

    def _sinyal_yolla(self, sinyal: int) -> None:
        ...

    def _sinyal_bekle(self) -> None:
        ...

    def _sinyal_kontrol(self) -> None:
        ...

    def __repr__(self) -> str:
        ...

    def process_olustur(self) -> multiprocessing.Process:
        ...

    def kapali(self) -> bool:
        ...

    def _aktiflik_yenile(self) -> None:
        ...


class Diller(object):
    __slots__ = []
    _instance = None
    _dil_kitapliklari = {}
    _aktif_dil: DilEnum | None = None

    def __new__(cls, dil: DilEnum | None = None) -> "Diller":
        if cls._instance is None:
            if dil is None:
                dil = DilEnum.TR
            cls._instance = super().__new__(cls)
        if dil is not None:
            cls.aktif_dil_degistir(dil)
        return cls._instance

    @classmethod
    def aktif_dil_getir(cls) -> DilEnum:
        return Diller._aktif_dil if Diller._aktif_dil is not None else DilEnum.TR

    @staticmethod
    def aktif_dil_degistir(dil: DilEnum):
        Diller._aktif_dil = dil
        Diller._dil_yukle()

    @staticmethod
    def _dil_yukle(dil: DilEnum | None = None):
        if dil is None:
            dil = Diller._aktif_dil
        if dil not in Diller._dil_kitapliklari:
            if dil == DilEnum.TR:
                from .lokalizasyon import tr as lokalizasyon_kitapligi
            elif dil == DilEnum.EN:
                from .lokalizasyon import en as lokalizasyon_kitapligi
            else:
                raise Hata("Dil bulunamadı.")
            Diller._dil_kitapliklari[dil] = lokalizasyon_kitapligi.to_dict()

    @staticmethod
    def dil_kitapligi(dil: DilEnum) -> dict[str, dict[str, str]]:
        Diller.aktif_dil = dil
        Diller._dil_yukle(dil)
        return Diller._dil_kitapliklari[dil]

    @staticmethod
    def lokalizasyon(kelime_anahtari, kitaplik="UI", dil: DilEnum | None = None):
        if dil is None:
            dil = Diller._aktif_dil
            if dil is None:
                raise Hata("Dil ayarlanmadı.")
        dil_kitapligi = Diller.dil_kitapligi(dil)
        if kitaplik in dil_kitapligi:
            if kelime_anahtari in dil_kitapligi[kitaplik]:
                return dil_kitapligi[kitaplik][kelime_anahtari]
        return "{}.{}".format(kitaplik, kelime_anahtari)

    @staticmethod
    def lang_cache_clear():
        """
        clear cache of to_dict function in lokalizasyon modules
        if they are imported
        """
        import sys

        # WARNING: del statement is not enough it seems to unimport modules
        if "moe_bot.lokalizasyon.tr" in sys.modules:
            module = sys.modules["moe_bot.lokalizasyon.tr"]
            if hasattr(module, "to_dict"):
                module.to_dict.cache_clear()
            del sys.modules["moe_bot.lokalizasyon.tr"]
        if "moe_bot.lokalizasyon.en" in sys.modules:
            module = sys.modules["moe_bot.lokalizasyon.en"]
            if hasattr(module, "to_dict"):
                module.to_dict.cache_clear()
            del sys.modules["moe_bot.lokalizasyon.en"]


class GorselYolu(pathlib.Path):
    __slots__ = ["data"]

    def gorsel_yukle(self):
        if not hasattr(self, "data"):
            if self.exists():
                try:
                    self.data = cv2.imread()  # noqa
                except Exception as exc:
                    _GUNLUKCU.error(f"dosya yüklenirken bir hata ile karşılaşıldı. hata kodu: {exc}")
                    KullaniciHatasi("dosyalar yüklenirken bir hata ile karşılaşıldı. hata kodu: 01")
        return self.data


def gorsel_yolu_oluştur(gorse_yolu_oneki: str) -> GorselYolu:
    gorsel_klasor_yolu = GenelAyarlar.gorsel_dosya_yolu(gorsel_yolu_oneki=gorse_yolu_oneki)
    tam_dosya_yolu = gorsel_klasor_yolu + gorse_yolu_oneki + ".png"
    return GorselYolu(tam_dosya_yolu)


def gorseller_yolu_olustur(gorsel_yolu_onekleri: list[str]) -> list[GorselYolu]:
    return [gorsel_yolu_oluştur(gorse_yolu_oneki) for gorse_yolu_oneki in gorsel_yolu_onekleri]


def singleton_(cls):
    """Decorator to create singleton classes"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


class Fare:
    # TODO: belki silinebilir direkt pyautogui kullanılabilir veya alternatif bir kütüphane

    @staticmethod
    def sagTikla(konum: Optional[Koordinat2D] = None, uyuma_suresi: int | float | None = None):
        if uyuma_suresi is None:
            uyuma_suresi = GenelAyarlar.FARE_UYUMA_SURESI
        _GUNLUKCU.debug("sağ tıklandı")
        time.sleep(uyuma_suresi)
        pyautogui.rightClick(konum)
        time.sleep(uyuma_suresi)

    @staticmethod
    def solTikla(konum: Optional[Koordinat2D] = None, uyuma_suresi: int | float | None = None):
        if uyuma_suresi is None:
            uyuma_suresi = GenelAyarlar.FARE_UYUMA_SURESI
        _GUNLUKCU.debug(f"sol tıklanıyor , konum: {str(konum)}")
        time.sleep(uyuma_suresi)
        pyautogui.leftClick(konum)
        time.sleep(uyuma_suresi)

    @staticmethod
    def hareketEt(konum: Koordinat2D, uyuma_suresi: int | float | None = None):
        if uyuma_suresi is None:
            uyuma_suresi = GenelAyarlar.FARE_UYUMA_SURESI
        _GUNLUKCU.debug(f"fare hareket ettiriliyor , konum: {str(konum)}")
        time.sleep(uyuma_suresi)
        pyautogui.moveTo(konum)
        time.sleep(uyuma_suresi)


class Klavye:
    # TODO: belki silinebilir direkt pyautogui kullanılabilir veya alternatif bir kütüphane
    @staticmethod
    def tus_tek(tus: str):
        pyautogui.press(tus)
        # eski versioyonda UYUMA_SURESI / 1.5
        time.sleep(GenelAyarlar.KLAVYE_UYUMA_SURESI)

    @staticmethod
    def tuslar(tuslar: list[str] | str):
        if isinstance(tuslar, int):
            tuslar = str(tuslar)
        pyautogui.write(tuslar, interval=GenelAyarlar.KLAVYE_UYUMA_SURESI)
