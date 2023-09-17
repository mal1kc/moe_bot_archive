from __future__ import annotations

import glob
import importlib

# TODO: finish this implementation and use example in ./ayarlar_kullanimi.py


def mod_yukle(mod: str) -> ModAyar:
    # TODO: implement this
    gorseller = []
    izin_verilen_modlar = ["moe_gatherer", "moe_camp"]
    if mod in izin_verilen_modlar:
        # TODO: önekleri değiştir
        genel_mod = importlib.import_module("karalama_dosyaları.ayarlar_modulu_karalama.moe_general")
        modul = importlib.import_module(f"karalama_dosyaları.ayarlar_modulu_karalama.{mod}")
        gorseller = genel_mod.GORSELLER
        print(gorseller)
        print(modul.__dict__)
    return ModAyar("moe_gatherer", gorseller)


class ModAyar(object):
    __slots__ = [
        "gorsel_dizini",  # relative path to the directory that contains images
        "gorseller",
    ]

    def __init__(
        self,
        gorsel_dizini: str,
        gorseller: list[CokluGorselAyar | GorselAyar],
    ):
        self.gorsel_dizini = gorsel_dizini
        self.gorseller = gorseller


class Ayarlar(object):
    GORSEL_DIZINI = "imgs"

    dil = "tr"
    ekran_boyutu = (1920, 1080)
    ayarlandi = False

    @classmethod
    def ayarla(cls, dil: str, mod: str, ekran_boyutu: EkranBoyut):  # type: ignore # noqa
        cls.dil = dil
        cls.ekran_boyutu = ekran_boyutu
        cls.mod = mod_yukle(mod)
        cls.ayarlandi = True


class GorselAyar(object):
    def __init__(
        self,
        gorsel_dosya_adi: str,
        gorsel_eminlik: float = 0.7,
    ):
        self.gorsel_dosya_adi = gorsel_dosya_adi
        self.gorsel_eminlik = gorsel_eminlik

    def __str__(self):
        return f"{self.gorsel_dosya_adi}, {self.gorsel_eminlik}"

    def __repr__(self):
        return f"{self.gorsel_dosya_adi}, {self.gorsel_eminlik}"

    def gorselGetir(self):
        if Ayarlar.ayarlandi:
            return f"{Ayarlar.GORSEL_DIZINI}/{Ayarlar.mod.gorsel_dizini}/{self.gorsel_dosya_adi}"


class CokluGorselAyar:
    """
    list that contains only GorselAyar objects and creates
    """

    def __init__(self, name: str, glob_gorsel_adi: str, eminlikler: list[float] = [0.7]):
        self.glob_gorsel_adi = glob_gorsel_adi
        if len(eminlikler) == 0 or eminlikler is None:
            self.eminlik = 0.7
        elif len(eminlikler) > 0:
            self.eminlikler = eminlikler
        self.eminlikler = eminlikler
        self.gorsel_ayarlari = []
        self.name = name
        self.gorseller_yuklendi = False

    def __str__(self):
        return f"{self.glob_gorsel_adi}, {self.eminlikler}"

    def __iter__(self):
        return iter(self.gorsel_ayarlari)

    def __repr__(self):
        return self.__str__()

    def gorselleri_yukle(self):
        if not Ayarlar.ayarlandi:
            raise Exception("Ayarlar ayarlanmadı")
        gorsel_dl_glob = glob.glob(f"{Ayarlar.GORSEL_DIZINI}/{Ayarlar.mod.gorsel_dizini}/{self.glob_gorsel_adi}")
        if len(gorsel_dl_glob) == 0:
            raise Exception("Görsel dosyası bulunamadı")
        if len(gorsel_dl_glob) == len(self.eminlikler):
            for gorsel_dl, eminlik in zip(gorsel_dl_glob, self.eminlikler):
                self.gorsel_ayarlari.append(GorselAyar(gorsel_dl, eminlik))
        elif len(gorsel_dl_glob) > len(self.eminlikler):
            for gorsel_dl in gorsel_dl_glob:
                if len(self.eminlikler) == 1 and hasattr(self, "eminlik"):
                    self.gorsel_ayarlari.append(GorselAyar(gorsel_dl, self.eminlik))
        self.gorseller_yuklendi = True

    def gorselleri_getir(self):
        if Ayarlar.ayarlandi and self.gorseller_yuklendi:
            return self.gorsel_ayarlari
        if Ayarlar.ayarlandi and not self.gorseller_yuklendi:
            self.gorselleri_yukle()
            return self.gorsel_ayarlari
        raise Exception("Ayarlar ayarlanmadı")
