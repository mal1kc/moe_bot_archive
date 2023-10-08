from moe_bot.kaynakislem import DosyaIslemleri, Tarayici, eminlikGetir, taramaBolgesiGetir
from moe_bot.temel_siniflar import Kare


def main():
    ad = "hizmet_basarisiz"
    d_yl = DosyaIslemleri.gorselGetir(ad)
    eminlik = eminlikGetir(ad)
    bolge = taramaBolgesiGetir(ad)
    # eminlik = 0.8
    bolge = Kare(1750, 500, 300, 300)
    tarayici = Tarayici(ornek_d=d_yl, eminlik=eminlik, bolge=bolge, gri_tarama=True)
    tarayici_kare = tarayici.ekranTara()
    if tarayici_kare is not None:
        print("buldum: ")
        print(tarayici_kare)
    else:
        print("bulamadim")


if __name__ == "__main__":
    main()
