from typing import Any, Optional


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
            if type(v) is dict:
                ic_sonuc = sozlukBirlestir(sozluk1[k], sozluk2[k])
            sonuc[k] = ic_sonuc
        return sonuc
    else:
        sonuc = {**sozluk1, **sozluk2}
    return sonuc
