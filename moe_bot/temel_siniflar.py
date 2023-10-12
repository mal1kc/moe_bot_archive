import logging

from collections import namedtuple
from enum import Enum, auto
import threading

# -- typing
from typing import Callable, Optional, NamedTuple
from threading import Timer

# -- end typing


from moe_bot.enumlar import DilEnum


from .hatalar import Hata


Koordinat2D = namedtuple("Koordinat2D", ["x", "y"], defaults=[0, 0])

_GUNLUKCU = logging.getLogger()


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


class Diller(object):
    __slots__ = []
    _instance = None
    _instance_kilit = threading.Lock()
    _dil_kitapliklari = {}
    _aktif_dil: DilEnum | None = None

    def __new__(cls, dil: DilEnum | None = None) -> "Diller":
        if cls._instance is None:
            with cls._instance_kilit:
                # Another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if not cls._instance:
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
        with Diller._instance_kilit:
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


class RepeatedTimer(object):
    def __init__(self, interval: int | float, function: Callable, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()  # type: ignore
        self.is_running = False
