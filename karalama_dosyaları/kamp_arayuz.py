import os
from tkinter import (
    BooleanVar,
    Button,
    Checkbutton,
    IntVar,
    Label,
    LabelFrame,
    StringVar,
    Tk,
    Frame,
    Radiobutton,
    Entry,
    PhotoImage,
    Toplevel,
)
from tkinter.ttk import Combobox
import ayarlar

# from kamp_islem import calistir


class DosyaYolllari:
    directory_path = ".\\img\\_3840/"

    # Get list of all files in current directory
    directory = os.listdir(path=directory_path)


KAMP_ICON = DosyaYolllari.directory_path + "kamp_icon.png"


class MoeKampPage:
    def __init__(self, root_window: Tk) -> None:
        # root_window.geometry("700x500")  # "300x300" vs
        root_window.title("MOE KAMP")
        root_window.resizable(True, True)
        self.frame = Frame(root_window, padx=15, pady=15, border=5)
        self.frame.pack(anchor="center")
        self.arayuz_girdileri = {"onsvy": [], "mevsim": None, "saat": None, "dakika": None, "sefer": None}

        self.warning_top_lbl = Label(
            self.frame,
            text="SEÇİMLERİNİZİ YAPINIZ",
            font="Verdana 14",
            fg="red",
        )
        self.warning_top_lbl.grid(row=1, column=0)

        self._ortadoldur()

        self.warning_bottom_lbl = Label(
            self.frame,
            text="........",
            font="Verdana 14",
            fg="red",
        )
        # centered last row
        self.warning_bottom_lbl.grid(row=3, column=0)

        #####  RESİM EKLEME

        self.moe_icon = PhotoImage(file=KAMP_ICON)
        self.icon_label = Label(self.frame, text="moe_logo_lbl", image=self.moe_icon, width=707, height=346)
        self.icon_label.grid(row=0, column=0)

    def _ortadoldur(self):
        self.mid_frame = Frame(self.frame, height=300, width=750)
        self.mid_frame.grid(row=2, column=0)
        self.mid_frame.grid_anchor("center")
        self.mid_frame.grid_columnconfigure((0, 1), pad=10)
        self.mid_frame.grid_rowconfigure(0, pad=10)

        #########################################
        #          BUTONLAR
        #####################################

        self.second_frame = Frame(self.mid_frame, padx=15, pady=15, border=5, width=25)
        self.second_frame.grid(row=0, column=3)

        self.AyarlarButon = Button(
            self.second_frame,
            text="AYARLAR",
            command=lambda: self.ayarlar_penceresi(),
            width=11,
            height=1,
            bg="#3598D1",
            font="verdana 14",
        )
        self.AyarlarButon.grid(row=0, column=0)
        self.butonframe = Frame(self.mid_frame, padx=15, pady=15, border=5, width=100)
        self.butonframe.grid(row=1, column=3, sticky="s")
        self.butonframe.grid_anchor("center")

        self.BaslaButon = Button(
            self.butonframe,
            text="BAŞLA",
            command=self.baslaClick,
            width=11,
            height=1,
            bg="#3598D1",
            font="verdana 14",
        )
        self.BaslaButon.grid(row=0, column=0, sticky="e")
        self.boslabel1 = Label(self.butonframe, text="", height=1)
        self.boslabel1.grid(row=1, column=0)
        self.CikisButon = Button(
            self.butonframe,
            text="ÇIKIŞ",
            command="",
            width=11,
            height=1,
            bg="#3598D1",
            font="verdana 14",
        )
        self.CikisButon.grid(row=3, column=0)

        # *****************************************#
        #      ÖN SEVİYE SEÇİMLERİ                #
        # ******************************************
        self.onseviye_labelframe = LabelFrame(
            self.mid_frame,
            text="SEVİYE SEÇİMİ",
            font="12",
            labelanchor="n",
            width=160,
            height=300,
            pady=10,
            padx=10,
        )
        self.onseviye_labelframe.grid(row=0, column=0, sticky="s")
        self.onseviye_var_dict = {}
        self.onseviye_chbx_dict = {}
        for onsvy in ayarlar.OnSvyEnum:
            self.onseviye_var_dict[onsvy] = BooleanVar()
            self.onseviye_chbx_dict[onsvy] = Checkbutton(
                self.onseviye_labelframe,
                onvalue=True,
                offvalue=False,
                text=str(onsvy.value),
                font="12",
                variable=self.onseviye_var_dict[onsvy],
            )
            if onsvy.value < 5:
                self.onseviye_chbx_dict[onsvy].grid(row=0, column=onsvy.value, sticky="w", ipadx=5, ipady=3)
            else:
                self.onseviye_chbx_dict[onsvy].grid(row=1, column=onsvy.value - 4, sticky="w", ipadx=5, ipady=3)

        # *******************************************
        #             MEVSİM SEÇİMİ                #
        # ******************************************#

        self.mevsim_labelframe = LabelFrame(
            self.mid_frame,
            text="MEVSİM SEÇİNİZ",
            font="12",
            labelanchor="n",
        )
        self.mevsim_labelframe.grid(row=1, column=0)
        self.mevsim_int_var = IntVar()
        self.mevsim_radio_butonlari = []
        for mevsim in ayarlar.MevsimTipiEnum:
            self.mevsim_radio_butonlari.append(
                Radiobutton(
                    self.mevsim_labelframe,
                    value=mevsim.value,
                    text=mevsim.name,
                    font="12",
                    variable=self.mevsim_int_var,
                ).grid(row=0, column=mevsim.value, sticky="w", ipadx=5, ipady=3)
            )

        # *****************************************#
        #         ÇALIŞMA SÜRESİ                   #
        # ******************************************

        self.calisma_saati_frm = LabelFrame(
            self.mid_frame,
            text="ÇALIŞMA SÜRESİ",
            labelanchor="n",
        )
        self.calisma_saati_frm.grid(row=0, column=1)
        self.calisma_saat_lbl = Label(self.calisma_saati_frm, text="Saat", width=5, height=1)
        self.calisma_saat_lbl.grid(row=0, column=0, sticky="s", ipadx=5, ipady=3)
        entry_validate = self.frame.register(self.entry_kontrol)
        self.calisma_saati_ent = Entry(
            self.calisma_saati_frm,
            width=5,
            justify="center",
            validate="all",
            validatecommand=(entry_validate, "%P"),
        )
        self.calisma_saati_ent.grid(row=1, column=0, sticky="n", ipadx=5, ipady=3)
        self.calisma_dakika_lbl = Label(self.calisma_saati_frm, text="Dakika", width=5, height=1)
        self.calisma_dakika_lbl.grid(row=0, column=1, sticky="w", ipadx=5, ipady=3)
        self.calisma_dakika_ent = Entry(
            self.calisma_saati_frm,
            width=5,
            justify="center",
            validate="all",
            validatecommand=(entry_validate, "%P"),
        )
        self.calisma_dakika_ent.grid(row=1, column=1, sticky="w", ipadx=5, ipady=3)

        ####  ALTTAN VE SAĞDAN BOŞLUK BIRAKMAYI DÜZENLEYEBİLMEK İÇİN BOŞ LABEL EKLENDİ
        self.sagbosluk_lbl = Label(self.calisma_saati_frm, text=" ", width=2)
        self.sagbosluk_lbl.grid(row=3, column=3, sticky="e", ipadx=5, ipady=3)
        self.altbosluk_lbl = Label(self.calisma_saati_frm, text=" ", width=10)
        self.altbosluk_lbl.grid(row=3, column=0, sticky="n", ipadx=5, ipady=3)

        ########
        self.mid_sep_frame = Label(self.mid_frame, text="", width=1, bg="black")
        self.mid_sep_frame.grid(row=1, column=1)

        # *****************************************#
        #         SEFER SAYISI SEÇİMİ              #
        # ******************************************
        self.sefer_secimi_labelframe = LabelFrame(
            self.mid_frame,
            text="SEFER SAYISI",
            labelanchor="n",
        )
        self.sefer_secimi_labelframe.grid(row=1, column=1)
        self.sefer_ust_bosluk_lbl = Label(self.sefer_secimi_labelframe, text="", width=5)
        self.sefer_ust_bosluk_lbl.grid(row=0, column=0, ipadx=5, ipady=3)
        self.sefer_sayisi_cmb = Combobox(
            self.sefer_secimi_labelframe,
            state="readonly",
            values=(1, 2, 3, 4, 5, 6),
            width=2,
        )
        self.sefer_sayisi_cmb.grid(row=1, column=1, sticky="ne", ipadx=5, ipady=3)
        self.sefer_alt_bosluk_lbl = Label(self.sefer_secimi_labelframe, text="", width=4)
        self.sefer_alt_bosluk_lbl.grid(row=2, column=1, ipadx=5, ipady=3)
        self.sefer_sol_bosluk_lbl = Label(self.sefer_secimi_labelframe, text="", width=6)
        self.sefer_sol_bosluk_lbl.grid(row=1, column=0, ipadx=5, ipady=3)
        self.sefer_sag_bosluk_lbl = Label(self.sefer_secimi_labelframe, text="", width=5)
        self.sefer_sag_bosluk_lbl.grid(row=1, column=2, ipadx=5, ipady=3)

    def entry_kontrol(self, P: str) -> bool:
        return str.isdigit(P)

    def ayarlar_penceresi(self):
        child_ayarlar = Toplevel(root)
        child_ayarlar.title = "Ayarlar"
        child_ayarlar.geometry("640x480")
        self.ayarlar_lbl_frame = LabelFrame(child_ayarlar, text="AYARLAR", labelanchor="nw", width=635, height=400)
        self.ayarlar_lbl_frame.grid(row=1, column=0, ipadx=10, padx=20, pady=10)

        self.sure_ayarlari_lbl_frm = LabelFrame(child_ayarlar, text="SÜRE AYARLARI", labelanchor="nw")
        self.sure_ayarlari_lbl_frm.grid(row=2, column=0, ipadx=10, padx=20, pady=10)

        self.kaydet_btn = Button(
            child_ayarlar,
            text="KAYDET",
            command="",
            width=11,
            height=1,
            bg="#3598D1",
            font="verdana 14",
        )
        self.kaydet_btn.grid(row=4, column=0, padx=10, pady=10)

        self.ayarlar_listesi_frm = Frame(self.ayarlar_lbl_frame, width=150, height=75)
        self.ayarlar_listesi_frm.grid(row=0, column=0, ipadx=3, ipady=3)

        self.bos_frm = Frame(self.ayarlar_listesi_frm, width=10)
        self.bos_frm.grid(row=0, column=1, ipadx=3, ipady=3)

        self.rd_alani1_frm = Frame(self.ayarlar_lbl_frame, width=150, height=75)
        self.rd_alani1_frm.grid(row=0, column=2, ipadx=3, ipady=3)

        self.bos2_frm = Frame(self.ayarlar_lbl_frame, width=10)
        self.bos2_frm.grid(row=0, column=3, ipadx=3, ipady=3)

        self.rd_alani2_frm = Frame(self.ayarlar_lbl_frame, width=10)
        self.rd_alani2_frm.grid(row=0, column=4, ipadx=3, ipady=3)

        self.isinlanma_tipi_lbl = Label(self.ayarlar_listesi_frm, text="Işınlanma Tipi")
        self.isinlanma_tipi_lbl.grid(row=0, column=0, padx=3, pady=3)
        self.harita_tarama_lbl = Label(self.ayarlar_listesi_frm, text="Harita Tarama Tipi")
        self.harita_tarama_lbl.grid(row=1, column=0, ipadx=3, ipady=3)
        self.enerji_biterse_lbl = Label(self.ayarlar_listesi_frm, text="Enerji Bittiğinde Dur")
        self.enerji_biterse_lbl.grid(row=2, column=0, ipadx=3, ipady=3)

        self.bos_lbl = Label(self.bos_frm, text="", width=10)
        self.bos_lbl.grid(row=0, column=1, ipadx=3, ipady=3)

        isin_secenek = StringVar()
        self.isin_koordinat_rd = Radiobutton(
            self.rd_alani1_frm,
            text="Koordinat",
            variable=isin_secenek,
            value="koord_i",
        )
        self.isin_koordinat_rd.grid(row=0, column=0, ipadx=3, ipady=3, sticky="w")
        self.isin_rastgele_rd = Radiobutton(
            self.rd_alani2_frm,
            text="Rastgele",
            variable=isin_secenek,
            value="rast_i",
        )
        self.isin_rastgele_rd.grid(row=0, column=0, ipadx=3, ipady=3, sticky="e")

        enerji_secenek = StringVar()
        self.enerji_bitti_rd = Radiobutton(
            self.rd_alani1_frm,
            text="Evet",
            variable=enerji_secenek,
            value="e_bitti",
        )
        self.enerji_bitti_rd.grid(row=2, column=0, ipadx=3, ipady=3, sticky="w")

        self.enerji_bitmedi_rd = Radiobutton(
            self.rd_alani2_frm,
            text="Hayır",
            variable=enerji_secenek,
            value="e_bitmedi",
        )
        self.enerji_bitmedi_rd.grid(row=2, column=0, ipadx=3, ipady=3, sticky="w")

        self.bos2_lbl = Label(self.bos2_frm, text="", width=10)
        self.bos2_lbl.grid(row=0, column=0, ipadx=3, ipady=3)

        tarama_secenek = StringVar()
        self.harita_tarama_rd = Radiobutton(
            self.rd_alani1_frm,
            text="Duz",
            variable=tarama_secenek,
            value="tarama_duz",
        )
        self.harita_tarama_rd.grid(row=1, column=0, ipadx=3, ipady=3)
        self.harita_tarama2_rd = Radiobutton(
            self.rd_alani2_frm,
            text="Yildiz",
            variable=tarama_secenek,
            value="tarama_yildiz",
        )
        self.harita_tarama2_rd.grid(row=1, column=0, ipadx=3, ipady=3)

        self.kamp_cikis_saati_frm = LabelFrame(
            self.sure_ayarlari_lbl_frm,
            text="Yeni Kamp Çıkış Saati",
            labelanchor="n",
        )
        self.kamp_cikis_saati_frm.grid(row=0, column=0, padx=10, pady=10)
        self.kamp_saat_lbl = Label(self.kamp_cikis_saati_frm, text="Saat", width=5, height=1)
        self.kamp_saat_lbl.grid(row=0, column=0, sticky="s", ipadx=5, ipady=3)
        entry_validate = self.frame.register(self.entry_kontrol)

        self.kamp_saati_ent = Entry(
            self.kamp_cikis_saati_frm,
            width=5,
            justify="center",
            validate="all",
            validatecommand=(entry_validate, "%P"),
        )
        self.kamp_saati_ent.grid(row=1, column=0, sticky="n", ipadx=5, ipady=3)
        self.kamp_dakika_lbl = Label(self.kamp_cikis_saati_frm, text="Dakika", width=5, height=1)
        self.kamp_dakika_lbl.grid(row=0, column=1, sticky="w", ipadx=5, ipady=3)
        self.kamp_dakika_ent = Entry(
            self.kamp_cikis_saati_frm,
            width=5,
            justify="center",
            validate="all",
            validatecommand=(entry_validate, "%P"),
        )
        self.kamp_dakika_ent.grid(row=1, column=1, sticky="w", ipadx=5, ipady=3)

        ####  ALTTAN VE SAĞDAN BOŞLUK BIRAKMAYI DÜZENLEYEBİLMEK İÇİN BOŞ LABEL EKLENDİ
        self.sagbosluk_lbl = Label(self.kamp_cikis_saati_frm, text=" ", width=2)
        self.sagbosluk_lbl.grid(row=3, column=3, sticky="e", ipadx=5, ipady=3)
        self.altbosluk_lbl = Label(self.kamp_cikis_saati_frm, text=" ", width=10)
        self.altbosluk_lbl.grid(row=3, column=0, sticky="n", ipadx=5, ipady=3)

        self.yeni_kamp_calisma_saati_frm = LabelFrame(
            self.sure_ayarlari_lbl_frm,
            text="Yeni Kamp Çalışma",
            labelanchor="n",
        )
        self.yeni_kamp_calisma_saati_frm.grid(row=0, column=1)
        self.yeni_kamp_calisma_saat_lbl = Label(self.yeni_kamp_calisma_saati_frm, text="Saat", width=5, height=1)
        self.yeni_kamp_calisma_saat_lbl.grid(row=0, column=0, sticky="s", ipadx=5, ipady=3)
        entry_validate = self.frame.register(self.entry_kontrol)
        self.yeni_kamp_calisma_saati_ent = Entry(
            self.yeni_kamp_calisma_saati_frm,
            width=5,
            justify="center",
            # validate="all",
            # validatecommand=(entry_validate, "%P"),
        )
        self.yeni_kamp_calisma_saati_ent.grid(row=1, column=0, sticky="n", ipadx=5, ipady=3)
        self.yeni_kamp_calisma_dakika_lbl = Label(self.yeni_kamp_calisma_saati_frm, text="Dakika", width=5, height=1)
        self.yeni_kamp_calisma_dakika_lbl.grid(row=0, column=1, sticky="w", ipadx=5, ipady=3)
        self.yeni_kamp_calisma_dakika_ent = Entry(
            self.yeni_kamp_calisma_saati_frm,
            width=5,
            justify="center",
            # validate="all",
            # validatecommand=(entry_validate, "%P"),
        )
        self.yeni_kamp_calisma_dakika_ent.grid(row=1, column=1, sticky="w", ipadx=5, ipady=3)

        ####  ALTTAN VE SAĞDAN BOŞLUK BIRAKMAYI DÜZENLEYEBİLMEK İÇİN BOŞ LABEL EKLENDİ
        self.sagbosluk_lbl = Label(self.yeni_kamp_calisma_saati_frm, text=" ", width=2)
        self.sagbosluk_lbl.grid(row=3, column=3, sticky="e", ipadx=5, ipady=3)
        self.altbosluk_lbl = Label(self.yeni_kamp_calisma_saati_frm, text=" ", width=10)
        self.altbosluk_lbl.grid(row=3, column=0, sticky="n", ipadx=5, ipady=3)

        ########
        # self.mid_sep_frame = Label(self.mid_frame, text="", width=1, bg="black")
        # self.mid_sep_frame.grid(row=1, column=1)

        # self.kaydirma_frame = Frame(ayarlar_lbl_frame, width=400, height=75)
        # self.kaydirma_frame.grid(row=0, column=0, ipadx=3, ipady=3)

        # self.lbl_kaydirma_hizi = Label(baslik_frame, text="Kaydırma Hızı")
        # self.lbl_kaydirma_hizi.grid(row=0, column=0, ipadx=3, ipady=3)

        # self.yeni_kampta_vur_lbl = Label(baslik_frame, text="Sadece Yeni Kapmlarda Çalıştır")
        # self.yeni_kampta_vur_lbl.grid(row=2, column=0, ipadx=3, ipady=3)

        # self.lbl_yeni_kamp_sonrasi_oyunu_kapat = Label(baslik_frame, text="Kamplar Yeni Çıktığında Oyından Çıkış")
        # self.lbl_yeni_kamp_sonrasi_oyunu_kapat.grid(row=3, column=0, ipadx=3, ipady=3)

    def baslaClick(self):
        self.arayuz_girdileri["onsvy"].clear()
        self.arayuz_girdileri["mevsim"] = None
        self.arayuz_girdileri["saat"] = None
        self.arayuz_girdileri["dakika"] = None
        self.arayuz_girdileri["sefer"] = None
        for onseviye_var_key, onseviye_var_val in self.onseviye_var_dict.items():
            if onseviye_var_val.get():
                self.arayuz_girdileri["onsvy"].append(onseviye_var_key)

        self.arayuz_girdileri["mevsim"] = ayarlar.MevsimTipiEnum(self.mevsim_int_var.get())
        self.arayuz_girdileri["saat"] = self.calisma_saati_ent.get()
        self.arayuz_girdileri["dakika"] = self.calisma_dakika_ent.get()

        self.arayuz_girdileri["sefer"] = self.sefer_sayisi_cmb.get()
        # TODO: ayarlar penceresindeki ayarlada eknecek

        self.frame.quit()


if __name__ == "__main__":
    root = Tk()
    mok_page = MoeKampPage(root)
    root.mainloop()
    print(mok_page.arayuz_girdileri)
