# TODO : pyautogui -> locateOnScreen ' e wrapper yaz (engeltarayici arada çalışsın)
# def _ekranTara(locateOnScreen:Callable,*args,**kwargs):
#     '''
#     wraps pyautogui.locateOnScreen
#     '''
#     if EngelTarayici().engelKontrol():

import logging
from typing import Any

from pyscreeze import locateOnScreen
from moe_bot.temel_siniflar import Kare, GorselYolu


class GorselTarayici:
    __slots__ = ("gorsel_d", "eminlik", "konum", "gri_tarama", "isim", "_gunlukcu")

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
        return self.ekran_tara()

    @property
    def _gunlukcu(self):
        return logging.getLogger(__name__)

    def ekran_tara(self) -> None | Kare:
        if isinstance(self.konum, Kare):
            tarama_sonucu = locateOnScreen(self.gorsel_d, confidence=self.eminlik, region=self.konum, grayscale=self.gri_tarama)
        else:
            tarama_sonucu = locateOnScreen(self.gorsel_d, confidence=self.eminlik, grayscale=self.gri_tarama)
        self._gunlukcu.debug(f"{self.isim} ekran taraması -> {tarama_sonucu}")
        if tarama_sonucu:
            return Kare(tarama_sonucu.left, tarama_sonucu.top, tarama_sonucu.width, tarama_sonucu.height)
        return None

    def __str__(self) -> str:
        return f"{self.isim} -> {self.gorsel_d} -> {self.eminlik} -> {self.konum} -> {self.gri_tarama}"

    def __repr__(self) -> str:
        return "{} -> {} -> {} -> {} -> {}".format(self.isim, self.gorsel_d, self.eminlik, self.konum, self.gri_tarama)
