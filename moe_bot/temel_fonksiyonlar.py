from typing import Any, Optional

from pyautogui import size as _ekranBoyutu

from moe_bot.enumlar import EkranBoyutEnum
from moe_bot.hatalar import KullaniciHatasi
from moe_bot.temel_siniflar import EkranBoyut


def tipVeyaNone(tip: type, degisken: Any) -> Optional[Any]:
    """
    değişkenin tipini kontrol eder
    """
    if isinstance(degisken, tip):
        return degisken
    else:
        return None


def ifItsNone(degisken1: Any, degisken2: Any) -> Any:
    """
    eğer değişken1 None ise değişken2'yi döndürür
    değil ise değişken1'i döndürür
    """
    if degisken1 is None:
        return degisken2
    return degisken1


def getValIfKeyExist(sozluk: dict, key: Any, default: Any = None) -> Any:
    if key in sozluk.keys():
        return sozluk[key]
    return default


def sozlukeriBirlestir(sozluk1: dict, *sozlukler: dict) -> dict:
    """
    iki ve daha fazla sözlüğü birleştirir
    """
    sonuc = sozluk1
    for sozluk in sozlukler:
        sonuc = sozlukBirlestir(sonuc, sozluk)
    return sonuc


def sozlukBirlestir(sozluk1: dict, sozluk2: dict):
    """
    iki sözlüğü birleştirir
    """
    sonuc = dict()
    if sozluk1.keys() == sozluk2.keys():
        for k, v in sozluk1.items():
            ic_sonuc = dict()
            if isinstance(v, dict):
                ic_sonuc = sozlukBirlestir(sozluk1[k], sozluk2[k])
            sonuc[k] = ic_sonuc
        return sonuc
    else:
        sonuc = {**sozluk1, **sozluk2}
    return sonuc


def aktifEkranBoyutu() -> EkranBoyutEnum:
    aktif_ekran_boyutu = _ekranBoyutu()
    aktif_ekran_boyutu = EkranBoyut(aktif_ekran_boyutu.width, aktif_ekran_boyutu.height)
    if aktif_ekran_boyutu not in [ekran_boyut.value for ekran_boyut in EkranBoyutEnum]:
        raise KullaniciHatasi("0x03 -> cannot find suitable screen size")
    return aktif_ekran_boyutu
