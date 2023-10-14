import sys
from typing import Any

import win32api  # noqa: F401
import win32con  # noqa: F401


class Hata(Exception):
    """
    Hata sınıfı
    """

    ...


class BaglantiHatasi(Hata):
    def __init__(self, *args: Any) -> None:
        self.hata_mesaji = args[0] if len(args) > 0 else "Bağlantı Hatası"
        return super().__init__(*args)


class KullaniciHatasi(Hata):
    """
    Kullaniciya msg box ile gösterilen hata sınıfı
    """

    def __init__(self, msg: str, *args, **kwargs) -> None:
        self.hata_mesaji = "❌ " + msg + " ❌"
        win32api.MessageBox(
            None,
            self.hata_mesaji,
            "❌ User Error ❌",
            win32con.MB_OK | win32con.MB_ICONERROR,
        )  # type: ignore
        super().__init__(*args, **kwargs)
        sys.exit(1)  # noqa: F821
