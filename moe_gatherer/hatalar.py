# circular import hatası alabiliriz
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
    belki kullanıcıdan kaynaklı hatalar için
    kullanılabilir

    Todo:
        - belki oluşturulabilir
        - msgbox vs ile hatalar kullanıcıya gösterilebilir
    """

    def __init__(self, *args: Any) -> None:
        self.hata_mesaji = args
        win32api.MessageBox(
            None,
            args[0],
            "Kullanıcı Hatası",
            win32con.MB_OK | win32con.MB_ICONERROR,
        )  # type: ignore
        exit(1)
