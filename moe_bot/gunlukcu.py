# -*- coding: utf-8 -*-
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Any

if __name__ == "__main__":
    GUNLUK_KLASOR = "loglar"

    try:
        print(f"{GUNLUK_KLASOR} klasorunu temizliyorum.")
        for gunluk in os.listdir(GUNLUK_KLASOR):
            os.remove(f"{GUNLUK_KLASOR}/{gunluk}")
    except Exception as e:
        print(f"hata meydana geldi {e}")
else:
    from moe_bot.ayarlar.genel_ayarlar import GUNLUK_KLASOR, GUNLUK_SEVIYESI

    # Hata => circular import hatası alabiliriz
    # gunlukcu = logging.getLogger('gunlukcu')
    """
    __qualname__ : classın ismini alıyor
    """

    class Gunlukcu(logging.Logger):
        def __init__(self, name=__qualname__, level: int = GUNLUK_SEVIYESI):  # noqa: F821
            super().__init__(name, level=level)
            # self.stream_handlr =logging.StreamHandler()

            # self.addHandler(self.stream_handlr)
            if not os.path.exists(GUNLUK_KLASOR):
                os.mkdir(GUNLUK_KLASOR)
            if level == logging.DEBUG:
                self.file_handlr = logging.handlers.RotatingFileHandler(
                    # f"{GUNLUK_KLASORU}/{name}_{_suan.hour}_{_suan.minute}.log",
                    f"{GUNLUK_KLASOR}/{name}.log",
                    mode="w",
                    maxBytes=1024 * 1024 * 10,  # 10 MB,
                    backupCount=10,
                )

                self.addHandler(self.file_handlr)
            for handler in self.handlers:
                handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            self.propagate = False
            # -- propagate --> bu loggerın parent loggerlara mesaj göndermesini engeller \
            # ----  ( eğer True ise parent loggerlara da mesaj gönderir)

    logging.setLoggerClass(Gunlukcu)

    # gunlukcu = logging.getLogger('gunlukcu')

    def gunlukcuGetir(name: str = "moe_gatherer", cls_instance: object = None) -> logging.Logger:
        if cls_instance is None:
            return logging.getLogger(name)
        if not hasattr(cls_instance, "gunlukcu"):
            gunlukcu = logging.getLogger(name + "." + cls_instance.__class__.__name__)
            cls_instance.gunlukcu = gunlukcu  # type: ignore
            return cls_instance.gunlukcu  # type: ignore
        return cls_instance.gunlukcu  # type: ignore

    def islemSuresiHesapla(gunluk_seviyesi: int = GUNLUK_SEVIYESI) -> Any:
        """
        islem süresini hesaplar ve gunlukler
        """

        def wrapper(func):
            def wrapper2(*args, **kwargs):
                baslangic = datetime.now()
                gunlukcu = logging.getLogger("gunlukcu.islemsuresihesapla")
                sonuc = func(*args, **kwargs)
                bitis = datetime.now()
                gunlukcu.debug(f"{func.__name__} fonksiyon çalışma süresi: {bitis - baslangic}")
                return sonuc

            return wrapper2

        return wrapper
