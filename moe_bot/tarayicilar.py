import logging
from pathlib import Path
from typing import Any

import cv2
import numpy
from pyscreeze import locateOnScreen

from moe_bot.temel_siniflar import GorselYolu, Kare


class PyAutoTarayici:
    __slots__ = ("gorsel_d", "eminlik", "konum", "gri_tarama", "isim")

    def __init__(
        self,
        gorsel_d: GorselYolu,
        eminlik: float,
        konum: Kare | None = None,
        gri_tarama: bool = False,
        isim: str = "isimsiz_tarayici",
    ):
        self.isim = isim
        self.gorsel_d = gorsel_d
        self.eminlik = eminlik
        self.konum = konum
        self.gri_tarama = gri_tarama

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.ekranTara()

    @property
    def _gunlukcu(self):
        return logging.getLogger(__name__)

    def ekranTara(self) -> Kare | None:
        if isinstance(self.konum, Kare):
            tarama_sonucu = locateOnScreen(self.gorsel_d, confidence=self.eminlik, region=self.konum, grayscale=self.gri_tarama)
        else:
            tarama_sonucu = locateOnScreen(self.gorsel_d, confidence=self.eminlik, grayscale=self.gri_tarama)
        self._gunlukcu.debug(f"{self.isim} ekran taraması -> {tarama_sonucu}")
        if tarama_sonucu:
            return Kare(tarama_sonucu.left, tarama_sonucu.top, tarama_sonucu.width, tarama_sonucu.height)
        return None

    @staticmethod
    def ekranTaraStatic(gorsel_d: GorselYolu, eminlik: float, konum: Kare | None = None, gri_tarama: bool = False) -> Kare | None:
        return PyAutoTarayici(
            gorsel_d=gorsel_d,
            eminlik=eminlik,
            konum=konum,
            gri_tarama=gri_tarama,
        ).ekranTara()

    def __str__(self) -> str:
        return f"{self.isim} -> {self.gorsel_d} -> {self.eminlik} -> {self.konum} -> {self.gri_tarama}"

    def __repr__(self) -> str:
        return "{} -> {} -> {} -> {} -> {}".format(self.isim, self.gorsel_d, self.eminlik, self.konum, self.gri_tarama)


class SiraliPyAutoTarayici:
    def __init__(
        self,
        bolge: Kare | None,
        eminlik: float,
        gri_tarama: bool,
        ornek_ds_yl: list[str],
        isim: str = "İsimsiz",
    ) -> None:
        self.isim = isim
        self.bolge = bolge
        self.eminlik = eminlik
        self.gri_tarama = gri_tarama
        self.ornek_ds_yl = ornek_ds_yl

    def _ekranTara(self) -> int | None:
        """
        ilk bulunan örnek dosyanın adının sonundaki sayıyı döndürür\n
        bulunamazsa None döndürür\n
        """
        # TODO for döngüsü yerine threading ile bir deneme yapılabilir
        for ornek_ds_yl in self.ornek_ds_yl:
            kare = locateOnScreen(
                ornek_ds_yl,
                region=self.bolge,
                confidence=self.eminlik,
                grayscale=self.gri_tarama,
            )
            if kare is not None:
                # TODO : daha iyi yol bulunabilir
                return int(ornek_ds_yl.split(".")[-2].split("_")[-1])
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
            haystack_img (np.array) : haystack image to search needle images

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
