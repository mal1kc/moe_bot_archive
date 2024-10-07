import logging
import multiprocessing
from os import PathLike
import threading

import pyscreeze

import cv2
import numpy

from cv2.typing import MatLike
from pathlib import Path
from typing import Any, Protocol
from PIL import Image
from pyscreeze import locateOnScreen


from moe_bot.temel_siniflar import Gorsel, IsimliDizi, Kare

# TODO: Cascade disindaki tum tarayticilar coklu olabilir


def ekran_goruntusu(bolge: Kare | None = None):
    screenshot_img = pyscreeze.screenshot(region=bolge)
    return screenshot_img


class ekranTaramaSonuc(Protocol):
    bulundu_mu: bool
    sirali_tarama: bool
    bulunan_kare: Kare | None
    bulunan_cisim: str | None
    bulunan_cisim_sirasi: int | None


# FIXME : tüm tarayicilar bu protokole uymalı
class Tarayici(Protocol):
    def __call__(self, *args: Any, **kwds: Any) -> Any: ...

    def ekranTara(self) -> ekranTaramaSonuc: ...


class PyAutoTarayici:
    __slots__ = ("isim", "gorsel_yollari", "eminlikler", "konum", "gri_tarama")

    def __init__(
        self,
        isim: str,
        gorsel_yollari: tuple[Gorsel, ...] | Gorsel,
        eminlikler: tuple[float, ...] | float,
        konum: Kare | None = None,
        gri_tarama: bool = False,
        resimleri_ramde_tut: bool = False,
    ) -> None:
        self.isim = isim
        if isinstance(gorsel_yollari, tuple):
            self.gorsel_yollari = gorsel_yollari
        elif isinstance(gorsel_yollari, str) or isinstance(gorsel_yollari, Path):
            self.gorsel_yollari = (gorsel_yollari,)
        else:
            raise TypeError("gorsel_yolları str|Path veya str|Pathlardan oluşan tuple olmalı")

        if isinstance(eminlikler, tuple):
            self.eminlikler = eminlikler
        elif isinstance(eminlikler, float):
            self.eminlikler = (eminlikler,)
        else:
            raise TypeError("eminlikler float veya floatlardan oluşan tuple olmalı")

        if len(self.gorsel_yollari) != len(self.eminlikler):
            raise ValueError("gorsel_yolları ve eminlikler aynı uzunlukta olmalı")

        self.konum = konum
        self.gri_tarama = gri_tarama

        if resimleri_ramde_tut:
            self._gunlukcu.debug(f"{self.isim} -> resimleri ramde tutulacak")
            if isinstance(self.gorsel_yollari[0], PathLike):
                self.gorsel_yollari = tuple(Image.open(gorsel_yol) for gorsel_yol in self.gorsel_yollari)  # type: ignore
        self._gunlukcu.debug(f"{self.isim} -> {self.gorsel_yollari}")

    @property
    def _gunlukcu(self):
        return logging.getLogger(__name__)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.ekranTara()

    def ekranTara(self) -> Kare | None:
        for dosya_yolu, eminlik in zip(self.gorsel_yollari, self.eminlikler):
            tarama_sonucu = locateOnScreen(dosya_yolu, confidence=eminlik, region=self.konum, grayscale=self.gri_tarama)
            self._gunlukcu.debug(f"{self.isim} ekran taraması -> {tarama_sonucu}")
            if tarama_sonucu:
                return Kare(tarama_sonucu.left, tarama_sonucu.top, tarama_sonucu.width, tarama_sonucu.height)
        return None


class SiraliPyAutoTarayici(Tarayici):
    def __init__(
        self,
        isimli_gorsel_yollari: IsimliDizi,
        bolge: Kare | None,
        eminlik: float,
        gri_tarama: bool,
        isim: str = "İsimsiz",
    ) -> None:
        self.isim = isim
        self.bolge = bolge
        self.eminlik = eminlik
        self.gri_tarama = gri_tarama
        self.isimli_gorsel_yollari = isimli_gorsel_yollari

    def ekranTara(self) -> tuple[Any, Kare] | None:
        """
        ilk bulunan örnek dosyanın adının sonundaki sayıyı döndürür\n
        bulunamazsa None döndürür\n
        """
        for ornek_ds_yl in self.isimli_gorsel_yollari:
            kare = locateOnScreen(
                ornek_ds_yl,
                region=self.bolge,
                confidence=self.eminlik,
                grayscale=self.gri_tarama,
            )
            if kare is not None:
                return self.isimli_gorsel_yollari.isim, Kare(kare.left, kare.top, kare.width, kare.height)
        return None

    def ekranTaraThreaded(self) -> tuple[Any, Kare] | None:
        """
        aynı anda birden fazla ekran taraması yapar \n
        isimli dizideki isim ve kareyi döndürür \n
        bulunamazsa None döndürür
        """
        buldum_etkilik = multiprocessing.Event()
        bulunan = multiprocessing.Queue(maxsize=1)

        def _tara(ornek_ds_yl: str | Image.Image):
            if buldum_etkilik.is_set():
                return
            kare = locateOnScreen(
                ornek_ds_yl,
                region=self.bolge,
                confidence=self.eminlik,
                grayscale=self.gri_tarama,
            )
            if kare is not None:
                nonlocal bulunan
                bulunan.put_nowait(Kare(kare.left, kare.top, kare.width, kare.height))
                buldum_etkilik.set()

        # basit thread pool
        threads = []
        for ornek_ds_yl in self.isimli_gorsel_yollari:
            thread = threading.Thread(target=_tara, args=(ornek_ds_yl,))
            if buldum_etkilik.is_set():
                break
            thread.start()
            threads.append(thread)

        while not buldum_etkilik.is_set():
            for thread in threads:
                thread.join()

        if bulunan.qsize() > 0:
            return self.isimli_gorsel_yollari.isim, bulunan.get_nowait()
        return None


class MultiImageTemplateMatcher:
    __slots__ = ("isim", "needle_image_paths", "threshold", "method")

    isim: str
    needle_image_paths: list[str | Path]
    threshold: float

    def __init__(
        self,
        isim: Any,
        needle_image_paths: list[str | Path],
        threshold=0.8,
        method=cv2.TM_CCOEFF_NORMED,
    ):
        self.isim = isim
        self.needle_image_paths = needle_image_paths
        self.threshold = threshold
        self.method = method

    def match(self, haystack_img: numpy.array) -> tuple[int, int, int, int] | None:  # type: ignore
        """
        Tries to find the needle images in the haystack image
        - If no match found in needle image tries the next needle image
        - If no match found in any needle image, returns None
        - If match found, returns the first match location

        Args:
            haystack_img (numpy.array) : haystack image to search needle images

        Returns:
            tuple[int,int,int,int] | None:
                 match location( top_left_x,top_left_y, w, h) of single needle image OR None if no match found
        """
        locations = []
        for template_image_path in self.needle_image_paths:
            needle_img = cv2.imread(str(template_image_path), cv2.IMREAD_GRAYSCALE)
            result = cv2.matchTemplate(haystack_img, needle_img, self.method)
            locations = numpy.where(result >= self.threshold)  # type: ignore
            locations = list(zip(*locations[::-1]))
            if locations:
                return (
                    locations[0][0],
                    locations[0][1],
                    needle_img.shape[1],
                    needle_img.shape[0],
                )
        return None


class SiraliOrnekTarayici(Tarayici):
    __slots__ = ("isim", "gorsel_yollari", "eminlik", "tarama_bolgesi", "gri_tarama", "tarama_metodu")

    def __init__(
        self,
        isim: str,
        gorsel_yollari: IsimliDizi,
        eminlik: float,
        tarama_bolgesi: Kare | None = None,
        gri_tarama: bool = False,
        gorselleri_onceden_yukle: bool = False,
    ) -> None:
        """
        TODO: burayı yaz
        """
        # IMPORTANT: eminlik tüm gorsel_yollari aynı ayarla tarama yapar
        # değiştirilebilir İsimliÇifteDizi oluşturulabilir

        if not isinstance(gorsel_yollari, IsimliDizi):
            raise TypeError("gorsel_yollari IsimliDizi olmalı")

        if not isinstance(eminlik, float):
            raise TypeError("eminlik float olmalı")

        self.isim = isim
        self.gorsel_yollari = gorsel_yollari

        if gorselleri_onceden_yukle:
            self.gorsel_yollari = IsimliDizi(
                gorsel_yollari.isim,
                tuple(Image.open(gorsel_yol) for gorsel_yol in gorsel_yollari),
            )

        self.tarama_bolgesi = tarama_bolgesi
        self.eminlik = eminlik
        self.gri_tarama = gri_tarama
        self.tarama_metodu = cv2.TM_CCOEFF_NORMED

    def ekranTara(
        self,
    ) -> Kare | None:
        ekran_g = ekran_goruntusu(bolge=self.tarama_bolgesi)
        for gorsel_yol in self.gorsel_yollari:
            if not Image.isImageType(gorsel_yol):
                gorsel_yol = Image.open(gorsel_yol)
            sonuc = SiraliOrnekTarayici.tara(gorsel_yol, ekran_g, self.eminlik, self.gri_tarama, self.tarama_metodu)
            if sonuc is not None:
                if self.tarama_bolgesi is not None:
                    return Kare(
                        sonuc.x + self.tarama_bolgesi.x,
                        sonuc.y + self.tarama_bolgesi.y,
                        genislik=sonuc.genislik,
                        yukseklik=sonuc.yukseklik,
                    )
                return sonuc
        return None

    @staticmethod
    def tara(
        ornek_gorsel: Image.Image,
        taranicak_gorsel: Image.Image,
        eminlik: float = 0.9,
        gri_tarama: bool = True,
        tarama_metodu=cv2.TM_CCOEFF_NORMED,
    ) -> Kare | None:
        gorsel: MatLike = numpy.array(ornek_gorsel)
        t_gorsel: MatLike = numpy.array(taranicak_gorsel)

        if gri_tarama:
            gorsel = cv2.cvtColor(gorsel, cv2.COLOR_RGB2GRAY)
            t_gorsel = cv2.cvtColor(t_gorsel, cv2.COLOR_RGB2GRAY)

        konumlar = []
        result = cv2.matchTemplate(t_gorsel, gorsel, tarama_metodu)  # type: ignore
        konumlar = numpy.where(result >= eminlik)  # type: ignore
        konumlar = list(zip(*konumlar[::-1]))
        if konumlar:
            # genel ekrana göre konumlandır
            return Kare(konumlar[0][0], konumlar[0][1], gorsel.shape[1], gorsel.shape[0])
        return None


class IsimliCascade:
    __slots__ = ("isim", "cascade_classifier")
    isim: str
    cascade_classifier: cv2.CascadeClassifier

    def __init__(self, isim: str, cascade_path: str) -> None:
        self.isim = isim
        self.cascade_classifier = cv2.CascadeClassifier(cascade_path)

    def kareBul(self, tarama_yapilacak_gorsel) -> Kare | None:
        """
        kendi cascade_classifier objesi ile tarama_yapilacak_gorsel üzerinde tarama yapar ve ilk bulunan kareyi döner

        """
        gecici_kareler = self.cascade_classifier.detectMultiScale(tarama_yapilacak_gorsel)
        for gecici_kare in gecici_kareler:
            if gecici_kare is not None:
                bulunan_kare = Kare(
                    int(gecici_kare[0]),
                    int(gecici_kare[1]),
                    int(gecici_kare[2]),
                    int(gecici_kare[3]),
                )
                return bulunan_kare

    def kareleriBul(self, tarama_yapilacak_gorsel) -> set[Kare] | None:
        """
        kendi cascade_classifier objesi ile tarama_yapilacak_gorsel üzerinde tarama yapar
        bulunan karelerden oluşan set objesi döner

        Args:
            tarama_yapilacak_gorsel (cv2.typing.MatLike): tarama yapilacak cv2 matrixi

        Returns:
            set[Kare] | None: bulunan karelerden oluşan set yada None
        """
        gecici_kareler = self.cascade_classifier.detectMultiScale(tarama_yapilacak_gorsel)
        return set(
            Kare(
                int(gecici_kare[0]),
                int(gecici_kare[1]),
                int(gecici_kare[2]),
                int(gecici_kare[3]),
            )
            for gecici_kare in gecici_kareler
        )

    def __repr__(self):
        return "<{}({}: {})>".format(
            self.__class__.__name__,
            "isim",
            self.isim,
        )
