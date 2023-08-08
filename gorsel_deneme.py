from moe_gatherer.kaynakislem import DosyaIslemleri, Tarayici, taramaBolgesiGetir


def main():
    ad = "geri_ok"
    d_yl = DosyaIslemleri.gorselGetir(ad)
    # eminlik = eminlikGetir(ad)
    bolge = taramaBolgesiGetir(ad)
    eminlik = 0.8
    # bolge = Kare(0, 0, 500, 500)
    tarayici = Tarayici(ornek_d=d_yl, eminlik=eminlik, bolge=bolge, gri_tarama=True)
    tarayici_kare = tarayici.ekranTara()
    if tarayici_kare is not None:
        print("buldum: ")
        print(tarayici_kare)
    else:
        print("bulamadim")


if __name__ == "__main__":
    main()
