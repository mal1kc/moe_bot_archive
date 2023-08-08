"""
Calisan -> calisir
Denetleyici -> 'Calisan' denetler
basYonetici -> 'Calisan' ve 'Denetleyici' yonetir

Calisan sonsuza kadar calisir
Detetleyici calisanin calismasini denetler | 
    eger calisan x output verirse, denetleyici calisanin calismasini durdurur ve x'i y' ye donusturur ve calisanin calismasini devam_ettirir
    eger calisan z output verise, denetleyici basyoneticiye programin calismasini durdurmasi icin bir sinyal gonderir
"""

from enum import IntEnum, auto
from multiprocessing import Process
import multiprocessing
import ctypes
import random
from time import sleep


class IslemSinyalleri(IntEnum):
    DEVAM_ET = 0
    DURDUR = 1
    MESAJ_ULASTI = 2
    MESAJ_ULASMADI = 3
    ISLEMI_SONLANDIR = 4


class Ciktilar(IntEnum):
    a = auto()
    b = auto()
    c = auto()
    d = auto()
    x = auto()
    y = auto()
    z = auto()


class Calisan:
    def calis(self):
        while self.acikmi():
            if self._sinyal_alma.value == IslemSinyalleri.DURDUR:
                self._sinyal_gonder(IslemSinyalleri.MESAJ_ULASTI)
                while self._sinyal_alma.value != IslemSinyalleri.DEVAM_ET:
                    self._sinyal_gonder(IslemSinyalleri.MESAJ_ULASTI)
                    print("Calisan -> durdum bekliyorum")
                    sleep(0.5)

            self._sinyal_gonder(IslemSinyalleri.MESAJ_ULASMADI)
            sleep(0.5)
            self._cikti_bant.value = random.choices([cikti for cikti in Ciktilar])[0]
            print("Calisan -> çalıştım üretim bantı: ", end="")
            print(self._cikti_bant.value)

    def _sinyal_gonder(self, sinyal):
        self._sinyal_gonderme.value = sinyal

    def process_olustur(self, cikti_bant, sinyal_alma, sinyal_gonderme) -> Process:
        self._acik_event = multiprocessing.Event()
        self._cikti_bant = cikti_bant

        self._sinyal_alma = sinyal_alma
        self._sinyal_gonderme = sinyal_gonderme
        return Process(target=self.calis, name="calisan_process")

    def acikmi(self):
        return not self._acik_event.is_set()


class Denetleyici:
    def calis(self):
        while self.acikmi():
            if self._calisan_cikti_bant.value == Ciktilar.x:
                self._sinyal_gonder(IslemSinyalleri.DURDUR)
                print("Denetleyici -> x geldi y'ye donusturuyorum")
                self._calisan_cikti_bant.value = Ciktilar.y
                sleep(0.5)
                self._sinyal_gonder(IslemSinyalleri.DEVAM_ET)
            if self._calisan_cikti_bant.value == Ciktilar.z:
                print("Denetleyici -> z geldi sonlandirma sinyali gonderiyorum")
                self._sinyal_gonder(IslemSinyalleri.ISLEMI_SONLANDIR)
                break

    def _sinyal_ulasdimi(self):
        while self._sinyal_alma.value != IslemSinyalleri.MESAJ_ULASTI:
            sleep(0.1)

    def _sinyal_gonder(self, sinyal):
        self._sinyal_gonderme.value = sinyal
        self._sinyal_ulasdimi()

    def process_olustur(self, calisan_cikti_bant, sinyal_alma, sinyal_gonderme) -> Process:
        self._acik_event = multiprocessing.Event()
        self._calisan_cikti_bant = calisan_cikti_bant

        self._sinyal_alma = sinyal_alma
        self._sinyal_gonderme = sinyal_gonderme
        return Process(target=self.calis, name="denetleyici_process")

    def acikmi(self):
        return not self._acik_event.is_set()


def sinyal_kontrol(sinyal_knl1):
    while True:
        while sinyal_knl1.value != IslemSinyalleri.ISLEMI_SONLANDIR:  # type: ignore
            sleep(0.1)
        exit()


class BasYonetici:
    def calis(self):
        print("BasYonetici -> calisan_process basladi")
        while True:
            self.calisan_process.start()
            self.sinyal_kontrol_process.start()
            self.denetleyici_process.start()
            self.sinyal_kontrol_process.join()
            if self._cikti_bant.value == Ciktilar.z:
                self.calisan_process.terminate()
                self.denetleyici_process.terminate()
                exit()

    def processleri_olustur(self):
        print("BasYonetici -> processler olusturuluyor")

        self._cikti_bant = multiprocessing.Value(ctypes.c_short, Ciktilar.a)
        self._sinyal_knl1 = multiprocessing.Value(ctypes.c_short, IslemSinyalleri.DEVAM_ET)
        self._sinyal_knl2 = multiprocessing.Value(ctypes.c_short, IslemSinyalleri.MESAJ_ULASMADI)

        self.calisan_process = Calisan().process_olustur(self._cikti_bant, self._sinyal_knl1, self._sinyal_knl2)
        self.denetleyici_process = Denetleyici().process_olustur(self._cikti_bant, self._sinyal_knl2, self._sinyal_knl1)
        self.sinyal_kontrol_process = Process(target=sinyal_kontrol, name="sinyal_kontrol_process", args=(self._sinyal_knl1,))
        print("BasYonetici -> processler olusturuldu")
        print("BasYonetici -> processler : ", end="")
        print(self.calisan_process.name, end=", ")
        print(self.denetleyici_process.name, end=", ")
        print(self.sinyal_kontrol_process.name)


if __name__ == "__main__":
    print([cikti for cikti in Ciktilar])
    bas_yonetici = BasYonetici()
    bas_yonetici.processleri_olustur()
    bas_yonetici.calis()
