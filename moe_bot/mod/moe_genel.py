import glob
import logging

from moe_bot.ayarlar.genel_ayarlar import BASE_PATH

_gunlukcu = logging.getLogger(__name__)


# TODO: kamp islemden cikarilacak ve buraya eklenecek
class DosyaIslemleri:
    @staticmethod
    def globCoz(glob_dsn: str) -> list[str]:
        """
        onune base_path ekler ve glob metodunu kullanır
        """
        concat_glob_dsn = "{}/{}".format(BASE_PATH, glob_dsn)
        dosyalar = glob.glob(concat_glob_dsn)
        return dosyalar

    @staticmethod
    def gorselGetir(gorsel_id) -> str:
        """
        DosyaIslemleri.gorselleriGetir(gorsel_id)[0] ile aynı işi yapar
        """
        dosyalar = DosyaIslemleri.gorselleriGetir(gorsel_id)
        return dosyalar[0]

    @staticmethod
    def gorselleriGetir(glob_dsn: str, sirala: bool = False) -> list[str]:
        """
        * dosya adları glob_dsn'e uygun olan dosya adlarını döndürür\n
        * not: önüne base_path eklenir\n
            gorsel_id : str\n
            sirala : bool = False
            -> uzanti olmadan , tersten sıralar
        """
        dosyalar = DosyaIslemleri.globCoz(glob_dsn)

        if len(dosyalar) == 0:
            raise ValueError(f"Gorsel bulunamadı : {glob_dsn}, glob_dsn : {glob_dsn}, base_path : {BASE_PATH}")

        if sirala:
            dosyalar.sort(key=lambda x: int(x.split(".")[-2].split("_")[-1]), reverse=True)

        _gunlukcu.debug(f"gorselleri_getir -> gorsel_id : {glob_dsn},  glob_dsn: {glob_dsn}, bulunan dosyalar : {dosyalar}")
        return dosyalar
