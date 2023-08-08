class DenemeSınıfı:
    def __init__(self, overrideEdilecekFonksiyon=None) -> None:
        if overrideEdilecekFonksiyon is not None:
            print("override edilecek fonksiyon değiştirildi")
            self.overrideEdilecekFonksiyon = overrideEdilecekFonksiyon
        print(f"{id(self)} deneme sınıfı oluşturuldu")

    def overrideEdilecekFonksiyon(self):
        """
        override edilecek fonksiyon
        """
        print("override edilecek fonksiyon çalıştı")


if __name__ == "__main__":

    def merhabaDunya():
        """
        merhaba dünya yazdırır
        """
        print("merhaba dünya")

    denemeSınıfı = DenemeSınıfı()
    denemeSınıfı2 = DenemeSınıfı(merhabaDunya)

    print(
        "deneme sınıfı override edilecek fonksiyon:",
        denemeSınıfı.overrideEdilecekFonksiyon.__doc__,
    )
    print(
        "deneme sınıfı2 override edilecek fonksiyon:",
        denemeSınıfı2.overrideEdilecekFonksiyon.__doc__,
    )
    denemeSınıfı.overrideEdilecekFonksiyon()
    denemeSınıfı.overrideEdilecekFonksiyon = merhabaDunya
    denemeSınıfı.overrideEdilecekFonksiyon()

    denemeSınıfı2.overrideEdilecekFonksiyon()
    print(
        "deneme sınıfı override edilecek fonksiyon:",
        denemeSınıfı.overrideEdilecekFonksiyon.__doc__,
    )
    print(
        "deneme sınıfı2 override edilecek fonksiyon:",
        denemeSınıfı2.overrideEdilecekFonksiyon.__doc__,
    )
