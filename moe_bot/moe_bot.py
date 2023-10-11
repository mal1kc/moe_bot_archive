from moe_bot.yonetici import BotIslemYonetici  # noqa


from moe_bot import arayuz

from moe_bot.temel_siniflar import DilEnum, Diller  # noqa

from moe_bot.hatalar import Hata  # noqa


def _bilgi_yazdir():
    print("\r")
    print(Diller.lokalizasyon("bot_start_info", "UI"))


def main():
    Diller.aktif_dil_degistir(DilEnum.TR)  # type: ignore
    moe_gatherer_arayuz = arayuz.MainGui()
    moe_gatherer_arayuz.mainloop()

    if len(moe_gatherer_arayuz.interaction_variables.items()) != 3:
        return exit()

    print(moe_gatherer_arayuz.interaction_variables)
    _bilgi_yazdir()

    # TODO: botislem yoneticisi ne mod adi verilecek? modları parçalı yaptıktan sonra
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


if __name__ == "__main__":
    main()
