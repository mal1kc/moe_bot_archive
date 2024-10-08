"""
bu dosya
- lokalizasyon anahtarını yazmak için kullanılan örnek
- runtime sırasında kullanılmayacak
- o yuzden dosya adı __ignore__.py
- anahtar karşılıklarını str olucak şekilde yazın
"""
from functools import lru_cache


@lru_cache
def to_dict():
    return {
        "UI": {
            "TR": None,
            "EN": None,
            "food": None,
            "wood": None,
            "stone": None,
            "iron": None,
            "silver": None,
            "gold": None,
            "select_lang_lbl": None,
            "login_lbl": None,
            "login_btn": None,
            "name_lbl": None,
            "pass_lbl": None,
            "rem_me_chkbx": None,
            "msgbx_error_title": None,
            "moe_gatherer": None,
            "mod_select_continue_btn": None,
            "mod_select_lbl": None,
            "march_selection_lbl": None,
            "resource_selection_lbl": None,
            "resource_select_all_chkbx": None,
            "lvl_selection_lbl": None,
            "lvl_select_all_chkbx": None,
            "start_bot_btn": None,
            "exit_btn": None,
            "warning_top_lbl": None,
            "warning_bottom_lbl": None,
            "window_title_gatherer": None,
            "window_title_login": None,
            "window_title_main": None,
            "window_title_mod_select": None,
            "login_error_username_too_short_or_long": None,
            "login_error_password_too_short_or_long": None,
            "login_error_connection_error": None,
            "login_error_package_not_found": None,
            "login_error_maximum_login_error": None,
            "login_error_user_not_found": None,
            "login_error_login_information_incorrect": None,
            "login_error_unsuccessful_login": None,
            "login_error_unknown_error": None,
            "resource_selection_error": None,
            "level_selection_warning": None,
            "bot_start_info": None,
            "unexpected_error": None,
            "gatherer_error_screen_resolution_error": None,
        },
        "IMG_FOLDER": None,
        "ERROR": {
            "server_connection_error": None,
            "server_session_renewal_error_package_not_found": None,
            "server_session_renewal_error_server_error": None,
            "server_session_renewal_error_unknown_error": None,
            "server_session_renewal_error_max_online_user": None,
        },
    }
