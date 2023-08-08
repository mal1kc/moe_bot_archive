import ctypes
import logging
import multiprocessing
from time import sleep

from .temel_siniflar import IslemSinyalleri
from .sabitler import ENGEL_KONTROL_SURESI
from .kaynakislem import DosyaIslemleri, Fare, Tarayici, eminlikGetir, taramaBolgesiGetir


class EngelTarayiciİslem:
    def __init__(self) -> None:
        self._gunlukcuBaslat()
        dler = (
            DosyaIslemleri.gorselGetir("sehir_ikonu"),
            DosyaIslemleri.gorselGetir("moe_logo"),
            DosyaIslemleri.gorselGetir("hizmet_basarisiz"),
            DosyaIslemleri.gorselGetir("baglanti_kesildi"),
            DosyaIslemleri.gorselGetir("dunya_ikonu"),
            DosyaIslemleri.gorselGetir("maks_Sefer"),
            DosyaIslemleri.gorselGetir("tekrar_dene"),
            DosyaIslemleri.gorselGetir("mavi_tamam"),
            DosyaIslemleri.gorselGetir("geri_ok"),
            DosyaIslemleri.gorselGetir("tamam_buton"),
            DosyaIslemleri.gorselGetir("oyundan_cik"),
        )
        eminlikler = (
            eminlikGetir("sehir_ikonu"),
            eminlikGetir("moe_logo"),
            eminlikGetir("hizmet_basarisiz"),
            eminlikGetir("baglanti_kesildi"),
            eminlikGetir("dunya_ikonu"),
            eminlikGetir("maks_Sefer"),
            eminlikGetir("tekrar_dene"),
            eminlikGetir("mavi_tamam"),
            eminlikGetir("geri_ok"),
            eminlikGetir("tamam_buton"),
            eminlikGetir("oyundan_cik"),
        )
        bolgeler = (
            taramaBolgesiGetir("sehir_ikonu"),
            taramaBolgesiGetir("moe_logo"),
            taramaBolgesiGetir("hizmet_basarisiz"),
            taramaBolgesiGetir("baglanti_kesildi"),
            taramaBolgesiGetir("dunya_ikonu"),
            taramaBolgesiGetir("maks_Sefer"),
            taramaBolgesiGetir("tekrar_dene"),
            taramaBolgesiGetir("mavi_tamam"),
            taramaBolgesiGetir("geri_ok"),
            taramaBolgesiGetir("tamam_buton"),
            taramaBolgesiGetir("oyundan_cik"),
        )
        self.sehirIkon_tarayici = Tarayici(
            ornek_d=dler[0], eminlik=eminlikler[0], bolge=bolgeler[0], gri_tarama=True, isim="engelTarayici.sehirIkon_tarayici"
        )
        self.moeLogo_tarayici = Tarayici(
            ornek_d=dler[1], eminlik=eminlikler[1], bolge=bolgeler[1], gri_tarama=True, isim="engelTarayici.moeLogo_tarayici"
        )
        self.hizmetBasarisiz_tarayici = Tarayici(
            ornek_d=dler[2], eminlik=eminlikler[2], bolge=bolgeler[2], gri_tarama=True, isim="engelTarayici.hizmetBasarisiz_tarayici"
        )
        self.baglantiKesildi_tarayici = Tarayici(
            ornek_d=dler[3], eminlik=eminlikler[3], bolge=bolgeler[3], gri_tarama=True, isim="engelTarayici.baglantiKesildi_tarayici"
        )
        self.dunyaIkon_tarayici = Tarayici(
            ornek_d=dler[4], eminlik=eminlikler[4], bolge=bolgeler[4], gri_tarama=True, isim="engelTarayici.dunyaIkon_tarayici"
        )
        self.maksSeferUyari_tarayici = Tarayici(
            ornek_d=dler[5], eminlik=eminlikler[5], bolge=bolgeler[5], gri_tarama=True, isim="engelTarayici.maksSeferUyari_tarayici"
        )
        self.tekrarDeneButon_tarayici = Tarayici(
            ornek_d=dler[6], eminlik=eminlikler[6], bolge=bolgeler[6], gri_tarama=True, isim="engelTarayici.tekrarDeneButon_tarayici"
        )
        self.maviTamam_tarayici = Tarayici(
            ornek_d=dler[7], eminlik=eminlikler[7], bolge=bolgeler[7], gri_tarama=True, isim="engelTarayici.maviTamam_tarayici"
        )
        self.geriOk_tarayici = Tarayici(
            ornek_d=dler[8], eminlik=eminlikler[8], bolge=bolgeler[8], gri_tarama=True, isim="engelTarayici.geriOk_tarayici"
        )
        self.tamam_tarayici = Tarayici(
            ornek_d=dler[9], eminlik=eminlikler[9], bolge=bolgeler[9], gri_tarama=True, isim="engelTarayici.tamam_tarayici"
        )

    def _gunlukcuBaslat(self) -> None:
        self.gunlukcu = logging.getLogger("engelTarayiciİslem")
        self.gunlukcu.debug("gunlukcu baslatidi")

    def engelKontrol(self) -> None:
        def _sehirIkonuTara() -> bool:
            _sehirIkonKare = self.sehirIkon_tarayici.ekranTara()
            if _sehirIkonKare is None:
                self._sinyalYolla(IslemSinyalleri.DUR)
                _sehirYoksa()
            return True

        def _geriOkTara() -> None:
            self.gunlukcu.debug("geri ok tarama basladi")
            _geriok_kare = self.geriOk_tarayici.ekranTara()
            if _geriok_kare is not None:
                self._sinyalYolla(IslemSinyalleri.DUR)
                self._sinyalBekle()
                Fare.solTikla(_geriok_kare.merkez())

        # FIXME oyundan çıkış engeli kaldırma

        def _sehirYoksa() -> None:
            _dunyaIkon_kare = self.dunyaIkon_tarayici.ekranTara()
            if _dunyaIkon_kare is not None:
                Fare.solTikla(_dunyaIkon_kare.merkez())
                if _sehirIkonuTara():
                    self._sinyalYolla(IslemSinyalleri.DEVAM_ET)
                self.gunlukcu.debug("_sehirYoksa :-> sehir ikonu bulunamadi")
            self.gunlukcu.debug("_sehirYoksa :-> dünya ikonu bulunamadi")

        def _hizmetBasarisizTara():
            if self.hizmetBasarisiz_tarayici.ekranTara() is not None:
                self._sinyalYolla(IslemSinyalleri.DUR)
                _yenidenDeneButonTikla()
                self._sinyalYolla(IslemSinyalleri.DEVAM_ET)

        def _baglantiKesildiTara():
            if self.baglantiKesildi_tarayici.ekranTara() is not None:
                # exit sinyali
                self._sinyalYolla(IslemSinyalleri.SONLANDIR)

        def _maksSeferUyariTara():
            if self.maksSeferUyari_tarayici.ekranTara() is not None:
                self._sinyalYolla(IslemSinyalleri.DUR)
                Fare.sagTikla()

                Fare.sagTikla()
                Fare.sagTikla()
                self._sinyalYolla(IslemSinyalleri.DEVAM_ET)

        def _yenidenDeneButonTikla():
            yenidenDeneButon_Kare = self.tekrarDeneButon_tarayici.ekranTara()
            if yenidenDeneButon_Kare is not None:
                sleep(ENGEL_KONTROL_SURESI)
                Fare.solTikla(yenidenDeneButon_Kare.merkez())

        def _maviTamamTara():
            maviTamamUyari_kare = self.maviTamam_tarayici.ekranTara()
            if maviTamamUyari_kare is not None:
                self._sinyalYolla(IslemSinyalleri.DUR)
                Fare.sagTikla()
                maviTamamUyari_kare = self.maviTamam_tarayici.ekranTara()
                if maviTamamUyari_kare is not None:
                    Fare.sagTikla()
                self._sinyalYolla(IslemSinyalleri.DEVAM_ET)

        # def _tamam2UyariTara() -> bool:
        #     tamam2Uyari_kare = self.tamam2Uyari_tarayici.ekranTara()
        #     if tamam2Uyari_kare is not None:
        #         self._sinyalYolla(IslemSinyalleri.DUR)
        #         Fare.sagTikla()
        #         if self.seferDuzenLogo_tarayici.ekranTara() is not None:
        #             Fare.sagTikla()
        #             Fare.sagTikla()
        #         self._sinyalYolla(IslemSinyalleri.DEVAM_ET)

        def _moeLogoBekle() -> None:
            while self.moeLogo_tarayici.ekranTara() is None:
                self._sinyalYolla(IslemSinyalleri.DUR)
                sleep(ENGEL_KONTROL_SURESI)
                _yenidenDeneButonTikla()
            self._sinyalYolla(IslemSinyalleri.DEVAM_ET)

        while True and self._acikmi():
            # _moeLogoBekle()
            _baglantiKesildiTara()
            _hizmetBasarisizTara()
            _maviTamamTara()
            _geriOkTara()
            _sehirIkonuTara()
            # _oyundancikisTara
            _maksSeferUyariTara()

            sleep(ENGEL_KONTROL_SURESI)

    def _sinyalYolla(self, sinyal) -> None:
        self.gunlukcu.debug("sinyal goderildi.")
        self._sinyal_gonderme = sinyal
        self._sinyalBekle()

    def _sinyalBekle(self) -> None:
        self.gunlukcu.debug("sinyal bekleniyor")
        while self._sinyal_alma == IslemSinyalleri.MESAJ_ULASMADI:
            self.gunlukcu.debug("sinyal ulasmasi bekleniyor")
            sleep(0.1)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}_(sinyal={self._sinyal.value})"  # type: ignore

    def _acikmi(self) -> bool:
        return not self.acik_event.is_set()

    def processOlustur(self) -> multiprocessing.Process:
        self._gunlukcuBaslat()
        self._sinyal_gonderme = multiprocessing.Value(ctypes.c_short, IslemSinyalleri.DEVAM_ET)
        self._sinyal_alma = multiprocessing.Value(ctypes.c_short, IslemSinyalleri.MESAJ_ULASMADI)
        self.acik_event = multiprocessing.Event()
        return multiprocessing.Process(target=self.engelKontrol)
