from dataclasses import dataclass
import os
import subprocess
from typing import Optional
import psutil
from hashlib import sha512
import platform
import xml.etree.ElementTree as ET

# ruff: noqa: E501


from .hatalar import Hata, KullaniciHatasi

izinli_anahtarlar = {
    "8a9c4d226984a4a25d812fcc1881dff100cd4b5c5c19a14d5a0386ba2402aed38fa55048bf12afd4c0a26b6e31cec73d3f6705f89b7ddc3e93ac12097a5ca0d8",  # 3840
    "e94ec556caaa2a3fda2b037cf9d8d6c88bab1e5036851b6a64ad2cc1aaf97c05858b10af5cafd32bbc8156177f57f066d9d9ca8351d96c6fe4e45dbc8b5ea189",  # mal1kc , 2023-08-08 - 1
    "0a787a57d281a4682cfbdcfeea938acd656e8c5276fdd4bbcd4bce451330d1037529473fbb04b601a8f35408f06425d30ef174a5f79b411eb386a70bce25a01e",  # mal1kc , laptop
    "3ea564c12301d7f2d15fde215f8fa89027d1d6c81cf8abd387a86578f146320e7c89b001a4f47ae250c6282b3c68bb9852e7f52ad34a1880d82ce2f2a8fdbcc6",  # burakAnaPC
    "bd332cebb9dc33358d9909236a17c12922d898edd0caae8d88b5c15f0aa2c76b5caaef38a1928c613fb20108ec8d400d60f17250718a282cacd9f916223f78e9",  # burak SanalPC
}
xml_dosya_sifresi = "moe__gatherR"

DXDIAG_KULLAN = True


def get_first_word(full_word):
    full_word = full_word.split(" ")[0].strip()
    return full_word


@dataclass
class SystemInfo:
    machine_name: str
    operating_system: str
    system_manufacturer: str
    system_model: str
    firmware_type: str
    bios: str  # type: ignore
    processor: str  # type: ignore
    # _processor: str = field(
    #     init=False,
    #     repr=False,
    # )

    @property
    def processor(self) -> str:
        return self._processor

    @processor.setter
    def processor(self, value):
        self._processor = get_first_word(value)

    @property
    def bios(self) -> str:
        return self._bios

    @bios.setter
    def bios(self, value):
        self._bios = get_first_word(value)

    def __str__(self) -> str:
        return "+".join([str(i) for i in self.__dict__.values()])


class DosyaSıfreleme:
    @staticmethod
    def sifrele(data, sifre):
        sifre = sifre.encode("utf-8")
        sifrelenmis = bytearray()
        for i, b in enumerate(data):
            sifrelenmis.append(b ^ sifre[i % len(sifre)])
        return bytes(sifrelenmis)

    @staticmethod
    def dosya_sifrele(dosya_adi, sifre):
        with open(dosya_adi, "rb") as f:
            data = f.read()

        with open(dosya_adi, "wb") as f:
            f.write(DosyaSıfreleme.sifrele(data, sifre))
        return True


@dataclass
class AnahtarKaynagi:
    cpu: str
    hostname: str
    machine_type: str
    process_total_cores: int
    processor_architecture: str
    wmicode: str
    _windows_uuid: str | None = None

    def anahtar_olustur(self):
        ozel_baslangic = "moe__gatherer"
        ozel_son = "yns"
        tum_bilgiler = (
            ozel_baslangic,
            self.cpu,
            self.hostname,
            self.machine_type,
            self.process_total_cores,
            self.processor_architecture,
            self.wmicode,
            self.windows_uuid,
            ozel_son,
        )
        b_tum_bilgiler = b"".join([str(i).encode("utf-8") for i in tum_bilgiler])

        return sha512(b_tum_bilgiler).hexdigest()

    @property
    def windows_uuid(self):
        if self._windows_uuid is None:
            self._windows_uuid = self._getWindowsUUID()
        return self._windows_uuid

    @staticmethod
    def _getWindowsUUID() -> str:
        sprocess = subprocess.Popen(["wmic", "csproduct", "get", "UUID"], stdout=subprocess.PIPE, shell=True)
        return sprocess.communicate()[0].decode().split("\n")[1].strip()


class AnahtarKaynagiDXdiag:
    def __init__(self):
        self._dxdiag = self._getDxdiag_xml()

    def anahtar_olustur(self, sys_info: Optional[SystemInfo] = None):
        ozel_baslangic = "moe__gatherer"
        ozel_son = "yns"
        if sys_info is None:
            sys_info = self.get_sys_info(self._dxdiag)
        tum_bilgiler = (
            ozel_baslangic,
            sys_info,
            ozel_son,
        )
        b_tum_bilgiler = b"".join([str(i).encode("utf-8") for i in tum_bilgiler])

        return sha512(b_tum_bilgiler).hexdigest()

    @staticmethod
    def _dxdiag_xml_olustur() -> str:
        temel_dosya_adi = "dxdiag.xml"
        yeni_dosya_adi = (
            f"{sha512(psutil.users()[0].name.encode('utf-8') + platform.uname().processor.encode('utf-8')).hexdigest()}_nfo"
        )

        if os.path.exists(yeni_dosya_adi):
            f_data = open(yeni_dosya_adi, "rb").read()
            n_f_data = DosyaSıfreleme.sifrele(f_data, xml_dosya_sifresi)
            return n_f_data.decode("utf-8")

        sprocess = subprocess.Popen(["dxdiag", "/x", temel_dosya_adi], stdout=subprocess.PIPE, shell=True)
        _, stderrdata = sprocess.communicate()
        if stderrdata:
            raise Hata(stderrdata)
        os.rename(temel_dosya_adi, yeni_dosya_adi)
        f_data = open(yeni_dosya_adi, "rb").read()
        n_f_data = DosyaSıfreleme.sifrele(f_data, xml_dosya_sifresi)

        with open(yeni_dosya_adi, "wb") as f:
            f.write(n_f_data)

        return f_data.decode("utf-8")

    @staticmethod
    def _getDxdiag_xml() -> ET.Element:
        f_data = AnahtarKaynagiDXdiag._dxdiag_xml_olustur()
        return ET.ElementTree(ET.fromstring(f_data)).getroot()

    @staticmethod
    def get_sys_info(xml_root) -> SystemInfo:
        sys_info_xml = xml_root.find("SystemInformation")
        return SystemInfo(
            machine_name=sys_info_xml.find("MachineName").text,
            operating_system=sys_info_xml.find("OperatingSystem").text.split("(")[0].strip(),  # remove build number
            system_manufacturer=sys_info_xml.find("SystemManufacturer").text,
            system_model=sys_info_xml.find("SystemModel").text,
            bios=sys_info_xml.find("BIOS").text,
            firmware_type=sys_info_xml.find("FirmwareType").text,
            processor=sys_info_xml.find("Processor").text,  # remove cpu count and clock speed
        )


def anahtar_olustur():
    if DXDIAG_KULLAN:
        anahtar_kaynagi = AnahtarKaynagiDXdiag()
        return anahtar_kaynagi.anahtar_olustur()

    uname = platform.uname()
    anahtar_kaynagi = AnahtarKaynagi(
        cpu=uname.processor,
        hostname=uname.node,
        machine_type=uname.machine,
        process_total_cores=psutil.cpu_count(),
        processor_architecture=platform.architecture()[0],
        wmicode=platform.win32_ver()[0],
    )
    return anahtar_kaynagi.anahtar_olustur()


def anahtar_kontrol(anahtar):
    if anahtar in izinli_anahtarlar:
        return True
    else:
        raise KullaniciHatasi("cihazın kullanma yetkisi yok.")


def cihaz_yetkilimi():
    anahtar = anahtar_olustur()
    return anahtar_kontrol(anahtar)


if __name__ == "__main__":
    print(anahtar_olustur())
