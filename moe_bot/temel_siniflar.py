import logging
import importlib

from collections import namedtuple
from enum import Enum, IntEnum, auto, StrEnum
from typing import NamedTuple, Optional

from .hatalar import Hata

Koordinat2D = namedtuple("Koordinat2D", ["x", "y"], defaults=[0, 0])

_GUNLUKCU = logging.getLogger()


class IslemSinyalleri(IntEnum):
    DEVAM_ET = auto()
    DUR = auto()
    SONLANDIR = auto()
    MESAJ_ULASMADI = auto()
    MESAJ_ULASTI = auto()
    FAILSAFE_SONLANDIR = auto()


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


# lazy loader
class AyarYukleyici(object):
    _yuklenebilir_ayarlar = ["lokalizasyon.tr", "lokalizasyon.en", "ayarlar.moe_gatherer", "ayarlar.ui", "ayarlar.moe_genel"]

    def __init__(self) -> None:
        self.aktif_ayarlar = None

    def ayar_yukle(self, ayar_dosyasi_adi):
        if ayar_dosyasi_adi not in self._yuklenebilir_ayarlar:
            raise Hata(f"Yüklenemeyen ayar dosyası: {ayar_dosyasi_adi}")
        ayar_dosyasi_adi = "." + ayar_dosyasi_adi
        self.ayarlar = importlib.import_module(ayar_dosyasi_adi, __package__).__dict__
        return self.ayarlar


class DilEnum(StrEnum):
    TR = auto()
    EN = auto()


class Diller(object):
    __slots__ = []
    _instance = None
    _EN_DICT = None
    _TR_DICT = None
    _aktif_dil = None

    def __new__(cls) -> "Diller":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, aktif_dil: DilEnum = DilEnum.TR) -> None:
        Diller.aktif_dil_ayarla(aktif_dil)

    @property
    def aktif_dil(self):
        return Diller._aktif_dil

    @staticmethod
    def _dil_yukle(dil: DilEnum | None = None):
        if dil is None:
            dil = Diller._aktif_dil
        if dil == DilEnum.TR:
            return Diller.TR
        elif dil == DilEnum.EN:
            return Diller.EN
        else:
            raise Hata("Dil bulunamadı.")

    @staticmethod
    def aktif_dil_ayarla(dil: DilEnum):
        Diller._aktif_dil = dil
        Diller._dil_yukle()

    @property
    def TR(self) -> dict[str, dict[str, str]]:
        if not hasattr(self, "_TR_DICT"):
            Diller._TR_DICT = None
        if Diller._TR_DICT is None:
            _GUNLUKCU.debug("TR_DICT oluşturuluyor.")
            Diller._TR_DICT = AyarYukleyici().ayar_yukle("lokalizasyon.tr")

        if not hasattr(self, "_EN_DICT"):
            Diller._EN_DICT = None
        else:
            if Diller._EN_DICT is not None:
                _GUNLUKCU.debug("EN_DICT siliniyor.")
                del Diller._EN_DICT

        return Diller._TR_DICT

    @property
    def EN(self) -> dict[str, dict[str, str]]:
        if not hasattr(self, "_EN_DICT"):
            Diller._EN_DICT = None
        if Diller._EN_DICT is None:
            _GUNLUKCU.debug("EN_DICT oluşturuluyor.")
            Diller._EN_DICT = AyarYukleyici().ayar_yukle("lokalizasyon.en")

        if not hasattr(self, "_TR_DICT"):
            Diller._TR_DICT = None
        else:
            if Diller._TR_DICT is not None:
                _GUNLUKCU.debug("TR_DICT siliniyor.")
                del Diller._TR_DICT

        return Diller._EN_DICT

    @staticmethod
    def dil_kitapligi(dil: DilEnum) -> dict[str, dict[str, str]]:
        diller_instance = Diller()
        if dil == DilEnum.TR:
            return diller_instance.TR
        elif dil == DilEnum.EN:
            return diller_instance.EN
        else:
            raise Hata("Dil bulunamadı.")

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
