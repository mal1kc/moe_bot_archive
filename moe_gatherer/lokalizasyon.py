import enum
from moe_gatherer.hatalar import Hata

from moe_gatherer.temel_siniflar import KaynakTipi


class DilEnum(enum.Enum):
    """
    dil enum
    """

    # TODO: geliştirme ihtimali var

    TR = {
        "ui": {
            KaynakTipi.EKMEK.name: KaynakTipi.EKMEK.name,
            KaynakTipi.ODUN.name: KaynakTipi.ODUN.name,
            KaynakTipi.TAS.name: KaynakTipi.TAS.name,
            KaynakTipi.DEMIR.name: KaynakTipi.DEMIR.name,
            KaynakTipi.GUMUS.name: KaynakTipi.GUMUS.name,
            KaynakTipi.ALTIN.name: KaynakTipi.ALTIN.name,
            "select_lang_lbl": "Dil Seçiniz",
            "login_lbl": "Giriş yap",
            "login_btn": "Giriş yap",
            "name_lbl": "Kullanıcı Adı : ",
            "pass_lbl": "Şifre : ",
            "msgbx_error_title": "!Hata!",
            "moe_gatherer": "MOE Toplayıcı",
            "mod_select_continue_btn": "Devam Et",
            "mod_select_lbl": "Mod Seçiniz",
            "march_select_lbl": "Sefer Seçiniz",
            "resource_select_lbl": "Kaynak Seçiniz",
            "resource_select_all_btn": "Hepsini Seç",
            "resource_select_none_btn": "Hiçbirini Seçme",
            "lvl_select_lbl": "Seviye Seçiniz",
            "lvl_select_all_btn": "Hepsini Seç",
            "lvl_select_none_btn": "Hiçbirini Seçme",
            "close_gui_btn": "Arayüzü Kapat / Botu Başlat",
            # -- Hata mesajları
            "login_error_username_too_short_or_long": "Kullanıcı adı 3 ile 45 karakter arasında olmalıdır.",
            "login_error_password_too_short_or_long": "Şifre 3 ile 45 karakter arasında olmalıdır.",
            "login_error_connection_error": "Sunucuya erişilemiyor.",
            "login_error_package_not_found": "Kullaniciya Ait Paket bulunamadı.",
            "login_error_maximum_login_error": "Kullanınıcıya ait maksimum giriş kotası doldu 25 dakika sonra tekrar deneyin.",
            "login_error_user_not_found": "Kullanıcı bulunamadı.",
            "login_error_login_information_incorrect": "Kullanıcı adı veya şifre hatalı.",
            "login_error_unsuccessful_login": "Giriş başarısız.",
            "login_error_unknown_error": "Bilinmeyen bir hata meydana geldi.",
            "resource_selection_error": "Kaynak seçimi yapmadınız.\nLütfen kaynak seçimi yapınız.",
            "level_selection_warning": "Seviye seçimi yapmadınız.Tüm seviyeler seçilecek.",
            # -- Bilgi mesajları
            "bot_start_info": "s: Bot başlat.\nd : Bot durdur. (Ekran taramasi bittikten sonra duracaktir)",
        },
    }

    EN = {
        "ui": {
            KaynakTipi.EKMEK.name: "FOOD",
            KaynakTipi.ODUN.name: "WOOD",
            KaynakTipi.TAS.name: "STONE",
            KaynakTipi.DEMIR.name: "IRON",
            KaynakTipi.GUMUS.name: "SILVER",
            KaynakTipi.ALTIN.name: "GOLD",
        },
    }


class _DilSabitleri:
    _instance = None

    def __init__(self, dil: DilEnum = DilEnum.TR) -> None:
        if isinstance(_DilSabitleri._instance, _DilSabitleri):
            raise Hata("DilSabitleri sınıfından birden fazla instance oluşturulamaz.")
        self.AktifDil = dil

    def aktifi_dil_degistir(self, dil: DilEnum) -> None:
        self.AktifDil = dil


# IMPORTANT: silme bu instance'ı
DilSabitleri = _DilSabitleri()


def lokalizasyon(kelime_anahtari: str) -> str:
    """
    kelime_anhatari verilen kelimeyi aktif dile göre getirir eğer yoksa kelime_anhatari döndürür
    """

    if kelime_anahtari in DilSabitleri.AktifDil.value["ui"]:
        return DilSabitleri.AktifDil.value["ui"][kelime_anahtari]
    else:
        return kelime_anahtari
