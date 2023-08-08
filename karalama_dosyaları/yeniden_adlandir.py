from glob import glob
from pathlib import Path
from pprint import pprint


class Sayac:
    def __init__(self, name, start=0):
        self.name = name
        self.num = start

    def __call__(self):
        self.num += 1
        return self.num

    def __str__(self):
        return f"{self.name}_{self.num}"

    def __repr__(self):
        return f"{self.__class__.__name__}_{self.name}:{self.num}"

    def __hash__(self):
        return hash(self.name)


if __name__ == "__main__":
    dosya_eklentisi = ".png"
    gorsel_1920 = glob(f"imgs/_1920/*{dosya_eklentisi}")
    gorsel_1920 = [Path(gorsel) for gorsel in gorsel_1920]
    eski_gorsel_1929 = gorsel_1920.copy()
    yeniden_adlandirilmis = []
    sayaclar = {}
    for gorsel in gorsel_1920:
        gorsel_ana_ad = gorsel.stem
        gorsel_k_tipi = gorsel_ana_ad.split("_")[0]
        if gorsel_k_tipi not in sayaclar:
            sayaclar[gorsel_k_tipi] = Sayac(gorsel_k_tipi, start=1)
        else:
            sayaclar[gorsel_k_tipi]()

        yeni_gorsel_ana_ad = f"{gorsel_k_tipi}_{sayaclar[gorsel_k_tipi].num}"
        yeniden_adlandirilmis.append(gorsel.parent / f"{yeni_gorsel_ana_ad}{dosya_eklentisi}")

    pprint(yeniden_adlandirilmis)
    pprint(sayaclar)

    # for eski, yeni in zip(eski_gorsel_1929, yeniden_adlandirilmis):
    #     if os.rename(eski, yeni) == None:
    #         print(f'{eski} dosyasi {yeni} olarak yeniden adlandirildi')
