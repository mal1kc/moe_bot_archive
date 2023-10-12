import timeit
from moe_bot import sabilter
from moe_bot.kaynakislem import (
    Varsayilanlar,
    _glob_dsn_sozluk_olustur,
    _glob_dsn_sozluk_olustur_no_comprehension,
    aktifEkranBoyutuEtiketi,
)
from moe_bot.temel_siniflar import Diller


def test_singleton_is_always_same():
    assert Varsayilanlar() is Varsayilanlar()

    class Dummy:
        pass

    assert Varsayilanlar() is not Dummy()


def test_compare_glob_dsn_olustur_funcs():
    ekran_byt_etiketi = aktifEkranBoyutuEtiketi()
    assert _glob_dsn_sozluk_olustur(ekran_byt_etiketi) == _glob_dsn_sozluk_olustur_no_comprehension(ekran_byt_etiketi)
    nd_time = timeit.timeit(lambda: _glob_dsn_sozluk_olustur_no_comprehension(ekran_byt_etiketi), number=1000)
    st_time = timeit.timeit(lambda: _glob_dsn_sozluk_olustur(ekran_byt_etiketi), number=1000)
    print(st_time, nd_time)
    # is that faster? yes
    # is that readable? no
    assert "EKMEK" in _glob_dsn_sozluk_olustur(ekran_byt_etiketi)
    img_klasor = sabilter.TaramaSabitleri.DOSYA_YOLLARI[1]
    beklenen_glob_dsn = f"{img_klasor}/{Diller.aktif_dil_getir().name.lower()}/{ekran_byt_etiketi}/{sabilter.TaramaSabitleri.GLOB_DSNLER['EKMEK']}"  # noqa
    assert _glob_dsn_sozluk_olustur(ekran_byt_etiketi)["EKMEK"] == beklenen_glob_dsn
