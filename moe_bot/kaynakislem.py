import logging
import multiprocessing
from dataclasses import dataclass
from functools import cache
from glob import glob
from pathlib import Path
from time import sleep, time_ns
from typing import Any, Callable, Optional

import pylightxl as xl
from pyautogui import click, locateAllOnScreen, locateOnScreen, moveTo, press, rightClick
from pyautogui import size as _ekranBoyutu
from pyautogui import write, FailSafeException

from .gunlukcu import Gunlukcu  # noqa
from .hatalar import Hata, KullaniciHatasi
from .sabilter import TaramaSabitleri, BASE_PATH, UYUMA_SURESI
from .temel_fonksiyonlar import ifItsNone, tipVeyaNone
from .temel_siniflar import EkranBoyut, IslemSinyalleri, Kare, KaynakKare, KaynakTipi, Koordinat2D

# TODO : pyautogui -> locateOnScreen ' e wrapper yaz (engeltarayici arada çalışsın)
# def _ekranTara(locateOnScreen:Callable,*args,**kwargs):
#     '''
#     wraps pyautogui.locateOnScreen
#     '''
#     if EngelTarayici().engelKontrol():

# TODO : secili_svyler [11,12,13] -> dler = [kaynak_svy_11,kaynak_svy_12,kaynak_svy_13]

_gunlukcu = logging.getLogger()


def ekranBoyutuEtiketi(EkranBoyut: EkranBoyut) -> str:
    return f"_{EkranBoyut.genislik}"


def aktifEkranBoyutu() -> EkranBoyut:
    aktif_ekran_boyutu = _ekranBoyutu()
    aktif_ekran_boyutu = EkranBoyut(aktif_ekran_boyutu.width, aktif_ekran_boyutu.height)
    if aktif_ekran_boyutu not in TaramaSabitleri.EKRAN_BOYUTLARI.values():
        raise KullaniciHatasi(f"aktif ekran çözünürlüğü {str(aktif_ekran_boyutu)}, bu çözünürlük desteklenmiyor.")
    return aktif_ekran_boyutu


@cache
def aktifEkranBoyutuEtiketi():
    return ekranBoyutuEtiketi(aktifEkranBoyutu())


def _glob_dsn_sozluk_olustur(ekran_boyut_etiket: str) -> dict[str, str]:
    return {K: f"{TaramaSabitleri.DOSYA_YOLLARI[1]}/{ekran_boyut_etiket}/{V}" for K, V in TaramaSabitleri.GLOB_DSNLER.items()}


@dataclass(frozen=True)
class Varsayilanlar:
    """
    çalışma başlangıcında belirlenen varsayılan değerler
    dinamik olarak değişir (sadece ilk çalışmada)
    """

    @classmethod
    def olustur(cls):
        cls.EKRAN_BOYUT_ETIKETI = ekranBoyutuEtiketi(aktifEkranBoyutu())

        cls.GLOB_DSNLER = _glob_dsn_sozluk_olustur(cls.EKRAN_BOYUT_ETIKETI)

        cls.TARAMA_BOLGELERI = TaramaSabitleri.TARAMA_BOLGELERI[cls.EKRAN_BOYUT_ETIKETI]

        cls.TIKLAMA_KISITLAMALARI = TaramaSabitleri.TIKLAMA_KISITLAMALARI[cls.EKRAN_BOYUT_ETIKETI]

        cls.TIKLAMA_NOKTALARI = TaramaSabitleri.TIKLAMA_NOKTALARI[cls.EKRAN_BOYUT_ETIKETI]

        cls.EMINLIKLER = TaramaSabitleri.EMINLIKLER[cls.EKRAN_BOYUT_ETIKETI]

        cls.PROCESS_OLARAK_CALISMA = True  # hardcoded , belki ilerde toggle edilebilir olur

        _gunlukcu.debug("varsayilanlar oluşturuldu.")

    EKRAN_BOYUT_ETIKETI = ekranBoyutuEtiketi(aktifEkranBoyutu())

    GLOB_DSNLER = _glob_dsn_sozluk_olustur(EKRAN_BOYUT_ETIKETI)

    TARAMA_BOLGELERI = TaramaSabitleri.TARAMA_BOLGELERI[EKRAN_BOYUT_ETIKETI]

    TIKLAMA_KISITLAMALARI = TaramaSabitleri.TIKLAMA_KISITLAMALARI[EKRAN_BOYUT_ETIKETI]

    TIKLAMA_NOKTALARI = TaramaSabitleri.TIKLAMA_NOKTALARI[EKRAN_BOYUT_ETIKETI]

    EMINLIKLER = TaramaSabitleri.EMINLIKLER[EKRAN_BOYUT_ETIKETI]

    PROCESS_OLARAK_CALISMA = True  # hardcoded , belki ilerde toggle edilebilir olur

    _gunlukcu.debug("varsayilanlar oluşturuldu.")


class Klavye:
    @staticmethod
    def tus_tek(tus: str):
        # _gunlukcu.info(f"{tus} tuşuna basılıyor.")
        press(tus)
        sleep(UYUMA_SURESI / 1.5)

    @staticmethod
    def tuslar(tuslar: list[str] | str):
        # _gunlukcu.info(f"{tuslar} tuşlarına basılıyor.")
        if isinstance(tuslar, int):
            tuslar = str(tuslar)
        write(tuslar, interval=UYUMA_SURESI / 1.5)


def tiklamaNoktasiGetir(nokta_adi: str) -> Koordinat2D:
    return Varsayilanlar.TIKLAMA_NOKTALARI[nokta_adi]


def eminlikGetir(eminlik_adi: str) -> float:
    return Varsayilanlar.EMINLIKLER[eminlik_adi]


def eminlikleriGetir(key_baslangic: str) -> tuple[float, ...]:
    eminlikler = []
    for eminlik in Varsayilanlar.EMINLIKLER.keys():
        if eminlik.startswith(key_baslangic):
            eminlikler.append(eminlikGetir(eminlik))
    return tuple(eminlikler)


def taramaBolgesiGetir(bolge_adi: str) -> Kare:
    return Varsayilanlar.TARAMA_BOLGELERI[bolge_adi]


# global gerektiren fonksiyonlar
# TODO: Daha iyi bir çözüm bulunmalı
#   - belki tüm siniflar bir sinifblogu içinde toplanabilir


@cache
def klavyeGetir() -> Klavye:
    # gunlukcuGetir().info("klavye oluşturuluyor.")
    if "klavye" not in globals():
        global _klavye
        _klavye = Klavye()
    return _klavye


@cache
def gunlukcuGetir() -> logging.Logger:
    return logging.getLogger("kaynak_islemi")


class BolgeTablosu:
    """
    Bolge tablosu sınıfı\n
    -> Excel dosyasından bolge tablosunu okur\n
    -> Bolge tablosundan bolge koordinatlarını alır\n
    -> Bolge tablosundan bolge sayısını alır\n
    """

    baslangic_konumlari = Koordinat2D("C4", "D4")

    bolgeler: list[Koordinat2D]
    bolge_sayisi: int

    def excelOku(self, dosya_yolu: str | Path = Path("./coordinates/regions.xlsx")) -> None:
        _gunlukcu.info("bolge tablosu okunuyor.")
        try:
            self.bolgeler = []
            bolge_excel = xl.readxl(fn=dosya_yolu)
            bolge_tablosu = bolge_excel.ws(ws="Bolge Tablosu")
            baslangic = int(self.baslangic_konumlari.x[1])
            self.bolge_sayisi = tipVeyaNone(
                int,
                bolge_tablosu.address(f"{self.baslangic_konumlari.x[0]}{str(baslangic - 2 )}"),
            )  # type: ignore
            if self.bolge_sayisi is None:
                raise KullaniciHatasi("bolge sayısı okunamadı", "bolge tablosu")

            bitis = baslangic + self.bolge_sayisi

            for adim in range(baslangic, bitis):
                bolge_x = tipVeyaNone(
                    int,
                    bolge_tablosu.address(f"{self.baslangic_konumlari.x[0]}{adim}"),
                )
                if bolge_x is None:
                    raise KullaniciHatasi("bolge C{adim} okunamadı", "bolge tablosu")

                bolge_y = tipVeyaNone(
                    int,
                    bolge_tablosu.address(f"{self.baslangic_konumlari.y[0]}{adim}"),
                )
                if bolge_y is None:
                    raise KullaniciHatasi("bolge D{adim} okunamadı", "bolge tablosu")

                self.bolgeler.append(Koordinat2D(bolge_x, bolge_y))

            _gunlukcu.info("bolge tablosu okundu.")
            _gunlukcu.debug(f"bolge tablosu: {self.bolgeler}")
        except Exception as e:
            raise Hata(f"{e}: bolge tablosu okunamadı")

    def __len__(self):
        return len(self.bolgeler)

    def __getitem__(self, __val: int):
        return self.bolgeler[__val]


class DosyaIslemleri:
    @staticmethod
    def globCoz(glob_dsn: str) -> list[str]:
        """
        glob_dsn : str
        sirala : bool = False
            -> uzanti olmadan , tersten sıralar
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
        glob_dsn = Varsayilanlar.GLOB_DSNLER[gorsel_id]
        dosyalar = DosyaIslemleri.globCoz(glob_dsn)

        if len(dosyalar) == 0:
            raise ValueError(f"Gorsel bulunamadı : {gorsel_id}, glob_dsn : {glob_dsn}, base_path : {BASE_PATH}")

        if sirala:
            dosyalar.sort(key=lambda x: int(x.split(".")[-2].split("_")[-1]), reverse=True)

        gunlukcuGetir().debug(f"gorselleri_getir -> gorsel_id : {gorsel_id},  glob_dsn: {glob_dsn}, bulunan dosyalar : {dosyalar}")
        return dosyalar


class Fare:
    @staticmethod
    def sagTikla(uyuma_suresi=UYUMA_SURESI):
        _gunlukcu.debug("sağ tıklandı")
        sleep(uyuma_suresi)
        rightClick()
        sleep(uyuma_suresi)

    @staticmethod
    def solTikla(konum: Optional[Koordinat2D] = None, uyuma_suresi=UYUMA_SURESI):
        _gunlukcu.debug(f"sol tıklanıyor , konum: {str(konum)}")
        sleep(uyuma_suresi)
        click(konum)
        sleep(uyuma_suresi)


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

        gunlukcuGetir().debug(f"BolgeDegistirici.__init__ -> {self.__repr__()}")

    def _sonrakiBolge(self):
        """
        BolgeTablosundan sonraki bolgeyi alır\n
        """
        self.hedef_bolge_index += 1
        if self.hedef_bolge_index >= len(self.bolge_tablosu):
            self.hedef_bolge_index = 0
        gunlukcuGetir().debug(f"BolgeDegistirici._sonrakiBolge -> {self.hedef_bolge_index}")

    def bolgeDegistir(self):
        self._bolgeDegistir(self.bolge_tablosu[self.hedef_bolge_index])

    def _bolgeDegistir(self, bolge: Koordinat2D) -> None:
        """
        BolgeTablosundan elde edilen bolgenin x y koordinatlarını alır\n
        -> buyutec ikonuna tıklar\n
        ve x y koordinatlarını kullanarak bolgeyi değiştirir\n
        """
        bul_ikonu_konum = tiklamaNoktasiGetir("bul_ikon")
        self.solTikla(bul_ikonu_konum)
        klavyeGetir().tuslar((self.bolge_tablosu[self.hedef_bolge_index].x))
        bul_y_konum = tiklamaNoktasiGetir("bul_y")
        self.solTikla(bul_y_konum)
        klavyeGetir().tuslar(self.bolge_tablosu[self.hedef_bolge_index].y)
        buyutec_ikonu_konum = tiklamaNoktasiGetir("buyutec_ikon")
        self.solTikla(buyutec_ikonu_konum)
        self._sonrakiBolge()

    def __repr__(self) -> str:
        return f"{self.bolge_tablosu=}"

    def _islemDevamEtsinMi(self) -> bool:
        """
        instance override edilecek
        """
        return True


class CokluTarayici:
    """
    birden fazla örnek dosya ile tarama yapar\n
    svy ve sefer tarayıcıları için temel sınıf\n
    """

    def __init__(
        self,
        bolge: Optional[Kare],
        eminlik: float,
        gri_tarama: bool,
        ornek_dler: list[str],
        isim: str = "İsimsiz",
    ) -> None:
        """
        bolge:Kare  -> tarama yapılacak bölge\n
        eminlik:float -> tarama yapılırken kullanılacak eminlik\n
        gri_tarama:bool -> tarama gri mi yapılsın \n
        ornk_dler:list[str] -> tarama yapılacak örnek dosyalarin dosya yollari listesi\n
        """
        # self.isim = isim + f"_{self.__class__.__name__}_" + str(id(self))
        self.isim = isim + "_" + str(id(self))
        self.bolge = bolge
        self.eminlik = eminlik
        self.gri_tarama = gri_tarama
        self.ornek_dler = ornek_dler
        gunlukcuGetir().debug(f"{self.__str__()}__init__ -> {self.__repr__()}")

    def _ekranTara(self) -> Optional[int]:
        """
        ilk bulunan örnek dosyanın indeksinin liste uzunluğundan çıkarılmış halini döndürür\n
        bulunamazsa None döndürür\n
        """
        gunlukcuGetir().debug(f"{self.__str__}._ekranTara -> {self.__repr__()}")
        for i, ornek_d in enumerate(self.ornek_dler):
            if self.bolge is None:
                kare = locateOnScreen(ornek_d, confidence=self.eminlik, grayscale=self.gri_tarama)
            else:
                kare = locateOnScreen(
                    ornek_d,
                    region=self.bolge,
                    confidence=self.eminlik,
                    grayscale=self.gri_tarama,
                )
            if kare is not None:
                gunlukcuGetir().debug(f"{self.isim} -> {ornek_d=}, {i=}, bulunan kare : {kare}")
                if self.isim.startswith("SvyTarayici"):
                    return len(self.ornek_dler) - i
                return i
        return None

    def __str__(self) -> str:
        return self.isim

    def __repr__(self) -> str:
        return f"{self.isim} bolge:{self.bolge} eminlik:{self.eminlik} gri_tarama:{self.gri_tarama} ornek_dler:{self.ornek_dler}"


class SvyTarayici(CokluTarayici):
    def __init__(self, eminlik=eminlikGetir("svy"), bolge: Optional[Kare] = None, kaynak_tipi: Optional[KaynakTipi] = None) -> None:
        if type(kaynak_tipi) is KaynakTipi:
            self.ornek_dler: list[str] = DosyaIslemleri.gorselleriGetir(
                gorsel_id=str(kaynak_tipi.name + "_svy"), sirala=True
            )  # siralamak önemli
        else:
            self.ornek_dler: list[str] = DosyaIslemleri.gorselleriGetir(gorsel_id="svy", sirala=True)

        # siralama = True -> svy_10.png, svy_9.png, ... svy_1.png
        if bolge is not None and Kare.gecersizMi(bolge):
            bolge = taramaBolgesiGetir("svy")

        self.eminlik = eminlik
        super().__init__(bolge=bolge, eminlik=eminlik, gri_tarama=False, ornek_dler=self.ornek_dler, isim="SvyTarayici")
        self.ekranTara = self._ekranTara


class SeferTarayici(CokluTarayici):
    def __init__(
        self,
        maks_sefer_sayisi: int,
        eminlik: Optional[float] = None,
        bolge: Optional[Kare] = None,
    ) -> None:
        if bolge is not None and Kare.gecersizMi(bolge):
            bolge = taramaBolgesiGetir("sefer")
        super().__init__(
            bolge=ifItsNone(bolge, taramaBolgesiGetir("sefer")),
            eminlik=ifItsNone(eminlik, eminlikGetir("sefer")),
            gri_tarama=True,  # FIXME gri_tarama icin varsayılanlar sozlugu
            ornek_dler=DosyaIslemleri.gorselleriGetir("sefer"),
            isim="SeferTarayici",
        )  # type:ignore

        self.maks_sefer_sayisi = maks_sefer_sayisi
        self.sefer_menusu_acik_mi = None  # çalışma anında değişmeli

    def _islemDevamEtsinMi(self) -> bool:
        """
        bu fonksiyonu override ederek process event set edilmis mi diye bakabiliriz
        """
        return True

    def _seferMenusuAcKapat(self):
        klavyeGetir().tus_tek("z")

    def seferKontrol(self, bekleme_suresi=1) -> bool | None:
        # eğer sefer sayisi full ise tekrar azalana kadar bekle

        sefer_sayisi = self._ekranTara()
        sayac = 0
        while sefer_sayisi is None and sayac < 3:
            gunlukcuGetir().debug(f"sefer sayisi bulunamadi tekrar bakılıyor , deneme:{sayac}")
            self._seferMenusuAcKapat()
            # sleep(UYUMA_SURESI)
            sefer_sayisi = self._ekranTara()
            sayac += 1

        if sefer_sayisi is not None:
            gunlukcuGetir().debug("bulunan sefer sayisi %d" % sefer_sayisi)

            while sefer_sayisi == self.maks_sefer_sayisi:
                # tarama sırasında tarama yaptığı belli olsun diye fareyi hareket ettiriyoruz bir ileri bir geri

                if not self._islemDevamEtsinMi():
                    return False
                gunlukcuGetir().debug("sefer sayisi maksimum azalması bekleniyor")
                moveTo((400, 200))
                sleep(bekleme_suresi)
                sefer_sayisi = self._ekranTara()
                moveTo((600, 400))
            self._seferMenusuAcKapat()
            return True
        return False


class KaynakFare(Fare):
    def __init__(self, maks_sefer_sayisi: Optional[int] = None, svyler: tuple[int, ...] = ()) -> None:
        super().__init__()

        self.tiklama_kisitlamalari = Varsayilanlar.TIKLAMA_KISITLAMALARI
        # self.svy_tarayici = SvyTarayici(bolge=taramaBolgesiGetir("svy"))
        self.isgal_durumu = Tarayici(
            DosyaIslemleri.gorselGetir("isgal_durumu"),
            bolge=taramaBolgesiGetir("isgal_durumu"),
            eminlik=eminlikGetir("isgal_durumu"),
            gri_tarama=True,
        )

        # FIXME geçici olarak iptal edilmiştir.

        # self.sehir_ikon_tarayici = Tarayici(
        #     DosyaIslemleri.gorselGetir("sehir_ikonu"),
        #     bolge=taramaBolgesiGetir("sehir_ikonu"),
        #     eminlik=eminlikGetir("sehir_ikonu"),
        # )

        self.isgal_butonu_konumu = tiklamaNoktasiGetir("isgal_1")
        self.isgal_butonu2_konumu = tiklamaNoktasiGetir("isgal_2")
        self.isgal_duzeni_konumu = tiklamaNoktasiGetir("isgal_duzeni")
        if maks_sefer_sayisi is not None:
            self.sefer_tarayici = SeferTarayici(maks_sefer_sayisi)

        self.svyler = svyler

    #  __tarama_islemi_gunlukcu().debug(f'KaynakFare.__init__ -> {self.__repr__()}')

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

    def kaynakTikla(self, kaynak_kare: KaynakKare, svy_tarayici: SvyTarayici) -> bool | None:
        """
        belirtilen kaynak karesin tıklar\n
        eğer kaynak kare isgal edilmemişse ve seviye uygunsa sefer yollar\n
        diğer durumlarda sag tiklama ile geri döner\n
        """
        if self._islemDevamEtsinMi.__doc__ != "instance override edilecek":
            # Rembember: instance override edilecek
            self.sefer_tarayici._islemDevamEtsinMi = self._islemDevamEtsinMi

        tiklama_konumu = kaynak_kare.merkez()
        bolge_kisitlimi = self._bolge_kisitlimi(tiklama_konumu)
        gunlukcuGetir().debug(
            f"bolge kisitli tiklama yapılmayacak {kaynak_kare=}"
            if bolge_kisitlimi
            else f"bolge kistili değil tıklama yapılacak {kaynak_kare=}"
        )
        if bolge_kisitlimi:
            return False

        if self.sefer_tarayici.seferKontrol() is False:
            "eğer false ise islem devam etmiyor demek"
            gunlukcuGetir().debug("sefer kontrol false dondu tiklama islemi yarım bırakılıyor.")
            return

        self.solTikla(tiklama_konumu)

        isgal_durumu_kare = self.isgal_durumu.ekranTara()
        gunlukcuGetir().debug(f"{isgal_durumu_kare=}")
        if isgal_durumu_kare:
            if len(self.svyler) == 0 | len(self.svyler) > 13:
                return self._seferYolla()
            else:
                seviye = svy_tarayici.ekranTara()
                if seviye in self.svyler:
                    return self._seferYolla()
                else:
                    self.sagTikla()
                    return False
        else:
            self.sagTikla()
            return False

    def _seferYolla(self) -> bool | None:
        """
        basması gereken butonların konumlarını tespit eder ve tıklayarak sefer yollar
        """
        self.solTikla(self.isgal_butonu_konumu)
        self.solTikla(self.isgal_duzeni_konumu)
        self.solTikla(self.isgal_butonu2_konumu)

    def _islemDevamEtsinMi(self) -> bool:
        """instance override edilecek"""
        return True


class Tarayici:
    def __init__(
        self,
        ornek_d: str,
        eminlik: float,
        bolge: Optional[Kare] = None,
        gri_tarama: bool = False,
        isim="İsimsiz",
    ) -> None:
        self.isim = isim + f"_{self.__class__.__name__}_" + str(id(self))  # debug için
        if bolge is not None and Kare.gecersizMi(bolge):
            bolge = None
        self.bolge = bolge

        self.ornek_d = ornek_d
        self.eminlik = eminlik
        self.gri_tarama = gri_tarama
        gunlukcuGetir().debug(f"{self.__str__()}__init__ -> {self.__repr__()}")

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.ekranTara()

    def ekranTara(self) -> None | KaynakKare:
        if self.bolge is None:
            kare = locateOnScreen(self.ornek_d, confidence=self.eminlik, grayscale=self.gri_tarama)
        else:
            kare = locateOnScreen(
                self.ornek_d,
                region=self.bolge,
                confidence=self.eminlik,
                grayscale=self.gri_tarama,
            )
        gunlukcuGetir().debug(f"{self.__str__()} ekranTara -> {kare}")
        if kare:
            return KaynakKare(kare.left, kare.top, kare.width, kare.height)
        return None

    def __str__(self) -> str:
        return self.isim

    def __repr__(self) -> str:
        return f"Tarayici_{self.isim=},{self.bolge=},{self.ornek_d=},{self.eminlik=},{self.gri_tarama=}"


class KaynakTarayici:
    def __init__(
        self,
        tip: KaynakTipi = KaynakTipi.ODUN,
        kaynak_fare: Optional[KaynakFare] = None,
    ):
        self.tip = tip
        self.ornek_dler: list[str] = []
        self.kaynak_kareleri: set[KaynakKare] = set()
        self.kaynak_fare = kaynak_fare if isinstance(kaynak_fare, KaynakFare) else None
        self.svy_tarayici = SvyTarayici(kaynak_tipi=self.tip)
        # kare * frame anlamında *
        self._dosyaTara()
        # self.kaynak_fare._islemDevamEtsinMi = self._islemDevamEtsinMi

    def _dosyaTara(self) -> None:
        self.ornek_dler = DosyaIslemleri.gorselleriGetir(self.tip.name)

    def _islemDevamEtsinMi(self) -> bool:
        """
        bu fonksiyonu override ederek process event set edilmis mi diye bakabiliriz
        """
        return True

    def ekranTara(self, eminlik: float = 0.7, liste_don=False) -> bool | set | None:
        """
        eğer herhangi bir kaynak bulunamazsa False döndürür, bulunursa True döndürür
        liste_don = True ise bulunan kaynak karelerini döndürür
        """
        tarama_baslangic = time_ns()
        gunlukcuGetir().debug(f"{self.tip} için tarama başladı {tarama_baslangic}")
        for ornek_d in self.ornek_dler:
            gecici_auto_kareler = locateAllOnScreen(ornek_d, confidence=eminlik)
            for py_auto_gui_kare in gecici_auto_kareler:
                islem_devam_etsin_mi = self._islemDevamEtsinMi()
                if not islem_devam_etsin_mi:
                    gunlukcuGetir().debug(f"{self.tip} için tarama durduruldu,islemDevamEtsinMi False döndü")
                    return

                if py_auto_gui_kare is not None:
                    bulunan_kare = KaynakKare(
                        py_auto_gui_kare[0],
                        py_auto_gui_kare[1],
                        py_auto_gui_kare[2],
                        py_auto_gui_kare[3],
                    )
                    gunlukcuGetir().debug(f"{self.tip} için taramada,{bulunan_kare=}")
                    islem_devam_etsin_mi = self._kaynakKareEkleVeTopla(bulunan_kare)
                    # TODO : tek kaynak toplamasına neden oluyor (bilmediğim bir noktadan none dönüyr)
                    # if islem_devam_etsin_mi is None:
                    #     gunlukcuGetir().debug(f"{self.tip} için tarama durduruldu,kaynakFare.kaynakTikla False döndü")
                    #     return
                del islem_devam_etsin_mi

        tarama_bitis = time_ns()
        gunlukcuGetir().debug(
            f"{self.tip} için tarama bitti ,gecen süre {tarama_bitis-tarama_baslangic},bulunan kareler {self.kaynak_kareleri}"
        )
        if len(self.kaynak_kareleri) > 0:
            if liste_don:
                return self.kaynak_kareleri
            # bütün tarama ve toplama işlemleri biter ve set hala dolu olursa temizle
            gunlukcuGetir().debug(f"tarama sonucu {self.kaynak_kareleri=}.", extra={"tip": self.tip})
            self._kaynak_kareleriTemizle()
            return True
        return False

    def _kaynakKareEkle(self, kare: KaynakKare) -> bool:
        if len(self.kaynak_kareleri) == 0:
            self.kaynak_kareleri.add(kare)
            return True

        kareler_elenmis = [kare.disindaMi(essiz_kare) for essiz_kare in self.kaynak_kareleri]
        gunlukcuGetir().debug(f"{kareler_elenmis=}", extra={"tip": self.tip})
        if all(kareler_elenmis):
            self.kaynak_kareleri.add(kare)
            gunlukcuGetir().debug(f"kareler_elenmise yeni kare eklendi {kare=}")
            return True
        return False

    def _kaynakKareEkleVeTopla(self, kare: KaynakKare) -> bool | None:
        if self._kaynakKareEkle(kare):
            gunlukcuGetir().debug(f"kaynak kare tiklaniyor {kare=}")
            if self.kaynak_fare:
                return self.kaynak_fare.kaynakTikla(kaynak_kare=kare, svy_tarayici=self.svy_tarayici)
            gunlukcuGetir().debug(f"kaynak kare tiklanamadi , self.kaynak_fare {self.kaynak_fare=}")

    def _kaynak_kareleriTemizle(self):
        self.kaynak_kareleri.clear()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.tip=})_({id(self)})"

    def __str__(self) -> str:
        return self.__repr__()


class TarayiciYonetim:
    def __init__(
        self,
        tipler: tuple[KaynakTipi, ...],
        tiklayici: Optional[KaynakFare] = None,
        islemDevamEtsinmiFonk: Optional[Callable[[], bool]] = None,
    ) -> None:
        if tiklayici is None:
            tiklayici = KaynakFare()

        self.tiklayici = tiklayici
        self.tarayicilar = [KaynakTarayici(KaynakTipi(tip), self.tiklayici) for tip in tipler]
        self.bolge_degistirici = BolgeDegistirici()

        if islemDevamEtsinmiFonk is not None:
            self._islemDevamEtsinMi = islemDevamEtsinmiFonk
            self._p_init()

    def _p_init(self):
        """
        egere islemDevamEtsinMi fonskiyonu verilirse, bu fonksiyon kendi tarayicilari, bolge degistirici, tiklayiciya ekler
        """
        for tarayici in self.tarayicilar:
            tarayici._islemDevamEtsinMi = self._islemDevamEtsinMi
        self.bolge_degistirici._islemDevamEtsinMi = self._islemDevamEtsinMi
        self.tiklayici._islemDevamEtsinMi = self._islemDevamEtsinMi

    def _islemDevamEtsinMi(self) -> bool:
        """
        bu fonksiyonu override ederek process event set edilmis mi diye bakabiliriz
        """
        return True

    def ekranTara(self, eminlik: float = 0.8):
        tarama_baslangic = time_ns()
        gunlukcuGetir().debug(f" tarama başladı. {self.tarayicilar},zaman:{tarama_baslangic}")
        self.bolge_degistirici.bolgeDegistir()
        for tarayici in self.tarayicilar:
            tarayici.ekranTara(eminlik)

        tarama_bitis = time_ns()
        gunlukcuGetir().debug(f" tarama bitti.tarama_bitis: {tarama_bitis},  gecen süre: {tarama_bitis - tarama_baslangic}")


class TaramaIslem:
    """
    tarayici yönetimin işlem döngüsünü yönetir\n
    --> tarama, tıklama, kaynakları toplama, kaynakları temizleme\n
    --> klavye yönetim ile etkileşim\n
    """

    def __init__(
        self,
        maks_sefer_sayisi: int,
        kaynak_tipleri: tuple[KaynakTipi, ...],
        svyler: tuple[int, ...] = (),
    ) -> None:
        """
        # -> secili kaynaklara göre kaynak tarayici oluştur
        """
        Varsayilanlar.olustur()
        self.acikmi_event = multiprocessing.Event()
        self.kaynak_yonetici: TarayiciYonetim = TarayiciYonetim(
            tipler=kaynak_tipleri,
            tiklayici=KaynakFare(svyler=svyler, maks_sefer_sayisi=maks_sefer_sayisi),
            islemDevamEtsinmiFonk=self.acikmi,
        )
        gunlukcuGetir().debug(msg=f"tarama işlemi oluşturuldu, {id(self)}")

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.otoKaynakToplama()

    def otoKaynakToplama(self):
        """ana işlem döngüsü gerçekleştiren fonksiyon\n"""
        while True:
            try:
                if not self.acikmi():
                    break
                self.kaynak_yonetici.ekranTara(0.7)
            except FailSafeException as pyautogui_failsafe_exc:
                gunlukcuGetir().debug(f"FailSafeException yakalandı, {pyautogui_failsafe_exc}")
                self._sinyal_gonderme.value = IslemSinyalleri.FAILSAFE_SONLANDIR
            except OSError as os_err:
                gunlukcuGetir().debug(f"OSError yakalandı, {os_err}")
                sleep(5)  # 5 saniye bekle ve tekrar dene
            except Exception as exc:
                gunlukcuGetir().debug(f"Exception yakalandı, {exc}")
                self._sinyal_gonderme.value = IslemSinyalleri.DUR

    def acikmi(self) -> bool:
        #  __tarama_islemi_gunlukcu().debug(
        #     f'tarama işlemi çalışmaya devam edecek mi kontrol edildi: {not self.acikmi_event.is_set()=}'
        # )   # type: ignore
        gunlukcuGetir().debug(f"sinyal kontrol : {self._sinyal_alma.value=} {self._sinyal_gonderme.value=}")
        while self._sinyal_alma.value == IslemSinyalleri.DUR:
            self._sinyal_gonderme.value = IslemSinyalleri.MESAJ_ULASTI
            sleep(3)
            if self._sinyal_alma.value == IslemSinyalleri.DEVAM_ET:
                self._sinyal_gonderme.value = IslemSinyalleri.MESAJ_ULASTI
                break
        if self._sinyal_alma.value == IslemSinyalleri.DEVAM_ET:
            self._sinyal_gonderme.value = IslemSinyalleri.MESAJ_ULASTI
        if self._sinyal_alma.value == IslemSinyalleri.SONLANDIR:
            self._sinyal_gonderme.value = IslemSinyalleri.SONLANDIR
            self.kapat()
            return False
        if self.acikmi_event.is_set():  # type: ignore
            return False
        return True

    def kapat(self):
        self.acikmi_event.set()

    def _yeniEvent(self):
        self.acikmi_event = multiprocessing.Event()

    def __repr__(self) -> str:
        return super().__repr__() + f"_{id(self)}"

    def __str__(self) -> str:
        return self.__str__()

    def processOlustur(self, sinyal_alma, sinyal_gonderme):
        self._yeniEvent()
        self._sinyal_alma = sinyal_alma
        self._sinyal_gonderme = sinyal_gonderme
        return multiprocessing.Process(target=self, name="tarama_islemi")

    # def __str__(self) -> str:
    #     return f'{self.__class__.__name__}_{id(self)}_{self.kaynak_yonetici}'

    # def __repr__(self) -> str:
    #     return f'{self.__class__.__name__}_{id(self)}'
