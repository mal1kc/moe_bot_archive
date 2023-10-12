import logging
import multiprocessing
from time import sleep

from moe_bot.temel_siniflar import Kare

from .enumlar import ModSinyal
from .sabilter import ENGEL_KONTROL_SURESI
from .kaynakislem import (
    DosyaIslemleri,
    Fare,
    Tarayici,
    eminlikGetir,
    taramaBolgesiGetir,
    tiklamaNoktasiGetir,
)


class EngelTarayiciİslem:
    def __init__(self) -> None:
        self._gunlukcuBaslat()
        dler: tuple[str, ...] = (
            DosyaIslemleri.gorselGetir("sehir_ikonu"),
            DosyaIslemleri.gorselGetir("moe_logo"),
            DosyaIslemleri.gorselGetir("hizmet_basarisiz"),
            DosyaIslemleri.gorselGetir("baglanti_kesildi"),
            DosyaIslemleri.gorselGetir("dunya_ikonu"),
            DosyaIslemleri.gorselGetir("maks_sefer"),
            DosyaIslemleri.gorselGetir("tekrar_dene"),
            DosyaIslemleri.gorselGetir("mavi_tamam"),
            DosyaIslemleri.gorselGetir("geri_ok"),
            DosyaIslemleri.gorselGetir("tamam_buton"),
            DosyaIslemleri.gorselGetir("oyundan_cik"),
            DosyaIslemleri.gorselGetir("geri_buton"),
            DosyaIslemleri.gorselGetir("baglanti_yok"),
            # DosyaIslemleri.gorselGetir("kalkan"),
            # DosyaIslemleri.gorselGetir("devre_disi"),
            # DosyaIslemleri.gorselGetir("devam_buton"),
        )
        eminlikler: tuple[float, ...] = (
            eminlikGetir("sehir_ikonu"),  # type: ignore
            eminlikGetir("moe_logo"),
            eminlikGetir("hizmet_basarisiz"),
            eminlikGetir("baglanti_kesildi"),
            eminlikGetir("dunya_ikonu"),
            eminlikGetir("maks_sefer"),
            eminlikGetir("tekrar_dene"),
            eminlikGetir("mavi_tamam"),
            eminlikGetir("geri_ok"),
            eminlikGetir("tamam_buton"),
            eminlikGetir("oyundan_cik"),
            eminlikGetir("geri_buton"),
            eminlikGetir("baglanti_yok"),
            # eminlikGetir("kalkan"),
            # eminlikGetir("devre_disi"),
            # eminlikGetir("devam_buton"),
        )
        bolgeler: tuple[Kare, ...] = (
            taramaBolgesiGetir("sehir_ikonu"),
            taramaBolgesiGetir("moe_logo"),
            taramaBolgesiGetir("hizmet_basarisiz"),
            taramaBolgesiGetir("baglanti_kesildi"),
            taramaBolgesiGetir("dunya_ikonu"),
            taramaBolgesiGetir("maks_sefer"),
            taramaBolgesiGetir("tekrar_dene"),
            taramaBolgesiGetir("mavi_tamam"),
            taramaBolgesiGetir("geri_ok"),
            taramaBolgesiGetir("tamam_buton"),
            taramaBolgesiGetir("oyundan_cik"),
            taramaBolgesiGetir("geri_buton"),
            taramaBolgesiGetir("baglanti_yok"),
            # taramaBolgesiGetir("kalkan"),
            # taramaBolgesiGetir("devre_disi"),
            # taramaBolgesiGetir("devam_buton"),
        )
        self.sehirIkon_tarayici = Tarayici(
            ornek_d=dler[0],
            eminlik=eminlikler[0],
            bolge=bolgeler[0],
            gri_tarama=True,
            isim="engelTarayici.sehirIkon_tarayici",
        )
        self.moeLogo_tarayici = Tarayici(
            ornek_d=dler[1],
            eminlik=eminlikler[1],
            bolge=bolgeler[1],
            gri_tarama=True,
            isim="engelTarayici.moeLogo_tarayici",
        )
        self.hizmetBasarisiz_tarayici = Tarayici(
            ornek_d=dler[2],
            eminlik=eminlikler[2],
            bolge=bolgeler[2],
            gri_tarama=True,
            isim="engelTarayici.hizmetBasarisiz_tarayici",
        )
        self.baglantiKesildi_tarayici = Tarayici(
            ornek_d=dler[3],
            eminlik=eminlikler[3],
            bolge=bolgeler[3],
            gri_tarama=True,
            isim="engelTarayici.baglantiKesildi_tarayici",
        )
        self.dunyaIkon_tarayici = Tarayici(
            ornek_d=dler[4],
            eminlik=eminlikler[4],
            bolge=bolgeler[4],
            gri_tarama=True,
            isim="engelTarayici.dunyaIkon_tarayici",
        )
        self.maksSeferUyari_tarayici = Tarayici(
            ornek_d=dler[5],
            eminlik=eminlikler[5],
            bolge=bolgeler[5],
            gri_tarama=True,
            isim="engelTarayici.maksSeferUyari_tarayici",
        )
        self.tekrarDeneButon_tarayici = Tarayici(
            ornek_d=dler[6],
            eminlik=eminlikler[6],
            bolge=bolgeler[6],
            gri_tarama=True,
            isim="engelTarayici.tekrarDeneButon_tarayici",
        )
        self.maviTamam_tarayici = Tarayici(
            ornek_d=dler[7],
            eminlik=eminlikler[7],
            bolge=bolgeler[7],
            gri_tarama=True,
            isim="engelTarayici.maviTamam_tarayici",
        )
        self.geriOk_tarayici = Tarayici(
            ornek_d=dler[8],
            eminlik=eminlikler[8],
            bolge=bolgeler[8],
            gri_tarama=True,
            isim="engelTarayici.geriOk_tarayici",
        )
        self.tamam_tarayici = Tarayici(
            ornek_d=dler[9],
            eminlik=eminlikler[9],
            bolge=bolgeler[9],
            gri_tarama=True,
            isim="engelTarayici.tamam_tarayici",
        )
        self.oyundan_cik = Tarayici(
            ornek_d=dler[10],
            eminlik=eminlikler[10],
            bolge=bolgeler[10],
            gri_tarama=True,
            isim="engelTarayici.oyundanCik_tarayici",
        )
        self.geri_buton_tarayici = Tarayici(
            ornek_d=dler[11],
            eminlik=eminlikler[11],
            bolge=bolgeler[11],
            gri_tarama=True,
            isim="engelTarayici.geri_tarayici",
        )
        self.baglantiYok_tarayici = Tarayici(
            ornek_d=dler[12],
            eminlik=eminlikler[12],
            bolge=bolgeler[12],
            gri_tarama=True,
            isim="engelTarayici.baglantiYok_tarayici",
        )
        # self.kalkan_tarayici = Tarayici(
        #     ornek_d=dler[13], eminlik=eminlikler[13], bolge=bolgeler[13], gri_tarama=True, isim="engelTarayici.kalkan_tarayici"
        # )
        # self.devre_disi_tarayici = Tarayici(
        #     ornek_d=dler[14], eminlik=eminlikler[14], bolge=bolgeler[14], gri_tarama=True, isim="engelTarayici.devre_disi_tarayici"
        # )
        # self.devam_buton_tarayici = Tarayici(
        #     ornek_d=dler[15], eminlik=eminlikler[15], bolge=bolgeler[15], gri_tarama=True, isim="engelTarayici.devam_buton_tarayici"
        # )

    def _gunlukcuBaslat(self) -> None:
        self.gunlukcu = logging.getLogger("engelTarayiciİslem")
        self.gunlukcu.debug("gunlukcu baslatidi")

    def engelKontrol(self) -> None:
        def _sehirIkonuTara() -> bool:
            _sehirIkonKare = self.sehirIkon_tarayici.ekranTara()
            if _sehirIkonKare is None:
                self._sinyalYolla(ModSinyal.Bekle)
                _sehirYoksa()
            return True

        def _geriOkTara() -> None:
            self.gunlukcu.debug("geri ok tarama basladi")
            _geriok_kare = self.geriOk_tarayici.ekranTara()
            if _geriok_kare is not None:
                self._sinyalYolla(ModSinyal.Bekle)
                Fare.solTikla(_geriok_kare.merkez())
                _geriOkTara()
            self.gunlukcu.debug("geri ok tarama bitti")

        def _sehirYoksa() -> None:
            _maviTamamTara()
            _dunyaIkon_kare = self.dunyaIkon_tarayici.ekranTara()
            if _dunyaIkon_kare is not None:
                self.gunlukcu.debug("dunya ikonu algilandi.")
                Fare.solTikla(_dunyaIkon_kare.merkez())
                if _sehirIkonuTara():
                    self.gunlukcu.debug("sehir ikonu algilandi")
                else:
                    self.gunlukcu.debug("_sehirYoksa :-> sehir ikonu bulunamadi")
                    Fare.sagTikla()
            else:
                self.gunlukcu.debug("_sehirYoksa :-> dünya ikonu bulunamadi")

        def _hizmetBasarisizTara():
            if self.hizmetBasarisiz_tarayici.ekranTara() is not None:
                self.gunlukcu.debug("hizmet basarisiz uyarisi algilandi.")
                self._sinyalYolla(ModSinyal.Bekle)
                _yenidenDeneButonTikla()

        def _baglantiKesildiTara():
            if self.baglantiKesildi_tarayici.ekranTara() is not None:
                self.gunlukcu.debug("baglanti kesildi uyarisi algilandi.")
                # kapama sinyali gönder
                self._sinyalYolla(ModSinyal.Sonlandir)

        def _maksSeferUyariTara():
            if self.maksSeferUyari_tarayici.ekranTara() is not None:
                self.gunlukcu.debug("maks sefer uyarisi algilandi.")
                self._sinyalYolla(ModSinyal.Bekle)
                tamam_konum = self.tamam_tarayici.ekranTara()
                if tamam_konum is not None:
                    Fare.solTikla(tamam_konum.merkez())
                    geri_konum = self.geri_buton_tarayici.ekranTara()
                    if geri_konum is not None:
                        Fare.solTikla(geri_konum.merkez())
                        Fare.sagTikla()

        # def _devambutonTara():
        #     devamTara = self.devam_buton_tarayici.ekranTara()
        #     if devamTara is not None:
        #         sleep(0.5)
        #         Fare.solTikla(devamTara.merkez())

        # def _barisKalkani():
        #     kalkanTara = self.kalkan_tarayici.ekranTara()
        #     if kalkanTara is None:
        #         Fare.solTikla(konum=tiklamaNoktasiGetir("kalkan"))
        #         Fare.solTikla(konum=tiklamaNoktasiGetir("kalkan2"))
        #         Fare.solTikla(konum=tiklamaNoktasiGetir("kullan"))
        #         devredisiTara = self.devre_disi_tarayici.ekranTara()
        #         if devredisiTara is not None:
        #             Fare.solTikla(konum=tiklamaNoktasiGetir("kalkan_al_Evet"))
        #         _geriok_kare = self.geriOk_tarayici.ekranTara()
        #         if _geriok_kare is not None:
        #             Fare.solTikla(_geriok_kare.merkez())

        def _yenidenDeneButonTikla():
            yenidenDeneButon_Kare = self.tekrarDeneButon_tarayici.ekranTara()
            if yenidenDeneButon_Kare is not None:
                self.gunlukcu.debug("yeniden dene butonu algilandi.")
                sleep(ENGEL_KONTROL_SURESI)
                Fare.solTikla(yenidenDeneButon_Kare.merkez())

        def _maviTamamTara():
            maviTamamUyari_kare = self.maviTamam_tarayici.ekranTara()
            if maviTamamUyari_kare is not None:
                self._sinyalYolla(ModSinyal.Bekle)
                self.gunlukcu.debug("mavi tamam butonu algilandi.")
                sleep(ENGEL_KONTROL_SURESI)  # 2
                Fare.solTikla(maviTamamUyari_kare.merkez())
                sleep(ENGEL_KONTROL_SURESI)  # 2
                _maviTamamTara()

        def _oyundancikisTara():
            sleep(ENGEL_KONTROL_SURESI / 2)
            if self.oyundan_cik.ekranTara() is not None:
                self.gunlukcu.debug("oyundak cik uyarrısı bulundu")
                self._sinyalYolla(ModSinyal.Bekle)
                Fare.solTikla(konum=tiklamaNoktasiGetir("cikis_hayir"))

        def _moeLogoBekle() -> None:
            while self.moeLogo_tarayici.ekranTara() is not None:
                self.gunlukcu.debug("moe logo algilandi.")
                self._sinyalYolla(ModSinyal.Bekle)
                sleep(ENGEL_KONTROL_SURESI)
                _yenidenDeneButonTikla()

        def _baglantiYokTara():
            if self.baglantiYok_tarayici.ekranTara() is not None:
                self.gunlukcu.debug("baglanti yok algilandi.")
                self._sinyalYolla(ModSinyal.Bekle)
                sleep(ENGEL_KONTROL_SURESI)
                _yenidenDeneButonTikla()

        while True and self._acikmi():
            _maviTamamTara()
            _moeLogoBekle()
            _baglantiYokTara()
            _baglantiKesildiTara()
            _hizmetBasarisizTara()
            _maviTamamTara()
            _geriOkTara()
            _oyundancikisTara()
            # _devambutonTara()
            _sehirIkonuTara()
            _maksSeferUyariTara()
            self._sinyalYolla(ModSinyal.DevamEt)
            sleep(ENGEL_KONTROL_SURESI)
            self._sinyalDurKontrol()

    def _sinyalYolla(self, sinyal) -> None:
        self.gunlukcu.debug("sinyal gonderildi.")
        self._sinyal_gonderme.value = sinyal
        if sinyal != ModSinyal.DevamEt:
            self._sinyalBekle()

    def _sinyalBekle(self) -> None:
        self.gunlukcu.debug("sinyal bekleniyor")
        while self._sinyal_alma.value == ModSinyal.MesajUlasmadi:
            self.gunlukcu.debug("sinyal ulasmasi bekleniyor")
            sleep(0.1)
        self._sinyal_alma.value = ModSinyal.MesajUlasmadi
        self.gunlukcu.debug("sinyal ulasti")

    def _sinyalDurKontrol(self) -> None:
        """
        sinyal dur kontrol
        """

        if self._sinyal_alma.value == ModSinyal.Bekle:
            self.gunlukcu.debug("sinyal dur kontrol")
            sleep(ENGEL_KONTROL_SURESI / 2)
            self.gunlukcu.debug("sinyal dur kontrol bitti")
        elif self._sinyal_alma == (ModSinyal.Sonlandir, ModSinyal.FailSafe):
            self.gunlukcu.debug("sinyal dur kontrol")
            self.kapat()
            sleep(ENGEL_KONTROL_SURESI)
            exit(0)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"  # type: ignore

    def _acikmi(self) -> bool:
        if not hasattr(self, "_acik_event"):
            self._acik_event = multiprocessing.Event()
        return not self._acik_event.is_set()

    def processOlustur(self, sinyal_gonderme, sinyal_alma) -> multiprocessing.Process:
        self._gunlukcuBaslat()
        self._sinyal_gonderme = sinyal_gonderme
        self._sinyal_alma = sinyal_alma
        self._acik_event = multiprocessing.Event()
        return multiprocessing.Process(target=self.engelKontrol)

    def kapat(self):
        if hasattr(self, "_acik_event"):
            self._acik_event.set()
