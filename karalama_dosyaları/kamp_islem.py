import ctypes
from glob import glob
import multiprocessing
from pathlib import Path
import threading

from time import sleep
import time
from typing import Any, Optional
import cv2
import os


import numpy
import pylightxl as xl
from PIL import Image
from pyautogui import (
    click,
    locateOnScreen,
    moveTo,
    press,
    rightClick,
    scroll,
    center,
    mouseDown,
    mouseUp,
)
from pyautogui import write
from ayarlar import (
    KampTaramaAyarlar,
    KampSaldiriAyarlar,
    Kare,
    MevsimTipiEnum,
    OnSvyEnum,
    TumEminlikler,
    TumTaramaBolgeleri,
    ekran_goruntusu_al,
    Koordinat2D,
    SabitTiklama,
    TIKLAMA_KISITLAMALARI,
)
from enumlar import ModSinyal


class IsimliDizi:
    def __init__(self, isim: str, dizi) -> None:
        self.isim = isim
        self.iterable = dizi

    def __iter__(self):
        for item in self.iterable:
            yield item


class MultiImageTemplateMatcher:
    def __init__(
        self,
        isim: Any,
        needle_image_paths: list[str | Path],
        threshold=0.8,
        method=cv2.TM_CCOEFF_NORMED,
    ):
        self.isim = isim
        self.needle_image_paths = needle_image_paths
        self.threshold = threshold
        self.method = method

    def match(self, haystack_img: numpy.array) -> tuple[int, int, int, int] | None:  # type: ignore
        """
        NOT: Verilen ana resmin içindeki konuma göre template konumu dönüyor.

        Tries to find the needle images in the haystack image
        - If no match found in needle image tries the next needle image
        - If no match found in any needle image, returns None
        - If match found, returns the first match location

        Args:
            haystack_img (np.array) : haystack image to search needle images

        Returns:
            tuple[int,int,int,int] | None:
                 match location( top_left_x,top_left_y, w, h) of single needle image OR None if no match found
        """
        locations = []
        for template_image_path in self.needle_image_paths:
            needle_img = cv2.imread(str(template_image_path), cv2.IMREAD_GRAYSCALE)
            result = cv2.matchTemplate(haystack_img, needle_img, self.method)
            locations = numpy.where(result >= self.threshold)  # type: ignore
            locations = list(zip(*locations[::-1]))
            if locations:
                return (
                    locations[0][0],
                    locations[0][1],
                    needle_img.shape[1],
                    needle_img.shape[0],
                )
        return None


# class IsimliCascade:
#     def __init__(self, isim: str, cascade_path: str) -> None:
#         self.isim = isim
#         self.cascade_classifier = cv2.CascadeClassifier(cascade_path)

#     def taramaYap(self, tarama_yapilacak_gorsel) -> Kare | None:
#         """
#         kendi cascade_classifier objesi ile tarama_yapilacak_gorsel üzerinde tarama yapar ve ilk bulunan kareyi döner

#         """
#         gecici_kareler = self.cascade_classifier.detectMultiScale(
#             tarama_yapilacak_gorsel
#         )
#         for gecici_kare in gecici_kareler:
#             if gecici_kare is not None:
#                 bulunan_kare = KampKare(
#                     int(gecici_kare[0]),
#                     int(gecici_kare[1]),
#                     int(gecici_kare[2]),
#                     int(gecici_kare[3]),
#                 )
#                 return bulunan_kare


class DosyaIslemleri:
    directory_path = ".\\img\\_3840/"

    # Get list of all files in current directory
    directory = os.listdir(path=directory_path)

    @staticmethod
    def globCoz(glob_dsn: str) -> list[str]:
        """
        glob_dsn : str
        """

        dosyalar = glob(glob_dsn)
        return dosyalar

    @staticmethod
    def gorselGetir(gorsel_id) -> str:
        """
        DosyaIslemleri.gorselleriGetir(gorsel_id)[0] ile aynı işi yapar
        """
        dosyalar = DosyaIslemleri.gorselleriGetir(gorsel_id)
        return dosyalar[0]

    @staticmethod
    def gorselleriGetir(gorsel_id: str, sirala: bool = False) -> list[str]:
        """
        varsayilanlar objesinin taşıdığı gorsel desen lerinden gorsel_id'ye ait olan desene uygun görsellerii döndürür\n
        gorsel_id : str\n
        sirala : bool = False
            -> uzanti olmadan , tersten sıralar
        """
        glob_dsn = DosyaIslemleri.directory_path + gorsel_id
        dosyalar = DosyaIslemleri.globCoz(glob_dsn)

        if len(dosyalar) == 0:
            raise ValueError(f"Gorsel bulunamadı : {gorsel_id}, glob_dsn : {glob_dsn}")

        if sirala:
            dosyalar.sort(key=lambda x: int(x.split(".")[-2].split("_")[-1]), reverse=True)

        return dosyalar

    @staticmethod
    def cascadeGetir(cascade_glob) -> str:
        glob_dsn = DosyaIslemleri.directory_path + cascade_glob
        cascade_dosyalr = DosyaIslemleri.globCoz(glob_dsn)
        if len(cascade_dosyalr) > 0:
            return cascade_dosyalr[0]
        raise FileNotFoundError(glob_dsn)

    @staticmethod
    def gorselleriYukle(dosya_yolları: list[str]) -> list[cv2.typing.MatLike]:
        img_list = []
        for dosya_yl in dosya_yolları:
            img_list.append(Image.open(dosya_yl))
        return img_list


# **************************************************#
#            IŞINLANMA (RASTGELE VE KOORDİNAT)     #
# **************************************************#
class BolgeDegistir:
    def __init__(
        self,
        bolge: Kare | None,
        eminlik: float,
        gri_tarama: True,
    ) -> None:
        self.bolge = bolge
        self.eminlik = eminlik
        self.gri_tarama = gri_tarama

        self.yardimci_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["yardimci_resim"])
        self.sekme_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["sekme_resim"])
        self.rastgele_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["rastgele_resim"])
        self.kullan_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["kullan_buton_resim"])
        self.satin_al_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["satin_al_resim"])

    def RastgeleBolge(self):
        press("4")
        sleep(0.2)
        click(500, 300)
        sleep(0.2)
        self.yardimci_buton = locateOnScreen(
            self.yardimci_resim,
            region=TumTaramaBolgeleri["yardimci_bolge"],
            confidence=TumEminlikler["yardimci_eminlik"],
            grayscale=self.gri_tarama,
        )
        if self.yardimci_buton is not None:
            click(self.yardimci_buton)
            self.sekme_buton = locateOnScreen(
                self.sekme_resim,
                region=TumTaramaBolgeleri["sekme_bolge"],
                confidence=TumEminlikler["sekme_eminlik"],
                grayscale=self.gri_tarama,
            )
            if self.sekme_buton is not None:
                click(self.sekme_buton)
                moveTo(3000, 1200)  # FIXME : sabitler değişçek
                self.rast_yazi = locateOnScreen(
                    self.rastgele_resim,
                    region=TumTaramaBolgeleri["rastgele_bolge"],
                    confidence=TumEminlikler["rastgele_eminlik"],
                    grayscale=self.gri_tarama,
                )
                while self.rast_yazi is None:
                    scroll(-10000)
                    rast_yazi2 = locateOnScreen(
                        self.rastgele_resim,
                        region=TumTaramaBolgeleri["rastgele_bolge"],
                        confidence=TumEminlikler["rastgele_eminlik"],
                        grayscale=self.gri_tarama,
                    )
                    if rast_yazi2 is not None:
                        kullan_buton = locateOnScreen(
                            self.kullan_resim,
                            # FIXME : sabitler değişçek
                            region=(
                                rast_yazi2[0] - 100,
                                rast_yazi2[1],
                                1200,
                                500,
                            ),
                            confidence=TumEminlikler["kullan_buton_eminlik"],
                            grayscale=self.gri_tarama,
                        )
                        if kullan_buton is None:
                            self.satin_al = locateOnScreen(
                                self.satin_al_resim,
                                # FIXME : sabitler değişçek
                                region=(
                                    rast_yazi2[0] - 100,
                                    rast_yazi2[1],
                                    1500,
                                    500,
                                ),
                                confidence=TumEminlikler["satin_al_eminlik"],
                                grayscale=self.gri_tarama,
                            )
                            if self.satin_al is not None:
                                click(self.satin_al)
                                kullan_buton = (
                                    locateOnScreen(
                                        self.kullan_resim,
                                        # FIXME : sabitler değişçek
                                        region=(
                                            rast_yazi2[0] - 100,
                                            rast_yazi2[1],
                                            1200,
                                            500,
                                        ),
                                        confidence=TumEminlikler["kullan_buton_eminlik"],
                                        grayscale=self.gri_tarama,
                                    ),
                                )
                                if self.kullan_buton is not None:
                                    click(self.kullan_buton)
                        if self.kullan_buton is not None:
                            click(self.kullan_buton)


class BolgeTablosu:
    baslangic_konumlari = Koordinat2D("C4", "D4")

    bolgeler: list[Koordinat2D]
    bolge_sayisi: int

    def excelOku(self, dosya_yolu: str | Path = Path("./coordinates/regions.xlsx")) -> None:
        try:
            self.bolgeler = []
            bolge_excel = xl.readxl(fn=dosya_yolu)
            bolge_tablosu = bolge_excel.ws(ws="Bolge Tablosu")
            baslangic = int(self.baslangic_konumlari.x[1])
            self.bolge_sayisi = bolge_tablosu.address(f"{self.baslangic_konumlari.x[0]}{int(baslangic - 2 )}")  # type: ignore

            bitis = baslangic + self.bolge_sayisi

            for adim in range(baslangic, bitis):
                bolge_x = bolge_tablosu.address(f"{self.baslangic_konumlari.x[0]}{adim}")

                bolge_y = bolge_tablosu.address(f"{self.baslangic_konumlari.y[0]}{adim}")

                self.bolgeler.append(Koordinat2D(bolge_x, bolge_y))

        except Exception as e:
            raise Exception(f"{e}: bolge tablosu okunamadı")

    def __len__(self):
        return len(self.bolgeler)

    def __getitem__(self, __val: int):
        return self.bolgeler[__val]


class Fare:
    @staticmethod
    def sagTikla(uyuma_suresi=0):
        sleep(uyuma_suresi)
        rightClick()
        sleep(uyuma_suresi)

    @staticmethod
    def solTikla(konum: Optional[Koordinat2D] = None, uyuma_suresi=0):
        sleep(uyuma_suresi)
        click(konum)
        sleep(uyuma_suresi)


class Klavye:
    _lock = threading.Lock()

    @staticmethod
    def tuslariBas(tus: str | list[str], aralik: float = 0.4):
        with Klavye._lock:
            tus = "".join(str(tus))
            write(tus, interval=aralik)


class BolgeDegistirici(Fare):
    """
    Fare sınıfından türetilmiş BolgeDegistirici sınıfı\n
     -> Fare sınıfının solTikla ve sagTikla metotlarını kullanır\n
     -> BolgeTablosu sınıfından bolge koordinatlarını alır\n
     -> KaynakKare sınıfından kareler oluşturur\n
     -> buyutec ikonuna tıklar\n
     -> BolgeTablosunda kaldigi yerden devam eder\n
     -> bolgeDegistir metodu ile bolge değiştirir\n
     -> eğer bolge tablosu sonuna gelirse başa döner\n
    """

    def __init__(
        self,
    ) -> None:
        super().__init__()
        self.bolge_tablosu = BolgeTablosu()
        self.bolge_tablosu.excelOku()
        self.hedef_bolge_index: int = 0

    def _sonrakiBolge(self):
        """
        BolgeTablosundan sonraki bolgeyi alır\n
        """
        self.hedef_bolge_index += 1
        if self.hedef_bolge_index >= len(self.bolge_tablosu):
            self.hedef_bolge_index = 0

    def bolgeDegistir(self):
        """
        bir sonraki bölge koordinatını
            otomatik olarak işleme alıp yeni koordinata gitmek için kullanılır.
        """

        self._bolgeDegistir(self.bolge_tablosu[self.hedef_bolge_index])

    def _bolgeDegistir(self, bolge: Koordinat2D) -> None:
        """
        BolgeTablosundan elde edilen bolgenin x y koordinatlarını alır\n
        -> buyutec ikonuna tıklar\n
        ve x y koordinatlarını kullanarak bolgeyi değiştirir\n
        """
        bul_ikonu_konum = (1550, 80)
        self.solTikla(bul_ikonu_konum)
        sleep(0.4)
        Klavye.tuslariBas(self.bolge_tablosu[self.hedef_bolge_index].x)
        bul_y_konum = (2050, 350)
        self.solTikla(bul_y_konum)
        sleep(0.1)
        Klavye.tuslariBas(self.bolge_tablosu[self.hedef_bolge_index].y)
        buyutec_ikonu_konum = (2300, 350)
        self.solTikla(buyutec_ikonu_konum)
        self._sonrakiBolge()

    def __repr__(self) -> str:
        return f"{self.bolge_tablosu=}"

    def _islemDevamEtsinMi(self) -> bool:
        """
        instance override edilecek
        """
        return True


class KaydirmaYontemleri:
    kaydirma_sonrasi_sure = 0.3

    @staticmethod
    def ekranSabitle():
        mouseDown(SabitTiklama["inaktif_bolge1"])
        moveTo(SabitTiklama["inaktif_bolge2"])
        mouseUp()

    @staticmethod
    def _kareSol():
        mouseDown(SabitTiklama["sol_nokta"], button="left")
        moveTo(SabitTiklama["sag_nokta"])
        moveTo(SabitTiklama["sag_nokta2"])
        # sleep(KaydirmaYontemleri.kaydirma_sonrasi_sure)
        mouseUp(button="left")
        # sleep(KaydirmaYontemleri.kaydirma_sonrasi_sure)
        KaydirmaYontemleri.ekranSabitle()

    @staticmethod
    def _kareSag():
        mouseDown(SabitTiklama["sag_nokta"], button="left")
        moveTo(SabitTiklama["sol_nokta"])
        moveTo(SabitTiklama["sol_nokta2"])
        # sleep(KaydirmaYontemleri.kaydirma_sonrasi_sure)
        mouseUp(button="left")

        # sleep(KaydirmaYontemleri.kaydirma_sonrasi_sure)
        KaydirmaYontemleri.ekranSabitle()

    @staticmethod
    def _kareUst():
        mouseDown(SabitTiklama["ust_nokta"], button="left")
        moveTo(SabitTiklama["ust_bitis"])
        moveTo(SabitTiklama["ust_bitis2"])
        # sleep(KaydirmaYontemleri.kaydirma_sonrasi_sure)
        mouseUp(button="left")
        # sleep(KaydirmaYontemleri.kaydirma_sonrasi_sure)
        KaydirmaYontemleri.ekranSabitle()

    @staticmethod
    def _kareAlt():
        mouseDown(SabitTiklama["alt_nokta"], button="left")
        moveTo(SabitTiklama["alt_bitis"])
        moveTo(SabitTiklama["alt_bitis2"])
        # sleep(KaydirmaYontemleri.kaydirma_sonrasi_sure)
        mouseUp(button="left")
        # sleep(KaydirmaYontemleri.kaydirma_sonrasi_sure)
        KaydirmaYontemleri.ekranSabitle()


class CokluTarayici:
    def __init__(
        self,
        bolge: Kare | None,
        eminlik: float,
        gri_tarama: bool,
        ornek_dosya_dizileri: list[IsimliDizi],
        isim: str = "İsimsiz",
    ) -> None:
        self.isim = isim
        self.bolge = bolge
        self.eminlik = eminlik
        self.gri_tarama = gri_tarama
        self.ornek_dosya_dizileri = ornek_dosya_dizileri

    def _islemDevamEtsinMi(self):
        """instance sirasinda uzerine yazilacak"""
        return True

    def _ekranTara(self) -> int | None:
        """
        ilk bulunan örnek dosyanın indeksinin liste uzunluğundan çıkarılmış halini döndürür\n
        bulunamazsa None döndürür\n
        """
        for ornek_dosya_dizisi in self.ornek_dosya_dizileri:
            for ornek_dosyasi in ornek_dosya_dizisi:
                islem_devam_etsin_mi = self._islemDevamEtsinMi()
                if not islem_devam_etsin_mi:
                    return None
                kare = locateOnScreen(
                    ornek_dosyasi,
                    region=self.bolge,
                    confidence=self.eminlik,
                    grayscale=self.gri_tarama,
                )
                if kare is not None:
                    return ornek_dosya_dizisi.isim
        return None


# class SeviyeTarayici(CokluTarayici):
#     def __init__(self) -> None:
#         eminlik = TumEminlikler["svy_eminlik"]

#         ornek_ds_yl: list[str] = DosyaIslemleri.gorselleriGetir(
#             KampTaramaAyarlar["svy"]
#         )

#         bolge = TumTaramaBolgeleri["seviye"]

#         super().__init__(
#             bolge=bolge,
#             eminlik=eminlik,
#             gri_tarama=False,
#             ornek_ds_yl=ornek_ds_yl,
#             isim="SeviyeTarayici",
#         )

#     def svyKontrol(self, svy) -> bool:
#         """
#         açılan kamp sayfasınının en üstündeki seviyenin ön seviye ile aynı olup olmadığını kontrol eder.
#         aynı olup olmadığına göre true ya da false (bool) bool
#         """
#         taramasonucu = self._ekranTara()
#         return taramasonucu == svy


###############################################################################
# class SeferBoncukTaryici(CokluTarayici):
#     def __init__(
#         self,
#         maks_sefer_boncuk: int,
#     ) -> None:
#         isim: str = "SeferBoncukTarayici"
#         bolge = TumTaramaBolgeleri["sefer_boncuk_bolge"]
#         eminlik = TumEminlikler["sefer_eminlik"]
#         gri_tarama = True
#         # ornek_ds_yl = DosyaIslemleri.gorselleriGetir(KampTaramaAyarlar["sefer"])
#         ornek_dosya_dizileri = [
#             IsimliDizi(
#                 isim=sefer_boncuk_sayisi,
#                 dizi=DosyaIslemleri.gorselleriGetir(
#                     KampTaramaAyarlar["sefer_boncuk_sayisi_resim"].format(
#                         sefer_boncuk_sayisi=sefer_boncuk_sayisi
#                     )
#                 ),
#             )
#             for sefer_boncuk_sayisi in range(maks_sefer_boncuk + 1)
#         ]


#         super().__init__(bolge, eminlik, gri_tarama, ornek_dosya_dizileri, isim)

#         self.sefer_boncuk_sayisi = maks_sefer_boncuk
#         self.sefer_menusu_acik_mi = None
#         self.bekleme_suresi = 1

#     def seferBoncukSayisiGetir(self) -> int :
#         """
#         -> kırmızı boncuktan sefer sayısının kaç olduğunu getirir.
#         """
#         sefer_boncuk_sayisi = self._ekranTara()
#         sayac = 0
#         while sefer_boncuk_sayisi is None and sayac < 3:
#             sefer_boncuk_sayisi = self._ekranTara()
#             sayac = sayac + 1
#         return sefer_boncuk_sayisi if sefer_boncuk_sayisi is not None else 1 #FIXME

#     def seferMaksBoncukKontrol(self) -> bool :
#         """
#         -> maksimum sefer sayısını, seferleri açmadan boncuk ile takip eder.
#         """
#         sefer_boncuk_sayisi = self.seferBoncukSayisiGetir()
#         while sefer_boncuk_sayisi > 0:
#             sefer_boncuk_sayisi = self.seferBoncukSayisiGetir()
#             moveTo(1250, 1000)
#             sleep(0.5)
#             moveTo(900, 1300)
#             if SeferTarayici._islemDevamEtsinMi() is False:
#                 return False
#         KampFare.kalemiGoster()
#         self._seferMenusuAcKapat()
#         return True


#########################################################################


class SeferTarayici:
    def __init__(
        self,
        maks_sefer_sayisi: int,
    ) -> None:
        # Ortak değişkenler
        eminlik = TumEminlikler["sefer_eminlik"]
        gri_tarama = True

        # Ana Sefer in değişkenleri
        ana_sefer_bolge = TumTaramaBolgeleri["sefer_bolge"]
        ana_sefer_ornek_dosya_dizileri = [
            IsimliDizi(
                isim=sefer_sayisi,
                dizi=DosyaIslemleri.gorselleriGetir(KampTaramaAyarlar["sefer_sayisi_resim"].format(sefer_sayisi=sefer_sayisi)),
            )
            for sefer_sayisi in range(maks_sefer_sayisi + 1)
        ]

        self.ana_sefer_tarayici = CokluTarayici(ana_sefer_bolge, eminlik, gri_tarama, ana_sefer_ornek_dosya_dizileri)

        self.maks_sefer_sayisi = maks_sefer_sayisi
        self.ana_sefer_menusu_acik_mi = None
        self.ana_bekleme_suresi = 1

        # Boncuk Sefer in değişkenleri
        boncuk_sefer_bolge = TumTaramaBolgeleri["sefer_boncuk_bolge"]
        boncuk_sefer_ornek_dosya_dizileri = [
            IsimliDizi(
                isim=sefer_boncuk_sayisi,
                dizi=DosyaIslemleri.gorselleriGetir(
                    KampTaramaAyarlar["sefer_boncuk_sayisi_resim"].format(sefer_boncuk_sayisi=sefer_boncuk_sayisi)
                ),
            )
            for sefer_boncuk_sayisi in range(1, maks_sefer_sayisi + 1)
        ]

        self.sefer_boncuk_tarayici = CokluTarayici(boncuk_sefer_bolge, eminlik, gri_tarama, boncuk_sefer_ornek_dosya_dizileri)

    def _islemDevamEtsinMi(self) -> bool:
        """
        instance override edilecek
        """
        return True

    def _anaSeferMenusuAcKapat(self):
        press("z", interval=0.5)

    def seferSayisiGetir(self, boncuk=True) -> int:
        """
        -> sefer sayısının kaç olduğunu döner
        ->bulamazsa none döner.
        """
        if boncuk:
            sefer_sayisi = self.sefer_boncuk_tarayici._ekranTara()
            return sefer_sayisi if sefer_sayisi is not None else 0  # FIXME

        # deaktif cünkü kampfarede bu kullanılmıyor.
        # if not self._islemDevamEtsinMi():
        #     return None

        sefer_sayisi = self.ana_sefer_tarayici._ekranTara()
        sayac = 0
        while sefer_sayisi is None and sayac < 3:
            self._anaSeferMenusuAcKapat()
            sefer_sayisi = self.ana_sefer_tarayici._ekranTara()
            sayac = sayac + 1

        return sefer_sayisi if sefer_sayisi is not None else 1  # FIXME

    def seferMaksKontrol(self, boncuk: bool = True) -> bool:
        """
        -> eğer sefer maks ise kodu bekletip sefer sayısının azalmasını bekler
        """
        sefer_sayisi = self.seferSayisiGetir(boncuk)
        while sefer_sayisi == self.maks_sefer_sayisi:
            sefer_sayisi = self.seferSayisiGetir(boncuk)
            moveTo(900, 350)
            sleep(0.5)
            moveTo(1300, 750)
            # if self._islemDevamEtsinMi() is False:
            #     return False
        if not boncuk:
            self._anaSeferMenusuAcKapat()
        return True

    def seferMinKontrol(self, boncuk: bool = False) -> bool:
        """
        -> sefer sayısı 0 olana kadar bekler
        """
        # FIXME: seferMinKontrol
        sefer_sayisi = self.seferSayisiGetir(boncuk)
        while sefer_sayisi > 0:
            sefer_sayisi = self.seferSayisiGetir(boncuk)
            moveTo(1250, 1000)
            sleep(0.5)
            moveTo(900, 1300)
            # if self._islemDevamEtsinMi() is False:
            #     return False
        if not boncuk:
            self._anaSeferMenusuAcKapat()
        return True


class KampKare(Kare):
    def __new__(
        cls,
        x: int | Kare,
        y: Optional[int] = None,
        genislik: Optional[int] = None,
        yukseklik: Optional[int] = None,
    ):
        if isinstance(x, Kare):
            return super().__new__(cls, x.x, x.y, x.genislik, x.yukseklik)
        return super().__new__(cls, x, y, genislik, yukseklik)

    def __init__(
        self,
        x: int | Kare,
        y: Optional[int] = None,
        genislik: Optional[int] = None,
        yukseklik: Optional[int] = None,
    ) -> None:
        self.gecici_auto_kareler = None
        if all([y is None, genislik is None, yukseklik is None]):
            Exception("Kare oluşturulamadı.")

        if isinstance(x, Kare):
            self.koordinat = x
        else:
            self.koordinat = Kare(x, y, genislik, yukseklik)  # type: ignore

        if Kare.gecersizMi(self.koordinat):  # type: ignore
            raise Exception(f"Geçersiz kare: {self.koordinat}")

    def __str__(self) -> str:
        return f"KampKare({self.koordinat.x},{self.koordinat.y},{self.koordinat.genislik},{self.koordinat.yukseklik})"

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return hash(str(self.koordinat))

    def disindaMi(self, dkare: Kare, buyutme_miktari: int = 30) -> bool:
        buyutulmus_kare = self.buyutulmusKare(buyutme_miktari)

        return (
            buyutulmus_kare.x > dkare.x + dkare.genislik
            or buyutulmus_kare.y > dkare.y + dkare.yukseklik
            or buyutulmus_kare.x + buyutulmus_kare.genislik < dkare.x
            or (buyutulmus_kare.y + buyutulmus_kare.yukseklik < dkare.y)
        )

    def buyutulmusKare(self, buyutme_miktari: int = 100) -> Kare:
        return Kare(
            self.koordinat.x - buyutme_miktari,
            self.koordinat.y - buyutme_miktari,
            self.koordinat.genislik + buyutme_miktari,
            self.koordinat.yukseklik + buyutme_miktari,
        )

    def merkez(self) -> Koordinat2D:
        return Koordinat2D(
            self.koordinat.x + self.koordinat.genislik / 2,
            self.koordinat.y + self.koordinat.yukseklik / 2,
        )

    def onSeviyeTaramaAlaniGetir(self) -> Kare:
        sol_ust_x = int(self.x - (self.genislik * 2))
        if sol_ust_x < 0:
            sol_ust_x = 0
        sol_ust_y = int(self.y)
        genislik = int(self.genislik * 4)
        yukseklik = int(self.yukseklik * 3)

        return Kare(sol_ust_x, sol_ust_y, genislik, yukseklik)


# class Soguma(CokluTarayici):  #  ENGEL TARAYICI İÇİNE GİDECEK
#     def __init__(
#         self,
#         bolge: Kare | None,
#         eminlik: float,
#         gri_tarama: True,
#     ) -> None:
#         self.bolge = bolge
#         self.eminlik = eminlik
#         self.gri_tarama = gri_tarama

#         self.soguma_resim = DosyaIslemleri.gorselGetir(
#             KampSaldiriAyarlar["soguma_resim"]
#         )
#         self.tamam_resim = DosyaIslemleri.gorselGetir(
#             KampSaldiriAyarlar["tamam_buton_resim"]
#         )

#     def sogumaKontrol(self):
#         self.sogumada = locateOnScreen(
#             self.soguma_resim,
# -            region=TumTaramaBolgeleri["pop_up_bolge"],
#             confidence=TumEminlikler["pop_up_eminlik"],
#             grayscale=self.gri_tarama,
#         )
#         if self.sogumada is not None:
#             self.tamam_kontrol = locateOnScreen(
#                 self.tamam_resim,
# -               region=TumTaramaBolgeleri["tamam_buton_bolge"],
#                 confidence=TumEminlikler["tamam_buton_eminlik"],
#                 grayscale=self.gri_tarama,
#             )
#             if self.tamam_kontrol is not None:
#                 click(self.tamam_kontrol)


class OnSeviyeTarayici:
    def __init__(self, on_svyler: tuple[OnSvyEnum]) -> None:
        self.template_matchers: list[MultiImageTemplateMatcher] = []
        for on_svy in on_svyler:
            self.template_matchers.append(
                MultiImageTemplateMatcher(
                    isim=on_svy.value,
                    needle_image_paths=DosyaIslemleri.gorselleriGetir(KampTaramaAyarlar["onsvy_ad"].format(onsvy_val=on_svy.value)),
                    threshold=TumEminlikler["onsvy_eminlik"],
                ),
            )

    def svyTara(self, tarama_alani: Kare) -> OnSvyEnum | None:  # FIXME thred ile seviye taraması yapılacak.
        for onsvy_template_matcher in self.template_matchers:
            screenshot: numpy.array[int, int, int] = ekran_goruntusu_al()
            # screenshot = [y,x]
            screenshot_crp = screenshot[
                tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
                tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
            ]
            print(f"tarama_alani: {tarama_alani}")
            print(f"kırpılmış ekran_g : genislik -> {screenshot_crp.shape[1]}, yukseklik -> {screenshot_crp.shape[0]}")
            onsvy_kare = onsvy_template_matcher.match(screenshot_crp)
            if onsvy_kare is not None:
                return onsvy_template_matcher.isim
        return None

    def svyTaraThreaded(self, tarama_alani: Kare) -> OnSvyEnum | None:
        buldum_etkinlik = threading.Event()
        buldum_etkinlik.clear()
        bulunan = multiprocessing.Queue(maxsize=1)

        def _tara(func, fixed_ret, *aargs: tuple):
            if buldum_etkinlik.is_set():
                return
            sonuc = func(*aargs)
            if sonuc is not None:
                nonlocal bulunan
                bulunan.put_nowait(fixed_ret)
                buldum_etkinlik.set()

        ekran_g = ekran_goruntusu_al()
        ekran_krp = ekran_g[
            tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
            tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
        ]

        threads = []
        for onsvy_template_matcher in self.template_matchers:
            thread = threading.Thread(
                target=_tara,
                args=(
                    onsvy_template_matcher.match,
                    onsvy_template_matcher.isim,
                    ekran_krp,
                ),
            )
            thread.start()
            threads.append(thread)

        while not buldum_etkinlik.is_set():
            for thread in threads:
                thread.join(0.1)

        if bulunan.qsize() > 0:
            return bulunan.get()
        return None


class MevsimTara:
    def __init__(self, mevsim: MevsimTipiEnum) -> None:
        self.mvsm_template_matcher = MultiImageTemplateMatcher(
            isim=mevsim.value,
            needle_image_paths=DosyaIslemleri.gorselleriGetir(KampTaramaAyarlar["mevsim"].format(mvsm_nm=mevsim.name)),
            threshold=0.75,
        )
        self.carpi_ikonu_dosya = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["cikiskamp_resim"])
        self.cikis_bina_dosya = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["cikis_bina_resim"])
        self.isin_kontrol_dosya = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["isinlanma_resim"])

    def mvsmTaraVeIsinlan(self, tarama_alani: Kare | None = None) -> MevsimTipiEnum | None:
        if tarama_alani is None:
            tarama_alani = TumTaramaBolgeleri["mevsim_bolge"]

        screenshot: numpy.array[int, int, int] = ekran_goruntusu_al()
        # screenshot = [y,x]
        screenshot_crp = screenshot[
            tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
            tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
        ]
        mvsm_kare = self.mvsm_template_matcher.match(screenshot_crp)
        if mvsm_kare is not None:
            # sınırlı alan içerisinde bulunan template in koordinatlarını normal ekran boyutuna göre ayarlama
            mvsm_kare = Kare(
                mvsm_kare[0] + tarama_alani.x,
                mvsm_kare[1] + tarama_alani.y,
                mvsm_kare[2],
                mvsm_kare[3],
            )
            # return mvsm_template_matcher.isim
            # FIXME return olarak mevsimin adı dönüyor ancak \
            # # burası tıklamaya uygunluğunu dönecek ve ona göre ışınlanılacak.
            click(center(mvsm_kare))
            sleep(0.5)
            isin_kontrol = locateOnScreen(
                self.isin_kontrol_dosya,
                region=TumTaramaBolgeleri["isinlanma_bolge"],
                confidence=TumEminlikler["isinlanma_eminlik"],
                grayscale=True,
            )
            if isin_kontrol is not None:
                click(center(isin_kontrol))
                sleep(0.5)

                carpi_kontrol = locateOnScreen(
                    self.carpi_ikonu_dosya,
                    region=TumTaramaBolgeleri["pop_up_cikis_bolge"],
                    confidence=TumEminlikler["pop_up_eminlik"],
                    grayscale=True,
                )
                if carpi_kontrol is not None:
                    click(center(carpi_kontrol))
                    sleep(0.1)

                    if tarama_alani is None:
                        tarama_alani = TumTaramaBolgeleri["mevsim_bolge"]

                    screenshot: numpy.array[int, int, int] = ekran_goruntusu_al()
                    # screenshot = [y,x]
                    screenshot_crp = screenshot[
                        tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
                        tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
                    ]
                    mvsm_kare = self.mvsm_template_matcher.match(screenshot_crp)
                    if mvsm_kare is not None:
                        # sınırlı alan içerisinde bulunan template in koordinatlarını normal ekran boyutuna göre ayarlama
                        mvsm_kare = Kare(
                            mvsm_kare[0] + tarama_alani.x,
                            mvsm_kare[1] + tarama_alani.y,
                            mvsm_kare[2],
                            mvsm_kare[3],
                        )
                        # return mvsm_template_matcher.isim #
                        # FIXME return olarak mevsimin adı dönüyor ancak \
                        # # burası tıklamaya uygunluğunu dönecek ve ona göre ışınlanılacak.
                        click(center(mvsm_kare))
                        sleep(0.5)

                self.cikis_bina_kontrol = locateOnScreen(
                    self.cikis_bina_dosya,
                    region=TumTaramaBolgeleri["cikis_bina_bolge"],
                    confidence=TumEminlikler["cikis_bina_eminlik"],
                    grayscale=True,
                )
                if self.cikis_bina_kontrol is not None:
                    click(center(self.cikis_bina_kontrol))
                    sleep(0.1)

                    if tarama_alani is None:
                        tarama_alani = TumTaramaBolgeleri["mevsim_bolge"]

                    screenshot: numpy.array[int, int, int] = ekran_goruntusu_al()
                    # screenshot = [y,x]
                    screenshot_crp = screenshot[
                        tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
                        tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
                    ]
                    mvsm_kare = self.mvsm_template_matcher.match(screenshot_crp)
                    if mvsm_kare is not None:
                        # sınırlı alan içerisinde bulunan template in koordinatlarını normal ekran boyutuna göre ayarlama
                        mvsm_kare = Kare(
                            mvsm_kare[0] + tarama_alani.x,
                            mvsm_kare[1] + tarama_alani.y,
                            mvsm_kare[2],
                            mvsm_kare[3],
                        )

                        click(center(mvsm_kare))
                        sleep(0.5)

            else:
                rightClick()

                if tarama_alani is None:
                    tarama_alani = TumTaramaBolgeleri["mevsim_bolge"]

                screenshot: numpy.array[int, int, int] = ekran_goruntusu_al()
                # screenshot = [y,x]
                screenshot_crp = screenshot[
                    tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
                    tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
                ]
                mvsm_kare = self.mvsm_template_matcher.match(screenshot_crp)
                if mvsm_kare is not None:
                    # sınırlı alan içerisinde bulunan template in koordinatlarını normal ekran boyutuna göre ayarlama
                    mvsm_kare = Kare(
                        mvsm_kare[0] + tarama_alani.x,
                        mvsm_kare[1] + tarama_alani.y,
                        mvsm_kare[2],
                        mvsm_kare[3],
                    )
                    click(center(mvsm_kare))
                    sleep(0.5)

            print(mvsm_kare)
            moveTo(mvsm_kare.x, mvsm_kare.y)

            isin_kontrol = locateOnScreen(
                self.isin_kontrol_dosya,
                region=TumTaramaBolgeleri["isinlanma_bolge"],
                confidence=TumEminlikler["isinlanma_eminlik"],
                grayscale=True,
            )
            if isin_kontrol is not None:
                click(center(isin_kontrol))
                sleep(0.1)

                return True

        return False


class KampFare:
    def __init__(self, sefer_tarayici: SeferTarayici, onseviye_tarayici: OnSeviyeTarayici) -> None:
        self.enerji_matcher = MultiImageTemplateMatcher(
            isim="e",
            needle_image_paths=[DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["enerji_resim"])],
            threshold=0.8,
        )
        self.musama_aktif_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["musama_aktif_resim"])
        self.musama_liste_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["musama_liste_resim"])
        self.popup_carpi_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["cikiskamp_resim"])
        # self.hizli_saldir = DosyaIslemleri.gorselGetir(
        #     KampSaldiriAyarlar["hizli_saldir_resim"]
        # )
        self.satin_al_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["satin_al_resim"])
        self.kullan_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["kullan_buton_resim"])
        self.kalemi_goster_matcher = MultiImageTemplateMatcher(
            isim="_kalemiGoster",
            needle_image_paths=[DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["kalemi_goster_resim"])],
            threshold=0.8,
        )
        self.saldir_buton_matcher = MultiImageTemplateMatcher(
            isim="m",
            needle_image_paths=[DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["saldir_buton_resim"])],
            threshold=0.8,
        )
        self.hizli_saldir_matcher = MultiImageTemplateMatcher(
            isim="_hizliSaldir",
            needle_image_paths=[DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["hizli_saldir_resim"])],
            threshold=0.8,
        )

        self.tiklama_kisitlamalari = TIKLAMA_KISITLAMALARI
        self.sefer_tarayici = sefer_tarayici
        self.onsvy_tarayici = onseviye_tarayici

        self.musama_sure_kontrol = 0
        self.ilk_saldiri_yapildimi = False

    def _menudeyimSinyaliYolla(self, giris=True):
        """
        instance uzerine yazilacak
        arg= giris: bool
        """
        return

    def _bolge_kisitlimi(self, tıklama_konumu: Koordinat2D) -> bool:
        """
        tiklanicak nokta dislanan bolgelerde mi
        evet > True
        hayır > False
        """

        kisitlimi_liste = list()
        for tiklama_kisitlaması in self.tiklama_kisitlamalari:
            for k, v in tiklama_kisitlaması.items():
                match k.split("_"):
                    case ["x", "taban"]:
                        if v <= tıklama_konumu.x:
                            kisitlimi_liste.append(True)
                    case ["x", "tavan"]:
                        if v >= tıklama_konumu.x:
                            kisitlimi_liste.append(True)
                    case ["y", "taban"]:
                        if v <= tıklama_konumu.y:
                            kisitlimi_liste.append(True)
                    case ["y", "tavan"]:
                        if v >= tıklama_konumu.y:
                            kisitlimi_liste.append(True)

            bos_ise_yanlis = all(kisitlimi_liste) if len(kisitlimi_liste) > 0 else False

            if len(tiklama_kisitlaması) == len(kisitlimi_liste) and bos_ise_yanlis:
                return True

            # bos_ise_yanlis = all(sefer_ozel_kisitlimi) if len(sefer_ozel_kisitlimi) > 0 else False
            kisitlimi_liste = list()
            # sefer_ozel_kisitlimi = list()
        return all(kisitlimi_liste) if len(kisitlimi_liste) > 0 else False

    def _enerjiKontrol(self) -> bool:
        """
        açılan kamp sayfasında enerji barının dolu olup olmadığını kontrol edecek
        arayüzden gelen "enerji bitse bile devam et" ayarına göre
        işleme devam edecek veya enerji bitince duracak.
        """
        ana_resim = ekran_goruntusu_al()
        tarama_alani = TumTaramaBolgeleri["enerji_bolge"]
        enerji_kontrol = ana_resim[
            tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
            tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
        ]
        loc = self.enerji_matcher.match(enerji_kontrol)
        if loc is not None:
            return True
        return False

    def _musamaAktiflestir(self):
        """
        -> musamanın aktif olup olmadığına bakar. eğer aktif değilse musamayı aktifleştirir.
        """
        ana_resim = ekran_goruntusu_al()
        tarama_alani = TumTaramaBolgeleri["saldir_buton_bolge"]

        ornek_resim = ana_resim[
            tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
            tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
        ]
        saldiri_kontrol = self.saldir_buton_matcher.match(ornek_resim)

        if saldiri_kontrol is None:
            self._menudeyimSinyaliYolla(giris=True)
            click(SabitTiklama["saldir_sayac"])
            sleep(0.23)
            musama_liste_kontrol = locateOnScreen(
                self.musama_liste_resim,
                region=TumTaramaBolgeleri["musama_liste_bolge"],
                confidence=TumEminlikler["musama_liste_eminlik"],
                grayscale=True,
            )
            if musama_liste_kontrol is not None:
                kullan_btn_kontrol = locateOnScreen(
                    self.kullan_resim,
                    region=TumTaramaBolgeleri["musama_kullan_bolge"],
                    confidence=TumEminlikler["kullan_buton_eminlik"],
                    grayscale=True,
                )
                if kullan_btn_kontrol is not None:
                    click(center(kullan_btn_kontrol))
                    sleep(0.2)
                    self.musama_sure_kontrol = time.time()
                else:
                    satin_al_buton_kontrol = locateOnScreen(
                        self.satin_al_resim,
                        region=TumTaramaBolgeleri["satin_al_resim"],
                        confidence=TumEminlikler["satin_al_eminlik"],
                        grayscale=True,
                    )
                    if satin_al_buton_kontrol is not None:
                        click(center(satin_al_buton_kontrol))
                        sleep(0.1)
                        kullan_btn_kontrol = locateOnScreen(
                            self.kullan_resim,
                            region=TumTaramaBolgeleri["kullan_resim"],
                            confidence=TumEminlikler["kullan_buton_eminlik"],
                            grayscale=True,
                        )
                        if kullan_btn_kontrol is not None:
                            click(center(kullan_btn_kontrol))
                            sleep(0.1)
                            self.musama_sure_kontrol = time.time()

        self._menudeyimSinyaliYolla(giris=False)

    def _musamaAktifKontrol(self) -> bool:
        """
        -> açılan kamp sayfasında musamanın aktif olup olmadığını kontrol eder.
            -> en son aktifleştirme üzerinden 895 saniye geçmediyse doğrudan hızlı saldırıya gitmek için True döner.

        """
        ana_resim = ekran_goruntusu_al()
        tarama_alani = TumTaramaBolgeleri["saldir_buton_bolge"]

        ornek_resim = ana_resim[
            tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
            tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
        ]
        loc = self.saldir_buton_matcher.match(ornek_resim)
        if loc is not None:
            return True
        return False

    def _cikisKamp(self):
        """
        açılan kamp sayfasından çıkış yapmak için kullanılır.
        """
        cikiskamp_resim_kontrol = locateOnScreen(
            self.popup_carpi_resim,
            region=TumTaramaBolgeleri["cikiskamp_bolge"],
            confidence=TumEminlikler["cikiskamp_eminlik"],
            grayscale=True,
        )
        if cikiskamp_resim_kontrol is not None:
            click(center(cikiskamp_resim_kontrol))

    def _sogumaKontrol(self):
        # TODO: cikis kamp ile birleşebilir
        sogumada_carpi = locateOnScreen(
            self.popup_carpi_resim,
            region=TumTaramaBolgeleri["pop_up_cikis_bolge"],
            confidence=TumEminlikler["pop_up_eminlik"],
            grayscale=True,
        )
        if sogumada_carpi is not None:
            click(center(sogumada_carpi))

    def kalemiGoster(self):
        """
        ->kaleyi ekranda ortalar.
        """
        kalemi_goster_resim_kontrol = ekran_goruntusu_al()
        tarama_alani = TumTaramaBolgeleri["kalemi_goster_bolge"]
        ornek_resim = kalemi_goster_resim_kontrol[
            tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
            tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
        ]
        loc = self.kalemi_goster_matcher.match(ornek_resim)
        if loc is not None:
            tiklama_konumu = Kare(
                loc[0] + tarama_alani.x,
                loc[1] + tarama_alani.y,
                loc[2],
                loc[3],
            )
            click(center(tiklama_konumu))

    def kampSaldiri(self, bulunan_kamp_karesi: KampKare) -> bool:
        """
        ->bulunan kamp karenin altındaki  karesi taranıp uygun olan seviyeler içindki görsellerden
            -> görsel bulunursa tıklama yapılıp hızlı saldırı yapılacak.
        """

        tarama_alani = bulunan_kamp_karesi.onSeviyeTaramaAlaniGetir()
        bolge_kisitlimi = self._bolge_kisitlimi(bulunan_kamp_karesi.merkez())

        if bolge_kisitlimi:
            return False

        onseviye = self.onsvy_tarayici.svyTara(tarama_alani)
        if onseviye is not None:
            if self.sefer_tarayici.seferMaksKontrol():  # FIXME
                # menü açlıdı (kamp menüsü)
                click(bulunan_kamp_karesi.merkez())
                sleep(0.4)

                if self._musamaAktifKontrol() is False and self.ilk_saldiri_yapildimi:
                    self._musamaAktiflestir()
                    sleep(0.1)

                # hizli saldiri tıklama
                hizli_saldir_resim_kontrol = ekran_goruntusu_al()
                tarama_alani = TumTaramaBolgeleri["hizli_saldir_bolge"]
                ornek_resim = hizli_saldir_resim_kontrol[
                    tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
                    tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
                ]
                loc = self.hizli_saldir_matcher.match(ornek_resim)
                if loc is not None:
                    tiklama_konumu = Kare(
                        loc[0] + tarama_alani.x,
                        loc[1] + tarama_alani.y,
                        loc[2],
                        loc[3],
                    )
                    click(center(tiklama_konumu))
                else:
                    self._cikisKamp()

                sleep(0.1)
                self._sogumaKontrol()
                self.ilk_saldiri_yapildimi = True
                return True
        return False

        # FIXME tıklama öncesi veya sonrası ihtiyaca göre _musamaAktifKontrol
        # FIXME self.onseviye_tarayici kullanılıp seviye belirlenecek ve ona göre tıklama yapılacak


class KampTarayici:
    """
    Önce önseviyeyi tarayıp sonrasında
    bulduğu ön seviyenin üzerindeki bölgede kamp tipini tarar ver tıklama yapar."""

    def __init__(self, kamp_fare: KampFare | None = None) -> None:
        cascade_xml = DosyaIslemleri.cascadeGetir(KampTaramaAyarlar["kamp_tip_cascade"])
        self.CascadeClassifier = cv2.CascadeClassifier(cascade_xml)
        self.tarama_bolgesi: Kare = TumTaramaBolgeleri["kamp_tip_tarama_bolge"]
        self.kamp_fare = kamp_fare
        self.kamp_kareleri = set()

    def _islemDevamEtsinMi(self) -> bool:
        return True

    def ekranTara(self, liste_don=False) -> bool | set | None:
        ekran_g = ekran_goruntusu_al()

        ekran_g_kirp = ekran_g[
            self.tarama_bolgesi.y : self.tarama_bolgesi.y + self.tarama_bolgesi.yukseklik,
            self.tarama_bolgesi.x : self.tarama_bolgesi.x + self.tarama_bolgesi.genislik,
        ]
        gecici_kareler = self.CascadeClassifier.detectMultiScale(ekran_g_kirp)
        for gecici_kare in gecici_kareler:
            islem_devam_etsin_mi = self._islemDevamEtsinMi()
            if not islem_devam_etsin_mi:
                return  # eğer işlem devam etmiyorsa erkenden tarama iptali
            if gecici_kare is not None:
                bulunan_kare = KampKare(
                    self.tarama_bolgesi.x + int(gecici_kare[0]),
                    self.tarama_bolgesi.y + int(gecici_kare[1]),
                    int(gecici_kare[2]),
                    int(gecici_kare[3]),
                )
                self._kampkareEkleVeSaldir(bulunan_kare)

        if len(self.kamp_kareleri) > 0:
            if liste_don:
                return self.kamp_kareleri
            print(self.kamp_kareleri)
            self.kamp_kareleri.clear()
            return True
        return False

    def _kampKareEkle(self, kare: KampKare) -> bool:
        if len(self.kamp_kareleri) == 0:
            self.kamp_kareleri.add(kare)
            return True

        kareler_elenmis = [kare.disindaMi(essiz_kare) for essiz_kare in self.kamp_kareleri]
        # kareler_elenmis = []
        # for essiz_kare in self.kamp_kareleri:
        #     kareler_elenmis.append(kare.disindaMi(essiz_kare))
        if all(kareler_elenmis):
            self.kamp_kareleri.add(kare)
            return True
        return False

    def _kampkareEkleVeSaldir(self, kare: KampKare) -> bool:
        if self._kampKareEkle(kare):
            if self.kamp_fare:
                return self.kamp_fare.kampSaldiri(bulunan_kamp_karesi=kare)
        return False


def yorumlar():
    ...
    # init_time = time.time()
    # if __name__ == "__main__":
    #     svyT = SeviyeTarayici()
    #     svyT.eminlik  = 0.9
    #     after_svy = time.time()
    #     print(after_svy - init_time)
    #     before_kntrl = time.time()
    #     print(svyT.svyKontrol(svy=4))
    #     after_kntrl = time.time()
    #     print(after_kntrl - before_kntrl)

    #     before_kntrl = time.time()
    #     print(svyT.svyKontrol(svy=5))
    #     after_kntrl = time.time()
    #     print(after_kntrl - before_kntrl)

    # if __name__ == "__main__":
    #     maks_sefer = 6
    #     svy_tarayici = SeviyeTarayici()
    #     sefer_tarayici = SeferTarayici(maks_sefer=maks_sefer)
    #     kamp_fare = KampFare(sefer_tarayici=sefer_tarayici, seviye_tarayici=svy_tarayici)

    #     bes_seviye_kamp_t = KampTarayici(=OnSvyEnum.BES, kamp_fare=kamp_fare)

    #     # alti_seviye_kamp_t = KampTarayici(=OnSvyEnum.ALTI, kamp_fare=kamp_fare)

    #     # bes_seviye_kamp_t_Thread = KampTarayici.threadOlustur()
    #     # bes_seviye_kamp_t_Thread.start()

    #     # alti_seviye_kamp_t_Thread = KampTarayici.threadOlustur()

    #     bes_seviye_kamp_t.islem_baslat()

    # -------------------------------------------------
    # ---------- DENEME FONKSİYONLARI -------------
    # --------------------------------------------


def cascade_kampT_deneme():
    kampT = KampTarayici(kamp_fare=None)
    sleep(0)
    kamp_varmi = kampT.ekranTara(liste_don=False)
    print("kamplar vardi" if kamp_varmi else "kamplar yoktu")


def onsvy_tarama_deneme():
    onsvT = OnSeviyeTarayici(on_svyler=(OnSvyEnum.BES,))
    simdiki_zaman = time.time()
    bulunan_svy = onsvT.svyTara(tarama_alani=KampKare(3075, 1100, 157, 157).onSeviyeTaramaAlaniGetir())
    tarama_sonrasi_zaman = time.time() - simdiki_zaman

    print(tarama_sonrasi_zaman)
    print(bulunan_svy)


def enerji_kontrol_deneme():
    enerji_matcher = MultiImageTemplateMatcher(
        isim="e",
        needle_image_paths=[DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["enerji_resim"])],
        threshold=0.8,
    )
    enerji = ekran_goruntusu_al()
    tarama_alani = Kare(1400, 750, 150, 100)
    ornek_resim = enerji[
        tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
        tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
    ]
    loc = enerji_matcher.match(ornek_resim)
    if loc:
        top_left_x, top_left_y, w, h = loc
        bottom_right_x = top_left_x + w
        bottom_right_y = top_left_y + h
        ornek_resim = cv2.rectangle(
            ornek_resim,
            (top_left_x, top_left_y),
            (bottom_right_x, bottom_right_y),
            (0, 255, 0),
            2,
        )
        cv2.imshow("Matches", ornek_resim)
        print("bulundu")
        cv2.waitKey()
    else:
        print("No match found")
        cv2.imshow("no match found", ornek_resim)


def musamaaktifkontrol_deneme():
    saldir_buton_matcher = MultiImageTemplateMatcher(
        isim="m",
        needle_image_paths=[DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["saldir_buton_resim"])],
        threshold=0.8,
    )
    ana_resim = ekran_goruntusu_al()
    tarama_alani = Kare(1900, 1700, 500, 300)

    ornek_resim = ana_resim[
        tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
        tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
    ]

    loc = saldir_buton_matcher.match(ornek_resim)
    if loc:
        top_left_x, top_left_y, w, h = loc
        bottom_right_x = top_left_x + w
        bottom_right_y = top_left_y + h
        ornek_resim = cv2.rectangle(
            ornek_resim,
            (top_left_x, top_left_y),
            (bottom_right_x, bottom_right_y),
            (0, 255, 0),
            2,
        )
        cv2.imshow("Matches", ornek_resim)
        print(bottom_right_x, bottom_right_y)
    else:
        print("No match found")
        cv2.imshow("no match found", ornek_resim)

    cv2.waitKey()


###alan kontrol
def deneme_alan():
    kampt_T = KampTarayici(None)
    kampkare_listesi = kampt_T.ekranTara(True)
    if kampkare_listesi:
        for ornek_kampkare in kampkare_listesi:
            tarama_alani = ornek_kampkare.onSeviyeTaramaAlaniGetir()
            print(ornek_kampkare)
            screenshot: numpy.array[int, int, int] = ekran_goruntusu_al()
            print(tarama_alani)
            # screenshot = [y,x]
            screenshot_crp = screenshot[
                tarama_alani.y : tarama_alani.yukseklik + tarama_alani.y,
                tarama_alani.x : tarama_alani.genislik + tarama_alani.x,
            ]
            cv2.imshow("cro", screenshot_crp)
            cv2.waitKey(0)
    cv2.destroyAllWindows()


def seferDeneme():
    sfr_tarayici = SeferTarayici(maks_sefer_sayisi=2)
    # print(sfr_tarayici.ornek_ds_yl)
    print(sfr_tarayici.seferSayisiGetir())


def seferMaksDeneme():
    sfr_tarayici = SeferTarayici(maks_sefer_sayisi=2)
    print(sfr_tarayici.seferSayisiGetir())


def calistir_eski():
    onsvy_tarayici = OnSeviyeTarayici(
        on_svyler=(
            OnSvyEnum.BES,
            OnSvyEnum.ALTI,
            # OnSvyEnum.BIR,
            # OnSvyEnum.IKI,
            # OnSvyEnum.UC,
            # OnSvyEnum.ON,
            # OnSvyEnum.ONBIR,
            # OnSvyEnum.ONIKI,
            OnSvyEnum.YEDI,
            # istenilen diger onseviyeler
        )
    )

    sfr_tarayici = SeferTarayici(maks_sefer_sayisi=3)

    kamp_fare_e = KampFare(sefer_tarayici=sfr_tarayici, onseviye_tarayici=onsvy_tarayici)

    kamp_t = KampTarayici(kamp_fare=kamp_fare_e)  # noqa
    bolge_degistirici = BolgeDegistirici()
    mevsim_tarayici = MevsimTara(MevsimTipiEnum.YAZ)

    akis_yonu = (
        KaydirmaYontemleri._kareAlt,  # false
        KaydirmaYontemleri._kareUst,
        KaydirmaYontemleri._kareSag,  # True
        KaydirmaYontemleri._kareSol,  # false
        KaydirmaYontemleri._kareUst,  # True
        KaydirmaYontemleri._kareAlt,  # kale göster,false
        KaydirmaYontemleri._kareSol,
        KaydirmaYontemleri._kareSag,
        # KaydirmaYontemleri._kareAlt,
    )
    kalemi_goster = False
    while True:
        sleep(0)
        kamp_t.kamp_fare.sefer_tarayici.seferMinKontrol()
        bolge_degistirici.bolgeDegistir()
        mevsim_tarayici.mvsmTaraVeIsinlan()
        kalemi_goster = False
        kamp_t.ekranTara()
        for siradaki_yon in akis_yonu:
            # not : sira onemli
            if kalemi_goster:
                kamp_t.kamp_fare.kalemiGoster()
                sleep(0.3)
            siradaki_yon()
            sleep(0.2)
            kamp_t.ekranTara()
            kalemi_goster = not kalemi_goster
            print(
                "------------------------------------------------------------- ",
                kalemi_goster,
            )


def kaydirma_deneme():
    kaydirma = KaydirmaYontemleri()
    i = 0
    while i < 2:
        kaydirma._kareSag()
        kaydirma._kareUst()
        kaydirma._kareSol()
        kaydirma._kareAlt()
        i = i + 1


def mevsim_deneme():
    mvsm = MevsimTara(mevsim=MevsimTipiEnum.YAZ)
    bulunandu_mu = mvsm.mvsmTaraVeIsinlan()
    print(bulunandu_mu)
    print(mvsm.mvsm_template_matcher.needle_image_paths)
    # moveTo((3105,727))


def tus_deneme():
    # Klavye.tuslariBas(("3\n",),.2)
    # Klavye.tuslariBas("".join(("3523", "124")),0.3)
    Klavye.tuslariBas("124 ", 0.25)
    Klavye.tuslariBas("124 ", 0.3)
    Klavye.tuslariBas("124 ", 0.4)


def maksdeneme():
    sf = SeferTarayici(maks_sefer_sayisi=6)
    KampFare(None, None)
    sf.seferMaksKontrol()


class MoeKamp:
    __slots__ = (
        "akis_yonu",
        "arayuz_degiskenleri",
        "bolge_degistirici",
        "faree",
        "kampp",
        "kapat_event",
        "mevsim_tarayici",
        "sfr_tarayici",
        "sinyal_kanal_1",
        "sinyal_kanal_2",
    )

    def __init__(self, arayuz_degiskenleri: dict, sinyal_kanal_1, sinyal_kanal_2) -> None:
        self.kapat_event = multiprocessing.Event()
        self.arayuz_degiskenleri = arayuz_degiskenleri  # (ön seviye, mevsim, maks sefer)
        self.sinyal_kanal_1 = sinyal_kanal_1
        self.sinyal_kanal_2 = sinyal_kanal_2
        onsvy_tarayici = OnSeviyeTarayici(on_svyler=tuple(self.arayuz_degiskenleri["onsvy"]))
        self.sfr_tarayici = SeferTarayici(maks_sefer_sayisi=int(self.arayuz_degiskenleri["sefer"]))

        self.faree = KampFare(sefer_tarayici=self.sfr_tarayici, onseviye_tarayici=onsvy_tarayici)

        self.kampp = KampTarayici(kamp_fare=self.faree)
        self.bolge_degistirici = BolgeDegistirici()
        self.mevsim_tarayici = MevsimTara(self.arayuz_degiskenleri["mevsim"])

        # TODO: belki functools.partial() kullanılmalı
        self.sfr_tarayici._islemDevamEtsinMi = self._devamEdiyorMu
        self.kampp._islemDevamEtsinMi = self._devamEdiyorMu
        self.bolge_degistirici._islemDevamEtsinMi = self._devamEdiyorMu
        self.faree._menudeyimSinyaliYolla = self._MenudeyimSinyaliYolla

        self.akis_yonu = (
            KaydirmaYontemleri._kareAlt,  # false
            KaydirmaYontemleri._kareUst,
            KaydirmaYontemleri._kareSag,  # True
            KaydirmaYontemleri._kareSol,  # false
            KaydirmaYontemleri._kareUst,  # True
            KaydirmaYontemleri._kareAlt,  # kale göster,false
            KaydirmaYontemleri._kareSol,
            KaydirmaYontemleri._kareSag,
            # KaydirmaYontemleri._kareAlt,
        )

    def _devamEdiyorMu(self):
        if self.sinyal_kanal_1.value == ModSinyal.Bekle:
            self.sinyal_kanal_2.value == ModSinyal.MesajUlasti
            while self.sinyal_kanal_1.value == ModSinyal.Bekle:
                print("sinyal bekleniyor")
                sleep(0.5)
            self.sinyal_kanal_2.value == ModSinyal.MesajUlasti
        elif self.sinyal_kanal_1.value == ModSinyal.Sonlandir or self.sinyal_kanal_1.value == ModSinyal.FailSafe:
            self.sinyal_kanal_2.value == ModSinyal.MesajUlasti
            return False
        self.sinyal_kanal_2.value == ModSinyal.MesajUlasmadi
        return True

    def _MenudeyimSinyaliYolla(self, giris=True):
        if giris:
            self.sinyal_kanal_2.value = ModSinyal.Menudeyim
        else:
            self.sinyal_kanal_2.value = ModSinyal.DevamEt

    def kapat(self):
        self.kapatevent.set()

    def _ana_dongu(self):
        kalemi_goster = False
        while True:
            sleep(0)
            if self.kapat_event.is_set():
                break
            self.kampp.kamp_fare.sefer_tarayici.seferMinKontrol()
            self.bolge_degistirici.bolgeDegistir()
            self.mevsim_tarayici.mvsmTaraVeIsinlan()
            kalemi_goster = False
            if self.kampp.ekranTara() is None:
                break

            for siradaki_yon in self.akis_yonu:
                # not : sira onemli
                if kalemi_goster:
                    self.kampp.kamp_fare.kalemiGoster()
                    sleep(0.3)
                siradaki_yon()
                sleep(0.2)
                self.kampp.ekranTara()
                kalemi_goster = not kalemi_goster
                print(
                    "------------------------------------------------------------- ",
                    kalemi_goster,
                )

    def processOlustur(self) -> multiprocessing.Process:
        self.kapat_event = multiprocessing.Event()
        return multiprocessing.Process(target=self.engelKontrol)


def yeni_calistir():
    kanal1 = multiprocessing.Value(ctypes.c_short, ModSinyal.DevamEt)
    kanal2 = multiprocessing.Value(ctypes.c_short, ModSinyal.DevamEt)
    moe_kamp = MoeKamp(
        {
            "onsvy": (OnSvyEnum.DOKUZ,),
            "mevsim": MevsimTipiEnum.YAZ,
            "saat": "12",
            "dakika": "0",
            "sefer": 3,
        },
        kanal1,
        kanal2,
    )
    # print(dir(moe_kamp))
    moe_kamp_process = moe_kamp.processOlustur()
    moe_kamp_process.start()
    moe_kamp_process.join()


if __name__ == "__main__":
    # play = KampFare(None, None)
    # play._musamaAktiflestir()
    # mevsim_deneme()
    # kaydirma_deneme()
    # cascade_kampT_deneme()
    # onsvy_tarama_deneme()
    # deneme_alan()
    # seferDeneme()
    calistir_eski()
    # maksdeneme()
    # musamaaktifkontrol_deneme()
    # enerji_kontrol_deneme()
    # seferMaksDeneme()
    # tus_deneme()
    # """
    # 124 124 124
    # """
