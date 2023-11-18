from functools import lru_cache


@lru_cache
def to_dict() -> dict[str, dict[str, str] | str]:
    return {
        "UI": {
            "TR": "TR",
            "EN": "EN",
            "food": "FOOD",
            "wood": "WOOD",
            "stone": "STONE",
            "iron": "IRON",
            "silver": "SILVER",
            "gold": "GOLD",
            "select_lang_lbl": "Select Language",
            "login_lbl": "Login",
            "login_btn": "Login",
            "name_lbl": "Username : ",
            "pass_lbl": "Password : ",
            "rem_me_chkbx": "Remember Me",
            "msgbx_error_title": "❌ ! Error ! ❌",
            "moe_gatherer": "MOE Gatherer",
            "mod_select_continue_btn": "Continue",
            "mod_select_lbl": "MOD SELECTION",
            "march_selection_lbl": "March Count",
            "resource_selection_lbl": "Resource Type",
            "resource_select_all_chkbx": "ALL",
            "lvl_selection_lbl": "Resource Level",
            "lvl_select_all_chkbx": "ALL",
            "start_bot_btn": "Start Bot",
            "exit_btn": "Exit",
            "warning_top_lbl": "PLEASE MAKE YOUR SELECTIONS",
            "warning_bottom_lbl": "7.March only works when Extra March is open.",
            "window_title_gatherer": "Gatherer Settings",
            "window_title_login": "Login",
            "window_title_main": "MOE Bot",
            "window_title_mod_select": "MOD SELECTION",
            # -- Error messages
            "login_error_username_too_short_or_long": "Username is too short or long.",
            "login_error_password_too_short_or_long": "Password is too short or long.",
            "login_error_connection_error": "Could not connect to server.",
            "login_error_package_not_found": "Package not found.",
            "login_error_maximum_login_error": "Maximum login quota reached. Try again later.",
            "login_error_user_not_found": "User not found.",
            "login_error_login_information_incorrect": "Username or password is incorrect.",
            "login_error_unsuccessful_login": "Login failed.",
            "login_error_unknown_error": "An unknown error has occurred.",
            "resource_selection_error": "You did not make a resource selection.\nPlease make a resource selection.",
            "level_selection_warning": "You did not make a level selection.",
            # -- Information messages
            "bot_start_info": "s: Start bot.\nd : Stop bot. (It will stop after the screen scan is finished)",
            # -- unexpected error
            "unexpected_error": "An error occured. Please restart the program again.",
            "gatherer_error_screen_resolution_error": "Screen resolution is not suitable. Please run it in 1366x768,1920x1080,3840x2160 resolutions.",  # noqa
        },
        "IMG_FOLDER": "en",
        "ERROR": {
            "server_session_renewal_error_package_not_found": "Package not found.",
            "server_connection_error": "Could not connect to server.",
            "server_session_renewal_error_server_error": "Server error.",
            "server_session_renewal_error_unknown_error": "An unknown error has occurred.",
            "server_session_renewal_error_max_online_user": "Maximum quota reached. Try again later.",
        },
    }
