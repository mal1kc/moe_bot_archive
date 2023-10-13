import multiprocessing
import sys
import threading
import time
from moe_bot.yonetici import BotIslemYonetici  # noqa


from moe_bot import arayuz

from moe_bot.temel_siniflar import DilEnum, Diller  # noqa

from moe_bot.hatalar import Hata  # noqa

CHILD_WAIT_TIME = 2


def _bilgi_yazdir():
    print("\r")
    print(Diller.lokalizasyon("bot_start_info", "UI"))


def _tum_tread_ve_alt_processleri_oldur():
    tum_threadler = threading.enumerate()
    tum_processler = multiprocessing.active_children()
    try:
        for thread in tum_threadler:
            if thread.name != "MainThread":
                time.sleep(CHILD_WAIT_TIME)
                try:
                    thread.join(timeout=CHILD_WAIT_TIME)
                except RuntimeError:
                    print(f"f* you {thread.name}")
        for process in tum_processler:
            process.join(timeout=CHILD_WAIT_TIME)
    except Exception:
        pass


def main():
    Diller.aktif_dil_degistir(DilEnum.TR)  # type: ignore
    moe_gatherer_arayuz = arayuz.MainGui()
    moe_gatherer_arayuz.mainloop()

    if len(moe_gatherer_arayuz.interaction_variables.items()) != 3:
        return sys.exit(0)

    _bilgi_yazdir()

    arayuz_degisgenleri_sunucu = moe_gatherer_arayuz.interaction_variables["server"]
    if moe_gatherer_arayuz.interaction_variables["mod_name"] == arayuz.ModEnum.MOE_GATHERER:
        arayuz_degisgenleri_mod_ayarlari = moe_gatherer_arayuz.interaction_variables["mod_settings"]
        del moe_gatherer_arayuz
    else:
        raise Hata("mod_hatalı")

    if arayuz_degisgenleri_mod_ayarlari is not None:
        bt = BotIslemYonetici(
            maks_sefer_sayisi=arayuz_degisgenleri_mod_ayarlari["march_count"],
            kaynak_tipleri=arayuz_degisgenleri_mod_ayarlari["resources"],
            svyler=arayuz_degisgenleri_mod_ayarlari["lvls"],
            sunucu_islem=arayuz_degisgenleri_sunucu,  # type: ignore
        )

        bt.botBaslat()
    _tum_tread_ve_alt_processleri_oldur()
    print(Diller.lokalizasyon("bot_stop_info", "UI"))
    sys.exit(0)


if __name__ == "__main__":
    main()
