import ctypes
import logging
from multiprocessing import RLock
import multiprocessing
from time import sleep

import pynput
import win32api
import win32con


# from .engelislem import EngelTarayiciİslem
from .engelislem import EngelTarayiciİslem
from .gunlukcu import Gunlukcu  # noqa
from .moe_gatherer import TaramaIslem
from .temel_siniflar import ModSinyal, KaynakTipi


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
    ) -> None:
        self.tarama_islem_argumanları = (kaynak_tipleri, svyler, maks_sefer_sayisi)
        self.tarama_islem = TaramaIslem(
            kaynak_tipleri=self.tarama_islem_argumanları[0],
            svyler=self.tarama_islem_argumanları[1],
            maks_sefer_sayisi=self.tarama_islem_argumanları[2],
        )
        self._sinyal_knl1 = multiprocessing.Value(ctypes.c_short, ModSinyal.DEVAM_ET)
        self._sinyal_knl2 = multiprocessing.Value(ctypes.c_short, ModSinyal.MESAJ_ULASMADI)
        self.engel_tarayici_islem = EngelTarayiciİslem()
        # self._process_listesi = []
        self._process_olusturma_kilidi = RLock()
        self.klavye_dinleyici = pynput.keyboard.Listener(on_press=self.tusKontrol)
        self.gunlukcu = logging.getLogger("gunlukcu.botyonetici")

        self.gunlukcu.debug(f"{self.__class__.__name__}_{id(self)} oluşturuldu")
        self.tarama_islem_kapatildi: bool = False
        # --> eğer program kapatılırsa çalışacak fonksiyonu belirle (pywin32 api)
        win32api.SetConsoleCtrlHandler(self._on_exit, True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return f"tarama_islem: {self.tarama_islem}, klavye_dinleyici: {self.klavye_dinleyici}"

    def _engelSinyalKontrol(self):
        while True:
            sleep(0.1)  # 100

            if hasattr(self, "tarama_islem_process") and hasattr(self, "engel_tarayici_islem_process"):
                if self.engel_tarayici_islem_process.is_alive():
                    sleep(0.1)
                    if self.engel_tarayici_islem._sinyal_gonderme.value == ModSinyal.SONLANDIR:
                        return
                # fail safe sonlandır check
                if self.tarama_islem_process.is_alive():
                    sleep(0.1)
                    if self.tarama_islem._sinyal_gonderme.value == ModSinyal.FAILSAFE_SONLANDIR:
                        self.engel_tarayici_islem._sinyal_gonderme.value = ModSinyal.DUR
            if self._sinyal_knl1 == ModSinyal.SONLANDIR:
                self._on_exit(win32con.CTRL_CLOSE_EVENT)

    def tusKontrol(self, key):
        """
        tuşa basıldığında çalışacak fonksiyon\n
        --> baslatma tuşuna basıldığında tarama başlat\n
        --> bitirme tuşuna basıldığında tarama durdur\n
        """
        sleep(0.2)
        self.gunlukcu.debug(f"tus basıldı {key}")
        with self._process_olusturma_kilidi:
            if key == pynput.keyboard.KeyCode.from_char("s"):
                if not hasattr(self, "engel_tarayici_islem_process"):
                    self.engel_tarayici_islem_process = self.engel_tarayici_islem.processOlustur(
                        sinyal_alma=self._sinyal_knl1, sinyal_gonderme=self._sinyal_knl2
                    )
                    self.engel_tarayici_islem_process.start()
                    self.gunlukcu.debug("engel tarayıcı işlemi başlatıldı,pid: %s", self.engel_tarayici_islem_process.pid)
                elif not self.engel_tarayici_islem_process.is_alive():
                    self.engel_tarayici_islem_process.start()

                if not hasattr(self, "tarama_islem_process"):
                    self.tarama_islem_process = self.tarama_islem.processOlustur(
                        sinyal_alma=self._sinyal_knl2, sinyal_gonderme=self._sinyal_knl1
                    )
                    self.tarama_islem_process.start()
                    self.gunlukcu.debug("tarama işlemi başlatıldı,pid: %s", self.tarama_islem_process.pid)
                    return
                elif not self.tarama_islem_process.is_alive():
                    self.tarama_islem_process.start()
                    return

            elif key == pynput.keyboard.KeyCode.from_char("d"):
                self.tarama_islem.kapat()
                self.gunlukcu.debug("tarama işlemi kapatıldı")
                self.tarama_islem_process = self.tarama_islem.processOlustur(
                    sinyal_alma=self._sinyal_knl2, sinyal_gonderme=self._sinyal_knl1
                )
                self.gunlukcu.debug("tarama işlemi process i oluşturuldu")

                self.engel_tarayici_islem._acik_event.set()
                self.gunlukcu.debug("engel tarayıcı işlemi kapatıldı")
                self.engel_tarayici_islem_process = self.engel_tarayici_islem.processOlustur(
                    sinyal_alma=self._sinyal_knl1, sinyal_gonderme=self._sinyal_knl2
                )
                self.gunlukcu.debug("engel tarayıcı işlemi process i oluşturuldu")
                return
            # FIXME : silmeyi unutma (test için sadece "q" tuşu ile çıkış)
            elif key == pynput.keyboard.KeyCode.from_char("q"):
                print("ciıkış tuşuna basıldı")
                self._on_exit(win32con.CTRL_CLOSE_EVENT)
            else:
                pass

    def _on_exit(self, signal) -> bool:
        """
        eğer program kapatılırsa çalışacak fonksiyon\n
        -> carpi ile kapatılırsa çalışacak fonksiyon\n
        -> ctrl+c ile kapatılırsa çalışacak fonksiyon\n
        """
        self.gunlukcu.debug(f"program kapatılma sinyali aldı sinyal: {signal}")
        if signal in (
            win32con.CTRL_C_EVENT,
            win32con.CTRL_BREAK_EVENT,
            win32con.CTRL_CLOSE_EVENT,
            win32con.CTRL_LOGOFF_EVENT,
            win32con.CTRL_SHUTDOWN_EVENT,
        ):
            self._sinyal_knl1.value = ModSinyal.SONLANDIR  # type: ignore
            self._sinyal_knl2.value = ModSinyal.SONLANDIR  # type: ignore
            # self.tarama_islem.kapat()
            # self.engel_tarayici_islem.kapat()
            # TODO: sleep muhtemelen gereksiz
            sleep(3)
            if not hasattr(self, "tarama_islem_process"):
                self.gunlukcu.info("program kapatılıyor")
            self.tarama_islem_process.terminate()
            self.engel_tarayici_islem_process.terminate()
            self.klavye_dinleyici.stop()
            exit(0)
        return False

    def botBaslat(self):
        try:
            self.klavye_dinleyici.start()
            self._engelSinyalKontrol()
            if self.tarama_islem_process.is_alive():
                self.tarama_islem.kapat()
            if self.engel_tarayici_islem_process.is_alive():
                self.engel_tarayici_islem.kapat()
            if self.klavye_dinleyici.is_alive():
                self.klavye_dinleyici.stop()
            exit(0)
        except KeyboardInterrupt:
            print("keyboard interrupt")
            self._on_exit(win32con.CTRL_C_EVENT)
        # self.klavye_dinleyici.join()
