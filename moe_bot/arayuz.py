from __future__ import annotations

import multiprocessing
from tkinter import BooleanVar, Button, Checkbutton, Entry, Frame, Label, PhotoImage, Tk
from tkinter.ttk import Combobox

from moe_bot.arayuz_temel import (
    ENTRY_WIDTH,
    ICON_PATH,
    LOGGER,
    UnExpectedPageError,
    _error_msgbx,
    _load_credentials,
    _save_credentials,
)
from moe_bot.enumlar import GUIPagesEnum, ModEnum, SelectibleModEnum
from moe_bot.hatalar import BaglantiHatasi, Hata
from moe_bot.mod.arayuz_gatherer import Moe_Gatherer_Page
from moe_bot.sifremele import sifre_hash_olustur
from moe_bot.sunucu_islemleri import SunucuIslem, SunucuIslemSonucu
from moe_bot.temel_siniflar import DilEnum, Diller, KullaniciGirisVerisi

multiprocessing.freeze_support()  # noqa # for pyinstaller


class MainGui:
    __slots__ = ["root", "page", "pageshow", "interaction_variables"]

    def __init__(
        self,
        root: Tk | None = None,
        title: str = "window_title_main",
        geometry: str = "500x600",
    ):
        self.interaction_variables = {
            "mod_name": None,
            "mod_settings": None,
            "server": None,
        }
        if root is None:
            root = Tk()
        self.root = root
        self.root.resizable(False, False)
        self.root.geometry(geometry)
        self.root.iconphoto(True, PhotoImage(file=ICON_PATH))
        self.change_title(title)
        self.interaction_variables = {}
        self.pageshow = Login_Page(self, self.root)

    def change_page(self, page: GUIPagesEnum):
        self.page = page
        if hasattr(self.pageshow, "frame"):
            self.pageshow.frame.destroy()  # type: ignore

        if self.page == GUIPagesEnum.MOD_SELECT:
            self.pageshow = Mod_Select_Page(self, self.root)

        elif self.page == GUIPagesEnum.MOE_GATHERER:
            self.pageshow = Moe_Gatherer_Page(self, self.root)

    def change_title(self, title: str):
        prefix = Diller.lokalizasyon("window_title_main")
        self.root.title("{} - {}".format(prefix, title))

    def make_interaction_variables_ready(self) -> None:
        if isinstance(self.pageshow.name, ModEnum):
            try:
                self.interaction_variables = {
                    "mod_name": self.pageshow.name,
                    "mod_settings": self.pageshow.get_settings(),  # type: ignore
                    "server": self.interaction_variables["server"],
                }
            except Hata as exc:
                LOGGER.exception(f"Exception occured {exc} while getting settings for {self.pageshow.name=}")
                return
            self.root.destroy()
            return
        raise UnExpectedPageError("Unexpected page")

    def mainloop(self):
        self.root.mainloop()


class Login_Page:
    def __init__(self, parent, window):
        self.parent = parent
        self.parent.change_title(Diller.lokalizasyon("window_title_login"))
        self.name = GUIPagesEnum.LOGIN
        self.window = window
        # change size of window to 360x140
        self.parent.root.geometry("360x140")

        self._init_frame()

    def _init_frame(self):
        # -- language selection --
        self.frame = Frame(self.window)
        self.frame.pack()
        self.select_lang_lbl = Label(self.frame, text=Diller.lokalizasyon("select_lang_lbl"))
        self.select_lang_lbl.grid(row=3, column=0)

        self.select_lang_combo = Combobox(
            self.frame,
            values=[Diller.lokalizasyon(lang.name) for lang in DilEnum],
            state="readonly",
        )
        self.select_lang_combo.current(0)  # default value
        self.select_lang_combo.bind("<<ComboboxSelected>>", self._lang_changed)
        self.select_lang_combo.grid(row=4, column=0)

        # -- language selection --

        def _focus_next_widget(event):
            event.widget.tk_focusNext().focus()
            return "break"

        def _press_btn(event):
            self.clicked()
            return "break"

        # -- login --

        self.login_lbl = Label(self.frame, text=Diller.lokalizasyon("login_lbl"))
        self.login_lbl.grid(row=0, column=1)

        self.name_lbl = Label(
            self.frame,
            text=Diller.lokalizasyon("name_lbl"),
            anchor="e",
            width=ENTRY_WIDTH // 2,
        )
        self.name_lbl.grid(row=1, column=0)

        self.name_entry = Entry(self.frame, width=ENTRY_WIDTH)
        self.name_entry.bind("<Return>", _focus_next_widget)
        self.name_entry.grid(row=1, column=1)

        self.pass_lbl = Label(
            self.frame,
            text=Diller.lokalizasyon("pass_lbl"),
            width=ENTRY_WIDTH // 2,
            anchor="e",
        )
        self.pass_lbl.grid(row=2, column=0)

        self.pass_entry = Entry(self.frame, width=ENTRY_WIDTH, show="*")
        self.pass_entry.bind("<Return>", _focus_next_widget)
        self.pass_entry.grid(row=2, column=1)

        self.rem_me_var = BooleanVar()
        self.rem_me_chkbx = Checkbutton(
            self.frame,
            text=Diller.lokalizasyon("rem_me_chkbx"),
            variable=self.rem_me_var,
        )
        self.rem_me_chkbx.grid(row=3, column=1)

        self.sbt = Button(self.frame, text=Diller.lokalizasyon("login_btn"), command=self.clicked)
        self.sbt.bind("<Return>", _press_btn)
        self.sbt.grid(row=4, column=1)

        # -- login --

        # -- save credentials --
        if (credentials := _load_credentials()) != ("", ""):
            self.name_entry.insert(0, credentials[0])
            self.pass_entry.insert(0, credentials[1])
            self.rem_me_var.set(True)

        # -- save credentials --

    def _lang_changed(self, event) -> None:
        # update language
        Diller.aktif_dil_degistir(DilEnum[self.select_lang_combo.get()])  # type: ignore
        self.name_lbl.config(text=Diller.lokalizasyon("name_lbl"))
        self.pass_lbl.config(text=Diller.lokalizasyon("pass_lbl"))
        self.rem_me_chkbx.config(text=Diller.lokalizasyon("rem_me_chkbx"))
        self.sbt.config(text=Diller.lokalizasyon("login_btn"))
        self.select_lang_lbl.config(text=Diller.lokalizasyon("select_lang_lbl"))
        self.login_lbl.config(text=Diller.lokalizasyon("login_lbl"))
        self.parent.change_title(Diller.lokalizasyon("window_title_login"))

    def clicked(self):
        user_data = (self.name_entry.get(), self.pass_entry.get())
        # check is short or too long
        if len(user_data[0]) < 3 or len(user_data[0]) > 45:
            LOGGER.debug(f"Kullanici adi kisa veya uzun hatasi {user_data[0]=}")
            _error_msgbx("login_error_username_too_short_or_long")
            return
        if len(user_data[1]) < 3 or len(user_data[1]) > 45:
            LOGGER.debug(f"Sifre kisa veya uzun hatasi {len(user_data[1])=}")
            _error_msgbx("login_error_password_too_short_or_long")
            return
        try:
            self.user_login_data = KullaniciGirisVerisi(
                name=user_data[0],
                password_hash=sifre_hash_olustur(user_data[1]),
            )
            self.sunucu_islem = SunucuIslem(self.user_login_data)
            if self.rem_me_var.get():
                _save_credentials(user_data)
            if (giris_sonucu := self.sunucu_islem.giris_yap()) == SunucuIslemSonucu.BASARILI:
                self.frame.destroy()
                self.parent.interaction_variables["server"] = self.sunucu_islem
                self.parent.change_page(GUIPagesEnum.MOE_GATHERER)
            elif giris_sonucu == SunucuIslemSonucu.BAGLANTI_HATASI:
                _error_msgbx("login_error_connection_error")
                return
            elif giris_sonucu == SunucuIslemSonucu.PAKET_BULUNAMADI:
                _error_msgbx("login_error_package_not_found")
            elif giris_sonucu == SunucuIslemSonucu.MAKSIMUM_GIRIS_HATASI:
                _error_msgbx("login_error_maximum_login_error")
            elif giris_sonucu == SunucuIslemSonucu.KULLANICI_BULUNAMADI:
                _error_msgbx("login_error_user_not_found")
            elif giris_sonucu == SunucuIslemSonucu.GIRIS_BILGISI_HATALI:
                _error_msgbx("login_error_login_information_incorrect")
            elif giris_sonucu == SunucuIslemSonucu.BASARISIZ:
                _error_msgbx("login_error_unsuccessful_login")
            return
        except BaglantiHatasi:
            _error_msgbx("login_error_connection_error")
        except Exception as exc:
            LOGGER.exception(f"Exception occured {exc}")
            _error_msgbx("login_error_unknown_error")


class Mod_Select_Page:
    def __init__(self, parent, window) -> None:
        self.parent = parent
        self.parent.change_title(Diller.lokalizasyon("window_title_mode_select"))
        self.name = GUIPagesEnum.MOD_SELECT

        # change size of window to 200x100
        self.parent.root.geometry("200x140")

        self.frame = Frame(window)
        self.frame.pack(fill="both", expand=False, padx=10, pady=10, anchor="center")

        self.mod_select_lbl = Label(self.frame, text="mod_select_lbl")
        self.mod_select_lbl.grid(row=0, column=1)

        self.mod_selection_combo = Combobox(
            self.frame,
            state="readonly",
            values=[Diller.lokalizasyon(module.name) for module in SelectibleModEnum],
        )
        self.mod_selection_combo.current(0)  # default value moe_gatherer
        self.mod_selection_combo.grid(row=1, column=1, padx=10, pady=10, ipadx=10, ipady=10)

        self.mod_select_continue_btn = Button(
            self.frame,
            text=Diller.lokalizasyon("mod_select_continue_btn"),
            command=self.clicked,
        )
        self.mod_select_continue_btn.grid(row=2, column=1)

    def clicked(self):
        self.frame.destroy()
        self.parent.change_page(GUIPagesEnum.MOE_GATHERER)


if __name__ == "__main__":
    root = Tk()
    # MainGui(root, "moe_auto_bot", "500x600")
    # root.attributes("-alpha", 0.95)
    # root.mainloop()
    main_gui = MainGui(root, "moe_auto_bot", "500x600")
    main_gui.pageshow = Moe_Gatherer_Page(main_gui, root)
    main_gui.mainloop()
