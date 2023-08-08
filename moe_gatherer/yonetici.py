import logging
from multiprocessing import RLock
import sys
from time import sleep

import pynput
import win32api
import win32con


# from .engelislem import EngelTarayiciİslem
from .engelislem import EngelTarayiciİslem
from .gunlukcu import Gunlukcu  # noqa
from .kaynakislem import TaramaIslem
from .temel_siniflar import IslemSinyalleri, KaynakTipi


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

        self.engel_tarayici_islem = EngelTarayiciİslem()
        self._process_listesi = []
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
            if hasattr(self, "tarama_islem_process") and hasattr(self, "engel_tarayici_islem_process"):
                if self.engel_tarayici_islem_process.is_alive():
                    sleep(0.1)
                    if self.engel_tarayici_islem._sinyal_gonderme == IslemSinyalleri.SONLANDIR:
                        return

    def tusKontrol(self, key):
        """
        tuşa basıldığında çalışacak fonksiyon\n
        --> baslatma tuşuna basıldığında tarama başlat\n
        --> bitirme tuşuna basıldığında tarama durdur\n
        """
        self.gunlukcu.debug(f"tus basıldı {key}")
        with self._process_olusturma_kilidi:
            if key == pynput.keyboard.KeyCode.from_char("s"):
                if not hasattr(self, "engel_tarayici_islem_process"):
                    self.engel_tarayici_islem_process = self.engel_tarayici_islem.processOlustur()
                    self.engel_tarayici_islem_process.start()
                    self.gunlukcu.debug("engel tarayıcı işlemi başlatıldı,pid: %s", self.engel_tarayici_islem_process.pid)
                elif not self.engel_tarayici_islem_process.is_alive():
                    self.engel_tarayici_islem_process.start()

                if not hasattr(self, "tarama_islem_process"):
                    self.tarama_islem_process = self.tarama_islem.processOlustur(
                        sinyal_alma=self.engel_tarayici_islem._sinyal_gonderme,
                        sinyal_gonderme=self.engel_tarayici_islem._sinyal_alma,
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
                    sinyal_alma=self.engel_tarayici_islem._sinyal_gonderme, sinyal_gonderme=self.engel_tarayici_islem._sinyal_alma
                )
                self.gunlukcu.debug("tarama işlemi process i oluşturuldu")

                self.engel_tarayici_islem.acik_event.set()
                self.gunlukcu.debug("engel tarayıcı işlemi kapatıldı")
                self.engel_tarayici_islem_process = self.engel_tarayici_islem.processOlustur()
                self.gunlukcu.debug("engel tarayıcı işlemi process i oluşturuldu")
                return
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
        ):
            self.tarama_islem.kapat()
            # TODO: sleep muhtemelen gereksiz
            sleep(3)
            if not hasattr(self, "tarama_islem_process"):
                self.gunlukcu.info("program kapatılıyor")
            elif self.tarama_islem_process.is_alive():
                self.gunlukcu.debug("tarama işlemi process i zorla sonlandırılıyor")
                self.tarama_islem_process.terminate()
            self.klavye_dinleyici.stop()
            sys.exit(0)
        return False

    def botBaslat(self):
        """
        klavye dinleyiciyi başlatır\n
        tarama işlemi process olarak başlatır\n
        klavye dinleyiciyi tarama işlem process i sonlanana kadar bekletir\n
        """
        self.klavye_dinleyici.start()
        self._engelSinyalKontrol()
        # self.klavye_dinleyici.join()
