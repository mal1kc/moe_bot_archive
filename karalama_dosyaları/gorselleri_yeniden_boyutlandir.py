from glob import glob

from PIL import Image

gorsel_glob_desen = "imgs/*.png"
# imgs/svy_1.png
oran = 0.5


def main():
    print(f"Görsel glob desen: {gorsel_glob_desen}")
    gorsel_dler = glob(gorsel_glob_desen)
    for gorsel_dl in gorsel_dler:
        PIL_gorsel = Image.open(gorsel_dl)
        genislik, yukseklik = PIL_gorsel.size
        yeni_genislik = int(genislik * oran)
        yeni_yukseklik = int(yukseklik * oran)
        PIL_gorsel = PIL_gorsel.resize((yeni_genislik, yeni_yukseklik))
        PIL_gorsel.save(f"{gorsel_dl}_yeni.png")


if __name__ == "__main__":
    main()
