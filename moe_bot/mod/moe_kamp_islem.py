import os
import time
from glob import glob
from pathlib import Path
from time import sleep
from typing import Any, Optional

import cv2
import numpy
import pylightxl as xl
from ayarlar import (
    TIKLAMA_KISITLAMALARI,
    KampSaldiriAyarlar,
    KampTaramaAyarlar,
    Kare,
    Koordinat2D,
    MevsimTipiEnum,
    OnSvyEnum,
    SabitTiklama,
    TumEminlikler,
    TumTaramaBolgeleri,
    ekran_goruntusu_al,
)
from PIL import Image
from pyautogui import center, click, locateOnScreen, mouseDown, mouseUp, moveTo, press, rightClick, scroll, write

# class IsimliDizi:
#     def __init__(self, isim: str, dizi) -> None:
#         self.isim = isim
#         self.iterable = dizi

#     def __iter__(self):
#         for item in self.iterable:
#             yield item


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
    directory_path = ".\img\_3840/"

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
                moveTo(3000, 1200)
                self.rast_yazi = locateOnScreen(
                    self.rastgele_resim,
                    region=TumTaramaBolgeleri["rastgele_bolge"],
                    confidence=TumEminlikler["rastgele_eminlik"],
                    grayscale=self.gri_tarama,
                )
                while self.rast_yazi is None:
                    scroll(-10000)
                    self.rast_yazi2 = locateOnScreen(
                        self.rastgele_resim,
                        region=TumTaramaBolgeleri["rastgele_bolge"],
                        confidence=TumEminlikler["rastgele_eminlik"],
                        grayscale=self.gri_tarama,
                    )
                    if self.rast_yazi2 is not None:
                        self.kullan_buton = locateOnScreen(
                            self.kullan_resim,
                            region=(
                                self.rast_yazi2[0] - 100,
                                self.rast_yazi2[1],
                                1200,
                                500,
                            ),
                            confidence=TumEminlikler["kullan_buton_eminlik"],
                            grayscale=self.gri_tarama,
                        )
                        if self.kullan_buton is None:
                            self.satin_al = locateOnScreen(
                                self.satin_al_resim,
                                region=(
                                    self.rast_yazi2[0] - 100,
                                    self.rast_yazi2[1],
                                    1500,
                                    500,
                                ),
                                confidence=TumEminlikler["satin_al_eminlik"],
                                grayscale=self.gri_tarama,
                            )
                            if self.satin_al is not None:
                                click(self.satin_al)
                                self.kullan_buton = (
                                    locateOnScreen(
                                        self.kullan_resim,
                                        region=(
                                            self.rast_yazi2[0] - 100,
                                            self.rast_yazi2[1],
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
                bolge_x = (bolge_tablosu.address(f"{self.baslangic_konumlari.x[0]}{adim}"),)

                bolge_y = (bolge_tablosu.address(f"{self.baslangic_konumlari.y[0]}{adim}"),)

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
    @staticmethod
    def tus_tek(tus: str):
        press(tus)
        sleep(0.75)

    @staticmethod
    def tuslar(tuslar: list[str] | str):
        if isinstance(tuslar, int):
            tuslar = str(tuslar)
        write(tuslar, interval=0.5)


class BolgeDegistirici(Fare):
    """
    Fare sınıfından türetilmiş BolgeDegistirici sınıfı\n
     -> Fare sınıfının solTikla ve sagTikla metotlarını kullanır\n
     -> BolgeTablosu sınıfından bolge koordinatlarını alır\n
     -> GelismisKare sınıfından kareler oluşturur\n
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
        Klavye.tuslar(tuslar=self.bolge_tablosu[self.hedef_bolge_index].x)
        bul_y_konum = (2050, 350)
        self.solTikla(bul_y_konum)
        Klavye.tuslar(tuslar=self.bolge_tablosu[self.hedef_bolge_index].y)
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
    @staticmethod
    def _kareSol():
        mouseDown(SabitTiklama["sol_nokta"], button="left")
        moveTo(SabitTiklama["sag_nokta"])
        sleep(0.1)
        mouseUp(button="left")
        sleep(0.5)

    @staticmethod
    def _kareSag():
        mouseDown(SabitTiklama["sag_nokta"], button="left")
        moveTo(SabitTiklama["sol_nokta"])
        sleep(0.1)
        mouseUp(button="left")
        sleep(0.5)

    @staticmethod
    def _kareUst():
        mouseDown(SabitTiklama["ust_nokta"], button="left")
        moveTo(SabitTiklama["ust_bitis"])
        sleep(0.1)
        mouseUp(button="left")
        sleep(0.5)

    @staticmethod
    def _kareAlt():
        mouseDown(SabitTiklama["alt_nokta"], button="left")
        moveTo(SabitTiklama["alt_bitis"])
        sleep(0.1)
        mouseUp(button="left")
        sleep(0.5)


class CokluTarayici:
    def __init__(
        self,
        bolge: Kare | None,
        eminlik: float,
        gri_tarama: bool,
        ornek_ds_yl: list[str],
        isim: str = "İsimsiz",
    ) -> None:
        self.isim = isim
        self.bolge = bolge
        self.eminlik = eminlik
        self.gri_tarama = gri_tarama
        self.ornek_ds_yl = ornek_ds_yl

    def _ekranTara(self) -> int | None:
        """
        ilk bulunan örnek dosyanın adının sonundaki sayıyı döndürür\n
        bulunamazsa None döndürür\n
        """
        for ornek_ds_yl in self.ornek_ds_yl:
            kare = locateOnScreen(
                ornek_ds_yl,
                region=self.bolge,
                confidence=self.eminlik,
                grayscale=self.gri_tarama,
            )
            if kare is not None:
                return int(ornek_ds_yl.split(".")[-2].split("_")[-1])
        return None


class SeviyeTarayici(CokluTarayici):
    def __init__(self) -> None:
        eminlik = TumEminlikler["svy_eminlik"]

        ornek_ds_yl: list[str] = DosyaIslemleri.gorselleriGetir(KampTaramaAyarlar["svy"])

        bolge = TumTaramaBolgeleri["seviye"]

        super().__init__(
            bolge=bolge,
            eminlik=eminlik,
            gri_tarama=False,
            ornek_ds_yl=ornek_ds_yl,
            isim="SeviyeTarayici",
        )

    def svyKontrol(self, svy) -> bool:
        """
        açılan kamp sayfasınının en üstündeki seviyenin ön seviye ile aynı olup olmadığını kontrol eder.
        aynı olup olmadığına göre true ya da false (bool) bool
        """
        taramasonucu = self._ekranTara()
        return taramasonucu == svy


class SeferTarayici(CokluTarayici):
    def __init__(
        self,
        maks_sefer_sayisi: int,
    ) -> None:
        isim: str = "SeferTarayici"
        bolge = TumTaramaBolgeleri["sefer_bolge"]
        eminlik = TumEminlikler["sefer_eminlik"]
        gri_tarama = True
        ornek_ds_yl = DosyaIslemleri.gorselleriGetir(KampTaramaAyarlar["sefer"])

        super().__init__(bolge, eminlik, gri_tarama, ornek_ds_yl, isim)

        self.maks_sefer_sayisi = maks_sefer_sayisi
        self.sefer_menusu_acik_mi = None
        self.bekleme_suresi = 1

    def _islemDevamEtsinMi(self) -> bool:
        return True

    def _seferMenusuAcKapat(self):
        press("z")

    def seferSayisiGetir(self) -> int | None:
        """
        -> sefer sayısının kaç olduğunu döner
        ->bulamazsa none döner.
        """

        sefer_sayisi = self._ekranTara()
        sayac = 0
        while sefer_sayisi is None and sayac < 3:
            self._seferMenusuAcKapat()
            sefer_sayisi = self._ekranTara()
            sayac = sayac + 1

        return sefer_sayisi

    def seferMaksKontrol(self) -> bool:
        """
        -> eğer sefer maks ise kodu bekletip sefer sayısının azalmasını bekler
        """
        sefer_sayisi = self.seferSayisiGetir()
        while sefer_sayisi >= self.maks_sefer_sayisi:
            sefer_sayisi = self.seferSayisiGetir()
            moveTo(920, 320)
            sleep(0.5)
            moveTo(1200, 700)
            if self._islemDevamEtsinMi() is False:
                return False
        # FIXME: bulamazsa da true döndüğünden dolayı iyileştirme için sefer sayısını bulmalı
        return True

    def seferMinKontrol(self) -> bool:
        """
        -> sefer sayısı 0 olana kadar bekler
        """
        # FIXME: seferMinKontrol
        sefer_sayisi = self.seferSayisiGetir()
        while sefer_sayisi == 0:
            sefer_sayisi = self.seferSayisiGetir()
            moveTo(1250, 1000)
            sleep(0.5)
            moveTo(900, 1300)
            if self._islemDevamEtsinMi() is False:
                return False
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
        sol_ust_y = int(self.y)
        genislik = int(self.genislik * 4)
        yukseklik = int(self.yukseklik * 3)

        return Kare(sol_ust_x, sol_ust_y, genislik, yukseklik)


class Soguma(CokluTarayici):  #  ENGEL TARAYICI İÇİNE GİDECEK
    def __init__(
        self,
        bolge: Kare | None,
        eminlik: float,
        gri_tarama: True,
    ) -> None:
        self.bolge = bolge
        self.eminlik = eminlik
        self.gri_tarama = gri_tarama

        self.soguma_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["soguma_resim"])
        self.tamam_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["tamam_buton_resim"])

    def sogumaKontrol(self):
        self.sogumada = locateOnScreen(
            self.soguma_resim,
            region=TumTaramaBolgeleri["pop_up_bolge"],
            confidence=TumEminlikler["pop_up_eminlik"],
            grayscale=self.gri_tarama,
        )
        if self.sogumada is not None:
            self.tamam_kontrol = locateOnScreen(
                self.tamam_resim,
                region=TumTaramaBolgeleri["tamam_buton_bolge"],
                confidence=TumEminlikler["tamam_buton_eminlik"],
                grayscale=self.gri_tarama,
            )
            if self.tamam_kontrol is not None:
                click(self.tamam_kontrol)


class OnSeviyeTarayici:
    def __init__(self, on_svyler: tuple[OnSvyEnum]) -> None:
        self.template_matchers: list[MultiImageTemplateMatcher] = []
        for on_svy in on_svyler:
            self.template_matchers.append(
                MultiImageTemplateMatcher(
                    isim=on_svy.value,
                    needle_image_paths=DosyaIslemleri.gorselleriGetir(KampTaramaAyarlar["onsvy_ad"].format(onsvy_val=on_svy.value)),
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
            onsvy_kare = onsvy_template_matcher.match(screenshot_crp)
            if onsvy_kare is not None:
                return onsvy_template_matcher.isim
        return None


#####---------###########-----------##################-------------------################


class MevsimTara:
    def __init__(self, mevsimler: tuple[MevsimTipiEnum]) -> None:
        self.template_matchers: list[MultiImageTemplateMatcher] = []
        for mevsim in mevsimler:
            self.template_matchers.append(
                MultiImageTemplateMatcher(
                    isim=mevsim.value,
                    needle_image_paths=DosyaIslemleri.gorselleriGetir(KampTaramaAyarlar["mvsm"].format(onsvy_val=mevsim.value)),
                ),
            )

    def mvsmTaraVeIsinlan(self, tarama_alani: Kare) -> MevsimTipiEnum | None:
        for mvsm_template_matcher in self.template_matchers:
            screenshot: numpy.array[int, int, int] = ekran_goruntusu_al()
            # screenshot = [y,x]
            tarama_alani = TumTaramaBolgeleri["mevsim_bolge"]
            screenshot_crp = screenshot[
                tarama_alani.y : tarama_alani.y + tarama_alani.yukseklik,
                tarama_alani.x : tarama_alani.x + tarama_alani.genislik,
            ]
            mvsm_kare = mvsm_template_matcher.match(screenshot_crp)
            if mvsm_kare is not None:
                # return mvsm_template_matcher.isim
                # #FIXME return olarak mevsimin adı dönüyor ancak burası tıklamaya uygunluğunu dönecek ve ona göre ışınlanılacak.
                click(center(mvsm_kare))
                isin_kontrol = locateOnScreen(
                    DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["isinlanma_resim"]),
                    region=TumTaramaBolgeleri["isinlanma_bolge"],
                    confidence=TumEminlikler["isinlanma_eminlik"],
                    grayscale=True,
                )
                if isin_kontrol is not None:
                    click(center(isin_kontrol))

        return None  # FIXME None dönmemesi gereiyor. ışınlanacak yer bulana kadar taramaya devam.


#####---------###########-----------##################-------------------################


class KampFare:
    def __init__(self, sefer_tarayici: SeferTarayici, onseviye_tarayici: OnSeviyeTarayici) -> None:
        self.enerji_matcher = MultiImageTemplateMatcher(
            isim="e",
            needle_image_paths=[DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["enerji_resim"])],
            threshold=0.8,
        )
        self.musama_aktif_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["musama_aktif_resim"])
        self.musama_liste_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["musama_liste_resim"])
        self.cikiskamp_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["cikiskamp_resim"])
        self.hizli_saldir = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["hizli_saldir_resim"])
        self.satin_al_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["satin_al_resim"])
        self.kullan_resim = DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["kullan_buton_resim"])
        self.kalemi_goster_matcher = MultiImageTemplateMatcher(
            isim="_kalemiGoster",
            needle_image_paths=[DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["kalemi_goster.png"])],
            threshold=0.8,
        )
        self.saldir_buton_matcher = MultiImageTemplateMatcher(
            isim="m",
            needle_image_paths=[DosyaIslemleri.gorselGetir(KampSaldiriAyarlar["saldir_buton_resim"])],
            threshold=0.8,
        )

        self.tiklama_kisitlamalari = TIKLAMA_KISITLAMALARI
        self.sefer_tarayici = sefer_tarayici
        self.onsvy_tarayici = onseviye_tarayici

        self.musama_sure_kontrol = 0
        self.ilk_saldiri = False

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
            click(SabitTiklama["saldir_sayac"])
            self.musama_liste_kontrol = locateOnScreen(
                self.musama_liste_resim,
                region=TumTaramaBolgeleri["musama_liste_resim"],
                confidence=TumEminlikler,
                grayscale=True,
            )
            if self.musama_liste_kontrol is not None:
                click(center(self.musama_liste_kontrol))
                self.kullan_btn_kontrol = locateOnScreen(
                    self.kullan_resim,
                    region=TumTaramaBolgeleri["musama_kullan_bolge"],
                    confidence=TumEminlikler["kullan_buton_eminlik"],
                    grayscale=True,
                )
                if self.kullan_btn_kontrol is not None:
                    click(center(self.kullan_btn_kontrol))
                    self.musama_sure_kontrol = time.time()
                else:
                    self.satin_al_buton_kontrol = locateOnScreen(
                        self.satin_al_resim,
                        region=TumTaramaBolgeleri["satin_al_resim"],
                        confidence=TumEminlikler["satin_al_eminlik"],
                        grayscale=True,
                    )
                    if self.satin_al_buton_kontrol is not None:
                        click(center(self.satin_al_buton_kontrol))
                        self.kullan_btn_kontrol = locateOnScreen(
                            self.kullan_resim,
                            region=TumTaramaBolgeleri["kullan_resim"],
                            confidence=TumEminlikler["kullan_buton_eminlik"],
                            grayscale=True,
                        )
                        if self.kullan_btn_kontrol is not None:
                            click(center(self.kullan_btn_kontrol))
                            self.musama_sure_kontrol = time.time()

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
        self.cikiskamp_resim_kontrol = locateOnScreen(
            self.cikiskamp_resim,
            region=TumTaramaBolgeleri["cikiskamp_resim"],
            confidence=TumTaramaBolgeleri["cikiskamp_bolge"],
            grayscale=True,
        )
        if self.cikiskamp_resim_kontrol is not None:
            click(center(self.cikiskamp_resim_kontrol))

    def _kalemiGoster(self):
        """
        ->Tarama yapılmadan önce kaleyi ekranda ortalar.
        """
        self.kalemi_goster_resim_kontrol = ekran_goruntusu_al()
        self.tarama_alani = TumTaramaBolgeleri["kalemi_goster_bolge"]
        ornek_resim = self.kalemi_goster_resim_kontrol[
            self.tarama_alani.y : self.tarama_alani.y + self.tarama_alani.yukseklik,
            self.tarama_alani.x : self.tarama_alani.x + self.tarama_alani.genislik,
        ]
        self.loc = self.kalemi_goster_matcher.match(ornek_resim)
        if self.loc is not None:
            click(center(self.loc))

    def kampSaldiri(self, bulunan_kamp_karesi: KampKare):
        """
        ->bulunan kamp karenin altındaki  karesi taranıp uygun olan seviyeler içindki görsellerden
            -> görsel bulunursa tıklama yapılıp hızlı saldırı yapılacak.
        """

        tarama_alani = bulunan_kamp_karesi.onSeviyeTaramaAlaniGetir()
        bolge_kisitlimi = self._bolge_kisitlimi(bulunan_kamp_karesi.merkez())
        if bolge_kisitlimi:
            return False
        if self.sefer_tarayici.seferMaksKontrol():
            seviye = self.onsvy_tarayici.svyTara(tarama_alani)
            if seviye is not None:
                click(bulunan_kamp_karesi.merkez())
                sleep(0.4)

                # menü açlıdı (kamp menüsü)

                if self._musamaAktifKontrol() is False and self.ilk_saldiri:
                    self._musamaAktiflestir()

                # tikla
                click(SabitTiklama["hizli_saldiri"])
                self.ilk_saldiri = True

        # FIXME tıklama öncesi veya sonrası ihtiyaca göre _musamaAktifKontrol
        # FIXME self.onseviye_tarayici kullanılıp seviye belirlenecek ve ona göre tıklama yapılacak


class KampTarayici:
    """
    Önce önseviyeyi tarayıp sonrasında
    bulduğu ön seviyenin üzerindeki bölgede kamp tipini tarar ver tıklama yapar."""

    def __init__(self, kamp_fare: KampFare | None = None) -> None:
        cascade_xml = DosyaIslemleri.cascadeGetir(KampTaramaAyarlar["kamp_tip_cascade"])
        self.CascadeClassifier = cv2.CascadeClassifier(cascade_xml)
        self.kamp_fare = kamp_fare
        self.kamp_kareleri = set()

    def _islemDevamEtsinMi(self) -> bool:
        return True

    def ekranTara(self, liste_don=False) -> bool | set | None:
        gecici_kareler = self.CascadeClassifier.detectMultiScale(ekran_goruntusu_al())
        for gecici_kare in gecici_kareler:
            islem_devam_etsin_mi = self._islemDevamEtsinMi()
            if not islem_devam_etsin_mi:
                return  # eğer işlem devam etmiyorsa erkenden tarama iptali
            if gecici_kare is not None:
                bulunan_kare = KampKare(
                    int(gecici_kare[0]),
                    int(gecici_kare[1]),
                    int(gecici_kare[2]),
                    int(gecici_kare[3]),
                )
                islem_devam_etsin_mi = self._kampkareEkleVeSaldir(bulunan_kare)
            del islem_devam_etsin_mi

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

    def _kampkareEkleVeSaldir(self, kare: KampKare) -> bool | None:
        if self._kampKareEkle(kare):
            # FIXME :  DENEME YAPILIRKEN PASS YORUMDAN ÇIKARILCAK
            # pass

            if self.kamp_fare:
                return self.kamp_fare.kampSaldiri(bulunan_kamp_karesi=kare)


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


def calistir():
    onsvy_tarayici = OnSeviyeTarayici(
        on_svyler=(
            OnSvyEnum.BES,
            # OnSvyEnum.ALTI
            # OnSvyEnum.BES,
            # istenilen diger onseviyeler
        )
    )

    sfr_tarayici = SeferTarayici(maks_sefer_sayisi=2)

    kamp_fare_e = KampFare(sefer_tarayici=sfr_tarayici, onseviye_tarayici=onsvy_tarayici)

    kamp_t = KampTarayici(kamp_fare=kamp_fare_e)  # noqa

    kamp_t.ekranTara()


def kaydirma_deneme():
    kaydirma = KaydirmaYontemleri()
    i = 0
    while i < 2:
        kaydirma._kareSag()
        kaydirma._kareUst()
        kaydirma._kareSol()
        kaydirma._kareAlt()
        i = i + 1


if __name__ == "__main__":
    # play = KampFare(None, None)
    # play._musamaAktiflestir()
    # kaydirma_deneme()
    # cascade_kampT_deneme()
    # onsvy_tarama_deneme()
    # deneme_alan()
    # seferDeneme()
    calistir()
    # musamaaktifkontrol_deneme()
    # enerji_kontrol_deneme()
