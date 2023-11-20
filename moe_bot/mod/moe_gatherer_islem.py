from __future__ import annotations

import functools
import logging
import multiprocessing
from enum import Enum, auto
from pathlib import Path
from time import sleep, time_ns
from typing import Any, Callable, Optional

import pylightxl as xl
from pyautogui import FailSafeException, locateAllOnScreen, locateOnScreen

from moe_bot.ayarlar import Ayarlar
from moe_bot.enumlar import IslemSinyal
from moe_bot.gunlukcu import Gunlukcu  # noqa
from moe_bot.hatalar import Hata, KullaniciHatasi
from moe_bot.mod.moe_genel import DosyaIslemleri
from moe_bot.tarayicilar import PyAutoTarayici
from moe_bot.temel_fonksiyonlar import ifItsNone, tipVeyaNone
from moe_bot.temel_siniflar import Fare, GelismisKare, Kare, Klavye, Koordinat2D
from moe_bot.types import Event


class KaynakTipi(Enum):
    EKMEK = auto()
    ODUN = auto()
    TAS = auto()
    DEMIR = auto()
    GUMUS = auto()
    ALTIN = auto()


class MoeGatherer:
    __slots__ = ("_sinyal_alma_knl", "_sinyal_gonderme_knl" + "_process") + (
        # mod spesifik degiskenler
        "_klavye",
        "_ayarlar",
    )  # type: ignore

    _mod_ad = "moe_gatherer"
    _aktif: Event

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        cls.__init__(*args, **kwargs)
        return cls.instance

    @functools.cached_property
    def _gunlukcu(self) -> logging.Logger:
        return logging.getLogger("moe_gatherer")

    @functools.cached_property
    def ayarlar(self) -> Ayarlar.ModAyarlari:
        if self._aktifmi():
            return self._ayarlar
        from moe_bot.ayarlar import moe_gatherer

        self._ayarlar = moe_gatherer.ayarları_olustur()
        return self._ayarlar

    @staticmethod
    def tiklamaNoktasiGetir(nokta_adi: str) -> Koordinat2D:
        return MoeGatherer.ayarlar.ekstra_ayarlar["tiklama_noktalari"][nokta_adi]  # type: ignore

    @staticmethod
    def tarayiciGetir(t_adi: str) -> tuple[str, float, Optional[Kare]]:
        return MoeGatherer.ayarlar.tarayicilar[t_adi]  # type: ignore

    @functools.cached_property
    def klavye(self) -> Klavye:
        if not hasattr(self, "_klavye"):
            self._klavye = Klavye()
        return self._klavye

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
            MoeGatherer._gunlukcu.info("bolge tablosu okunuyor.")  # type: ignore
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

                MoeGatherer._gunlukcu.info("bolge tablosu okundu.")  # type: ignore
                MoeGatherer._gunlukcu.debug(f"bolge tablosu: {self.bolgeler}")  # type: ignore
            except Exception as e:
                raise Hata(f"{e}: bolge tablosu okunamadı")

        def __len__(self):
            return len(self.bolgeler)

        def __getitem__(self, __val: int):
            return self.bolgeler[__val]

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
            self.bolge_tablosu = MoeGatherer.BolgeTablosu()
            self.bolge_tablosu.excelOku()
            self.hedef_bolge_index: int = 0

            MoeGatherer._gunlukcu.debug(f"BolgeDegistirici.__init__ -> {self.__repr__()}")  # type: ignore

        def _sonrakiBolge(self):
            """
            BolgeTablosundan sonraki bolgeyi alır\n
            """
            self.hedef_bolge_index += 1
            if self.hedef_bolge_index >= len(self.bolge_tablosu):
                self.hedef_bolge_index = 0
            MoeGatherer._gunlukcu.debug(f"BolgeDegistirici._sonrakiBolge -> {self.hedef_bolge_index}")  # type: ignore

        def bolgeDegistir(self):
            self._bolgeDegistir(self.bolge_tablosu[self.hedef_bolge_index])

        def _bolgeDegistir(self, bolge: Koordinat2D) -> None:
            """
            BolgeTablosundan elde edilen bolgenin x y koordinatlarını alır\n
            -> buyutec ikonuna tıklar\n
            ve x y koordinatlarını kullanarak bolgeyi değiştirir\n
            """
            bul_ikonu_konum = MoeGatherer.tiklamaNoktasiGetir("bul_ikon")
            self.solTikla(bul_ikonu_konum)
            Klavye.tuslariBas((self.bolge_tablosu[self.hedef_bolge_index].x))
            bul_y_konum = MoeGatherer.tiklamaNoktasiGetir("bul_y")
            self.solTikla(bul_y_konum)
            Klavye.tuslariBas((self.bolge_tablosu[self.hedef_bolge_index].y))
            buyutec_ikonu_konum = MoeGatherer.tiklamaNoktasiGetir("buyutec_ikon")
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
            MoeGatherer._gunlukcu.debug(f"{self.__str__()}__init__ -> {self.__repr__()}")  # type: ignore

        def _ekranTara(self) -> Optional[int]:
            """
            ilk bulunan örnek dosyanın indeksinin liste uzunluğundan çıkarılmış halini döndürür\n
            bulunamazsa None döndürür\n
            """
            MoeGatherer._gunlukcu.debug(f"{self.__str__}._ekranTara -> {self.__repr__()}")  # type: ignore
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
                    MoeGatherer._gunlukcu.debug(f"{self.isim} -> {ornek_d=}, {i=}, bulunan kare : {kare}")  # type: ignore
                    if self.isim.startswith("SvyTarayici"):
                        return len(self.ornek_dler) - i
                    return i
            return None

        def __str__(self) -> str:
            return self.isim

        def __repr__(self) -> str:
            return f"{self.isim} bolge:{self.bolge} eminlik:{self.eminlik} gri_tarama:{self.gri_tarama} ornek_dler:{self.ornek_dler}"

    class SvyTarayici(CokluTarayici):
        def __init__(
            self,
            # eminlik: float = MoeGatherer.eminlikGetir("svy"),
            eminlik: float = 0.9,
            bolge: Optional[Kare] = None,
            kaynak_tipi: Optional[KaynakTipi] = None,
        ) -> None:
            if type(kaynak_tipi) is KaynakTipi:
                self.ornek_dler: list[str] = DosyaIslemleri.gorselleriGetir(
                    gorsel_id=str(kaynak_tipi.name + "_svy"), sirala=True
                )  # siralamak önemli
            else:
                self.ornek_dler: list[str] = DosyaIslemleri.gorselleriGetir(gorsel_id="svy", sirala=True)

            # siralama = True -> svy_10.png, svy_9.png, ... svy_1.png
            if bolge is not None and Kare.gecersizMi(bolge):
                bolge = MoeGatherer.taramaBolgesiGetir("svy")

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
                bolge = MoeGatherer.taramaBolgesiGetir("sefer")
            super().__init__(
                bolge=ifItsNone(bolge, MoeGatherer.taramaBolgesiGetir("sefer")),
                eminlik=ifItsNone(eminlik, MoeGatherer.eminlikGetir("sefer")),
                gri_tarama=True,  # FIXME gri_tarama icin varsayılanlar sozlugu
                ornek_dler=DosyaIslemleri.gorselleriGetir("sefer"),
                isim="SeferTarayici",
            )  # type:ignore

            self.maks_sefer_sayisi = maks_sefer_sayisi if maks_sefer_sayisi > 0 else 0
            self.sefer_menusu_acik_mi = None  # çalışma anında değişmeli

        def _islemDevamEtsinMi(self) -> bool:
            """
            bu fonksiyonu override ederek process event set edilmis mi diye bakabiliriz
            """
            return True

        def _seferMenusuAcKapat(self):
            Klavye.tuslariBas("z")

        def seferKontrol(self, bekleme_suresi=1) -> bool | None:
            # eğer sefer sayisi full ise tekrar azalana kadar bekle

            sefer_sayisi = self._ekranTara()
            sayac = 0
            while sefer_sayisi is None and sayac < 3:
                MoeGatherer._gunlukcu.debug(f"sefer sayisi bulunamadi tekrar bakılıyor , deneme:{sayac}")  # type: ignore
                self._seferMenusuAcKapat()
                # sleep(UYUMA_SURESI)
                sefer_sayisi = self._ekranTara()
                sayac += 1

            if sefer_sayisi is not None:
                MoeGatherer._gunlukcu.debug("bulunan sefer sayisi %d" % sefer_sayisi)  # type: ignore

                while sefer_sayisi >= self.maks_sefer_sayisi:  # noqa
                    # tarama sırasında tarama yaptığı belli olsun diye fareyi hareket ettiriyoruz bir ileri bir geri

                    if not self._islemDevamEtsinMi():
                        return False
                    MoeGatherer._gunlukcu.debug("sefer sayisi maksimum azalması bekleniyor")  # type: ignore
                    Fare.hareketEt((400, 200))  # type: ignore
                    sefer_sayisi = self._ekranTara()
                    Fare.hareketEt((600, 400))  # type: ignore
                self._seferMenusuAcKapat()
                return True
            return False

    class KaynakFare(Fare):
        def __init__(self, maks_sefer_sayisi: Optional[int] = None, svyler: tuple[int, ...] = ()) -> None:
            super().__init__()

            self.tiklama_kisitlamalari = MoeGatherer.TIKLAMA_KISITLAMALARI  # FIXME: TIKLAMA_KISITLAMALARI
            # self.svy_tarayici = SvyTarayici(bolge=taramaBolgesiGetir("svy"))
            self.isgal_durumu = PyAutoTarayici(
                DosyaIslemleri.gorselGetir("isgal_durumu"),
                bolge=MoeGatherer.taramaBolgesiGetir("isgal_durumu"),
                eminlik=MoeGatherer.eminlikGetir("isgal_durumu"),
                gri_tarama=True,
            )

            # FIXME geçici olarak iptal edilmiştir.

            # self.sehir_ikon_tarayici = Tarayici(
            #     DosyaIslemleri.gorselGetir("sehir_ikonu"),
            #     bolge=taramaBolgesiGetir("sehir_ikonu"),
            #     eminlik=eminlikGetir("sehir_ikonu"),
            # )

            self.isgal_butonu_konumu = MoeGatherer.tiklamaNoktasiGetir("isgal_1")
            self.isgal_butonu2_konumu = MoeGatherer.tiklamaNoktasiGetir("isgal_2")
            self.isgal_duzeni_konumu = MoeGatherer.tiklamaNoktasiGetir("isgal_duzeni")
            if maks_sefer_sayisi is not None:
                self.sefer_tarayici = MoeGatherer.SeferTarayici(maks_sefer_sayisi)

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

        def kaynakTikla(self, kaynak_kare: GelismisKare, svy_tarayici: MoeGatherer.SvyTarayici) -> bool | None:
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
            MoeGatherer._gunlukcu.debug(  # type: ignore
                f"bolge kisitli tiklama yapılmayacak {kaynak_kare=}"
                if bolge_kisitlimi
                else f"bolge kistili değil tıklama yapılacak {kaynak_kare=}"
            )
            if bolge_kisitlimi:
                return False

            if self.sefer_tarayici.seferKontrol() is False:
                "eğer false ise islem devam etmiyor demek"
                MoeGatherer._gunlukcu.debug("sefer kontrol false dondu tiklama islemi yarım bırakılıyor.")  # type: ignore
                return

            self.solTikla(tiklama_konumu)

            isgal_durumu_kare = self.isgal_durumu.ekranTara()
            MoeGatherer._gunlukcu.debug(f"{isgal_durumu_kare=}")  # type: ignore
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

    class KaynakTarayici:
        def __init__(
            self,
            tip: KaynakTipi = KaynakTipi.ODUN,
            kaynak_fare: Optional[MoeGatherer.KaynakFare] = None,
        ):
            self.tip = tip
            self.ornek_dler: list[str] = []
            self.kaynak_kareleri: set[GelismisKare] = set()
            self.kaynak_fare = kaynak_fare if isinstance(kaynak_fare, MoeGatherer.KaynakFare) else None
            self.svy_tarayici = MoeGatherer.SvyTarayici(kaynak_tipi=self.tip)
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
            MoeGatherer._gunlukcu.debug(f"{self.tip} için tarama başladı {tarama_baslangic}")
            for ornek_d in self.ornek_dler:
                gecici_auto_kareler = locateAllOnScreen(ornek_d, confidence=eminlik)
                for py_auto_gui_kare in gecici_auto_kareler:
                    islem_devam_etsin_mi = self._islemDevamEtsinMi()
                    if not islem_devam_etsin_mi:
                        MoeGatherer._gunlukcu.debug(f"{self.tip} için tarama durduruldu,islemDevamEtsinMi False döndü")
                        return

                    if py_auto_gui_kare is not None:
                        bulunan_kare = GelismisKare(
                            py_auto_gui_kare[0],
                            py_auto_gui_kare[1],
                            py_auto_gui_kare[2],
                            py_auto_gui_kare[3],
                        )
                        MoeGatherer._gunlukcu.debug(f"{self.tip} için taramada,{bulunan_kare=}")
                        islem_devam_etsin_mi = self._kaynakKareEkleVeTopla(bulunan_kare)
                        # TODO : tek kaynak toplamasına neden oluyor (bilmediğim bir noktadan none dönüyr)
                        # if islem_devam_etsin_mi is None:
                        #     MoeGatherer._gunlukcu.debug(f"{self.tip} için tarama durduruldu,kaynakFare.kaynakTikla False döndü")
                        #     return
                    del islem_devam_etsin_mi

            tarama_bitis = time_ns()
            MoeGatherer._gunlukcu.debug(
                f"{self.tip} için tarama bitti ,gecen süre {tarama_bitis-tarama_baslangic},bulunan kareler {self.kaynak_kareleri}"
            )
            if len(self.kaynak_kareleri) > 0:
                if liste_don:
                    return self.kaynak_kareleri
                # bütün tarama ve toplama işlemleri biter ve set hala dolu olursa temizle
                MoeGatherer._gunlukcu.debug(f"tarama sonucu {self.kaynak_kareleri=}.", extra={"tip": self.tip})
                self._kaynak_kareleriTemizle()
                return True
            return False

        def _kaynakKareEkle(self, kare: GelismisKare) -> bool:
            if len(self.kaynak_kareleri) == 0:
                self.kaynak_kareleri.add(kare)
                return True

            kareler_elenmis = [kare.disindaMi(essiz_kare) for essiz_kare in self.kaynak_kareleri]
            MoeGatherer._gunlukcu.debug(f"{kareler_elenmis=}", extra={"tip": self.tip})
            if all(kareler_elenmis):
                self.kaynak_kareleri.add(kare)
                MoeGatherer._gunlukcu.debug(f"kareler_elenmise yeni kare eklendi {kare=}")
                return True
            return False

        def _kaynakKareEkleVeTopla(self, kare: GelismisKare) -> bool | None:
            if self._kaynakKareEkle(kare):
                MoeGatherer._gunlukcu.debug(f"kaynak kare tiklaniyor {kare=}")
                if self.kaynak_fare:
                    return self.kaynak_fare.kaynakTikla(kaynak_kare=kare, svy_tarayici=self.svy_tarayici)
                MoeGatherer._gunlukcu.debug(f"kaynak kare tiklanamadi , self.kaynak_fare {self.kaynak_fare=}")

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
            tiklayici: Optional[MoeGatherer.KaynakFare] = None,
            islemDevamEtsinmiFonk: Optional[Callable[[], bool]] = None,
        ) -> None:
            if tiklayici is None:
                tiklayici = MoeGatherer.KaynakFare()

            self.tiklayici = tiklayici
            self.tarayicilar = [MoeGatherer.KaynakTarayici(KaynakTipi(tip), self.tiklayici) for tip in tipler]
            self.bolge_degistirici = MoeGatherer.BolgeDegistirici()

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
            MoeGatherer._gunlukcu.debug(f" tarama başladı. {self.tarayicilar},zaman:{tarama_baslangic}")
            self.bolge_degistirici.bolgeDegistir()
            for tarayici in self.tarayicilar:
                tarayici.ekranTara(eminlik)

            tarama_bitis = time_ns()
            MoeGatherer._gunlukcu.debug(f" tarama bitti.tarama_bitis: {tarama_bitis},  gecen süre: {tarama_bitis - tarama_baslangic}")

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
            MoeGatherer.Varsayilanlar.olustur()
            self.acikmi_event = multiprocessing.Event()
            self.kaynak_yonetici: MoeGatherer.TarayiciYonetim = MoeGatherer.TarayiciYonetim(
                tipler=kaynak_tipleri,
                tiklayici=MoeGatherer.KaynakFare(svyler=svyler, maks_sefer_sayisi=maks_sefer_sayisi),
                islemDevamEtsinmiFonk=self.acikmi,
            )
            MoeGatherer._gunlukcu.debug(msg=f"tarama işlemi oluşturuldu, {id(self)}")

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
                    MoeGatherer._gunlukcu.debug(f"FailSafeException yakalandı, {pyautogui_failsafe_exc}")
                    self._sinyal_gonderme.value = IslemSinyal.FAILSAFE_SONLANDIR
                except OSError as os_err:
                    MoeGatherer._gunlukcu.debug(f"OSError yakalandı, {os_err}")
                    sleep(5)  # 5 saniye bekle ve tekrar dene
                except Exception as exc:
                    MoeGatherer._gunlukcu.debug(f"Exception yakalandı, {exc}")
                    self._sinyal_gonderme.value = IslemSinyal.DUR

        def acikmi(self) -> bool:
            #  __tarama_islemi_gunlukcu().debug(
            #     f'tarama işlemi çalışmaya devam edecek mi kontrol edildi: {not self.acikmi_event.is_set()=}'
            # )   # type: ignore
            MoeGatherer._gunlukcu.debug(f"sinyal kontrol : {self._sinyal_alma.value=} {self._sinyal_gonderme.value=}")
            while self._sinyal_alma.value == IslemSinyal.DUR:
                self._sinyal_gonderme.value = IslemSinyal.MESAJ_ULASTI
                sleep(3)
                if self._sinyal_alma.value == IslemSinyal.DEVAM_ET:
                    self._sinyal_gonderme.value = IslemSinyal.MESAJ_ULASTI
                    break
            if self._sinyal_alma.value == IslemSinyal.DEVAM_ET:
                self._sinyal_gonderme.value = IslemSinyal.MESAJ_ULASTI
            if self._sinyal_alma.value == IslemSinyal.SONLANDIR:
                self._sinyal_gonderme.value = IslemSinyal.SONLANDIR
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
