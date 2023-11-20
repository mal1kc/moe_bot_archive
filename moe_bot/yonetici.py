import ctypes
import functools
import logging
import multiprocessing
from multiprocessing import RLock
from time import sleep

import pynput
import win32api
import win32con

from moe_bot.gunlukcu import Gunlukcu  # noqa
from moe_bot.hatalar import KullaniciHatasi
from moe_bot.mod.moe_engelislem import EngelIslemModulu
from moe_bot.mod.moe_gatherer_islem import MoeGatherer, KaynakTipi
from moe_bot.sunucu_islemleri import SUNUCU_OTURUM_SURESI, SunucuIslem, SunucuIslemSonucu
from moe_bot.enumlar import IslemSinyal
from moe_bot.temel_siniflar import Diller, RepeatedTimer


class BotIslemYonetici:
    """
    klavyede basılan tuşlara göre tarama işlemi yönetir\n
    --> tarama islemi process olarak başlatma sinyali gönder\n
    --> tarama isleme process olarak sonlandırma sinyali gönder\n
    """

    def __init__(
        self,
        maks_sefer_sayisi: int,
        kaynak_tipleri: tuple[KaynakTipi, ...],
        svyler: tuple[int, ...],
        sunucu_islem: SunucuIslem,
    ) -> None:
        try:
            self._acik_event = multiprocessing.Event()
            self.s_islem = sunucu_islem
            self.sunucu_o_kontrol_zamanlayici = RepeatedTimer(SUNUCU_OTURUM_SURESI, self._oturum_kontrol)
            self.tarama_islem_argumanları = (kaynak_tipleri, svyler, maks_sefer_sayisi)
            self.tarama_islem = MoeGatherer.TaramaIslem(
                kaynak_tipleri=self.tarama_islem_argumanları[0],
                svyler=self.tarama_islem_argumanları[1],
                maks_sefer_sayisi=self.tarama_islem_argumanları[2],
            )
            self._sinyal_knl1 = multiprocessing.Value(ctypes.c_short, IslemSinyal.DevamEt)
            self._sinyal_knl2 = multiprocessing.Value(ctypes.c_short, IslemSinyal.MesajUlasmadi)
            self.engel_tarayici_islem = EngelIslemModulu()
            # self._process_listesi = []
            self._process_olusturma_kilidi = RLock()
            self.klavye_dinleyici = pynput.keyboard.Listener(on_press=self.tusKontrol)

            self._gunlukcu.debug(f"{self.__class__.__name__}_{id(self)} oluşturuldu")
            self.tarama_islem_kapatildi: bool = False
            # --> eğer program kapatılırsa çalışacak fonksiyonu belirle (pywin32 api)
            win32api.SetConsoleCtrlHandler(self._on_exit, True)

            # start sunucu oturum kontrol
            self.sunucu_o_kontrol_zamanlayici.start()
        except Exception as e:
            self._gunlukcu.exception(f"{self.__class__.__name__} oluşturulurken hata oluştu", exc_info=e)
            raise KullaniciHatasi(Diller.lokalizasyon("unexpected_error", "UI"))

    @functools.cached_property
    def _gunlukcu(self):
        return logging.getLogger("gunlukcu.botyonetici")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return f"tarama_islem: {self.tarama_islem}, klavye_dinleyici: {self.klavye_dinleyici}"

    def _engelSinyalKontrol(self):
        while True:
            sleep(0.1)  # 100 ms
            if self._acik_event.is_set():
                # güvenli bir şekilde botu (çocuk processleri vs kapat)
                self.botKapat()
                # ardından döngüyü kır
                break
            if hasattr(self, "tarama_islem_process") and hasattr(self, "engel_tarayici_islem_process"):
                if self.engel_tarayici_islem_process.is_alive():
                    if self.engel_tarayici_islem._sinyal_gonderme.value == IslemSinyal.Sonlandir:
                        return
                if self.tarama_islem_process.is_alive():
                    if self.tarama_islem._sinyal_gonderme.value == IslemSinyal.FailSafe:
                        self.engel_tarayici_islem._sinyal_gonderme.value = IslemSinyal.Bekle
            if self._sinyal_knl1 == IslemSinyal.Sonlandir:
                self._on_exit(win32con.CTRL_CLOSE_EVENT)

    def tusKontrol(self, key):
        """
        tuşa basıldığında çalışacak fonksiyon\n
        --> baslatma tuşuna basıldığında tarama başlat\n
        --> bitirme tuşuna basıldığında tarama durdur\n
        """
        sleep(0.1)
        self._gunlukcu.debug(f"tus basıldı {key}")
        with self._process_olusturma_kilidi:
            if key == pynput.keyboard.KeyCode.from_char("s"):
                if not hasattr(self, "engel_tarayici_islem_process"):
                    self.engel_tarayici_islem_process = self.engel_tarayici_islem.processOlustur(
                        sinyal_alma=self._sinyal_knl1, sinyal_gonderme=self._sinyal_knl2
                    )
                    self.engel_tarayici_islem_process.start()
                    self._gunlukcu.debug("engel tarayıcı işlemi başlatıldı,pid: %s", self.engel_tarayici_islem_process.pid)
                elif not self.engel_tarayici_islem_process.is_alive():
                    self.engel_tarayici_islem_process.start()

                if not hasattr(self, "tarama_islem_process"):
                    self.tarama_islem_process = self.tarama_islem.processOlustur(
                        sinyal_alma=self._sinyal_knl2, sinyal_gonderme=self._sinyal_knl1
                    )
                    self.tarama_islem_process.start()
                    self._gunlukcu.debug("tarama işlemi başlatıldı,pid: %s", self.tarama_islem_process.pid)
                    return
                elif not self.tarama_islem_process.is_alive():
                    self.tarama_islem_process.start()
                    return

            elif key == pynput.keyboard.KeyCode.from_char("d"):
                self.tarama_islem.kapat()
                self._gunlukcu.debug("tarama işlemi kapatıldı")
                self.tarama_islem_process = self.tarama_islem.processOlustur(
                    sinyal_alma=self._sinyal_knl2, sinyal_gonderme=self._sinyal_knl1
                )
                self._gunlukcu.debug("tarama işlemi process i oluşturuldu")

                self.engel_tarayici_islem.kapat()
                self._gunlukcu.debug("engel tarayıcı işlemi kapatıldı")
                self.engel_tarayici_islem_process = self.engel_tarayici_islem.processOlustur(
                    sinyal_alma=self._sinyal_knl1, sinyal_gonderme=self._sinyal_knl2
                )
                self._gunlukcu.debug("engel tarayıcı işlemi process i oluşturuldu")
                return

            # elif key == pynput.keyboard.Key.f12:
            #     print(Diller.lokalizasyon("bot_failsafe_close", "UI"))
            #     self._on_exit(win32con.CTRL_CLOSE_EVENT)
            else:
                pass

    def _oturum_kontrol(self):
        sonuc = self.s_islem.giris_yenile()
        # TODO : oturum yenileme hatası alınırsa ne yapılacak?
        # - geçici çözüm olarak k.hata fırlatılacak ve program kapatılacak
        # TODO : durma durumunda giriş yenileme yapılacak mı?
        # - geçici çözüm olarak hiçbir şey yapılmayacak
        self._gunlukcu.debug(f"sunucu oturum yenileme sonucu: {sonuc.name}")
        if sonuc != SunucuIslemSonucu.BASARILI:
            self._acik_event.set()
            self._gunlukcu.error(f"sunucu oturum yenileme hatası: {sonuc.name}")
            if sonuc == SunucuIslemSonucu.PAKET_BULUNAMADI:
                raise KullaniciHatasi(Diller.lokalizasyon("server_session_renewal_error_package_not_found", "ERROR"))
            elif sonuc == SunucuIslemSonucu.BAGLANTI_HATASI:
                raise KullaniciHatasi(Diller.lokalizasyon("server_connection_error", "ERROR"))
            elif sonuc == SunucuIslemSonucu.GIRIS_BILGISI_HATALI:
                raise KullaniciHatasi(Diller.lokalizasyon("server_session_renewal_error_server_error", "ERROR"))
            elif sonuc == SunucuIslemSonucu.MAKSIMUM_GIRIS_HATASI:
                raise KullaniciHatasi(Diller.lokalizasyon("server_session_renewal_error_max_online_user", "ERROR"))
            raise KullaniciHatasi(Diller.lokalizasyon("server_session_renewal_error_unknown_error", "ERROR"))

    def _on_exit(self, signal) -> bool:
        """
        eğer program kapatılırsa çalışacak fonksiyon\n
        """
        self._gunlukcu.debug(f"program kapatılma sinyali aldı sinyal: {signal}")
        if signal in (
            win32con.CTRL_C_EVENT,
            win32con.CTRL_BREAK_EVENT,
            win32con.CTRL_CLOSE_EVENT,
            win32con.CTRL_LOGOFF_EVENT,
            win32con.CTRL_SHUTDOWN_EVENT,
        ):
            self._gunlukcu.debug("program kapatılıyor")
            self._sinyal_knl1.value = IslemSinyal.Sonlandir
            sleep(3)
            if hasattr(self, "tarama_islem_process"):
                if self.tarama_islem_process.is_alive():
                    self.tarama_islem_process.terminate()
            if hasattr(self, "engel_tarayici_islem_process"):
                if self.engel_tarayici_islem_process.is_alive():
                    self.engel_tarayici_islem_process.terminate()
            self._acik_event.set()
            self.klavye_dinleyici.stop()
            self.sunucu_o_kontrol_zamanlayici.stop()
        return False

    def botKapat(self):
        self._on_exit(win32con.CTRL_CLOSE_EVENT)

    def botBaslat(self):
        try:
            self.klavye_dinleyici.start()
            self._engelSinyalKontrol()
        except KeyboardInterrupt:
            self._on_exit(win32con.CTRL_C_EVENT)
