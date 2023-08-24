from __future__ import annotations
from dataclasses import dataclass

from tkinter import Tk, Canvas, Label, Entry, StringVar

import multiprocessing

multiprocessing.freeze_support()


@dataclass
class KullaniciVerisi:
    name: str
    password_hash: str


# def btn_giris():
#     pass


# def btn_cikis():
#     main.quit()


# text_kullaniciadi = StringVar()

# text_sifre = StringVar()

# canvas = Canvas(main, bg="light blue", height=220, width=300)

# canvas.pack()


# labetl_top1 = Label(
#     main,
#     text="MOE Toplama Botu",
#     font="verdana, 13",
#     bg="light blue",
# )

# labetl_top1.place(x=80, y=20)


# labetl_top2 = Label(
#     main,
#     text="By YnS & MSTF",
#     font="verdana, 13",
#     bg="light blue",
# )

# labetl_top2.place(x=90, y=50)


# label_kullaniciadi = Label(main, bg="light blue", text="Kullanıcı Adı:", font="verdana 11")

# label_kullaniciadi.place(x=30, y=95)

# entry_kullaniciadi = Entry(main, textvariable=text_kullaniciadi)

# entry_kullaniciadi.place(x=130, y=95)


# label_sifre = Label(main, bg="light blue", text="Şifre:", font="verdana 11")

# label_sifre.place(x=80, y=135)

# entry_sifre = Entry(main, textvariable=text_sifre, show="*")

# entry_sifre.place(x=130, y=135)


# btn_cikis = Button(main, text="İptal Et", width=10, bg="light blue", font="verdana 11 bold", command=btn_cikis)

# btn_cikis.place(x=25, y=180)


# btn_giris = Button(main, text="Giriş", width=10, bg="light blue", font="verdana 11 bold", command=btn_giris)

# btn_giris.place(x=165, y=180)


# main.mainloop()


class KullaniciGirisi(object):
    def __new__(cls, *args, **kwargs) -> KullaniciGirisi:
        if not hasattr(cls, "instance"):
            cls.instance = super(KullaniciGirisi, cls).__new__(cls)
            cls.instance._init_(*args, **kwargs)
        return cls.instance

    def __init__(
        self, title="Kullanıcı Girişi", width=300, height=220, varsayilan_entry_degerleri: dict[str, str] | None = None
    ) -> None:
        return self.__new__(title, width, height, varsayilan_entry_degerleri)

    def _init_(
        self, title="Kullanıcı Girişi", width=300, height=220, varsayilan_entry_degerleri: dict[str, str] | None = None
    ) -> None:
        self.main_w = Tk()
        self.main_w.resizable(False, False)
        self.main_w.title(title)
        self.main_w.eval("tk::PlaceWindow . center")

        self._create_gui(width, height, varsayilan_entry_degerleri)

    def _create_gui(self, width, height, varsayilan_entry_degerleri):
        self.canvas = Canvas(self.main_w, bg="light blue", height=220, width=300)
        self.canvas.pack()

        self.labetl_top1 = Label(
            self.main_w,
            text="MOE Toplama Botu",
            font="verdana, 13",
            bg="light blue",
        )

        self.labetl_top1.place(x=80, y=20)

        self.labetl_top2 = Label(
            self.main_w,
            text="By YnS & MSTF",
            font="verdana, 13",
            bg="light blue",
        )

        self.labetl_top2.place(x=90, y=50)

        self.label_kullaniciadi = Label(self.main_w, bg="light blue", text="Kullanıcı Adı:", font="verdana 11")
        self.label_kullaniciadi.place(x=30, y=95)

        text_kullaniciadi = StringVar()

        if varsayilan_entry_degerleri:
            text_kullaniciadi = StringVar(value=varsayilan_entry_degerleri["kullaniciadi"])
        self.entry_kullaniciadi = Entry(self.main_w, textvariable=text_kullaniciadi)


if __name__ == "__main__":
    "this is only for testing"
    main = KullaniciGirisi(title="deneme Kullanıcı Girişi deneme")
    main.main_w.mainloop()
