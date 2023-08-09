from glob import glob

from PIL import Image

gorsel_glob_desen = "imgs/*.png"
# imgs/svy_1.png
ORAN = 0.5


def main():
    gorsel_listesi = (
        "imgs/_3840/sehir_ikonu*.png",
        "imgs/_3840/hizmet_basarisiz*.png",
        "imgs/_3840/dunya_ikonu*.png",
        "imgs/_3840/duzen_logo*.png",
        "imgs/_3840/maks_sefer*",
        "imgs/_3840/mavi_tamam*.png",
        "imgs/_3840/geri_ok*.png",
    )
    gorsel_listesi = [glob(gorsel_glob_desen)[0] for gorsel_glob_desen in gorsel_listesi]
    yeni_gorsel_listesi = [f"{gorsel_dl}_1980.png" for gorsel_dl in gorsel_listesi]
    liste_ile_boyutlandir(gorsel_listesi, ORAN, yeni_gorsel_listesi)


def liste_ile_boyutlandir(gorsel_listesi, oran, yeni_gorsel_listesi):
    for gorsel, yeni_gorsel in zip(gorsel_listesi, yeni_gorsel_listesi):
        yeniden_boyutlandir(gorsel, oran, yeni_gorsel)


def glob_ile_boyutlandir(gorsel_glob_desen, oran):
    print(f"Görsel glob desen: {gorsel_glob_desen}")
    gorsel_dler = glob(gorsel_glob_desen)
    yeni_gorsel_dler = [f"{gorsel_dl}_yeni.png" for gorsel_dl in gorsel_dler]
    liste_ile_boyutlandir(gorsel_dler, oran, yeni_gorsel_dler)


def yeniden_boyutlandir(gorsel_yl, oran, yeni_gorsel_yl):
    print(f"Görsel yol: {gorsel_yl}, oran: {oran}, yeni görsel yol: {yeni_gorsel_yl}")
    PIL_gorsel = Image.open(gorsel_yl)
    genislik, yukseklik = PIL_gorsel.size
    yeni_genislik = int(genislik * oran)
    yeni_yukseklik = int(yukseklik * oran)
    PIL_gorsel = PIL_gorsel.resize((yeni_genislik, yeni_yukseklik))
    PIL_gorsel.save(yeni_gorsel_yl)
    print(f"Yeniden boyutlandırıldı: {yeni_gorsel_yl}")


if __name__ == "__main__":
    main()
