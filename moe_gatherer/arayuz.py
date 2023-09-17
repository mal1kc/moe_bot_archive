from __future__ import annotations
import multiprocessing

from moe_gatherer.hatalar import BaglantiHatasi, Hata

from moe_gatherer.sifremele import sifre_hash_olustur
from moe_gatherer.sunucu_islemleri import SunucuIslem, SunucuIslemSonucu


from tkinter import BooleanVar, Checkbutton, LabelFrame, PhotoImage, Tk, Frame, Label, Entry, Button, messagebox
from tkinter.ttk import Combobox
from enum import Enum, auto

from moe_gatherer.temel_siniflar import KaynakTipi, KullaniciGirisVerisi
from moe_gatherer.gunlukcu import gunlukcuGetir
from moe_gatherer.lokalizasyon import DilEnum, DilSabitleri, lokalizasyon

multiprocessing.freeze_support()  # noqa # for pyinstaller
LOGGER = gunlukcuGetir(__name__)

# TODO : ayarlardan al
LOGO_PATH = "./arayuz/moe_logo.png"

ENTRY_WIDTH = 30


def _error_msgbx(error: str) -> None:
    messagebox.showerror(lokalizasyon("msgbx_error_title"), lokalizasyon(error))


def _warning_msgbx(warning: str) -> None:
    messagebox.showwarning(lokalizasyon("msgbx_warning_title"), lokalizasyon(warning))


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

    def __init__(self, root: Tk | None = None, title: str = "moe_auto_bot", geometry: str = "500x600"):
        if root is None:
            root = Tk()
        self.root = root
        self.root.title(title)
        self.root.resizable(False, False)
        self.root.geometry(geometry)
        self.pageshow = Login_Page(self, self.root)
        self.interaction_variables = {}

    def change_page(self, page: GUIPagesEnum):
        self.page = page

        if self.page == GUIPagesEnum.MOD_SELECT:
            # del self.pageshow
            self.pageshow = Mod_Select_Page(self, self.root)

        elif self.page == GUIPagesEnum.MOE_GATHERER:
            # del self.pageshow
            self.pageshow = Moe_Gatherer_Page(self, self.root)

    def make_interaction_variables_ready(self) -> None:
        if isinstance(self.pageshow.name, ModEnum):
            try:
                self.interaction_variables = {
                    "mod_name": self.pageshow.name,
                    "mod_settings": self.pageshow.get_settings(),  # type: ignore
                }
            except Hata as exc:
                LOGGER.exception(f"Exception occured {exc} while getting settings for {self.pageshow.name=}")
                return
            print(self.interaction_variables)
            self.root.destroy()
            return
        raise UnExpectedPageError("Unexpected page")

    def mainloop(self):
        self.root.mainloop()


class Login_Page:
    def __init__(self, parent, window):
        self.parent = parent
        self.name = GUIPagesEnum.LOGIN
        self.window = window
        # change size of window to 360x140
        self.parent.root.geometry("360x140")

        self._init_frame()

    def _init_frame(self):
        # -- language selection --
        self.frame = Frame(self.window)
        self.frame.pack()
        self.select_lang_lbl = Label(self.frame, text=lokalizasyon("select_lang_lbl"))
        self.select_lang_lbl.grid(row=3, column=0)

        self.select_lang_combo = Combobox(self.frame, values=[lokalizasyon(lang.name) for lang in DilEnum], state="readonly")
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

        self.login_lbl = Label(self.frame, text=lokalizasyon("login_lbl"))
        self.login_lbl.grid(row=0, column=1)

        self.name_lbl = Label(self.frame, text=lokalizasyon("name_lbl"), anchor="e", width=ENTRY_WIDTH // 2)
        self.name_lbl.grid(row=1, column=0)

        self.name_entry = Entry(self.frame, width=ENTRY_WIDTH)
        self.name_entry.bind("<Return>", _focus_next_widget)
        self.name_entry.grid(row=1, column=1)

        self.pass_lbl = Label(self.frame, text=lokalizasyon("pass_lbl"), width=ENTRY_WIDTH // 2, anchor="e")
        self.pass_lbl.grid(row=2, column=0)

        self.pass_entry = Entry(self.frame, width=ENTRY_WIDTH, show="*")
        self.pass_entry.bind("<Return>", _focus_next_widget)
        self.pass_entry.grid(row=2, column=1)

        self.sbt = Button(self.frame, text=lokalizasyon("login_btn"), command=self.clicked)
        self.sbt.bind("<Return>", _press_btn)
        self.sbt.grid(row=4, column=1)

        # -- login --

    def _lang_changed(self, event) -> None:
        # update language

        DilSabitleri.aktifi_dil_degistir(DilEnum[self.select_lang_combo.get()])
        self.name_lbl.config(text=lokalizasyon("name_lbl"))
        self.pass_lbl.config(text=lokalizasyon("pass_lbl"))
        self.sbt.config(text=lokalizasyon("login_btn"))
        self.select_lang_lbl.config(text=lokalizasyon("select_lang_lbl"))
        self.login_lbl.config(text=lokalizasyon("login_lbl"))

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
            if (giris_sonucu := self.sunucu_islem.giris_yap()) == SunucuIslemSonucu.BASARILI:
                # TODO: sadece kullanicinin sahip oldugu modlari goster
                self.frame.destroy()
                self.parent.change_page(GUIPagesEnum.MOD_SELECT)
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
            # TODO: bilinmeyen hata mesaji goster
            _error_msgbx("login_error_unknown_error")


class Mod_Select_Page:
    def __init__(self, parent, window) -> None:
        self.parent = parent
        self.name = GUIPagesEnum.MOD_SELECT

        # change size of window to 200x100
        self.parent.root.geometry("200x100")

        self.main_frame = Frame(window)
        self.main_frame.pack()

        self.mod_select_lbl = Label(self.main_frame, text="mod_select_lbl")
        self.mod_select_lbl.grid(row=0, column=1)

        self.mod_selection_combo = Combobox(
            self.main_frame, state="readonly", values=[lokalizasyon(module.name) for module in SelectibleModEnum]
        )
        self.mod_selection_combo.current(0)  # default value moe_gatherer
        self.mod_selection_combo.grid(row=1, column=1)

        self.mod_select_continue_btn = Button(self.main_frame, text=lokalizasyon("mod_select_continue_btn"), command=self.clicked)
        self.mod_select_continue_btn.grid(row=2, column=1)

    def clicked(self):
        self.main_frame.destroy()
        # TODO: go to selected mod page
        self.parent.change_page(GUIPagesEnum.MOE_GATHERER)


class Moe_Gatherer_Page:
    def __init__(self, parent, window) -> None:
        self.parent = parent
        self.name = ModEnum.MOE_GATHERER

        # change size of window to 580x380
        self.parent.root.geometry("580x380")

        self.main_frame = Frame(window, padx=10, pady=10)
        self.main_frame.pack()

        self.moe_logo_img = PhotoImage(file=LOGO_PATH, width=148, height=78)
        self.moe_logo_lbl = Label(
            self.main_frame,
            text="moe_logo_lbl",
            image=self.moe_logo_img,
        )
        self.moe_logo_lbl.grid(row=0, column=0)
        # -- march selection --

        self.march_select_lbl = LabelFrame(
            self.main_frame, text=lokalizasyon("march_select_lbl"), height=100, width=100, padx=10, pady=10
        )
        self.march_select_lbl.grid(row=0, column=1)

        self.march_selection_combo = Combobox(
            self.march_select_lbl, state="readonly", values=[str(march_count) for march_count in range(1, 8)]
        )
        self.march_selection_combo.current(0)  # default value
        self.march_selection_combo.grid(row=0, column=0)

        # -- resource selection --
        self.resource_selection_lbl = LabelFrame(
            self.main_frame, text=lokalizasyon("resource_selection_lbl"), height=100, width=100, padx=10, pady=10
        )
        self.resource_selection_lbl.grid(row=1, column=0)

        self.resorce_variables = {
            KaynakTipi.EKMEK: BooleanVar(),
            KaynakTipi.ODUN: BooleanVar(),
            KaynakTipi.TAS: BooleanVar(),
            KaynakTipi.GUMUS: BooleanVar(),
            KaynakTipi.DEMIR: BooleanVar(),
            KaynakTipi.ALTIN: BooleanVar(),
        }

        self.resource_selection_checkbuttons = {
            resource: Checkbutton(
                self.resource_selection_lbl,
                onvalue=True,
                offvalue=False,
                text=lokalizasyon(resource.name),
                variable=self.resorce_variables[resource],
            )
            for resource in self.resorce_variables
        }
        for i, resource in enumerate(self.resource_selection_checkbuttons):
            self.resource_selection_checkbuttons[resource].grid(row=i, column=0)

        self.resource_select_all_btn = Button(
            self.resource_selection_lbl, text=lokalizasyon("resource_select_all_btn"), command=self.resource_select_all_clicked
        )
        self.resource_select_all_btn.grid(row=len(self.resorce_variables), column=0)

        self.resource_select_none_btn = Button(
            self.resource_selection_lbl, text=lokalizasyon("resource_select_none_btn"), command=self.resource_select_none_clicked
        )
        self.resource_select_none_btn.grid(row=len(self.resorce_variables) + 1, column=0)

        # -- resource selection --

        # -- lvl selection --

        self.lvl_select_lbl = LabelFrame(self.main_frame, text=lokalizasyon("lvl_select_lbl"), height=100, width=100, padx=10, pady=10)
        self.lvl_select_lbl.grid(sticky="E", row=1, column=1, padx=10, pady=10, ipadx=10, ipady=10)

        self.lvl_selection_variables = [BooleanVar() for _ in range(1, 13)]

        self.lvl_selection_checkbuttons = {
            i: Checkbutton(
                self.lvl_select_lbl,
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
                self.lvl_selection_checkbuttons[i].grid(row=i - 1, column=0)
            else:
                self.lvl_selection_checkbuttons[i].grid(row=i - 7, column=1)

        self.lvl_select_all_btn = Button(
            self.lvl_select_lbl, text=lokalizasyon("lvl_select_all_btn"), command=self.lvl_select_all_clicked
        )
        self.lvl_select_all_btn.grid(row=6, column=0)
        self.lvl_select_all_btn = Button(
            self.lvl_select_lbl, text=lokalizasyon("lvl_select_none_btn"), command=self.lvl_select_none_clicked
        )
        self.lvl_select_all_btn.grid(row=6, column=1)

        # -- lvl selection --

        # -- close gui btn --

        self.close_gui_btn = Button(self.main_frame, text=lokalizasyon("close_gui_btn"), command=self.clicked)
        self.close_gui_btn.grid(row=1, column=2)

    def resource_select_all_clicked(self):
        for resource in self.resorce_variables:
            self.resource_selection_checkbuttons[resource].select()

    def resource_select_none_clicked(self):
        for resource in self.resorce_variables:
            self.resource_selection_checkbuttons[resource].deselect()

    def lvl_select_all_clicked(self):
        for lvl in self.lvl_selection_checkbuttons:
            self.lvl_selection_checkbuttons[lvl].select()

    def lvl_select_none_clicked(self):
        for lvl in self.lvl_selection_checkbuttons:
            self.lvl_selection_checkbuttons[lvl].deselect()

    def get_settings(self) -> dict:
        # check if is there any resource selected if not raise error
        if not any([self.resorce_variables[resource].get() for resource in self.resorce_variables]):
            LOGGER.debug("Kaynak seçimi yapılmadı. Hata mesajı gösteriliyor.")
            _error_msgbx("resource_selection_error")
            raise Hata("Kaynak seçimi yapılmadı.")

        # check if is there any lvl selected if not show warning
        if not any([self.lvl_selection_variables[lvl_num - 1].get() for lvl_num in range(1, len(self.lvl_selection_variables) + 1)]):
            LOGGER.debug("Seviye seçimi yapılmadı. Uyarı mesajı gösteriliyor.")
            _warning_msgbx("level_selection_warning")
            self.lvl_select_all_clicked()
        return {
            "march_count": str(self.march_selection_combo.get()),
            "resources": [resource for resource in self.resorce_variables if self.resorce_variables[resource].get()],
            "lvls": [
                lvl_num
                for lvl_num in range(1, len(self.lvl_selection_variables) + 1)
                if self.lvl_selection_variables[lvl_num - 1].get()
            ],
        }

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
