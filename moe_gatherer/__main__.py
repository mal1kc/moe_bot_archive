from .gunlukcu import Gunlukcu  # noqa
from .temel_siniflar import KaynakTipi  # noqa
from .yonetici import BotIslemYonetici  # noqa

from . import BotIslemYonetici, arayuz, cihaz_yetkilimi  # noqa
from .temel_siniflar import KaynakTipi  # noqa


def _bilgi_yazdir():
    print("\r")
    print("s: Bot başlat.\nd : Bot durdur. (Ekran taramasi bittikten sonra duracaktir)")


def main():
    if cihaz_yetkilimi():
        botarayuz = arayuz.BotArayuz()
        _bilgi_yazdir()
        botarayuz.mainloop()
        arayuz_degisgenleri = botarayuz.arayuz_degiskenleri

        if arayuz_degisgenleri is not None:
            bt = BotIslemYonetici(
                maks_sefer_sayisi=arayuz_degisgenleri["sefer_sayisi"],
                kaynak_tipleri=arayuz_degisgenleri["kaynak_tipleri"],
                svyler=arayuz_degisgenleri["svyler"],
            )
            bt.botBaslat()


if __name__ == "__main__":
    main()
