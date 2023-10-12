from functools import lru_cache


@lru_cache
def to_dict() -> dict[str, dict[str, str] | str]:
    return {
        "UI": {
            "TR": "TR",
            "EN": "EN",
            "food": "EKMEK",
            "wood": "ODUN",
            "stone": "TAŞ",
            "iron": "DEMİR",
            "silver": "GÜMÜŞ",
            "gold": "ALTIN",
            "select_lang_lbl": "Dil Seçiniz",
            "login_lbl": "Giriş yap",
            "login_btn": "Giriş yap",
            "name_lbl": "Kullanıcı Adı : ",
            "pass_lbl": "Şifre : ",
            "rem_me_chkbx": "Beni Hatırla",
            "msgbx_error_title": "❌ ! Hata ! ❌",
            "moe_gatherer": "MOE Toplayıcı",
            "mod_select_continue_btn": "Devam Et",
            "mod_select_lbl": "MOD SEÇİMİ",
            "march_selection_lbl": "Sefer Sayısı",
            "resource_selection_lbl": "Kaynak Tipi",
            "resource_select_all_chkbx": "HEPSİ",
            "lvl_selection_lbl": "Kaynak Seviye",
            "lvl_select_all_chkbx": "HEPSİ",
            "start_bot_btn": "Botu Başlat",
            "exit_btn": "Çıkış",
            "warning_top_lbl": "LÜTFEN SEÇİMLERİNİZİ YAPINIZ",
            "warning_bottom_lbl": "7.Sefer sadece Ekstra Sefer açıldığında çalışır.",
            "window_title_gatherer": "Kaynak Toplayıcı Ayarları",
            "window_title_login": "Giriş",
            "window_title_main": "MOE Bot",
            "window_title_mod_select": "MOD SEÇİMİ",
            # -- Hata mesajları
            "login_error_username_too_short_or_long": "Kullanıcı adı çok kısa veya çok uzun.",
            "login_error_password_too_short_or_long": "Şifre çok kısa veya çok uzun.",
            "login_error_connection_error": "Sunucuya erişilemiyor.",
            "login_error_package_not_found": "Kullaniciya Ait Paket bulunamadı.",
            "login_error_maximum_login_error": "Kullanınıcıya ait maksimum giriş kotası doldu. Daha sonra tekrar deneyiniz.",
            "login_error_user_not_found": "Kullanıcı bulunamadı.",
            "login_error_login_information_incorrect": "Kullanıcı adı veya şifre hatalı.",
            "login_error_unsuccessful_login": "Giriş başarısız.",
            "login_error_unknown_error": "Bilinmeyen bir hata meydana geldi.",
            "resource_selection_error": "Kaynak seçimi yapmadınız.\nLütfen kaynak seçimi yapınız.",
            "level_selection_warning": "Seviye seçimi yapmadınız.",
            # -- Bilgi mesajları
            "bot_start_info": "s: Bot başlat.\nd : Bot durdur. (Ekran taramasi bittikten sonra duracaktir)",
        },
        "IMG_FOLDER": "tr",
        "ERROR": {
            "server_session_renewal_error_package_not_found": "Kullaniciya Ait Paket bulunamadı.",
            "server_session_renewal_error_connection_error": "Sunucuya erişilemiyor.",
            "server_session_renewal_error_server_error": "Sunucu hatası.",
            "server_session_renewal_error_unknown_error": "Bilinmeyen bir hata meydana geldi.",
            "server_session_renewal_error_max_online_user": "Kullanınıcıya ait maksimum giriş kotası doldu. Daha sonra tekrar deneyiniz.",  # noqa
        },
    }
