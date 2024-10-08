from __future__ import annotations

import logging
import sys
from tkinter import BooleanVar, Button, Checkbutton, Frame, Label, LabelFrame, PhotoImage
from tkinter.ttk import Combobox

from moe_bot.arayuz_temel import LOGO_PATH, _error_msgbx, _warning_msgbx
from moe_bot.enumlar import ModEnum
from moe_bot.hatalar import Hata, KullaniciHatasi
from moe_bot.mod.moe_gatherer_islem import KaynakTipi
from moe_bot.temel_fonksiyonlar import aktifEkranBoyutu
from moe_bot.temel_siniflar import Diller

LOGGER = logging.getLogger(__name__)


class Moe_Gatherer_Page:
    def __init__(self, parent, window) -> None:
        self.parent = parent
        self.name = ModEnum.MOE_GATHERER
        try:
            aktifEkranBoyutu()  # eğer uygun değilse zaten hata fırlatır
        except KullaniciHatasi as exc:
            LOGGER.exception(f"Exception occured {exc}")
            _error_msgbx("gatherer_error_screen_resolution_error")
            try:
                self.parent.root.destroy()
            except Exception as exc:
                LOGGER.exception(f"Exception occured {exc}")
                sys.exit(1)
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
