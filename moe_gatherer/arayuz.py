import logging
import os
from tkinter import BooleanVar, Button, Canvas, Checkbutton, IntVar, Label, LabelFrame, Tk, messagebox, ttk
from typing import Any


from .temel_siniflar import KaynakTipi
from .sabitler import BASE_PATH


class BotArayuz(Tk):
    def __init__(
        self,
        screenName: str | None = None,
        baseName: str | None = None,
        className: str = "Tk",
        useTk: bool = True,
        sync: bool = False,
        use: str | None = None,
    ) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.looger = logging.getLogger(__name__)

        self.resizable(False, False)
        self.title("MOE Toplama Botu By YnS & MSTF")
        self.iconbitmap(os.path.join(BASE_PATH, "arayuz/moe_icon.ico"))
        self.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.config(bg="white")
        # self.option_add('*Font', 'Verdana 13')
        self.option_add("*Dialog.msg.font", "Verdana 21")

        self.baslatma_basildi = False
        self.kaynak_durum = {
            KaynakTipi.EKMEK: BooleanVar(),
            KaynakTipi.ODUN: BooleanVar(),
            KaynakTipi.TAS: BooleanVar(),
            KaynakTipi.DEMIR: BooleanVar(),
            KaynakTipi.GUMUS: BooleanVar(),
            KaynakTipi.ALTIN: BooleanVar(),
        }

        kaynak_tum_durum = BooleanVar()

        self.seviye_durum_listesi = [BooleanVar() for _ in range(1, 13)]

        seviye_tum_durum = BooleanVar()

        self.sefer_durum = IntVar()

        def all_tip_sec():
            if kaynak_tum_durum.get() == 1:
                for kaynak_chkbx in chkbks_kaynak.values():
                    kaynak_chkbx.select()

            if kaynak_tum_durum.get() == 0:
                for kaynak_chkbx in chkbks_kaynak.values():
                    kaynak_chkbx.deselect()

        def all_seviye_sec():
            if seviye_tum_durum.get() == 1:
                for seviye_chkbx in svy_chkbks.values():
                    seviye_chkbx.select()

            if seviye_tum_durum.get() == 0:
                for seviye_chkbx in svy_chkbks.values():
                    seviye_chkbx.deselect()

        def buton_baslat():
            if self.sefer_durum.get() == 0:
                messagebox.showerror("Sefer sayisi hatali", "Sefer sayısı 0 olamaz")
                cmbx_sefersayisi.focus_set()
                return
            self.baslatma_basildi = True
            self.arayuz_degiskenleri = self._secenekleriGetir()
            self._on_exit()

        def buton_cikis():
            self.arayuz_degiskenleri = None
            self.quit()

        canvas = Canvas(self, height=390, width=530)
        canvas.pack()

        label_top = Label(self, text="LÜTFEN SEÇİMLERİNİZİ YAPINIZ", font="Verdana 14", foreground="RED")
        label_top.place(x=105, y=15)

        label_bottom = Label(self, text="7. sefer sadece Ekstra Sefer açıldığında çalışır.", font="Verdana 13", foreground="RED")
        label_bottom.place(x=65, y=355)

        frame_KaynakTipi = LabelFrame(self, text="Kaynak Tipi", font="Verdana 12")
        frame_KaynakTipi.place(x=20, y=60, width=160, height=287)

        chkbks_kaynak = {
            k: Checkbutton(
                frame_KaynakTipi, text=k.name.upper(), variable=self.kaynak_durum[k], onvalue=True, offvalue=False, font="Verdana 10"
            )
            for k in self.kaynak_durum.keys()
        }

        for i in range(len(chkbks_kaynak)):
            chkbks_kaynak[list(self.kaynak_durum.keys())[i]].place(x=20, y=20 + i * 30)

        chkbks_all_tip = Checkbutton(
            frame_KaynakTipi,
            text="HEPSİ",
            variable=kaynak_tum_durum,
            onvalue=True,
            offvalue=False,
            command=all_tip_sec,
            font="Verdana 10",
        )
        chkbks_all_tip.place(x=20, y=220)

        frame_KaynakSeviyesi = LabelFrame(self, text="Kaynak Seviye", font="Verdana 12")
        frame_KaynakSeviyesi.place(x=190, y=60, width=170, height=287)

        svy_chkbks = {
            i: Checkbutton(
                frame_KaynakSeviyesi,
                text=str(i),
                variable=self.seviye_durum_listesi[i - 1],
                onvalue=True,
                offvalue=False,
                font="Verdana 10",
            )
            for i in range(1, 13)
        }

        for i in range(len(svy_chkbks)):
            if i < 6:
                svy_chkbks[i + 1].place(x=25, y=20 + i * 30)
                continue
            svy_chkbks[i + 1].place(x=85, y=20 + ((i - 6) * 30))

        chkbks_all_seviye = Checkbutton(
            frame_KaynakSeviyesi,
            text="HEPSİ",
            variable=seviye_tum_durum,
            onvalue=True,
            offvalue=False,
            command=all_seviye_sec,
            font="Verdana 10",
        )
        chkbks_all_seviye.place(x=30, y=220)

        frame_SeferSayisi = LabelFrame(self, text="Sefer Sayısı", font="Verdana 12")
        frame_SeferSayisi.place(x=370, y=60, width=145, height=75)

        cmbx_sefersayisi = ttk.Combobox(
            frame_SeferSayisi,
            font="Verdana 10",
            state="readonly",
            values=["1", "2", "3", "4", "5", "6", "7"],
            textvariable=self.sefer_durum,
            width=10,
        )
        cmbx_sefersayisi.place(x=45, y=10, width=50)
        # FIXME geçici olarak yoruma alındı

        # resim_yl = "%s\\arayuz\\moe_logo.jpeg" % os.path.dirname(__file__)
        # resim_frame = Frame(self)

        # resim = ImageTk.PhotoImage(Image.open(fp=resim_yl))  # type: ignore
        # label = Label(resim_frame, image=resim)
        # label.place(height=resim.height(), width=resim.width())
        # # label.pack(side=tkinter.RIGHT)
        # resim_frame.place(x=370, y=190)
        # label.pack()

        buton_basla = Button(self, width=10, height=1, text="BAŞLAT", font="VERDANA 18", bg="#62aade", command=buton_baslat)
        buton_basla.place(x=370, y=180, width=145)

        buton_cikis_ = Button(self, width=145, height=1, text="ÇIKIŞ", font="VERDANA 18", bg="#62aade", command=buton_cikis)
        buton_cikis_.place(x=370, y=270, width=145)

    def _on_exit(self) -> bool:
        if not self.baslatma_basildi:
            self.arayuz_degiskenleri = None
        self.looger.debug("çıkış yapılıyor")
        self.destroy()
        return True

    def _secenekleriGetir(self) -> dict[str, Any]:
        secenekler = {"kaynak_tipleri": [], "svyler": [], "sefer_sayisi": 0}
        for k, v in self.kaynak_durum.items():
            if v.get():
                secenekler["kaynak_tipleri"].append(k)

        if len(secenekler["kaynak_tipleri"]) == 0:
            for k in self.kaynak_durum.keys():
                secenekler["kaynak_tipleri"].append(k)

        for indx, svy in enumerate(self.seviye_durum_listesi, start=1):
            if svy.get():
                secenekler["svyler"].append(indx)

        if len(secenekler["svyler"]) == 0:
            secenekler["svyler"] = [i for i in range(1, 13)]

        secenekler["sefer_sayisi"] = self.sefer_durum.get()

        return secenekler
