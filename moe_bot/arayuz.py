from __future__ import annotations
import multiprocessing

import os

from moe_bot.hatalar import BaglantiHatasi, Hata, KullaniciHatasi
from moe_bot.kaynakislem import aktifEkranBoyutu
from moe_bot.sabilter import CRED_PATH, GUI_LOGO_PATH, GUI_ICON_PATH, GUI_ENTRY_WIDTH

from moe_bot.sifremele import sifre_hash_olustur
from moe_bot.sunucu_islemleri import SunucuIslem, SunucuIslemSonucu


from tkinter import (
    BooleanVar,
    Checkbutton,
    LabelFrame,
    PhotoImage,
    Tk,
    Frame,
    Label,
    Entry,
    Button,
    messagebox,
)
from tkinter.ttk import Combobox
from enum import Enum, auto

from moe_bot.temel_siniflar import KaynakTipi, KullaniciGirisVerisi, Diller, DilEnum
from moe_bot.gunlukcu import gunlukcuGetir

multiprocessing.freeze_support()  # noqa # for pyinstaller
LOGGER = gunlukcuGetir(__name__)

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


class SelectibleModEnum(Enum):
    moe_gatherer = auto()
    # moe_raid = auto()
    # moe_camp = auto()
    # moe_arena = auto()


class GUIPagesEnum(Enum):
    LOGIN = auto()
    MOD_SELECT = auto()
    MOE_GATHERER = auto()


class ModEnum(Enum):
    MOE_GATHERER = auto()
    # MOE_RAID = auto()
    # MOE_CAMP = auto()
    # MOE_ARENA = auto()


class UnExpectedPageError(Exception):
    pass


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


class Moe_Gatherer_Page:
    def __init__(self, parent, window) -> None:
        self.parent = parent
        self.name = ModEnum.MOE_GATHERER
        try:
            aktifEkranBoyutu()  # eğer uygun değilse zaten hata fırlatır
        except KullaniciHatasi as exc:
            LOGGER.exception(f"Exception occured {exc}")
            _error_msgbx("gatherer_error_screen_resolution_error")
            self.parent.root.destroy()
            return

        self.parent.root.geometry("540x400")
        self.parent.change_title(Diller.lokalizasyon("window_title_gatherer"))
        self.frame = Frame(window, padx=15, pady=15, border=5)
        self.frame.pack(anchor="center")

        # -- warning top --

        self.warning_top_lbl = Label(
            self.frame,
            text=Diller.lokalizasyon("warning_top_lbl"),
            font="Verdana 18",
            fg="red",
        )
        # centered first row
        self.warning_top_lbl.grid(row=0, column=0)

        # -- warning top --
        self._fill_mid_frame()

        # -- warning bottom --
        self.warning_bottom_lbl = Label(
            self.frame,
            text=Diller.lokalizasyon("warning_bottom_lbl"),
            font="Verdana 14",
            fg="red",
        )
        # centered last row
        self.warning_bottom_lbl.grid(row=2, column=0)

    def _fill_mid_frame(self):
        self.mid_frame = Frame(self.frame, height=300)
        self.mid_frame.grid(row=1, column=0)
        self.mid_frame.grid_anchor("center")
        self.mid_frame.grid_columnconfigure((0, 1, 2), pad=10)
        self.mid_frame.grid_rowconfigure(0, pad=10)

        # mid left frame -> resource selection labelframe
        # mid center frame -> lvl selection labelframe
        # mid right frame -> right frame

        # -- resource selection --
        self.resource_selection_lbl = LabelFrame(
            self.mid_frame,
            text=Diller.lokalizasyon("resource_selection_lbl"),
            font="Verdana 12",
            width=160,
            height=300,
            pady=10,
            padx=10,
        )
        self.resource_selection_lbl.grid(
            row=0,
            column=0,
            sticky="w",
        )
        self.resource_selection_lbl.grid_propagate(False)

        self.resorce_variables = {
            KaynakTipi.EKMEK: BooleanVar(),
            KaynakTipi.ODUN: BooleanVar(),
            KaynakTipi.TAS: BooleanVar(),
            KaynakTipi.DEMIR: BooleanVar(),
            KaynakTipi.GUMUS: BooleanVar(),
            KaynakTipi.ALTIN: BooleanVar(),
        }

        localization = (
            "food",
            "wood",
            "stone",
            "iron",
            "silver",
            "gold",
        )

        self.resource_selection_checkbuttons = {
            resource: Checkbutton(
                self.resource_selection_lbl,
                onvalue=True,
                offvalue=False,
                text=Diller.lokalizasyon(localization[resource.value - 1]),
                variable=self.resorce_variables[resource],
            )
            for resource in self.resorce_variables
        }
        for i, resource in enumerate(self.resource_selection_checkbuttons):
            # self.resource_selection_checkbuttons[resource].grid(row=i, column=0, ipadx=25, ipady=2, sticky="w")
            if i == 0:
                self.resource_selection_checkbuttons[resource].grid(
                    row=i,
                    column=0,
                    sticky="w",
                    ipadx=15,
                    ipady=3,
                )
                continue
            self.resource_selection_checkbuttons[resource].grid(
                row=i,
                column=0,
                sticky="w",
                ipadx=15,
                ipady=3,
            )

        self.resource_select_all_chkbx_var = BooleanVar()
        self.resource_select_all_chkbx = Checkbutton(
            self.resource_selection_lbl,
            text=Diller.lokalizasyon("resource_select_all_chkbx"),
            font=("Verdana 10"),
            command=self.resource_select_all_command,
            variable=self.resource_select_all_chkbx_var,
        )
        self.resource_select_all_chkbx.grid(row=6, column=0, ipadx=15, ipady=20, pady=0, padx=0)
        # centered in last row of resource selection (6th row)
        # self.resource_select_all_chkbx.place(x=20, y=205, width=100, height=30)

        # -- resource selection --

        # -- lvl selection --

        self.lvl_selection_lbl = LabelFrame(
            self.mid_frame,
            text=Diller.lokalizasyon("lvl_selection_lbl"),
            font="Verdana 12",
            width=160,
            height=300,
            pady=10,
            padx=10,
        )
        self.lvl_selection_lbl.grid(row=0, column=1, sticky="w")
        self.lvl_selection_lbl.grid_propagate(False)

        self.lvl_selection_variables = [BooleanVar() for _ in range(1, 13)]

        self.lvl_selection_checkbuttons = {
            i: Checkbutton(
                self.lvl_selection_lbl,
                onvalue=True,
                offvalue=False,
                text=str(i),
                variable=self.lvl_selection_variables[i - 1],
                font=("Verdana 10"),
            )
            for i in range(1, len(self.lvl_selection_variables) + 1)
        }

        for i in range(1, len(self.lvl_selection_checkbuttons) + 1):
            if i < 7:
                self.lvl_selection_checkbuttons[i].grid(
                    row=i - 1,
                    column=0,
                    sticky="w",
                    ipadx=20,
                    ipady=3,
                )
            else:
                self.lvl_selection_checkbuttons[i].grid(
                    row=i - 7,
                    column=1,
                    sticky="w",
                    ipadx=0,
                    ipady=3,
                )

        self.lvl_select_all_chkbx_var = BooleanVar()
        self.lvl_select_all_chkbx = Checkbutton(
            self.lvl_selection_lbl,
            text=Diller.lokalizasyon("lvl_select_all_chkbx"),
            font=("Verdana 10"),
            command=self.lvl_select_all_command,
            variable=self.lvl_select_all_chkbx_var,
        )
        # centered in last row of lvl selection (6th row)
        self.lvl_select_all_chkbx.place(x=25, y=205, width=100, height=30)
        # self.lvl_select_all_chkbx.grid(ipadx=20, ipady=20, pady=0, padx=0)

        # -- lvl selection --

        # ------------- mid right frame -------------

        self.mid_right_frame = Frame(
            self.mid_frame,
            width=160,
            height=300,
        )

        self.mid_right_frame.grid(
            row=0,
            column=2,
            sticky="w",
        )
        # self.mid_right_frame.grid_columnconfigure(0, pad=10)
        self.mid_right_frame.grid_propagate(False)
        # ------------- mid right frame -------------

        # -- march selection --
        self.march_selection_lbl = LabelFrame(
            self.mid_right_frame,
            text=Diller.lokalizasyon("march_selection_lbl"),
            font="Verdana 12",
            height=120,
        )

        self.march_selection_lbl.grid(row=0, column=0)
        # self.march_selection_lbl.grid_propagate(False)

        self.march_selection_combo = Combobox(
            self.march_selection_lbl,
            state="readonly",
            values=[str(march_count) for march_count in range(1, 8)],
            width=5,
            height=7,
        )
        self.march_selection_combo.current(0)  # default value
        self.march_selection_combo.grid(row=1, column=1, padx=50, pady=5)
        # self.march_selection_combo.grid_propagate(False)

        # -- march selection --

        # -- moe logo --

        self.moe_logo_img = PhotoImage(file=LOGO_PATH, width=150, height=80)
        self.moe_logo_lbl = Label(
            self.mid_right_frame,
            text="moe_logo_lbl",
            image=self.moe_logo_img,
            width=150,
            height=80,
        )
        # centered in mid right frame (2nd row) ipadding y 20px
        self.moe_logo_lbl.grid(row=2, column=0, ipady=20)

        # -- moe logo --

        self.start_bot_btn = Button(
            self.mid_right_frame,
            width=10,
            height=1,
            font="Verdana 18",
            text=Diller.lokalizasyon("start_bot_btn"),
            bg="#62aade",
            command=self.clicked,
        )
        self.start_bot_btn.grid(row=4, column=0)

        self.exit_btn = Button(
            self.mid_right_frame,
            width=10,
            height=1,
            font="Verdana 18",
            text=Diller.lokalizasyon("exit_btn"),
            bg="#62aade",
            command=self.parent.root.destroy,
        )
        self.exit_btn.grid(row=5, column=0, pady=10)

    def resource_select_all_command(self):
        if self.resource_select_all_chkbx_var.get():
            for resource in self.resorce_variables:
                self.resource_selection_checkbuttons[resource].select()
            return
        for resource in self.resorce_variables:
            self.resource_selection_checkbuttons[resource].deselect()
        return

    def lvl_select_all_command(self):
        if self.lvl_select_all_chkbx_var.get():
            for lvl in self.lvl_selection_checkbuttons:
                self.lvl_selection_checkbuttons[lvl].select()
            return
        for lvl in self.lvl_selection_checkbuttons:
            self.lvl_selection_checkbuttons[lvl].deselect()
        return

    def get_settings(self) -> dict:
        if not any([self.resorce_variables[resource].get() for resource in self.resorce_variables]):
            LOGGER.debug("Kaynak seçimi yapılmadı. Hata mesajı gösteriliyor.")
            _error_msgbx("resource_selection_error")
            raise Hata(Diller.lokalizasyon("resource_selection_error", "UI"))

        if not any([self.lvl_selection_variables[lvl_num - 1].get() for lvl_num in range(1, len(self.lvl_selection_variables) + 1)]):
            LOGGER.debug("Seviye seçimi yapılmadı. Uyarı mesajı gösteriliyor.")
            _warning_msgbx("level_selection_warning")
            raise Hata(Diller.lokalizasyon("level_selection_warning", "UI"))

        return {
            "march_count": int(self.march_selection_combo.get()),
            "resources": [resource for resource in self.resorce_variables if self.resorce_variables[resource].get()],
            "lvls": [
                lvl_num
                for lvl_num in range(1, len(self.lvl_selection_variables) + 1)
                if self.lvl_selection_variables[lvl_num - 1].get()
            ],
        }
        pass

    def clicked(self):
        self.parent.make_interaction_variables_ready()


if __name__ == "__main__":
    root = Tk()
    # MainGui(root, "moe_auto_bot", "500x600")
    # root.attributes("-alpha", 0.95)
    # root.mainloop()
    main_gui = MainGui(root, "moe_auto_bot", "500x600")
    main_gui.pageshow = Moe_Gatherer_Page(main_gui, root)
    main_gui.mainloop()
