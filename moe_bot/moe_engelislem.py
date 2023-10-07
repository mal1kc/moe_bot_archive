import functools
import logging
import multiprocessing
import time
from moe_bot.tarayicilar import GorselTarayici

# -- moe_bot
from moe_bot.types import Event, SynchronizedBase, Self

from moe_bot.enumlar import ModSinyal
from moe_bot.ayarlar import Ayarlar


class EngelIslemModulu:
    __slots__ = ("_sinyal_alma_knl", "_sinyal_gonderme_knl", "_process", "_ayarlar") + (
        "sehirIkon_tarayici",
        "dunyaIkon_tarayici",
        "hizmetBasarisiz_tarayici",
        "baglantiKesildi_tarayici",
        "maksSeferUyari_tarayici",
        "devam_buton_tarayici",
        "kalkan_tarayici",
        "devre_disi_tarayici",
        "tekrarDeneButon_tarayici",
        "maviTamam_tarayici",
        "geriOk_tarayici",
        "oyundan_cik",
        "moeLogo_tarayici",
        "baglantiYok_tarayici",
        "tamam_tarayici",
        "geri_buton_tarayici",
    )
    _mod_ad: str = "EngelIslemModulu"
    _aktif: Event = multiprocessing.Event()

    def __new__(cls, *args, **kwargs) -> Self:
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        cls.__init__(*args, **kwargs)
        return cls.instance

    @functools.cached_property
    def _gunlukcu(self) -> logging.Logger:
        return logging.getLogger(__name__)

    @functools.cached_property
    def ayarlar(self) -> Ayarlar.ModAyarlari:
        if self._aktifmi():
            return self._ayarlar
        from moe_bot.ayarlar import moe_engelislem

        self._ayarlar = moe_engelislem.ayarları_olustur()
        return self._ayarlar

    def __init__(self):
        self._gunlukcu.info("EngelIslemModulu nesnesi oluşturuluyor.")
        # tarayıcıları oluştur
        sehir_ikon_ayarlari = self.ayarlar.tarayicilar["sehir_ikonu"]

        self.sehirIkon_tarayici = GorselTarayici(
            gorsel_d=sehir_ikon_ayarlari[0], eminlik=sehir_ikon_ayarlari[1], konum=sehir_ikon_ayarlari[2]
        )
        dunya_ikon_ayarlari = self.ayarlar.tarayicilar["dunya_ikonu"]
        self.dunyaIkon_tarayici = GorselTarayici(
            gorsel_d=dunya_ikon_ayarlari[0], eminlik=dunya_ikon_ayarlari[1], konum=dunya_ikon_ayarlari[2]
        )
        hizmet_basarisiz_ayarlari = self.ayarlar.tarayicilar["hizmet_basarisiz"]
        self.hizmetBasarisiz_tarayici = GorselTarayici(
            gorsel_d=hizmet_basarisiz_ayarlari[0], eminlik=hizmet_basarisiz_ayarlari[1], konum=hizmet_basarisiz_ayarlari[2]
        )
        baglanti_kesildi_ayarlari = self.ayarlar.tarayicilar["baglanti_kesildi"]
        self.baglantiKesildi_tarayici = GorselTarayici(
            gorsel_d=baglanti_kesildi_ayarlari[0], eminlik=baglanti_kesildi_ayarlari[1], konum=baglanti_kesildi_ayarlari[2]
        )
        maks_sefer_uyari_ayarlari = self.ayarlar.tarayicilar["maks_sefer_uyari"]
        self.maksSeferUyari_tarayici = GorselTarayici(
            gorsel_d=maks_sefer_uyari_ayarlari[0], eminlik=maks_sefer_uyari_ayarlari[1], konum=maks_sefer_uyari_ayarlari[2]
        )
        devam_buton_ayarlari = self.ayarlar.tarayicilar["devam_butonu"]
        self.devam_buton_tarayici = GorselTarayici(
            gorsel_d=devam_buton_ayarlari[0], eminlik=devam_buton_ayarlari[1], konum=devam_buton_ayarlari[2]
        )
        kalkan_ayarlari = self.ayarlar.tarayicilar["kalkan"]
        self.kalkan_tarayici = GorselTarayici(gorsel_d=kalkan_ayarlari[0], eminlik=kalkan_ayarlari[1], konum=kalkan_ayarlari[2])
        devre_disi_ayarlari = self.ayarlar.tarayicilar["devre_disi"]
        self.devre_disi_tarayici = GorselTarayici(
            gorsel_d=devre_disi_ayarlari[0], eminlik=devre_disi_ayarlari[1], konum=devre_disi_ayarlari[2]
        )
        tekrar_dene_buton_ayarlari = self.ayarlar.tarayicilar["tekrar_dene_butonu"]
        self.tekrarDeneButon_tarayici = GorselTarayici(
            gorsel_d=tekrar_dene_buton_ayarlari[0], eminlik=tekrar_dene_buton_ayarlari[1], konum=tekrar_dene_buton_ayarlari[2]
        )

    def _aktifmi(self) -> bool:
        if self._process is not None:
            return self._process.is_alive() and self._aktif.is_set()
        return self._aktif.is_set()

    def _sinyal_yolla(self, sinyal: int) -> None:
        self._gunlukcu.debug(f"{self._mod_ad} sinyal yolluyor: {sinyal}")
        self._sinyal_gonderme_knl.value = sinyal  # type: ignore
        if sinyal != ModSinyal.DevamEt:
            self._sinyal_bekle()

    def _sinyal_bekle(self) -> None:
        self._gunlukcu.debug(f"{self._mod_ad} sinyal bekleniyor.")
        while self._sinyal_alma_knl.value == ModSinyal.MesajUlasmadi:  # type: ignore
            self._gunlukcu.debug(f"{self._mod_ad} sinyal bekleniyor.")
            time.sleep(self.ayarlar.bosta_bekleme_suresi)
        self._sinyal_kontrol()  # kapama sinalı gelmiş olabilir.
        self._gunlukcu.debug(f"{self._mod_ad} sinyal alındı.")
        self._sinyal_alma_knl.value = ModSinyal.MesajUlasmadi  # type: ignore

    def _sinyal_kontrol(self) -> None:
        self._gunlukcu.debug(f"{self._mod_ad} sinyal kontrol ediliyor.")
        if self._sinyal_alma_knl.value == ModSinyal.Bekle:  # type: ignore
            self._gunlukcu.debug(f"{self._mod_ad} sinyal kontrol edildi.")
            self._gunlukcu.info(f"{self._mod_ad} durduruluyor.")
            while self._sinyal_alma_knl.value == ModSinyal.Bekle:  # type: ignore
                time.sleep(self.ayarlar.bekleme_suresi)
        elif self._sinyal_alma_knl.value in (ModSinyal.Sonlandir, ModSinyal.FailSafe):  # type: ignore
            self._gunlukcu.debug(f"{self._mod_ad} sinyal kontrol edildi.")
            self._gunlukcu.info(f"{self._mod_ad} kapatılıyor.")
            self.kapat()
            # eğer kapanmazsa diye biraz bekleyelim.
            time.sleep(self.ayarlar.bekleme_suresi)

    def __repr__(self) -> str:
        return f"<{self._mod_ad}(aktif: {self._aktifmi()})>"

    def process_olustur(self, sinyal_gonderme_kanal: SynchronizedBase, sinyal_alma_knl: SynchronizedBase) -> multiprocessing.Process:
        self._gunlukcu.info(f"{self._mod_ad} process oluşturuluyor.")
        self._sinyal_alma_knl = multiprocessing.Value("i", ModSinyal.MesajUlasmadi)
        self._sinyal_gonderme_knl = multiprocessing.Value("i", ModSinyal.MesajUlasmadi)
        self._aktiflik_yenile()
        self._process = multiprocessing.Process(target=self.engelKontrol, args=())
        return self._process

    def _aktiflik_yenile(self) -> None:
        if self._aktifmi():
            self._aktif.clear()

    def kapat(self) -> None:
        raise NotImplementedError

    def engelKontrol(self) -> None:
        def _sehirIkonuTara() -> bool:
            _sehirIkonKare = self.sehirIkon_tarayici.ekran_tara()
            if _sehirIkonKare is None:
                self._sinyal_yolla(ModSinyal.Bekle)
                _sehirYoksa()
            return True

        def _geriOkTara() -> None:
            self._gunlukcu.debug("geri ok tarama basladi")
            _geriok_kare = self.geriOkTarayici.ekranTara()
            if _geriok_kare is not None:
                self._sinyalYolla(IslemSinyalleri.DUR)
                Fare.solTikla(_geriok_kare.merkez())
            self.gunlukcu.debug("geri ok tarama bitti")

        # FIXME oyundan çıkış engeli kaldırma

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
                self._sinyalYolla(IslemSinyalleri.DUR)
                _yenidenDeneButonTikla()

        def _baglantiKesildiTara():
            if self.baglantiKesildi_tarayici.ekranTara() is not None:
                self.gunlukcu.debug("baglanti kesildi uyarisi algilandi.")
                # exit sinyali
                self._sinyalYolla(IslemSinyalleri.SONLANDIR)

        def _maksSeferUyariTara():
            if self.maksSeferUyari_tarayici.ekranTara() is not None:
                self.gunlukcu.debug("maks sefer uyarisi algilandi.")
                self._sinyalYolla(IslemSinyalleri.DUR)
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
                self._sinyalYolla(IslemSinyalleri.DUR)
                self.gunlukcu.debug("mavi tamam butonu algilandi.")
                sleep(ENGEL_KONTROL_SURESI)  # 2
                Fare.solTikla(maviTamamUyari_kare.merkez())
                sleep(ENGEL_KONTROL_SURESI)  # 2
                _maviTamamTara()

        def _oyundancikisTara():
            sleep(ENGEL_KONTROL_SURESI / 2)
            if self.oyundan_cik.ekranTara() is not None:
                self.gunlukcu.debug("oyundak cik uyarrısı bulundu")
                self._sinyalYolla(IslemSinyalleri.DUR)
                Fare.solTikla(konum=tiklamaNoktasiGetir("cikis_hayir"))

        def _moeLogoBekle() -> None:
            while self.moeLogo_tarayici.ekranTara() is not None:
                self.gunlukcu.debug("moe logo algilandi.")
                self._sinyalYolla(IslemSinyalleri.DUR)
                sleep(ENGEL_KONTROL_SURESI)
                _yenidenDeneButonTikla()

        def _baglantiYokTara():
            if self.baglantiYok_tarayici.ekranTara() is not None:
                self.gunlukcu.debug("baglanti yok algilandi.")
                self._sinyalYolla(IslemSinyalleri.DUR)
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
            self._sinyalYolla(IslemSinyalleri.DEVAM_ET)
            sleep(ENGEL_KONTROL_SURESI)
            self._sinyalDurKontrol()
