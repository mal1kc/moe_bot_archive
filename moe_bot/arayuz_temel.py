import logging
import os
from tkinter import messagebox

from moe_bot.ayarlar.arayuz_ayarları import CRED_PATH, GUI_ENTRY_WIDTH, GUI_ICON_PATH, GUI_LOGO_PATH
from moe_bot.temel_siniflar import Diller

LOGGER = logging.getLogger(__name__)

LOGO_PATH = GUI_LOGO_PATH

ENTRY_WIDTH = GUI_ENTRY_WIDTH

ICON_PATH = GUI_ICON_PATH


def _load_credentials() -> tuple[str, str]:
    if not os.path.exists(CRED_PATH):
        return ("", "")
    try:
        with open(CRED_PATH, "r") as f:
            name = f.readline().strip()
            password = f.readline().strip()
            return (name, password)
    except Exception as exc:
        LOGGER.exception(f"Exception occured {exc} while loading credentials")
        _error_msgbx("login_error_credential_load_error")
    return ("", "")


def _save_credentials(credentials: tuple[str, str]) -> None:
    if not os.path.exists(os.path.dirname(CRED_PATH)):
        os.makedirs(os.path.dirname(CRED_PATH))
    with open(CRED_PATH, "w") as f:
        f.write(credentials[0] + "\n")
        f.write(credentials[1] + "\n")


def _error_msgbx(error: str) -> None:
    messagebox.showerror(Diller.lokalizasyon("msgbx_error_title", "UI"), Diller.lokalizasyon(error, "UI"))


def _warning_msgbx(warning: str) -> None:
    messagebox.showwarning(Diller.lokalizasyon("msgbx_warning_title", "UI"), Diller.lokalizasyon(warning, "UI"))


class UnExpectedPageError(Exception):
    pass
