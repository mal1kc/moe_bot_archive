from dataclasses import dataclass
import os
import subprocess
from typing import Optional
import psutil
from hashlib import sha512
import platform
import xml.etree.ElementTree as ET
import subprocess

from .hatalar import Hata, KullaniciHatasi

izinli_anahtarlar = {
    "3c4d6bfb1a3bc68738a2ceb5db57ea61a003fbcd65357cd91027db9966149e7bad99affe5c86093644f141973e488a03bd049e28a26768ad395fe883d5d3b06e",  # 3840
    "e94ec556caaa2a3fda2b037cf9d8d6c88bab1e5036851b6a64ad2cc1aaf97c05858b10af5cafd32bbc8156177f57f066d9d9ca8351d96c6fe4e45dbc8b5ea189",  # mal1kc , 2023-08-08 - 1
    # --------------------------------- önceki metod ile oluşturulan anahtarlar --------------------------------------------------------
    # "37af94aabee2109538566f1d6f7608e4ced073f2323a06e9598219600338d82a541868546cef6a0ddbc3539bb9442ff4f72b4501977d2e8d9d3f13bbae843fa1",  # mal1kc, 2023-07-23 - 1
    # "21eb42dbaa182e50736e39d40baa36048969adde335c0eeb09530a138ac1d7f161ebb69c48d9332f3ef0b587d413b0ecb3ad76e0e5b113d62ee73ff2d1cc96c1",
    # "51fc11a03b9a87c31aff8c78fada6cea9207a5df19d5db96cdf5173bda7c992615f5da44dc887482a3654e2eae105222789f2dcbd97c3e36edd166070f2b9ec4",  # 4K
    # "c4b1e398cca4faaaa62dcf651f28be0ab94596324ab3a179a291ea406eb8d372e833f98bf41d479326d6a7b975482a97c96efdbfba26c1e8d9bdd71e0f2bfc81",  # mal1kc, 2023-07-26 - 2 - laptop
    # "6f05eec579929bdb5cf9bdb176b216768487938bafaaaaafc9f00865280e86edc5daf36e73dfcdfe152bb25af2cf8c446550f2560172d2e1cce4807428c3c457",
    # "67e02484e71adc6df8f5a6b20ecb8f065692c82d6b20835d182531e46e0b7542a912efc0904cdff78ad3efa837e6749d74b85c10da0a055e2f81a59366cc3484",
    # "5d75174a1b84fa8dce9d21fb73ec43ea91fd74cd6171191a0332795c9cc6964202fd2918f3a70eae799e9cdd168c4216675d0ac8dc87f347e1f8b1d0ae511c57",
    # "f13187b500624a03eb7f6d5259e733ff2b2166f5897869706add8cf90a5898122715a04f68dd72460f94bbf8fc3aeec4b66916cde0f036b31e63564b74ae1581",
    # "62ee5de20245db583e28242956012117bf5d90e7c12af760889cbdc52b6d10df6ccd0292115519b9df52af6944c632b1a34df16531f6886aa7eaf8e006c9233a",  # burak
    # "89cf268ee7a6d844a7816adcc1ab1dd6f749d16ffeb01b83270b0968348b4f5c515ecd05728ebbd2bb1720670987d4495ea61ce26384c558570d4daba9add12d",  # serdar
    # "15d4e39d024cd53993507bd12ef175f1ace2fc85ec9e8352b87a6632a8b163aeb7bcf3912f44717a4671ee66b818d2b47887ec9b971902f2c5782599d7f39e96",  # burak sanal
    # "7f26bc60b995a80e306fc4be78265d7b4771d99e697d302ef56b7613db551dcd8f4600bf80afe7715c39a59eb05b2904385e34f0eed19fa6e6366668b2d4a21a",  # muhammet
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
        sys_info_tuple = (
            sys_info_xml.find("MachineName").text,
            # sys_info_xml.find("MachineId").text, TODO: bu kısım eklenecek
            sys_info_xml.find("OperatingSystem").text.split("(")[0].strip(),  # remove build number
            sys_info_xml.find("SystemManufacturer").text,
            sys_info_xml.find("SystemModel").text,
            sys_info_xml.find("BIOS").text,
            sys_info_xml.find("FirmwareType").text,
            sys_info_xml.find(
                "Processor"
            ).text,  # remove cpu count and clock speed , # FIXME: bug var burda -> Intel(R) Core(TM) i7-7700HQ CPU @ 2.80GHz
        )
        return SystemInfo(*sys_info_tuple)


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
