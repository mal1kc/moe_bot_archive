# circular import hatası alabiliriz
import logging
from typing import Any
import win32api
import win32con

hata_gunlukcu = logging.getLogger("gunlukcu.hatalar")

hata_gunlukcu.setLevel(logging.ERROR)


class Hata(Exception):
    """
    Hata sınıfı
    """

    def __init__(self, *args: Any) -> None:
        hata_gunlukcu.exception(f"Hata oluştu {args}")
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
